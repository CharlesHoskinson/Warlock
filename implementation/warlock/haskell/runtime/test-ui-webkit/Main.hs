{-# LANGUAGE ForeignFunctionInterface #-}
{-# LANGUAGE ScopedTypeVariables #-}
{-# LANGUAGE OverloadedStrings #-}
-- Real GObject signal lifecycle and isolated namespace guard controls. No GTK
-- display, WebKit page, original-scenario or GUI acceptance.
module Main (main) where

import Control.Exception (IOException, SomeException, displayException, try, finally, bracket, onException)
import Control.Concurrent (threadDelay)
import Control.Monad (foldM, forM_, unless)
import Data.IORef
import Data.Either (isLeft)
import qualified Warlock.Protocol.Identity as Identity
import qualified Warlock.Protocol.ForeignToplevel as FT
import qualified Warlock.Backend.ForeignToplevelOwner as ForeignOwner
import Warlock.Backend (DirectoryPin(..))
import Warlock.Platform.Resolver (Identity(..))
import qualified System.Posix.Files as EndpointFiles
import Data.Bits ((.&.))
import qualified Data.Text as T
import qualified Data.ByteString.Char8 as BS
import qualified Data.ByteString as B
import qualified Data.Text.Encoding as TE
import qualified Crypto.Hash.SHA256 as SHA256
import qualified Warlock.Platform.Resolver as Resolver
import qualified System.Posix.IO as PosixIO
import System.Posix.Types (Fd(..))
import System.Posix.User (getEffectiveUserID)
import System.Timeout (timeout)
import qualified Warlock.Backend as ConnectedBackend
import qualified Warlock.Bootstrap as ConnectedBootstrap
import qualified Warlock.Capture.Process.Bootstrap as ConnectedProcess
import qualified Warlock.Protocol.Desktop as ConnectedDesktop
import Numeric (showHex)
import Warlock.Ui.Owner (retainRequestTrace)
import qualified Warlock.Protocol.StrictJson as J
import Warlock.Protocol.Identity (renderCounter)
import Warlock.Ui.Mvp (MvpFocusRole(..), parseMvpFocusIntent, mvpFocusTransition, leaseScope, leaseRevision, leasePublication, leaseToken, leasePopupOpen)
import Foreign.C.String (CString, withCString)
import Foreign.C.Types (CInt(..))
import Foreign.Ptr (FunPtr, Ptr, castFunPtr, freeHaskellFunPtr, nullPtr)
import System.Exit (ExitCode(..))
import System.Environment (getArgs, getEnv)
import System.IO (hFlush, stdout, stdin, hClose, hGetChar, hIsEOF, openBinaryTempFile)
import System.Directory (removeFile)
import System.FilePath (takeFileName)
import System.IO.Error (ioeGetErrorString)
import System.Posix.Process (ProcessStatus(..), exitImmediately, forkProcess, getProcessStatus)
import System.Posix.Signals (sigKILL, signalProcess)
import Warlock.Capture.Process.Bootstrap (AdmissionDeadline, deadlineAfter, deadlineFromAbsoluteNs, remainingMicros)
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


-- Menu handoff is origin-sensitive; DOM target selection stays with Elm.
menuKeyboardFocusControls :: IO ()
menuKeyboardFocusControls = do
 let replace key value (J.JObject fields) = J.JObject [(name,if name==key then value else oldValue) | (name,oldValue)<-fields]
     replace _ _ value = value
     selected = replace "focusOwner" (J.JObject [("id",J.JString "7"),("generation",J.JString "3")])
     row ident dom enabled = J.JObject [("id",J.JString ident),("domId",J.JString dom),("enabled",J.JBool enabled),("focusOnly",J.JBool False)]
     frame pub token popup keyboard controls bar = replace "frame" (J.JObject
       ([("surfaceProtocol",J.JNumber "2"),("publication",J.JString (T.pack (show pub))),("lease",J.JString (T.pack (show token)))
        ,("mode",J.JString (if popup then "menu" else "closed")),("bar",J.JArray bar),("popup",J.JArray controls)]
        ++ maybe [] (\value -> [("keyboardParent",J.JBool value)]) keyboard)) (selected (projection pub token popup))
     opener = row "bar:applications" "owned-opener" True
     menuClose = row "control:menu-close" "menu:1:close" True
     parse value = either (ioError . userError . T.unpack) pure (parseMvpFocusIntent value)
     menu pub token = frame pub token True (Just True) [menuClose] [opener]
     goesPopup = maybe False ((==Just MvpFocusPopup) . mvpFocusTransition Nothing)
     refused value = case parseMvpFocusIntent value of Left _ -> True; _ -> False
 closed <- parse (frame 1 0 False Nothing [] [opener])
 opened <- parse (menu 2 8)
 updated <- parse (menu 3 8)
 reopened <- parse (menu 4 9)
 check "keyboard menu opening transfers physical focus into Popup" (maybe False ((==Just MvpFocusPopup) . mvpFocusTransition closed) opened)
 check "same menu lease publication does not steal traversal" (maybe False ((==Nothing) . mvpFocusTransition opened) updated)
 check "new keyboard menu lease is one physical transition" (maybe False ((==Just MvpFocusPopup) . mvpFocusTransition opened) reopened)
 check "menu dismissal restores only physical Bar role" (maybe False ((==Just MvpFocusBar) . mvpFocusTransition opened) closed)
 pointer <- parse (frame 2 8 True (Just False) [menuClose] [opener])
 unknownOrigin <- parse (frame 2 8 True Nothing [menuClose] [opener])
 check "pointer menu cannot steal physical keyboard focus" (pointer==Nothing)
 check "menu without keyboard-origin witness stays inert" (unknownOrigin==Nothing)
 disabled <- parse (frame 2 8 True (Just True) [row "control:menu-close" "menu:1:close" False] [opener])
 missing <- parse (frame 2 8 True (Just True) [] [opener])
 check "disabled menu close cannot authorize focus" (disabled==Nothing)
 check "missing menu close cannot authorize focus" (missing==Nothing)
 check "duplicate menu close ids refuse" (refused (frame 2 8 True (Just True) [menuClose,menuClose] [opener]))
 check "cross-renderer menu DOM alias refuses" (refused (frame 2 8 True (Just True) [menuClose] [row "bar:applications" "menu:1:close" True]))
 check "foreign menu popup owner refuses" (refused (replace "popupOwner" (J.JObject [("id",J.JString "99"),("generation",J.JString "3")]) (menu 2 8)))
 unselected <- parse (replace "focusOwner" J.JNull (menu 2 8))
 check "unselected menu cannot take physical focus" (unselected==Nothing)
 unscoped <- parse (replace "views" (J.JArray []) (replace "focusOwner" J.JNull (replace "popupOwner" J.JNull (frame 1 0 False Nothing [] [opener]))))
 check "unscoped menu state remains inert" (unscoped==Nothing)
 -- Fixed reproducible source-only matrix, four predicates repeated at fresh counters.
 forM_ [0..31 :: Int] $ \seed -> do
  let pub = fromIntegral seed + 10
      token = fromIntegral seed + 1
      variant = seed `mod` 4
      candidate = case variant of
       0 -> menu pub token
       1 -> frame pub token True (Just False) [menuClose] [opener]
       2 -> frame pub token True (Just True) [row "control:menu-close" "menu:1:close" False] [opener]
       _ -> replace "popupOwner" (J.JObject [("id",J.JString "99"),("generation",J.JString "3")]) (menu pub token)
      accepted = case parseMvpFocusIntent candidate of
       Left _ -> variant==3
       Right intent -> if variant==0 then goesPopup intent else variant/=3 && intent==Nothing
  check ("menu physical-focus seeded case " ++ show seed) accepted

allocationControls :: IO ()
allocationControls = do
 rendererPhaseControls
 keyboardFocusControls
 notificationKeyboardFocusControls
 menuKeyboardFocusControls
 foreignToplevelControls
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
  ["--foreign-endpoint-refusal-only"] -> foreignEndpointAdmissionControls
  ["--foreign-endpoint-observe-only",path,digest] -> foreignEndpointObservationControls path digest
  ["--foreign-endpoint-window-producer",path,digest] -> foreignEndpointWindowProducer path digest
  [] -> ordinaryControls
  _ -> ioError (userError "expected fixed ordinary, allocation, endpoint-refusal, connected-observer or window-producer arguments")

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

-- Standard v3 protocol events only; no display, IPC, backend or native effect.
foreignToplevelControls :: IO ()
foreignToplevelControls = do
 let checked value = either (ioError . userError . show) pure value
 generation <- checked (Identity.parseCounter False "1")
 otherGeneration <- checked (Identity.parseCounter False "2")
 empty <- checked (FT.newOwner generation)
 (withOutput,output) <- checked (FT.addOutput 10 empty)
 (created,handle) <- checked (FT.addToplevel 20 withOutput)
 let apply events state = foldM (flip FT.applyEvent) state events
     initial = [FT.Title handle "Document",FT.AppId handle "documents",FT.States handle [2],FT.OutputEnter handle output]
     onlyRow state = FT.snapshot state >>= \view -> case FT.toplevels view of
       [value] -> Right value
       _ -> Left FT.Incomplete
 staged <- checked (apply initial created)
 committed <- checked (FT.applyEvent (FT.Done handle) staged)
 row <- checked (onlyRow committed)
 check "foreign toplevel remains absent before done" (fmap FT.toplevels (FT.snapshot staged)==Right [])
 check "foreign toplevel done publishes exact title/app/state/output" (FT.toplevelTitle row=="Document" && FT.toplevelAppId row=="documents" && FT.toplevelStates row==[FT.Activated] && FT.toplevelOutputs row==[output] && FT.toplevelParent row==Nothing)
 check "foreign toplevel incomplete initial done refuses" (isLeft (FT.applyEvent (FT.Done handle) created))
 pending <- checked (FT.applyEvent (FT.Title handle "Renamed") committed)
 check "foreign toplevel later pending title is not published" (fmap FT.toplevelTitle (onlyRow pending)==Right "Document")
 renamed <- checked (FT.applyEvent (FT.Done handle) pending)
 check "foreign toplevel later done publishes new title" (fmap FT.toplevelTitle (onlyRow renamed)==Right "Renamed")
 check "foreign toplevel duplicate active wire id refuses" (isLeft (FT.addToplevel 20 committed))
 check "foreign toplevel zero wire id refuses" (isLeft (FT.addToplevel 0 committed))
 check "foreign toplevel unknown state refuses" (isLeft (FT.applyEvent (FT.States handle [4]) committed))
 check "foreign toplevel duplicate state refuses" (isLeft (FT.applyEvent (FT.States handle [1,1]) committed))
 check "foreign toplevel UTF16 bound refuses astral overflow" (isLeft (FT.applyEvent (FT.Title handle (T.replicate 129 "😀")) committed))
 check "foreign toplevel C0 text refuses" (isLeft (FT.applyEvent (FT.AppId handle "bad\n") committed))
 check "foreign toplevel empty title remains truthful" (not (isLeft (FT.applyEvent (FT.Title handle "") committed)))
 check "foreign toplevel duplicate output enter refuses" (isLeft (FT.applyEvent (FT.OutputEnter handle output) committed))
 left <- checked (FT.applyEvent (FT.OutputLeave handle output) committed)
 check "foreign toplevel output leave waits for done" (fmap FT.toplevelOutputs (onlyRow left)==Right [output])
 leftDone <- checked (FT.applyEvent (FT.Done handle) left)
 check "foreign toplevel no outputs does not fabricate visibility" (fmap FT.toplevelOutputs (onlyRow leftDone)==Right [])
 check "foreign toplevel unmatched output leave refuses" (isLeft (FT.applyEvent (FT.OutputLeave handle output) leftDone))
 other <- checked (FT.newOwner otherGeneration)
 (_,foreignHandle) <- checked (FT.addToplevel 20 other)
 (_,foreignOutput) <- checked (FT.addOutput 10 other)
 check "foreign toplevel wrong owner event refuses" (isLeft (FT.applyEvent (FT.Title foreignHandle "Other") committed))
 check "foreign toplevel wrong owner output refuses" (isLeft (FT.applyEvent (FT.OutputEnter handle foreignOutput) committed))
 check "foreign toplevel wrong owner parent refuses" (isLeft (FT.applyEvent (FT.Parent handle (Just foreignHandle)) committed))
 closed <- checked (FT.applyEvent (FT.Closed handle) committed)
 check "foreign toplevel closed removes committed row" (fmap FT.toplevels (FT.snapshot closed)==Right [])
 check "foreign toplevel closed callback refuses" (isLeft (FT.applyEvent (FT.Title handle "Late") closed))
 (reused,replacement) <- checked (FT.addToplevel 20 closed)
 check "foreign toplevel reused wire gets new incarnation" (replacement/=handle)
 check "foreign toplevel old token cannot mutate replacement" (isLeft (FT.applyEvent (FT.Done handle) reused))
 removed <- checked (FT.removeOutput output committed)
 check "foreign toplevel retired output removed from snapshots" (fmap FT.toplevelOutputs (onlyRow removed)==Right [])
 (outputReused,newOutput) <- checked (FT.addOutput 10 removed)
 check "foreign toplevel output reuse changes identity" (newOutput/=output)
 check "foreign toplevel stale output token refuses" (isLeft (FT.applyEvent (FT.OutputEnter handle output) outputReused))
 (two,child) <- checked (FT.addToplevel 21 committed)
 childPending <- checked (apply [FT.Title child "Child",FT.AppId child "documents",FT.States child [],FT.Parent child (Just handle)] two)
 childDone <- checked (FT.applyEvent (FT.Done child) childPending)
 check "foreign toplevel current parent survives commit" (fmap (map FT.toplevelParent . FT.toplevels) (FT.snapshot childDone)==Right [Nothing,Just handle])
 cyclePending <- checked (FT.applyEvent (FT.Parent handle (Just child)) childDone)
 cycleDone <- checked (FT.applyEvent (FT.Done handle) cyclePending)
 check "foreign toplevel parent cycle cannot publish snapshot" (isLeft (FT.snapshot cycleDone))
 parentClosed <- checked (FT.applyEvent (FT.Closed handle) childDone)
 check "foreign toplevel stale committed parent cannot publish snapshot" (isLeft (FT.snapshot parentClosed))
 repaired <- checked (apply [FT.Parent child Nothing,FT.Done child] parentClosed)
 check "foreign toplevel actual parent-null event repairs current graph" (fmap (map FT.toplevelParent . FT.toplevels) (FT.snapshot repaired)==Right [Nothing])
 finished <- checked (FT.applyEvent FT.ManagerFinished committed)
 check "foreign toplevel manager finished prevents publication" (isLeft (FT.snapshot finished))
 check "foreign toplevel manager finished prevents new handles" (isLeft (FT.addToplevel 30 finished))
 check "foreign toplevel manager finished prevents callbacks" (isLeft (FT.applyEvent (FT.Done handle) finished))
 full <- checked (foldM (\state wire -> fmap fst (FT.addToplevel wire state)) empty [1..256])
 check "foreign toplevel live row bound refuses 257th" (isLeft (FT.addToplevel 257 full))
 forM_ [0..31 :: Int] $ \seed -> do
   let label="Seed "<>T.pack (show seed)
   draft <- checked (FT.applyEvent (FT.Title handle label) committed)
   check ("foreign toplevel seed pending "<>show seed) (fmap FT.toplevelTitle (onlyRow draft)==Right "Document")
   if even seed then do
     done <- checked (FT.applyEvent (FT.Done handle) draft)
     check ("foreign toplevel seed done "<>show seed) (fmap FT.toplevelTitle (onlyRow done)==Right label)
   else do
     retired <- checked (FT.applyEvent (FT.Closed handle) draft)
     check ("foreign toplevel seed closed "<>show seed) (isLeft (FT.applyEvent (FT.Done handle) retired) && fmap FT.toplevels (FT.snapshot retired)==Right [])


-- CPU IO controls, not pure accumulator or provider/GTK controls. Invalid
-- selections below fail before socket creation/connect. The root-only cases
-- open/read/close actual directory FDs; none creates a display or a socket.
foreignEndpointAdmissionControls :: IO ()
foreignEndpointAdmissionControls = do
 deadlineText <- getEnv "WARLOCK_FOREIGN_ENDPOINT_DEADLINE_NS"
 deadline <- deadlineFromAbsoluteNs deadlineText >>= either (ioError . userError . show) pure
 initialRemaining <- remainingMicros deadline
 check "endpoint CPU deadline is inherited and clipped to five seconds" (initialRemaining>0 && initialRemaining<=5000000)
 connectedExecutableDigestControls deadline
 generation <- either (ioError . userError . show) pure (Identity.parseCounter False "1")
 rootStatus <- EndpointFiles.getSymbolicLinkStatus "/"
 let rootDevice=toInteger (EndpointFiles.deviceID rootStatus)
     rootInode=toInteger (EndpointFiles.fileID rootStatus)
     rootUid=toInteger (EndpointFiles.fileOwner rootStatus)
     rootMode=toInteger (EndpointFiles.fileMode rootStatus .&. 0o7777)
     rootPin=ForeignOwner.AncestorPin (DirectoryPin "/" rootDevice rootInode) rootUid rootMode
     base=ForeignOwner.EndpointSelection
       { ForeignOwner.endpointBootId="00000000-0000-0000-0000-000000000000"
       , ForeignOwner.endpointDirectory=[]
       , ForeignOwner.endpointName="never-connected"
       , ForeignOwner.endpointSocketIdentity=Identity 0 0
       , ForeignOwner.endpointSocketUid=rootUid
       , ForeignOwner.endpointSocketMode=0o600
       , ForeignOwner.endpointProcesses=[]
       , ForeignOwner.endpointExecutable=ForeignOwner.ExecutablePin (Identity 0 0) [] "never-read" [] 0 ""
       , ForeignOwner.endpointGeneration=generation
       }
     one pin=base {ForeignOwner.endpointDirectory=[pin]}
     alteredRoot uid mode=ForeignOwner.AncestorPin (DirectoryPin "/" rootDevice rootInode) uid mode
     named value=base {ForeignOwner.endpointDirectory=[rootPin],ForeignOwner.endpointName=value}
     refused name fragment selection=do
       entered <- newIORef False
       result <- ForeignOwner.withForeignToplevelOwner selection deadline (\_ -> writeIORef entered True)
       called <- readIORef entered
       check (name++": callback never entered") (not called)
       case result of
        ForeignOwner.ObservationResult (Left problem) ForeignOwner.Retired ->
         check (name++": exact pre-connect refusal and confirmed cleanup")
           (T.pack fragment `T.isInfixOf` T.pack (displayException problem))
        _ -> check (name++": refusal must retire all acquired resources") False
 check "endpoint CPU setup uses actual safe root directory" (EndpointFiles.isDirectory rootStatus && rootMode .&. 0o022==0)
 refused "endpoint-empty-ancestors" "ancestor bound" base
 refused "endpoint-ancestor-count" "ancestor bound" (base {ForeignOwner.endpointDirectory=replicate 65 rootPin})
 refused "endpoint-root-not-first" "unsafe ancestor selection"
   (one (ForeignOwner.AncestorPin (DirectoryPin "/not-the-root" rootDevice rootInode) rootUid rootMode))
 refused "endpoint-negative-uid" "unsafe ancestor selection" (one (alteredRoot (-1) rootMode))
 refused "endpoint-negative-mode" "unsafe ancestor selection" (one (alteredRoot rootUid (-1)))
 refused "endpoint-mode-range" "unsafe ancestor selection" (one (alteredRoot rootUid 0o10000))
 refused "endpoint-group-write" "unsafe ancestor selection" (one (alteredRoot rootUid 0o775))
 refused "endpoint-other-write" "unsafe ancestor selection" (one (alteredRoot rootUid 0o757))
 refused "endpoint-held-root-mismatch" "ancestor changed"
   (one (ForeignOwner.AncestorPin (DirectoryPin "/" rootDevice 0) rootUid rootMode))
 refused "endpoint-noncontiguous-chain" "ancestor chain differs"
   (base {ForeignOwner.endpointDirectory=[rootPin,ForeignOwner.AncestorPin (DirectoryPin "/not/contiguous" 0 0) rootUid rootMode]})
 forM_ [("empty",""),("slash","wayland/1"),("dot","."),("dotdot","..")
       ,("overlong",replicate 65 'w'),("nul","wayland\0x"),("non-ascii","wayland\233")] $ \(name,value) ->
   refused ("endpoint-socket-name-"++name) "socket name refused" (named value)
 -- Literal reproducible seeds exercise different invalid names, never a
 -- guessed valid endpoint. Successful retirement is the positive witness.
 forM_ ([0..31] :: [Int]) $ \seed -> do
  let sample=(toInteger seed*1103515245+12345) `mod` 2147483648
      value=case sample `mod` 4 of
       0 -> "x/"++show sample
       1 -> "x\0"++show sample
       2 -> replicate (65+fromInteger (sample `mod` 16)) 'w'
       _ -> "x\233"++show sample
  refused ("endpoint-invalid-name-seed-"++show seed) "socket name refused" (named value)
 -- Expire the SAME inherited deadline, rather than making a fresh deadline
 -- per attempt. No display or callback dispatcher can be created after it.
 let awaitExpiry=do
      left <- remainingMicros deadline
      if left==0 then pure () else threadDelay left >> awaitExpiry
 awaitExpiry
 entered <- newIORef False
 result <- ForeignOwner.withForeignToplevelOwner base deadline (\_ -> writeIORef entered True)
 called <- readIORef entered
 check "expired endpoint never enters user callback" (not called)
 case result of
  ForeignOwner.ObservationResult (Left _) (ForeignOwner.Retained owner) -> do
   retried <- try (ForeignOwner.readToplevelSnapshot owner) :: IO (Either SomeException FT.Snapshot)
   check "expired retained owner refuses observation reuse" (isLeft retried)
  _ -> check "expired deadline cannot claim confirmed retirement" False
 putStrLn "foreign-endpoint-admission-cpu:17-refusals;32-seeds;expired-retained;no-connect"


-- Fixed native qualification entrypoint. These operations connect to the one
-- parent-selected private compositor; they are NOT allocation/CPU controls.
-- The pipe carries only a four-step schedule, never observation data or code.
data ConnectedConfiguration = ConnectedConfiguration T.Text Identity.Binding String ForeignOwner.EndpointSelection

connectedObject :: [T.Text] -> J.Json -> Either String [(T.Text,J.Json)]
connectedObject keys = either (Left . show) Right . J.exactObject keys
connectedField :: T.Text -> [(T.Text,J.Json)] -> Either String J.Json
connectedField key fields = maybe (Left "missing connected field") Right (lookup key fields)
connectedText :: J.Json -> Either String T.Text
connectedText (J.JString value) = Right value
connectedText _ = Left "connected string required"
connectedNatural :: J.Json -> Either String Integer
connectedNatural value = do
 text <- connectedText value
 _ <- either (Left . show) Right (Identity.parseCounter True text)
 pure (read (T.unpack text))
connectedCounter :: J.Json -> Either String Identity.Counter
connectedCounter value = connectedText value >>= either (Left . show) Right . Identity.parseCounter False
connectedList :: Int -> (J.Json -> Either String a) -> J.Json -> Either String [a]
connectedList limit decode (J.JArray values)
 | length values<=limit = mapM decode values
 | otherwise = Left "connected array bound"
connectedList _ _ _ = Left "connected array required"
connectedCheck :: Bool -> String -> Either String ()
connectedCheck good label = if good then Right () else Left label
connectedDigest :: T.Text -> Either String BS.ByteString
connectedDigest value = do
 connectedCheck (T.length value==64 && T.all (\c -> c>='0' && c<='9' || c>='a' && c<='f') value) "canonical SHA256 required"
 let digit c=if c<='9' then fromEnum c-fromEnum '0' else 10+fromEnum c-fromEnum 'a'
     pairs []=[]
     pairs (a:b:rest)=fromIntegral (digit a*16+digit b):pairs rest
     pairs _=[]
 pure (B.pack (pairs (T.unpack value)))
connectedBinding :: J.Json -> Either String Identity.Binding
connectedBinding value = do
 fields <- connectedObject ["lifetime","session","frontend"] value
 life <- connectedField "lifetime" fields >>= connectedCounter
 sess <- connectedField "session" fields >>= connectedCounter
 front <- connectedField "frontend" fields >>= connectedCounter
 either (Left . show) Right (Identity.binding life sess front)
connectedIdentity :: J.Json -> Either String Identity
connectedIdentity value = do
 fields <- connectedObject ["device","inode"] value
 Identity <$> (connectedField "device" fields >>= connectedNatural) <*> (connectedField "inode" fields >>= connectedNatural)
connectedAncestor :: J.Json -> Either String ForeignOwner.AncestorPin
connectedAncestor value = do
 fields <- connectedObject ["path","device","inode","uid","mode"] value
 path <- connectedField "path" fields >>= connectedText
 dev <- connectedField "device" fields >>= connectedNatural
 ino <- connectedField "inode" fields >>= connectedNatural
 uid <- connectedField "uid" fields >>= connectedNatural
 mode <- connectedField "mode" fields >>= connectedNatural
 connectedCheck (T.length path<=4096 && T.isPrefixOf "/" path && not (T.any (=='\0') path) && mode<=4095) "ancestor syntax"
 pure (ForeignOwner.AncestorPin (DirectoryPin (T.unpack path) dev ino) uid mode)
connectedProcess :: J.Json -> Either String ForeignOwner.ProcessPin
connectedProcess value = do
 fields <- connectedObject ["pid","birth","parent","uid","gid"] value
 pid <- connectedField "pid" fields >>= connectedNatural
 birth <- connectedField "birth" fields >>= connectedNatural
 parent <- connectedField "parent" fields >>= connectedNatural
 uid <- connectedField "uid" fields >>= connectedNatural
 gid <- connectedField "gid" fields >>= connectedNatural
 connectedCheck (pid>0 && birth>0) "process identity required"
 pure (ForeignOwner.ProcessPin pid birth parent uid gid)
connectedPin :: J.Json -> Either String Resolver.Pin
connectedPin value = do
 fields <- connectedObject ["path","device","inode","kind"] value
 path <- connectedField "path" fields >>= connectedText
 dev <- connectedField "device" fields >>= connectedNatural
 ino <- connectedField "inode" fields >>= connectedNatural
 kind <- connectedField "kind" fields >>= connectedText
 selected <- case kind of
  "directory" -> Right Resolver.Directory
  "regular" -> Right Resolver.Regular
  _ -> Left "no executable symlink or unknown kind admitted"
 connectedCheck (T.length path<=4096 && T.isPrefixOf "/" path && not (T.any (=='\0') path)) "executable pin path"
 pure (Resolver.Pin (TE.encodeUtf8 path) (Identity dev ino) selected)
connectedExecutable :: J.Json -> Either String ForeignOwner.ExecutablePin
connectedExecutable value = do
 fields <- connectedObject ["root","pins","path","size","sha256"] value
 root <- connectedField "root" fields >>= connectedIdentity
 pins <- connectedField "pins" fields >>= connectedList 64 connectedPin
 path <- connectedField "path" fields >>= connectedText
 size <- connectedField "size" fields >>= connectedNatural
 digestText <- connectedField "sha256" fields >>= connectedText
 _ <- connectedDigest digestText
 let digest = TE.encodeUtf8 digestText
 connectedCheck (not (null pins) && size>0 && size<=67108864 && not (T.null path) && T.length path<=4096 && not (T.isPrefixOf "/" path) && not (T.any (=='\0') path) && all (\part -> part/="" && part/="." && part/="..") (T.splitOn "/" path)) "selected executable bounds"
 pure (ForeignOwner.ExecutablePin root pins (TE.encodeUtf8 path) [] size digest)
connectedConfiguration :: String -> J.Json -> Either String ConnectedConfiguration
connectedConfiguration inherited value = do
 fields <- connectedObject ["schema","nonce","binding","deadlineMonotonicNs","endpoint"] value
 version <- connectedField "schema" fields
 connectedCheck (version==J.JNumber "1") "connected schema"
 nonce <- connectedField "nonce" fields >>= connectedText
 _ <- connectedDigest nonce
 bound <- connectedField "binding" fields >>= connectedBinding
 deadline <- connectedField "deadlineMonotonicNs" fields >>= connectedText
 _ <- either (Left . show) Right (Identity.parseCounter False deadline)
 connectedCheck (T.unpack deadline==inherited) "original absolute deadline differs"
 endpoint <- connectedField "endpoint" fields >>= connectedObject ["bootId","ancestors","name","socket","processes","executable","generation"]
 boot <- connectedField "bootId" endpoint >>= connectedText
 connectedCheck (T.length boot==36 && all (\i -> T.index boot i=='-') [8,13,18,23] && T.all (\c -> c=='-' || c>='0' && c<='9' || c>='a' && c<='f') boot) "boot UUID"
 ancestors <- connectedField "ancestors" endpoint >>= connectedList 64 connectedAncestor
 name <- connectedField "name" endpoint >>= connectedText
 connectedCheck (not (null ancestors) && not (T.null name) && T.length name<=64 && name/="." && name/=".." && T.all (\c -> c>='a' && c<='z' || c>='A' && c<='Z' || c>='0' && c<='9' || c=='-' || c=='_' || c=='.') name) "selected socket name"
 socket <- connectedField "socket" endpoint >>= connectedObject ["device","inode","uid","mode"]
 dev <- connectedField "device" socket >>= connectedNatural
 ino <- connectedField "inode" socket >>= connectedNatural
 uid <- connectedField "uid" socket >>= connectedNatural
 mode <- connectedField "mode" socket >>= connectedNatural
 connectedCheck (ino>0 && mode<=4095) "selected socket identity"
 processes <- connectedField "processes" endpoint >>= connectedList 32 connectedProcess
 connectedCheck (not (null processes)) "selected peer process required"
 executable <- connectedField "executable" endpoint >>= connectedExecutable
 generation <- connectedField "generation" endpoint >>= connectedCounter
 connectedCheck (generation==Identity.frontend bound) "owner generation must match actual full binding frontend"
 pure (ConnectedConfiguration nonce bound (T.unpack deadline) (ForeignOwner.EndpointSelection (TE.encodeUtf8 boot) ancestors (T.unpack name) (Identity dev ino) uid mode processes executable generation))

-- Installed AArch64 asm/fcntl.h overrides asm-generic O_NOFOLLOW to1<<15;
-- bits/fcntl.h independently declares0100000. Preserve NONBLOCK/CLOEXEC too.
-- The generic1<<17 value is LARGEFILE here and must not substitute NOFOLLOW.
foreign import ccall unsafe "open" connectedOpen :: CString -> CInt -> IO CInt
connectedOpenFlags :: CInt
connectedOpenFlags = 559104
connectedSafeConfigFlags :: CInt -> Bool
connectedSafeConfigFlags flags = flags .&. 32768==32768 && flags .&. 2048==2048
 && flags .&. 524288==524288 && flags .&. 131072==0
connectedWithin :: AdmissionDeadline -> IO a -> IO a
connectedWithin deadline operation = do
 left <- remainingMicros deadline
 check "connected original deadline exhausted" (left>0)
 outcome <- timeout left operation
 case outcome of
  Nothing -> ioError (userError "connected original deadline exhausted")
  Just value -> do
   after <- remainingMicros deadline
   check "connected operation crossed original deadline" (after>0)
   pure value
connectedReadConfig :: AdmissionDeadline -> FilePath -> T.Text -> IO J.Json
connectedReadConfig deadline path expected = connectedWithin deadline $ do
 digest <- either (ioError . userError) pure (connectedDigest expected)
 check "connected config path" (not (null path) && head path=='/' && length path<=4096 && '\0' `notElem` path)
 bracket (do
  raw <- withCString path (\name -> connectedOpen name connectedOpenFlags)
  check "connected config nofollow open" (raw>=0)
  pure (Fd raw)) PosixIO.closeFd $ \fd -> do
   before <- EndpointFiles.getFdStatus fd
   uid <- getEffectiveUserID
   check "connected config private regular bound" (EndpointFiles.isRegularFile before && EndpointFiles.fileOwner before==uid && EndpointFiles.fileMode before .&. 0o7777==0o600 && EndpointFiles.linkCount before==1 && EndpointFiles.fileSize before>0 && EndpointFiles.fileSize before<=65536)
   -- dup transfers only the duplicate into Handle ownership; original stays held.
   duplicate <- PosixIO.dup fd
   bracket (PosixIO.fdToHandle duplicate `onException` PosixIO.closeFd duplicate) hClose $ \handle -> do
    raw <- BS.hGet handle (fromIntegral (EndpointFiles.fileSize before)+1)
    after <- EndpointFiles.getFdStatus fd
    named <- EndpointFiles.getSymbolicLinkStatus path
    let stamp status=(EndpointFiles.deviceID status,EndpointFiles.fileID status,EndpointFiles.fileOwner status,EndpointFiles.fileMode status,EndpointFiles.fileSize status,EndpointFiles.linkCount status,EndpointFiles.modificationTimeHiRes status,EndpointFiles.statusChangeTimeHiRes status)
    check "connected config changed or SHA differs" (stamp before==stamp after && stamp after==stamp named && B.length raw==fromIntegral (EndpointFiles.fileSize before) && SHA256.hash raw==digest)
    limits <- either (ioError . userError . show) pure (J.bounds 65536 12)
    either (ioError . userError . show) pure (J.decodeStrict limits raw)
connectedReadCommand :: AdmissionDeadline -> String -> IO ()
connectedReadCommand deadline expected = connectedWithin deadline $ do
 let loop count reversed = do
      check "connected command byte bound" (count<13)
      char <- hGetChar stdin
      if char=='\n' then pure (reverse reversed) else do
       check "connected command ASCII" (char>='A' && char<='Z' || char=='_')
       loop (count+1) (char:reversed)
 actual <- loop (0::Int) []
 check "connected fixed phase order" (actual==expected)
connectedWrite :: AdmissionDeadline -> J.Json -> IO ()
connectedWrite deadline value = connectedWithin deadline $ do
 let bytes=TE.encodeUtf8 (J.renderJson value)<>"\n"
 check "connected response bound" (B.length bytes<=262144)
 BS.hPut stdout bytes
 hFlush stdout
connectedBindingJson :: Identity.Binding -> J.Json
connectedBindingJson bound = J.JObject [("lifetime",J.JString (Identity.renderCounter (Identity.lifetime bound))),("session",J.JString (Identity.renderCounter (Identity.session bound))),("frontend",J.JString (Identity.renderCounter (Identity.frontend bound)))]
connectedConfigControls :: String -> J.Json -> IO Int
connectedConfigControls deadline original = do
 check "actual ARM64 nofollow nonblock cloexec flags" (connectedSafeConfigFlags connectedOpenFlags)
 check "generic NOFOLLOW bit is not ARM64 NOFOLLOW" (not (connectedSafeConfigFlags 657408))
 let set key value (J.JObject fields)=J.JObject (map (\(name,old)->(name,if name==key then value else old)) fields)
     set _ _ other=other
     alterEndpoint fn (J.JObject fields)=J.JObject (map (\(name,value)->(name,if name=="endpoint" then fn value else value)) fields)
     alterEndpoint _ other=other
     cases=[set "schema" (J.JNumber "2") original,set "nonce" (J.JString "not-a-nonce") original
       ,set "deadlineMonotonicNs" (J.JString "1") original,set "binding" (J.JObject []) original
       ,alterEndpoint (set "generation" (J.JString "0")) original
       ,alterEndpoint (set "name" (J.JString "../wayland")) original
       ,alterEndpoint (set "ancestors" (J.JArray [])) original
       ,alterEndpoint (set "processes" (J.JArray [])) original
       ,alterEndpoint (set "socket" (J.JObject [])) original
       ,alterEndpoint (set "executable" (J.JObject [])) original
       ,alterEndpoint (set "bootId" (J.JString "bad")) original
       ,case original of J.JObject fields->J.JObject (fields++[("command",J.JString "forbidden")]);other->other]
 check "actual connected config decodes" (case connectedConfiguration deadline original of Right _->True;Left _->False)
 forM_ (zip [0::Int ..] cases) $ \(index,value) -> check ("connected config negative "++show index) (isLeft (connectedConfiguration deadline value))
 pure (length cases+3)

foreignEndpointObservationControls :: FilePath -> String -> IO ()
foreignEndpointObservationControls path suppliedSha = do
 inherited <- getEnv "WARLOCK_FOREIGN_ENDPOINT_DEADLINE_NS"
 deadline <- deadlineFromAbsoluteNs inherited >>= either (ioError . userError . show) pure
 initialRemaining <- remainingMicros deadline
 check "connected deadline must be inherited native28s" (initialRemaining>0 && initialRemaining<=28000000)
 raw <- connectedReadConfig deadline path (T.pack suppliedSha)
 configChecks <- connectedConfigControls inherited raw
 ConnectedConfiguration nonce bound _ selection <- either (ioError . userError) pure (connectedConfiguration inherited raw)
 completed <- newIORef (0::Int)
 outputTokens <- newIORef ([]::[FT.Output])
 let base sequenceNo phase = [("schema",J.JNumber "1"),("nonce",J.JString nonce),("sequence",J.JNumber (T.pack (show (sequenceNo::Int)))),("phase",J.JString phase),("binding",connectedBindingJson bound),("configChecks",J.JNumber (T.pack (show configChecks))),("nativeAcceptance",J.JBool False)]
     outputOrdinal token = do
      known <- readIORef outputTokens
      case lookup token (zip known [1::Int ..]) of
       Just ordinal -> pure ordinal
       Nothing -> do
        check "connected cumulative output report bound" (length known<4096)
        writeIORef outputTokens (known++[token])
        pure (length known+1)
     rowJson row = do
      outputs <- mapM outputOrdinal (FT.toplevelOutputs row)
      check "singleton has no external parent" (FT.toplevelParent row==Nothing)
      let state value=case value of FT.Maximized->"maximized";FT.Minimized->"minimized";FT.Activated->"activated";FT.Fullscreen->"fullscreen"
      pure (J.JObject [("handleOrdinal",J.JString "1"),("identityScope",J.JString "same-owner-QA-label-not-protocol-wire-id")
        ,("title",J.JString (FT.toplevelTitle row)),("appId",J.JString (FT.toplevelAppId row))
        ,("states",J.JArray (map (J.JString . state) (FT.toplevelStates row)))
        ,("outputOrdinals",J.JArray (map (J.JString . T.pack . show) outputs)),("parentOrdinal",J.JNull)])
     publish sequenceNo phase attempts rows = do
      values <- mapM rowJson rows
      connectedWrite deadline (J.JObject (base sequenceNo phase++[("readsPerformed",J.JNumber (T.pack (show (attempts::Int)))),("rows",J.JArray values)]))
      writeIORef completed sequenceNo
 result <- ForeignOwner.withForeignToplevelOwner selection deadline $ \owner -> do
  connectedReadCommand deadline "READ_INITIAL"
  initial <- ForeignOwner.readToplevelSnapshot owner
  check "actual initial committed snapshot not empty" (null (FT.toplevels initial))
  publish 1 "READ_INITIAL" 1 []
  connectedReadCommand deadline "READ_WINDOW"
  let awaitWindow count = do
       check "connected mapped snapshot read bound" (count<=16)
       observed <- ForeignOwner.readToplevelSnapshot owner
       case FT.toplevels observed of
        [row] -> pure (row,count)
        [] -> awaitWindow (count+1)
        _ -> ioError (userError "more than one actual committed window")
  (window,windowReads) <- awaitWindow (1::Int)
  publish 2 "READ_WINDOW" windowReads [window]
  connectedReadCommand deadline "READ_CLOSED"
  let awaitClosed count = do
       check "connected closed snapshot read bound" (count<=16)
       observed <- ForeignOwner.readToplevelSnapshot owner
       case FT.toplevels observed of
        [] -> pure count
        [row] | FT.toplevelHandle row==FT.toplevelHandle window -> awaitClosed (count+1)
        _ -> ioError (userError "observed window replaced during close")
  closedReads <- awaitClosed (1::Int)
  publish 3 "READ_CLOSED" closedReads []
  connectedReadCommand deadline "RETIRE"
  ended <- connectedWithin deadline (hIsEOF stdin)
  check "connected no fifth command" ended
  writeIORef completed 4
 actualCompleted <- readIORef completed
 let actionPassed=case result of
      ForeignOwner.ObservationResult (Right ()) _ -> True
      _ -> False
     retired=case result of
      ForeignOwner.ObservationResult _ ForeignOwner.Retired -> True
      _ -> False
     status=if retired then "Retired" else "RetainedUnknown"
     failure=case result of
      ForeignOwner.ObservationResult (Left problem) _ -> J.JString (T.pack (take 1024 (displayException problem)))
      _ -> J.JNull
 connectedWrite deadline (J.JObject (base 4 "RETIRE"++[("completedPhases",J.JNumber (T.pack (show actualCompleted))),("actionPassed",J.JBool actionPassed),("error",failure),("status",J.JString status),("passed",J.JBool (actionPassed && retired && actualCompleted==4))]))
 check "connected qualification incomplete or retained Unknown" (actionPassed && retired && actualCompleted==4)

-- Same public real Backend observer as fixture-ux003-native-observer/Main.hs,
-- linked into this fresh threaded test image. No fake GUI or attachment route.
connectedHex :: B.ByteString -> T.Text
connectedHex = T.pack . concatMap (\n -> let encoded=showHex n "" in if length encoded==1 then '0':encoded else encoded) . B.unpack
connectedJsonValue :: B.ByteString -> J.Json
connectedJsonValue raw = case J.bounds 1048576 20 of
 Left _ -> J.JNull
 Right limits -> either (const J.JNull) id (J.decodeStrict limits raw)
connectedDesktopJson :: ConnectedDesktop.DesktopReply -> J.Json
connectedDesktopJson reply = either (const J.JNull) connectedJsonValue (ConnectedDesktop.encodeDesktopReply reply)
connectedSelected :: ConnectedProcess.SelectedOutcome -> J.Json
connectedSelected result = J.JObject
 ([("exit",maybe J.JNull (J.JNumber . T.pack . show) (ConnectedProcess.selectedObservedExit result))
  ,("custody",J.JString (T.pack (show (ConnectedProcess.selectedCustody result))))
  ,("containment",J.JString (T.pack (show (ConnectedProcess.selectedContainment result))))]
  ++ case ConnectedProcess.selectedOperation result of
   Left _ -> [("stdoutHex",J.JNull),("stderrHex",J.JNull),("operationSucceeded",J.JBool False)]
   Right captured -> [("stdoutHex",J.JString (connectedHex (ConnectedProcess.output captured)))
                    ,("stderrHex",J.JString (connectedHex (ConnectedProcess.diagnostics captured)))
                    ,("operationSucceeded",J.JBool True)])
foreignEndpointWindowProducer :: FilePath -> String -> IO ()
foreignEndpointWindowProducer path suppliedSha = do
 inherited <- getEnv "WARLOCK_FOREIGN_ENDPOINT_DEADLINE_NS"
 deadline <- deadlineFromAbsoluteNs inherited >>= either (ioError . userError . show) pure
 left <- remainingMicros deadline
 check "producer inherits original native28s" (left>0 && left<=28000000)
 before <- connectedReadConfig deadline path (T.pack suppliedSha)
 let fields=case before of J.JObject values->values;_->[]
 check "producer config original deadline" (lookup "deadlineMonotonicNs" fields==Just (J.JString (T.pack inherited)))
 configured <- connectedWithin deadline (ConnectedBackend.loadBackendConfig path)
 after <- connectedReadConfig deadline path (T.pack suppliedSha)
 check "producer startup bytes changed across trusted decoder" (before==after)
 config <- either (const (ioError (userError "QA producer trusted startup refused"))) pure configured
 result <- ConnectedBackend.runBackend config
 let owner=case ConnectedBackend.backendBootstrap result of
      Right (ConnectedBootstrap.Executed outcome) -> case ConnectedProcess.selectedOperation outcome of
       Right captured | B.null (ConnectedProcess.diagnostics captured) -> connectedJsonValue (ConnectedProcess.output captured)
       _ -> J.JNull
      _ -> J.JNull
     app=case ConnectedBackend.backendApplicationReceipt result of
      Nothing -> J.JNull
      Just (request,outcome) -> case connectedSelected outcome of
       J.JObject values -> J.JObject (("request",J.JString (renderCounter request)):values)
       _ -> J.JNull
     published=maybe J.JNull connectedDesktopJson (ConnectedBackend.backendCatalogObservation result)
     launch=case ConnectedBackend.backendApplicationObservation result of
      Nothing -> J.JNull
      Just (intent,snapshot) -> J.JObject
       [("request",J.JString (renderCounter (ConnectedDesktop.launchRequest intent)))
       ,("lifetime",J.JString (renderCounter (ConnectedDesktop.launchLifetime intent)))
       ,("generation",J.JString (renderCounter (ConnectedDesktop.launchGeneration intent)))
       ,("entry",J.JString (ConnectedDesktop.launchEntry intent)),("catalog",maybe J.JNull connectedDesktopJson snapshot)]
     failure=case ConnectedBackend.backendBootstrap result of
      Left problem -> J.JString (T.take 4096 problem)
      Right _ -> J.JNull
     receipt=J.JObject
      [("schema",J.JNumber "1"),("kind",J.JString "ux003-backend-observation")
      ,("backend",connectedJsonValue (ConnectedBackend.backendResultJson result)),("bootstrapFailure",failure),("owner",owner)
      ,("application",app),("publishedCatalog",published),("publishedLaunch",launch)
      ,("nativeAcceptance",J.JBool False),("originalAcceptance",J.JBool False)]
 -- Preserve the incumbent observer's terminal reporting after Backend cleanup;
 -- parent custody bounds that cleanup/report by its existing originalD+2s.
 BS.putStrLn (TE.encodeUtf8 (J.renderJson receipt))
 check "actual Backend producer did not pass" (ConnectedBackend.backendPassed result)


-- Metadata/held-file CPU regression. No endpoint, socket or compositor is used.
-- The parser feeds the same public resolver/descriptor route as verifyExecutable.
connectedExecutableDigestControls :: AdmissionDeadline -> IO ()
connectedExecutableDigestControls deadline = connectedWithin deadline $ do
 let known = "ba7816bf8f01cfea414140de5dae2223b00361a396177a9cb410ff61f20015ad" :: T.Text
     content = "abc" :: BS.ByteString
     temporaryRoot = "/tmp"
 check "config digest remains the raw32 SHA256 known vector"
   (connectedDigest known==Right (SHA256.hash content) && B.length (SHA256.hash content)==32)
 bracket
   (do
     (file,writer) <- openBinaryTempFile temporaryRoot ".warlock-digest-adapter-"
     (do
       BS.hPut writer content
       hFlush writer
       hClose writer
       pure file)
       `onException` (hClose writer `finally` removeFile file))
   removeFile $ \file -> do
    rootStatus <- EndpointFiles.getSymbolicLinkStatus temporaryRoot
    fileStatus <- EndpointFiles.getSymbolicLinkStatus file
    let natural :: Show a => a -> J.Json
        natural = J.JString . T.pack . show
        rootJson = J.JObject [("device",natural (EndpointFiles.deviceID rootStatus)),("inode",natural (EndpointFiles.fileID rootStatus))]
        leaf = T.pack (takeFileName file)
        pinJson = J.JObject [("path",J.JString ("/"<>leaf)),("device",natural (EndpointFiles.deviceID fileStatus)),("inode",natural (EndpointFiles.fileID fileStatus)),("kind",J.JString "regular")]
        executableJson encoded = J.JObject [("root",rootJson),("pins",J.JArray [pinJson]),("path",J.JString leaf),("size",J.JString "3"),("sha256",J.JString encoded)]
    check "executable digest rejects uppercase hex" (isLeft (connectedExecutable (executableJson (T.toUpper known))))
    check "executable digest rejects short hex" (isLeft (connectedExecutable (executableJson (T.drop 1 known))))
    check "executable digest rejects nonhex text" (isLeft (connectedExecutable (executableJson ("g"<>T.drop 1 known))))
    selected <- either (ioError . userError) pure (connectedExecutable (executableJson known))
    case selected of
     ForeignOwner.ExecutablePin rootIdentity pins path links size expected -> do
      check "executable parser supplies validated ASCII64 descriptor digest"
        (expected==TE.encodeUtf8 known && B.length expected==64)
      observed <- Resolver.withRoot (BS.pack temporaryRoot) rootIdentity $ \root -> do
       accepted <- Resolver.resolveSnapshot root pins path links size 3 expected
       rawRejected <- Resolver.resolveSnapshot root pins path links size 3 (SHA256.hash content)
       pure (accepted,rawRejected)
      case observed of
       Right (Right (resolution,bytes),Left rejected) -> do
        check "parsed executable known vector passes actual held descriptor"
          (bytes==content && Resolver.resolvedIdentity resolution==Identity (toInteger (EndpointFiles.deviceID fileStatus)) (toInteger (EndpointFiles.fileID fileStatus)))
        check "raw32 counterexample fails actual held descriptor with DigestMismatch"
          (show rejected=="FileFailure DigestMismatch")
       _ -> check ("parser and held descriptor digest contracts must agree: "++take 1024 (show observed)) False
