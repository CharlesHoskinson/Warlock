{-# LANGUAGE OverloadedStrings #-}
module Main (main) where
import qualified Data.ByteString.Char8 as C
import System.Environment (getArgs)
import System.Exit (exitFailure)
import Warlock.Backend (loadBackendConfig,newNotificationIssuer,provisionNotificationIssuer,retireNotificationIssuer)
main :: IO ()
main = do
 args <- getArgs
 ok <- case args of
  [configPath] -> do
   configured <- loadBackendConfig configPath
   case configured of
    Left _ -> pure False
    Right config -> do
     issuer <- newNotificationIssuer config
     result <- provisionNotificationIssuer issuer
     retired <- retireNotificationIssuer issuer
     pure (retired && either (const False) (const True) result)
  _ -> pure False
 if ok then C.putStrLn "{\"schema\":1,\"provisioned\":true}"
 else C.putStrLn "{\"schema\":1,\"provisioned\":false}" >> exitFailure
