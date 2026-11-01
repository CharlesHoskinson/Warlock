{-# LANGUAGE OverloadedStrings #-}
-- Independent public-library boundary corpus; no internal decoder or test CPP.
module Main (main) where

import Control.Monad (forM_, unless)
import qualified Data.ByteString as B
import qualified Data.ByteString.Char8 as C
import Data.Either (isLeft, isRight)
import Data.IORef (modifyIORef', newIORef, readIORef)
import qualified Data.Text as T
import qualified Data.Text.Encoding as TE
import Warlock.Protocol.Codec
import qualified Warlock.Protocol.Desktop as D
import qualified Warlock.Protocol.Framing as F
import Warlock.Protocol.Identity (Counter, Binding, parseCounter, binding)
import qualified Warlock.Protocol.StrictJson as J

counter :: T.Text -> Counter
counter value = either (error . show) id (parseCounter False value)
owner :: Binding
owner = either (error . show) id (binding (counter "9007199254740993") (counter "9007199254740995") (counter "9007199254740997"))
bound :: B.ByteString
bound = "{\"lifetime\":\"9007199254740993\",\"session\":\"9007199254740995\",\"frontend\":\"9007199254740997\"}"
quote :: T.Text -> B.ByteString
quote = TE.encodeUtf8 . J.renderJson . J.JString
catalog :: Int -> B.ByteString
catalog n = "{\"protocolVersion\":3,\"kind\":\"catalog-request\",\"binding\":" <> bound <> ",\"requestId\":\"" <> C.pack (show n) <> "\"}"
pins :: B.ByteString -> B.ByteString
pins identities = "{\"protocolVersion\":3,\"kind\":\"taskbar-pins-write\",\"binding\":" <> bound <> ",\"requestId\":\"8\",\"proposal\":{\"revision\":\"9007199254740999\",\"identities\":" <> identities <> "}}"
commit :: B.ByteString -> [B.ByteString] -> B.ByteString
commit projection requests = "{\"viewProtocol\":1,\"kind\":\"view-commit\",\"projection\":" <> projection <> ",\"requests\":[" <> B.intercalate "," requests <> "],\"focus\":[]}"
must :: Show e => Either e a -> IO a
must = either (ioError . userError . show) pure

-- Fixed, portable LCG input generation. The expected classifications below
-- come from the documented schema, not another implementation of its decoder.
-- Each retained case number identifies its input without ambient randomness.
fuzzStates :: [Integer]
fuzzStates = take 256 (tail (iterate (\n -> (1664525*n+1013904223) `mod` 4294967296) 20261101))
rawBinding :: B.ByteString -> B.ByteString -> B.ByteString -> B.ByteString
rawBinding life sess front = "{\"lifetime\":"<>life<>",\"session\":"<>sess<>",\"frontend\":"<>front<>"}"
rawRequest :: B.ByteString -> B.ByteString -> B.ByteString -> B.ByteString -> B.ByteString
rawRequest kind ownerBytes identity extra = "{\"protocolVersion\":3,\"kind\":"<>kind<>",\"binding\":"<>ownerBytes<>",\"requestId\":"<>identity<>extra<>"}"

generatedCorpus :: (String -> Bool -> IO ()) -> IO ()
generatedCorpus check = forM_ (zip [0 :: Int ..] fuzzStates) $ \(index,state) -> do
  let label="LCG20261101 case "++show index++" state "++show state
      -- Cross the JavaScript exact-integer boundary and periodically reach the
      -- full UInt64 endpoint, always as independently authored decimal strings.
      wide=if index `mod` 16==0 then 18446744073709551615 else 9007199254740993+state
      life=T.pack (show wide)
      sess=T.pack (show (9007199254740995+state))
      front=T.pack (show (9007199254740997+state))
      requestId=T.pack (show (9007199254741001+state))
      pinId=T.pack (show (9007199254741002+state))
      revision=T.pack (show (9007199254741011+state))
      boundBytes=rawBinding (quote life) (quote sess) (quote front)
      identities=[T.pack ("generated-"++show state++"-"++show n)<>" α😀 app" | n <- [1..fromInteger (state `mod` 5) :: Int]]
      ids="["<>B.intercalate "," (map quote identities)<>"]"
      proposalBytes="{\"revision\":"<>quote revision<>",\"identities\":"<>ids<>"}"
      readWire=rawRequest "\"catalog-request\"" boundBytes (quote requestId) ""
      writeWire=rawRequest "\"taskbar-pins-write\"" boundBytes (quote pinId) (",\"proposal\":"<>proposalBytes)
      projection=TE.encodeUtf8 (J.renderJson (J.JObject [("generated",J.JString (T.replicate (fromInteger (state `mod` 97)) "α😀\"")),("nested",J.JArray [J.JBool (even state),J.JNumber (T.pack (show state))])]))
      goodBytes=commit projection [readWire,writeWire]
  good <- must (decodeClientCheckedWith desktopProfile goodBytes)
  check (label++" two generated valid operations accepted") (maybe False ((==2) . length . D.commitRequests) (checkedDesktopCommit good))
  encoded <- must (encodeClientCheckedWith desktopProfile good)
  check (label++" complete generated client roundtrip") (decodeClientCheckedWith desktopProfile encoded==Right good)
  let badBinding replacement=rawBinding replacement (quote sess) (quote front)
      badBound bindingBytes=rawRequest "\"catalog-request\"" bindingBytes (quote pinId) ""
      badPins value=rawRequest "\"taskbar-pins-write\"" boundBytes (quote pinId) (",\"proposal\":"<>value)
      selector=case index `mod` 5 of 0 -> "/tmp/generated-"<>T.pack (show state); 1 -> "../generated"; 2 -> "file:generated"; 3 -> "a\\generated"; _ -> "$(touch generated)"
      mutation=case index `mod` 16 of
        0 -> rawRequest (quote ("unknown-"<>T.pack (show state))) boundBytes (quote pinId) ""
        1 -> "{\"protocolVersion\":2,\"kind\":\"catalog-request\",\"binding\":"<>boundBytes<>",\"requestId\":"<>quote pinId<>"}"
        2 -> "{\"protocolVersion\":\"3\",\"kind\":\"catalog-request\",\"binding\":"<>boundBytes<>",\"requestId\":"<>quote pinId<>"}"
        3 -> badBound (B.init boundBytes<>",\"unexpected\":true}")
        4 -> badBound (badBinding "\"0\"")
        5 -> badBound (badBinding (quote ("0"<>life)))
        6 -> badBound (badBinding (TE.encodeUtf8 life))
        7 -> rawRequest "\"catalog-request\"" boundBytes "\"18446744073709551616\"" ""
        8 -> badPins ("{\"revision\":"<>TE.encodeUtf8 revision<>",\"identities\":"<>ids<>"}")
        9 -> badPins ("{\"revision\":"<>quote revision<>",\"identities\":["<>quote selector<>"]}")
        10 -> badPins (B.init proposalBytes<>",\"revision\":"<>quote revision<>"}")
        11 -> badPins (B.init proposalBytes<>",\"unexpected\":null}")
        12 -> rawRequest "\"catalog-request\"" boundBytes (quote pinId) (",\"path\":"<>quote selector)
        13 -> rawRequest "\"application-catalog\"" boundBytes (quote pinId) ",\"snapshot\":null,\"preferences\":null"
        14 -> rawRequest "\"shell-command\"" boundBytes (quote pinId) (",\"command\":"<>quote ("touch generated-"<>T.pack (show state)))
        _ -> B.init writeWire<>",\"kind\":\"taskbar-pins-write\"}"
      corrupted=commit projection [readWire,mutation]
  check (label++" generated invalid suffix rejected before checked commit") (isLeft (D.decodeDesktopCommit corrupted))
  check (label++" generated invalid suffix rejected by real codec") (isLeft (decodeClientCheckedWith desktopProfile corrupted))
  generatedOwner <- must (binding (counter life) (counter sess) (counter front))
  preferences <- must (D.pinSnapshot (counter revision) identities)
  entries <- mapM (\n -> must (D.catalogEntry (T.pack ("catalog-"++show state++"-"++show n)) (T.pack ("Name \""++show state)<>" α😀") "application-x-executable" "Generated" "Program" ["α","key"])) [1..1+fromInteger (state `mod` 8) :: Int]
  snapshot <- must (D.catalogSnapshot (counter life) (counter revision) entries)
  reply <- must (D.catalogReply generatedOwner (counter requestId) (Just snapshot) (Just preferences) >>= checkDesktopReply)
  gateway <- must (encodeServerCheckedWith desktopProfile reply)
  check (label++" generated catalog/pins gateway roundtrip") (decodeServerCheckedWith desktopProfile gateway==Right reply)
  check (label++" generated server unknown field rejects") (isLeft (decodeServerCheckedWith desktopProfile (B.init gateway<>",\"unexpected\":true}")))

main :: IO ()
main = do
  checked <- newIORef (0 :: Int)
  let check label good = do
        modifyIORef' checked (+1)
        unless good (ioError (userError label))
      reject label bytes = do
        check (label ++ " rejects before a checked desktop commit exists") (isLeft (D.decodeDesktopCommit bytes))
        check (label ++ " rejects through public profiled codec") (isLeft (decodeClientCheckedWith desktopProfile bytes))
      positive = commit "{}" [catalog 7, pins ("[\"alpha\","<>quote "βeta app"<>"]")]
  good <- must (decodeClientCheckedWith desktopProfile positive)
  check "actual complete commit produces two typed domain requests" (maybe False ((==2) . length . D.commitRequests) (checkedDesktopCommit good))
  encoded <- must (encodeClientCheckedWith desktopProfile good)
  check "complete valid client roundtrip preserves checked value" (decodeClientCheckedWith desktopProfile encoded == Right good)
  check "native default rejects desktop client" (isLeft (decodeClientChecked positive))
  check "native encoder cannot leak desktop checked value" (isLeft (encodeClientChecked good))
  let nativeHello = "{\"version\":1,\"kind\":\"hello\",\"body\":{\"binding\":" <> bound <> "}}"
  check "native positive control remains accepted" (isRight (decodeServerChecked nativeHello))
  check "desktop server cannot borrow native hello" (isLeft (decodeServerCheckedWith desktopProfile nativeHello))
  check "desktop client cannot borrow native hello" (isLeft (decodeClientCheckedWith desktopProfile nativeHello))
  check "empty complete presentation commit is legitimate" (isRight (decodeClientCheckedWith desktopProfile (commit "{}" [])))
  check "sixteen complete requests accepted" (isRight (decodeClientCheckedWith desktopProfile (commit "{}" (map catalog [1..16]))))
  reject "seventeen requests" (commit "{}" (map catalog [1..17]))
  reject "bare RPC is not actual Main outgoing stream" (catalog 7)
  forM_ (["/etc/passwd", "../outside", "a/b", "a\\b", "file:///secret", "http:secret", ".", "..", "$(touch sentinel)", "x;touch sentinel", "`id`", "a|sh", "a>file"] :: [T.Text]) $ \selector ->
    reject ("unsafe selector " ++ T.unpack selector) (commit "{}" [catalog 7, pins ("[" <> quote selector <> "]")])
  forM_ [20261101..20261108 :: Int] $ \seed -> do
    let suffix = C.pack (show seed)
        badMethod = "{\"protocolVersion\":3,\"kind\":\"shell-command\",\"binding\":" <> bound <> ",\"requestId\":\"7\",\"command\":\"touch sentinel-" <> suffix <> "\"}"
        badPath = "{\"protocolVersion\":3,\"kind\":\"catalog-request\",\"binding\":" <> bound <> ",\"requestId\":\"7\",\"path\":\"/tmp/sentinel-" <> suffix <> "\"}"
    reject ("seeded unknown method " ++ show seed) (commit "{}" [catalog 7, badMethod])
    reject ("seeded arbitrary path " ++ show seed) (commit "{}" [catalog 7, badPath])
    reject ("seeded duplicate key " ++ show seed) ("{\"viewProtocol\":1,\"viewProtocol\":1,\"kind\":\"view-commit\",\"projection\":{},\"requests\":[],\"focus\":[]}")
  reject "forged server event as operation" (commit "{}" ["{\"protocolVersion\":3,\"kind\":\"application-catalog\",\"binding\":" <> bound <> ",\"requestId\":\"7\",\"snapshot\":null,\"preferences\":null}"])
  reject "forged native effect" (commit "{}" ["{\"protocolVersion\":3,\"kind\":\"window-effect\",\"binding\":" <> bound <> "}"])
  reject "invalid UTF8" (B.pack [255])
  reject "NUL" (positive <> B.singleton 0)
  reject "trailing bytes" (positive <> "x")
  reject "numeric revision" (commit "{}" ["{\"protocolVersion\":3,\"kind\":\"taskbar-pins-write\",\"binding\":" <> bound <> ",\"requestId\":\"8\",\"proposal\":{\"revision\":9007199254740999,\"identities\":[]}}"])
  reject "depth overflow" (commit (B.concat (replicate 20 "{\"x\":") <> "0" <> B.concat (replicate 20 "}")) [])
  let padded n = commit ("{\"pad\":\"" <> B.replicate n 97 <> "\"}") [catalog 7]
      overhead = B.length (padded 0)
      maximumWire = padded (131072 - overhead)
  check "full Main commit reaches exact131072 byte positive boundary" (B.length maximumWire == 131072 && isRight (decodeClientCheckedWith desktopProfile maximumWire))
  reject "complete commit byte overflow" (padded (131073 - overhead))
  check "default native prefix still rejects above64KiB" (isLeft (F.prefix maximumWire))
  framed <- must (F.desktopCommitPrefix maximumWire)
  check "desktop frame length matches real full commit" (F.desktopCommitHeaderLength (B.take 4 framed) == Right 131072)
  check "native header limit is unchanged" (isLeft (F.headerLength (B.take 4 framed)))
  check "native exact65536 prefix remains reachable" (isRight (F.prefix (B.replicate 65536 97)))
  check "pin UTF16 exact256 positive" (isRight (D.pinSnapshot (counter "1") [T.replicate 128 "😀"]))
  check "pin UTF16 overflow rejected" (isLeft (D.pinSnapshot (counter "1") [T.replicate 129 "😀"]))
  let entry n name = D.catalogEntry (T.pack ("app-" ++ show n)) name "" "" "" []
  check "catalog name UTF16 exact512 positive" (isRight (entry (0 :: Int) (T.replicate 256 "😀")))
  check "catalog name UTF16 overflow" (isLeft (entry (0 :: Int) (T.replicate 257 "😀")))
  entries <- mapM (\n -> must (entry n (T.replicate 80 "n"))) [1..2048 :: Int]
  snapshot <- must (D.catalogSnapshot (counter "9007199254740993") (counter "9") entries)
  preferences <- must (D.pinSnapshot (counter "1") ["alpha", "βeta app"])
  reply <- must (D.catalogReply owner (counter "7") (Just snapshot) (Just preferences))
  server <- must (checkDesktopReply reply)
  gateway <- must (encodeServerCheckedWith desktopProfile server)
  check "real2048 entry response crosses64KiB without truncation" (B.length gateway > 65536 && B.length gateway <= 1048704 && decodeServerCheckedWith desktopProfile gateway == Right server)
  jsonLimits <- must (J.bounds 1048704 16)
  tree <- must (J.decodeStrict jsonLimits gateway)
  let at key (J.JObject fields) = maybe J.JNull id (lookup key fields)
      at _ _ = J.JNull
      observedEntries = at "entries" (at "snapshot" (at "payload" tree))
  check "independent raw tree retains all2048 entries" (case observedEntries of J.JArray xs -> length xs == 2048 && at "id" (last xs) == J.JString "app-2048"; _ -> False)
  check "native decoder rejects large application gateway" (isLeft (decodeServerChecked gateway))
  serverFramed <- must (F.desktopGatewayPrefix gateway)
  check "actual application gateway framing accepts large response" (F.desktopGatewayHeaderLength (B.take 4 serverFramed) == Right (B.length gateway))
  check "native response framing remains64KiB" (isLeft (F.headerLength (B.take 4 serverFramed)))
  extra <- must (entry (2049 :: Int) "extra")
  check "catalog count2049 unique entries refuses instead of truncating" (isLeft (D.catalogSnapshot (counter "1") (counter "1") (entries ++ [extra])))
  -- All entries independently fit their field bounds; only aggregate capacity fails.
  hugeEntries <- mapM (\n -> must (D.catalogEntry (T.pack ("big-" ++ show n)) (T.replicate 512 "n") (T.replicate 512 "i") (T.replicate 512 "w") (T.replicate 512 "g") [])) [1..2048 :: Int]
  let huge = D.catalogSnapshot (counter "1") (counter "1") hugeEntries >>= \s -> D.catalogReply owner (counter "7") (Just s) Nothing >>= D.encodeDesktopReply
  check "oversize full reply is refused without partial catalog" (isLeft huge)
  unavailable <- must (D.catalogReply owner (counter "7") Nothing Nothing >>= checkDesktopReply >>= encodeServerCheckedWith desktopProfile)
  check "explicit unavailable server frame still validates" (isRight (decodeServerCheckedWith desktopProfile unavailable))
  generatedCorpus check
  count <- readIORef checked
  putStrLn ("{\"schema\":1,\"suite\":\"desktop-boundary-controls\",\"passed\":true,\"checks\":" ++ show count ++ ",\"seed\":20261101,\"generatedCases\":256,\"mutationClasses\":16,\"nativeAcceptance\":false}")
