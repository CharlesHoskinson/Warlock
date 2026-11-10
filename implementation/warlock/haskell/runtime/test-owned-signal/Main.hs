{-# LANGUAGE ForeignFunctionInterface #-}
module Main (main) where

import Control.Exception (AsyncException(ThreadKilled), SomeException, catch, mask_, throwIO, try)
import Control.Monad (unless)
import Control.Concurrent (MVar, forkIO, myThreadId, newEmptyMVar, putMVar, takeMVar, tryPutMVar, tryReadMVar)
import Data.IORef
import Foreign
import Foreign.C
import System.Environment (getArgs)
import System.Timeout (timeout)
import Warlock.Capture.Process.Bootstrap (AdmissionDeadline, deadlineFromAbsoluteNs, remainingMicros)
import Warlock.Ui.WebKit (SignalDisconnectObservation, connectOwnedSignal, connectOwnedSignalObserved, signalDisconnectReturned, signalRetirementConfirmed, withOwnedDefaultContext)

data Action

type Callback = Ptr Action -> Ptr () -> Ptr () -> IO ()
foreign import ccall "wrapper" wrapCallback :: Callback -> IO (FunPtr Callback)
foreign import ccall unsafe "g_simple_action_new" actionNew :: CString -> Ptr () -> IO (Ptr Action)
foreign import ccall safe "g_action_activate" activate :: Ptr Action -> Ptr () -> IO ()
foreign import ccall unsafe "g_object_unref" unref :: Ptr Action -> IO ()

check :: String -> Bool -> IO ()
check name result = unless result (ioError (userError name))

waitUntil :: AdmissionDeadline -> String -> IO a -> IO a
waitUntil deadline label action = do
  left <- remainingMicros deadline
  unless (left > 0) (ioError (userError (label ++ ": deadline expired; custody uncertain")) )
  result <- timeout left action
  maybe (ioError (userError (label ++ ": deadline expired; custody uncertain"))) pure result

-- Catch the entire foreign callback, including entry, deadline reads and exit
-- publication. The handler runs masked and tryPutMVar never waits on a full
-- slot. Keep the first failure; no exception string authorizes cleanup.
containCallback :: MVar SomeException -> IO () -> IO ()
containCallback faults action = mask_ action `catch` recordFault
  where
    recordFault problem = do
      _ <- tryPutMVar faults problem
      pure ()

publishOnce :: MVar a -> a -> IO ()
publishOnce cell value = do
  stored <- tryPutMVar cell value
  check "duplicate-callback-publication" stored

checkNoFault :: MVar SomeException -> String -> IO ()
checkNoFault faults label = do
  fault <- tryReadMVar faults
  check label (maybe True (const False) fault)

-- These inject exception values into the same containment function. They
-- establish no OS-thread identity or asynchronous-delivery/native claim.
containmentControls :: AdmissionDeadline -> IO ()
containmentControls deadline = do
  faults <- newEmptyMVar
  waitUntil deadline "fault-slot-first" $
    containCallback faults (ioError (userError "first callback fault"))
  first <- tryReadMVar faults
  check "whole-callback-fault-recorded" (maybe False (const True) first)
  waitUntil deadline "fault-slot-full" $
    containCallback faults (throwIO ThreadKilled)
  second <- tryReadMVar faults
  check "full-fault-slot-nonblocking-first-preserved" (fmap show second == fmap show first)
  asyncFault <- newEmptyMVar
  waitUntil deadline "async-exception-value" $
    containCallback asyncFault (throwIO ThreadKilled)
  recorded <- tryReadMVar asyncFault
  check "async-exception-value-contained" (maybe False (const True) recorded)
  publication <- newEmptyMVar
  putMVar publication ()
  publicationFault <- newEmptyMVar
  waitUntil deadline "exit-publication-fault" $
    containCallback publicationFault (publishOnce publication ())
  publicationRecorded <- tryReadMVar publicationFault
  check "exit-publication-fault-contained" (maybe False (const True) publicationRecorded)

main :: IO ()
main = do
  args <- getArgs
  deadline <- case args of
    [absolute] -> deadlineFromAbsoluteNs absolute >>= either (ioError . userError . show) pure
    _ -> ioError (userError "expected one original absolute monotonic deadline in nanoseconds")
  withOwnedDefaultContext (runFixture deadline)

runFixture :: AdmissionDeadline -> IO ()
runFixture deadline = do
  containmentControls deadline
  obj <- withCString "owned-fixture" $ \name -> actionNew name nullPtr
  check "object-created" (obj /= nullPtr)
  calls <- newIORef (0 :: Int)
  releases <- newIORef (0 :: Int)
  faults <- newEmptyMVar
  cb <- wrapCallback $ \_ _ _ -> containCallback faults $
    atomicModifyIORef' calls (\count -> (count + 1, ()))
  disconnect <- connectOwnedSignal obj "activate" (castFunPtr cb) $ do
    checkNoFault faults "normal-release-no-callback-fault"
    modifyIORef' releases (+ 1)
    freeHaskellFunPtr cb
  activate obj nullPtr
  checkNoFault faults "normal-callback-no-fault"
  readIORef calls >>= check "callback-once" . (== 1)
  disconnect
  readIORef releases >>= check "destroy-receipt-once" . (== 1)
  disconnect
  readIORef releases >>= check "repeat-no-second-release" . (== 1)
  activate obj nullPtr
  readIORef calls >>= check "no-callback-after-disconnect" . (== 1)
  unref obj
  obj3 <- withCString "inflight-fixture" $ \name -> actionNew name nullPtr
  check "inflight-object-created" (obj3 /= nullPtr)
  entered <- newEmptyMVar
  gate <- newEmptyMVar
  callbackExit <- newEmptyMVar
  destroyed <- newEmptyMVar
  emitted <- newEmptyMVar
  disconnectDone <- newEmptyMVar
  active <- newIORef False
  inflightFault <- newEmptyMVar
  activeCallback <- wrapCallback $ \_ _ _ -> containCallback inflightFault $ do
    atomicWriteIORef active True
    tid <- myThreadId
    publishOnce entered tid
    left <- remainingMicros deadline
    gateResult <- if left > 0 then timeout left (takeMVar gate) else pure Nothing
    atomicWriteIORef active False
    publishOnce callbackExit gateResult
  stop <- connectOwnedSignalObserved obj3 "activate" (castFunPtr activeCallback)
    (publishOnce destroyed ())
  _ <- forkIO $ do
    result <- try (activate obj3 nullPtr) :: IO (Either SomeException ())
    publishOnce emitted result
  callbackThread <- waitUntil deadline "callback-enter" (takeMVar entered)
  putStrLn ("callback-thread=" ++ show callbackThread)
  _ <- forkIO $ do
    result <- try stop :: IO (Either SomeException SignalDisconnectObservation)
    publishOnce disconnectDone result
  -- A pre-call thread marker and a caught exception are not native returns.
  -- Keep the callback gate closed until the typed post-FFI observation arrives.
  firstStop <- waitUntil deadline "disconnect-return" (takeMVar disconnectDone)
  observation <- either throwIO pure firstStop
  check "disconnect-returned-while-gate-closed" (signalDisconnectReturned observation)
  check "retirement-pending-while-gate-closed" (not (signalRetirementConfirmed observation))
  gateBefore <- tryReadMVar gate
  check "gate-still-closed-after-disconnect-return" (gateBefore == Nothing)
  wasActive <- atomicModifyIORef' active (\value -> (value, value))
  check "callback-still-active-after-disconnect-return" wasActive
  checkNoFault inflightFault "inflight-before-release-no-fault"
  earlyExit <- tryReadMVar callbackExit
  check "callback-exit-not-published-before-release" (earlyExit == Nothing)
  earlyDestroy <- tryReadMVar destroyed
  check "destroy-not-published-before-release" (earlyDestroy == Nothing)
  repeated <- stop
  check "repeat-does-not-mint-disconnect-return" (not (signalDisconnectReturned repeated))
  check "repeat-before-release-remains-pending" (not (signalRetirementConfirmed repeated))
  putMVar gate ()
  exitResult <- waitUntil deadline "callback-exit" (takeMVar callbackExit)
  check "gate-observed" (exitResult == Just ())
  emitResult <- waitUntil deadline "emitter-join" (takeMVar emitted)
  check "emitter-returned" (either (const False) (const True) emitResult)
  waitUntil deadline "destroy-notice" (takeMVar destroyed)
  checkNoFault inflightFault "inflight-after-join-no-fault"
  final <- stop
  check "retirement-confirmed-after-emitter-and-destroy" (signalRetirementConfirmed final)
  check "retirement-recheck-no-new-disconnect-return" (not (signalDisconnectReturned final))
  freeHaskellFunPtr activeCallback
  unref obj3
  obj2 <- withCString "retained-fixture" $ \name -> actionNew name nullPtr
  check "second-object-created" (obj2 /= nullPtr)
  retainedFault <- newEmptyMVar
  cb2 <- wrapCallback $ \_ _ _ -> containCallback retainedFault (pure ())
  disconnect2 <- connectOwnedSignal obj2 "activate" (castFunPtr cb2) $
    ioError (userError "injected release failure")
  first <- try disconnect2 :: IO (Either SomeException ())
  second <- try disconnect2 :: IO (Either SomeException ())
  check "release-exception-uncertain" (either (const True) (const False) first)
  check "repeat-remains-uncertain" (either (const True) (const False) second)
  -- obj2 and cb2 remain retained until this isolated process exits.
  putStrLn "owned-signal-lifecycle: complete"
