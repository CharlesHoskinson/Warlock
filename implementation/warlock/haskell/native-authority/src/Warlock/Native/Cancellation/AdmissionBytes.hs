{-# LANGUAGE OverloadedStrings #-}
-- Private canonical encoding only. Bytes and their hash do not grant admission.
module Warlock.Native.Cancellation.AdmissionBytes
 ( PairBytes, PairError(..), pendingFor, encodePair, pairKey, pendingBytes, reservedBytes, submittedBytes ) where
import qualified Crypto.Hash.SHA256 as SHA
import qualified Data.ByteString as B
import qualified Data.ByteString.Char8 as C
import Data.Char (ord)
import qualified Data.Text as T
import Numeric (showHex)
import Warlock.Native.Cancellation.Selection
import Warlock.Protocol.Custody (Intent,Operation(Restore),intentBinding,intentRequest,intentGeneration,intentIncarnation,intentContext,intentOperation)
import Warlock.Protocol.Identity (Counter,Binding,lifetime,session,frontend,contextLifetime,contextEpoch,contextOutput,contextRevision,renderCounter)

data PairError = WrongSelection | TooLarge deriving (Eq,Show)
data PairBytes = PairBytes !B.ByteString !B.ByteString !B.ByteString !B.ByteString deriving (Eq,Show)
pairKey, pendingBytes, reservedBytes, submittedBytes :: PairBytes -> B.ByteString
pairKey (PairBytes key _ _ _) = key
pendingBytes (PairBytes _ pending _ _) = pending
reservedBytes (PairBytes _ _ reserved _) = reserved
submittedBytes (PairBytes _ _ _ submitted) = submitted

quote :: T.Text -> B.ByteString
quote value = C.pack ('"' : concatMap escaped (T.unpack value) ++ "\"")
 where
  u4 n = let digits = showHex n "" in "\\u" ++ replicate (4-length digits) '0' ++ digits
  escaped ch = case ch of
   '"' -> "\\\""; '\\' -> "\\\\"; '\b' -> "\\b"; '\f' -> "\\f"; '\n' -> "\\n"; '\r' -> "\\r"; '\t' -> "\\t"
   _ | ord ch < 32 || ord ch >= 127 -> let n = ord ch in if n <= 65535 then u4 n else let k=n-65536 in u4 (55296+k `div` 1024) ++ u4 (56320+k `mod` 1024)
     | otherwise -> [ch]
strCounter :: Counter -> B.ByteString
strCounter = quote . renderCounter
object :: [(T.Text,B.ByteString)] -> B.ByteString
object fields = "{" <> B.intercalate "," [quote name <> ":" <> value | (name,value) <- fields] <> "}"
bindingJSON :: Binding -> B.ByteString
bindingJSON b = object [("frontend",strCounter (frontend b)),("lifetime",strCounter (lifetime b)),("session",strCounter (session b))]
intentJSON :: Intent -> B.ByteString
intentJSON action =
 let ctx = intentContext action
     contextJSON = object [("epoch",strCounter (contextEpoch ctx)),("lifetime",strCounter (contextLifetime ctx)),("output",strCounter (contextOutput ctx)),("revision",strCounter (contextRevision ctx))]
 in object [("context",contextJSON),("generation",strCounter (intentGeneration action)),("incarnation",strCounter (intentIncarnation action)),("operation","\"restore\""),("request",strCounter (intentRequest action))]
hexBytes :: B.ByteString -> B.ByteString
hexBytes = C.pack . concatMap (\byte -> let h=showHex byte "" in if length h==1 then '0':h else h) . B.unpack

-- Preview is untrusted canonical data for full inventory checks BEFORE spending
-- a selection. It grants neither publication nor queue/native permission.
pendingFor :: Intent -> Either PairError (B.ByteString,B.ByteString)
pendingFor action
 | intentOperation action /= Restore = Left WrongSelection
 | otherwise =
  let bound=intentBinding action; ctx=intentContext action
      fields=[strCounter (lifetime bound),strCounter (session bound),strCounter (frontend bound),"1",strCounter (intentRequest action),strCounter (intentGeneration action),strCounter (intentIncarnation action),"\"restore\"",strCounter (contextLifetime ctx),strCounter (contextEpoch ctx),strCounter (contextOutput ctx),strCounter (contextRevision ctx)]
      key=hexBytes (SHA.hash ("[" <> B.intercalate "," fields <> "]"))
      pending=object [("binding",bindingJSON bound),("effectProtocol","1"),("intent",intentJSON action),("schema","2"),("status","\"Pending\"")]
  in if B.length pending>4096 then Left TooLarge else Right (key,pending)

-- `spent` is an owner-issued prequeue selection; the caller still needs the
-- owner registry, locked durable pair writer and one-use enqueue discipline.
encodePair :: Selection -> Intent -> Either PairError PairBytes
encodePair selected action
 | selectionPhase selected /= Spent || selectionBinding selected /= intentBinding action || selectionIntent selected /= action || intentOperation action /= Restore = Left WrongSelection
 | otherwise = do
  (key,pending) <- pendingFor action
  let (viewId,viewGeneration) = selectionScope selected
      scope = object [("generation",strCounter viewGeneration),("id",strCounter viewId)]
      selection = object [("acceptedMonotonicNs",strCounter (selectionAccepted selected)),("clock","\"CLOCK_MONOTONIC\""),("controlId",quote (selectionControl selected)),("deadlineMonotonicNs",strCounter (selectionDeadline selected)),("lease",strCounter (selectionLease selected)),("publication",strCounter (selectionPublication selected)),("scope",scope),("selectionId",quote (selectionId selected))]
      companion state = object [("admission",pending),("key","\"" <> key <> "\""),("kind","\"host-cancellation-admission\""),("schema","1"),("selection",selection),("state",state)]
      reserved = companion "\"Reserved\""; submitted = companion "\"Submitted\""
  if B.length pending > 4096 || B.length reserved > 8192 || B.length submitted > 8192 then Left TooLarge else Right (PairBytes key pending reserved submitted)
