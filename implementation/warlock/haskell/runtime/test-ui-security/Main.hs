{-# LANGUAGE OverloadedStrings #-}
-- VM-only selected UI image. The parent must be the actual authenticated
-- backend, which pins this image and passes its original fd 0 and deadline.
-- This executable deliberately provides no fabricated owner events.
module Main (main) where

import qualified Data.ByteString.Char8 as C
import Control.Exception (finally)
import qualified Data.Text as T
import qualified Data.Text.Encoding as TE
import System.Environment (getArgs)
import System.Exit (exitFailure)
import System.Posix.Files (readSymbolicLink, setFileMode)
import System.Posix.Process (getProcessID, getParentProcessID)
import Warlock.Capture.Process.Bootstrap (remainingMicros)
import qualified Warlock.Protocol.StrictJson as J
import Warlock.Ui.Config (loadUiConfig, uiDeadline)
import Warlock.Ui.EngineCustody (startCustody, abandonCustody)
import Warlock.Ui.Owner (runUiOwner, uiPassed, uiResultJson)
import Warlock.Ui.PrivateNetwork (enterPrivateNetwork, withPeerNetwork)
import Warlock.Ui.WebKit (runWebKitWithCustody)

main :: IO ()
main = do
 (output, deadline, result, fields) <- withPeerNetwork $ \witness -> do
  -- Match the production nonthreaded entry point: isolate before GTK or IO.
  enterPrivateNetwork
  args <- getArgs
  (path, output) <- case args of
    [value, destination] | take 1 value == "/" && take 1 destination == "/" -> pure (value, destination)
    _ -> ioError (userError "expected trusted absolute UI configuration and observation path")
  config <- loadUiConfig path >>= either (ioError . userError . show) pure
  custody <- startCustody (remainingMicros (uiDeadline config))
  pid <- getProcessID
  parent <- getParentProcessID
  fd0 <- readSymbolicLink "/proc/self/fd/0"
  userNamespace <- readSymbolicLink "/proc/self/ns/user"
  networkNamespace <- readSymbolicLink "/proc/self/ns/net"
  pidNamespace <- readSymbolicLink "/proc/self/ns/pid"
  result <- runUiOwner witness config (runWebKitWithCustody custody) `finally` abandonCustody custody
  let string = J.JString . T.pack
      fields = [("pid", string (show pid)), ("parentPid", string (show parent)),
        ("fd0", string fd0), ("userNamespace", string userNamespace),
        ("networkNamespace", string networkNamespace), ("pidNamespace", string pidNamespace)]
  pure (output, uiDeadline config, result, fields)
 -- The witness bracket must retire successfully before recording a result.
 remaining <- remainingMicros deadline
 let withinDeadline = remaining > 0
 -- Only root's VM harness chooses this private external evidence path. This
 -- status is an owner observation, not a CSP or native acceptance verdict.
 bounds <- either (ioError . userError . show) pure (J.bounds 1048576 32)
 owner <- either (ioError . userError . show) pure (J.decodeStrict bounds (uiResultJson result))
 let receipt = J.JObject (fields ++ [("owner", owner), ("peerWitnessRetired", J.JBool True),
                  ("withinOriginalDeadline", J.JBool withinDeadline), ("nativeAcceptance", J.JBool False)])
 C.writeFile output (TE.encodeUtf8 (J.renderJson receipt))
 setFileMode output 0o600
 C.putStrLn (uiResultJson result)
 if uiPassed result && withinDeadline then pure () else exitFailure
