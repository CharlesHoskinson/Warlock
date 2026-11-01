{-# LANGUAGE OverloadedStrings #-}
-- The broker alone owns native fd0. GTK runs in the held-image PID1 role.
module Main (main) where

import Control.Exception (finally, mask_, onException)
import Control.Monad (unless)
import qualified Data.ByteString.Char8 as C
import qualified Data.Text as T
import GHC.Clock (getMonotonicTimeNSec)
import System.Environment (getArgs)
import System.Exit (exitFailure)
import Warlock.Capture.Process.Bootstrap (remainingMicros, deadlineAbsoluteNs)
import Warlock.Ui.Config (UiConfig, loadUiConfig, uiDeadline)
import Warlock.Ui.Display (DisplayEnvironment, captureDisplayEnvironment, displayEnvironmentPairs)
import qualified Warlock.Ui.EngineBroker as Broker
import Warlock.Ui.EngineCustody
  (startUnreadyEngine, takeEngineChannel, engineCredentialGuard, stopEngineProcess)
import Warlock.Ui.EngineEntrypoint (Mode(..), classifyMode, runEngineOnly)
import qualified Warlock.Ui.EngineProtocol as Protocol
import Warlock.Ui.Owner
  (UiEndpoints(..), TrustedOwnerEvent, EngineResult(..), runUiOwnerPrepared, uiPassed, uiResultJson)
import Warlock.Ui.Policy (Origin, hostBytes)
import Warlock.Ui.PrivateNetwork (enterPrivateNetwork, withPeerNetwork)

require :: Bool -> String -> IO ()
require good reason = unless good (ioError (userError reason))

-- Immutable library-issued loopback origins, never page input.
port :: Origin -> IO Int
port origin = case C.readInt (C.drop 10 (hostBytes origin)) of
  Just (value,rest) | C.null rest -> pure value
  _ -> ioError (userError "engine origin invariant")

prepareSelected :: UiConfig -> DisplayEnvironment -> UiEndpoints
  -> (TrustedOwnerEvent -> IO (Either T.Text ())) -> IO (IO EngineResult, IO ())
prepareSelected config display endpoints ownerEvent = mask_ $ do
  let deadline = uiDeadline config
  incarnation <- getMonotonicTimeNSec
  identity <- either (ioError . userError . show) pure
    (Protocol.sessionId (T.pack (show incarnation)))
  controller <- port (controllerOrigin endpoints)
  bar <- port (barOrigin endpoints)
  popup <- port (popupOrigin endpoints)
  startup <- either (ioError . userError . show) pure
    (Protocol.startup controller bar popup (T.pack (deadlineAbsoluteNs deadline)) identity)
  engine <- startUnreadyEngine deadline incarnation
    ([("LANG","C.UTF-8"),("LC_ALL","C.UTF-8")] ++ displayEnvironmentPairs display)
  let stop = do
        retired <- stopEngineProcess engine
        require retired "engine process retirement unconfirmed"
  -- prepareBroker takes this known >=3 socket even on failure. Custody no
  -- longer owns it after the single masked takeEngineChannel transfer.
  prepared <- (do
    channel <- takeEngineChannel engine
    Broker.prepareBroker channel deadline startup endpoints ownerEvent)
    `onException` stop
  broker <- Broker.attachBroker prepared (engineCredentialGuard engine)
    `onException` (Broker.closePrepared prepared `finally` stop)
  let retire = do
        receipt <- Broker.closeBroker broker `finally` stop
        require (receipt == Broker.CloseConfirmed) "engine RPC retirement unconfirmed"
      run = do
        ready <- Broker.completeStartup broker
        require (ready == Broker.StartupWrittenLocally) "engine startup unconfirmed"
        let loop = do
              stopping <- uiShouldStop endpoints
              if stopping then pure () else do
                result <- Broker.serveBrokerOnce broker
                case result of
                  Broker.ReplyWrittenLocally -> loop
                  _ -> pure ()
        loop
        -- Window mapping/local writes/namespace exit cannot qualify provider
        -- callback and backing retirement. Preserve the unknown facts.
        pure (EngineResult False False)
  pure (run,retire)

runBroker :: FilePath -> IO ()
runBroker path = do
  (result,deadline) <- withPeerNetwork $ \witness -> do
    display <- captureDisplayEnvironment >>= either (ioError . userError . T.unpack) pure
    require (not (null (displayEnvironmentPairs display))) "engine Wayland transport unavailable"
    enterPrivateNetwork
    configured <- loadUiConfig path
    config <- either (ioError . userError . T.unpack) pure configured
    result <- runUiOwnerPrepared witness config (prepareSelected config display)
    pure (result,uiDeadline config)
  left <- remainingMicros deadline
  require (left > 0) "UI witness cleanup exceeded original deadline"
  C.putStrLn (uiResultJson result)
  unless (uiPassed result) exitFailure

main :: IO ()
main = do
  mode <- classifyMode <$> getArgs
  case mode of
    BrokerConfig path -> runBroker path
    EngineOnly args -> do
      result <- runEngineOnly args
      case result of
        Right observed | enginePassed observed -> pure ()
        _ -> exitFailure
    Reject -> ioError (userError "expected trusted UI configuration or owned engine role")
