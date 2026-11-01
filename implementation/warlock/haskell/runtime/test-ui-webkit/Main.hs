{-# LANGUAGE ForeignFunctionInterface #-}
{-# LANGUAGE ScopedTypeVariables #-}
{-# LANGUAGE OverloadedStrings #-}
-- Real GObject signal lifecycle and isolated namespace guard controls. No GTK
-- display, WebKit page, original-scenario or GUI acceptance.
module Main (main) where

import Control.Exception (IOException, SomeException, displayException, try, finally)
import Control.Concurrent (threadDelay)
import Control.Monad (forM_, unless)
import Data.IORef
import qualified Data.Text as T
import qualified Warlock.Protocol.StrictJson as J
import Warlock.Protocol.Identity (renderCounter)
import Warlock.Ui.Mvp (leaseScope, leaseRevision, leasePublication, leaseToken, leasePopupOpen)
import Foreign.C.String (CString, withCString)
import Foreign.C.Types (CInt(..))
import Foreign.Ptr (FunPtr, Ptr, castFunPtr, freeHaskellFunPtr, nullPtr)
import System.Exit (ExitCode(..))
import System.IO (hFlush, stdout)
import System.IO.Error (ioeGetErrorString)
import System.Posix.Process (ProcessStatus(..), exitImmediately, forkProcess, getProcessStatus)
import System.Posix.Signals (sigKILL, signalProcess)
import Warlock.Capture.Process.Bootstrap (deadlineAfter, remainingMicros)
import Warlock.Ui.EngineCustody (startCustody, stopCustody, abandonCustody)
import Warlock.Ui.PrivateNetwork (enterPrivateNetwork)
import Warlock.Ui.WebKit (connectOwnedSignal, withOwnedDefaultContext, retireInOrder, readMvpLease, handleMvpDispatch, requireThreadCompatibleNamespace)

data Object
type Notify = Ptr Object -> Ptr () -> Ptr () -> IO ()
foreign import ccall safe "g_simple_action_new" actionNew :: CString -> Ptr () -> IO (Ptr Object)
foreign import ccall safe "g_simple_action_set_enabled" actionEnabled :: Ptr Object -> CInt -> IO ()
foreign import ccall safe "g_object_unref" unref :: Ptr Object -> IO ()
foreign import ccall unsafe "g_main_context_new" contextNew :: IO (Ptr ())
foreign import ccall unsafe "g_main_context_push_thread_default" contextPush :: Ptr () -> IO ()
foreign import ccall unsafe "g_main_context_pop_thread_default" contextPop :: Ptr () -> IO ()
foreign import ccall unsafe "g_main_context_unref" contextUnref :: Ptr () -> IO ()
foreign import ccall "wrapper" wrapNotify :: Notify -> IO (FunPtr Notify)

check :: String -> Bool -> IO ()
check name ok = unless ok (ioError (userError name))

newAction :: IO (Ptr Object)
newAction = withCString "warlock-test" $ \name -> do
 value <- actionNew name nullPtr
 check "GSimpleAction allocated" (value /= nullPtr)
 pure value

-- Each sequence drives the actual GObject notify signal, then checks that
-- disconnection prevents later invocation and releases the wrapper once.
normalSequence :: Int -> IO ()
normalSequence seed = do
 object <- newAction
 calls <- newIORef (0 :: Int)
 frees <- newIORef (0 :: Int)
 handler <- wrapNotify $ \_ _ _ -> modifyIORef' calls (+1)
 let release = modifyIORef' frees (+1) >> freeHaskellFunPtr handler
 disconnect <- connectOwnedSignal object "notify::enabled" (castFunPtr handler) release
 let next x = (x * 1103515245 + 12345) `mod` 2147483648
     values = take (20 + seed `mod` 64) (map (\x -> fromIntegral ((x `div` 65536) `mod` 2) :: CInt) (iterate next (toInteger seed)))
     transitions = length (filter (uncurry (/=)) (zip (1:values) values))
 forM_ values (actionEnabled object)
 before <- readIORef calls
 check "notifications match actual value transitions" (before == transitions)
 disconnect
 disconnect
 freed <- readIORef frees
 check "successful disconnect releases exactly once" (freed == 1)
 case reverse values of
  current:_ -> actionEnabled object (if current == 0 then 1 else 0)
  [] -> ioError (userError "empty generated sequence")
 after <- readIORef calls
 check "no callback after disconnect" (after == before)
 unref object

-- Disconnect from inside the active callback. The synchronous attempt must
-- stay uncertain until GLib finishes using that closure; a later retry sees
-- the real destroy notification without disconnecting or freeing twice.
delayedNotify :: IO ()
delayedNotify = do
 object <- newAction
 disconnectCell <- newIORef Nothing
 handlerCell <- newIORef Nothing
 frees <- newIORef (0 :: Int)
 inside <- newIORef Nothing
 handler <- wrapNotify $ \_ _ _ -> do
  maybeAction <- readIORef disconnectCell
  case maybeAction of
   Nothing -> ioError (userError "missing disconnect")
   Just disconnect -> do
    result <- try disconnect :: IO (Either SomeException ())
    released <- readIORef frees
    writeIORef inside (Just (either (const True) (const False) result, released))
 writeIORef handlerCell (Just handler)
 let release = do
      modifyIORef' frees (+1)
      value <- readIORef handlerCell
      maybe (ioError (userError "missing handler")) freeHaskellFunPtr value
 disconnect <- connectOwnedSignal object "notify::enabled" (castFunPtr handler) release
 writeIORef disconnectCell (Just disconnect)
 actionEnabled object 0
 during <- readIORef inside
 check "active callback retained and uncertainty reported" (during == Just (True,0))
 disconnect
 freed <- readIORef frees
 check "deferred notify retires once" (freed == 1)
 actionEnabled object 1
 unref object

-- A notifier-side cleanup failure must never become a successful receipt,
-- and retries must not invoke the release action a second time.
failedRelease :: IO ()
failedRelease = do
 object <- newAction
 count <- newIORef (0 :: Int)
 handler <- wrapNotify $ \_ _ _ -> pure ()
 let release = do
      modifyIORef' count (+1)
      freeHaskellFunPtr handler
      ioError (userError "injected release failure")
 disconnect <- connectOwnedSignal object "notify::enabled" (castFunPtr handler) release
 first <- try disconnect :: IO (Either SomeException ())
 second <- try disconnect :: IO (Either SomeException ())
 calls <- readIORef count
 check "failed release stays uncertain" (either (const True) (const False) first && either (const True) (const False) second)
 check "failed release not repeated" (calls == 1)
 unref object

-- Real GLib active-emission uncertainty must stop the same release chain
-- used by WebKit before the owning GObject can be unreferenced.
activeQuarantine :: IO ()
activeQuarantine = do
 object <- newAction
 disconnectCell <- newIORef Nothing
 handlerCell <- newIORef Nothing
 freed <- newIORef (0 :: Int)
 unrefs <- newIORef (0 :: Int)
 resultCell <- newIORef Nothing
 handler <- wrapNotify $ \_ _ _ -> do
  pending <- readIORef disconnectCell
  case pending of
   Nothing -> ioError (userError "missing quarantine disconnect")
   Just disconnect -> do
    outcomes <- retireInOrder (pure 1000000)
      [disconnect, modifyIORef' unrefs (+1) >> unref object]
    writeIORef resultCell (Just (any (either (const True) (const False)) outcomes))
 writeIORef handlerCell (Just handler)
 let release = do
      modifyIORef' freed (+1)
      value <- readIORef handlerCell
      maybe (ioError (userError "missing quarantine handler")) freeHaskellFunPtr value
 disconnect <- connectOwnedSignal object "notify::enabled" (castFunPtr handler) release
 writeIORef disconnectCell (Just disconnect)
 actionEnabled object 0
 uncertain <- readIORef resultCell
 before <- readIORef unrefs
 check "active disconnect quarantines dependent object" (uncertain == Just True && before == 0)
 afterNotify <- readIORef freed
 check "deferred closure receipt arrived" (afterNotify == 1)
 outcomes <- retireInOrder (pure 1000000)
   [disconnect, modifyIORef' unrefs (+1) >> unref object]
 after <- readIORef unrefs
 check "confirmed retirement permits later unref" (all (either (const False) (const True)) outcomes && after == 1)

-- Inject a failure at every position: no subsequent release may execute.
releaseSequenceProperties :: IO ()
releaseSequenceProperties = do
 forM_ [0..15 :: Int] $ \fault -> do
  observed <- newIORef ([] :: [Int])
  let action n = do
       modifyIORef' observed (++ [n])
       if n == fault then ioError (userError "injected cleanup failure") else pure ()
  results <- retireInOrder (pure 1000000) (map action [0..15])
  actual <- readIORef observed
  check "cleanup stops on first failed release" (actual == [0..fault] && any (either (const True) (const False)) results)
 called <- newIORef False
 expired <- retireInOrder (pure 250000) [writeIORef called True]
 actual <- readIORef called
 check "cleanup reserve quarantines without call" (not actual && any (either (const True) (const False)) expired)
 budget <- newIORef (300000 :: Int)
 lateCalled <- newIORef False
 overrun <- retireInOrder (readIORef budget) [writeIORef budget 200000, writeIORef lateCalled True]
 later <- readIORef lateCalled
 check "synchronous release overrun stops later calls" (not later && any (either (const True) (const False)) overrun)

projection :: Integer -> Integer -> Bool -> J.Json
projection publication token popup =
 let scope = J.JObject [("id",J.JString "7"),("generation",J.JString "3")]
 in J.JObject
  [("viewProtocol",J.JNumber "1"),("kind",J.JString "view-frame"),("revision",J.JString "11"),
   ("views",J.JArray [scope]),("focusOwner",J.JNull),
   ("popupOwner",if popup then scope else J.JNull),
   ("frame",J.JObject [("surfaceProtocol",J.JNumber "2"),("publication",J.JString (T.pack (show publication))),("lease",J.JString (T.pack (show token)))]),
   ("announcer",J.JNull),("announcement",J.JNull)]

leaseSequenceProperties :: IO ()
leaseSequenceProperties = do
 absent <- readMvpLease (pure Nothing)
 check "absent committed projection has no lease" (case absent of Nothing -> True; Just _ -> False)
 forM_ [1..64 :: Integer] $ \seed -> do
  let publication = 18446744073709551615 - seed
      token = (seed * 7919) `mod` 100000
      popup = odd seed
  value <- readMvpLease (pure (Just (projection publication token popup)))
  check "committed full-width lease survives" $ case value of
   Just lease -> renderCounter (leasePublication lease) == T.pack (show publication)
     && renderCounter (leaseToken lease) == T.pack (show token) && leasePopupOpen lease == popup
     && renderCounter (leaseRevision lease) == "11"
     && case leaseScope lease of
          Just (scopeId,generation) -> renderCounter scopeId == "7" && renderCounter generation == "3"
          Nothing -> False
   Nothing -> False
 invalid <- try (readMvpLease (pure (Just (projection 0 1 True))) >> pure ()) :: IO (Either SomeException ())
 check "invalid publication refuses lease" (either (const True) (const False) invalid)
 let mismatch = case projection 1 2 True of
      J.JObject fields -> J.JObject [(key, if key == "popupOwner" then J.JObject [("id",J.JString "8"),("generation",J.JString "3")] else value) | (key,value) <- fields]
      other -> other
 refused <- try (readMvpLease (pure (Just mismatch)) >> pure ()) :: IO (Either SomeException ())
 check "mismatched popup scope refuses lease" (either (const True) (const False) refused)

-- Exercise the exact Owner refusal contract used by the real MVP loop:
-- only the explicitly stale snapshot can be dropped; malformed/other errors
-- remain failures, and no retry or successful event count is invented.
staleDispatch :: IO ()
staleDispatch = do
 stale <- try (handleMvpDispatch (Left "stale native UI projection")) :: IO (Either SomeException ())
 check "stale projection is dropped" (either (const False) (const True) stale)
 forM_ ["", "stale native UI projection ", "invalid native UI projection", "UI event queue full"] $ \reason -> do
  failure <- try (handleMvpDispatch (Left reason)) :: IO (Either SomeException ())
  check "non-stale owner failure propagates" (either (const True) (const False) failure)
 success <- try (handleMvpDispatch (Right 1)) :: IO (Either SomeException ())
 check "successful dispatch continues" (either (const False) (const True) success)

contextOwnership :: IO ()
contextOwnership = do
 entered <- newIORef False
 context <- contextNew
 check "alternate context allocated" (context /= nullPtr)
 contextPush context
 wrong <- (try (withOwnedDefaultContext (writeIORef entered True)) :: IO (Either SomeException ()))
   `finally` (contextPop context >> contextUnref context)
 actual <- readIORef entered
 check "nondefault thread context refused before action" (either (const True) (const False) wrong && not actual)
 withOwnedDefaultContext (withOwnedDefaultContext (writeIORef entered True))
 worked <- readIORef entered
 check "default context ownership is recursive" worked

-- Actual thread/PID-for-children guard; no GTK initialization. The mismatched
-- namespace is confined to an owned fork child and its real custody bracket.
namespaceCompatibility :: IO ()
namespaceCompatibility = do
 requireThreadCompatibleNamespace
 deadline <- deadlineAfter 5000000 >>= either (ioError . userError . show) pure
 pid <- forkProcess $ do
  outcome <- try $ do
   enterPrivateNetwork
   requireThreadCompatibleNamespace
   custody <- startCustody (remainingMicros deadline)
   flip finally (abandonCustody custody) $ do
    refused <- try requireThreadCompatibleNamespace :: IO (Either IOException ())
    check "PID-for-children mismatch refused before GTK" $ case refused of
     Left problem -> ioeGetErrorString problem == "GTK thread PID namespace incompatible or unavailable"
     Right () -> False
    clean <- stopCustody (remainingMicros deadline) custody
    check "mismatch fixture custody normally retired" clean
  case outcome of
   Right () -> exitImmediately ExitSuccess
   Left (problem :: SomeException) -> do
    putStrLn ("namespace compatibility child failure: " ++ displayException problem)
    hFlush stdout
    exitImmediately (ExitFailure 1)
 let await = do
      status <- getProcessStatus False False pid
      case status of
       Just value -> pure (Just value)
       Nothing -> do
        remaining <- remainingMicros deadline
        if remaining <= 0 then pure Nothing else threadDelay (min remaining 1000) >> await
 status <- await
 case status of
  Just (Exited ExitSuccess) -> pure ()
  Just _ -> ioError (userError "namespace compatibility child failed")
  Nothing -> do
   -- Only this owned direct child is signalled; forced cleanup is a failure.
   signalProcess sigKILL pid
   _ <- getProcessStatus True False pid
   ioError (userError "namespace compatibility child exceeded original deadline")

main :: IO ()
main = do
 namespaceCompatibility
 -- Reproducible, bounded sequence variation, including repeated toggles.
 forM_ [0..63] normalSequence
 delayedNotify
 failedRelease
 activeQuarantine
 releaseSequenceProperties
 leaseSequenceProperties
 staleDispatch
 contextOwnership
