{-# LANGUAGE OverloadedStrings #-}
-- Codec values are observations only; they are not native evidence or permission.
module Warlock.Protocol.Codec (CheckedClient, CheckedServer, decodeClientChecked, decodeServerChecked, encodeClientChecked, encodeServerChecked) where
import qualified Data.ByteString as BS
import qualified Crypto.Hash.SHA256 as SHA
import Data.Char (ord)
import Data.Text (Text)
import qualified Data.Text as T
import qualified Data.Text.Encoding as TE
import Numeric (showHex)
import Warlock.Protocol.StrictJson
import Warlock.Protocol.Wire (decodeCommand)
import Warlock.Protocol.Server (ServerFrame, ServerKind(..), serverKind, serverJson, decodeServer, CheckedHistory, verifyHistoryKey, checkedHistoryFrame, verifyPositionalKey, verifyLookupResultKey)

newtype ClientFrame = ClientFrame Json deriving (Eq, Show)
decodeClient :: BS.ByteString -> Either Text ClientFrame
decodeClient raw = do
  _ <- decodeCommand raw
  b <- either (Left . T.pack . show) Right (bounds 65536 16)
  ClientFrame <$> either (Left . T.pack . show) Right (decodeStrict b raw)
encodeServer :: ServerFrame -> Either Text BS.ByteString
encodeServer frame = do
  let raw = TE.encodeUtf8 (render (serverJson frame))
  _ <- decodeServer raw
  pure raw
render :: Json -> Text
render json = case json of
  JObject pairs -> "{" <> T.intercalate "," [quote key <> ":" <> render value | (key,value) <- pairs] <> "}"
  JArray values -> "[" <> T.intercalate "," (map render values) <> "]"
  JString value -> quote value
  JNumber value -> value
  JBool True -> "true"
  JBool False -> "false"
  JNull -> "null"
quote :: Text -> Text
quote value = "\"" <> T.concatMap escaped value <> "\""
escaped :: Char -> Text
escaped c = case c of
  '"' -> "\\\""
  '\\' -> "\\\\"
  _ | ord c < 32 -> let h = showHex (ord c) "" in "\\u" <> T.pack (replicate (4 - length h) '0' ++ h)
    | otherwise -> T.singleton c

-- CheckedServer validates K for historical frames using the chosen reviewed
-- backend SHA256. It is still untrusted wire data, never native evidence.
data CheckedServer = CheckedOrdinary ServerFrame | CheckedHistoric CheckedHistory deriving (Eq, Show)
decodeServerChecked :: BS.ByteString -> Either Text CheckedServer
decodeServerChecked bytes = do
  frame <- decodeServer bytes
  if serverKind frame == History then CheckedHistoric <$> verifyHistoryKey SHA.hash frame
  else if serverKind frame == LookupResult then verifyLookupResultKey SHA.hash frame >> Right (CheckedOrdinary frame)
  else Right (CheckedOrdinary frame)
encodeServerChecked :: CheckedServer -> Either Text BS.ByteString
encodeServerChecked checked = case checked of
  CheckedOrdinary frame -> encodeServer frame
  CheckedHistoric history -> encodeServer (checkedHistoryFrame history)

-- Checked client lookup validates its positional key; not an authenticated
-- session, query permission, persisted receipt, or right to act.
newtype CheckedClient = CheckedClient ClientFrame deriving (Eq, Show)
decodeClientChecked :: BS.ByteString -> Either Text CheckedClient
decodeClientChecked raw = do
  frame <- decodeClient raw
  let ClientFrame root = frame
  fields <- case root of JObject pairs -> Right pairs; _ -> Left "object required"
  case (lookup "kind" fields,lookup "body" fields) of
    (Just (JString "lookup"),Just (JObject body)) -> do
      key <- textField "key" body
      original <- required "originalBinding" body
      target <- required "intent" body
      verifyPositionalKey SHA.hash key original target
      pure (CheckedClient frame)
    _ -> pure (CheckedClient frame)
required :: Text -> [(Text,Json)] -> Either Text Json
required name fields = maybe (Left "missing field") Right (lookup name fields)
textField :: Text -> [(Text,Json)] -> Either Text Text
textField name fields = do
  x <- required name fields
  case x of JString text -> Right text; _ -> Left "text required"

-- Re-encoding never grants action authority and validates the resulting frame.
encodeClientChecked :: CheckedClient -> Either Text BS.ByteString
encodeClientChecked (CheckedClient (ClientFrame frame)) = do
  let raw = TE.encodeUtf8 (render frame)
  _ <- decodeClientChecked raw
  pure raw
