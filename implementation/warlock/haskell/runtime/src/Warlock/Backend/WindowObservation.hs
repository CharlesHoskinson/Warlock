{-# LANGUAGE OverloadedStrings #-}
{-# LANGUAGE ScopedTypeVariables #-}
-- One lexical, authenticated observation owner; no native action authority.
module Warlock.Backend.WindowObservation (decodeSelection,Reader,newReader,admitReader,readWindowReply,readWindowWatchReply) where
import Control.Exception (SomeException,SomeAsyncException,try,throwIO,fromException)
import Control.Monad (unless)
import Data.IORef
import Data.List (nub)
import Data.Text (Text)
import qualified Data.Text as T
import qualified Data.Text.Encoding as TE
import System.Mem.StableName (StableName,makeStableName)
import qualified Warlock.Backend.ForeignToplevelOwner as Owner
import Warlock.Backend.Store (DirectoryPin(..))
import Warlock.Bootstrap.ScopedPeer (Scope,withCurrentAdmission,scopeApplicationContext)
import Warlock.Capture.Process.Bootstrap (AdmissionDeadline,deadlineAbsoluteNs,remainingMicros)
import Warlock.Platform.Resolver (Identity(..))
import qualified Warlock.Platform.Resolver as Resolver
import Warlock.Protocol.Identity (Binding,Counter,frontend,parseCounter,renderCounter,addCounter)
import qualified Warlock.Protocol.ForeignToplevel as FT
import qualified Warlock.Protocol.Desktop as D
import Warlock.Protocol.PeerCredential (PeerCredential)
import Warlock.Protocol.StrictJson (Json(..),exactObject)
import qualified Warlock.Protocol.StrictJson as J

failure :: Show a => Either a b -> Either Text b
failure = either (Left . T.pack . show) Right
require :: Bool -> Text -> Either Text ()
require good reason = if good then Right () else Left reason
selectedObject :: [Text] -> Json -> Either Text [(Text,Json)]
selectedObject names = failure . exactObject names
selectedField :: Text -> [(Text,Json)] -> Either Text Json
selectedField name pairs = maybe (Left "missing endpoint field") Right (lookup name pairs)
selectedText :: Json -> Either Text Text
selectedText (JString value) = Right value
selectedText _ = Left "endpoint string required"
selectedNatural :: Json -> Either Text Integer
selectedNatural value = do
 text <- selectedText value
 _ <- failure (parseCounter True text)
 pure (read (T.unpack text))
selectedList :: Int -> (Json -> Either Text a) -> Json -> Either Text [a]
selectedList limit decode (JArray values)
 | length values<=limit = mapM decode values
 | otherwise = Left "endpoint array bound"
selectedList _ _ _ = Left "endpoint array required"
selectedIdentity :: J.Json -> Either Text Identity
selectedIdentity value = do
 fields <- selectedObject ["device","inode"] value
 Identity <$> (selectedField "device" fields >>= selectedNatural) <*> (selectedField "inode" fields >>= selectedNatural)
selectedAncestor :: J.Json -> Either Text Owner.AncestorPin
selectedAncestor value = do
 fields <- selectedObject ["path","device","inode","uid","mode"] value
 path <- selectedField "path" fields >>= selectedText
 dev <- selectedField "device" fields >>= selectedNatural
 ino <- selectedField "inode" fields >>= selectedNatural
 uid <- selectedField "uid" fields >>= selectedNatural
 mode <- selectedField "mode" fields >>= selectedNatural
 require (T.length path<=4096 && T.isPrefixOf "/" path && not (T.any (=='\0') path) && mode<=4095) "ancestor syntax"
 pure (Owner.AncestorPin (DirectoryPin (T.unpack path) dev ino) uid mode)
selectedProcess :: J.Json -> Either Text Owner.ProcessPin
selectedProcess value = do
 fields <- selectedObject ["pid","birth","parent","uid","gid"] value
 pid <- selectedField "pid" fields >>= selectedNatural
 birth <- selectedField "birth" fields >>= selectedNatural
 parent <- selectedField "parent" fields >>= selectedNatural
 uid <- selectedField "uid" fields >>= selectedNatural
 gid <- selectedField "gid" fields >>= selectedNatural
 require (pid>0 && birth>0) "process identity required"
 pure (Owner.ProcessPin pid birth parent uid gid)
selectedPin :: J.Json -> Either Text Resolver.Pin
selectedPin value = do
 fields <- selectedObject ["path","device","inode","kind"] value
 path <- selectedField "path" fields >>= selectedText
 dev <- selectedField "device" fields >>= selectedNatural
 ino <- selectedField "inode" fields >>= selectedNatural
 kind <- selectedField "kind" fields >>= selectedText
 selected <- case kind of
  "directory" -> Right Resolver.Directory
  "regular" -> Right Resolver.Regular
  _ -> Left "no executable symlink or unknown kind admitted"
 require (T.length path<=4096 && T.isPrefixOf "/" path && not (T.any (=='\0') path)) "executable pin path"
 pure (Resolver.Pin (TE.encodeUtf8 path) (Identity dev ino) selected)
selectedExecutable :: J.Json -> Either Text Owner.ExecutablePin
selectedExecutable value = do
 fields <- selectedObject ["root","pins","path","size","sha256"] value
 root <- selectedField "root" fields >>= selectedIdentity
 pins <- selectedField "pins" fields >>= selectedList 64 selectedPin
 path <- selectedField "path" fields >>= selectedText
 size <- selectedField "size" fields >>= selectedNatural
 digestText <- selectedField "sha256" fields >>= selectedText
 require (T.length digestText==64 && T.all (\c -> c>='0' && c<='9' || c>='a' && c<='f') digestText) "canonical SHA256 required"
 let digest = TE.encodeUtf8 digestText
 require (not (null pins) && size>0 && size<=67108864 && not (T.null path) && T.length path<=4096 && not (T.isPrefixOf "/" path) && not (T.any (=='\0') path) && all (\part -> part/="" && part/="." && part/="..") (T.splitOn "/" path)) "selected executable bounds"
 pure (Owner.ExecutablePin root pins (TE.encodeUtf8 path) [] size digest)

-- Generation comes from this full binding, never a separate startup counter.
decodeSelection :: Binding -> Json -> Either Text Owner.EndpointSelection
decodeSelection bound raw = do
 endpoint <- selectedObject ["bootId","ancestors","name","socket","processes","executable"] raw
 boot <- selectedField "bootId" endpoint >>= selectedText
 require (T.length boot==36 && all (\i -> T.index boot i=='-') [8,13,18,23] && T.all (\c -> c=='-' || c>='0' && c<='9' || c>='a' && c<='f') boot) "boot UUID"
 ancestors <- selectedField "ancestors" endpoint >>= selectedList 64 selectedAncestor
 name <- selectedField "name" endpoint >>= selectedText
 require (not (null ancestors) && not (T.null name) && T.length name<=64 && name/="." && name/=".." && T.all (\c -> c>='a' && c<='z' || c>='A' && c<='Z' || c>='0' && c<='9' || c=='-' || c=='_' || c=='.') name) "selected socket name"
 socket <- selectedField "socket" endpoint >>= selectedObject ["device","inode","uid","mode"]
 dev <- selectedField "device" socket >>= selectedNatural
 ino <- selectedField "inode" socket >>= selectedNatural
 uid <- selectedField "uid" socket >>= selectedNatural
 mode <- selectedField "mode" socket >>= selectedNatural
 require (ino>0 && mode<=4095) "selected socket identity"
 processes <- selectedField "processes" endpoint >>= selectedList 32 selectedProcess
 require (not (null processes)) "selected peer process required"
 executable <- selectedField "executable" endpoint >>= selectedExecutable
 pure (Owner.EndpointSelection (TE.encodeUtf8 boot) ancestors (T.unpack name) (Identity dev ino) uid mode processes executable (frontend bound))

data Ledger = Ledger Counter Counter [(FT.Handle,Counter)] [(FT.Output,Counter)] Counter (Maybe FT.Snapshot)
data Reader = Reader Binding AdmissionDeadline Owner.ForeignToplevelOwner
 (IORef Ledger) (IORef (Maybe (StableName Scope,PeerCredential))) (IORef Bool)
newReader :: Binding -> AdmissionDeadline -> Owner.ForeignToplevelOwner -> IO Reader
newReader bound deadline owner = do
 zero <- either (ioError . userError . show) pure (parseCounter True "0")
 Reader bound deadline owner <$> newIORef (Ledger zero zero [] [] zero Nothing) <*> newIORef Nothing <*> newIORef False

validateReaderScope :: Reader -> Scope -> PeerCredential -> IO ()
validateReaderScope (Reader bound deadline _ _ admitted failed) scope credential = do
 context <- scopeApplicationContext scope
 unless (maybe False (\(original,actual) -> actual==bound && deadlineAbsoluteNs original==deadlineAbsoluteNs deadline) context
        )
   (ioError (userError "window observation admission differs"))
 current <- makeStableName scope
 previous <- readIORef admitted
 case previous of
  Nothing -> writeIORef admitted (Just (current,credential))
  Just (original,peer) -> unless (current==original && credential==peer) (ioError (userError "window observation scope changed"))
 broken <- readIORef failed
 unless (not broken) (ioError (userError "window observation owner unavailable"))

admitReader :: Reader -> Scope -> PeerCredential -> IO ()
admitReader reader@(Reader _ _ owner _ _ _) scope credential = do
 result <- withCurrentAdmission scope credential $ do
  validateReaderScope reader scope credential
  -- Only initial capability admission reads here. Requests reserve their ID
  -- before their sole read, inside the Unknown conversion boundary below.
  _ <- Owner.readToplevelSnapshot owner
  pure ()
 either (ioError . userError . show) pure result

readWindowReply :: Reader -> Scope -> PeerCredential -> D.DesktopRequest -> IO D.DesktopReply
readWindowReply reader@(Reader bound deadline owner ledger _ failed) scope credential request = do
 unless (D.requestBinding request==bound && D.requestKind request==D.WindowRead) (ioError (userError "window request binding differs"))
 result <- withCurrentAdmission scope credential $ do
  validateReaderScope reader scope credential
  Ledger revision serial handles outputs lastRequest cached <- readIORef ledger
  unless (D.requestId request>lastRequest) (ioError (userError "window observation replay refused"))
  -- Consume before IO. Neither an uncertain read nor its response is replayed.
  writeIORef ledger (Ledger revision serial handles outputs (D.requestId request) cached)
  attempted <- try $ do
   left <- remainingMicros deadline
   unless (left>0) (ioError (userError "window observation deadline"))
   snapshot <- Owner.readToplevelSnapshot owner
   next <- either (ioError . userError . show) pure (addCounter revision 1)
   (issued,raw) <- either (ioError . userError . T.unpack) pure (encodeObserved bound next serial handles outputs snapshot)
   after <- remainingMicros deadline
   unless (after>0) (ioError (userError "window observation deadline"))
   let (serialNext,handlesNext,outputsNext)=issued
   reply <- either (ioError . userError . T.unpack) pure (D.windowSnapshot bound raw >>= \value -> D.windowObservationReply bound (D.requestId request) "Observed" (Just value))
   writeIORef ledger (Ledger next serialNext handlesNext outputsNext (D.requestId request) (Just snapshot))
   pure reply
  case attempted of
   Right reply -> pure reply
   Left (problem :: SomeException) -> do
    writeIORef failed True
    case fromException problem :: Maybe SomeAsyncException of
     Just _ -> throwIO problem
     Nothing -> either (ioError . userError . T.unpack) pure (D.windowObservationReply bound (D.requestId request) "Unknown" Nothing)
 either (ioError . userError . show) pure result

-- Retired tokens remain reserved. Exhaustion refuses instead of recycling IDs.
issue :: Eq a => Counter -> [(a,Counter)] -> [a] -> Either Text (Counter,[(a,Counter)])
issue serial table [] = Right (serial,table)
issue serial table (token:rest) = case lookup token table of
 Just _ -> issue serial table rest
 Nothing -> do
  require (length table<4096) "window observation identity ledger exhausted"
  next <- failure (addCounter serial 1)
  issue next (table++[(token,next)]) rest

encodeObserved :: Binding -> Counter -> Counter -> [(FT.Handle,Counter)] -> [(FT.Output,Counter)] -> FT.Snapshot
 -> Either Text ((Counter,[(FT.Handle,Counter)],[(FT.Output,Counter)]),Json)
encodeObserved bound revision serial handles outputs snapshot = do
 let rows=FT.toplevels snapshot
     memberships=nub (concatMap FT.toplevelOutputs rows)
 (afterHandles,knownHandles) <- issue serial handles (map FT.toplevelHandle rows)
 (afterOutputs,knownOutputs) <- issue afterHandles outputs memberships
 let ident table token=maybe (Left "unissued observation token") (Right . JString . renderCounter) (lookup token table)
     state value=JString (case value of FT.Maximized -> "maximized"; FT.Minimized -> "minimized"; FT.Activated -> "activated"; FT.Fullscreen -> "fullscreen")
     row value=do
      key <- ident knownHandles (FT.toplevelHandle value)
      parent <- maybe (Right JNull) (ident knownHandles) (FT.toplevelParent value)
      member <- mapM (ident knownOutputs) (FT.toplevelOutputs value)
      pure (JObject [("id",key),("title",JString (FT.toplevelTitle value)),("appId",JString (FT.toplevelAppId value)),("states",JArray (map state (FT.toplevelStates value))),("outputs",JArray member),("parent",parent)])
 encoded <- mapM row rows
 currentOutputs <- mapM (ident knownOutputs) memberships
 pure ((afterOutputs,knownHandles,knownOutputs),JObject [("owner",JString (renderCounter (frontend bound))),("revision",JString (renderCounter revision)),("view",JString "global"),("outputs",JArray currentOutputs),("windows",JArray encoded)])

-- This is a bounded authenticated read on the same lexical owner thread. It
-- never starts a worker, reconnects, grants effects, or refreshes the deadline.
readWindowWatchReply :: Reader -> Scope -> PeerCredential -> D.DesktopRequest -> IO D.DesktopReply
readWindowWatchReply reader@(Reader bound deadline owner ledger _ failed) scope credential request = do
 unless (D.requestBinding request==bound && D.requestKind request==D.WindowWatch) (ioError (userError "window watch binding differs"))
 base <- maybe (ioError (userError "window watch revision absent")) pure (D.windowWatchRevision request)
 let reply status snapshot = either (ioError . userError . T.unpack) pure (D.windowWatchReply bound (D.requestId request) base status snapshot)
 result <- withCurrentAdmission scope credential $ do
  validateReaderScope reader scope credential
  Ledger revision serial handles outputs lastRequest cached <- readIORef ledger
  unless (D.requestId request>lastRequest) (ioError (userError "window observation replay refused"))
  writeIORef ledger (Ledger revision serial handles outputs (D.requestId request) cached)
  -- A stale base consumes its request but performs no owner IO.
  if base/=revision || cached==Nothing then reply "Unavailable" Nothing else do
   attempted <- try $ do
    left <- remainingMicros deadline
    unless (left>0) (ioError (userError "window observation deadline"))
    snapshot <- Owner.readToplevelSnapshot owner
    after <- remainingMicros deadline
    unless (after>0) (ioError (userError "window observation deadline"))
    if cached==Just snapshot then reply "Unchanged" Nothing else do
     next <- either (ioError . userError . show) pure (addCounter revision 1)
     (issued,raw) <- either (ioError . userError . T.unpack) pure (encodeObserved bound next serial handles outputs snapshot)
     value <- either (ioError . userError . T.unpack) pure (D.windowSnapshot bound raw)
     changed <- reply "Changed" (Just value)
     final <- remainingMicros deadline
     unless (final>0) (ioError (userError "window observation deadline"))
     let (serialNext,handlesNext,outputsNext)=issued
     writeIORef ledger (Ledger next serialNext handlesNext outputsNext (D.requestId request) (Just snapshot))
     pure changed
   case attempted of
    Right value -> pure value
    Left (problem :: SomeException) -> do
     writeIORef failed True
     case fromException problem :: Maybe SomeAsyncException of
      Just _ -> throwIO problem
      Nothing -> reply "Unknown" Nothing
 either (ioError . userError . show) pure result
