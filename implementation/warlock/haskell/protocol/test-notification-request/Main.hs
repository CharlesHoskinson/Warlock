{-# LANGUAGE OverloadedStrings #-}
-- Source-first codec controls. This file performs no native operation.
module Main (main) where

import Control.Monad (unless)
import Data.Either (isLeft)
import qualified Data.Text as T
import qualified Data.Text.Encoding as TE
import Warlock.Protocol.Desktop
import Warlock.Protocol.Identity (renderCounter)

owner :: T.Text
owner = "{\"lifetime\":\"1\",\"session\":\"2\",\"frontend\":\"3\"}"

intent :: T.Text
intent = "{\"service\":\"1\",\"id\":\"7\",\"incarnation\":\"11\",\"producer\":\":1.21\",\"action\":\"open\",\"verb\":\"invoke\"}"

request :: T.Text -> T.Text -> T.Text
request kind extra = "{\"protocolVersion\":3,\"kind\":\"" <> kind <> "\",\"binding\":" <> owner <> ",\"requestId\":\"4\"" <> extra <> "}"

commit :: [T.Text] -> T.Text
commit requests = "{\"viewProtocol\":1,\"kind\":\"view-commit\",\"projection\":{},\"requests\":[" <> T.intercalate "," requests <> "],\"focus\":[]}"

check :: String -> Bool -> IO ()
check label value = unless value (ioError (userError label))

accept :: String -> [T.Text] -> IO ()
accept label requests = case decodeDesktopCommit (TE.encodeUtf8 (commit requests)) of
  Left reason -> ioError (userError (label <> ": " <> T.unpack reason))
  Right value -> do
    check (label <> ": membership") (length (commitRequests value) == length requests)
    check (label <> ": opaque request") (all ((== "4") . renderCounter . requestId) (commitRequests value))
    check (label <> ": preserved wire") (encodeDesktopCommit value == Right (TE.encodeUtf8 (commit requests)))

refuse :: String -> [T.Text] -> IO ()
refuse label requests = check label (isLeft (decodeDesktopCommit (TE.encodeUtf8 (commit requests))))

main :: IO ()
main = do
  let readRequest = request "notification-request" ""
      action value = request "notification-effect" (",\"intent\":" <> value)
      invoke = action intent
      changed old new = action (T.replace old new intent)
  accept "notification history request crosses strict desktop boundary" [readRequest]
  accept "current notification action identity crosses strict desktop boundary" [invoke]
  accept "existing catalog request remains supported" [request "catalog-request" ""]
  accept "dismiss target has empty action" [action (T.replace "\"open\"" "\"\"" (T.replace "\"invoke\"" "\"dismiss\"" intent))]
  refuse "zero service" [changed "\"service\":\"1\"" "\"service\":\"0\""]
  refuse "noncanonical incarnation" [changed "\"incarnation\":\"11\"" "\"incarnation\":\"011\""]
  refuse "D-Bus identifier overflow" [changed "\"id\":\"7\"" "\"id\":\"4294967296\""]
  refuse "well-known name is not producer identity" [changed ":1.21" "org.example.Producer"]
  refuse "unknown notification verb" [changed "invoke" "execute"]
  refuse "empty invoke action" [changed "\"open\"" "\"\""]
  refuse "extra request field" [request "notification-request" ",\"extra\":true"]
  refuse "duplicate request field" [request "notification-request" ",\"requestId\":\"5\""]
  refuse "extra target field" [action (T.dropEnd 1 intent <> ",\"extra\":true}")]
  refuse "commit request bound remains sixteen" (replicate 17 readRequest)
  putStrLn "notification-desktop-controls: 14 controls passed"
