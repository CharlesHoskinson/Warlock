{-# LANGUAGE ForeignFunctionInterface #-}
{-# LANGUAGE ScopedTypeVariables #-}
-- Linux-only, nonthreaded early startup. The owner stays in its original PID
-- namespace; its subsequently forked children enter the new PID namespace.
module Warlock.Ui.EngineCustody
  ( Custody, startCustody, stopCustody, abandonCustody, verifyChild, openPidfd, pidfdExited, fdReady
  , Setup(..), NamespaceExit(..), CallbackRetirement(..), OwnerIdentity(..)
  , ProviderRoute(..), CleanupFacts(..), CleanupIssue(..), cleanupIssues
  , productionCleanupFacts
  ) where

#define _GNU_SOURCE
#include <sched.h>
#include <unistd.h>
#include <fcntl.h>
#include <poll.h>
#include <signal.h>
#include <sys/syscall.h>
#include <sys/wait.h>
#include <sys/prctl.h>
#include <limits.h>

import Control.Concurrent (threadDelay)
import Control.Exception (IOException, mask, onException, try)
import Control.Monad (unless, when)
import Data.Bits ((.|.), (.&.))
import Data.IORef
import Foreign (Ptr, alloca, allocaBytes, fillBytes, peek, peekByteOff, poke, pokeByteOff, nullPtr)
import Foreign.C
import System.Posix.Process (forkProcess, exitImmediately)
import System.Posix.Types (CSsize(..))
import System.Exit (ExitCode(..))
import System.Directory (listDirectory)

foreign import ccall unsafe "sigaction" c_sigaction :: CInt -> Ptr () -> Ptr () -> IO CInt
foreign import ccall unsafe "getpid" c_getpid :: IO CInt
foreign import ccall unsafe "getppid" c_getppid :: IO CInt
foreign import ccall unsafe "unshare" c_unshare :: CInt -> IO CInt
foreign import ccall unsafe "pipe2" c_pipe2 :: Ptr CInt -> CInt -> IO CInt
foreign import ccall unsafe "close" c_close :: CInt -> IO CInt
foreign import ccall unsafe "read" c_read :: CInt -> Ptr CChar -> CSize -> IO CSsize
foreign import ccall unsafe "write" c_write :: CInt -> Ptr CChar -> CSize -> IO CSsize
foreign import ccall unsafe "poll" c_poll :: Ptr () -> CULong -> CInt -> IO CInt
foreign import ccall unsafe "syscall" c_pidfdOpen :: CLong -> CInt -> CUInt -> IO CLong
foreign import ccall unsafe "syscall" c_closeRange :: CLong -> CUInt -> CUInt -> CUInt -> IO CLong
foreign import ccall unsafe "prctl" c_prctl :: CInt -> CULong -> CULong -> CULong -> CULong -> IO CInt
foreign import ccall unsafe "syscall" c_pidfdSignal :: CLong -> CInt -> CInt -> Ptr () -> CUInt -> IO CLong
foreign import ccall unsafe "waitid" c_waitid :: CInt -> CUInt -> Ptr () -> CInt -> IO CInt

-- Only the authenticated direct child may receive a pidfd-targeted signal.
-- Namespace descendants are terminated by the kernel; no numeric PID or
-- process group is signalled and unrelated children are never reaped.
data Custody = Custody (IORef (Maybe CInt)) (IORef (Maybe CInt))

closeQuiet :: CInt -> IO ()
closeQuiet fd = do _ <- c_close fd; pure ()

pipe :: IO (CInt,CInt)
pipe = allocaBytes (2 * #{size int}) $ \p -> do
  _ <- throwErrnoIfMinus1 "custody pipe2" (c_pipe2 p #{const O_CLOEXEC})
  (,) <$> peek p <*> peekByteOff p #{size int}

-- Called only in the just-forked, single-threaded PID1, before it handles
-- anything from the UI. close_range failures are fatal, not retried via a
-- partial descriptor census. Neither inherited fd0 nor fd1/fd2 survives.
child :: CInt -> CInt -> IO ()
child lifeline ready = do
  let lo = min lifeline ready; hi = max lifeline ready
      range a b = if a > b then pure True else do
        result <- c_closeRange #{const SYS_close_range} (fromIntegral a) (fromIntegral b) 0
        pure (result == 0)
  a <- range 0 (lo-1)
  b <- range (lo+1) (hi-1)
  c <- range (hi+1) (maxBound :: CInt)
  parentDeath <- c_prctl #{const PR_SET_PDEATHSIG} #{const SIGKILL} 0 0 0
  localPid <- c_getpid
  localParent <- c_getppid
  if not (a && b && c) || parentDeath /= 0 || localPid /= 1 || localParent /= 0 then exitImmediately (ExitFailure 111) else do
    sent <- alloca $ \p -> do poke p (1 :: CChar); c_write ready p 1
    closeQuiet ready
    if sent /= 1 then exitImmediately (ExitFailure 112) else do
      -- The writer is CLOEXEC, but a forked child can hold it until exec.
      -- EOF (or unexpected data/error) exits PID1; owner death and the
      -- exact pidfd shutdown also cover inherited writers.
      _ <- alloca $ \p -> c_read lifeline p 1
      exitImmediately ExitSuccess

pollFlags :: CInt -> IO CShort
pollFlags fd = allocaBytes #{size struct pollfd} $ \p -> do
  fillBytes p 0 #{size struct pollfd}
  pokeByteOff p #{offset struct pollfd, fd} fd
  pokeByteOff p #{offset struct pollfd, events} (#{const POLLIN} :: CShort)
  n <- throwErrnoIfMinus1 "custody poll" (c_poll p 1 0)
  if n == 0 then pure 0 else peekByteOff p #{offset struct pollfd, revents}

fdReady :: CInt -> IO Bool
fdReady fd = (/= 0) <$> pollFlags fd

readReady :: CInt -> IO Bool
readReady fd = alloca $ \p -> do
 n <- c_read fd p 1
 if n /= 1 then pure False else (== (1 :: CChar)) <$> peek p

-- Read-only references support source-level child/foreign ownership tests;
-- the only signal path accepts the opaque Custody, never a supplied PID.
openPidfd :: CInt -> IO CInt
openPidfd pid = do
 result <- c_pidfdOpen #{const SYS_pidfd_open} pid 0
 if result < 0 then throwErrno "custody pidfd_open" else pure (fromIntegral result)

pidfdExited :: CInt -> IO Bool
pidfdExited fd = do
 flags <- pollFlags fd
 pure (flags .&. #{const POLLIN} /= 0)

-- waitid(P_PIDFD) verifies that this descriptor still names our child. With
-- WNOWAIT it does not consume the status or interfere with GLib child reaping.
verifyChild :: CInt -> IO Bool
verifyChild fd = allocaBytes #{size siginfo_t} $ \p -> do
 fillBytes p 0 #{size siginfo_t}
 result <- c_waitid #{const P_PIDFD} (fromIntegral fd) p
   (#{const WEXITED} .|. #{const WNOHANG} .|. #{const WNOWAIT})
 pure (result == 0)

-- Reap only the already observed, directly owned PID1, never a wildcard or
-- a WebKit/GLib child. A failed or raced wait is uncertainty.
reapChild :: CInt -> IO Bool
reapChild fd = allocaBytes #{size siginfo_t} $ \p -> do
 fillBytes p 0 #{size siginfo_t}
 result <- c_waitid #{const P_PIDFD} (fromIntegral fd) p
   (#{const WEXITED} .|. #{const WNOHANG})
 if result /= 0 then pure False else do
  observedPid <- peekByteOff p #{offset siginfo_t, si_pid} :: IO CInt
  pure (observedPid > 0)

waitReady :: IO Int -> CInt -> CInt -> IO ()
waitReady remaining ready pidfd = do
 left <- remaining
 when (left <= 500000) (ioError (userError "custody ready deadline"))
 exited <- pollFlags pidfd
 when (exited /= 0) (ioError (userError "custodian exited before ready"))
 flags <- pollFlags ready
 if flags .&. #{const POLLIN} /= 0 then do
   ok <- readReady ready
   unless ok (ioError (userError "custodian ready invalid"))
 else if flags /= 0 then ioError (userError "custodian ready closed") else do
   threadDelay (min 1000 (left-500000))
   waitReady remaining ready pidfd

-- pidfd_open after fork has an identity guarantee only while the direct child
-- cannot be auto-reaped or reaped by another thread/handler. Refuse inherited
-- SIGCHLD handlers, SIG_IGN, SA_NOCLDWAIT, or an already multithreaded owner.
-- No signal disposition is changed. This is checked immediately around fork.
requireForkOwnership :: IO ()
requireForkOwnership = do
 tasks <- listDirectory "/proc/self/task"
 unless (length tasks == 1) (ioError (userError "custody requires a single OS thread"))
 allocaBytes #{size struct sigaction} $ \p -> do
  fillBytes p 0 #{size struct sigaction}
  _ <- throwErrnoIfMinus1 "custody SIGCHLD disposition" (c_sigaction #{const SIGCHLD} nullPtr p)
  handler <- peekByteOff p #{offset struct sigaction, sa_handler} :: IO (Ptr ())
  flags <- peekByteOff p #{offset struct sigaction, sa_flags} :: IO CInt
  unless (handler == nullPtr && flags .&. #{const SA_NOCLDWAIT} == 0)
    (ioError (userError "custody SIGCHLD ownership unavailable"))

-- Must be called after the user/network namespace but before any IO workers,
-- GTK, or renderer children. Any failure after unshare requires process exit:
-- this namespace-for-children cannot be rolled back in the same process.
startCustody :: IO Int -> IO Custody
startCustody remaining = mask $ \_ -> do
 left <- remaining
 when (left <= 500000) (ioError (userError "custody startup deadline"))
 requireForkOwnership
 (lifeRead,lifeWrite) <- pipe
 (readyRead,readyWrite) <- pipe `onException` (closeQuiet lifeRead >> closeQuiet lifeWrite)
 ownedFds <- newIORef [lifeRead,lifeWrite,readyRead,readyWrite]
 let forget fd = modifyIORef' ownedFds (filter (/= fd))
     closeOwned fd = forget fd >> closeQuiet fd
     closeAll = readIORef ownedFds >>= mapM_ closeQuiet
 flip onException closeAll $ do
  _ <- throwErrnoIfMinus1 "custody unshare PID" (c_unshare #{const CLONE_NEWPID})
  pid <- forkProcess (child lifeRead readyWrite)
  requireForkOwnership
  closeOwned lifeRead
  closeOwned readyWrite
  pidfd <- openPidfd (fromIntegral pid)
  modifyIORef' ownedFds (pidfd:)
  owned <- verifyChild pidfd
  unless owned (ioError (userError "custodian ownership uncertain"))
  waitReady remaining readyRead pidfd
  closeOwned readyRead
  life <- newIORef (Just lifeWrite)
  pidfdCell <- newIORef (Just pidfd)
  forget lifeWrite
  forget pidfd
  pure (Custody life pidfdCell)

-- Closing the owner's lifeline is idempotent. Never close a stale numeric fd
-- twice; atomically withdraw it first. This also handles exceptions/parent exit.
closeLife :: Custody -> IO ()
closeLife (Custody life _) = do
 fd <- atomicModifyIORef' life (\old -> (Nothing,old))
 maybe (pure ()) closeQuiet fd

-- Only a readable owned pidfd after lifeline closure is an exit observation.
-- Leave 200ms for the owner to finish its own original-deadline work. Polling
-- and timeout are bounded; expiry, poll errors and stale ownership stay false.
stopCustody :: IO Int -> Custody -> IO Bool
stopCustody remaining custody@(Custody _ pidfdCell) = mask $ \_ -> do
 closeLife custody
 fd <- readIORef pidfdCell
 case fd of
  Nothing -> pure False
  Just pidfd -> do
   owned <- verifyChild pidfd
   if not owned then pure False else do
    -- pidfd targets exactly the verified child, never a numeric PID or a
    -- process group. This also closes the fork-before-exec lifeline leak gap.
    _ <- c_pidfdSignal #{const SYS_pidfd_send_signal} pidfd #{const SIGKILL} nullPtr 0
    let loop = do
         left <- remaining
         if left <= 200000 then pure False else do
          flags <- pollFlags pidfd
          if flags .&. #{const POLLIN} /= 0 then reapChild pidfd else
           if flags /= 0 then pure False else threadDelay (min 1000 (left-200000)) >> loop
    outcome <- try loop :: IO (Either IOException Bool)
    pure (either (const False) id outcome)

-- Safe even if called repeatedly. No wait/reap here.
abandonCustody :: Custody -> IO ()
abandonCustody custody@(Custody _ pidfdCell) = mask $ \_ -> do
 closeLife custody
 fd <- atomicModifyIORef' pidfdCell (\old -> (Nothing,old))
 case fd of
  Nothing -> pure ()
  Just pidfd -> do
   owned <- verifyChild pidfd
   when owned $ do
    _ <- c_pidfdSignal #{const SYS_pidfd_send_signal} pidfd #{const SIGKILL} nullPtr 0
    pure ()
   closeQuiet pidfd

data Setup = SetupRefused | SetupUnknown | SetupReady deriving (Eq,Show)
data NamespaceExit = ExitUnobserved | ExitObserved deriving (Eq,Show)
data CallbackRetirement = CallbackPending | CallbacksRetired deriving (Eq,Show)
data OwnerIdentity = OwnerUncertain | OwnerForeign | OwnerCurrent deriving (Eq,Show)
data ProviderRoute = ProviderUnqualified | ProviderConfined deriving (Eq,Show)
data CleanupFacts = CleanupFacts { custodySetup :: Setup, custodyExit :: NamespaceExit
  , custodyCallbacks :: CallbackRetirement, custodyOwner :: OwnerIdentity
  , custodyProvider :: ProviderRoute, custodyBeforeDeadline :: Bool } deriving (Eq,Show)
data CleanupIssue = NamespaceNotReady | NamespaceExitNotObserved | CallbacksNotRetired
  | OwnershipNotCurrent | ProviderNotQualified | DeadlineExpired deriving (Eq,Show)
cleanupIssues :: CleanupFacts -> [CleanupIssue]
cleanupIssues facts = [NamespaceNotReady | custodySetup facts /= SetupReady] ++
  [NamespaceExitNotObserved | custodyExit facts /= ExitObserved] ++
  [CallbacksNotRetired | custodyCallbacks facts /= CallbacksRetired] ++
  [OwnershipNotCurrent | custodyOwner facts /= OwnerCurrent] ++
  [ProviderNotQualified | custodyProvider facts /= ProviderConfined] ++
  [DeadlineExpired | not (custodyBeforeDeadline facts)]
productionCleanupFacts :: CleanupFacts
productionCleanupFacts = CleanupFacts SetupUnknown ExitUnobserved CallbackPending OwnerUncertain ProviderUnqualified False
