{-# LANGUAGE CApiFFI #-}
{-# LANGUAGE ForeignFunctionInterface #-}
{-# LANGUAGE ScopedTypeVariables #-}
module Main (main, connectSignal, disconnectSignal, wrapNotify, wrapCallback, wrapMarshal, wrapDecision, wrapReady, wrapLoad, wrapLoadFailed, wrapDownload, invokeNotify, invokeCallback, invokeMarshal) where

import Control.Concurrent.MVar (MVar, newEmptyMVar, tryPutMVar, tryReadMVar)
import Control.Exception (AsyncException(ThreadKilled), Exception, SomeException, bracket, catch, fromException, mask, mask_, throwIO, toException, try, uninterruptibleMask_)
import Control.Monad (unless, void)
import Data.IORef (atomicModifyIORef', modifyIORef', newIORef, readIORef)
import Foreign.C.String (CString)
import Foreign.C.Types (CInt(..), CUInt(..), CULong(..))
import Foreign.Marshal.Alloc (allocaBytes)
import Foreign.Ptr (FunPtr, Ptr, castPtr, freeHaskellFunPtr, nullFunPtr, nullPtr)

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

foreign import ccall safe "warlock_fixture_notify"
 invokeNotify :: FunPtr Notify -> Ptr () -> Ptr GClosure -> IO ()
foreign import ccall safe "warlock_fixture_callback"
 invokeCallback :: FunPtr Callback -> IO ()
foreign import ccall safe "warlock_fixture_marshal"
 invokeMarshal :: FunPtr Marshal -> Ptr GClosure -> Ptr GValue -> CUInt -> Ptr GValue -> Ptr () -> Ptr () -> IO ()

-- The test owns every generated callback until the synchronous C call returns.
-- Exceptions are contained at the foreign boundary and recorded as literals.
originalControls :: IO ()
originalControls = mask_ $ do
 faults <- newEmptyMVar
 events <- newIORef ([] :: [String])
 let record event = modifyIORef' events (++ [event])
     contain action = boundary faults (\(_ :: SomeException) -> record "caught") action
     notify dat closure = contain $ do
      record (if dat == nullPtr && closure == nullPtr then "notify-null" else "notify-wrong")
      throwIO (userError "fixture exception")
     generic = contain (record "callback")
     marshal closure result count values hint dat = contain $
      record (if closure == nullPtr && result == nullPtr && count == 7 && values == nullPtr && hint == nullPtr && dat == nullPtr then "marshal-7-null" else "marshal-wrong")
 bracket (wrapNotify notify) freeHaskellFunPtr $ \pointer -> invokeNotify pointer nullPtr nullPtr
 bracket (wrapCallback generic) freeHaskellFunPtr invokeCallback
 bracket (wrapMarshal marshal) freeHaskellFunPtr $ \pointer -> invokeMarshal pointer nullPtr nullPtr 7 nullPtr nullPtr nullPtr
 observed <- readIORef events
 unless (observed == ["notify-null", "caught", "callback", "marshal-7-null"]) (ioError (userError "callback literal mismatch"))

-- These imports use the exact public I1 shim. Only valid GValues are read.
foreign import ccall safe "warlock_fixture_valid_marshal"
 invokeValidMarshal :: FunPtr Marshal -> IO CInt
foreign import capi unsafe "glib-object.h g_value_get_int"
 valueInt :: Ptr GValue -> IO CInt

data FixtureFault = BodyFailure | RecorderFailure deriving (Eq, Show)
instance Exception FixtureFault

-- The fallback has no user callback and never waits for a full fault cell.
-- The recorder is inside the outer catch, including its exception handler.
boundary :: MVar SomeException -> (SomeException -> IO ()) -> IO () -> IO ()
boundary faults recorder action = mask $ \restore ->
 (restore action `catch` (\(failure :: SomeException) -> do
   remember failure
   restore (recorder failure))) `catch` remember
 where
  remember failure = uninterruptibleMask_ (void (tryPutMVar faults failure))

check :: String -> Bool -> IO ()
check label condition = unless condition (ioError (userError label))

-- This shim is synchronous and does not retain the callback. A failed call
-- never reaches freeHaskellFunPtr: an uncertain return retains the pointer.
withReturned :: IO (FunPtr a) -> (FunPtr a -> IO b) -> IO (b, [String])
withReturned acquire call = mask_ $ do
 retirement <- newIORef ([] :: [String])
 pointer <- acquire
 result <- try (call pointer)
 case result of
  Left (failure :: SomeException) -> throwIO failure
  Right value -> do
   modifyIORef' retirement (++ ["ffi-returned"])
   freeHaskellFunPtr pointer
   modifyIORef' retirement (++ ["callback-freed"])
   trace <- readIORef retirement
   pure (value, trace)

newControls :: IO ()
newControls = do
 faults <- newEmptyMVar
 let noRecorder _ = pure ()
     contain = boundary faults noRecorder
 notifyCalls <- newIORef (0 :: Int)
 positions <- newIORef False
 allocaBytes 1 $ \first -> allocaBytes 1 $ \second -> do
  check "notify-distinct-storage" (first /= second && first /= nullPtr && second /= nullPtr)
  let notify dat closure = contain $ do
       atomicModifyIORef' notifyCalls (\n -> (n + 1, ()))
       atomicModifyIORef' positions (\_ -> (dat == first && closure == castPtr second, ()))
  (_, retired) <- withReturned (wrapNotify notify) (\pointer -> invokeNotify pointer first (castPtr second))
  check "notify-return-before-retirement" (retired == ["ffi-returned", "callback-freed"])
 countNotify <- readIORef notifyCalls
 correctPositions <- readIORef positions
 check "notify-distinct-positions" (countNotify == 1 && correctPositions)
 calls <- newIORef (0 :: Int)
 observed <- newIORef ([] :: [(Bool, Bool, CUInt, Bool, Bool, Bool, CInt)])
 let marshal closure result count values hint dat = contain $ do
      atomicModifyIORef' calls (\n -> (n + 1, ()))
      -- This pointer is borrowed from the exact synchronous I1 allocation.
      value <- if values /= nullPtr && count == 1 then valueInt values else pure (-1)
      atomicModifyIORef' observed (\rows -> (rows ++ [(closure /= nullPtr, result /= nullPtr, count, values /= nullPtr, hint == nullPtr, dat == nullPtr, value)], ()))
 (status, retired) <- withReturned (wrapMarshal marshal) invokeValidMarshal
 rows <- readIORef observed
 countBefore <- readIORef calls
 check "valid-marshal-literal" (status == 1 && countBefore == 1 && rows == [(True, True, 1, True, True, True, 42)])
 check "marshal-return-before-retirement" (retired == ["ffi-returned", "callback-freed"])
 nullStatus <- invokeValidMarshal nullFunPtr
 countAfter <- readIORef calls
 check "valid-marshal-null-callback-refusal" (nullStatus == 0 && countAfter == 1)
 unexpected <- tryReadMVar faults
 check "positive-callback-no-fault" (case unexpected of Nothing -> True; Just _ -> False)

faultControl :: String -> Bool -> (SomeException -> IO ()) -> IO ()
faultControl label prefill recorder = do
 faults <- newEmptyMVar
 attempts <- newIORef (0 :: Int)
 if prefill then void (tryPutMVar faults (toSome BodyFailure)) else pure ()
 let record failure = do
      atomicModifyIORef' attempts (\n -> (n + 1, ()))
      recorder failure
     action = if prefill then throwIO RecorderFailure else throwIO BodyFailure
     callback = boundary faults record action
 (_, retired) <- withReturned (wrapCallback callback) invokeCallback
 first <- tryReadMVar faults
 count <- readIORef attempts
 check (label ++ "-first-fault") (case first >>= fromException of Just BodyFailure -> True; _ -> False)
 check (label ++ "-recorder-once") (count == 1)
 check (label ++ "-return-before-retirement") (retired == ["ffi-returned", "callback-freed"])
 where
  toSome :: FixtureFault -> SomeException
  toSome = toException

main :: IO ()
main = do
 originalControls
 newControls
 faultControl "body-fault" False (\_ -> pure ())
 faultControl "recorder-fault" False (\_ -> throwIO RecorderFailure)
 -- Explicit typed exception injection, not a scheduling or OS-thread proof.
 faultControl "async-recorder-fault" False (\_ -> throwIO ThreadKilled)
 faultControl "full-fault-slot" True (\_ -> throwIO RecorderFailure)
 putStrLn "webkit-callback-capi-controls: complete"
