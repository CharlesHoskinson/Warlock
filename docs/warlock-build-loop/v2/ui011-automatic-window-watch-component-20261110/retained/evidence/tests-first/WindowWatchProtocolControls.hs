{-# LANGUAGE OverloadedStrings #-}
-- Tests-first public wire boundaries. No endpoint, owner or native authority.
module Main (main) where
import Control.Monad (unless, forM_)
import qualified Data.ByteString as B
import Data.Either (isLeft, isRight)
import Data.Text (Text)
import qualified Data.Text.Encoding as TE
import qualified Warlock.Protocol.Desktop as D
import Warlock.Protocol.Codec (decodeClientCheckedWith, decodeClientChecked, desktopProfile)
import qualified Warlock.Protocol.StrictJson as J

bytes :: J.Json -> B.ByteString
bytes = TE.encodeUtf8 . J.renderJson
bound :: J.Json
bound = J.JObject [("lifetime",J.JString "1"),("session",J.JString "1"),("frontend",J.JString "1")]
replace :: Text -> J.Json -> J.Json -> J.Json
replace key value (J.JObject pairs) = J.JObject (map (\(name,old)->(name,if name==key then value else old)) pairs)
replace _ _ value = value
extra :: Text -> J.Json -> J.Json -> J.Json
extra key value (J.JObject pairs) = J.JObject (pairs++[(key,value)])
extra _ _ value = value
request :: J.Json
request = J.JObject [("protocolVersion",J.JNumber "3"),("kind",J.JString "window-watch"),("binding",bound),("requestId",J.JString "10"),("observedRevision",J.JString "7")]
commit :: [J.Json] -> J.Json
commit requests = J.JObject [("viewProtocol",J.JNumber "1"),("kind",J.JString "view-commit"),("projection",J.JObject []),("requests",J.JArray requests),("focus",J.JArray [])]
attached :: J.Json -> J.Json
attached ops = J.JObject [("protocolVersion",J.JNumber "3"),("kind",J.JString "application-attached"),("binding",bound),("nativeOperations",J.JArray []),("applicationOperations",J.JArray []),("localOperations",J.JArray [J.JString "notification-policy"]),("windowObservationOperations",ops)]
row :: Text -> J.Json
row ident = J.JObject [("id",J.JString ident),("title",J.JString "Observed document"),("appId",J.JString "org.example.Editor"),("states",J.JArray []),("outputs",J.JArray [J.JString "41"]),("parent",J.JNull)]
snapshot :: Text -> [J.Json] -> J.Json
snapshot revision rows = J.JObject [("owner",J.JString "1"),("revision",J.JString revision),("view",J.JString "global"),("outputs",J.JArray [J.JString "41"]),("windows",J.JArray rows)]
reply :: Text -> J.Json -> J.Json
reply status body = J.JObject [("protocolVersion",J.JNumber "3"),("kind",J.JString "window-watch-result"),("binding",bound),("requestId",J.JString "10"),("observedRevision",J.JString "7"),("status",J.JString status),("snapshot",body)]
accepts :: J.Json -> Bool
accepts = isRight . D.decodeDesktopReply . bytes
rejects :: J.Json -> Bool
rejects = isLeft . D.decodeDesktopReply . bytes
acceptRequest :: J.Json -> Bool
acceptRequest value = isRight (decodeClientCheckedWith desktopProfile (bytes (commit [value])))
rejectRequest :: J.Json -> Bool
rejectRequest value = isLeft (decodeClientCheckedWith desktopProfile (bytes (commit [value])))
roundtrip :: J.Json -> Bool
roundtrip value = case D.decodeDesktopReply (bytes value) of
  Right decoded -> (D.encodeDesktopReply decoded >>= D.decodeDesktopReply)==Right decoded
  Left _ -> False

checks :: [(String,Bool)]
checks =
 [ ("explicit-watch-capability",accepts (attached (J.JArray [J.JString "window-read",J.JString "window-watch"])))
 , ("legacy-read-capability-unchanged",accepts (attached (J.JArray [J.JString "window-read"])))
 , ("empty-capability-unchanged",accepts (attached (J.JArray [])))
 , ("watch-alone-refused",rejects (attached (J.JArray [J.JString "window-watch"])))
 , ("watch-duplicate-refused",rejects (attached (J.JArray [J.JString "window-read",J.JString "window-watch",J.JString "window-watch"])))
 , ("watch-reversed-refused",rejects (attached (J.JArray [J.JString "window-watch",J.JString "window-read"])))
 , ("mutation-capability-refused",rejects (attached (J.JArray [J.JString "window-read",J.JString "window-activate"])))
 , ("public-desktop-watch-request",acceptRequest request)
 , ("legacy-native-profile-rejects-watch",isLeft (decodeClientChecked (bytes (commit [request]))))
 , ("zero-request-refused",rejectRequest (replace "requestId" (J.JString "0") request))
 , ("zero-base-revision-refused",rejectRequest (replace "observedRevision" (J.JString "0") request))
 , ("numeric-revision-refused",rejectRequest (replace "observedRevision" (J.JNumber "7") request))
 , ("deadline-selector-refused",rejectRequest (extra "timeoutMs" (J.JNumber "100") request))
 , ("endpoint-selector-refused",rejectRequest (extra "path" (J.JString "/tmp/not-authority") request))
 , ("unknown-suffix-rejects-whole-batch",isLeft (D.decodeDesktopCommit (bytes (commit [request,replace "kind" (J.JString "window-activate") request]))))
 , ("unchanged-null-roundtrip",roundtrip (reply "Unchanged" J.JNull))
 , ("changed-closed-origin-roundtrip",roundtrip (reply "Changed" (snapshot "8" [])))
 , ("changed-replacement-roundtrip",roundtrip (reply "Changed" (snapshot "8" [row "12"])))
 , ("unknown-null-roundtrip",roundtrip (reply "Unknown" J.JNull))
 , ("unavailable-null-roundtrip",roundtrip (reply "Unavailable" J.JNull))
 , ("unchanged-cannot-carry-snapshot",rejects (reply "Unchanged" (snapshot "8" [])))
 , ("changed-requires-snapshot",rejects (reply "Changed" J.JNull))
 , ("changed-revision-must-advance",rejects (reply "Changed" (snapshot "7" [])))
 , ("changed-old-revision-refused",rejects (reply "Changed" (snapshot "6" [])))
 , ("unknown-cannot-carry-snapshot",rejects (reply "Unknown" (snapshot "8" [])))
 , ("foreign-snapshot-owner-refused",rejects (reply "Changed" (replace "owner" (J.JString "2") (snapshot "8" []))))
 , ("duplicate-handle-refused",rejects (reply "Changed" (snapshot "8" [row "11",row "11"])))
 , ("extra-reply-field-refused",rejects (extra "nativeAvailable" (J.JBool True) (reply "Unchanged" J.JNull)))
 , ("legacy-observed-status-not-watch-status",rejects (reply "Observed" (snapshot "8" [])))
 ]

main :: IO ()
main = do
 -- Print every actual result; never stop at the first baseline refusal.
 forM_ checks $ \(name,passed) -> putStrLn (name++":"++if passed then "PASS" else "FAIL")
 let failures=[name | (name,False)<-checks]
 unless (null failures) (ioError (userError ("window-watch protocol failures: "++show failures)))
 putStrLn "window-watch-protocol:29-controls:PASS"
