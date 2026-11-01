{-# LANGUAGE OverloadedStrings #-}
-- Internal adapter. Observation is not a native grant or a process manager.
module Warlock.Bootstrap.Aggregate (BootstrapOwner, BootstrapResult(..), AuthObservation(..), newBootstrapOwner, runBootstrap, runBootstrapWithArguments, bootstrapAuthObservation, bootstrapCredentialTrace, bootstrapSelectedPid, retireBootstrap) where
import Control.Concurrent.MVar
import Control.Concurrent (forkFinally,killThread)
import Control.Exception (Exception,AsyncException(ThreadKilled),SomeException,SomeAsyncException,fromException,mask,mask_,uninterruptibleMask_,onException,throwIO,try,finally)
import qualified Data.ByteString as B
import Data.IORef (IORef,newIORef,readIORef,writeIORef)
import Warlock.Bootstrap.ScopedPeer (PeerRefusal)
import Warlock.Bootstrap.CurrentSessions (CurrentSessions, Registration, newRegistration, withApprovedOwnedPeer, retireRegistration)
import Warlock.Protocol.CredentialIngress (CredentialIngress, CredentialIngressResult(..), CredentialFrameError(CredentialTransport), receiveCredentialIngress, retireCredentialIngress)
import Warlock.Protocol.Ingress (ChannelError(StreamEOF))
import Warlock.Bootstrap.SocketOwner (SocketOwner,newSocketOwner,acquireSocketOwner,withEndpoints,claimTransfer,shutdownPeerWrite,retireSocketOwner)
import Warlock.Capture.Process.Bootstrap (Owner,OwnerStatus(..),SelectedOutcome,AdmissionDeadline,ToolError(..),newOwner,status,selectedHeld,remainingMicros,runSelectedDetailed,awaitLeader,observeSession,observedPid)
import Warlock.Platform.Executable (HeldExecutable,retireHeld,LeaseError(..))
import Warlock.Capture.Process.Bootstrap (TransferTicket,TransferDisposition(..),newTransferTicket,closeCallerTransfer,transferDisposition)
import Warlock.Platform.Resolver (Root,Pin,Link,Resolution(..))
import Warlock.Platform.Executable (LeaseRole(..),ExecutableLease,newExecutableLease,acquireExecutableLease,issueReadyExecutable,retireExecutableLease)
import Warlock.Bootstrap.CredentialScopeGuard (guardForScopeTracing,CredentialObservation)

data Phase = Fresh | Running | Finished | Uncertain
data State = State Phase (Maybe HeldExecutable) (Maybe TransferTicket)
data AuthObservation = EpochRefused | SessionRetired | ScopeRefused PeerRefusal | FrameObserved (CredentialIngressResult PeerRefusal) deriving (Eq,Show)
data BootstrapOwner = BootstrapOwner Owner ExecutableLease SocketOwner (MVar State) (IORef (Maybe AuthObservation)) (IORef [CredentialObservation]) (IORef (Maybe Integer)) Registration
data BootstrapResult = Executed SelectedOutcome | Refused | PendingCustody deriving (Eq,Show)
data LeaderWatchFailure = LeaderWatchFailure ToolError deriving (Show)
instance Exception LeaderWatchFailure
newBootstrapOwner :: CurrentSessions -> IO BootstrapOwner
newBootstrapOwner currentSessions = BootstrapOwner <$> newOwner <*> newExecutableLease <*> newSocketOwner <*> newMVar (State Fresh Nothing Nothing) <*> newIORef Nothing <*> newIORef [] <*> newIORef Nothing <*> newRegistration currentSessions
bootstrapAuthObservation :: BootstrapOwner -> IO (Maybe AuthObservation)
bootstrapAuthObservation (BootstrapOwner _ _ _ _ observation _ _ _) = readIORef observation

-- The one D is supplied before selection and is also the core callback D.
-- Every checked frame uses the same approved scope and original deadline.
-- The exact resolver receipt and owned Session remain scoped to the core callback.
runBootstrap :: BootstrapOwner -> Root -> [Pin] -> B.ByteString -> [Link] -> Integer -> B.ByteString -> AdmissionDeadline -> [(String,String)] -> CredentialIngress -> IO BootstrapResult
runBootstrap owner root pins path links size digest deadline environment ingress =
 runBootstrapWithArguments owner root pins path links size digest [] deadline environment ingress

-- Arguments are selected by the trusted supervisor, never by a wire request.
-- Keep the original entry point, owner, deadline and authentication unchanged.
runBootstrapWithArguments :: BootstrapOwner -> Root -> [Pin] -> B.ByteString -> [Link] -> Integer -> B.ByteString -> [String] -> AdmissionDeadline -> [(String,String)] -> CredentialIngress -> IO BootstrapResult
runBootstrapWithArguments owner@(BootstrapOwner core lease pair state authObservation trace selectedPid admission) root pins path links size digest arguments deadline environment ingress =
 (mask $ \restore -> do
  admitted <- uninterruptibleMask_ $ modifyMVar state $ \s@(State phase held ticket) -> case phase of
    Fresh -> pure (State Running held ticket,True)
    _ -> pure (s,False)
  if not admitted then pure Refused else do
    budget <- remainingMicros deadline
    if budget == 0 then finish Refused else do
      resolved <- acquireExecutableLease lease root pins path links size digest UiImage
      case resolved of
        Left _ -> finish Refused
        Right () -> do
          moved <- issueReadyExecutable lease
          case moved of
            Nothing -> poison >> pure PendingCustody
            Just (held,receipt,role) -> do
              uninterruptibleMask_ $ modifyMVar_ state $ \(State phase _ ticket) -> pure (State phase (Just held) ticket)
              left <- remainingMicros deadline
              if left == 0 then finish Refused else do
                made <- acquireSocketOwner pair
                if not made then finish Refused else do
                  outcome <- withEndpoints pair ingress $ \peer input -> do
                    -- Under the enclosing mask publish the ticket before the
                    -- pair relinquishes its only Handle close right.
                    ticket <- newTransferTicket input
                    uninterruptibleMask_ $ modifyMVar_ state $ \(State phase current _) -> pure (State phase current (Just ticket))
                    movedTransfer <- claimTransfer pair
                    if not movedTransfer then poison >> pure PendingCustody else
                      case selectedHeld held arguments ticket environment of
                        Left _ -> finish Refused
                        Right plan -> do
                          result <- try (restore (runSelectedDetailed core plan 1048576 deadline $ \session -> do
                            identity <- observeSession session
                            case identity of
                              Left reason -> pure (Left reason)
                              Right observation -> do
                                writeIORef selectedPid (Just (toInteger (observedPid observation)))
                                scoped <- withApprovedOwnedPeer admission session peer (resolvedIdentity receipt) role $ \scope -> do
                                  let guard = guardForScopeTracing trace scope
                                      pump delivered = do
                                        frame <- receiveCredentialIngress ingress guard
                                        case frame of
                                          CredentialDelivered -> do
                                            writeIORef authObservation (Just (FrameObserved frame))
                                            pump True
                                          CredentialFrameRejected (CredentialTransport StreamEOF) | delivered -> pure True
                                          _ -> do
                                            writeIORef authObservation (Just (FrameObserved frame))
                                            pure False
                                  withLeaderExit session (pump False)
                                case scoped of
                                  Left reason -> writeIORef authObservation (Just (ScopeRefused reason)) >> refuseAfterExit session
                                  Right (Left err) -> retireCredentialIngress ingress >> pure (Left err)
                                  Right (Right True) -> awaitLeader session
                                  Right (Right False) -> refuseAfterExit session))
                            :: IO (Either SomeException SelectedOutcome)
                          case result of
                            Left e -> do
                              poison
                              case fromException e :: Maybe SomeAsyncException of Just _ -> throwIO e; Nothing -> pure ()
                              pure PendingCustody
                            Right observed -> finish (Executed observed)
                  maybe (finish Refused) pure outcome)
 `onException` retainOnException owner
 where
  finish value = uninterruptibleMask_ $ modifyMVar_ state (\(State _ held ticket) -> pure (State Finished held ticket)) >> pure value
  poison = uninterruptibleMask_ $ modifyMVar_ state (\(State _ held ticket) -> pure (State Uncertain held ticket))
  refuseAfterExit session = do
    _ <- retireCredentialIngress ingress
    exited <- awaitLeader session
    pure $ case exited of Left err -> Left err; Right () -> Left BadArguments
  -- Observe the already-owned leader without reaping it. The retained peer FD
  -- prevents EOF even after the child's own FD closes, so only this independent
  -- exit observation may end its write direction. Main admission stays on the
  -- Scope's original thread; no Scope or credential guard enters the watcher.
  withLeaderExit session action = mask $ \restore -> do
    completion <- newEmptyMVar
    watcher <- forkFinally (restore (do
      exited <- awaitLeader session
      case exited of
        Left err -> pure (Left err)
        Right () -> do
          ended <- shutdownPeerWrite pair
          if ended then pure (Right ()) else ioError (userError "owned peer write-end shutdown unconfirmed"))) (putMVar completion)
    let cleanup = do
          before <- tryReadMVar completion
          let stopping = case before of Nothing -> True; Just _ -> False
              join deferred = do
                waited <- try (killThread watcher >> readMVar completion) :: IO (Either SomeException (Either SomeException (Either ToolError ())))
                case waited of
                  Left err -> join (case deferred of Nothing -> Just err; other -> other)
                  Right result -> case deferred of
                    Just err -> throwIO err
                    Nothing -> case result of
                      Left err | stopping && (fromException err :: Maybe AsyncException) == Just ThreadKilled -> pure ()
                      Left err -> throwIO err
                      Right (Left err) -> throwIO (LeaderWatchFailure err)
                      Right (Right ()) -> pure ()
          join Nothing
    result <- try (restore action `finally` cleanup) :: IO (Either LeaderWatchFailure Bool)
    pure $ case result of Left (LeaderWatchFailure err) -> Left err; Right value -> Right value

-- Preserve the original exception; leave every aggregate owner reachable.
retainOnException :: BootstrapOwner -> IO ()
retainOnException (BootstrapOwner _ _ _ state _ _ _ _) = mask_ $
  uninterruptibleMask_ $ modifyMVar_ state $ \(State _ held ticket) -> pure (State Uncertain held ticket)

-- Guarded ticket operation, never status-then-raw-hClose. Core ownership or
-- uncertainty retains the entire aggregate and does not grant cleanup rights.
retireBootstrap :: BootstrapOwner -> IO Bool
retireBootstrap (BootstrapOwner core lease pair state _ _ _ admission) = mask_ $ do
  _ <- retireRegistration admission
  (phase,held,ticket) <- do State p h t <- readMVar state; pure (p,h,t)
  -- While Running, the pair may still own the Handle and the ticket may
  -- already exist. Never close a ticket before the handoff has completed.
  -- Uncertain handoffs retain both references and permit no guessed close.
  case phase of
    Finished -> retireFinished held ticket
    _ -> pure False
 where
  retireFinished held ticket = do
   current <- status core
   if current /= Available then pure False else do
    guarded <- case ticket of
      Nothing -> pure True
      Just t -> do
        result <- closeCallerTransfer t
        case result of
          Right () -> pure True
          Left _ -> do disposition <- transferDisposition t; pure (disposition == TransferClosed)
    if not guarded then pure False else do
      pairResult <- try (retireSocketOwner pair) :: IO (Either SomeException Bool)
      leaseResult <- fmap (fmap leaseSettled) $ case held of
        Nothing -> try (retireExecutableLease lease)
        Just h -> try (retireHeld h)
      let yes (Right True) = True; yes _ = False
          errors = [e | Left e <- [pairResult,leaseResult], Just _ <- [fromException e :: Maybe SomeAsyncException]]
      case errors of e:_ -> throwIO e; [] -> pure (yes pairResult && yes leaseResult)

-- Already-closed is settled; busy and uncertain never certify retirement.
leaseSettled :: Either LeaseError () -> Bool
leaseSettled (Right ()) = True
leaseSettled (Left LeaseClosed) = True
leaseSettled (Left LeaseBusy) = False
leaseSettled (Left LeaseCloseUncertain) = False

-- Bounded, read-only observations, independent of approval and physical effects.
bootstrapCredentialTrace :: BootstrapOwner -> IO [CredentialObservation]
bootstrapCredentialTrace (BootstrapOwner _ _ _ _ _ observations _ _) = reverse <$> readIORef observations

-- Retained observation only: no Session, signal right, or authentication grant.
bootstrapSelectedPid :: BootstrapOwner -> IO (Maybe Integer)
bootstrapSelectedPid (BootstrapOwner _ _ _ _ _ _ selectedPid _) = readIORef selectedPid
