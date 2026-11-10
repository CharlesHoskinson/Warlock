{-# LANGUAGE OverloadedStrings #-}
-- QA configuration data. This value grants no compositor or focus authority.
module OpenerAdmission
  (Configuration, decodeConfiguration, configurationDeadline, configurationNonce,
   configurationBinding) where

import Control.Monad (unless)
import qualified Data.ByteString as B
import Data.Text (Text)
import qualified Data.Text as T
import Data.Word (Word64)
import qualified Warlock.Protocol.Identity as I
import Warlock.Protocol.StrictJson

data Configuration = Configuration Integer Text I.Binding

configurationDeadline :: Configuration -> Integer
configurationDeadline (Configuration deadline _ _) = deadline
configurationNonce :: Configuration -> Text
configurationNonce (Configuration _ nonce _) = nonce
configurationBinding :: Configuration -> I.Binding
configurationBinding (Configuration _ _ owner) = owner

decodeConfiguration :: Integer -> Integer -> B.ByteString -> Either String Configuration
decodeConfiguration now inherited raw = do
  unless (now >= 0 && inherited > now && inherited-now <= 28000000000
    && inherited <= toInteger (maxBound :: Word64)) (Left "original deadline refused")
  limits <- shown (bounds 4096 8)
  value <- shown (decodeStrict limits raw)
  fields <- shown (exactObject ["schema","nonce","binding","deadlineMonotonicNs"] value)
  schema <- field "schema" fields
  unless (schema == JNumber "1") (Left "schema refused")
  nonce <- field "nonce" fields >>= text
  unless (T.length nonce == 64 && T.all lowerHex nonce) (Left "nonce refused")
  deadline <- field "deadlineMonotonicNs" fields >>= text >>= shown . I.parseCounter False
  unless (I.renderCounter deadline == T.pack (show inherited)) (Left "inherited deadline differs")
  ownerFields <- field "binding" fields >>= shown . exactObject ["lifetime","session","frontend"]
  life <- identity "lifetime" ownerFields
  session <- identity "session" ownerFields
  frontend <- identity "frontend" ownerFields
  owner <- shown (I.binding life session frontend)
  pure (Configuration inherited nonce owner)
  where
    lowerHex c = (c >= '0' && c <= '9') || (c >= 'a' && c <= 'f')
    identity key fields = field key fields >>= text >>= shown . I.parseCounter False

shown :: Show e => Either e a -> Either String a
shown = either (Left . show) Right

field :: Text -> [(Text,Json)] -> Either String Json
field key fields = maybe (Left "missing field") Right (lookup key fields)

text :: Json -> Either String Text
text (JString value) = Right value
text _ = Left "string required"
