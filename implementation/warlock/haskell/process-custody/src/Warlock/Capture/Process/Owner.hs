{-# LANGUAGE OverloadedStrings #-}
-- Scoped private custody; never exports a raw ProcessHandle or retry authority.
module Warlock.Capture.Process.Owner
 ( Owner, OwnerStatus(..), Child, newOwner, begin, abortBegin, tryAbortUnborrowed, retainHeldBorrow, tryReleaseRetainedHeld, tryAbortHeldNoInput, tryAbortHeldWithCore, tryAbortHeldNotAcquired, tryAbortHeldNoInputBefore, tryAbortHeldWithCoreBefore, tryAbortHeldNotAcquiredBefore, publish, quarantine, failUnsettled, settle, status, retainPipe, retainReader, retainBorrow, releaseBorrows, retainTransfer, clearTransfers, retainTicket, clearTickets, retainCore, clearCore, closeRetainedCore, recordStartupFailure, startupFailures, Pending, PendingFD(..), FDIdentity(..), newPending, retainPending, ownerPending, pendingRecordFD, pendingIdentityFD, pendingMarkFD, pendingTransferFD, clearPending, pendingRecordPid, pendingRecordHandle, pendingSnapshot, pendingStart, pendingRecordIssue, NativePhase(..), pendingNativeRecord, pendingNativeMark, pendingNativeTakeFreeable, pendingNativeSnapshot, pendingIssues, childHandle, newChild, childPid, setPid, readers, pipes ) where
import Control.Concurrent (MVar, ThreadId, modifyMVar, modifyMVar_, newMVar, putMVar, readMVar, tryTakeMVar)
import Data.IORef (IORef, newIORef, readIORef, writeIORef, atomicModifyIORef')
import Data.Text (Text)
import Control.Exception (SomeException, mask_, onException, try, throwIO, uninterruptibleMask_)
import Warlock.Platform.Executable (HeldBorrow, tryReleaseHeld, tryHeldBorrowNotAcquired)
import GHC.Clock (getMonotonicTimeNSec)
import Warlock.Capture.Process.Transfer.Internal (CoreTransfer, TransferError, closeCoreTransfer, tryCoreClosedMatches)
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
data HeldReceipt = HeldReceiptPending | HeldReceiptConfirmed | HeldReceiptUnknown
data BorrowRef = LegacyBorrow (IO ()) | RetainedHeld HeldBorrow (IORef HeldReceipt)
data Owner = Owner (MVar State) (IORef [BorrowRef]) (IORef [Handle]) (IORef [TransferTicket]) (IORef (Maybe CoreTransfer)) (IORef [(SomeException, Maybe SomeException)]) (IORef (Maybe Pending))
data Child = Child { childHandle :: ProcessHandle, childPidRef :: IORef (Maybe ProcessID), pipeRef :: IORef [Handle], readerRef :: IORef [(ThreadId,IO ())] }
newOwner :: IO Owner
newOwner = Owner <$> newMVar Idle <*> newIORef [] <*> newIORef [] <*> newIORef [] <*> newIORef Nothing <*> newIORef [] <*> newIORef Nothing
begin :: Owner -> IO Bool
begin (Owner m _ _ _ _ _ _) = modifyMVar m $ \s -> case s of Idle -> pure (Beginning,True); _ -> pure (s,False)
abortBegin :: Owner -> IO ()
abortBegin (Owner m _ _ _ _ _ _) = modifyMVar_ m $ \s -> case s of Beginning -> pure Idle; _ -> pure s
-- Only for the fresh PersistentOwner startup path, after the acquisition
-- returns proven-unborrowed and before input preparation or spawn. That path
-- is the sole writer of this private raw Owner and its Pending references;
-- the stop requester uses the separate phase/gate and never mutates these refs.
-- This is NOT a general concurrent snapshot API. An occupied state lock or
-- any unexpected retained evidence refuses without dropping the owner/pending.
tryAbortUnborrowed :: Owner -> Pending -> IO Bool
tryAbortUnborrowed (Owner gate borrows transfers tickets core failures slot) expected = mask_ $ do
 state <- tryTakeMVar gate
 case state of
  Nothing -> pure False
  Just held -> do
   let restoreState = putMVar gate held
   clean <- (case held of
    Beginning -> do
     registered <- readIORef slot
     bs <- readIORef borrows
     ts <- readIORef transfers
     ks <- readIORef tickets
     cs <- readIORef core
     fs <- readIORef failures
     case (registered, expected) of
      (Just (Pending f p h started issues native), Pending ef _ _ _ _ _)
       | f == ef -> do
        fdValues <- readIORef f
        pidValue <- readIORef p
        handleValue <- readIORef h
        began <- readIORef started
        issueValues <- readIORef issues
        nativeValues <- readIORef native
        let emptyMaybe Nothing = True
            emptyMaybe _ = False
        pure (null bs && null ts && null ks && emptyMaybe cs && null fs
          && null fdValues && emptyMaybe pidValue && emptyMaybe handleValue
          && not began && null issueValues && null nativeValues)
      _ -> pure False
    _ -> pure False) `onException` restoreState
   if clean then do
    -- No other raw-Owner writer exists in this pre-spawn branch. The masked
    -- two writes therefore form the only checked beginning-to-idle receipt.
    writeIORef slot Nothing `onException` restoreState
    putMVar gate Idle
    pure True
   else restoreState >> pure False

-- The caller holds phase then stop gate, checked this owner's original D,
-- and is the sole raw writer. No action or descriptor close is invoked here.
-- The core variant additionally requires the exact retained core and ticket
-- to share a confirmed Closed (Core matching-token) transfer state.
tryAbortHeldNoInput :: Owner -> Pending -> IO Bool
tryAbortHeldNoInput = tryAbortHeld False False Nothing

tryAbortHeldWithCore :: Owner -> Pending -> IO Bool
tryAbortHeldWithCore = tryAbortHeld True False Nothing

-- Only a terminal NotAcquired from the exact retained preowned HeldBorrow
-- can authorize a no-borrow raw abort. New/Activating/busy/Unknown refuse.
tryAbortHeldNotAcquired :: Owner -> Pending -> IO Bool
tryAbortHeldNotAcquired = tryAbortHeld False True Nothing

-- Internal callers pass the exact already-selected same-owner absolute D in
-- monotonic nanoseconds. These fixed metadata checks invoke no supplied action.
tryAbortHeldNoInputBefore :: Integer -> Owner -> Pending -> IO Bool
tryAbortHeldNoInputBefore end = tryAbortHeld False False (Just end)

tryAbortHeldWithCoreBefore :: Integer -> Owner -> Pending -> IO Bool
tryAbortHeldWithCoreBefore end = tryAbortHeld True False (Just end)

tryAbortHeldNotAcquiredBefore :: Integer -> Owner -> Pending -> IO Bool
tryAbortHeldNotAcquiredBefore end = tryAbortHeld False True (Just end)

tryAbortHeld :: Bool -> Bool -> Maybe Integer -> Owner -> Pending -> IO Bool
tryAbortHeld requireCore requireNotAcquired limit (Owner gate borrows transfers tickets core failures slot) expected = mask_ $ do
 state <- tryTakeMVar gate
 case state of
  Nothing -> pure False
  Just held -> do
   let restoreState = putMVar gate held
   (clean, savedBorrows, savedTickets, savedCore) <- (case held of
    Beginning -> do
     registered <- readIORef slot
     bs <- readIORef borrows
     ts <- readIORef transfers
     ks <- readIORef tickets
     cs <- readIORef core
     fs <- readIORef failures
     coreOk <- case (requireCore, cs, ks) of
      (False, Nothing, []) -> pure True
      (True, Just retainedCore, [retainedTicket]) -> do
       coreClosed <- tryCoreClosedMatches retainedCore retainedTicket
       pure (coreClosed == Just True)
      _ -> pure False
     case (registered, expected, bs) of
      (Just (Pending f p h started issues native), Pending ef _ _ _ _ _,
       [RetainedHeld capability receipt]) | f == ef -> do
        settled <- readIORef receipt
        noBorrow <- if requireNotAcquired then tryHeldBorrowNotAcquired capability else pure False
        fdValues <- readIORef f
        pidValue <- readIORef p
        handleValue <- readIORef h
        began <- readIORef started
        issueValues <- readIORef issues
        nativeValues <- readIORef native
        let emptyMaybe Nothing = True; emptyMaybe _ = False
            released = case settled of
             HeldReceiptConfirmed -> not requireNotAcquired
             HeldReceiptPending -> requireNotAcquired && noBorrow
             HeldReceiptUnknown -> False
        pure (coreOk && released && null ts && null fs && null fdValues &&
         emptyMaybe pidValue && emptyMaybe handleValue && not began &&
         null issueValues && null nativeValues, bs, ks, cs)
      _ -> pure (False,bs,ks,cs)
    _ -> pure (False,[],[],Nothing)) `onException` restoreState
   if not clean then restoreState >> pure False else do
    let inTime = case limit of
         Nothing -> pure True
         Just end -> (< end) . toInteger <$> getMonotonicTimeNSec
        rollback = uninterruptibleMask_ $ do
         writeIORef borrows savedBorrows
         writeIORef tickets savedTickets
         writeIORef core savedCore
         writeIORef slot (Just expected)
         putMVar gate (Poisoned Nothing ["held-abort-finalization-unconfirmed"])
    before <- inTime `onException` restoreState
    if not before then restoreState >> pure False else do
     outcome <- try (do
      writeIORef borrows []
      writeIORef tickets []
      writeIORef core Nothing
      writeIORef slot Nothing
      inTime) :: IO (Either SomeException Bool)
     case outcome of
      Left err -> rollback >> throwIO err
      Right False -> rollback >> pure False
      Right True -> putMVar gate Idle >> pure True

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
 writeIORef refs (LegacyBorrow action:previous)

-- Only the persistent sole startup writer stores the opaque HeldBorrow returned
-- by its selected acquisition. Neither operation nor receipt comes from a caller
-- boolean or a supplied callback. Legacy selected-tool callers remain unchanged.
retainHeldBorrow :: Owner -> HeldBorrow -> IO ()
retainHeldBorrow (Owner _ refs _ _ _ _ _) capability = mask_ $ do
 receipt <- newIORef HeldReceiptPending
 previous <- readIORef refs
 writeIORef refs (RetainedHeld capability receipt:previous)

-- Caller holds the same owner's nonblocking stop gate and checked original D.
-- Nothing is definite no-commit, False/exception sticky Unknown, True confirms
-- this exact retained capability. Never call an arbitrary closure under a gate.
tryReleaseRetainedHeld :: Owner -> IO (Maybe Bool)
tryReleaseRetainedHeld (Owner _ refs _ _ _ _ _) = mask_ $ do
 saved <- readIORef refs
 case saved of
  [RetainedHeld capability receipt] -> do
   state <- readIORef receipt
   case state of
    HeldReceiptConfirmed -> pure (Just True)
    HeldReceiptUnknown -> pure (Just False)
    HeldReceiptPending -> do
     outcome <- try (tryReleaseHeld capability) :: IO (Either SomeException (Maybe Bool))
     case outcome of
      Left err -> writeIORef receipt HeldReceiptUnknown >> throwIO err
      Right Nothing -> pure Nothing
      Right (Just False) -> writeIORef receipt HeldReceiptUnknown >> pure (Just False)
      Right (Just True) -> writeIORef receipt HeldReceiptConfirmed >> pure (Just True)
  _ -> pure (Just False)

releaseBorrows :: Owner -> IO ()
releaseBorrows (Owner _ refs _ _ _ _ _) = do
 actions <- readIORef refs
 let release action = case action of
      LegacyBorrow legacy -> legacy
      RetainedHeld capability receipt -> do
       state <- readIORef receipt
       case state of
        HeldReceiptConfirmed -> pure ()
        HeldReceiptUnknown -> ioError (userError "retained held borrow uncertain")
        HeldReceiptPending -> do
         result <- tryReleaseHeld capability
         case result of
          Just True -> writeIORef receipt HeldReceiptConfirmed
          Just False -> writeIORef receipt HeldReceiptUnknown >> ioError (userError "retained held borrow uncertain")
          Nothing -> ioError (userError "retained held borrow busy")
 mapM_ release actions
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
