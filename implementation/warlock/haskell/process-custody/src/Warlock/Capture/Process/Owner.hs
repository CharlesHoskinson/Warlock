{-# LANGUAGE OverloadedStrings #-}
-- Scoped private custody; never exports a raw ProcessHandle or retry authority.
module Warlock.Capture.Process.Owner
 ( Owner, OwnerStatus(..), Child, newOwner, begin, abortBegin, publish, quarantine, failUnsettled, settle, status, retainPipe, retainReader, retainBorrow, releaseBorrows, retainTransfer, clearTransfers, retainTicket, clearTickets, retainCore, clearCore, closeRetainedCore, recordStartupFailure, startupFailures, childHandle, newChild, childPid, setPid, readers, pipes ) where
import Control.Concurrent (MVar, ThreadId, modifyMVar, modifyMVar_, newMVar, readMVar)
import Data.IORef (IORef, newIORef, readIORef, writeIORef)
import Data.Text (Text)
import Control.Exception (SomeException)
import Warlock.Capture.Process.Transfer.Internal (CoreTransfer, TransferError, closeCoreTransfer)
import System.IO (Handle)
import Warlock.Capture.Process.Transfer (TransferTicket)
import System.Posix.Types (ProcessID)
import System.Process (ProcessHandle)

data OwnerStatus = Available | Starting | Active | Quarantined [Text] deriving (Eq,Show)
data State = Idle | Beginning | Held Child | Poisoned (Maybe Child) [Text]
data Owner = Owner (MVar State) (IORef [IO ()]) (IORef [Handle]) (IORef [TransferTicket]) (IORef (Maybe CoreTransfer)) (IORef [(SomeException, Maybe SomeException)])
data Child = Child { childHandle :: ProcessHandle, childPidRef :: IORef (Maybe ProcessID), pipeRef :: IORef [Handle], readerRef :: IORef [(ThreadId,IO ())] }
newOwner :: IO Owner
newOwner = Owner <$> newMVar Idle <*> newIORef [] <*> newIORef [] <*> newIORef [] <*> newIORef Nothing <*> newIORef []
begin :: Owner -> IO Bool
begin (Owner m _ _ _ _ _) = modifyMVar m $ \s -> case s of Idle -> pure (Beginning,True); _ -> pure (s,False)
abortBegin :: Owner -> IO ()
abortBegin (Owner m _ _ _ _ _) = modifyMVar_ m $ \s -> case s of Beginning -> pure Idle; _ -> pure s
newChild :: ProcessHandle -> IO Child
newChild h = Child h <$> newIORef Nothing <*> newIORef [] <*> newIORef []
publish :: Owner -> Child -> IO ()
publish (Owner m _ _ _ _ _) c = modifyMVar_ m $ \s -> case s of Beginning -> pure (Held c); _ -> pure (Poisoned (Just c) ["invalid-owner-transition"])
quarantine :: Owner -> Maybe Child -> [Text] -> IO ()
quarantine (Owner m _ _ _ _ _) c reasons = modifyMVar_ m (const (pure (Poisoned c reasons)))

failUnsettled :: Owner -> Text -> IO ()
failUnsettled (Owner m _ _ _ _ _) reason = modifyMVar_ m $ \s -> case s of
 Beginning -> pure (Poisoned Nothing [reason])
 Held c -> pure (Poisoned (Just c) [reason])
 _ -> pure s
settle :: Owner -> IO ()
settle (Owner m _ _ _ _ _) = modifyMVar_ m $ \s -> case s of Held _ -> pure Idle; _ -> pure s
status :: Owner -> IO OwnerStatus
status (Owner m _ _ _ _ _) = do
 s <- readMVar m
 pure $ case s of Idle -> Available; Beginning -> Starting; Held _ -> Active; Poisoned _ xs -> Quarantined xs
setPid :: Child -> ProcessID -> IO ()
setPid c p = writeIORef (childPidRef c) (Just p)
childPid :: Child -> IO (Maybe ProcessID)
childPid = readIORef . childPidRef
retainPipe :: Child -> Handle -> IO ()
retainPipe c h = do hs <- readIORef (pipeRef c); writeIORef (pipeRef c) (h:hs)
retainReader :: Child -> ThreadId -> IO () -> IO ()
retainReader c t await = do ts <- readIORef (readerRef c); writeIORef (readerRef c) ((t,await):ts)
pipes :: Child -> IO [Handle]
pipes = readIORef . pipeRef
readers :: Child -> IO [(ThreadId,IO ())]
readers = readIORef . readerRef

-- The aggregate holds borrowed executable references even in Poisoned state.
retainBorrow :: Owner -> IO () -> IO ()
retainBorrow (Owner _ refs _ _ _ _) action = do
 previous <- readIORef refs
 writeIORef refs (action:previous)
releaseBorrows :: Owner -> IO ()
releaseBorrows (Owner _ refs _ _ _ _) = do
 actions <- readIORef refs
 sequence_ actions
 writeIORef refs []

retainTransfer :: Owner -> Handle -> IO ()
retainTransfer (Owner _ _ refs _ _ _) handle = do
 previous <- readIORef refs
 writeIORef refs (handle:previous)
clearTransfers :: Owner -> IO ()
clearTransfers (Owner _ _ refs _ _ _) = writeIORef refs []

-- A reference retains the ticket but confers no right to close its handle.
retainTicket :: Owner -> TransferTicket -> IO ()
retainTicket (Owner _ _ _ refs _ _) ticket = do
 previous <- readIORef refs
 writeIORef refs (ticket:previous)

clearTickets :: Owner -> IO ()
clearTickets (Owner _ _ _ refs _ _) = writeIORef refs []

-- These retain only the unique guarded capability; no raw handle or token
-- is reconstructed. The caller must keep this Owner through quarantine.
retainCore :: Owner -> CoreTransfer -> IO ()
retainCore (Owner _ _ _ _ ref _) core = writeIORef ref (Just core)
clearCore :: Owner -> IO ()
clearCore (Owner _ _ _ _ ref _) = writeIORef ref Nothing
closeRetainedCore :: Owner -> IO (Maybe (Either TransferError ()))
closeRetainedCore owner@(Owner _ _ _ _ ref _) = do
 ownerState <- status owner
 case ownerState of
  Quarantined _ -> do
   current <- readIORef ref
   case current of
    Nothing -> pure Nothing
    Just core -> do
     result <- closeCoreTransfer core
     pure (Just result)
  _ -> pure Nothing
recordStartupFailure :: Owner -> SomeException -> Maybe SomeException -> IO ()
recordStartupFailure (Owner _ _ _ _ _ ref) original cleanup = do
 previous <- readIORef ref
 writeIORef ref ((original,cleanup):previous)
startupFailures :: Owner -> IO [(SomeException, Maybe SomeException)]
startupFailures (Owner _ _ _ _ _ ref) = readIORef ref
