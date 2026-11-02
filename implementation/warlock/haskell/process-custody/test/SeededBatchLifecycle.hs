-- Source-only QA control: Root supplies a fresh *live* owner/session, the
-- original frame admission deadline and stop budget for EACH seed, plus its
-- pinned fixture and external guardian. Never share an owner across seeds.
-- Uses public opaque admission tokens; no fabricated native authority or ACK.
module SeededBatchLifecycle (seeds, runSeed) where

import Control.Concurrent (forkFinally)
import Control.Concurrent.MVar (newEmptyMVar, putMVar, readMVar, tryPutMVar)
import Control.Exception (finally, mask)
import Control.Monad (forM_, unless, void)
import Data.Bits (shiftL, shiftR, xor)
import Data.IORef (modifyIORef', newIORef, readIORef, writeIORef)
import Data.Word (Word32)
import Foreign.StablePtr (newStablePtr)
import System.Timeout (timeout)
import Warlock.Capture.Process (ToolError(..))
import Warlock.Capture.Process.Bootstrap (AdmissionDeadline, remainingMicros)
import Warlock.Capture.Process.Persistent
 ( LiveSession, PersistentOwner, StopBudget, StopReceipt(..), StopDeadlineObservation(..)
 , LiveOperationFailure(..), withLiveFrameAdmission, beginLiveFrameRequestBatch
 , enterLiveBatchRequest, defaultPersistentActionBudget, requestSessionStop
 , stopBudgetMicros, stopBudgetMicrosValue, tryPersistentStopDeadline )

data Mode = Complete | StopBefore | CallbackUnknown | StopDuring deriving (Eq, Show)
data Plan = Plan { quota :: Int, successes :: Int, mode :: Mode } deriving Show

-- Fixed controls force empty, full 16, pre-entry stop and Unknown; remaining
-- reproducible plans vary quota and the actual position of stop/failure.
seeds :: [Word32]
seeds = [0..31]

mix :: Word32 -> Word32
mix x = let a = x `xor` (x `shiftL` 13)
            b = a `xor` (a `shiftR` 17)
        in b `xor` (b `shiftL` 5)

plan :: Word32 -> Plan
plan seed
 | seed == 0 = Plan 0 0 Complete
 | seed == 1 = Plan 16 16 Complete
 | seed == 2 = Plan 1 0 StopBefore
 | seed == 3 = Plan 2 0 CallbackUnknown
 | seed == 4 = Plan 2 0 StopDuring
 | otherwise =
    let x = mix seed
        q = 1 + fromIntegral (x `mod` 16)
        n = fromIntegral ((x `shiftR` 8) `mod` fromIntegral q)
    in case (x `shiftR` 16) `mod` 4 of
      0 -> Plan q q Complete
      1 -> Plan q n StopBefore
      2 -> Plan q n CallbackUnknown
      _ -> Plan q n StopDuring

check :: String -> Bool -> IO ()
check label ok = unless ok (ioError (userError ("seeded batch lifecycle: " ++ label)))

-- This is a QA observation bound, not physical preemption. If it expires,
-- the still-live worker and owner remain strongly rooted for Root's guardian.
observeStop :: PersistentOwner -> StopBudget -> Int -> IO StopReceipt
observeStop owner budget waitMicros = mask $ \restore -> do
 check "positive stop observation bound" (waitMicros > 0)
 done <- newEmptyMVar
 workerRef <- newIORef Nothing
 _ <- newStablePtr (owner,done,workerRef)
 tid <- forkFinally (restore (requestSessionStop owner budget)) (putMVar done)
 writeIORef workerRef (Just tid)
 result <- restore (timeout waitMicros (readMVar done))
 case result of
  Nothing -> ioError (userError "stop observation expired; retain owner/worker for guardian")
  Just (Left err) -> ioError (userError ("stop worker failed: " ++ show err))
  Just (Right receipt) -> pure receipt

latched :: StopDeadlineObservation -> IO AdmissionDeadline
latched observation = case observation of
 StopDeadlineLatched deadline -> pure deadline
 _ -> ioError (userError ("stop deadline not latched: " ++ show observation))

-- The oracle comes from the plan, not measured implementation output. Actions
-- append their own unique ordinal only after actually entering. The callback
-- failure is deterministic and exercises Unknown without relying on sleep.
runSeed :: PersistentOwner -> LiveSession -> AdmissionDeadline -> StopBudget -> Word32 -> IO ()
runSeed owner live frameD stopBudget seed = do
 let spec = plan seed
     q = quota spec
     n = successes spec
     expectedCount = case mode spec of Complete -> q; StopBefore -> n; CallbackUnknown -> n + 1; StopDuring -> n + 1
 effects <- newIORef ([] :: [Int])
 alternateStop <- either (ioError . userError . show) pure (stopBudgetMicros 1)
 before <- tryPersistentStopDeadline owner
 check (show seed ++ " starts without stop") (before == StopDeadlineNotLatched)
 entered <- withLiveFrameAdmission live $ \admission -> do
  invalid <- beginLiveFrameRequestBatch admission frameD False 17
  check "17 rejected before consuming frame" (case invalid of Left BadArguments -> True; _ -> False)
  batchResult <- beginLiveFrameRequestBatch admission frameD False q
  batch <- either (ioError . userError . show) pure batchResult
  repeated <- beginLiveFrameRequestBatch admission frameD False q
  check "second batch claim refused" (case repeated of Left OwnerBusy -> True; _ -> False)
  let action i = do
       modifyIORef' effects (++ [i])
       pure (Right ())
      invoke i = enterLiveBatchRequest batch defaultPersistentActionBudget Nothing (\_ -> action i)
  forM_ [0..n-1] $ \i -> do
   outcome <- invoke i
   check "expected successful ordered entry" (outcome == Right ())
  case mode spec of
   Complete -> do
    overflow <- invoke q
    check "exhausted quota refuses before effect" (overflow == Left (OperationRefusedPreDispatch OwnerBusy))
   StopBefore -> do
    first <- observeStop owner stopBudget (stopBudgetMicrosValue stopBudget)
    check "actual live stop signalled" (first == StopSignalSent)
    firstD <- tryPersistentStopDeadline owner
    deadline <- latched firstD
    waitLeft <- remainingMicros deadline
    _ <- observeStop owner alternateStop waitLeft
    secondD <- tryPersistentStopDeadline owner
    check "repeated stop retains first exact D" (secondD == firstD)
    stopped <- invoke n
    check "stop refuses pending entry" (stopped == Left (OperationRefusedPreDispatch SessionClosed))
   CallbackUnknown -> do
    result <- enterLiveBatchRequest batch defaultPersistentActionBudget Nothing $ \_ -> do
     modifyIORef' effects (++ [n])
     pure (Left BadArguments :: Either ToolError ())
    check "entered failure is Unknown" (result == Left (OperationOutcomeUnknown BadArguments))
    noReplay <- invoke (n+1)
    check "Unknown poisons remaining batch before effect" (noReplay == Left (OperationRefusedPreDispatch SessionClosed))
   StopDuring -> do
    -- A tracked stopper runs only after the callback records entry. Barriers
    -- establish the interleaving; no sleep or physical syscall timeout claim.
    signal <- newEmptyMVar
    release <- newEmptyMVar
    done <- newEmptyMVar
    workerRef <- newIORef Nothing
    _ <- newStablePtr (owner,signal,release,done,effects,workerRef)
    let worker = do
         started <- readMVar signal
         if started then Just <$> requestSessionStop owner stopBudget else pure Nothing
        finalize = do
         void (tryPutMVar signal False)
         void (tryPutMVar release ())
         stopState <- tryPersistentStopDeadline owner
         waitLeft <- case stopState of
          StopDeadlineLatched deadline -> min 2000000 <$> remainingMicros deadline
          _ -> pure 0
         settled <- if waitLeft > 0 then timeout waitLeft (readMVar done) else pure Nothing
         check "stop worker completion observed" (case settled of Just _ -> True; Nothing -> False)
    mask $ \restore -> do
     workerId <- forkFinally (restore worker) (\result -> putMVar done result >> void (tryPutMVar release ()))
     writeIORef workerRef (Just workerId)
     restore (do
      result <- enterLiveBatchRequest batch defaultPersistentActionBudget Nothing $ \_ -> do
       modifyIORef' effects (++ [n])
       putMVar signal True
       readMVar release
       pure (Right ())
      firstD <- tryPersistentStopDeadline owner
      deadline <- latched firstD
      receiptWait <- remainingMicros deadline
      receipt <- if receiptWait > 0 then timeout receiptWait (readMVar done) else pure Nothing
      check "stop ran after callback entry" (case receipt of Just (Right (Just StopSignalSent)) -> True; _ -> False)
      check "entered stop outcome is Unknown" (result == Left (OperationOutcomeUnknown SessionClosed))
      waitLeft <- remainingMicros deadline
      _ <- observeStop owner alternateStop waitLeft
      secondD <- tryPersistentStopDeadline owner
      check "in-flight repeated stop retains exact D" (secondD == firstD)
      noReplay <- invoke (n+1)
      check "post-stop batch has no replay" (noReplay == Left (OperationRefusedPreDispatch SessionClosed))) `finally` finalize
  pure (admission,batch)
 (escapedAdmission,escapedBatch) <- either (ioError . userError . show) pure entered
 escapedClaim <- beginLiveFrameRequestBatch escapedAdmission frameD False 1
 check "escaped frame token cannot claim again" (case escapedClaim of Left SessionClosed -> True; _ -> False)
 escaped <- enterLiveBatchRequest escapedBatch defaultPersistentActionBudget Nothing $ \_ -> do
  modifyIORef' effects (++ [999])
  pure (Right ())
 check "escaped batch cannot run effect" (escaped == Left (OperationRefusedPreDispatch SessionClosed))
 observed <- readIORef effects
 check ("seed=" ++ show seed ++ " plan=" ++ show spec ++ " observed=" ++ show observed)
  (observed == [0..expectedCount-1])
