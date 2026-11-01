{-# LANGUAGE OverloadedStrings #-}
{-# LANGUAGE ScopedTypeVariables #-}
-- Actual local UI owner: roles originate in separate bound listeners, never in
-- browser-supplied tags. Native authority remains on the inherited Unix peer.
module Warlock.Ui.Owner
 (UiEndpoints(..),TrustedOwnerEvent(..),EngineResult(..),UiResult(..),runUiOwner,runUiOwnerPrepared,uiResultJson) where
import Control.Concurrent (ThreadId,forkFinally,killThread)
import Control.Concurrent.MVar
import Control.Exception (SomeException,SomeAsyncException,fromException,mask,mask_,throwIO,try,finally)
import Control.Monad (forM,forM_,unless,when)
import qualified Crypto.Hash.SHA256 as SHA
import qualified Data.ByteString as B
import qualified Data.ByteString.Char8 as C
import Data.IORef
import Data.Text (Text)
import qualified Data.Text as T
import qualified Data.Text.Encoding as TE
import qualified Network.Socket as S
import Numeric (showHex)
import System.Posix.IO (FdOption(CloseOnExec),setFdOption)
import System.Posix.Types (Fd(..))
import System.Timeout (timeout)
import Warlock.Capture.Process.Bootstrap (remainingMicros)
import qualified Warlock.Protocol.Desktop as D
import Warlock.Protocol.Identity (Counter,parseCounter)
import qualified Warlock.Protocol.StrictJson as J
import Warlock.Ui.Config
import Warlock.Ui.Http
import Warlock.Ui.Native
import Warlock.Ui.Policy
import Warlock.Ui.PrivateNetwork (PeerNetwork, verifyPrivateNetwork)

data UiEndpoints = UiEndpoints {controllerOrigin :: Origin,barOrigin :: Origin,popupOrigin :: Origin,uiShouldStop :: IO Bool,uiRemainingMicros :: IO Int,uiLastProjection :: IO (Maybe J.Json)}
data TrustedOwnerEvent = OwnerTopology J.Json | OwnerDismiss J.Json | OwnerEscape J.Json | OwnerReflow J.Json deriving (Eq,Show)
data EngineResult = EngineResult {enginePassed :: Bool,engineCleanup :: Bool} deriving (Eq,Show)
data UiResult = UiResult
 {uiPassed :: Bool,uiCleanup :: Bool,uiEngineCleanup :: Bool,uiPeerPid :: Maybe Int,uiRequestCount :: Int,uiCommitCount :: Int,uiActionCount :: Int
 ,uiOrigins :: [(Role,B.ByteString)],uiTrace :: [J.Json],uiFailure :: Maybe Text} deriving (Eq,Show)
data CloseState = Open | Closed | Uncertain
data Ticket = Ticket S.Socket (MVar CloseState)
data Ledger = Ledger Bool Bool [Ticket]

require :: Bool -> String -> IO ()
require good reason = unless good (ioError (userError reason))
jsonBytes :: J.Json -> B.ByteString
jsonBytes = TE.encodeUtf8 . J.renderJson
gateway :: Text -> J.Json -> B.ByteString
gateway kind payload = jsonBytes (J.JObject [("bridgeProtocol",J.JNumber "1"),("kind",J.JString kind),("payload",payload)])
field :: Text -> J.Json -> Either Text J.Json
field name (J.JObject fields) = maybe (Left "UI field missing") Right (lookup name fields)
field _ _ = Left "UI object required"
object :: [Text] -> J.Json -> Either Text [(Text,J.Json)]
object names = either (Left . T.pack . show) Right . J.exactObject names
string :: J.Json -> Either Text Text
string (J.JString value) = Right value
string _ = Left "UI string required"
positive :: J.Json -> Either Text Counter
positive value = string value >>= either (Left . T.pack . show) Right . parseCounter False
counter :: J.Json -> Either Text Counter
counter value = string value >>= either (Left . T.pack . show) Right . parseCounter True
ensure :: Bool -> Text -> Either Text ()
ensure good reason = unless good (Left reason)

scope :: J.Json -> Either Text J.Json
scope value = do
 fields <- object ["id","generation"] value
 mapM_ (\name -> maybe (Left "UI scope field") positive (lookup name fields)) ["id","generation"]
 pure value

closeTicket :: Ticket -> IO Bool
closeTicket (Ticket socket cell) = mask_ $ do
 outcome <- modifyMVar cell $ \state -> case state of
  Closed -> pure (Closed,Right True)
  Uncertain -> pure (Uncertain,Right False)
  Open -> do
   result <- try (S.close socket) :: IO (Either SomeException ())
   pure $ case result of Right () -> (Closed,Right True); Left err -> (Uncertain,Left err)
 case outcome of
  Right clean -> pure clean
  Left err -> case fromException err :: Maybe SomeAsyncException of Just _ -> throwIO err; Nothing -> pure False
sameTicket :: Ticket -> Ticket -> Bool
sameTicket (Ticket _ a) (Ticket _ b) = a==b

acquire :: MVar Ledger -> IO S.Socket -> IO Ticket
acquire ledger create = mask_ $ do
 socket <- create
 ticket <- Ticket socket <$> newMVar Open
 granted <- modifyMVar ledger $ \state@(Ledger stopped poisoned held) ->
  if stopped || poisoned || length held>=8 then pure (state,False) else pure (Ledger stopped poisoned (ticket:held),True)
 if granted then do
  S.withFdSocket socket (\fd -> setFdOption (Fd fd) CloseOnExec True)
  pure ticket
 else do
  closed <- try (closeTicket ticket) :: IO (Either SomeException Bool)
  unless (either (const False) id closed) $ modifyMVar_ ledger $ \(Ledger stopped _ held) -> pure (Ledger stopped True (ticket:held))
  case closed of Left err | Just _ <- (fromException err :: Maybe SomeAsyncException) -> throwIO err; _ -> pure ()
  ioError (userError "UI socket owner unavailable")

release :: MVar Ledger -> Ticket -> IO Bool
release ledger ticket = mask_ $ do
 result <- closeTicket ticket
 modifyMVar_ ledger $ \(Ledger stopped poisoned held) -> pure
  (Ledger stopped (poisoned || not result) (if result then filter (not . sameTicket ticket) held else held))
 pure result

runUiOwner :: PeerNetwork -> UiConfig -> (UiEndpoints -> (TrustedOwnerEvent -> IO (Either Text ())) -> IO EngineResult) -> IO UiResult
runUiOwner witness config runEngine = runUiOwnerPrepared witness config $ \endpoints ownerEvent ->
 pure (runEngine endpoints ownerEvent, pure ())

-- Prepare the owned engine after binding its immutable origins but before
-- starting any listener/native workers. Acquisition owns its own partial
-- failure cleanup. Once returned, retirement runs even if worker startup or
-- engine execution fails; it remains responsible for its original deadline.
runUiOwnerPrepared :: PeerNetwork -> UiConfig
 -> (UiEndpoints -> (TrustedOwnerEvent -> IO (Either Text ())) -> IO (IO EngineResult, IO ()))
 -> IO UiResult
runUiOwnerPrepared witness config prepareEngine = mask $ \restore -> do
 ledger <- newMVar (Ledger False False [])
 nativeCell <- newIORef Nothing
 threads <- newIORef ([] :: [(ThreadId,MVar (Either SomeException ()))])
 failure <- newIORef Nothing
 trace <- newIORef []
 counts <- newIORef (0,0,0)
 originCell <- newIORef []
 engineStarted <- newIORef False
 engineStatus <- newIORef Nothing
 engineRetired <- newIORef False
 lastProjection <- newIORef Nothing
 scopeCell <- newMVar (Nothing,Nothing :: Maybe Counter)
 queues <- newMVar [(Controller,[]),(Bar,[]),(Popup,[])]
 let deadline=uiDeadline config
     failOwner reason = atomicModifyIORef' failure (\old -> ((case old of Nothing -> Just reason; other -> other),()))
     stopping = do
      Ledger stopped poisoned _ <- readMVar ledger
      bad <- readIORef failure
      left <- remainingMicros deadline
      pure (stopped || poisoned || bad/=Nothing || left<=0)
     record role route bytes = atomicModifyIORef' trace $ \rows ->
      let digest=C.pack (concatMap (\octet -> let hex=showHex octet "" in if length hex==1 then '0':hex else hex) (B.unpack (SHA.hash bytes)))
          row=J.JObject [("role",J.JString (T.pack (show role))),("route",J.JString route),("bytes",J.JNumber (T.pack (show (B.length bytes)))),("sha256",J.JString (TE.decodeUtf8 digest))]
      in (take 64 (row:rows),())
     enqueue rows = modifyMVar queues $ \old -> do
      let updated=[(role,existing++[bytes | (destination,bytes)<-rows,destination==role]) | (role,existing)<-old]
          valid=all (\(_,items) -> length items<=16 && all ((<=1048704) . B.length) items) updated
             && sum [B.length bytes | (_,items)<-updated,bytes<-items]<=16*1048704
      pure (if valid then updated else old,valid)
     dequeue role = modifyMVar queues $ \old ->
      let items=maybe [] id (lookup role old)
          (selected,rest)=case items of [] -> (Nothing,[]); x:xs -> (Just x,xs)
      in pure ([(key,if key==role then rest else value) | (key,value)<-old],selected)
     launch work = do
      done <- newEmptyMVar
      thread <- forkFinally (restore work) $ \result -> do
       stop <- stopping
       case result of Left err | not stop -> failOwner (T.pack (show err)); _ -> pure ()
       putMVar done result
      modifyIORef' threads ((thread,done):)
     ownerEvent event = do
      stop <- stopping
      if stop then pure (Left "UI owner retired") else do
       result <- case event of
        OwnerTopology payload -> modifyMVar scopeCell $ \state@(_,prior) -> case topology prior payload of
         Left reason -> pure (state,Left reason)
         Right (selected,revision) -> do
          accepted <- enqueue [(Controller,gateway "view-topology" payload)]
          when accepted (writeIORef lastProjection Nothing)
          pure (if accepted then (selected,Just revision) else state,if accepted then Right () else Left "UI event queue full")
        OwnerDismiss payload -> nativeEvent "view-dismiss" ["scope","lease"] payload
        OwnerEscape payload -> nativeEvent "view-escape" ["scope","publication","lease"] payload
        OwnerReflow payload -> nativeEvent "view-reflow" ["scope","lease"] payload
       case result of Left reason | reason /= staleOwnerEvent -> failOwner reason; _ -> pure ()
       pure result
     nativeEvent kind fields payload = withMVar scopeCell $ \(selected,_) -> do
      current <- readIORef lastProjection
      case validateOwnerEvent selected current fields payload of
       Left reason -> pure (Left reason)
       Right False -> pure (Left staleOwnerEvent)
       Right True -> do
        accepted <- enqueue [(Controller,gateway kind payload)]
        pure (if accepted then Right () else Left "UI event queue full")
     serve native role origin document listenerTicket@(Ticket listener _) = do
      stop <- stopping
      unless stop $ do
       ticket@(Ticket connection _) <- acquire ledger (fst <$> S.accept listener)
       result <- try $ do
        decoded <- readRequest deadline connection
        case decoded of
         Left _ -> do _ <- sendResponse deadline connection 400 [] B.empty; pure ()
         Right request -> case admitRequest origin role (requestMethod request) (requestTarget request) (requestHeaders request) (requestBody request) of
          Left _ -> do _ <- sendResponse deadline connection 403 [] B.empty; pure ()
          Right route -> do
           stopNow <- stopping
           if stopNow then do _ <- sendResponse deadline connection 503 [] B.empty; pure () else do
            atomicModifyIORef' counts (\(a,b,c) -> ((a+1,b,c),()))
            record role (T.pack (show route)) (requestBody request)
            response <- case route of
             Document -> do
              policy <- either (ioError . userError . show) pure (contentSecurityPolicy origin (documentScriptHash document) (documentStyleHash document))
              pure (200,[("Content-Type","text/html; charset=utf-8"),("Content-Security-Policy",policy)],documentBytes document)
             Events -> do
              event <- dequeue role
              pure $ case event of Nothing -> (204,[],B.empty); Just bytes -> (200,[("Content-Type","application/json")],bytes)
             Commit -> withMVar scopeCell $ \(selected,_) -> do
              let preflight = do
                   checked <- D.decodeDesktopCommit (requestBody request)
                   ensure (all ((==uiBinding config) . D.requestBinding) (D.commitRequests checked)) "HTTP commit binding"
                   projections <- presentation selected (D.commitProjection checked) (D.commitFocus checked)
                   pure (checked,projections)
              case preflight of
               Left _ -> pure (400,[],B.empty)
               Right (checked,projections) -> do
                reserved <- enqueue projections
                require reserved "UI presentation queue full"
                sent <- sendCommit native (requestBody request)
                _ <- either (ioError . userError . T.unpack) pure sent
                writeIORef lastProjection (Just (D.commitProjection checked))
                atomicModifyIORef' counts (\(a,b,c) -> ((a,b+1,c),()))
                pure (204,[],B.empty)
             Actions -> do
              selected <- fst <$> readMVar scopeCell
              case action role selected (requestBody request) of
               Left _ -> pure (400,[],B.empty)
               Right payload -> do
                accepted <- enqueue [(Controller,gateway "view-action" payload)]
                require accepted "UI action queue full"
                atomicModifyIORef' counts (\(a,b,c) -> ((a,b,c+1),()))
                pure (204,[],B.empty)
            let (code,headers,body)=response
                security=[("Cache-Control","no-store"),("X-Content-Type-Options","nosniff"),("Referrer-Policy","no-referrer"),("Cross-Origin-Resource-Policy","same-origin")]
            delivered <- sendResponse deadline connection code (security++headers) body
            require delivered "UI HTTP response unconfirmed"
       clean <- release ledger ticket
       unless clean (failOwner "UI connection closure uncertain")
       case result of Left (err :: SomeException) -> failOwner (T.pack (show err)); Right () -> pure ()
       serve native role origin document listenerTicket
     bindRole role document = do
      ticket@(Ticket socket _) <- acquire ledger (S.socket S.AF_INET S.Stream S.defaultProtocol)
      S.bind socket (S.SockAddrInet 0 (S.tupleToHostAddress (127,0,0,1)))
      S.listen socket 4
      address <- S.getSocketName socket
      port <- case address of S.SockAddrInet value host | host==S.tupleToHostAddress (127,0,0,1) -> pure (fromIntegral value); _ -> ioError (userError "UI listener address")
      origin <- either (ioError . userError . show) pure (makeOrigin port)
      pure (role,origin,document,ticket)
 attempted <- try $ do
  native <- adoptNative (uiBinding config) deadline
  writeIORef nativeCell (Just native)
  private <- restore (verifyPrivateNetwork witness)
  require private "owned private UI network unavailable"
  documents <- restore (prepareDocuments config)
  listeners <- mapM (\role -> case filter ((==role) . documentRole) documents of [document] -> bindRole role document; _ -> ioError (userError "UI role document missing")) [Controller,Bar,Popup]
  writeIORef originCell [(role,originBytes origin) | (role,origin,_,_)<-listeners]
  require (length (unique [originBytes origin | (_,origin,_,_)<-listeners])==3) "UI origins not distinct"
  let getOrigin role=case [origin | (key,origin,_,_)<-listeners,key==role] of [origin] -> pure origin; _ -> ioError (userError "UI role invariant")
  controller <- getOrigin Controller
  bar <- getOrigin Bar
  popup <- getOrigin Popup
  let endpoints=UiEndpoints controller bar popup stopping (remainingMicros deadline) (withMVar scopeCell (\_ -> readIORef lastProjection))
  left <- remainingMicros deadline
  require (left>0) "original UI deadline expired"
  -- The trusted GTK owner observes uiShouldStop on its main loop and owns
  -- cancellation/draining of native async callbacks. Do not inject a Haskell
  -- timeout through those callbacks. The original parent Bootstrap deadline
  -- still bounds this selected process; HTTP/native admission also retains D.
  writeIORef engineStarted True
  (runEngine,retireEngine) <- prepareEngine endpoints ownerEvent
  (do
    forM_ listeners (\(role,origin,document,ticket) -> launch (serve native role origin document ticket))
    launch $ let loop = do raw <- receiveGateway native; record Controller "native-event" raw; accepted <- enqueue [(Controller,raw)]; require accepted "native event queue full"; loop in loop
    result <- restore runEngine
    writeIORef engineStatus (Just result)
    remaining <- remainingMicros deadline
    require (remaining>0) "original UI engine deadline expired"
    pure (enginePassed result)) `finally` (retireEngine >> writeIORef engineRetired True)
 held <- modifyMVar ledger (\(Ledger _ poisoned tickets) -> pure (Ledger True poisoned tickets,tickets))
 socketCleanups <- forM held (\ticket -> try (closeTicket ticket) :: IO (Either SomeException Bool))
 native <- readIORef nativeCell
 nativeCleanup <- try (maybe (pure True) retireNative native) :: IO (Either SomeException Bool)
 workers <- readIORef threads
 joins <- forM workers $ \(thread,done) -> try $ do
  ended <- tryReadMVar done
  case ended of
   Just _ -> pure True
   Nothing -> do
    killThread thread
    left <- remainingMicros deadline
    finished <- if left>0 then timeout left (readMVar done) else tryReadMVar done
    pure (case finished of Just _ -> True; Nothing -> False)
 let asyncs=[err | Left err <- socketCleanups++[nativeCleanup]++joins,Just _ <- [fromException err :: Maybe SomeAsyncException]]
 case attempted of Left err | Just _ <- (fromException err :: Maybe SomeAsyncException) -> throwIO (err :: SomeException); _ -> case asyncs of first:_ -> throwIO first; [] -> pure ()
 bad <- readIORef failure
 started <- readIORef engineStarted
 status <- readIORef engineStatus
 retired <- readIORef engineRetired
 let engineClean=not started || (retired && maybe False engineCleanup status)
     clean=engineClean && all (either (const False) id) (nativeCleanup:socketCleanups) && all (either (const False) id) joins
     problem=case attempted of Left (err :: SomeException) -> Just (T.pack (show err)); Right _ -> bad
     passed=either (const False) id attempted && clean && problem==Nothing
 (requests,commits,actions) <- readIORef counts
 origins <- readIORef originCell
 rows <- reverse <$> readIORef trace
 pure (UiResult passed clean engineClean (nativePeerPid <$> native) requests commits actions origins rows problem)

unique :: Eq a => [a] -> [a]
unique = foldr (\item rest -> if item `elem` rest then rest else item:rest) []

topology :: Maybe Counter -> J.Json -> Either Text (Maybe J.Json,Counter)
topology prior payload = do
 version <- field "viewProtocol" payload
 let names=if version==J.JNumber "2" then ["viewProtocol","kind","revision","views","locations"] else ["viewProtocol","kind","revision","views"]
 _ <- object names payload
 ensure (version `elem` [J.JNumber "1",J.JNumber "2"]) "UI topology version"
 kind <- field "kind" payload
 ensure (kind==J.JString "view-topology") "UI topology kind"
 revision <- field "revision" payload >>= positive
 ensure (maybe True (<revision) prior) "stale UI topology"
 table <- field "views" payload
 selected <- case table of J.JArray [] -> Right Nothing; J.JArray [entry] -> Just <$> scope entry; _ -> Left "this UI owner supports one actually owned view"
 when (version==J.JNumber "2") $ do
  locations <- field "locations" payload
  let expected=maybe [] (:[]) selected
  rows <- case locations of J.JArray values | length values==length expected -> Right values; _ -> Left "UI topology location count"
  forM_ (zip expected rows) $ \(identity,row) -> do
   _ <- object ["scope","box"] row
   ensure (field "scope" row==Right identity) "UI topology location scope"
   box <- field "box" row
   case box of
    J.JArray [J.JNumber x,J.JNumber y,J.JNumber width,J.JNumber height] ->
     ensure (all integral [x,y,width,height] && positiveDimension width && positiveDimension height) "UI topology box"
    _ -> Left "UI topology box fields"
 pure (selected,revision)
 where
  integral text = case reads (T.unpack text) of [(value,"")] -> value>=(negate 2147483648::Integer) && value<=2147483647; _ -> False
  positiveDimension text = case reads (T.unpack text) of [(value,"")] -> value>(0::Integer); _ -> False

-- Stale well-formed observations are explicit refusals, not owner failures.
-- Dismiss/Reflow carry no publication, so their comparison is limited to the
-- scope and lease present on the wire. Escape also compares publication.
staleOwnerEvent :: Text
staleOwnerEvent = "stale native UI projection"

validateOwnerEvent :: Maybe J.Json -> Maybe J.Json -> [Text] -> J.Json -> Either Text Bool
validateOwnerEvent selected current names payload = do
 _ <- object names payload
 target <- field "scope" payload >>= scope
 lease <- field "lease" payload
 _ <- counter lease
 publication <- if "publication" `elem` names then do
  value <- field "publication" payload
  _ <- positive value
  pure (Just value)
 else pure Nothing
 case current of
  Nothing -> pure False
  Just value -> do
   frameValue <- field "frame" value
   currentLease <- field "lease" frameValue
   currentPublication <- field "publication" frameValue
   pure (selected == Just target && lease == currentLease && maybe True (==currentPublication) publication)

presentation :: Maybe J.Json -> J.Json -> [Text] -> Either Text [(Role,B.ByteString)]
presentation selected projection targets = do
 _ <- object ["viewProtocol","kind","revision","views","focusOwner","popupOwner","frame","announcer","announcement"] projection
 ensure ((field "viewProtocol" projection)==Right (J.JNumber "1") && field "kind" projection==Right (J.JString "view-frame")) "UI view frame header"
 _ <- field "revision" projection >>= counter
 views <- field "views" projection
 ensure (views==J.JArray (maybe [] (:[]) selected)) "UI projection view custody"
 focused <- field "focusOwner" projection
 popup <- field "popupOwner" projection
 ensure (all (\value -> value==J.JNull || Just value==selected) [focused,popup]) "UI projection owner custody"
 frameValue <- field "frame" projection
 _ <- field "surfaceProtocol" frameValue >>= \value -> ensure (value==J.JNumber "2") "UI surface version"
 publication <- field "publication" frameValue
 _ <- positive publication
 lease <- field "lease" frameValue
 _ <- counter lease
 announcer <- field "announcer" projection
 message <- field "announcement" projection
 let forRole role =
      let surface=if role==Bar then "bar" else "popup"
          recipient=J.JObject [("scope",maybe J.JNull id selected),("surface",J.JString surface)]
          announcement=J.JObject [("announcementProtocol",J.JNumber "1"),("kind",J.JString "announcement-projection"),("recipient",recipient),("announcer",announcer),("publication",publication),("lease",lease),("message",message),("deliver",J.JBool (announcer==recipient))]
      in [(role,gateway "presentation" frameValue),(role,gateway "announcements" announcement)]
 focusEvents <- mapM (focusEvent frameValue publication lease) targets
 pure (concatMap forRole [Bar,Popup]++focusEvents)
 where
  focusEvent frameValue publication lease target = do
   bar <- controls "bar" frameValue
   popup <- controls "popup" frameValue
   let matching=[(role,surface) | (role,surface,rows)<-[(Bar,"bar",bar),(Popup,"popup",popup)],row<-rows,field "domId" row==Right (J.JString target),field "enabled" row==Right (J.JBool True) || field "focusOnly" row==Right (J.JBool True)]
   (role,surface) <- case matching of [entry] -> Right entry; _ -> Left "focus target is absent, disabled or ambiguous"
   let packet=J.JObject [("focusProtocol",J.JNumber "1"),("kind",J.JString "focus"),("surface",J.JString surface),("publication",publication),("lease",lease),("domId",J.JString target)]
   pure (role,gateway "focus" packet)
  controls surface value = do
   rows <- field surface value
   case rows of J.JArray entries -> Right entries; _ -> Left "UI controls required"


action :: Role -> Maybe J.Json -> B.ByteString -> Either Text J.Json
action role selected raw = do
 limit <- either (Left . T.pack . show) Right (J.bounds 8192 16)
 value <- either (Left . T.pack . show) Right (J.decodeStrict limit raw)
 kind <- field "kind" value >>= string
 let common=["surfaceProtocol","kind","surface","publication","lease"]
     extras=case kind of
      "surface-action" -> ["id"]++(case field "trigger" value of Right _ -> ["trigger"]; _ -> [])
      "surface-query" -> ["id","query"]
      "surface-context" -> ["id","trigger","x","y"]
      "surface-menu-navigation" -> ["key"]
      "surface-notification-focus" -> ["id"]
      _ -> []
 ensure (not (null extras)) "unapproved renderer method"
 _ <- object (common++extras) value
 ensure (field "surfaceProtocol" value==Right (J.JNumber "2")) "renderer surface version"
 ensure (field "surface" value==Right (J.JString (if role==Bar then "bar" else "popup"))) "renderer role mismatch"
 _ <- field "publication" value >>= positive
 _ <- field "lease" value >>= counter
 forM_ (filter (`elem` extras) ["id","query","key","trigger"]) $ \name -> do
  text <- field name value >>= string
  ensure (J.utf16Length text<=512 && not (T.any (\c -> c<' ' || c=='\127') text) && (name/="id" || kind=="surface-notification-focus" || not (T.null text))) "renderer text bound"
 when ("trigger" `elem` extras) $ do
  trigger <- field "trigger" value >>= string
  ensure (trigger `elem` ["pointer","keyboard"]) "renderer trigger"
 forM_ (filter (`elem` extras) ["x","y"]) $ \name -> do
  coordinate <- field name value
  case coordinate of
   J.JNumber text -> case reads (T.unpack text) of
    [(number,"")] | number>=(negate 2147483648::Integer) && number<=2147483647 -> pure ()
    _ -> Left "renderer coordinate bound"
   _ -> Left "renderer coordinate"
 current <- maybe (Left "renderer has no owned view") Right selected
 pure (J.JObject [("viewProtocol",J.JNumber "1"),("kind",J.JString "view-action"),("scope",current),("action",value)])

uiResultJson :: UiResult -> B.ByteString
uiResultJson result = jsonBytes (J.JObject
 [("passed",J.JBool (uiPassed result)),("cleanup",J.JBool (uiCleanup result)),("engineCleanup",J.JBool (uiEngineCleanup result)),("peerPid",maybe J.JNull (J.JNumber . T.pack . show) (uiPeerPid result))
 ,("requests",J.JNumber (T.pack (show (uiRequestCount result)))),("commits",J.JNumber (T.pack (show (uiCommitCount result)))),("actions",J.JNumber (T.pack (show (uiActionCount result))))
 ,("origins",J.JArray [J.JObject [("role",J.JString (T.pack (show role))),("origin",J.JString (TE.decodeUtf8 origin))] | (role,origin)<-uiOrigins result])
 ,("trace",J.JArray (uiTrace result)),("failure",maybe J.JNull J.JString (uiFailure result)),("nativeAcceptance",J.JBool False),("releaseAccepted",J.JBool False)])
