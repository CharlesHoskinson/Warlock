{-# LANGUAGE CPP #-}
{-# LANGUAGE OverloadedStrings #-}
{-# LANGUAGE RankNTypes #-}
{-# LANGUAGE ScopedTypeVariables #-}
-- Package-private persistent process-custody implementation aligned with
-- contract 951861, terra_q_lifetime_app_owner, and terra_q_lifetime_frame_admission.
-- Single custody owner from creation through callback/wake/observation drain
-- and direct leader reap; never wraps runSelectedDetailed, never renews an
-- AdmissionDeadline, never guesses peer exit from socket EOF, and claims
-- neither descendant namespace containment nor provider cleanup.
module Warlock.Capture.Process.Persistent.Internal
 ( PersistentOwner
 , PersistentStatus(..)
 , PidfdCustody(..)
 , PersistentSpawn
 , persistentHeld
 , persistentHeldNoInput
 , persistentFixture
 , persistentTicketFixture
 , StartBudget
 , startBudgetFromDeadline
 , startBudgetAfter
 , startBudgetDeadline
 , StopBudget
 , stopBudgetMicros
 , stopBudgetMicrosValue
 , ActionBudget
 , maxPersistentActionBudgetMicros
 , defaultPersistentActionBudget
 , actionBudgetMicros
 , actionBudgetMicrosValue
 , LiveSession
 , LiveWakeReason(..)
 , LiveWaitOutcome(..)
 , LiveFrameAdmission
 , LiveFrameBatch
 , maxLiveFrameBatchRequests
 , LiveOperationFailure(..)
 , StopReceipt(..)
 , StopDeadlineObservation(..)
 , tryPersistentStopDeadline
 , SessionExit(..)
 , newPersistentOwner
 , persistentStatus
 , persistentPidfdCustody
 , persistentUnderlyingStatus
 , withPersistentOwner
 , withPersistentOwnerHook
 , borrowReleasedReceipt
 , awaitLiveSessionStopOrExit
 , liveSessionStopRequestedSTM
 , withLiveSessionWakeSTM
 , withLiveFrameAdmission
 , enterLiveFrameAction
 , beginLiveFrameBatch
 , beginLiveFrameRequestBatch
 , enterLiveBatchAttachmentRequest
 , enterLiveBatchAttachment
 , enterLiveBatchRequest
 , enterLiveBatchBudgetedAction
 , observeLiveStartup
 , observeLiveSession
 , runBoundedLiveOperation
 , requestSessionStop
 ) where

import Control.Concurrent (ThreadId, forkFinally, killThread)
import Control.Concurrent.MVar (MVar, isEmptyMVar, modifyMVar, modifyMVar_, newEmptyMVar, newMVar, putMVar, readMVar, tryPutMVar, tryReadMVar, tryTakeMVar, withMVar)
import Control.Exception (IOException, SomeAsyncException, SomeException, bracket, finally, fromException, mask, mask_, onException, throwIO, try)
import Control.Monad (unless, void, when)
import qualified Data.ByteString as B
import Data.IORef (IORef, atomicModifyIORef', newIORef, readIORef, writeIORef)
import Data.Text (Text)
import qualified Data.Text as T
import Foreign.C.Error (eSRCH, getErrno)
import Foreign.Ptr (nullPtr)
import GHC.Conc (STM, TVar, atomically, newTVarIO, orElse, readTVar, retry, threadWaitReadSTM, writeTVar)
import System.Exit (ExitCode)
import System.IO (Handle, hClose)
import System.Posix.Files (FileStatus, deviceID, fileID, getFdStatus)
import System.Posix.IO (closeFd)
import System.Posix.Signals (sigKILL, sigTERM)
import System.Posix.Types (Fd(..), ProcessID)
import System.Process (CreateProcess(..), ProcessHandle, StdStream(..), createProcess_, getPid, getProcessExitCode, proc, waitForProcess)
import System.Timeout (timeout)
import Warlock.Capture.Process.Internal
 ( AdmissionDeadline
 , Captured(..)
 , ReaderResult
 , SessionObservation(..)
 , SessionScope
 , ToolError(..)
 , c_getpgid
 , c_kill
 , c_pidfd_open
 , c_pidfd_send_signal
 , capAdmissionDeadline
 , closeSessionScope
 , deadlineAbsoluteNs
 , deadlineAfter
 , drainSessionScope
 , inScope
 , leaderExited
 , newSessionScope
 , observeChild
 , pidfdNonblockFlags
 , remainingMicros
 , spawnReader
 , startupAction
 )
import Warlock.Capture.Process.Lease (HeldExecutable)
import Warlock.Platform.Executable (prepareHeldBorrow, activateHeldBorrowWhile, tryReleaseHeld)
import Text.Read (readMaybe)
import qualified Warlock.Capture.Process.Owner as O
import Warlock.Capture.Process.Transfer (TransferTicket)
import Warlock.Capture.Process.Transfer.Internal
 ( TransferError(DeadlineExpired)
 , claimTransferWhen
 , closeCoreTransfer
 , coreCloseDiagnostic
 , coreHandle
 , newOwnerToken
 )

data PersistentInput = FixtureHandle Handle | TransferInput TransferTicket

data PersistentSpawn = PersistentSpawn FilePath [String] (Maybe PersistentInput) [(String, String)] (Maybe HeldExecutable)

-- Startup admission must finish before the caller's original AdmissionDeadline
-- (for example 28s, constructor-capped at <= 30s). Zero implicit grace is added.
newtype StartBudget = StartBudget AdmissionDeadline deriving (Eq, Show)

startBudgetFromDeadline :: AdmissionDeadline -> StartBudget
startBudgetFromDeadline = StartBudget

startBudgetAfter :: Int -> IO (Either ToolError StartBudget)
startBudgetAfter micros = fmap StartBudget <$> deadlineAfter micros

startBudgetDeadline :: StartBudget -> AdmissionDeadline
startBudgetDeadline (StartBudget d) = d

-- Explicit stop window (1..30_000_000 us) minted once into a single absolute
-- AdmissionDeadline at the first stop event (including stop-during-starting);
-- shared across drain, signal, reap, pidfd close and pipe close so StopBudget
-- is never multiplied or re-minted across sub-steps.
newtype StopBudget = StopBudget Int deriving (Eq, Show)

stopBudgetMicros :: Int -> Either ToolError StopBudget
stopBudgetMicros micros
 | micros <= 0 || micros > 30000000 = Left BadArguments
 | otherwise = Right (StopBudget micros)

stopBudgetMicrosValue :: StopBudget -> Int
stopBudgetMicrosValue (StopBudget micros) = micros

-- Trusted caller-configured per-action budget (1..5_000_000 us per Root
-- persistent-request-budget-decision.json), fixed at supervisor setup and
-- never constructed from untrusted wire input. At admission of each distinct
-- attachment/request, the owner mints one fresh immutable AdmissionDeadline
-- intersected with any stricter existing deadline and passes it lexically.
newtype ActionBudget = ActionBudget Int deriving (Eq, Show)

maxPersistentActionBudgetMicros :: Int
maxPersistentActionBudgetMicros = 5000000

defaultPersistentActionBudget :: ActionBudget
defaultPersistentActionBudget = ActionBudget maxPersistentActionBudgetMicros

actionBudgetMicros :: Int -> Either ToolError ActionBudget
actionBudgetMicros micros
 | micros <= 0 || micros > maxPersistentActionBudgetMicros = Left BadArguments
 | otherwise = Right (ActionBudget micros)

actionBudgetMicrosValue :: ActionBudget -> Int
actionBudgetMicrosValue (ActionBudget micros) = micros

data PersistentStatus
 = PersistentAvailable
 | PersistentStarting
 | PersistentLive
 | PersistentStopping
 | PersistentRetired
 | PersistentQuarantined [Text]
 deriving (Eq, Show)

data SpawnPhase = SpawnUnreserved | SpawnReserved
 deriving (Eq, Show)

-- Single-MVar owner-level admission gate + one-shot sticky stop-deadline state
-- + atomic pre-spawn reservation. Created in newPersistentOwner so
-- requestSessionStop in PhaseAvailable or PhaseStarting latches the immutable
-- StopDeadline once without losing stop or racing pre-spawn checks.
data GateState = GateState
 !(Maybe (Either ToolError AdmissionDeadline))
 !(Maybe Int)
 !Bool
 !SpawnPhase
 !Int
 ![MVar ()]

newtype CallbackGate = CallbackGate (MVar GateState)

newCallbackGate :: IO CallbackGate
newCallbackGate = CallbackGate <$> newMVar (GateState Nothing Nothing False SpawnUnreserved 0 [])

setGateStopCap :: CallbackGate -> Int -> IO (Maybe (Either ToolError AdmissionDeadline))
setGateStopCap (CallbackGate gateVar) capMicros = modifyMVar gateVar $ \(GateState mStop mCap attempted spawnPh activeCount waiters) ->
 let nextCap = Just (maybe capMicros (min capMicros) mCap)
 in pure (GateState mStop nextCap attempted spawnPh activeCount waiters, mStop)

peekGateStop :: CallbackGate -> IO (Maybe (Either ToolError AdmissionDeadline))
peekGateStop (CallbackGate gateVar) = withMVar gateVar $ \(GateState mStop _ _ _ _ _) -> pure mStop

peekGateAttempted :: CallbackGate -> IO Bool
peekGateAttempted (CallbackGate gateVar) = withMVar gateVar $ \(GateState _ _ attempted _ _ _) -> pure attempted

-- A contended stop gate is uncertain; never wait beyond the original StartD.
tryPeekPreSpawnStop :: CallbackGate -> IO (Either ToolError (Maybe (Either ToolError AdmissionDeadline)))
tryPeekPreSpawnStop (CallbackGate gateVar) = do
 snapshot <- tryReadMVar gateVar
 pure $ case snapshot of
  Nothing -> Left OwnerBusy
  Just (GateState mStop _ _ _ _ _) -> Right mStop

-- Reserve under the same gate as stop, but only while the original StartD
-- still has time remaining.  The clock sample and state update are masked;
-- no external callback or spawn runs while the gate is held.
tryReserveSpawnUnderGate :: CallbackGate -> AdmissionDeadline -> IO (Either ToolError (Maybe (Either ToolError AdmissionDeadline)))
tryReserveSpawnUnderGate (CallbackGate gateVar) startDl = mask_ $ do
 taken <- tryTakeMVar gateVar
 case taken of
  Nothing -> pure (Left OwnerBusy)
  Just st@(GateState mStop mCap attempted spawnPh activeCount waiters) -> do
   (next, result) <- (case mStop of
    Just latched -> pure (st, Right (Just latched))
    Nothing -> case spawnPh of
     SpawnReserved -> pure (st, Left OwnerBusy)
     SpawnUnreserved -> do
      left <- remainingMicros startDl
      if left <= 0 then pure (st, Left TimedOut)
       else pure (GateState Nothing mCap attempted SpawnReserved activeCount waiters, Right Nothing))
    `onException` putMVar gateVar st
   putMVar gateVar next
   pure result

closeCallbackGate :: CallbackGate -> TVar Bool -> MVar () -> IO ()
closeCallbackGate (CallbackGate gateVar) stopReadyVar stopBell = modifyMVar_ gateVar $ \(GateState mStop mCap attempted spawnPh activeCount waiters) -> do
 let nextStop = case mStop of
      Just existing -> Just existing
      Nothing -> Just (Left SessionClosed)
 atomically (writeTVar stopReadyVar True)
 void (tryPutMVar stopBell ())
 if activeCount == 0 then do
  mapM_ (\w -> void (tryPutMVar w ())) waiters
  pure (GateState nextStop mCap attempted spawnPh 0 [])
 else
  pure (GateState nextStop mCap attempted spawnPh activeCount waiters)

admitCallback :: CallbackGate -> IO Bool
admitCallback (CallbackGate gateVar) = modifyMVar gateVar $ \st@(GateState mStop mCap attempted spawnPh activeCount waiters) ->
 case mStop of
  Nothing -> pure (GateState Nothing mCap attempted spawnPh (activeCount + 1) waiters, True)
  Just _ -> pure (st, False)

-- Atomically checks that CallbackGate is still open (no stop), verifies both
-- frameDl and actionDl remain positive, and increments activeCount by +1 for
-- the entered action itself so even an overlapping/forked action that outlives
-- withLiveFrameAdmission's outer callback holds CallbackGate until completion.
admitFrameActionAttempt
 :: CallbackGate
 -> AdmissionDeadline
 -> AdmissionDeadline
 -> IO (Either ToolError Int)
admitFrameActionAttempt (CallbackGate gateVar) frameDl actionDl =
 modifyMVar gateVar $ \st@(GateState mStop mCap attempted spawnPh activeCount waiters) ->
  case mStop of
   Just _ -> pure (st, Left SessionClosed)
   Nothing -> do
    remFrame <- remainingMicros frameDl
    remAction <- remainingMicros actionDl
    if remFrame <= 0 || remAction <= 0 then
     pure (st, Left TimedOut)
    else
     pure (GateState Nothing mCap attempted spawnPh (activeCount + 1) waiters, Right remAction)

-- Atomically checks that CallbackGate remains open (no stop) and that the
-- action's own immutable AdmissionDeadline remains positive after frame batch
-- admission has already validated Channel's frameDl on entry.
admitBatchActionAttempt
 :: CallbackGate
 -> AdmissionDeadline
 -> IO (Either ToolError Int)
admitBatchActionAttempt (CallbackGate gateVar) actionDl =
 modifyMVar gateVar $ \st@(GateState mStop mCap attempted spawnPh activeCount waiters) ->
  case mStop of
   Just _ -> pure (st, Left SessionClosed)
   Nothing -> do
    remAction <- remainingMicros actionDl
    if remAction <= 0 then
     pure (st, Left TimedOut)
    else
     pure (GateState Nothing mCap attempted spawnPh (activeCount + 1) waiters, Right remAction)

releaseCallback :: CallbackGate -> IO ()
releaseCallback (CallbackGate gateVar) = modifyMVar_ gateVar $ \(GateState mStop mCap attempted spawnPh activeCount waiters) ->
 let nextCount = max 0 (activeCount - 1)
 in case mStop of
     Just _ | nextCount == 0 -> do
      mapM_ (\w -> void (tryPutMVar w ())) waiters
      pure (GateState mStop mCap attempted spawnPh 0 [])
     _ ->
      pure (GateState mStop mCap attempted spawnPh nextCount waiters)

drainCallbackGate :: CallbackGate -> IO ()
drainCallbackGate (CallbackGate gateVar) = do
 maybeWaiter <- modifyMVar gateVar $ \(GateState mStop mCap attempted spawnPh activeCount waiters) ->
  let closedStop = case mStop of
       Just existing -> Just existing
       Nothing -> Just (Left SessionClosed)
  in if activeCount == 0 then do
      mapM_ (\w -> void (tryPutMVar w ())) waiters
      pure (GateState closedStop mCap attempted spawnPh 0 [], Nothing)
     else do
      w <- newEmptyMVar
      pure (GateState closedStop mCap attempted spawnPh activeCount (w : waiters), Just w)
 case maybeWaiter of
  Nothing -> pure ()
  Just w -> readMVar w

-- Linearizes first-stop monotonic deadline sampling atomically with closing
-- CallbackGate admission, setting stopReadyVar, and ringing stopBell under
-- CallbackGate's single MVar. Sticky on Left err so no fresh D can be minted.
beginStopGateAndDeadline :: CallbackGate -> TVar Bool -> MVar () -> Int -> IO (Either ToolError AdmissionDeadline)
beginStopGateAndDeadline (CallbackGate gateVar) stopReadyVar stopBell reqMicros =
 modifyMVar gateVar $ \(GateState mStop mCap attempted spawnPh activeCount waiters) -> do
  let effectiveMicros = maybe reqMicros (min reqMicros) mCap
  chosen <- case mStop of
   Just existing -> pure existing
   Nothing -> deadlineAfter effectiveMicros
  atomically (writeTVar stopReadyVar True)
  void (tryPutMVar stopBell ())
  if activeCount == 0 then do
   mapM_ (\w -> void (tryPutMVar w ())) waiters
   pure (GateState (Just chosen) mCap attempted spawnPh 0 [], chosen)
  else
   pure (GateState (Just chosen) mCap attempted spawnPh activeCount waiters, chosen)

-- Claims the one-shot explicit requestSessionStop flag atomically with minting
-- or reusing the sticky StopDeadline under CallbackGate's single MVar.
claimExplicitStop :: CallbackGate -> TVar Bool -> MVar () -> Int -> IO (Bool, Either ToolError AdmissionDeadline)
claimExplicitStop (CallbackGate gateVar) stopReadyVar stopBell reqMicros =
 modifyMVar gateVar $ \(GateState mStop mCap attempted spawnPh activeCount waiters) -> do
  let effectiveMicros = maybe reqMicros (min reqMicros) mCap
  chosen <- case mStop of
   Just existing -> pure existing
   Nothing -> deadlineAfter effectiveMicros
  atomically (writeTVar stopReadyVar True)
  void (tryPutMVar stopBell ())
  if activeCount == 0 then do
   mapM_ (\w -> void (tryPutMVar w ())) waiters
   pure (GateState (Just chosen) mCap True spawnPh 0 [], (attempted, chosen))
  else
   pure (GateState (Just chosen) mCap True spawnPh activeCount waiters, (attempted, chosen))

claimStoppingAttemptFlag :: CallbackGate -> IO Bool
claimStoppingAttemptFlag (CallbackGate gateVar) =
 modifyMVar gateVar $ \(GateState mStop mCap attempted spawnPh activeCount waiters) ->
  pure (GateState mStop mCap True spawnPh activeCount waiters, attempted)

-- Tracks active withLiveSessionWakeSTM registrations on the owned pidfd so
-- finishContainment never closes pidfd before GHC's epoll unregistration drains.
data WakeState = WakeState !Bool !Int ![MVar ()]

newtype WakeGate = WakeGate (MVar WakeState)

newWakeGate :: IO WakeGate
newWakeGate = WakeGate <$> newMVar (WakeState True 0 [])

admitWake :: WakeGate -> IO Bool
admitWake (WakeGate wgVar) = modifyMVar wgVar $ \st@(WakeState open activeCount waiters) ->
 if open then pure (WakeState True (activeCount + 1) waiters, True)
 else pure (st, False)

releaseWake :: WakeGate -> IO ()
releaseWake (WakeGate wgVar) = modifyMVar_ wgVar $ \(WakeState open activeCount waiters) ->
 let nextCount = max 0 (activeCount - 1)
 in if not open && nextCount == 0 then do
     mapM_ (\w -> void (tryPutMVar w ())) waiters
     pure (WakeState False 0 [])
    else
     pure (WakeState open nextCount waiters)

closeWakeGate :: WakeGate -> IO ()
closeWakeGate (WakeGate wgVar) = modifyMVar_ wgVar $ \(WakeState _ activeCount waiters) ->
 if activeCount == 0 then do
  mapM_ (\w -> void (tryPutMVar w ())) waiters
  pure (WakeState False 0 [])
 else
  pure (WakeState False activeCount waiters)

drainWakeGate :: WakeGate -> IO ()
drainWakeGate (WakeGate wgVar) = do
 maybeWaiter <- modifyMVar wgVar $ \(WakeState _ activeCount waiters) ->
  if activeCount == 0 then do
   mapM_ (\w -> void (tryPutMVar w ())) waiters
   pure (WakeState False 0 [], Nothing)
  else do
   w <- newEmptyMVar
   pure (WakeState False activeCount (w : waiters), Just w)
 case maybeWaiter of
  Nothing -> pure ()
  Just w -> readMVar w

-- Public audit-only pidfd custody projection retained on PersistentOwner across
-- quarantine. Never exports a raw numeric Fd so external callers cannot close
-- or signal a descriptor whose close disposition is uncertain.
data PidfdCustody
 = PidfdUnopened
 | PidfdKnownOpen !ProcessID !(Maybe O.FDIdentity)
 | PidfdClosing !ProcessID !(Maybe O.FDIdentity)
 | PidfdClosed
 | PidfdCloseUncertain !ProcessID !(Maybe O.FDIdentity) !Text
 deriving (Eq, Show)

data InternalPidfdState
 = InternalPidfdUnopened
 | InternalPidfdKnownOpen !Fd !ProcessID !(Maybe O.FDIdentity)
 | InternalPidfdClosing !ProcessID !(Maybe O.FDIdentity)
 | InternalPidfdClosed
 | InternalPidfdCloseUncertain !ProcessID !(Maybe O.FDIdentity) !Text

projectPidfdCustody :: InternalPidfdState -> PidfdCustody
projectPidfdCustody st = case st of
 InternalPidfdUnopened -> PidfdUnopened
 InternalPidfdKnownOpen _ pid ident -> PidfdKnownOpen pid ident
 InternalPidfdClosing pid ident -> PidfdClosing pid ident
 InternalPidfdClosed -> PidfdClosed
 InternalPidfdCloseUncertain pid ident detail -> PidfdCloseUncertain pid ident detail

data ActiveHandle = ActiveHandle
 { activeScope :: SessionScope
 , activePid :: ProcessID
 , activePidfdCell :: IORef InternalPidfdState
 , activeInitialObs :: SessionObservation
 , activeStopMicros :: Int
 , activeHook :: String -> IO ()
 }

data OwnerPhase
 = PhaseAvailable
 | PhaseStarting
 | PhaseLive ActiveHandle
 | PhaseStopping
 | PhaseRetired
 | PhaseQuarantined [Text]

data PersistentOwner = PersistentOwner O.Owner (MVar OwnerPhase) CallbackGate (TVar Bool) (MVar ()) (IORef InternalPidfdState) (IORef (IO Bool))

-- Snapshot only. Busy and not-yet-latched are never cleanup authority; even a
-- latched D is not a receipt that any resource or callback retired. It is the
-- exact sticky deadline already minted by this owner, never a new budget.
data StopDeadlineObservation
 = StopDeadlineBusy
 | StopDeadlineNotLatched
 | StopDeadlineFailed ToolError
 | StopDeadlineLatched AdmissionDeadline
 deriving (Eq, Show)

tryPersistentStopDeadline :: PersistentOwner -> IO StopDeadlineObservation
tryPersistentStopDeadline (PersistentOwner _ _ (CallbackGate gate) _ _ _ _) = do
 snapshot <- tryReadMVar gate
 pure $ case snapshot of
  Nothing -> StopDeadlineBusy
  Just (GateState Nothing _ _ _ _ _) -> StopDeadlineNotLatched
  Just (GateState (Just (Left err)) _ _ _ _ _) -> StopDeadlineFailed err
  Just (GateState (Just (Right deadline)) _ _ _ _ _) -> StopDeadlineLatched deadline

data LiveWakeReason
 = LiveWakeStopRequested
 | LiveWakeLeaderExited
 | LiveWakeScopeExited
 deriving (Eq, Show)

data LiveWaitOutcome
 = LiveStopRequested
 | LiveLeaderExited
 | LiveOutputFault ToolError
 | LiveScopeClosed
 deriving (Eq, Show)

-- Per-frame state lock (acquired BEFORE CallbackGate's MVar; zero cycle)
-- serializing frame-scope exit against one-shot enterLiveFrameAction and
-- bounded serial LiveFrameBatch admission (optional 1 attachment + 0..16
-- ordered requests) so every entered action holds CallbackGate until completion
-- and one-shot vs batch modes stay disjoint.
data FrameMode
 = FrameModeUnused
 | FrameModeOneShotUsed
 | FrameModeBatch !Bool !Int !Bool !Bool
 deriving (Eq, Show)

data FrameState = FrameState !Bool !FrameMode

-- Private lexical frame-admission token minted only inside withLiveFrameAdmission
-- after idle readiness and before Channel mints its 5s FrameDeadline.
data LiveFrameAdmission = LiveFrameAdmission
 !(MVar FrameState)
 !CallbackGate
 !SessionScope
 !ProcessID
 !SessionObservation
 !(TVar Bool)
 !(String -> IO ())

-- Opaque bounded per-frame batch admission capability minted at most once per
-- LiveFrameAdmission by beginLiveFrameBatch / beginLiveFrameRequestBatch after
-- validating frameDl and live peer.
newtype LiveFrameBatch = LiveFrameBatch LiveFrameAdmission

maxLiveFrameBatchRequests :: Int
maxLiveFrameBatchRequests = 16

tryAny :: IO b -> IO (Either SomeException b)
tryAny = try

-- Wrapper-owned classification: callbacks accept IO (Either ToolError a) and
-- cannot forge OperationRefusedPreDispatch. Once Entered, any Left, timeout,
-- stop, actionD expiry, or sync IO fault maps to OperationOutcomeUnknown.
data LiveOperationFailure
 = OperationRefusedPreDispatch ToolError
 | OperationOutcomeUnknown ToolError
 deriving (Eq, Show)

-- StopLatchedBeforeLive reports that stop was latched in PhaseAvailable or
-- PhaseStarting with an immutable one-shot StopDeadline before any live session
-- was published; no SIGTERM was sent yet and liveBody will never be entered.
data StopReceipt
 = StopSignalSent
 | StopLeaderAlreadyExited
 | StopLatchedBeforeLive
 | StopAlreadyRequested
 | StopNoLiveSession
 | StopUncertain ToolError
 deriving (Eq, Show)

-- LeaderReaped proves direct owned child leader reap + pidfd/pipe closure only;
-- claims neither PID-namespace descendant containment nor provider cleanup.
data SessionExit
 = LeaderReaped Captured
 | StartupRefused ToolError
 | ExitUncertain ToolError [Text]
 deriving (Eq, Show)

data LiveSession = LiveSession
 { liveWaitAction :: IO LiveWaitOutcome
 , liveStopReadySTM :: STM ()
 , liveWakeScopeAction :: forall a. (STM LiveWakeReason -> IO a) -> IO (Either ToolError a)
 , liveFrameAdmissionAction :: forall a. (LiveFrameAdmission -> IO a) -> IO (Either ToolError a)
 , liveObserveStartupAction :: IO (Either ToolError SessionObservation)
 , liveObserveAction :: AdmissionDeadline -> IO (Either ToolError SessionObservation)
 , liveBoundedAction :: forall a. AdmissionDeadline -> IO (Either ToolError a) -> IO (Either LiveOperationFailure a)
 }

awaitLiveSessionStopOrExit :: LiveSession -> IO LiveWaitOutcome
awaitLiveSessionStopOrExit s = liveWaitAction s

-- Monotonic owner stop/retirement latch (GHC.Conc in base). Observes owner stop
-- only; inter-frame socket idle must use withLiveSessionWakeSTM so child death
-- also wakes even while SocketOwner retains a duplicate peer fd0.
liveSessionStopRequestedSTM :: LiveSession -> STM ()
liveSessionStopRequestedSTM s = liveStopReadySTM s

-- Scoped owner stop + verified-pidfd child-death STM wake. Holds a WakeGate pin
-- across GHC epoll registration/unregistration so the private pidfd is never
-- closed before threadWaitReadSTM unregisters, and wakes immediately on
-- EXIT_ZOMBIE even when SocketOwner retains a duplicate peer descriptor.
withLiveSessionWakeSTM :: LiveSession -> (STM LiveWakeReason -> IO a) -> IO (Either ToolError a)
withLiveSessionWakeSTM s = liveWakeScopeAction s

-- Atomically claims CallbackGate after socket readiness and before Channel mints
-- its 5s FrameDeadline (no pre-idle deadline minted). Retains active admission
-- across SCM fragment checks and optional single enterLiveFrameAction.
withLiveFrameAdmission :: LiveSession -> (LiveFrameAdmission -> IO a) -> IO (Either ToolError a)
withLiveFrameAdmission s = liveFrameAdmissionAction s

-- Enters at most one bounded mutation inside an active LiveFrameAdmission.
-- Both frameDl (Channel's frame admission deadline) and actionDl (immutable
-- action deadline) must be unexpired at entry; once Entered, actionDl and owner
-- stop govern completion and any post-entry failure/expiry/stop yields
-- OperationOutcomeUnknown (matching terra_q_lifetime_frame_admission.qnt).
--
-- Kernel-exit linearization contract: pre-entry synchronous waitid(WNOHANG|WNOWAIT)
-- + /proc birth/exe verification rejects an already-exited peer with
-- OperationRefusedPreDispatch SessionClosed. Because kernel child exit is an
-- asynchronous OS transition that no user-space mutex can block, a peer exit
-- after that pre-entry sample linearizes as a concurrent/in-flight exit
-- (ChildExitDuringExecution -> OperationOutcomeUnknown). A synchronous
-- post-action owned-liveness check ensures Right val is never returned if the
-- owned peer exited in that interval or during act.
enterLiveFrameAction
 :: forall a.
    LiveFrameAdmission
 -> AdmissionDeadline
 -> AdmissionDeadline
 -> IO (Either ToolError a)
 -> IO (Either LiveOperationFailure a)
enterLiveFrameAction (LiveFrameAdmission frameStateVar cbGate scope pid expectedObs stopReadyVar hook) frameDl actionDl act =
 mask $ \restore -> do
  FrameState isOpen0 mode0 <- readMVar frameStateVar
  if not isOpen0 then pure (Left (OperationRefusedPreDispatch SessionClosed))
  else if mode0 /= FrameModeUnused then pure (Left (OperationRefusedPreDispatch OwnerBusy))
  else do
   -- Synchronous kernel waitid + /proc birth/exe check under SessionScope (never
   -- inferred from absence of async GHC event-manager pidfd readiness).
   liveCheck <- inScope scope frameDl $ do
    exited <- leaderExited pid
    if exited then pure (Right True) else do
     obsNow <- observeChild frameDl pid
     pure $ case obsNow of
      Right currentObs | currentObs == expectedObs -> Right False
      Right _ -> Left SpawnOrIO
      Left err -> Left err
   case liveCheck of
    Left err -> pure (Left (OperationRefusedPreDispatch err))
    Right True -> pure (Left (OperationRefusedPreDispatch SessionClosed))
    Right False -> do
     entered <- modifyMVar frameStateVar $ \st@(FrameState isOpen mode) ->
      if not isOpen then
       pure (st, Left SessionClosed)
      else if mode /= FrameModeUnused then
       pure (st, Left OwnerBusy)
      else do
       admittedAct <- admitFrameActionAttempt cbGate frameDl actionDl
       case admittedAct of
        Left preErr -> pure (st, Left preErr)
        Right _ -> pure (FrameState True FrameModeOneShotUsed, Right ())
     case entered of
      Left preErr -> pure (Left (OperationRefusedPreDispatch preErr))
      Right () ->
       finally
        (do
          hook "persistent-before-action-timeout"
          stoppedBeforeTimeout <- atomically (readTVar stopReadyVar)
          freshActionBudget <- remainingMicros actionDl
          if stoppedBeforeTimeout then
           pure (Left (OperationOutcomeUnknown SessionClosed))
          else if freshActionBudget <= 0 then
           pure (Left (OperationOutcomeUnknown TimedOut))
          else do
           ran <- tryAny (restore (timeout freshActionBudget (hook "persistent-callback-dispatched" >> act)))
           afterAction <- remainingMicros actionDl
           stoppedAfter <- atomically (readTVar stopReadyVar)
           case ran of
            Left ex -> case fromException ex :: Maybe SomeAsyncException of
             Just _ -> throwIO ex
             Nothing -> pure (Left (OperationOutcomeUnknown SpawnOrIO))
            Right Nothing -> pure (Left (OperationOutcomeUnknown TimedOut))
            Right (Just _) | stoppedAfter -> pure (Left (OperationOutcomeUnknown SessionClosed))
            Right (Just _) | afterAction <= 0 -> pure (Left (OperationOutcomeUnknown TimedOut))
            Right (Just (Left callbackErr)) -> pure (Left (OperationOutcomeUnknown callbackErr))
            Right (Just (Right val)) -> do
             postLive <- inScope scope actionDl $ do
              exitedAfter <- leaderExited pid
              if exitedAfter then pure (Right True) else do
               obsAfter <- observeChild actionDl pid
               pure $ case obsAfter of
                Right currentObs | currentObs == expectedObs -> Right False
                Right _ -> Left SpawnOrIO
                Left err -> Left err
             finalBudget <- remainingMicros actionDl
             stoppedFinal <- atomically (readTVar stopReadyVar)
             pure $ case postLive of
              _ | stoppedFinal -> Left (OperationOutcomeUnknown SessionClosed)
              _ | finalBudget <= 0 -> Left (OperationOutcomeUnknown TimedOut)
              Left err -> Left (OperationOutcomeUnknown err)
              Right True -> Left (OperationOutcomeUnknown SessionClosed)
              Right False -> Right val)
        (releaseCallback cbGate)

poisonBatchFrameState :: MVar FrameState -> IO ()
poisonBatchFrameState frameStateVar =
 modifyMVar_ frameStateVar $ \st@(FrameState isOpen mode) ->
  pure $ case mode of
   FrameModeBatch attPend remReqs inFlight _ -> FrameState isOpen (FrameModeBatch attPend remReqs inFlight True)
   _ -> st

beginLiveFrameBatchInternal
 :: LiveFrameAdmission
 -> AdmissionDeadline
 -> Bool
 -> Int
 -> IO (Either ToolError LiveFrameBatch)
beginLiveFrameBatchInternal adm@(LiveFrameAdmission frameStateVar cbGate scope pid expectedObs stopReadyVar _) frameDl allowAttachment remQuota =
 mask $ \restore -> do
  FrameState isOpen0 mode0 <- readMVar frameStateVar
  if not isOpen0 then pure (Left SessionClosed)
  else if mode0 /= FrameModeUnused then pure (Left OwnerBusy)
  else do
   stopped0 <- atomically (readTVar stopReadyVar)
   remFrame0 <- remainingMicros frameDl
   if stopped0 then pure (Left SessionClosed)
   else if remFrame0 <= 0 then pure (Left TimedOut)
   else do
    liveCheck <- restore $ inScope scope frameDl $ do
     exited <- leaderExited pid
     if exited then pure (Right True) else do
      obsNow <- observeChild frameDl pid
      pure $ case obsNow of
       Right currentObs | currentObs == expectedObs -> Right False
       Right _ -> Left SpawnOrIO
       Left err -> Left err
    case liveCheck of
     Left err -> pure (Left err)
     Right True -> pure (Left SessionClosed)
     Right False ->
      modifyMVar frameStateVar $ \st@(FrameState isOpen mode) ->
       if not isOpen then
        pure (st, Left SessionClosed)
       else if mode /= FrameModeUnused then
        pure (st, Left OwnerBusy)
       else do
        latched <- peekGateStop cbGate
        remFrame <- remainingMicros frameDl
        case latched of
         Just _ -> pure (st, Left SessionClosed)
         Nothing | remFrame <= 0 -> pure (st, Left TimedOut)
         Nothing ->
          pure (FrameState True (FrameModeBatch allowAttachment remQuota False False), Right (LiveFrameBatch adm))

-- Claims bounded serial no-attachment request admission (0..16 checked
-- DesktopCommit requests ONLY; 17+ refused) once for an open LiveFrameAdmission
-- before Channel's frameDl expires, mutually exclusive with enterLiveFrameAction
-- and any second batch claim.
beginLiveFrameBatch
 :: LiveFrameAdmission
 -> AdmissionDeadline
 -> Int
 -> IO (Either ToolError LiveFrameBatch)
beginLiveFrameBatch adm frameDl requestQuota =
 beginLiveFrameRequestBatch adm frameDl False requestQuota

-- Claims bounded serial multi-action admission with an explicit separate
-- initial-attachment boolean and 0..16 checked DesktopCommit request quota
-- (16 requests + 1 attachment is the ONLY 17-step case).
beginLiveFrameRequestBatch
 :: LiveFrameAdmission
 -> AdmissionDeadline
 -> Bool
 -> Int
 -> IO (Either ToolError LiveFrameBatch)
beginLiveFrameRequestBatch adm frameDl allowAttachment requestQuota
 | requestQuota < 0 || requestQuota > maxLiveFrameBatchRequests = pure (Left BadArguments)
 | otherwise = beginLiveFrameBatchInternal adm frameDl allowAttachment requestQuota

runBatchStepWithBudget
 :: forall a.
    Bool
 -> LiveFrameBatch
 -> ActionBudget
 -> Maybe AdmissionDeadline
 -> (AdmissionDeadline -> IO (Either ToolError a))
 -> IO (Either LiveOperationFailure a)
runBatchStepWithBudget isAttachment (LiveFrameBatch (LiveFrameAdmission frameStateVar cbGate scope pid expectedObs stopReadyVar hook)) (ActionBudget micros) mStricterDl actWithDl =
 mask $ \restore -> do
  preCheck <- modifyMVar frameStateVar $ \st@(FrameState isOpen mode) ->
   if not isOpen then
    pure (st, Left SessionClosed)
   else case mode of
    FrameModeBatch attPend remReqs inFlight poisoned
     | poisoned -> pure (st, Left SessionClosed)
     | inFlight -> pure (FrameState isOpen (FrameModeBatch attPend remReqs True True), Left OwnerBusy)
     | isAttachment && not attPend -> pure (st, Left OwnerBusy)
     | not isAttachment && attPend -> pure (FrameState isOpen (FrameModeBatch True remReqs False True), Left OwnerBusy)
     | not isAttachment && remReqs <= 0 -> pure (st, Left OwnerBusy)
     | otherwise -> pure (st, Right ())
    _ -> pure (st, Left OwnerBusy)
  case preCheck of
   Left preErr -> pure (Left (OperationRefusedPreDispatch preErr))
   Right () -> do
    stopped0 <- atomically (readTVar stopReadyVar)
    if stopped0 then do
     poisonBatchFrameState frameStateVar
     pure (Left (OperationRefusedPreDispatch SessionClosed))
    else do
     dlRes <- deadlineAfter micros
     case dlRes of
      Left preErr -> do
       poisonBatchFrameState frameStateVar
       pure (Left (OperationRefusedPreDispatch preErr))
      Right mintedDl -> do
       let actionDl = maybe mintedDl (capAdmissionDeadline mintedDl) mStricterDl
       remAct0 <- remainingMicros actionDl
       if remAct0 <= 0 then do
        poisonBatchFrameState frameStateVar
        pure (Left (OperationRefusedPreDispatch TimedOut))
       else do
        liveCheck <- restore $ inScope scope actionDl $ do
         exited <- leaderExited pid
         if exited then pure (Right True) else do
          obsNow <- observeChild actionDl pid
          pure $ case obsNow of
           Right currentObs | currentObs == expectedObs -> Right False
           Right _ -> Left SpawnOrIO
           Left err -> Left err
        case liveCheck of
         Left err -> do
          poisonBatchFrameState frameStateVar
          pure (Left (OperationRefusedPreDispatch err))
         Right True -> do
          poisonBatchFrameState frameStateVar
          pure (Left (OperationRefusedPreDispatch SessionClosed))
         Right False -> do
          -- Allocate succeededRef BEFORE incrementing cbGate activeCount or
          -- setting inFlight=True so finally wraps admission with zero gap.
          succeededRef <- newIORef False
          entered <- modifyMVar frameStateVar $ \st@(FrameState isOpen mode) ->
           if not isOpen then
            pure (st, Left SessionClosed)
           else case mode of
            FrameModeBatch attPend remReqs inFlight poisoned
             | poisoned -> pure (st, Left SessionClosed)
             | inFlight -> pure (FrameState isOpen (FrameModeBatch attPend remReqs True True), Left OwnerBusy)
             | isAttachment && not attPend -> pure (st, Left OwnerBusy)
             | not isAttachment && attPend -> pure (FrameState isOpen (FrameModeBatch True remReqs False True), Left OwnerBusy)
             | not isAttachment && remReqs <= 0 -> pure (st, Left OwnerBusy)
             | otherwise -> do
                admittedAct <- admitBatchActionAttempt cbGate actionDl
                case admittedAct of
                 Left preErr ->
                  pure (FrameState isOpen (FrameModeBatch attPend remReqs False True), Left preErr)
                 Right _ ->
                  let nextMode =
                       if isAttachment then FrameModeBatch False remReqs True False
                       else FrameModeBatch False (remReqs - 1) True False
                  in pure (FrameState True nextMode, Right ())
            _ -> pure (st, Left OwnerBusy)
          case entered of
           Left preErr -> pure (Left (OperationRefusedPreDispatch preErr))
           Right () ->
            finally
             (do
               hook "persistent-before-action-timeout"
               stoppedBeforeTimeout <- atomically (readTVar stopReadyVar)
               freshActionBudget <- remainingMicros actionDl
               if stoppedBeforeTimeout then
                pure (Left (OperationOutcomeUnknown SessionClosed))
               else if freshActionBudget <= 0 then
                pure (Left (OperationOutcomeUnknown TimedOut))
               else do
                ran <- tryAny (restore (timeout freshActionBudget (hook "persistent-callback-dispatched" >> actWithDl actionDl)))
                afterAction <- remainingMicros actionDl
                stoppedAfter <- atomically (readTVar stopReadyVar)
                case ran of
                 Left ex -> case fromException ex :: Maybe SomeAsyncException of
                  Just _ -> throwIO ex
                  Nothing -> pure (Left (OperationOutcomeUnknown SpawnOrIO))
                 Right Nothing -> pure (Left (OperationOutcomeUnknown TimedOut))
                 Right (Just _) | stoppedAfter -> pure (Left (OperationOutcomeUnknown SessionClosed))
                 Right (Just _) | afterAction <= 0 -> pure (Left (OperationOutcomeUnknown TimedOut))
                 Right (Just (Left callbackErr)) -> pure (Left (OperationOutcomeUnknown callbackErr))
                 Right (Just (Right val)) -> do
                  postLive <- inScope scope actionDl $ do
                   exitedAfter <- leaderExited pid
                   if exitedAfter then pure (Right True) else do
                    obsAfter <- observeChild actionDl pid
                    pure $ case obsAfter of
                     Right currentObs | currentObs == expectedObs -> Right False
                     Right _ -> Left SpawnOrIO
                     Left err -> Left err
                  finalBudget <- remainingMicros actionDl
                  stoppedFinal <- atomically (readTVar stopReadyVar)
                  case postLive of
                   _ | stoppedFinal -> pure (Left (OperationOutcomeUnknown SessionClosed))
                   _ | finalBudget <= 0 -> pure (Left (OperationOutcomeUnknown TimedOut))
                   Left err -> pure (Left (OperationOutcomeUnknown err))
                   Right True -> pure (Left (OperationOutcomeUnknown SessionClosed))
                   Right False -> do
                    writeIORef succeededRef True
                    pure (Right val))
             (do
               ok <- readIORef succeededRef
               modifyMVar_ frameStateVar $ \st@(FrameState isOpen mode) ->
                pure $ case mode of
                 FrameModeBatch attPend remReqs _ alreadyPoisoned ->
                  FrameState isOpen (FrameModeBatch attPend remReqs False (alreadyPoisoned || not ok))
                 _ -> st
               releaseCallback cbGate)

-- Admits the optional single initial attachment reply before any request in a
-- beginLiveFrameRequestBatch frame, minting one immutable <=5s owner
-- AdmissionDeadline intersected with any stricter applicable authority deadline
-- and passing that exact deadline lexically to the pinned sender.
enterLiveBatchAttachmentRequest
 :: forall a.
    LiveFrameBatch
 -> ActionBudget
 -> Maybe AdmissionDeadline
 -> (AdmissionDeadline -> IO (Either ToolError a))
 -> IO (Either LiveOperationFailure a)
enterLiveBatchAttachmentRequest batch budget mStricterDl actWithDl =
 runBatchStepWithBudget True batch budget mStricterDl actWithDl

enterLiveBatchAttachment
 :: forall a.
    LiveFrameBatch
 -> ActionBudget
 -> (AdmissionDeadline -> IO (Either ToolError a))
 -> IO (Either LiveOperationFailure a)
enterLiveBatchAttachment batch budget actWithDl =
 runBatchStepWithBudget True batch budget Nothing actWithDl

-- Admits one serial request action after any scheduled attachment has
-- completed, minting one immutable <=5s owner AdmissionDeadline intersected
-- with any stricter applicable authority deadline and passing that exact
-- deadline lexically to the request handler and pinned reply sender.
enterLiveBatchRequest
 :: forall a.
    LiveFrameBatch
 -> ActionBudget
 -> Maybe AdmissionDeadline
 -> (AdmissionDeadline -> IO (Either ToolError a))
 -> IO (Either LiveOperationFailure a)
enterLiveBatchRequest batch budget mStricterDl actWithDl =
 runBatchStepWithBudget False batch budget mStricterDl actWithDl

enterLiveBatchBudgetedAction
 :: forall a.
    LiveFrameBatch
 -> ActionBudget
 -> (AdmissionDeadline -> IO (Either ToolError a))
 -> IO (Either LiveOperationFailure a)
enterLiveBatchBudgetedAction batch budget actWithDl =
 runBatchStepWithBudget False batch budget Nothing actWithDl

observeLiveStartup :: LiveSession -> IO (Either ToolError SessionObservation)
observeLiveStartup s = liveObserveStartupAction s

observeLiveSession :: LiveSession -> AdmissionDeadline -> IO (Either ToolError SessionObservation)
observeLiveSession s = liveObserveAction s

runBoundedLiveOperation :: LiveSession -> AdmissionDeadline -> IO (Either ToolError a) -> IO (Either LiveOperationFailure a)
runBoundedLiveOperation s opDl act = do
 framed <- withLiveFrameAdmission s $ \adm ->
  enterLiveFrameAction adm opDl opDl act
 pure $ case framed of
  Left preErr -> Left (OperationRefusedPreDispatch preErr)
  Right outcome -> outcome

safeEnvironment :: [(String, String)] -> Bool
safeEnvironment = all (\(key, val) -> not (null key) && all (`notElem` ['=', '\0']) key && '\0' `notElem` val)

persistentHeld :: HeldExecutable -> [String] -> TransferTicket -> [(String, String)] -> Either ToolError PersistentSpawn
persistentHeld lease args ticket childEnvironment
 | safeEnvironment childEnvironment = Right (PersistentSpawn "/" args (Just (TransferInput ticket)) childEnvironment (Just lease))
 | otherwise = Left BadArguments

persistentHeldNoInput :: HeldExecutable -> [String] -> [(String, String)] -> Either ToolError PersistentSpawn
persistentHeldNoInput lease args childEnvironment
 | safeEnvironment childEnvironment = Right (PersistentSpawn "/" args Nothing childEnvironment (Just lease))
 | otherwise = Left BadArguments

persistentFixture :: FilePath -> [String] -> Handle -> PersistentSpawn
persistentFixture exe args handle =
 PersistentSpawn exe args (Just (FixtureHandle handle)) [("LC_ALL", "C"), ("LANG", "C"), ("PATH", "/usr/bin")] Nothing

persistentTicketFixture :: FilePath -> [String] -> TransferTicket -> PersistentSpawn
persistentTicketFixture exe args ticket =
 PersistentSpawn exe args (Just (TransferInput ticket)) [("LC_ALL", "C"), ("LANG", "C"), ("PATH", "/usr/bin")] Nothing

newPersistentOwner :: IO PersistentOwner
newPersistentOwner =
 PersistentOwner
  <$> O.newOwner
  <*> newMVar PhaseAvailable
  <*> newCallbackGate
  <*> newTVarIO False
  <*> newEmptyMVar
  <*> newIORef InternalPidfdUnopened
  <*> newIORef (pure True)

persistentStatus :: PersistentOwner -> IO PersistentStatus
persistentStatus (PersistentOwner _ phaseVar _ _ _ _ _) = do
 current <- readMVar phaseVar
 pure $ case current of
  PhaseAvailable -> PersistentAvailable
  PhaseStarting -> PersistentStarting
  PhaseLive _ -> PersistentLive
  PhaseStopping -> PersistentStopping
  PhaseRetired -> PersistentRetired
  PhaseQuarantined reasons -> PersistentQuarantined reasons

persistentPidfdCustody :: PersistentOwner -> IO PidfdCustody
persistentPidfdCustody (PersistentOwner _ _ _ _ _ pidfdCell _) =
 projectPidfdCustody <$> readIORef pidfdCell

persistentUnderlyingStatus :: PersistentOwner -> IO O.OwnerStatus
persistentUnderlyingStatus (PersistentOwner rawOwner _ _ _ _ _ _) = O.status rawOwner

-- Pure receipt classifier: Just False from HeldExecutable's interruptible
-- releaseNow is an explicit HeldUnknown receipt, never a successful release.
-- Exported only from package-private Internal with zero ownership mutator.
borrowReleasedReceipt :: Either SomeException (Maybe Bool) -> Bool
borrowReleasedReceipt (Right (Just True)) = True
borrowReleasedReceipt _ = False

data StopDispatch
 = DispatchImmediate StopReceipt
 | DispatchLiveTerm ActiveHandle AdmissionDeadline

-- Serialized against PhaseAvailable/PhaseStarting/PhaseLive transitions under
-- phaseVar so stop-during-starting is never lost and mints at most one StopDeadline.
requestSessionStop :: PersistentOwner -> StopBudget -> IO StopReceipt
requestSessionStop (PersistentOwner _ phaseVar cbGate stopReadyVar stopBell _ _) stopBudget = mask_ $ do
 let reqMicros = stopBudgetMicrosValue stopBudget
 dispatch <- withMVar phaseVar $ \ph -> case ph of
  PhaseAvailable -> do
   (already, res) <- claimExplicitStop cbGate stopReadyVar stopBell reqMicros
   pure . DispatchImmediate $
    if already then StopAlreadyRequested
    else either StopUncertain (const StopLatchedBeforeLive) res
  PhaseStarting -> do
   (already, res) <- claimExplicitStop cbGate stopReadyVar stopBell reqMicros
   pure . DispatchImmediate $
    if already then StopAlreadyRequested
    else either StopUncertain (const StopLatchedBeforeLive) res
  PhaseLive active -> do
   let capped = min (activeStopMicros active) reqMicros
   (already, res) <- claimExplicitStop cbGate stopReadyVar stopBell capped
   pure $
    if already then DispatchImmediate StopAlreadyRequested
    else case res of
     Left err -> DispatchImmediate (StopUncertain err)
     Right stopDl -> DispatchLiveTerm active stopDl
  PhaseStopping -> do
   already <- claimStoppingAttemptFlag cbGate
   pure (DispatchImmediate (if already then StopAlreadyRequested else StopNoLiveSession))
  PhaseRetired -> do
   already <- peekGateAttempted cbGate
   pure (DispatchImmediate (if already then StopAlreadyRequested else StopNoLiveSession))
  PhaseQuarantined _ -> do
   already <- peekGateAttempted cbGate
   pure (DispatchImmediate (if already then StopAlreadyRequested else StopNoLiveSession))
 case dispatch of
  DispatchImmediate receipt -> pure receipt
  DispatchLiveTerm active stopDl -> do
   step <- inScope (activeScope active) stopDl (sendVerifiedTerm active stopDl)
   pure $ case step of
    Right True -> StopLeaderAlreadyExited
    Right False -> StopSignalSent
    Left SessionClosed -> StopNoLiveSession
    Left err -> StopUncertain err
 where
  sendVerifiedTerm :: ActiveHandle -> AdmissionDeadline -> IO (Either ToolError Bool)
  sendVerifiedTerm active stopDl = do
   let pid = activePid active
       pidfdCell = activePidfdCell active
       initialObs = activeInitialObs active
       hook = activeHook active
   outcome <- try $ do
    hook "persistent-stop-before-observation"
    exited <- leaderExited pid
    if exited then pure (Right True) else do
     firstObs <- observeChild stopDl pid
     secondObs <- observeChild stopDl pid
     case (firstObs, secondObs) of
      (Right a, Right b) | a == initialObs && b == initialObs && observedPid a == pid -> do
       hook "persistent-stop-before-signal"
       left <- remainingMicros stopDl
       if left <= 0 then pure (Left TimedOut) else do
        cust <- readIORef pidfdCell
        case cust of
         InternalPidfdKnownOpen (Fd rawPidfd) cPid _ | cPid == pid -> do
          sent <- c_pidfd_send_signal (fromIntegral rawPidfd) (fromIntegral sigTERM) nullPtr 0
          if sent == 0 then pure (Right False) else do
           err <- getErrno
           pure (if err == eSRCH then Right True else Left SpawnOrIO)
         _ -> pure (Left SessionClosed)
      (Left problem, _) -> pure (Left problem)
      (_, Left problem) -> pure (Left problem)
      _ -> pure (Left SpawnOrIO)
   pure (either (const (Left SpawnOrIO)) id (outcome :: Either IOException (Either ToolError Bool)))

withPersistentOwner
 :: PersistentOwner
 -> PersistentSpawn
 -> Int
 -> StartBudget
 -> StopBudget
 -> (SessionObservation -> IO (Either ToolError ()))
 -> (LiveSession -> IO a)
 -> IO (Either SessionExit (a, SessionExit))
withPersistentOwner pOwner selection cap startBudget stopBudget verifyReady liveBody =
 withPersistentOwnerHook pOwner selection cap startBudget stopBudget verifyReady liveBody (const (pure ()))

data EntryDecision
 = EntryBusy
 | EntryPreStopped (Either ToolError AdmissionDeadline)
 | EntryProceed

data PublishDecision
 = PublishPreStopped (Either ToolError AdmissionDeadline)
 | PublishLive

withPersistentOwnerHook
 :: forall a.
    PersistentOwner
 -> PersistentSpawn
 -> Int
 -> StartBudget
 -> StopBudget
 -> (SessionObservation -> IO (Either ToolError ()))
 -> (LiveSession -> IO a)
 -> (String -> IO ())
 -> IO (Either SessionExit (a, SessionExit))
withPersistentOwnerHook (PersistentOwner rawOwner phaseVar cbGate stopReadyVar stopBell pidfdCell borrowReleaseCell) (PersistentSpawn exe args selectedInput selectedEnv selectedLease) cap startBudget stopBudget verifyReady liveBody hook
 | null exe || head exe /= '/' || cap <= 0 || cap > 4194304 = pure (Left (StartupRefused BadArguments))
 | otherwise = mask $ \restore -> do
  entryDecision <- modifyMVar phaseVar $ \ph -> case ph of
   PhaseAvailable -> do
    latched <- setGateStopCap cbGate stopMicros
    case latched of
     Nothing -> pure (PhaseStarting, EntryProceed)
     Just (Right stopDl) -> pure (PhaseRetired, EntryPreStopped (Right stopDl))
     Just (Left err) -> pure (PhaseQuarantined ["persistent-stop-deadline-mint-failed"], EntryPreStopped (Left err))
   _ -> pure (ph, EntryBusy)
  case entryDecision of
   EntryBusy -> pure (Left (StartupRefused OwnerBusy))
   EntryPreStopped (Right _) -> pure (Left (StartupRefused SessionClosed))
   EntryPreStopped (Left _) -> pure (Left (ExitUncertain CleanupUncertain ["persistent-stop-deadline-mint-failed"]))
   EntryProceed -> do
    initialBudget <- remainingMicros startDl
    if initialBudget == 0 then do
     modifyMVar_ phaseVar (const (pure PhaseRetired))
     pure (Left (StartupRefused TimedOut))
    else do
     admitted <- O.begin rawOwner
     if not admitted then do
      modifyMVar_ phaseVar (const (pure (PhaseQuarantined ["underlying-owner-busy"])))
      pure (Left (StartupRefused OwnerBusy))
     else do
      outcome <- (try (do
       writeIORef pidfdCell InternalPidfdUnopened
       writeIORef borrowReleaseCell (pure True)
       pending <- O.newPending
       retainedPending <- O.retainPending rawOwner pending
       unless retainedPending (ioError (userError "persistent pending slot already occupied"))
       selectedPathResult <- case selectedLease of
        Nothing -> pure (Just exe)
        Just lease -> do
         let cancelled = do
              stopped <- atomically (readTVar stopReadyVar)
              left <- remainingMicros startDl
              pure (stopped || left <= 0)
             pause = do
              left <- remainingMicros startDl
              when (left > 0) $
               void (timeout (min 5000 left) (atomically $ do
                stopped <- readTVar stopReadyVar
                if stopped then pure () else retry))
         -- Pre-own the exact capability before its single-use activation. Any
         -- exception retains it in rawOwner; no uninterruptible fallback runs.
         capability <- prepareHeldBorrow lease
         O.retainHeldBorrow rawOwner capability
         borrowed <- activateHeldBorrowWhile capability cancelled pause
         case borrowed of
          Nothing -> pure Nothing
          Just (Left _) -> ioError (userError "executable lease unavailable")
          Just (Right path) -> do
           writeIORef borrowReleaseCell (maybe False id <$> tryReleaseHeld capability)
           pure (Just path)
       case selectedPathResult of
        Nothing -> abortBeforeBorrow pending
        Just selectedPath -> do
         stopSnapshot <- tryPeekPreSpawnStop cbGate
         latchedAfterBorrow <- case stopSnapshot of
          Left _ -> ioError (userError "persistent-postborrow-stop-gate-busy")
          Right latched -> pure latched
         claimBudget <- remainingMicros startDl
         case latchedAfterBorrow of
          Just (Left _) -> abortPreSpawnNothing pending Nothing ["persistent-stop-deadline-mint-failed"] (ExitUncertain CleanupUncertain ["persistent-stop-deadline-mint-failed"]) True
          Just (Right stopDl) -> abortPreSpawnNothing pending (Just stopDl) [] (StartupRefused SessionClosed) False
          Nothing | claimBudget == 0 -> abortPreSpawnNothing pending Nothing [] (StartupRefused TimedOut) False
          Nothing -> do
           prepared <- prepareInput startDl
           case prepared of
            Left problem -> do
             if problem == CleanupUncertain then do
              O.pendingRecordIssue pending "claimed-ticket-state-uncertain"
              O.failUnsettled rawOwner "claimed-ticket-state-uncertain"
              modifyMVar_ phaseVar (const (pure (PhaseQuarantined ["claimed-ticket-state-uncertain"])))
              pure (Left (ExitUncertain CleanupUncertain ["claimed-ticket-state-uncertain"]))
             else
              abortPreSpawnNothing pending Nothing [] (StartupRefused problem) False
            Right (selectedHandle, closeInput) -> do
             beforeSpawn <- startupAction rawOwner (hook "persistent-before-spawn" >> hook "persistent-before-spawn-reserve" >> remainingMicros startDl) closeInput
             reservedResult <- if beforeSpawn == 0
              then tryPeekPreSpawnStop cbGate
              else tryReserveSpawnUnderGate cbGate startDl
             case reservedResult of
              Left TimedOut -> abortPreSpawnWithInput pending closeInput Nothing [] (StartupRefused TimedOut) False
              Left _ -> do
               -- A fixture handle has not yet been transferred to the owner at
               -- this point. Keep it as evidence while retirement is unknown.
               case selectedInput of Just (FixtureHandle h) -> O.retainTransfer rawOwner h; _ -> pure ()
               O.pendingRecordIssue pending "persistent-spawn-gate-busy"
               O.failUnsettled rawOwner "persistent-spawn-gate-busy"
               modifyMVar_ phaseVar (const (pure (PhaseQuarantined ["persistent-spawn-gate-busy"])))
               pure (Left (ExitUncertain CleanupUncertain ["persistent-spawn-gate-busy"]))
              Right (Just (Left _)) -> abortPreSpawnWithInput pending closeInput Nothing ["persistent-stop-deadline-mint-failed"] (ExitUncertain CleanupUncertain ["persistent-stop-deadline-mint-failed"]) True
              Right (Just (Right stopDl)) -> abortPreSpawnWithInput pending closeInput (Just stopDl) [] (StartupRefused SessionClosed) False
              Right Nothing | beforeSpawn == 0 -> abortPreSpawnWithInput pending closeInput Nothing [] (StartupRefused TimedOut) False
              Right Nothing -> do
               _ <- startupAction rawOwner (hook "persistent-after-spawn-reserve") closeInput
               case selectedInput of Just (FixtureHandle h) -> O.retainTransfer rawOwner h; _ -> pure ()
               vWorkerCell <- newIORef (Nothing :: Maybe (ThreadId, IO ()))
               (outH, errH, ph, pid, child) <- startupAction rawOwner (spawnOwned pending selectedPath selectedHandle) closeInput
               (outTid, outRes) <- spawnReader outH cap `onException` cleanupStartup pending closeInput child outH errH ph pid Nothing
               O.retainReader child outTid (void outRes)
               (errTid, errRes) <- spawnReader errH cap `onException` cleanupStartup pending closeInput child outH errH ph pid (Just (outTid, outRes))
               O.retainReader child errTid (void errRes)
               transferClosed <- try (hook "persistent-transfer-close" >> closeInput) :: IO (Either SomeException ())
               scope <- newSessionScope
               wakeGate <- newWakeGate
               (case transferClosed of
                Left _ -> retireStartupFailure pending child scope wakeGate outTid outRes outH errTid errRes errH ph pid ["selected-stdin-close"] CleanupUncertain
                Right () -> do
                 readyObs <- inScope scope startDl (observeChild startDl pid)
                 case readyObs of
                  Left err -> retireStartupOrLatchedStop pending child Nothing scope wakeGate outTid outRes outH errTid errRes errH ph pid err
                  Right obs -> do
                   pidfdRes <- openSessionPidfd scope startDl pid obs pending
                   case pidfdRes of
                    Left err -> retireStartupOrLatchedStop pending child (Just obs) scope wakeGate outTid outRes outH errTid errRes errH ph pid err
                    Right pfd -> do
                     remStart <- remainingMicros startDl
                     latchedBeforeVerify <- peekGateStop cbGate
                     case latchedBeforeVerify of
                      Just stopDlRes ->
                       retireLatchedStartupStop pending stopDlRes obs child scope wakeGate outTid outRes outH errTid errRes errH ph pid
                      Nothing | remStart == 0 ->
                       retireStartupOrLatchedStop pending child (Just obs) scope wakeGate outTid outRes outH errTid errRes errH ph pid TimedOut
                      Nothing -> do
                       -- Race verifyReady against owner stop so requestSessionStop
                       -- during PhaseStarting cancels immediately under its immutable D,
                       -- while retaining vTid in O.Child for bounded drain on async interrupt.
                       vDoneVar <- newTVarIO Nothing
                       let waitVerifyDone = atomically (readTVar vDoneVar >>= maybe retry pure)
                       vTid <- mask_ $ do
                        tid <- forkFinally
                         (restore (timeout remStart (verifyReady obs)))
                         (\r -> atomically (writeTVar vDoneVar (Just r)))
                        O.retainReader child tid (void waitVerifyDone)
                        writeIORef vWorkerCell (Just (tid, void waitVerifyDone))
                        pure tid
                       hook "persistent-verify-ready-started"
                       raceOut <- atomically $
                        (do s <- readTVar stopReadyVar
                            if s then pure Nothing else retry)
                        `orElse`
                        (readTVar vDoneVar >>= maybe retry (pure . Just))
                       case raceOut of
                        Nothing -> do
                         mStopRes <- peekGateStop cbGate
                         let stopDlRes = maybe (Left SessionClosed) id mStopRes
                         case stopDlRes of
                          Left _ -> do
                           let reasons = ["persistent-stop-deadline-mint-failed"]
                           O.pendingRecordIssue pending "persistent-stop-deadline-mint-failed"
                           O.quarantine rawOwner (Just child) reasons
                           modifyMVar_ phaseVar (const (pure (PhaseQuarantined reasons)))
                           pure (Left (ExitUncertain CleanupUncertain reasons))
                          Right latchedStopDl -> do
                           killedV <- boundedByDl latchedStopDl (killThread vTid)
                           joinedV <- boundedByDl latchedStopDl waitVerifyDone
                           if not (completed killedV && completed joinedV) then do
                            let reasons = ["persistent-startup-verify-not-drained"]
                            O.pendingRecordIssue pending "persistent-startup-verify-not-drained"
                            O.quarantine rawOwner (Just child) reasons
                            modifyMVar_ phaseVar (const (pure (PhaseQuarantined reasons)))
                            case asyncErrors killedV ++ asyncErrors joinedV of firstEx : _ -> throwIO firstEx; [] -> pure (Left (ExitUncertain CleanupUncertain reasons))
                           else do
                            writeIORef vWorkerCell Nothing
                            retireLatchedStartupStop pending (Right latchedStopDl) obs child scope wakeGate outTid outRes outH errTid errRes errH ph pid
                        Just checkedReady -> do
                         writeIORef vWorkerCell Nothing
                         afterReady <- remainingMicros startDl
                         case checkedReady of
                          Left ex -> case fromException ex :: Maybe SomeAsyncException of
                           Just _ -> do
                            _ <- retireStartupOrLatchedStop pending child (Just obs) scope wakeGate outTid outRes outH errTid errRes errH ph pid SpawnOrIO
                            throwIO ex
                           Nothing -> retireStartupOrLatchedStop pending child (Just obs) scope wakeGate outTid outRes outH errTid errRes errH ph pid SpawnOrIO
                          Right Nothing -> retireStartupOrLatchedStop pending child (Just obs) scope wakeGate outTid outRes outH errTid errRes errH ph pid TimedOut
                          Right (Just (Left err)) -> retireStartupOrLatchedStop pending child (Just obs) scope wakeGate outTid outRes outH errTid errRes errH ph pid err
                          Right (Just (Right ())) | afterReady == 0 ->
                           retireStartupOrLatchedStop pending child (Just obs) scope wakeGate outTid outRes outH errTid errRes errH ph pid TimedOut
                          Right (Just (Right ())) -> do
                           let active = ActiveHandle scope pid pidfdCell obs stopMicros hook
                           pubDecision <- modifyMVar phaseVar $ \_ -> do
                            mLatched <- peekGateStop cbGate
                            case mLatched of
                             Just stopDlRes -> pure (PhaseStopping, PublishPreStopped stopDlRes)
                             Nothing -> pure (PhaseLive active, PublishLive)
                           case pubDecision of
                            PublishPreStopped stopDlRes ->
                             retireLatchedStartupStop pending stopDlRes obs child scope wakeGate outTid outRes outH errTid errRes errH ph pid
                            PublishLive -> do
                             let sessionCap = LiveSession
                                  { liveWaitAction = waitLive scope pid stopBell outRes errRes
                                  , liveStopReadySTM = do
                                      stopped <- readTVar stopReadyVar
                                      if stopped then pure () else retry
                                  , liveWakeScopeAction = \wakeBody -> runWakeScope wakeGate pid pfd stopReadyVar wakeBody
                                  , liveFrameAdmissionAction = \frameBody -> runFrameAdmission cbGate scope pid obs stopReadyVar frameBody
                                  , liveObserveStartupAction = inScope scope startDl $ do
                                      checkedObs <- observeChild startDl pid
                                      pure $ case checkedObs of
                                       Right currentObs | currentObs == obs -> Right currentObs
                                       Right _ -> Left SpawnOrIO
                                       Left err -> Left err
                                  , liveObserveAction = \opDl -> inScope scope opDl (do
                                      hook "persistent-scope-observation"
                                      checkedObs <- observeChild opDl pid
                                      hook "persistent-scope-observation-complete"
                                      pure $ case checkedObs of
                                       Right currentObs | currentObs == obs -> Right currentObs
                                       Right _ -> Left SpawnOrIO
                                       Left err -> Left err)
                                  , liveBoundedAction = \opDl act -> do
                                      framed <- runFrameAdmission cbGate scope pid obs stopReadyVar $ \adm ->
                                       enterLiveFrameAction adm opDl opDl act
                                      pure $ case framed of
                                       Left preErr -> Left (OperationRefusedPreDispatch preErr)
                                       Right res -> res
                                  }
                             bodyResult <- try (restore (liveBody sessionCap)) :: IO (Either SomeException a)
                             modifyMVar_ phaseVar (const (pure PhaseStopping))
                             retireLive pending stopMicros (Just obs) child scope wakeGate outTid outRes outH errTid errRes errH ph pid bodyResult
                ) `onException` retireInterruptedStartup pending child scope wakeGate vWorkerCell outTid outRes outH errTid errRes errH ph pid
       ) :: IO (Either IOException (Either SessionExit (a, SessionExit)))) `onException` markInterrupted
      case outcome of
       Left _ -> do
        O.failUnsettled rawOwner "persistent-spawn-or-io"
        ownerState <- O.status rawOwner
        case ownerState of
         O.Available -> do
          modifyMVar_ phaseVar (const (pure PhaseRetired))
          pure (Left (StartupRefused SpawnOrIO))
         O.Quarantined reasons -> do
          modifyMVar_ phaseVar (const (pure (PhaseQuarantined reasons)))
          pure (Left (ExitUncertain CleanupUncertain reasons))
         _ -> do
          modifyMVar_ phaseVar (const (pure (PhaseQuarantined ["persistent-spawn-or-io"])))
          pure (Left (ExitUncertain CleanupUncertain ["persistent-spawn-or-io"]))
       Right val -> pure val
 where
  startDl :: AdmissionDeadline
  startDl = startBudgetDeadline startBudget

  stopMicros :: Int
  stopMicros = stopBudgetMicrosValue stopBudget

  borrowReleased :: Either SomeException (Maybe Bool) -> Bool
  borrowReleased = borrowReleasedReceipt

  -- Called only after the synchronous acquisition returns Nothing: no future
  -- acquire can commit, and this branch has not prepared input or spawned.
  -- The private raw Owner has one writer in this phase; stop only uses phaseVar
  -- and cbGate. False or a busy phase/gate retains custody and never reports a
  -- clean retirement. A late receipt does not claim timely StartD completion.
  abortBeforeBorrow :: O.Pending -> IO (Either SessionExit (a, SessionExit))
  abortBeforeBorrow pending = case selectedLease of
   Just _ -> do
    baseResult <- emergencyPreSpawnDl
    case baseResult of
     Left _ -> pure (Left (ExitUncertain CleanupUncertain ["startup-preowned-deadline-unavailable"]))
     Right base -> finishTracked pending base False True (StartupRefused TimedOut)
   Nothing -> abortBeforeBorrowLegacy pending

  abortBeforeBorrowLegacy :: O.Pending -> IO (Either SessionExit (a, SessionExit))
  abortBeforeBorrowLegacy pending = do
   rawClean <- O.tryAbortUnborrowed rawOwner pending
   if not rawClean then do
    let reasons = ["startup-unborrowed-raw-abort-unconfirmed"]
    O.pendingRecordIssue pending "startup-unborrowed-raw-abort-unconfirmed"
    current <- tryTakeMVar phaseVar
    case current of
     Nothing -> pure ()
     Just PhaseStarting -> putMVar phaseVar (PhaseQuarantined reasons)
     Just other -> putMVar phaseVar other
    pure (Left (ExitUncertain CleanupUncertain reasons))
   else do
#ifdef WARLOCK_OWNER_QA
    -- Test-component-only barrier; production never exports or invokes it.
    hook "persistent-unborrowed-raw-aborted"
#endif
    current <- tryTakeMVar phaseVar
    case current of
     Nothing -> pure (Left (ExitUncertain CleanupUncertain ["startup-unborrowed-phase-busy"]))
     Just oldPhase -> do
      decision <- (case oldPhase of
       PhaseStarting -> do
        let CallbackGate gate = cbGate
        snapshot <- tryReadMVar gate
        case snapshot of
         Nothing -> pure (PhaseQuarantined ["startup-unborrowed-stop-gate-busy"], Left (ExitUncertain CleanupUncertain ["startup-unborrowed-stop-gate-busy"]))
         Just (GateState latched _ _ _ _ _) -> case latched of
          Just (Left _) -> pure (PhaseQuarantined ["persistent-stop-deadline-mint-failed"], Left (ExitUncertain CleanupUncertain ["persistent-stop-deadline-mint-failed"]))
          Just (Right _) -> pure (PhaseRetired, Left (StartupRefused SessionClosed))
          Nothing -> do
           left <- remainingMicros startDl
           if left <= 0 then pure (PhaseRetired, Left (StartupRefused TimedOut))
           else pure (PhaseQuarantined ["startup-unborrowed-unexplained"], Left (ExitUncertain CleanupUncertain ["startup-unborrowed-unexplained"]))
       _ -> pure (oldPhase, Left (ExitUncertain CleanupUncertain ["startup-unborrowed-phase-changed"])))
       `onException` putMVar phaseVar oldPhase
      let (nextPhase, result) = decision
      putMVar phaseVar nextPhase
      pure result

  releaseBorrowBounded :: AdmissionDeadline -> IO (Either SomeException (Maybe Bool))
  releaseBorrowBounded dl = do
   hookStep <- boundedByDl dl (hook ("qa-before-held-borrow-release:" ++ deadlineAbsoluteNs dl))
   case hookStep of
    Left ex -> pure (Left ex)
    Right Nothing -> pure (Right Nothing)
    Right (Just ()) -> do
     relNow <- readIORef borrowReleaseCell
     boundedByDl dl relNow

  -- Re-sample the same owner's sticky stop at each pre-spawn release boundary.
  -- Busy or a failed stop mint is uncertainty, never permission to extend D.
  preSpawnEffectiveDl :: AdmissionDeadline -> IO (Maybe AdmissionDeadline)
  preSpawnEffectiveDl base = do
   let CallbackGate gate = cbGate
   snapshot <- tryReadMVar gate
   pure $ case snapshot of
    Nothing -> Nothing
    Just (GateState Nothing _ _ _ _ _) -> Just base
    Just (GateState (Just (Left _)) _ _ _ _ _) -> Nothing
    Just (GateState (Just (Right stopDl)) _ _ _ _ _) -> Just (capAdmissionDeadline base stopDl)

  releaseBorrowPreSpawn :: AdmissionDeadline -> IO (Either SomeException (Maybe Bool))
  releaseBorrowPreSpawn base = do
   hookStep <- boundedByDl base (hook ("qa-before-held-borrow-release:" ++ deadlineAbsoluteNs base))
   case hookStep of
    Left ex -> pure (Left ex)
    Right Nothing -> pure (Right Nothing)
    Right (Just ()) -> do
     effective <- preSpawnEffectiveDl base
     case effective of
      Nothing -> pure (Right Nothing)
      Just currentDl -> do
       result <- case selectedLease of
        Nothing -> do
         relNow <- readIORef borrowReleaseCell
         boundedByDl currentDl relNow
        Just _ -> releaseTrackedGuarded currentDl
       case result of
        Right (Just True) -> do
         final <- preSpawnEffectiveDl currentDl
         case final of
          Nothing -> pure (Right Nothing)
          Just finalDl -> do
           left <- remainingMicros finalDl
           pure (if left > 0 then result else Right Nothing)
        _ -> pure result

  -- Same stop gate serializes a single nonblocking retained capability release
  -- with the first stop latch. No handle close or arbitrary hook holds the gate.
  releaseTrackedGuarded :: AdmissionDeadline -> IO (Either SomeException (Maybe Bool))
  releaseTrackedGuarded base = mask_ $ do
   let CallbackGate gate = cbGate
   selected <- tryTakeMVar gate
   case selected of
    Nothing -> pure (Right Nothing)
    Just saved@(GateState latched _ _ _ _ _) ->
     (case latched of
       Just (Left _) -> pure (Right Nothing)
       _ -> do
        let effective = case latched of Just (Right stopDl) -> capAdmissionDeadline base stopDl; _ -> base
        before <- remainingMicros effective
        if before <= 0 then pure (Right Nothing) else do
         released <- try (O.tryReleaseRetainedHeld rawOwner) :: IO (Either SomeException (Maybe Bool))
         after <- remainingMicros effective
         pure (if after <= 0 then either Left (const (Right Nothing)) released else released))
      `finally` putMVar gate saved

  -- Exact no-input / matching closed-core / terminal no-borrow state is
  -- validated by raw Owner. Taking phase then stop gate serializes with stop;
  -- both gates and raw-owner operation are nonblocking, no external actions.
  -- Busy/expiry/uncertainty retains raw refs and never claims a clean finish.
  finishTracked :: O.Pending -> AdmissionDeadline -> Bool -> Bool -> SessionExit -> IO (Either SessionExit (a, SessionExit))
  finishTracked pending base needsCore noBorrow fallback = mask_ $ do
   let reasons = ["startup-tracked-finish-unconfirmed"]
       unknown = Left (ExitUncertain CleanupUncertain reasons)
       CallbackGate gate = cbGate
   phase <- tryTakeMVar phaseVar
   case phase of
    Nothing -> pure unknown
    Just prior -> case prior of
     PhaseStarting -> do
      selected <- tryTakeMVar gate `onException` putMVar phaseVar prior
      case selected of
       Nothing -> putMVar phaseVar (PhaseQuarantined reasons) >> pure unknown
       Just saved@(GateState latched _ _ _ _ _) -> do
        result <- (case latched of
         Just (Left _) -> pure (False, fallback)
         _ -> do
          let effective = case latched of Just (Right stopDl) -> capAdmissionDeadline base stopDl; _ -> base
              finalExit = case latched of Just (Right _) -> StartupRefused SessionClosed; _ -> fallback
          left <- remainingMicros effective
          case readMaybe (deadlineAbsoluteNs effective) :: Maybe Integer of
           Nothing -> pure (False, finalExit)
           Just _ | left <= 0 -> pure (False, finalExit)
           Just end -> do
            clean <- if noBorrow then O.tryAbortHeldNotAcquiredBefore end rawOwner pending
             else if needsCore then O.tryAbortHeldWithCoreBefore end rawOwner pending
             else O.tryAbortHeldNoInputBefore end rawOwner pending
            pure (clean, finalExit)) `onException` (putMVar gate saved >> putMVar phaseVar prior)
        putMVar gate saved
        let (clean, finalExit) = result
        if clean then putMVar phaseVar PhaseRetired >> pure (Left finalExit)
         else putMVar phaseVar (PhaseQuarantined reasons) >> pure unknown
     _ -> putMVar phaseVar prior >> pure unknown

  emergencyPreSpawnDl :: IO (Either ToolError AdmissionDeadline)
  emergencyPreSpawnDl = do
   let CallbackGate gate = cbGate
   snapshot <- tryReadMVar gate
   case snapshot of
    Nothing -> pure (Left OwnerBusy)
    Just (GateState (Just existing) _ _ _ _ _) -> pure existing
    Just (GateState Nothing _ _ _ _ _) -> deadlineAfter 2000000

  abortPreSpawnNothing :: O.Pending -> Maybe AdmissionDeadline -> [Text] -> SessionExit -> Bool -> IO (Either SessionExit (a, SessionExit))
  abortPreSpawnNothing pending mStopDl reasons exitVal quarantineOwner =
   if quarantineOwner then do
    O.clearTickets rawOwner
    O.pendingRecordIssue pending "persistent-stop-deadline-mint-failed"
    O.failUnsettled rawOwner "persistent-stop-deadline-mint-failed"
    modifyMVar_ phaseVar (const (pure (PhaseQuarantined reasons)))
    pure (Left exitVal)
   else do
    dlRes <- maybe emergencyPreSpawnDl (pure . Right) mStopDl
    relStep <- case dlRes of
     Left _ -> pure (Right Nothing)
     Right dl -> releaseBorrowPreSpawn dl
    if borrowReleased relStep then case (selectedLease, dlRes) of
     (Just _, Right base) -> finishTracked pending base False False exitVal
     _ -> do
      O.releaseBorrows rawOwner
      O.clearTickets rawOwner
      O.clearPending rawOwner
      O.abortBegin rawOwner
      modifyMVar_ phaseVar (const (pure PhaseRetired))
      pure (Left exitVal)
    else do
     let bReasons = ["startup-borrow-release"]
     O.pendingRecordIssue pending "startup-borrow-release"
     O.failUnsettled rawOwner "startup-borrow-release"
     modifyMVar_ phaseVar (const (pure (PhaseQuarantined bReasons)))
     case asyncErrors relStep of
      firstEx : _ -> throwIO firstEx
      [] -> pure (Left (ExitUncertain CleanupUncertain bReasons))

  abortPreSpawnCleaned :: SessionExit -> IO (Either SessionExit (a, SessionExit))
  abortPreSpawnCleaned exitVal = do
   O.releaseBorrows rawOwner
   O.clearCore rawOwner
   O.clearTickets rawOwner
   O.clearPending rawOwner
   O.abortBegin rawOwner
   modifyMVar_ phaseVar (const (pure PhaseRetired))
   pure (Left exitVal)

  abortPreSpawnWithInput :: O.Pending -> IO () -> Maybe AdmissionDeadline -> [Text] -> SessionExit -> Bool -> IO (Either SessionExit (a, SessionExit))
  abortPreSpawnWithInput pending closeInput mStopDl reasons exitVal quarantineOwner =
   if quarantineOwner then do
    dlRes <- deadlineAfter 2000000
    closedIn <- case dlRes of
     Left _ -> pure (Right Nothing)
     Right dl -> boundedByDl dl closeInput
    O.clearTickets rawOwner
    O.pendingRecordIssue pending "persistent-stop-deadline-mint-failed"
    O.failUnsettled rawOwner "persistent-stop-deadline-mint-failed"
    modifyMVar_ phaseVar (const (pure (PhaseQuarantined reasons)))
    case asyncErrors closedIn of
     firstEx : _ -> throwIO firstEx
     [] -> pure (Left exitVal)
   else do
    dlRes <- maybe emergencyPreSpawnDl (pure . Right) mStopDl
    closedIn <- case dlRes of
     Left _ -> pure (Right Nothing)
     Right dl -> boundedByDl dl closeInput
    relStep <- case dlRes of
     Right dl | completed closedIn -> releaseBorrowPreSpawn dl
     _ -> pure (Right Nothing)
    if completed closedIn && borrowReleased relStep then
     case (selectedLease, selectedInput, dlRes) of
      (Just _, Just (TransferInput _), Right base) -> finishTracked pending base True False exitVal
      (Just _, Nothing, Right base) -> finishTracked pending base False False exitVal
      (Just _, _, _) -> pure (Left (ExitUncertain CleanupUncertain ["startup-input-receipt-unavailable"]))
      _ -> abortPreSpawnCleaned exitVal
    else do
     let reason = if not (completed closedIn) then "startup-transfer-close" else "startup-borrow-release"
         bReasons = [T.pack reason]
     O.pendingRecordIssue pending reason
     O.failUnsettled rawOwner (T.pack reason)
     modifyMVar_ phaseVar (const (pure (PhaseQuarantined bReasons)))
     case asyncErrors closedIn ++ asyncErrors relStep of
      firstEx : _ -> throwIO firstEx
      [] -> pure (Left (ExitUncertain CleanupUncertain bReasons))

  markInterrupted :: IO ()
  markInterrupted = do
   O.failUnsettled rawOwner "persistent-interrupted"
   ownerState <- O.status rawOwner
   case ownerState of
    O.Available -> modifyMVar_ phaseVar $ \ph -> pure $ case ph of
     PhaseRetired -> PhaseRetired
     PhaseQuarantined rs -> PhaseQuarantined rs
     _ -> PhaseRetired
    O.Quarantined rs -> modifyMVar_ phaseVar (const (pure (PhaseQuarantined rs)))
    _ -> modifyMVar_ phaseVar (const (pure (PhaseQuarantined ["persistent-interrupted"])))

  openSessionPidfd :: SessionScope -> AdmissionDeadline -> ProcessID -> SessionObservation -> O.Pending -> IO (Either ToolError Fd)
  openSessionPidfd scope dl pid expectedObs pending = do
   beforeObs <- inScope scope dl (observeChild dl pid)
   case beforeObs of
    Left err -> pure (Left err)
    Right bObs | bObs /= expectedObs -> pure (Left SpawnOrIO)
    Right _ -> do
     remBefore <- remainingMicros dl
     if remBefore <= 0 then pure (Left TimedOut) else do
      openedPfd <- mask_ $ do
       rawFd <- c_pidfd_open (fromIntegral pid) pidfdNonblockFlags
       if rawFd < 0 then
        pure Nothing
       else do
        let pfd = Fd rawFd
        writeIORef pidfdCell (InternalPidfdKnownOpen pfd pid Nothing)
        O.pendingRecordFD pending pfd
        statRes <- try (getFdStatus pfd) :: IO (Either IOException FileStatus)
        case statRes of
         Left _ -> pure ()
         Right st -> do
          let ident = O.FDIdentity (toInteger (deviceID st)) (toInteger (fileID st))
          writeIORef pidfdCell (InternalPidfdKnownOpen pfd pid (Just ident))
          O.pendingIdentityFD pending pfd ident
        pure (Just pfd)
      case openedPfd of
       Nothing -> pure (Left SpawnOrIO)
       Just pfd -> do
        hook "persistent-after-pidfd-open"
        afterObs <- inScope scope dl (observeChild dl pid)
        remAfter <- remainingMicros dl
        case afterObs of
         Right aObs | aObs == expectedObs && remAfter > 0 -> pure (Right pfd)
         Right _ | remAfter <= 0 -> pure (Left TimedOut)
         Right _ -> pure (Left SpawnOrIO)
         Left err -> pure (Left err)

  prepareInput :: AdmissionDeadline -> IO (Either ToolError (Maybe Handle, IO ()))
  prepareInput prepDl = case selectedInput of
   Nothing -> pure (Right (Nothing, pure ()))
   Just (FixtureHandle h) -> pure (Right (Just h, hClose h))
   Just (TransferInput ticket) -> do
    O.retainTicket rawOwner ticket
    token <- newOwnerToken
    claimed <- claimTransferWhen ((> 0) <$> remainingMicros prepDl) token ticket
    case claimed of
     Left DeadlineExpired -> pure (Left TimedOut)
     Left _ -> pure (Left TransferUnavailable)
     Right core -> do
      O.retainCore rawOwner core
      borrowedHandle <- coreHandle core
      case borrowedHandle of
       Left _ -> pure (Left CleanupUncertain)
       Right h -> pure (Right (Just h, do
        res <- closeCoreTransfer core
        case res of
         Left _ -> do
          cause <- coreCloseDiagnostic core
          case cause of Just ex -> throwIO ex; Nothing -> ioError (userError "selected transfer close uncertain")
         Right () -> pure ()))

  spawnOwned :: O.Pending -> FilePath -> Maybe Handle -> IO (Handle, Handle, ProcessHandle, ProcessID, O.Child)
  spawnOwned pending selectedPath selectedHandle = do
   (inPipe, outPipe, errPipe, ph) <- createProcess_ "warlock-persistent-owned" (proc selectedPath args)
    { env = Just selectedEnv
    , std_in = maybe NoStream UseHandle selectedHandle
    , std_out = CreatePipe
    , std_err = CreatePipe
    , close_fds = True
    , create_group = True
    }
   child <- O.newChild ph
   O.publish rawOwner child
   void (O.pendingRecordHandle pending ph)
   mapM_ (O.retainPipe child) [h | Just h <- [inPipe, outPipe, errPipe]]
   case (inPipe, outPipe, errPipe) of
    (Nothing, Just o, Just e) -> do
     ident <- getPid ph
     case ident of
      Just pid | pid > 0 -> do
       O.setPid child pid
       void (O.pendingRecordPid pending pid)
       grp <- c_getpgid (fromIntegral pid)
       if grp == fromIntegral pid then pure (o, e, ph, pid, child)
       else O.quarantine rawOwner (Just child) ["unconfirmed-owned-group"] >> ioError (userError "unconfirmed owned group")
      _ -> O.quarantine rawOwner (Just child) ["missing-owned-pid"] >> ioError (userError "missing owned pid")
    _ -> O.quarantine rawOwner (Just child) ["missing-owned-pipes"] >> ioError (userError "missing owned pipes")

  runWakeScope :: forall b. WakeGate -> ProcessID -> Fd -> TVar Bool -> (STM LiveWakeReason -> IO b) -> IO (Either ToolError b)
  runWakeScope wg pid pfd stopVar wakeBody = mask $ \restore -> do
   pinned <- admitWake wg
   if not pinned then pure (Left SessionClosed) else do
    scopeExitedVar <- newTVarIO False
    registrationSafe <- newIORef True
    let withTombstone :: STM LiveWakeReason -> STM LiveWakeReason
        withTombstone coreSTM = do
         exitedScope <- readTVar scopeExitedVar
         if exitedScope then pure LiveWakeScopeExited else coreSTM
    finally
     (do
       hook "persistent-wake-registered"
       stoppedNow <- atomically (readTVar stopVar)
       if stoppedNow then
        Right <$> restore (wakeBody (withTombstone (pure LiveWakeStopRequested)))
       else do
        deadNow <- leaderExited pid
        if deadNow then
         Right <$> restore (wakeBody $ withTombstone $ do
          s <- readTVar stopVar
          pure (if s then LiveWakeStopRequested else LiveWakeLeaderExited))
        else do
         let Fd rawPidfd = pfd
         regRes <- try $ do
          writeIORef registrationSafe False
          bracket
           (threadWaitReadSTM (fromIntegral rawPidfd))
           (\(_, unregister) -> do
             atomically (writeTVar scopeExitedVar True)
             hook "persistent-wake-tombstoned-before-unregister"
             unregister
             writeIORef registrationSafe True)
           (\(pidfdReadable, _) ->
             let wakeSTM = withTombstone $
                  (do s <- readTVar stopVar
                      if s then pure LiveWakeStopRequested else retry)
                  `orElse`
                  (pidfdReadable >> pure LiveWakeLeaderExited)
             in restore (wakeBody wakeSTM))
         case regRes of
          Left ex -> case fromException ex :: Maybe SomeAsyncException of
           Just _ -> throwIO ex
           Nothing -> do
            safe <- readIORef registrationSafe
            if safe then throwIO ex else pure (Left SpawnOrIO)
          Right val -> pure (Right val))
     (do
       atomically (writeTVar scopeExitedVar True)
       safe <- readIORef registrationSafe
       if safe then
        releaseWake wg
       else
        (closeWakeGate wg >> void (beginStopGateAndDeadline cbGate stopReadyVar stopBell stopMicros))
         `onException` closeCallbackGate cbGate stopReadyVar stopBell)

  runFrameAdmission :: forall b. CallbackGate -> SessionScope -> ProcessID -> SessionObservation -> TVar Bool -> (LiveFrameAdmission -> IO b) -> IO (Either ToolError b)
  runFrameAdmission gate scope pid expectedObs stopVar frameBody = mask $ \restore -> do
   admittedCb <- admitCallback gate
   if not admittedCb then pure (Left SessionClosed) else do
    frameStateVar <- newMVar (FrameState True FrameModeUnused)
    finally
     (do
       stoppedNow <- atomically (readTVar stopVar)
       if stoppedNow then pure (Left SessionClosed) else do
        deadNow <- leaderExited pid
        if deadNow then pure (Left SessionClosed) else do
         let adm = LiveFrameAdmission frameStateVar gate scope pid expectedObs stopVar hook
         Right <$> restore (frameBody adm))
     (modifyMVar_ frameStateVar (\(FrameState _ mode) -> pure (FrameState False mode)) >> releaseCallback gate)

  waitLive :: SessionScope -> ProcessID -> MVar () -> IO ReaderResult -> IO ReaderResult -> IO LiveWaitOutcome
  waitLive scope pid bell getOut getErr = do
   stoppedNow <- not <$> isEmptyMVar bell
   if stoppedNow then pure LiveStopRequested else do
    probeDlRes <- deadlineAfter 2000000
    case probeDlRes of
     Left err -> pure (LiveOutputFault err)
     Right probeDl -> do
      step <- inScope scope probeDl $ do
       a <- timeout 1 getOut
       b <- timeout 1 getErr
       case (a, b) of
        (Just (Right (Left x)), _) -> pure (Left x)
        (_, Just (Right (Left x))) -> pure (Left x)
        (Just (Left _), _) -> pure (Left SpawnOrIO)
        (_, Just (Left _)) -> pure (Left SpawnOrIO)
        _ -> Right <$> leaderExited pid
      case step of
       Left SessionClosed -> do
        bellSet <- not <$> isEmptyMVar bell
        pure (if bellSet then LiveStopRequested else LiveScopeClosed)
       Left err -> pure (LiveOutputFault err)
       Right True -> pure LiveLeaderExited
       Right False -> do
        woken <- timeout 10000 (readMVar bell)
        case woken of
         Just () -> pure LiveStopRequested
         Nothing -> waitLive scope pid bell getOut getErr

  boundedByDl :: AdmissionDeadline -> IO b -> IO (Either SomeException (Maybe b))
  boundedByDl dl action = do
   left <- remainingMicros dl
   if left <= 0 then pure (Right Nothing) else do
    out <- try (timeout left action)
    case out of
     Right (Just val) -> do
      after <- remainingMicros dl
      pure (if after > 0 then Right (Just val) else Right Nothing)
     other -> pure other

  -- QA-only observation hooks bracket the real action while resampling remaining
  -- budget before and after each hook so neither pre-entry stall nor post-return
  -- stall can enter action after D or settle cleanly after D.
  boundedByDlObserved :: AdmissionDeadline -> IO () -> IO () -> IO b -> IO (Either SomeException (Maybe b))
  boundedByDlObserved dl afterSample afterAction action = do
   left0 <- remainingMicros dl
   if left0 <= 0 then pure (Right Nothing) else do
    sampleStep <- try (timeout left0 afterSample)
    case sampleStep of
     Left ex -> pure (Left ex)
     Right Nothing -> pure (Right Nothing)
     Right (Just ()) -> do
      left <- remainingMicros dl
      if left <= 0 then pure (Right Nothing) else do
       out <- try (timeout left action)
       case out of
        Right (Just val) -> do
         leftPost <- remainingMicros dl
         postStep <- try (timeout (max 1 leftPost) afterAction)
         case postStep of
          Left ex -> pure (Left ex)
          Right Nothing -> pure (Right Nothing)
          Right (Just ()) -> do
           after <- remainingMicros dl
           pure (if after > 0 then Right (Just val) else Right Nothing)
        other -> pure other

  completed :: Either SomeException (Maybe b) -> Bool
  completed (Right (Just _)) = True
  completed _ = False

  asyncErrors :: Either SomeException b -> [SomeException]
  asyncErrors (Left ex) | Just _ <- (fromException ex :: Maybe SomeAsyncException) = [ex]
  asyncErrors _ = []

  -- Closes the owned pidfd at most once within closeDl while distinguishing:
  -- 1. pre-claim or post-claim/pre-syscall deadline expiry or abort (never
  --    entered closeFd -> remains/rolls back to InternalPidfdKnownOpen),
  -- 2. closeFd completing (commits InternalPidfdClosed + PendingClosed under
  --    mask immediately upon syscall return; if post-close deadline expired,
  --    retains truthful InternalPidfdClosed while returning Right Nothing),
  -- 3. pre-return timeout/exception in close region (sticky
  --    InternalPidfdCloseUncertain, never retried or signaled again).
  closeOwnedPidfdDl :: AdmissionDeadline -> O.Pending -> IO (Either SomeException (Maybe ()))
  closeOwnedPidfdDl closeDl pending = do
   cur <- readIORef pidfdCell
   case cur of
    InternalPidfdUnopened -> pure (Right (Just ()))
    InternalPidfdClosed -> pure (Right (Just ()))
    InternalPidfdClosing _ _ -> pure (Right Nothing)
    InternalPidfdCloseUncertain _ _ _ -> pure (Right Nothing)
    InternalPidfdKnownOpen _ _ _ -> do
     preCheck <- boundedByDl closeDl (hook "persistent-before-pidfd-close-precheck")
     case preCheck of
      Left ex -> do
       O.pendingRecordIssue pending "pidfd-preclose-aborted-known-open"
       pure (Left ex)
      Right Nothing -> do
       O.pendingRecordIssue pending "pidfd-close-deadline-expired-known-open"
       pure (Right Nothing)
      Right (Just ()) -> do
       gapStep <- boundedByDl closeDl (hook "persistent-after-pidfd-close-budget-sample")
       case gapStep of
        Left ex -> do
         O.pendingRecordIssue pending "pidfd-preclose-aborted-known-open"
         pure (Left ex)
        Right Nothing -> do
         O.pendingRecordIssue pending "pidfd-close-deadline-expired-before-claim-known-open"
         pure (Right Nothing)
        Right (Just ()) -> mask $ \restore -> do
         leftAtClaim <- remainingMicros closeDl
         if leftAtClaim <= 0 then do
          O.pendingRecordIssue pending "pidfd-close-deadline-expired-before-claim-known-open"
          pure (Right Nothing)
         else do
          claimed <- atomicModifyIORef' pidfdCell $ \st -> case st of
           InternalPidfdKnownOpen pfd cPid ident ->
            (InternalPidfdClosing cPid ident, Just (pfd, cPid, ident))
           other ->
            (other, Nothing)
          case claimed of
           Nothing -> do
            after <- readIORef pidfdCell
            pure $ case after of
             InternalPidfdUnopened -> Right (Just ())
             InternalPidfdClosed -> Right (Just ())
             _ -> Right Nothing
           Just (pfd, cPid, ident) -> do
            claimGap <- boundedByDl closeDl (restore (do
             hook "persistent-after-pidfd-claim-before-syscall"
             hook "persistent-before-pidfd-close"))
            leftBeforeSyscall <- remainingMicros closeDl
            case claimGap of
             Left ex -> do
              writeIORef pidfdCell (InternalPidfdKnownOpen pfd cPid ident)
              O.pendingRecordIssue pending "pidfd-claim-aborted-before-syscall-known-open"
              pure (Left ex)
             Right Nothing -> do
              writeIORef pidfdCell (InternalPidfdKnownOpen pfd cPid ident)
              O.pendingRecordIssue pending "pidfd-close-deadline-expired-after-claim-known-open"
              pure (Right Nothing)
             Right (Just ()) | leftBeforeSyscall <= 0 -> do
              writeIORef pidfdCell (InternalPidfdKnownOpen pfd cPid ident)
              O.pendingRecordIssue pending "pidfd-close-deadline-expired-after-claim-known-open"
              pure (Right Nothing)
             Right (Just ()) -> do
              -- leftBeforeSyscall verified closeDl > 0 before PendingUncertain
              -- (rolling back to KnownOpen on pre-entry expiry). Once
              -- pendingMarkFD marks PendingUncertain, leftAtClose re-samples
              -- closeDl after persistent-in-pidfd-close immediately before
              -- closeFd (recording conservative CloseUncertain without calling
              -- closeFd if expired in-region; bounded up to OS scheduler
              -- preemption between user-space sample and close(2) entry).
              O.pendingMarkFD pending pfd False
              res <- try (restore (timeout leftBeforeSyscall (mask $ \restoreInner -> do
               restoreInner (hook "persistent-in-pidfd-close")
               leftAtClose <- remainingMicros closeDl
               if leftAtClose <= 0 then
                pure False
               else do
                closeFd pfd
                writeIORef pidfdCell InternalPidfdClosed
                O.pendingMarkFD pending pfd True
                pure True))) :: IO (Either SomeException (Maybe Bool))
              postState <- readIORef pidfdCell
              case postState of
               InternalPidfdClosed ->
                case res of
                 Left ex -> pure (Left ex)
                 Right (Just True) -> do
                  postHook <- boundedByDl closeDl (restore (hook "persistent-after-pidfd-close-receipt"))
                  case postHook of
                   Left ex -> do
                    O.pendingRecordIssue pending "pidfd-postclose-hook-aborted"
                    pure (Left ex)
                   Right Nothing -> do
                    O.pendingRecordIssue pending "pidfd-closed-after-deadline"
                    pure (Right Nothing)
                   Right (Just ()) -> do
                    afterClose <- remainingMicros closeDl
                    if afterClose > 0 then
                     pure (Right (Just ()))
                    else do
                     O.pendingRecordIssue pending "pidfd-closed-after-deadline"
                     pure (Right Nothing)
                 _ -> do
                  O.pendingRecordIssue pending "pidfd-closed-after-deadline"
                  pure (Right Nothing)
               _ ->
                case res of
                 Right (Just True) -> do
                  writeIORef pidfdCell InternalPidfdClosed
                  O.pendingMarkFD pending pfd True
                  afterClose <- remainingMicros closeDl
                  if afterClose > 0 then
                   pure (Right (Just ()))
                  else do
                   O.pendingRecordIssue pending "pidfd-closed-after-deadline"
                   pure (Right Nothing)
                 Right _ -> do
                  writeIORef pidfdCell (InternalPidfdCloseUncertain cPid ident "pidfd-close-timed-out")
                  O.pendingRecordIssue pending "pidfd-close-timed-out-uncertain"
                  pure (Right Nothing)
                 Left ex -> do
                  writeIORef pidfdCell (InternalPidfdCloseUncertain cPid ident (T.pack (show ex)))
                  O.pendingRecordIssue pending "pidfd-close-exception-uncertain"
                  pure (Left ex)

  -- Signals only the verified unreaped direct child leader (via pidfd_send_signal
  -- when pidfd custody is InternalPidfdKnownOpen, otherwise c_kill only when no
  -- pidfd was ever opened on the unreaped ProcessHandle), never global negative-PGID
  -- killGroup and never through a Closing/Closed/CloseUncertain descriptor.
  terminateLeaderDl :: AdmissionDeadline -> Maybe SessionObservation -> ProcessHandle -> ProcessID -> IO ExitCode
  terminateLeaderDl dl expectedObs ph pid = do
   leftBefore <- remainingMicros dl
   when (leftBefore <= 0) $
    ioError (userError "owned persistent leader stop deadline expired before exit check")
   hook "persistent-before-leader-exit-probe"
   wasDead <- leaderExited pid
   racedExit <- if wasDead then hook "persistent-leader-already-exited" >> pure Nothing else do
    hook "persistent-before-leader-observation"
    case expectedObs of
     Nothing -> pure Nothing
     Just initialObs -> do
      verified <- observeChild dl pid
      case verified of
       Right currentObs | currentObs == initialObs -> pure Nothing
       _ -> do
        hook "persistent-leader-observation-invalid"
        -- Exit can remove /proc metadata after the non-reaping liveness probe.
        -- Only this same owned handle can confirm/reap that exit; missing
        -- metadata never authorizes a signal to the numeric PID.
        leftProbe <- remainingMicros dl
        when (leftProbe <= 0) $
         ioError (userError "owned persistent leader stop deadline expired before handle probe")
        hook "persistent-before-owned-handle-probe"
        observedExit <- timeout leftProbe (getProcessExitCode ph)
        afterProbe <- remainingMicros dl
        case observedExit of
         Just (Just code) | afterProbe > 0 -> pure (Just code)
         Just Nothing -> do
          hook "persistent-owned-handle-no-exit"
          -- Kernel exit can remove exe metadata before waitpid is ready.
          -- Wait only on the original owned handle, without signalling; a
          -- Only an actual owned-handle exit before D confirms retirement.
          leftWait <- remainingMicros dl
          when (leftWait <= 0) $
           ioError (userError "owned persistent leader stop deadline expired before natural exit wait")
          hook "persistent-owned-handle-awaiting-natural-exit"
          naturalExit <- timeout leftWait (waitForProcess ph)
          afterWait <- remainingMicros dl
          case naturalExit of
           Just code | afterWait > 0 -> pure (Just code)
           _ -> ioError (userError "owned persistent leader natural exit unconfirmed within stop deadline")
         Nothing -> do
          hook "persistent-owned-handle-probe-timed-out"
          ioError (userError "owned persistent leader observation invalid before SIGKILL")
         _ -> do
          hook "persistent-owned-handle-reap-after-stop-deadline"
          ioError (userError "owned persistent leader observation invalid before SIGKILL")
   case racedExit of
    Just code -> pure code
    Nothing -> do
     unless wasDead $ do
      hook "persistent-before-leader-kill"
      leftSignal <- remainingMicros dl
      when (leftSignal <= 0) $
       ioError (userError "owned persistent leader stop deadline expired before SIGKILL")
      cust <- readIORef pidfdCell
      sent <- case cust of
       InternalPidfdKnownOpen (Fd rawPidfd) cPid _ | cPid == pid ->
        c_pidfd_send_signal (fromIntegral rawPidfd) (fromIntegral sigKILL) nullPtr 0
       InternalPidfdUnopened ->
        c_kill (fromIntegral pid) (fromIntegral sigKILL)
       _ ->
        ioError (userError "owned persistent leader pidfd custody uncertain before SIGKILL")
      if sent == 0 then pure () else do
       err <- getErrno
       if err == eSRCH then pure () else ioError (userError "owned persistent leader signal failed")
     left <- remainingMicros dl
     if left <= 0 then ioError (userError "owned persistent leader reap deadline expired") else do
      hook "persistent-before-owned-leader-wait"
      waited <- timeout left (waitForProcess ph)
      case waited of
       Just code -> pure code
       Nothing -> do
        hook "persistent-owned-leader-wait-timed-out"
        ioError (userError "owned persistent leader reap timed out")

  -- Emergency containment/cleanup-only budget after startup spawn exception;
  -- never admits a live session or counts as completion within original 28s/30s D.
  cleanupStartup :: O.Pending -> IO () -> O.Child -> Handle -> Handle -> ProcessHandle -> ProcessID -> Maybe (ThreadId, IO ReaderResult) -> IO ()
  cleanupStartup pending closeInput child outH errH ph pid maybeOut = do
   O.quarantine rawOwner (Just child) ["persistent-startup-cleanup-pending"]
   mLatched <- peekGateStop cbGate
   cleanupDlRes <- case mLatched of
    Just existing -> pure existing
    Nothing -> deadlineAfter 2000000
   case cleanupDlRes of
    Left _ -> do
     let reasons = ["persistent-startup-deadline-mint-failed"]
     O.pendingRecordIssue pending "persistent-startup-deadline-mint-failed"
     O.quarantine rawOwner (Just child) reasons
     modifyMVar_ phaseVar (const (pure (PhaseQuarantined reasons)))
    Right cleanupDl -> do
     stopRes <- boundedByDl cleanupDl (terminateLeaderDl cleanupDl Nothing ph pid)
     closePfd <-
      if completed stopRes then
       closeOwnedPidfdDl cleanupDl pending
      else do
       O.pendingRecordIssue pending "pidfd-retained-unreaped-leader"
       pure (Right (Just ()))
     cancelRes <- case maybeOut of Nothing -> pure (Right (Just ())); Just (tid, _) -> boundedByDl cleanupDl (killThread tid)
     joinRes <- case maybeOut of Nothing -> pure (Right (Just ())); Just (_, r) -> fmap (fmap (const ())) <$> boundedByDl cleanupDl r
     let joined = completed joinRes
     closeOut <- if joined then boundedByDl cleanupDl (hClose outH) else pure (Right Nothing)
     closeErr <- boundedByDl cleanupDl (hClose errH)
     closeIn <- boundedByDl cleanupDl closeInput
     let bads = [T.pack nm | (nm, bad) <- [("startup-leader-reap", not (completed stopRes)), ("startup-pidfd-close", not (completed closePfd)), ("startup-reader-stop", not (completed cancelRes)), ("startup-reader-join", not joined), ("startup-stdout-close", not (completed closeOut)), ("startup-stderr-close", not (completed closeErr)), ("startup-transfer-close", not (completed closeIn))], bad]
         reasons = if null bads then ["persistent-startup-review-required"] else bads
     O.quarantine rawOwner (Just child) reasons
     modifyMVar_ phaseVar (const (pure (PhaseQuarantined reasons)))
     case asyncErrors stopRes ++ asyncErrors closePfd ++ asyncErrors cancelRes ++ asyncErrors joinRes ++ asyncErrors closeOut ++ asyncErrors closeErr ++ asyncErrors closeIn of
      firstEx : _ -> throwIO firstEx
      [] -> pure ()

  -- Bounded drain/containment when an async exception interrupts PhaseStarting
  -- (for example while verifyReady is running); no-op if normal retirement
  -- already settled PhaseRetired or PhaseQuarantined.
  retireInterruptedStartup :: O.Pending -> O.Child -> SessionScope -> WakeGate -> IORef (Maybe (ThreadId, IO ())) -> ThreadId -> IO ReaderResult -> Handle -> ThreadId -> IO ReaderResult -> Handle -> ProcessHandle -> ProcessID -> IO ()
  retireInterruptedStartup pending child scope wg vWorkerCell outTid outRes outH errTid errRes errH ph pid = do
   curPhase <- readMVar phaseVar
   case curPhase of
    PhaseRetired -> pure ()
    PhaseQuarantined _ -> pure ()
    _ -> do
     mLatched <- peekGateStop cbGate
     closeCallbackGate cbGate stopReadyVar stopBell
     closeWakeGate wg
     closeSessionScope scope
     dlRes <- case mLatched of
      Just existing -> pure existing
      Nothing -> deadlineAfter 2000000
     case dlRes of
      Left _ -> do
       let reasons = ["persistent-startup-cleanup-deadline-failed"]
       O.pendingRecordIssue pending "persistent-startup-cleanup-deadline-failed"
       O.quarantine rawOwner (Just child) reasons
       modifyMVar_ phaseVar (const (pure (PhaseQuarantined reasons)))
      Right cleanupDl -> do
       mWorker <- atomicModifyIORef' vWorkerCell (\cur -> (Nothing, cur))
       vDrained <- case mWorker of
        Nothing -> pure True
        Just (vTid, waitV) -> do
         killedV <- boundedByDl cleanupDl (killThread vTid)
         joinedV <- boundedByDl cleanupDl waitV
         pure (completed killedV && completed joinedV)
       cbDrained <- if vDrained then boundedByDl cleanupDl (drainCallbackGate cbGate) else pure (Right Nothing)
       wakeDrained <- if completed cbDrained then boundedByDl cleanupDl (drainWakeGate wg) else pure (Right Nothing)
       obsDrained <- if completed wakeDrained then boundedByDl cleanupDl (drainSessionScope scope) else pure (Right Nothing)
       if not (vDrained && completed cbDrained && completed wakeDrained && completed obsDrained) then do
        let reasons = if not vDrained then ["persistent-startup-verify-not-drained"] else ["persistent-startup-observation-not-drained"]
        O.pendingRecordIssue pending "persistent-startup-drain-incomplete"
        O.quarantine rawOwner (Just child) reasons
        modifyMVar_ phaseVar (const (pure (PhaseQuarantined reasons)))
       else do
        let extra = case curPhase of PhaseStarting -> []; _ -> ["persistent-interrupted"]
        (_, _, _) <- finishContainment pending cleanupDl Nothing child outTid outRes outH errTid errRes errH ph pid extra
        pure ()

  -- Retires a spawned child when stop was latched during PhaseStarting using ONLY
  -- the immutable StopDeadline minted at first requestSessionStop (never fresh 2s).
  retireLatchedStartupStop :: O.Pending -> Either ToolError AdmissionDeadline -> SessionObservation -> O.Child -> SessionScope -> WakeGate -> ThreadId -> IO ReaderResult -> Handle -> ThreadId -> IO ReaderResult -> Handle -> ProcessHandle -> ProcessID -> IO (Either SessionExit (a, SessionExit))
  retireLatchedStartupStop pending stopDlRes obs child scope wg outTid outRes outH errTid errRes errH ph pid = do
   closeCallbackGate cbGate stopReadyVar stopBell
   closeWakeGate wg
   closeSessionScope scope
   case stopDlRes of
    Left _ -> do
     let reasons = ["persistent-stop-deadline-mint-failed"]
     O.pendingRecordIssue pending "persistent-stop-deadline-mint-failed"
     O.quarantine rawOwner (Just child) reasons
     modifyMVar_ phaseVar (const (pure (PhaseQuarantined reasons)))
     pure (Left (ExitUncertain CleanupUncertain reasons))
    Right stopDl -> do
     cbDrained <- boundedByDl stopDl (drainCallbackGate cbGate)
     wakeDrained <- if completed cbDrained then boundedByDl stopDl (drainWakeGate wg) else pure (Right Nothing)
     obsDrained <- if completed wakeDrained then boundedByDl stopDl (drainSessionScope scope) else pure (Right Nothing)
     if not (completed cbDrained && completed wakeDrained && completed obsDrained) then do
      let reasons = ["persistent-startup-observation-not-drained"]
      O.pendingRecordIssue pending "persistent-startup-observation-not-drained"
      O.quarantine rawOwner (Just child) reasons
      modifyMVar_ phaseVar (const (pure (PhaseQuarantined reasons)))
      case asyncErrors cbDrained ++ asyncErrors wakeDrained ++ asyncErrors obsDrained of firstEx : _ -> throwIO firstEx; [] -> pure (Left (ExitUncertain CleanupUncertain reasons))
     else do
      (_, cleanupFailures, deferredAsync) <- finishContainment pending stopDl (Just obs) child outTid outRes outH errTid errRes errH ph pid []
      case deferredAsync of firstEx : _ -> throwIO firstEx; [] -> pure ()
      if null cleanupFailures then
       pure (Left (StartupRefused SessionClosed))
      else
       pure (Left (ExitUncertain CleanupUncertain cleanupFailures))

  -- If stop was latched concurrently during startup failure/refusal, honor that
  -- immutable StopDeadline; otherwise use emergency containment-only 2s cleanup
  -- (never admitting a live session or counting as completion within 28s/30s D).
  retireStartupOrLatchedStop :: O.Pending -> O.Child -> Maybe SessionObservation -> SessionScope -> WakeGate -> ThreadId -> IO ReaderResult -> Handle -> ThreadId -> IO ReaderResult -> Handle -> ProcessHandle -> ProcessID -> ToolError -> IO (Either SessionExit (a, SessionExit))
  retireStartupOrLatchedStop pending child maybeObs scope wg outTid outRes outH errTid errRes errH ph pid refusalErr = do
   mLatched <- peekGateStop cbGate
   closeCallbackGate cbGate stopReadyVar stopBell
   closeWakeGate wg
   closeSessionScope scope
   dlRes <- case mLatched of
    Just existing -> pure existing
    Nothing -> deadlineAfter 2000000
   case dlRes of
    Left _ -> do
     let reasons = ["persistent-startup-cleanup-deadline-failed"]
     O.pendingRecordIssue pending "persistent-startup-cleanup-deadline-failed"
     O.quarantine rawOwner (Just child) reasons
     modifyMVar_ phaseVar (const (pure (PhaseQuarantined reasons)))
     pure (Left (ExitUncertain CleanupUncertain reasons))
    Right cleanupDl -> do
     cbDrained <- boundedByDl cleanupDl (drainCallbackGate cbGate)
     wakeDrained <- if completed cbDrained then boundedByDl cleanupDl (drainWakeGate wg) else pure (Right Nothing)
     obsDrained <- if completed wakeDrained then boundedByDl cleanupDl (drainSessionScope scope) else pure (Right Nothing)
     if not (completed cbDrained && completed wakeDrained && completed obsDrained) then do
      let reasons = ["persistent-startup-observation-not-drained"]
      O.pendingRecordIssue pending "persistent-startup-observation-not-drained"
      O.quarantine rawOwner (Just child) reasons
      modifyMVar_ phaseVar (const (pure (PhaseQuarantined reasons)))
      case asyncErrors cbDrained ++ asyncErrors wakeDrained ++ asyncErrors obsDrained of firstEx : _ -> throwIO firstEx; [] -> pure (Left (ExitUncertain CleanupUncertain reasons))
     else do
      (_, cleanupFailures, deferredAsync) <- finishContainment pending cleanupDl maybeObs child outTid outRes outH errTid errRes errH ph pid []
      case deferredAsync of firstEx : _ -> throwIO firstEx; [] -> pure ()
      if null cleanupFailures then
       pure (Left (StartupRefused (case mLatched of Just _ -> SessionClosed; Nothing -> refusalErr)))
      else
       pure (Left (ExitUncertain CleanupUncertain cleanupFailures))

  retireStartupFailure :: O.Pending -> O.Child -> SessionScope -> WakeGate -> ThreadId -> IO ReaderResult -> Handle -> ThreadId -> IO ReaderResult -> Handle -> ProcessHandle -> ProcessID -> [Text] -> ToolError -> IO (Either SessionExit (a, SessionExit))
  retireStartupFailure pending child scope wg outTid outRes outH errTid errRes errH ph pid extraReasons errTag = do
   mLatched <- peekGateStop cbGate
   closeCallbackGate cbGate stopReadyVar stopBell
   closeWakeGate wg
   closeSessionScope scope
   dlRes <- case mLatched of
    Just existing -> pure existing
    Nothing -> deadlineAfter 2000000
   case dlRes of
    Left _ -> do
     let reasons = "persistent-startup-cleanup-deadline-failed" : extraReasons
     O.pendingRecordIssue pending "persistent-startup-cleanup-deadline-failed"
     O.quarantine rawOwner (Just child) reasons
     modifyMVar_ phaseVar (const (pure (PhaseQuarantined reasons)))
     pure (Left (ExitUncertain CleanupUncertain reasons))
    Right cleanupDl -> do
     cbDrained <- boundedByDl cleanupDl (drainCallbackGate cbGate)
     wakeDrained <- if completed cbDrained then boundedByDl cleanupDl (drainWakeGate wg) else pure (Right Nothing)
     obsDrained <- if completed wakeDrained then boundedByDl cleanupDl (drainSessionScope scope) else pure (Right Nothing)
     if not (completed cbDrained && completed wakeDrained && completed obsDrained) then do
      let reasons = "persistent-startup-observation-not-drained" : extraReasons
      O.pendingRecordIssue pending "persistent-startup-observation-not-drained"
      O.quarantine rawOwner (Just child) reasons
      modifyMVar_ phaseVar (const (pure (PhaseQuarantined reasons)))
      case asyncErrors cbDrained ++ asyncErrors wakeDrained ++ asyncErrors obsDrained of firstEx : _ -> throwIO firstEx; [] -> pure (Left (ExitUncertain CleanupUncertain reasons))
     else do
      (_, cleanupFailures, deferredAsync) <- finishContainment pending cleanupDl Nothing child outTid outRes outH errTid errRes errH ph pid extraReasons
      case deferredAsync of firstEx : _ -> throwIO firstEx; [] -> pure ()
      pure (Left (ExitUncertain errTag cleanupFailures))

  retireLive :: O.Pending -> Int -> Maybe SessionObservation -> O.Child -> SessionScope -> WakeGate -> ThreadId -> IO ReaderResult -> Handle -> ThreadId -> IO ReaderResult -> Handle -> ProcessHandle -> ProcessID -> Either SomeException a -> IO (Either SessionExit (a, SessionExit))
  retireLive pending liveStopMicros expectedObs child scope wg outTid outRes outH errTid errRes errH ph pid bodyResult = do
   stopDlRes <- beginStopGateAndDeadline cbGate stopReadyVar stopBell liveStopMicros
   closeWakeGate wg
   closeSessionScope scope
   case stopDlRes of
    Left _ -> do
     let reasons = ["persistent-stop-deadline-mint-failed"]
     O.pendingRecordIssue pending "persistent-stop-deadline-mint-failed"
     O.quarantine rawOwner (Just child) reasons
     modifyMVar_ phaseVar (const (pure (PhaseQuarantined reasons)))
     case asyncErrors bodyResult of firstEx : _ -> throwIO firstEx; [] -> pure (Left (ExitUncertain CleanupUncertain reasons))
    Right stopDl -> do
     cbDrained <- boundedByDl stopDl (hook "persistent-callback-drain" >> drainCallbackGate cbGate)
     if not (completed cbDrained) then do
      let reasons = ["persistent-callback-not-drained"]
      O.pendingRecordIssue pending "persistent-callback-not-drained"
      O.quarantine rawOwner (Just child) reasons
      modifyMVar_ phaseVar (const (pure (PhaseQuarantined reasons)))
      case asyncErrors bodyResult ++ asyncErrors cbDrained of
       firstEx : _ -> throwIO firstEx
       [] -> pure (Left (ExitUncertain CleanupUncertain reasons))
     else do
      wakeDrained <- boundedByDl stopDl (hook "persistent-wake-drain" >> drainWakeGate wg)
      if not (completed wakeDrained) then do
       let reasons = ["persistent-wake-not-drained"]
       O.pendingRecordIssue pending "persistent-wake-not-drained"
       O.quarantine rawOwner (Just child) reasons
       modifyMVar_ phaseVar (const (pure (PhaseQuarantined reasons)))
       case asyncErrors bodyResult ++ asyncErrors wakeDrained of
        firstEx : _ -> throwIO firstEx
        [] -> pure (Left (ExitUncertain CleanupUncertain reasons))
      else do
       obsDrained <- boundedByDl stopDl (hook "persistent-scope-invalidate" >> drainSessionScope scope)
       if not (completed obsDrained) then do
        let reasons = ["persistent-observation-not-drained"]
        O.pendingRecordIssue pending "persistent-observation-not-drained"
        O.quarantine rawOwner (Just child) reasons
        modifyMVar_ phaseVar (const (pure (PhaseQuarantined reasons)))
        case asyncErrors bodyResult ++ asyncErrors obsDrained of
         firstEx : _ -> throwIO firstEx
         [] -> pure (Left (ExitUncertain CleanupUncertain reasons))
       else do
        hook "persistent-after-operation-drain-before-reap"
        (capturedPair, cleanupFailures, deferredAsync) <- finishContainment pending stopDl expectedObs child outTid outRes outH errTid errRes errH ph pid []
        case asyncErrors bodyResult ++ deferredAsync of
         firstEx : _ -> throwIO firstEx
         [] -> pure ()
        case (bodyResult, cleanupFailures, capturedPair) of
         (Left ex, _, _) -> throwIO ex
         (_, _ : _, _) -> pure (Left (ExitUncertain CleanupUncertain cleanupFailures))
         (Right val, [], Just (Right stdoutBytes, Right stderrBytes)) ->
          pure (Right (val, LeaderReaped (Captured stdoutBytes stderrBytes)))
         (Right _, [], Just (Left readerErr, _)) ->
          pure (Left (ExitUncertain readerErr ["stdout-reader-fault"]))
         (Right _, [], Just (_, Left readerErr)) ->
          pure (Left (ExitUncertain readerErr ["stderr-reader-fault"]))
         (Right _, [], Nothing) ->
          pure (Left (ExitUncertain OutputUnavailable ["persistent-output-unavailable"]))

  finishContainment :: O.Pending -> AdmissionDeadline -> Maybe SessionObservation -> O.Child -> ThreadId -> IO ReaderResult -> Handle -> ThreadId -> IO ReaderResult -> Handle -> ProcessHandle -> ProcessID -> [Text] -> IO (Maybe (Either ToolError B.ByteString, Either ToolError B.ByteString), [Text], [SomeException])
  finishContainment pending stopDl expectedObs child outTid outRes outH errTid errRes errH ph pid extraFailures = do
   reaped <- try (terminateLeaderDl stopDl expectedObs ph pid) :: IO (Either SomeException ExitCode)
   let leaderWasReaped = either (const False) (const True) reaped
   closePfd <-
    if leaderWasReaped then
     closeOwnedPidfdDl stopDl pending
    else do
     O.pendingRecordIssue pending "pidfd-retained-unreaped-leader"
     pure (Right (Just ()))
   captured <-
    if leaderWasReaped then
     boundedByDl stopDl ((,) <$> (readerOutput <$> outRes) <*> (readerOutput <$> errRes))
    else
     pure (Right Nothing)
   killedA <- boundedByDl stopDl (killThread outTid)
   killedB <- boundedByDl stopDl (killThread errTid)
   joinedA <- boundedByDl stopDl outRes
   joinedB <- boundedByDl stopDl errRes
   closeA <- if completed joinedA then boundedByDl stopDl (hClose outH) else pure (Right Nothing)
   closeB <-
    if completed joinedB then
     boundedByDlObserved
      stopDl
      (hook "qa-stderr-after-budget-sample")
      (hook "qa-stderr-after-close-return")
      (hook "qa-stderr-close-entered" >> hClose errH)
    else
     pure (Right Nothing)
   let stepFailures =
        [ T.pack label
        | (label, failed) <-
           [ ("leader-reap", not leaderWasReaped)
           , ("pidfd-close", leaderWasReaped && not (completed closePfd))
           , ("stdout-stop", not (completed killedA))
           , ("stderr-stop", not (completed killedB))
           , ("stdout-join", not (completed joinedA))
           , ("stderr-join", not (completed joinedB))
           , ("stdout-close", not (completed closeA))
           , ("stderr-close", not (completed closeB))
           ]
        , failed
        ]
       preBorrowFailures = extraFailures ++ stepFailures
   borrowStep <-
    if null preBorrowFailures then
     releaseBorrowBounded stopDl
    else
     pure (Right (Just True))
   let borrowFailures =
        if null preBorrowFailures && not (borrowReleased borrowStep) then
         ["borrow-release"]
        else
         []
       allFailures = preBorrowFailures ++ borrowFailures
       deferredAsync =
        asyncErrors reaped
         ++ asyncErrors closePfd
         ++ asyncErrors captured
         ++ asyncErrors killedA
         ++ asyncErrors killedB
         ++ asyncErrors joinedA
         ++ asyncErrors joinedB
         ++ asyncErrors closeA
         ++ asyncErrors closeB
         ++ asyncErrors borrowStep
   if null allFailures then do
    O.releaseBorrows rawOwner
    O.clearTransfers rawOwner
    O.clearCore rawOwner
    O.clearTickets rawOwner
    O.clearPending rawOwner
    O.settle rawOwner
    modifyMVar_ phaseVar (const (pure PhaseRetired))
   else do
    O.quarantine rawOwner (Just child) allFailures
    modifyMVar_ phaseVar (const (pure (PhaseQuarantined allFailures)))
   pure (either (const Nothing) id captured, allFailures, deferredAsync)

  readerOutput :: ReaderResult -> Either ToolError B.ByteString
  readerOutput = either (const (Left OutputUnavailable)) id
