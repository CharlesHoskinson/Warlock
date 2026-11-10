{-# LANGUAGE ForeignFunctionInterface #-}
{-# LANGUAGE ScopedTypeVariables #-}
-- Production signals have no Haskell GClosureNotify entry. Their Haskell
-- wrappers and captured state stay pinned until the actual owner process dies.
module Warlock.Ui.ProcessSignalOwner
 (ProcessSignal, ProcessSignalDisconnect(..), connectProcessSignal,
  disconnectProcessSignal) where

import Control.Exception (SomeException, catch, mask_, throwIO)
import Control.Monad (unless, void)
import Data.IORef (IORef, atomicModifyIORef', newIORef)
import Foreign.C.String (CString, withCString)
import Foreign.C.Types (CInt(..), CULong(..))
import Foreign.Ptr (FunPtr, Ptr, castFunPtr, castPtr, nullFunPtr, nullPtr)
import Foreign.StablePtr (newStablePtr)
import Warlock.Ui.DefaultContextOwner
 (PhysicalDefaultContextOwner, requirePhysicalDefaultContextOwner)

type DestroyNotify = Ptr () -> Ptr () -> IO ()
foreign import ccall safe "g_signal_connect_data"
 signalConnect :: Ptr () -> CString -> FunPtr () -> Ptr () -> FunPtr DestroyNotify -> CInt -> IO CULong
foreign import ccall safe "g_signal_handler_disconnect"
 signalDisconnect :: Ptr () -> CULong -> IO ()

data Connection = Connecting | Connected CULong | Requested | Returned | Uncertain
-- The callback pointer is part of the pinned record even after disconnect.
-- The caller retains the object's owning reference; this is not an unref API.
data ProcessSignal = ProcessSignal PhysicalDefaultContextOwner (Ptr ()) (FunPtr ()) (IORef Connection)
data ProcessSignalDisconnect = DisconnectReturnedRetained | DisconnectNotRepeatedRetained
 deriving (Eq, Show)

connectProcessSignal :: PhysicalDefaultContextOwner -> Ptr a -> String -> FunPtr b -> IO ProcessSignal
connectProcessSignal owner object name callback = mask_ $ do
 requirePhysicalDefaultContextOwner owner
 unless (object /= nullPtr && callback /= nullFunPtr)
   (ioError (userError "process signal requires object and callback"))
 state <- newIORef Connecting
 let signal = ProcessSignal owner (castPtr object) (castFunPtr callback) state
 -- Deliberate process-lifetime root, allocated BEFORE possible native custody.
 -- There is no freeStablePtr/freeHaskellFunPtr or child self-retirement path.
 void (newStablePtr signal)
 (do
   ident <- withCString name $ \label ->
     signalConnect (castPtr object) label (castFunPtr callback) nullPtr nullFunPtr 0
   requirePhysicalDefaultContextOwner owner
   unless (ident /= 0) (ioError (userError "process signal connection uncertain"))
   atomicModifyIORef' state (\_ -> (Connected ident, ()))
   pure signal)
  `catch` (\(failure :: SomeException) -> do
    atomicModifyIORef' state (\_ -> (Uncertain, ()))
    throwIO failure)

disconnectProcessSignal :: ProcessSignal -> IO ProcessSignalDisconnect
disconnectProcessSignal (ProcessSignal owner object _callback state) = mask_ $ do
 requirePhysicalDefaultContextOwner owner
 selected <- atomicModifyIORef' state (\old -> case old of
   Connected ident -> (Requested, Just ident)
   _ -> (old, Nothing))
 case selected of
  Nothing -> pure DisconnectNotRepeatedRetained
  Just ident ->
   (do
     requirePhysicalDefaultContextOwner owner
     signalDisconnect object ident
     requirePhysicalDefaultContextOwner owner
     atomicModifyIORef' state (\_ -> (Returned, ()))
     pure DisconnectReturnedRetained)
    `catch` (\(failure :: SomeException) -> do
      atomicModifyIORef' state (\_ -> (Uncertain, ()))
      throwIO failure)
