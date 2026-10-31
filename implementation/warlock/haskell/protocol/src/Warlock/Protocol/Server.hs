{-# LANGUAGE OverloadedStrings #-}
-- Untrusted wire values only: parsing does not authenticate or create evidence.
module Warlock.Protocol.Server (ServerFrame, ServerKind(..), OutcomeStatus(..), LookupState(..), serverKind, serverJson, lookupResultState, decodeServer, capabilityMatches, batchMatches, CheckedHistory, verifyHistoryKey, lookupCheckedHistory, checkedHistoryFrame, verifyPositionalKey, verifyLookupResultKey) where
import qualified Data.ByteString as BS
import qualified Data.Set as Set
import Data.List (sortOn)
import Numeric (showHex)
import Data.Text (Text)
import qualified Data.Text as T
import qualified Data.Text.Encoding as TE
import Warlock.Protocol.StrictJson
import Warlock.Protocol.Identity
import Warlock.Protocol.Custody (Intent)
import Warlock.Protocol.Wire (parseBinding,parseIntent,parseLookup)

data ServerKind = Hello | Capabilities | Selection | Prepared | Outcome | History | BatchRegistered | BatchDisposition | LookupResult deriving (Eq, Show)
data OutcomeStatus = OutcomeCommitted | OutcomeRefused Text | OutcomeCancelled | OutcomeUnknown deriving (Eq, Show)
data LookupState = LookupAbsent | LookupUnknown | LookupPrepared | LookupSettlementAvailable deriving (Eq, Show)
data ServerFrame = ServerFrame ServerKind Json deriving (Eq, Show)
serverKind :: ServerFrame -> ServerKind
serverKind (ServerFrame k _) = k
serverJson :: ServerFrame -> Json
serverJson (ServerFrame _ j) = j

canonical :: Json -> Json
canonical j = case j of
  JObject fields -> JObject (sortOn fst [(k,canonical v) | (k,v) <- fields])
  JArray values -> JArray (map canonical values)
  _ -> j

err :: Show a => Either a b -> Either Text b
err = either (Left . T.pack . show) Right
obj :: [Text] -> Json -> Either Text [(Text,Json)]
obj names = err . exactObject names
f :: Text -> [(Text,Json)] -> Either Text Json
f key fields = maybe (Left "missing field") Right (lookup key fields)
str :: Json -> Either Text Text
str (JString t) = Right t
str _ = Left "string required"
counter :: Json -> Either Text Counter
counter x = str x >>= err . parseCounter False
hex :: Int -> Json -> Either Text Text
hex size x = do
  t <- str x
  if T.length t == size && T.all (\c -> (c >= '0' && c <= '9') || (c >= 'a' && c <= 'f')) t
    then Right t else Left "bad hexadecimal identity"
value :: Text -> Json -> Either Text ()
value t x = if x == JString t then Right () else Left "unexpected fixed value"

data Ident = Ident Binding Intent Text Counter Counter deriving (Eq, Show)
identityFields :: [Text]
identityFields = ["binding","intent","selectionId","deadlineMonotonicNs","preparedId"]
identity :: [(Text,Json)] -> Either Text Ident
identity fields = do
  owner <- f "binding" fields >>= parseBinding
  target <- f "intent" fields >>= parseIntent owner
  selected <- f "selectionId" fields >>= hex 32
  deadline <- f "deadlineMonotonicNs" fields >>= counter
  prepared <- f "preparedId" fields >>= counter
  pure (Ident owner target selected deadline prepared)
identityJson :: Json -> Either Text Ident
identityJson j = obj identityFields j >>= identity

selection :: Json -> Either Text (Text,Counter)
selection j = do
  o <- obj ["selectionId","scope","publication","lease","controlId","clock","acceptedMonotonicNs","deadlineMonotonicNs"] j
  selected <- f "selectionId" o >>= hex 32
  sc <- f "scope" o >>= obj ["id","generation"]
  _ <- f "id" sc >>= counter
  _ <- f "generation" sc >>= counter
  _ <- f "publication" o >>= counter
  _ <- f "lease" o >>= counter
  control <- f "controlId" o >>= str
  if T.null control || BS.length (TE.encodeUtf8 control) > 512 then Left "bad control" else pure ()
  f "clock" o >>= value "CLOCK_MONOTONIC"
  accepted <- f "acceptedMonotonicNs" o >>= counter
  deadline <- f "deadlineMonotonicNs" o >>= counter
  expected <- err (addCounter accepted 2000000000)
  if deadline /= expected then Left "deadline differs" else pure (selected,deadline)

refusals :: [Text]
refusals = ["original-deadline-expired","ambiguous-or-ineligible-restore-focus","dependency-mismatch","exclusive-input","family-state-mismatch","implicit-transfer-required","ineligible-family","ineligible-workspace-owner","invalid-family","invalid-family-root","mixed-family-workspace-owner","native-operation-bound","native-operation-unresolved","native-pointer-owned","navigation-family-state-changed","navigation-recipient-changed","navigation-refused","seat-grab","stale-incarnation","state-bound","superseded-switcher-selection","switcher-cancelled-or-retired","unsupported-operation","workspace-navigation-unresolved"]
outcome :: Json -> Either Text (Ident,OutcomeStatus)
outcome j = do
  o <- obj (identityFields ++ ["status","reason","revision","outputGeneration"]) j
  key <- identity o
  status <- f "status" o >>= str
  reason <- f "reason" o >>= str
  _ <- f "revision" o >>= counter
  _ <- f "outputGeneration" o >>= counter
  case (status,reason) of
    ("Committed","applied") -> Right (key,OutcomeCommitted)
    ("Cancelled","cancelled-before-commit") -> Right (key,OutcomeCancelled)
    ("Unknown","effect-unproven") -> Right (key,OutcomeUnknown)
    ("Refused",_) | reason `elem` refusals -> Right (key,OutcomeRefused reason)
    _ -> Left "bad status or reason"

member :: Binding -> Json -> Either Text ()
member owner j = do
  o <- case j of JObject v -> Right v; _ -> Left "member object required"
  kind <- f "kind" o >>= str
  case kind of
    "negotiate" -> do
      a <- obj ["kind","requestId"] j; _ <- f "requestId" a >>= counter; pure ()
    "prepare" -> do
      a <- obj ["kind","intent","selectionId"] j
      _ <- f "intent" a >>= parseIntent owner; _ <- f "selectionId" a >>= hex 32; pure ()
    "decision" -> do
      a <- obj ["kind","intent","selectionId","deadlineMonotonicNs","preparedId","decision"] j
      _ <- f "intent" a >>= parseIntent owner; _ <- f "selectionId" a >>= hex 32
      _ <- f "deadlineMonotonicNs" a >>= counter; _ <- f "preparedId" a >>= counter
      d <- f "decision" a >>= str
      if d `elem` ["commit","cancel"] then pure () else Left "bad decision"
    _ -> Left "bad member kind"

batch :: Bool -> Json -> Either Text ()
batch disposition j = do
  let names = ["binding","batchId","packetSHA256","members"] ++ if disposition then ["disposition"] else []
  o <- obj names j
  owner <- f "binding" o >>= parseBinding
  _ <- f "batchId" o >>= hex 32
  _ <- f "packetSHA256" o >>= hex 64
  m <- f "members" o
  case m of
    JArray entries | not (null entries) && length entries <= 16 -> do
      mapM_ (member owner) entries
      -- Object key order is immaterial to a complete typed member identity.
      if length entries /= Set.size (Set.fromList (map (show . canonical) entries)) then Left "duplicate member" else pure ()
    _ -> Left "bad members"
  if disposition then do
    d <- f "disposition" o >>= str
    if d `elem` ["preflight-unsent","admitted","uncertain"] then pure () else Left "bad disposition"
  else pure ()

history :: Json -> Either Text ()
history j = do
  o <- obj ["deliveryBinding","key","originalBinding","intent","selection","preparedId","certificate","ackState","acknowledgement","executionAuthorized"] j
  delivery <- f "deliveryBinding" o >>= parseBinding
  _ <- f "key" o >>= hex 64
  original <- f "originalBinding" o >>= parseBinding
  target <- f "intent" o >>= parseIntent original
  (selected,deadline) <- f "selection" o >>= selection
  prep <- f "preparedId" o >>= counter
  (cert,status) <- f "certificate" o >>= outcome
  if lifetime delivery /= lifetime original || cert /= Ident original target selected deadline prep || status == OutcomeUnknown then Left "history correlation" else pure ()
  state <- f "ackState" o >>= str
  ack <- f "acknowledgement" o
  case (state,ack) of
    ("not-sent",JNull) -> pure ()
    ("pending",JNull) -> pure ()
    ("acknowledged",_) -> do parsed <- identityJson ack; if parsed == cert then pure () else Left "ack correlation"
    _ -> Left "ack state"
  authorized <- f "executionAuthorized" o
  if authorized == JBool False then pure () else Left "history cannot authorize execution"

decodeServer :: BS.ByteString -> Either Text ServerFrame
decodeServer bytes = do
  limits <- err (bounds 65536 16)
  root <- err (decodeStrict limits bytes)
  validateServerJson root

validateServerJson :: Json -> Either Text ServerFrame
validateServerJson root = do
  top <- obj ["version","kind","body"] root
  version <- f "version" top
  if version `elem` [JNumber "1",JNumber "2"] then pure () else Left "bad version"
  kind <- f "kind" top >>= str
  body <- f "body" top
  parsed <- case kind of
    "hello" -> do o <- obj ["binding"] body; _ <- f "binding" o >>= parseBinding; pure Hello
    "capabilities" -> do
      o <- obj ["binding","requestId","operations","maxPreparedPerSession","maxPreparedGlobal","deadlineClock"] body
      _ <- f "binding" o >>= parseBinding; _ <- f "requestId" o >>= counter
      ops <- f "operations" o; one <- f "maxPreparedPerSession" o; total <- f "maxPreparedGlobal" o
      clock <- f "deadlineClock" o
      if ops == JArray [JString "restore"] && one == JNumber "1" && total == JNumber "64" && clock == JString "CLOCK_MONOTONIC" then pure Capabilities else Left "bad capability"
    "selection" -> do o <- obj ["binding","selection"] body; _ <- f "binding" o >>= parseBinding; _ <- f "selection" o >>= selection; pure Selection
    "prepared" -> identityJson body >> pure Prepared
    "outcome" -> outcome body >> pure Outcome
    "history" -> history body >> pure History
    "batch-registered" -> batch False body >> pure BatchRegistered
    "batch-disposition" -> batch True body >> pure BatchDisposition
    "lookup-result" | version == JNumber "2" -> do
      fields <- obj ["deliveryBinding","requestId","key","originalBinding","intent","selection","preparedId","result","observedPreparedId"] body
      let query = JObject [(k,v) | (k,v) <- fields, k /= "result" && k /= "observedPreparedId"]
      _ <- parseLookup query
      result <- f "result" fields >>= str
      requested <- f "preparedId" fields
      observed <- f "observedPreparedId" fields
      case (result,requested,observed) of
        ("prepared",JNull,_) -> counter observed >> pure LookupResult
        ("prepared",_,_) -> do
          p <- counter requested
          q <- counter observed
          if p == q then pure LookupResult else Left "lookup preparation mismatch"
        (other,_,JNull) | other `elem` ["absent","unknown","settlement-available"] -> pure LookupResult
        _ -> Left "bad lookup result"
    _ -> Left "unsupported server kind"
  pure (ServerFrame parsed root)

-- These compare decoded identities only. They do not attest packet bytes, peer
-- authentication, delivery or a native proof.
capabilityMatches :: Binding -> Counter -> ServerFrame -> Bool
capabilityMatches expected request (ServerFrame Capabilities root) =
  case do
    top <- obj ["version","kind","body"] root
    o <- f "body" top >>= obj ["binding","requestId","operations","maxPreparedPerSession","maxPreparedGlobal","deadlineClock"]
    owner <- f "binding" o >>= parseBinding
    rid <- f "requestId" o >>= counter
    pure (owner == expected && rid == request) of
    Right matched -> matched
    Left _ -> False
capabilityMatches _ _ _ = False

batchMatches :: ServerFrame -> ServerFrame -> Bool
batchMatches (ServerFrame BatchRegistered first) (ServerFrame BatchDisposition second) =
  case (body first, body second) of
    (Right a,Right b) -> all (\name -> fmap canonical (lookup name a) == fmap canonical (lookup name b)) ["binding","batchId","packetSHA256","members"]
    _ -> False
  where
    body root = do
      top <- obj ["version","kind","body"] root
      v <- f "body" top
      case v of JObject fields -> Right fields; _ -> Left "body"
batchMatches _ _ = False

-- Full K is an independently verified positional SHA256 over the recorded
-- admission, not the syntax of a 64-hex string. Digest is a reviewed backend
-- primitive; this pure interface alone does not authenticate the record.
newtype CheckedHistory = CheckedHistory ServerFrame deriving (Eq, Show)
checkedHistoryFrame :: CheckedHistory -> ServerFrame
checkedHistoryFrame (CheckedHistory frame) = frame
verifyHistoryKey :: (BS.ByteString -> BS.ByteString) -> ServerFrame -> Either Text CheckedHistory
verifyHistoryKey digest frame@(ServerFrame History root) = do
  top <- obj ["version","kind","body"] root
  h <- f "body" top >>= obj ["deliveryBinding","key","originalBinding","intent","selection","preparedId","certificate","ackState","acknowledgement","executionAuthorized"]
  claimed <- f "key" h >>= hex 64
  original <- f "originalBinding" h
  target <- f "intent" h
  verifyPositionalKey digest claimed original target
  pure (CheckedHistory frame)

verifyHistoryKey _ _ = Left "history frame required"

verifyPositionalKey :: (BS.ByteString -> BS.ByteString) -> Text -> Json -> Json -> Either Text ()
verifyPositionalKey digest claimed original target = do
  _ <- hex 64 (JString claimed)
  owner <- parseBinding original
  _ <- parseIntent owner target
  b <- obj ["lifetime","session","frontend"] original
  i <- obj ["request","generation","incarnation","operation","context"] target
  c <- f "context" i >>= obj ["lifetime","epoch","output","revision"]
  life <- f "lifetime" b >>= str
  sessionId <- f "session" b >>= str
  front <- f "frontend" b >>= str
  request <- f "request" i >>= str
  generation <- f "generation" i >>= str
  incarnation <- f "incarnation" i >>= str
  operation <- f "operation" i >>= str
  ilife <- f "lifetime" c >>= str
  epoch <- f "epoch" c >>= str
  output <- f "output" c >>= str
  revision <- f "revision" c >>= str
  let quoted x = "\"" <> x <> "\""
      terms = map quoted [life,sessionId,front] ++ ["1"] ++ map quoted [request,generation,incarnation,operation,ilife,epoch,output,revision]
      source = TE.encodeUtf8 ("[" <> T.intercalate "," terms <> "]")
      hashBytes = digest source
      hexByte n = let s = showHex n "" in if length s == 1 then '0':s else s
      actual = T.pack (concatMap hexByte (BS.unpack hashBytes))
  if BS.length hashBytes == 32 && claimed == actual then Right () else Left "positional key mismatch"

verifyLookupResultKey :: (BS.ByteString -> BS.ByteString) -> ServerFrame -> Either Text ()
verifyLookupResultKey digest (ServerFrame LookupResult root) = do
  top <- obj ["version","kind","body"] root
  bodyFields <- f "body" top >>= obj ["deliveryBinding","requestId","key","originalBinding","intent","selection","preparedId","result","observedPreparedId"]
  key <- f "key" bodyFields >>= hex 64
  original <- f "originalBinding" bodyFields
  target <- f "intent" bodyFields
  verifyPositionalKey digest key original target
verifyLookupResultKey _ _ = Left "lookup result required"

-- Internal read-only lookup over verified identities. No fresh grant or ACK is
-- created. A store interpreter must still supply durable/authenticated history.
lookupCheckedHistory :: Binding -> Text -> [CheckedHistory] -> Either Text (Maybe CheckedHistory)
lookupCheckedHistory current key records = do
  _ <- hex 64 (JString key)
  matches <- filterMatches records
  case matches of
    [] -> Right Nothing
    [one] -> Right (Just one)
    _ -> Left "ambiguous history key"
  where
    filterMatches [] = Right []
    filterMatches (h@(CheckedHistory (ServerFrame History root)):rest) = do
      top <- obj ["version","kind","body"] root
      fields <- f "body" top >>= obj ["deliveryBinding","key","originalBinding","intent","selection","preparedId","certificate","ackState","acknowledgement","executionAuthorized"]
      delivery <- f "deliveryBinding" fields >>= parseBinding
      k <- f "key" fields >>= hex 64
      tailMatches <- filterMatches rest
      pure (if delivery == current && k == key then h:tailMatches else tailMatches)
    filterMatches (_:_) = Left "invalid checked history"

lookupResultState :: ServerFrame -> Maybe LookupState
lookupResultState (ServerFrame LookupResult root) = case root of
  JObject top -> case lookup "body" top of
    Just (JObject fields) -> case lookup "result" fields of
      Just (JString "absent") -> Just LookupAbsent
      Just (JString "unknown") -> Just LookupUnknown
      Just (JString "prepared") -> Just LookupPrepared
      Just (JString "settlement-available") -> Just LookupSettlementAvailable
      _ -> Nothing
    _ -> Nothing
  _ -> Nothing
lookupResultState _ = Nothing
