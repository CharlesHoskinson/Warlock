{-# LANGUAGE OverloadedStrings #-}
-- VM-only selected UI image. The parent must be the actual authenticated
-- backend, which pins this image and passes its original fd 0 and deadline.
-- This executable deliberately provides no fabricated owner events.
module Main (main) where

import qualified Data.ByteString.Char8 as C
import Control.Exception (IOException, SomeAsyncException, SomeException, finally, fromException, throwIO, try)
import qualified Data.Text as T
import qualified Data.Text.Encoding as TE
import Data.IORef (newIORef, readIORef, writeIORef)
import GHC.IO.Exception (ioe_errno)
import System.Environment (getArgs)
import System.Exit (exitFailure)
import System.IO.Error (ioeGetErrorString, ioeGetErrorType, ioeGetLocation)
import System.Posix.Files (readSymbolicLink, setFileMode)
import System.Posix.Process (getProcessID, getParentProcessID)
import Warlock.Capture.Process.Bootstrap (remainingMicros)
import qualified Warlock.Protocol.StrictJson as J
import Warlock.Ui.Config (loadUiConfig, uiDeadline)
import Warlock.Ui.EngineCustody (startCustody, abandonCustody)
import Warlock.Ui.Owner (runUiOwner, uiPassed, uiResultJson)
import Warlock.Ui.PrivateNetwork (enterPrivateNetwork, withPeerNetwork)
import Warlock.Ui.WebKit (runWebKitWithCustody)

-- Only known static setup messages/operation names may enter the receipt.
-- Paths, arguments, peer data, frames and arbitrary exception text are omitted.
staticSetupDetail :: IOException -> J.Json
staticSetupDetail problem =
 let message = ioeGetErrorString problem
     location = ioeGetLocation problem
     messages = ["private UI namespace needs one actual OS thread", "private UI needs its ordinary owning identity",
                 "private UI identity changed", "network namespace did not change", "custody ready deadline",
                 "custodian exited before ready", "custodian ready invalid", "custodian ready closed",
                 "custody requires a single OS thread", "custody SIGCHLD ownership unavailable",
                 "custody startup deadline", "custodian ownership uncertain"]
     locations = ["create private UI namespaces", "open procfs", "private network procfs",
                  "open namespace map", "write namespace map", "get loopback flags", "enable private loopback",
                  "custody pipe2", "custody poll", "custody pidfd_open", "custody SIGCHLD disposition",
                  "custody unshare PID", "native peer credentials unavailable", "duplicate native peer",
                  "native socket type", "poll native peer", "peek native peer", "poll peer pidfd"]
     value | message `elem` messages = Just message
           | location `elem` locations = Just location
           | otherwise = Nothing
 in maybe J.JNull (J.JString . T.pack) value

main :: IO ()
main = do
 -- The backend independently supplies the two trusted absolute paths. Argument
 -- parsing occurs before any namespace/worker acquisition; production isolation
 -- order within the witness scope is otherwise unchanged.
 args <- getArgs
 (path, output) <- case args of
  [value, destination] | take 1 value == "/" && take 1 destination == "/" -> pure (value, destination)
  _ -> ioError (userError "expected trusted absolute UI configuration and observation path")
 selfPid <- getProcessID
 phase <- newIORef ("acquire-peer-witness" :: String)
 attempt <- try $ do
  (deadline, result, fields) <- withPeerNetwork $ \witness -> do
   writeIORef phase "enter-private-network"
   enterPrivateNetwork
   writeIORef phase "load-ui-config"
   config <- loadUiConfig path >>= either (ioError . userError . show) pure
   writeIORef phase "start-custody"
   custody <- startCustody (remainingMicros (uiDeadline config))
   (result, fields) <- (do
     writeIORef phase "capture-owner-facts"
     pid <- getProcessID
     parent <- getParentProcessID
     fd0 <- readSymbolicLink "/proc/self/fd/0"
     userNamespace <- readSymbolicLink "/proc/self/ns/user"
     networkNamespace <- readSymbolicLink "/proc/self/ns/net"
     pidNamespace <- readSymbolicLink "/proc/self/ns/pid"
     writeIORef phase "run-ui-owner"
     ownerResult <- runUiOwner witness config (runWebKitWithCustody custody)
     let string = J.JString . T.pack
         facts = [("pid", string (show pid)), ("parentPid", string (show parent)),
           ("fd0", string fd0), ("userNamespace", string userNamespace),
           ("networkNamespace", string networkNamespace), ("pidNamespace", string pidNamespace)]
     pure (ownerResult, facts)) `finally` abandonCustody custody
   writeIORef phase "retire-peer-witness"
   pure (uiDeadline config, result, fields)
  -- The witness bracket must retire successfully before recording a result.
  writeIORef phase "write-owner-result"
  remaining <- remainingMicros deadline
  let withinDeadline = remaining > 0
  bounds <- either (ioError . userError . show) pure (J.bounds 1048576 32)
  owner <- either (ioError . userError . show) pure (J.decodeStrict bounds (uiResultJson result))
  let receipt = J.JObject (fields ++ [("owner", owner), ("peerWitnessRetired", J.JBool True),
                   ("withinOriginalDeadline", J.JBool withinDeadline), ("nativeAcceptance", J.JBool False)])
  C.writeFile output (TE.encodeUtf8 (J.renderJson receipt))
  setFileMode output 0o600
  C.putStrLn (uiResultJson result)
  pure (uiPassed result && withinDeadline)
 case attempt of
  Right passed -> if passed then pure () else exitFailure
  Left problem -> case fromException problem :: Maybe SomeAsyncException of
   Just _ -> throwIO (problem :: SomeException)
   Nothing -> do
    whereFailed <- readIORef phase
    let ioProblem = fromException problem :: Maybe IOException
        errorType = maybe "non-io-exception" (show . ioeGetErrorType) ioProblem
        number = maybe J.JNull (maybe J.JNull (J.JString . T.pack . show) . ioe_errno) ioProblem
        detail = maybe J.JNull staticSetupDetail ioProblem
        failure = J.JObject [("schema", J.JNumber "1"), ("kind", J.JString "vm-ui-startup-failure"),
                  ("passed", J.JBool False), ("pid", J.JString (T.pack (show selfPid))),
                  ("phase", J.JString (T.pack whereFailed)),
                  ("errorType", J.JString (T.pack errorType)), ("errno", number), ("staticSetupDetail", detail),
                  ("peerWitnessRetired", J.JNull), ("cleanupQualified", J.JBool False),
                  ("withinOriginalDeadline", J.JNull), ("nativeAcceptance", J.JBool False)]
    C.writeFile output (TE.encodeUtf8 (J.renderJson failure))
    setFileMode output 0o600
    C.putStrLn "VM UI startup failed; scoped diagnostic receipt written"
    exitFailure
