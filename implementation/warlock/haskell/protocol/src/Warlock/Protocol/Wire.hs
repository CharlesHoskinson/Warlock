{-# LANGUAGE OverloadedStrings #-}
-- Proposal maps only Elm->Haskell v0; no native authority follows from decoding.
module Warlock.Protocol.Wire (SelectionId, Choice(..), Lookup, Command(..), decodeCommand, parseBinding, parseIntent, parseSelection, parseLookup) where

import qualified Data.ByteString as BS
import Data.Char (isAsciiLower, isDigit)
import qualified Data.Text.Encoding as TE
import Data.Text (Text)
import qualified Data.Text as T
import Warlock.Protocol.StrictJson
import Warlock.Protocol.Identity
import Warlock.Protocol.Custody (Intent, Operation(Restore), intent)

newtype SelectionId = SelectionId Text deriving (Eq, Show)
data Choice = Commit | Cancel deriving (Eq, Show)
data Lookup = Lookup Binding Counter Text Binding Intent Json (Maybe Counter) deriving (Eq, Show)
data Command = Negotiate Binding Counter | Prepare Binding Intent SelectionId
             | Decide Binding Intent SelectionId Counter Counter Choice | LookupRequest Lookup deriving (Eq, Show)

-- Choice is an untrusted request; no admission is implied.
decodeCommand :: BS.ByteString -> Either Text Command
decodeCommand bytes = do
  limit <- firstError (bounds 65536 16)
  raw <- firstError (decodeStrict limit bytes)
  top <- firstError (exactObject ["version","kind","body"] raw)
  version <- field "version" top
  if version `elem` [JNumber "1",JNumber "2"] then pure () else Left "unsupported version"
  kind <- field "kind" top >>= textValue
  body <- field "body" top
  case kind of
    "negotiate" -> do
      o <- firstError (exactObject ["binding","requestId"] body)
      owner <- field "binding" o >>= parseBinding
      request <- field "requestId" o >>= positive
      pure (Negotiate owner request)
    "prepare" -> do
      o <- firstError (exactObject ["binding","intent","selectionId"] body)
      owner <- field "binding" o >>= parseBinding
      target <- field "intent" o >>= parseIntent owner
      selection <- field "selectionId" o >>= selectionId
      pure (Prepare owner target selection)
    "decision" -> do
      o <- firstError (exactObject ["binding","intent","selectionId","deadlineMonotonicNs","preparedId","decision"] body)
      owner <- field "binding" o >>= parseBinding
      target <- field "intent" o >>= parseIntent owner
      selection <- field "selectionId" o >>= selectionId
      deadline <- field "deadlineMonotonicNs" o >>= positive
      prepared <- field "preparedId" o >>= positive
      decision <- field "decision" o >>= textValue
      case decision of
        "commit" -> pure (Decide owner target selection deadline prepared Commit)
        "cancel" -> pure (Decide owner target selection deadline prepared Cancel)
        _ -> Left "unsupported decision"
    "lookup" | version == JNumber "2" -> LookupRequest <$> parseLookup body
    _ -> Left "unsupported kind"

firstError :: Show a => Either a b -> Either Text b
firstError = either (Left . T.pack . show) Right
field :: Text -> [(Text,Json)] -> Either Text Json
field key values = maybe (Left "missing field") Right (lookup key values)
textValue :: Json -> Either Text Text
textValue (JString text) = Right text
textValue _ = Left "string required"
positive :: Json -> Either Text Counter
positive value = textValue value >>= firstError . parseCounter False
selectionId :: Json -> Either Text SelectionId
selectionId value = do
  raw <- textValue value
  let lowerHex c = isDigit c && c <= '9' || isAsciiLower c && c <= 'f'
  if T.length raw == 32 && T.all lowerHex raw then Right (SelectionId raw)
  else Left "invalid selection identity"
parseBinding :: Json -> Either Text Binding
parseBinding value = do
  o <- firstError (exactObject ["lifetime","session","frontend"] value)
  a <- field "lifetime" o >>= positive
  b <- field "session" o >>= positive
  c <- field "frontend" o >>= positive
  firstError (binding a b c)
parseIntent :: Binding -> Json -> Either Text Intent
parseIntent owner value = do
  o <- firstError (exactObject ["request","generation","incarnation","operation","context"] value)
  request <- field "request" o >>= positive
  generation <- field "generation" o >>= positive
  incarnation <- field "incarnation" o >>= positive
  operation <- field "operation" o >>= textValue
  if operation /= "restore" then Left "unsupported operation" else pure ()
  cv <- field "context" o
  co <- firstError (exactObject ["lifetime","epoch","output","revision"] cv)
  l <- field "lifetime" co >>= positive
  e <- field "epoch" co >>= positive
  out <- field "output" co >>= positive
  rev <- field "revision" co >>= positive
  ctx <- firstError (context owner l e out rev)
  firstError (intent owner request generation incarnation ctx Restore)

-- Selection is an untrusted display token, not authority to execute.
parseSelection :: Json -> Either Text (Text,Counter)
parseSelection j = do
  o <- firstError (exactObject ["selectionId","scope","publication","lease","controlId","clock","acceptedMonotonicNs","deadlineMonotonicNs"] j)
  token <- field "selectionId" o >>= selectionId
  let SelectionId selected = token
  sc <- field "scope" o >>= firstError . exactObject ["id","generation"]
  _ <- field "id" sc >>= positive
  _ <- field "generation" sc >>= positive
  _ <- field "publication" o >>= positive
  _ <- field "lease" o >>= positive
  control <- field "controlId" o >>= textValue
  if T.null control || BS.length (TE.encodeUtf8 control) > 512 then Left "bad control" else pure ()
  clock <- field "clock" o >>= textValue
  if clock /= "CLOCK_MONOTONIC" then Left "bad clock" else pure ()
  accepted <- field "acceptedMonotonicNs" o >>= positive
  deadline <- field "deadlineMonotonicNs" o >>= positive
  expected <- firstError (addCounter accepted 2000000000)
  if deadline == expected then Right (selected,deadline) else Left "deadline differs"

parseLookup :: Json -> Either Text Lookup
parseLookup body = do
  o <- firstError (exactObject ["deliveryBinding","requestId","key","originalBinding","intent","selection","preparedId"] body)
  delivery <- field "deliveryBinding" o >>= parseBinding
  request <- field "requestId" o >>= positive
  key <- field "key" o >>= textValue
  if T.length key == 64 && T.all (\c -> (c >= '0' && c <= '9') || (c >= 'a' && c <= 'f')) key then pure () else Left "bad key"
  original <- field "originalBinding" o >>= parseBinding
  if lifetime delivery == lifetime original then pure () else Left "foreign lifetime"
  target <- field "intent" o >>= parseIntent original
  sel <- field "selection" o
  _ <- parseSelection sel
  prepared <- field "preparedId" o
  pid <- case prepared of JNull -> Right Nothing; _ -> Just <$> positive prepared
  pure (Lookup delivery request key original target sel pid)
