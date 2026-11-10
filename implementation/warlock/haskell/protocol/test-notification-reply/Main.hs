{-# LANGUAGE OverloadedStrings #-}
-- Public decoder/encoder only. No new constructors, imports or native operations.
module Main (main) where
import Control.Monad (unless)
import Data.Either (isLeft)
import qualified Data.Text as T
import qualified Data.Text.Encoding as TE
import Warlock.Protocol.Desktop (decodeDesktopReply, encodeDesktopReply)

data Case = Accept String [T.Text] | Refuse String [T.Text] | Exact String [T.Text]
owner :: T.Text
owner = "{\"lifetime\":\"1\",\"session\":\"2\",\"frontend\":\"3\"}"
list :: [T.Text] -> T.Text
list values = "[" <> T.intercalate "," values <> "]"
field :: T.Text -> T.Text -> T.Text
field key value = "\"" <> key <> "\":\"" <> value <> "\""
action :: Int -> T.Text
action n = "{\"key\":\"a" <> T.pack (show n) <> "\",\"label\":\"Open\"}"
entry :: T.Text -> T.Text -> T.Text -> [T.Text] -> T.Text -> T.Text
entry ident incarnation state actions urgency = "{" <> T.intercalate ","
  [field "id" ident,field "incarnation" incarnation,field "producer" ":1.21",field "app" "A",field "summary" "S",field "body" "B",field "state" state,"\"actions\":" <> list actions] <> urgency <> "}"
live :: T.Text
live = entry "7" "11" "live" [action 1] ",\"urgency\":1"
snapshot :: [T.Text] -> T.Text
snapshot entries = "{\"service\":\"1\",\"revision\":\"2\",\"available\":true,\"reason\":\"\",\"entries\":" <> list entries <> "}"
reply :: T.Text -> T.Text -> T.Text
reply kind rest = "{\"protocolVersion\":3,\"binding\":" <> owner <> ",\"kind\":\"" <> kind <> "\"" <> rest <> "}"
snap :: T.Text -> T.Text
snap value = reply "notification-snapshot" (",\"requestId\":\"4\",\"snapshot\":" <> value)
outcome :: T.Text -> T.Text -> T.Text
outcome status reason = reply "notification-outcome" (",\"requestId\":\"4\",\"status\":\"" <> status <> "\",\"snapshot\":" <> snapshot [live] <> reason)
attached :: T.Text -> T.Text
attached extra = reply "application-attached" (",\"nativeOperations\":[],\"applicationOperations\":[]" <> extra)
changed :: T.Text -> T.Text -> T.Text
changed old new = snap (T.replace old new (snapshot [live]))
textChange :: T.Text -> T.Text -> T.Text -> T.Text
textChange key old new = changed (field key old) (field key new)

cases :: [Case]
cases =
  [ Accept "01 first new snapshot crosses existing public reply API" [snap (snapshot [live])]
  , Accept "02 positive uint32 endpoint" [snap (snapshot [entry "4294967295" "11" "live" [] ",\"urgency\":1"])]
  , Refuse "03 positive canonical service revision id incarnation" [changed (field "service" "1") (field "service" "0"),changed (field "revision" "2") (field "revision" "0"),textChange "id" "7" "0",textChange "id" "7" "4294967296",textChange "id" "7" "07",textChange "incarnation" "11" "0",textChange "incarnation" "11" "011"]
  , Accept "04 producer exact128 ASCII unique-name bound" [textChange "producer" ":1.21" (":" <> T.replicate 125 "a" <> ".b")]
  , Refuse "05 producer unique-name and129 bound" [textChange "producer" ":1.21" value | value <- ["org.example.Producer",":alone",":1..2",":.2",":1.é",":" <> T.replicate 126 "a" <> ".b"]]
  , Accept "06 eight unique actions" [snap (snapshot [entry "7" "11" "live" (map action [1..8]) ",\"urgency\":1"])]
  , Refuse "07 action capacity uniqueness nonempty lifecycle identifiers" [snap (snapshot [entry "7" "11" "live" (map action [1..9]) ",\"urgency\":1"]),snap (snapshot [entry "7" "11" "live" [action 1,action 1] ",\"urgency\":1"]),textChange "key" "a1" "",textChange "label" "Open" "",textChange "state" "live" "expired",textChange "key" "a1" "bad\\tkey",textChange "key" "a1" "bad\\u007fkey"]
  , Accept "08 thirtytwo independently identified entries" [snap (snapshot [entry (T.pack (show n)) (T.pack (show (100+n))) "live" [] ",\"urgency\":1" | n <- [1::Int ..32]])]
  , Refuse "09 entry capacity and duplicate id incarnation" [snap (snapshot [entry (T.pack (show n)) (T.pack (show (100+n))) "live" [] ",\"urgency\":1" | n <- [1::Int ..33]]),snap (snapshot [live,entry "7" "12" "live" [] ",\"urgency\":1"]),snap (snapshot [live,entry "8" "11" "live" [] ",\"urgency\":1"])]
  , Accept "10 exact UTF16 text bounds" [textChange "app" "A" (T.replicate 128 "a"),textChange "summary" "S" (T.replicate 256 "s"),textChange "body" "B" (T.replicate 1024 "b"),textChange "reason" "" (T.replicate 256 "r"),textChange "label" "Open" (T.replicate 128 "l"),textChange "key" "a1" (T.replicate 32 "🚀")]
  , Refuse "11 over UTF16 text bounds" [textChange "app" "A" (T.replicate 129 "a"),textChange "summary" "S" (T.replicate 257 "s"),textChange "body" "B" (T.replicate 1025 "b"),textChange "reason" "" (T.replicate 257 "r"),textChange "label" "Open" (T.replicate 65 "🚀"),textChange "key" "a1" (T.replicate 33 "🚀")]
  , Refuse "12 disallowed text controls" [textChange "app" "A" "bad\\u0001app",textChange "body" "B" "bad\\u0001body"]
  , Accept "13 labels and body allow Elm newline tab" [textChange "body" "B" "line\\n\\tbody",textChange "label" "Open" "line\\n\\tlabel"]
  , Accept "14 optional urgency0to2 and all eight states" ([snap (snapshot [entry "7" "11" "live" [] suffix]) | suffix <- ["",",\"urgency\":0",",\"urgency\":1",",\"urgency\":2"]] ++ [snap (snapshot [entry "7" "11" state [] ",\"urgency\":1"]) | state <- ["live","expired","invoked","dismissed","closed","disconnected","unknown","unavailable"]])
  , Refuse "15 invalid urgency state" [changed "\"urgency\":1" "\"urgency\":3",changed "\"urgency\":1" "\"urgency\":-1",changed "\"urgency\":1" "\"urgency\":\"Critical\"",textChange "state" "live" "invented"]
  , Refuse "16 strict snapshot entry action fields" [snap (T.dropEnd 1 (snapshot [live]) <> ",\"extra\":true}"),snap (T.dropEnd 1 (snapshot [live]) <> ",\"service\":\"2\"}"),snap (snapshot [T.dropEnd 1 live <> ",\"extra\":true}"]),snap (snapshot [T.replace (action 1) (T.dropEnd 1 (action 1) <> ",\"key\":\"duplicate\"}") live])]
  , Accept "17 three outcome states with absent or exact optional reasons" ([outcome value "" | value <- ["Dispatched","Refused","Unknown"]] ++ [outcome "Refused" (",\"reason\":\"" <> reason <> "\"") | reason <- ["","expired","changed","unavailable","already-handled"]])
  , Refuse "18 outcome status reason request binding strictness" [outcome "Succeeded" "",outcome "Refused" ",\"reason\":\"invented\"",T.replace "\"requestId\":\"4\"" "\"requestId\":\"0\"" (outcome "Unknown" ""),outcome "Unknown" ",\"status\":\"Refused\"",outcome "Unknown" ",\"extra\":true"]
  , Exact "19 legacy attachment absence retains original wire" [reply "application-attached" ",\"nativeOperations\":[]",attached "",attached ",\"localOperations\":[\"notification-policy\"]"]
  , Accept "20 explicit empty notification operations safely unavailable" [attached ",\"notificationOperations\":[]"]
  , Accept "21 exact complete notification capability" [attached ",\"notificationOperations\":[\"notification-read\",\"notification-action\"]"]
  , Refuse "22 duplicate unknown incomplete reversed capabilities" [attached (",\"notificationOperations\":" <> value) | value <- ["[\"notification-read\",\"notification-read\"]","[\"notification-read\",\"unknown\"]","[\"notification-read\"]","[\"notification-action\"]","[\"notification-action\",\"notification-read\"]"]]
  , Refuse "23 notification support cannot forge native operations" [T.replace "\"nativeOperations\":[]" "\"nativeOperations\":[\"notification-action\"]" (attached ",\"notificationOperations\":[\"notification-read\",\"notification-action\"]")]
  , Refuse "24 duplicate capability or extra attachment fields" [attached ",\"notificationOperations\":[],\"notificationOperations\":[]",attached ",\"notificationOperations\":[],\"extra\":true"]
  ]

accept :: String -> Bool -> T.Text -> IO ()
accept label exact raw = case decodeDesktopReply (TE.encodeUtf8 raw) of
  Left reason -> ioError (userError (label <> ": " <> T.unpack reason))
  Right value -> case encodeDesktopReply value of
    Left reason -> ioError (userError (label <> ": encode: " <> T.unpack reason))
    Right encoded -> do
      let wire = TE.decodeUtf8 encoded
          complete = "\"notificationOperations\":[\"notification-read\",\"notification-action\"]"
      unless (not (T.isInfixOf complete raw) || T.isInfixOf complete wire) (ioError (userError (label <> ": capability dropped")))
      unless (not (T.isInfixOf "\"notificationOperations\":[]" raw) || not (T.isInfixOf "\"notification-read\"" wire || T.isInfixOf "\"notification-action\"" wire)) (ioError (userError (label <> ": unavailable capability expanded")))
      unless (not exact || encoded == TE.encodeUtf8 raw) (ioError (userError (label <> ": legacy wire changed")))
      case decodeDesktopReply encoded of
        Left reason -> ioError (userError (label <> ": roundtrip: " <> T.unpack reason))
        Right again -> unless (again == value && encodeDesktopReply again == Right encoded) (ioError (userError (label <> ": canonical roundtrip changed")))
run :: Case -> IO ()
run value = case value of
  Accept label values -> mapM_ (accept label False) values
  Exact label values -> mapM_ (accept label True) values
  Refuse label values -> mapM_ (\raw -> unless (isLeft (decodeDesktopReply (TE.encodeUtf8 raw))) (ioError (userError label))) values
main :: IO ()
main = do
  mapM_ run cases
  putStrLn "notification-reply-controls: 24 groups passed"
