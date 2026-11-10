{-# LANGUAGE OverloadedStrings #-}
-- Private, unexecuted tests-first proposal. No GTK window or display is opened.
module Main (main) where

import Control.Monad (forM_, unless)
import qualified Data.ByteString as B
import qualified Data.Text as T
import qualified Data.Text.Encoding as TE
import Data.Either (isLeft, isRight)
import OpenerAdmission (decodeConfiguration, configurationDeadline, configurationNonce)
import Warlock.Protocol.StrictJson (Json(..), renderJson)

assert :: String -> Bool -> IO ()
assert label value = unless value (ioError (userError label))

now :: Integer
now = 100000000000

originalDeadline :: Integer
originalDeadline = now + 28000000000

nonce :: T.Text
nonce = T.replicate 64 "a"

binding :: Json
binding = JObject [("lifetime",JString "1"),("session",JString "2"),("frontend",JString "3")]

configuration :: Integer -> Json
configuration deadline = JObject
  [("schema",JNumber "1"),("nonce",JString nonce),("binding",binding)
  ,("deadlineMonotonicNs",JString (T.pack (show deadline)))]

encoded :: Json -> B.ByteString
encoded = TE.encodeUtf8 . renderJson

replace :: T.Text -> Json -> Json -> Json
replace key value (JObject fields) = JObject [(name,if name==key then value else old) | (name,old)<-fields]
replace _ _ value = value

main :: IO ()
main = do
  let input = configuration originalDeadline
      parse = decodeConfiguration now originalDeadline
      bad label value = assert label (isLeft (parse (encoded value)))
  case parse (encoded input) of
    Left _ -> assert "original inherited configuration is accepted" False
    Right admitted -> do
      assert "admission retains original absolute deadline" (configurationDeadline admitted==originalDeadline)
      assert "admission retains exact nonce" (configurationNonce admitted==nonce)
  bad "schema is exact" (replace "schema" (JNumber "2") input)
  bad "numeric schema cannot be a string" (replace "schema" (JString "1") input)
  bad "short nonce refused" (replace "nonce" (JString (T.take 63 nonce)) input)
  bad "uppercase nonce refused" (replace "nonce" (JString (T.replicate 64 "A")) input)
  bad "nonhex nonce refused" (replace "nonce" (JString (T.replicate 64 "g")) input)
  bad "deadline cannot be numeric" (replace "deadlineMonotonicNs" (JNumber (T.pack (show originalDeadline))) input)
  bad "deadline cannot acquire another budget" (configuration (originalDeadline+1))
  bad "earlier deadline cannot masquerade as inherited" (configuration (originalDeadline-1))
  bad "empty binding refused" (replace "binding" (JObject []) input)
  bad "foreign extra binding field refused" (replace "binding" (JObject [("lifetime",JString "1"),("session",JString "2"),("frontend",JString "3"),("foreign",JBool True)]) input)
  bad "zero lifetime refused" (replace "binding" (JObject [("lifetime",JString "0"),("session",JString "2"),("frontend",JString "3")]) input)
  bad "fractional lifetime refused" (replace "binding" (JObject [("lifetime",JString "1.5"),("session",JString "2"),("frontend",JString "3")]) input)
  bad "unknown top field refused" (case input of JObject fields -> JObject (fields++[("nativeAuthority",JBool True)]); value -> value)
  bad "duplicate JSON fields refused" (case input of JObject fields -> JObject (fields++[("schema",JNumber "1")]); value -> value)
  assert "trailing JSON refused" (isLeft (parse (encoded input<>" null")))
  let padTo amount = encoded input <> B.replicate (amount-B.length (encoded input)) 32
  assert "valid JSON at maximum size accepted" (isRight (parse (padTo 4096)))
  assert "otherwise valid overlarge JSON refused" (isLeft (parse (padTo 4097)))
  assert "expired original deadline refused" (isLeft (decodeConfiguration originalDeadline originalDeadline (encoded input)))
  assert "past original deadline refused" (isLeft (decodeConfiguration (originalDeadline+1) originalDeadline (encoded input)))
  assert "overlong initial budget refused" (isLeft (decodeConfiguration now (originalDeadline+1) (encoded (configuration (originalDeadline+1)))))
  forM_ [0..31 :: Integer] $ \seed -> do
    let selected = originalDeadline-seed*1000000
        valid = encoded (configuration selected)
    assert ("seeded current inherited deadline "++show seed) (isRight (decodeConfiguration now selected valid))
    let replay = encoded (configuration (selected+1))
    assert ("seeded deadline replay refusal "++show seed) (isLeft (decodeConfiguration now selected replay))
    assert ("seeded expired refusal "++show seed) (isLeft (decodeConfiguration selected selected valid))
  putStrLn "UI011 opener admission: 22 contracts and 32 seeded triples passed"
