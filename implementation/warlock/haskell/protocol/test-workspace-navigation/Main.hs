{-# LANGUAGE OverloadedStrings #-}
module Main where

import qualified Data.ByteString as B
import qualified Data.ByteString.Char8 as C
import Data.Either (isLeft)
import Control.Monad (unless)
import qualified Data.Text.Encoding as TE
import qualified Data.Text as T
import Warlock.Protocol.Identity (renderCounter)
import Warlock.Protocol.WorkspaceNavigation
import qualified WorkspaceStandaloneLiterals as Extra

owner, source, destination, intent, navigate, recover :: B.ByteString
owner = "{\"lifetime\":\"1\",\"session\":\"2\",\"frontend\":\"3\"}"
source = "{\"identity\":\"1\",\"generation\":\"4\",\"monitor\":\"0\",\"outputOwnershipGeneration\":\"5\"}"
destination = "{\"identity\":\"2\",\"generation\":\"6\",\"monitor\":\"0\",\"outputOwnershipGeneration\":\"5\"}"
intent = "{\"request\":\"7\",\"generation\":\"8\",\"source\":" <> source <> ",\"destination\":" <> destination <> ",\"context\":{\"lifetime\":\"1\",\"epoch\":\"3\",\"output\":\"9\",\"revision\":\"10\"}}"
navigate = "{\"protocolVersion\":3,\"kind\":\"workspace-navigation\",\"workspaceProtocol\":1,\"binding\":" <> owner <> ",\"intent\":" <> intent <> "}"
recover = "{\"protocolVersion\":3,\"kind\":\"workspace-navigation-recover\",\"workspaceProtocol\":1,\"binding\":" <> owner <> "}"

replace :: T.Text -> T.Text -> B.ByteString -> B.ByteString
replace old new = TE.encodeUtf8 . T.replace old new . TE.decodeUtf8

main :: IO ()
main = do
  let decoded = decodeWorkspaceNavigation navigate
      decodedRecovery = decodeWorkspaceNavigation recover
      checks =
        [ ("existing-navigate", either (const False) (\r -> maybe False ((== "7") . renderCounter . navigationRequest) (navigationIntent r)) decoded)
        , ("existing-recovery-has-no-request", either (const False) ((== Nothing) . navigationIntent) decodedRecovery)
        , ("byte-roundtrip", (decoded >>= encodeWorkspaceNavigation) == Right navigate)
        , ("recovery-roundtrip", (decodedRecovery >>= encodeWorkspaceNavigation) == Right recover)
        , ("foreign-context", isLeft (decodeWorkspaceNavigation (replace "\"epoch\":\"3\"" "\"epoch\":\"4\"" navigate)))
        , ("zero-request", isLeft (decodeWorkspaceNavigation (replace "\"request\":\"7\"" "\"request\":\"0\"" navigate)))
        , ("noncanonical-counter", isLeft (decodeWorkspaceNavigation (replace "\"request\":\"7\"" "\"request\":\"07\"" navigate)))
        , ("counter-overflow", isLeft (decodeWorkspaceNavigation (replace "\"request\":\"7\"" "\"request\":\"18446744073709551616\"" navigate)))
        , ("signed-workspace-overflow", isLeft (decodeWorkspaceNavigation (replace "\"identity\":\"2\"" "\"identity\":\"9223372036854775808\"" navigate)))
        , ("negative-workspace", isLeft (decodeWorkspaceNavigation (replace "\"identity\":\"2\"" "\"identity\":\"-2\"" navigate)))
        , ("wrong-version", isLeft (decodeWorkspaceNavigation (replace "\"workspaceProtocol\":1" "\"workspaceProtocol\":2" navigate)))
        , ("extra-request-id-refused", isLeft (decodeWorkspaceNavigation (B.init navigate <> ",\"requestId\":\"7\"}")))
        , ("duplicate-field", isLeft (decodeWorkspaceNavigation (B.init navigate <> ",\"kind\":\"workspace-navigation\"}")))
        , ("recovery-extra-intent", isLeft (decodeWorkspaceNavigation (B.init recover <> ",\"intent\":" <> intent <> "}")))
        , ("raw-whitespace-preserved", either (const False) (const True) (decodeWorkspaceNavigation (navigate <> C.replicate 8193 ' ')))
        , ("outer-exact-bound", either (const False) (const True) (decodeWorkspaceNavigation (navigate <> C.replicate (131072 - B.length navigate) ' ')))
        , ("outer-over-bound", isLeft (decodeWorkspaceNavigation (navigate <> C.replicate (131073 - B.length navigate) ' ')))
        , ("valid-after-refusal-data-pair", case (decodeWorkspaceNavigation (replace "\"epoch\":\"3\"" "\"epoch\":\"4\"" navigate), decodeWorkspaceNavigation navigate) of
            (Left _, Right valid) -> maybe False ((== "7") . renderCounter . navigationRequest) (navigationIntent valid)
            _ -> False)
        ]
  let allChecks = checks ++ Extra.additionalChecks
  mapM_ (\(name,ok) -> unless ok (ioError (userError name))) allChecks
  print allChecks
