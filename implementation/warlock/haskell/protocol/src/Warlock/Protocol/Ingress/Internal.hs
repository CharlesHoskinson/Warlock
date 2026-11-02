{-# LANGUAGE RankNTypes #-}
{-# LANGUAGE ScopedTypeVariables #-}
-- Private owner shell: ownership is not peer authentication or native authority.
module Warlock.Protocol.Ingress.Internal
 (IngressOwner,IngressBinding,ingressBinding,CounterError(..),Direction(..),Reason(..),GateStatus(..),
  Priority(..),ChannelError(..),EndpointState(..),Phase(..),OwnerStatus(..),OfferResult(..),ActivationResult(..),IngressResult(..),
  CredentialIngress,CredentialIngressT,CredentialIngressResult(..),newDesktopCredentialIngressWithContext,receivePersistentCredentialIngressOwned,PersistentIngressResult(..),PersistentSendResult(..),receivePersistentCredentialIngress,sendPersistentCredentialIngress,newCredentialIngress,newDesktopCredentialIngress,newCredentialIngressWithReaderForTest,transferCredentialSocket,activateCredentialIngress,receiveCredentialIngress,receiveDesktopCredentialIngressAfterIdle,retireCredentialIngress,credentialIngressStatus,enqueueCredentialIngress,sendCredentialIngress,retainedCredentialIngressFrames,
  WaitProbe,newWaitProbe,waitProbeRegistered,releaseWaitProbe,receivePersistentCredentialIngressWithProbe,sendPersistentCredentialIngressWithHook,sendPersistentCredentialIngressWithHooks,
  newIngressOwner,newIngressOwnerWithHooks,newIngressOwnerWithPrepareHook,holdOwnerGateForTest,holdCloseGateForTest,flagsForTest,transferSocket,transferSocketWithHooks,activateIngress,activateIngressWithHook,receiveIngress,enqueueIngress,sendIngress,retainedIngressFrames,retireIngress,ingressStatus,ingressRejections) where
import Control.Concurrent.MVar
import Warlock.Capture.Process (ToolError)
import qualified Warlock.Capture.Process.Persistent as Persistent
import Data.IORef (IORef, newIORef, readIORef, writeIORef)
import GHC.Conc (STM, TVar, atomically, newTVarIO, readTVar, writeTVar, orElse, retry, threadWaitReadSTM)
import Control.Exception (bracket)
import Control.Exception (SomeException,SomeAsyncException,finally,fromException,mask,uninterruptibleMask_,try,throwIO)
import qualified Data.ByteString as B
import Data.Text (Text)
import qualified Network.Socket as S
import qualified Warlock.Protocol.Boundary.Internal as G
import Warlock.Protocol.Boundary.Internal (Direction(..),Reason(..),GateStatus(..))
import Warlock.Protocol.Codec (CheckedClient,CheckedServer)
import Warlock.Protocol.Profile
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
-- Closing bit and borrower count belong to the unique SharedClose owner.
type SocketPins = TVar (Bool,Int)
data SharedClose = SharedClose S.Socket (IO ()) (MVar (EndpointState,Maybe String)) SocketPins
data Slot = NoSocket | Offered SharedClose | Setup SharedClose Bool | Running SharedClose C.Channel | Broken SharedClose | Stopped (Maybe SharedClose) (Maybe C.Channel)
data State = State Slot Bool (Maybe String)
data IngressOwnerT ctx = IngressOwner CodecProfile (G.GateT ctx) Direction (MVar State) (MVar ()) (S.Socket -> IO ()) (S.Socket -> IO ())
type IngressOwner = IngressOwnerT ()

-- Private deterministic fixture only; never exported through the public facade.
holdOwnerGateForTest :: (IngressOwnerT ctx) -> MVar () -> MVar () -> IO ()
holdOwnerGateForTest (IngressOwner _ _ _ state _ _ _) entered release =
 modifyMVar_ state $ \current -> putMVar entered () >> takeMVar release >> pure current
holdCloseGateForTest :: (IngressOwnerT ctx) -> MVar () -> MVar () -> IO ()
holdCloseGateForTest (IngressOwner _ _ _ state _ _ _) entered release = do
 selected <- withMVar state $ \(State slot _ _) -> pure $ case slot of Offered shared -> Just shared; _ -> Nothing
 case selected of
  Nothing -> ioError (userError "fixture requires pending socket")
  Just (SharedClose _ _ cell _) -> modifyMVar_ cell $ \current -> putMVar entered () >> takeMVar release >> pure current
-- Nonconcurrent fixture observation; never exposes a socket or raw descriptor.
flagsForTest :: (IngressOwnerT ctx) -> IO Bool
flagsForTest (IngressOwner _ _ _ state _ _ _) = do
 selected <- withMVar state $ \(State slot _ _) -> pure $ case slot of Running shared _ -> Just shared; _ -> Nothing
 case selected of Nothing -> pure False; Just (SharedClose sock _ _ _) -> F.socketFlagsVerified sock

newIngressOwner :: IngressBinding -> Direction -> (CheckedClient -> IO ()) -> (CheckedServer -> IO ()) -> IO IngressOwner
newIngressOwner b d client server = newIngressOwnerWithHooks b d client server F.configureSocketFlags S.close
-- Private fixture seams; the public facade does not export these hooks.
newIngressOwnerWithHooks :: IngressBinding -> Direction -> (CheckedClient -> IO ()) -> (CheckedServer -> IO ()) -> (S.Socket -> IO ()) -> (S.Socket -> IO ()) -> IO IngressOwner
newIngressOwnerWithHooks = newIngressOwnerWithPrepareHook (pure ())
newIngressOwnerWithPrepareHook :: IO () -> IngressBinding -> Direction -> (CheckedClient -> IO ()) -> (CheckedServer -> IO ()) -> (S.Socket -> IO ()) -> (S.Socket -> IO ()) -> IO IngressOwner
newIngressOwnerWithPrepareHook = newIngressOwnerWithProfile nativeProfile
newIngressOwnerWithProfile :: CodecProfile -> IO () -> IngressBinding -> Direction -> (CheckedClient -> IO ()) -> (CheckedServer -> IO ()) -> (S.Socket -> IO ()) -> (S.Socket -> IO ()) -> IO IngressOwner
newIngressOwnerWithProfile profile prepare bindingValue direction client server configure closer =
 newIngressOwnerWithProfileContext profile prepare bindingValue direction (\() value -> client value) (\() value -> server value) configure closer
newIngressOwnerWithProfileContext :: CodecProfile -> IO () -> IngressBinding -> Direction -> (ctx -> CheckedClient -> IO ()) -> (ctx -> CheckedServer -> IO ()) -> (S.Socket -> IO ()) -> (S.Socket -> IO ()) -> IO (IngressOwnerT ctx)
newIngressOwnerWithProfileContext profile prepare (IngressBinding bindingValue) direction client server configure closer = do
 prepare
 serial <- newMVar ()
 state <- newMVar (State NoSocket False Nothing)
 gateValue <- G.newGateWithContext profile bindingValue (\ctx -> G.foldEnvelope (client ctx) (server ctx))
 pure (IngressOwner profile gateValue direction state serial configure closer)

-- One exclusive caller offers one socket. Before the MVar publication the
-- caller owns it; afterwards the owner does, regardless of return/exception.
transferSocket :: (IngressOwnerT ctx) -> S.Socket -> IO OfferResult
transferSocket = transferSocketWithHooks (pure ()) (pure ())
transferSocketWithHooks :: IO () -> IO () -> (IngressOwnerT ctx) -> S.Socket -> IO OfferResult
transferSocketWithHooks before after (IngressOwner _ _ _ state _ _ closer) sock = mask $ \restore -> do
 restore before
 closeState <- newMVar (EndpointOpen,Nothing)
 pins <- newTVarIO (False,0)
 let shared = SharedClose sock (closer sock) closeState pins
 result <- modifyMVar state $ \current@(State slot wasAccepted failure) -> case slot of
  NoSocket | not wasAccepted -> pure (State (Offered shared) True failure,OfferAccepted)
  _ -> pure (current,OfferRefused)
 case result of OfferAccepted -> restore after >> pure result; OfferRefused -> pure result

-- The MVar holds the exact object and once-only close outcome even when close
-- fails. No numeric descriptor is retained or retried.
closeShared :: SharedClose -> IO ()
closeShared (SharedClose _ action cell pins) = mask $ \restore -> do
 previous <- modifyMVar cell $ \old@(status,_) -> case status of
  EndpointOpen -> pure ((EndpointClosing,Nothing),EndpointOpen)
  _ -> pure (old,status)
 case previous of
  EndpointConfirmed -> pure ()
  EndpointClosing -> ioError (userError "socket close in progress")
  EndpointUncertain -> ioError (userError "socket close uncertain")
  EndpointOpen -> do
   -- An overlapping persistent read keeps the socket alive. Latch closure
   -- and report uncertain without invoking the closer; no retry is authorized.
   canClose <- atomically $ do
    (_,n) <- readTVar pins
    writeTVar pins (True,n)
    pure (n == 0)
   result <- try (if canClose then restore action else ioError (userError "socket borrow still active")) :: IO (Either SomeException ())
   uninterruptibleMask_ $ modifyMVar_ cell $ \_ -> pure $ case result of
    Right () -> (EndpointConfirmed,Nothing)
    Left err -> (EndpointUncertain,Just (show err))
   either throwIO pure result

-- Only a genuinely unclaimed close may be attempted again. In particular,
-- Closing and Uncertain never cause another numerical socket close.
closeIfUnclaimed :: SharedClose -> IO ()
closeIfUnclaimed shared@(SharedClose _ _ cell _) = do
 (status,_) <- readMVar cell
 case status of EndpointOpen -> closeShared shared; _ -> pure ()

-- Private deterministic test seam. It exposes no socket, fd or event action.
-- The public facade does not export this probe.
data WaitProbe = WaitProbe (TVar Bool) (TVar Bool)
newWaitProbe :: IO WaitProbe
newWaitProbe = WaitProbe <$> newTVarIO False <*> newTVarIO False
waitProbeRegistered :: WaitProbe -> STM ()
waitProbeRegistered (WaitProbe registered _) = do
 ready <- readTVar registered
 if ready then pure () else retry
releaseWaitProbe :: WaitProbe -> IO ()
releaseWaitProbe (WaitProbe _ released) = atomically (writeTVar released True)

-- A false marker means acquisition/unregistration was not proved complete.
-- The pin remains counted forever and the shared owner must quarantine it.
withPinnedSocket :: SharedClose -> (IORef Bool -> IO a) -> IO (Maybe a)
withPinnedSocket (SharedClose _ _ _ pins) action = mask $ \restore -> do
 safe <- newIORef True
 acquired <- atomically $ do
  (closing,n) <- readTVar pins
  if closing then pure False else writeTVar pins (False,n+1) >> pure True
 if not acquired then pure Nothing else
  (Just <$> restore (action safe)) `finally` do
    releasable <- readIORef safe
    if not releasable then pure () else atomically $ do
      (closing,n) <- readTVar pins
      writeTVar pins (closing,n-1)

-- The safety flag becomes true only after successful event unregistration.
-- Masking closes the registration/finalizer handoff against async exceptions.
waitPinnedSocket :: SharedClose -> IORef Bool -> Maybe WaitProbe -> STM reason -> IO (Either (Maybe reason) ())
waitPinnedSocket (SharedClose sock _ _ pins) safe probe ownerWake = mask $ \restore -> do
 writeIORef safe False
 S.withFdSocket sock $ \fd -> bracket (threadWaitReadSTM (fromIntegral fd))
  (\(_,unregister) -> unregister >> writeIORef safe True) $ \(readable,_) -> do
   case probe of
    Nothing -> pure ()
    Just (WaitProbe registered released) -> do
     atomically (writeTVar registered True)
     restore $ atomically $ do
      allowed <- readTVar released
      if allowed then pure () else retry
   restore $ atomically ((Left . Just <$> ownerWake) `orElse`
     (do (closing,_) <- readTVar pins; if closing then pure (Left Nothing) else retry) `orElse`
     (readable >> pure (Right ())))

activateIngress :: (IngressOwnerT ctx) -> IO ActivationResult
activateIngress = activateIngressWithHook (pure ())
-- Controlled private seam after Live is already published in the retained shell.
activateIngressWithHook :: IO () -> (IngressOwnerT ctx) -> IO ActivationResult
activateIngressWithHook afterPublication owner@(IngressOwner profile _ direction state _ configure _) = mask $ \restore -> do
 selected <- modifyMVar state $ \current@(State slot wasAccepted failure) -> case slot of
  Offered shared -> pure (State (Setup shared False) wasAccepted failure,Just shared)
  _ -> pure (current,Nothing)
 case selected of
  Nothing -> pure ActivationUnavailable
  Just shared@(SharedClose sock _ _ _) -> do
   result <- try (restore (configure sock >> C.newConfiguredChannelWith profile sock (case direction of FromElm -> C.ClientInbound; FromNative -> C.ServerInbound) (closeShared shared))) :: IO (Either SomeException C.Channel)
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

liveChannel :: (IngressOwnerT ctx) -> IO (Maybe C.Channel)
liveChannel (IngressOwner _ _ _ state _ _ _) = do
 selected <- withMVar state $ \(State slot _ _) -> pure $ case slot of
  Running shared channel -> Just (shared,channel)
  _ -> Nothing
 case selected of
  Just (SharedClose _ _ cell _,channel) -> do
   (status,_) <- readMVar cell
   pure (if status==EndpointOpen then Just channel else Nothing)
  Nothing -> pure Nothing

receiveIngress :: IngressOwner -> IO IngressResult
receiveIngress owner@(IngressOwner _ gateValue direction _ serial _ _) = mask $ \restore -> do
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
retireOnError :: (IngressOwnerT ctx) -> SomeException -> IO a
retireOnError owner original = do
 cleanup <- try (retireIngress owner) :: IO (Either SomeException OwnerStatus)
 throwPreferred original (case cleanup of Left e -> Left e; Right _ -> Right ())

enqueueIngress :: (IngressOwnerT ctx) -> Priority -> B.ByteString -> IO (Either ChannelError ())
enqueueIngress owner priority bytes = withLiveOperation owner (\channel -> C.enqueue channel priority bytes)
sendIngress :: (IngressOwnerT ctx) -> IO (Either ChannelError ())
sendIngress owner = withLiveOperation owner C.sendNext

-- Observation only: uncertain queued bytes never authorize retransmission.
retainedIngressFrames :: (IngressOwnerT ctx) -> IO [(Priority,B.ByteString)]
retainedIngressFrames (IngressOwner _ _ _ state _ _ _) = do
 selected <- withMVar state $ \(State slot _ _) -> pure $ case slot of
  Running _ channel -> Just channel
  Stopped _ channel -> channel
  _ -> Nothing
 case selected of Nothing -> pure []; Just channel -> C.retainedFrames channel

withLiveOperation :: (IngressOwnerT ctx) -> (C.Channel -> IO (Either ChannelError ())) -> IO (Either ChannelError ())
withLiveOperation owner action = mask $ \restore -> do
 result <- try (restore (do
  selected <- liveChannel owner
  case selected of Nothing -> pure (Left C.Closed); Just channel -> action channel)) :: IO (Either SomeException (Either ChannelError ()))
 case result of Left err -> retireOnError owner err; Right value -> pure value

retireIngress :: (IngressOwnerT ctx) -> IO OwnerStatus
retireIngress owner@(IngressOwner _ gateValue _ state _ _ _) = mask $ \_ -> do
 -- Mark retirement before gate closure to serialize against setup publication;
 -- the gate still closes before any live socket close is attempted.
 action <- uninterruptibleMask_ $ modifyMVar state $ \(State slot wasAccepted failure) -> case slot of
  NoSocket -> pure (State (Stopped Nothing Nothing) wasAccepted failure,Nothing)
  Offered shared -> pure (State (Stopped (Just shared) Nothing) wasAccepted failure,Just (closeShared shared))
  Setup shared _ -> pure (State (Setup shared True) wasAccepted failure,Nothing)
  Running shared channel -> pure (State (Stopped (Just shared) (Just channel)) wasAccepted failure,Just (do _ <- C.closeChannel channel; pure ()))
  Broken shared -> pure (State (Stopped (Just shared) Nothing) wasAccepted failure,Just (closeShared shared))
  Stopped saved channel -> pure (State (Stopped saved channel) wasAccepted failure,case channel of
   Just value -> Just (do _ <- C.closeChannel value; pure ())
   Nothing -> fmap closeIfUnclaimed saved)
 gateResult <- try (uninterruptibleMask_ (G.retire gateValue)) :: IO (Either SomeException GateStatus)
 -- A draining callback can still use its endpoint. Keep the exact owner and
 -- queued bytes; a later same-owner retire may close only after G.Retired.
 cleanup <- case gateResult of
  Right G.Retired -> case action of Nothing -> pure (Right ()); Just closeAction -> try closeAction
  _ -> pure (Right ())
 case gateResult of
  Left err -> throwPreferred err cleanup
  Right _ -> case cleanup of Left err -> throwIO (err :: SomeException); Right () -> ingressStatus owner

ingressStatus :: (IngressOwnerT ctx) -> IO OwnerStatus
ingressStatus (IngressOwner _ gateValue _ state _ _ _) = do
 (p,wasAccepted,failure,shared) <- withMVar state $ \(State slot a f) -> pure $ case slot of
  NoSocket -> (OwnerEmpty,a,f,Nothing)
  Offered s -> (OwnerPending,a,f,Just s)
  Setup s False -> (OwnerActivating,a,f,Just s)
  Setup s True -> (OwnerRetiring,a,f,Just s)
  Running s _ -> (OwnerLive,a,f,Just s)
  Broken s -> (OwnerFailed,a,f,Just s)
  Stopped s _ -> (OwnerRetired,a,f,s)
 (closeState,closeErr) <- case shared of Nothing -> pure (Nothing,Nothing); Just (SharedClose _ _ cell _) -> do (c,e) <- readMVar cell; pure (Just c,e)
 gateState <- G.gateStatus gateValue
 let actualPhase
      | p==OwnerLive && closeState/=Just EndpointOpen = OwnerFailed
      | p==OwnerRetired && closeState==Just EndpointUncertain = OwnerFailed
      | p==OwnerRetired && (gateState/=G.Retired || closeState==Just EndpointClosing || closeState==Just EndpointOpen) = OwnerRetiring
      | otherwise = p
 pure (OwnerStatus actualPhase wasAccepted gateState closeState failure closeErr)
ingressRejections :: (IngressOwnerT ctx) -> IO [Reason]
ingressRejections (IngressOwner _ gateValue _ _ _ _ _) = G.rejectionReasons gateValue

-- This owner is allocated before a socket is offered. Its reader and any
-- quarantined ancillary descriptors remain reachable even after socket close.
data CredentialIngressT ctx = CredentialIngress (IngressOwnerT ctx) P.CredentialReader
type CredentialIngress = CredentialIngressT ()
data CredentialIngressResult refusal = CredentialDelivered | CredentialRejected Reason
 | CredentialFrameRejected (C.CredentialFrameError refusal) | CredentialAdmissionRejected refusal
 | CredentialNotLive deriving (Eq,Show)

newCredentialIngress :: IngressBinding -> Direction -> (CheckedClient -> IO ()) -> (CheckedServer -> IO ()) -> IO CredentialIngress
newCredentialIngress = newCredentialIngressWithProfile nativeProfile
newDesktopCredentialIngress :: IngressBinding -> Direction -> (CheckedClient -> IO ()) -> (CheckedServer -> IO ()) -> IO CredentialIngress
newDesktopCredentialIngress = newCredentialIngressWithProfile desktopProfile
-- One owner, same Gate; callback context and checked handlers are fixed at construction.
newDesktopCredentialIngressWithContext :: IngressBinding -> Direction -> (ctx -> CheckedClient -> IO ()) -> (ctx -> CheckedServer -> IO ()) -> IO (CredentialIngressT ctx)
newDesktopCredentialIngressWithContext bindingValue direction client server = do
 reader <- P.newCredentialReader
 owner <- newIngressOwnerWithProfileContext desktopProfile (pure ()) bindingValue direction client server
   (\socket -> F.configureSocketFlags socket >> P.enablePassCredentials socket) S.close
 pure (CredentialIngress owner reader)
newCredentialIngressWithProfile :: CodecProfile -> IngressBinding -> Direction -> (CheckedClient -> IO ()) -> (CheckedServer -> IO ()) -> IO CredentialIngress
newCredentialIngressWithProfile profile bindingValue direction client server = do
 reader <- P.newCredentialReader
 owner <- newIngressOwnerWithProfile profile (pure ()) bindingValue direction client server
   (\socket -> F.configureSocketFlags socket >> P.enablePassCredentials socket) S.close
 pure (CredentialIngress owner reader)
-- Same-package source-fixture seam. The public facade cannot replace a reader.
newCredentialIngressWithReaderForTest :: P.CredentialReader -> IngressBinding -> Direction -> (CheckedClient -> IO ()) -> (CheckedServer -> IO ()) -> IO CredentialIngress
newCredentialIngressWithReaderForTest reader bindingValue direction client server = do
 owner <- newIngressOwnerWithHooks bindingValue direction client server
   (\socket -> F.configureSocketFlags socket >> P.enablePassCredentials socket) S.close
 pure (CredentialIngress owner reader)
transferCredentialSocket :: (CredentialIngressT ctx) -> S.Socket -> IO OfferResult
transferCredentialSocket (CredentialIngress owner _) = transferSocket owner
activateCredentialIngress :: (CredentialIngressT ctx) -> IO ActivationResult
activateCredentialIngress (CredentialIngress owner _) = activateIngress owner
credentialIngressStatus :: (CredentialIngressT ctx) -> IO (OwnerStatus,P.ReaderStatus)
credentialIngressStatus (CredentialIngress owner reader) = (,) <$> ingressStatus owner <*> P.credentialReaderStatus reader
retireCredentialIngress :: (CredentialIngressT ctx) -> IO OwnerStatus
retireCredentialIngress (CredentialIngress owner _) = retireIngress owner
enqueueCredentialIngress :: (CredentialIngressT ctx) -> Priority -> B.ByteString -> IO (Either ChannelError ())
enqueueCredentialIngress (CredentialIngress owner _) = enqueueIngress owner
sendCredentialIngress :: (CredentialIngressT ctx) -> IO (Either ChannelError ())
sendCredentialIngress (CredentialIngress owner _) = sendIngress owner
retainedCredentialIngressFrames :: (CredentialIngressT ctx) -> IO [(Priority,B.ByteString)]
retainedCredentialIngressFrames (CredentialIngress owner _) = retainedIngressFrames owner

-- The same serial admission and channel read gate serve legacy and credential
-- paths. Scope admission encloses the actual checked gate dispatch and handler;
-- no credential or checked envelope is an effect or native capability.
receiveCredentialIngress :: forall refusal. CredentialIngress -> CredentialGuard refusal -> IO (CredentialIngressResult refusal)
receiveCredentialIngress = receiveCredentialIngressWithIdle Nothing

-- The original session deadline is supplied by the retained bootstrap owner.
-- Native profile and the first receive keep their original immediate frame D.
receiveDesktopCredentialIngressAfterIdle :: Integer -> CredentialIngress -> CredentialGuard refusal -> IO (CredentialIngressResult refusal)
receiveDesktopCredentialIngressAfterIdle deadline = receiveCredentialIngressWithIdle (Just deadline)

receiveCredentialIngressWithIdle :: forall refusal. Maybe Integer -> CredentialIngress -> CredentialGuard refusal -> IO (CredentialIngressResult refusal)
receiveCredentialIngressWithIdle idleDeadline (CredentialIngress owner@(IngressOwner profile gateValue direction _ serial _ _) reader) guard = mask $ \restore -> do
 acquired <- tryTakeMVar serial
 case acquired of
  Nothing -> pure (CredentialFrameRejected (C.CredentialTransport C.Busy))
  Just () -> (do
   selected <- try (restore (liveChannel owner)) :: IO (Either SomeException (Maybe C.Channel))
   case selected of
    Left err -> retireOnError owner err
    Right Nothing -> pure CredentialNotLive
    Right (Just channel) -> do
     readResult <- try (restore (case idleDeadline of
       Just deadline | profile == desktopProfile -> C.receiveCredentialFrameAfterIdle deadline reader guard channel
       _ -> C.receiveCredentialFrame reader guard channel)) :: IO (Either SomeException (Either (C.CredentialFrameError refusal) (B.ByteString,Integer,P.PeerCredential)))
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

-- InterruptedFrame includes any consumed-but-unadmitted frame, even a complete one.
data PersistentIngressResult refusal reason
 = PersistentOutcome (CredentialIngressResult refusal) | PersistentOwnerWake reason
 | PersistentInterruptedFrame reason | PersistentOwnerWakeDraining reason
 | PersistentFrameDraining reason | PersistentCloseUncertain (CredentialIngressResult refusal)
 | PersistentGateDraining (CredentialIngressResult refusal)
 deriving (Eq,Show)

-- Internal application-only preparation route. First receive retains the 5s
-- frame budget; later idle waits mint the frame deadline only after readiness.
-- The supplied guard MUST be the private owner scope and serialize final
-- callback admission with owner stop. This function cannot establish pidfd or
-- birth identity; an after-fragment stop race needs that actual owner's guard.
receivePersistentCredentialIngress :: forall refusal reason. Bool -> STM reason -> CredentialIngress -> (C.FrameDeadline -> CredentialGuard refusal)
 -> IO (PersistentIngressResult refusal reason)
receivePersistentCredentialIngress = receivePersistentCredentialIngressWithProbe Nothing

-- Same-package test-only probe path; production facade never exports it.
receivePersistentCredentialIngressWithProbe :: forall refusal reason. Maybe WaitProbe -> Bool -> STM reason -> CredentialIngress -> (C.FrameDeadline -> CredentialGuard refusal)
 -> IO (PersistentIngressResult refusal reason)
receivePersistentCredentialIngressWithProbe probe afterDelivered ownerWake (CredentialIngress owner@(IngressOwner profile gateValue direction state serial _ _) reader) guardFor = mask $ \restore -> do
 acquired <- tryTakeMVar serial
 case acquired of
  Nothing -> pure (PersistentOutcome (CredentialFrameRejected (C.CredentialTransport C.Busy)))
  Just () -> (do
   chosen <- withMVar state $ \(State slot _ _) -> pure $ case slot of
    Running shared channel | profile == desktopProfile -> Just (shared,channel)
    _ -> Nothing
   case chosen of
    Nothing -> pure (PersistentOutcome CredentialNotLive)
    Just (shared,channel) -> do
     wakeRef <- newIORef Nothing
     frameStarted <- newIORef False
     let retireOnWake reason = do
          partial <- readIORef frameStarted
          retired <- try (G.retire gateValue) :: IO (Either SomeException GateStatus)
          case retired of
           Left failure -> retireOnError owner failure
           Right G.Retired -> pure (if partial then PersistentInterruptedFrame reason else PersistentOwnerWake reason)
           Right _ -> pure (if partial then PersistentFrameDraining reason else PersistentOwnerWakeDraining reason)
         failAndRetire outcome = do
          retired <- try (G.retire gateValue) :: IO (Either SomeException GateStatus)
          case retired of
           Left failure -> retireOnError owner failure
           Right G.Retired -> do
            closed <- try (C.closeChannel channel) :: IO (Either SomeException C.CloseResult)
            case closed of
             Left failure -> retireOnError owner failure
             Right C.ClosedNow -> pure (PersistentOutcome outcome)
             Right C.AlreadyClosed -> pure (PersistentOutcome outcome)
             Right C.CloseFailed -> pure (PersistentCloseUncertain outcome)
             Right C.CloseInProgress -> pure (PersistentCloseUncertain outcome)
           Right _ -> pure (PersistentGateDraining outcome)
         waitOwned safe = do
          wake <- waitPinnedSocket shared safe probe ownerWake
          case wake of
           Left reason -> writeIORef wakeRef reason >> pure False
           Right () -> pure True
         readOwned safe = if afterDelivered
          then C.receiveCredentialFrameWithOwnedFrameGuard True (waitOwned safe) (writeIORef frameStarted True) reader guardFor channel
          else do
           ready <- atomically ((Just <$> ownerWake) `orElse` pure Nothing)
           case ready of
            Just reason -> writeIORef wakeRef (Just reason) >> pure (Left (C.CredentialTransport C.Closed))
            Nothing -> C.receiveCredentialFrameWithOwnedFrameGuard False (waitOwned safe) (writeIORef frameStarted True) reader guardFor channel
     received <- try (restore (withPinnedSocket shared readOwned)) :: IO (Either SomeException (Maybe (Either (C.CredentialFrameError refusal) (B.ByteString,C.FrameDeadline,P.PeerCredential))))
     case received of
      Left err -> retireOnError owner err
      Right Nothing -> pure (PersistentOutcome CredentialNotLive)
      Right (Just (Left err)) -> do
       reason <- readIORef wakeRef
       case reason of
        Just why -> retireOnWake why
        Nothing -> failAndRetire (CredentialFrameRejected err)
      Right (Just (Right (bytes,deadline,credential))) -> do
       beforeAdmission <- atomically ((Just <$> ownerWake) `orElse` pure Nothing)
       case beforeAdmission of
        Just why -> retireOnWake why
        Nothing -> do
         admission <- try (restore (withCredentialAdmission (guardFor deadline) credential (G.dispatchUntil gateValue direction bytes (C.frameDeadlineNs deadline)))) :: IO (Either SomeException (Either refusal (Either Reason ())))
         case admission of
          Left err -> retireOnError owner err
          Right (Left refusal) -> failAndRetire (CredentialAdmissionRejected refusal)
          Right (Right (Left reason)) -> failAndRetire (CredentialRejected reason)
          Right (Right (Right ())) -> pure (PersistentOutcome CredentialDelivered)) `finally` putMVar serial ()

-- Caller-owned frame admission: readiness precedes the lexical frame scope.
-- first frame no idle wait is introduced. The scope encloses the actual frame
-- read, credential guard and checked dispatch; guardFor receives the same token
-- throughout. No native grant, owner-death proof, or close receipt is implied.
-- A scope refusal is tagged with whether its continuation was entered; caller
-- must retire the owner and preserve possible post-entry Unknown/no replay.
receivePersistentCredentialIngressScoped
 :: forall token scopeErr refusal reason.
    Bool -> STM reason -> CredentialIngressT (token,C.FrameDeadline)
 -> (forall a. (token -> IO a) -> IO (Either scopeErr a))
 -> (token -> C.FrameDeadline -> CredentialGuard refusal)
 -> IO (Either (Bool,scopeErr) (PersistentIngressResult refusal reason))
receivePersistentCredentialIngressScoped afterDelivered ownerWake
 (CredentialIngress owner@(IngressOwner profile gateValue direction state serial _ _) reader)
 enterScope guardFor = mask $ \restore -> do
 acquired <- tryTakeMVar serial
 case acquired of
  Nothing -> pure (Right (PersistentOutcome (CredentialFrameRejected (C.CredentialTransport C.Busy))))
  Just () -> (do
   chosen <- withMVar state $ \(State slot _ _) -> pure $ case slot of
    Running shared channel | profile == desktopProfile -> Just (shared,channel)
    _ -> Nothing
   case chosen of
    Nothing -> pure (Right (PersistentOutcome CredentialNotLive))
    Just (shared,channel) -> do
     wakeRef <- newIORef Nothing
     frameStarted <- newIORef False
     let retireOnWake reason = do
          partial <- readIORef frameStarted
          retired <- try (G.retire gateValue) :: IO (Either SomeException GateStatus)
          case retired of
           Left failure -> retireOnError owner failure
           Right G.Retired -> pure (if partial then PersistentInterruptedFrame reason else PersistentOwnerWake reason)
           Right _ -> pure (if partial then PersistentFrameDraining reason else PersistentOwnerWakeDraining reason)
         failAndRetire outcome = do
          retired <- try (G.retire gateValue) :: IO (Either SomeException GateStatus)
          case retired of
           Left failure -> retireOnError owner failure
           Right G.Retired -> do
            closed <- try (C.closeChannel channel) :: IO (Either SomeException C.CloseResult)
            case closed of
             Left failure -> retireOnError owner failure
             Right C.ClosedNow -> pure (PersistentOutcome outcome)
             Right C.AlreadyClosed -> pure (PersistentOutcome outcome)
             Right C.CloseFailed -> pure (PersistentCloseUncertain outcome)
             Right C.CloseInProgress -> pure (PersistentCloseUncertain outcome)
           Right _ -> pure (PersistentGateDraining outcome)
         waitOwned safe = do
          wake <- waitPinnedSocket shared safe Nothing ownerWake
          case wake of
           Left reason -> writeIORef wakeRef reason >> pure False
           Right () -> pure True
         runScoped token = do
          received <- try (restore (withPinnedSocket shared (\safe ->
            C.receiveCredentialFrameWithOwnedFrameGuard False (waitOwned safe)
              (writeIORef frameStarted True) reader (guardFor token) channel)))
            :: IO (Either SomeException (Maybe (Either (C.CredentialFrameError refusal) (B.ByteString,C.FrameDeadline,P.PeerCredential))))
          case received of
           Left err -> retireOnError owner err
           Right Nothing -> pure (PersistentOutcome CredentialNotLive)
           Right (Just (Left err)) -> do
            reason <- readIORef wakeRef
            case reason of
             Just why -> retireOnWake why
             Nothing -> failAndRetire (CredentialFrameRejected err)
           Right (Just (Right (bytes,deadline,credential))) -> do
            beforeAdmission <- atomically ((Just <$> ownerWake) `orElse` pure Nothing)
            case beforeAdmission of
             Just why -> retireOnWake why
             Nothing -> do
              admission <- try (restore (withCredentialAdmission (guardFor token deadline) credential
                (G.dispatchUntilContext gateValue (token,deadline) direction bytes (C.frameDeadlineNs deadline))))
                :: IO (Either SomeException (Either refusal (Either Reason ())))
              case admission of
               Left err -> retireOnError owner err
               Right (Left refusal) -> failAndRetire (CredentialAdmissionRejected refusal)
               Right (Right (Left reason)) -> failAndRetire (CredentialRejected reason)
               Right (Right (Right ())) -> pure (PersistentOutcome CredentialDelivered)
     -- Holding a socket pin only while awaiting readiness ensures event-manager
     -- unregister happens before it is released; no callback permit is held.
     ready <- if afterDelivered
      then try (restore (withPinnedSocket shared waitOwned)) :: IO (Either SomeException (Maybe Bool))
      else do
       stopped <- atomically ((Just <$> ownerWake) `orElse` pure Nothing)
       case stopped of
        Just why -> writeIORef wakeRef (Just why) >> pure (Right (Just False))
        Nothing -> pure (Right (Just True))
     case ready of
      Left err -> Right <$> retireOnError owner err
      Right Nothing -> pure (Right (PersistentOutcome CredentialNotLive))
      Right (Just False) -> do
       why <- readIORef wakeRef
       case why of
        Just reason -> Right <$> retireOnWake reason
        Nothing -> pure (Right (PersistentOutcome CredentialNotLive))
      Right (Just True) -> do
       entered <- newIORef False
       outcome <- try (restore (enterScope (\token -> writeIORef entered True >> runScoped token))) :: IO (Either SomeException (Either scopeErr (PersistentIngressResult refusal reason)))
       case outcome of
        Left err -> Right <$> retireOnError owner err
        Right (Right result) -> pure (Right result)
        Right (Left failure) -> do
         wasEntered <- readIORef entered
         pure (Left (wasEntered,failure))) `finally` putMVar serial ()

-- Actual opaque owner session supplies the synchronous wake and frame
-- brackets. No arbitrary scope provider crosses the public facade. A wake
-- bracket can fail after work ran; mark that outcome conservatively unknown.
-- Every Left requires caller-owned retirement; never replay a possibly entered
-- frame. Owner callback exceptions remain owner failures.
receivePersistentCredentialIngressOwned
 :: forall refusal.
    Bool -> Persistent.LiveSession
 -> CredentialIngressT (Persistent.LiveFrameAdmission,C.FrameDeadline)
 -> (Persistent.LiveFrameAdmission -> C.FrameDeadline -> CredentialGuard refusal)
 -> IO (Either (Bool,ToolError) (PersistentIngressResult refusal Persistent.LiveWakeReason))
receivePersistentCredentialIngressOwned afterDelivered session ingress guardFor = do
 outcome <- Persistent.withLiveSessionWakeSTM session $ \wake ->
  receivePersistentCredentialIngressScoped afterDelivered wake ingress
   (Persistent.withLiveFrameAdmission session) guardFor
 case outcome of
  Left err -> pure (Left (True,err))
  Right result -> pure result

-- WrittenLocally says only sendAll completed before the caller's immutable D;
-- it does not acknowledge peer receipt, callback retirement, or native work.
-- Unknown is never a reason to retry or reuse the same queued operation.
data PersistentSendResult = WrittenLocally | SendRefused ChannelError | SendUnknown ChannelError
 deriving (Eq,Show)

-- Private runtime owner must wrap this call in the actual active frame/action
-- authority, supply its already-established monotonic action D, and map stop
-- after entry to Unknown. No authority is created here or read from the wire.
-- All application-path writers must use this scoped entry, never sendIngress.
sendPersistentCredentialIngress :: Integer -> CredentialIngressT ctx -> IO PersistentSendResult
sendPersistentCredentialIngress = sendPersistentCredentialIngressWithHook (pure ())

-- Same-package fixture hook only. Public callers cannot inject this hook.
sendPersistentCredentialIngressWithHook :: IO () -> Integer -> CredentialIngressT ctx -> IO PersistentSendResult
sendPersistentCredentialIngressWithHook beforeSend = sendPersistentCredentialIngressWithHooks beforeSend (pure ())

-- The after-write hook is private to tests; production supplies no-op hooks.
sendPersistentCredentialIngressWithHooks :: IO () -> IO () -> Integer -> CredentialIngressT ctx -> IO PersistentSendResult
sendPersistentCredentialIngressWithHooks beforeSend afterWrite absoluteD (CredentialIngress owner@(IngressOwner profile gateValue _ state _ _ _) _) = mask $ \restore -> do
 selected <- withMVar state $ \(State slot _ _) -> pure $ case slot of
  Running shared channel | profile == desktopProfile -> Just (shared,channel)
  _ -> Nothing
 case selected of
  Nothing -> pure (SendRefused C.Closed)
  Just (shared,channel) -> do
   result <- try (restore (withPinnedSocket shared $ \safe ->
    C.sendNextPersistent absoluteD (writeIORef safe False) beforeSend afterWrite (writeIORef safe True) channel)) :: IO (Either SomeException (Maybe (Either ChannelError ())))
   case result of
    Left err -> retireOnError owner err
    Right Nothing -> pure (SendRefused C.Closed)
    Right (Just (Right ())) -> pure WrittenLocally
    Right (Just (Left C.OutputUncertain)) -> do
     -- No retry: failed/unknown send retains any unsafe pin. Retiring the gate
     -- is not a drain receipt and must not itself authorize a close.
     retired <- try (G.retire gateValue) :: IO (Either SomeException GateStatus)
     case retired of Left err -> retireOnError owner err
                     Right _ -> pure (SendUnknown C.OutputUncertain)
    Right (Just (Left reason)) -> pure (SendRefused reason)
