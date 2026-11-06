{-# LANGUAGE OverloadedStrings #-}
{-# LANGUAGE ScopedTypeVariables #-}
-- Production application actor. GUI policy and presentation stay in Elm.
module Warlock.Backend
 (DirectoryPin(..),BackendConfig,loadBackendConfig,configuredNotificationBusAddress,BackendResult(..),BackendAttemptStage(..),BackendRetirement(..),runBackend,backendResultJson,NotificationGeneration,NotificationIssuer,IssuerFailure,issuerFailureCustody,IssuerInterrupted(..),newNotificationIssuer,provisionNotificationIssuer,reserveNotificationGeneration,retireNotificationIssuer,notificationGenerationText,BackendCustodyException(..),BackendCustodyFailure(..)) where
import Control.Exception (Exception(..),SomeException,SomeAsyncException,asyncExceptionFromException,asyncExceptionToException,fromException,mask,throwIO,try)
import Control.Monad (forM_,unless)
import qualified Data.ByteString as B
import Data.IORef
import qualified Data.Set as Set
import Data.Text (Text)
import qualified Data.Text as T
import qualified Data.Text.Encoding as TE
import System.Posix.Files (deviceID,fileID,getSymbolicLinkStatus)
import Text.Read (readMaybe)
import Warlock.Backend.Catalog
import Warlock.Backend.NotificationIssuer (NotificationGeneration,NotificationIssuer,IssuerFailure,issuerFailureCustody,IssuerInterrupted(..),newIssuer,provisionIssuer,reserveGeneration,retireIssuer,generationText)
import Warlock.Backend.PinStore
import Warlock.Backend.Store
import Warlock.Ui.Display (readDisplayEnvironment)
import Warlock.Bootstrap
import Warlock.Capture.Process.Bootstrap (Containment(..),OwnerStatus(..),ToolError(..),deadlineFromAbsoluteNs,selectedCustody,selectedContainment,selectedOperation,selectedObservedExit)
import Warlock.Platform.Resolver (Identity(..),Kind(..),Pin(..),withRoot)
import Warlock.Protocol.Codec (checkedDesktopCommit,checkDesktopReply,desktopProfile,encodeServerCheckedWith)
import Warlock.Protocol.CredentialIngress
import qualified Warlock.Protocol.Desktop as D
import Warlock.Protocol.Identity (Binding,Counter,binding,parseCounter,renderCounter,lifetime,session,frontend)
import Warlock.Protocol.Ingress (Direction(..),Priority(..),ingressBinding)
import Warlock.Protocol.StrictJson

data UiImage = UiImage FilePath Integer Integer Integer B.ByteString [String] [DirectoryPin]
data BackendConfig = BackendConfig Binding String UiImage [DirectoryPin] DirectoryPin Text Bool (Maybe Text)

-- Selected startup data only. Actual bus authentication, ownership, deadline
-- and lifecycle checks remain necessary before any notification operation.
configuredNotificationBusAddress :: BackendConfig -> Maybe Text
configuredNotificationBusAddress (BackendConfig _ _ _ _ _ _ _ address) = address

notificationAddress :: Text -> Either Text Text
notificationAddress raw = do
 body <- maybe (Left "notification bus must use one explicit unix path") Right (T.stripPrefix "unix:path=" raw)
 let (path,suffix) = T.breakOn ",guid=" body
     asciiPath c = (c>='a' && c<='z') || (c>='A' && c<='Z') || (c>='0' && c<='9') || c `elem` ("/_-." :: String)
     parts = T.splitOn "/" path
     guidValid = case T.stripPrefix ",guid=" suffix of
      Nothing -> T.null suffix
      Just guid -> T.length guid==32 && T.all (\c -> (c>='0' && c<='9') || (c>='a' && c<='f')) guid
 require (T.isPrefixOf "/" path && T.length path<=4096 && T.all asciiPath path
   && length parts>=2 && all (\part -> not (T.null part) && part/="." && part/="..") (drop 1 parts)
   && guidValid) "invalid explicit notification bus address"
 pure raw
-- The exception remains asynchronously classified, and retains the original
-- exception and issuer whenever ordinary result custody cannot be returned.
data BackendCustodyException = BackendCustodyException SomeException NotificationIssuer
instance Show BackendCustodyException where show _ = "backend interrupted with issuer custody"
instance Exception BackendCustodyException where
 toException = asyncExceptionToException
 fromException = asyncExceptionFromException
-- Synchronous observation errors retain custody without being misclassified.
data BackendCustodyFailure = BackendCustodyFailure SomeException NotificationIssuer
instance Show BackendCustodyFailure where show _ = "backend observation failed with issuer custody"
instance Exception BackendCustodyFailure

newNotificationIssuer :: BackendConfig -> IO NotificationIssuer
newNotificationIssuer (BackendConfig _ deadlineText _ _ pin _ _ _) = newIssuer pin deadlineText
provisionNotificationIssuer :: NotificationIssuer -> IO (Either IssuerFailure ())
provisionNotificationIssuer = provisionIssuer
reserveNotificationGeneration :: NotificationIssuer -> IO (Either IssuerFailure NotificationGeneration)
reserveNotificationGeneration = reserveGeneration
retireNotificationIssuer :: NotificationIssuer -> IO Bool
retireNotificationIssuer = retireIssuer
notificationGenerationText :: NotificationGeneration -> Text
notificationGenerationText = generationText

-- Closed diagnostic classifications only; none is a grant or success proof.
data BackendAttemptStage = AttemptConversationException | AttemptRootRefused
 | AttemptBootstrapRefused | AttemptPendingCustody | AttemptExecuted deriving (Eq,Show)
data BackendRetirement = RetirementConfirmed | RetirementUnconfirmed | RetirementException deriving (Eq,Show)

data BackendResult = BackendResult
 {backendPassed :: Bool,backendCleanup :: Bool,backendCallbackCount :: Int,backendOperationCount :: Int
 ,backendBootstrap :: Either Text BootstrapResult,backendAuthObservation :: Maybe AuthObservation
 ,backendCredentialTrace :: [CredentialObservation],backendSelectedPid :: Maybe Integer
 ,backendProcessCleanup :: Bool,backendCatalogCleanup :: Bool,backendPinCleanup :: Bool
 ,backendAttemptStage :: BackendAttemptStage
 ,backendRetirements :: (BackendRetirement,BackendRetirement,BackendRetirement)
 ,backendNotificationCustody :: Maybe NotificationIssuer} deriving (Eq,Show)

loadBackendConfig :: FilePath -> IO (Either Text BackendConfig)
loadBackendConfig path = mask $ \restore -> do
 owner <- newStoreOwner
 observed <- try (restore (readStartupFile owner path))
 retirement <- try (retireStoreOwner owner) :: IO (Either SomeException Bool)
 let cleanupAsync=[problem | Left problem <- [retirement],Just _ <- [fromException problem :: Maybe SomeAsyncException]]
 case observed of
  Left (problem :: SomeException) -> case fromException problem :: Maybe SomeAsyncException of
   Just _ -> throwIO problem
   Nothing -> case cleanupAsync of other:_ -> throwIO other; [] -> pure (Left "trusted startup configuration unavailable")
  Right bytes -> case cleanupAsync of
   problem:_ -> throwIO problem
   [] -> pure $ if either (const False) id retirement then decodeConfig bytes else Left "startup configuration retirement uncertain"

decodeConfig :: B.ByteString -> Either Text BackendConfig
decodeConfig bytes = do
 limits <- failure (bounds 131072 16)
 raw <- failure (decodeStrict limits bytes)
 let names=["schema","binding","deadlineMonotonicNs","ui","catalogRoots","pinsRoot","locale"]
 let optionalNames = case raw of
      JObject pairs -> [name | name <- ["applicationAttachment","notificationBusAddress"], any ((==name) . fst) pairs]
      _ -> []
 fields <- object (names++optionalNames) raw
 attachment <- case lookup "applicationAttachment" fields of
  Nothing -> Right False
  Just (JBool value) -> Right value
  _ -> Left "invalid application attachment opt-in"
 notificationBus <- case lookup "notificationBusAddress" fields of
  Nothing -> Right Nothing
  Just (JString address) -> Just <$> notificationAddress address
  _ -> Left "invalid notification bus selection"
 require (lookup "schema" fields==Just (JNumber "1")) "unsupported startup schema"
 bound <- key "binding" fields >>= bindingConfig
 deadline <- key "deadlineMonotonicNs" fields >>= string
 _ <- failure (parseCounter False deadline)
 image <- key "ui" fields >>= imageConfig
 roots <- key "catalogRoots" fields >>= array >>= mapM directoryConfig
 require (length roots<=32) "catalog root capacity"
 pins <- key "pinsRoot" fields >>= directoryConfig
 locale <- key "locale" fields >>= string
 require (T.length locale<=128 && not (T.any (< ' ') locale)) "invalid trusted locale"
 pure (BackendConfig bound (T.unpack deadline) image roots pins locale attachment notificationBus)
 where
  bindingConfig raw = do
   fields <- object ["lifetime","session","frontend"] raw
   life <- key "lifetime" fields >>= positive
   sess <- key "session" fields >>= positive
   front <- key "frontend" fields >>= positive
   failure (binding life sess front)
  directoryConfig raw = do
   fields <- object ["path","device","inode"] raw
   path <- key "path" fields >>= pathString
   dev <- key "device" fields >>= integer True
   ino <- key "inode" fields >>= integer False
   pure (DirectoryPin path dev ino)
  imageConfig raw = do
   fields <- object ["path","device","inode","size","sha256","arguments","ancestors"] raw
   path <- key "path" fields >>= pathString
   dev <- key "device" fields >>= integer True
   ino <- key "inode" fields >>= integer False
   size <- key "size" fields >>= integer False
   digest <- key "sha256" fields >>= string
   require (T.length digest==64 && T.all (\char -> char>='0' && char<='9' || char>='a' && char<='f') digest) "invalid UI digest"
   args <- key "arguments" fields >>= array >>= mapM string
   require (length args<=128 && sum (map T.length args)<=32768 && all (\arg -> T.length arg<=4096 && not (T.any (=='\0') arg)) args) "invalid trusted UI arguments"
   parents <- key "ancestors" fields >>= array >>= mapM directoryConfig
   require (length parents<=64) "UI ancestor capacity"
   pure (UiImage path dev ino size (TE.encodeUtf8 digest) (map T.unpack args) parents)
  pathString raw = do
   path <- string raw
   require (T.isPrefixOf "/" path && T.length path<=4096 && not (T.any (\char -> char=='\0' || char<' ') path) && all (\part -> part/="." && part/="..") (T.splitOn "/" path)) "invalid trusted path"
   pure (T.unpack path)
  integer zero raw = do
   value <- string raw >>= failure . parseCounter zero
   maybe (Left "invalid native integer") Right (readMaybe (T.unpack (renderCounter value)))

failure :: Show a => Either a b -> Either Text b
failure = either (Left . T.pack . show) Right
require :: Bool -> Text -> Either Text ()
require good reason = if good then Right () else Left reason
object :: [Text] -> Json -> Either Text [(Text,Json)]
object names = failure . exactObject names
key :: Text -> [(Text,Json)] -> Either Text Json
key name fields = maybe (Left "missing startup field") Right (lookup name fields)
string :: Json -> Either Text Text
string (JString value) = Right value
string _ = Left "startup string required"
array :: Json -> Either Text [Json]
array (JArray values) = Right values
array _ = Left "startup array required"
positive :: Json -> Either Text Counter
positive value = string value >>= failure . parseCounter False

-- Single production authority for desktop request semantics. The bounded runner uses it;
-- a future persistent runner can share it; admission/deadline
-- ownership stays with the caller and no wire input chooses a callback.
applyDesktopRequest
 :: Binding -> Catalog -> PinStore -> IORef Int
 -> IORef (Maybe (Counter,D.PinSnapshot,D.DesktopReply))
 -> (D.DesktopReply -> IO ()) -> D.DesktopRequest -> IO ()
applyDesktopRequest bound catalog pins operations lastWrite sendReply request = case D.requestKind request of
  D.CatalogRead -> do
   modifyIORef' operations (+1)
   actual <- prepareCatalogPublication catalog
   preferences <- either (const Nothing) Just <$> readPins pins
   case actual of
    Left _ -> do
     construct (D.catalogReply bound (D.requestId request) Nothing preferences) >>= sendReply
    Right (snapshot,_,publication) -> do
     -- Only the actual successful write of this exact constructed reply may
     -- publish its revision for data resolution. Overflow/failed writes never
     -- publish, and an uncertain write is not followed by a fallback replay.
     case D.catalogReply bound (D.requestId request) (Just snapshot) preferences of
      Left _ -> do
       construct (D.catalogReply bound (D.requestId request) Nothing preferences) >>= sendReply
      Right reply -> do
       catalogPublicationResult <- publishCatalog publication (sendReply reply)
       case catalogPublicationResult of
        Left _ -> ioError (userError "catalog reply publication unconfirmed")
        Right () -> pure ()
  D.PinsWrite -> case D.pinProposal request of
   Nothing -> ioError (userError "checked pin proposal missing")
   Just proposal -> do
    previous <- readIORef lastWrite
    case previous of
     Just (identity,old,reply) | D.requestId request==identity && old==proposal -> sendReply reply
     Just (identity,_,_) | D.requestId request<=identity -> construct (D.pinsReply bound (D.requestId request) D.PinRefused Nothing) >>= sendReply
     _ -> do
      -- Reserve an unconfirmed disposition before any store mutation.
      unknown <- construct (D.pinsReply bound (D.requestId request) D.PinUnknown Nothing)
      writeIORef lastWrite (Just (D.requestId request,proposal,unknown))
      modifyIORef' operations (+1)
      -- A cold backend validates additions against actual current catalog
      -- data as well; no preceding read/cache in this session is required.
      known <- either (const Set.empty) snd <$> readCatalog catalog
      (status,snapshot) <- savePins pins known proposal
      reply <- construct (D.pinsReply bound (D.requestId request) status snapshot)
      writeIORef lastWrite (Just (D.requestId request,proposal,reply))
      sendReply reply
 where
  construct = either (ioError . userError . T.unpack) pure

runBackend :: BackendConfig -> IO BackendResult
runBackend (BackendConfig bound deadlineText (UiImage image dev ino size digest arguments parents) roots pinsRoot locale attachmentEnabled _) = mask $ \restore -> do
 catalog <- newCatalog roots locale (lifetime bound)
 pins <- newPinStore pinsRoot
 notificationIssuer <- newIssuer pinsRoot deadlineText
 attachmentAttempted <- newIORef False
 callbacks <- newIORef 0
 operations <- newIORef 0
 -- One bounded last-disposition cell plus a high-water mark prevents replay
 -- of old/uncertain pin writes without retaining an unbounded request history.
 lastWrite <- newIORef (Nothing :: Maybe (Counter,D.PinSnapshot,D.DesktopReply))
 current <- newCurrentSessions
 owner <- newBootstrapOwner current
 slot <- newIORef Nothing
 ingressBound <- either (ioError . userError . show) pure (ingressBinding (renderCounter (lifetime bound)) (renderCounter (session bound)) (renderCounter (frontend bound)))
 let sendReply reply = do
      checked <- either (ioError . userError . T.unpack) pure (checkDesktopReply reply)
      bytes <- either (ioError . userError . T.unpack) pure (encodeServerCheckedWith desktopProfile checked)
      ingress <- readIORef slot >>= maybe (ioError (userError "backend ingress not activated")) pure
      queued <- enqueueCredentialIngress ingress Ordinary bytes
      unless (queued==Right ()) (ioError (userError "backend reply enqueue refused"))
      sent <- sendCredentialIngress ingress
      unless (sent==Right ()) (ioError (userError "backend reply delivery unconfirmed"))
     construct = either (ioError . userError . T.unpack) pure
     handle = applyDesktopRequest bound catalog pins operations lastWrite sendReply
     handler checked = case checkedDesktopCommit checked of
      Nothing -> ioError (userError "native profile reached desktop actor")
      Just commit -> do
       modifyIORef' callbacks (+1)
       let requests=D.commitRequests commit
       unless (all ((==bound) . D.requestBinding) requests) (ioError (userError "checked commit binding mismatch"))
       -- Reserve the one attempt before enqueue/delivery. Any exception ends
       -- this authenticated session; an uncertain send is never replayed.
       firstAttempt <- if attachmentEnabled
        then atomicModifyIORef' attachmentAttempted (\attempted -> (True,not attempted))
        else pure False
       if firstAttempt then construct (D.applicationAttached bound) >>= sendReply else pure ()
       -- The shared codec/gate has validated ALL requests before this point.
       -- Presentation-only commits run this empty loop, with zero domain IO.
       forM_ requests handle
 ingress <- newDesktopCredentialIngress ingressBound FromElm handler (\_ -> ioError (userError "unexpected server input"))
 writeIORef slot (Just ingress)
 attempted <- try $ restore $ do
  deadline <- deadlineFromAbsoluteNs deadlineText >>= either (ioError . userError . show) pure
  displayEnvironment <- readDisplayEnvironment >>= either (ioError . userError . T.unpack) pure
  rootStat <- getSymbolicLinkStatus "/"
  let imagePins=[Pin (TE.encodeUtf8 (T.pack (directoryPath parent))) (Identity (directoryDevice parent) (directoryInode parent)) Directory | parent <- parents]
       ++[Pin (TE.encodeUtf8 (T.pack image)) (Identity dev ino) Regular]
  withRoot "/" (Identity (toInteger (deviceID rootStat)) (toInteger (fileID rootStat))) $ \root ->
   runBootstrapWithArguments owner root imagePins (TE.encodeUtf8 (T.pack (drop 1 image))) [] size digest arguments deadline ([("LANG","C"),("LC_ALL","C")] ++ displayEnvironment) ingress
 processRetirement <- try (retireBootstrap owner) :: IO (Either SomeException Bool)
 catalogRetirement <- try (retireCatalog catalog) :: IO (Either SomeException Bool)
 pinRetirement <- try (retirePinStore pins) :: IO (Either SomeException Bool)
 notificationRetirement <- try (retireIssuer notificationIssuer) :: IO (Either SomeException Bool)
 observations <- try $ do
  observed <- bootstrapAuthObservation owner
  trace <- bootstrapCredentialTrace owner
  selected <- bootstrapSelectedPid owner
  count <- readIORef callbacks
  dispatched <- readIORef operations
  pure (observed,trace,selected,count,dispatched)
 (observed,trace,selected,count,dispatched) <- case observations of
  Right values -> pure values
  Left (problem :: SomeException) ->
   if either (const False) id notificationRetirement then throwIO problem
   else case fromException problem :: Maybe SomeAsyncException of
    Just _ -> throwIO (BackendCustodyException problem notificationIssuer)
    Nothing -> throwIO (BackendCustodyFailure problem notificationIssuer)
 let outcome=case attempted of
      Left (_ :: SomeException) -> Left "backend conversation failed"
      Right (Left _) -> Left "backend root acquisition refused"
      Right (Right value) -> Right value
     attemptStage=case attempted of
      Left (_ :: SomeException) -> AttemptConversationException
      Right (Left _) -> AttemptRootRefused
      Right (Right Refused) -> AttemptBootstrapRefused
      Right (Right PendingCustody) -> AttemptPendingCustody
      Right (Right (Executed _)) -> AttemptExecuted
     processClean=either (const False) id processRetirement
     catalogClean=either (const False) id catalogRetirement
     pinClean=either (const False) id pinRetirement
     clean=processClean && catalogClean && pinClean && either (const False) id notificationRetirement
     success=case outcome of
      Right (Executed result) -> selectedCustody result==Available && selectedContainment result==BeforeSignalLeaderExited && either (const False) (const True) (selectedOperation result)
      _ -> False
 let originals=case attempted of Left (problem :: SomeException) -> [problem]; _ -> []
     cleanupProblems=[problem | Left problem <- [processRetirement,catalogRetirement,pinRetirement,notificationRetirement]]
     asynchronous=[problem | problem <- originals++cleanupProblems,Just _ <- [fromException problem :: Maybe SomeAsyncException]]
 -- Every independent owner was attempted before an asynchronous failure can
 -- escape. Prefer the original asynchronous exception over cleanup failures.
 case asynchronous of
  problem:_ -> if either (const False) id notificationRetirement
   then throwIO problem else throwIO (BackendCustodyException problem notificationIssuer)
  [] -> pure ()
 pure (BackendResult (clean && success) clean count dispatched outcome observed trace selected processClean catalogClean pinClean
       attemptStage (retirementStage processRetirement,retirementStage catalogRetirement,retirementStage pinRetirement)
       (if either (const False) id notificationRetirement then Nothing else Just notificationIssuer))

retirementStage :: Either a Bool -> BackendRetirement
retirementStage (Left _) = RetirementException
retirementStage (Right True) = RetirementConfirmed
retirementStage (Right False) = RetirementUnconfirmed

attemptName :: BackendAttemptStage -> Text
attemptName AttemptConversationException = "conversation-exception"
attemptName AttemptRootRefused = "root-acquisition-refused"
attemptName AttemptBootstrapRefused = "bootstrap-refused"
attemptName AttemptPendingCustody = "bootstrap-custody-pending"
attemptName AttemptExecuted = "executed"

retirementName :: BackendRetirement -> Text
retirementName RetirementConfirmed = "confirmed"
retirementName RetirementUnconfirmed = "unconfirmed"
retirementName RetirementException = "exception"

-- Never render ToolError with Show: a closed code and exit status are enough.
operationFailureJson :: ToolError -> Json
operationFailureJson problem = JObject [("code",JString code),("exitCode",exitCode)]
 where
  (code,exitCode) = case problem of
   ToolHashMismatch -> ("tool-hash-mismatch",JNull)
   BadArguments -> ("bad-arguments",JNull)
   SpawnOrIO -> ("spawn-or-io",JNull)
   TimedOut -> ("timed-out",JNull)
   OutputLimit -> ("output-limit",JNull)
   Unsuccessful status -> ("unsuccessful",JNumber (T.pack (show status)))
   CleanupUncertain -> ("cleanup-uncertain",JNull)
   OwnerBusy -> ("owner-busy",JNull)
   OutputUnavailable -> ("output-unavailable",JNull)
   SessionClosed -> ("session-closed",JNull)
   TransferUnavailable -> ("transfer-unavailable",JNull)
   StopAlreadyAttempted -> ("stop-already-attempted",JNull)

-- Ordinary executable diagnostics contain statuses/counts only, never captured
-- UI stdout, catalog content, draft text, pixels or supplied arguments.
backendResultJson :: BackendResult -> B.ByteString
backendResultJson result = TE.encodeUtf8 (renderJson (JObject
 [("schema",JNumber "1"),("passed",JBool (backendPassed result)),("cleanup",JBool (backendCleanup result))
 ,("callbacks",number (backendCallbackCount result)),("operations",number (backendOperationCount result))
 ,("auth",JString (T.pack (show (backendAuthObservation result)))),("credentialRows",number (length (backendCredentialTrace result)))
 ,("selectedPid",maybe JNull (JNumber . T.pack . show) (backendSelectedPid result))
 ,("attempt",JString (attemptName (backendAttemptStage result))),("checks",JObject checks)
 ,("failureStages",JArray [JString name | (name,JBool False) <- checks])
 ,("selectedOperationError",case backendBootstrap result of
    Right (Executed selected) -> either operationFailureJson (const JNull) (selectedOperation selected)
    _ -> JNull)
 ,("selectedObservedExit",case backendBootstrap result of
    Right (Executed selected) -> case selectedObservedExit selected of
     Just code -> JObject [("kind",JString "exit-code-observation"),("trust",JString "untrusted"),
                           ("authority",JBool False),("code",JNumber (T.pack (show code)))]
     Nothing -> JNull
    _ -> JNull)
 ,("retirement",JObject [("process",JString (retirementName processRetirement)),("catalog",JString (retirementName catalogRetirement)),("pins",JString (retirementName pinRetirement))])
 ,("nativeAccepted",JBool False),("releaseAccepted",JBool False)]))
 where
  number = JNumber . T.pack . show
  (processRetirement,catalogRetirement,pinRetirement) = backendRetirements result
  selectedCheck check = case backendBootstrap result of
   Right (Executed selected) -> JBool (check selected)
   _ -> JNull
  checks = [("bootstrapExecuted",JBool (backendAttemptStage result==AttemptExecuted))
           ,("selectedCustodyAvailable",selectedCheck ((==Available) . selectedCustody))
           ,("selectedLeaderExited",selectedCheck ((==BeforeSignalLeaderExited) . selectedContainment))
           ,("selectedOperationSucceeded",selectedCheck (either (const False) (const True) . selectedOperation))
           ,("processCleanup",JBool (backendProcessCleanup result)),("catalogCleanup",JBool (backendCatalogCleanup result)),("pinCleanup",JBool (backendPinCleanup result))]
