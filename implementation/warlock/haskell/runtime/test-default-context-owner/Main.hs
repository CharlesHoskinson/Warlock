{-# LANGUAGE ForeignFunctionInterface #-}
{-# LANGUAGE ScopedTypeVariables #-}
module Main (main) where

import Control.Concurrent (forkIO, forkOS, isCurrentThreadBound, rtsSupportsBoundThreads)
import Control.Concurrent.MVar (newEmptyMVar, putMVar, takeMVar)
import Control.Exception (Exception, SomeException, bracket, catch, finally, mask_, throwIO, try)
import Control.Monad (unless, void)
import Data.IORef (newIORef, readIORef, writeIORef)
import Foreign.C.String (CString, withCString)
import Foreign.C.Types (CInt(..))
import Foreign.Ptr (FunPtr, Ptr, nullFunPtr, nullPtr)
import GHC.Clock (getMonotonicTimeNSec)
import System.Environment (getArgs)
import System.Timeout (timeout)
import Warlock.Ui.CallbackRetirement
  (newCallbackState, captureOwnedCallback, callbackObservation, retireOwnedCallback, runCallbackOperation)
import Warlock.Ui.DefaultContextOwner
  (PhysicalDefaultContextOwner, withPhysicalDefaultContextOwner,
   requirePhysicalDefaultContextOwner, ownerRemainingMicros)

import Warlock.Ui.ProcessSignalOwner
  (ProcessSignalDisconnect(..), connectProcessSignal, disconnectProcessSignal)

type ActionCallback = Ptr () -> Ptr () -> Ptr () -> IO ()
foreign import ccall "wrapper" wrapActionCallback :: ActionCallback -> IO (FunPtr ActionCallback)
foreign import ccall unsafe "g_simple_action_new" actionNew :: CString -> Ptr () -> IO (Ptr ())
foreign import ccall safe "g_action_activate" actionActivate :: Ptr () -> Ptr () -> IO ()

foreign import ccall unsafe "gettid" kernelTid :: IO CInt
foreign import ccall unsafe "getpid" kernelPid :: IO CInt
foreign import ccall unsafe "g_main_context_default" defaultContext :: IO (Ptr ())
foreign import ccall unsafe "g_main_context_is_owner" isOwner :: Ptr () -> IO CInt
foreign import ccall unsafe "g_main_context_new" contextNew :: IO (Ptr ())
foreign import ccall unsafe "g_main_context_unref" contextUnref :: Ptr () -> IO ()
foreign import ccall unsafe "g_main_context_push_thread_default" contextPush :: Ptr () -> IO ()
foreign import ccall unsafe "g_main_context_pop_thread_default" contextPop :: Ptr () -> IO ()
foreign import ccall unsafe "g_main_context_acquire" contextAcquire :: Ptr () -> IO CInt
foreign import ccall unsafe "g_main_context_release" contextRelease :: Ptr () -> IO ()

data ExpectedFailure = ExpectedFailure deriving Show
instance Exception ExpectedFailure

check :: String -> Bool -> IO ()
check label ok = unless ok (ioError (userError label))

refused :: IO a -> IO Bool
refused action = do
 result <- try (void action)
 pure (case result of Left (_ :: SomeException) -> True; Right () -> False)

bounded :: IO Int -> IO a -> IO a
bounded remaining action = do
 left <- remaining
 check "original deadline remains" (left > 0)
 result <- timeout left action
 maybe (ioError (userError "original deadline wait exhausted")) pure result

retained :: IO (Maybe PhysicalDefaultContextOwner) -> IO PhysicalDefaultContextOwner
retained readOwner = readOwner >>= maybe (ioError (userError "missing actual owner")) pure

controls :: IO Int -> IO ()
controls remaining = do
 tid <- kernelTid
 pid <- kernelPid
 check "actual initial kernel thread" (tid > 0 && tid == pid)
 context <- defaultContext
 check "actual default context" (context /= nullPtr)
 before <- isOwner context
 check "fixture starts without borrowed context" (before == 0)
 saved <- newIORef Nothing
 withPhysicalDefaultContextOwner remaining $ \owner -> do
  writeIORef saved (Just owner)
  requirePhysicalDefaultContextOwner owner
  actual <- isOwner context
  check "actual acquired default context" (actual /= 0)
  left <- ownerRemainingMicros owner
  check "original remaining callback" (left > 0 && left <= 5000000)
  withPhysicalDefaultContextOwner remaining $ \nested -> requirePhysicalDefaultContextOwner nested
  requirePhysicalDefaultContextOwner owner
  afterNested <- isOwner context
  check "inner release preserves outer acquisition" (afterNested /= 0)
 after <- isOwner context
 check "scope releases actual context" (after == 0)
 previous <- retained (readIORef saved)
 stale <- refused (requirePhysicalDefaultContextOwner previous)
 check "retired opaque owner refuses" stale
 entered <- newIORef False
 expired <- refused (withPhysicalDefaultContextOwner (pure 0) (\_ -> writeIORef entered True))
 invoked <- readIORef entered
 check "zero remaining literal refuses before action" (expired && not invoked)
 bracket contextNew contextUnref $ \foreignContext -> do
  check "distinct context allocated" (foreignContext /= nullPtr && foreignContext /= context)
  contextPush foreignContext
  foreignResult <- refused (withPhysicalDefaultContextOwner remaining (\_ -> writeIORef entered True))
    `finally` contextPop foreignContext
  check "foreign thread default refuses acquisition" foreignResult
  withPhysicalDefaultContextOwner remaining $ \owner -> do
   contextPush foreignContext
   changed <- refused (requirePhysicalDefaultContextOwner owner) `finally` contextPop foreignContext
   check "changed thread default refuses live use" changed
   requirePhysicalDefaultContextOwner owner
 escaped <- newIORef Nothing
 outcome <- try (withPhysicalDefaultContextOwner remaining $ \owner -> do
   writeIORef escaped (Just owner)
   throwIO ExpectedFailure)
 check "exact synchronous exception propagated" (case outcome of Left ExpectedFailure -> True; Right () -> False)
 afterException <- isOwner context
 check "exception scope released context" (afterException == 0)
 leaked <- retained (readIORef escaped)
 invalid <- refused (requirePhysicalDefaultContextOwner leaked)
 check "exception scope invalidated owner" invalid
 retirementControls remaining
 processSignalControls remaining
 if rtsSupportsBoundThreads then threadedControls remaining context else do
  bound <- isCurrentThreadBound
  check "nonthreaded mode never pretends GHC bound" (not bound)
  putStrLn "physical-context-owner: nonthreaded-main complete"

threadedControls :: IO Int -> Ptr () -> IO ()
threadedControls remaining context = do
 bound <- isCurrentThreadBound
 check "threaded fixture main is bound" bound
 withPhysicalDefaultContextOwner remaining $ \owner -> do
  done <- newEmptyMVar
  _ <- forkOS $ do
   tid <- kernelTid
   pid <- kernelPid
   result <- refused (requirePhysicalDefaultContextOwner owner)
   fresh <- refused (withPhysicalDefaultContextOwner remaining (\_ -> pure ()))
   putMVar done (tid /= pid && result && fresh)
  foreignRefused <- bounded remaining (takeMVar done)
  check "actual foreign physical thread refuses old and new owner" foreignRefused
 unbound <- newEmptyMVar
 _ <- forkIO $ do
  boundNow <- isCurrentThreadBound
  result <- refused (withPhysicalDefaultContextOwner remaining (\_ -> pure ()))
  putMVar unbound (not boundNow && result)
 unboundRefused <- bounded remaining (takeMVar unbound)
 check "threaded unbound caller refuses" unboundRefused
 ready <- newEmptyMVar
 release <- newEmptyMVar
 finished <- newEmptyMVar
 _ <- forkOS $ do
  outcome <- try $ do
   acquired <- contextAcquire context
   check "other physical thread acquired real context" (acquired /= 0)
   (putMVar ready True >> bounded remaining (takeMVar release)) `finally` contextRelease context
  putMVar finished (outcome :: Either SomeException ())
 busyReady <- bounded remaining (takeMVar ready)
 check "busy fixture actual owner ready" busyReady
 busy <- refused (withPhysicalDefaultContextOwner remaining (\_ -> pure ()))
 putMVar release ()
 joined <- bounded remaining (takeMVar finished)
 check "busy context refuses without releasing other owner" (busy && either (const False) (const True) joined)
 remainingOwner <- isOwner context
 check "other owner released after handshake" (remainingOwner == 0)
 putStrLn "physical-context-owner: threaded-main complete"

main :: IO ()
main = do
 args <- getArgs
 absolute <- case args of
  [text] | not (null text) && all (\c -> c >= '0' && c <= '9') text ->
    case reads text of [(value, "")] -> pure (value :: Integer); _ -> ioError (userError "invalid absolute D")
  _ -> ioError (userError "one original absolute monotonic deadline required")
 now <- toInteger <$> getMonotonicTimeNSec
 check "original D positive and at most five seconds" (absolute > now && absolute - now <= 5000000000)
 let remaining = do
      current <- toInteger <$> getMonotonicTimeNSec
      pure (fromInteger (max 0 (min 5000000 ((absolute - current) `div` 1000))))
 controls remaining

-- These literals use the SAME retirement cell as compileFilter. The release
-- actions are IORef receipts, not real native frees or WebKit callbacks.
retirementControls :: IO Int -> IO ()
retirementControls remaining = do
 withPhysicalDefaultContextOwner remaining $ \owner -> do
  normal <- newCallbackState
  releases <- newIORef ([] :: [String])
  captureOwnedCallback owner normal (pure (7 :: Int))
  (result, fault) <- callbackObservation normal
  clean <- retireOwnedCallback owner normal [writeIORef releases ["release"]]
  rows <- readIORef releases
  twice <- retireOwnedCallback owner normal [writeIORef releases ["duplicate"]]
  afterTwice <- readIORef releases
  check "normal callback completes and retires once" (result == Just 7 && not fault && clean && not twice && rows == ["release"] && afterTwice == ["release"])
  recursive <- newCallbackState
  captureOwnedCallback owner recursive (pure (19 :: Int))
  releaseCount <- newIORef (0 :: Int)
  nestedAccepted <- newIORef True
  let release = do
       count <- readIORef releaseCount
       writeIORef releaseCount (count + 1)
  outerClean <- retireOwnedCallback owner recursive [do
    release
    innerClean <- retireOwnedCallback owner recursive [release]
    writeIORef nestedAccepted innerClean]
  actualCount <- readIORef releaseCount
  innerAccepted <- readIORef nestedAccepted
  check "same-owner recursive retirement refuses second release" (outerClean && not innerAccepted && actualCount == 1)
  pending <- newCallbackState
  pendingClean <- retireOwnedCallback owner pending [writeIORef releases ["pending-release"]]
  afterPending <- readIORef releases
  check "pending callback never releases" (not pendingClean && afterPending == ["release"])
  bracket contextNew contextUnref $ \foreignContext -> do
   check "retirement foreign context allocated" (foreignContext /= nullPtr)
   failed <- newCallbackState
   entered <- newIORef False
   contextPush foreignContext
   captureOwnedCallback owner failed (writeIORef entered True >> pure (9 :: Int))
     `finally` contextPop foreignContext
   (failedResult, quarantined) <- callbackObservation failed
   released <- newIORef False
   failedClean <- retireOwnedCallback owner failed [writeIORef released True]
   actionRan <- readIORef entered
   releaseRan <- readIORef released
   check "ready owner-proof failure quarantines not completed" (failedResult == Nothing && quarantined && not actionRan && not failedClean && not releaseRan)
   changed <- newCallbackState
   captureOwnedCallback owner changed (pure (11 :: Int))
   contextPush foreignContext
   changedClean <- retireOwnedCallback owner changed [writeIORef released True]
     `finally` contextPop foreignContext
   (_, changedFault) <- callbackObservation changed
   changedRelease <- readIORef released
   check "changed lease at retirement releases nothing" (not changedClean && changedFault && not changedRelease)
  bodyFault <- newCallbackState
  captureOwnedCallback owner bodyFault (throwIO ExpectedFailure :: IO Int)
  (_, bodyQuarantined) <- callbackObservation bodyFault
  bodyRelease <- newIORef False
  bodyClean <- retireOwnedCallback owner bodyFault [writeIORef bodyRelease True]
  bodyFreed <- readIORef bodyRelease
  check "callback exception remains quarantine" (bodyQuarantined && not bodyClean && not bodyFreed)
 -- A literal failure of the ORIGINAL remaining callback; it is never restored
 -- or replaced inside this scope. The Root-supplied absolute D is unchanged.
 zero <- newIORef False
 let originalRemaining = do
      expired <- readIORef zero
      if expired then pure 0 else remaining
 withPhysicalDefaultContextOwner originalRemaining $ \owner -> do
  complete <- newCallbackState
  captureOwnedCallback owner complete (pure (13 :: Int))
  writeIORef zero True
  released <- newIORef False
  clean <- retireOwnedCallback owner complete [writeIORef released True]
  (_, fault) <- callbackObservation complete
  ran <- readIORef released
  check "expired retirement quarantines with zero release" (not clean && fault && not ran)
 midZero <- newIORef False
 let midRemaining = do
      expired <- readIORef midZero
      if expired then pure 0 else remaining
 withPhysicalDefaultContextOwner midRemaining $ \owner -> do
  complete <- newCallbackState
  captureOwnedCallback owner complete (pure (17 :: Int))
  releases <- newIORef ([] :: [String])
  clean <- retireOwnedCallback owner complete
    [writeIORef releases ["first-valid-release"] >> writeIORef midZero True,
     writeIORef releases ["invalid-second-release"]]
  (_, fault) <- callbackObservation complete
  rows <- readIORef releases
  check "mid-retirement loss stops remaining releases" (not clean && fault && rows == ["first-valid-release"])
 cancelZero <- newIORef False
 let cancelRemaining = do
      expired <- readIORef cancelZero
      if expired then pure 0 else remaining
 withPhysicalDefaultContextOwner cancelRemaining $ \owner -> do
  pending <- newCallbackState
  cancelled <- newIORef False
  writeIORef cancelZero True
  failure <- refused (runCallbackOperation owner pending (writeIORef cancelled True))
  (_, fault) <- callbackObservation pending
  ran <- readIORef cancelled
  check "expired cancellation proof prevents operation" (failure && fault && not ran)

-- Process pins and owning object refs intentionally survive this fixture.
-- No destroy-notifier/free callback exists; Root must observe process death.
processSignalControls :: IO Int -> IO ()
processSignalControls remaining = do
 withPhysicalDefaultContextOwner remaining $ \owner -> do
  object <- withCString "process-pinned" $ \name -> actionNew name nullPtr
  check "process signal cold object allocated" (object /= nullPtr)
  calls <- newIORef (0 :: Int)
  faults <- newIORef False
  callback <- wrapActionCallback $ \_ _ _ -> mask_ $
    (do
      requirePhysicalDefaultContextOwner owner
      count <- readIORef calls
      writeIORef calls (count + 1))
    `catch` (\(_ :: SomeException) -> writeIORef faults True)
  signal <- connectProcessSignal owner object "activate" callback
  actionActivate object nullPtr
  first <- readIORef calls
  check "process signal callback runs under owner" (first == 1)
  bracket contextNew contextUnref $ \foreignContext -> do
   check "process signal foreign context allocated" (foreignContext /= nullPtr)
   contextPush foreignContext
   denied <- refused (disconnectProcessSignal signal) `finally` contextPop foreignContext
   check "process signal foreign context refuses disconnect" denied
  result <- disconnectProcessSignal signal
  check "process signal disconnect return retains callback" (result == DisconnectReturnedRetained)
  actionActivate object nullPtr
  after <- readIORef calls
  repeated <- disconnectProcessSignal signal
  fault <- readIORef faults
  check "process signal disconnected callback not invoked again" (after == 1 && not fault)
  check "process signal repeat never claims another return" (repeated == DisconnectNotRepeatedRetained)
  badObject <- refused (connectProcessSignal owner nullPtr "activate" callback)
  badCallback <- refused (connectProcessSignal owner object "activate" (nullFunPtr :: FunPtr ActionCallback))
  check "process signal null object refused" badObject
  check "process signal null callback refused" badCallback
 zero <- newIORef False
 let originalRemaining = do
      expired <- readIORef zero
      if expired then pure 0 else remaining
 withPhysicalDefaultContextOwner originalRemaining $ \owner -> do
  object <- withCString "process-pinned-expired" $ \name -> actionNew name nullPtr
  check "process signal expiry object allocated" (object /= nullPtr)
  callback <- wrapActionCallback $ \_ _ _ -> pure ()
  signal <- connectProcessSignal owner object "activate" callback
  writeIORef zero True
  denied <- refused (disconnectProcessSignal signal)
  check "process signal expired owner retains connection" denied
 escaped <- withPhysicalDefaultContextOwner remaining $ \owner -> do
  object <- withCString "process-pinned-stale" $ \name -> actionNew name nullPtr
  check "process signal stale object allocated" (object /= nullPtr)
  callback <- wrapActionCallback $ \_ _ _ -> pure ()
  connectProcessSignal owner object "activate" callback
 stale <- refused (disconnectProcessSignal escaped)
 check "process signal stale owner retains connection" stale
