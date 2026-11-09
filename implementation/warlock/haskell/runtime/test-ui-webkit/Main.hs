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
import qualified Data.ByteString.Char8 as BS
import Warlock.Ui.Owner (retainRequestTrace)
import qualified Warlock.Protocol.StrictJson as J
import Warlock.Protocol.Identity (renderCounter)
import Warlock.Ui.Mvp (MvpFocusRole(..), parseMvpFocusIntent, mvpFocusTransition, leaseScope, leaseRevision, leasePublication, leaseToken, leasePopupOpen)
import Foreign.C.String (CString, withCString)
import Foreign.C.Types (CInt(..))
import Foreign.Ptr (FunPtr, Ptr, castFunPtr, freeHaskellFunPtr, nullPtr)
import System.Exit (ExitCode(..))
import System.Environment (getArgs)
import System.IO (hFlush, stdout)
import System.IO.Error (ioeGetErrorString)
import System.Posix.Process (ProcessStatus(..), exitImmediately, forkProcess, getProcessStatus)
import System.Posix.Signals (sigKILL, signalProcess)
import Warlock.Capture.Process.Bootstrap (deadlineAfter, remainingMicros)
import Warlock.Ui.EngineCustody (startCustody, stopCustody, abandonCustody)
import Warlock.Ui.PrivateNetwork (enterPrivateNetwork)
import Warlock.Ui.WebKit (rendererPhaseFlags, rendererPhasePolling, rendererPhasePublication, rendererPhaseRequest, rendererPhaseLeaf, rendererPhaseSnapshotScript, firstMouseupDiagnosticScript, finiteDpiFallbackSetting, rendererAllocationReady, rendererDiagnosticEnvelope, providerVersionQualified, connectOwnedSignal, withOwnedDefaultContext, retireInOrder, readMvpLease, handleMvpDispatch, requireThreadCompatibleNamespace)

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

-- Literal current projection controls for physical GTK renderer focus.
keyboardFocusControls :: IO ()
keyboardFocusControls = do
 let field key value (J.JObject fields) = J.JObject [(name,if name==key then value else old) | (name,old)<-fields]
     field _ _ value = value
     selected = field "focusOwner" (J.JObject [("id",J.JString "7"),("generation",J.JString "3")])
     row ident dom enabled = J.JObject [("id",J.JString ident),("domId",J.JString dom),("enabled",J.JBool enabled),("focusOnly",J.JBool False)]
     frame pub token popup mode = field "frame" (J.JObject
       [("surfaceProtocol",J.JNumber "2"),("publication",J.JString (T.pack (show pub))),("lease",J.JString (T.pack (show token))),
        ("mode",J.JString mode),("bar",J.JArray [row "bar:applications" "owned-opener" True]),
        ("popup",J.JArray [row "control:search" "launcher-search" True])]) (selected (projection pub token popup))
     parse value = either (ioError . userError . T.unpack) pure (parseMvpFocusIntent value)
 closed <- parse (frame 1 0 False "menu")
 opened <- parse (frame 2 8 True "applications")
 typed <- parse (frame 3 8 True "applications")
 reopened <- parse (frame 4 9 True "applications")
 check "initial current Bar is keyboard focus destination" (maybe False ((==Just MvpFocusBar) . mvpFocusTransition Nothing) closed)
 check "current launcher opens into Popup widget" (maybe False ((==Just MvpFocusPopup) . mvpFocusTransition closed) opened)
 check "query publication does not refocus current popup" (maybe False ((==Nothing) . mvpFocusTransition opened) typed)
 check "new launcher lease is a new focus transition" (maybe False ((==Just MvpFocusPopup) . mvpFocusTransition opened) reopened)
 check "normal launcher dismissal restores Bar" (maybe False ((==Just MvpFocusBar) . mvpFocusTransition opened) closed)
 other <- parse (frame 5 10 True "settings")
 check "other popup policies are not inferred from scope" (other==Nothing)
 let disabled = field "frame" (J.JObject [("surfaceProtocol",J.JNumber "2"),("publication",J.JString "1"),("lease",J.JString "0"),("mode",J.JString "menu"),("bar",J.JArray [row "bar:applications" "owned-opener" False]),("popup",J.JArray [])]) (selected (projection 1 0 False))
 noTarget <- parse disabled
 check "disabled opener is not a restoration destination" (noTarget==Nothing)
 let duplicate = field "frame" (J.JObject [("surfaceProtocol",J.JNumber "2"),("publication",J.JString "2"),("lease",J.JString "8"),("mode",J.JString "applications"),("bar",J.JArray [row "bar:applications" "launcher-search" True]),("popup",J.JArray [row "control:search" "launcher-search" True])]) (selected (projection 2 8 True))
 check "ambiguous cross-renderer dom target refuses focus" (case parseMvpFocusIntent duplicate of Left _ -> True; _ -> False)
 let wrongOwner = field "popupOwner" (J.JObject [("id",J.JString "99"),("generation",J.JString "3")]) (frame 2 8 True "applications")
 check "foreign popup scope refuses physical focus" (case parseMvpFocusIntent wrongOwner of Left _ -> True; _ -> False)
 let noScope = field "views" (J.JArray []) (field "focusOwner" J.JNull (field "popupOwner" J.JNull (frame 1 0 False "menu")))
 absent <- parse noScope
 check "unscoped projection does not focus a widget" (absent==Nothing)
 unselected <- parse (field "focusOwner" J.JNull (frame 1 0 False "closed"))
 check "mapped scope without selected focus owner cannot take keyboard focus" (unselected==Nothing)

-- Notifications is a separate real popup keyboard destination.
notificationKeyboardFocusControls :: IO ()
notificationKeyboardFocusControls = do
 let field key value (J.JObject fields) = J.JObject [(name,if name==key then value else old) | (name,old)<-fields]
     field _ _ value = value
     selected = field "focusOwner" (J.JObject [("id",J.JString "7"),("generation",J.JString "3")])
     row ident dom enabled = J.JObject [("id",J.JString ident),("domId",J.JString dom),("enabled",J.JBool enabled),("focusOnly",J.JBool False)]
     frame pub token popup controls bar = field "frame" (J.JObject
       [("surfaceProtocol",J.JNumber "2"),("publication",J.JString (T.pack (show pub))),("lease",J.JString (T.pack (show token))),
        ("mode",J.JString (if popup then "notifications" else "closed")),("bar",J.JArray bar),
        ("popup",J.JArray controls)]) (selected (projection pub token popup))
     opener = row "bar:applications" "owned-opener" True
     close = row "control:close" "notifications-close" True
     parse value = either (ioError . userError . T.unpack) pure (parseMvpFocusIntent value)
     notifications pub token = frame pub token True [close] [opener]
 closed <- parse (frame 1 0 False [] [opener])
 opened <- parse (notifications 2 8)
 updated <- parse (notifications 3 8)
 reopened <- parse (notifications 4 9)
 check "notifications opening transfers keyboard focus into Popup" (maybe False ((==Just MvpFocusPopup) . mvpFocusTransition closed) opened)
 check "notifications same-lease publication preserves keyboard traversal" (maybe False ((==Nothing) . mvpFocusTransition opened) updated)
 check "notifications dismissal transfers keyboard focus back to Bar" (maybe False ((==Just MvpFocusBar) . mvpFocusTransition opened) closed)
 check "new notifications lease transfers Popup focus once" (maybe False ((==Just MvpFocusPopup) . mvpFocusTransition opened) reopened)
 disabled <- parse (frame 2 8 True [row "control:close" "notifications-close" False] [opener])
 check "disabled notifications close is not a keyboard destination" (disabled==Nothing)
 missing <- parse (frame 2 8 True [] [opener])
 check "missing notifications close does not invent a keyboard destination" (missing==Nothing)
 let duplicate = frame 2 8 True [close,close] [opener]
 check "duplicate notifications controls refuse keyboard focus" (case parseMvpFocusIntent duplicate of Left _ -> True; _ -> False)
 let crossRenderer = frame 2 8 True [close] [row "bar:applications" "notifications-close" True]
 check "notifications target cannot alias another renderer" (case parseMvpFocusIntent crossRenderer of Left _ -> True; _ -> False)
 let wrongOwner = field "popupOwner" (J.JObject [("id",J.JString "99"),("generation",J.JString "3")]) (notifications 2 8)
 check "foreign notifications scope refuses physical focus" (case parseMvpFocusIntent wrongOwner of Left _ -> True; _ -> False)
 let noSelection = field "focusOwner" J.JNull (notifications 2 8)
 unselected <- parse noSelection
 check "unselected notifications scope cannot take keyboard focus" (unselected==Nothing)

rendererPhaseControls :: IO ()
rendererPhaseControls = do
 let nonce = BS.replicate 64 'a'
 check "phase request exact64hex and LF" (rendererPhaseRequest (nonce <> BS.pack "\n")==Just (T.replicate 64 (T.pack "a")))
 forM_ [BS.empty,nonce,nonce <> BS.pack "\nextra",BS.replicate 64 'g' <> BS.pack "\n",BS.replicate 63 'a' <> BS.pack "\n"] $ \raw ->
  check "phase malformed or overbound request refuses" (rendererPhaseRequest raw==Nothing)
 check "phase sequence fixed first and last" (rendererPhaseLeaf 1==Just "01" && rendererPhaseLeaf 16==Just "16")
 forM_ [0,17,-1,maxBound] $ \number -> check "phase sequence outside fixed cap refuses" (rendererPhaseLeaf number==Nothing)
 let script = rendererPhaseSnapshotScript
 forM_ ["document.hasFocus()","document.activeElement","data-retained-query-state","http-popup-retained-query","data-publication","data-lease","data-surface-loading","control:search"] $ \literal ->
  check "phase reads existing DOM evidence" (BS.pack literal `BS.isInfixOf` script)
 forM_ [".focus(",".click(","dispatchEvent","setTimeout","setInterval","new Promise","fetch(","XMLHttpRequest","preventDefault"] $ \literal ->
  check "phase fixed script cannot input wait or consume HTTP" (not (BS.pack literal `BS.isInfixOf` script))

 check "phase actual ARM flags override generic directory/nofollow" (rendererPhaseFlags==(575488,559104,559297) && rendererPhaseFlags/=(722944,657408,657601))
 check "phase passive polling soft-skips exhausted reserve" (not (rendererPhasePolling 500000) && not (rendererPhasePolling 0) && rendererPhasePolling 500001)
 check "phase search uses actual Elm field attribute" (BS.pack "input[data-surface-field=\"control:search\"]" `BS.isInfixOf` rendererPhaseSnapshotScript && BS.pack "getAttribute('data-surface-field')" `BS.isInfixOf` rendererPhaseSnapshotScript)
 publicationLog <- newIORef ([] :: [String])
 publicationLive <- newIORef True
 let live = readIORef publicationLive >>= \ok -> unless ok (ioError (userError "original phase deadline"))
     recordStep name = modifyIORef' publicationLog (++[name])
 latePublication <- try (rendererPhasePublication live (recordStep "write" >> writeIORef publicationLive False) (recordStep "link") (recordStep "unlink") >> recordStep "complete") :: IO (Either IOException ())
 lateLog <- readIORef publicationLog
 check "phase write crossing original deadline never links or completes" (case latePublication of Left _ -> lateLog==["write"]; Right _ -> False)
 writeIORef publicationLog []
 writeIORef publicationLive True
 rendererPhasePublication live (recordStep "write") (recordStep "link") (recordStep "unlink")
 recordStep "complete"
 normalLog <- readIORef publicationLog
 check "phase normal publication retains fixed order" (normalLog==["write","link","unlink","complete"])

allocationControls :: IO ()
allocationControls = do
 rendererPhaseControls
 keyboardFocusControls
 notificationKeyboardFocusControls
 -- Fixed passive observation cannot generate or suppress the real input.
 let script = firstMouseupDiagnosticScript
 forM_ ["new Promise", "'mouseup'", "capture:true", "passive:true", "once:true", "isTrusted", "data-surface-control", "data-publication", "data-lease"] $ \literal ->
  check "fixed first-mouseup observation contract" (BS.pack literal `BS.isInfixOf` script)
 forM_ ["dispatchEvent", ".click(", "preventDefault", "setTimeout", "setInterval", "eval("] $ \literal ->
  check "diagnostic does not synthesize input or add timers" (not (BS.pack literal `BS.isInfixOf` script))
 let row route ordinal = J.JObject [("route",J.JString route),("ordinal",J.JNumber (T.pack (show ordinal))),("sha256",J.JString "redacted-digest-only")]
     keep rows = foldl (flip retainRequestTrace) [] rows
     eventRows = [row "Events" n | n <- [1..200 :: Int]]
     action = row "Actions" (0 :: Int)
     retained = keep (action:eventRows)
 check "polling cannot evict the preceding admitted Actions row" (action `elem` retained)
 check "trace stays64max with48poll rows" (length retained==49 && length (filter (/=action) retained)==48)
 check "latest poll chronology preserved" (retained==reverse (drop 152 eventRows)++[action])
 let mixed = [row (if even n then "Events" else "native-event") n | n <- [1..200 :: Int]]
     expected = reverse ([r | (n,r) <- zip [1..200 :: Int] mixed, (even n && n>=106) || (odd n && n>=169)])
 check "newest16nonevents and48events retain global order" (keep mixed==expected && length expected==64)
 check "identical redacted rows do not defeat trace cap" (length (keep (replicate 200 action))==16)
 -- Finite DPI policy uses actual metadata; it never forces valid user DPI.
 check "default DPI on zero-mm virtual monitor uses CSS nominal96" (finiteDpiFallbackSetting (-1) 1280 720 0 0==Just (96*1024))
 check "zero DPI on zero-mm virtual monitor gets finite fallback" (finiteDpiFallbackSetting 0 1280 720 0 0==Just (96*1024))
 forM_ [1,96*1024,192*1024] $ \setting ->
  check "positive configured DPI preserved even with zero-mm monitor" (finiteDpiFallbackSetting setting 1280 720 0 0==Nothing)
 forM_ [(340,190),(0,190),(340,0)] $ \(mmw,mmh) ->
  check "finite physical diagonal preserves automatic DPI" (finiteDpiFallbackSetting (-1) 1280 720 mmw mmh==Nothing)
 forM_ [(0,720),(1280,0),(-1,720)] $ \(w,h) ->
  check "unknown pixel geometry is not fabricated into monitor evidence" (finiteDpiFallbackSetting (-1) w h 0 0==Nothing)
 forM_ [(False,980,72),(True,0,72),(True,980,0),(True,-1,72)] $ \(mapped,w,h) ->
  check "renderer zero/unmapped child cannot issue a query" (not (rendererAllocationReady mapped w h))
 check "renderer positive mapped child permits query" (rendererAllocationReady True 980 72)
 captured <- either (ioError . userError . show) pure (rendererDiagnosticEnvelope 980 72 "123" "{\"status\":\"observed\",\"viewport\":[980,72]}")
 check "literal allocation timestamp and DOM preserved" (captured=="{\"gtkAllocation\":{\"mapped\":true,\"width\":980,\"height\":72,\"observedMonotonicNs\":\"123\"},\"dom\":{\"status\":\"observed\",\"viewport\":[980,72]}}")
 check "zero allocation envelope refused" (case rendererDiagnosticEnvelope 0 72 "123" "{}" of Left _ -> True; _ -> False)
 check "nonpositive monotonic observation refused" (case rendererDiagnosticEnvelope 980 72 "0" "{}" of Left _ -> True; _ -> False)
 check "malformed DOM JSON refused" (case rendererDiagnosticEnvelope 980 72 "123" "{" of Left _ -> True; _ -> False)
 check "nonobject DOM JSON refused" (case rendererDiagnosticEnvelope 980 72 "123" "[]" of Left _ -> True; _ -> False)
 large <- either (ioError . userError . show) pure (rendererDiagnosticEnvelope 980 72 "123" ("{\"text\":\"" <> T.replicate 8180 "a" <> "\"}"))
 check "overbound DOM omitted with allocation receipt retained" (T.isInfixOf "result-over-envelope-byte-bound" large && T.isInfixOf "observedMonotonicNs" large && not (T.isInfixOf (T.replicate 100 "a") large))
 putStrLn "allocation-controls: PASS"

main :: IO ()
main = do
 args <- getArgs
 case args of
  ["--allocation-only"] -> allocationControls
  [] -> ordinaryControls
  _ -> ioError (userError "expected no arguments or fixed --allocation-only")

ordinaryControls :: IO ()
ordinaryControls = do
 check "provider exact2.52.6 remains qualified" (providerVersionQualified (2,52,6))
 check "provider exact2.54.1 remains qualified" (providerVersionQualified (2,54,1))
 check "provider selected2.54.2 qualifies only exact tuple" (providerVersionQualified (2,54,2))
 check "provider nearby2.54.3 refused" (not (providerVersionQualified (2,54,3)))
 check "provider foreign major3.54.2 refused" (not (providerVersionQualified (3,54,2)))
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
