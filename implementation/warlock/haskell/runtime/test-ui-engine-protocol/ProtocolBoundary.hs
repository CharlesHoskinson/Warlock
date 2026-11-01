{-# LANGUAGE OverloadedStrings #-}
-- PREPARATION DRAFT ONLY: no execution or acceptance. Independently authored
-- valid JSON projection replies exercise the actual EngineProtocol client
-- entrypoint. This does not exercise transport, credentials, callbacks, or the
-- actual owner's projection validation. Root runs all protected checks.
module ProtocolBoundary (run) where

import Control.Monad (forM_, unless)
import Data.Bits (shiftR)
import qualified Data.ByteString as B
import qualified Data.ByteString.Char8 as C
import qualified Data.Text as T
import qualified Warlock.Protocol.StrictJson as J
import Warlock.Ui.EngineProtocol

assert :: String -> Bool -> IO ()
assert label ok = unless ok (ioError (userError label))
need :: Show e => Either e a -> IO a
need = either (ioError . userError . show) pure

frame :: B.ByteString -> B.ByteString -> B.ByteString
frame header body = B.pack [fromIntegral (n `shiftR` 24), fromIntegral (n `shiftR` 16),
                            fromIntegral (n `shiftR` 8), fromIntegral n] <> header <> body
 where n = B.length header

replyHeader :: B.ByteString
replyHeader = "{\"version\":1,\"direction\":\"reply\",\"session\":\"91\",\"request\":\"1\",\"method\":\"lastProjection\"}"

initial :: IO Startup
initial = do
 sid <- need (sessionId "91")
 need (startup 12001 12002 12003 "123456789" sid)

-- Exactly n nested objects; each leaf is the valid JSON integer 0. Root object
-- counts as depth 1, so depth 15 remains legal and depth 16 must be rejected.
nestedBytes :: Int -> B.ByteString
nestedBytes n = B.concat (replicate n "{\"k\":") <> "0" <> C.replicate n '}'

nestedValue :: Int -> J.Json
nestedValue n = foldr (\_ value -> J.JObject [("k",value)]) (J.JNumber "0") [1..n]

-- Every size candidate is a valid one-field object, differing by one ASCII
-- payload byte. The semantic oracle is independently assembled below.
sizedBytes :: Int -> B.ByteString
sizedBytes size = prefix <> B.replicate (size - B.length prefix - B.length suffix) 120 <> suffix
 where prefix = "{\"v\":\""; suffix = "\"}"

sizedValue :: Int -> J.Json
sizedValue size = J.JObject [("v", J.JString (T.replicate (size - 8) "x"))]

-- Each check starts with a genuine pending LastProjection request. Directly
-- feed an independent reply, rather than asking the codec to create its input.
checkPayload :: Startup -> String -> B.ByteString -> J.Json -> Bool -> IO ()
checkPayload start label payload expected shouldAccept = do
 assert (label ++ " remains inside outer frame cap") (B.length (frame replyHeader payload) <= maxFrameBytes)
 let (pending, issued) = beginRequest (newSession start) GetLastProjection
 _ <- need issued
 let (after, result) = acceptReply pending (frame replyHeader payload)
 if shouldAccept then case result of
   Right (ProjectionReply (Just actual)) -> do
     assert (label ++ " retains semantic value") (projectionJson actual == expected)
     assert (label ++ " keeps session live") (not (isPoisoned after))
   _ -> ioError (userError (label ++ " rejected valid boundary value"))
 else do
   assert (label ++ " rejected") (case result of Left _ -> True; _ -> False)
   assert (label ++ " poisons") (isPoisoned after)
   let (again, retry) = beginRequest after GetStop
   assert (label ++ " cannot restart after refusal") (retry == Left Poisoned && isPoisoned again)

run :: IO ()
run = do
 start <- initial
 assert "reviewed payload limit changed" (maxPayloadBytes == 393216)
 -- Validate that all candidates, including rejected ones, are otherwise valid
 -- JSON under deliberately larger independent bounds. This distinguishes the
 -- protocol boundary from malformed input or a wrong reply type.
 referenceBounds <- need (J.bounds (maxPayloadBytes + 1024) 64)
 forM_ [14,15,16] $ \depth -> do
   let payload = nestedBytes depth
       expected = nestedValue depth
   assert ("depth fixture valid " ++ show depth) (J.decodeStrict referenceBounds payload == Right expected)
   checkPayload start ("depth " ++ show depth) payload expected (depth <= 15)
 forM_ [maxPayloadBytes - 1, maxPayloadBytes, maxPayloadBytes + 1] $ \size -> do
   let payload = sizedBytes size
       expected = sizedValue size
   assert ("size fixture length " ++ show size) (B.length payload == size)
   assert ("size fixture valid " ++ show size) (J.decodeStrict referenceBounds payload == Right expected)
   checkPayload start ("payload bytes " ++ show size) payload expected (size <= maxPayloadBytes)
 putStrLn "engine protocol valid JSON boundaries: depth 14/15/16, bytes 393215/393216/393217"
