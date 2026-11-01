{-# LANGUAGE ForeignFunctionInterface #-}
{-# LANGUAGE OverloadedStrings #-}
-- Enter before creating threads, listeners or the renderer. Kernel refusal is
-- fatal: this executable never falls back to the authority's host network.
module Warlock.Ui.PrivateNetwork (PeerNetwork, withPeerNetwork, enterPrivateNetwork, verifyPrivateNetwork) where

#define _GNU_SOURCE
#include <sched.h>
#include <sys/socket.h>
#include <sys/ioctl.h>
#include <sys/vfs.h>
#include <linux/magic.h>
#include <net/if.h>
#include <fcntl.h>
#include <unistd.h>
#include <sys/syscall.h>
#include <linux/nsfs.h>
#include <poll.h>

import Control.Exception (IOException, bracket, bracketOnError, bracket_, finally, mask, mask_, onException, try)
import Data.IORef (IORef, atomicModifyIORef', newIORef, readIORef)
import Control.Monad (unless)
import Data.Bits ((.|.), (.&.))
import Data.Int (Int64)
import qualified Data.ByteString as B
import qualified Data.ByteString.Char8 as C
import Foreign (Ptr, allocaBytes, peekByteOff, pokeByteOff, copyBytes, fillBytes, castPtr, nullPtr)
import Foreign.C
import System.IO (IOMode(ReadMode), withBinaryFile)
import System.Posix.Files (deviceID, fileID, getFileStatus, getFdStatus)
import System.Posix.Types (Fd(..))
import qualified Network.Socket as S
import System.Posix.Process (getProcessID, getParentProcessID)
import System.Posix.User (getRealUserID, getEffectiveUserID, getRealGroupID, getEffectiveGroupID)
import System.Directory (listDirectory)

foreign import ccall unsafe "unshare" c_unshare :: CInt -> IO CInt
foreign import ccall unsafe "socket" c_socket :: CInt -> CInt -> CInt -> IO CInt
foreign import ccall unsafe "ioctl" c_ioctl :: CInt -> CULong -> Ptr () -> IO CInt
foreign import ccall unsafe "open" c_open :: CString -> CInt -> IO CInt
foreign import ccall unsafe "openat" c_openat :: CInt -> CString -> CInt -> IO CInt
foreign import ccall unsafe "write" c_write :: CInt -> Ptr CChar -> CSize -> IO #{type ssize_t}
foreign import ccall unsafe "close" c_close :: CInt -> IO CInt
foreign import ccall unsafe "fstatfs" c_fstatfs :: CInt -> Ptr () -> IO CInt
foreign import ccall unsafe "fcntl" c_fcntl :: CInt -> CInt -> CInt -> IO CInt
foreign import ccall unsafe "syscall" c_syscall :: CLong -> CInt -> CUInt -> IO CLong
foreign import ccall unsafe "poll" c_poll :: Ptr () -> CULong -> CInt -> IO CInt
foreign import ccall unsafe "getsockopt" c_getsockopt :: CInt -> CInt -> CInt -> Ptr () -> Ptr CUInt -> IO CInt
foreign import ccall unsafe "recv" c_recv :: CInt -> Ptr () -> CSize -> CInt -> IO #{type ssize_t}


require :: Bool -> String -> IO ()
require good reason = unless good (ioError (userError reason))

close :: CInt -> IO ()
close fd = do
 _ <- throwErrnoIfMinus1 "private network close" (c_close fd)
 pure ()

withProc :: (CInt -> IO a) -> IO a
withProc action = bracket acquire close $ \fd -> do
 allocaBytes #{size struct statfs} $ \buffer -> do
  _ <- throwErrnoIfMinus1Retry "private network procfs" (c_fstatfs fd buffer)
  magic <- peekByteOff buffer #{offset struct statfs, f_type} :: IO CLong
  require (magic == fromIntegral (#{const PROC_SUPER_MAGIC} :: Integer)) "private network needs actual procfs"
 action fd
 where
  acquire = withCString "/proc" $ \path -> throwErrnoIfMinus1Retry "open procfs"
    (c_open path (#{const O_RDONLY} .|. #{const O_DIRECTORY} .|. #{const O_NOFOLLOW} .|. #{const O_CLOEXEC}))

writeMap :: CInt -> String -> B.ByteString -> IO ()
writeMap proc name bytes = withCString name $ \path ->
 bracket (throwErrnoIfMinus1Retry "open namespace map" (c_openat proc path (#{const O_WRONLY} .|. #{const O_NOFOLLOW} .|. #{const O_CLOEXEC}))) close $ \fd ->
  B.useAsCStringLen bytes $ \(pointer,count) -> do
   written <- throwErrnoIfMinus1Retry "write namespace map" (c_write fd pointer (fromIntegral count))
   require (written == fromIntegral count) "partial namespace map write"

withLoopback :: (CInt -> Ptr () -> CShort -> IO a) -> IO a
withLoopback action = bracket acquire close $ \fd -> allocaBytes #{size struct ifreq} $ \request -> do
 fillBytes request 0 #{size struct ifreq}
 withCString "lo" $ \name -> copyBytes request (castPtr name) 3
 _ <- throwErrnoIfMinus1Retry "get loopback flags" (c_ioctl fd #{const SIOCGIFFLAGS} request)
 flags <- peekByteOff request #{offset struct ifreq, ifr_flags} :: IO CShort
 require (flags .&. #{const IFF_LOOPBACK} /= 0) "not a loopback interface"
 action fd request flags
 where
  acquire = throwErrnoIfMinus1Retry "private network socket"
    (c_socket #{const AF_INET} (#{const SOCK_DGRAM} .|. #{const SOCK_CLOEXEC}) 0)

namespaceIdentity :: String -> IO (Integer,Integer)
namespaceIdentity name = do
 status <- getFileStatus ("/proc/" ++ name ++ "/ns/net")
 pure (toInteger (deviceID status),toInteger (fileID status))

-- A single mapping for the caller's own real/effective UID and GID. This uses
-- no privileged mapping helper, supplementary identity or cross-user grant.
-- Compile without -threaded and bake -with-rtsopts=-V0: this pinned RTS otherwise
-- creates a ticker OS thread, including after forkProcess. Inspect actual tasks
-- rather than treating the Cabal stanza as proof. Original deadlines are
-- monotonic observations and do not depend on the RTS tick.
enterPrivateNetwork :: IO ()
enterPrivateNetwork = withProc $ \proc -> do
 tasks <- listDirectory "/proc/self/task"
 require (length tasks == 1) "private UI namespace needs one actual OS thread"
 uid <- getRealUserID
 effectiveUid <- getEffectiveUserID
 gid <- getRealGroupID
 effectiveGid <- getEffectiveGroupID
 require (uid /= 0 && uid == effectiveUid && gid == effectiveGid) "private UI needs its ordinary owning identity"
 before <- namespaceIdentity "self"
 _ <- throwErrnoIfMinus1 "create private UI namespaces" (c_unshare (#{const CLONE_NEWUSER} .|. #{const CLONE_NEWNET}))
 writeMap proc "self/setgroups" "deny\n"
 writeMap proc "self/uid_map" (C.pack (show uid ++ " " ++ show uid ++ " 1\n"))
 writeMap proc "self/gid_map" (C.pack (show gid ++ " " ++ show gid ++ " 1\n"))
 mappedUid <- getRealUserID
 mappedGid <- getRealGroupID
 require (mappedUid == uid && mappedGid == gid) "private UI identity changed"
 after <- namespaceIdentity "self"
 require (after /= before) "network namespace did not change"
 withLoopback $ \fd request flags -> do
  pokeByteOff request #{offset struct ifreq, ifr_flags} (flags .|. #{const IFF_UP})
  _ <- throwErrnoIfMinus1Retry "enable private loopback" (c_ioctl fd #{const SIOCSIFFLAGS} request)
  pure ()

-- Opaque witness is created only from fd0, before entering the user namespace.
-- Both retained handles are CLOEXEC; the pidfd pins the process incarnation.
-- The backend must remain in its captured network namespace while alive; the
-- pidfd pins a process, not its later namespace membership.
-- A successful callback is returned only after both close operations succeed.
data LeaseState = Live Int | Retired Int | Closed
-- Only the process owning the witness may acquire a lease. Retired handles
-- cannot acquire new leases; the last outstanding verifier owns deferred close.
data PeerNetwork = PeerNetwork CInt CInt Identity Identity Integer Integer Int Integer Integer Integer (IORef LeaseState)

closePair :: CInt -> CInt -> IO ()
closePair pidfd netfd = close netfd `finally` close pidfd

acquireLease :: IORef LeaseState -> IO ()
acquireLease cell = do
 ok <- atomicModifyIORef' cell $ \state -> case state of
  Live count | count < 1024 -> (Live (count + 1), True)
  _ -> (state, False)
 require ok "network witness retired or verifier capacity exhausted"

releaseLease :: CInt -> CInt -> IORef LeaseState -> IO ()
releaseLease pidfd netfd cell = mask_ $ do
 disposition <- atomicModifyIORef' cell $ \state -> case state of
  Live count | count > 0 -> (Live (count - 1), 0 :: Int)
  Retired 1 -> (Closed, 1)
  Retired count | count > 1 -> (Retired (count - 1), 0)
  _ -> (state, 2)
 case disposition of
  0 -> pure ()
  1 -> closePair pidfd netfd
  _ -> ioError (userError "network witness lease accounting failure")

retirePeer :: PeerNetwork -> IO ()
retirePeer (PeerNetwork pidfd netfd _ _ _ _ _ _ _ _ cell) = mask_ $ do
 disposition <- atomicModifyIORef' cell $ \state -> case state of
  Live 0 -> (Closed, 0 :: Int)
  Live count -> (Retired count, 1)
  _ -> (state, 2)
 case disposition of
  0 -> closePair pidfd netfd
  1 -> ioError (userError "network witness retirement pending active verifier")
  _ -> ioError (userError "network witness already retired")

type Identity = (Integer,Integer)
fdIdentity :: CInt -> IO Identity
fdIdentity fd = do
 st <- getFdStatus (Fd fd)
 pure (toInteger (deviceID st), toInteger (fileID st))

-- An owned duplicate prevents Network.Socket from taking ownership of fd0.
withSocketFacts :: (Identity -> Int -> Integer -> Integer -> IO a) -> IO a
withSocketFacts action = mask $ \restore -> do
 (ident,pid,uid,gid) <- bracket acquire S.close $ \socket -> do
  peer <- S.getPeerName socket
  require (case peer of S.SockAddrUnix _ -> True; _ -> False) "native endpoint is not Unix"
  creds <- S.getPeerCredential socket
  (pid,uid,gid) <- case creds of
   (Just p,Just u,Just g) | p > 0 -> pure (fromIntegral p,toInteger u,toInteger g)
   _ -> ioError (userError "native peer credentials unavailable")
  ident <- S.withFdSocket socket $ \fd -> do
   requireOpenStream fd
   fdIdentity fd
  pure (ident,pid,uid,gid)
 restore (action ident pid uid gid)
 where
  acquire = do
   fd <- throwErrnoIfMinus1 "duplicate native peer" (c_fcntl 0 #{const F_DUPFD_CLOEXEC} 3)
   S.mkSocket fd `onException` close fd

-- Inspect without consuming framed protocol data. Readable may be real data or
-- EOF; HUP/error always refuses, even if buffered data remains.
requireOpenStream :: CInt -> IO ()
requireOpenStream fd = do
 allocaBytes #{size int} $ \value -> allocaBytes #{size socklen_t} $ \sizePtr -> do
  pokeByteOff sizePtr 0 (#{size int} :: CUInt)
  _ <- throwErrnoIfMinus1Retry "native socket type" (c_getsockopt fd #{const SOL_SOCKET} #{const SO_TYPE} value sizePtr)
  kind <- peekByteOff value 0 :: IO CInt
  require (kind == #{const SOCK_STREAM}) "native peer is not a stream"
 allocaBytes #{size struct pollfd} $ \p -> do
  fillBytes p 0 #{size struct pollfd}
  pokeByteOff p #{offset struct pollfd, fd} fd
  pokeByteOff p #{offset struct pollfd, events} ((#{const POLLIN} .|. #{const POLLRDHUP}) :: CShort)
  _ <- throwErrnoIfMinus1Retry "poll native peer" (c_poll p 1 0)
  flags <- peekByteOff p #{offset struct pollfd, revents} :: IO CShort
  require (flags .&. (#{const POLLERR} .|. #{const POLLHUP} .|. #{const POLLNVAL} .|. #{const POLLRDHUP}) == 0) "native peer terminal"
  if flags .&. #{const POLLIN} == 0 then pure () else allocaBytes 1 $ \byte -> do
   count <- throwErrnoIfMinus1 "peek native peer" (c_recv fd byte 1 (#{const MSG_PEEK} .|. #{const MSG_DONTWAIT}))
   require (count > 0) "native peer EOF"

pidAlive :: CInt -> IO Bool
pidAlive fd = allocaBytes #{size struct pollfd} $ \p -> do
 fillBytes p 0 #{size struct pollfd}
 pokeByteOff p #{offset struct pollfd, fd} fd
 pokeByteOff p #{offset struct pollfd, events} (#{const POLLIN} :: CShort)
 result <- throwErrnoIfMinus1Retry "poll peer pidfd" (c_poll p 1 0)
 pure (result == 0)

validateNetFd :: CInt -> IO ()
validateNetFd fd = do
 allocaBytes #{size struct statfs} $ \buffer -> do
  _ <- throwErrnoIfMinus1Retry "peer namespace fs" (c_fstatfs fd buffer)
  magic <- peekByteOff buffer #{offset struct statfs, f_type} :: IO CLong
  require (magic == fromIntegral (#{const NSFS_MAGIC} :: Integer)) "peer namespace is not nsfs"
 kind <- throwErrnoIfMinus1 "peer namespace type" (c_ioctl fd #{const NS_GET_NSTYPE} nullPtr)
 require (kind == #{const CLONE_NEWNET}) "peer namespace is not network"

openPeerNamespace :: CInt -> Int -> IO CInt
openPeerNamespace proc pid = withCString (show pid ++ "/ns/net") $ \path -> do
 fd <- throwErrnoIfMinus1Retry "open peer network namespace" (c_openat proc path (#{const O_RDONLY} .|. #{const O_CLOEXEC}))
 (validateNetFd fd >> pure fd) `onException` close fd

withPeerNetwork :: (PeerNetwork -> IO a) -> IO a
withPeerNetwork action = mask $ \restore -> withSocketFacts $ \(dev,ino) pid uid gid -> do
 owner <- getProcessID
 parent <- getParentProcessID
 ownUid <- getRealUserID
 ownGid <- getRealGroupID
 effectiveUid <- getEffectiveUserID
 effectiveGid <- getEffectiveGroupID
 require (ownUid /= 0 && ownUid == effectiveUid && ownGid == effectiveGid) "private UI needs ordinary owning identity"
 require (uid == toInteger ownUid && gid == toInteger ownGid) "native peer identity differs from UI owner"
 require (pid == fromIntegral parent && pid /= fromIntegral owner) "native peer is not parent"
 let acquirePid = do
      raw <- throwErrnoIfMinus1 "pidfd_open" (c_syscall #{const SYS_pidfd_open} (fromIntegral pid) 0)
      pure (fromIntegral raw)
 withProc $ \proc -> do
  let acquireWitness = bracketOnError acquirePid close $ \pidfd -> do
       alive <- pidAlive pidfd
       require alive "native peer exited before namespace observation"
       bracketOnError (openPeerNamespace proc pid) close $ \netfd -> do
        aliveAfter <- pidAlive pidfd
        parentAfter <- getParentProcessID
        require (aliveAfter && fromIntegral parentAfter == pid) "native peer exited or changed during namespace observation"
        withSocketFacts $ \ident p u g -> require (ident == (dev,ino) && p == pid && u == uid && g == gid) "native peer changed during witness acquisition"
        pidIdentity <- fdIdentity pidfd
        netIdentity <- fdIdentity netfd
        cell <- newIORef (Live 0)
        pure (PeerNetwork pidfd netfd pidIdentity netIdentity dev ino pid uid gid (toInteger owner) cell)
  bracket acquireWitness retirePeer (restore . action)

-- The witness is checked against current fd0 and its kernel credentials, never
-- an HTTP/config PID. Failed/uncertain proc, pidfd, socket or close refuses.
verifyPrivateNetwork :: PeerNetwork -> IO Bool
verifyPrivateNetwork (PeerNetwork pidfd netfd pidIdentity netIdentity dev ino pid uid gid owner cell) = do
 result <- try $ do
  self <- getProcessID
  require (toInteger self == owner) "network witness used by another process"
  bracket_ (acquireLease cell) (releaseLease pidfd netfd cell) $ do
   currentPidIdentity <- fdIdentity pidfd
   currentNetIdentity <- fdIdentity netfd
   require (currentPidIdentity == pidIdentity && currentNetIdentity == netIdentity) "network witness descriptors replaced"
   validateNetFd netfd
   alive <- pidAlive pidfd
   require alive "network witness peer exited"
   withSocketFacts $ \ident p u g -> require (ident == (dev,ino) && p == pid && u == uid && g == gid) "native socket no longer matches witness"
   own <- namespaceIdentity "self"
   peer <- fdIdentity netfd
   require (own /= peer) "UI is on the backend network"
   bytes <- withBinaryFile "/proc/net/dev" ReadMode (\handle -> B.hGet handle 16385)
   require (B.length bytes <= 16384) "network interface inventory exceeds bound"
   let interfaces = [C.filter (/= ' ') (fst (C.break (== ':') line)) | line <- drop 2 (C.lines bytes), not (B.null line)]
   require (interfaces == [C.pack "lo"]) "private UI network is not loopback-only"
   withLoopback $ \_ _ flags -> require (flags .&. #{const IFF_UP} /= 0) "private loopback is down"
   aliveAfter <- pidAlive pidfd
   require aliveAfter "network witness peer exited during verification"
   current <- readIORef cell
   require (case current of Live _ -> True; _ -> False) "network witness retired during verification"
   pure True
 pure (either (const False) id (result :: Either IOException Bool))
