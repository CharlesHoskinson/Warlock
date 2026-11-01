{-# LANGUAGE OverloadedStrings #-}
-- PREPARATION DRAFT. Pure wire/state contract; not an authentication,
-- deadline-enforcement, process-custody, or native-acceptance receipt.
module Warlock.Ui.EngineProtocol
  ( SessionId, RequestId, Startup, Scope, Box, Event(..), Projection
  , Method(..), Request(..), Reply(..), EventResult(..), ProtocolError(..)
  , Session, sessionId, requestId, startup, startupOrigins, startupDeadline
  , startupIncarnation, scope, box, projection, projectionJson, eventJson, parseEvent
  , newSession, isPoisoned, beginRequest, acceptRequest, finishRequest, confirmReplySent
  , acceptReply, poisonSession, encodeStartup, decodeStartup
  , maxHeaderBytes, maxPayloadBytes, maxFrameBytes
  ) where

import Control.Monad (foldM, unless, when)
import Data.Bits ((.|.), shiftL, shiftR)
import qualified Data.ByteString as B
import Data.Char (ord)
import Data.Int (Int32)
import Data.Text (Text)
import qualified Data.Text as T
import qualified Data.Text.Encoding as TE
import Data.Word (Word32)
import Warlock.Protocol.Identity (Counter, parseCounter, renderCounter, addCounter)
import qualified Warlock.Protocol.StrictJson as J
import Warlock.Ui.Policy (Origin, makeOrigin)

-- Projection is the unchanged decoded subtree of a <=131072-byte desktop
-- commit; StrictJson's rendering expands an input byte by at most 3x.
-- Bound must be re-reviewed if its producer or renderer changes.
maxHeaderBytes, maxPayloadBytes, maxFrameBytes :: Int
maxHeaderBytes = 512
maxPayloadBytes = 393216
maxFrameBytes = 4 + maxHeaderBytes + maxPayloadBytes

data ProtocolError = Invalid | TooLarge | InvalidState | ForeignSession
                   | Replay | WrongReply | Exhausted | Poisoned deriving (Eq, Show)
newtype SessionId = SessionId Counter deriving (Eq, Ord, Show)
newtype RequestId = RequestId Counter deriving (Eq, Ord, Show)
-- The numeric port representation is private; Origin validation stays in Policy.
data Startup = Startup Origin Origin Origin Int Int Int Counter SessionId deriving (Eq, Show)
data Scope = Scope Counter Counter deriving (Eq, Show)
data Box = Box Int32 Int32 Int32 Int32 deriving (Eq, Show)
-- These constructors carry typed fields, never owner/gateway JSON constructors.
-- Escape's counters are publication then lease. The MVP emits v1 empty or
-- single-scope topology, and v2 single-scope topology with a box. Owner also
-- accepts v2 empty topology; this narrower codec does not claim full equivalence.
data Event = Topology Counter (Maybe (Scope, Maybe Box))
           | Dismiss Scope Counter | Escape Scope Counter Counter
           | Reflow Scope Counter deriving (Eq, Show)
newtype Projection = Projection J.Json deriving (Eq, Show)
data Method = Stop | Remaining | LastProjection | OwnerTopology | OwnerDismiss
            | OwnerEscape | OwnerReflow deriving (Eq, Ord, Show)
data Request = GetStop | GetRemaining | GetLastProjection | OwnerEvent Event deriving (Eq, Show)
data EventResult = Accepted | Stale | Refused deriving (Eq, Show)
data Reply = StopReply Bool | RemainingReply Int | ProjectionReply (Maybe Projection)
           | EventReply EventResult deriving (Eq, Show)
data Pending = AwaitReply | NeedReply | SendingReply deriving (Eq, Show)
data Session = Session SessionId (Maybe Counter) (Maybe (RequestId, Method, Pending)) Bool deriving (Eq, Show)

counter :: Bool -> Text -> Either ProtocolError Counter
counter zero value = either (const (Left Invalid)) Right (parseCounter zero value)
sessionId :: Text -> Either ProtocolError SessionId
sessionId value = SessionId <$> counter False value
requestId :: Text -> Either ProtocolError RequestId
requestId value = RequestId <$> counter False value
scope :: Text -> Text -> Either ProtocolError Scope
scope a b = Scope <$> counter False a <*> counter False b
box :: Int32 -> Int32 -> Int32 -> Int32 -> Either ProtocolError Box
box x y w h | w > 0 && h > 0 = Right (Box x y w h)
            | otherwise = Left Invalid

-- Deadline is the original absolute CLOCK_MONOTONIC nanosecond value. The
-- caller must validate future/30-second admission against the real clock;
-- this pure codec cannot extend it or assert that it is currently live.
startup :: Int -> Int -> Int -> Text -> SessionId -> Either ProtocolError Startup
startup a b c deadline incarnation = do
  unless (a /= b && b /= c && a /= c) (Left Invalid)
  oa <- either (const (Left Invalid)) Right (makeOrigin a)
  ob <- either (const (Left Invalid)) Right (makeOrigin b)
  oc <- either (const (Left Invalid)) Right (makeOrigin c)
  d <- counter False deadline
  pure (Startup oa ob oc a b c d incarnation)
startupOrigins :: Startup -> (Origin, Origin, Origin)
startupOrigins (Startup a b c _ _ _ _ _) = (a,b,c)
startupDeadline :: Startup -> Text
startupDeadline (Startup _ _ _ _ _ _ d _) = renderCounter d
startupIncarnation :: Startup -> SessionId
startupIncarnation (Startup _ _ _ _ _ _ _ i) = i

bytes :: J.Json -> B.ByteString
bytes = TE.encodeUtf8 . J.renderJson
parse :: Int -> Int -> B.ByteString -> Either ProtocolError J.Json
parse cap depth raw = do
  limits <- either (const (Left Invalid)) Right (J.bounds cap depth)
  either (const (Left Invalid)) Right (J.decodeStrict limits raw)
exact :: [Text] -> J.Json -> Either ProtocolError [(Text,J.Json)]
exact keys value = either (const (Left Invalid)) Right (J.exactObject keys value)
field :: Text -> [(Text,J.Json)] -> Either ProtocolError J.Json
field key entries = maybe (Left Invalid) Right (lookup key entries)
textValue :: J.Json -> Either ProtocolError Text
textValue (J.JString value) = Right value
textValue _ = Left Invalid
number :: Int -> Int -> J.Json -> Either ProtocolError Int
number low high (J.JNumber value) = case reads (T.unpack value) of
  [(n,"")] | n >= low && n <= high && T.pack (show n) == value -> Right n
  _ -> Left Invalid
number _ _ _ = Left Invalid
counterField :: Bool -> Text -> [(Text,J.Json)] -> Either ProtocolError Counter
counterField allowZero name entries = field name entries >>= textValue >>= counter allowZero
jcounter :: Counter -> J.Json
jcounter = J.JString . renderCounter
sidText :: SessionId -> Text
sidText (SessionId value) = renderCounter value
ridText :: RequestId -> Text
ridText (RequestId value) = renderCounter value

-- Even values constructed in-process are rendered then decoded strictly, so
-- duplicate keys, invalid JSON numbers, depth and byte limits cannot bypass
-- the wire validator. Only an owner-validated projection may be supplied by
-- the broker: syntax validation here does not grant projection authority.
projection :: J.Json -> Either ProtocolError Projection
projection value = do
  _ <- measure 15 value
  let raw = bytes value
  when (B.length raw > maxPayloadBytes) (Left TooLarge)
  checked <- parse maxPayloadBytes 15 raw
  case checked of J.JObject _ -> pure (Projection checked); _ -> Left Invalid
projectionJson :: Projection -> J.Json
projectionJson (Projection value) = value

-- Check the exact rendered byte count before allocating rendered bytes. The
-- supplied value is still required to be an owner-validated snapshot.
measure :: Int -> J.Json -> Either ProtocolError Int
measure depth value = case value of
  J.JObject entries | depth > 0 -> do
    (body,_) <- foldM (\(n,first) (key,item) -> do
      k <- measureText True key
      v <- measure (depth-1) item
      itemSize <- addBound k =<< addBound v 1
      total <- addBound n =<< addBound itemSize (if first then 0 else 1)
      pure (total,False)) (0,True) entries
    addBound 2 body
  J.JArray entries | depth > 0 -> do
    (body,_) <- foldM (\(n,first) item -> do
      v <- measure (depth-1) item
      total <- addBound n =<< addBound v (if first then 0 else 1)
      pure (total,False)) (0,True) entries
    addBound 2 body
  J.JObject _ -> Left Invalid
  J.JArray _ -> Left Invalid
  J.JString t -> measureText True t
  J.JNumber t -> measureText False t
  J.JBool True -> Right 4
  J.JBool False -> Right 5
  J.JNull -> Right 4
  where
    addBound a b | a > maxPayloadBytes - b = Left TooLarge
                 | otherwise = Right (a+b)
    measureText quoted t = do
      n <- T.foldl' step (Right 0) t
      addBound n (if quoted then 2 else 0)
      where
        step acc ch = do
          n <- acc
          let o = ord ch
              count | quoted && (ch == '"' || ch == '\\') = 2
                    | quoted && o < 32 = 6
                    | o < 128 = 1
                    | o < 2048 = 2
                    | o < 65536 = 3
                    | otherwise = 4
          addBound n count

scopeJson :: Scope -> J.Json
scopeJson (Scope a b) = J.JObject [("id",jcounter a),("generation",jcounter b)]
parseScope :: J.Json -> Either ProtocolError Scope
parseScope value = do
  fs <- exact ["id","generation"] value
  Scope <$> counterField False "id" fs <*> counterField False "generation" fs
boxJson :: Box -> J.Json
boxJson (Box x y w h) = J.JArray (map (J.JNumber . T.pack . show) [x,y,w,h])
parseBox :: J.Json -> Either ProtocolError Box
parseBox (J.JArray [x,y,w,h]) = do
  let part = fmap fromIntegral . number (-2147483648) 2147483647
  a <- part x; b <- part y; c <- part w; d <- part h
  box a b c d
parseBox _ = Left Invalid

eventJson :: Event -> J.Json
eventJson event = case event of
  Topology rev Nothing -> J.JObject [("viewProtocol",J.JNumber "1"),("kind",J.JString "view-topology"),("revision",jcounter rev),("views",J.JArray [])]
  Topology rev (Just (s,Nothing)) -> J.JObject [("viewProtocol",J.JNumber "1"),("kind",J.JString "view-topology"),("revision",jcounter rev),("views",J.JArray [scopeJson s])]
  Topology rev (Just (s,Just rect)) -> J.JObject [("viewProtocol",J.JNumber "2"),("kind",J.JString "view-topology"),("revision",jcounter rev),("views",J.JArray [scopeJson s]),("locations",J.JArray [J.JObject [("scope",scopeJson s),("box",boxJson rect)]])]
  Dismiss s lease -> J.JObject [("scope",scopeJson s),("lease",jcounter lease)]
  Escape s publication lease -> J.JObject [("scope",scopeJson s),("publication",jcounter publication),("lease",jcounter lease)]
  Reflow s lease -> J.JObject [("scope",scopeJson s),("lease",jcounter lease)]

parseEvent :: Method -> J.Json -> Either ProtocolError Event
parseEvent OwnerTopology value = do
  version <- case value of J.JObject fs -> field "viewProtocol" fs; _ -> Left Invalid
  fs <- case version of
    J.JNumber "1" -> exact ["viewProtocol","kind","revision","views"] value
    J.JNumber "2" -> exact ["viewProtocol","kind","revision","views","locations"] value
    _ -> Left Invalid
  kind <- field "kind" fs
  unless (kind == J.JString "view-topology") (Left Invalid)
  rev <- counterField False "revision" fs
  views <- field "views" fs
  case (version,views) of
    (J.JNumber "1",J.JArray []) -> pure (Topology rev Nothing)
    (J.JNumber "1",J.JArray [v]) -> do s <- parseScope v; pure (Topology rev (Just (s,Nothing)))
    (J.JNumber "2",J.JArray [v]) -> do
      s <- parseScope v
      locations <- field "locations" fs
      loc <- case locations of J.JArray [item] -> exact ["scope","box"] item; _ -> Left Invalid
      locScope <- field "scope" loc >>= parseScope
      unless (locScope == s) (Left Invalid)
      rect <- field "box" loc >>= parseBox
      pure (Topology rev (Just (s,Just rect)))
    _ -> Left Invalid
parseEvent selectedMethod value = do
  fs <- exact (if selectedMethod == OwnerEscape then ["scope","publication","lease"] else ["scope","lease"]) value
  s <- field "scope" fs >>= parseScope
  lease <- counterField True "lease" fs
  case selectedMethod of
    OwnerDismiss -> pure (Dismiss s lease)
    OwnerReflow -> pure (Reflow s lease)
    OwnerEscape -> Escape s <$> counterField False "publication" fs <*> pure lease
    _ -> Left Invalid

method :: Request -> Method
method GetStop = Stop
method GetRemaining = Remaining
method GetLastProjection = LastProjection
method (OwnerEvent event) = case event of Topology _ _ -> OwnerTopology; Dismiss _ _ -> OwnerDismiss; Escape _ _ _ -> OwnerEscape; Reflow _ _ -> OwnerReflow
methodName :: Method -> Text
methodName m = case m of Stop -> "stop"; Remaining -> "remaining"; LastProjection -> "lastProjection"; OwnerTopology -> "topology"; OwnerDismiss -> "dismiss"; OwnerEscape -> "escape"; OwnerReflow -> "reflow"
parseMethod :: Text -> Either ProtocolError Method
parseMethod value = case [m | m <- [Stop,Remaining,LastProjection,OwnerTopology,OwnerDismiss,OwnerEscape,OwnerReflow], methodName m == value] of
  [m] -> Right m
  _ -> Left Invalid
requestBody :: Request -> J.Json
requestBody (OwnerEvent e) = eventJson e
requestBody _ = J.JNull
parseRequestBody :: Method -> J.Json -> Either ProtocolError Request
parseRequestBody Stop J.JNull = Right GetStop
parseRequestBody Remaining J.JNull = Right GetRemaining
parseRequestBody LastProjection J.JNull = Right GetLastProjection
parseRequestBody m value = OwnerEvent <$> parseEvent m value
replyBody :: Reply -> J.Json
replyBody r = case r of
  StopReply value -> J.JBool value
  RemainingReply n -> J.JNumber (T.pack (show n))
  ProjectionReply Nothing -> J.JNull
  ProjectionReply (Just p) -> projectionJson p
  EventReply result -> J.JString (case result of Accepted -> "accepted"; Stale -> "stale"; Refused -> "refused")
parseReplyBody :: Method -> J.Json -> Either ProtocolError Reply
parseReplyBody Stop (J.JBool b) = Right (StopReply b)
parseReplyBody Remaining value = RemainingReply <$> number 0 30000000 value
parseReplyBody LastProjection J.JNull = Right (ProjectionReply Nothing)
parseReplyBody LastProjection value = ProjectionReply . Just <$> projection value
parseReplyBody m (J.JString value) | m `elem` [OwnerTopology,OwnerDismiss,OwnerEscape,OwnerReflow] =
  EventReply <$> case value of "accepted" -> Right Accepted; "stale" | m /= OwnerTopology -> Right Stale; "refused" -> Right Refused; _ -> Left Invalid
parseReplyBody _ _ = Left Invalid
replyMatches :: Method -> Reply -> Bool
replyMatches m r = case (m,r) of
  (Stop,StopReply _) -> True; (Remaining,RemainingReply n) -> n >= 0 && n <= 30000000
  (LastProjection,ProjectionReply _) -> True
  (OwnerTopology,EventReply Stale) -> False
  (event,EventReply _) -> event `elem` [OwnerTopology,OwnerDismiss,OwnerEscape,OwnerReflow]
  _ -> False

-- Framing: 4-byte big-endian header length, strict JSON header, then one
-- standalone strict JSON payload. Transport must separately frame the whole
-- message, reject its length before allocation, authenticate every fragment,
-- and bind it to the owned peer; this codec alone cannot establish provenance.
word32 :: Int -> B.ByteString
word32 n = B.pack [fromIntegral (n `shiftR` 24),fromIntegral (n `shiftR` 16),fromIntegral (n `shiftR` 8),fromIntegral n]
headerLength :: B.ByteString -> Int
headerLength = fromIntegral . B.foldl' (\n w -> (n `shiftL` 8) .|. fromIntegral w) (0 :: Word32)
wire :: Text -> SessionId -> RequestId -> Method -> J.Json -> Either ProtocolError B.ByteString
wire direction s r m body = do
  let h = bytes (J.JObject [("version",J.JNumber "1"),("direction",J.JString direction),("session",J.JString (sidText s)),("request",J.JString (ridText r)),("method",J.JString (methodName m))])
      p = bytes body
  when (B.length h > maxHeaderBytes || B.length p > maxPayloadBytes) (Left TooLarge)
  _ <- parse maxPayloadBytes 15 p
  pure (word32 (B.length h) <> h <> p)
readWire :: Text -> B.ByteString -> Either ProtocolError (SessionId,RequestId,Method,J.Json)
readWire direction raw = do
  when (B.length raw > maxFrameBytes || B.length raw < 5) (Left TooLarge)
  let n = headerLength (B.take 4 raw)
  when (n <= 0 || n > maxHeaderBytes || 4+n >= B.length raw) (Left Invalid)
  h <- parse maxHeaderBytes 3 (B.take n (B.drop 4 raw))
  fs <- exact ["version","direction","session","request","method"] h
  v <- field "version" fs; dir <- field "direction" fs
  unless (v == J.JNumber "1" && dir == J.JString direction) (Left Invalid)
  s <- field "session" fs >>= textValue >>= sessionId
  r <- field "request" fs >>= textValue >>= requestId
  m <- field "method" fs >>= textValue >>= parseMethod
  p <- parse maxPayloadBytes 15 (B.drop (4+n) raw)
  pure (s,r,m,p)

-- Startup is a separate broker-to-engine one-time object. The transport must
-- bind it to the validated exec and never accept it as an engine request.
encodeStartup :: Startup -> B.ByteString
encodeStartup (Startup _ _ _ a b c d s) = bytes (J.JObject [("version",J.JNumber "1"),("controller",J.JNumber (T.pack (show a))),("bar",J.JNumber (T.pack (show b))),("popup",J.JNumber (T.pack (show c))),("deadline",jcounter d),("incarnation",J.JString (sidText s))])
decodeStartup :: B.ByteString -> Either ProtocolError Startup
decodeStartup raw = do
  value <- parse maxHeaderBytes 3 raw
  fs <- exact ["version","controller","bar","popup","deadline","incarnation"] value
  v <- field "version" fs
  unless (v == J.JNumber "1") (Left Invalid)
  a <- field "controller" fs >>= number 1024 65535
  b <- field "bar" fs >>= number 1024 65535
  c <- field "popup" fs >>= number 1024 65535
  d <- field "deadline" fs >>= textValue
  s <- field "incarnation" fs >>= textValue >>= sessionId
  startup a b c d s

newSession :: Startup -> Session
newSession initial = Session (startupIncarnation initial) (either (const Nothing) Just (parseCounter False "1")) Nothing False
isPoisoned :: Session -> Bool
isPoisoned (Session _ _ _ bad) = bad
poisonSession :: Session -> Session
poisonSession (Session s n p _) = Session s n p True
next :: Counter -> Maybe Counter
next value = either (const Nothing) Just (addCounter value 1)
failClosed :: Session -> ProtocolError -> (Session, Either ProtocolError a)
failClosed state problem = (poisonSession state, Left problem)

-- Client: issue exactly one request. Any invalid transition poisons the session.
-- A failed or uncertain request write must poison; the original D is enforced
-- independently by the broker, never extended from a Remaining reply.
beginRequest :: Session -> Request -> (Session, Either ProtocolError B.ByteString)
beginRequest state@(Session s nextId pending bad) req
  | bad = (state,Left Poisoned)
  | otherwise = case (nextId,pending) of
      (Nothing,_) -> failClosed state Exhausted
      (_,Just _) -> failClosed state InvalidState
      (Just n,Nothing) ->
        let checkedRequest = do
              decoded <- parseRequestBody (method req) (requestBody req)
              unless (decoded == req) (Left Invalid)
              wire "request" s (RequestId n) (method req) (requestBody req)
        in case checkedRequest of
          Left err -> failClosed state err
          Right raw -> (Session s (next n) (Just (RequestId n,method req,AwaitReply)) False,Right raw)

-- Server must execute a returned request at most once and must never retry it
-- after any uncertain transport outcome. EOF/timeouts call poisonSession.
acceptRequest :: Session -> B.ByteString -> (Session, Either ProtocolError Request)
acceptRequest state@(Session s nextId pending bad) raw
  | bad = (state,Left Poisoned)
  | otherwise = case (nextId,pending) of
      (Nothing,_) -> failClosed state Exhausted
      (_,Just _) -> failClosed state InvalidState
      (Just n,Nothing) -> case readWire "request" raw of
        Left err -> failClosed state err
        Right (actual,r,m,p)
          | actual /= s -> failClosed state ForeignSession
          | r /= RequestId n -> failClosed state Replay
          | otherwise -> case parseRequestBody m p of
              Left err -> failClosed state err
              Right req -> (Session s (next n) (Just (r,m,NeedReply)) False,Right req)
finishRequest :: Session -> Reply -> (Session, Either ProtocolError B.ByteString)
finishRequest state@(Session s n pending bad) reply
  | bad = (state,Left Poisoned)
  | otherwise = case pending of
      Nothing -> failClosed state InvalidState
      Just (r,m,NeedReply) | not (replyMatches m reply) -> failClosed state WrongReply
                           | otherwise -> case wire "reply" s r m (replyBody reply) of
                     Left err -> failClosed state err
                     Right raw -> (Session s n (Just (r,m,SendingReply)) False,Right raw)
      Just _ -> failClosed state InvalidState

-- The sole transport owner must call this only after a complete confirmed
-- write. On partial write, timeout, EOF or uncertainty it must poison instead.
confirmReplySent :: Session -> (Session, Either ProtocolError ())
confirmReplySent state@(Session s n pending bad)
  | bad = (state,Left Poisoned)
  | otherwise = case pending of
      Just (_,_,SendingReply) -> (Session s n Nothing False,Right ())
      _ -> failClosed state InvalidState
acceptReply :: Session -> B.ByteString -> (Session, Either ProtocolError Reply)
acceptReply state@(Session s n pending bad) raw
  | bad = (state,Left Poisoned)
  | otherwise = case pending of
      Nothing -> failClosed state InvalidState
      Just (expected,expectedMethod,AwaitReply) -> case readWire "reply" raw of
        Left err -> failClosed state err
        Right (actual,r,m,p)
          | actual /= s -> failClosed state ForeignSession
          | r /= expected || m /= expectedMethod -> failClosed state WrongReply
          | otherwise -> case parseReplyBody m p of
              Left err -> failClosed state err
              Right reply -> (Session s n Nothing False,Right reply)
      Just _ -> failClosed state InvalidState
