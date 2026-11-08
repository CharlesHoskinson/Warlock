{-# LANGUAGE OverloadedStrings #-}
{-# LANGUAGE ForeignFunctionInterface #-}
{-# LANGUAGE ScopedTypeVariables #-}
-- WebKitGTK 6 boundary; no page loads before its role filter is installed.
module Warlock.Ui.WebKit
  (firstMouseupDiagnosticScript, finiteDpiFallbackSetting, rendererAllocationReady, rendererDiagnosticEnvelope, providerVersionQualified, runWebKitObservedWithBacking, runWebKitObserved, runWebKit, runWebKitWithCustody, requireThreadCompatibleNamespace, DecisionHandler, newDecisionHandler, freeDecisionHandler, connectOwnedSignal, SignalDisconnectObservation, connectOwnedSignalObserved, signalDisconnectReturned, signalRetirementConfirmed, withOwnedDefaultContext, retireInOrder, readMvpLease, handleMvpDispatch) where

import Control.Exception (SomeException, SomeAsyncException, fromException, throwIO, catch, mask_, mask, onException, try, finally, bracket, toException)
import Control.Concurrent (threadDelay)
import Control.Monad (unless, when, forM_)
import Data.Bits ((.&.))
import Data.IORef
import GHC.Clock (getMonotonicTimeNSec)
import System.Environment (getEnvironment)
import System.IO.Error (isDoesNotExistError)
import System.Posix.Files (getSymbolicLinkStatus, isDirectory, fileMode, fileOwner, deviceID, fileID)
import qualified System.Posix.Directory as PosixDirectory
import System.Posix.User (getEffectiveUserID)
import qualified Data.ByteString as B
import qualified Data.ByteString.Char8 as C
import Data.Text (Text)
import qualified Data.Text as T
import qualified Data.Text.Encoding as TE
import Foreign.C.String (CString, withCString, peekCString, newCString)
import Foreign.C.Types (CInt(..), CUInt(..), CULong(..), CSize(..), CPtrdiff(..))
import Foreign.Marshal.Alloc (allocaBytesAligned, alloca, free)
import Foreign.Marshal.Array (withArray, allocaArray)
import Foreign.Marshal.Utils (fillBytes)
import Foreign.Storable (peek, poke, peekByteOff, peekElemOff)
import Foreign.StablePtr (newStablePtr)
import Foreign.Ptr (FunPtr, Ptr, nullPtr, freeHaskellFunPtr, plusPtr, castPtr)
import qualified Warlock.Ui.EngineProtocol as Protocol
import Warlock.Ui.Owner (UiEndpoints(..), TrustedOwnerEvent, EngineResult(..))
import Warlock.Ui.Policy (Origin, Role(..), navigationAllowed, resourceAllowed, resourceFilter, documentUri)
import Warlock.Ui.Mvp (MvpViews(..), SurfaceLease, parseProjectionLease, attachMvpWindow, stepMvpWindow, mvpCloseRequested, retireMvpWindow)
import qualified Warlock.Protocol.StrictJson as J
import Warlock.Ui.ThreadNamespace (requireThreadCompatibleNamespace)
import Warlock.Ui.DefaultContextOwner (PhysicalDefaultContextOwner, withPhysicalDefaultContextOwner, requirePhysicalDefaultContextOwner)
import Warlock.Ui.ProcessSignalOwner (connectProcessSignal, disconnectProcessSignal)
import Warlock.Ui.CallbackRetirement (newCallbackState, captureOwnedCallback, callbackObservation, quarantineCallback, runCallbackOperation, retireOwnedCallback)
import Warlock.Ui.WebKitABI (gValueSize, gValueAlignment, enumValueOffset)
import Warlock.Ui.EngineCustody (Custody, stopCustody, cleanupIssues, productionCleanupFacts, CleanupFacts(..), Setup(..), NamespaceExit(..), OwnerIdentity(..))

data Object
type DecisionCallback = Ptr Object -> Ptr Object -> CInt -> Ptr () -> IO CInt
newtype DecisionHandler = DecisionHandler (FunPtr DecisionCallback)

foreign import ccall "wrapper"
  wrapDecision :: DecisionCallback -> IO (FunPtr DecisionCallback)
foreign import ccall unsafe "webkit_navigation_policy_decision_get_navigation_action"
  navigationAction :: Ptr Object -> IO (Ptr Object)
foreign import ccall unsafe "webkit_navigation_action_get_request"
  actionRequest :: Ptr Object -> IO (Ptr Object)
foreign import ccall unsafe "webkit_response_policy_decision_get_request"
  responseRequest :: Ptr Object -> IO (Ptr Object)
foreign import ccall unsafe "webkit_response_policy_decision_get_response"
  decisionResponse :: Ptr Object -> IO (Ptr Object)
foreign import ccall unsafe "webkit_response_policy_decision_is_mime_type_supported"
  mimeSupported :: Ptr Object -> IO CInt
foreign import ccall unsafe "webkit_uri_request_get_uri"
  requestUri :: Ptr Object -> IO CString
foreign import ccall unsafe "webkit_uri_response_get_uri"
  responseUri :: Ptr Object -> IO CString
foreign import ccall unsafe "webkit_uri_response_get_status_code"
  responseStatus :: Ptr Object -> IO CUInt
foreign import ccall unsafe "webkit_uri_response_get_http_headers"
  responseHeaders :: Ptr Object -> IO (Ptr Object)
foreign import ccall unsafe "soup_message_headers_get_one"
  headerOne :: Ptr Object -> CString -> IO CString
foreign import ccall safe "webkit_policy_decision_use"
  decisionUse :: Ptr Object -> IO ()
foreign import ccall safe "webkit_policy_decision_ignore"
  decisionIgnore :: Ptr Object -> IO ()

-- Keep this function pointer alive for the entire connected signal lifetime.
-- Disconnect the exact handler before calling freeDecisionHandler.
newDecisionHandler :: Origin -> Role -> IO DecisionHandler
newDecisionHandler = newDecisionHandlerChecked (pure ()) (pure ())

newDecisionHandlerChecked :: IO () -> IO () -> Origin -> Role -> IO DecisionHandler
newDecisionHandlerChecked checkAffinity refused origin role = do
  checkAffinity
  navigationDecision <- enumValue policyType "WEBKIT_POLICY_DECISION_TYPE_NAVIGATION_ACTION"
  responseDecision <- enumValue policyType "WEBKIT_POLICY_DECISION_TYPE_RESPONSE"
  DecisionHandler <$> wrapDecision (callback navigationDecision responseDecision)
  where
    callback navigationDecision responseDecision _ decision kind _ = mask_ $ do
      affinity <- try checkAffinity :: IO (Either SomeException ())
      case affinity of
        Left _ -> do
          -- No GTK/WebKit call on an unproved physical thread or stale lease.
          refused `catch` ignoreException
          pure 1
        Right () -> if decision == nullPtr then pure 1 else do
          allowed <- decide navigationDecision responseDecision decision kind `catch` denyException
          (if allowed then decisionUse decision else decisionIgnore decision)
            `catch` ignoreException
          pure 1
    denyException :: SomeException -> IO Bool
    denyException _ = pure False
    ignoreException :: SomeException -> IO ()
    ignoreException _ = pure ()
    decide navigationDecision responseDecision decision kind
      | decision == nullPtr = pure False
      | kind == navigationDecision = do
          action <- navigationAction decision
          request <- if action == nullPtr then pure nullPtr else actionRequest action
          uri <- if request == nullPtr then pure Nothing else readUri requestUri request
          pure (maybe False (navigationAllowed origin) uri)
      | kind == responseDecision = do
          request <- responseRequest decision
          response <- decisionResponse decision
          if request == nullPtr || response == nullPtr then pure False else do
            requested <- readUri requestUri request
            received <- readUri responseUri response
            status <- responseStatus response
            supported <- mimeSupported decision
            headers <- responseHeaders response
            disposition <- if headers == nullPtr then pure True else
              B.useAsCString (B.pack [67,111,110,116,101,110,116,45,68,105,115,112,111,115,105,116,105,111,110]) $ \name ->
                (/= nullPtr) <$> headerOne headers name
            pure (not disposition && status `elem` [200,204] && supported /= 0
              && requested == received && maybe False (resourceAllowed origin role) received)
      | otherwise = pure False

readUri :: (Ptr Object -> IO CString) -> Ptr Object -> IO (Maybe B.ByteString)
readUri getter object = do
  value <- getter object
  if value == nullPtr then pure Nothing else Just <$> B.packCString value

freeDecisionHandler :: DecisionHandler -> IO ()
freeDecisionHandler (DecisionHandler handler) = freeHaskellFunPtr handler

-- All opaque engine objects are owned here.  Calls which can dispatch a signal
-- use safe FFI so the runtime may enter Haskell callbacks.
type GType = CULong
type ReadyCallback = Ptr Object -> Ptr Object -> Ptr () -> IO ()
type LoadCallback = Ptr Object -> CInt -> Ptr () -> IO ()
type LoadFailedCallback = Ptr Object -> CInt -> CString -> Ptr Object -> Ptr () -> IO CInt
type DownloadCallback = Ptr Object -> Ptr Object -> Ptr () -> IO ()
data LoadState = LoadState {loadStarted :: Bool, loadReady :: Bool, loadFailed :: Bool}

foreign import ccall unsafe "webkit_policy_decision_type_get_type" policyType :: IO GType
foreign import ccall unsafe "webkit_network_proxy_mode_get_type" proxyType :: IO GType
foreign import ccall unsafe "g_type_class_ref" typeClassRef :: GType -> IO (Ptr Object)
foreign import ccall unsafe "g_type_class_unref" typeClassUnref :: Ptr Object -> IO ()
foreign import ccall unsafe "g_enum_get_value_by_name" enumByName :: Ptr Object -> CString -> IO (Ptr Object)
foreign import ccall unsafe "webkit_web_view_get_type" viewType :: IO GType
foreign import ccall unsafe "webkit_network_session_get_type" sessionType :: IO GType
foreign import ccall unsafe "webkit_user_content_manager_get_type" managerType :: IO GType
foreign import ccall unsafe "webkit_web_context_get_type" contextType :: IO GType
foreign import ccall unsafe "g_value_init" valueInit :: Ptr () -> GType -> IO (Ptr ())
foreign import ccall unsafe "g_value_set_object" valueObject :: Ptr () -> Ptr Object -> IO ()
foreign import ccall unsafe "g_value_unset" valueUnset :: Ptr () -> IO ()
foreign import ccall safe "g_object_new_with_properties" objectNew :: GType -> CUInt -> Ptr CString -> Ptr () -> IO (Ptr Object)
foreign import ccall unsafe "g_object_ref_sink" refSink :: Ptr Object -> IO (Ptr Object)
foreign import ccall safe "g_object_unref" unref :: Ptr Object -> IO ()
foreign import ccall unsafe "webkit_get_major_version" webkitMajor :: IO CUInt
foreign import ccall unsafe "webkit_get_minor_version" webkitMinor :: IO CUInt
foreign import ccall unsafe "webkit_get_micro_version" webkitMicro :: IO CUInt
foreign import ccall safe "gtk_init_check" gtkInit :: IO CInt
foreign import ccall unsafe "gdk_display_get_default" dpiDefaultDisplay :: IO (Ptr Object)
foreign import ccall unsafe "gtk_settings_get_for_display" dpiDisplaySettings :: Ptr Object -> IO (Ptr Object)
foreign import ccall unsafe "gdk_display_get_monitors" dpiDisplayMonitors :: Ptr Object -> IO (Ptr Object)
foreign import ccall unsafe "g_list_model_get_n_items" dpiMonitorCount :: Ptr Object -> IO CUInt
foreign import ccall unsafe "g_list_model_get_item" dpiMonitorItem :: Ptr Object -> CUInt -> IO (Ptr Object)
foreign import ccall unsafe "gdk_monitor_is_valid" dpiMonitorValid :: Ptr Object -> IO CInt
foreign import ccall unsafe "gdk_monitor_get_geometry" dpiMonitorGeometry :: Ptr Object -> Ptr CInt -> IO ()
foreign import ccall unsafe "gdk_monitor_get_width_mm" dpiMonitorWidthMm :: Ptr Object -> IO CInt
foreign import ccall unsafe "gdk_monitor_get_height_mm" dpiMonitorHeightMm :: Ptr Object -> IO CInt
foreign import ccall unsafe "g_type_from_name" dpiTypeFromName :: CString -> IO GType
foreign import ccall unsafe "g_object_get_property" dpiGetProperty :: Ptr Object -> CString -> Ptr () -> IO ()
foreign import ccall safe "g_object_set_property" dpiSetProperty :: Ptr Object -> CString -> Ptr () -> IO ()
foreign import ccall unsafe "g_value_get_int" dpiValueGetInt :: Ptr () -> IO CInt
foreign import ccall unsafe "g_value_set_int" dpiValueSetInt :: Ptr () -> CInt -> IO ()
foreign import ccall unsafe "gtk_widget_get_display" dpiWidgetDisplay :: Ptr Object -> IO (Ptr Object)
foreign import ccall safe "webkit_network_session_new_ephemeral" sessionNew :: IO (Ptr Object)
foreign import ccall unsafe "webkit_network_session_is_ephemeral" sessionEphemeral :: Ptr Object -> IO CInt
foreign import ccall safe "webkit_network_session_set_proxy_settings" sessionProxy :: Ptr Object -> CInt -> Ptr Object -> IO ()
foreign import ccall safe "webkit_user_content_manager_new" managerNew :: IO (Ptr Object)
foreign import ccall safe "webkit_web_context_new" contextNew :: IO (Ptr Object)
foreign import ccall safe "webkit_user_content_filter_store_new" storeNew :: CString -> IO (Ptr Object)
foreign import ccall safe "webkit_user_content_filter_store_save" storeSave :: Ptr Object -> CString -> Ptr Object -> Ptr Object -> FunPtr ReadyCallback -> Ptr () -> IO ()
foreign import ccall safe "webkit_user_content_filter_store_save_finish" storeFinish :: Ptr Object -> Ptr Object -> Ptr (Ptr Object) -> IO (Ptr Object)
foreign import ccall unsafe "webkit_user_content_filter_unref" filterUnref :: Ptr Object -> IO ()
foreign import ccall safe "webkit_user_content_manager_add_filter" managerFilter :: Ptr Object -> Ptr Object -> IO ()
foreign import ccall unsafe "g_bytes_new" bytesNew :: Ptr a -> CSize -> IO (Ptr Object)
foreign import ccall unsafe "g_bytes_unref" bytesUnref :: Ptr Object -> IO ()
foreign import ccall unsafe "g_cancellable_new" cancellableNew :: IO (Ptr Object)
foreign import ccall safe "g_cancellable_cancel" cancellableCancel :: Ptr Object -> IO ()
foreign import ccall unsafe "g_error_free" errorFree :: Ptr Object -> IO ()
foreign import ccall safe "g_signal_connect_data" signalConnect :: Ptr Object -> CString -> FunPtr () -> Ptr () -> FunPtr (Ptr () -> Ptr () -> IO ()) -> CInt -> IO CULong
foreign import ccall safe "g_signal_handler_disconnect" signalDisconnect :: Ptr Object -> CULong -> IO ()
foreign import ccall safe "webkit_web_view_load_uri" viewLoad :: Ptr Object -> CString -> IO ()
foreign import ccall safe "g_main_context_iteration" contextIteration :: Ptr () -> CInt -> IO CInt
foreign import ccall unsafe "g_main_context_default" contextDefault :: IO (Ptr ())
foreign import ccall unsafe "g_main_context_get_thread_default" contextThreadDefault :: IO (Ptr ())
foreign import ccall unsafe "g_main_context_acquire" contextAcquire :: Ptr () -> IO CInt
foreign import ccall unsafe "g_main_context_release" contextRelease :: Ptr () -> IO ()
foreign import ccall "wrapper" wrapClosureNotify :: (Ptr () -> Ptr () -> IO ()) -> IO (FunPtr (Ptr () -> Ptr () -> IO ()))
foreign import ccall "wrapper" wrapReady :: ReadyCallback -> IO (FunPtr ReadyCallback)
foreign import ccall "wrapper" wrapLoad :: LoadCallback -> IO (FunPtr LoadCallback)
foreign import ccall "wrapper" wrapLoadFailed :: LoadFailedCallback -> IO (FunPtr LoadFailedCallback)
foreign import ccall "wrapper" wrapDownload :: DownloadCallback -> IO (FunPtr DownloadCallback)
foreign import ccall unsafe "webkit_load_event_get_type" loadEventType :: IO GType
foreign import ccall unsafe "webkit_web_view_get_network_session" viewSession :: Ptr Object -> IO (Ptr Object)
foreign import ccall unsafe "webkit_web_view_get_user_content_manager" viewManager :: Ptr Object -> IO (Ptr Object)
foreign import ccall unsafe "webkit_web_view_get_context" viewContext :: Ptr Object -> IO (Ptr Object)
foreign import ccall unsafe "webkit_web_view_get_uri" viewUri :: Ptr Object -> IO CString
foreign import ccall safe "webkit_download_cancel" downloadCancel :: Ptr Object -> IO ()
foreign import ccall safe "webkit_web_view_call_async_javascript_function"
  callAsyncJavascript :: Ptr Object -> CString -> CPtrdiff -> Ptr Object -> CString -> CString -> Ptr Object -> FunPtr ReadyCallback -> Ptr () -> IO ()
foreign import ccall safe "webkit_web_view_call_async_javascript_function_finish"
  callAsyncJavascriptFinish :: Ptr Object -> Ptr Object -> Ptr (Ptr Object) -> IO (Ptr Object)
foreign import ccall unsafe "jsc_value_is_string" javascriptIsString :: Ptr Object -> IO CInt
foreign import ccall unsafe "jsc_value_to_string_as_bytes" javascriptStringBytes :: Ptr Object -> IO (Ptr Object)
foreign import ccall unsafe "g_bytes_get_data" bytesData :: Ptr Object -> Ptr CSize -> IO (Ptr ())
foreign import ccall unsafe "gtk_widget_get_mapped" rendererWidgetMapped :: Ptr Object -> IO CInt
foreign import ccall unsafe "gtk_widget_get_width" rendererWidgetWidth :: Ptr Object -> IO CInt
foreign import ccall unsafe "gtk_widget_get_height" rendererWidgetHeight :: Ptr Object -> IO CInt
foreign import ccall unsafe "mkdtemp" mkdtemp :: CString -> IO CString

must :: Ptr a -> String -> IO (Ptr a)
must p label = if p == nullPtr then ioError (userError label) else pure p

enumValue :: IO GType -> String -> IO CInt
enumValue getType name = do
  typ <- getType
  cls <- typeClassRef typ >>= (`must` "enum class")
  (withCString name $ \n -> do
    item <- enumByName cls n >>= (`must` "enum value")
    peekByteOff item enumValueOffset) `finally` typeClassUnref cls

-- GValue layout comes from the GLib headers used by the selected toolchain.
makeView :: Ptr Object -> Ptr Object -> Ptr Object -> IO (Ptr Object)
makeView session manager context = do
  ts <- sequence [sessionType, managerType, contextType]
  let os = [session,manager,context]
  withCString "network-session" $ \a -> withCString "user-content-manager" $ \b -> withCString "web-context" $ \c ->
    withArray [a,b,c] $ \ns -> allocaBytesAligned (3*gValueSize) gValueAlignment $ \values -> do
      fillBytes values 0 (3*gValueSize)
      let slots = [values `plusPtr` (i*gValueSize) | i <- [0..2]]
      forM_ (zip3 slots ts os) $ \(slot,t,o) -> do _ <- valueInit slot t; valueObject slot o
      (do t <- viewType; objectNew t 3 ns values >>= (`must` "WebView constructor"))
        `finally` mapM_ valueUnset slots

-- Reject inherited WebKit overrides and proxy configuration rather than allowing
-- a caller to select a different engine or disable its sandbox.
-- Exact reviewed provider tuples only; no environment or probe override.
providerVersionQualified :: (CUInt, CUInt, CUInt) -> Bool
providerVersionQualified version = version `elem` [(2,52,6),(2,54,1),(2,54,2)]

checkEnvironment :: IO ()
checkEnvironment = do
  env <- getEnvironment
  let bad (key,_) = take 7 key == "WEBKIT_" || key `elem`
        ["http_proxy","https_proxy","all_proxy","HTTP_PROXY","HTTPS_PROXY","ALL_PROXY","GIO_USE_PROXY_RESOLVER"]
  when (any bad env || any (\(key,_) -> key `elem` ["SNAP","SNAP_NAME","SNAP_REVISION","FLATPAK_ID"]) env)
    (ioError (userError "untrusted WebKit or proxy environment"))
  flatpak <- try (getSymbolicLinkStatus "/.flatpak-info")
  case flatpak of
    Right _ -> ioError (userError "Flatpak engine route unsupported")
    Left problem -> unless (isDoesNotExistError problem) (ioError problem)
  version <- (,,) <$> webkitMajor <*> webkitMinor <*> webkitMicro
  unless (providerVersionQualified version) (ioError (userError "unqualified WebKit version"))

-- A connected callback may still be executing when disconnected. GLib's
-- closure notifier is the receipt that the handler is no longer in use.
-- Keep the notifier FunPtr itself for process lifetime: freeing it from inside
-- its own invocation would have the same lifetime race as the old handler.
-- The constructor is private. A return witness describes only this invocation,
-- never a request marker, an exception, or an already-requested retry. It does
-- not establish retirement, callback return, thread ownership or native readiness.
data SignalDisconnectObservation = SignalDisconnectObservation Bool Bool

signalDisconnectReturned :: SignalDisconnectObservation -> Bool
signalDisconnectReturned (SignalDisconnectObservation returned _) = returned

signalRetirementConfirmed :: SignalDisconnectObservation -> Bool
signalRetirementConfirmed (SignalDisconnectObservation _ retired) = retired

-- Preserve the original interface and retirement requirement for every caller.
connectOwnedSignal :: Ptr a -> String -> FunPtr () -> IO () -> IO (IO ())
connectOwnedSignal object name callback releaseCallback = mask_ $ do
  observe <- connectOwnedSignalObserved object name callback releaseCallback
  pure $ mask_ $ do
    observation <- observe
    unless (signalRetirementConfirmed observation)
      (ioError (userError "WebKit signal retirement uncertain"))

connectOwnedSignalObserved :: Ptr a -> String -> FunPtr () -> IO () -> IO (IO SignalDisconnectObservation)
connectOwnedSignalObserved object name callback releaseCallback = mask_ $ do
  retired <- newIORef False
  requested <- newIORef False
  notifier <- wrapClosureNotify $ \_ _ -> mask_ $ do
    result <- try releaseCallback :: IO (Either SomeException ())
    case result of
      Right () -> atomicWriteIORef retired True
      Left _ -> pure ()
  ident <- withCString name $ \signal -> signalConnect (castPtr object) signal callback nullPtr notifier 0
  -- On a failed/uncertain connection retain callback and notifier: it is not
  -- safe to guess whether GLib already owns the closure.
  if ident == 0 then ioError (userError "WebKit signal connection failed") else
    pure $ mask_ $ do
      already <- atomicModifyIORef' requested (\old -> (True,old))
      returned <- if already then pure False else do
        signalDisconnect (castPtr object) ident
        pure True
      finished <- atomicModifyIORef' retired (\value -> (value,value))
      pure (SignalDisconnectObservation returned finished)

-- GTask dispatches on its captured thread-default GMainContext. Hold the
-- actual default context exclusively across registration, dispatch, and
-- retirement. Then observing a result after contextIteration returns also
-- establishes that this thread has returned from the callback.
withOwnedDefaultContext :: IO a -> IO a
withOwnedDefaultContext action = bracket acquire contextRelease (const action)
  where
    acquire = do
      context <- contextDefault
      threadContext <- contextThreadDefault
      unless (context /= nullPtr && (threadContext == nullPtr || threadContext == context))
        (ioError (userError "unsupported WebKit callback context"))
      owned <- contextAcquire context
      unless (owned /= 0) (ioError (userError "WebKit callback context busy"))
      pure context

-- A missing retirement receipt quarantines the remainder of the LIFO chain.
-- Do not run dependent object unrefs after a failed or uncertain disconnect.
-- This checks the original deadline before each call; synchronous foreign
-- calls themselves have no established execution-time bound.
retireInOrder :: IO Int -> [IO ()] -> IO [Either SomeException ()]
retireInOrder _ [] = pure []
retireInOrder remaining (action:rest) = do
  left <- remaining
  if left <= 250000 then pure [Left (toException (userError "WebKit cleanup deadline uncertain"))] else do
    result <- try action
    case result of
      Left problem -> pure [Left problem]
      Right () -> do
        after <- remaining
        if after <= 250000 then pure [Left (toException (userError "WebKit cleanup deadline uncertain"))]
          else (Right () :) <$> retireInOrder remaining rest

-- The owner getter supplies only the last validated, sent projection and
-- clears it with topology changes. Malformed data fails closed rather than
-- inventing or silently reusing a lease.
readMvpLease :: IO (Maybe J.Json) -> IO (Maybe SurfaceLease)
readMvpLease getProjection = do
  projection <- getProjection
  traverse (either (ioError . userError . T.unpack) pure . parseProjectionLease) projection

-- Owner explicitly refuses a well-formed event whose committed projection
-- changed after observation. It was not enqueued: continue observation,
-- without replaying or treating that refusal as a successful dispatch.
-- All other errors remain fatal to this engine run.
handleMvpDispatch :: Either Text Int -> IO ()
handleMvpDispatch result = case result of
  Right _ -> pure ()
  Left reason | reason == T.pack "stale native UI projection" -> pure ()
  Left reason -> ioError (userError (T.unpack reason))

-- The async completion owns its result cell and callback until completion has
-- actually been observed. If cancellation cannot retire it, those objects are
-- intentionally retained for process lifetime instead of risking a callback UAF.
compileFilter :: PhysicalDefaultContextOwner -> UiEndpoints -> Ptr Object -> Origin -> Role -> IO (Maybe (Ptr Object), Bool)
compileFilter contextOwner endpoints store origin role = withOwnedDefaultContext $ mask $ \restore -> do
  result <- newCallbackState
  let affine = runCallbackOperation contextOwner result
  cancellable <- affine (cancellableNew >>= (`must` "filter cancellable"))
  bytes <- B.useAsCStringLen (resourceFilter origin role) $ \(ptr,len) ->
    affine (bytesNew ptr (fromIntegral len) >>= (`must` "filter bytes"))
  callback <- wrapReady $ \source async _ -> captureOwnedCallback contextOwner result $
    alloca $ \err -> do
      poke err nullPtr
      value <- affine (storeFinish source async err)
      problem <- peek err
      if problem /= nullPtr then do
        affine (errorFree problem)
        when (value /= nullPtr) (affine (filterUnref value))
        pure Nothing
      else pure (if value == nullPtr then Nothing else Just value)
  let waitResult = do
        (observed, quarantined) <- callbackObservation result
        if quarantined then pure Nothing else case observed of
          Just value -> pure value
          Nothing -> do
            stopped <- uiShouldStop endpoints
            remaining <- uiRemainingMicros endpoints
            if stopped || remaining <= 500000 then pure Nothing else do
              _ <- affine (contextIteration nullPtr 0)
              threadDelay 1000
              waitResult
      drain 0 = pure ()
      drain count = do
        (observed, quarantined) <- callbackObservation result
        remaining <- uiRemainingMicros endpoints
        if quarantined then pure () else case observed of
          Just _ -> pure ()
          Nothing -> when (remaining > 250000) $ do
            _ <- affine (contextIteration nullPtr 0)
            threadDelay (min 1000 (remaining-250000))
            drain (count-1)
      retire returned = do
        retirement <- try $ do
          (observed, quarantined) <- callbackObservation result
          if quarantined then pure False else do
            remaining <- uiRemainingMicros endpoints
            when (observed == Nothing && remaining > 250000) $
              affine (cancellableCancel cancellable) >> drain (250 :: Int)
            (completed, failedProof) <- callbackObservation result
            case (completed, failedProof) of
              (Just value, False) -> do
                -- Release a late/unreturned filter only with the same fresh
                -- owner proof as all other releases. Callback is released last.
                let late = case value of
                      Just object | returned /= Just object -> [filterUnref object]
                      _ -> []
                retireOwnedCallback contextOwner result
                  (late ++ [unref cancellable, bytesUnref bytes, freeHaskellFunPtr callback])
              _ -> pure False
        case retirement of
          Right clean -> pure clean
          Left (failure :: SomeException) -> do
            quarantineCallback result
            case fromException failure :: Maybe SomeAsyncException of
              Just _ -> throwIO failure
              Nothing -> pure False
  withCString "warlock" $ \ident -> affine (storeSave store ident bytes cancellable callback nullPtr)
  outcome <- try (restore waitResult) :: IO (Either SomeException (Maybe (Ptr Object)))
  let returned = either (const Nothing) id outcome
  clean <- retire returned
  case outcome of
    Left problem -> throwIO problem
    -- Never hand an uncertain filter to the manager. All unretired references,
    -- callback and backing store stay quarantined by the caller.
    Right value -> pure (if clean then value else Nothing, clean)

-- The UI main thread owns all signal dispatch. Store objects and their private
-- compiled directories are deliberately retained until full engine/helper and
-- internal filter-reference retirement can be observed. Releasing local GTK
-- references alone is not that receipt; this implementation reports the whole
-- engine as unqualified/uncertain even after three successful document loads.
runWebKit :: UiEndpoints -> (TrustedOwnerEvent -> IO (Either Text ())) -> IO EngineResult
runWebKit = runWebKitInternal Nothing

runWebKitWithCustody :: Custody -> UiEndpoints -> (TrustedOwnerEvent -> IO (Either Text ())) -> IO EngineResult
runWebKitWithCustody custody = runWebKitInternal (Just custody)

-- A task whose child PID namespace differs from its own cannot create threads
-- on Linux. GTK may create threads during initialization, before it can report
-- a recoverable error. Inspect the calling thread, and refuse when the procfs
-- identities cannot be observed as well as when they differ.

-- Legacy callers retain the original EngineResult and cleanup semantics.
runWebKitInternal :: Maybe Custody -> UiEndpoints -> (TrustedOwnerEvent -> IO (Either Text ())) -> IO EngineResult
runWebKitInternal custody endpoints ownerEvent =
  fst <$> runWebKitInternalObserved custody Nothing endpoints ownerEvent

-- Selected child route reports bounded observations, never cleanup authority.
runWebKitObserved :: UiEndpoints -> (TrustedOwnerEvent -> IO (Either Text ())) -> IO Protocol.GuiObservation
runWebKitObserved _ _ = ioError (userError "observed WebKit requires parent backing root")

runWebKitObservedWithBacking :: Protocol.BackingRootBinding -> UiEndpoints -> (TrustedOwnerEvent -> IO (Either Text ())) -> IO Protocol.GuiObservation
runWebKitObservedWithBacking binding endpoints ownerEvent =
  snd <$> runWebKitInternalObserved Nothing (Just binding) endpoints ownerEvent

runWebKitInternalObserved :: Maybe Custody -> Maybe Protocol.BackingRootBinding -> UiEndpoints -> (TrustedOwnerEvent -> IO (Either Text ())) -> IO (EngineResult, Protocol.GuiObservation)
runWebKitInternalObserved custody binding endpoints ownerEvent = do
  requireThreadCompatibleNamespace
  checkEnvironment
  mapM_ (requireBackingRoot (uiRemainingMicros endpoints)) binding
  withPhysicalDefaultContextOwner (uiRemainingMicros endpoints) $ \contextOwner ->
    runWebKitOwned contextOwner custody binding endpoints ownerEvent


-- No deletion is available here. The parent retains the root descriptor and
-- can discharge it only after the same owned namespace PID1 has been reaped.
-- The root is private to the same UID; this is not isolation from that UID.
requireBackingRoot :: IO Int -> Protocol.BackingRootBinding -> IO ()
requireBackingRoot remaining binding = do
  left <- remaining
  unless (left > 0) (ioError (userError "backing root original deadline expired"))
  let (path,dev,ino,uid) = Protocol.backingRootFields binding
  currentUid <- getEffectiveUserID
  status <- getSymbolicLinkStatus (T.unpack path)
  unless (isDirectory status && fileMode status .&. 0o7777 == 0o700
       && toInteger (fileOwner status) == uid && toInteger currentUid == uid
       && toInteger (deviceID status) == dev && toInteger (fileID status) == ino)
    (ioError (userError "parent backing root identity changed"))
  after <- remaining
  unless (after > 0) (ioError (userError "backing root original deadline expired"))

createBoundBacking :: IO Int -> Protocol.BackingRootBinding -> Role -> IO (FilePath,IO ())
createBoundBacking remaining binding role = do
  requireBackingRoot remaining binding
  let (root,_,_,uid) = Protocol.backingRootFields binding
      leaf = case role of Controller -> "controller"; Bar -> "bar"; Popup -> "popup"
      path = T.unpack root ++ "/" ++ leaf
  -- mkdir is exclusive: existing files, directories and links all refuse.
  PosixDirectory.createDirectory path 0o700
  first <- getSymbolicLinkStatus path
  let checkChild status = isDirectory status && fileMode status .&. 0o7777 == 0o700
        && toInteger (fileOwner status) == uid
        && deviceID status == deviceID first && fileID status == fileID first
      recheck = do
        requireBackingRoot remaining binding
        current <- getSymbolicLinkStatus path
        unless (checkChild current) (ioError (userError "filter backing identity changed"))
        requireBackingRoot remaining binding
  unless (checkChild first) (ioError (userError "filter backing not private"))
  recheck
  pure (path,recheck)

-- One read-only query per visible role, issued only after the first validated
-- projection. The existing GUI loop drives callbacks; no new wait or timer is
-- introduced. Pending diagnostics do not delay terminal ACK or certify cleanup.
-- Two fixed passive operations: one first-mouseup observation per visible
-- role. No event synthesis, timer, UI wait or acceptance authority. A never
-- resolved Promise remains pending/unknown and process-pinned through exit.
firstMouseupDiagnosticScript :: B.ByteString
firstMouseupDiagnosticScript = C.pack (concat
 ["const cap=(v,n=96)=>String(v==null?'':v).slice(0,n);\n","const number=v=>Number.isFinite(v)&&Math.abs(v)<=65536?v:null;\n","const box=e=>{if(!e||!e.getBoundingClientRect)return null;const r=e.getBoundingClientRect();return [r.x,r.y,r.width,r.height].map(number);};\n","const element=e=>e?{tag:cap(e.tagName,32),id:cap(e.id,128),control:cap(e.getAttribute('data-surface-control'),128)}:null;\n","const installedPerformanceMs=number(performance.now());\n","return new Promise(resolve=>{\n","  const rows=[];\n","  const row=e=>{if(rows.length<8)rows.push({type:cap(e.type,24),isTrusted:e.isTrusted===true,button:number(e.button),buttons:number(e.buttons),client:[number(e.clientX),number(e.clientY)],timeStamp:number(e.timeStamp),target:element(e.target instanceof Element?e.target:e.target&&e.target.parentElement)});};\n","  const types=['pointerdown','mousedown','pointerup'];\n","  const finish=e=>{\n","    row(e);\n","    for(const type of types)document.removeEventListener(type,row,true);\n","    try {\n","      const target=e.target instanceof Element?e.target:e.target&&e.target.parentElement;\n","      const control=target&&target.closest?target.closest('[data-surface-control]'):null;\n","      const root=document.querySelector('.surface-bar,.surface-popup');\n","      const style=control?getComputedStyle(control):null;\n","      const data={status:'first-mouseup-observed',phase:'capture-before-target',isTrusted:e.isTrusted===true,installedPerformanceMs,eventPerformanceMs:number(performance.now()),eventRows:rows,eventLimit:8,viewport:[number(innerWidth),number(innerHeight)],bodyText:cap(document.body?document.body.innerText:'',512),target:element(target),control:control?Object.assign(element(control),{disabled:typeof control.disabled==='boolean'?control.disabled:null,ariaDisabled:cap(control.getAttribute('aria-disabled'),8),focusOnly:cap(control.getAttribute('data-focus-only'),8),bounds:box(control),pointerEvents:cap(style.pointerEvents,32),display:cap(style.display,32),visibility:cap(style.visibility,32),opacity:cap(style.opacity,16)}):null,surface:root?{publication:cap(root.getAttribute('data-publication'),20),lease:cap(root.getAttribute('data-lease'),20),mode:cap(root.getAttribute('data-mode'),16),theme:cap(root.getAttribute('data-theme'),16),textScale:cap(root.getAttribute('data-text-scale'),4)}:null,activeElement:element(document.activeElement),priorScriptExceptions:'not-observed',clickAfterMouseup:'not-observed'};\n","      const result=JSON.stringify(data);\n","      resolve(new TextEncoder().encode(result).length<=8192?result:JSON.stringify({status:'first-mouseup-result-over-byte-bound'}));\n","    } catch(error) { resolve(JSON.stringify({status:'first-mouseup-query-error',error:cap(error,256)})); }\n","  };\n","  for(const type of types)document.addEventListener(type,row,{capture:true,passive:true});\n","  document.addEventListener('mouseup',finish,{capture:true,passive:true,once:true});\n","});\n"])

-- Pure readiness for a diagnostic only: never part of GUI completeness.
rendererAllocationReady :: Bool -> Int -> Int -> Bool
rendererAllocationReady mapped width height = mapped && width>0 && height>0
-- GTK4/WebKit's automatic screen DPI divides by the physical diagonal.
-- Preserve every positive application setting and every nonzero diagonal.
finiteDpiFallbackSetting :: Int -> Int -> Int -> Int -> Int -> Maybe Int
finiteDpiFallbackSetting setting width height widthMm heightMm
 | setting<=0 && width>0 && height>0 && widthMm==0 && heightMm==0 = Just (96*1024)
 | otherwise = Nothing

-- Application-local initialization, before a WebContext or page can capture
-- font DPI. No environment/global setting changes and no additional wait.
initializeFiniteDisplayDpi :: PhysicalDefaultContextOwner -> UiEndpoints -> IO (Ptr Object,J.Json)
initializeFiniteDisplayDpi contextOwner endpoints = do
 let live = do
       requirePhysicalDefaultContextOwner contextOwner
       remaining <- uiRemainingMicros endpoints
       unless (remaining>0) (ioError (userError "display DPI original deadline"))
     affine action = do
       live
       result <- action
       live
       pure result
 dpiDisplay <- affine (dpiDefaultDisplay >>= (`must` "DPI default display"))
 dpiSettings <- affine (dpiDisplaySettings dpiDisplay >>= (`must` "DPI display settings"))
 dpiIntType <- affine (withCString "gint" dpiTypeFromName)
 unless (dpiIntType/=0) (ioError (userError "DPI integer GType absent"))
 let withDpiValue action = allocaBytesAligned gValueSize gValueAlignment $ \slot -> do
       fillBytes slot 0 gValueSize
       _ <- affine (valueInit slot dpiIntType)
       action slot `finally` affine (valueUnset slot)
     readDpi = withDpiValue $ \slot -> do
       affine (withCString "gtk-xft-dpi" $ \name -> dpiGetProperty dpiSettings name slot)
       fromIntegral <$> affine (dpiValueGetInt slot)
     writeDpi target = withDpiValue $ \slot -> do
       affine (dpiValueSetInt slot (fromIntegral target))
       affine (withCString "gtk-xft-dpi" $ \name -> dpiSetProperty dpiSettings name slot)
 dpiBefore <- readDpi
 dpiMonitors <- affine (dpiDisplayMonitors dpiDisplay >>= (`must` "DPI monitor model"))
 dpiCount <- affine (dpiMonitorCount dpiMonitors)
 -- GTK4's WebKit screen manager selects item zero as its primary screen.
 dpiPrimary <- if dpiCount==0 then pure Nothing else do
   dpiMonitor <- affine (dpiMonitorItem dpiMonitors 0 >>= (`must` "DPI primary monitor"))
   (do
     dpiValid <- affine (dpiMonitorValid dpiMonitor)
     if dpiValid==0 then pure Nothing else allocaArray 4 $ \rectangle -> do
       affine (dpiMonitorGeometry dpiMonitor rectangle)
       dpiWidth <- fromIntegral <$> peekElemOff rectangle 2
       dpiHeight <- fromIntegral <$> peekElemOff rectangle 3
       dpiWidthMm <- fromIntegral <$> affine (dpiMonitorWidthMm dpiMonitor)
       dpiHeightMm <- fromIntegral <$> affine (dpiMonitorHeightMm dpiMonitor)
       live
       pure (Just (dpiWidth,dpiHeight,dpiWidthMm,dpiHeightMm)))
       `finally` affine (unref dpiMonitor)
 let dpiFallback = case dpiPrimary of
       Just (width,height,widthMm,heightMm) -> finiteDpiFallbackSetting dpiBefore width height widthMm heightMm
       Nothing -> Nothing
 case dpiFallback of Nothing -> pure (); Just target -> writeDpi target
 dpiAfter <- readDpi
 case dpiFallback of
   Just target -> unless (dpiAfter==target) (ioError (userError "finite display DPI readback differs"))
   Nothing -> pure ()
 let number value = J.JNumber (T.pack (show value))
     pixels = case dpiPrimary of Just (width,height,_,_) -> J.JArray [number width,number height]; Nothing -> J.JNull
     physical = case dpiPrimary of Just (_,_,widthMm,heightMm) -> J.JArray [number widthMm,number heightMm]; Nothing -> J.JNull
     facts = J.JObject [("gtkXftDpiBefore",number dpiBefore),("gtkXftDpiAfter",number dpiAfter),
       ("fallbackApplied",J.JBool (dpiFallback/=Nothing)),("monitorCount",number dpiCount),
       ("primaryPixels",pixels),("primaryPhysicalMm",physical)]
 live
 pure (dpiDisplay,facts)

-- Retain the measured property even when no override or DOM request occurred.
-- The diagnostic remains inert, strictly bounded and outside completeness.
withDisplayDpiDiagnostic :: J.Json -> Text -> Text
withDisplayDpiDiagnostic facts details = either (const fallback) id encoded
 where
  fallback = J.renderJson (J.JObject [("status",J.JString "result-over-display-dpi-byte-bound"),("displayDpi",facts)])
  encoded = do
   limits <- either (const (Left Protocol.Invalid)) Right (J.bounds 8192 16)
   parsed <- either (const (Left Protocol.Invalid)) Right (J.decodeStrict limits (TE.encodeUtf8 details))
   fields <- case parsed of J.JObject values -> Right values; _ -> Left Protocol.Invalid
   Protocol.rendererDiagnosticText (TE.encodeUtf8 (J.renderJson (J.JObject (("displayDpi",facts):fields))))

rendererDiagnosticEnvelope :: Int -> Int -> Text -> Text -> Either Protocol.ProtocolError Text
rendererDiagnosticEnvelope width height observedAt details = do
 unless (rendererAllocationReady True width height) (Left Protocol.Invalid)
 _ <- either (const (Left Protocol.Invalid)) Right (Protocol.requestId observedAt)
 diagnosticRaw <- Protocol.rendererDiagnosticText (TE.encodeUtf8 details)
 limits <- either (const (Left Protocol.Invalid)) Right (J.bounds 8192 16)
 dom <- either (const (Left Protocol.Invalid)) Right (J.decodeStrict limits (TE.encodeUtf8 diagnosticRaw))
 case dom of J.JObject _ -> pure (); _ -> Left Protocol.Invalid
 let allocation = J.JObject [("mapped",J.JBool True),("width",J.JNumber (T.pack (show width))),
        ("height",J.JNumber (T.pack (show height))),("observedMonotonicNs",J.JString observedAt)]
     encode value = TE.encodeUtf8 (J.renderJson (J.JObject [("gtkAllocation",allocation),("dom",value)]))
 case Protocol.rendererDiagnosticText (encode dom) of
  Left Protocol.TooLarge -> Protocol.rendererDiagnosticText (encode (J.JObject [("status",J.JString "result-over-envelope-byte-bound")]))
  value -> value

-- Read each exact child on the existing physical owner thread. The existing
-- loop observes readiness; this function neither waits nor creates a timer.
readRendererAllocation :: PhysicalDefaultContextOwner -> UiEndpoints -> Ptr Object -> IO (Bool,Int,Int,Text)
readRendererAllocation contextOwner endpoints view = do
  let live = do
        requirePhysicalDefaultContextOwner contextOwner
        remaining <- uiRemainingMicros endpoints
        unless (remaining>500000) (ioError (userError "renderer allocation original deadline"))
      affine action = do
        live
        value <- action
        live
        pure value
  mapped <- affine (rendererWidgetMapped view)
  width <- affine (rendererWidgetWidth view)
  height <- affine (rendererWidgetHeight view)
  observedAt <- getMonotonicTimeNSec
  live
  pure (mapped/=0,fromIntegral width,fromIntegral height,T.pack (show observedAt))

beginRendererDiagnostic :: PhysicalDefaultContextOwner -> UiEndpoints -> Ptr Object -> Int -> Int -> Text -> IO (IO Text)
beginRendererDiagnostic contextOwner endpoints view width height observedAt = mask_ $ do
  result <- newCallbackState
  let live = do
        requirePhysicalDefaultContextOwner contextOwner
        remaining <- uiRemainingMicros endpoints
        unless (remaining>500000) (ioError (userError "renderer diagnostic original deadline"))
      affine action = live >> runCallbackOperation contextOwner result action
      envelope details = either (ioError . userError . show) pure
        (rendererDiagnosticEnvelope width height observedAt details)
      status = do
        (value,quarantined) <- callbackObservation result
        if quarantined then envelope (T.pack "{\"status\":\"callback-quarantined\"}")
          else maybe (envelope (T.pack "{\"status\":\"pending-original-deadline\"}")) pure value
  -- This extra object reference and the stable root are process-pinned. Never
  -- release the wrapper, cancellable, view or cell while a callback can arrive.
  held <- affine (refSink view)
  cancellable <- affine (cancellableNew >>= (`must` "renderer diagnostic cancellable"))
  callback <- wrapReady $ \source async _ -> captureOwnedCallback contextOwner result $ do
    live
    unless (source==held && async/=nullPtr) (ioError (userError "renderer diagnostic source identity"))
    alloca $ \err -> do
      poke err nullPtr
      value <- affine (callAsyncJavascriptFinish held async err)
      problem <- peek err
      if problem/=nullPtr then do
        affine (errorFree problem)
        when (value/=nullPtr) (affine (unref value))
        envelope (T.pack "{\"status\":\"javascript-evaluation-failed\"}")
      else if value==nullPtr then envelope (T.pack "{\"status\":\"javascript-result-absent\"}") else
        (do
          isString <- affine (javascriptIsString value)
          unless (isString/=0) (ioError (userError "renderer diagnostic result not string"))
          bytes <- affine (javascriptStringBytes value >>= (`must` "renderer diagnostic bytes"))
          (alloca $ \size -> do
            pointer <- affine (bytesData bytes size)
            lengthBytes <- peek size
            unless (lengthBytes<=8192 && (pointer/=nullPtr || lengthBytes==0)) (ioError (userError "renderer diagnostic byte bound"))
            raw <- affine (B.packCStringLen (castPtr pointer,fromIntegral lengthBytes))
            details <- either (ioError . userError . show) pure (Protocol.rendererDiagnosticText raw)
            envelope details)
              `finally` affine (bytesUnref bytes)) `finally` affine (unref value)
  _ <- newStablePtr (held,cancellable,callback,result)
  B.useAsCStringLen firstMouseupDiagnosticScript $ \(script,lengthBytes) ->
    affine (callAsyncJavascript held script (fromIntegral lengthBytes) nullPtr nullPtr nullPtr cancellable callback nullPtr)
  pure status

runWebKitOwned :: PhysicalDefaultContextOwner -> Maybe Custody -> Maybe Protocol.BackingRootBinding -> UiEndpoints -> (TrustedOwnerEvent -> IO (Either Text ())) -> IO (EngineResult, Protocol.GuiObservation)
runWebKitOwned contextOwner custody binding endpoints ownerEvent = mask $ \restore -> do
  requirePhysicalDefaultContextOwner contextOwner
  ok <- gtkInit
  unless (ok /= 0) (ioError (userError "GTK initialization failed"))
  (dpiDisplay,dpiFacts) <- initializeFiniteDisplayDpi contextOwner endpoints
  noProxy <- enumValue proxyType "WEBKIT_NETWORK_PROXY_MODE_NO_PROXY"
  startedEvent <- enumValue loadEventType "WEBKIT_LOAD_STARTED"
  finishedEvent <- enumValue loadEventType "WEBKIT_LOAD_FINISHED"
  releases <- newIORef ([] :: [IO ()])
  -- Retain the store's owning reference AND directory, not just a borrowed
  -- pathname, through every manager/view lifetime and unresolved async task.
  backings <- newIORef ([] :: [(FilePath,Ptr Object)])
  states <- newIORef ([] :: [(Role,IORef LoadState)])
  rendererViews <- newIORef ([] :: [(Role,Ptr Object)])
  rendererDiagnostics <- newIORef ([] :: [(Role,IO Text)])
  diagnosticAttempted <- newIORef False
  diagnosticNotIssued <- newIORef (T.pack "{\"status\":\"not-issued-load-or-projection-unready\"}")
  attached <- newIORef False
  uncertain <- newIORef False
  let own action release = do
        requirePhysicalDefaultContextOwner contextOwner
        value <- action
        modifyIORef' releases ((requirePhysicalDefaultContextOwner contextOwner >> release value):)
        pure value
      connect object name callback = do
        signal <- connectProcessSignal contextOwner object name callback
        modifyIORef' releases ((do
          _ <- disconnectProcessSignal signal
          writeIORef uncertain True
          ioError (userError "production signal callback retained until owner process exit")):)
      failed state = modifyIORef' state (\old -> old {loadReady=False,loadFailed=True})
      observe state action = (requirePhysicalDefaultContextOwner contextOwner >> action)
        `catch` (\(_ :: SomeException) -> writeIORef uncertain True >> failed state)
      cleanup = do
        pending <- readIORef uncertain
        if pending then pure [] else do
          actions <- readIORef releases
          retireInOrder (uiRemainingMicros endpoints) actions
      setup (role,origin) = do
        requirePhysicalDefaultContextOwner contextOwner
        state <- newIORef (LoadState False False False)
        modifyIORef' states ((role,state):)
        session <- own (sessionNew >>= (`must` "ephemeral session")) unref
        ephemeral <- sessionEphemeral session
        unless (ephemeral /= 0) (ioError (userError "non-ephemeral session"))
        sessionProxy session noProxy nullPtr
        downloadHandler <- wrapDownload $ \_ download _ -> mask_ $ observe state $ do
          failed state
          when (download /= nullPtr) (downloadCancel download)
        connect session "download-started" downloadHandler
        manager <- own (managerNew >>= (`must` "content manager")) unref
        context <- own (contextNew >>= (`must` "WebKit context")) unref
        -- A partial allocation retains its directory as an explicit ownership
        -- obligation; no uncertain async task can reopen a removed pathname.
        (path,recheckBacking) <- case binding of
          Nothing -> do
            -- Legacy EngineResult callers retain their original unowned path;
            -- this branch cannot report parent-owned backing cleanup.
            template <- newCString "/tmp/warlock-filter-XXXXXX"
            legacy <- (mkdtemp template >>= (`must` "private filter directory") >>= peekCString) `finally` free template
            pure (legacy,pure ())
          Just root -> createBoundBacking (uiRemainingMicros endpoints) root role
        modifyIORef' backings ((path,nullPtr):)
        recheckBacking
        store <- withCString path $ \name -> storeNew name >>= (`must` "filter store")
        modifyIORef' backings (map (\(name,value) -> if name==path then (name,store) else (name,value)))
        recheckBacking
        (compiled,retired) <- compileFilter contextOwner endpoints store origin role `onException` writeIORef uncertain True
        unless retired $ do
          writeIORef uncertain True
          ioError (userError "filter callback retirement uncertain")
        case compiled of
          Nothing -> ioError (userError "filter compilation failed")
          Just filterObject ->
            ((requirePhysicalDefaultContextOwner contextOwner >> managerFilter manager filterObject)
              `finally` (requirePhysicalDefaultContextOwner contextOwner >> filterUnref filterObject))
              `onException` writeIORef uncertain True
        view <- own (makeView session manager context >>= refSink) unref
        actualSession <- viewSession view
        actualManager <- viewManager view
        actualContext <- viewContext view
        actualEphemeral <- if actualSession==nullPtr then pure 0 else sessionEphemeral actualSession
        unless (actualSession==session && actualManager==manager && actualContext==context && actualEphemeral/=0)
          (ioError (userError "WebView constructor ownership mismatch"))
        DecisionHandler decision <- newDecisionHandlerChecked
          (requirePhysicalDefaultContextOwner contextOwner)
          (writeIORef uncertain True >> failed state) origin role
        connect view "decide-policy" decision
        changed <- wrapLoad $ \current event _ -> mask_ $ observe state $
          if event==startedEvent then modifyIORef' state (\old -> old {loadStarted=True,loadReady=False}) else
            when (event==finishedEvent) $ do
              uri <- readUri viewUri current
              modifyIORef' state (\old -> old {loadReady=loadStarted old && not (loadFailed old) && maybe False (navigationAllowed origin) uri})
        connect view "load-changed" changed
        loadFailure <- wrapLoadFailed $ \_ _ _ _ _ -> mask_ $ do
          failed state
          -- Suppress WebKit's unapproved stock error document.
          pure 1
        connect view "load-failed" loadFailure
        terminated <- wrapLoad $ \_ _ _ -> mask_ (failed state)
        connect view "web-process-terminated" terminated
        when (role/=Controller) (modifyIORef' rendererViews ((role,view):))
        B.useAsCString (documentUri origin) (viewLoad view)
        pure view
      loop mvp = do
        requirePhysicalDefaultContextOwner contextOwner
        stopped <- uiShouldStop endpoints
        remaining <- uiRemainingMicros endpoints
        active <- readIORef states >>= mapM (readIORef . snd)
        closed <- mvpCloseRequested mvp
        unless (stopped || remaining<=500000 || any loadFailed active || (closed && not (all loadReady active))) $ do
          requirePhysicalDefaultContextOwner contextOwner
          _ <- contextIteration nullPtr 0
          current <- readIORef states >>= mapM (readIORef . snd)
          when (length current == 3 && all (\state -> loadStarted state && loadReady state && not (loadFailed state)) current) $ do
            result <- stepMvpWindow mvp (readMvpLease (uiLastProjection endpoints)) ownerEvent
            handleMvpDispatch result
            projection <- uiLastProjection endpoints
            attempted <- readIORef diagnosticAttempted
            when (binding/=Nothing && not attempted) $ case projection of
              Nothing -> writeIORef diagnosticNotIssued (T.pack "{\"status\":\"not-issued-no-validated-projection\"}")
              Just _ -> do
                views <- readIORef rendererViews
                case (lookup Bar views,lookup Popup views) of
                  (Just bar,Just popup) -> do
                    allocations <- try (mapM (\(role,view) -> do
                      measured <- readRendererAllocation contextOwner endpoints view
                      pure (role,view,measured)) [(Bar,bar),(Popup,popup)])
                      :: IO (Either SomeException [(Role,Ptr Object,(Bool,Int,Int,Text))])
                    case allocations of
                      Left failure -> case fromException failure :: Maybe SomeAsyncException of
                        Just _ -> throwIO failure
                        Nothing -> writeIORef diagnosticNotIssued (T.pack "{\"status\":\"not-issued-allocation-observation-failed\"}")
                      Right measured -> do
                        let ready (_,_,(mapped,width,height,_)) = rendererAllocationReady mapped width height
                            allMapped = all (\(_,_,(mapped,_,_,_)) -> mapped) measured
                        if not (all ready measured) then
                          writeIORef diagnosticNotIssued (T.pack (if allMapped then "{\"status\":\"not-issued-child-zero-allocation\"}" else "{\"status\":\"not-issued-child-unmapped\"}"))
                        else do
                          -- Reserve both one-shot requests only after real child
                          -- mapping/allocation, never a guessed delay or top-level size.
                          writeIORef diagnosticAttempted True
                          forM_ measured $ \(role,view,(_,width,height,observedAt)) -> do
                            started <- try (beginRendererDiagnostic contextOwner endpoints view width height observedAt) :: IO (Either SomeException (IO Text))
                            case started of
                              Right collect -> modifyIORef' rendererDiagnostics ((role,collect):)
                              Left failure -> case fromException failure :: Maybe SomeAsyncException of
                                Just _ -> throwIO failure
                                Nothing -> modifyIORef' rendererDiagnostics ((role,either (ioError . userError . show) pure (rendererDiagnosticEnvelope width height observedAt (T.pack "{\"status\":\"preparation-failed\"}"))):)
                  _ -> writeIORef diagnosticNotIssued (T.pack "{\"status\":\"not-issued-role-view-absent\"}")
          nowClosed <- mvpCloseRequested mvp
          unless nowClosed (threadDelay 1000 >> loop mvp)
      start = do
        views <- mapM setup [(Controller,controllerOrigin endpoints),(Bar,barOrigin endpoints),(Popup,popupOrigin endpoints)]
        case views of
          [controller,bar,popup] -> do
            mvp <- own (attachMvpWindow contextOwner (MvpViews controller bar popup)) retireMvpWindow
            -- gtk_widget_get_display requires an actual GtkRoot hierarchy.
            -- Initialization above still precedes every session/context/page.
            forM_ views $ \view -> do
              requirePhysicalDefaultContextOwner contextOwner
              remainingForDisplay <- uiRemainingMicros endpoints
              unless (remainingForDisplay>0) (ioError (userError "WebView display original deadline"))
              actualDisplay <- dpiWidgetDisplay view
              requirePhysicalDefaultContextOwner contextOwner
              afterDisplay <- uiRemainingMicros endpoints
              unless (actualDisplay==dpiDisplay && afterDisplay>0)
                (ioError (userError "WebView display differs from initialized DPI display"))
            writeIORef attached True
            restore (loop mvp)
          _ -> ioError (userError "WebKit role view invariant")
  outcome <- try start :: IO (Either SomeException ())
  observed <- readIORef states >>= mapM (readIORef . snd)
  let loaded = length observed==3 && all (\state -> loadStarted state && loadReady state && not (loadFailed state)) observed
  roleStates <- readIORef states
  let roleLoaded role = case lookup role roleStates of
        Nothing -> pure False
        Just cell -> do
          value <- readIORef cell
          pure (loadStarted value && loadReady value && not (loadFailed value))
  controllerLoaded <- roleLoaded Controller
  barLoaded <- roleLoaded Bar
  popupLoaded <- roleLoaded Popup
  mvpAttached <- readIORef attached
  preCleanupFault <- readIORef uncertain
  diagnostics <- readIORef rendererDiagnostics
  notIssued <- readIORef diagnosticNotIssued
  let collect role = maybe (pure notIssued) id (lookup role diagnostics)
      originalObservation = Protocol.guiObservation controllerLoaded barLoaded popupLoaded mvpAttached
        (not preCleanupFault && either (const False) (const True) outcome)
  barDiagnostic <- collect Bar
  popupDiagnostic <- collect Popup
  let observation = either (const originalObservation) id
        (Protocol.withRendererDiagnostics (withDisplayDpiDiagnostic dpiFacts barDiagnostic) (withDisplayDpiDiagnostic dpiFacts popupDiagnostic) originalObservation)
  cleanupOutcome <- try cleanup :: IO (Either SomeException [Either SomeException ()])
  lost <- readIORef uncertain
  retained <- readIORef backings
  namespaceExited <- maybe (pure False) (stopCustody (uiRemainingMicros endpoints)) custody
  let localReferencesRetired = not lost && either (const False) (all (either (const False) (const True))) cleanupOutcome
      -- Namespace exit alone does not qualify the exact provider route or
      -- callback retirement. Retain stores and private directories; local
      -- GObject unref is not a whole-engine retirement receipt.
      custodyIssues = cleanupIssues (productionCleanupFacts { custodySetup=maybe SetupUnknown (const SetupReady) custody
        , custodyExit=if namespaceExited then ExitObserved else ExitUnobserved
        , custodyOwner=if namespaceExited then OwnerCurrent else OwnerUncertain })
      wholeClean = null custodyIssues && localReferencesRetired && null retained
      passed = loaded && either (const False) (const True) outcome && wholeClean
      cleanupErrors = case cleanupOutcome of Left problem -> [problem]; Right results -> [problem | Left problem <- results]
      asynchronous = [problem | problem <- cleanupErrors,Just _ <- [fromException problem :: Maybe SomeAsyncException]]
  case outcome of
    Left problem | Just _ <- (fromException problem :: Maybe SomeAsyncException) -> throwIO problem
    _ -> case asynchronous of problem:_ -> throwIO problem; [] -> pure ()
  pure (EngineResult passed wholeClean, observation)
