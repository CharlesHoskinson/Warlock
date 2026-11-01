{-# LANGUAGE ForeignFunctionInterface #-}
{-# LANGUAGE OverloadedStrings #-}
{-# LANGUAGE ScopedTypeVariables #-}
-- Concrete GTK4/GDK4 single-window bridge for the Warlock UI owner.
-- Zero GTK-authored text, headerbars, or buttons: all GUI elements stay in Elm.
-- Observes live Wayland/GDK surface and monitor state without fabricating
-- monitor boxes, bindings, admissions, or engine-retirement receipts.
module Warlock.Ui.Mvp
  ( MonitorBox
  , makeMonitorBox
  , monitorBoxCoords
  , SurfaceSize
  , makeSurfaceSize
  , surfaceSizeDims
  , SurfaceLease
  , makeSurfaceLease
  , leaseScope
  , leaseRevision
  , leasePublication
  , leaseToken
  , leasePopupOpen
  , parseProjectionLease
  , readProjectedLease
  , isStaleOwnerProjection
  , ViewObservation(..)
  , MvpStepState
  , initialMvpState
  , mvpCurrentScope
  , advanceMvpState
  , MvpViews(..)
  , MvpWindow
  , attachMvpWindow
  , observeGtkWindow
  , stepMvpWindow
  , mvpCloseRequested
  , retireMvpWindow
  ) where

#include <glib-object.h>

import Control.Exception (SomeAsyncException, SomeException, bracket, fromException, mask, mask_, onException, throwIO, try)
import Control.Monad (unless)
import Data.Int (Int32)
import Data.IORef (IORef, atomicModifyIORef', modifyIORef', newIORef, readIORef, writeIORef)
import Data.Text (Text)
import qualified Data.Text as T
import Foreign.C.String (CString, withCString)
import Foreign.C.Types (CDouble(..), CInt(..), CUInt(..), CULong(..))
import Foreign.Marshal.Array (allocaArray)
import Foreign.Marshal.Utils (fillBytes)
import Foreign.Ptr (FunPtr, Ptr, castFunPtr, castPtr, freeHaskellFunPtr, nullPtr, plusPtr)
import Foreign.Storable (peek, peekElemOff)
import Warlock.Protocol.Identity (Counter, addCounter, isZero, parseCounter, renderCounter)
import qualified Warlock.Protocol.StrictJson as J
import Warlock.Ui.Owner (TrustedOwnerEvent(..))

int32MinInteger :: Integer
int32MinInteger = -2147483648

int32MaxInteger :: Integer
int32MaxInteger = 2147483647

cIntToInt32 :: CInt -> Either Text Int32
cIntToInt32 raw =
  let val = toInteger raw
   in if val >= int32MinInteger && val <= int32MaxInteger
        then Right (fromIntegral val)
        else Left "C integer exceeds signed 32-bit coordinate bounds"

-- | Validated monitor rectangle from GDK with positive dimensions and non-overflowing Int32 extent.
data MonitorBox = MonitorBox !Int32 !Int32 !Int32 !Int32
  deriving (Eq, Show)

makeMonitorBox :: Int32 -> Int32 -> Int32 -> Int32 -> Either Text MonitorBox
makeMonitorBox x y w h
  | w <= 0 || h <= 0 = Left "monitor geometry dimensions must be positive"
  | toInteger x + toInteger w > int32MaxInteger = Left "monitor geometry X extent overflows Int32"
  | toInteger y + toInteger h > int32MaxInteger = Left "monitor geometry Y extent overflows Int32"
  | otherwise = Right (MonitorBox x y w h)

monitorBoxCoords :: MonitorBox -> (Int32, Int32, Int32, Int32)
monitorBoxCoords (MonitorBox x y w h) = (x, y, w, h)

-- | Validated mapped GdkSurface dimensions with positive width and height.
data SurfaceSize = SurfaceSize !Int32 !Int32
  deriving (Eq, Show)

makeSurfaceSize :: Int32 -> Int32 -> Either Text SurfaceSize
makeSurfaceSize w h
  | w <= 0 || h <= 0 = Left "surface dimensions must be positive"
  | otherwise = Right (SurfaceSize w h)

surfaceSizeDims :: SurfaceSize -> (Int32, Int32)
surfaceSizeDims (SurfaceSize w h) = (w, h)

-- | Validated committed @view-frame@ surface publication and lease snapshot.
-- Unscoped frames (@views == []@) carry 'Nothing' in 'leaseScope' so they can be
-- decoded without error while never matching a mapped window scope.
data SurfaceLease = SurfaceLease
  { slScope :: !(Maybe (Counter, Counter))
  , slRevision :: !Counter
  , slPublication :: !Counter
  , slLease :: !Counter
  , slPopupOpen :: !Bool
  }
  deriving (Eq, Show)

makeSurfaceLease
  :: Maybe (Counter, Counter)
  -> Counter
  -> Counter
  -> Counter
  -> Bool
  -> Either Text SurfaceLease
makeSurfaceLease mScope rev pub token popupOpen
  | Just (scopeId, gen) <- mScope
  , isZero scopeId || isZero gen =
      Left "surface lease scope counters must be positive"
  | isZero pub =
      Left "surface lease publication counter must be positive"
  | popupOpen && isZero token =
      Left "open popup surface lease token must be positive"
  | otherwise =
      Right
        SurfaceLease
          { slScope = mScope
          , slRevision = rev
          , slPublication = pub
          , slLease = token
          , slPopupOpen = popupOpen
          }

leaseScope :: SurfaceLease -> Maybe (Counter, Counter)
leaseScope = slScope

leaseRevision :: SurfaceLease -> Counter
leaseRevision = slRevision

leasePublication :: SurfaceLease -> Counter
leasePublication = slPublication

leaseToken :: SurfaceLease -> Counter
leaseToken = slLease

leasePopupOpen :: SurfaceLease -> Bool
leasePopupOpen = slPopupOpen

-- | Exact non-fatal refusal string returned by 'Warlock.Ui.Owner' when the
-- committed projection changed after observation.
staleOwnerProjectionMessage :: Text
staleOwnerProjectionMessage = "stale native UI projection"

isStaleOwnerProjection :: Text -> Bool
isStaleOwnerProjection = (== staleOwnerProjectionMessage)

-- | Decode a validated 'SurfaceLease' from a committed @view-frame@ object.
parseProjectionLease :: J.Json -> Either Text SurfaceLease
parseProjectionLease projection = do
  fields <-
    exactFields
      [ "viewProtocol"
      , "kind"
      , "revision"
      , "views"
      , "focusOwner"
      , "popupOwner"
      , "frame"
      , "announcer"
      , "announcement"
      ]
      projection
  vp <- lookupField "viewProtocol" fields
  unlessMatched (vp == J.JNumber "1") "unexpected view-frame protocol version"
  kindVal <- lookupField "kind" fields
  unlessMatched (kindVal == J.JString "view-frame") "expected view-frame kind"
  revText <- lookupField "revision" fields >>= expectString "revision"
  rev <- parseNonNegative revText
  viewsVal <- lookupField "views" fields
  (mScopeVal, mScopeCounters) <-
    case viewsVal of
      J.JArray [] -> Right (Nothing, Nothing)
      J.JArray [single] -> do
        scopeFields <- exactFields ["id", "generation"] single
        scopeIdText <- lookupField "id" scopeFields >>= expectString "id"
        genText <- lookupField "generation" scopeFields >>= expectString "generation"
        scopeId <- parsePositive scopeIdText
        gen <- parsePositive genText
        Right (Just single, Just (scopeId, gen))
      _ -> Left "invalid view-frame views array"
  focusVal <- lookupField "focusOwner" fields
  case mScopeVal of
    Just scopeVal ->
      unlessMatched (focusVal == J.JNull || focusVal == scopeVal) "view-frame focusOwner mismatch"
    Nothing ->
      pure ()
  popupVal <- lookupField "popupOwner" fields
  popupOpen <-
    case popupVal of
      J.JNull -> Right False
      J.JObject _ ->
        case mScopeVal of
          Just scopeVal ->
            if popupVal == scopeVal
              then Right True
              else Left "view-frame popupOwner does not match owned scope"
          Nothing ->
            Right True
      _ -> Left "expected object or null for popupOwner"
  frameVal <- lookupField "frame" fields
  framePairs <-
    case frameVal of
      J.JObject pairs -> Right pairs
      _ -> Left "expected JSON object for frame"
  case lookup "surfaceProtocol" framePairs of
    Just surfVer ->
      unlessMatched (surfVer == J.JNumber "2") "unexpected surfaceProtocol version"
    Nothing ->
      pure ()
  pubText <- lookupField "publication" framePairs >>= expectString "publication"
  leaseText <- lookupField "lease" framePairs >>= expectString "lease"
  pub <- parsePositive pubText
  token <- parseNonNegative leaseText
  makeSurfaceLease mScopeCounters rev pub token popupOpen
  where
    unlessMatched ok msg = if ok then Right () else Left msg
    exactFields names val =
      either (Left . T.pack . show) Right (J.exactObject names val)
    lookupField name pairs =
      maybe (Left ("missing field: " <> name)) Right (lookup name pairs)
    expectString _ (J.JString txt) = Right txt
    expectString name _ = Left ("expected string field: " <> name)
    parsePositive txt =
      either (Left . T.pack . show) Right (parseCounter False txt)
    parseNonNegative txt =
      either (Left . T.pack . show) Right (parseCounter True txt)

-- | Read and validate 'UiEndpoints.uiLastProjection' into a 'SurfaceLease',
-- failing closed on malformed JSON if present.
readProjectedLease :: IO (Maybe J.Json) -> IO (Maybe SurfaceLease)
readProjectedLease fetchProjection = do
  mRaw <- fetchProjection
  traverse (either (ioError . userError . T.unpack) pure . parseProjectionLease) mRaw

-- | Live GTK/GDK window observation on a single main-context tick.
data ViewObservation
  = ViewUnmapped
  | ViewMapped
      { observedSurface :: !SurfaceSize
      , observedActive :: !Bool
      , observedMonitor :: !(Maybe MonitorBox)
      }
  deriving (Eq, Show)

data PublishedTopology
  = TopologyNone
  | TopologyUnretiredEmpty
  | TopologyMapped !Counter !Counter !(Maybe MonitorBox)
  | TopologyClosed
  deriving (Eq, Show)

-- | Bounded O(1) pure state machine deriving monotonic 'TrustedOwnerEvent' values.
data MvpStepState = MvpStepState
  { stateRevision :: !(Maybe Counter)
  , stateHighestScopeId :: !(Maybe Counter)
  , stateTopology :: !PublishedTopology
  , stateLastSize :: !(Maybe SurfaceSize)
  , stateLastReflow :: !(Maybe (Counter, SurfaceSize))
  , stateLastEscape :: !(Maybe (Counter, Counter))
  }
  deriving (Eq, Show)

initialMvpState :: MvpStepState
initialMvpState = MvpStepState
  { stateRevision = Nothing
  , stateHighestScopeId = Nothing
  , stateTopology = TopologyNone
  , stateLastSize = Nothing
  , stateLastReflow = Nothing
  , stateLastEscape = Nothing
  }

mvpCurrentScope :: MvpStepState -> Maybe J.Json
mvpCurrentScope st =
  case stateTopology st of
    TopologyMapped scopeId gen _ -> Just (encodeScope scopeId gen)
    _ -> Nothing

counterOne :: Either Text Counter
counterOne = either (Left . T.pack . show) Right (parseCounter False "1")

nextCounter :: Maybe Counter -> Either Text Counter
nextCounter Nothing = counterOne
nextCounter (Just prev) = either (Left . T.pack . show) Right (addCounter prev 1)

encodeScope :: Counter -> Counter -> J.Json
encodeScope scopeId gen =
  J.JObject
    [ ("id", J.JString (renderCounter scopeId))
    , ("generation", J.JString (renderCounter gen))
    ]

encodeEmptyTopology :: Counter -> J.Json
encodeEmptyTopology rev =
  J.JObject
    [ ("viewProtocol", J.JNumber "1")
    , ("kind", J.JString "view-topology")
    , ("revision", J.JString (renderCounter rev))
    , ("views", J.JArray [])
    ]

encodeMappedTopology :: Counter -> Counter -> Counter -> Maybe MonitorBox -> J.Json
encodeMappedTopology rev scopeId gen Nothing =
  J.JObject
    [ ("viewProtocol", J.JNumber "1")
    , ("kind", J.JString "view-topology")
    , ("revision", J.JString (renderCounter rev))
    , ("views", J.JArray [encodeScope scopeId gen])
    ]
encodeMappedTopology rev scopeId gen (Just box) =
  let scopeVal = encodeScope scopeId gen
      (x, y, w, h) = monitorBoxCoords box
      num n = J.JNumber (T.pack (show n))
      loc =
        J.JObject
          [ ("scope", scopeVal)
          , ("box", J.JArray [num x, num y, num w, num h])
          ]
   in J.JObject
        [ ("viewProtocol", J.JNumber "2")
        , ("kind", J.JString "view-topology")
        , ("revision", J.JString (renderCounter rev))
        , ("views", J.JArray [scopeVal])
        , ("locations", J.JArray [loc])
        ]

encodeDismiss :: Counter -> Counter -> Counter -> J.Json
encodeDismiss scopeId gen token =
  J.JObject
    [ ("scope", encodeScope scopeId gen)
    , ("lease", J.JString (renderCounter token))
    ]

encodeEscape :: Counter -> Counter -> Counter -> Counter -> J.Json
encodeEscape scopeId gen pub token =
  J.JObject
    [ ("scope", encodeScope scopeId gen)
    , ("publication", J.JString (renderCounter pub))
    , ("lease", J.JString (renderCounter token))
    ]

encodeReflow :: Counter -> Counter -> Counter -> J.Json
encodeReflow scopeId gen token =
  J.JObject
    [ ("scope", encodeScope scopeId gen)
    , ("lease", J.JString (renderCounter token))
    ]

matchingScopeLease
  :: Counter
  -> Counter
  -> Maybe Counter
  -> Maybe SurfaceLease
  -> Maybe SurfaceLease
matchingScopeLease scopeId gen expectedRev (Just lease)
  | leaseScope lease == Just (scopeId, gen)
  , Just (leaseRevision lease) == expectedRev =
      Just lease
matchingScopeLease _ _ _ _ = Nothing

matchingOpenLease
  :: Counter
  -> Counter
  -> Maybe Counter
  -> Maybe SurfaceLease
  -> Maybe SurfaceLease
matchingOpenLease scopeId gen expectedRev mLease =
  case matchingScopeLease scopeId gen expectedRev mLease of
    Just lease
      | leasePopupOpen lease
      , not (isZero (leaseToken lease)) ->
          Just lease
    _ -> Nothing

admitFreshMap
  :: SurfaceSize
  -> Maybe MonitorBox
  -> MvpStepState
  -> Either Text (MvpStepState, TrustedOwnerEvent)
admitFreshMap surf0 mMon0 prior = do
  -- OutputController requires any newly admitted scope id after an unmap
  -- to exceed model.highest strictly.
  scopeId <- nextCounter (stateHighestScopeId prior)
  gen <- counterOne
  rev <- nextCounter (stateRevision prior)
  let payload = encodeMappedTopology rev scopeId gen mMon0
      nextSt = prior
        { stateRevision = Just rev
        , stateHighestScopeId = Just scopeId
        , stateTopology = TopologyMapped scopeId gen mMon0
        , stateLastSize = Just surf0
        , stateLastReflow = Nothing
        , stateLastEscape = Nothing
        }
  Right (nextSt, OwnerTopology payload)

-- | Advance pure MVP topology/popup state assuming all emitted events are accepted.
advanceMvpState
  :: ViewObservation
  -> Bool
  -> Bool
  -> Maybe SurfaceLease
  -> MvpStepState
  -> Either Text (MvpStepState, [TrustedOwnerEvent])
advanceMvpState obs closeNow escapePressed mLease st
  | stateTopology st == TopologyClosed =
      Right (st, [])
  | closeNow =
      retireMappedOrClose TopologyClosed st
  | otherwise =
      case (stateTopology st, obs) of
        (TopologyNone, ViewUnmapped) ->
          Right (st, [])
        (TopologyUnretiredEmpty, ViewUnmapped) ->
          Right (st, [])
        (TopologyMapped _ _ _, ViewUnmapped) ->
          retireMappedOrClose TopologyUnretiredEmpty st
        (TopologyNone, ViewMapped surf0 _ mMon0) -> do
          (nextSt, ev) <- admitFreshMap surf0 mMon0 st
          Right (nextSt, [ev])
        (TopologyUnretiredEmpty, ViewMapped surf0 _ mMon0) -> do
          (nextSt, ev) <- admitFreshMap surf0 mMon0 st
          Right (nextSt, [ev])
        (TopologyMapped scopeId gen prevMon, ViewMapped surf _ curMon)
          | curMon /= prevMon -> do
              rev <- nextCounter (stateRevision st)
              let payload = encodeMappedTopology rev scopeId gen curMon
                  nextSt = st
                    { stateRevision = Just rev
                    , stateTopology = TopologyMapped scopeId gen curMon
                    , stateLastReflow = Nothing
                    , stateLastEscape = Nothing
                    }
              Right (nextSt, [OwnerTopology payload])
          | otherwise ->
              case matchingScopeLease scopeId gen (stateRevision st) mLease of
                Nothing ->
                  Right (st, [])
                Just lease
                  | not (leasePopupOpen lease) || isZero (leaseToken lease) ->
                      Right
                        ( st
                            { stateLastSize = Just surf
                            , stateLastReflow = Nothing
                            , stateLastEscape = Nothing
                            }
                        , []
                        )
                  | otherwise ->
                      let sizeChanged =
                            case stateLastSize st of
                              Just prevSurf -> surf /= prevSurf
                              Nothing -> True
                          needReflow =
                            sizeChanged && stateLastReflow st /= Just (leaseToken lease, surf)
                          needEscape =
                            escapePressed
                              && stateLastEscape st /= Just (leasePublication lease, leaseToken lease)
                          afterReflow =
                            if needReflow
                              then
                                st
                                  { stateLastSize = Just surf
                                  , stateLastReflow = Just (leaseToken lease, surf)
                                  }
                              else st
                          afterEscape =
                            if needEscape
                              then
                                afterReflow
                                  { stateLastEscape = Just (leasePublication lease, leaseToken lease)
                                  }
                              else afterReflow
                          reflowEvents =
                            if needReflow
                              then [OwnerReflow (encodeReflow scopeId gen (leaseToken lease))]
                              else []
                          escapeEvents =
                            if needEscape
                              then [OwnerEscape (encodeEscape scopeId gen (leasePublication lease) (leaseToken lease))]
                              else []
                       in Right (afterEscape, reflowEvents ++ escapeEvents)
        (TopologyClosed, _) ->
          Right (st, [])
  where
    retireMappedOrClose targetTopo prior =
      case stateTopology prior of
        TopologyMapped scopeId gen _ -> do
          let dismissEvents =
                case matchingOpenLease scopeId gen (stateRevision prior) mLease of
                  Just lease -> [OwnerDismiss (encodeDismiss scopeId gen (leaseToken lease))]
                  Nothing -> []
          rev <- nextCounter (stateRevision prior)
          let retireEvent = OwnerTopology (encodeEmptyTopology rev)
              nextSt = prior
                { stateRevision = Just rev
                , stateTopology = targetTopo
                , stateLastSize = Nothing
                , stateLastReflow = Nothing
                , stateLastEscape = Nothing
                }
          Right (nextSt, dismissEvents ++ [retireEvent])
        _ ->
          Right
            ( prior
                { stateTopology = targetTopo
                , stateLastSize = Nothing
                , stateLastReflow = Nothing
                , stateLastEscape = Nothing
                }
            , []
            )

-- ---------------------------------------------------------------------------
-- GTK4 / GDK4 single-window host bridge (libgtk-4.so.1 + libgobject-2.0.so.0)
-- ---------------------------------------------------------------------------

data MvpObject

type GType = CULong
type ClosureNotifyCallback = Ptr () -> Ptr () -> IO ()
type CloseRequestCallback = Ptr MvpObject -> Ptr () -> IO CInt
type KeyPressedCallback = Ptr MvpObject -> CUInt -> CUInt -> CInt -> Ptr () -> IO CInt

gdkKeyEscape :: CUInt
gdkKeyEscape = 0xff1b

enumValueByteOffset :: Int
enumValueByteOffset = #{offset GEnumValue, value}

cIntByteSize :: Int
cIntByteSize = #{size int}

foreign import ccall "wrapper"
  wrapClosureNotify :: ClosureNotifyCallback -> IO (FunPtr ClosureNotifyCallback)

foreign import ccall "wrapper"
  wrapCloseRequest :: CloseRequestCallback -> IO (FunPtr CloseRequestCallback)

foreign import ccall "wrapper"
  wrapKeyPressed :: KeyPressedCallback -> IO (FunPtr KeyPressedCallback)

foreign import ccall unsafe "g_object_ref"
  gObjectRef :: Ptr MvpObject -> IO (Ptr MvpObject)

foreign import ccall safe "g_object_unref"
  gObjectUnref :: Ptr MvpObject -> IO ()

foreign import ccall unsafe "g_object_ref_sink"
  gObjectRefSink :: Ptr MvpObject -> IO (Ptr MvpObject)

foreign import ccall unsafe "g_type_class_ref"
  gTypeClassRef :: GType -> IO (Ptr MvpObject)

foreign import ccall unsafe "g_type_class_unref"
  gTypeClassUnref :: Ptr MvpObject -> IO ()

foreign import ccall unsafe "g_enum_get_value_by_name"
  gEnumByName :: Ptr MvpObject -> CString -> IO (Ptr MvpObject)

foreign import ccall safe "g_signal_connect_data"
  gSignalConnectData
    :: Ptr MvpObject
    -> CString
    -> FunPtr ()
    -> Ptr ()
    -> FunPtr ClosureNotifyCallback
    -> CInt
    -> IO CULong

foreign import ccall safe "g_signal_handler_disconnect"
  gSignalDisconnect :: Ptr MvpObject -> CULong -> IO ()

foreign import ccall unsafe "gtk_orientation_get_type"
  gtkOrientationGetType :: IO GType

foreign import ccall unsafe "gtk_propagation_phase_get_type"
  gtkPropagationPhaseGetType :: IO GType

foreign import ccall safe "gtk_window_new"
  gtkWindowNew :: IO (Ptr MvpObject)

foreign import ccall safe "gtk_window_set_default_size"
  gtkWindowSetDefaultSize :: Ptr MvpObject -> CInt -> CInt -> IO ()

foreign import ccall safe "gtk_window_set_decorated"
  gtkWindowSetDecorated :: Ptr MvpObject -> CInt -> IO ()

foreign import ccall safe "gtk_window_set_resizable"
  gtkWindowSetResizable :: Ptr MvpObject -> CInt -> IO ()

foreign import ccall safe "gtk_window_set_child"
  gtkWindowSetChild :: Ptr MvpObject -> Ptr MvpObject -> IO ()

foreign import ccall safe "gtk_window_present"
  gtkWindowPresent :: Ptr MvpObject -> IO ()

foreign import ccall safe "gtk_window_destroy"
  gtkWindowDestroy :: Ptr MvpObject -> IO ()

foreign import ccall unsafe "gtk_window_is_active"
  gtkWindowIsActive :: Ptr MvpObject -> IO CInt

foreign import ccall safe "gtk_box_new"
  gtkBoxNew :: CInt -> CInt -> IO (Ptr MvpObject)

foreign import ccall safe "gtk_box_append"
  gtkBoxAppend :: Ptr MvpObject -> Ptr MvpObject -> IO ()

foreign import ccall safe "gtk_widget_set_hexpand"
  gtkWidgetSetHexpand :: Ptr MvpObject -> CInt -> IO ()

foreign import ccall safe "gtk_widget_set_vexpand"
  gtkWidgetSetVexpand :: Ptr MvpObject -> CInt -> IO ()

foreign import ccall safe "gtk_widget_set_size_request"
  gtkWidgetSetSizeRequest :: Ptr MvpObject -> CInt -> CInt -> IO ()

foreign import ccall safe "gtk_widget_set_visible"
  gtkWidgetSetVisible :: Ptr MvpObject -> CInt -> IO ()

foreign import ccall safe "gtk_widget_set_opacity"
  gtkWidgetSetOpacity :: Ptr MvpObject -> CDouble -> IO ()

foreign import ccall safe "gtk_widget_set_focusable"
  gtkWidgetSetFocusable :: Ptr MvpObject -> CInt -> IO ()

foreign import ccall safe "gtk_widget_set_can_target"
  gtkWidgetSetCanTarget :: Ptr MvpObject -> CInt -> IO ()

foreign import ccall safe "gtk_widget_add_controller"
  gtkWidgetAddController :: Ptr MvpObject -> Ptr MvpObject -> IO ()

foreign import ccall unsafe "gtk_widget_get_mapped"
  gtkWidgetGetMapped :: Ptr MvpObject -> IO CInt

foreign import ccall unsafe "gtk_widget_get_native"
  gtkWidgetGetNative :: Ptr MvpObject -> IO (Ptr MvpObject)

foreign import ccall unsafe "gtk_native_get_surface"
  gtkNativeGetSurface :: Ptr MvpObject -> IO (Ptr MvpObject)

foreign import ccall safe "gtk_event_controller_key_new"
  gtkEventControllerKeyNew :: IO (Ptr MvpObject)

foreign import ccall safe "gtk_event_controller_set_propagation_phase"
  gtkEventControllerSetPropagationPhase :: Ptr MvpObject -> CInt -> IO ()

foreign import ccall unsafe "gdk_surface_get_mapped"
  gdkSurfaceGetMapped :: Ptr MvpObject -> IO CInt

foreign import ccall unsafe "gdk_surface_get_width"
  gdkSurfaceGetWidth :: Ptr MvpObject -> IO CInt

foreign import ccall unsafe "gdk_surface_get_height"
  gdkSurfaceGetHeight :: Ptr MvpObject -> IO CInt

foreign import ccall unsafe "gdk_surface_get_display"
  gdkSurfaceGetDisplay :: Ptr MvpObject -> IO (Ptr MvpObject)

foreign import ccall unsafe "gdk_display_get_monitor_at_surface"
  gdkDisplayGetMonitorAtSurface :: Ptr MvpObject -> Ptr MvpObject -> IO (Ptr MvpObject)

foreign import ccall unsafe "gdk_monitor_is_valid"
  gdkMonitorIsValid :: Ptr MvpObject -> IO CInt

foreign import ccall unsafe "gdk_monitor_get_geometry"
  gdkMonitorGetGeometry :: Ptr MvpObject -> Ptr CInt -> IO ()

-- | Three distinct WebKitWebView widget pointers owned by the caller.
data MvpViews view = MvpViews
  { mvpControllerView :: !(Ptr view)
  , mvpBarView :: !(Ptr view)
  , mvpPopupView :: !(Ptr view)
  }

-- | Live single-window GTK4 container and signal/state cells.
data MvpWindow = MvpWindow
  { mvpGtkWindow :: !(Ptr MvpObject)
  , mvpCloseRef :: !(IORef Bool)
  , mvpEscapeRef :: !(IORef Bool)
  , mvpStateRef :: !(IORef MvpStepState)
  , mvpRetiredRef :: !(IORef Bool)
  , mvpSignalReleasesRef :: !(IORef [IO ()])
  , mvpObjectReleasesRef :: !(IORef [IO ()])
  }

mustPtr :: Ptr a -> String -> IO (Ptr a)
mustPtr ptr label =
  if ptr == nullPtr
    then ioError (userError label)
    else pure ptr

resolveEnumValue :: IO GType -> String -> IO CInt
resolveEnumValue getType valueName = do
  gtype <- getType
  bracket (gTypeClassRef gtype >>= (`mustPtr` "MVP GEnumClass")) gTypeClassUnref $ \cls ->
    withCString valueName $ \cname -> do
      entry <- gEnumByName cls cname >>= (`mustPtr` "MVP GEnumValue")
      peek (plusPtr entry enumValueByteOffset)

-- | Connect a GObject signal whose Haskell FunPtr is freed ONLY when GLib's
-- GClosureNotify confirms the closure is disconnected and no longer executing.
-- The notifier FunPtr itself is intentionally retained for process lifetime.
connectOwnedMvpSignal
  :: Ptr MvpObject
  -> String
  -> IO (FunPtr a)
  -> (FunPtr a -> IO ())
  -> IO (IO ())
connectOwnedMvpSignal obj signalName makeHandler releaseHandler = mask_ $ do
  retired <- newIORef False
  requested <- newIORef False
  handler <- makeHandler
  notifier <-
    wrapClosureNotify
      ( \_ _ -> mask_ $ do
          outcome <- try (releaseHandler handler) :: IO (Either SomeException ())
          case outcome of
            Right () -> writeIORef retired True
            Left _ -> pure ()
      )
      `onException` releaseHandler handler
  ident <- withCString signalName $ \sig ->
    gSignalConnectData obj sig (castFunPtr handler) nullPtr notifier 0
  -- If g_signal_connect_data returns 0, retain handler and notifier rather than
  -- guessing whether GLib already referenced the closure.
  if ident == 0
    then ioError (userError ("MVP signal connection failed: " ++ signalName))
    else pure $ mask_ $ do
      already <- atomicModifyIORef' requested (\old -> (True, old))
      unless already (gSignalDisconnect obj ident)
      done <- readIORef retired
      unless done (ioError (userError ("MVP signal retirement uncertain: " ++ signalName)))

runCleanupSequence :: IORef [IO ()] -> IORef [IO ()] -> IO [SomeException]
runCleanupSequence sigRelRef objRelRef = mask_ $ do
  sigActions <- atomicModifyIORef' sigRelRef (\old -> ([], old))
  sigOutcomes <- mapM (\act -> try act :: IO (Either SomeException ())) sigActions
  let sigErrors = [err | Left err <- sigOutcomes]
  -- Only destroy/unref GTK objects once every connected signal closure has
  -- confirmed retirement via GClosureNotify; otherwise quarantine the objects
  -- and report the cleanup failure upward.
  if not (null sigErrors)
    then pure sigErrors
    else do
      objActions <- atomicModifyIORef' objRelRef (\old -> ([], old))
      objOutcomes <- mapM (\act -> try act :: IO (Either SomeException ())) objActions
      pure [err | Left err <- objOutcomes]

-- | Pack the three role WebKitWebViews into one undecorated GTK4 window
-- (zero GTK headerbar, title text, or buttons; all GUI is rendered in Elm).
-- Runs masked so no async exception can separate acquisition from release registration.
attachMvpWindow :: MvpViews view -> IO MvpWindow
attachMvpWindow views = mask $ \_ -> do
  let cView = castPtr (mvpControllerView views) :: Ptr MvpObject
      bView = castPtr (mvpBarView views) :: Ptr MvpObject
      pView = castPtr (mvpPopupView views) :: Ptr MvpObject
  unless
    ( cView /= nullPtr
        && bView /= nullPtr
        && pView /= nullPtr
        && cView /= bView
        && cView /= pView
        && bView /= pView
    )
    (ioError (userError "MVP requires three distinct non-null WebKitWebView pointers"))
  sigReleases <- newIORef ([] :: [IO ()])
  objReleases <- newIORef ([] :: [IO ()])
  closeRef <- newIORef False
  escapeRef <- newIORef False
  stateRef <- newIORef initialMvpState
  retiredRef <- newIORef False
  let acquireObj acquire release = mask_ $ do
        val <- acquire
        modifyIORef' objReleases (release val :)
        pure val
      acquireSignal obj sigName mkCb freeCb = mask_ $ do
        disconnect <- connectOwnedMvpSignal obj sigName mkCb freeCb
        modifyIORef' sigReleases (disconnect :)
      abortAttach = mask_ $ do
        writeIORef retiredRef True
        errs <- runCleanupSequence sigReleases objReleases
        case [e | e <- errs, Just _ <- [fromException e :: Maybe SomeAsyncException]] of
          asyncErr : _ -> throwIO asyncErr
          [] -> pure ()
  ( do
      vertical <- resolveEnumValue gtkOrientationGetType "GTK_ORIENTATION_VERTICAL"
      capturePhase <- resolveEnumValue gtkPropagationPhaseGetType "GTK_PHASE_CAPTURE"
      box <- acquireObj (gtkBoxNew vertical 0 >>= (`mustPtr` "MVP GtkBox") >>= gObjectRefSink) gObjectUnref
      window <-
        acquireObj
          (gtkWindowNew >>= (`mustPtr` "MVP GtkWindow") >>= gObjectRefSink)
          (\win -> gtkWindowDestroy win >> gObjectUnref win)

      -- Undecorated: suppresses GTK4 client-side headerbar, title label, and buttons.
      gtkWindowSetDecorated window 0
      gtkWindowSetResizable window 1
      gtkWindowSetDefaultSize window 980 680

      acquireSignal
        window
        "close-request"
        (wrapCloseRequest $ \_ _ -> mask_ (writeIORef closeRef True >> pure 1))
        freeHaskellFunPtr

      -- Capture-phase key observation sees physical Escape before WebKit can
      -- consume it, while returning 0 (GDK_EVENT_PROPAGATE) so normal typing
      -- and IME composition reach the focused WebKitWebView untouched.
      keyCtrl <- acquireObj (gtkEventControllerKeyNew >>= (`mustPtr` "MVP GtkEventControllerKey")) gObjectUnref
      gtkEventControllerSetPropagationPhase keyCtrl capturePhase
      acquireSignal
        keyCtrl
        "key-pressed"
        ( wrapKeyPressed $ \_ keyval _ _ _ -> mask_ $ do
            if keyval == gdkKeyEscape
              then writeIORef escapeRef True
              else pure ()
            pure 0
        )
        freeHaskellFunPtr

      -- gtk_widget_add_controller is [transfer full]; pass an extra ref inside
      -- this masked region so objReleases retains ownership until signal retirement.
      transferredCtrl <- gObjectRef keyCtrl >>= (`mustPtr` "MVP key controller ref")
      gtkWidgetAddController window transferredCtrl

      -- Bar strip at top of window.
      gtkWidgetSetHexpand bView 1
      gtkWidgetSetVexpand bView 0
      gtkWidgetSetSizeRequest bView (-1) 72
      gtkWidgetSetVisible bView 1
      gtkBoxAppend box bView

      -- Popup/Applications workspace fills primary window body.
      gtkWidgetSetHexpand pView 1
      gtkWidgetSetVexpand pView 1
      gtkWidgetSetSizeRequest pView 640 480
      gtkWidgetSetVisible pView 1
      gtkBoxAppend box pView

      -- Controller runs HttpMain policy loop in a realized 1x1 untargetable cell.
      gtkWidgetSetHexpand cView 0
      gtkWidgetSetVexpand cView 0
      gtkWidgetSetSizeRequest cView 1 1
      gtkWidgetSetOpacity cView (CDouble 0.0)
      gtkWidgetSetFocusable cView 0
      gtkWidgetSetCanTarget cView 0
      gtkWidgetSetVisible cView 1
      gtkBoxAppend box cView

      gtkWindowSetChild window box
      gtkWindowPresent window

      pure
        MvpWindow
          { mvpGtkWindow = window
          , mvpCloseRef = closeRef
          , mvpEscapeRef = escapeRef
          , mvpStateRef = stateRef
          , mvpRetiredRef = retiredRef
          , mvpSignalReleasesRef = sigReleases
          , mvpObjectReleasesRef = objReleases
          }
    )
    `onException` abortAttach

-- | Observe live GTK4/GDK4 mapped surface dimensions and Wayland monitor geometry.
-- Never falls back to requested widget dimensions when GdkSurface lacks a positive allocation.
observeGtkWindow :: MvpWindow -> IO ViewObservation
observeGtkWindow mvp = do
  retired <- readIORef (mvpRetiredRef mvp)
  if retired
    then pure ViewUnmapped
    else do
      let win = mvpGtkWindow mvp
      widgetMapped <- gtkWidgetGetMapped win
      if widgetMapped == 0
        then pure ViewUnmapped
        else do
          nativePtr <- gtkWidgetGetNative win
          if nativePtr == nullPtr
            then pure ViewUnmapped
            else do
              surfacePtr <- gtkNativeGetSurface nativePtr
              if surfacePtr == nullPtr
                then pure ViewUnmapped
                else do
                  surfMapped <- gdkSurfaceGetMapped surfacePtr
                  if surfMapped == 0
                    then pure ViewUnmapped
                    else do
                      surfW <- gdkSurfaceGetWidth surfacePtr
                      surfH <- gdkSurfaceGetHeight surfacePtr
                      case (,) <$> cIntToInt32 surfW <*> cIntToInt32 surfH >>= uncurry makeSurfaceSize of
                        Left _ -> pure ViewUnmapped
                        Right surfSize -> do
                          activeFlag <- gtkWindowIsActive win
                          mMon <- observeSurfaceMonitor surfacePtr
                          pure
                            ViewMapped
                              { observedSurface = surfSize
                              , observedActive = activeFlag /= 0
                              , observedMonitor = mMon
                              }

observeSurfaceMonitor :: Ptr MvpObject -> IO (Maybe MonitorBox)
observeSurfaceMonitor surfacePtr = do
  displayPtr <- gdkSurfaceGetDisplay surfacePtr
  if displayPtr == nullPtr
    then pure Nothing
    else do
      monitorPtr <- gdkDisplayGetMonitorAtSurface displayPtr surfacePtr
      if monitorPtr == nullPtr
        then pure Nothing
        else do
          valid <- gdkMonitorIsValid monitorPtr
          if valid == 0
            then pure Nothing
            else allocaArray 4 $ \rectPtr -> do
              fillBytes rectPtr 0 (4 * cIntByteSize)
              gdkMonitorGetGeometry monitorPtr rectPtr
              mx <- peekElemOff rectPtr 0
              my <- peekElemOff rectPtr 1
              mw <- peekElemOff rectPtr 2
              mh <- peekElemOff rectPtr 3
              let checked = do
                    x32 <- cIntToInt32 mx
                    y32 <- cIntToInt32 my
                    w32 <- cIntToInt32 mw
                    h32 <- cIntToInt32 mh
                    makeMonitorBox x32 y32 w32 h32
              pure $
                case checked of
                  Right box -> Just box
                  Left _ -> Nothing

-- | Poll whether the user/compositor requested closing the MVP window.
mvpCloseRequested :: MvpWindow -> IO Bool
mvpCloseRequested = readIORef . mvpCloseRef

-- | Observe the GTK window once and dispatch resulting 'TrustedOwnerEvent' values
-- transactionally. State fields advance ONLY for events actually accepted by 'emit':
--   * On close/unmap, a stale 'OwnerDismiss' refusal drops only the stale dismiss
--     and still dispatches 'OwnerTopology' @[]@ so view retirement is never skipped.
--   * On steady mapped ticks, a stale 'OwnerReflow' or 'OwnerEscape' refusal leaves
--     'stateLastSize', 'stateLastReflow', and 'stateLastEscape' uncommitted, never
--     invents a successful event count, and surfaces @Left "stale native UI projection"@
--     when zero events were accepted.
stepMvpWindow
  :: MvpWindow
  -> IO (Maybe SurfaceLease)
  -> (TrustedOwnerEvent -> IO (Either Text ()))
  -> IO (Either Text Int)
stepMvpWindow mvp readLease emit = do
  escapeFlag <- atomicModifyIORef' (mvpEscapeRef mvp) (\old -> (False, old))
  closeFlag <- readIORef (mvpCloseRef mvp)
  obs <- observeGtkWindow mvp
  mLease <- readLease
  curState <- readIORef (mvpStateRef mvp)
  if stateTopology curState == TopologyClosed
    then pure (Right 0)
    else
      if closeFlag
        then stepRetireOrClose TopologyClosed mLease curState
        else
          case (stateTopology curState, obs) of
            (TopologyNone, ViewUnmapped) ->
              pure (Right 0)
            (TopologyUnretiredEmpty, ViewUnmapped) ->
              pure (Right 0)
            (TopologyMapped _ _ _, ViewUnmapped) ->
              stepRetireOrClose TopologyUnretiredEmpty mLease curState
            (TopologyNone, ViewMapped surf0 _ mMon0) ->
              stepFreshMap surf0 mMon0 curState
            (TopologyUnretiredEmpty, ViewMapped surf0 _ mMon0) ->
              stepFreshMap surf0 mMon0 curState
            (TopologyMapped scopeId gen prevMon, ViewMapped surf _ curMon)
              | curMon /= prevMon ->
                  stepMonitorUpdate scopeId gen curMon curState
              | otherwise ->
                  stepSteadyMapped scopeId gen surf escapeFlag mLease curState
            (TopologyClosed, _) ->
              pure (Right 0)
  where
    stateRef = mvpStateRef mvp

    stepRetireOrClose targetTopo leaseSnap prior =
      case stateTopology prior of
        TopologyMapped scopeId gen _ -> do
          dismissOutcome <-
            case matchingOpenLease scopeId gen (stateRevision prior) leaseSnap of
              Nothing -> pure (Right 0)
              Just lease -> do
                res <- emit (OwnerDismiss (encodeDismiss scopeId gen (leaseToken lease)))
                pure $
                  case res of
                    Right () -> Right 1
                    Left reason | isStaleOwnerProjection reason -> Right 0
                    Left fatal -> Left fatal
          case dismissOutcome of
            Left fatal -> pure (Left fatal)
            Right dismissAccepted ->
              case nextCounter (stateRevision prior) of
                Left counterErr -> pure (Left counterErr)
                Right rev -> do
                  topoRes <- emit (OwnerTopology (encodeEmptyTopology rev))
                  case topoRes of
                    Left fatal -> pure (Left fatal)
                    Right () -> do
                      writeIORef
                        stateRef
                        prior
                          { stateRevision = Just rev
                          , stateTopology = targetTopo
                          , stateLastSize = Nothing
                          , stateLastReflow = Nothing
                          , stateLastEscape = Nothing
                          }
                      pure (Right (dismissAccepted + 1))
        _ -> do
          writeIORef
            stateRef
            prior
              { stateTopology = targetTopo
              , stateLastSize = Nothing
              , stateLastReflow = Nothing
              , stateLastEscape = Nothing
              }
          pure (Right 0)

    stepFreshMap surf0 mMon0 prior =
      case admitFreshMap surf0 mMon0 prior of
        Left counterErr -> pure (Left counterErr)
        Right (nextSt, topoEv) -> do
          res <- emit topoEv
          case res of
            Left fatal -> pure (Left fatal)
            Right () -> do
              writeIORef stateRef nextSt
              pure (Right 1)

    stepMonitorUpdate scopeId gen curMon prior =
      case nextCounter (stateRevision prior) of
        Left counterErr -> pure (Left counterErr)
        Right rev -> do
          let payload = encodeMappedTopology rev scopeId gen curMon
              nextSt = prior
                { stateRevision = Just rev
                , stateTopology = TopologyMapped scopeId gen curMon
                , stateLastReflow = Nothing
                , stateLastEscape = Nothing
                }
          res <- emit (OwnerTopology payload)
          case res of
            Left fatal -> pure (Left fatal)
            Right () -> do
              writeIORef stateRef nextSt
              pure (Right 1)

    stepSteadyMapped scopeId gen surf escapePressed leaseSnap prior =
      case matchingScopeLease scopeId gen (stateRevision prior) leaseSnap of
        Nothing ->
          pure (Right 0)
        Just lease
          | not (leasePopupOpen lease) || isZero (leaseToken lease) -> do
              writeIORef
                stateRef
                prior
                  { stateLastSize = Just surf
                  , stateLastReflow = Nothing
                  , stateLastEscape = Nothing
                  }
              pure (Right 0)
          | otherwise -> do
              let sizeChanged =
                    case stateLastSize prior of
                      Just prevSurf -> surf /= prevSurf
                      Nothing -> True
                  needReflow =
                    sizeChanged && stateLastReflow prior /= Just (leaseToken lease, surf)
                  needEscape =
                    escapePressed
                      && stateLastEscape prior /= Just (leasePublication lease, leaseToken lease)
              reflowStep <-
                if not needReflow
                  then pure (Right (prior, 0, False))
                  else do
                    res <- emit (OwnerReflow (encodeReflow scopeId gen (leaseToken lease)))
                    case res of
                      Right () -> do
                        let updated =
                              prior
                                { stateLastSize = Just surf
                                , stateLastReflow = Just (leaseToken lease, surf)
                                }
                        writeIORef stateRef updated
                        pure (Right (updated, 1, False))
                      Left reason | isStaleOwnerProjection reason ->
                        pure (Right (prior, 0, True))
                      Left fatal ->
                        pure (Left fatal)
              case reflowStep of
                Left fatal -> pure (Left fatal)
                Right (afterReflow, reflowAccepted, reflowStale) ->
                  if not needEscape || reflowStale
                    then
                      pure $
                        if reflowAccepted == 0 && reflowStale
                          then Left staleOwnerProjectionMessage
                          else Right reflowAccepted
                    else do
                      escRes <-
                        emit
                          ( OwnerEscape
                              (encodeEscape scopeId gen (leasePublication lease) (leaseToken lease))
                          )
                      case escRes of
                        Right () -> do
                          let updated =
                                afterReflow
                                  { stateLastEscape = Just (leasePublication lease, leaseToken lease)
                                  }
                          writeIORef stateRef updated
                          pure (Right (reflowAccepted + 1))
                        Left reason | isStaleOwnerProjection reason ->
                          pure $
                            if reflowAccepted == 0
                              then Left staleOwnerProjectionMessage
                              else Right reflowAccepted
                        Left fatal ->
                          pure (Left fatal)

-- | Disconnect MVP window signals (requiring GClosureNotify receipts) and destroy
-- the GTK container in LIFO order. Quarantines objects if any signal retirement
-- is uncertain. Never alters WebKit filter-store or provider cleanup status.
retireMvpWindow :: MvpWindow -> IO ()
retireMvpWindow mvp = mask_ $ do
  already <- atomicModifyIORef' (mvpRetiredRef mvp) (\old -> (True, old))
  unless already $ do
    errs <- runCleanupSequence (mvpSignalReleasesRef mvp) (mvpObjectReleasesRef mvp)
    case [e | e <- errs, Just _ <- [fromException e :: Maybe SomeAsyncException]] of
      asyncErr : _ -> throwIO asyncErr
      [] ->
        case errs of
          firstErr : _ -> ioError (userError (show firstErr))
          [] -> pure ()
