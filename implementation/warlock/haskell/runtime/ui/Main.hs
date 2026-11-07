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
  (startUnreadyEngine, takeEngineChannel, engineCredentialGuard, stopEngineProcess
  , finishEngineProcess, engineNormalExit, engineExitLiveImageFacts)
import Warlock.Ui.EngineEntrypoint (Mode(..), classifyMode, runEngineObserved)
import qualified Warlock.Ui.EngineProtocol as Protocol
import Warlock.Ui.FilterBackingRoot
  (newFilterBackingRoot, filterBackingBinding, markFilterBackingSpawn, bindFilterBacking
  , retireFilterBacking, discardUnstartedBacking)
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
  backing <- newFilterBackingRoot deadline
  rootBinding <- filterBackingBinding backing `onException` discardUnstartedBacking backing
  startup <- (either (ioError . userError . show) pure
    (Protocol.startupWithBacking controller bar popup (T.pack (deadlineAbsoluteNs deadline)) identity rootBinding))
    `onException` discardUnstartedBacking backing
  -- After this reservation a startup failure may already have forked. Never
  -- delete the root through the unstarted path or invent a normal receipt.
  markFilterBackingSpawn backing
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
  bindFilterBacking backing engine broker
    `onException` ((do _ <- Broker.closeBroker broker; pure ()) `finally` stop)
  let retire = do
        closed <- Broker.closeBroker broker `finally` stop
        require (closed == Broker.CloseConfirmed) "engine RPC retirement unconfirmed"
        process <- finishEngineProcess engine
        clean <- retireFilterBacking backing process
        require clean "owned filter backing retirement unconfirmed"
      run = do
        ready <- Broker.completeStartup broker
        require (ready == Broker.StartupWrittenLocally) "engine startup unconfirmed"
        -- A local stop is returned through the existing Stop RPC. Keep serving
        -- the child's final observation/ACK while the SAME original D permits;
        -- breaking before serve would strand its natural-exit handshake.
        let loop = do
              result <- Broker.serveBrokerOnce broker
              case result of
                Broker.ReplyWrittenLocally -> loop
                Broker.GuiObservationWrittenLocally -> pure True
                _ -> pure False
        terminalAck <- loop
        observation <- Broker.brokerGuiObservation broker
        -- Child holds its live/image identity until this authenticated
        -- channel reaches EOF after the terminal ACK/postguard. Closing it
        -- before natural wait is the barrier, not a second RPC roundtrip.
        closed <- Broker.closeBroker broker
        require (closed == Broker.CloseConfirmed) "engine completion EOF unconfirmed"
        receipt <- finishEngineProcess engine
        backingClean <- retireFilterBacking backing receipt
        let complete = maybe False Protocol.guiObservationComplete observation
            normal = engineNormalExit receipt
            imageValidated = case engineExitLiveImageFacts receipt of
              Just _ -> True
              Nothing -> False
        -- Parent cleanup derives only from this same opaque normal process
        -- receipt and the actual owned backing-tree/Broker retirement. The
        -- child supplies GUI data, never this cleanup proof. Native/original
        -- journey acceptance still requires its separately observed oracles.
        pure (EngineResult (terminalAck && complete && imageValidated && normal && backingClean)
          (normal && backingClean))
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
      result <- runEngineObserved args
      case result of
        Right () -> pure ()
        _ -> exitFailure
    Reject -> ioError (userError "expected trusted UI configuration or owned engine role")
