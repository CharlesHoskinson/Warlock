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
attached :: B.ByteString -> B.ByteString -> B.ByteString
attached ownerBytes operations = "{\"protocolVersion\":3,\"kind\":\"application-attached\",\"binding\":"<>ownerBytes<>",\"nativeOperations\":"<>operations<>"}"
gatewayOf :: B.ByteString -> B.ByteString
gatewayOf payload = "{\"bridgeProtocol\":1,\"kind\":\"native-event\",\"payload\":"<>payload<>"}"

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
  attachment <- must (D.applicationAttached generatedOwner)
  attachmentChecked <- must (checkDesktopReply attachment)
  attachmentWire <- must (encodeServerCheckedWith desktopProfile attachmentChecked)
  check (label++" authenticated attachment public gateway roundtrip")
    (D.replyBinding attachment == generatedOwner && decodeServerCheckedWith desktopProfile attachmentWire == Right attachmentChecked && D.decodeDesktopGateway (gatewayOf (attached boundBytes "[]")) == Right attachment)
  let badAttach=case index `mod` 10 of
        0 -> attached boundBytes "[\"activate\"]"
        1 -> attached boundBytes "{}"
        2 -> attached boundBytes "null"
        3 -> B.init (attached boundBytes "[]")<>",\"extra\":true}"
        4 -> B.init (attached boundBytes "[]")<>",\"nativeOperations\":[]}"
        5 -> attached (badBinding "\"0\"") "[]"
        6 -> attached (badBinding (quote ("0"<>life))) "[]"
        7 -> "{\"protocolVersion\":2,\"kind\":\"application-attached\",\"binding\":"<>boundBytes<>",\"nativeOperations\":[]}"
        8 -> "{\"protocolVersion\":3,\"kind\":\"application-attached\",\"binding\":"<>boundBytes<>"}"
        _ -> "{\"protocolVersion\":3,\"kind\":\"application-attached\",\"binding\":"<>boundBytes<>",\"nativeOperations\":[],\"requestId\":\"1\"}"
  check (label++" hostile attachment rejected by public codec") (isLeft (decodeServerCheckedWith desktopProfile (gatewayOf badAttach)))
  preferences <- must (D.pinSnapshot (counter revision) identities)
  entries <- mapM (\n -> must (D.catalogEntry (T.pack ("catalog-"++show state++"-"++show n)) (T.pack ("Name \""++show state)<>" α😀") "application-x-executable" "Generated" "Program" ["α","key"])) [1..1+fromInteger (state `mod` 8) :: Int]
  snapshot <- must (D.catalogSnapshot (counter life) (counter revision) entries)
  reply <- must (D.catalogReply generatedOwner (counter requestId) (Just snapshot) (Just preferences) >>= checkDesktopReply)
  gateway <- must (encodeServerCheckedWith desktopProfile reply)
  check (label++" generated catalog/pins gateway roundtrip") (decodeServerCheckedWith desktopProfile gateway==Right reply)
  check (label++" generated server unknown field rejects") (isLeft (decodeServerCheckedWith desktopProfile (B.init gateway<>",\"unexpected\":true}")))


-- Read-only compositor observations use a separate literal wire vocabulary.
-- These controls enter the public Desktop/Codec routes; they grant no endpoint.
windowObservationControls :: (String -> Bool -> IO ()) -> IO ()
windowObservationControls check = do
  let bytes = TE.encodeUtf8 . J.renderJson
      ownerJson = either (error . show) id (J.bounds 1024 8 >>= \limit -> J.decodeStrict limit bound)
      attachmentValue ops = J.JObject
        [("protocolVersion",J.JNumber "3"),("kind",J.JString "application-attached"),("binding",ownerJson)
        ,("nativeOperations",J.JArray []),("applicationOperations",J.JArray [])
        ,("localOperations",J.JArray [J.JString "notification-policy"]),("windowObservationOperations",ops)]
      row ident parent = J.JObject [("id",J.JString ident),("title",J.JString "Document α😀"),("appId",J.JString "org.example.Editor")
        ,("states",J.JArray [J.JString "activated"]),("outputs",J.JArray [J.JString "41"]),("parent",parent)]
      snapshotValue rows = J.JObject [("owner",J.JString "9007199254740997"),("revision",J.JString "7"),("view",J.JString "global")
        ,("outputs",J.JArray [J.JString "41"]),("windows",J.JArray rows)]
      goodSnapshot=snapshotValue [row "11" J.JNull,row "12" (J.JString "11")]
      replyValue status body=J.JObject [("protocolVersion",J.JNumber "3"),("kind",J.JString "window-observation")
        ,("binding",ownerJson),("requestId",J.JString "9"),("status",J.JString status),("snapshot",body)]
      replace key value (J.JObject fields)=J.JObject (map (\(name,old)->(name,if name==key then value else old)) fields)
      replace _ _ value=value
      accepts value=isRight (D.decodeDesktopReply (bytes value))
      rejects value=isLeft (D.decodeDesktopReply (bytes value))
      readRequest=rawRequest "\"window-read\"" bound "\"9\"" ""
      goodWire=commit "{}" [readRequest]
      expect label value=check ("window observation: "++label) value
  expect "strict read-only capability attaches" (accepts (attachmentValue (J.JArray [J.JString "window-read"])))
  expect "empty capability is explicitly unavailable" (accepts (attachmentValue (J.JArray [])))
  expect "checked public client accepts bound read" (isRight (decodeClientCheckedWith desktopProfile goodWire))
  expect "default native client never borrows observation read" (isLeft (decodeClientChecked goodWire))
  expect "unknown effect suffix rejects complete batch" (isLeft (D.decodeDesktopCommit (commit "{}" [readRequest,rawRequest "\"window-activate\"" bound "\"10\"" ""])))
  expect "read rejects path selector" (isLeft (D.decodeDesktopCommit (commit "{}" [rawRequest "\"window-read\"" bound "\"9\"" ",\"path\":\"/tmp/socket\""])))
  expect "read refuses zero request" (isLeft (D.decodeDesktopCommit (commit "{}" [rawRequest "\"window-read\"" bound "\"0\"" ""])))
  expect "bound observed snapshot accepted" (accepts (replyValue "Observed" goodSnapshot))
  expect "public profiled server accepts observed gateway" (isRight (decodeServerCheckedWith desktopProfile (gatewayOf (bytes (replyValue "Observed" goodSnapshot)))))
  expect "default native server rejects observation gateway" (isLeft (decodeServerChecked (gatewayOf (bytes (replyValue "Observed" goodSnapshot)))))
  expect "unavailable has no fabricated snapshot" (accepts (replyValue "Unavailable" J.JNull))
  expect "unknown has no fabricated snapshot" (accepts (replyValue "Unknown" J.JNull))
  expect "observed cannot omit snapshot" (rejects (replyValue "Observed" J.JNull))
  expect "unknown cannot publish partial snapshot" (rejects (replyValue "Unknown" goodSnapshot))
  expect "unavailable cannot publish old snapshot" (rejects (replyValue "Unavailable" goodSnapshot))
  expect "unknown status refused" (rejects (replyValue "Ready" goodSnapshot))
  expect "duplicate handles refused" (rejects (replyValue "Observed" (snapshotValue [row "11" J.JNull,row "11" J.JNull])))
  expect "stale parent refused" (rejects (replyValue "Observed" (snapshotValue [row "11" (J.JString "12")])))
  expect "parent cycle refused" (rejects (replyValue "Observed" (snapshotValue [row "11" (J.JString "12"),row "12" (J.JString "11")])))
  expect "self parent refused" (rejects (replyValue "Observed" (snapshotValue [row "11" (J.JString "11")])))
  expect "unknown state refused" (rejects (replyValue "Observed" (snapshotValue [replace "states" (J.JArray [J.JString "hidden"]) (row "11" J.JNull)])))
  expect "duplicate state refused" (rejects (replyValue "Observed" (snapshotValue [replace "states" (J.JArray [J.JString "activated",J.JString "activated"]) (row "11" J.JNull)])))
  expect "unannounced output refused" (rejects (replyValue "Observed" (snapshotValue [replace "outputs" (J.JArray [J.JString "42"]) (row "11" J.JNull)])))
  expect "duplicate output refused" (rejects (replyValue "Observed" (replace "outputs" (J.JArray [J.JString "41",J.JString "41"]) goodSnapshot)))
  expect "zero owner refused" (rejects (replyValue "Observed" (replace "owner" (J.JString "0") goodSnapshot)))
  expect "owner must match full binding frontend" (rejects (replyValue "Observed" (replace "owner" (J.JString "2") goodSnapshot)))
  expect "numeric identity refused" (rejects (replyValue "Observed" (snapshotValue [replace "id" (J.JNumber "11") (row "11" J.JNull)])))
  expect "invented workspace refused" (rejects (replyValue "Observed" (case goodSnapshot of J.JObject fields->J.JObject (fields++[("workspace",J.JString "1")]); other->other)))
  expect "global scope is explicit not UI output" (rejects (replyValue "Observed" (replace "view" (J.JString "1") goodSnapshot)))
  expect "control character refused" (rejects (replyValue "Observed" (snapshotValue [replace "title" (J.JString "bad\ntext") (row "11" J.JNull)])))
  expect "UTF16 title bound refused" (rejects (replyValue "Observed" (snapshotValue [replace "title" (J.JString (T.replicate 129 "😀")) (row "11" J.JNull)])))
  expect "handle capacity refuses first excess" (rejects (replyValue "Observed" (snapshotValue [row (T.pack (show n)) J.JNull | n<-[1..257::Int]])))
  forM_ [J.JArray [J.JString "window-read",J.JString "window-read"],J.JArray [J.JString "window-effect"],J.JBool True] $ \bad ->
    expect "malformed capability rejected without grant" (rejects (attachmentValue bad))
  -- Literal seeds, alternating valid observations and one independently chosen
  -- forbidden field. No random generator and no decoder-derived oracle.
  forM_ [0..31::Int] $ \seed -> do
    let ident=T.pack (show (9007199254740993+toInteger seed))
        observed=replyValue "Observed" (snapshotValue [row ident J.JNull])
        invalid=replace "requestId" (J.JString "0") observed
    expect ("literal seed "++show seed++" wide identity") (accepts observed)
    expect ("literal seed "++show seed++" zero correlation") (rejects invalid)

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
  localReply <- must (D.applicationAttachedWithLocalNotifications owner D.ApplicationUnavailable)
  localWire <- must (D.encodeDesktopReply localReply)
  let localEnvelope extra = B.init (attached bound "[]") <> ",\"applicationOperations\":[],\"localOperations\":" <> extra <> "}"
  check "local policy attachment is typed and bound without native operations" (D.decodeDesktopReply (localEnvelope "[\"notification-policy\"]") == Right localReply && D.replyBinding localReply == owner)
  check "local policy attachment roundtrips exactly" (D.decodeDesktopReply localWire == Right localReply)
  check "local policy capability absent stays legacy" (D.decodeDesktopReply (B.init (attached bound "[]") <> ",\"applicationOperations\":[]}") /= Right localReply)
  forM_ ["[]","[\"invented\"]","[\"notification-policy\",\"notification-policy\"]","true","null"] $ \bad ->
    check "unknown empty duplicate or malformed local capabilities refused" (isLeft (D.decodeDesktopReply (localEnvelope bad)))
  check "local policy cannot advertise native window authority" (isLeft (D.decodeDesktopReply (B.init (attached bound "[\"window-effect\"]") <> ",\"applicationOperations\":[],\"localOperations\":[\"notification-policy\"]}")))
  check "local policy requires explicit application capability envelope" (isLeft (D.decodeDesktopReply (B.init (attached bound "[]") <> ",\"localOperations\":[\"notification-policy\"]}")))
  attachedReply <- must (D.applicationAttached owner)
  attachedChecked <- must (checkDesktopReply attachedReply)
  attachedWire <- must (encodeServerCheckedWith desktopProfile attachedChecked)
  check "independent exact attachment wire is accepted" (D.decodeDesktopGateway (gatewayOf (attached bound "[]")) == Right attachedReply)
  check "attachment public decoder roundtrip and binding retained" (decodeServerCheckedWith desktopProfile attachedWire == Right attachedChecked && D.replyBinding attachedReply == owner)
  check "attachment never accepted as native reply" (isLeft (decodeServerChecked attachedWire))
  check "attachment rejects malformed UTF8" (isLeft (D.decodeDesktopGateway (gatewayOf (attached bound (B.pack [255])))))
  check "numeric rounded session cannot select attachment binding" (isLeft (D.decodeDesktopGateway (gatewayOf (attached (rawBinding "\"9007199254740993\"" "9007199254740996" "\"9007199254740997\"") "[]"))))
  check "zero session cannot select attachment binding" (isLeft (D.decodeDesktopGateway (gatewayOf (attached (rawBinding "\"9007199254740993\"" "\"0\"" "\"9007199254740997\"") "[]"))))
  check "missing full binding is refused" (isLeft (D.decodeDesktopGateway (gatewayOf "{\"protocolVersion\":3,\"kind\":\"application-attached\",\"nativeOperations\":[]}")))
  check "duplicate binding field is refused" (isLeft (D.decodeDesktopGateway (gatewayOf (B.init (attached bound "[]")<>",\"binding\":"<>bound<>"}"))))
  -- The codec preserves a distinct valid binding; it does not authenticate it.
  -- Actual foreign-session refusal belongs to the owner-bound ingress gate.
  foreignReply <- must (D.decodeDesktopGateway (gatewayOf (attached (rawBinding "\"9007199254740993\"" "\"9007199254740996\"" "\"9007199254740997\"") "[]")))
  check "foreign session remains distinguishable for owner admission" (D.replyBinding foreignReply /= owner)
  reject "browser attachment masquerading as a commit request" (commit "{}" [attached bound "[]"])
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
  -- HTTP preview controls use the same opaque decoder as the authenticated
  -- native socket. They do not grant a renderer control ordinals or commands.
  let control kind controlFields = gatewayOf ("{\"protocolVersion\":3,\"kind\":\""<>kind<>"\",\"binding\":"<>bound<>" ,\"receiverEpoch\":\"1\""<>controlFields<>"}")
      controls = [control "native-preview-grant" ",\"capacity\":1",
                  control "native-preview-quarantine" "",
                  control "native-preview-closed" ""]
  forM_ controls $ \wire -> do
    typed <- must (D.decodeDesktopGateway wire)
    roundtrip <- must (D.encodeDesktopGateway typed >>= D.decodeDesktopGateway)
    check "preview controls retain exact binding and typed roundtrip" (D.replyBinding typed==owner && roundtrip==typed)
  forM_ ["0","-1","1066","18446744073709551617","1.0","1e0","\"1\"","true"] $ \capacity ->
    check "preview grant refuses invalid or overflowing capacity"
      (isLeft (D.decodeDesktopGateway (control "native-preview-grant" (",\"capacity\":"<>capacity))))
  forM_ [control "native-preview-quarantine" ",\"capacity\":1",
         control "native-preview-closed" ",\"receiverEpoch\":\"2\"",
         control "native-preview-unknown" "",
         control "native-preview-grant" ""] $ \wire ->
    check "preview controls refuse unknown duplicate and mismatched fields" (isLeft (D.decodeDesktopGateway wire))
  windowObservationControls check
  generatedCorpus check
  count <- readIORef checked
  putStrLn ("{\"schema\":1,\"suite\":\"desktop-boundary-controls\",\"passed\":true,\"checks\":" ++ show count ++ ",\"seed\":20261101,\"generatedCases\":256,\"mutationClasses\":16,\"nativeAcceptance\":false}")
