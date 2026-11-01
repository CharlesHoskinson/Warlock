-- Real approved UI image; no host-network fallback and no adapter script.
module Main (main) where
import qualified Data.ByteString.Char8 as C
import System.Environment (getArgs)
import Control.Exception (finally)
import Warlock.Capture.Process.Bootstrap (remainingMicros)
import Warlock.Ui.EngineCustody (startCustody, abandonCustody)
import System.Exit (exitFailure)
import Warlock.Ui.Config (loadUiConfig,uiDeadline)
import Warlock.Ui.Owner (runUiOwner,uiPassed,uiResultJson)
import Warlock.Ui.PrivateNetwork (enterPrivateNetwork, withPeerNetwork)
import Warlock.Ui.WebKit (runWebKitWithCustody)

main :: IO ()
main = do
 (result, deadline) <- withPeerNetwork $ \witness -> do
  -- The executable is deliberately nonthreaded. Namespace ownership precedes
  -- configuration reads, IO workers, listeners and engine subprocess creation.
  enterPrivateNetwork
  args <- getArgs
  path <- case args of [value] | take 1 value=="/" -> pure value; _ -> ioError (userError "expected trusted absolute UI configuration")
  configured <- loadUiConfig path
  config <- either (ioError . userError . show) pure configured
  custody <- startCustody (remainingMicros (uiDeadline config))
  result <- runUiOwner witness config (runWebKitWithCustody custody) `finally` abandonCustody custody
  pure (result, uiDeadline config)
 left <- remainingMicros deadline
 if left > 0 then pure () else ioError (userError "UI witness cleanup exceeded original deadline")
 C.putStrLn (uiResultJson result)
 if uiPassed result then pure () else exitFailure
