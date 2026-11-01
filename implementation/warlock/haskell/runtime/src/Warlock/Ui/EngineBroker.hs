{-# LANGUAGE OverloadedStrings #-}
{-# LANGUAGE ScopedTypeVariables #-}
-- PREPARATION DRAFT: not a runtime integration or an authentication receipt.
-- Caller transfers one separately owned engine RPC socket, never UI fd 0.
module Warlock.Ui.EngineBroker
  ( PreparedBroker, Broker, BrokerResult(..), CloseReceipt(..), prepareBroker
  , attachBroker, closePrepared, completeStartup, serveBrokerOnce, closeBroker ) where

import Control.Exception (SomeException, SomeAsyncException, fromException, mask, mask_, onException, throwIO, try)
import Control.Monad (unless, when)
import qualified Data.ByteString as B
import Data.IORef (IORef, atomicModifyIORef', newIORef, readIORef)
import qualified Data.Text as T
import qualified Data.Text.Encoding as TE
import qualified Network.Socket as Socket
import qualified Network.Socket.ByteString as SocketBytes
import System.Timeout (timeout)
import Warlock.Capture.Process.Bootstrap (AdmissionDeadline, deadlineAbsoluteNs, remainingMicros)
import Warlock.Protocol.CredentialGuard (CredentialGuard(..))
import qualified Warlock.Protocol.EngineTransport as Transport
import Warlock.Protocol.PeerCredential (PeerCredential)
import qualified Warlock.Protocol.StrictJson as J
import qualified Warlock.Ui.EngineAdapter as Adapter
import qualified Warlock.Ui.EngineProtocol as Protocol
import Warlock.Ui.Owner (UiEndpoints(..), TrustedOwnerEvent)

-- A completed local write is not evidence that the child received or acted on
-- a reply; its independent liveness/consumption and cleanup remain unknown.
data BrokerResult = StartupWrittenLocally | ReplyWrittenLocally | Busy | NotReady | Closed | OwnerRefused CloseReceipt | Indeterminate deriving (Eq,Show)
data CloseReceipt = CloseConfirmed | CloseInProgress | CloseUncertain deriving (Eq,Show)
data Phase = BootReady Protocol.Session | BootReading | BootAdmitted
           | Ready Protocol.Session | Running | Admitted | Retired
data CloseState = SocketOpen | SocketClosing | SocketClosed | SocketUncertain
data PrepareState = PrepareOpen | PrepareTaken | PrepareClosing | PrepareClosed | PrepareUncertain

data PreparedBroker = PreparedBroker Socket.Socket Transport.CredentialReader AdmissionDeadline
  Protocol.Startup UiEndpoints (TrustedOwnerEvent -> IO (Either T.Text ())) (IORef PrepareState)

data Broker refusal = Broker
  { brokerSocket :: Socket.Socket
  , brokerReader :: Transport.CredentialReader
  , brokerGuard :: CredentialGuard refusal
  , brokerDeadline :: AdmissionDeadline
  , brokerStartup :: Protocol.Startup
  , brokerEndpoints :: UiEndpoints
  , brokerOwner :: TrustedOwnerEvent -> IO (Either T.Text ())
  , brokerPhase :: IORef Phase
  , brokerClose :: IORef CloseState
  }

-- Standard descriptors are refused before transfer; thereafter socket close
-- ownership transfers even on failure. The custody owner must independently
-- prove this socket is not an alias of fd 0 or another resource, configure
-- SO_PASSCRED before fork, and transfer the close right exactly once. This
-- function may run after fork: re-enabling the option does not establish that
-- queued ready bytes had credentials enabled at send time. The attached guard
-- must be tied to the held pidfd, birth identity and live owned child; a
-- CredentialGuard value alone proves none of those properties.
prepareBroker :: Socket.Socket -> AdmissionDeadline -> Protocol.Startup -> UiEndpoints
              -> (TrustedOwnerEvent -> IO (Either T.Text ())) -> IO PreparedBroker
prepareBroker socket deadline startup endpoints owner = mask_ $ do
  Socket.withFdSocket socket $ \descriptor ->
    unless (descriptor >= 3) (ioError (userError "engine RPC standard descriptor refused"))
  (do
    kind <- Socket.getSocketType socket
    peer <- Socket.getPeerName socket
    unless (kind == Socket.Stream && case peer of Socket.SockAddrUnix _ -> True; _ -> False)
      (ioError (userError "engine RPC requires connected Unix stream"))
    unless (Protocol.startupDeadline startup == T.pack (deadlineAbsoluteNs deadline))
      (ioError (userError "engine broker deadline mismatch"))
    let (controller,bar,popup) = Protocol.startupOrigins startup
    unless (controller == controllerOrigin endpoints && bar == barOrigin endpoints && popup == popupOrigin endpoints)
      (ioError (userError "engine broker origin mismatch"))
    left <- remainingMicros deadline
    unless (left > 0) (ioError (userError "engine broker deadline expired"))
    Transport.configureSocketFlags socket
    Transport.enablePassCredentials socket
    reader <- Transport.newCredentialReader
    prepareState <- newIORef PrepareOpen
    pure (PreparedBroker socket reader deadline startup endpoints owner prepareState))
  `onException` Socket.close socket

-- Called only after the actual held child has been created and a guard tied
-- to its PID/birth/pidfd is available. The preparation token transfers once.
attachBroker :: PreparedBroker -> CredentialGuard refusal -> IO (Broker refusal)
attachBroker (PreparedBroker socket reader deadline startup endpoints owner prepareState) guard = mask_ $ do
  taken <- atomicModifyIORef' prepareState $ \state -> case state of
    PrepareOpen -> (PrepareTaken,True)
    _ -> (state,False)
  unless taken (ioError (userError "engine broker preparation unavailable"))
  (do
    phase <- newIORef (BootReady (Protocol.newSession startup))
    closeState <- newIORef SocketOpen
    pure (Broker socket reader guard deadline startup endpoints owner phase closeState))
   `onException` (do
     result <- try (Socket.close socket) :: IO (Either SomeException ())
     let state = case result of Right () -> PrepareClosed; Left _ -> PrepareUncertain
     atomicModifyIORef' prepareState (const (state,())))

-- Use only if attachBroker did not transfer ownership. A failed close is an
-- uncertain socket receipt, not evidence of child or ancillary retirement.
closePrepared :: PreparedBroker -> IO CloseReceipt
closePrepared (PreparedBroker socket _ _ _ _ _ state) = mask_ $ do
  owns <- atomicModifyIORef' state $ \value -> case value of
    PrepareOpen -> (PrepareClosing,True)
    _ -> (value,False)
  if not owns then do
    current <- readIORef state
    pure $ case current of PrepareClosed -> CloseConfirmed; PrepareClosing -> CloseInProgress; _ -> CloseUncertain
  else do
    result <- try (Socket.close socket) :: IO (Either SomeException ())
    let status = case result of Right () -> PrepareClosed; Left _ -> PrepareUncertain
    atomicModifyIORef' state (const (status,()))
    case result of
      Right () -> pure CloseConfirmed
      Left err -> case fromException err :: Maybe SomeAsyncException of
        Just _ -> throwIO err
        Nothing -> pure CloseUncertain

-- State publication precedes close. Only this broker closes its transferred
-- socket; no process, fd 0, callback backing or namespace cleanup is implied.
closeBroker :: Broker refusal -> IO CloseReceipt
closeBroker broker = mask_ $ do
  atomicModifyIORef' (brokerPhase broker) (const (Retired,()))
  own <- atomicModifyIORef' (brokerClose broker) $ \state -> case state of
    SocketOpen -> (SocketClosing,True)
    _ -> (state,False)
  if not own then do
    state <- readIORef (brokerClose broker)
    pure $ case state of SocketClosed -> CloseConfirmed; SocketClosing -> CloseInProgress; _ -> CloseUncertain
  else do
    result <- try (Socket.close (brokerSocket broker)) :: IO (Either SomeException ())
    let finalState = case result of Right () -> SocketClosed; Left _ -> SocketUncertain
    atomicModifyIORef' (brokerClose broker) (const (finalState,()))
    case result of
      Right () -> pure CloseConfirmed
      Left err -> case fromException err :: Maybe SomeAsyncException of
        Just _ -> throwIO err
        Nothing -> pure CloseUncertain

-- One outer four-byte length frames each complete EngineProtocol message.
-- The trusted reader MUST use recvmsg and refuse malformed ancillary data and
-- unexpected rights. Check every fragment, including the length prefix; keep
-- the first credential and reject mixed credentials in the same frame.
readFrame :: Broker refusal -> (B.ByteString -> Either e Int) -> IO (B.ByteString, PeerCredential)
readFrame broker lengthOf = do
  (header,credential) <- pieces 4 Nothing []
  size <- either (const (ioError (userError "engine frame length invalid"))) pure
            (lengthOf header)
  (payload,finalCredential) <- pieces size (Just credential) []
  pure (payload,finalCredential)
  where
    pieces 0 first fragments = case first of
      Nothing -> ioError (userError "engine frame missing credential")
      Just credential -> pure (B.concat (reverse fragments),credential)
    pieces count first fragments = do
      left <- remainingMicros (brokerDeadline broker)
      unless (left > 0) (ioError (userError "engine frame deadline"))
      let requested = min count 65536
      result <- Transport.receiveCredentialChunk (brokerReader broker) (brokerSocket broker) requested
      case result of
        Left _ -> ioError (userError "engine ancillary uncertain")
        Right Transport.EndOfStream -> ioError (userError "engine frame EOF")
        Right (Transport.CredentialChunk chunk credential) -> do
          when (B.null chunk || B.length chunk > requested) (ioError (userError "engine fragment length invalid"))
          accepted <- checkFragment (brokerGuard broker) credential
          either (const (ioError (userError "engine fragment refused"))) pure accepted
          when (maybe False (/= credential) first) (ioError (userError "engine fragment identity changed"))
          pieces (count - B.length chunk) (Just credential) (chunk:fragments)

-- This timeout cannot preempt a synchronous noninterruptible provider or owner
-- callback. A return after D is uncertainty, never a fresh deadline or replay.
withinOriginalDeadline :: AdmissionDeadline -> IO a -> IO a
withinOriginalDeadline deadline action = do
  left <- remainingMicros deadline
  -- Keep 500ms of the SAME original D for the sole custody stop/reap path.
  -- This is an operation budget, never a renewed admission deadline.
  unless (left > 500000) (ioError (userError "engine broker cleanup reserve"))
  result <- timeout (left - 500000) action
  after <- remainingMicros deadline
  case result of
    Just value | after > 0 -> pure value
    _ -> ioError (userError "engine broker outcome uncertain")

-- One fixed ready object is sent by the real engine after exec. The two
-- canonical decimal strings must match the broker's immutable Startup. The
-- sole reader authenticates every fragment and the final custody admission.
-- A successful return is a local startup write, not proof of engine receipt.
completeStartup :: Broker refusal -> IO BrokerResult
completeStartup broker = mask $ \restore -> do
  selected <- atomicModifyIORef' (brokerPhase broker) $ \phase -> case phase of
    BootReady session -> (BootReading,Right session)
    BootReading -> (BootReading,Left Busy)
    BootAdmitted -> (BootAdmitted,Left Busy)
    Retired -> (Retired,Left Closed)
    _ -> (Retired,Left Indeterminate)
  case selected of
    Left Indeterminate -> do
      _ <- closeBroker broker
      pure Indeterminate
    Left result -> pure result
    Right session -> do
      outcome <- try (restore (withinOriginalDeadline (brokerDeadline broker) (startupTransaction broker)))
                 :: IO (Either SomeException ())
      case outcome of
        Left err -> do
          _ <- closeBroker broker
          case fromException err :: Maybe SomeAsyncException of
            Just _ -> throwIO err
            Nothing -> pure Indeterminate
        Right () -> do
          published <- atomicModifyIORef' (brokerPhase broker) $ \phase -> case phase of
            BootAdmitted -> (Ready session,True)
            _ -> (phase,False)
          if published then pure StartupWrittenLocally else do
            _ <- closeBroker broker
            pure Indeterminate

startupTransaction :: Broker refusal -> IO ()
startupTransaction broker = do
  (raw,credential) <- readFrame broker Transport.startupHeaderLength
  bounds <- either (const (ioError (userError "engine ready bounds"))) pure (J.bounds 512 3)
  let startup = brokerStartup broker
  startupJson <- either (const (ioError (userError "engine startup invalid"))) pure
                   (J.decodeStrict bounds (Protocol.encodeStartup startup))
  fields <- either (const (ioError (userError "engine startup invalid"))) pure
              (J.exactObject ["version","controller","bar","popup","deadline","incarnation"] startupJson)
  incarnation <- maybe (ioError (userError "engine startup invalid")) pure (lookup "incarnation" fields)
  let expected = TE.encodeUtf8 $ J.renderJson $ J.JObject
        [("engineReady",J.JNumber "1"),("deadline",J.JString (Protocol.startupDeadline startup)),("incarnation",incarnation)]
  -- Exact bytes also exclude duplicate keys, whitespace, alternate numeric
  -- spellings and extra fields; they do not provide process authentication.
  unless (raw == expected) (ioError (userError "engine ready invalid"))
  admitted <- withCredentialAdmission (brokerGuard broker) credential $ do
    left <- remainingMicros (brokerDeadline broker)
    unless (left > 0) (ioError (userError "engine ready deadline"))
    live <- atomicModifyIORef' (brokerPhase broker) $ \phase -> case phase of
      BootReading -> (BootAdmitted,True)
      _ -> (phase,False)
    unless live (ioError (userError "engine broker retired"))
    either (const (ioError (userError "engine startup too large"))) pure
      (Transport.startupPrefix (Protocol.encodeStartup startup))
  startupFrame <- either (const (ioError (userError "engine ready refused"))) pure admitted
  current <- readIORef (brokerPhase broker)
  case current of BootAdmitted -> pure (); _ -> ioError (userError "engine broker retired")
  stillOwned <- checkFragment (brokerGuard broker) credential
  either (const (ioError (userError "engine ready peer changed"))) pure stillOwned
  beforeSend <- remainingMicros (brokerDeadline broker)
  unless (beforeSend > 0) (ioError (userError "engine startup deadline"))
  SocketBytes.sendAll (brokerSocket broker) startupFrame
  afterWrite <- checkFragment (brokerGuard broker) credential
  either (const (ioError (userError "engine startup peer uncertain"))) pure afterWrite
  after <- remainingMicros (brokerDeadline broker)
  unless (after > 0) (ioError (userError "engine startup outcome uncertain"))

-- One caller at a time can claim the phase. No MVar, owner scope lock or
-- protocol lock is held across recvmsg, the owner callback, or sendAll.
-- Concurrent close retires the phase; a subsequent success cannot revive it.
serveBrokerOnce :: Broker refusal -> IO BrokerResult
serveBrokerOnce broker = mask $ \restore -> do
  selected <- atomicModifyIORef' (brokerPhase broker) $ \phase -> case phase of
    Ready session -> (Running,Right session)
    Running -> (Running,Left Busy)
    Admitted -> (Admitted,Left Busy)
    BootReady _ -> (phase,Left NotReady)
    BootReading -> (phase,Left Busy)
    BootAdmitted -> (phase,Left Busy)
    Retired -> (Retired,Left Closed)
  case selected of
    Left result -> pure result
    Right session -> do
      outcome <- try (restore (withinOriginalDeadline (brokerDeadline broker) (transaction broker session)))
                 :: IO (Either SomeException (Protocol.Session,Bool))
      case outcome of
        Left err -> do
          _ <- closeBroker broker
          case fromException err :: Maybe SomeAsyncException of
            Just _ -> throwIO err
            Nothing -> pure Indeterminate
        Right (_,True) -> OwnerRefused <$> closeBroker broker
        Right (updated,False) -> do
          published <- atomicModifyIORef' (brokerPhase broker) $ \phase -> case phase of
            Admitted -> (Ready updated,True)
            _ -> (phase,False)
          if published then pure ReplyWrittenLocally else do
            _ <- closeBroker broker
            pure Indeterminate

transaction :: Broker refusal -> Protocol.Session -> IO (Protocol.Session,Bool)
transaction broker session = do
  (raw,credential) <- readFrame broker Transport.engineHeaderLength
  let (accepted,decoded) = Protocol.acceptRequest session raw
  request <- either (const (ioError (userError "engine protocol refused"))) pure decoded
  -- Guard must serialize final peer admission with its own retirement, and
  -- must reject child exit/replacement after the last fragment. It must not
  -- invoke the supplied action on refusal. This module cannot prove the guard.
  admitted <- withCredentialAdmission (brokerGuard broker) credential $ do
    left <- remainingMicros (brokerDeadline broker)
    unless (left > 0) (ioError (userError "engine admission deadline"))
    -- Linearize admission against this broker's concurrent close. A callback
    -- already admitted can still be running when closeBroker returns; socket
    -- closure is not a callback-retirement receipt.
    live <- atomicModifyIORef' (brokerPhase broker) $ \phase -> case phase of
      Running -> (Admitted,True)
      _ -> (phase,False)
    unless live (ioError (userError "engine broker retired"))
    replyResult <- Adapter.serveRequest (brokerEndpoints broker) (brokerOwner broker) request
    reply <- either (const (ioError (userError "engine owner refused"))) pure replyResult
    remaining <- remainingMicros (brokerDeadline broker)
    unless (remaining > 0) (ioError (userError "engine owner outcome uncertain"))
    let (sending,encoded) = Protocol.finishRequest accepted reply
    response <- either (const (ioError (userError "engine reply refused"))) pure encoded
    framed <- either (const (ioError (userError "engine reply too large"))) pure
                (Transport.enginePrefix response)
    let ownerRefused = case reply of Protocol.EventReply Protocol.Refused -> True; _ -> False
    pure (sending,framed,ownerRefused)
  (sending,framed,ownerRefused) <- either (const (ioError (userError "engine admission refused"))) pure admitted
  -- Admission lease is released before socket IO; no Owner/custody admission
  -- scope is held across the reply write. Concurrent retirement is uncertain.
  current <- readIORef (brokerPhase broker)
  case current of Admitted -> pure (); _ -> ioError (userError "engine broker retired")
  beforeSend <- remainingMicros (brokerDeadline broker)
  unless (beforeSend > 0) (ioError (userError "engine reply deadline"))
  SocketBytes.sendAll (brokerSocket broker) framed
  leftAfter <- remainingMicros (brokerDeadline broker)
  unless (leftAfter > 0) (ioError (userError "engine reply outcome uncertain"))
  let (finished,receipt) = Protocol.confirmReplySent sending
  either (const (ioError (userError "engine reply state uncertain"))) (const (pure (finished,ownerRefused))) receipt
