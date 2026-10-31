{-# LANGUAGE OverloadedStrings #-}
{-# LANGUAGE ScopedTypeVariables #-}
-- Source-only owned endpoint; adoption is not bootstrap or peer authentication.
module Warlock.Transport.Channel
  ( Channel, Direction(..), Priority(..), ChannelError(..), CloseResult(..)
  , CloseState(..), channelState, channelFlagsVerified, newConfiguredChannel, receive, receiveWith, receiveWithStart, receiveRawDeadline, receiveRawDeadlineWithStart, CredentialFrameError(..), receiveCredentialFrame, enqueue, sendNext, closeChannel, retainedFrames ) where
import Control.Concurrent.MVar
import Control.Exception (SomeException, SomeAsyncException, fromException, throwIO, evaluate, mask, uninterruptibleMask_, try, finally, onException)
import System.Timeout (timeout)
import GHC.Clock (getMonotonicTimeNSec)
import qualified Data.ByteString as B
import Data.Text (Text)
import qualified Network.Socket as S
import qualified Network.Socket.ByteString as N
import Warlock.Transport.Frame (FrameError(..),headerLength,prefix)
import Warlock.Protocol.Codec (decodeClientChecked,decodeServerChecked)
import qualified Warlock.Transport.SocketFlags as F
import qualified Warlock.Transport.PeerCredentials as P
import Warlock.Protocol.CredentialGuard (CredentialGuard(..))

data Direction = ClientInbound | ServerInbound deriving (Eq,Show)
data Priority = Ordinary | Control deriving (Eq,Show)
data ChannelError = Closed | Busy | QueueFull | EmptyQueue | TimedOut | StreamEOF | FrameFault FrameError | InvalidPayload Text | IOErrorClosed deriving (Eq,Show)
data CloseResult = ClosedNow | AlreadyClosed | CloseFailed | CloseInProgress deriving (Eq,Show)
data CloseState = Open | Closing | Confirmed | Uncertain deriving (Eq,Show)
data State = State CloseState (Maybe B.ByteString) (Maybe B.ByteString) Bool
data Channel = Channel S.Socket Direction (MVar State) (MVar ()) (MVar ()) (IO ())
channelState :: Channel -> IO CloseState
channelState (Channel _ _ state _ _ _) = withMVar state $ \(State current _ _ _) -> pure current
-- Internal fixture observation; it does not export the owned descriptor.
channelFlagsVerified :: Channel -> IO Bool
channelFlagsVerified (Channel sock _ state _ _ _) = do
  closed <- isClosed state
  if closed then pure False else F.socketFlagsVerified sock

-- Used only after the pre-published owner has configured the socket.
-- Failure does not close or transfer ownership: the owner retains its closer.
newConfiguredChannel :: S.Socket -> Direction -> IO () -> IO Channel
newConfiguredChannel sock direction closeAction =
  Channel sock direction <$> newMVar (State Open Nothing Nothing False) <*> newMVar () <*> newMVar () <*> pure closeAction
closeChannel :: Channel -> IO CloseResult
closeChannel (Channel _ _ state _ _ closeAction) = mask $ \_ -> do
  prior <- modifyMVar state $ \(State status ordinary control lastControl) -> case status of
    Open -> pure (State Closing ordinary control lastControl,Open)
    other -> pure (State other ordinary control lastControl,other)
  case prior of
    Confirmed -> pure AlreadyClosed
    Uncertain -> pure CloseFailed
    Closing -> pure CloseInProgress
    Open -> do
      result <- try closeAction :: IO (Either SomeException ())
      uninterruptibleMask_ $ modifyMVar_ state $ \(State _ ordinary control lastControl) ->
        pure (State (either (const Uncertain) (const Confirmed) result) ordinary control lastControl)
      case result of
        Right () -> pure ClosedNow
        Left e -> case fromException e :: Maybe SomeAsyncException of
          Just _ -> throwIO e
          Nothing -> pure CloseFailed
-- Queued frames after a failure are uncertain and may only be reconciled by
-- the owning policy. This function does not resend or grant authority.
retainedFrames :: Channel -> IO [(Priority,B.ByteString)]
retainedFrames (Channel _ _ state _ _ _) = withMVar state $ \(State _ ordinary control _) ->
  pure (maybe [] (\bytes -> [(Control,bytes)]) control ++ maybe [] (\bytes -> [(Ordinary,bytes)]) ordinary)
isClosed :: MVar State -> IO Bool
isClosed state = withMVar state $ \(State status _ _ _) -> pure (status /= Open)
withGate :: MVar () -> IO (Either ChannelError a) -> IO (Either ChannelError a)
withGate gate action = mask $ \restore -> do
  acquired <- tryTakeMVar gate
  case acquired of
    Nothing -> pure (Left Busy)
    Just () -> restore action `finally` putMVar gate ()
-- Linux recv(2) without a control buffer does not expose an ancillary FD.
-- OS-specific SCM_RIGHTS discard/close behavior must be separately qualified.
readExact :: S.Socket -> Int -> ChannelError -> IO (Either ChannelError B.ByteString)
readExact sock required onEof = go required []
  where
    go 0 chunks = pure (Right (B.concat (reverse chunks)))
    go remaining chunks = do
      bytes <- N.recv sock remaining
      if B.null bytes then pure (Left (if null chunks && onEof == FrameFault TruncatedHeader then StreamEOF else onEof)) else go (remaining - B.length bytes) (bytes:chunks)

-- Internal owner-only handoff. The returned deadline is the original read
-- deadline; the gate must reject admission after it, without renewing it.
receiveRawDeadline :: Channel -> IO (Either ChannelError (B.ByteString,Integer))
receiveRawDeadline = receiveRawDeadlineWithStart (pure ())
receiveRawDeadlineWithStart :: IO () -> Channel -> IO (Either ChannelError (B.ByteString,Integer))
receiveRawDeadlineWithStart started channel@(Channel sock _ state readGate _ _) = withGate readGate $ (do
  closed <- isClosed state
  if closed then pure (Left Closed) else do
    start <- getMonotonicTimeNSec
    let deadline = toInteger start + 5000000000
    result <- try (timeout 5000000 $ do
      started
      header <- readExact sock 4 (FrameFault TruncatedHeader)
      case header of
        Left e -> pure (Left e)
        Right raw -> case headerLength raw of
          Left e -> pure (Left (FrameFault e))
          Right size -> readExact sock size (FrameFault TruncatedBody)) :: IO (Either SomeException (Maybe (Either ChannelError B.ByteString)))
    end <- getMonotonicTimeNSec
    case result of
      Right _ | toInteger end >= deadline -> closeChannel channel >> pure (Left TimedOut)
      Right (Just (Right bytes)) -> pure (Right (bytes,deadline))
      Right (Just (Left e)) -> closeChannel channel >> pure (Left e)
      Right _ -> closeChannel channel >> pure (Left TimedOut)
      Left e -> handleException channel e) `onException` cleanupNoThrow channel

-- The credential reader is retained by the ingress owner.  It borrows the
-- channel socket only under the same read gate as the legacy receive path.
data CredentialFrameError refusal = CredentialTransport ChannelError | CredentialAncillary P.CredentialError
 | CredentialPeer refusal | CredentialChanged deriving (Eq,Show)

receiveCredentialFrame :: forall refusal. P.CredentialReader -> CredentialGuard refusal -> Channel
 -> IO (Either (CredentialFrameError refusal) (B.ByteString,Integer,P.PeerCredential))
receiveCredentialFrame reader guard channel@(Channel sock _ state readGate _ _) = mask $ \restore -> do
 acquired <- tryTakeMVar readGate
 case acquired of
  Nothing -> pure (Left (CredentialTransport Busy))
  Just () -> (restore run `onException` cleanupNoThrow channel) `finally` putMVar readGate ()
 where
  run = do
   closed <- isClosed state
   if closed then pure (Left (CredentialTransport Closed)) else do
    start <- getMonotonicTimeNSec
    let deadline = toInteger start + 5000000000
    result <- try (timeout 5000000 (frame deadline)) :: IO (Either SomeException (Maybe (Either (CredentialFrameError refusal) (B.ByteString,P.PeerCredential))))
    end <- getMonotonicTimeNSec
    case result of
     Left err -> do failure <- (handleException channel err :: IO (Either ChannelError ())); pure (either (Left . CredentialTransport) (const (Left (CredentialTransport IOErrorClosed))) failure)
     Right _ | toInteger end >= deadline -> failFrame (CredentialTransport TimedOut)
     Right Nothing -> failFrame (CredentialTransport TimedOut)
     Right (Just (Left err)) -> failFrame err
     Right (Just (Right (bytes,credential))) -> pure (Right (bytes,deadline,credential))
  failFrame err = do _ <- closeChannel channel; pure (Left err)
  frame deadline = do
   header <- pieces deadline 4 Nothing [] (FrameFault TruncatedHeader)
   case header of
    Left err -> pure (Left err)
    Right (raw,credential) -> case headerLength raw of
     Left err -> pure (Left (CredentialTransport (FrameFault err)))
     Right size -> pieces deadline size (Just credential) [] (FrameFault TruncatedBody)
  pieces deadline remaining first chunks eofFault
   | remaining == 0 = case first of
      Nothing -> pure (Left (CredentialTransport eofFault))
      Just credential -> pure (Right (B.concat (reverse chunks),credential))
   | otherwise = do
      now <- getMonotonicTimeNSec
      if toInteger now >= deadline then pure (Left (CredentialTransport TimedOut)) else do
       result <- P.receiveCredentialChunk reader sock remaining
       case result of
        Left err -> pure (Left (CredentialAncillary err))
        Right P.EndOfStream -> pure (Left (CredentialTransport (if null chunks && first == Nothing && eofFault == FrameFault TruncatedHeader then StreamEOF else eofFault)))
        Right (P.CredentialChunk bytes credential) -> do
         approved <- checkFragment guard credential
         case approved of
          Left err -> pure (Left (CredentialPeer err))
          Right () | B.null bytes || B.length bytes > remaining -> pure (Left (CredentialTransport (FrameFault eofFaultFrame)))
                   | maybe False (/= credential) first -> pure (Left CredentialChanged)
                   | otherwise -> pieces deadline (remaining - B.length bytes) (Just credential) (bytes:chunks) eofFault
   where eofFaultFrame = case eofFault of FrameFault err -> err; _ -> TruncatedBody

-- Evaluate every decoded field before the deadline scope exits. `show` here
-- forces the existing total codec values, is not emitted or logged.
forceDecoded :: Direction -> B.ByteString -> IO (Either Text ())
forceDecoded ClientInbound bytes = case decodeClientChecked bytes of
  Left reason -> pure (Left reason)
  Right frame -> evaluate (length (show frame)) >> pure (Right ())
forceDecoded ServerInbound bytes = case decodeServerChecked bytes of
  Left reason -> pure (Left reason)
  Right frame -> evaluate (length (show frame)) >> pure (Right ())
readFrame :: Integer -> (B.ByteString -> IO ()) -> S.Socket -> Direction -> IO (Either ChannelError B.ByteString)
readFrame deadline hook sock direction = do
  header <- readExact sock 4 (FrameFault TruncatedHeader)
  case header of
    Left e -> pure (Left e)
    Right raw -> case headerLength raw of
      Left e -> pure (Left (FrameFault e))
      Right size -> do
        body <- readExact sock size (FrameFault TruncatedBody)
        case body of
          Left e -> pure (Left e)
          Right bytes -> do
            before <- getMonotonicTimeNSec
            if toInteger before >= deadline then pure (Left TimedOut) else do
              hook bytes
              valid <- forceDecoded direction bytes
              after <- getMonotonicTimeNSec
              pure (if toInteger after >= deadline then Left TimedOut else either (Left . InvalidPayload) (const (Right bytes)) valid)
receive :: Channel -> IO (Either ChannelError B.ByteString)
receive = receiveWith (const (pure ()))
-- Internal hook is source-fixture only; production receive cannot bypass it.
receiveWith :: (B.ByteString -> IO ()) -> Channel -> IO (Either ChannelError B.ByteString)
receiveWith hook = receiveWithStart (pure ()) hook
-- Internal fixture can observe that the real read is about to begin.
receiveWithStart :: IO () -> (B.ByteString -> IO ()) -> Channel -> IO (Either ChannelError B.ByteString)
receiveWithStart started hook channel@(Channel sock direction state readGate _ _) = withGate readGate $ (do
  closed <- isClosed state
  if closed then pure (Left Closed) else do
    start <- getMonotonicTimeNSec
    result <- try (timeout 5000000 (started >> readFrame (toInteger start + 5000000000) hook sock direction)) :: IO (Either SomeException (Maybe (Either ChannelError B.ByteString)))
    end <- getMonotonicTimeNSec
    case result of
      Right _ | toInteger end - toInteger start >= 5000000000 -> closeChannel channel >> pure (Left TimedOut)
      Right (Just (Right bytes)) -> pure (Right bytes)
      Right (Just (Left e)) -> closeChannel channel >> pure (Left e)
      Right _ -> closeChannel channel >> pure (Left TimedOut)
      Left e -> handleException channel e) `onException` cleanupNoThrow channel
cleanupNoThrow :: Channel -> IO ()
cleanupNoThrow channel = do
  _ <- try (closeChannel channel) :: IO (Either SomeException CloseResult)
  pure ()
handleException :: Channel -> SomeException -> IO (Either ChannelError a)
handleException channel err = do
  cleanup <- try (closeChannel channel) :: IO (Either SomeException CloseResult)
  case fromException err :: Maybe SomeAsyncException of
    Just _ -> throwIO err
    Nothing -> case cleanup of
      Left cleanupError -> case fromException cleanupError :: Maybe SomeAsyncException of
        Just _ -> throwIO cleanupError
        Nothing -> pure (Left IOErrorClosed)
      Right _ -> pure (Left IOErrorClosed)

enqueue :: Channel -> Priority -> B.ByteString -> IO (Either ChannelError ())
enqueue channel@(Channel _ direction state _ _ _) priority bytes = case prefix bytes of
  Left e -> pure (Left (FrameFault e))
  Right framed -> do
    start <- getMonotonicTimeNSec
    let outbound = case direction of ClientInbound -> ServerInbound; ServerInbound -> ClientInbound
    result <- try (timeout 5000000 (forceDecoded outbound bytes)) :: IO (Either SomeException (Maybe (Either Text ())))
    end <- getMonotonicTimeNSec
    case result of
      Left e -> handleException channel e
      Right _ | toInteger end - toInteger start >= 5000000000 -> closeChannel channel >> pure (Left TimedOut)
      Right Nothing -> closeChannel channel >> pure (Left TimedOut)
      Right (Just (Left reason)) -> pure (Left (InvalidPayload reason))
      Right (Just (Right ())) -> modifyMVar state $ \current@(State status ordinary control lastControl) ->
        if status /= Open then pure (current,Left Closed) else case (priority,ordinary,control) of
          (Ordinary,Nothing,_) -> pure (State Open (Just framed) control lastControl,Right ())
          (Control,_,Nothing) -> pure (State Open ordinary (Just framed) lastControl,Right ())
          _ -> pure (current,Left QueueFull)
sendNext :: Channel -> IO (Either ChannelError ())
sendNext channel@(Channel sock _ state _ writeGate _) = withGate writeGate $ (do
  choice <- withMVar state $ \(State status ordinary control lastControl) -> pure $
    if status /= Open then Left Closed else case (control,ordinary,lastControl) of
      (Just bytes,_,False) -> Right (Control,bytes)
      (Just bytes,Nothing,_) -> Right (Control,bytes)
      (_,Just bytes,_) -> Right (Ordinary,bytes)
      _ -> Left EmptyQueue
  case choice of
    Left e -> pure (Left e)
    Right (priority,bytes) -> do
      result <- try (timeout 5000000 (N.sendAll sock bytes)) :: IO (Either SomeException (Maybe ()))
      case result of
        Right (Just ()) -> do
          modifyMVar_ state $ \(State status ordinary control _) -> pure $ case priority of
            Control -> State status ordinary Nothing True
            Ordinary -> State status Nothing control False
          pure (Right ())
        Right Nothing -> closeChannel channel >> pure (Left TimedOut)
        Left e -> handleException channel e) `onException` cleanupNoThrow channel
