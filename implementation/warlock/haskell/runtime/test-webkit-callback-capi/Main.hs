{-# LANGUAGE CApiFFI #-}
{-# LANGUAGE ForeignFunctionInterface #-}
module Main (main, connectSignal, disconnectSignal, wrapNotify, wrapCallback, wrapMarshal, wrapDecision, wrapReady, wrapLoad, wrapLoadFailed, wrapDownload) where

import Foreign.C.String (CString)
import Foreign.C.Types (CInt(..), CUInt(..), CULong(..))
import Foreign.Ptr (FunPtr, Ptr)

data GClosure
data GValue

data Object

type Decision = Ptr Object -> Ptr Object -> CInt -> Ptr () -> IO CInt
type Ready = Ptr Object -> Ptr Object -> Ptr () -> IO ()
type Load = Ptr Object -> CInt -> Ptr () -> IO ()
type LoadFailed = Ptr Object -> CInt -> CString -> Ptr Object -> Ptr () -> IO CInt
type Download = Ptr Object -> Ptr Object -> Ptr () -> IO ()

type Notify = Ptr () -> Ptr GClosure -> IO ()
type Callback = IO ()
type Marshal = Ptr GClosure -> Ptr GValue -> CUInt -> Ptr GValue -> Ptr () -> Ptr () -> IO ()

foreign import capi safe "glib-object.h g_signal_connect_data"
 connectSignal :: Ptr () -> CString -> FunPtr Callback -> Ptr () -> FunPtr Notify -> CInt -> IO CULong
foreign import capi safe "glib-object.h g_signal_handler_disconnect"
 disconnectSignal :: Ptr () -> CULong -> IO ()
foreign import ccall "wrapper"
 wrapNotify :: Notify -> IO (FunPtr Notify)
foreign import ccall "wrapper"
 wrapCallback :: Callback -> IO (FunPtr Callback)
foreign import ccall "wrapper"
 wrapMarshal :: Marshal -> IO (FunPtr Marshal)

foreign import ccall "wrapper"
 wrapDecision :: Decision -> IO (FunPtr Decision)
foreign import ccall "wrapper"
 wrapReady :: Ready -> IO (FunPtr Ready)
foreign import ccall "wrapper"
 wrapLoad :: Load -> IO (FunPtr Load)
foreign import ccall "wrapper"
 wrapLoadFailed :: LoadFailed -> IO (FunPtr LoadFailed)
foreign import ccall "wrapper"
 wrapDownload :: Download -> IO (FunPtr Download)

-- The compile-only target does not enter GObject or create callbacks.
main :: IO ()
main = pure ()
