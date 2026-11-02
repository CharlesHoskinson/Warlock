-- Private QA adapter only. Root supplies registered owners, pinned child,
-- marker lifecycle, current original budgets and external process guardian.
-- It is not a backend/native acceptance test or a cleanup-success receipt.
module SeededBatchHarness (runAll) where

import Control.Exception (finally, mask)
import Control.Monad (forM_, unless)
import Data.IORef (atomicModifyIORef', newIORef, readIORef)
import Foreign.StablePtr (newStablePtr)
import System.IO (IOMode(ReadMode), openFile)
import Warlock.Capture.Process (SessionObservation, ToolError)
import Warlock.Capture.Process.Bootstrap (AdmissionDeadline, remainingMicros)
import Warlock.Capture.Process.Persistent
 ( PersistentOwner, StartBudget, StopBudget, SessionExit(..), StopDeadlineObservation(..), tryPersistentStopDeadline )
import Warlock.Capture.Process.Persistent.Internal (persistentFixture, withPersistentOwnerHook)
import qualified SeededBatchLifecycle as Seeded

-- Each allocator invocation is a fresh registered owner and a distinct owned
-- marker. removeMarker must be idempotent. suppliedFrameD mints the test frame's one original bound; it is never
-- renewed inside the generated sequence. verifyReady is Root's real fixture
-- check; this adapter cannot certify selected-executable or namespace identity.
runAll :: FilePath -> IO PersistentOwner -> IO FilePath -> (FilePath -> IO ())
       -> (FilePath -> SessionObservation -> IO (Either ToolError ()))
       -> IO StartBudget -> IO AdmissionDeadline -> StopBudget -> IO ()
runAll child allocOwner newMarker removeMarker verifyReady suppliedStart suppliedFrameD stopBudget =
 forM_ Seeded.seeds $ \seed -> mask $ \restore -> do
  owner <- allocOwner
  marker <- newMarker
  childInput <- openFile "/dev/null" ReadMode
  traceRef <- newIORef ([] :: [(String,StopDeadlineObservation,Maybe Int)])
  _ <- newStablePtr (owner,marker,childInput,traceRef)
  start <- suppliedStart
  let cleanup = removeMarker marker
      traceStage stage = do
       observedStop <- tryPersistentStopDeadline owner
       left <- case observedStop of StopDeadlineLatched deadline -> Just <$> remainingMicros deadline; _ -> pure Nothing
       atomicModifyIORef' traceRef (\events -> (events ++ [(stage,observedStop,left)],()))
  result <- restore (withPersistentOwnerHook owner (persistentFixture child [marker,"exit-when-removed"] childInput)
   4096 start stopBudget (verifyReady marker) (\live -> do
    frameD <- suppliedFrameD
    Seeded.runSeed owner live frameD stopBudget seed
    removeMarker marker) traceStage) `finally` cleanup
  trace <- readIORef traceRef
  unless (case result of Right ((), LeaderReaped _) -> True; _ -> False)
   (ioError (userError ("seed " ++ show seed ++ " owner outcome unconfirmed: " ++ show result ++ "; trace=" ++ show trace)))
  putStrLn ("PASS seeded lifecycle " ++ show seed ++ "; owned-handle natural-exit wait=" ++ show (any (\(stage,_,_) -> stage=="persistent-owned-handle-awaiting-natural-exit") trace))
