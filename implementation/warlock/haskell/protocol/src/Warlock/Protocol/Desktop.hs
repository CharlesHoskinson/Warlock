{-# LANGUAGE OverloadedStrings #-}
-- Application data only. No decoded commit or reply grants native authority.
module Warlock.Protocol.Desktop
  ( DesktopCommit, decodeDesktopCommit, encodeDesktopCommit, commitRequests, commitProjection, commitFocus
  , DesktopRequest, RequestKind(..), requestKind, requestBinding, requestId, pinProposal
  , LaunchIntent, launchIntent, launchRequest, launchLifetime, launchGeneration, launchEntry
  , LaunchStatus(..), LaunchRefusal(..), launchReply, launchOutcome
  , PinSnapshot, pinSnapshot, pinRevision, pinIdentities, decodePinSnapshot, encodePinSnapshot
  , CatalogEntry, catalogEntry, CatalogSnapshot, catalogSnapshot
  , DesktopReply, PinStatus(..), ApplicationAvailability(..), applicationAttached, applicationAttachedWithAvailability, applicationAvailability, catalogReply, pinsReply, replyBinding
  , decodeDesktopReply, encodeDesktopReply, decodeDesktopGateway, encodeDesktopGateway, popupControl ) where

import qualified Data.ByteString as B
import Data.Char (ord)
import qualified Data.Set as Set
import Data.Text (Text)
import qualified Data.Text as T
import qualified Data.Text.Encoding as TE
import Warlock.Protocol.Identity
import Warlock.Protocol.StrictJson
import Warlock.Protocol.Wire (parseBinding)

data RequestKind = CatalogRead | PinsWrite | ApplicationLaunch deriving (Eq, Show)
data LaunchIntent = LaunchIntent Counter Counter Counter Text deriving (Eq, Show)
data LaunchRefusal = RetiredAuthority | RequestReuse | RetiredRequest | CatalogUnavailable | StaleCatalog | RemovedEntry | NativeEntryUnavailable | DesktopEntryRaced deriving (Eq, Show)
data LaunchStatus = LaunchSubmitted | LaunchUnknown | LaunchRefused LaunchRefusal deriving (Eq, Show)
data PinSnapshot = PinSnapshot Counter [Text] deriving (Eq, Show)
data DesktopRequest = CatalogRequest Binding Counter | PinsRequest Binding Counter PinSnapshot | LaunchRequest Binding LaunchIntent deriving (Eq, Show)
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
requestBinding :: DesktopRequest -> Binding
requestBinding (CatalogRequest owner _) = owner
requestBinding (PinsRequest owner _ _) = owner
requestBinding (LaunchRequest owner _) = owner
requestId :: DesktopRequest -> Counter
requestId (CatalogRequest _ request) = request
requestId (PinsRequest _ request _) = request
requestId (LaunchRequest _ intent) = launchRequest intent
pinProposal :: DesktopRequest -> Maybe PinSnapshot
pinProposal (CatalogRequest _ _) = Nothing
pinProposal (PinsRequest _ _ proposal) = Just proposal
pinProposal (LaunchRequest _ _) = Nothing
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
applicationAvailability :: DesktopReply -> Maybe ApplicationAvailability
applicationAvailability (ApplicationAttached _ selected) = Just (maybe ApplicationUnavailable id selected)
applicationAvailability _ = Nothing
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
      exact <- object (["protocolVersion","kind","binding","nativeOperations"] ++ case present of Nothing -> []; Just _ -> ["applicationOperations"]) value
      owner <- field "binding" exact >>= parseBinding
      field "nativeOperations" exact >>= fixed (JArray [])
      case present of
       Nothing -> applicationAttached owner
       Just (JArray []) -> applicationAttachedWithAvailability owner ApplicationUnavailable
       Just (JArray [JString "application-launch"]) -> applicationAttachedWithAvailability owner ApplicationLaunchAvailable
       Just _ -> Left "unsupported application operations"
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
