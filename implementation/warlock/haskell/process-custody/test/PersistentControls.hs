{-# LANGUAGE OverloadedStrings #-}
-- Literal positive/negative persistent custody prerequisite controls wired
-- through the existing deadline-stop-controls suite in process-custody.cabal:
--   1. Exact 28s / <=30s StartBudget & StopBudget bounds + runSelectedDetailed coexistence
--   2. Stop-during-starting in PhaseAvailable (before withPersistentOwner): StopLatchedBeforeLive,
--      idempotent StopAlreadyRequested, zero child spawn, clean PersistentRetired
--   3. Stop-during-starting in PhaseStarting (while blocked in verifyReady): immediate wake via
--      stopReadyVar race and child reap under immutable latched StopDeadline (no 5s wait)
--   4. Stop-during-starting expired latched StopDeadline: proves zero fresh 2s grace minted;
--      aborts before pidfd_send_signal(SIGKILL) and quarantines ["leader-reap"]
--   5. Retained-peer-fd0 child-death wake (SocketOwner counterexample): parent retains open
--      duplicate stdin pipe endpoints so child exit produces zero EOF; withLiveSessionWakeSTM
--      wakes immediately with LiveWakeLeaderExited via verified SYS_pidfd_open + epoll
--   6. Stop wake + WakeGate drain before pidfd close + negative hung-wake quarantine
--   7. Lexical withLiveFrameAdmission / enterLiveFrameAction matching terra_q_lifetime_frame_admission.qnt:
--      distinct frameDl vs actionDl (action completes after frameDl expires while actionDl holds),
--      expired frameDl or expired actionDl refused pre-dispatch, single-attempt cap, stop before
--      enter refused pre-dispatch, stop/expiry after enter -> OperationOutcomeUnknown, escaped token refused
module PersistentControls (runPersistentControls, runPersistentControlsWithRegistry) where

import qualified SeededBatchHarness as SeededBatch
import Control.Concurrent (MVar, forkFinally, forkIO, newEmptyMVar, putMVar, readMVar, takeMVar, threadDelay, tryPutMVar)
import Control.Exception (SomeException, finally, mask_, toException)
import Control.Monad (unless, void, when)
import Data.Bits (shiftR, xor)
import Data.IORef (IORef, atomicModifyIORef', modifyIORef', newIORef, readIORef, writeIORef)
import Foreign.StablePtr (StablePtr, newStablePtr)
import Data.List (stripPrefix)
import Data.Word (Word64)
import GHC.Clock (getMonotonicTimeNSec)
import GHC.Conc (STM, atomically, orElse)
import System.Directory (doesFileExist, getTemporaryDirectory, removeFile)
import System.IO (IOMode(ReadMode), hClose, openFile, openTempFile)
import System.Posix.IO (closeFd, createPipe, dup, fdToHandle)
import System.Posix.Types (ProcessID)
import System.Timeout (timeout)
import Text.Read (readMaybe)
import Warlock.Capture.Process.Internal
 ( Captured(..)
 , OwnerStatus(..)
 , SelectedOutcome(..)
 , SessionObservation(..)
 , ToolError(..)
 , deadlineAbsoluteNs
 , deadlineAfter
 , deadlineFromAbsoluteNsAt
 , leaderExited
 , newOwner
 , runSelectedDetailed
 , selectedFixture
 , remainingMicros
 , status
 )
import Warlock.Capture.Process.Persistent
 ( ActionBudget
 , LiveFrameAdmission
 , LiveFrameBatch
 , LiveOperationFailure(..)
 , LiveSession
 , LiveWakeReason(..)
 , PersistentOwner
 , PersistentStatus(..)
 , PidfdCustody(..)
 , SessionExit(..)
 , StopDeadlineObservation(..)
 , StopReceipt(..)
 , actionBudgetMicros
 , actionBudgetMicrosValue
 , beginLiveFrameBatch
 , beginLiveFrameRequestBatch
 , defaultPersistentActionBudget
 , enterLiveBatchAttachment
 , enterLiveBatchAttachmentRequest
 , enterLiveBatchBudgetedAction
 , enterLiveBatchRequest
 , enterLiveFrameAction
 , liveSessionStopRequestedSTM
 , maxLiveFrameBatchRequests
 , maxPersistentActionBudgetMicros
 , newPersistentOwner
 , observeLiveSession
 , observeLiveStartup
 , persistentPidfdCustody
 , persistentStatus
 , persistentUnderlyingStatus
 , requestSessionStop
 , runBoundedLiveOperation
 , startBudgetAfter
 , startBudgetDeadline
 , startBudgetFromDeadline
 , stopBudgetMicros
 , stopBudgetMicrosValue
 , tryPersistentStopDeadline
 , withLiveFrameAdmission
 , withLiveSessionWakeSTM
 , withPersistentOwner
 )
import Warlock.Capture.Process.Persistent.Internal
 ( persistentFixture
 , borrowReleasedReceipt
 , withPersistentOwnerHook
 )

check :: String -> Bool -> IO ()
check label ok = unless ok (ioError (userError ("PersistentControls failed: " ++ label)))

boundedTest :: String -> IO a -> IO a
boundedTest label act = do
 out <- timeout 2000000 act
 maybe (ioError (userError ("PersistentControls timed out: " ++ label))) pure out

newMarker :: IO FilePath
newMarker = do
 dir <- getTemporaryDirectory
 (path, h) <- openTempFile dir "persistent-prereq-ready"
 hClose h
 removeFile path
 pure path

cleanMarker :: FilePath -> IO ()
cleanMarker path = do
 ex <- doesFileExist path
 whenExists ex (removeFile path)
 where
  whenExists True act = act
  whenExists False _ = pure ()

awaitMarker :: FilePath -> Int -> IO Bool
awaitMarker _ 0 = pure False
awaitMarker path n = do
 ready <- doesFileExist path
 if ready then pure True else threadDelay 10000 >> awaitMarker path (n - 1)

-- Observes child self-exit into zombie state via leaderExited (waitid WNOWAIT)
-- without reaping any quarantined ProcessHandle or claiming closed pipes/pidfd
-- on quarantined owners; quarantined PersistentOwner values remain retained
-- un-reaped through DeadlineStop.main exit.
awaitFixtureExited :: ProcessID -> IO ()
awaitFixtureExited pid = do
 dead <- leaderExited pid
 if dead then pure () else threadDelay 10000 >> awaitFixtureExited pid

nextSeed :: Word64 -> (Word64, Word64)
nextSeed s =
 let s' = s + 0x9E3779B97F4A7C15
     z1 = (s' `xor` (s' `shiftR` 30)) * 0xBF58476D1CE4E5B9
     z2 = (z1 `xor` (z1 `shiftR` 27)) * 0x94D049BB133111EB
     val = z2 `xor` (z2 `shiftR` 31)
 in (val, s')

runPersistentControls :: FilePath -> IO ()
runPersistentControls childExe = do
 outerRegistry <- newIORef ([] :: [(PersistentOwner, StablePtr PersistentOwner)])
 runPersistentControlsWithRegistry outerRegistry childExe

-- Pre-registers every PersistentOwner + an unreleased GHC RTS StablePtr into
-- the caller-owned outer IORef BEFORE acquisition/spawn begins so every owner
-- remains strongly rooted across both normal return and mid-flight exceptions.
runPersistentControlsWithRegistry :: IORef [(PersistentOwner, StablePtr PersistentOwner)] -> FilePath -> IO ()
runPersistentControlsWithRegistry outerRegistry childExe = do
 let allocOwner = mask_ $ do
      o <- newPersistentOwner
      sp <- newStablePtr o
      atomicModifyIORef' outerRegistry (\xs -> ((o, sp) : xs, ()))
      pure o
 -- 1. Pure 28s / <=30s StartBudget & StopBudget invariants + SplitMix64 property.
 let t0 = 500000000000 :: Word64
 case deadlineFromAbsoluteNsAt t0 "528000000000" of
  Right d28 -> do
   let sb28 = startBudgetFromDeadline d28
   check "exact-28s-start-budget-preserved" (deadlineAbsoluteNs (startBudgetDeadline sb28) == "528000000000")
  Left _ -> check "exact-28s-start-budget-preserved" False
 check "beyond-30s-start-refused" (deadlineFromAbsoluteNsAt t0 "530000000001" == Left BadArguments)
 check "stop-budget-bounds"
  (stopBudgetMicros 0 == Left BadArguments
    && stopBudgetMicros (-1) == Left BadArguments
    && stopBudgetMicros 30000001 == Left BadArguments
    && fmap stopBudgetMicrosValue (stopBudgetMicros 2000000) == Right 2000000)

 let goProp 0 _ = pure ()
     goProp n sd = do
      let (raw, sd') = nextSeed sd
          cand = fromIntegral (raw `mod` 40000000) - 5000000 :: Int
      case stopBudgetMicros cand of
       Right b -> check "seeded-valid-stop-budget" (cand >= 1 && cand <= 30000000 && stopBudgetMicrosValue b == cand)
       Left e -> check "seeded-invalid-stop-budget" ((cand <= 0 || cand > 30000000) && e == BadArguments)
      goProp (n - 1 :: Int) sd'
 goProp 128 0x5741524C4F434B33

 stop2s <- either (ioError . userError . show) pure (stopBudgetMicros 2000000)
 stop800ms <- either (ioError . userError . show) pure (stopBudgetMicros 800000)
 stop60ms <- either (ioError . userError . show) pure (stopBudgetMicros 60000)

 -- Coexistence: diagnostic runSelectedDetailed still expires at original D.
 diagOwner <- newOwner
 diagMarker <- newMarker
 diagDl <- deadlineAfter 120000 >>= either (ioError . userError . show) pure
 diagIn <- openFile "/dev/null" ReadMode
 diagOut <- runSelectedDetailed diagOwner (selectedFixture childExe [diagMarker] diagIn) 4096 diagDl (\_ -> threadDelay 250000 >> pure (Right ()))
 cleanMarker diagMarker
 diagSt <- status diagOwner
 check "diagnostic-runSelectedDetailed-expires-at-original-D"
  (selectedOperation diagOut == Left TimedOut && diagSt == Available)

 -- 2. Stop-during-starting in PhaseAvailable (before withPersistentOwner).
 preStopOwner <- allocOwner
 preReceipt1 <- requestSessionStop preStopOwner stop2s
 preReceipt2 <- requestSessionStop preStopOwner stop2s
 check "stop-before-start-latches-once"
  (preReceipt1 == StopLatchedBeforeLive && preReceipt2 == StopAlreadyRequested)
 preMarker <- newMarker
 preIn <- openFile "/dev/null" ReadMode
 preStart <- startBudgetAfter 1000000 >>= either (ioError . userError . show) pure
 preRes <- withPersistentOwner preStopOwner (persistentFixture childExe [preMarker] preIn) 4096 preStart stop2s (\_ -> pure (Right ())) (\_ -> pure ())
 hClose preIn
 preMarkerExists <- doesFileExist preMarker
 prePhase <- persistentStatus preStopOwner
 preRaw <- persistentUnderlyingStatus preStopOwner
 check "stop-in-PhaseAvailable-prevents-spawn-and-settles"
  (preRes == Left (StartupRefused SessionClosed)
    && not preMarkerExists
    && prePhase == PersistentRetired
    && preRaw == Available)

 -- 3. Stop-during-starting in PhaseStarting while verifyReady blocks (wakes immediately, reaps under immutable latched D).
 startingStopOwner <- allocOwner
 startingMarker <- newMarker
 startingIn <- openFile "/dev/null" ReadMode
 startingStart <- startBudgetAfter 5000000 >>= either (ioError . userError . show) pure
 verifyStarted <- newEmptyMVar
 finishesRef <- newIORef False
 neverVar <- newEmptyMVar
 tBeforeStartStop <- getMonotonicTimeNSec
 startingDone <- newEmptyMVar
 _ <- forkIO $ do
  r <- withPersistentOwnerHook
   startingStopOwner
   (persistentFixture childExe [startingMarker] startingIn)
   4096
   startingStart
   stop2s
   (\_ -> do
     _ <- awaitMarker startingMarker 150
     _ <- takeMVar neverVar
     pure (Right ()))
   (\_ -> writeIORef finishesRef True)
   (\stage -> if stage == "persistent-verify-ready-started" then void (putMVar verifyStarted ()) else pure ())
  putMVar startingDone r
 takeMVar verifyStarted
 _ <- awaitMarker startingMarker 150
 startingStopReceipt <- requestSessionStop startingStopOwner stop800ms
 startingStopDup <- requestSessionStop startingStopOwner stop800ms
 startingRes <- takeMVar startingDone
 tAfterStartStop <- getMonotonicTimeNSec
 liveEnteredOnStartStop <- readIORef finishesRef
 startingPhase <- persistentStatus startingStopOwner
 startingRaw <- persistentUnderlyingStatus startingStopOwner
 cleanMarker startingMarker
 let elapsedStartStopMs = (tAfterStartStop - tBeforeStartStop) `div` 1000000
 check "stop-during-PhaseStarting-interrupts-verifyReady-and-reaps-under-latched-D"
  (startingStopReceipt == StopLatchedBeforeLive
    && startingStopDup == StopAlreadyRequested
    && startingRes == Left (StartupRefused SessionClosed)
    && not liveEnteredOnStartStop
    && elapsedStartStopMs < 2000
    && startingPhase == PersistentRetired
    && startingRaw == Available)

 -- 4. Stop-during-starting expired latched StopDeadline: zero fresh 2s grace minted; aborts before SIGKILL and quarantines.
 expStartOwner <- allocOwner
 expStartMarker <- newMarker
 expStartIn <- openFile "/dev/null" ReadMode
 expStartBudget <- startBudgetAfter 5000000 >>= either (ioError . userError . show) pure
 expVerifyStarted <- newEmptyMVar
 expHoldVerify <- newEmptyMVar
 expPidRef <- newIORef (Nothing :: Maybe ProcessID)
 expUnsignaledRef <- newIORef False
 expDone <- newEmptyMVar
 _ <- forkIO $ do
  r <- withPersistentOwnerHook
   expStartOwner
   (persistentFixture childExe [expStartMarker, "exit-when-removed"] expStartIn)
   4096
   expStartBudget
   stop2s
   (\obs -> do
     writeIORef expPidRef (Just (observedPid obs))
     _ <- awaitMarker expStartMarker 150
     _ <- takeMVar expHoldVerify
     pure (Right ()))
   (\_ -> pure ())
   (\stage ->
     if stage == "persistent-verify-ready-started" then
      void (putMVar expVerifyStarted ())
     else if stage == "persistent-before-leader-kill" then
      threadDelay 90000
     else pure ())
  putMVar expDone r
 takeMVar expVerifyStarted
 _ <- awaitMarker expStartMarker 150
 expStopReceipt <- requestSessionStop expStartOwner stop60ms
 expRes <- mask_ $ do
  r <- takeMVar expDone
  mPid <- readIORef expPidRef
  case mPid of
   Nothing -> pure ()
   Just p -> do
    dead <- leaderExited p
    writeIORef expUnsignaledRef (not dead)
  pure r
 mLeakPid <- readIORef expPidRef
 expUnsignaled <- readIORef expUnsignaledRef
 expPhase <- persistentStatus expStartOwner
 expRaw <- persistentUnderlyingStatus expStartOwner
 expCustody <- persistentPidfdCustody expStartOwner
 cleanMarker expStartMarker
 case mLeakPid of
  Nothing -> check "exp-start-pid-observed" False
  Just p -> boundedTest "exp-start-fixture-self-exit" (awaitFixtureExited p)
 expCustodyAfter <- persistentPidfdCustody expStartOwner
 check "expired-latched-startup-stop-D-never-mints-2s-and-quarantines-before-sigkill"
  (expStopReceipt == StopLatchedBeforeLive
    && expUnsignaled
    && expCustodyAfter == expCustody
    && (case expCustody of PidfdKnownOpen p (Just _) -> Just p == mLeakPid; _ -> False)
    && (case expRes of Left (ExitUncertain CleanupUncertain rs) -> "leader-reap" `elem` rs && "pidfd-close" `notElem` rs; _ -> False)
    && (case expPhase of PersistentQuarantined rs -> "leader-reap" `elem` rs && "pidfd-close" `notElem` rs; _ -> False)
    && (case expRaw of Quarantined rs -> "leader-reap" `elem` rs && "pidfd-close" `notElem` rs; _ -> False))

 -- 5. Retained-peer-fd0 child-death wake (SocketOwner counterexample):
 -- Parent retains BOTH readDupFd and writeFd open across child exit so zero pipe/socket EOF occurs;
 -- withLiveSessionWakeSTM wakes immediately with LiveWakeLeaderExited via SYS_pidfd_open + epoll.
 (pipeReadFd, pipeWriteFd) <- createPipe
 retainedReadDup <- dup pipeReadFd
 childStdinHandle <- fdToHandle pipeReadFd
 deathOwner <- allocOwner
 deathMarker <- newMarker
 deathStart <- startBudgetAfter 2000000 >>= either (ioError . userError . show) pure
 deathWakeRef <- newIORef (Nothing :: Maybe (Either ToolError LiveWakeReason))
 deathRes <- withPersistentOwner
  deathOwner
  (persistentFixture childExe [deathMarker, "exit-soon"] childStdinHandle)
  4096
  deathStart
  stop2s
  (\_ -> do
    ok <- awaitMarker deathMarker 150
    pure (if ok then Right () else Left TimedOut))
  (\session -> do
    woke <- withLiveSessionWakeSTM session $ \wakeSTM -> atomically wakeSTM
    writeIORef deathWakeRef (Just woke))
 closeFd retainedReadDup
 closeFd pipeWriteFd
 cleanMarker deathMarker
 deathWoke <- readIORef deathWakeRef
 deathPhase <- persistentStatus deathOwner
 deathRaw <- persistentUnderlyingStatus deathOwner
 check "retained-fd0-child-exit-wakes-with-LiveWakeLeaderExited-and-reaps"
  (deathWoke == Just (Right LiveWakeLeaderExited)
    && (case deathRes of Right ((), LeaderReaped cap) -> output cap == "READY\n"; _ -> False)
    && deathPhase == PersistentRetired
    && deathRaw == Available)

 -- 6. Stop wake + lexical withLiveFrameAdmission / enterLiveFrameAction (all .qnt properties).
 escapedSessionRef <- newIORef (Nothing :: Maybe LiveSession)
 escapedAdmRef <- newIORef (Nothing :: Maybe LiveFrameAdmission)
 frameOwner <- allocOwner
 frameMarker <- newMarker
 frameIn <- openFile "/dev/null" ReadMode
 frameStart <- startBudgetAfter 250000 >>= either (ioError . userError . show) pure
 frameStopTrace <- newIORef ([] :: [(String,StopDeadlineObservation,Maybe Int)])
 frameRes <- withPersistentOwnerHook
  frameOwner
  (persistentFixture childExe [frameMarker] frameIn)
  4096
  frameStart
  stop2s
  (\_ -> do
    ok <- awaitMarker frameMarker 150
    pure (if ok then Right () else Left TimedOut))
  (\session -> do
    writeIORef escapedSessionRef (Just session)
    -- Startup observation succeeds before 250ms startDl expires, then refuses after idle.
    obsStartOk <- observeLiveStartup session
    check "observeLiveStartup-ok-while-startDl-positive" (case obsStartOk of Right o -> observedPid o > 0; Left _ -> False)
    threadDelay 320000
    obsStartExp <- observeLiveStartup session
    freshObsDl <- deadlineAfter 300000 >>= either (ioError . userError . show) pure
    obsLiveOk <- observeLiveSession session freshObsDl
    check "observeLiveStartup-refuses-after-startDl-expired-while-observeLiveSession-succeeds"
     (obsStartExp == Left TimedOut && (case obsLiveOk of Right o -> observedPid o > 0; Left _ -> False))

    -- Escaped wakeSTM after lexical withLiveSessionWakeSTM returns yields tombstone LiveWakeScopeExited.
    escapedWakeRes <- withLiveSessionWakeSTM session pure
    case escapedWakeRes of
     Left _ -> check "escaped-wakeSTM-captured" False
     Right escapedSTM -> do
      tombstone <- atomically escapedSTM
      check "escaped-wakeSTM-returns-LiveWakeScopeExited" (tombstone == LiveWakeScopeExited)

    -- (a) Positive distinct frameDl vs actionDl: frameDl (60ms) expires DURING action while actionDl (600ms) holds!
    frameShort <- deadlineAfter 60000 >>= either (ioError . userError . show) pure
    actionLong <- deadlineAfter 600000 >>= either (ioError . userError . show) pure
    posDistinct <- withLiveFrameAdmission session $ \adm -> do
     writeIORef escapedAdmRef (Just adm)
     firstTry <- enterLiveFrameAction adm frameShort actionLong (threadDelay 100000 >> pure (Right ("distinct-ok" :: String)))
     secondTry <- enterLiveFrameAction adm actionLong actionLong (pure (Right ("dup" :: String)))
     pure (firstTry, secondTry)
    check "distinct-frameDl-vs-actionDl-and-single-attempt-cap"
     (posDistinct == Right (Right "distinct-ok", Left (OperationRefusedPreDispatch OwnerBusy)))

    -- Escaped LiveFrameAdmission after lexical scope exits is refused pre-dispatch.
    mEscAdm <- readIORef escapedAdmRef
    case mEscAdm of
     Nothing -> check "escaped-adm-captured" False
     Just escAdm -> do
      freshDl <- deadlineAfter 300000 >>= either (ioError . userError . show) pure
      escTry <- enterLiveFrameAction escAdm freshDl freshDl (pure (Right ()))
      check "escaped-LiveFrameAdmission-refused" (escTry == Left (OperationRefusedPreDispatch SessionClosed))

    -- (b) Expired frameDl before entry refuses pre-dispatch even when actionDl is valid.
    expFrame <- deadlineAfter 20000 >>= either (ioError . userError . show) pure
    validAction <- deadlineAfter 500000 >>= either (ioError . userError . show) pure
    threadDelay 35000
    refusedExpFrame <- withLiveFrameAdmission session $ \adm ->
     enterLiveFrameAction adm expFrame validAction (pure (Right ()))
    check "expired-frameDl-refused-pre-dispatch"
     (refusedExpFrame == Right (Left (OperationRefusedPreDispatch TimedOut)))

    -- (c) Expired actionDl before entry refuses pre-dispatch even when frameDl is valid.
    validFrame <- deadlineAfter 500000 >>= either (ioError . userError . show) pure
    expAction <- deadlineAfter 20000 >>= either (ioError . userError . show) pure
    threadDelay 35000
    refusedExpAction <- withLiveFrameAdmission session $ \adm ->
     enterLiveFrameAction adm validFrame expAction (pure (Right ()))
    check "expired-actionDl-refused-pre-dispatch"
     (refusedExpAction == Right (Left (OperationRefusedPreDispatch TimedOut)))

    -- (d) Action exceeding actionDl maps to OperationOutcomeUnknown TimedOut.
    validFrame2 <- deadlineAfter 500000 >>= either (ioError . userError . show) pure
    shortAction <- deadlineAfter 40000 >>= either (ioError . userError . show) pure
    unknownTimeout <- withLiveFrameAdmission session $ \adm ->
     enterLiveFrameAction adm validFrame2 shortAction (threadDelay 90000 >> pure (Right ()))
    check "expired-entered-action-maps-to-OperationOutcomeUnknown"
     (unknownTimeout == Right (Left (OperationOutcomeUnknown TimedOut)))

    -- (e) Left from entered callback maps to OperationOutcomeUnknown.
    validFrame3 <- deadlineAfter 500000 >>= either (ioError . userError . show) pure
    unknownLeft <- runBoundedLiveOperation session validFrame3 (pure (Left SpawnOrIO) :: IO (Either ToolError ()))
    check "callback-Left-maps-to-OperationOutcomeUnknown"
     (unknownLeft == Left (OperationOutcomeUnknown SpawnOrIO))

    -- (f) Real epoll-registered withLiveSessionWakeSTM preempted by async requestSessionStop
    -- while a LiveFrameAdmission is in Framing (proving both epoll unregister + admittedBeforeStopDrainsWithoutDispatch).
    stmIdleBefore <- atomically ((liveSessionStopRequestedSTM session >> pure True) `orElse` pure False)
    check "stm-stop-idle-before-stop" (not stmIdleBefore)
    validFrame4 <- deadlineAfter 500000 >>= either (ioError . userError . show) pure
    stopDuringFraming <- withLiveFrameAdmission session $ \adm -> do
     _ <- forkIO (threadDelay 30000 >> void (requestSessionStop frameOwner stop2s))
     woke <- withLiveSessionWakeSTM session $ \wakeSTM -> atomically wakeSTM
     tryEnterAfterStop <- enterLiveFrameAction adm validFrame4 validFrame4 (pure (Right ()))
     pure (woke, tryEnterAfterStop)
    stmAfterStop <- atomically ((liveSessionStopRequestedSTM session >> pure True) `orElse` pure False)
    postStopAdm <- withLiveFrameAdmission session (\_ -> pure ())
    check "epoll-stop-wake-and-stop-during-framing-refuses-pre-dispatch"
     (stopDuringFraming == Right (Right LiveWakeStopRequested, Left (OperationRefusedPreDispatch SessionClosed))
       && stmAfterStop
       && postStopAdm == Left SessionClosed))
  (\stage -> when (stage `elem`
    [ "persistent-before-leader-exit-probe", "persistent-leader-already-exited"
    , "persistent-before-leader-observation", "persistent-leader-observation-invalid"
    , "persistent-before-owned-handle-probe", "persistent-owned-handle-no-exit", "persistent-owned-handle-awaiting-natural-exit"
    , "persistent-owned-handle-probe-timed-out", "persistent-owned-handle-reap-after-stop-deadline"
    , "persistent-before-leader-kill", "persistent-before-owned-leader-wait"
    , "persistent-owned-leader-wait-timed-out" ]) $ do
     observedStop <- tryPersistentStopDeadline frameOwner
     left <- case observedStop of StopDeadlineLatched deadline -> Just <$> remainingMicros deadline; _ -> pure Nothing
     modifyIORef' frameStopTrace (++ [(stage,observedStop,left)]))
 cleanMarker frameMarker
 framePhase <- persistentStatus frameOwner
 frameRaw <- persistentUnderlyingStatus frameOwner
 frameCustody <- persistentPidfdCustody frameOwner
 frameTrace <- readIORef frameStopTrace
 check ("frame-session-settled-cleanly: result=" ++ show frameRes ++ "; phase=" ++ show framePhase ++ "; raw=" ++ show frameRaw ++ "; pidfd=" ++ show frameCustody ++ "; trace=" ++ show frameTrace)
  ((case frameRes of Right ((), LeaderReaped cap) -> output cap == "READY\n"; _ -> False)
    && framePhase == PersistentRetired
    && frameRaw == Available)
 putStrLn ("PASS frame-session clean retirement; owned-handle natural-exit wait=" ++ show (any (\(stage,_,_) -> stage=="persistent-owned-handle-awaiting-natural-exit") frameTrace))

 mEscSession <- readIORef escapedSessionRef
 case mEscSession of
  Nothing -> check "escaped-session-captured" False
  Just escSess -> do
   escWake <- withLiveSessionWakeSTM escSess (\_ -> pure ())
   escAdm <- withLiveFrameAdmission escSess (\_ -> pure ())
   check "escaped-LiveSession-refused" (escWake == Left SessionClosed && escAdm == Left SessionClosed)

 -- 7. Negative hung-wake-drain quarantine control: WakeGate callback refusing to exit past StopBudget
 -- quarantines ["persistent-wake-not-drained"] without closing pidfd underneath epoll or reaping child.
 hungWakeOwner <- allocOwner
 hungWakeMarker <- newMarker
 hungWakeIn <- openFile "/dev/null" ReadMode
 hungWakeStart <- startBudgetAfter 1000000 >>= either (ioError . userError . show) pure
 wakeEntered <- newEmptyMVar
 releaseHungWake <- newEmptyMVar
 hungWakeDone <- newEmptyMVar :: IO (MVar (Either SomeException (Either ToolError ())))
 hungPidRef <- newIORef (Nothing :: Maybe ProcessID)
 hungWakeRes <- withPersistentOwnerHook
  hungWakeOwner
  (persistentFixture childExe [hungWakeMarker, "exit-when-removed"] hungWakeIn)
  4096
  hungWakeStart
  stop60ms
  (\obs -> do
    writeIORef hungPidRef (Just (observedPid obs))
    ok <- awaitMarker hungWakeMarker 150
    pure (if ok then Right () else Left TimedOut))
  (\session -> do
    _ <- forkFinally
     (withLiveSessionWakeSTM session (\_ -> takeMVar releaseHungWake))
     (putMVar hungWakeDone)
    boundedTest "hung-wake-entered" (takeMVar wakeEntered))
  (\stage -> if stage == "persistent-wake-registered" then void (tryPutMVar wakeEntered ()) else pure ())
 mHungPid <- readIORef hungPidRef
 stillAliveOnWakeQuarantine <- case mHungPid of
  Nothing -> pure False
  Just p -> not <$> leaderExited p
 hungCustody <- persistentPidfdCustody hungWakeOwner
 hungPhase <- persistentStatus hungWakeOwner
 hungRaw <- persistentUnderlyingStatus hungWakeOwner
 void (tryPutMVar releaseHungWake ())
 _ <- boundedTest "hung-wake-worker-exit" (readMVar hungWakeDone)
 cleanMarker hungWakeMarker
 case mHungPid of
  Nothing -> check "hung-wake-pid-observed" False
  Just p -> boundedTest "hung-wake-fixture-self-exit" (awaitFixtureExited p)
 check "hung-wake-drain-quarantines-without-closing-pidfd-or-reaping"
  (stillAliveOnWakeQuarantine
    && (case hungCustody of PidfdKnownOpen p (Just _) -> Just p == mHungPid; _ -> False)
    && hungWakeRes == Left (ExitUncertain CleanupUncertain ["persistent-wake-not-drained"])
    && hungPhase == PersistentQuarantined ["persistent-wake-not-drained"]
    && hungRaw == Quarantined ["persistent-wake-not-drained"])

 -- 8. Forked enterLiveFrameAction overlapping withLiveFrameAdmission return (UAF race regression):
 -- frameBody forks enterLiveFrameAction and returns immediately while act is still in flight;
 -- retireLive must block in CallbackGate drain until the forked act finishes BEFORE reaping child.
 overlapOwner <- allocOwner
 overlapMarker <- newMarker
 overlapIn <- openFile "/dev/null" ReadMode
 overlapStart <- startBudgetAfter 2000000 >>= either (ioError . userError . show) pure
 forkedEntered <- newEmptyMVar
 releaseForked <- newEmptyMVar
 forkedDone <- newEmptyMVar
 drainBeforeReapRef <- newIORef False
 childAliveDuringForkRef <- newIORef False
 overlapPidRef <- newIORef (Nothing :: Maybe ProcessID)
 overlapRes <- withPersistentOwnerHook
  overlapOwner
  (persistentFixture childExe [overlapMarker] overlapIn)
  4096
  overlapStart
  stop2s
  (\obs -> do
    writeIORef overlapPidRef (Just (observedPid obs))
    ok <- awaitMarker overlapMarker 150
    pure (if ok then Right () else Left TimedOut))
  (\session -> do
    forkDl <- deadlineAfter 1500000 >>= either (ioError . userError . show) pure
    admOut <- withLiveFrameAdmission session $ \adm -> do
     _ <- forkIO $ do
      r <- enterLiveFrameAction adm forkDl forkDl $ do
       putMVar forkedEntered ()
       takeMVar releaseForked
       mPid <- readIORef overlapPidRef
       aliveNow <- case mPid of Nothing -> pure False; Just p -> not <$> leaderExited p
       reapReached <- readIORef drainBeforeReapRef
       writeIORef childAliveDuringForkRef (aliveNow && not reapReached)
       pure (Right ("overlap-drained" :: String))
      putMVar forkedDone r
     takeMVar forkedEntered
    check "outer-withLiveFrameAdmission-returned-while-forked-act-running" (admOut == Right ())
    void (forkIO (threadDelay 60000 >> putMVar releaseForked ())))
  (\stage ->
    if stage == "persistent-after-operation-drain-before-reap" then
     writeIORef drainBeforeReapRef True
    else pure ())
 forkedOutcome <- takeMVar forkedDone
 cleanMarker overlapMarker
 aliveDuringFork <- readIORef childAliveDuringForkRef
 drainReachedAfter <- readIORef drainBeforeReapRef
 overlapPhase <- persistentStatus overlapOwner
 overlapRaw <- persistentUnderlyingStatus overlapOwner
 check "forked-frame-action-outliving-withLiveFrameAdmission-drains-before-reap"
  (aliveDuringFork
    && drainReachedAfter
    && forkedOutcome == Left (OperationOutcomeUnknown SessionClosed)
    && (case overlapRes of Right ((), LeaderReaped cap) -> output cap == "READY\n"; _ -> False)
    && overlapPhase == PersistentRetired
    && overlapRaw == Available)

 -- 9. Post-open pidfd startDl expiry regression: c_pidfd_open succeeds and stores pfd in pidfdCell,
 -- then startDl expires before post-open observeChild finishes; finishContainment closes pfd cleanly.
 pidfdExpOwner <- allocOwner
 pidfdExpMarker <- newMarker
 pidfdExpIn <- openFile "/dev/null" ReadMode
 pidfdExpStart <- startBudgetAfter 120000 >>= either (ioError . userError . show) pure
 pidfdClosedRef <- newIORef False
 pidfdExpRes <- withPersistentOwnerHook
  pidfdExpOwner
  (persistentFixture childExe [pidfdExpMarker] pidfdExpIn)
  4096
  pidfdExpStart
  stop2s
  (\_ -> pure (Right ()))
  (\_ -> pure ())
  (\stage ->
    if stage == "persistent-after-pidfd-open" then
     threadDelay 160000
    else if stage == "persistent-before-pidfd-close" then
     writeIORef pidfdClosedRef True
    else pure ())
 cleanMarker pidfdExpMarker
 pidfdWasClosed <- readIORef pidfdClosedRef
 pidfdExpPhase <- persistentStatus pidfdExpOwner
 pidfdExpRaw <- persistentUnderlyingStatus pidfdExpOwner
 pidfdExpCustody <- persistentPidfdCustody pidfdExpOwner
 check "post-open-pidfd-startDl-expiry-closes-pidfdCell-and-retires"
  (pidfdWasClosed
    && pidfdExpCustody == PidfdClosed
    && pidfdExpRes == Left (StartupRefused TimedOut)
    && pidfdExpPhase == PersistentRetired
    && pidfdExpRaw == Available)

 -- 10. Fresh actionDl sample right before timeout: if actionDl expires between admission and
 -- timeout entry, act is NEVER invoked and enterLiveFrameAction returns OperationOutcomeUnknown TimedOut.
 freshSampleOwner <- allocOwner
 freshSampleMarker <- newMarker
 freshSampleIn <- openFile "/dev/null" ReadMode
 freshSampleStart <- startBudgetAfter 1000000 >>= either (ioError . userError . show) pure
 actInvokedRef <- newIORef False
 preTimeoutOutRef <- newIORef (Nothing :: Maybe (Either ToolError (Either LiveOperationFailure ())))
 freshSampleRes <- withPersistentOwnerHook
  freshSampleOwner
  (persistentFixture childExe [freshSampleMarker] freshSampleIn)
  4096
  freshSampleStart
  stop2s
  (\_ -> do
    ok <- awaitMarker freshSampleMarker 150
    pure (if ok then Right () else Left TimedOut))
  (\session -> do
    fDl <- deadlineAfter 500000 >>= either (ioError . userError . show) pure
    aDl <- deadlineAfter 50000 >>= either (ioError . userError . show) pure
    r <- withLiveFrameAdmission session $ \adm ->
     enterLiveFrameAction adm fDl aDl (writeIORef actInvokedRef True >> pure (Right ()))
    writeIORef preTimeoutOutRef (Just r))
  (\stage ->
    if stage == "persistent-before-action-timeout" then
     threadDelay 80000
    else pure ())
 cleanMarker freshSampleMarker
 actWasInvoked <- readIORef actInvokedRef
 preTimeoutOut <- readIORef preTimeoutOutRef
 check "expired-fresh-actionDl-before-timeout-never-invokes-act"
  (not actWasInvoked
    && preTimeoutOut == Just (Right (Left (OperationOutcomeUnknown TimedOut)))
    && (case freshSampleRes of Right ((), LeaderReaped cap) -> output cap == "READY\n"; _ -> False))

 -- 11. Post-action owned-liveness check (death TOCTOU closure): if owned child exits while act is
 -- running (without requestSessionStop), enterLiveFrameAction refuses Right val and returns OperationOutcomeUnknown.
 midDeathOwner <- allocOwner
 midDeathMarker <- newMarker
 midDeathIn <- openFile "/dev/null" ReadMode
 midDeathStart <- startBudgetAfter 1000000 >>= either (ioError . userError . show) pure
 midDeathOutRef <- newIORef (Nothing :: Maybe (Either ToolError (Either LiveOperationFailure String)))
 _ <- withPersistentOwner
  midDeathOwner
  (persistentFixture childExe [midDeathMarker, "exit-soon"] midDeathIn)
  4096
  midDeathStart
  stop2s
  (\_ -> do
    ok <- awaitMarker midDeathMarker 150
    pure (if ok then Right () else Left TimedOut))
  (\session -> do
    opDl <- deadlineAfter 800000 >>= either (ioError . userError . show) pure
    r <- withLiveFrameAdmission session $ \adm ->
     enterLiveFrameAction adm opDl opDl (threadDelay 160000 >> pure (Right "must-not-succeed"))
    writeIORef midDeathOutRef (Just r))
 cleanMarker midDeathMarker
 midDeathOut <- readIORef midDeathOutRef
 midDeathPhase <- persistentStatus midDeathOwner
 midDeathRaw <- persistentUnderlyingStatus midDeathOwner
 check "child-exit-during-entered-action-maps-to-OperationOutcomeUnknown-never-Right"
  (midDeathOut == Just (Right (Left (OperationOutcomeUnknown SessionClosed)))
    && midDeathPhase == PersistentRetired
    && midDeathRaw == Available)

 -- 12. Inner-bracket wake tombstone ordering: scopeExitedVar commits LiveWakeScopeExited
 -- inside bracket release BEFORE epoll unregister runs, eliminating the post-wakeBody
 -- / pre-finally window where an escaped STM could still observe live readiness.
 tombOwner <- allocOwner
 tombMarker <- newMarker
 tombIn <- openFile "/dev/null" ReadMode
 tombStart <- startBudgetAfter 1000000 >>= either (ioError . userError . show) pure
 tombEntered <- newEmptyMVar
 tombRelease <- newEmptyMVar
 escapedWakeMVar <- newEmptyMVar :: IO (MVar (STM LiveWakeReason))
 tombWorkerDone <- newEmptyMVar :: IO (MVar (Either SomeException (Either ToolError ())))
 tombDuringUnregRef <- newIORef (Nothing :: Maybe LiveWakeReason)
 tombRes <- withPersistentOwnerHook
  tombOwner
  (persistentFixture childExe [tombMarker] tombIn)
  4096
  tombStart
  stop2s
  (\_ -> do
    ok <- awaitMarker tombMarker 150
    pure (if ok then Right () else Left TimedOut))
  (\session -> do
    _ <- forkFinally
     (withLiveSessionWakeSTM session (putMVar escapedWakeMVar))
     (putMVar tombWorkerDone)
    (do
      escSTM <- boundedTest "capture-escaped-wake-stm" (takeMVar escapedWakeMVar)
      boundedTest "wake-tombstoned-hook-entered" (takeMVar tombEntered)
      duringUnreg <- boundedTest "sample-escaped-wake-during-unregister" (atomically escSTM)
      writeIORef tombDuringUnregRef (Just duringUnreg)
      void (tryPutMVar tombRelease ())
      wOut <- boundedTest "wake-tombstone-worker-done" (readMVar tombWorkerDone)
      check "wake-tombstone-worker-clean-exit" (case wOut of Right (Right ()) -> True; _ -> False))
     `finally` do
      void (tryPutMVar tombRelease ())
      settled <- timeout 2000000 (readMVar tombWorkerDone)
      case settled of
       Just _ -> pure ()
       Nothing -> do
        ioError (userError "PersistentControls timed out: wake-tombstone-worker-finally"))
  (\stage ->
    if stage == "persistent-wake-tombstoned-before-unregister" then do
     void (tryPutMVar tombEntered ())
     takeMVar tombRelease
    else pure ())
 cleanMarker tombMarker
 tombDuringUnreg <- readIORef tombDuringUnregRef
 tombPhase <- persistentStatus tombOwner
 tombRaw <- persistentUnderlyingStatus tombOwner
 tombCustody <- persistentPidfdCustody tombOwner
 check "inner-bracket-wake-tombstone-visible-before-unregister"
  (tombDuringUnreg == Just LiveWakeScopeExited
    && (case tombRes of Right ((), LeaderReaped cap) -> output cap == "READY\n"; _ -> False)
    && tombPhase == PersistentRetired
    && tombRaw == Available
    && tombCustody == PidfdClosed)

 -- 13. Sticky unregister-fault containment: injected failure before epoll unregister
 -- returns Left SpawnOrIO, synchronously latches stop + closes WakeGate/CallbackGate
 -- (refusing later wake/frame admissions), retains the WakeGate pin across drainWakeGate,
 -- quarantines ["persistent-wake-not-drained"] under the same capped StopBudget, and
 -- retains PidfdKnownOpen without closing pidfd underneath uncertain registration.
 unregFaultOwner <- allocOwner
 unregFaultMarker <- newMarker
 unregFaultIn <- openFile "/dev/null" ReadMode
 unregFaultStart <- startBudgetAfter 1000000 >>= either (ioError . userError . show) pure
 unregPidRef <- newIORef (Nothing :: Maybe ProcessID)
 unregProbesRef <- newIORef (False, False, False, False)
 unregRes <- withPersistentOwnerHook
  unregFaultOwner
  (persistentFixture childExe [unregFaultMarker, "exit-when-removed"] unregFaultIn)
  4096
  unregFaultStart
  stop60ms
  (\obs -> do
    writeIORef unregPidRef (Just (observedPid obs))
    ok <- awaitMarker unregFaultMarker 150
    pure (if ok then Right () else Left TimedOut))
  (\session -> do
    firstWake <- withLiveSessionWakeSTM session (\_ -> pure ())
    stoppedNow <- atomically ((liveSessionStopRequestedSTM session >> pure True) `orElse` pure False)
    secondWake <- withLiveSessionWakeSTM session (\_ -> pure ())
    laterFrame <- withLiveFrameAdmission session (\_ -> pure ())
    writeIORef unregProbesRef
     ( firstWake == Left SpawnOrIO
     , stoppedNow
     , secondWake == Left SessionClosed
     , laterFrame == Left SessionClosed
     ))
  (\stage ->
    if stage == "persistent-wake-tombstoned-before-unregister" then
     ioError (userError "injected-failure-before-unregister")
    else pure ())
 mUnregPid <- readIORef unregPidRef
 aliveAfterUnregQuarantine <- case mUnregPid of
  Nothing -> pure False
  Just p -> not <$> leaderExited p
 unregCustody <- persistentPidfdCustody unregFaultOwner
 unregPhase <- persistentStatus unregFaultOwner
 unregRaw <- persistentUnderlyingStatus unregFaultOwner
 cleanMarker unregFaultMarker
 case mUnregPid of
  Nothing -> check "unreg-fault-pid-observed" False
  Just p -> boundedTest "unreg-fault-fixture-self-exit" (awaitFixtureExited p)
 (uWakeErr, uStopLatched, uWakeClosed, uFrameClosed) <- readIORef unregProbesRef
 check "unregister-fault-retains-wake-pin-latches-stop-and-retains-known-open-pidfd"
  (uWakeErr
    && uStopLatched
    && uWakeClosed
    && uFrameClosed
    && aliveAfterUnregQuarantine
    && (case unregCustody of PidfdKnownOpen p (Just _) -> Just p == mUnregPid; _ -> False)
    && unregRes == Left (ExitUncertain CleanupUncertain ["persistent-wake-not-drained"])
    && unregPhase == PersistentQuarantined ["persistent-wake-not-drained"]
    && unregRaw == Quarantined ["persistent-wake-not-drained"])

 let expectedExpiredCloseFailures =
      [ "pidfd-close"
      , "stdout-stop"
      , "stderr-stop"
      , "stdout-join"
      , "stderr-join"
      , "stdout-close"
      , "stderr-close"
      ]

 -- 14. Bounded pre-close StopDeadline expiry: precheck hook is bounded by the same
 -- immutable StopDeadline; on expiry closeFd is skipped, pidfd custody stays
 -- PidfdKnownOpen, and remaining boundedByDl steps fail with the exact expired-D list.
 preExpOwner <- allocOwner
 preExpMarker <- newMarker
 preExpIn <- openFile "/dev/null" ReadMode
 preExpStart <- startBudgetAfter 1000000 >>= either (ioError . userError . show) pure
 preExpPidRef <- newIORef (Nothing :: Maybe ProcessID)
 preExpCloseEnteredRef <- newIORef (0 :: Int)
 preExpRes <- withPersistentOwnerHook
  preExpOwner
  (persistentFixture childExe [preExpMarker] preExpIn)
  4096
  preExpStart
  stop60ms
  (\obs -> do
    writeIORef preExpPidRef (Just (observedPid obs))
    ok <- awaitMarker preExpMarker 150
    pure (if ok then Right () else Left TimedOut))
  (\_ -> pure ())
  (\stage ->
    if stage == "persistent-before-pidfd-close-precheck" then
     threadDelay 90000
    else if stage == "persistent-in-pidfd-close" then
     modifyIORef' preExpCloseEnteredRef (+ 1)
    else pure ())
 cleanMarker preExpMarker
 mPreExpPid <- readIORef preExpPidRef
 preExpCloseEntered <- readIORef preExpCloseEnteredRef
 preExpCustody <- persistentPidfdCustody preExpOwner
 preExpPhase <- persistentStatus preExpOwner
 preExpRaw <- persistentUnderlyingStatus preExpOwner
 check "pre-close-deadline-expiry-retains-PidfdKnownOpen-and-quarantines"
  (preExpCloseEntered == 0
    && (case preExpCustody of PidfdKnownOpen p (Just _) -> Just p == mPreExpPid; _ -> False)
    && preExpRes == Left (ExitUncertain CleanupUncertain expectedExpiredCloseFailures)
    && preExpPhase == PersistentQuarantined expectedExpiredCloseFailures
    && preExpRaw == Quarantined expectedExpiredCloseFailures)

 -- 15. Pre-close abort before closeFd: synchronous fault in precheck never enters closeFd
 -- and keeps sticky PidfdKnownOpen (distinguished from PidfdCloseUncertain).
 preAbortOwner <- allocOwner
 preAbortMarker <- newMarker
 preAbortIn <- openFile "/dev/null" ReadMode
 preAbortStart <- startBudgetAfter 1000000 >>= either (ioError . userError . show) pure
 preAbortPidRef <- newIORef (Nothing :: Maybe ProcessID)
 preAbortCloseEnteredRef <- newIORef (0 :: Int)
 preAbortRes <- withPersistentOwnerHook
  preAbortOwner
  (persistentFixture childExe [preAbortMarker] preAbortIn)
  4096
  preAbortStart
  stop2s
  (\obs -> do
    writeIORef preAbortPidRef (Just (observedPid obs))
    ok <- awaitMarker preAbortMarker 150
    pure (if ok then Right () else Left TimedOut))
  (\_ -> pure ())
  (\stage ->
    if stage == "persistent-before-pidfd-close-precheck" then
     ioError (userError "injected-preclose-abort")
    else if stage == "persistent-in-pidfd-close" then
     modifyIORef' preAbortCloseEnteredRef (+ 1)
    else pure ())
 cleanMarker preAbortMarker
 mPreAbortPid <- readIORef preAbortPidRef
 preAbortCloseEntered <- readIORef preAbortCloseEnteredRef
 preAbortCustody <- persistentPidfdCustody preAbortOwner
 preAbortPhase <- persistentStatus preAbortOwner
 preAbortRaw <- persistentUnderlyingStatus preAbortOwner
 check "pre-close-abort-retains-PidfdKnownOpen-and-quarantines"
  (preAbortCloseEntered == 0
    && (case preAbortCustody of PidfdKnownOpen p (Just _) -> Just p == mPreAbortPid; _ -> False)
    && preAbortRes == Left (ExitUncertain CleanupUncertain ["pidfd-close"])
    && preAbortPhase == PersistentQuarantined ["pidfd-close"]
    && preAbortRaw == Quarantined ["pidfd-close"])

 -- 16. Conservative post-claim uncertain region (injected at persistent-in-pidfd-close
 -- before closeFd; does not claim an OS close(2) syscall failure) marks sticky
 -- PidfdCloseUncertain once and never retries raw closeFd.
 inCloseOwner <- allocOwner
 inCloseMarker <- newMarker
 inCloseIn <- openFile "/dev/null" ReadMode
 inCloseStart <- startBudgetAfter 1000000 >>= either (ioError . userError . show) pure
 inClosePidRef <- newIORef (Nothing :: Maybe ProcessID)
 inCloseAttemptsRef <- newIORef (0 :: Int)
 inCloseRes <- withPersistentOwnerHook
  inCloseOwner
  (persistentFixture childExe [inCloseMarker] inCloseIn)
  4096
  inCloseStart
  stop2s
  (\obs -> do
    writeIORef inClosePidRef (Just (observedPid obs))
    ok <- awaitMarker inCloseMarker 150
    pure (if ok then Right () else Left TimedOut))
  (\_ -> pure ())
  (\stage ->
    if stage == "persistent-in-pidfd-close" then do
     modifyIORef' inCloseAttemptsRef (+ 1)
     ioError (userError "injected-in-close-fault")
    else pure ())
 cleanMarker inCloseMarker
 mInClosePid <- readIORef inClosePidRef
 inCloseAttempts <- readIORef inCloseAttemptsRef
 inCloseCustody <- persistentPidfdCustody inCloseOwner
 inClosePhase <- persistentStatus inCloseOwner
 inCloseRaw <- persistentUnderlyingStatus inCloseOwner
 postUncertainStop <- requestSessionStop inCloseOwner stop2s
 check "in-close-fault-marks-PidfdCloseUncertain-without-retry"
  (inCloseAttempts == 1
    && postUncertainStop == StopNoLiveSession
    && (case inCloseCustody of PidfdCloseUncertain p (Just _) _ -> Just p == mInClosePid; _ -> False)
    && inCloseRes == Left (ExitUncertain CleanupUncertain ["pidfd-close"])
    && inClosePhase == PersistentQuarantined ["pidfd-close"]
    && inCloseRaw == Quarantined ["pidfd-close"])

 -- 17. Unconfirmed leader reap with ample StopBudget remaining skips pointless EOF capture
 -- wait, closes parent pipe read ends within budget, and retains PidfdKnownOpen so
 -- quarantine never closes the verified pidfd of a potentially live unreaped leader.
 unreapedOwner <- allocOwner
 unreapedMarker <- newMarker
 unreapedIn <- openFile "/dev/null" ReadMode
 unreapedStart <- startBudgetAfter 1000000 >>= either (ioError . userError . show) pure
 unreapedPidRef <- newIORef (Nothing :: Maybe ProcessID)
 unreapedCloseEnteredRef <- newIORef (0 :: Int)
 unreapedRes <- withPersistentOwnerHook
  unreapedOwner
  (persistentFixture childExe [unreapedMarker, "exit-when-removed"] unreapedIn)
  4096
  unreapedStart
  stop2s
  (\obs -> do
    writeIORef unreapedPidRef (Just (observedPid obs))
    ok <- awaitMarker unreapedMarker 150
    pure (if ok then Right () else Left TimedOut))
  (\_ -> pure ())
  (\stage ->
    if stage == "persistent-before-leader-kill" then
     ioError (userError "injected-leader-kill-abort")
    else if stage == "persistent-in-pidfd-close" then
     modifyIORef' unreapedCloseEnteredRef (+ 1)
    else pure ())
 mUnreapedPid <- readIORef unreapedPidRef
 stillAliveUnreaped <- case mUnreapedPid of
  Nothing -> pure False
  Just p -> not <$> leaderExited p
 unreapedCustody <- persistentPidfdCustody unreapedOwner
 unreapedCloseEntered <- readIORef unreapedCloseEnteredRef
 unreapedPhase <- persistentStatus unreapedOwner
 unreapedRaw <- persistentUnderlyingStatus unreapedOwner
 cleanMarker unreapedMarker
 case mUnreapedPid of
  Nothing -> check "unreaped-pid-observed" False
  Just p -> boundedTest "unreaped-fixture-self-exit" (awaitFixtureExited p)
 check "unconfirmed-leader-reap-retains-PidfdKnownOpen-with-budget-remaining"
  (stillAliveUnreaped
    && unreapedCloseEntered == 0
    && (case unreapedCustody of PidfdKnownOpen p (Just _) -> Just p == mUnreapedPid; _ -> False)
    && unreapedRes == Left (ExitUncertain CleanupUncertain ["leader-reap"])
    && unreapedPhase == PersistentQuarantined ["leader-reap"]
    && unreapedRaw == Quarantined ["leader-reap"])

 -- 18a. Sample-to-claim gap expiry: delay after precheck and before masked claim
 -- expires StopDeadline -> closeFd is never entered and PidfdKnownOpen is retained.
 gapExpOwner <- allocOwner
 gapExpMarker <- newMarker
 gapExpIn <- openFile "/dev/null" ReadMode
 gapExpStart <- startBudgetAfter 1000000 >>= either (ioError . userError . show) pure
 gapExpPidRef <- newIORef (Nothing :: Maybe ProcessID)
 gapExpCloseEnteredRef <- newIORef (0 :: Int)
 gapExpRes <- withPersistentOwnerHook
  gapExpOwner
  (persistentFixture childExe [gapExpMarker] gapExpIn)
  4096
  gapExpStart
  stop60ms
  (\obs -> do
    writeIORef gapExpPidRef (Just (observedPid obs))
    ok <- awaitMarker gapExpMarker 150
    pure (if ok then Right () else Left TimedOut))
  (\_ -> pure ())
  (\stage ->
    if stage == "persistent-after-pidfd-close-budget-sample" then
     threadDelay 90000
    else if stage == "persistent-in-pidfd-close" then
     modifyIORef' gapExpCloseEnteredRef (+ 1)
    else pure ())
 cleanMarker gapExpMarker
 mGapExpPid <- readIORef gapExpPidRef
 gapExpCustody <- persistentPidfdCustody gapExpOwner
 gapExpCloseEntered <- readIORef gapExpCloseEnteredRef
 gapExpPhase <- persistentStatus gapExpOwner
 gapExpRaw <- persistentUnderlyingStatus gapExpOwner
 check "sample-to-claim-gap-expiry-retains-PidfdKnownOpen-without-entering-closeFd"
  (gapExpCloseEntered == 0
    && (case gapExpCustody of PidfdKnownOpen p (Just _) -> Just p == mGapExpPid; _ -> False)
    && gapExpRes == Left (ExitUncertain CleanupUncertain expectedExpiredCloseFailures)
    && gapExpPhase == PersistentQuarantined expectedExpiredCloseFailures
    && gapExpRaw == Quarantined expectedExpiredCloseFailures)

 -- 18b. Pre-return timeout in claimed close region (interruptible delay at
 -- persistent-in-pidfd-close before closeFd) marks sticky PidfdCloseUncertain
 -- without retry and quarantines with expectedExpiredCloseFailures.
 inCloseTimeoutOwner <- allocOwner
 inCloseTimeoutMarker <- newMarker
 inCloseTimeoutIn <- openFile "/dev/null" ReadMode
 inCloseTimeoutStart <- startBudgetAfter 1000000 >>= either (ioError . userError . show) pure
 inCloseTimeoutPidRef <- newIORef (Nothing :: Maybe ProcessID)
 inCloseTimeoutAttemptsRef <- newIORef (0 :: Int)
 inCloseTimeoutRes <- withPersistentOwnerHook
  inCloseTimeoutOwner
  (persistentFixture childExe [inCloseTimeoutMarker] inCloseTimeoutIn)
  4096
  inCloseTimeoutStart
  stop60ms
  (\obs -> do
    writeIORef inCloseTimeoutPidRef (Just (observedPid obs))
    ok <- awaitMarker inCloseTimeoutMarker 150
    pure (if ok then Right () else Left TimedOut))
  (\_ -> pure ())
  (\stage ->
    if stage == "persistent-in-pidfd-close" then do
     modifyIORef' inCloseTimeoutAttemptsRef (+ 1)
     threadDelay 90000
    else pure ())
 cleanMarker inCloseTimeoutMarker
 mInCloseTimeoutPid <- readIORef inCloseTimeoutPidRef
 inCloseTimeoutAttempts <- readIORef inCloseTimeoutAttemptsRef
 inCloseTimeoutCustody <- persistentPidfdCustody inCloseTimeoutOwner
 inCloseTimeoutPhase <- persistentStatus inCloseTimeoutOwner
 inCloseTimeoutRaw <- persistentUnderlyingStatus inCloseTimeoutOwner
 check "in-close-timeout-marks-PidfdCloseUncertain-without-retry"
  (inCloseTimeoutAttempts == 1
    && (case inCloseTimeoutCustody of PidfdCloseUncertain p (Just _) _ -> Just p == mInCloseTimeoutPid; _ -> False)
    && inCloseTimeoutRes == Left (ExitUncertain CleanupUncertain expectedExpiredCloseFailures)
    && inCloseTimeoutPhase == PersistentQuarantined expectedExpiredCloseFailures
    && inCloseTimeoutRaw == Quarantined expectedExpiredCloseFailures)

 -- 18c. Post-syscall receipt deadline expiry: closeFd commits InternalPidfdClosed +
 -- PendingClosed under mask, then delay at persistent-after-pidfd-close-receipt
 -- crosses StopDeadline -> PidfdClosed receipt is preserved (never overwritten by
 -- PidfdCloseUncertain) while containment quarantines on late completion.
 lateCloseOwner <- allocOwner
 lateCloseMarker <- newMarker
 lateCloseIn <- openFile "/dev/null" ReadMode
 lateCloseStart <- startBudgetAfter 1000000 >>= either (ioError . userError . show) pure
 lateCloseAttemptsRef <- newIORef (0 :: Int)
 lateCloseRes <- withPersistentOwnerHook
  lateCloseOwner
  (persistentFixture childExe [lateCloseMarker] lateCloseIn)
  4096
  lateCloseStart
  stop60ms
  (\_ -> do
    ok <- awaitMarker lateCloseMarker 150
    pure (if ok then Right () else Left TimedOut))
  (\_ -> pure ())
  (\stage ->
    if stage == "persistent-in-pidfd-close" then
     modifyIORef' lateCloseAttemptsRef (+ 1)
    else if stage == "persistent-after-pidfd-close-receipt" then
     threadDelay 90000
    else pure ())
 cleanMarker lateCloseMarker
 lateCloseAttempts <- readIORef lateCloseAttemptsRef
 lateCloseCustody <- persistentPidfdCustody lateCloseOwner
 lateClosePhase <- persistentStatus lateCloseOwner
 lateCloseRaw <- persistentUnderlyingStatus lateCloseOwner
 check "late-close-records-PidfdClosed-receipt-while-quarantining-over-deadline"
  (lateCloseAttempts == 1
    && lateCloseCustody == PidfdClosed
    && lateCloseRes == Left (ExitUncertain CleanupUncertain expectedExpiredCloseFailures)
    && lateClosePhase == PersistentQuarantined expectedExpiredCloseFailures
    && lateCloseRaw == Quarantined expectedExpiredCloseFailures)

 -- 18d. Post-claim / pre-syscall deadline expiry: delay at
 -- persistent-after-pidfd-claim-before-syscall rolls InternalPidfdClosing back
 -- to PidfdKnownOpen before O.pendingMarkFD or closeFd is ever entered.
 claimGapOwner <- allocOwner
 claimGapMarker <- newMarker
 claimGapIn <- openFile "/dev/null" ReadMode
 claimGapStart <- startBudgetAfter 1000000 >>= either (ioError . userError . show) pure
 claimGapPidRef <- newIORef (Nothing :: Maybe ProcessID)
 claimGapCloseEnteredRef <- newIORef (0 :: Int)
 claimGapRes <- withPersistentOwnerHook
  claimGapOwner
  (persistentFixture childExe [claimGapMarker] claimGapIn)
  4096
  claimGapStart
  stop60ms
  (\obs -> do
    writeIORef claimGapPidRef (Just (observedPid obs))
    ok <- awaitMarker claimGapMarker 150
    pure (if ok then Right () else Left TimedOut))
  (\_ -> pure ())
  (\stage ->
    if stage == "persistent-after-pidfd-claim-before-syscall" then
     threadDelay 90000
    else if stage == "persistent-in-pidfd-close" then
     modifyIORef' claimGapCloseEnteredRef (+ 1)
    else pure ())
 cleanMarker claimGapMarker
 mClaimGapPid <- readIORef claimGapPidRef
 claimGapCloseEntered <- readIORef claimGapCloseEnteredRef
 claimGapCustody <- persistentPidfdCustody claimGapOwner
 claimGapPhase <- persistentStatus claimGapOwner
 claimGapRaw <- persistentUnderlyingStatus claimGapOwner
 check "post-claim-pre-syscall-expiry-rolls-back-to-PidfdKnownOpen"
  (claimGapCloseEntered == 0
    && (case claimGapCustody of PidfdKnownOpen p (Just _) -> Just p == mClaimGapPid; _ -> False)
    && claimGapRes == Left (ExitUncertain CleanupUncertain expectedExpiredCloseFailures)
    && claimGapPhase == PersistentQuarantined expectedExpiredCloseFailures
    && claimGapRaw == Quarantined expectedExpiredCloseFailures)

 -- 19. Final stderr close D expiry (pre-entry stall refuses hClose entry after D;
 -- post-return stall preserves closed receipt while quarantining ["stderr-close"]).
 stderrPreOwner <- allocOwner
 stderrPreMarker <- newMarker
 stderrPreIn <- openFile "/dev/null" ReadMode
 stderrPreStart <- startBudgetAfter 1000000 >>= either (ioError . userError . show) pure
 stderrPreEnteredRef <- newIORef False
 stderrPreRes <- withPersistentOwnerHook
  stderrPreOwner
  (persistentFixture childExe [stderrPreMarker] stderrPreIn)
  4096
  stderrPreStart
  stop60ms
  (\_ -> do
    ok <- awaitMarker stderrPreMarker 150
    pure (if ok then Right () else Left TimedOut))
  (\_ -> pure ())
  (\stage -> do
    when (stage == "qa-stderr-after-budget-sample") (threadDelay 90000)
    when (stage == "qa-stderr-close-entered") (writeIORef stderrPreEnteredRef True))
 cleanMarker stderrPreMarker
 stderrPreEntered <- readIORef stderrPreEnteredRef
 stderrPreCustody <- persistentPidfdCustody stderrPreOwner
 stderrPrePhase <- persistentStatus stderrPreOwner
 stderrPreRaw <- persistentUnderlyingStatus stderrPreOwner
 check "stderr-pre-entry-expiry-refuses-hClose-and-quarantines"
  (not stderrPreEntered
    && stderrPreCustody == PidfdClosed
    && stderrPreRes == Left (ExitUncertain CleanupUncertain ["stderr-close"])
    && stderrPrePhase == PersistentQuarantined ["stderr-close"]
    && stderrPreRaw == Quarantined ["stderr-close"])

 stderrPostOwner <- allocOwner
 stderrPostMarker <- newMarker
 stderrPostIn <- openFile "/dev/null" ReadMode
 stderrPostStart <- startBudgetAfter 1000000 >>= either (ioError . userError . show) pure
 stderrPostReturnedRef <- newIORef False
 stderrPostRes <- withPersistentOwnerHook
  stderrPostOwner
  (persistentFixture childExe [stderrPostMarker] stderrPostIn)
  4096
  stderrPostStart
  stop60ms
  (\_ -> do
    ok <- awaitMarker stderrPostMarker 150
    pure (if ok then Right () else Left TimedOut))
  (\_ -> pure ())
  (\stage ->
    when (stage == "qa-stderr-after-close-return") $ do
     writeIORef stderrPostReturnedRef True
     threadDelay 90000)
 cleanMarker stderrPostMarker
 stderrPostReturned <- readIORef stderrPostReturnedRef
 stderrPostCustody <- persistentPidfdCustody stderrPostOwner
 stderrPostPhase <- persistentStatus stderrPostOwner
 stderrPostRaw <- persistentUnderlyingStatus stderrPostOwner
 check "stderr-post-return-expiry-preserves-close-and-quarantines"
  (stderrPostReturned
    && stderrPostCustody == PidfdClosed
    && stderrPostRes == Left (ExitUncertain CleanupUncertain ["stderr-close"])
    && stderrPostPhase == PersistentQuarantined ["stderr-close"]
    && stderrPostRaw == Quarantined ["stderr-close"])

 -- 20. Bounded held-borrow release step: expiry before/during borrow release
 -- quarantines ["borrow-release"] without settling cleanly after D.
 borrowExpOwner <- allocOwner
 borrowExpMarker <- newMarker
 borrowExpIn <- openFile "/dev/null" ReadMode
 borrowExpStart <- startBudgetAfter 1000000 >>= either (ioError . userError . show) pure
 borrowWireDlRef <- newIORef (Nothing :: Maybe Integer)
 borrowExpRes <- withPersistentOwnerHook
  borrowExpOwner
  (persistentFixture childExe [borrowExpMarker] borrowExpIn)
  4096
  borrowExpStart
  stop60ms
  (\_ -> do
    ok <- awaitMarker borrowExpMarker 150
    pure (if ok then Right () else Left TimedOut))
  (\_ -> pure ())
  (\stage -> case stripPrefix "qa-before-held-borrow-release:" stage of
    Nothing -> pure ()
    Just wire -> do
     writeIORef borrowWireDlRef (readMaybe wire)
     threadDelay 90000)
 cleanMarker borrowExpMarker
 mBorrowWireDl <- readIORef borrowWireDlRef
 borrowExpCustody <- persistentPidfdCustody borrowExpOwner
 borrowExpPhase <- persistentStatus borrowExpOwner
 borrowExpRaw <- persistentUnderlyingStatus borrowExpOwner
 check "bounded-borrow-release-expiry-quarantines-without-settling"
  ((case mBorrowWireDl of Just d -> d > 0; Nothing -> False)
    && borrowExpCustody == PidfdClosed
    && borrowExpRes == Left (ExitUncertain CleanupUncertain ["borrow-release"])
    && borrowExpPhase == PersistentQuarantined ["borrow-release"]
    && borrowExpRaw == Quarantined ["borrow-release"])

 -- 18e. Post-claim persistent-before-pidfd-close deadline expiry also runs
 -- before PendingUncertain/closeFd and rolls back to PidfdKnownOpen.
 beforeCloseExpOwner <- allocOwner
 beforeCloseExpMarker <- newMarker
 beforeCloseExpIn <- openFile "/dev/null" ReadMode
 beforeCloseExpStart <- startBudgetAfter 1000000 >>= either (ioError . userError . show) pure
 beforeCloseExpPidRef <- newIORef (Nothing :: Maybe ProcessID)
 beforeCloseExpEnteredRef <- newIORef (0 :: Int)
 beforeCloseExpRes <- withPersistentOwnerHook
  beforeCloseExpOwner
  (persistentFixture childExe [beforeCloseExpMarker] beforeCloseExpIn)
  4096
  beforeCloseExpStart
  stop60ms
  (\obs -> do
    writeIORef beforeCloseExpPidRef (Just (observedPid obs))
    ok <- awaitMarker beforeCloseExpMarker 150
    pure (if ok then Right () else Left TimedOut))
  (\_ -> pure ())
  (\stage ->
    if stage == "persistent-before-pidfd-close" then
     threadDelay 90000
    else if stage == "persistent-in-pidfd-close" then
     modifyIORef' beforeCloseExpEnteredRef (+ 1)
    else pure ())
 cleanMarker beforeCloseExpMarker
 mBeforeCloseExpPid <- readIORef beforeCloseExpPidRef
 beforeCloseExpEntered <- readIORef beforeCloseExpEnteredRef
 beforeCloseExpCustody <- persistentPidfdCustody beforeCloseExpOwner
 beforeCloseExpPhase <- persistentStatus beforeCloseExpOwner
 beforeCloseExpRaw <- persistentUnderlyingStatus beforeCloseExpOwner
 check "before-pidfd-close-hook-expiry-rolls-back-to-PidfdKnownOpen"
  (beforeCloseExpEntered == 0
    && (case beforeCloseExpCustody of PidfdKnownOpen p (Just _) -> Just p == mBeforeCloseExpPid; _ -> False)
    && beforeCloseExpRes == Left (ExitUncertain CleanupUncertain expectedExpiredCloseFailures)
    && beforeCloseExpPhase == PersistentQuarantined expectedExpiredCloseFailures
    && beforeCloseExpRaw == Quarantined expectedExpiredCloseFailures)

 -- 21. Pure HeldExecutable releaseNow receipt classifier: only Right (Just True)
 -- counts as confirmed borrow release; sticky Right (Just False) (HeldUnknown),
 -- Right Nothing (timeout), and Left ex (exception) all classify as unconfirmed
 -- without introducing any production ownership mutator in Persistent.Internal.
 check "borrowReleasedReceipt-accepts-only-Right-Just-True"
  (borrowReleasedReceipt (Right (Just True))
    && not (borrowReleasedReceipt (Right (Just False)))
    && not (borrowReleasedReceipt (Right Nothing))
    && not (borrowReleasedReceipt (Left (toException (userError "fault")))))

 -- 22. Per-request frame batch admission (ActionBudget + LiveFrameBatch):
 --   - Trusted ActionBudget bounds (1..5_000_000 us = 5s) + defaultPersistentActionBudget
 --   - Invalid quotas (< 0, > maxLiveFrameBatchActions=17, > maxLiveFrameBatchRequests=16)
 --     and expired frameDl refused pre-dispatch
 --   - Zero-quota presentation-only frame admits zero actions
 --   - Mutual exclusion between 1-shot enterLiveFrameAction and beginLiveFrameBatch,
 --     plus initial-attachment ordering enforcement on beginLiveFrameRequestBatch
 --   - Positive 17-action serial batch (1 attachment + 16 DesktopCommit requests)
 --     passes fresh distinct monotonic lexical AdmissionDeadline to each callback
 --     and completes in order after frameDl expires during step 1
 --   - Stricter authority deadline clamping (enterLiveBatchRequest Just stricterDl)
 --     clamps lexical actionDl without renewal and refuses expired stricterDl
 --   - Exhausted quota (18th call) and escaped batch token refused pre-dispatch
 --   - Sticky poison after OperationOutcomeUnknown blocks later requests in frame
 --   - Stop between serial requests refuses request 2 pre-dispatch with zero
 --     post-stop side effects and latches sticky tryPersistentStopDeadline
 check "ActionBudget-5s-bounds-and-LiveFrameBatch-limits"
  (maxPersistentActionBudgetMicros == 5000000
    && actionBudgetMicrosValue defaultPersistentActionBudget == 5000000
    && maxLiveFrameBatchRequests == 16
    && actionBudgetMicros 0 == Left BadArguments
    && actionBudgetMicros (-5) == Left BadArguments
    && actionBudgetMicros 5000001 == Left BadArguments
    && fmap actionBudgetMicrosValue (actionBudgetMicros 1) == Right 1
    && fmap actionBudgetMicrosValue (actionBudgetMicros 5000000) == Right 5000000)
 actBudget500ms <- either (ioError . userError . show) pure (actionBudgetMicros 500000 :: Either ToolError ActionBudget)
 actBudget20ms <- either (ioError . userError . show) pure (actionBudgetMicros 20000 :: Either ToolError ActionBudget)

 batchOwner <- allocOwner
 stopBeforeSpawnObs <- tryPersistentStopDeadline batchOwner
 check "tryPersistentStopDeadline-fresh-owner-not-latched"
  (stopBeforeSpawnObs == StopDeadlineNotLatched)
 batchMarker <- newMarker
 batchIn <- openFile "/dev/null" ReadMode
 batchStart <- startBudgetAfter 1000000 >>= either (ioError . userError . show) pure
 batchStop <- either (ioError . userError . show) pure (stopBudgetMicros 1000000)
 escapedBatchRef <- newIORef (Nothing :: Maybe LiveFrameBatch)
 batchTrace17Ref <- newIORef ([] :: [Int])
 batchDeadlines17Ref <- newIORef ([] :: [Integer])
 poisonStep3CountRef <- newIORef (0 :: Int)
 postStopStep2CountRef <- newIORef (0 :: Int)
 batchOwnerRes <- withPersistentOwner
  batchOwner
  (persistentFixture childExe [batchMarker] batchIn)
  4096
  batchStart
  batchStop
  (\_ -> do
    ok <- awaitMarker batchMarker 150
    pure (if ok then Right () else Left TimedOut))
  (\live -> do
    -- 22a. Invalid quotas and expired frameDl refused; 0-quota presentation frame refuses actions.
    zeroSideEffects <- newIORef (0 :: Int)
    frameZeroOut <- withLiveFrameAdmission live $ \adm -> do
     fDl <- deadlineAfter 300000 >>= either (ioError . userError . show) pure
     negQuota <- beginLiveFrameBatch adm fDl (-1)
     overQuota17 <- beginLiveFrameBatch adm fDl 17
     overReqQuota <- beginLiveFrameRequestBatch adm fDl True (maxLiveFrameBatchRequests + 1)
     expFDl <- deadlineAfter 2000 >>= either (ioError . userError . show) pure
     threadDelay 5000
     expBatch <- beginLiveFrameBatch adm expFDl 1
     bZeroRes <- beginLiveFrameBatch adm fDl 0
     case (negQuota, overQuota17, overReqQuota, expBatch, bZeroRes) of
      (Left BadArguments, Left BadArguments, Left BadArguments, Left TimedOut, Right bZero) -> do
       extraZero <- enterLiveBatchBudgetedAction bZero actBudget500ms (\_ -> modifyIORef' zeroSideEffects (+ 1) >> pure (Right ()))
       extraAtt <- enterLiveBatchAttachment bZero actBudget500ms (\_ -> modifyIORef' zeroSideEffects (+ 1) >> pure (Right ()))
       pure (extraZero == Left (OperationRefusedPreDispatch OwnerBusy)
         && extraAtt == Left (OperationRefusedPreDispatch OwnerBusy))
      _ -> pure False
    zeroEffs <- readIORef zeroSideEffects
    -- Direct no-attachment 16-request batch refuses 17th request with 0 side effects.
    noAtt17SideEffects <- newIORef (0 :: Int)
    noAtt16Out <- withLiveFrameAdmission live $ \adm -> do
     fDl <- deadlineAfter 300000 >>= either (ioError . userError . show) pure
     b16 <- beginLiveFrameBatch adm fDl 16 >>= either (ioError . userError . show) pure
     ok16 <- mapM (\i -> enterLiveBatchRequest b16 actBudget500ms Nothing (\_ -> pure (Right i))) [1 .. 16 :: Int]
     over17 <- enterLiveBatchRequest b16 actBudget500ms Nothing $ \_ -> do
      modifyIORef' noAtt17SideEffects (+ 1)
      pure (Right (17 :: Int))
     pure (ok16 == map Right [1 .. 16]
       && over17 == Left (OperationRefusedPreDispatch OwnerBusy))
    noAtt17Effs <- readIORef noAtt17SideEffects
    check "batch-quota-bounds-no-attachment-16-cap-expired-frameDl-and-zero-quota"
     (frameZeroOut == Right True && zeroEffs == 0 && noAtt16Out == Right True && noAtt17Effs == 0)

    -- 22b. Mode mutual exclusion + attachment ordering enforcement.
    exclOneShotOut <- withLiveFrameAdmission live $ \adm -> do
     fDl <- deadlineAfter 300000 >>= either (ioError . userError . show) pure
     aDl <- deadlineAfter 500000 >>= either (ioError . userError . show) pure
     oneRes <- enterLiveFrameAction adm fDl aDl (pure (Right (1 :: Int)))
     batchAfterOne <- beginLiveFrameBatch adm fDl 1
     pure $ case (oneRes, batchAfterOne) of
      (Right 1, Left OwnerBusy) -> True
      _ -> False
    check "one-shot-enterLiveFrameAction-blocks-beginLiveFrameBatch"
     (exclOneShotOut == Right True)

    exclBatchOut <- withLiveFrameAdmission live $ \adm -> do
     fDl <- deadlineAfter 300000 >>= either (ioError . userError . show) pure
     aDl <- deadlineAfter 500000 >>= either (ioError . userError . show) pure
     bRes1 <- beginLiveFrameRequestBatch adm fDl True 1
     bRes2 <- beginLiveFrameBatch adm fDl 1
     oneAfterBatch <- enterLiveFrameAction adm fDl aDl (pure (Right (99 :: Int)))
     case (bRes1, bRes2, oneAfterBatch) of
      (Right bAttReq, Left OwnerBusy, Left (OperationRefusedPreDispatch OwnerBusy)) -> do
       skipAtt <- enterLiveBatchBudgetedAction bAttReq actBudget500ms (\_ -> pure (Right (7 :: Int)))
       afterOrderPoison <- enterLiveBatchAttachment bAttReq actBudget500ms (\_ -> pure (Right (8 :: Int)))
       pure (skipAtt == Left (OperationRefusedPreDispatch OwnerBusy)
         && afterOrderPoison == Left (OperationRefusedPreDispatch SessionClosed))
      _ -> pure False
    check "beginLiveFrameRequestBatch-blocks-second-batch-one-shot-and-enforces-attachment-order"
     (exclBatchOut == Right True)

    -- 22c. Positive 17-step batch (1 attachment + 16 requests) surviving frameDl expiry
    --      and passing monotonic lexical AdmissionDeadlines to every step.
    pos17Out <- withLiveFrameAdmission live $ \adm -> do
     shortFrameDl <- deadlineAfter 40000 >>= either (ioError . userError . show) pure
     b17Res <- beginLiveFrameRequestBatch adm shortFrameDl True 16
     case b17Res of
      Left err -> ioError (userError ("expected 1+16 batch admission, got " ++ show err))
      Right b17 -> do
       writeIORef escapedBatchRef (Just b17)
       let recordDl dl = case readMaybe (deadlineAbsoluteNs dl) :: Maybe Integer of
            Just ns -> modifyIORef' batchDeadlines17Ref (++ [ns])
            Nothing -> ioError (userError "unparseable lexical action deadline")
       attRes <- enterLiveBatchAttachment b17 actBudget500ms $ \attDl -> do
        recordDl attDl
        threadDelay 55000
        modifyIORef' batchTrace17Ref (++ [0])
        pure (Right (0 :: Int))
       dupAtt <- enterLiveBatchAttachment b17 actBudget500ms (\_ -> pure (Right (-1 :: Int)))
       let runReq idx = enterLiveBatchBudgetedAction b17 actBudget500ms $ \reqDl -> do
            threadDelay 1000
            recordDl reqDl
            modifyIORef' batchTrace17Ref (++ [idx])
            pure (Right idx)
       results16 <- mapM runReq [1 .. 16 :: Int]
       over17 <- enterLiveBatchBudgetedAction b17 actBudget500ms $ \_ -> do
        modifyIORef' batchTrace17Ref (++ [17])
        pure (Right (17 :: Int))
       pure (attRes == Right 0
         && dupAtt == Left (OperationRefusedPreDispatch OwnerBusy)
         && results16 == map Right [1 .. 16]
         && over17 == Left (OperationRefusedPreDispatch OwnerBusy))
    trace17 <- readIORef batchTrace17Ref
    dls17 <- readIORef batchDeadlines17Ref
    mEscapedBatch <- readIORef escapedBatchRef
    escapedBatchCall <- case mEscapedBatch of
     Nothing -> pure (Right (0 :: Int))
     Just escB -> enterLiveBatchBudgetedAction escB actBudget500ms (\_ -> pure (Right 0))
    check "positive-1-plus-16-batch-lexical-deadlines-monotonic-and-closes-escaped"
     (pos17Out == Right True
       && trace17 == [0 .. 16]
       && length dls17 == 17
       && and (zipWith (<) dls17 (drop 1 dls17))
       && escapedBatchCall == Left (OperationRefusedPreDispatch SessionClosed))

    -- 22d. Stricter authority deadline clamping (enterLiveBatchRequest Just stricterDl)
    --      and pre-dispatch refusal on already-expired stricter authority deadline.
    clampSideEffects <- newIORef (0 :: Int)
    clampOut <- withLiveFrameAdmission live $ \adm -> do
     fDl <- deadlineAfter 300000 >>= either (ioError . userError . show) pure
     bClamp <- beginLiveFrameRequestBatch adm fDl True 2 >>= either (ioError . userError . show) pure
     stricter120ms <- deadlineAfter 120000 >>= either (ioError . userError . show) pure
     attClampedEq <- enterLiveBatchAttachmentRequest bClamp defaultPersistentActionBudget (Just stricter120ms) $ \lexDl ->
      pure (Right (deadlineAbsoluteNs lexDl == deadlineAbsoluteNs stricter120ms))
     clampedEq <- enterLiveBatchRequest bClamp defaultPersistentActionBudget (Just stricter120ms) $ \lexDl ->
      pure (Right (deadlineAbsoluteNs lexDl == deadlineAbsoluteNs stricter120ms))
     expiredAuth <- deadlineAfter 2000 >>= either (ioError . userError . show) pure
     threadDelay 5000
     expiredRes <- enterLiveBatchRequest bClamp defaultPersistentActionBudget (Just expiredAuth) $ \_ -> do
      modifyIORef' clampSideEffects (+ 1)
      pure (Right True)
     pure (attClampedEq == Right True
       && clampedEq == Right True
       && expiredRes == Left (OperationRefusedPreDispatch TimedOut))
    clampEffs <- readIORef clampSideEffects
    check "enterLiveBatchRequest-clamps-stricter-authority-and-refuses-expired-authority"
     (clampOut == Right True && clampEffs == 0)

    -- 22e. Sticky batch poison after post-entry OperationOutcomeUnknown blocks later actions.
    poisonOut <- withLiveFrameAdmission live $ \adm -> do
     fDl <- deadlineAfter 300000 >>= either (ioError . userError . show) pure
     bPoison <- beginLiveFrameBatch adm fDl 3 >>= either (ioError . userError . show) pure
     step1 <- enterLiveBatchBudgetedAction bPoison actBudget500ms (\_ -> pure (Right (10 :: Int)))
     step2 <- enterLiveBatchBudgetedAction bPoison actBudget20ms (\_ -> threadDelay 45000 >> pure (Right (20 :: Int)))
     step3 <- enterLiveBatchBudgetedAction bPoison actBudget500ms $ \_ -> do
      modifyIORef' poisonStep3CountRef (+ 1)
      pure (Right (30 :: Int))
     pure (step1 == Right 10
       && step2 == Left (OperationOutcomeUnknown TimedOut)
       && step3 == Left (OperationRefusedPreDispatch SessionClosed))
    poisonStep3Count <- readIORef poisonStep3CountRef
    check "batch-poisons-stickily-on-OperationOutcomeUnknown"
     (poisonOut == Right True && poisonStep3Count == 0)

    -- 22f. Owner stop between serial batch actions refuses action 2 pre-dispatch with 0 effects.
    stopBetweenOut <- withLiveFrameAdmission live $ \adm -> do
     fDl <- deadlineAfter 300000 >>= either (ioError . userError . show) pure
     bStop <- beginLiveFrameBatch adm fDl 2 >>= either (ioError . userError . show) pure
     firstOk <- enterLiveBatchBudgetedAction bStop actBudget500ms (\_ -> pure (Right (101 :: Int)))
     obsBeforeStop <- tryPersistentStopDeadline batchOwner
     stopRec <- requestSessionStop batchOwner batchStop
     obsAfterFirstStop <- tryPersistentStopDeadline batchOwner
     stopRec2 <- requestSessionStop batchOwner batchStop
     obsAfterSecondStop <- tryPersistentStopDeadline batchOwner
     secondAfterStop <- enterLiveBatchBudgetedAction bStop actBudget500ms $ \_ -> do
      modifyIORef' postStopStep2CountRef (+ 1)
      pure (Right (102 :: Int))
     pure (firstOk == Right 101
       && obsBeforeStop == StopDeadlineNotLatched
       && (stopRec == StopSignalSent || stopRec == StopLeaderAlreadyExited)
       && stopRec2 == StopAlreadyRequested
       && (case (obsAfterFirstStop, obsAfterSecondStop) of
            (StopDeadlineLatched d1, StopDeadlineLatched d2) -> d1 == d2
            _ -> False)
       && secondAfterStop == Left (OperationRefusedPreDispatch SessionClosed))
    postStopStep2Count <- readIORef postStopStep2CountRef
    check "stop-between-batch-actions-refuses-second-action-pre-dispatch"
     (stopBetweenOut == Right True && postStopStep2Count == 0))
 cleanMarker batchMarker
 batchStopObsAfterRetire <- tryPersistentStopDeadline batchOwner
 batchPhase <- persistentStatus batchOwner
 batchRaw <- persistentUnderlyingStatus batchOwner
 batchCustody <- persistentPidfdCustody batchOwner
 check "batchOwner-retires-cleanly-after-batch-controls"
  ((case batchOwnerRes of Right ((), LeaderReaped _) -> True; _ -> False)
    && (case batchStopObsAfterRetire of StopDeadlineLatched _ -> True; _ -> False)
    && batchPhase == PersistentRetired
    && batchRaw == Available
    && batchCustody == PidfdClosed)

 registered <- readIORef outerRegistry
 statuses <- mapM (persistentStatus . fst) registered
 let quarantinedCount = length [() | PersistentQuarantined _ <- statuses]
     retiredCount = length [() | PersistentRetired <- statuses]
 check "all-25-test-owners-pre-registered-and-accounted"
  (length registered == 25 && quarantinedCount == 15 && retiredCount == 10)

 -- Preserve the original 25-owner oracle before adding fresh generated cases.
 -- Every generated owner remains in the same externally retained registry.
 SeededBatch.runAll childExe allocOwner newMarker cleanMarker
  (\marker _ -> do ready <- awaitMarker marker 150; pure (if ready then Right () else Left TimedOut))
  (startBudgetAfter 1000000 >>= either (ioError . userError . show) pure)
  (deadlineAfter 5000000 >>= either (ioError . userError . show) pure) stop2s
 generatedRegistry <- readIORef outerRegistry
 generatedStatuses <- mapM (persistentStatus . fst) generatedRegistry
 check "32-generated-owners-retire-with-original-25-retained"
  (length generatedRegistry == 57
    && length [() | PersistentQuarantined _ <- generatedStatuses] == 15
    && length [() | PersistentRetired <- generatedStatuses] == 42)
