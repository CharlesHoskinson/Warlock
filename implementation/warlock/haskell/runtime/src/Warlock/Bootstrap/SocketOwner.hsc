{-# LANGUAGE CPP #-}
{-# LANGUAGE ForeignFunctionInterface #-}
-- Internal ownership: each endpoint and transfer has its own sticky state.
module Warlock.Bootstrap.SocketOwner
 (SocketOwner, newSocketOwner, acquireSocketOwner, withEndpoints, withEndpointsFault, Fault(..), socketStatus, claimTransfer, retireSocketOwner
#ifdef WARLOCK_SOCKETOWNER_TESTING
 , PublicationProbe(..), holdStateForTest, acquireSocketOwnerProbed, withEndpointsProbed, custodyForTest, rawPairOpenForTest
#endif
 ) where
#include <sys/types.h>
#include <sys/socket.h>
#include <fcntl.h>
import Control.Concurrent.MVar
import Control.Exception (SomeException, SomeAsyncException, fromException, mask_, uninterruptibleMask_, onException, throwIO, try)
import Data.Bits ((.|.))
import Data.IORef (IORef, atomicWriteIORef)
import Foreign (Ptr, allocaArray, peekElemOff)
import Foreign.C (CInt(..), throwErrnoIfMinus1)
import System.IO (Handle,hClose)
import System.Posix.IO (closeFd,fdToHandle)
#ifdef WARLOCK_SOCKETOWNER_TESTING
import System.Posix.Files (getFdStatus)
import Control.Exception (IOException)
#endif
import System.Posix.Types (Fd(..))
import qualified Network.Socket as S
import Warlock.Protocol.Ingress (OfferResult(..), ActivationResult(..), OwnerStatus(..), Phase(..), EndpointState(..))
import Warlock.Protocol.CredentialIngress (CredentialIngress, transferCredentialSocket, activateCredentialIngress, retireCredentialIngress, credentialIngressStatus, ReaderStatus(..))
foreign import ccall unsafe "socketpair" c_pair :: CInt -> CInt -> CInt -> Ptr CInt -> IO CInt
foreign import ccall unsafe "fcntl" c_fcntl :: CInt -> CInt -> CInt -> IO CInt

data Host = HEmpty | HRaw Fd | HMoving Fd | HSocket S.Socket | HAdopting S.Socket CredentialIngress | HChannel CredentialIngress | HClosing | HClosed | HUnknown (Maybe Fd) (Maybe S.Socket) (Maybe CredentialIngress)
data Peer = PEmpty | PRaw Fd | PClosing | PClosed | PUnknown Fd
data Transfer = TEmpty | TConverting Fd | THandle Handle | TTransferred | TClosing | TClosed | TUnknown (Maybe Fd) (Maybe Handle)
data State = State Host Peer Transfer Bool
newtype SocketOwner = SocketOwner (MVar State)
-- Internal source-control seam: the before action runs before acquisition,
-- and the marker is a nonblocking atomic write after the kernel result. No
-- callback runs under the state lock or inside the protected publication.
data PublicationProbe = PublicationProbe (IO ()) (IORef Bool)
beforeProbe :: Maybe PublicationProbe -> IO ()
beforeProbe Nothing = pure ()
beforeProbe (Just (PublicationProbe before _)) = before
markProbe :: Maybe PublicationProbe -> IO ()
markProbe Nothing = pure ()
markProbe (Just (PublicationProbe _ marker)) = atomicWriteIORef marker True
#ifdef WARLOCK_SOCKETOWNER_TESTING
holdStateForTest :: SocketOwner -> MVar () -> MVar () -> IO ()
holdStateForTest (SocketOwner state) entered release = withMVar state $ \_ -> putMVar entered () >> takeMVar release
-- Snapshot only: never closes or grants a borrowed descriptor.
custodyForTest :: SocketOwner -> IO (Bool,Bool,Bool)
custodyForTest (SocketOwner state) = withMVar state $ \(State host peer transfer _) -> pure
  (case host of HRaw _ -> True; HSocket _ -> True; HAdopting _ _ -> True; HChannel _ -> True; HUnknown _ _ _ -> True; _ -> False,
   case peer of PRaw _ -> True; PUnknown _ -> True; _ -> False,
   case transfer of TConverting _ -> True; THandle _ -> True; TUnknown _ _ -> True; TTransferred -> True; _ -> False)
-- Only call in the quiescent fixture after the worker has exited; no close or
-- ownership transfer races this observation. It does not export descriptors.
rawPairOpenForTest :: SocketOwner -> IO Bool
rawPairOpenForTest (SocketOwner state) = do
 pair <- withMVar state $ \(State host peer _ _) -> pure $ case (host,peer) of
   (HRaw first,PRaw second) -> Just (first,second)
   _ -> Nothing
 case pair of
  Nothing -> pure False
  Just (first,second) -> do
   result <- try (getFdStatus first >> getFdStatus second >> pure ()) :: IO (Either IOException ())
   pure $ either (const False) (const True) result
#endif
-- Private fixture fault points always close the resource before reporting an
-- uncertain post-close outcome; they cannot skip close on the real path.
data Fault = NoFault | HostPostClose | TransferPostClose deriving (Eq,Show)
socketStatus :: SocketOwner -> IO (Bool,Bool,Bool)
socketStatus (SocketOwner state) = withMVar state $ \(State h p t _) -> pure
  ((case h of HEmpty -> True; HClosed -> True; _ -> False),
   (case p of PEmpty -> True; PClosed -> True; _ -> False),
   (case t of TEmpty -> True; TClosed -> True; TTransferred -> True; _ -> False))
newSocketOwner :: IO SocketOwner
newSocketOwner = SocketOwner <$> newMVar (State HEmpty PEmpty TEmpty False)

acquireSocketOwner :: SocketOwner -> IO Bool
acquireSocketOwner owner = acquireSocketOwnerProbed owner Nothing
acquireSocketOwnerProbed :: SocketOwner -> Maybe PublicationProbe -> IO Bool
acquireSocketOwnerProbed (SocketOwner state) probe = mask_ $ do
  admitted <- uninterruptibleMask_ $ modifyMVar state $ \s@(State host peer transfer busy) -> case (host,peer,transfer,busy) of
    (HEmpty,PEmpty,TEmpty,False) -> pure (State host peer transfer True,True)
    _ -> pure (s,False)
  if not admitted then pure False else (beforeProbe probe `onException` clearBusy state) >> allocaArray 2 (\out -> do
    result <- try (throwErrnoIfMinus1 "socketpair" (c_pair #{const AF_UNIX} (#{const SOCK_STREAM} .|. #{const SOCK_CLOEXEC}) 0 out)) :: IO (Either SomeException CInt)
    case result of
      Left e -> do
        uninterruptibleMask_ $ modifyMVar_ state (const (pure (State HEmpty PEmpty TEmpty False)))
        case fromException e :: Maybe SomeAsyncException of Just _ -> throwIO e; Nothing -> pure False
      Right _ -> do
        a <- peekElemOff out 0
        b <- peekElemOff out 1
        markProbe probe
        uninterruptibleMask_ $ modifyMVar_ state (const (pure (State (HRaw (Fd a)) (PRaw (Fd b)) TEmpty False)))
        pure True)

-- The selected peer remains pair-owned. The callback transfers only the fresh
-- duplicate to ParentExec and must claimTransfer immediately after newOwner.
withEndpoints :: SocketOwner -> CredentialIngress -> (Fd -> Handle -> IO a) -> IO (Maybe a)
withEndpoints = withEndpointsFault NoFault
-- Test-only seam in this internal module; production calls withEndpoints.
withEndpointsFault :: Fault -> SocketOwner -> CredentialIngress -> (Fd -> Handle -> IO a) -> IO (Maybe a)
withEndpointsFault fault owner ingress action = withEndpointsProbed fault owner ingress Nothing Nothing action
withEndpointsProbed :: Fault -> SocketOwner -> CredentialIngress -> Maybe PublicationProbe -> Maybe PublicationProbe -> (Fd -> Handle -> IO a) -> IO (Maybe a)
withEndpointsProbed fault (SocketOwner state) ingress offerProbe dupProbe action = mask_ $ do
  host <- uninterruptibleMask_ $ modifyMVar state $ \s@(State h p t busy) -> case (h,p,t,busy) of
    (HRaw fd,PRaw _,TEmpty,False) -> pure (State (HMoving fd) p t True,Just fd)
    _ -> pure (s,Nothing)
  case host of
    Nothing -> pure Nothing
    Just (Fd fd) -> do
      wrapped <- try (S.mkSocket fd) :: IO (Either SomeException S.Socket)
      case wrapped of
        Left e -> failHost state e
        Right sock -> do
          uninterruptibleMask_ $ modifyMVar_ state $ \(State _ p t _) -> pure (State (HSocket sock) p t True)
          uninterruptibleMask_ $ modifyMVar_ state $ \(State _ p t _) -> pure (State (HAdopting sock ingress) p t True)
          beforeProbe offerProbe `onException` clearBusy state
          offered <- try (if fault == HostPostClose
            then S.close sock >> ioError (userError "injected host post-close")
            else transferCredentialSocket ingress sock) :: IO (Either SomeException OfferResult)
          case offered of
            Left e -> failHost state e
            Right OfferRefused -> do
              uninterruptibleMask_ $ modifyMVar_ state $ \(State _ p t _) -> pure (State (HSocket sock) p t False)
              pure Nothing
            Right OfferAccepted -> do
              markProbe offerProbe
              -- Offer publication transfers the sole close right. Record the
              -- ingress owner before activation, which may fail or be interrupted.
              uninterruptibleMask_ $ modifyMVar_ state $ \(State _ p t _) -> pure (State (HChannel ingress) p t True)
              activated <- try (activateCredentialIngress ingress) :: IO (Either SomeException ActivationResult)
              case activated of
                Left e -> clearBusy state >> rethrow e >> pure Nothing
                Right ActivationLive -> runPeer fault state ingress dupProbe action
                Right _ -> clearBusy state >> pure Nothing

runPeer :: Fault -> MVar State -> CredentialIngress -> Maybe PublicationProbe -> (Fd -> Handle -> IO a) -> IO (Maybe a)
runPeer fault state ingress probe action = do
              peer <- uninterruptibleMask_ $ modifyMVar state $ \s@(State _ p t _) -> case p of
                PRaw f -> pure (State (HChannel ingress) p t True,Just f)
                _ -> pure (s,Nothing)
              case peer of
                Nothing -> clearBusy state >> pure Nothing
                Just selected@(Fd child) -> do
                  beforeProbe probe `onException` clearBusy state
                  copied <- try (throwErrnoIfMinus1 "F_DUPFD_CLOEXEC" (c_fcntl child #{const F_DUPFD_CLOEXEC} 3)) :: IO (Either SomeException CInt)
                  case copied of
                    Left e -> clearBusy state >> rethrow e >> pure Nothing
                    Right n -> do
                      let duplicate = Fd n
                      markProbe probe
                      uninterruptibleMask_ $ modifyMVar_ state $ \(State h p _ _) -> pure (State h p (TConverting duplicate) True)
                      converted <- try (do
                        h <- fdToHandle duplicate
                        if fault == TransferPostClose then hClose h >> ioError (userError "injected transfer post-close") else pure h) :: IO (Either SomeException Handle)
                      case converted of
                        Left e -> do
                          uninterruptibleMask_ $ modifyMVar_ state $ \(State h p _ _) -> pure (State h p (TUnknown (Just duplicate) Nothing) False)
                          rethrow e
                          pure Nothing
                        Right handle -> do
                          uninterruptibleMask_ $ modifyMVar_ state $ \(State h p _ _) -> pure (State h p (THandle handle) False)
                          Just <$> action selected handle

claimTransfer :: SocketOwner -> IO Bool
claimTransfer (SocketOwner state) = mask_ $ uninterruptibleMask_ $ modifyMVar state $ \s@(State h p t busy) -> case t of
  THandle _ | not busy -> pure (State h p TTransferred False,True)
  _ -> pure (s,False)

clearBusy :: MVar State -> IO ()
clearBusy state = uninterruptibleMask_ $ modifyMVar_ state $ \(State h p t _) -> pure (State h p t False)
failHost :: MVar State -> SomeException -> IO (Maybe a)
failHost state e = do
  uninterruptibleMask_ $ modifyMVar_ state $ \(State old p t _) -> pure (State (case old of
    HMoving fd -> HUnknown (Just fd) Nothing Nothing
    HAdopting sock candidate -> HUnknown Nothing (Just sock) (Just candidate)
    _ -> HUnknown Nothing Nothing Nothing) p t False)
  rethrow e
  pure Nothing
rethrow :: SomeException -> IO ()
rethrow e = case fromException e :: Maybe SomeAsyncException of Just _ -> throwIO e; Nothing -> pure ()

-- Each resource is independently removed from shared state before its one
-- cleanup attempt. I/O occurs outside the MVar and failed closes become sticky.
retireSocketOwner :: SocketOwner -> IO Bool
retireSocketOwner (SocketOwner state) = mask_ $ do
  (hostOk,hostError) <- closeHost state
  (peerOk,peerError) <- closePeer state
  (transferOk,transferError) <- closeTransfer state
  case [e | Just e <- [hostError,peerError,transferError], Just _ <- [fromException e :: Maybe SomeAsyncException]] of
    e:_ -> throwIO e
    [] -> pure (hostOk && peerOk && transferOk)

closeHost :: MVar State -> IO (Bool,Maybe SomeException)
closeHost state = do
  picked <- uninterruptibleMask_ $ modifyMVar state $ \s@(State h p t busy) -> case (h,busy) of
    (HRaw fd,False) -> pure (State HClosing p t False,Just (Left fd))
    (HSocket sock,False) -> pure (State HClosing p t False,Just (Right (Left sock)))
    (HChannel channel,False) -> pure (State HClosing p t False,Just (Right (Right channel)))
    _ -> pure (s,Nothing)
  case picked of
    Nothing -> withMVar state $ \(State h _ _ _) -> pure ((case h of HEmpty -> True; HClosed -> True; _ -> False),Nothing)
    Just item -> do
      result <- try $ case item of
        Left fd -> closeFd fd >> pure True
        Right (Left sock) -> S.close sock >> pure True
        Right (Right owner) -> do
          _ <- retireCredentialIngress owner
          (report,reader) <- credentialIngressStatus owner
          pure (phase report == OwnerRetired && endpoint report == Just EndpointConfirmed && reader == ReaderReady)
      let ok = either (const False) id (result :: Either SomeException Bool)
      let uncertain = case item of
            Left fd -> HUnknown (Just fd) Nothing Nothing
            Right (Left sock) -> HUnknown Nothing (Just sock) Nothing
            Right (Right channel) -> HUnknown Nothing Nothing (Just channel)
      uninterruptibleMask_ $ modifyMVar_ state $ \(State _ p t b) -> pure (State (if ok then HClosed else uncertain) p t b)
      pure (ok,either Just (const Nothing) result)

closePeer :: MVar State -> IO (Bool,Maybe SomeException)
closePeer state = do
  picked <- uninterruptibleMask_ $ modifyMVar state $ \s@(State h p t busy) -> case (p,busy) of
    (PRaw fd,False) -> pure (State h PClosing t False,Just fd)
    _ -> pure (s,Nothing)
  case picked of
    Nothing -> withMVar state $ \(State _ p _ _) -> pure ((case p of PEmpty -> True; PClosed -> True; _ -> False),Nothing)
    Just fd -> do
      result <- try (closeFd fd) :: IO (Either SomeException ())
      uninterruptibleMask_ $ modifyMVar_ state $ \(State h _ t b) -> pure (State h (either (const (PUnknown fd)) (const PClosed) result) t b)
      pure (either (const False) (const True) result,either Just (const Nothing) result)

closeTransfer :: MVar State -> IO (Bool,Maybe SomeException)
closeTransfer state = do
  picked <- uninterruptibleMask_ $ modifyMVar state $ \s@(State h p t busy) -> case (t,busy) of
    (THandle handle,False) -> pure (State h p TClosing False,Just handle)
    _ -> pure (s,Nothing)
  case picked of
    Nothing -> withMVar state $ \(State _ _ t _) -> pure ((case t of TEmpty -> True; TClosed -> True; TTransferred -> True; _ -> False),Nothing)
    Just handle -> do
      result <- try (hClose handle) :: IO (Either SomeException ())
      uninterruptibleMask_ $ modifyMVar_ state $ \(State h p _ b) -> pure (State h p (either (const (TUnknown Nothing (Just handle))) (const TClosed) result) b)
      pure (either (const False) (const True) result,either Just (const Nothing) result)
