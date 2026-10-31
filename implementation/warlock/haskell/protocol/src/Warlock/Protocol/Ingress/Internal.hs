{-# LANGUAGE ScopedTypeVariables #-}
-- Private owner shell: ownership is not peer authentication or native authority.
module Warlock.Protocol.Ingress.Internal
 (IngressOwner,IngressBinding,ingressBinding,CounterError(..),Direction(..),Reason(..),GateStatus(..),
  Priority(..),ChannelError(..),EndpointState(..),Phase(..),OwnerStatus(..),OfferResult(..),ActivationResult(..),IngressResult(..),
  CredentialIngress,CredentialIngressResult(..),newCredentialIngress,newCredentialIngressWithReaderForTest,transferCredentialSocket,activateCredentialIngress,receiveCredentialIngress,retireCredentialIngress,credentialIngressStatus,enqueueCredentialIngress,sendCredentialIngress,retainedCredentialIngressFrames,
  newIngressOwner,newIngressOwnerWithHooks,newIngressOwnerWithPrepareHook,holdOwnerGateForTest,holdCloseGateForTest,flagsForTest,transferSocket,transferSocketWithHooks,activateIngress,activateIngressWithHook,receiveIngress,enqueueIngress,sendIngress,retainedIngressFrames,retireIngress,ingressStatus,ingressRejections) where
import Control.Concurrent.MVar
import Control.Exception (SomeException,SomeAsyncException,finally,fromException,mask,uninterruptibleMask_,try,throwIO)
import qualified Data.ByteString as B
import Data.Text (Text)
import qualified Network.Socket as S
import qualified Warlock.Protocol.Boundary.Internal as G
import Warlock.Protocol.Boundary.Internal (Direction(..),Reason(..),GateStatus(..))
import Warlock.Protocol.Codec (CheckedClient,CheckedServer)
import Warlock.Protocol.Identity (Binding,CounterError(..),binding,parseCounter)
import qualified Warlock.Transport.Channel as C
import Warlock.Transport.Channel (Priority(..),ChannelError(..))
import qualified Warlock.Transport.SocketFlags as F
import qualified Warlock.Transport.PeerCredentials as P
import Warlock.Protocol.CredentialGuard (CredentialGuard(..))

newtype IngressBinding = IngressBinding Binding
ingressBinding :: Text -> Text -> Text -> Either CounterError IngressBinding
ingressBinding life session frontend = do
 a <- parseCounter False life
 b <- parseCounter False session
 c <- parseCounter False frontend
 IngressBinding <$> binding a b c

data EndpointState = EndpointOpen | EndpointClosing | EndpointConfirmed | EndpointUncertain deriving (Eq,Show)
data Phase = OwnerEmpty | OwnerPending | OwnerActivating | OwnerLive | OwnerFailed | OwnerRetiring | OwnerRetired deriving (Eq,Show)
data OwnerStatus = OwnerStatus { phase :: Phase, accepted :: Bool, gate :: GateStatus, endpoint :: Maybe EndpointState, setupFailure :: Maybe String, closeFailure :: Maybe String } deriving (Eq,Show)
data OfferResult = OfferAccepted | OfferRefused deriving (Eq,Show)
data ActivationResult = ActivationLive | ActivationRetired | ActivationUnavailable deriving (Eq,Show)
data IngressResult = Delivered | Rejected Reason | TransportFailure ChannelError | NotLive deriving (Eq,Show)
data SharedClose = SharedClose S.Socket (IO ()) (MVar (EndpointState,Maybe String))
data Slot = NoSocket | Offered SharedClose | Setup SharedClose Bool | Running SharedClose C.Channel | Broken SharedClose | Stopped (Maybe SharedClose) (Maybe C.Channel)
data State = State Slot Bool (Maybe String)
data IngressOwner = IngressOwner G.Gate Direction (MVar State) (MVar ()) (S.Socket -> IO ()) (S.Socket -> IO ())

-- Private deterministic fixture only; never exported through the public facade.
holdOwnerGateForTest :: IngressOwner -> MVar () -> MVar () -> IO ()
holdOwnerGateForTest (IngressOwner _ _ state _ _ _) entered release =
 modifyMVar_ state $ \current -> putMVar entered () >> takeMVar release >> pure current
holdCloseGateForTest :: IngressOwner -> MVar () -> MVar () -> IO ()
holdCloseGateForTest (IngressOwner _ _ state _ _ _) entered release = do
 selected <- withMVar state $ \(State slot _ _) -> pure $ case slot of Offered shared -> Just shared; _ -> Nothing
 case selected of
  Nothing -> ioError (userError "fixture requires pending socket")
  Just (SharedClose _ _ cell) -> modifyMVar_ cell $ \current -> putMVar entered () >> takeMVar release >> pure current
-- Nonconcurrent fixture observation; never exposes a socket or raw descriptor.
flagsForTest :: IngressOwner -> IO Bool
flagsForTest (IngressOwner _ _ state _ _ _) = do
 selected <- withMVar state $ \(State slot _ _) -> pure $ case slot of Running shared _ -> Just shared; _ -> Nothing
 case selected of Nothing -> pure False; Just (SharedClose sock _ _) -> F.socketFlagsVerified sock

newIngressOwner :: IngressBinding -> Direction -> (CheckedClient -> IO ()) -> (CheckedServer -> IO ()) -> IO IngressOwner
newIngressOwner b d client server = newIngressOwnerWithHooks b d client server F.configureSocketFlags S.close
-- Private fixture seams; the public facade does not export these hooks.
newIngressOwnerWithHooks :: IngressBinding -> Direction -> (CheckedClient -> IO ()) -> (CheckedServer -> IO ()) -> (S.Socket -> IO ()) -> (S.Socket -> IO ()) -> IO IngressOwner
newIngressOwnerWithHooks = newIngressOwnerWithPrepareHook (pure ())
newIngressOwnerWithPrepareHook :: IO () -> IngressBinding -> Direction -> (CheckedClient -> IO ()) -> (CheckedServer -> IO ()) -> (S.Socket -> IO ()) -> (S.Socket -> IO ()) -> IO IngressOwner
newIngressOwnerWithPrepareHook prepare (IngressBinding bindingValue) direction client server configure closer = do
 prepare
 serial <- newMVar ()
 state <- newMVar (State NoSocket False Nothing)
 gateValue <- G.newGate bindingValue (G.foldEnvelope client server)
 pure (IngressOwner gateValue direction state serial configure closer)

-- One exclusive caller offers one socket. Before the MVar publication the
-- caller owns it; afterwards the owner does, regardless of return/exception.
transferSocket :: IngressOwner -> S.Socket -> IO OfferResult
transferSocket = transferSocketWithHooks (pure ()) (pure ())
transferSocketWithHooks :: IO () -> IO () -> IngressOwner -> S.Socket -> IO OfferResult
transferSocketWithHooks before after (IngressOwner _ _ state _ _ closer) sock = mask $ \restore -> do
 restore before
 closeState <- newMVar (EndpointOpen,Nothing)
 let shared = SharedClose sock (closer sock) closeState
 result <- modifyMVar state $ \current@(State slot wasAccepted failure) -> case slot of
  NoSocket | not wasAccepted -> pure (State (Offered shared) True failure,OfferAccepted)
  _ -> pure (current,OfferRefused)
 case result of OfferAccepted -> restore after >> pure result; OfferRefused -> pure result

-- The MVar holds the exact object and once-only close outcome even when close
-- fails. No numeric descriptor is retained or retried.
closeShared :: SharedClose -> IO ()
closeShared (SharedClose _ action cell) = mask $ \restore -> do
 previous <- modifyMVar cell $ \old@(status,_) -> case status of
  EndpointOpen -> pure ((EndpointClosing,Nothing),EndpointOpen)
  _ -> pure (old,status)
 case previous of
  EndpointConfirmed -> pure ()
  EndpointClosing -> ioError (userError "socket close in progress")
  EndpointUncertain -> ioError (userError "socket close uncertain")
  EndpointOpen -> do
   result <- try (restore action) :: IO (Either SomeException ())
   uninterruptibleMask_ $ modifyMVar_ cell $ \_ -> pure $ case result of
    Right () -> (EndpointConfirmed,Nothing)
    Left err -> (EndpointUncertain,Just (show err))
   either throwIO pure result

-- Only a genuinely unclaimed close may be attempted again. In particular,
-- Closing and Uncertain never cause another numerical socket close.
closeIfUnclaimed :: SharedClose -> IO ()
closeIfUnclaimed shared@(SharedClose _ _ cell) = do
 (status,_) <- readMVar cell
 case status of EndpointOpen -> closeShared shared; _ -> pure ()

activateIngress :: IngressOwner -> IO ActivationResult
activateIngress = activateIngressWithHook (pure ())
-- Controlled private seam after Live is already published in the retained shell.
activateIngressWithHook :: IO () -> IngressOwner -> IO ActivationResult
activateIngressWithHook afterPublication owner@(IngressOwner _ direction state _ configure _) = mask $ \restore -> do
 selected <- modifyMVar state $ \current@(State slot wasAccepted failure) -> case slot of
  Offered shared -> pure (State (Setup shared False) wasAccepted failure,Just shared)
  _ -> pure (current,Nothing)
 case selected of
  Nothing -> pure ActivationUnavailable
  Just shared@(SharedClose sock _ _) -> do
   result <- try (restore (configure sock >> C.newConfiguredChannel sock (case direction of FromElm -> C.ClientInbound; FromNative -> C.ServerInbound) (closeShared shared))) :: IO (Either SomeException C.Channel)
   -- Finite ownership publication only: never interrupt after setup has
   -- finished but before its lease/state transition is recorded.
   disposition <- uninterruptibleMask_ $ modifyMVar state $ \current@(State slot wasAccepted _) -> case slot of
    Setup _ retiring -> case result of
     Right channel | not retiring -> pure (State (Running shared channel) wasAccepted Nothing,False)
     Right channel -> pure (State (Stopped (Just shared) (Just channel)) wasAccepted Nothing,True)
     Left err -> pure (State (Broken shared) wasAccepted (Just (show err)),True)
    _ -> pure (current,True)
   if not disposition then restore afterPublication >> pure ActivationLive else do
    cleanup <- try (closeShared shared) :: IO (Either SomeException ())
    case result of
     Left err -> throwPreferred err cleanup
     Right _ -> case cleanup of
      Left err -> throwIO err
      Right () -> do
       _ <- ingressStatus owner
       pure ActivationRetired

throwPreferred :: SomeException -> Either SomeException () -> IO a
throwPreferred original cleanup = case fromException original :: Maybe SomeAsyncException of
 Just _ -> throwIO original
 Nothing -> case cleanup of
  Left later -> case fromException later :: Maybe SomeAsyncException of Just _ -> throwIO later; Nothing -> throwIO original
  Right () -> throwIO original

liveChannel :: IngressOwner -> IO (Maybe C.Channel)
liveChannel (IngressOwner _ _ state _ _ _) = do
 selected <- withMVar state $ \(State slot _ _) -> pure $ case slot of
  Running shared channel -> Just (shared,channel)
  _ -> Nothing
 case selected of
  Just (SharedClose _ _ cell,channel) -> do
   (status,_) <- readMVar cell
   pure (if status==EndpointOpen then Just channel else Nothing)
  Nothing -> pure Nothing

receiveIngress :: IngressOwner -> IO IngressResult
receiveIngress owner@(IngressOwner gateValue direction _ serial _ _) = mask $ \restore -> do
 acquired <- tryTakeMVar serial
 case acquired of
  Nothing -> pure (TransportFailure C.Busy)
  Just () -> (do
   selectedResult <- try (restore (liveChannel owner)) :: IO (Either SomeException (Maybe C.Channel))
   case selectedResult of
    Left err -> retireOnError owner err
    Right Nothing -> pure NotLive
    Right (Just channel) -> do
     readResult <- try (restore (C.receiveRawDeadline channel)) :: IO (Either SomeException (Either C.ChannelError (B.ByteString,Integer)))
     case readResult of
      Left err -> retireOnError owner err
      Right (Left err) -> do
       retired <- try (G.retire gateValue) :: IO (Either SomeException GateStatus)
       case retired of Left failure -> retireOnError owner failure; Right _ -> pure (TransportFailure err)
      Right (Right (bytes,deadline)) -> do
       dispatched <- try (restore (G.dispatchUntil gateValue direction bytes deadline)) :: IO (Either SomeException (Either Reason ()))
       case dispatched of
        Right (Right ()) -> pure Delivered
        Right (Left reason) -> do
         closed <- try (C.closeChannel channel) :: IO (Either SomeException C.CloseResult)
         case closed of Left err -> retireOnError owner err; Right _ -> pure (Rejected reason)
        Left err -> retireOnError owner err) `finally` putMVar serial ()
retireOnError :: IngressOwner -> SomeException -> IO a
retireOnError owner original = do
 cleanup <- try (retireIngress owner) :: IO (Either SomeException OwnerStatus)
 throwPreferred original (case cleanup of Left e -> Left e; Right _ -> Right ())

enqueueIngress :: IngressOwner -> Priority -> B.ByteString -> IO (Either ChannelError ())
enqueueIngress owner priority bytes = withLiveOperation owner (\channel -> C.enqueue channel priority bytes)
sendIngress :: IngressOwner -> IO (Either ChannelError ())
sendIngress owner = withLiveOperation owner C.sendNext

-- Observation only: uncertain queued bytes never authorize retransmission.
retainedIngressFrames :: IngressOwner -> IO [(Priority,B.ByteString)]
retainedIngressFrames (IngressOwner _ _ state _ _ _) = do
 selected <- withMVar state $ \(State slot _ _) -> pure $ case slot of
  Running _ channel -> Just channel
  Stopped _ channel -> channel
  _ -> Nothing
 case selected of Nothing -> pure []; Just channel -> C.retainedFrames channel

withLiveOperation :: IngressOwner -> (C.Channel -> IO (Either ChannelError ())) -> IO (Either ChannelError ())
withLiveOperation owner action = mask $ \restore -> do
 result <- try (restore (do
  selected <- liveChannel owner
  case selected of Nothing -> pure (Left C.Closed); Just channel -> action channel)) :: IO (Either SomeException (Either ChannelError ()))
 case result of Left err -> retireOnError owner err; Right value -> pure value

retireIngress :: IngressOwner -> IO OwnerStatus
retireIngress owner@(IngressOwner gateValue _ state _ _ _) = mask $ \_ -> do
 -- Mark retirement before gate closure to serialize against setup publication;
 -- the gate still closes before any live socket close is attempted.
 action <- uninterruptibleMask_ $ modifyMVar state $ \(State slot wasAccepted failure) -> case slot of
  NoSocket -> pure (State (Stopped Nothing Nothing) wasAccepted failure,Nothing)
  Offered shared -> pure (State (Stopped (Just shared) Nothing) wasAccepted failure,Just (closeShared shared))
  Setup shared _ -> pure (State (Setup shared True) wasAccepted failure,Nothing)
  Running shared channel -> pure (State (Stopped (Just shared) (Just channel)) wasAccepted failure,Just (do _ <- C.closeChannel channel; pure ()))
  Broken shared -> pure (State (Stopped (Just shared) Nothing) wasAccepted failure,Just (closeShared shared))
  Stopped saved channel -> pure (State (Stopped saved channel) wasAccepted failure,fmap closeIfUnclaimed saved)
 gateResult <- try (uninterruptibleMask_ (G.retire gateValue)) :: IO (Either SomeException GateStatus)
 cleanup <- case action of Nothing -> pure (Right ()); Just closeAction -> try closeAction
 case gateResult of
  Left err -> throwPreferred err cleanup
  Right _ -> case cleanup of Left err -> throwIO (err :: SomeException); Right () -> ingressStatus owner

ingressStatus :: IngressOwner -> IO OwnerStatus
ingressStatus (IngressOwner gateValue _ state _ _ _) = do
 (p,wasAccepted,failure,shared) <- withMVar state $ \(State slot a f) -> pure $ case slot of
  NoSocket -> (OwnerEmpty,a,f,Nothing)
  Offered s -> (OwnerPending,a,f,Just s)
  Setup s False -> (OwnerActivating,a,f,Just s)
  Setup s True -> (OwnerRetiring,a,f,Just s)
  Running s _ -> (OwnerLive,a,f,Just s)
  Broken s -> (OwnerFailed,a,f,Just s)
  Stopped s _ -> (OwnerRetired,a,f,s)
 (closeState,closeErr) <- case shared of Nothing -> pure (Nothing,Nothing); Just (SharedClose _ _ cell) -> do (c,e) <- readMVar cell; pure (Just c,e)
 gateState <- G.gateStatus gateValue
 let actualPhase
      | p==OwnerLive && closeState/=Just EndpointOpen = OwnerFailed
      | p==OwnerRetired && closeState==Just EndpointUncertain = OwnerFailed
      | p==OwnerRetired && (gateState/=G.Retired || closeState==Just EndpointClosing || closeState==Just EndpointOpen) = OwnerRetiring
      | otherwise = p
 pure (OwnerStatus actualPhase wasAccepted gateState closeState failure closeErr)
ingressRejections :: IngressOwner -> IO [Reason]
ingressRejections (IngressOwner gateValue _ _ _ _ _) = G.rejectionReasons gateValue

-- This owner is allocated before a socket is offered. Its reader and any
-- quarantined ancillary descriptors remain reachable even after socket close.
data CredentialIngress = CredentialIngress IngressOwner P.CredentialReader
data CredentialIngressResult refusal = CredentialDelivered | CredentialRejected Reason
 | CredentialFrameRejected (C.CredentialFrameError refusal) | CredentialAdmissionRejected refusal
 | CredentialNotLive deriving (Eq,Show)

newCredentialIngress :: IngressBinding -> Direction -> (CheckedClient -> IO ()) -> (CheckedServer -> IO ()) -> IO CredentialIngress
newCredentialIngress bindingValue direction client server = do
 reader <- P.newCredentialReader
 owner <- newIngressOwnerWithHooks bindingValue direction client server
   (\socket -> F.configureSocketFlags socket >> P.enablePassCredentials socket) S.close
 pure (CredentialIngress owner reader)
-- Same-package source-fixture seam. The public facade cannot replace a reader.
newCredentialIngressWithReaderForTest :: P.CredentialReader -> IngressBinding -> Direction -> (CheckedClient -> IO ()) -> (CheckedServer -> IO ()) -> IO CredentialIngress
newCredentialIngressWithReaderForTest reader bindingValue direction client server = do
 owner <- newIngressOwnerWithHooks bindingValue direction client server
   (\socket -> F.configureSocketFlags socket >> P.enablePassCredentials socket) S.close
 pure (CredentialIngress owner reader)
transferCredentialSocket :: CredentialIngress -> S.Socket -> IO OfferResult
transferCredentialSocket (CredentialIngress owner _) = transferSocket owner
activateCredentialIngress :: CredentialIngress -> IO ActivationResult
activateCredentialIngress (CredentialIngress owner _) = activateIngress owner
credentialIngressStatus :: CredentialIngress -> IO (OwnerStatus,P.ReaderStatus)
credentialIngressStatus (CredentialIngress owner reader) = (,) <$> ingressStatus owner <*> P.credentialReaderStatus reader
retireCredentialIngress :: CredentialIngress -> IO OwnerStatus
retireCredentialIngress (CredentialIngress owner _) = retireIngress owner
enqueueCredentialIngress :: CredentialIngress -> Priority -> B.ByteString -> IO (Either ChannelError ())
enqueueCredentialIngress (CredentialIngress owner _) = enqueueIngress owner
sendCredentialIngress :: CredentialIngress -> IO (Either ChannelError ())
sendCredentialIngress (CredentialIngress owner _) = sendIngress owner
retainedCredentialIngressFrames :: CredentialIngress -> IO [(Priority,B.ByteString)]
retainedCredentialIngressFrames (CredentialIngress owner _) = retainedIngressFrames owner

-- The same serial admission and channel read gate serve legacy and credential
-- paths. Scope admission encloses the actual checked gate dispatch and handler;
-- no credential or checked envelope is an effect or native capability.
receiveCredentialIngress :: forall refusal. CredentialIngress -> CredentialGuard refusal -> IO (CredentialIngressResult refusal)
receiveCredentialIngress (CredentialIngress owner@(IngressOwner gateValue direction _ serial _ _) reader) guard = mask $ \restore -> do
 acquired <- tryTakeMVar serial
 case acquired of
  Nothing -> pure (CredentialFrameRejected (C.CredentialTransport C.Busy))
  Just () -> (do
   selected <- try (restore (liveChannel owner)) :: IO (Either SomeException (Maybe C.Channel))
   case selected of
    Left err -> retireOnError owner err
    Right Nothing -> pure CredentialNotLive
    Right (Just channel) -> do
     readResult <- try (restore (C.receiveCredentialFrame reader guard channel)) :: IO (Either SomeException (Either (C.CredentialFrameError refusal) (B.ByteString,Integer,P.PeerCredential)))
     case readResult of
      Left err -> retireOnError owner err
      Right (Left err) -> do
       retired <- try (G.retire gateValue) :: IO (Either SomeException GateStatus)
       case retired of Left failure -> retireOnError owner failure; Right _ -> pure (CredentialFrameRejected err)
      Right (Right (bytes,deadline,credential)) -> do
       admission <- try (restore (withCredentialAdmission guard credential (G.dispatchUntil gateValue direction bytes deadline))) :: IO (Either SomeException (Either refusal (Either Reason ())))
       case admission of
        Left err -> retireOnError owner err
        Right (Left refusal) -> do
         closed <- try (C.closeChannel channel) :: IO (Either SomeException C.CloseResult)
         case closed of Left err -> retireOnError owner err; Right _ -> pure (CredentialAdmissionRejected refusal)
        Right (Right (Left reason)) -> do
         closed <- try (C.closeChannel channel) :: IO (Either SomeException C.CloseResult)
         case closed of Left err -> retireOnError owner err; Right _ -> pure (CredentialRejected reason)
        Right (Right (Right ())) -> pure CredentialDelivered) `finally` putMVar serial ()
