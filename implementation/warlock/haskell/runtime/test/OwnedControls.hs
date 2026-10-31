{-# LANGUAGE OverloadedStrings #-}
{-# LANGUAGE ScopedTypeVariables #-}
{-# LANGUAGE RankNTypes #-}
-- Source-only private integration fixture: real sessions and kernel senders.
module OwnedControls (Registry,newRegistry,runOwnedControls,checkCredentialTrace) where
import Control.Concurrent (forkIO)
import Control.Concurrent.MVar (MVar,newEmptyMVar,putMVar,takeMVar)
import Control.Exception (SomeException,mask,try)
import Control.Monad (unless,void)
import qualified Data.ByteString as B
import Data.IORef (IORef,atomicModifyIORef',modifyIORef',newIORef,readIORef,writeIORef)
import Foreign.Ptr (castPtr)
import System.Posix.IO (fdWriteBuf)
import System.Posix.Files (deviceID,fileID,getFdStatus)
import System.Posix.User (getRealUserID,getRealGroupID)
import System.Posix.Process (getProcessID)
import System.Posix.Types (Fd)
import System.Timeout (timeout)
import Warlock.Bootstrap.CurrentSessions
import Warlock.Bootstrap.ScopedPeer (Scope,PeerRefusal(..),withAdmissionAfterAuthenticationForTest)
import Warlock.Bootstrap.SocketOwner
import Warlock.Capture.Process.Bootstrap
import Warlock.Platform.Executable (retireHeld)
import Warlock.Platform.Resolver (Root,Pin,Link,resolvedIdentity)
import Warlock.Platform.Executable (LeaseRole(..),ExecutableLease,newExecutableLease,acquireExecutableLease,issueReadyExecutable)
import Warlock.Protocol.Codec (decodeClientChecked)
import Warlock.Protocol.Ingress (Direction(..),Phase(..),EndpointState(..),phase,endpoint,ingressBinding)
import Warlock.Protocol.CredentialIngress
import Warlock.Protocol.Ingress (Priority(Control))
import Warlock.Bootstrap.CredentialScopeGuard (guardForScopeTracing,CredentialStage(..),CredentialObservation(..))
import Warlock.Protocol.PeerCredential (credentialPid,credentialUid,credentialGid)
import Warlock.Protocol.Framing (prefix)

control :: B.ByteString -> B.ByteString
control session = "{\"version\":1,\"kind\":\"hello\",\"body\":{\"binding\":{\"lifetime\":\"1\",\"session\":\"" <> session <> "\",\"frontend\":\"3\"}}}"
check :: String -> Bool -> IO ()
check msg ok = unless ok (ioError (userError msg))
sendControl :: CredentialIngress -> B.ByteString -> IO ()
sendControl ingress bytes = do
 queued <- enqueueCredentialIngress ingress Control bytes
 check "control enqueue" (queued == Right ())
 sent <- sendCredentialIngress ingress
 check "control send" (sent == Right ())

-- A same-UID parent writes the actual peer FD; recvmsg must report the parent,
-- not the selected child. Small frame is one write; no credential is invented.
foreignWrite :: B.ByteString -> Fd -> IO ()
foreignWrite prepare peer = do
 frame <- either (ioError . userError . show) pure (prefix prepare)
 wrote <- B.useAsCStringLen frame $ \(ptr,n) -> fdWriteBuf peer (castPtr ptr) (fromIntegral n)
 check "foreign complete fixture write" (fromIntegral wrote == B.length frame)

boundedTake :: AdmissionDeadline -> MVar a -> IO a
boundedTake d gate = do
 left <- remainingMicros d
 if left <= 0 then ioError (userError "fixture deadline") else do
  result <- timeout left (takeMVar gate)
  maybe (ioError (userError "fixture synchronization deadline")) pure result

-- Fresh per-case traces must remain below the production truncation boundary.
-- AdmissionObserved records the final admission attempt, not handler success.
checkCredentialTrace :: String -> Integer -> Integer -> Integer -> Bool -> [CredentialObservation] -> IO ()
checkCredentialTrace label pid uid gid admission rows = do
 let identities = [p == pid && u == uid && g == gid | CredentialObservation _ p u g <- rows]
     stages = [stage | CredentialObservation stage _ _ _ <- rows]
     fragments = takeWhile (== FragmentObserved) stages
     expectedTail = if admission then [AdmissionObserved] else []
 check (label ++ " bounded nonempty kernel credential vector") (not (null rows) && length rows < 64 && and identities)
 check (label ++ " fragment/admission ordering")
  (length fragments >= (if admission then 2 else 1) && drop (length fragments) stages == expectedTail)
 putStrLn ("credential_trace " ++ label ++ " " ++ show rows)

sessionPid :: Session -> IO Integer
sessionPid session = toInteger . observedPid <$> (observeSession session >>= either (ioError . userError . show) pure)

assertTrace :: String -> Integer -> Bool -> IORef [CredentialObservation] -> IO ()
assertTrace label pid admission trace = do
 uid <- toInteger <$> getRealUserID
 gid <- toInteger <$> getRealGroupID
 rows <- reverse <$> readIORef trace
 checkCredentialTrace label pid uid gid admission rows

-- Explicit owner retirement, outside all admission locks. Channel also attempts
-- close on frame refusal; this assertion does not diagnose the prior child exit failure.
retireRefusedIngress :: CredentialIngress -> IO ()
retireRefusedIngress ingress = do
 retired <- retireCredentialIngress ingress
 (_,reader) <- credentialIngressStatus ingress
 check "refused ingress retired before waiting child" (phase retired == OwnerRetired && endpoint retired == Just EndpointConfirmed && reader == ReaderReady)

-- Only the test component can name the exact-window hook. Fragment checks use
-- the ordinary traced guard; final admission still authenticates the real peer.
raceGuard :: IORef [CredentialObservation] -> IO () -> Scope -> CredentialGuard PeerRefusal
raceGuard trace afterAuthentication scope = (guardForScopeTracing trace scope)
 { withCredentialAdmission = \credential action -> do
    atomicModifyIORef' trace $ \rows ->
     let next = take 64 (CredentialObservation AdmissionObserved (credentialPid credential) (credentialUid credential) (credentialGid credential) : rows)
         force [] = ()
         force (row:rest) = row `seq` force rest
     in force next `seq` (next,())
    withAdmissionAfterAuthenticationForTest afterAuthentication scope credential action
 }

-- Registry keeps the opaque resources reachable on any uncertain exception.
data Retained = Retained ExecutableLease (IORef (Maybe HeldExecutable)) (IORef (Maybe SocketOwner)) (IORef (Maybe TransferTicket)) (IORef (Maybe Owner)) (IORef (Maybe CredentialIngress))
newtype Registry = Registry (IORef [Retained])
newRegistry :: IO Registry
newRegistry = Registry <$> newIORef []

type Action = Scope -> Fd -> CredentialIngress -> IORef Int -> Session -> IO (Either ToolError ())
withLive :: Registry -> Root -> [Pin] -> B.ByteString -> [Link] -> Integer -> B.ByteString -> AdmissionDeadline -> B.ByteString -> Registration -> Action -> IO ()
withLive = withLiveMode "controlled"

withLiveMode :: String -> Registry -> Root -> [Pin] -> B.ByteString -> [Link] -> Integer -> B.ByteString -> AdmissionDeadline -> B.ByteString -> Registration -> Action -> IO ()
withLiveMode fixtureMode (Registry registry) root pins path links size digest deadline prepare registration action = mask $ \restore -> do
 lease <- newExecutableLease
 heldRef <- newIORef Nothing
 pairRef <- newIORef Nothing
 ticketRef <- newIORef Nothing
 coreRef <- newIORef Nothing
 ingressRef <- newIORef Nothing
 atomicModifyIORef' registry (\items -> (Retained lease heldRef pairRef ticketRef coreRef ingressRef : items,()))
 acquired <- restore (acquireExecutableLease lease root pins path links size digest UiImage)
 either (ioError . userError . show) pure acquired
 issued <- issueReadyExecutable lease
 (held,receipt,role) <- maybe (ioError (userError "selected lease unavailable")) pure issued
 writeIORef heldRef (Just held)
 expected <- either (ioError . userError . show) pure (decodeClientChecked prepare)
 binding <- either (ioError . userError . show) pure (ingressBinding "1" "2" "3")
 calls <- newIORef (0 :: Int)
 ingress <- newCredentialIngress binding FromElm (\client -> do check "checked prepare" (client == expected); modifyIORef' calls (+1)) (\_ -> ioError (userError "wrong handler"))
 writeIORef ingressRef (Just ingress)
 pair <- newSocketOwner
 writeIORef pairRef (Just pair)
 made <- restore (acquireSocketOwner pair)
 check "owned socketpair" made
 core <- newOwner
 writeIORef coreRef (Just core)
 result <- withEndpoints pair ingress $ \peer handle -> do
  ticket <- newTransferTicket handle
  writeIORef ticketRef (Just ticket)
  claimed <- claimTransfer pair
  check "transfer claim" claimed
  selected <- either (ioError . userError . show) pure (selectedHeld held [] ticket [("DEL010_MODE",fixtureMode),("LANG","C")])
  observed <- restore (runSelectedDetailed core selected 1048576 deadline $ \session -> do
   sessionObservation <- observeSession session >>= either (ioError . userError . show) pure
   endpointStat <- getFdStatus peer
   uid <- getRealUserID
   putStrLn ("selected_session=" ++ show sessionObservation ++ " real_uid=" ++ show uid ++ " endpoint_dev=" ++ show (deviceID endpointStat) ++ " endpoint_ino=" ++ show (fileID endpointStat))
   scoped <- withApprovedOwnedPeer registration session peer (resolvedIdentity receipt) role (\scope -> action scope peer ingress calls session)
   case scoped of Left _ -> pure (Left BadArguments); Right value -> pure value)
  pure (observed,ticket)
 (observed,ticket) <- maybe (ioError (userError "endpoint acquisition")) pure result
 check ("normal owned child status: " ++ show observed) (selectedCustody observed == Available && selectedContainment observed == BeforeSignalLeaderExited && either (const False) (const True) (selectedOperation observed))
 disposition <- transferDisposition ticket
 check "ticket core close" (disposition == TransferClosed)
 pairClosed <- retireSocketOwner pair
 pairState <- socketStatus pair
 (ingressState,readerState) <- credentialIngressStatus ingress
 leaseClosed <- retireHeld held
 check "independent socket and executable retirement" (pairClosed && pairState == (True,True,True) && phase ingressState == OwnerRetired && endpoint ingressState == Just EndpointConfirmed && readerState == ReaderReady && either (const False) (const True) leaseClosed)
 putStrLn ("transfer=" ++ show disposition ++ " socket=" ++ show pairState ++ " ingress=" ++ show ingressState ++ " reader=" ++ show readerState ++ " executable=" ++ show leaseClosed)

runOwnedControls :: Registry -> Root -> [Pin] -> B.ByteString -> [Link] -> Integer -> B.ByteString -> AdmissionDeadline -> B.ByteString -> IO ()
runOwnedControls registry root pins path links size digest deadline prepare = do
 single <- newCurrentSessions >>= newRegistration
 withLiveMode "controlled-refusal" registry root pins path links size digest deadline prepare single $ \scope peer ingress calls session -> do
  selectedPid <- sessionPid session
  parentPid <- toInteger <$> getProcessID
  check "foreign fixture differs from selected child" (parentPid /= selectedPid)
  trace <- newIORef []
  foreignWrite prepare peer
  result <- receiveCredentialIngress ingress (guardForScopeTracing trace scope)
  assertTrace "unrelated-parent" parentPid False trace
  count <- readIORef calls
  check "real same-UID parent refusal" (result == CredentialFrameRejected (CredentialPeer ForeignProcess) && count == 0)
  retireRefusedIngress ingress
  awaitLeader session
 authority <- newCurrentSessions
 old <- newRegistration authority
 newer <- newRegistration authority
 oldReady <- newEmptyMVar
 newReady <- newEmptyMVar
 oldDone <- newEmptyMVar
 newDone <- newEmptyMVar
 let oldAction scope _ ingress calls session = do
      pid <- sessionPid session
      trace <- newIORef []
      putMVar oldReady ()
      _ <- boundedTake deadline newReady
      sendControl ingress (control "3")
      result <- receiveCredentialIngress ingress (guardForScopeTracing trace scope)
      assertTrace "replaced-before-read" pid False trace
      n <- readIORef calls
      check "old registration refusal" (n == 0 && case result of CredentialFrameRejected (CredentialPeer ScopeClosed) -> True; CredentialFrameRejected (CredentialPeer ForeignSession) -> True; _ -> False)
      retireRefusedIngress ingress
      awaitLeader session
     newAction scope _ ingress calls session = do
      pid <- sessionPid session
      trace <- newIORef []
      putMVar newReady ()
      oldResult <- boundedTake deadline oldDone
      either (ioError . userError . show) pure oldResult
      sendControl ingress (control "2")
      result <- receiveCredentialIngress ingress (guardForScopeTracing trace scope)
      assertTrace "current-after-replaced-cleanup" pid True trace
      n <- readIORef calls
      check "new registration after old cleanup" (result == CredentialDelivered && n == 1)
      sendControl ingress (control "2")
      awaitLeader session
 _ <- forkIO $ do result <- try (withLive registry root pins path links size digest deadline prepare old oldAction) :: IO (Either SomeException ()); putMVar oldDone result
 _ <- boundedTake deadline oldReady
 _ <- forkIO $ do result <- try (withLive registry root pins path links size digest deadline prepare newer newAction) :: IO (Either SomeException ()); putMVar newDone result
 final <- boundedTake deadline newDone
 either (ioError . userError . show) pure final
 void (retireRegistration old)
 void (retireRegistration newer)

 -- A separate real-child case pauses after successful final authentication,
 -- then publishes a newer approved registration before the old claim executes.
 -- All waits and both selected children use the original controls deadline.
 raceAuthority <- newCurrentSessions
 raceOld <- newRegistration raceAuthority
 raceNew <- newRegistration raceAuthority
 authenticated <- newEmptyMVar
 replacementPublished <- newEmptyMVar
 raceOldDone <- newEmptyMVar
 raceNewDone <- newEmptyMVar
 raceOldPid <- newIORef Nothing
 let pausedOld scope _ ingress calls session = do
      pid <- sessionPid session
      trace <- newIORef []
      sendControl ingress (control "3")
      let pause = do
           putMVar authenticated pid
           _ <- boundedTake deadline replacementPublished
           pure ()
      result <- receiveCredentialIngress ingress (raceGuard trace pause scope)
      assertTrace "replaced-after-auth-before-claim" pid True trace
      n <- readIORef calls
      check "exact admission recheck refuses old child" (result == CredentialAdmissionRejected ScopeClosed && n == 0)
      retireRefusedIngress ingress
      awaitLeader session
     replacing scope _ ingress calls session = do
      pid <- sessionPid session
      oldPid <- readIORef raceOldPid
      check "concurrent selected child identities differ" (Just pid /= oldPid && oldPid /= Nothing)
      trace <- newIORef []
      -- This action runs only after real withApprovedOwnedPeer publication.
      putMVar replacementPublished ()
      oldResult <- boundedTake deadline raceOldDone
      either (ioError . userError . show) pure oldResult
      _ <- retireRegistration raceOld
      sendControl ingress (control "2")
      result <- receiveCredentialIngress ingress (guardForScopeTracing trace scope)
      assertTrace "current-after-exact-race-cleanup" pid True trace
      n <- readIORef calls
      check "new child admitted after exact-race old cleanup" (result == CredentialDelivered && n == 1)
      sendControl ingress (control "2")
      awaitLeader session
 _ <- forkIO $ do
  result <- try (withLive registry root pins path links size digest deadline prepare raceOld pausedOld) :: IO (Either SomeException ())
  putMVar raceOldDone result
 oldPid <- boundedTake deadline authenticated
 writeIORef raceOldPid (Just oldPid)
 _ <- forkIO $ do
  result <- try (withLive registry root pins path links size digest deadline prepare raceNew replacing) :: IO (Either SomeException ())
  putMVar raceNewDone result
 raceFinal <- boundedTake deadline raceNewDone
 either (ioError . userError . show) pure raceFinal
 void (retireRegistration raceOld)
 void (retireRegistration raceNew)
