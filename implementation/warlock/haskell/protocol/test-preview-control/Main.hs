{-# LANGUAGE OverloadedStrings #-}
module Main (main) where

import Control.Monad (forM_, unless)
import qualified Data.ByteString as B
import Data.Text (Text)
import qualified Data.Text as T
import qualified Data.Text.Encoding as TE
import System.Exit (exitFailure)
import Warlock.Protocol.Identity
import Warlock.Protocol.PreviewControl
import Warlock.Protocol.StrictJson

encode :: Json -> B.ByteString
encode = TE.encodeUtf8 . renderJson
bind :: Text -> Text -> Text -> Json
bind a b c = JObject [("lifetime",JString a),("session",JString b),("frontend",JString c)]
owner :: Json
owner = bind "1" "2" "3"
command :: Json
command = JObject [("kind",JString "reconcile"),("binding",owner)]
row :: Json
row = JObject [("identity",JString "binding:1:2:3"),("commands",JArray [command])]
proposal :: Json
proposal = JObject [("previewProtocol",JNumber "3"),("kind",JString "preview-proposals"),("binding",owner),("receiverEpoch",JString "4"),("entries",JArray [row])]
packet :: Json
packet = JObject [("previewProtocol",JNumber "3"),("kind",JString "preview-commands"),("binding",owner),("receiverEpoch",JString "4"),("controlOrdinal",JString "5"),("entries",JArray [row])]
outer :: Text -> B.ByteString -> Json
outer kind raw = JObject ([("previewProtocol",JNumber "3"),("kind",JString kind),("binding",owner),("receiverEpoch",JString "4"),("controlOrdinal",JString "5")] ++
  (if kind == "preview-control-ticket" then [("alreadyDelivered",JBool False)] else []) ++ [("wire",JString (TE.decodeUtf8 raw))])
set :: Text -> Json -> Json -> Json
set key value (JObject fields) = JObject [(k,if k == key then value else v) | (k,v) <- fields]
set _ _ value = value
extra :: Text -> Json -> Json
extra key (JObject fields) = JObject (fields ++ [(key,JNull)])
extra _ value = value
changeRow :: (Json -> Json) -> Json -> Json
changeRow f = set "entries" (JArray [f row])
changeCommand :: (Json -> Json) -> Json -> Json
changeCommand f = changeRow (set "commands" (JArray [f command]))
assert :: String -> Bool -> IO ()
assert label ok = unless ok $ putStrLn ("FAIL " ++ label) >> exitFailure
right :: Either a b -> Bool
right (Right _) = True
right _ = False
left :: Either a b -> Bool
left = not . right

-- Exercise each public decoder independently; the final positive is freshly
-- applied after the hostile input. These decoders are pure, not state machines.
exercise :: String -> (B.ByteString -> Either PreviewControlError a) -> B.ByteString -> B.ByteString -> IO ()
exercise label decoder valid invalid = do
  assert (label ++ " valid before") (right (decoder valid))
  assert (label ++ " hostile") (left (decoder invalid))
  assert (label ++ " valid after") (right (decoder valid))

main :: IO ()
main = do
  let p = encode proposal
      raw = encode packet
      t = encode (outer "preview-control-ticket" raw)
      c = encode (outer "preview-control-consumed" raw)
      positive = right (decodePreviewProposal p) && right (decodePreviewTicket t) && right (decodeConsumptionConfirmation c)
      bad label value = do
        assert label (left (decodePreviewProposal value))
        assert (label ++ ": positive control") positive
  assert "positive three schemas" positive
  case (decodePreviewTicket t, decodeConsumptionConfirmation c, decodePreviewProposal p, parseCounter False "5") of
    (Right ticket,Right confirmation,Right prop,Right ordinal) -> do
      assert "ticket retains wire" (ticketOriginalWire ticket == raw)
      assert "confirmation retains wire" (confirmationOriginalWire confirmation == raw)
      assert "outer roundtrip" (decodePreviewTicket (encodePreviewTicket ticket) == Right ticket)
      assert "confirmation roundtrip" (decodeConsumptionConfirmation (encodeConsumptionConfirmation confirmation) == Right confirmation)
      assert "pure ticket construction" (makeTicketWire prop ordinal == Right raw)
      assert "advisory retained" (case ticketFromWire True raw of Right x -> ticketAlreadyDelivered x; _ -> False)
    _ -> assert "decode fixtures" False
  let variants =
        [ ("wrong version",set "previewProtocol" (JNumber "4") proposal)
        , ("wrong kind",set "kind" (JString "preview-commands") proposal)
        , ("extra outer",extra "extra" proposal)
        , ("duplicate outer",extra "kind" proposal)
        , ("extra binding",set "binding" (extra "extra" owner) proposal)
        , ("duplicate binding",set "binding" (extra "session" owner) proposal)
        , ("extra entry",changeRow (extra "extra") proposal)
        , ("duplicate entry",changeRow (extra "identity") proposal)
        , ("extra command",changeCommand (extra "extra") proposal)
        , ("duplicate command",changeCommand (extra "kind") proposal)
        , ("extra command binding",changeCommand (set "binding" (extra "extra" owner)) proposal)
        , ("duplicate command binding",changeCommand (set "binding" (extra "frontend" owner)) proposal)
        , ("identity mismatch",changeRow (set "identity" (JString "binding:1:2:4")) proposal)
        , ("identity oversized unicode",changeRow (set "identity" (JString (T.replicate 257 "é"))) proposal)
        , ("foreign command binding",changeCommand (set "binding" (bind "1" "2" "4")) proposal)
        , ("multiple entries",set "entries" (JArray [row,row]) proposal)
        , ("empty entries",set "entries" (JArray []) proposal)
        , ("multiple commands",changeRow (set "commands" (JArray [command,command])) proposal)
        , ("empty commands",changeRow (set "commands" (JArray [])) proposal)
        ] ++ [("unsupported " ++ T.unpack k,changeCommand (set "kind" (JString k)) proposal) | k <- ["acquire","cancel","release","acknowledge","paint"]]
  forM_ variants $ \(label,value) -> bad label (encode value)
  forM_ ["0","01","18446744073709551616","-1",""] $ \n -> do
    bad ("epoch " ++ T.unpack n) (encode (set "receiverEpoch" (JString n) proposal))
    bad ("binding counter " ++ T.unpack n) (encode (set "binding" (bind n "2" "3") proposal))
    assert "bad ordinal" (left (ticketFromWire False (encode (set "controlOrdinal" (JString n) packet))))
  bad "invalid UTF8" (B.pack [255])
  bad "literal NUL" (p <> B.singleton 0)
  bad "escaped NUL" (TE.encodeUtf8 (T.replace "binding:1:2:3" "binding:1:2:3\\u0000" (TE.decodeUtf8 p)))
  let padTo n bytes = bytes <> B.replicate (n - B.length bytes) 32
  assert "proposal exactly 4096" (right (decodePreviewProposal (padTo 4096 p)))
  bad "proposal 4097" (padTo 4097 p)
  assert "wire exactly 4096" (right (ticketFromWire False (padTo 4096 raw)))
  assert "wire 4097" (left (ticketFromWire False (padTo 4097 raw)))
  assert "outer exactly 32768" (right (decodePreviewTicket (padTo 32768 t)))
  assert "outer 32769" (left (decodePreviewTicket (padTo 32769 t)))
  assert "confirmation exactly 32768" (right (decodeConsumptionConfirmation (padTo 32768 c)))
  assert "confirmation 32769" (left (decodeConsumptionConfirmation (padTo 32769 c)))
  forM_ ["receiverEpoch","controlOrdinal"] $ \key -> do
    assert (T.unpack key ++ " mismatch") (left (decodePreviewTicket (encode (set key (JString "9") (outer "preview-control-ticket" raw)))))
    assert "confirmation mismatch" (left (decodeConsumptionConfirmation (encode (set key (JString "9") (outer "preview-control-consumed" raw)))))
  assert "outer binding mismatch" (left (decodePreviewTicket (encode (set "binding" (bind "1" "2" "9") (outer "preview-control-ticket" raw)))))
  assert "outer duplicate" (left (decodePreviewTicket (encode (extra "wire" (outer "preview-control-ticket" raw)))))
  assert "confirmation duplicate" (left (decodeConsumptionConfirmation (encode (extra "wire" (outer "preview-control-consumed" raw)))))
  forM_ [("proposal", decodePreviewProposal, p)] $ \(label,decoder,valid) -> do
    exercise (label ++ " utf8") decoder valid (B.pack [255])
    exercise (label ++ " nul") decoder valid (valid <> B.singleton 0)
  exercise "ticket utf8" decodePreviewTicket t (B.pack [255])
  exercise "ticket nul" decodePreviewTicket t (t <> B.singleton 0)
  exercise "confirmation utf8" decodeConsumptionConfirmation c (B.pack [255])
  exercise "confirmation nul" decodeConsumptionConfirmation c (c <> B.singleton 0)
  exercise "proposal duplicate" decodePreviewProposal p (encode (extra "kind" proposal))
  exercise "ticket duplicate" decodePreviewTicket t (encode (extra "wire" (outer "preview-control-ticket" raw)))
  exercise "confirmation duplicate" decodeConsumptionConfirmation c (encode (extra "wire" (outer "preview-control-consumed" raw)))
  let alteredWire = encode (set "controlOrdinal" (JString "6") packet)
  exercise "ticket altered inner ordinal" decodePreviewTicket t (encode (outer "preview-control-ticket" alteredWire))
  exercise "confirmation altered inner ordinal" decodeConsumptionConfirmation c (encode (outer "preview-control-consumed" alteredWire))
  exercise "confirmation foreign binding" decodeConsumptionConfirmation c (encode (set "binding" (bind "1" "2" "9") (outer "preview-control-consumed" raw)))
  exercise "ticket malformed envelope utf8" decodePreviewTicket t (B.take (B.length t - 1) t <> B.pack [255,125])
  exercise "confirmation malformed envelope utf8" decodeConsumptionConfirmation c (B.take (B.length c - 1) c <> B.pack [255,125])
  forM_ [extra "kind" packet, set "binding" (extra "session" owner) packet,
         changeRow (extra "identity") packet, changeCommand (extra "kind") packet,
         changeCommand (set "binding" (extra "lifetime" owner)) packet] $ \invalid -> do
    let invalidWire = encode invalid
    assert "inner duplicate ticket" (left (decodePreviewTicket (encode (outer "preview-control-ticket" invalidWire))))
    assert "inner duplicate confirmation" (left (decodeConsumptionConfirmation (encode (outer "preview-control-consumed" invalidWire))))
    assert "inner refusal positive control" positive
  let preserved = " \n" <> TE.encodeUtf8 (T.replace "reconcile" "\\u0072econcile" (TE.decodeUtf8 raw)) <> " \t"
  case ticketFromWire False preserved of
    Left _ -> assert "escaped wire accepted" False
    Right x -> do
      assert "escape and whitespace retained" (ticketOriginalWire x == preserved)
      assert "outer encode preserves bytes" (case decodePreviewTicket (encodePreviewTicket x) of Right y -> ticketOriginalWire y == preserved; _ -> False)
  case decodeConsumptionConfirmation (encode (outer "preview-control-consumed" preserved)) of
    Left _ -> assert "escaped confirmation accepted" False
    Right x -> do
      assert "confirmation escape and whitespace retained" (confirmationOriginalWire x == preserved)
      assert "confirmation outer encode preserves bytes" (case decodeConsumptionConfirmation (encodeConsumptionConfirmation x) of Right y -> confirmationOriginalWire y == preserved; _ -> False)
  let maxText = "18446744073709551615"
      maxBinding = bind maxText maxText maxText
      maxRow = JObject [("identity",JString ("binding:" <> maxText <> ":" <> maxText <> ":" <> maxText)),("commands",JArray [set "binding" maxBinding command])]
      maxP = set "entries" (JArray [maxRow]) (set "receiverEpoch" (JString maxText) (set "binding" maxBinding proposal))
  assert "max UInt64 identities" (right (decodePreviewProposal (encode maxP)))
  assert "max UInt64 ordinal" (right (ticketFromWire False (encode (set "controlOrdinal" (JString maxText) packet))))
  -- Canonical binding:L:S:F has at most 70 ASCII bytes (3*20+2+8),
  -- so a valid 512-byte identity or literal multibyte identity is impossible.
  -- JSON escape spellings and whitespace are preserved by the checks above.
  -- Schema-valid nesting is below 16; this hostile depth check cannot establish
  -- acceptance at depth 16, since a valid reconciliation cannot reach it.
  let deep = iterate (JArray . (:[])) JNull !! 18
  exercise "proposal hostile deep nesting" decodePreviewProposal p (encode (set "entries" deep proposal))
  exercise "ticket hostile deep nesting" decodePreviewTicket t (encode (set "wire" (JString (TE.decodeUtf8 (encode (set "entries" deep packet)))) (outer "preview-control-ticket" raw)))
  exercise "confirmation hostile deep nesting" decodeConsumptionConfirmation c (encode (set "wire" (JString (TE.decodeUtf8 (encode (set "entries" deep packet)))) (outer "preview-control-consumed" raw)))
  -- Deterministic enumeration, not a PRNG. Each index isolates one mutation.
  forM_ [1..128 :: Int] $ \index -> do
    let n = T.pack (show index)
        b = bind n "2" "3"
        r = JObject [("identity",JString ("binding:" <> n <> ":2:3")),("commands",JArray [set "binding" b command])]
        v = set "entries" (JArray [r]) (set "binding" b proposal)
        generatedPacket = set "entries" (JArray [r]) (set "binding" b packet)
        generatedWire = encode generatedPacket
        ticket = set "binding" b (outer "preview-control-ticket" generatedWire)
        confirmation = set "binding" b (outer "preview-control-consumed" generatedWire)
        name = "enumeration " ++ show index
    assert ("generated valid " ++ name) (right (decodePreviewProposal (encode v)))
    bad ("generated hostile " ++ name) (encode (set "binding" (bind ("0" <> n) "2" "3") v))
    exercise ("proposal isolated epoch " ++ name) decodePreviewProposal (encode v) (encode (set "receiverEpoch" (JString "0") v))
    exercise ("ticket isolated ordinal " ++ name) decodePreviewTicket (encode ticket) (encode (set "controlOrdinal" (JString "6") ticket))
    exercise ("confirmation isolated ordinal " ++ name) decodeConsumptionConfirmation (encode confirmation) (encode (set "controlOrdinal" (JString "6") confirmation))
  putStrLn "preview-control schema controls passed"
