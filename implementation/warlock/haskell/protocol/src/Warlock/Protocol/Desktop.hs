{-# LANGUAGE OverloadedStrings #-}
-- Application data only. No decoded commit or reply grants native authority.
module Warlock.Protocol.Desktop
  ( DesktopCommit, decodeDesktopCommit, encodeDesktopCommit, commitRequests, commitProjection, commitFocus
  , DesktopRequest, RequestKind(..), requestKind, requestBinding, requestId, pinProposal
  , PinSnapshot, pinSnapshot, pinRevision, pinIdentities, decodePinSnapshot, encodePinSnapshot
  , CatalogEntry, catalogEntry, CatalogSnapshot, catalogSnapshot
  , DesktopReply, PinStatus(..), applicationAttached, catalogReply, pinsReply, replyBinding
  , decodeDesktopReply, encodeDesktopReply, decodeDesktopGateway, encodeDesktopGateway ) where

import qualified Data.ByteString as B
import Data.Char (ord)
import qualified Data.Set as Set
import Data.Text (Text)
import qualified Data.Text as T
import qualified Data.Text.Encoding as TE
import Warlock.Protocol.Identity
import Warlock.Protocol.StrictJson
import Warlock.Protocol.Wire (parseBinding)

data RequestKind = CatalogRead | PinsWrite deriving (Eq, Show)
data PinSnapshot = PinSnapshot Counter [Text] deriving (Eq, Show)
data DesktopRequest = CatalogRequest Binding Counter | PinsRequest Binding Counter PinSnapshot deriving (Eq, Show)
data DesktopCommit = DesktopCommit Json [DesktopRequest] [Text] deriving (Eq, Show)
data CatalogEntry = CatalogEntry Text Text Text Text Text [Text] deriving (Eq, Show)
data CatalogSnapshot = CatalogSnapshot Counter Counter [CatalogEntry] deriving (Eq, Show)
data PinStatus = PinSaved | PinRefused | PinUnknown deriving (Eq, Show)
data DesktopReply = CatalogReply Binding Counter (Maybe CatalogSnapshot) (Maybe PinSnapshot)
                  | PinsReply Binding Counter PinStatus (Maybe PinSnapshot)
                  | ApplicationAttached Binding deriving (Eq, Show)

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
requestBinding :: DesktopRequest -> Binding
requestBinding (CatalogRequest owner _) = owner
requestBinding (PinsRequest owner _ _) = owner
requestId :: DesktopRequest -> Counter
requestId (CatalogRequest _ request) = request
requestId (PinsRequest _ request _) = request
pinProposal :: DesktopRequest -> Maybe PinSnapshot
pinProposal (CatalogRequest _ _) = Nothing
pinProposal (PinsRequest _ _ proposal) = Just proposal
parseRequest :: Json -> Either Text DesktopRequest
parseRequest value = do
  require (B.length (jsonBytes value) <= 8192) "desktop request capacity"
  fields <- case value of JObject pairs -> Right pairs; _ -> Left "request object required"
  field "protocolVersion" fields >>= fixed (JNumber "3")
  kind <- field "kind" fields >>= textValue
  let names = ["protocolVersion","kind","binding","requestId"]
  exact <- object (names ++ if kind == "taskbar-pins-write" then ["proposal"] else []) value
  owner <- field "binding" exact >>= parseBinding
  request <- field "requestId" exact >>= counter
  case kind of
    "catalog-request" -> pure (CatalogRequest owner request)
    "taskbar-pins-write" -> PinsRequest owner request <$> (field "proposal" exact >>= parsePins)
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
replyBinding (ApplicationAttached owner) = owner
replyJson :: DesktopReply -> Json
replyJson reply = JObject $ [("protocolVersion",JNumber "3"),("binding",bindingJson (replyBinding reply))] ++ case reply of
  CatalogReply _ request catalog pins -> [("kind",JString "application-catalog"),("requestId",JString (renderCounter request)),("snapshot",nullable catalogJson catalog),("preferences",nullable pinJson pins)]
  PinsReply _ request status pins -> [("kind",JString "taskbar-pins-outcome"),("requestId",JString (renderCounter request)),("status",JString (case status of PinSaved -> "Saved"; PinRefused -> "Refused"; PinUnknown -> "Unknown")),("preferences",nullable pinJson pins)]
  ApplicationAttached _ -> [("kind",JString "application-attached"),("nativeOperations",JArray [])]
-- Application attachment announces only the already authenticated application
-- binding. It creates no native authority or native operations.
applicationAttached :: Binding -> Either Text DesktopReply
applicationAttached owner = do
  let reply = ApplicationAttached owner
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
      exact <- object ["protocolVersion","kind","binding","nativeOperations"] value
      owner <- field "binding" exact >>= parseBinding
      field "nativeOperations" exact >>= fixed (JArray [])
      applicationAttached owner
    "application-catalog" -> do
      exact <- object ["protocolVersion","kind","binding","requestId","preferences","snapshot"] value
      owner <- field "binding" exact >>= parseBinding
      request <- field "requestId" exact >>= counter
      pins <- field "preferences" exact >>= optional parsePins
      field "snapshot" exact >>= optional parseCatalog >>= \catalog -> catalogReply owner request catalog pins
    "taskbar-pins-outcome" -> do
      exact <- object ["protocolVersion","kind","binding","requestId","preferences","status"] value
      owner <- field "binding" exact >>= parseBinding
      request <- field "requestId" exact >>= counter
      pins <- field "preferences" exact >>= optional parsePins
      status <- field "status" exact >>= textValue
      typed <- case status of "Saved" -> Right PinSaved; "Refused" -> Right PinRefused; "Unknown" -> Right PinUnknown; _ -> Left "pin status"
      pinsReply owner request typed pins
    _ -> Left "unsupported desktop reply kind"
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
