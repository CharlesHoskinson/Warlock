{-# LANGUAGE OverloadedStrings #-}
-- Scoped private custody; never exports a raw ProcessHandle or retry authority.
module Warlock.Capture.Process.Owner
 ( Owner, OwnerStatus(..), Child, newOwner, begin, abortBegin, publish, quarantine, failUnsettled, settle, status, retainPipe, retainReader, retainBorrow, releaseBorrows, retainTransfer, clearTransfers, retainTicket, clearTickets, retainCore, clearCore, closeRetainedCore, recordStartupFailure, startupFailures, Pending, PendingFD(..), FDIdentity(..), newPending, retainPending, ownerPending, pendingRecordFD, pendingIdentityFD, pendingMarkFD, pendingTransferFD, clearPending, pendingRecordPid, pendingRecordHandle, pendingSnapshot, pendingStart, pendingRecordIssue, NativePhase(..), pendingNativeRecord, pendingNativeMark, pendingNativeTakeFreeable, pendingNativeSnapshot, pendingIssues, childHandle, newChild, childPid, setPid, readers, pipes ) where
import Control.Concurrent (MVar, ThreadId, modifyMVar, modifyMVar_, newMVar, readMVar)
import Data.IORef (IORef, newIORef, readIORef, writeIORef, atomicModifyIORef')
import Data.Text (Text)
import Control.Exception (SomeException)
import Warlock.Capture.Process.Transfer.Internal (CoreTransfer, TransferError, closeCoreTransfer)
import System.IO (Handle)
import Foreign.Ptr (Ptr)
import Warlock.Capture.Process.Transfer (TransferTicket)
import System.Posix.Types (ProcessID, Fd)
import System.Process (ProcessHandle)

data OwnerStatus = Available | Starting | Active | Quarantined [Text] deriving (Eq,Show)
data State = Idle | Beginning | Held Child | Poisoned (Maybe Child) [Text]
data FDIdentity = FDIdentity Integer Integer deriving (Eq,Show)
data PendingFD = PendingOpen Fd (Maybe FDIdentity) | PendingClosed Fd (Maybe FDIdentity) | PendingUncertain Fd (Maybe FDIdentity) | PendingHandle Fd Handle (Maybe FDIdentity) deriving (Eq,Show)
data NativePhase = NativeAllocated | NativeInitialized | NativeDestroyed | NativeUncertain | NativeFreed deriving (Eq,Show)
data Pending = Pending (IORef [PendingFD]) (IORef (Maybe ProcessID)) (IORef (Maybe ProcessHandle)) (IORef Bool) (IORef [String]) (IORef [(Ptr (),Ptr (),NativePhase)])
data Owner = Owner (MVar State) (IORef [IO ()]) (IORef [Handle]) (IORef [TransferTicket]) (IORef (Maybe CoreTransfer)) (IORef [(SomeException, Maybe SomeException)]) (IORef (Maybe Pending))
data Child = Child { childHandle :: ProcessHandle, childPidRef :: IORef (Maybe ProcessID), pipeRef :: IORef [Handle], readerRef :: IORef [(ThreadId,IO ())] }
newOwner :: IO Owner
newOwner = Owner <$> newMVar Idle <*> newIORef [] <*> newIORef [] <*> newIORef [] <*> newIORef Nothing <*> newIORef [] <*> newIORef Nothing
begin :: Owner -> IO Bool
begin (Owner m _ _ _ _ _ _) = modifyMVar m $ \s -> case s of Idle -> pure (Beginning,True); _ -> pure (s,False)
abortBegin :: Owner -> IO ()
abortBegin (Owner m _ _ _ _ _ _) = modifyMVar_ m $ \s -> case s of Beginning -> pure Idle; _ -> pure s
newChild :: ProcessHandle -> IO Child
newChild h = Child h <$> newIORef Nothing <*> newIORef [] <*> newIORef []
publish :: Owner -> Child -> IO ()
publish (Owner m _ _ _ _ _ _) c = modifyMVar_ m $ \s -> case s of Beginning -> pure (Held c); _ -> pure (Poisoned (Just c) ["invalid-owner-transition"])
quarantine :: Owner -> Maybe Child -> [Text] -> IO ()
quarantine (Owner m _ _ _ _ _ _) c reasons = modifyMVar_ m (const (pure (Poisoned c reasons)))

failUnsettled :: Owner -> Text -> IO ()
failUnsettled (Owner m _ _ _ _ _ _) reason = modifyMVar_ m $ \s -> case s of
 Beginning -> pure (Poisoned Nothing [reason])
 Held c -> pure (Poisoned (Just c) [reason])
 _ -> pure s
settle :: Owner -> IO ()
settle (Owner m _ _ _ _ _ _) = modifyMVar_ m $ \s -> case s of Held _ -> pure Idle; _ -> pure s
status :: Owner -> IO OwnerStatus
status (Owner m _ _ _ _ _ _) = do
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
retainBorrow (Owner _ refs _ _ _ _ _) action = do
 previous <- readIORef refs
 writeIORef refs (action:previous)
releaseBorrows :: Owner -> IO ()
releaseBorrows (Owner _ refs _ _ _ _ _) = do
 actions <- readIORef refs
 sequence_ actions
 writeIORef refs []

retainTransfer :: Owner -> Handle -> IO ()
retainTransfer (Owner _ _ refs _ _ _ _) handle = do
 previous <- readIORef refs
 writeIORef refs (handle:previous)
clearTransfers :: Owner -> IO ()
clearTransfers (Owner _ _ refs _ _ _ _) = writeIORef refs []

-- A reference retains the ticket but confers no right to close its handle.
retainTicket :: Owner -> TransferTicket -> IO ()
retainTicket (Owner _ _ _ refs _ _ _) ticket = do
 previous <- readIORef refs
 writeIORef refs (ticket:previous)

clearTickets :: Owner -> IO ()
clearTickets (Owner _ _ _ refs _ _ _) = writeIORef refs []

-- These retain only the unique guarded capability; no raw handle or token
-- is reconstructed. The caller must keep this Owner through quarantine.
retainCore :: Owner -> CoreTransfer -> IO ()
retainCore (Owner _ _ _ _ ref _ _) core = writeIORef ref (Just core)
clearCore :: Owner -> IO ()
clearCore (Owner _ _ _ _ ref _ _) = writeIORef ref Nothing
closeRetainedCore :: Owner -> IO (Maybe (Either TransferError ()))
closeRetainedCore owner@(Owner _ _ _ _ ref _ _) = do
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
recordStartupFailure (Owner _ _ _ _ _ ref _) original cleanup = do
 previous <- readIORef ref
 writeIORef ref ((original,cleanup):previous)
startupFailures :: Owner -> IO [(SomeException, Maybe SomeException)]
startupFailures (Owner _ _ _ _ _ ref _) = readIORef ref

-- One pending slot is installed before any selected-spawn acquisition. It is
-- not a second reaper; PID and descriptor states remain under this Owner.
newPending :: IO Pending
newPending = Pending <$> newIORef [] <*> newIORef Nothing <*> newIORef Nothing <*> newIORef False <*> newIORef [] <*> newIORef []
retainPending :: Owner -> Pending -> IO Bool
retainPending (Owner _ _ _ _ _ _ ref) pending = atomicModifyIORef' ref $ \old -> case old of Nothing -> (Just pending,True); Just _ -> (old,False)
-- Inspection/recovery remains private to the same Owner; no raw PID is a signal grant.
ownerPending :: Owner -> IO (Maybe Pending)
ownerPending (Owner _ _ _ _ _ _ ref) = readIORef ref
pendingRecordFD :: Pending -> Fd -> IO ()
pendingRecordFD (Pending ref _ _ _ _ _) fd = atomicModifyIORef' ref (\xs -> (PendingOpen fd Nothing:xs,()))
pendingIdentityFD :: Pending -> Fd -> FDIdentity -> IO ()
pendingIdentityFD (Pending ref _ _ _ _ _) fd identity = atomicModifyIORef' ref $ \xs -> (map (\x -> case x of PendingOpen n _ | n == fd -> PendingOpen n (Just identity); _ -> x) xs,())
pendingMarkFD :: Pending -> Fd -> Bool -> IO ()
pendingMarkFD (Pending ref _ _ _ _ _) fd closed = atomicModifyIORef' ref $ \xs -> (map (\x -> case x of PendingOpen n identity | n == fd -> if closed then PendingClosed n identity else PendingUncertain n identity; PendingUncertain n identity | n == fd && closed -> PendingClosed n identity; _ -> x) xs,())
-- Mark before fdToHandle; failed conversion may have consumed the number.
pendingTransferFD :: Pending -> Fd -> Handle -> IO ()
pendingTransferFD (Pending ref _ _ _ _ _) fd handle = atomicModifyIORef' ref $ \xs -> (map (\x -> case x of PendingUncertain n identity | n == fd -> PendingHandle n handle identity; _ -> x) xs,())
clearPending :: Owner -> IO ()
clearPending (Owner _ _ _ _ _ _ ref) = writeIORef ref Nothing
pendingRecordPid :: Pending -> ProcessID -> IO Bool
pendingRecordPid (Pending _ ref _ _ _ _) pid = atomicModifyIORef' ref $ \old -> case old of Nothing -> (Just pid,True); Just _ -> (old,False)
pendingRecordHandle :: Pending -> ProcessHandle -> IO Bool
pendingRecordHandle (Pending _ _ ref _ _ _) ph = atomicModifyIORef' ref $ \old -> case old of Nothing -> (Just ph,True); Just _ -> (old,False)
pendingSnapshot :: Pending -> IO ([PendingFD],Maybe ProcessID,Bool)
pendingSnapshot (Pending fds pid ph _ _ _) = do
 fdState <- readIORef fds
 process <- readIORef pid
 handle <- readIORef ph
 pure (fdState,process,case handle of Nothing -> False; Just _ -> True)

pendingStart :: Pending -> IO Bool
pendingStart (Pending _ _ _ ref _ _) = atomicModifyIORef' ref (\started -> if started then (True,False) else (True,True))

pendingRecordIssue :: Pending -> String -> IO ()
pendingRecordIssue (Pending _ _ _ _ ref _) issue = atomicModifyIORef' ref (\xs -> (issue:xs,()))

pendingNativeRecord :: Pending -> Ptr () -> Ptr () -> IO ()
pendingNativeRecord (Pending _ _ _ _ _ ref) base aligned = atomicModifyIORef' ref (\xs -> ((base,aligned,NativeAllocated):xs,()))
pendingNativeMark :: Pending -> Ptr () -> NativePhase -> IO ()
pendingNativeMark (Pending _ _ _ _ _ ref) aligned phase = atomicModifyIORef' ref $ \xs -> (map (\entry@(base,p,current) -> if p == aligned && current /= NativeFreed then (base,p,phase) else entry) xs,())
pendingNativeTakeFreeable :: Pending -> IO [Ptr ()]
pendingNativeTakeFreeable (Pending _ _ _ _ _ ref) = atomicModifyIORef' ref $ \xs ->
 let releasable = [base | (base,_,phase) <- xs, phase == NativeAllocated || phase == NativeDestroyed]
     changed = map (\entry@(base,p,phase) -> if phase == NativeAllocated || phase == NativeDestroyed then (base,p,NativeFreed) else entry) xs
 in (changed,releasable)

-- Inspection does not return or free opaque storage pointers.
pendingNativeSnapshot :: Pending -> IO [NativePhase]
pendingNativeSnapshot (Pending _ _ _ _ _ ref) = map (\(_,_,phase) -> phase) <$> readIORef ref
pendingIssues :: Pending -> IO [String]
pendingIssues (Pending _ _ _ _ ref _) = reverse <$> readIORef ref
