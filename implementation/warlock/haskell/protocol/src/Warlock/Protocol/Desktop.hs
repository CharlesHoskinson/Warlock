{-# LANGUAGE OverloadedStrings #-}
-- Application data only. No decoded commit or reply grants native authority.
module Warlock.Protocol.Desktop
  ( DesktopCommit, decodeDesktopCommit, encodeDesktopCommit, commitRequests, commitProjection, commitFocus
  , DesktopRequest, RequestKind(..), requestKind, requestBinding, requestId, pinProposal
  , NotificationVerb(..), NotificationTarget, notificationTarget, notificationService, notificationId, notificationIncarnation, notificationProducer, notificationAction, notificationVerb
  , LaunchIntent, launchIntent, launchRequest, launchLifetime, launchGeneration, launchEntry
  , LaunchStatus(..), LaunchRefusal(..), launchReply, launchOutcome
  , PinSnapshot, pinSnapshot, pinRevision, pinIdentities, decodePinSnapshot, encodePinSnapshot
  , CatalogEntry, catalogEntry, CatalogSnapshot, catalogSnapshot
  , WindowSnapshot, windowSnapshot, windowObservationReply, applicationAttachedWithWindowObservation
  , windowWatchRevision, windowWatchReply, applicationAttachedWithWindowWatch
  , notificationSnapshotReply, notificationOutcomeReply, applicationAttachedWithNotificationService
  , DesktopReply, PinStatus(..), ApplicationAvailability(..), applicationAttached, applicationAttachedWithAvailability, applicationAttachedWithLocalNotifications, applicationAvailability, catalogReply, pinsReply, replyBinding
  , decodeDesktopReply, encodeDesktopReply, decodeDesktopGateway, encodeDesktopGateway, popupControl ) where

import qualified Data.ByteString as B
import Data.Char (ord, isAscii, isAlphaNum)
import qualified Data.Set as Set
import Data.Text (Text)
import qualified Data.Text as T
import qualified Data.Text.Encoding as TE
import Warlock.Protocol.Identity
import Warlock.Protocol.StrictJson
import Warlock.Protocol.Wire (parseBinding)

data RequestKind = CatalogRead | PinsWrite | ApplicationLaunch | NotificationRead | NotificationEffect | WindowRead | WindowWatch deriving (Eq, Show)
data NotificationVerb = NotificationInvoke | NotificationDismiss deriving (Eq, Show)
-- Checked wire data only; actual service ownership and current producer custody
-- must still be established by the backend before any effect.
data NotificationTarget = NotificationTarget Counter Counter Counter Text Text NotificationVerb deriving (Eq, Show)
data LaunchIntent = LaunchIntent Counter Counter Counter Text deriving (Eq, Show)
data LaunchRefusal = RetiredAuthority | RequestReuse | RetiredRequest | CatalogUnavailable | StaleCatalog | RemovedEntry | NativeEntryUnavailable | DesktopEntryRaced deriving (Eq, Show)
data LaunchStatus = LaunchSubmitted | LaunchUnknown | LaunchRefused LaunchRefusal deriving (Eq, Show)
data PinSnapshot = PinSnapshot Counter [Text] deriving (Eq, Show)
data DesktopRequest = CatalogRequest Binding Counter | PinsRequest Binding Counter PinSnapshot | LaunchRequest Binding LaunchIntent
                    | WindowReadRequest Binding Counter
                    | WindowWatchRequest Binding Counter Counter
                    | NotificationHistoryRequest Binding Counter
                    | NotificationActionRequest Binding Counter NotificationTarget deriving (Eq, Show)
newtype WindowSnapshot = WindowSnapshot Json deriving (Eq, Show)
data DesktopCommit = DesktopCommit Json [DesktopRequest] [Text] deriving (Eq, Show)
data CatalogEntry = CatalogEntry Text Text Text Text Text [Text] deriving (Eq, Show)
data CatalogSnapshot = CatalogSnapshot Counter Counter [CatalogEntry] deriving (Eq, Show)
data PinStatus = PinSaved | PinRefused | PinUnknown deriving (Eq, Show)
-- Availability DATA only; this never constructs native/window admission.
data ApplicationAvailability = ApplicationUnavailable | ApplicationLaunchAvailable deriving (Eq,Show)
data DesktopReply = CatalogReply Binding Counter (Maybe CatalogSnapshot) (Maybe PinSnapshot)
                  | PinsReply Binding Counter PinStatus (Maybe PinSnapshot)
                  | LaunchReply Binding LaunchIntent LaunchStatus
                  | ApplicationAttached Binding (Maybe ApplicationAvailability)
                  | LocalNotificationsAttached Binding ApplicationAvailability
                  | NotificationCapabilitiesAttached Binding ApplicationAvailability Bool Bool
                  | WindowObservationAttached Binding ApplicationAvailability Bool (Maybe Bool) Bool
                  | WindowObservationReply Binding Counter Text (Maybe WindowSnapshot)
                  | WindowWatchAttached Binding ApplicationAvailability Bool (Maybe Bool)
                  | WindowWatchReply Binding Counter Counter Text (Maybe WindowSnapshot)
                  | NotificationSnapshotReply Binding Counter Json
                  | NotificationOutcomeReply Binding Counter Text Json (Maybe Text)
                  | PreviewGrant Binding Counter Int
                  | PreviewQuarantine Binding Counter
                  | PreviewClosed Binding Counter deriving (Eq, Show)

err :: Show a => Either a b -> Either Text b
err = either (Left . T.pack . show) Right
require :: Bool -> Text -> Either Text ()
require yes reason = if yes then Right () else Left reason
object :: [Text] -> Json -> Either Text [(Text,Json)]
object names = err . exactObject names
field :: Text -> [(Text,Json)] -> Either Text Json
field key fields = maybe (Left "missing field") Right (lookup key fields)
textValue :: Json -> Either Text Text
textValue (JString value) = Right value
textValue _ = Left "string required"
counter :: Json -> Either Text Counter
counter value = textValue value >>= err . parseCounter False
positive :: Counter -> Either Text ()
positive value = require (not (isZero value)) "zero authority counter"
fixed :: Json -> Json -> Either Text ()
fixed expected actual = require (expected == actual) "unsupported version or kind"
array :: Json -> Either Text [Json]
array (JArray values) = Right values
array _ = Left "array required"
optional :: (Json -> Either Text a) -> Json -> Either Text (Maybe a)
optional _ JNull = Right Nothing
optional parser value = Just <$> parser value
jsonBytes :: Json -> B.ByteString
jsonBytes = TE.encodeUtf8 . renderJson
decodeBounded :: Int -> B.ByteString -> Either Text Json
decodeBounded limit raw = do
  b <- err (bounds limit 16)
  value <- err (decodeStrict b raw)
  source <- err (TE.decodeUtf8' raw)
  require (utf16Length source <= limit) "UTF16 envelope capacity"
  pure value
encodeBounded :: Int -> Json -> Either Text B.ByteString
encodeBounded limit value = do
  let raw = jsonBytes value
  _ <- decodeBounded limit raw
  pure raw

-- Opaque identities never become paths or command fragments at this boundary.
pinIdentity :: Text -> Bool
pinIdentity value = not (T.null value) && utf16Length value <= 256
  && value /= "." && value /= ".."
  && not (T.any (\c -> ord c < 32 || ord c == 127 || c `elem` ("/\\:'\"`$;&|<>(){}[]*?!~#" :: String)) value)
pinSnapshot :: Counter -> [Text] -> Either Text PinSnapshot
pinSnapshot revision identities = do
  positive revision
  require (length identities <= 32 && all pinIdentity identities && Set.size (Set.fromList identities) == length identities) "pin identities"
  require (B.length (jsonBytes (JArray (map JString identities))) <= 3000) "pin byte capacity"
  pure (PinSnapshot revision identities)
pinRevision :: PinSnapshot -> Counter
pinRevision (PinSnapshot revision _) = revision
pinIdentities :: PinSnapshot -> [Text]
pinIdentities (PinSnapshot _ identities) = identities
pinJson :: PinSnapshot -> Json
pinJson (PinSnapshot revision identities) = JObject [("revision",JString (renderCounter revision)),("identities",JArray (map JString identities))]
parsePins :: Json -> Either Text PinSnapshot
parsePins value = do
  fields <- object ["revision","identities"] value
  revision <- field "revision" fields >>= counter
  identities <- field "identities" fields >>= array >>= mapM textValue
  pinSnapshot revision identities
decodePinSnapshot :: B.ByteString -> Either Text PinSnapshot
decodePinSnapshot raw = decodeBounded 8192 raw >>= parsePins
encodePinSnapshot :: PinSnapshot -> B.ByteString
encodePinSnapshot = jsonBytes . pinJson

requestKind :: DesktopRequest -> RequestKind
requestKind (CatalogRequest _ _) = CatalogRead
requestKind (PinsRequest _ _ _) = PinsWrite
requestKind (LaunchRequest _ _) = ApplicationLaunch
requestKind (WindowReadRequest _ _) = WindowRead
requestKind (WindowWatchRequest _ _ _) = WindowWatch
requestKind (NotificationHistoryRequest _ _) = NotificationRead
requestKind (NotificationActionRequest _ _ _) = NotificationEffect
requestBinding :: DesktopRequest -> Binding
requestBinding (CatalogRequest owner _) = owner
requestBinding (PinsRequest owner _ _) = owner
requestBinding (LaunchRequest owner _) = owner
requestBinding (WindowReadRequest owner _) = owner
requestBinding (WindowWatchRequest owner _ _) = owner
requestBinding (NotificationHistoryRequest owner _) = owner
requestBinding (NotificationActionRequest owner _ _) = owner
requestId :: DesktopRequest -> Counter
requestId (CatalogRequest _ request) = request
requestId (PinsRequest _ request _) = request
requestId (LaunchRequest _ intent) = launchRequest intent
requestId (WindowReadRequest _ request) = request
requestId (WindowWatchRequest _ request _) = request
requestId (NotificationHistoryRequest _ request) = request
requestId (NotificationActionRequest _ request _) = request
pinProposal :: DesktopRequest -> Maybe PinSnapshot
pinProposal (CatalogRequest _ _) = Nothing
pinProposal (PinsRequest _ _ proposal) = Just proposal
pinProposal (LaunchRequest _ _) = Nothing
pinProposal (WindowReadRequest _ _) = Nothing
pinProposal (WindowWatchRequest _ _ _) = Nothing
pinProposal (NotificationHistoryRequest _ _) = Nothing
pinProposal (NotificationActionRequest _ _ _) = Nothing
launchIntent :: DesktopRequest -> Maybe LaunchIntent
launchIntent (LaunchRequest _ intent) = Just intent
launchIntent _ = Nothing
launchRequest, launchLifetime, launchGeneration :: LaunchIntent -> Counter
launchRequest (LaunchIntent request _ _ _) = request
launchLifetime (LaunchIntent _ life _ _) = life
launchGeneration (LaunchIntent _ _ generation _) = generation
launchEntry :: LaunchIntent -> Text
launchEntry (LaunchIntent _ _ _ entry) = entry
parseLaunchIntent :: Json -> Either Text LaunchIntent
parseLaunchIntent value = do
  fields <- object ["request","lifetime","generation","entry"] value
  request <- field "request" fields >>= counter
  life <- field "lifetime" fields >>= counter
  generation <- field "generation" fields >>= counter
  entry <- field "entry" fields >>= textValue
  require (not (T.null entry) && utf16Length entry <= 256 && not (T.any ((<32) . ord) entry)) "launch identity"
  pure (LaunchIntent request life generation entry)
launchIntentJson :: LaunchIntent -> Json
launchIntentJson (LaunchIntent request life generation entry) = JObject
  [("request",JString (renderCounter request)),("lifetime",JString (renderCounter life)),("generation",JString (renderCounter generation)),("entry",JString entry)]
notificationTarget :: DesktopRequest -> Maybe NotificationTarget
notificationTarget (NotificationActionRequest _ _ target) = Just target
notificationTarget _ = Nothing
notificationService, notificationId, notificationIncarnation :: NotificationTarget -> Counter
notificationService (NotificationTarget value _ _ _ _ _) = value
notificationId (NotificationTarget _ value _ _ _ _) = value
notificationIncarnation (NotificationTarget _ _ value _ _ _) = value
notificationProducer, notificationAction :: NotificationTarget -> Text
notificationProducer (NotificationTarget _ _ _ value _ _) = value
notificationAction (NotificationTarget _ _ _ _ value _) = value
notificationVerb :: NotificationTarget -> NotificationVerb
notificationVerb (NotificationTarget _ _ _ _ _ value) = value

parseNotificationTarget :: Json -> Either Text NotificationTarget
parseNotificationTarget value = do
  fields <- object ["service","id","incarnation","producer","action","verb"] value
  service <- field "service" fields >>= counter
  ident <- field "id" fields >>= counter
  incarnation <- field "incarnation" fields >>= counter
  producer <- field "producer" fields >>= textValue
  action <- field "action" fields >>= textValue
  verbText <- field "verb" fields >>= textValue
  -- D-Bus notification identifiers are uint32; the shared counter remains opaque.
  let identifier = reads (T.unpack (renderCounter ident)) :: [(Integer,String)]
  require (case identifier of [(number,"")] -> number <= 4294967295; _ -> False) "notification id exceeds uint32"
  require (T.length producer <= 128 && T.isPrefixOf ":" producer && uniqueName (T.drop 1 producer)) "notification unique producer"
  require (utf16Length action <= 64 && not (T.any (\c -> ord c < 32 || ord c == 127) action)) "notification action"
  verb <- case verbText of
    "invoke" | not (T.null action) -> Right NotificationInvoke
    "dismiss" | T.null action -> Right NotificationDismiss
    _ -> Left "notification verb/action"
  pure (NotificationTarget service ident incarnation producer action verb)
 where
  uniqueName name = let parts = T.splitOn "." name
                    in length parts >= 2 && all (\part -> not (T.null part) && T.all (\c -> isAscii c && (isAlphaNum c || c == '_' || c == '-')) part) parts

parseRequest :: Json -> Either Text DesktopRequest
parseRequest value = do
  require (B.length (jsonBytes value) <= 8192) "desktop request capacity"
  fields <- case value of JObject pairs -> Right pairs; _ -> Left "request object required"
  field "protocolVersion" fields >>= fixed (JNumber "3")
  kind <- field "kind" fields >>= textValue
  case kind of
    "application-launch" -> do
      exact <- object ["protocolVersion","kind","binding","intent"] value
      owner <- field "binding" exact >>= parseBinding
      intent <- field "intent" exact >>= parseLaunchIntent
      pure (LaunchRequest owner intent)
    "catalog-request" -> do
      exact <- object ["protocolVersion","kind","binding","requestId"] value
      owner <- field "binding" exact >>= parseBinding
      request <- field "requestId" exact >>= counter
      pure (CatalogRequest owner request)
    "taskbar-pins-write" -> do
      exact <- object ["protocolVersion","kind","binding","requestId","proposal"] value
      owner <- field "binding" exact >>= parseBinding
      request <- field "requestId" exact >>= counter
      PinsRequest owner request <$> (field "proposal" exact >>= parsePins)
    "window-watch" -> do
      exact <- object ["protocolVersion","kind","binding","requestId","observedRevision"] value
      owner <- field "binding" exact >>= parseBinding
      request <- field "requestId" exact >>= counter
      observed <- field "observedRevision" exact >>= counter
      positive request
      positive observed
      pure (WindowWatchRequest owner request observed)
    "window-read" -> do
      exact <- object ["protocolVersion","kind","binding","requestId"] value
      owner <- field "binding" exact >>= parseBinding
      request <- field "requestId" exact >>= counter
      pure (WindowReadRequest owner request)
    "notification-request" -> do
      exact <- object ["protocolVersion","kind","binding","requestId"] value
      owner <- field "binding" exact >>= parseBinding
      request <- field "requestId" exact >>= counter
      pure (NotificationHistoryRequest owner request)
    "notification-effect" -> do
      exact <- object ["protocolVersion","kind","binding","requestId","intent"] value
      owner <- field "binding" exact >>= parseBinding
      request <- field "requestId" exact >>= counter
      target <- field "intent" exact >>= parseNotificationTarget
      pure (NotificationActionRequest owner request target)
    _ -> Left "unsupported desktop request kind"
decodeDesktopCommit :: B.ByteString -> Either Text DesktopCommit
decodeDesktopCommit raw = do
  value <- decodeBounded 131072 raw
  fields <- object ["viewProtocol","kind","projection","requests","focus"] value
  field "viewProtocol" fields >>= fixed (JNumber "1")
  field "kind" fields >>= fixed (JString "view-commit")
  projection <- field "projection" fields
  case projection of JObject _ -> pure (); _ -> Left "projection object required"
  requests <- field "requests" fields >>= array
  require (length requests <= 16) "commit request capacity"
  checked <- mapM parseRequest requests
  focus <- field "focus" fields >>= array >>= mapM textValue
  pure (DesktopCommit value checked focus)
encodeDesktopCommit :: DesktopCommit -> Either Text B.ByteString
encodeDesktopCommit (DesktopCommit value _ _) = encodeBounded 131072 value
commitRequests :: DesktopCommit -> [DesktopRequest]
commitRequests (DesktopCommit _ requests _) = requests
commitProjection :: DesktopCommit -> Json
commitProjection (DesktopCommit value _ _) = case value of
  JObject fields -> maybe JNull id (lookup "projection" fields)
  _ -> JNull
commitFocus :: DesktopCommit -> [Text]
commitFocus (DesktopCommit _ _ focus) = focus

boundedText :: Int -> Bool -> Text -> Bool
boundedText limit nonempty value = utf16Length value <= limit && (not nonempty || not (T.null value)) && not (T.any ((<32) . ord) value)
catalogEntry :: Text -> Text -> Text -> Text -> Text -> [Text] -> Either Text CatalogEntry
catalogEntry identity name icon wmclass generic keywords = do
  require (boundedText 256 True identity && all (boundedText 512 False) [name,icon,wmclass,generic]) "catalog entry text"
  require (length keywords <= 64 && all (boundedText 128 False) keywords) "catalog keywords"
  pure (CatalogEntry identity name icon wmclass generic keywords)
catalogSnapshot :: Counter -> Counter -> [CatalogEntry] -> Either Text CatalogSnapshot
catalogSnapshot life generation entries = do
  positive life
  positive generation
  let identities = [identity | CatalogEntry identity _ _ _ _ _ <- entries]
  require (length entries <= 2048 && Set.size (Set.fromList identities) == length entries) "catalog identities"
  pure (CatalogSnapshot life generation entries)
entryJson :: CatalogEntry -> Json
entryJson (CatalogEntry identity name icon wmclass generic keywords) = JObject
  [("id",JString identity),("name",JString name),("iconHint",JString icon),("wmclass",JString wmclass),("genericName",JString generic),("keywords",JArray (map JString keywords))]
catalogJson :: CatalogSnapshot -> Json
catalogJson (CatalogSnapshot life generation entries) = JObject
  [("catalogProtocol",JNumber "2"),("lifetime",JString (renderCounter life)),("generation",JString (renderCounter generation)),("entries",JArray (map entryJson entries))]
parseEntry :: Json -> Either Text CatalogEntry
parseEntry value = do
  fields <- object ["id","name","iconHint","wmclass","genericName","keywords"] value
  identity <- field "id" fields >>= textValue
  name <- field "name" fields >>= textValue
  icon <- field "iconHint" fields >>= textValue
  wmclass <- field "wmclass" fields >>= textValue
  generic <- field "genericName" fields >>= textValue
  keywords <- field "keywords" fields >>= array >>= mapM textValue
  catalogEntry identity name icon wmclass generic keywords
parseCatalog :: Json -> Either Text CatalogSnapshot
parseCatalog value = do
  fields <- object ["catalogProtocol","lifetime","generation","entries"] value
  field "catalogProtocol" fields >>= fixed (JNumber "2")
  life <- field "lifetime" fields >>= counter
  generation <- field "generation" fields >>= counter
  raw <- field "entries" fields >>= array
  require (length raw <= 2048) "catalog capacity"
  entries <- mapM parseEntry raw
  catalogSnapshot life generation entries
bindingJson :: Binding -> Json
bindingJson owner = JObject [("lifetime",JString (renderCounter (lifetime owner))),("session",JString (renderCounter (session owner))),("frontend",JString (renderCounter (frontend owner)))]
nullable :: (a -> Json) -> Maybe a -> Json
nullable f = maybe JNull f
replyBinding :: DesktopReply -> Binding
replyBinding (CatalogReply owner _ _ _) = owner
replyBinding (PinsReply owner _ _ _) = owner
replyBinding (LaunchReply owner _ _) = owner
replyBinding (ApplicationAttached owner _) = owner
replyBinding (LocalNotificationsAttached owner _) = owner
replyBinding (NotificationCapabilitiesAttached owner _ _ _) = owner
replyBinding (WindowObservationAttached owner _ _ _ _) = owner
replyBinding (WindowObservationReply owner _ _ _) = owner
replyBinding (WindowWatchAttached owner _ _ _) = owner
replyBinding (WindowWatchReply owner _ _ _ _) = owner
replyBinding (NotificationSnapshotReply owner _ _) = owner
replyBinding (NotificationOutcomeReply owner _ _ _ _) = owner
replyBinding (PreviewGrant owner _ _) = owner
replyBinding (PreviewQuarantine owner _) = owner
replyBinding (PreviewClosed owner _) = owner

-- These facts retain their authenticated peer binding. Projection creates no
-- grant: the existing Elm realm/presenter remains the lifetime authority.
popupControl :: DesktopReply -> Maybe (Text,Json)
popupControl reply = case reply of
  PreviewGrant owner epoch capacity -> Just ("native-preview-grant",JObject (domain owner epoch ++ [("capacity",JNumber (T.pack (show capacity)))]))
  PreviewQuarantine owner epoch -> Just ("native-preview-quarantine",JObject (domain owner epoch))
  PreviewClosed owner epoch -> Just ("native-preview-closed",JObject (domain owner epoch))
  _ -> Nothing
 where
  domain owner epoch = [("binding",bindingJson owner),("receiverEpoch",JString (renderCounter epoch))]
replyJson :: DesktopReply -> Json
replyJson reply = JObject $ [("protocolVersion",JNumber "3"),("binding",bindingJson (replyBinding reply))] ++ case reply of
  CatalogReply _ request catalog pins -> [("kind",JString "application-catalog"),("requestId",JString (renderCounter request)),("snapshot",nullable catalogJson catalog),("preferences",nullable pinJson pins)]
  PinsReply _ request status pins -> [("kind",JString "taskbar-pins-outcome"),("requestId",JString (renderCounter request)),("status",JString (case status of PinSaved -> "Saved"; PinRefused -> "Refused"; PinUnknown -> "Unknown")),("preferences",nullable pinJson pins)]
  LaunchReply _ intent status -> [("kind",JString "application-launch-outcome"),("outcome",launchOutcomeJson intent status)]
  ApplicationAttached _ selected -> [("kind",JString "application-attached"),("nativeOperations",JArray [])]
    ++ case selected of
      Nothing -> []
      Just availability -> [("applicationOperations",JArray (case availability of ApplicationUnavailable -> []; ApplicationLaunchAvailable -> [JString "application-launch"]))]
  LocalNotificationsAttached _ availability -> [("kind",JString "application-attached"),("nativeOperations",JArray []),("applicationOperations",JArray (case availability of ApplicationUnavailable -> []; ApplicationLaunchAvailable -> [JString "application-launch"])),("localOperations",JArray [JString "notification-policy"])]
  NotificationCapabilitiesAttached _ availability local ready ->
    [("kind",JString "application-attached"),("nativeOperations",JArray []),("applicationOperations",JArray (case availability of ApplicationUnavailable -> []; ApplicationLaunchAvailable -> [JString "application-launch"]))]
    ++ (if local then [("localOperations",JArray [JString "notification-policy"])] else [])
    ++ [("notificationOperations",JArray (if ready then [JString "notification-read",JString "notification-action"] else []))]
  WindowObservationAttached _ availability local notifications ready ->
    [("kind",JString "application-attached"),("nativeOperations",JArray []),("applicationOperations",JArray (case availability of ApplicationUnavailable -> []; ApplicationLaunchAvailable -> [JString "application-launch"]))]
    ++ (if local then [("localOperations",JArray [JString "notification-policy"])] else [])
    ++ maybe [] (\supported -> [("notificationOperations",JArray (if supported then [JString "notification-read",JString "notification-action"] else []))]) notifications
    ++ [("windowObservationOperations",JArray (if ready then [JString "window-read"] else []))]
  WindowWatchAttached _ availability local notifications ->
    [("kind",JString "application-attached"),("nativeOperations",JArray []),("applicationOperations",JArray (case availability of ApplicationUnavailable -> []; ApplicationLaunchAvailable -> [JString "application-launch"]))]
    ++ (if local then [("localOperations",JArray [JString "notification-policy"])] else [])
    ++ maybe [] (\ready -> [("notificationOperations",JArray (if ready then [JString "notification-read",JString "notification-action"] else []))]) notifications
    ++ [("windowObservationOperations",JArray [JString "window-read",JString "window-watch"])]
  WindowWatchReply _ request observedRevision status observed -> [("kind",JString "window-watch-result"),("requestId",JString (renderCounter request)),("observedRevision",JString (renderCounter observedRevision)),("status",JString status),("snapshot",nullable (\(WindowSnapshot value) -> value) observed)]
  WindowObservationReply _ request status observed -> [("kind",JString "window-observation"),("requestId",JString (renderCounter request)),("status",JString status),("snapshot",nullable (\(WindowSnapshot value) -> value) observed)]
  NotificationSnapshotReply _ request snapshot -> [("kind",JString "notification-snapshot"),("requestId",JString (renderCounter request)),("snapshot",snapshot)]
  NotificationOutcomeReply _ request status snapshot reason -> [("kind",JString "notification-outcome"),("requestId",JString (renderCounter request)),("status",JString status),("snapshot",snapshot)]
    ++ maybe [] (\value -> [("reason",JString value)]) reason
  PreviewGrant _ epoch capacity -> [("kind",JString "native-preview-grant"),("receiverEpoch",JString (renderCounter epoch)),("capacity",JNumber (T.pack (show capacity)))]
  PreviewQuarantine _ epoch -> [("kind",JString "native-preview-quarantine"),("receiverEpoch",JString (renderCounter epoch))]
  PreviewClosed _ epoch -> [("kind",JString "native-preview-closed"),("receiverEpoch",JString (renderCounter epoch))]
launchOutcomeJson :: LaunchIntent -> LaunchStatus -> Json
launchOutcomeJson intent status = JObject
  [("catalogProtocol",JNumber "1"),("kind",JString "launch-outcome"),("intent",launchIntentJson intent),("status",JString state),("reason",JString reason)]
 where
  (state,reason) = case status of
    LaunchSubmitted -> ("Submitted","native-submission-accepted")
    LaunchUnknown -> ("Unknown","submission-not-confirmed")
    LaunchRefused refusal -> ("Refused",case refusal of
      RetiredAuthority -> "retired-authority"; RequestReuse -> "request-reuse"
      RetiredRequest -> "retired-request"; CatalogUnavailable -> "catalog-unavailable"
      StaleCatalog -> "stale-catalog"; RemovedEntry -> "removed-entry"
      NativeEntryUnavailable -> "native-entry-unavailable"; DesktopEntryRaced -> "desktop-entry-raced")
parseLaunchOutcome :: Json -> Either Text (LaunchIntent,LaunchStatus)
parseLaunchOutcome value = do
  fields <- object ["catalogProtocol","kind","intent","status","reason"] value
  field "catalogProtocol" fields >>= fixed (JNumber "1")
  field "kind" fields >>= fixed (JString "launch-outcome")
  intent <- field "intent" fields >>= parseLaunchIntent
  state <- field "status" fields >>= textValue
  reason <- field "reason" fields >>= textValue
  status <- case (state,reason) of
    ("Submitted","native-submission-accepted") -> Right LaunchSubmitted
    ("Unknown","submission-not-confirmed") -> Right LaunchUnknown
    ("Refused","retired-authority") -> Right (LaunchRefused RetiredAuthority)
    ("Refused","request-reuse") -> Right (LaunchRefused RequestReuse)
    ("Refused","retired-request") -> Right (LaunchRefused RetiredRequest)
    ("Refused","catalog-unavailable") -> Right (LaunchRefused CatalogUnavailable)
    ("Refused","stale-catalog") -> Right (LaunchRefused StaleCatalog)
    ("Refused","removed-entry") -> Right (LaunchRefused RemovedEntry)
    ("Refused","native-entry-unavailable") -> Right (LaunchRefused NativeEntryUnavailable)
    ("Refused","desktop-entry-raced") -> Right (LaunchRefused DesktopEntryRaced)
    _ -> Left "unsupported launch outcome"
  pure (intent,status)
-- Inspection is data only; it does not establish receipt or effect authority.
launchOutcome :: DesktopReply -> Maybe (LaunchIntent,LaunchStatus)
launchOutcome (LaunchReply _ intent status) = Just (intent,status)
launchOutcome _ = Nothing

-- Typed application data only: construction grants no authority or effect.
launchReply :: Binding -> LaunchIntent -> LaunchStatus -> Either Text DesktopReply
launchReply owner intent status = do
  let reply = LaunchReply owner intent status
  _ <- encodeDesktopReply reply
  pure reply
-- Application attachment announces only the already authenticated application
-- binding. It creates no native authority or native operations.
applicationAttached :: Binding -> Either Text DesktopReply
applicationAttached owner = do
  let reply = ApplicationAttached owner Nothing
  _ <- encodeDesktopReply reply
  pure reply
-- Explicit new producer uses this constructor even for the empty list.
-- Legacy constructor retains old wire bytes; legacy absence decodes unavailable.
applicationAttachedWithAvailability :: Binding -> ApplicationAvailability -> Either Text DesktopReply
applicationAttachedWithAvailability owner available = do
 let reply = ApplicationAttached owner (Just available)
 _ <- encodeDesktopReply reply
 pure reply
-- Local UI session policy only: no notification service, producer or native authority.
-- Keep the old constructor's exact wire behavior for legacy callers.
applicationAttachedWithLocalNotifications :: Binding -> ApplicationAvailability -> Either Text DesktopReply
applicationAttachedWithLocalNotifications owner available = do
 let reply = LocalNotificationsAttached owner available
 _ <- encodeDesktopReply reply
 pure reply
applicationAvailability :: DesktopReply -> Maybe ApplicationAvailability
applicationAvailability (ApplicationAttached _ selected) = Just (maybe ApplicationUnavailable id selected)
applicationAvailability (LocalNotificationsAttached _ selected) = Just selected
applicationAvailability (WindowObservationAttached _ selected _ _ _) = Just selected
applicationAvailability (WindowWatchAttached _ selected _ _) = Just selected
applicationAvailability (NotificationCapabilitiesAttached _ selected _ _) = Just selected
applicationAvailability _ = Nothing
-- Notification wire values remain application DATA. A capability field does not
-- acquire a bus or identify its producer; only the backend may announce actual
-- service availability. Existing attachment constructors keep their exact bytes.
applicationAttachedWithNotificationService :: Binding -> ApplicationAvailability -> Bool -> Either Text DesktopReply
applicationAttachedWithNotificationService owner available ready = do
  let reply = NotificationCapabilitiesAttached owner available True ready
  _ <- encodeDesktopReply reply
  pure reply

notificationText :: Int -> Bool -> Text -> Bool
notificationText limit nonempty value = utf16Length value <= limit
  && (not nonempty || not (T.null value))
  && not (T.any (\c -> ord c < 32 && c /= '\n' && c /= '\t') value)
notificationUniqueProducer :: Text -> Bool
notificationUniqueProducer value = T.length value <= 128 && T.isPrefixOf ":" value
  && let parts = T.splitOn "." (T.drop 1 value)
     in length parts >= 2 && all (\part -> not (T.null part)
       && T.all (\c -> isAscii c && (isAlphaNum c || c == '_' || c == '-')) part) parts
notificationUint32 :: Counter -> Bool
notificationUint32 value = case reads (T.unpack (renderCounter value)) :: [(Integer,String)] of
  [(number,"")] -> number <= 4294967295
  _ -> False

checkedNotificationEntry :: Json -> Either Text (Counter,Counter)
checkedNotificationEntry value = do
  pairs <- case value of JObject fields -> Right fields; _ -> Left "notification entry object"
  let urgency = lookup "urgency" pairs
  fields <- object (["id","incarnation","producer","app","summary","body","state","actions"]
                    ++ maybe [] (const ["urgency"]) urgency) value
  ident <- field "id" fields >>= counter
  incarnation <- field "incarnation" fields >>= counter
  require (notificationUint32 ident) "notification id exceeds uint32"
  producer <- field "producer" fields >>= textValue
  require (notificationUniqueProducer producer) "notification unique producer"
  app <- field "app" fields >>= textValue
  summary <- field "summary" fields >>= textValue
  body <- field "body" fields >>= textValue
  require (notificationText 128 False app && notificationText 256 False summary
           && notificationText 1024 False body) "notification entry text"
  state <- field "state" fields >>= textValue
  require (state `elem` ["live","expired","invoked","dismissed","closed","disconnected","unknown","unavailable"]) "notification entry state"
  actions <- field "actions" fields >>= array
  require (length actions <= 8 && (state == "live" || null actions)) "notification action lifecycle"
  keys <- mapM checkAction actions
  require (length keys == Set.size (Set.fromList keys)) "duplicate notification action"
  case urgency of
    Nothing -> pure ()
    Just number -> require (number `elem` [JNumber "0",JNumber "1",JNumber "2"]) "notification urgency"
  pure (ident,incarnation)
 where
  checkAction action = do
    fields <- object ["key","label"] action
    key <- field "key" fields >>= textValue
    label <- field "label" fields >>= textValue
    require (boundedText 64 True key && not (T.any ((==127) . ord) key)
             && notificationText 128 True label) "notification action text"
    pure key

checkedNotificationSnapshot :: Json -> Either Text Json
checkedNotificationSnapshot value = do
  fields <- object ["service","revision","available","reason","entries"] value
  _ <- field "service" fields >>= counter
  _ <- field "revision" fields >>= counter
  available <- field "available" fields
  require (case available of JBool _ -> True; _ -> False) "notification availability"
  reason <- field "reason" fields >>= textValue
  require (notificationText 256 False reason) "notification reason"
  entries <- field "entries" fields >>= array
  require (length entries <= 32) "notification entry capacity"
  identities <- mapM checkedNotificationEntry entries
  require (length identities == Set.size (Set.fromList (map fst identities))
           && length identities == Set.size (Set.fromList (map snd identities))) "duplicate notification identity"
  pure value

notificationSnapshotReply :: Binding -> Counter -> Json -> Either Text DesktopReply
notificationSnapshotReply owner request value = do
  positive request
  snapshot <- checkedNotificationSnapshot value
  let reply = NotificationSnapshotReply owner request snapshot
  _ <- encodeDesktopReply reply
  pure reply
notificationOutcomeReply :: Binding -> Counter -> Text -> Json -> Either Text DesktopReply
notificationOutcomeReply owner request status value = do
  positive request
  require (status `elem` ["Dispatched","Refused","Unknown"]) "notification outcome status"
  snapshot <- checkedNotificationSnapshot value
  let reply = NotificationOutcomeReply owner request status snapshot Nothing
  _ <- encodeDesktopReply reply
  pure reply

catalogReply :: Binding -> Counter -> Maybe CatalogSnapshot -> Maybe PinSnapshot -> Either Text DesktopReply
catalogReply owner request catalog pins = do
  positive request
  let reply = CatalogReply owner request catalog pins
  _ <- encodeDesktopReply reply
  pure reply
pinsReply :: Binding -> Counter -> PinStatus -> Maybe PinSnapshot -> Either Text DesktopReply
pinsReply owner request status pins = do
  positive request
  let reply = PinsReply owner request status pins
  _ <- encodeDesktopReply reply
  pure reply
encodeDesktopReply :: DesktopReply -> Either Text B.ByteString
encodeDesktopReply = encodeBounded 1048576 . replyJson
decodeDesktopReply :: B.ByteString -> Either Text DesktopReply
decodeDesktopReply raw = do
  value <- decodeBounded 1048576 raw
  fields <- case value of JObject pairs -> Right pairs; _ -> Left "reply object required"
  field "protocolVersion" fields >>= fixed (JNumber "3")
  kind <- field "kind" fields >>= textValue
  case kind of
    "application-attached" -> do
      let present = lookup "applicationOperations" fields
          local = lookup "localOperations" fields
          notifications = lookup "notificationOperations" fields
          observations = lookup "windowObservationOperations" fields
      exact <- object (["protocolVersion","kind","binding","nativeOperations"] ++ (case present of Nothing -> []; Just _ -> ["applicationOperations"]) ++ (case local of Nothing -> []; Just _ -> ["localOperations"]) ++ (case notifications of Nothing -> []; Just _ -> ["notificationOperations"]) ++ (case observations of Nothing -> []; Just _ -> ["windowObservationOperations"])) value
      owner <- field "binding" exact >>= parseBinding
      field "nativeOperations" exact >>= fixed (JArray [])
      availability <- case present of
       Nothing -> Right Nothing
       Just (JArray []) -> Right (Just ApplicationUnavailable)
       Just (JArray [JString "application-launch"]) -> Right (Just ApplicationLaunchAvailable)
       Just _ -> Left "unsupported application operations"
      case observations of
       Just operations -> do
        ready <- case operations of
          JArray [] -> Right False
          JArray [JString "window-read"] -> Right True
          JArray [JString "window-read",JString "window-watch"] -> Right True
          _ -> Left "unsupported window observation operations"
        available <- maybe (Left "explicit application operations required") Right availability
        localPolicy <- case local of
          Nothing -> Right False
          Just (JArray [JString "notification-policy"]) -> Right True
          _ -> Left "unsupported local operations"
        service <- case notifications of
          Nothing -> Right Nothing
          Just (JArray []) -> Right (Just False)
          Just (JArray [JString "notification-read",JString "notification-action"]) -> Right (Just True)
          _ -> Left "unsupported notification operations"
        pure (if operations==JArray [JString "window-read",JString "window-watch"] then WindowWatchAttached owner available localPolicy service else WindowObservationAttached owner available localPolicy service ready)
       Nothing ->
        case (notifications,local,availability) of
         (Nothing,Nothing,Nothing) -> applicationAttached owner
         (Nothing,Nothing,Just available) -> applicationAttachedWithAvailability owner available
         (Nothing,Just (JArray [JString "notification-policy"]),Just available) -> applicationAttachedWithLocalNotifications owner available
         (Just operations,localValue,Just available) -> do
          ready <- case operations of
            JArray [] -> Right False
            JArray [JString "notification-read",JString "notification-action"] -> Right True
            _ -> Left "unsupported notification operations"
          localPolicy <- case localValue of
            Nothing -> Right False
            Just (JArray [JString "notification-policy"]) -> Right True
            _ -> Left "unsupported local operations"
          pure (NotificationCapabilitiesAttached owner available localPolicy ready)
         _ -> Left "unsupported local or notification operations"
    "window-watch-result" -> do
      exact <- object ["protocolVersion","kind","binding","requestId","observedRevision","status","snapshot"] value
      owner <- field "binding" exact >>= parseBinding
      request <- field "requestId" exact >>= counter
      observedRevision <- field "observedRevision" exact >>= counter
      status <- field "status" exact >>= textValue
      snapshot <- field "snapshot" exact >>= optional (windowSnapshot owner)
      windowWatchReply owner request observedRevision status snapshot
    "window-observation" -> do
      exact <- object ["protocolVersion","kind","binding","requestId","status","snapshot"] value
      owner <- field "binding" exact >>= parseBinding
      request <- field "requestId" exact >>= counter
      status <- field "status" exact >>= textValue
      snapshot <- field "snapshot" exact >>= optional (windowSnapshot owner)
      windowObservationReply owner request status snapshot
    "notification-snapshot" -> do
      exact <- object ["protocolVersion","kind","binding","requestId","snapshot"] value
      owner <- field "binding" exact >>= parseBinding
      request <- field "requestId" exact >>= counter
      snapshot <- field "snapshot" exact
      notificationSnapshotReply owner request snapshot
    "notification-outcome" -> do
      let reasonField = lookup "reason" fields
      exact <- object (["protocolVersion","kind","binding","requestId","status","snapshot"]
                       ++ maybe [] (const ["reason"]) reasonField) value
      owner <- field "binding" exact >>= parseBinding
      request <- field "requestId" exact >>= counter
      status <- field "status" exact >>= textValue
      snapshot <- field "snapshot" exact
      reply <- notificationOutcomeReply owner request status snapshot
      case reasonField of
        Nothing -> pure reply
        Just rawReason -> do
          reason <- textValue rawReason
          require (reason `elem` ["","expired","changed","unavailable","already-handled"]) "notification refusal reason"
          pure (NotificationOutcomeReply owner request status snapshot (Just reason))
    "application-catalog" -> do
      exact <- object ["protocolVersion","kind","binding","requestId","preferences","snapshot"] value
      owner <- field "binding" exact >>= parseBinding
      request <- field "requestId" exact >>= counter
      pins <- field "preferences" exact >>= optional parsePins
      field "snapshot" exact >>= optional parseCatalog >>= \catalog -> catalogReply owner request catalog pins
    "application-launch-outcome" -> do
      exact <- object ["protocolVersion","kind","binding","outcome"] value
      owner <- field "binding" exact >>= parseBinding
      (intent,status) <- field "outcome" exact >>= parseLaunchOutcome
      launchReply owner intent status
    "taskbar-pins-outcome" -> do
      exact <- object ["protocolVersion","kind","binding","requestId","preferences","status"] value
      owner <- field "binding" exact >>= parseBinding
      request <- field "requestId" exact >>= counter
      pins <- field "preferences" exact >>= optional parsePins
      status <- field "status" exact >>= textValue
      typed <- case status of "Saved" -> Right PinSaved; "Refused" -> Right PinRefused; "Unknown" -> Right PinUnknown; _ -> Left "pin status"
      pinsReply owner request typed pins
    "native-preview-grant" -> do
      exact <- object ["protocolVersion","kind","binding","receiverEpoch","capacity"] value
      owner <- field "binding" exact >>= parseBinding
      epoch <- field "receiverEpoch" exact >>= counter
      positive epoch
      capacity <- case field "capacity" exact of
        Right (JNumber number) -> case reads (T.unpack number) :: [(Integer,String)] of
          [(count,"")] | count>0 && count<=1065 -> Right (fromInteger count)
          _ -> Left "bounded native preview capacity"
        _ -> Left "native preview capacity integer"
      pure (PreviewGrant owner epoch capacity)
    "native-preview-quarantine" -> previewDomain PreviewQuarantine value
    "native-preview-closed" -> previewDomain PreviewClosed value
    _ -> Left "unsupported desktop reply kind"
 where
  previewDomain constructor value = do
    exact <- object ["protocolVersion","kind","binding","receiverEpoch"] value
    owner <- field "binding" exact >>= parseBinding
    epoch <- field "receiverEpoch" exact >>= counter
    positive epoch
    pure (constructor owner epoch)
encodeDesktopGateway :: DesktopReply -> Either Text B.ByteString
encodeDesktopGateway reply = do
  _ <- encodeDesktopReply reply
  encodeBounded 1048704 (JObject [("bridgeProtocol",JNumber "1"),("kind",JString "native-event"),("payload",replyJson reply)])
decodeDesktopGateway :: B.ByteString -> Either Text DesktopReply
decodeDesktopGateway raw = do
  value <- decodeBounded 1048704 raw
  fields <- object ["bridgeProtocol","kind","payload"] value
  field "bridgeProtocol" fields >>= fixed (JNumber "1")
  field "kind" fields >>= fixed (JString "native-event")
  field "payload" fields >>= decodeDesktopReply . jsonBytes

-- Observation data stays distinct from action projection. IDs name one lexical
-- owner and actual opaque token incarnations; they never confer native actions.
windowSnapshot :: Binding -> Json -> Either Text WindowSnapshot
windowSnapshot bound value = do
  fields <- object ["owner","revision","view","outputs","windows"] value
  owner <- field "owner" fields >>= counter
  _ <- field "revision" fields >>= counter
  require (owner==frontend bound) "window observation owner differs"
  field "view" fields >>= fixed (JString "global")
  outputs <- field "outputs" fields >>= array >>= mapM counter
  require (length outputs<=64 && distinct outputs) "window output capacity or duplicates"
  rows <- field "windows" fields >>= array
  require (length rows<=256) "window capacity"
  identities <- mapM (row outputs) rows
  require (distinct (map fst identities)) "duplicate window identity"
  mapM_ (walk identities Set.empty . fst) identities
  require (B.length (jsonBytes value)<=524288) "window snapshot capacity"
  pure (WindowSnapshot value)
 where
  distinct values = length values==Set.size (Set.fromList values)
  row outputs raw = do
    fields <- object ["id","title","appId","states","outputs","parent"] raw
    ident <- field "id" fields >>= counter
    heading <- field "title" fields >>= textValue
    application <- field "appId" fields >>= textValue
    require (all (\text -> boundedText 256 False text && not (T.any ((==127) . ord) text)) [heading,application]) "window text bound"
    states <- field "states" fields >>= array >>= mapM textValue
    require (distinct states && all (`elem` ["maximized","minimized","activated","fullscreen"]) states) "window states"
    membership <- field "outputs" fields >>= array >>= mapM counter
    require (distinct membership && all (`elem` outputs) membership) "window output membership"
    parent <- field "parent" fields >>= optional counter
    pure (ident,parent)
  walk rows seen ident = do
    require (not (Set.member ident seen)) "window parent cycle"
    parent <- maybe (Left "window parent retired") Right (lookup ident rows)
    maybe (Right ()) (walk rows (Set.insert ident seen)) parent

windowObservationReply :: Binding -> Counter -> Text -> Maybe WindowSnapshot -> Either Text DesktopReply
windowObservationReply bound request status observed = do
  positive request
  require (case (status,observed) of ("Observed",Just _) -> True; ("Unknown",Nothing) -> True; ("Unavailable",Nothing) -> True; _ -> False) "window observation status/snapshot"
  case observed of
    Just (WindowSnapshot raw) -> windowSnapshot bound raw >> pure ()
    Nothing -> pure ()
  let reply = WindowObservationReply bound request status observed
  _ <- encodeDesktopReply reply
  pure reply

applicationAttachedWithWindowObservation :: Binding -> ApplicationAvailability -> Either Text DesktopReply
applicationAttachedWithWindowObservation owner available = do
  let reply = WindowObservationAttached owner available True Nothing True
  _ <- encodeDesktopReply reply
  pure reply

windowWatchRevision :: DesktopRequest -> Maybe Counter
windowWatchRevision (WindowWatchRequest _ _ revision) = Just revision
windowWatchRevision _ = Nothing

windowWatchReply :: Binding -> Counter -> Counter -> Text -> Maybe WindowSnapshot -> Either Text DesktopReply
windowWatchReply bound request observedRevision status observed = do
  positive request
  positive observedRevision
  require (case (status,observed) of ("Changed",Just _) -> True; ("Unchanged",Nothing) -> True; ("Unknown",Nothing) -> True; ("Unavailable",Nothing) -> True; _ -> False) "window watch status/snapshot"
  case observed of
    Nothing -> pure ()
    Just (WindowSnapshot raw) -> do
      _ <- windowSnapshot bound raw
      fields <- object ["owner","revision","view","outputs","windows"] raw
      revision <- field "revision" fields >>= counter
      require (revision>observedRevision) "window watch revision did not advance"
  let reply = WindowWatchReply bound request observedRevision status observed
  _ <- encodeDesktopReply reply
  pure reply

applicationAttachedWithWindowWatch :: Binding -> ApplicationAvailability -> Either Text DesktopReply
applicationAttachedWithWindowWatch bound available = do
  let reply = WindowWatchAttached bound available True Nothing
  _ <- encodeDesktopReply reply
  pure reply
