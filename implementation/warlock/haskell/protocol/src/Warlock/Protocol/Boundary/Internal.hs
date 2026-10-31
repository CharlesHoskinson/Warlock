{-# LANGUAGE OverloadedStrings #-}
-- Internal owner integration only. A validated envelope is not a native grant.
module Warlock.Protocol.Boundary.Internal
 (Direction(..), Reason(..), Envelope, Gate, GateStatus(..), newGate,
  decodeFor, foldEnvelope, dispatch, retire, gateStatus, rejectionReasons) where
import Control.Concurrent.MVar
import Control.Exception (SomeException,mask,uninterruptibleMask_,throwIO,try)
import qualified Data.ByteString as B
import Data.Text (Text)
import qualified Data.Text as T
import qualified Warlock.Protocol.Codec as C
import Warlock.Protocol.Identity (Binding)
import qualified Warlock.Protocol.StrictJson as J
import Warlock.Protocol.Wire (parseBinding)

data Direction = FromElm | FromNative deriving (Eq,Show)
data Reason = BadUtf8 | TooLarge | BadNul | TooDeep | DuplicateField | Malformed | BadSchema | UnsupportedVersion | BadDigest | ForeignBinding | GateRetired | GateBusy | HandlerFailed deriving (Eq,Show)
data Envelope = Client C.CheckedClient | Server C.CheckedServer deriving (Eq,Show)
data GateStatus = Live !Int | Draining !Int | Retired deriving (Eq,Show)
data State = State { status :: !GateStatus, reasons :: ![Reason] }
data Gate = Gate Binding (Envelope -> IO ()) (MVar State)

-- This function is NOT exposed in the public library. The existing trusted
-- owner must provide its live authenticated binding and own callback lifecycle.
newGate :: Binding -> (Envelope -> IO ()) -> IO Gate
newGate owner action = Gate owner action <$> newMVar (State (Live 0) [])
record :: Reason -> State -> State
record reason s =
 let bounded = take 128 (reason : reasons s)
 in forceReasons bounded `seq` s {reasons = bounded}
 where
  forceReasons [] = ()
  forceReasons (r:rs) = r `seq` forceReasons rs
-- Publish a forced state, not a closure retaining the previous state/history.
publish :: State -> IO State
publish next = next `seq` pure next
publishWith :: State -> a -> IO (State,a)
publishWith next value = next `seq` pure (next,value)

-- Observed checked data only. This cannot create a native grant or certificate.
foldEnvelope :: (C.CheckedClient -> a) -> (C.CheckedServer -> a) -> Envelope -> a
foldEnvelope client server envelope = case envelope of
 Client value -> client value
 Server value -> server value
jsonReason :: J.DecodeError -> Reason
jsonReason e = case e of
 J.InvalidBounds -> BadSchema
 J.ByteLimit -> TooLarge
 J.InvalidUtf8 -> BadUtf8
 J.Nul -> BadNul
 J.DepthLimit -> TooDeep
 J.MalformedJson -> Malformed
 J.DuplicateKey _ -> DuplicateField
 J.UnexpectedFields -> BadSchema

-- Binding is checked against the owner's current live registration; historic
-- records use deliveryBinding, never originalBinding as a fresh authority.
decodeFor :: Binding -> Direction -> B.ByteString -> Either Reason Envelope
decodeFor expected direction raw = do
 bounds <- either (Left . jsonReason) Right (J.bounds 65536 16)
 root <- either (Left . jsonReason) Right (J.decodeStrict bounds raw)
 top <- either (Left . jsonReason) Right (J.exactObject ["version","kind","body"] root)
 v <- maybe (Left BadSchema) Right (lookup "version" top)
 case v of
  J.JNumber "1" -> Right ()
  J.JNumber "2" -> Right ()
  J.JNumber _ -> Left UnsupportedVersion
  _ -> Left BadSchema
 kind <- case lookup "kind" top of Just (J.JString k) -> Right k; _ -> Left BadSchema
 fields <- case lookup "body" top of Just (J.JObject xs) -> Right xs; _ -> Left BadSchema
 let name = if kind `elem` ["lookup","lookup-result","history"] then "deliveryBinding" else "binding"
 actual <- maybe (Left BadSchema) (either (const (Left BadSchema)) Right . parseBinding) (lookup name fields)
 if actual == expected then Right () else Left ForeignBinding
 case direction of
  FromElm -> either (Left . codecReason) (Right . Client) (C.decodeClientChecked raw)
  FromNative -> either (Left . codecReason) (Right . Server) (C.decodeServerChecked raw)
 where
  codecReason :: Text -> Reason
  codecReason message = if "positional key mismatch" `T.isInfixOf` message then BadDigest else BadSchema

dispatch :: Gate -> Direction -> B.ByteString -> IO (Either Reason ())
dispatch (Gate owner action state) direction raw = mask $ \restore -> do
 case decodeFor owner direction raw of
  Left reason -> modifyMVar_ state (publish . record reason) >> pure (Left reason)
  Right envelope -> do
   admitted <- modifyMVar state $ \s -> case status s of
    Live n | n < 64 -> publishWith (s {status=Live (n+1)}) (Right ())
    Live _ -> publishWith (record GateBusy s) (Left GateBusy)
    _ -> publishWith (record GateRetired s) (Left GateRetired)
   case admitted of
    Left reason -> pure (Left reason)
    Right () -> do
     result <- try (restore (action envelope)) :: IO (Either SomeException ())
     uninterruptibleMask_ $ modifyMVar_ state $ \s -> do
      let next = case status s of
            Live n -> Live (n-1)
            Draining n | n == 1 -> Retired
                       | otherwise -> Draining (n-1)
            Retired -> Retired
          released = s {status=next}
      publish (case result of Left _ -> record HandlerFailed released; Right () -> released)
     either throwIO (const (pure (Right ()))) result
-- Existing admitted callbacks complete under caller-owned threads. No hidden
-- workers are created. Retired means none in flight; Draining is not retired.
retire :: Gate -> IO GateStatus
retire (Gate _ _ state) = modifyMVar state $ \s ->
 let next = case status s of Live 0 -> Retired; Live n -> Draining n; other -> other
 in publishWith (s {status=next}) next
gateStatus :: Gate -> IO GateStatus
gateStatus (Gate _ _ state) = status <$> readMVar state
rejectionReasons :: Gate -> IO [Reason]
rejectionReasons (Gate _ _ state) = reverse . reasons <$> readMVar state
