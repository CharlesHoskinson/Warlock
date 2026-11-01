{-# LANGUAGE ForeignFunctionInterface #-}
{-# LANGUAGE ScopedTypeVariables #-}
-- WebKitGTK 6 boundary; no page loads before its role filter is installed.
module Warlock.Ui.WebKit
  (runWebKit, runWebKitWithCustody, requireThreadCompatibleNamespace, DecisionHandler, newDecisionHandler, freeDecisionHandler, connectOwnedSignal, withOwnedDefaultContext, retireInOrder, readMvpLease, handleMvpDispatch) where

import Control.Exception (SomeException, SomeAsyncException, fromException, throwIO, catch, mask_, mask, onException, try, finally, bracket, toException)
import Control.Concurrent (threadDelay)
import Control.Monad (unless, when, forM_)
import Data.IORef
import System.Environment (getEnvironment)
import System.IO.Error (isDoesNotExistError)
import System.Posix.Files (getSymbolicLinkStatus)
import qualified Data.ByteString as B
import Data.Text (Text)
import qualified Data.Text as T
import Foreign.C.String (CString, withCString, peekCString, newCString)
import Foreign.C.Types (CInt(..), CUInt(..), CULong(..), CSize(..))
import Foreign.Marshal.Alloc (allocaBytesAligned, alloca, free)
import Foreign.Marshal.Array (withArray)
import Foreign.Marshal.Utils (fillBytes)
import Foreign.Storable (peek, poke, peekByteOff)
import Foreign.Ptr (FunPtr, Ptr, nullPtr, freeHaskellFunPtr, plusPtr, castFunPtr, castPtr)
import Warlock.Ui.Owner (UiEndpoints(..), TrustedOwnerEvent, EngineResult(..))
import Warlock.Ui.Policy (Origin, Role(..), navigationAllowed, resourceAllowed, resourceFilter, documentUri)
import Warlock.Ui.Mvp (MvpViews(..), SurfaceLease, parseProjectionLease, attachMvpWindow, stepMvpWindow, mvpCloseRequested, retireMvpWindow)
import qualified Warlock.Protocol.StrictJson as J
import Warlock.Ui.ThreadNamespace (requireThreadCompatibleNamespace)
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
newDecisionHandler origin role = do
  navigationDecision <- enumValue policyType "WEBKIT_POLICY_DECISION_TYPE_NAVIGATION_ACTION"
  responseDecision <- enumValue policyType "WEBKIT_POLICY_DECISION_TYPE_RESPONSE"
  DecisionHandler <$> wrapDecision (callback navigationDecision responseDecision)
  where
    callback navigationDecision responseDecision _ decision kind _ = mask_ $ do
      if decision == nullPtr then pure 1 else do
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
  unless (version `elem` [(2,52,6),(2,54,1)]) (ioError (userError "unqualified WebKit version"))

-- A connected callback may still be executing when disconnected. GLib's
-- closure notifier is the receipt that the handler is no longer in use.
-- Keep the notifier FunPtr itself for process lifetime: freeing it from inside
-- its own invocation would have the same lifetime race as the old handler.
connectOwnedSignal :: Ptr a -> String -> FunPtr () -> IO () -> IO (IO ())
connectOwnedSignal object name callback releaseCallback = mask_ $ do
  retired <- newIORef False
  requested <- newIORef False
  notifier <- wrapClosureNotify $ \_ _ -> mask_ $ do
    result <- try releaseCallback :: IO (Either SomeException ())
    case result of
      Right () -> writeIORef retired True
      Left _ -> pure ()
  ident <- withCString name $ \signal -> signalConnect (castPtr object) signal callback nullPtr notifier 0
  -- On a failed/uncertain connection retain callback and notifier: it is not
  -- safe to guess whether GLib already owns the closure.
  if ident == 0 then ioError (userError "WebKit signal connection failed") else
    pure $ mask_ $ do
      already <- atomicModifyIORef' requested (\old -> (True,old))
      unless already (signalDisconnect (castPtr object) ident)
      finished <- readIORef retired
      unless finished (ioError (userError "WebKit signal retirement uncertain"))

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
compileFilter :: UiEndpoints -> Ptr Object -> Origin -> Role -> IO (Maybe (Ptr Object), Bool)
compileFilter endpoints store origin role = withOwnedDefaultContext $ mask $ \restore -> do
  cancellable <- cancellableNew >>= (`must` "filter cancellable")
  bytes <- B.useAsCStringLen (resourceFilter origin role) $ \(ptr,len) ->
    bytesNew ptr (fromIntegral len) >>= (`must` "filter bytes")
  result <- newIORef Nothing
  callback <- wrapReady $ \source async _ -> mask_ $ do
    outcome <- try $ alloca $ \err -> do
      poke err nullPtr
      value <- storeFinish source async err
      problem <- peek err
      if problem /= nullPtr then do
        errorFree problem
        when (value /= nullPtr) (filterUnref value)
        pure Nothing
      else pure (if value == nullPtr then Nothing else Just value)
    writeIORef result (Just (either (const Nothing) id (outcome :: Either SomeException (Maybe (Ptr Object)))))
  let waitResult = do
        observed <- readIORef result
        case observed of
          Just value -> pure value
          Nothing -> do
            stopped <- uiShouldStop endpoints
            remaining <- uiRemainingMicros endpoints
            if stopped || remaining <= 500000 then pure Nothing else do
              _ <- contextIteration nullPtr 0
              threadDelay 1000
              waitResult
      drain 0 = pure ()
      drain count = do
        observed <- readIORef result
        remaining <- uiRemainingMicros endpoints
        case observed of
          Just _ -> pure ()
          Nothing -> when (remaining > 250000) $ do
            _ <- contextIteration nullPtr 0
            threadDelay (min 1000 (remaining-250000))
            drain (count-1)
      retire = do
        observed <- readIORef result
        remaining <- uiRemainingMicros endpoints
        when (observed == Nothing && remaining > 250000) $
          cancellableCancel cancellable >> drain (250 :: Int)
        completed <- readIORef result
        case completed of
          -- Quarantine every C reference, callback and backing store. No
          -- callback pointer or source bytes are released before completion.
          Nothing -> pure False
          Just _ -> do
            freeHaskellFunPtr callback
            unref cancellable
            bytesUnref bytes
            pure True
  withCString "warlock" $ \ident -> storeSave store ident bytes cancellable callback nullPtr
  outcome <- try (restore waitResult) :: IO (Either SomeException (Maybe (Ptr Object)))
  clean <- retire
  case outcome of
    Left problem -> do
      when clean $ do
        observed <- readIORef result
        case observed of Just (Just value) -> filterUnref value; _ -> pure ()
      throwIO problem
    Right value -> do
      when (value == Nothing && clean) $ do
        observed <- readIORef result
        case observed of Just (Just late) -> filterUnref late; _ -> pure ()
      pure (value,clean)

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

runWebKitInternal :: Maybe Custody -> UiEndpoints -> (TrustedOwnerEvent -> IO (Either Text ())) -> IO EngineResult
runWebKitInternal custody endpoints ownerEvent = mask $ \restore -> do
  requireThreadCompatibleNamespace
  checkEnvironment
  ok <- gtkInit
  unless (ok /= 0) (ioError (userError "GTK initialization failed"))
  noProxy <- enumValue proxyType "WEBKIT_NETWORK_PROXY_MODE_NO_PROXY"
  startedEvent <- enumValue loadEventType "WEBKIT_LOAD_STARTED"
  finishedEvent <- enumValue loadEventType "WEBKIT_LOAD_FINISHED"
  releases <- newIORef ([] :: [IO ()])
  -- Retain the store's owning reference AND directory, not just a borrowed
  -- pathname, through every manager/view lifetime and unresolved async task.
  backings <- newIORef ([] :: [(FilePath,Ptr Object)])
  states <- newIORef ([] :: [IORef LoadState])
  uncertain <- newIORef False
  let own action release = do
        value <- action
        modifyIORef' releases (release value:)
        pure value
      connect object name callback releaseCallback = do
        disconnect <- connectOwnedSignal object name (castFunPtr callback) releaseCallback
        modifyIORef' releases (disconnect:)
      failed state = modifyIORef' state (\old -> old {loadReady=False,loadFailed=True})
      observe state action = action `catch` (\(_ :: SomeException) -> failed state)
      cleanup = do
        pending <- readIORef uncertain
        if pending then pure [] else do
          actions <- readIORef releases
          retireInOrder (uiRemainingMicros endpoints) actions
      setup (role,origin) = do
        state <- newIORef (LoadState False False False)
        modifyIORef' states (state:)
        session <- own (sessionNew >>= (`must` "ephemeral session")) unref
        ephemeral <- sessionEphemeral session
        unless (ephemeral /= 0) (ioError (userError "non-ephemeral session"))
        sessionProxy session noProxy nullPtr
        downloadHandler <- wrapDownload $ \_ download _ -> mask_ $ observe state $ do
          failed state
          when (download /= nullPtr) (downloadCancel download)
        connect session "download-started" downloadHandler (freeHaskellFunPtr downloadHandler)
        manager <- own (managerNew >>= (`must` "content manager")) unref
        context <- own (contextNew >>= (`must` "WebKit context")) unref
        -- A partial allocation retains its directory as an explicit ownership
        -- obligation; no uncertain async task can reopen a removed pathname.
        path <- do
          template <- newCString "/tmp/warlock-filter-XXXXXX"
          (mkdtemp template >>= (`must` "private filter directory") >>= peekCString) `finally` free template
        modifyIORef' backings ((path,nullPtr):)
        store <- withCString path $ \name -> storeNew name >>= (`must` "filter store")
        modifyIORef' backings (map (\(name,value) -> if name==path then (name,store) else (name,value)))
        (compiled,retired) <- compileFilter endpoints store origin role `onException` writeIORef uncertain True
        unless retired (writeIORef uncertain True)
        case compiled of
          Nothing -> ioError (userError "filter compilation failed")
          Just filterObject -> managerFilter manager filterObject `finally` filterUnref filterObject
        unless retired (ioError (userError "filter callback retirement uncertain"))
        view <- own (makeView session manager context >>= refSink) unref
        actualSession <- viewSession view
        actualManager <- viewManager view
        actualContext <- viewContext view
        actualEphemeral <- if actualSession==nullPtr then pure 0 else sessionEphemeral actualSession
        unless (actualSession==session && actualManager==manager && actualContext==context && actualEphemeral/=0)
          (ioError (userError "WebView constructor ownership mismatch"))
        handler@(DecisionHandler decision) <- newDecisionHandler origin role
        connect view "decide-policy" decision (freeDecisionHandler handler)
        changed <- wrapLoad $ \current event _ -> mask_ $ observe state $
          if event==startedEvent then modifyIORef' state (\old -> old {loadStarted=True,loadReady=False}) else
            when (event==finishedEvent) $ do
              uri <- readUri viewUri current
              modifyIORef' state (\old -> old {loadReady=loadStarted old && not (loadFailed old) && maybe False (navigationAllowed origin) uri})
        connect view "load-changed" changed (freeHaskellFunPtr changed)
        loadFailure <- wrapLoadFailed $ \_ _ _ _ _ -> mask_ $ do
          failed state
          -- Suppress WebKit's unapproved stock error document.
          pure 1
        connect view "load-failed" loadFailure (freeHaskellFunPtr loadFailure)
        terminated <- wrapLoad $ \_ _ _ -> mask_ (failed state)
        connect view "web-process-terminated" terminated (freeHaskellFunPtr terminated)
        B.useAsCString (documentUri origin) (viewLoad view)
        pure view
      loop mvp = do
        stopped <- uiShouldStop endpoints
        remaining <- uiRemainingMicros endpoints
        active <- readIORef states >>= mapM readIORef
        closed <- mvpCloseRequested mvp
        unless (stopped || remaining<=500000 || any loadFailed active || (closed && not (all loadReady active))) $ do
          _ <- contextIteration nullPtr 0
          current <- readIORef states >>= mapM readIORef
          when (length current == 3 && all (\state -> loadStarted state && loadReady state && not (loadFailed state)) current) $ do
            result <- stepMvpWindow mvp (readMvpLease (uiLastProjection endpoints)) ownerEvent
            handleMvpDispatch result
          nowClosed <- mvpCloseRequested mvp
          unless nowClosed (threadDelay 1000 >> loop mvp)
      start = do
        views <- mapM setup [(Controller,controllerOrigin endpoints),(Bar,barOrigin endpoints),(Popup,popupOrigin endpoints)]
        case views of
          [controller,bar,popup] -> do
            mvp <- own (attachMvpWindow (MvpViews controller bar popup)) retireMvpWindow
            restore (loop mvp)
          _ -> ioError (userError "WebKit role view invariant")
  outcome <- try start :: IO (Either SomeException ())
  observed <- readIORef states >>= mapM readIORef
  let loaded = length observed==3 && all (\state -> loadStarted state && loadReady state && not (loadFailed state)) observed
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
  pure (EngineResult passed wholeClean)
