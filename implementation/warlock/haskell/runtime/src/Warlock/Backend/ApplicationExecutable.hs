{-# LANGUAGE ScopedTypeVariables #-}
-- Internal backend producer. Image plans are startup DATA, not admission.
-- Only a current admitted, authenticated Scope can acquire or run an image.
module Warlock.Backend.ApplicationExecutable
 ( ApplicationIssuer,ApplicationImage,ApplicationPlan,ApplicationError(..)
 ,ApplicationRetirement(..),ApplicationFailure(..),ApplicationAsyncFailure(..)
 ,applicationPlan,newApplicationIssuer,issueApplicationImage,runApplicationImage
 ,retireApplicationIssuer,settleApplicationImage,applicationReceipt ) where
import Control.Concurrent (ThreadId,myThreadId)
import Control.Concurrent.MVar
import Control.Exception
import qualified Crypto.Hash.SHA256 as SHA
import qualified Data.ByteString as B
import qualified Data.ByteString.Char8 as C
import Data.IORef
import Data.Text (Text)
import qualified Data.Text as T
import qualified Data.Text.Encoding as TE
import Data.Unique (Unique,newUnique)
import Numeric (showHex)
import Warlock.Bootstrap.ScopedPeer (Scope,PeerRefusal,withCurrentAdmission,claimApplicationProducer,scopeApplicationContext)
import Warlock.Protocol.PeerCredential (PeerCredential)
import Warlock.Protocol.Identity (Binding,Counter,lifetime)
import qualified Warlock.Backend.Catalog as Catalog
import Warlock.Platform.Resolver (Identity,Pin,Link,withRoot,resolveSnapshot)
import Warlock.Platform.Executable
 ( ExecutableLease,HeldExecutable,LeaseError(..),LeaseState(ClosedLease)
 ,newExecutableLease,acquireApplicationExecutableLease,issueReadyExecutable
 ,retireExecutableLease,executableLeaseState )
import Warlock.Capture.Process.Bootstrap
 (AdmissionDeadline,remainingMicros,Owner,OwnerStatus(..),newOwner,status
 ,SelectedOutcome,selectedHeldNoInput,runSelectedDetailed,awaitLeader)

data ApplicationPlan = ApplicationPlan Text B.ByteString B.ByteString [String]
 B.ByteString Identity [Pin] B.ByteString [Link] Integer B.ByteString
-- source id, exact desktop SHA256/Exec, approved argv (excluding argv0),
-- pinned executable root/path/links/size/digest. No environment PATH search.
data ApplicationError = AdmissionRefused PeerRefusal | WrongOwnerThread
 | DeadlineExpired | IssuerClosed | IssuerBusy | ReplayRefused | SourceRefused
 | ImageUnconfigured | TerminalUnavailable | AcquisitionRefused | ImageNotReady
 | ForeignImage | ImageAlreadyUsed | RevalidationRefused | SpawnRefused | EffectUnconfirmed
 deriving (Eq,Show)
data Phase = Acquiring | Issued | Running | Observed | Uncertain
 deriving Eq
data Attempt = Attempt Unique Counter ExecutableLease Owner ApplicationPlan
 Catalog.ResolvedDesktop (Maybe HeldExecutable) Phase
data IssuerState = IssuerState Bool (Maybe Counter) (Maybe Attempt) (Maybe (Counter,SelectedOutcome))
data ApplicationIssuer = ApplicationIssuer Unique ThreadId Scope AdmissionDeadline
 Binding Catalog.Catalog [ApplicationPlan] Int (MVar ()) (MVar IssuerState)
-- Diagnostic equality compares the real retained issuer identity only.
instance Eq ApplicationIssuer where
 ApplicationIssuer a _ _ _ _ _ _ _ _ _ == ApplicationIssuer b _ _ _ _ _ _ _ _ _ = a==b
instance Show ApplicationIssuer where show _ = "<opaque application issuer>"
data ApplicationImage = ApplicationImage Unique Unique Counter HeldExecutable (IORef Bool)
data ApplicationRetirement = ApplicationRetired | ApplicationRetained ApplicationIssuer
-- Both failures retain the actual owner. Async classification is preserved.
data ApplicationFailure = ApplicationFailure SomeException ApplicationIssuer
data ApplicationAsyncFailure = ApplicationAsyncFailure SomeException ApplicationIssuer
instance Show ApplicationFailure where show _ = "application operation failed; owner retained"
instance Show ApplicationAsyncFailure where show _ = "application operation interrupted; owner retained"
instance Exception ApplicationFailure
instance Exception ApplicationAsyncFailure where
 toException = asyncExceptionToException
 fromException = asyncExceptionFromException

hex :: B.ByteString -> B.ByteString
hex = C.pack . concatMap (\n -> let s=showHex n "" in if length s==1 then '0':s else s) . B.unpack
validHash :: B.ByteString -> Bool
validHash value = B.length value==64 && B.all (\c -> c>=48 && c<=57 || c>=97 && c<=102) value

-- Package-internal startup-data validation, never an endpoint/action factory.
-- A configured exact Exec/argv mapping is the narrow walking-skeleton policy;
-- general desktop expansion is a separate producer and cannot be assumed here.
applicationPlan :: Text -> B.ByteString -> B.ByteString -> [String]
 -> B.ByteString -> Identity -> [Pin] -> B.ByteString -> [Link] -> Integer
 -> B.ByteString -> Either ApplicationError ApplicationPlan
applicationPlan entry sourceHash rawExec args root identity pins path links size digest =
 if T.null entry || T.length entry>256 || T.any (< ' ') entry || B.length rawExec>262144 || B.null rawExec || B.elem 0 rawExec || not (validHash sourceHash)
  || any (elem '\0') args || length args>4096 || sum (map (B.length . TE.encodeUtf8 . T.pack) args)>262144
  || B.null root || B.head root/=47 || B.elem 0 root || B.length root>4096
  || B.null path || B.head path==47 || B.elem 0 path || B.length path>4096 || length pins>16384
  || length links>40 || size<0 || size>67108864 || not (validHash digest)
 then Left ImageUnconfigured
 else Right (ApplicationPlan entry sourceHash rawExec args root identity pins path links size digest)

newApplicationIssuer :: Scope -> PeerCredential
 -> Catalog.Catalog -> [ApplicationPlan] -> Int
 -> IO (Either ApplicationError ApplicationIssuer)
newApplicationIssuer scope credential catalog plans cap = do
 original <- scopeApplicationContext scope
 case original of
  Nothing -> pure (Left DeadlineExpired)
  Just (deadline,binding) -> create deadline binding
 where
  create deadline binding = do
   remaining <- remainingMicros deadline
   if remaining==0 then pure (Left DeadlineExpired)
   else if cap<=0 || cap>4194304 || length plans>2048 then pure (Left ImageUnconfigured)
   else do
    claimed <- claimApplicationProducer scope credential
    case claimed of
     Left reason -> pure (Left (AdmissionRefused reason))
     Right () -> do
      result <- withCurrentAdmission scope credential $ do
       remainingAgain <- remainingMicros deadline
       if remainingAgain==0 then pure (Left DeadlineExpired) else do
        identity <- newUnique
        thread <- myThreadId
        lock <- newMVar ()
        state <- newMVar (IssuerState False Nothing Nothing Nothing)
        pure (Right (ApplicationIssuer identity thread scope deadline binding catalog plans cap lock state))
      pure (either (Left . AdmissionRefused) id result)
withOperation :: ApplicationIssuer -> PeerCredential -> IO (Either ApplicationError a)
 -> IO (Either ApplicationError a)
withOperation issuer@(ApplicationIssuer _ thread scope deadline _ _ _ _ lock state) credential action =
 handle (retainFailure issuer) $ mask $ \restore -> do
  current <- myThreadId
  if current/=thread then pure (Left WrongOwnerThread) else do
   active <- withCurrentAdmission scope credential $ do
    remaining <- remainingMicros deadline
    closed <- withMVar state (\(IssuerState stop _ _ _) -> pure stop)
    if remaining==0 then pure (Left DeadlineExpired) else if closed then pure (Left IssuerClosed) else do
     available <- tryTakeMVar lock
     case available of
      Nothing -> pure (Left IssuerBusy)
      Just () -> restore action `finally` putMVar lock ()
   pure (either (Left . AdmissionRefused) id active)

retainFailure :: ApplicationIssuer -> SomeException -> IO a
retainFailure issuer@(ApplicationIssuer _ _ _ _ _ _ _ _ _ state) problem = do
 modifyMVar_ state $ \(IssuerState _ frontier attempt journal) ->
  pure (IssuerState True frontier (fmap uncertain attempt) journal)
 case fromException problem :: Maybe SomeAsyncException of
  Just _ -> throwIO (ApplicationAsyncFailure problem issuer)
  Nothing -> throwIO (ApplicationFailure problem issuer)
 where
  uncertain (Attempt ident request lease owner plan source held _) =
   Attempt ident request lease owner plan source held Uncertain

issueApplicationImage :: ApplicationIssuer -> PeerCredential -> Binding -> Counter
 -> Counter -> Text -> IO (Either ApplicationError ApplicationImage)
issueApplicationImage issuer@(ApplicationIssuer identity _ _ deadline binding catalog plans _ _ state)
 credential requested request generation entry = withOperation issuer credential $ do
 if requested/=binding then pure (Left SourceRefused) else do
  reserved <- modifyMVar state $ \old@(IssuerState stop frontier active journal) ->
   if stop || maybe False (request<=) frontier || maybe False (const True) active
   then pure (old,False)
   else pure (IssuerState False (Just request) Nothing journal,True)
  if not reserved then pure (Left ReplayRefused) else do
   resolved <- Catalog.resolveDesktop catalog (lifetime binding) generation entry
   issueResolved resolved
 where
  issueResolved resolved = case resolved of
   Left _ -> pure (Left SourceRefused)
   Right source | not (terminalAllowed (Catalog.resolvedTerminal source)) -> pure (Left TerminalUnavailable)
   Right source -> case [p | p@(ApplicationPlan name sourceHash rawExec _ _ _ _ _ _ _ _) <- plans,
     name==entry, sourceHash==hex (SHA.hash (Catalog.resolvedBytes source)), rawExec==Catalog.resolvedExec source] of
    [plan] -> do
     lease <- newExecutableLease
     owner <- newOwner
     ticket <- newUnique
     admitted <- modifyMVar state $ \old@(IssuerState stop frontier current journal) ->
      if stop || frontier/=Just request || maybe False (const True) current
      then pure (old,False)
      else pure (IssuerState False (Just request) (Just (Attempt ticket request lease owner plan source Nothing Acquiring)) journal,True)
     if not admitted then pure (Left ReplayRefused) else do
      acquired <- acquire plan lease
      remaining <- remainingMicros deadline
      case acquired of
       False -> do
        -- Failed resolution can already have confirmed close. This attempt
        -- has no returned image handle; release ONLY confirmed no-resource
        -- custody now under the existing operation lock. Keep the frontier.
        leaseStatus <- executableLeaseState lease
        ownerStatus <- status owner
        if leaseStatus==ClosedLease && ownerStatus==Available
         then clearAttempt state ticket
         else pure ()
        pure (Left AcquisitionRefused)
       True | remaining==0 -> pure (Left DeadlineExpired)
       True -> do
        result <- issueReadyExecutable lease
        case result of
         Just (held,_,_) -> do
          modifyMVar_ state $ \(IssuerState stop frontier attempt journal) ->
           pure (IssuerState stop frontier (fmap (setHeld held) attempt) journal)
          closed <- withMVar state (\(IssuerState stop _ _ _) -> pure stop)
          if closed then pure (Left IssuerClosed) else do
           used <- newIORef False
           pure (Right (ApplicationImage identity ticket request held used))
         _ -> pure (Left ImageNotReady)
    _ -> pure (Left ImageUnconfigured)
  terminalAllowed value = T.null value || T.toLower value==T.pack "false"
  setHeld held (Attempt ticket number lease owner plan source _ _) = Attempt ticket number lease owner plan source (Just held) Issued

acquire :: ApplicationPlan -> ExecutableLease -> IO Bool
acquire (ApplicationPlan _ _ _ _ root identity pins path links size digest) lease = do
 result <- withRoot root identity $ \heldRoot ->
  acquireApplicationExecutableLease lease heldRoot pins path links size digest
 pure $ case result of Right (Right ()) -> True; _ -> False

revalidate :: ApplicationPlan -> IO Bool
revalidate (ApplicationPlan _ _ _ _ root identity pins path links size digest) = do
 result <- withRoot root identity $ \heldRoot -> resolveSnapshot heldRoot pins path links size 67108864 digest
 pure $ case result of Right (Right _) -> True; _ -> False

runApplicationImage :: ApplicationIssuer -> PeerCredential -> ApplicationImage
 -> IO (Either ApplicationError SelectedOutcome)
runApplicationImage issuer@(ApplicationIssuer identity _ _ deadline binding catalog _ cap _ state)
 credential (ApplicationImage original ticket request held used) = withOperation issuer credential $ do
 if original/=identity then pure (Left ForeignImage) else do
  attempt <- withMVar state $ \(IssuerState _ _ value _) -> pure value
  case attempt of
   Just (Attempt ident number _ owner plan@(ApplicationPlan _ _ _ args _ _ _ _ _ _ _) source _ Issued)
    | ident==ticket && number==request -> do
     consumed <- atomicModifyIORef' used (\old -> (True,old))
     if consumed then pure (Left ImageAlreadyUsed) else do
      fresh <- Catalog.resolveDesktop catalog (lifetime binding) (Catalog.resolvedGeneration source) (Catalog.resolvedIdentity source)
      stable <- revalidate plan
      remaining <- remainingMicros deadline
      case fresh of
       Right current | Catalog.resolvedBytes current==Catalog.resolvedBytes source && stable && remaining>0 ->
        case selectedHeldNoInput held args [("LANG","C.UTF-8"),("LC_ALL","C.UTF-8")] of
         Left _ -> pure (Left SpawnRefused)
         Right selected -> do
          modifyMVar_ state (\(IssuerState stop frontier a journal) -> pure (IssuerState stop frontier (fmap (phase Running) a) journal))
          observed <- runSelectedDetailed owner selected cap deadline awaitLeader
          modifyMVar_ state (\(IssuerState stop frontier a _) -> pure (IssuerState stop frontier (fmap (phase Observed) a) (Just (request,observed))))
          remainingAfter <- remainingMicros deadline
          closedAfter <- withMVar state (\(IssuerState stop _ _ _) -> pure stop)
          if remainingAfter==0 || closedAfter then pure (Left EffectUnconfirmed)
          else pure (Right observed)
       _ -> pure (Left RevalidationRefused)
   _ -> pure (Left ForeignImage)
 where
  phase next (Attempt ident number lease owner plan source executable _) = Attempt ident number lease owner plan source executable next

-- Cleanup is independent of admission/deadline. Closed is published first;
-- busy/uncertain child or held-close retains the whole actual issuer, not a Bool.
retireApplicationIssuer :: ApplicationIssuer -> IO ApplicationRetirement
retireApplicationIssuer issuer@(ApplicationIssuer _ _ _ _ _ _ _ _ _ state) = mask_ $ do
 modifyMVar_ state (\(IssuerState _ frontier attempt journal) -> pure (IssuerState True frontier attempt journal))
 settle issuer

settleApplicationImage :: ApplicationIssuer -> ApplicationImage -> IO ApplicationRetirement
settleApplicationImage issuer@(ApplicationIssuer identity _ _ _ _ _ _ _ _ state)
 (ApplicationImage original ticket request _ _) = mask_ $ do
 matching <- withMVar state $ \(IssuerState _ _ active _) -> pure $ case active of
  Just (Attempt ident number _ _ _ _ _ _) -> original==identity && ident==ticket && number==request
  Nothing -> original==identity
 if matching then settle issuer else pure (ApplicationRetained issuer)

settle :: ApplicationIssuer -> IO ApplicationRetirement
settle issuer@(ApplicationIssuer _ _ _ _ _ _ _ _ lock state) = mask_ $ do
 available <- tryTakeMVar lock
 case available of
  Nothing -> pure (ApplicationRetained issuer)
  Just () -> (do
   attempt <- withMVar state (\(IssuerState _ _ value _) -> pure value)
   case attempt of
    Nothing -> pure ApplicationRetired
    Just (Attempt _ _ lease owner _ _ _ _) -> do
     actual <- status owner
     if actual/=Available then pure (ApplicationRetained issuer) else do
      result <- try (retireExecutableLease lease) :: IO (Either SomeException (Either LeaseError ()))
      case result of
       Right (Right ()) -> do
        modifyMVar_ state (\(IssuerState stop frontier _ journal) -> pure (IssuerState stop frontier Nothing journal))
        pure ApplicationRetired
       Right (Left LeaseClosed) -> do
        confirmed <- executableLeaseState lease
        if confirmed==ClosedLease then do
         modifyMVar_ state (\(IssuerState stop frontier _ journal) -> pure (IssuerState stop frontier Nothing journal))
         pure ApplicationRetired
        else pure (ApplicationRetained issuer)
       Right (Left _) -> pure (ApplicationRetained issuer)
       Left (problem :: SomeException) -> case fromException problem :: Maybe SomeAsyncException of
        Just _ -> throwIO (ApplicationAsyncFailure problem issuer)
        Nothing -> throwIO (ApplicationFailure problem issuer)) `finally` putMVar lock ()

-- Bounded retained receipt, not permission to replay a native action.
applicationReceipt :: ApplicationIssuer -> IO (Maybe (Counter,SelectedOutcome))
applicationReceipt (ApplicationIssuer _ _ _ _ _ _ _ _ _ state) =
 withMVar state (\(IssuerState _ _ _ journal) -> pure journal)

-- Only the operation that owns the actual attempt may discard its confirmed
-- resource-free cell. No request frontier, stop flag, receipt or Scope slot is
-- reset, and this helper is not exported as an action or authority factory.
clearAttempt :: MVar IssuerState -> Unique -> IO ()
clearAttempt state ticket = modifyMVar_ state $ \old@(IssuerState stop frontier current journal) ->
 case current of
  Just (Attempt actual _ _ _ _ _ _ _) | actual==ticket ->
   pure (IssuerState stop frontier Nothing journal)
  _ -> pure old
