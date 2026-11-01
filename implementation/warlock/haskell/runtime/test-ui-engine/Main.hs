{-# LANGUAGE ScopedTypeVariables #-}
-- Real private child-process controls. Run only under the protected launcher,
-- nonthreaded, in a reviewed environment with user/PID namespaces available.
-- These are not WebKit, original-scenario, GUI or release acceptance.
module Main (main) where

import Control.Concurrent (threadDelay)
import Control.Exception (IOException, SomeException, displayException, try)
import Control.Monad (unless, void)
import Foreign.C.Types (CInt)
import Foreign.C.String (peekCStringLen)
import Foreign (allocaBytes, castPtr)
import System.Exit (ExitCode(..))
import System.IO (hFlush, stdout)
import System.Posix.Files (deviceID, fileID, getFdStatus, readSymbolicLink)
import System.Posix.IO (closeFd, createPipe, fdReadBuf, fdWrite)
import System.Posix.Process (ProcessStatus(..), exitImmediately, forkProcess,
  getParentProcessID, getProcessID, getProcessStatus)
import System.Posix.Types (Fd(..), ProcessID)
import Warlock.Capture.Process.Bootstrap (deadlineAfter, remainingMicros)
import Warlock.Ui.EngineCustody
import Warlock.Ui.PrivateNetwork (enterPrivateNetwork)

check :: String -> Bool -> IO ()
check label ok = unless ok (ioError (userError label))

newDeadline :: Int -> IO (IO Int)
newDeadline micros = do
 result <- deadlineAfter micros
 deadline <- either (ioError . userError . show) pure result
 pure (remainingMicros deadline)

ownedPid :: IO CInt
ownedPid = do
 -- The inherited procfs is mounted in the original PID namespace; its self
 -- link supplies the actual ancestor-visible identity, not the nested PID.
 value <- readSymbolicLink "/proc/self"
 case reads value of [(pid,"")] | pid > 0 -> pure pid; _ -> ioError (userError "proc self identity")

waitForExit :: IO Int -> CInt -> IO Bool
waitForExit remaining ref = do
 left <- remaining
 if left <= 0 then pure False else do
  done <- pidfdExited ref
  if done then pure True else threadDelay (min left 1000) >> waitForExit remaining ref

waitChild :: ProcessID -> IO Bool
waitChild pid = do
 remaining <- newDeadline 5000000
 let loop = do
      left <- remaining
      if left <= 0 then pure False else do
       result <- getProcessStatus False False pid
       case result of
        Just status -> pure (status == Exited ExitSuccess)
        Nothing -> threadDelay (min left 1000) >> loop
 loop

readFixture :: Fd -> IO String
readFixture fd@(Fd rawFd) = do
 remaining <- newDeadline 5000000
 let loop = do
      left <- remaining
      if left <= 0 then ioError (userError "fixture read deadline") else do
       ready <- fdReady rawFd
       if ready then allocaBytes 64 (\buffer -> do
         count <- fdReadBuf fd buffer 64
         peekCStringLen (castPtr buffer, fromIntegral count))
        else threadDelay (min left 1000) >> loop
 loop

closeRef :: CInt -> IO ()
closeRef ref = closeFd (Fd ref)

-- An independently forked owner starts PID1, then dies without cleanup while
-- a descendant still holds an inherited lifeline writer. The outer observer
-- obtains a pidfd before acknowledging owner exit. No host PID is signalled.
parentDeath :: IO ()
parentDeath = do
 (observedRead,observedWrite) <- createPipe
 (ackRead,ackWrite) <- createPipe
 owner <- forkProcess $ do
  closeFd observedRead
  closeFd ackWrite
  outcome <- try $ do
   enterPrivateNetwork
   remaining <- newDeadline 5000000
   _custody <- startCustody remaining
   _ <- forkProcess $ do
    ident <- ownedPid
    void (fdWrite observedWrite (show ident))
    closeFd observedWrite
    threadDelay 20000000
    exitImmediately ExitSuccess
   closeFd observedWrite
   _ <- readFixture ackRead
   exitImmediately ExitSuccess
  case outcome of
   Left (problem :: SomeException) -> do
    putStrLn ("parent_death_owner_failure=" ++ displayException problem)
    hFlush stdout
    exitImmediately (ExitFailure 1)
   Right () -> exitImmediately ExitSuccess
 closeFd observedWrite
 closeFd ackRead
 raw <- readFixture observedRead
 closeFd observedRead
 ident <- case reads raw of [(value,"")] -> pure value; _ -> ioError (userError "parent-death child identity")
 ref <- openPidfd ident
 alive <- pidfdExited ref
 check "parent-death descendant was alive" (not alive)
 void (fdWrite ackWrite "x")
 closeFd ackWrite
 ok <- waitChild owner
 check "parent-death owner exited" ok
 remaining <- newDeadline 5000000
 dead <- waitForExit remaining ref
 closeRef ref
 check "parent death terminates namespace descendants" dead

normalCustody :: IO ()
normalCustody = do
 refused <- try (startCustody (pure 0)) :: IO (Either IOException Custody)
 check "expired deadline refuses setup" (either (const True) (const False) refused)
 beforePid <- getProcessID
 beforeFd <- getFdStatus (Fd 0)
 beforeNs <- readSymbolicLink "/proc/self/ns/pid"
 -- A sibling created before PID-namespace setup must remain live and waitable
 -- after custody shutdown. It is controlled only by its own pipe, never by a
 -- PID or process-group signal; its pipe wait has a bounded deadline.
 (siblingRead,siblingWrite) <- createPipe
 sibling <- forkProcess $ do
  closeFd siblingWrite
  outcome <- try (readFixture siblingRead) :: IO (Either SomeException String)
  closeFd siblingRead
  exitImmediately (case outcome of Right "x" -> ExitSuccess; _ -> ExitFailure 1)
 closeFd siblingRead
 siblingRef <- openPidfd (fromIntegral sibling)
 siblingOwned <- verifyChild siblingRef
 siblingExited <- pidfdExited siblingRef
 check "pre-namespace sibling is owned and alive" (siblingOwned && not siblingExited)
 enterPrivateNetwork
 remaining <- newDeadline 8000000
 custody <- startCustody remaining
 afterPid <- getProcessID
 afterFd <- getFdStatus (Fd 0)
 afterNs <- readSymbolicLink "/proc/self/ns/pid"
 check "original owner PID retained" (beforePid == afterPid && beforeNs == afterNs)
 check "original fd0 retained" (deviceID beforeFd == deviceID afterFd && fileID beforeFd == fileID afterFd)
 foreignPid <- getParentProcessID
 foreignRef <- openPidfd (fromIntegral foreignPid)
 foreignOwned <- verifyChild foreignRef
 closeRef foreignRef
 check "foreign pidfd rejected" (not foreignOwned)
 stale <- verifyChild (-1)
 check "stale descriptor rejected" (not stale)
 second <- try (startCustody remaining) :: IO (Either IOException Custody)
 check "kernel refuses repeated PID namespace unshare" (either (const True) (const False) second)
 (reader,writer) <- createPipe
 worker <- forkProcess $ do
  closeFd reader
  _ <- forkProcess $ do
   ident <- ownedPid
   void (fdWrite writer (show ident))
   closeFd writer
   -- Deliberately retains the fork-inherited owner lifeline before exec.
   threadDelay 20000000
   exitImmediately ExitSuccess
  closeFd writer
  exitImmediately ExitSuccess
 closeFd writer
 raw <- readFixture reader
 closeFd reader
 ident <- case reads raw of [(value,"")] -> pure value; _ -> ioError (userError "grandchild identity")
 grandchild <- openPidfd ident
 reparented <- waitChild worker
 check "direct child exits before cleanup" reparented
 alive <- pidfdExited grandchild
 check "reparented descendant alive before cleanup" (not alive)
 exited <- stopCustody remaining custody
 descendantGone <- pidfdExited grandchild
 closeRef grandchild
 check "owned PID1 exit observed within deadline" exited
 check "reparented descendant terminated" descendantGone
 siblingStillOwned <- verifyChild siblingRef
 siblingStillAlive <- not <$> pidfdExited siblingRef
 check "namespace stop leaves unrelated child alive and waitable" (siblingStillOwned && siblingStillAlive)
 void (fdWrite siblingWrite "x")
 closeFd siblingWrite
 siblingFinished <- waitChild sibling
 closeRef siblingRef
 check "unrelated child exits normally under its own control" siblingFinished
 repeated <- stopCustody remaining custody
 check "already reaped custodian cannot certify cleanup twice" (not repeated)
 abandonCustody custody
 abandonCustody custody
 let unknown = productionCleanupFacts
 check "unqualified WebKit and callbacks remain false" (not (null (cleanupIssues unknown)))
 check "callback uncertainty distinct" (CallbacksNotRetired `elem` cleanupIssues unknown)
 check "deadline uncertainty distinct" (DeadlineExpired `elem` cleanupIssues unknown)

deadlineUncertainty :: Int -> IO ()
deadlineUncertainty remainingAtStop = do
 process <- forkProcess $ do
  outcome <- try $ do
   enterPrivateNetwork
   remaining <- newDeadline 5000000
   custody <- startCustody remaining
   observed <- stopCustody (pure remainingAtStop) custody
   abandonCustody custody
   check "expired cleanup remains uncertain" (not observed)
  case outcome of
   Left (_ :: SomeException) -> exitImmediately (ExitFailure 1)
   Right () -> exitImmediately ExitSuccess
 ok <- waitChild process
 check "deadline fixture" ok

main :: IO ()
main = parentDeath >> deadlineUncertainty 0 >> deadlineUncertainty 200000 >> normalCustody
