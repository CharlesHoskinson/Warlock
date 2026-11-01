module Main (main) where
import qualified Data.ByteString.Char8 as B
import System.Environment (getArgs)
import System.Exit (exitFailure)
import Warlock.Backend

main :: IO ()
main = do
 arguments <- getArgs
 case arguments of
  [path] -> do
   configured <- loadBackendConfig path
   case configured of
    Left _ -> B.putStrLn (B.pack "{\"schema\":1,\"passed\":false,\"error\":\"startup-refused\"}") >> exitFailure
    Right config -> do
     result <- runBackend config
     B.putStrLn (backendResultJson result)
     if backendPassed result then pure () else exitFailure
  _ -> B.putStrLn (B.pack "{\"schema\":1,\"passed\":false,\"error\":\"expected-trusted-config\"}") >> exitFailure
