{-# LANGUAGE ScopedTypeVariables #-}
-- Shared by the real async filter path and its literal retirement controls.
module Warlock.Ui.CallbackRetirement
  (CallbackState, newCallbackState, captureOwnedCallback, callbackObservation,
   quarantineCallback, runCallbackOperation, retireOwnedCallback) where

import Control.Exception
  (SomeAsyncException, SomeException, catch, evaluate, fromException, mask_, throwIO, try, uninterruptibleMask_)
import Control.Monad (unless)
import Data.IORef (IORef, atomicModifyIORef', newIORef)
import Warlock.Ui.DefaultContextOwner
  (PhysicalDefaultContextOwner, requirePhysicalDefaultContextOwner)

data Completion a = Pending | Running | Completed a | Retiring | Quarantined | Retired
newtype CallbackState a = CallbackState (IORef (Completion a))

newCallbackState :: IO (CallbackState a)
newCallbackState = CallbackState <$> newIORef Pending

quarantineCallback :: CallbackState a -> IO ()
quarantineCallback (CallbackState cell) = uninterruptibleMask_ $
 atomicModifyIORef' cell (\_ -> (Quarantined, ()))

callbackObservation :: CallbackState a -> IO (Maybe a, Bool)
callbackObservation (CallbackState cell) = atomicModifyIORef' cell $ \state ->
 (state, case state of
   Completed value -> (Just value, False)
   Quarantined -> (Nothing, True)
   _ -> (Nothing, False))

-- Fresh proof before EACH actual affine operation, and again after return.
-- The caller still owns the original D; this cell has no clock or authority.
runCallbackOperation :: PhysicalDefaultContextOwner -> CallbackState a -> IO b -> IO b
runCallbackOperation owner state@(CallbackState cell) action =
 (do
   permitted <- atomicModifyIORef' cell (\old -> (old, case old of Quarantined -> False; Retiring -> False; Retired -> False; _ -> True))
   unless permitted (ioError (userError "callback custody quarantined or retired"))
   requirePhysicalDefaultContextOwner owner
   value <- action
   requirePhysicalDefaultContextOwner owner
   (_, afterFault) <- callbackObservation state
   unless (not afterFault) (ioError (userError "callback custody lost during operation"))
   pure value) `catch` (\(failure :: SomeException) -> quarantineCallback state >> throwIO failure)

-- Entire foreign callback body, including proof/forcing/publication, is caught.
-- Fault publication is bounded, nonblocking and cannot call a user recorder.
captureOwnedCallback :: PhysicalDefaultContextOwner -> CallbackState a -> IO a -> IO ()
captureOwnedCallback owner state@(CallbackState cell) action = mask_ $
 (do
   admitted <- atomicModifyIORef' cell (\old -> case old of
     Pending -> (Running, True)
     _ -> (Quarantined, False))
   unless admitted (ioError (userError "callback completion repeated or retired"))
   value <- runCallbackOperation owner state action >>= evaluate
   atomicModifyIORef' cell (\old -> case old of
     Running -> (Completed value, ())
     _ -> (Quarantined, ())))
 `catch` (\(_ :: SomeException) -> quarantineCallback state)

-- Call only after the synchronous native dispatch/save call has returned on
-- the exclusively acquired default context. Completed alone is not an ABI
-- proof that an arbitrary foreign-thread callback has left its trampoline.
retireOwnedCallback :: PhysicalDefaultContextOwner -> CallbackState a -> [IO ()] -> IO Bool
retireOwnedCallback owner state@(CallbackState cell) actions = mask_ $ do
 -- There is no transition back to Completed. Only this successful reservation
 -- may run release actions; nested retirement refuses without disturbing it.
 reserved <- atomicModifyIORef' cell (\old -> case old of
   Completed _ -> (Retiring, True)
   _ -> (old, False))
 if not reserved then pure False else do
  let requireReservation = do
       owned <- atomicModifyIORef' cell (\old -> (old, case old of
         Retiring -> True
         _ -> False))
       unless owned (ioError (userError "callback retirement reservation lost"))
      release action = do
       requireReservation
       requirePhysicalDefaultContextOwner owner
       requireReservation
       _ <- action
       requirePhysicalDefaultContextOwner owner
       requireReservation
  result <- try $ do
   mapM_ release actions
   requirePhysicalDefaultContextOwner owner
   atomicModifyIORef' cell (\old -> case old of
     Retiring -> (Retired, True)
     _ -> (Quarantined, False))
  case result of
   Right clean -> pure clean
   Left (failure :: SomeException) -> do
    quarantineCallback state
    case fromException failure :: Maybe SomeAsyncException of
     Just _ -> throwIO failure
     Nothing -> pure False
