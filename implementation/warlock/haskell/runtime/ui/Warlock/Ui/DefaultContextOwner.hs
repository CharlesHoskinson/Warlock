{-# LANGUAGE ForeignFunctionInterface #-}
-- Physical main-thread/default-context custody. Nonthreaded mode is not GHC-bound.
module Warlock.Ui.DefaultContextOwner
  (PhysicalDefaultContextOwner, withPhysicalDefaultContextOwner,
   requirePhysicalDefaultContextOwner, ownerRemainingMicros) where

import Control.Concurrent (isCurrentThreadBound, rtsSupportsBoundThreads)
import Control.Exception (finally, mask, mask_)
import Control.Monad (unless)
import Data.IORef (IORef, atomicModifyIORef', newIORef)
import Foreign.C.Types (CInt(..))
import Foreign.Ptr (Ptr, nullPtr)
import System.Posix.Files (deviceID, fileID, getFileStatus)
import Warlock.Ui.ThreadNamespace (requireThreadCompatibleNamespace)

data Context
data PhysicalMode = NonthreadedMain | ThreadedBoundMain
data PhysicalDefaultContextOwner = Owner
  !PhysicalMode !(Ptr Context) !CInt !CInt !(Integer, Integer) !(IORef Bool) (IO Int)

foreign import ccall unsafe "gettid" kernelTid :: IO CInt
foreign import ccall unsafe "getpid" kernelPid :: IO CInt
foreign import ccall unsafe "g_main_context_default" defaultContext :: IO (Ptr Context)
foreign import ccall unsafe "g_main_context_get_thread_default" threadDefault :: IO (Ptr Context)
foreign import ccall unsafe "g_main_context_acquire" acquireContext :: Ptr Context -> IO CInt
foreign import ccall unsafe "g_main_context_is_owner" isOwner :: Ptr Context -> IO CInt
foreign import ccall unsafe "g_main_context_release" releaseContext :: Ptr Context -> IO ()

require :: Bool -> String -> IO ()
require ok reason = unless ok (ioError (userError reason))

pidNamespace :: IO (Integer, Integer)
pidNamespace = do
 status <- getFileStatus "/proc/thread-self/ns/pid"
 pure (toInteger (deviceID status), toInteger (fileID status))

runtimeMode :: IO PhysicalMode
runtimeMode = if rtsSupportsBoundThreads then do
 bound <- isCurrentThreadBound
 require bound "threaded context caller is not GHC bound"
 pure ThreadedBoundMain
 else pure NonthreadedMain

requireMode :: PhysicalMode -> IO ()
requireMode NonthreadedMain = require (not rtsSupportsBoundThreads) "context RTS mode changed"
requireMode ThreadedBoundMain = do
 require rtsSupportsBoundThreads "context RTS mode changed"
 bound <- isCurrentThreadBound
 require bound "threaded context caller is no longer GHC bound"

-- This check does not enter a context or manufacture a physical-thread proof.
-- It never accepts a caller-supplied Bool, ThreadId, mode or native pointer.
requirePhysical :: PhysicalDefaultContextOwner -> IO ()
requirePhysical (Owner mode context tid pid namespace _ _) = do
 requireMode mode
 actualTid <- kernelTid
 actualPid <- kernelPid
 require (actualTid > 0 && actualTid == tid && actualPid == pid && actualTid == actualPid)
   "physical initial kernel thread changed"
 actualNamespace <- pidNamespace
 require (actualNamespace == namespace) "context PID namespace changed"
 actualDefault <- defaultContext
 selected <- threadDefault
 require (actualDefault == context && (selected == nullPtr || selected == context))
   "default or thread-default context changed"
 owned <- isOwner context
 require (owned /= 0) "default context is not owned by this physical thread"

withPhysicalDefaultContextOwner :: IO Int -> (PhysicalDefaultContextOwner -> IO a) -> IO a
withPhysicalDefaultContextOwner remaining action = mask $ \restore -> do
 requireThreadCompatibleNamespace
 mode <- runtimeMode
 tid <- kernelTid
 pid <- kernelPid
 require (tid > 0 && tid == pid) "context requires the initial kernel thread"
 namespace <- pidNamespace
 context <- defaultContext
 selected <- threadDefault
 require (context /= nullPtr && (selected == nullPtr || selected == context))
   "foreign or missing default context"
 left <- remaining
 require (left > 0) "original context deadline expired"
 -- Allocate the lifetime cell before acquiring native ownership.
 active <- newIORef False
 owned <- acquireContext context
 require (owned /= 0) "default context is busy"
 let owner = Owner mode context tid pid namespace active remaining
     release = mask_ $ do
      -- Invalidate first, even when identity uncertainty prevents safe release.
      wasLive <- atomicModifyIORef' active (\old -> (False, old))
      if wasLive then requirePhysical owner >> releaseContext context else pure ()
 atomicModifyIORef' active (\_ -> (True, ()))
 (requirePhysicalDefaultContextOwner owner >> restore (action owner)) `finally` release

ownerRemainingMicros :: PhysicalDefaultContextOwner -> IO Int
ownerRemainingMicros owner@(Owner _ _ _ _ _ active remaining) = do
 live <- atomicModifyIORef' active (\value -> (value, value))
 require live "physical context lease retired"
 requirePhysical owner
 left <- remaining
 require (left > 0) "original context deadline expired"
 requirePhysical owner
 stillLive <- atomicModifyIORef' active (\value -> (value, value))
 require stillLive "physical context lease retired during use"
 pure left

requirePhysicalDefaultContextOwner :: PhysicalDefaultContextOwner -> IO ()
requirePhysicalDefaultContextOwner owner = ownerRemainingMicros owner >> pure ()
