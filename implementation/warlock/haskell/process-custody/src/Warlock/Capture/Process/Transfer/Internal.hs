{-# LANGUAGE ScopedTypeVariables #-}
-- Internal capability boundary. Never publish raw handles or OwnerToken outside
-- this module and the selected-process core.
module Warlock.Capture.Process.Transfer.Internal
 (TransferTicket, CoreTransfer, OwnerToken, TransferDisposition(..), TransferError(..),
  newTransferTicket, closeCallerTransfer, transferDisposition, newOwnerToken,
  claimTransfer, claimTransferWhen, coreHandle, coreCloseDiagnostic, closeCoreTransfer, fixtureTicketWithClose) where
import Control.Concurrent.MVar
import Control.Exception (SomeException, SomeAsyncException, fromException, mask, try, throwIO, uninterruptibleMask_)
import Data.Unique (Unique, newUnique)
import System.IO (Handle, hClose)

data Tag = Caller | Core Unique deriving Eq
data State = CallerLive Handle (IO ()) | CoreLive Handle (IO ()) Unique
           | Closing Handle Tag | Closed Tag | Uncertain Handle Tag TransferError (Maybe SomeException)
newtype TransferTicket = TransferTicket (MVar State)
newtype OwnerToken = OwnerToken Unique
data CoreTransfer = CoreTransfer TransferTicket Unique
data TransferDisposition = CallerOwned | CoreOwned | ClosePending | TransferClosed | TransferUncertain deriving (Eq,Show)
data TransferError = AlreadyClaimed | DeadlineExpired | WrongOwner | ClosingOrUncertain | CloseFailed deriving (Eq,Show)

newTransferTicket :: Handle -> IO TransferTicket
newTransferTicket h = fixtureTicketWithClose h (hClose h)
-- INTERNAL source fixture seam: the close action is still invoked once through
-- the actual shared state machine. Never export this from the caller facade.
fixtureTicketWithClose :: Handle -> IO () -> IO TransferTicket
fixtureTicketWithClose h closeAction = TransferTicket <$> newMVar (CallerLive h closeAction)
newOwnerToken :: IO OwnerToken
newOwnerToken = OwnerToken <$> newUnique
transferDisposition :: TransferTicket -> IO TransferDisposition
transferDisposition (TransferTicket m) = withMVar m $ \s -> pure $ case s of
 CallerLive _ _ -> CallerOwned; CoreLive _ _ _ -> CoreOwned; Closing _ _ -> ClosePending; Closed _ -> TransferClosed; Uncertain _ _ _ _ -> TransferUncertain
claimTransfer :: OwnerToken -> TransferTicket -> IO (Either TransferError CoreTransfer)
claimTransfer = claimTransferWhen (pure True)
-- Core supplies only its monotonic deadline predicate; it executes while the
-- ticket transition is locked, immediately before CallerLive becomes CoreLive.
claimTransferWhen :: IO Bool -> OwnerToken -> TransferTicket -> IO (Either TransferError CoreTransfer)
claimTransferWhen permitted (OwnerToken token) ticket@(TransferTicket m) = modifyMVar m $ \s -> case s of
 CallerLive h closeAction -> do
  allowed <- permitted
  if allowed then pure (CoreLive h closeAction token,Right (CoreTransfer ticket token))
  else pure (s,Left DeadlineExpired)
 _ -> pure (s,Left AlreadyClaimed)

coreHandle :: CoreTransfer -> IO (Either TransferError Handle)
coreHandle (CoreTransfer (TransferTicket m) token) = withMVar m $ \s -> pure $ case s of
 CoreLive h _ owner | owner == token -> Right h
 _ -> Left WrongOwner
-- Only the matching retained core capability can inspect its close diagnostic.
coreCloseDiagnostic :: CoreTransfer -> IO (Maybe SomeException)
coreCloseDiagnostic (CoreTransfer (TransferTicket m) token) = withMVar m $ \s -> pure $ case s of
 Uncertain _ (Core owner) _ cause | owner == token -> cause
 _ -> Nothing
closeCallerTransfer :: TransferTicket -> IO (Either TransferError ())
closeCallerTransfer ticket = closeFor Caller ticket
closeCoreTransfer :: CoreTransfer -> IO (Either TransferError ())
closeCoreTransfer (CoreTransfer ticket token) = closeFor (Core token) ticket
closeFor :: Tag -> TransferTicket -> IO (Either TransferError ())
closeFor tag (TransferTicket m) = mask $ \_ -> do
 selection <- modifyMVar m $ \s -> case s of
  CallerLive h action | tag == Caller -> pure (Closing h tag,Right (Just (h,action)))
  CoreLive h action owner | tag == Core owner -> pure (Closing h tag,Right (Just (h,action)))
  Closed owner | tag == owner -> pure (s,Right Nothing)
  Closing _ _ -> pure (s,Left ClosingOrUncertain)
  Uncertain _ _ _ _ -> pure (s,Left ClosingOrUncertain)
  _ -> pure (s,Left WrongOwner)
 case selection of
  Left err -> pure (Left err)
  Right Nothing -> pure (Right ())
  Right (Just (h,action)) -> do
   outcome <- try action :: IO (Either SomeException ())
   published <- uninterruptibleMask_ $ modifyMVar m $ \s -> case s of
    Closing _ original | original == tag -> pure ((case outcome of Right () -> Closed original; Left ex -> Uncertain h original CloseFailed (Just ex)),True)
    _ -> pure (Uncertain h tag CloseFailed Nothing,False)
   case outcome of
    Right () -> pure (if published then Right () else Left CloseFailed)
    Left ex -> case (fromException ex :: Maybe SomeAsyncException) of
     Just _ -> throwIO ex
     Nothing -> pure (Left CloseFailed)
