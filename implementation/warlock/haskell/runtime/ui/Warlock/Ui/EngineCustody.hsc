{-# LANGUAGE ForeignFunctionInterface #-}
{-# LANGUAGE ScopedTypeVariables #-}
{-# LANGUAGE RankNTypes #-}
-- Linux-only, nonthreaded early startup. The owner stays in its original PID
-- namespace; its subsequently forked children enter the new PID namespace.
module Warlock.Ui.EngineCustody
  ( EngineProcess, ImageFacts(..), startUnreadyEngine, takeEngineChannel, enginePid, engineImageFacts, engineExpectedIds, engineLiveChild, engineCredentialGuard, stopEngineProcess
  , Custody, startCustody, stopCustody, abandonCustody, verifyChild, openPidfd, pidfdExited, fdReady
  , Setup(..), NamespaceExit(..), CallbackRetirement(..), OwnerIdentity(..)
  , ProviderRoute(..), CleanupFacts(..), CleanupIssue(..), cleanupIssues
  , productionCleanupFacts
  ) where

#define _GNU_SOURCE
#include <sched.h>
#include <sys/mount.h>
#include <sys/socket.h>
#include <linux/capability.h>
#include <linux/close_range.h>
#include <sys/vfs.h>
#include <linux/magic.h>
#include <unistd.h>
#include <fcntl.h>
#include <poll.h>
#include <signal.h>
#include <sys/syscall.h>
#include <sys/wait.h>
#include <sys/prctl.h>
#include <limits.h>

import Control.Concurrent (threadDelay)
import Control.Concurrent.MVar (MVar, newMVar, withMVar)
import Control.Exception (IOException, SomeException, bracket, mask, mask_, onException, try, throwIO)
import Control.Monad (unless, when)
import Data.Bits ((.|.), (.&.), complement)
import Data.Word (Word32, Word64)
import qualified Data.ByteString as B
import qualified Data.Text as T
import qualified Crypto.Hash.SHA256 as SHA256
import qualified Network.Socket as S
import Text.Read (readMaybe)
import System.IO (hClose)
import System.Timeout (timeout)
import System.Posix.Files (FileStatus, getFdStatus, isRegularFile, isNamedPipe, isSocket, deviceID, fileID, fileSize)
import System.Posix.IO (FdOption(CloseOnExec,NonBlockingRead), OpenMode(ReadOnly), closeFd, createPipe, defaultFileFlags, fdToHandle, openFd, setFdOption)
import System.Posix.Types (Fd(..))
import System.Posix.User (getEffectiveUserID, getEffectiveGroupID)
import Warlock.Capture.Process.Bootstrap (AdmissionDeadline, deadlineAbsoluteNs, remainingMicros)
import Warlock.Protocol.CredentialGuard (CredentialGuard(..))
import qualified Warlock.Protocol.PeerCredential as Credential
import Foreign.Marshal.Alloc (mallocBytes, free)
import Foreign.Marshal.Array (withArray0)
import Foreign.Marshal.Utils (withMany)
import Data.IORef
import Foreign (Ptr, alloca, allocaBytes, fillBytes, peek, peekByteOff, poke, pokeByteOff, nullPtr)
import Foreign.C
import System.Posix.Process (forkProcess, exitImmediately)
import System.Posix.Types (CSsize(..))
import System.Exit (ExitCode(..))
import System.Directory (listDirectory)

foreign import ccall unsafe "mount" c_mount :: CString -> CString -> CString -> CULong -> Ptr () -> IO CInt
foreign import ccall unsafe "fcntl" c_fcntl :: CInt -> CInt -> CInt -> IO CInt
foreign import ccall unsafe "setsockopt" c_setsockopt :: CInt -> CInt -> CInt -> Ptr CInt -> CUInt -> IO CInt
foreign import ccall unsafe "fstatfs" c_fstatfs :: CInt -> Ptr () -> IO CInt
foreign import ccall unsafe "syscall" c_execveat :: CLong -> CInt -> CString -> Ptr CString -> Ptr CString -> CInt -> IO CLong
foreign import ccall unsafe "syscall" c_capset :: CLong -> Ptr () -> Ptr () -> IO CLong
foreign import ccall unsafe "syscall" c_capget :: CLong -> Ptr () -> Ptr () -> IO CLong
foreign import ccall unsafe "_exit" c_exit :: CInt -> IO ()
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


-- BEGIN UNEXECUTED ENGINE PREPARATION DRAFT. Existing custody APIs above are unchanged.
data ImageFacts = ImageFacts !Integer !Integer !Integer !B.ByteString deriving (Eq,Show)
data Prepared = Prepared
  { pendingSlots :: !(Ptr ())
  , heldSelf :: !(IORef (Maybe Fd))
  , brokerSocket :: !(IORef (Maybe S.Socket))
  , childSocket :: !(IORef (Maybe S.Socket))
  , preparedLifeRead :: !(IORef (Maybe Fd))
  , preparedLifeWrite :: !(IORef (Maybe Fd))
  , heldImageFacts :: !ImageFacts
  , preparedDeadline :: !AdmissionDeadline
  }

slotSize :: Int
slotSize = #{size int}

-- Only this fixed set of roles is representable; no caller-provided FD map.
slotCount :: Int
slotCount = 3

putSlot :: Ptr () -> Int -> CInt -> IO ()
putSlot slots index fd = pokeByteOff slots (index * slotSize) fd
getSlot :: Ptr () -> Int -> IO CInt
getSlot slots index = peekByteOff slots (index * slotSize)

require :: Bool -> String -> IO ()
require b message = unless b (ioError (userError message))

-- A close attempt irrevocably withdraws a cell even if close reports an error.
-- This prevents unsafe numeric-FD retry; the caller must mark custody unknown.
withdraw :: IORef (Maybe a) -> IO (Maybe a)
withdraw cell = atomicModifyIORef' cell (\old -> (Nothing,old))

closeCell :: (a -> IO ()) -> IORef (Maybe a) -> IO (Either SomeException ())
closeCell close cell = do
  owned <- withdraw cell
  case owned of Nothing -> pure (Right ()); Just value -> try (close value)

closeRawSlot :: Ptr () -> Int -> IO (Either SomeException ())
closeRawSlot slots index = do
  fd <- getSlot slots index
  if fd < 0 then pure (Right ()) else do
    putSlot slots index (-1)
    try (closeFd (Fd fd))

-- This routine NEVER calls waitpid or sends signals: it cleans only the
-- acquisition phase or descriptors whose sole custody has been settled by
-- EngineCustody. It is NOT safe to call while fork child ownership is unknown.
-- Repeated calls on already released/free slots are forbidden; EngineCustody
-- owns the Prepared once. Failure retains a failed/unknown cleanup result.
releasePrepared :: Prepared -> IO (Either SomeException ())
releasePrepared p = mask_ $ do
  raw <- mapM (closeRawSlot (pendingSlots p)) [0..slotCount-1]
  cc <- closeCell S.close (childSocket p)
  bc <- closeCell S.close (brokerSocket p)
  lr <- closeCell closeFd (preparedLifeRead p)
  lw <- closeCell closeFd (preparedLifeWrite p)
  held <- closeCell closeFd (heldSelf p)
  free (pendingSlots p)
  case [err | Left err <- raw ++ [cc,bc,lr,lw,held]] of
    [] -> pure (Right ())
    err:_ -> pure (Left err)

-- Verify a *held* self descriptor's device/inode/size and SHA256 from its own
-- duplicate, NOT from a child assertion. A finite ELF image limit bounds memory.
-- Concurrent writes/in-place mutation, proc mount identity and source/build
-- provenance still require independent verification at ready and retirement.
sameFile :: FileStatus -> FileStatus -> Bool
sameFile a b = deviceID a == deviceID b && fileID a == fileID b && fileSize a == fileSize b

hashHeld :: Fd -> IO ImageFacts
hashHeld fd@(Fd number) = do
  before <- getFdStatus fd
  let size = toInteger (fileSize before)
  require (isRegularFile before && size > 0 && size <= 268435456) "held ELF size/type refused"
  duplicate <- c_fcntl number #{const F_DUPFD_CLOEXEC} 3
  require (duplicate >= 3) "hash duplicate failed"
  -- Ownership transfers exactly once from the duplicate fd to Handle. The
  -- Handle is CLOSED BEFORE FORK; it does not own any raw child role duplicate.
  handle <- fdToHandle (Fd duplicate) `onException` closeFd (Fd duplicate)
  bytes <- B.hGet handle (fromInteger size + 1) `onException` hClose handle
  hClose handle
  after <- getFdStatus fd
  require (sameFile before after && toInteger (B.length bytes) == size) "held ELF changed/short read"
  require (B.take 4 bytes == B.pack [0x7f,0x45,0x4c,0x46]) "held image is not ELF"
  pure (ImageFacts (toInteger (deviceID before)) (toInteger (fileID before)) size (SHA256.hash bytes))

-- Record F_DUPFD_CLOEXEC result before any fstat, allocation or subsequent
-- duplicate. The mask plus unsafe FFI narrows the acquisition/publication gap;
-- actual Haskell synchronous exceptions, RTS behavior, preexisting stale
-- finalizers and no foreign concurrent close remain mandatory review gates.
duplicateRole :: Ptr () -> Int -> CInt -> IO ()
duplicateRole slots index source = do
  duplicate <- c_fcntl source #{const F_DUPFD_CLOEXEC} 3
  require (duplicate >= 3) "engine fixed-role duplicate failed"
  putSlot slots index duplicate

enableCredentials :: S.Socket -> IO ()
enableCredentials socket = S.withFdSocket socket $ \fd -> alloca $ \value -> do
  poke value (1 :: CInt)
  rc <- c_setsockopt fd #{const SOL_SOCKET} #{const SO_PASSCRED} value (#{size int} :: CUInt)
  require (rc == 0) "engine SO_PASSCRED unavailable"

-- Set nonblocking status before either endpoint is used; otherwise sendAll
-- can block the nonthreaded RTS past D despite a Haskell-level timeout.
-- Child re-establishes CLOEXEC after exec and verifies both flags again.
configureEngineSocket :: S.Socket -> IO ()
configureEngineSocket socket = S.withFdSocket socket $ \number -> do
  let fd = Fd number
  setFdOption fd CloseOnExec True
  setFdOption fd NonBlockingRead True
  status <- c_fcntl number #{const F_GETFL} 0
  descriptor <- c_fcntl number #{const F_GETFD} 0
  require (status >= 0 && descriptor >= 0
           && status .&. #{const O_NONBLOCK} /= 0
           && descriptor .&. #{const FD_CLOEXEC} /= 0) "engine socket flags invalid"

-- Both socket endpoints and both pipe endpoints are ordinary parent-owned
-- resources. All get CLOEXEC before fork. A copied child holds the lifeline
-- writer UNTIL exec: the child pre-exec poll therefore cannot prove the
-- parent survived the fork/PDEATHSIG race. Engine FIRST postexec admission must
-- rearm/check PDEATHSIG and poll the lifeline, then monitor it continuously.
--
-- IMPORTANT: EngineCustody must allocate `slots` and publish all EMPTY resource
-- cells into its existing pending ledger BEFORE calling this, rather than use
-- this illustrative standalone constructor without that outer owner. Socket and
-- createPipe acquisition also need actual exception-publication review. A raw
-- fd returned by the kernel but not yet registered cannot be safely forgotten.
prepareEngineOwned :: AdmissionDeadline -> IO Prepared
prepareEngineOwned deadline = mask_ $ do
  left <- remainingMicros deadline
  require (left > 500000) "engine preparation deadline"
  slots <- mallocBytes (slotCount * slotSize)
  mapM_ (\i -> putSlot slots i (-1)) [0..slotCount-1]
  selfCell <- newIORef Nothing
  brokerCell <- newIORef Nothing
  childCell <- newIORef Nothing
  lifeReadCell <- newIORef Nothing
  lifeWriteCell <- newIORef Nothing
  -- Temporary initial facts cannot be published as a valid Prepared; only
  -- constructing the final record after real hash succeeds permits return.
  let cleanup = do
        raw <- mapM (closeRawSlot slots) [0..slotCount-1]
        cc <- closeCell S.close childCell
        bc <- closeCell S.close brokerCell
        lr <- closeCell closeFd lifeReadCell
        lw <- closeCell closeFd lifeWriteCell
        self <- closeCell closeFd selfCell
        free slots
        case [err | Left err <- raw ++ [cc,bc,lr,lw,self]] of
          [] -> pure ()
          err:_ -> throwIO err
      register cell value = atomicModifyIORef' cell (\_ -> (Just value,()))
  (do
    -- /proc/self/exe is a kernel magic link, so O_NOFOLLOW must NOT be applied
    -- to this final component. Verify trusted procfs and held inode separately;
    -- retain the open file through fork and compare to the real owner image.
    image <- openFd "/proc/self/exe" ReadOnly defaultFileFlags
    register selfCell image
    setFdOption image CloseOnExec True
    facts <- hashHeld image
    (broker,childSocketValue) <- S.socketPair S.AF_UNIX S.Stream S.defaultProtocol
    register brokerCell broker
    register childCell childSocketValue
    S.withFdSocket broker (\fd -> require (fd >= 3) "engine broker standard descriptor refused")
    S.withFdSocket childSocketValue (\fd -> require (fd >= 3) "engine child standard descriptor refused")
    configureEngineSocket broker
    configureEngineSocket childSocketValue
    enableCredentials broker
    (reader,writer) <- createPipe
    register lifeReadCell reader
    register lifeWriteCell writer
    setFdOption reader CloseOnExec True
    setFdOption writer CloseOnExec True
    let Fd imageNumber = image
        Fd lifeNumber = reader
    duplicateRole slots 0 imageNumber
    S.withFdSocket childSocketValue (duplicateRole slots 1)
    duplicateRole slots 2 lifeNumber
    values <- mapM (getSlot slots) [0..slotCount-1]
    require (all (>=3) values && length values == 3 && length (unique values) == 3) "engine roles invalid"
    imageDup <- getFdStatus (Fd (values !! 0))
    rpcDup <- getFdStatus (Fd (values !! 1))
    lifeDup <- getFdStatus (Fd (values !! 2))
    imageSource <- getFdStatus image
    lifeSource <- getFdStatus reader
    rpcSource <- S.withFdSocket childSocketValue (getFdStatus . Fd)
    let ImageFacts dev ino size _ = facts
    require (sameFile imageDup imageSource && toInteger (deviceID imageDup) == dev
             && toInteger (fileID imageDup) == ino && toInteger (fileSize imageDup) == size)
            "engine image duplicate identity"
    require (isSocket rpcDup && sameFile rpcDup rpcSource) "engine RPC duplicate identity"
    require (isNamedPipe lifeDup && sameFile lifeDup lifeSource) "engine lifeline duplicate identity"
    lifeFlags <- c_fcntl (values !! 2) #{const F_GETFL} 0
    require (lifeFlags >= 0 && lifeFlags .&. #{const O_ACCMODE} == #{const O_RDONLY}) "engine lifeline is not read-only"
    remaining <- remainingMicros deadline
    require (remaining > 0) "engine preparation deadline"
    pure (Prepared slots selfCell brokerCell childCell lifeReadCell lifeWriteCell facts deadline))
    `onException` cleanup
  where
    unique [] = []
    unique (x:xs) = x : unique (filter (/= x) xs)


data ChildInputs = ChildInputs
  { imageFd :: !CInt, rpcFd :: !CInt, lifeFd :: !CInt
  , emptyPath :: !CString, rootPath :: !CString, procPath :: !CString
  , procType :: !CString, childArgv :: !(Ptr CString), childEnv :: !(Ptr CString)
  , pollSlot :: !(Ptr ())
  -- Pinned parent-allocated buffers: cap header and two v3 capability words.
  -- Parent obtains kernel cap_last_cap before fork, rejects malformed or >1024.
  , capHeader :: !(Ptr ()), capData :: !(Ptr ()), capLast :: !CInt
  }

-- Must run after the mount and before exec, GTK, helper creation or any
-- authenticated engine message. Bounding drop needs CAP_SETPCAP, so it must
-- precede clearing permitted/effective sets. A partial operation is fatal.
-- capLast comes from a validated actual-kernel read, not a compiled constant.
-- This Haskell recursion and FFI are STILL subject to the open post-fork RTS
-- safety proof; all buffers must have been allocated before fork.
dropCapabilities :: ChildInputs -> IO Bool
dropCapabilities p = do
 let lastCap = capLast p
     eachDrop n | n > lastCap = pure True
                | otherwise = do
                    result <- c_prctl #{const PR_CAPBSET_DROP} (fromIntegral n) 0 0 0
                    if result /= 0 then pure False else eachDrop (n+1)
     eachCheck n | n > lastCap = pure True
                 | otherwise = do
                    bound <- c_prctl #{const PR_CAPBSET_READ} (fromIntegral n) 0 0 0
                    ambient <- c_prctl #{const PR_CAP_AMBIENT} #{const PR_CAP_AMBIENT_IS_SET} (fromIntegral n) 0 0
                    if bound /= 0 || ambient /= 0 then pure False else eachCheck (n+1)
 if lastCap < 0 || lastCap > 1024 then pure False else do
  dropped <- eachDrop 0
  if not dropped then pure False else do
   ambient <- c_prctl #{const PR_CAP_AMBIENT} #{const PR_CAP_AMBIENT_CLEAR_ALL} 0 0 0
   if ambient /= 0 then pure False else do
    fillBytes (capHeader p) 0 #{size struct __user_cap_header_struct}
    pokeByteOff (capHeader p) #{offset struct __user_cap_header_struct, version} (#{const _LINUX_CAPABILITY_VERSION_3} :: Word32)
    fillBytes (capData p) 0 (2 * #{size struct __user_cap_data_struct})
    cleared <- c_capset #{const SYS_capset} (capHeader p) (capData p)
    if cleared /= 0 then pure False else do
     noPrivs <- c_prctl #{const PR_SET_NO_NEW_PRIVS} 1 0 0 0
     if noPrivs /= 0 then pure False else do
      -- Sentinel first, so a failed or partial read is never mistaken for zero.
      fillBytes (capData p) 255 (2 * #{size struct __user_cap_data_struct})
      got <- c_capget #{const SYS_capget} (capHeader p) (capData p)
      if got /= 0 then pure False else do
       a <- peekByteOff (capData p) 0 :: IO Word32
       b <- peekByteOff (capData p) 4 :: IO Word32
       c <- peekByteOff (capData p) 8 :: IO Word32
       d <- peekByteOff (capData p) 12 :: IO Word32
       e <- peekByteOff (capData p) 16 :: IO Word32
       f <- peekByteOff (capData p) 20 :: IO Word32
       if a /= 0 || b /= 0 || c /= 0 || d /= 0 || e /= 0 || f /= 0
        then pure False else eachCheck 0

-- Parent validates actual held image / FD identities and exact engine-only
-- argument/environment; range, collision and ownership checks are repeated
-- below. F_GETFD identifies an already closed descriptor only; it is not proof
-- of underlying identity. Authentication and readiness happen AFTER exec.
childSetupExec :: ChildInputs -> IO ()
childSetupExec p = do
 let image = imageFd p; rpc = rpcFd p; life = lifeFd p
     failChild = c_exit 121
     valid = image >= 3 && rpc >= 3 && life >= 3
          && image /= rpc && image /= life && rpc /= life
 if not valid then failChild else do
  local <- c_getpid
  parent <- c_getppid
  -- Outside-namespace parent appears as zero, not as proof of liveness.
  if local /= 1 || parent /= 0 then failChild else do
   death <- c_prctl #{const PR_SET_PDEATHSIG} #{const SIGKILL} 0 0 0
   if death /= 0 then failChild else do
    -- Parent-only writer is retained by the broker, never inherited past exec.
    pokeByteOff (pollSlot p) #{offset struct pollfd, fd} life
    pokeByteOff (pollSlot p) #{offset struct pollfd, events} (#{const POLLIN} :: CShort)
    pokeByteOff (pollSlot p) #{offset struct pollfd, revents} (0 :: CShort)
    alive <- c_poll (pollSlot p) 1 0
    events <- peekByteOff (pollSlot p) #{offset struct pollfd, revents} :: IO CShort
    -- EOF/HUP, data, error and EINTR all refuse; no retry after uncertainty.
    if alive /= 0 || events /= 0 then failChild else do
     moved <- c_unshare #{const CLONE_NEWNS}
     if moved /= 0 then failChild else do
      private <- c_mount nullPtr (rootPath p) nullPtr
         (#{const MS_REC} .|. #{const MS_PRIVATE}) nullPtr
      if private /= 0 then failChild else do
       proc <- c_mount (procType p) (procPath p) (procType p)
          (#{const MS_NOSUID} .|. #{const MS_NODEV} .|. #{const MS_NOEXEC}) nullPtr
       if proc /= 0 then failChild else do
        capsClear <- dropCapabilities p
        if not capsClear then failChild else do
        -- Mark, do not close: preserve copied-heap descriptor numbering.
         marked <- c_closeRange #{const SYS_close_range} 0 (maxBound :: CUInt) #{const CLOSE_RANGE_CLOEXEC}
         if marked /= 0 then failChild else do
          rpcFlags <- c_fcntl rpc #{const F_GETFD} 0
          lifeFlags <- c_fcntl life #{const F_GETFD} 0
          imageFlags <- c_fcntl image #{const F_GETFD} 0
          if rpcFlags < 0 || lifeFlags < 0 || imageFlags < 0
            || imageFlags .&. #{const FD_CLOEXEC} == 0
           then failChild else do
            a <- c_fcntl rpc #{const F_SETFD} (rpcFlags .&. complement #{const FD_CLOEXEC})
            b <- c_fcntl life #{const F_SETFD} (lifeFlags .&. complement #{const FD_CLOEXEC})
            if a /= 0 || b /= 0 then failChild else do
            -- Only the same verified held ELF; not a path lookup. An ELF
            -- loader, kernel and executable-FD CLOEXEC combination must be
            -- proven in the exact target; scripts/interpreters are excluded.
             _ <- c_execveat #{const SYS_execveat} image (emptyPath p)
                  (childArgv p) (childEnv p) #{const AT_EMPTY_PATH}
             failChild


-- EngineProcess is owned but intentionally NOT authenticated or provider-ready.
-- Internal API for the trusted engine transport. This is merely a launched
-- owned process; no authentication or readiness is represented here.
-- Before starting workers or returning a passing result, the caller must
-- validate peer credentials on every fragment, held image, namespace/PID1,
-- post-exec lifeline and capability facts and original deadline.
data EngineProcess = EngineProcess Custody (IORef (Maybe S.Socket)) CInt ImageFacts (Integer,Integer) AdmissionDeadline (MVar ())

enginePid :: EngineProcess -> CInt
enginePid (EngineProcess _ _ pid _ _ _ _) = pid

engineImageFacts :: EngineProcess -> ImageFacts
engineImageFacts (EngineProcess _ _ _ facts _ _ _) = facts

-- Source is the actual parent identity captured after entering the user
-- namespace, never a request body or caller-supplied credential string.
engineExpectedIds :: EngineProcess -> (Integer,Integer)
engineExpectedIds (EngineProcess _ _ _ _ ids _ _) = ids

-- Package-internal ownership TRANSFER, not a borrow: atomically withdraw once
-- under the same gate used by stop. The trusted Broker takes sole close
-- ownership after transfer; stopEngineProcess no longer owns this Socket.
-- Caller must hold an outer mask across transfer and Broker construction and
-- explicitly track the precise constructor ownership boundary. Close exactly
-- once if transfer has returned but Broker has NOT yet accepted ownership;
-- never repeat close after Broker has adopted/closed it on failure. Never
-- expose this channel to page content or bypass SCM/ready checks.
takeEngineChannel :: EngineProcess -> IO S.Socket
takeEngineChannel (EngineProcess _ cell _ _ _ _ gate) = mask_ $ withMVar gate $ \_ -> do
  current <- withdraw cell
  maybe (ioError (userError "engine channel already transferred or retired")) pure current

-- Original D bounds stopping/reaping. A failed close or unobserved reap is
-- false; no finalizer, second waiter or unrelated PID is used.
stopEngineProcess :: EngineProcess -> IO Bool
stopEngineProcess (EngineProcess custody socketCell _ _ _ deadline gate) = mask_ $ withMVar gate $ \_ -> do
  stopped <- stopCustody (remainingMicros deadline) custody
  closed <- closeCell S.close socketCell
  abandonCustody custody
  pure (stopped && either (const False) (const True) closed)

-- Trusted transport checks this around each bounded SCM-credential-bearing
-- receive. This is a nonreaping owned-pidfd check, not PID authentication by
-- itself; transport must compare kernel sender PID/UID/GID, session, frame,
-- held image/birth, namespace and original deadline independently. Both stop
-- and this observation serialize through the same gate; transport must check
-- again after each receive because the peer can exit immediately afterward.
engineLiveChild :: EngineProcess -> CInt -> IO Bool
engineLiveChild (EngineProcess (Custody _ pidCell) _ expected _ _ _ gate) sender =
 withMVar gate $ \_ -> do
  current <- readIORef pidCell
  case current of
   Just pidfd | sender == expected -> do
    ownedChild <- verifyChild pidfd
    flags <- pollFlags pidfd
    pure (ownedChild && flags == 0)
   _ -> pure False

-- Private helper is called ONLY with this EngineProcess gate held; it never
-- reacquires the MVar, never reaps and never supplies a raw pidfd to callers.
-- Kernel SCM credentials and the held child pidfd are both required. The
-- pidfd owns process birth; expected IDs come from trusted parent sampling.
checkCredentialHeld :: EngineProcess -> Credential.PeerCredential -> IO (Either T.Text ())
checkCredentialHeld (EngineProcess (Custody _ pidCell) _ expected _ (uid,gid) deadline _) credential = do
 left <- remainingMicros deadline
 current <- readIORef pidCell
 case current of
  Just pidfd | left > 0
             && Credential.credentialPid credential == toInteger expected
             && Credential.credentialUid credential == uid
             && Credential.credentialGid credential == gid -> do
   owned <- verifyChild pidfd
   flags <- pollFlags pidfd
   after <- remainingMicros deadline
   pure (if owned && flags == 0 && after > 0 then Right () else Left (T.pack "engine child unavailable"))
  _ -> pure (Left (T.pack "engine credential refused"))

-- Only the package-owned process can construct this paired guard. Every recv
-- fragment must pass checkFragment. The final finite Owner admission callback
-- is serialized against stopEngineProcess through THE SAME gate, verified
-- both before and after, and bounded by the original D. It must not perform
-- RPC, native effects, reaping, or re-enter this gate. If it times out or the
-- post-check fails, its effects may already have occurred: poison the channel,
-- never replay, and never report clean retirement based on this Left. Haskell
-- timeout cannot interrupt an unsafe/blocking FFI; review actual callback and
-- provider scheduling rather than treating this as hard real-time proof.
engineCredentialGuard :: EngineProcess -> CredentialGuard T.Text
engineCredentialGuard process@(EngineProcess _ _ _ _ _ deadline gate) = CredentialGuard
  (\credential -> withMVar gate (\_ -> checkCredentialHeld process credential))
  (\credential action -> withMVar gate $ \_ -> do
    before <- checkCredentialHeld process credential
    case before of
     Left refusal -> pure (Left refusal)
     Right () -> do
      left <- remainingMicros deadline
      if left <= 0 then pure (Left (T.pack "engine admission deadline")) else do
       result <- timeout left action
       case result of
        Nothing -> pure (Left (T.pack "engine admission outcome uncertain"))
        Just value -> do
         after <- checkCredentialHeld process credential
         pure (case after of Left refusal -> Left refusal; Right () -> Right value))

-- Limit this kernel-read-before-fork to capability v3's two words. If the
-- kernel ever supports more, fail closed until the ABI is redesigned.
readLastCapability :: IO CInt
readLastCapability = do
  raw <- B.readFile "/proc/sys/kernel/cap_last_cap"
  require (B.length raw > 0 && B.length raw <= 16) "cap_last_cap size"
  case readMaybe (map (toEnum . fromEnum) (B.unpack raw)) :: Maybe Int of
    Just value | value >= 0 && value <= 63 -> pure (fromIntegral value)
    _ -> ioError (userError "cap_last_cap unsupported")

-- Reject an alternate filesystem at /proc before using self/exe or kernel cap
-- metadata. Mount identity/namespace must also remain bound and be checked by
-- the eventual authenticated startup verifier; filesystem magic alone is not
-- evidence of the required namespace.
requireProcfs :: IO ()
requireProcfs = bracket (openFd "/proc" ReadOnly defaultFileFlags) closeFd $ \(Fd fd) ->
 allocaBytes #{size struct statfs} $ \p -> do
  rc <- c_fstatfs fd p
  require (rc == 0) "engine procfs fstatfs failed"
  magic <- peekByteOff p #{offset struct statfs, f_type} :: IO CLong
  require (magic == fromIntegral (#{const PROC_SUPER_MAGIC} :: Integer)) "engine procfs required"

-- Trusted config only: do not pass an inherited environment wholesale. The
-- separately reviewed Display validation must establish the runtime directory
-- and Wayland socket first. Duplicate, NUL and unexpected names are fatal.
engineEnvironment :: [(String,String)] -> IO [String]
engineEnvironment pairs = do
  let keys = map fst pairs
      valid (key,value) = key `elem` ["LANG","LC_ALL","XDG_RUNTIME_DIR","WAYLAND_DISPLAY"]
                       && '\0' `notElem` value && not (null value)
      unique [] = True
      unique (x:xs) = x `notElem` xs && unique xs
  require (all valid pairs && unique keys) "engine environment invalid"
  pure [key ++ "=" ++ value | (key,value) <- pairs]

-- START PHASE ONLY. Called after native adoption and binding all origins, but
-- before Owner starts ANY workers. Source of env is reviewed Display, not page
-- data. Retains original deadline, exact held self ELF, fixed RPC/lifeline raw
-- descriptors and existing EngineCustody sole reaper. Returning EngineProcess
-- means OWNED/UNREADY, not ready/provider/native acceptance. The transport
-- MUST perform its real authenticated handshake before using the engine.
--
-- This draft has NOT been compiled or executed. In particular, the exception
-- boundary from successful unshare/fork to publication, existing fd cleanup
-- semantics, trusted procfs, image provenance and post-fork RTS/finalizer
-- behavior require independent review. No default success replaces them.
startUnreadyEngine :: AdmissionDeadline -> Word64 -> [(String,String)] -> IO EngineProcess
startUnreadyEngine deadline session envPairs = mask $ \_ -> do
  requireForkOwnership
  require (session > 0) "engine session must be positive"
  env <- engineEnvironment envPairs
  requireProcfs
  uid <- toInteger <$> getEffectiveUserID
  gid <- toInteger <$> getEffectiveGroupID
  require (uid >= 0 && uid <= 4294967295 && gid >= 0 && gid <= 4294967295)
          "engine effective identity out of bounds"
  capMax <- readLastCapability
  remaining <- remainingMicros deadline
  when (remaining <= 500000) (ioError (userError "engine startup deadline"))
  prepared <- prepareEngineOwned deadline
  require (deadlineAbsoluteNs (preparedDeadline prepared) == deadlineAbsoluteNs deadline) "engine prepared deadline mismatch"
  -- Allocate ownership cells BEFORE fork. Direct child and pidfd are recorded
  -- while masked; the existing Custody remains the ONLY signalling/reaper path.
  lifeCell <- newIORef Nothing
  pidCell <- newIORef Nothing
  pidRecord <- newIORef (Nothing :: Maybe CInt)
  changedPidNamespace <- newIORef False
  releasedPrepared <- newIORef False
  transferredSocket <- newIORef Nothing
  gate <- newMVar ()
  let custody = Custody lifeCell pidCell
      releaseOnce = do
        previous <- atomicModifyIORef' releasedPrepared (\old -> (True,old))
        if previous then pure (Right ()) else releasePrepared prepared
      failOwned = do
        pidfd <- readIORef pidCell
        case pidfd of
          Nothing -> pure ()
          Just _ -> do
            -- Even on expiry stopCustody may return False; that is NOT clean.
            _ <- try (stopCustody (remainingMicros deadline) custody) :: IO (Either SomeException Bool)
            abandonCustody custody
        _ <- closeCell S.close transferredSocket
        _ <- releaseOnce
        changed <- readIORef changedPidNamespace
        -- Once CLONE_NEWPID has succeeded, the owner must terminate on any
        -- startup failure; it cannot restore pid_for_children. If no pidfd was
        -- acquired, this exit does NOT prove child reap/descendant cleanup.
        if changed then exitImmediately (ExitFailure 119) else pure ()
      runFork = do
        imageNumber <- getSlot (pendingSlots prepared) 0
        rpcNumber <- getSlot (pendingSlots prepared) 1
        lifeNumber <- getSlot (pendingSlots prepared) 2
        let argv = ["/proc/self/exe", "--engine-only", show rpcNumber, show lifeNumber,
                    deadlineAbsoluteNs deadline, show session, show uid, show gid]
        withCString "" $ \empty -> withCString "/" $ \root ->
         withCString "/proc" $ \proc -> withCString "proc" $ \procTypeName ->
          withMany withCString argv $ \argvStrings -> withArray0 nullPtr argvStrings $ \argvPtr ->
           withMany withCString env $ \envStrings -> withArray0 nullPtr envStrings $ \envPtr ->
            allocaBytes #{size struct pollfd} $ \pollStorage ->
             allocaBytes #{size struct __user_cap_header_struct} $ \header ->
              allocaBytes (2 * #{size struct __user_cap_data_struct}) $ \caps -> do
               requireForkOwnership
               currentUid <- toInteger <$> getEffectiveUserID
               currentGid <- toInteger <$> getEffectiveGroupID
               require (currentUid == uid && currentGid == gid) "engine identity changed"
               now <- remainingMicros deadline
               when (now <= 500000) (ioError (userError "engine fork deadline"))
               _ <- throwErrnoIfMinus1 "engine unshare PID" (c_unshare #{const CLONE_NEWPID})
               writeIORef changedPidNamespace True
               let inputs = ChildInputs imageNumber rpcNumber lifeNumber empty root proc procTypeName argvPtr envPtr pollStorage header caps capMax
               pid <- forkProcess (childSetupExec inputs)
               writeIORef pidRecord (Just (fromIntegral pid))
               requireForkOwnership
               pidfd <- openPidfd (fromIntegral pid)
               writeIORef pidCell (Just pidfd)
               verified <- verifyChild pidfd
               unless verified (ioError (userError "engine child ownership uncertain"))
               originalWriter <- withdraw (preparedLifeWrite prepared)
               case originalWriter of
                 Nothing -> ioError (userError "engine lifeline ownership missing")
                 Just (Fd fd) -> writeIORef lifeCell (Just fd)
               ownedSocket <- withdraw (brokerSocket prepared)
               case ownedSocket of
                 Nothing -> ioError (userError "engine broker socket ownership missing")
                 Just socket -> writeIORef transferredSocket (Just socket)
               closed <- releaseOnce
               either throwIO pure closed
               still <- remainingMicros deadline
               when (still <= 0) (ioError (userError "engine fork exceeded deadline"))
               pure (EngineProcess custody transferredSocket (fromIntegral pid) (heldImageFacts prepared) (uid,gid) deadline gate)
  runFork `onException` failOwned

-- Integration remains incomplete: validate trusted procfs AND selected-held
-- image against the backend; pin exact source/build; implement phase-safe raw
-- descriptor publication and replacement for `exitImmediately` where a full
-- observed cleanup is possible; fix source-level sync-exception/close ambiguity;
-- authenticate every RPC fragment using kernel credentials bound to pid/birth;
-- post-exec lifeline/capset/proc and PID1 readiness before any GTK/message;
-- prove no stale fd finalizers or unwanted descriptor mutation; test actual
-- copy/exec and one-reaper behavior. Never treat the returned UNREADY handle as
-- a successful engine, provider, ARC024/DEL014, native or release verdict.
