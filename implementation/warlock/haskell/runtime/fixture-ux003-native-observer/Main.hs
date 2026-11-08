{-# LANGUAGE OverloadedStrings #-}
-- QA-only observer. Calls the real public backend with its trusted config.
-- It does not create a peer, catalog reply, Scope, application or GUI result.
module Main (main) where

import qualified Data.ByteString as B
import qualified Data.ByteString.Char8 as C
import qualified Data.Text as T
import qualified Data.Text.Encoding as TE
import Numeric (showHex)
import System.Environment (getArgs)
import System.Exit (exitFailure)
import Warlock.Backend
import Warlock.Bootstrap (BootstrapResult(..))
import Warlock.Capture.Process.Bootstrap
  (SelectedOutcome,selectedObservedExit,selectedCustody,selectedContainment,selectedOperation,output,diagnostics)
import qualified Warlock.Protocol.Desktop as D
import Warlock.Protocol.Identity (renderCounter)
import Warlock.Protocol.StrictJson (Json(..),renderJson,decodeStrict,bounds)

hex :: B.ByteString -> T.Text
hex = T.pack . concatMap (\n -> let encoded=showHex n "" in if length encoded==1 then '0':encoded else encoded) . B.unpack

jsonValue :: B.ByteString -> Json
jsonValue raw = case bounds 1048576 20 of
  Left _ -> JNull
  Right limits -> either (const JNull) id (decodeStrict limits raw)

desktopJson :: D.DesktopReply -> Json
desktopJson reply = either (const JNull) jsonValue (D.encodeDesktopReply reply)

selected :: SelectedOutcome -> Json
selected result = JObject
  ([("exit",maybe JNull (JNumber . T.pack . show) (selectedObservedExit result))
   ,("custody",JString (T.pack (show (selectedCustody result))))
   ,("containment",JString (T.pack (show (selectedContainment result))))]
   ++ case selectedOperation result of
      Left _ -> [("stdoutHex",JNull),("stderrHex",JNull),("operationSucceeded",JBool False)]
      Right captured -> [("stdoutHex",JString (hex (output captured)))
                       ,("stderrHex",JString (hex (diagnostics captured)))
                       ,("operationSucceeded",JBool True)])

main :: IO ()
main = do
  arguments <- getArgs
  case arguments of
    [path] -> do
      configured <- loadBackendConfig path
      case configured of
        Left _ -> ioError (userError "QA observer trusted startup refused")
        Right config -> do
          result <- runBackend config
          let owner = case backendBootstrap result of
                Right (Executed outcome) -> case selectedOperation outcome of
                  Right captured | B.null (diagnostics captured) -> jsonValue (output captured)
                  _ -> JNull
                _ -> JNull
              app = case backendApplicationReceipt result of
                Nothing -> JNull
                Just (request,outcome) -> case selected outcome of
                  JObject fields -> JObject (("request",JString (renderCounter request)):fields)
                  _ -> JNull
              published = maybe JNull desktopJson (backendCatalogObservation result)
              launch = case backendApplicationObservation result of
                Nothing -> JNull
                Just (intent,snapshot) -> JObject
                  [("request",JString (renderCounter (D.launchRequest intent)))
                  ,("lifetime",JString (renderCounter (D.launchLifetime intent)))
                  ,("generation",JString (renderCounter (D.launchGeneration intent)))
                  ,("entry",JString (D.launchEntry intent)),("catalog",maybe JNull desktopJson snapshot)]
              bootstrapFailure = case backendBootstrap result of
                Left problem -> JString (T.take 4096 problem)
                Right _ -> JNull
              receipt = JObject
                [("schema",JNumber "1"),("kind",JString "ux003-backend-observation")
                ,("backend",jsonValue (backendResultJson result)),("bootstrapFailure",bootstrapFailure),("owner",owner)
                ,("application",app),("publishedCatalog",published),("publishedLaunch",launch)
                ,("nativeAcceptance",JBool False),("originalAcceptance",JBool False)]
          C.putStrLn (TE.encodeUtf8 (renderJson receipt))
          if backendPassed result then pure () else exitFailure
    _ -> ioError (userError "QA observer expects exactly one trusted config")
