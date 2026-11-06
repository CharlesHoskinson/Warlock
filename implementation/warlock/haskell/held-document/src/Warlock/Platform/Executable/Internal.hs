{-# LANGUAGE ScopedTypeVariables #-}
module Warlock.Platform.Executable.Internal
 (ExecutableLease, HeldExecutable, LeaseRole(..), LeaseState(..), LeaseError(..)
 ,newExecutableLease, acquireExecutableLease, acquireExecutableLeaseWithHooks, issueReadyExecutable, retireExecutableLease
 ,executableLeaseState, observeHeldRole, HeldBorrow, prepareHeldBorrow, activateHeldBorrowWhile, tryHeldBorrowNotAcquired, tryReleaseHeld, releaseHeldBorrow, borrowHeld, borrowHeldInterruptible, borrowHeldWhile, retireHeld) where

import Control.Concurrent.MVar
import Control.Exception (SomeException, SomeAsyncException, fromException, mask, onException, throwIO, try, uninterruptibleMask_)
import qualified Data.ByteString as B
import System.Posix.IO (closeFd)
import System.Posix.Process (getProcessID)
import System.Posix.Types (Fd(..))
import Warlock.Platform.Resolver.Internal (Root,Pin,Link,Resolution,ResolveError(..),Hooks,clone,noHooks,resolveSnapshotVia)

data LeaseRole = UiImage deriving (Eq,Show)
data LeaseState = EmptyLease | BuildingLease | PendingLease | ReadyLease | ClosingLease | ClosedLease | MovedLease | UncertainLease deriving (Eq,Show)
data LeaseError = LeaseBusy | LeaseClosed | LeaseCloseUncertain deriving (Eq,Show)
data Slot = Empty | Building | Pending Fd | Ready Fd Resolution LeaseRole | Closing Fd | Closed | Moved HeldExecutable | Unknown Fd
newtype ExecutableLease = ExecutableLease (MVar Slot)
data HeldState = Live Integer | HeldClosing | HeldClosed | HeldUnknown
data BorrowRelease = BorrowNew | BorrowActivating | BorrowNotAcquired | BorrowPending | BorrowReleased | BorrowUnknown
-- Exactly one package-private owner; no external constructor from an FD.
data HeldExecutable = HeldExecutable Fd (MVar HeldState) !LeaseRole
-- Opaque per-acquisition release state; constructor never leaves this module.
data HeldBorrow = HeldBorrow Fd (MVar BorrowRelease) (MVar HeldState)

-- No syscall, callback, or external action is run inside these state operations.
transition :: MVar a -> (a -> (a,b)) -> IO b
transition gate f = uninterruptibleMask_ $ modifyMVar gate (pure . f)
observe :: MVar a -> (a -> b) -> IO b
observe gate f = uninterruptibleMask_ $ withMVar gate (pure . f)
newExecutableLease :: IO ExecutableLease
newExecutableLease = ExecutableLease <$> newMVar Empty
executableLeaseState :: ExecutableLease -> IO LeaseState
executableLeaseState (ExecutableLease gate) = observe gate $ \s -> case s of
 Empty -> EmptyLease; Building -> BuildingLease; Pending _ -> PendingLease
 Ready _ _ _ -> ReadyLease; Closing _ -> ClosingLease; Closed -> ClosedLease
 Moved _ -> MovedLease; Unknown _ -> UncertainLease

-- The only acquisition route consumes bytes read from the original held inode.
-- A duplicate is made pending before the resolver's outer parent and close checks.
acquireExecutableLease :: ExecutableLease -> Root -> [Pin] -> B.ByteString -> [Link] -> Integer -> B.ByteString -> LeaseRole -> IO (Either ResolveError ())
acquireExecutableLease lease root pins path links size digest role =
 acquireExecutableLeaseWithHooks lease root pins path links size digest role noHooks (pure ())

-- Package-private source fixture hook after Pending; no raw FD is exposed.
acquireExecutableLeaseWithHooks :: ExecutableLease -> Root -> [Pin] -> B.ByteString -> [Link] -> Integer -> B.ByteString -> LeaseRole -> Hooks -> IO () -> IO (Either ResolveError ())
acquireExecutableLeaseWithHooks lease@(ExecutableLease gate) root pins path links size digest role hooks afterPending = mask $ \restore -> do
 admitted <- transition gate $ \s -> case s of Empty -> (Building,True); _ -> (s,False)
 if not admitted then pure (Left OsFailure) else do
  outcome <- try (restore (resolveSnapshotVia root pins path links size 67108864 digest hooks consume)) :: IO (Either SomeException (Either ResolveError (Resolution,())))
  case outcome of
   Right (Right (receipt,())) -> do
    promoted <- transition gate $ \s -> case s of Pending fd -> (Ready fd receipt role,True); _ -> (s,False)
    pure (if promoted then Right () else Left OsFailure)
   Right (Left e) -> do _ <- discardPending lease; pure (Left e)
   Left e -> do
    cleanup <- try (discardPending lease) :: IO (Either SomeException (Either LeaseError ()))
    case (fromException e :: Maybe SomeAsyncException, cleanup) of
     (Just _,_) -> throwIO e
     (_,Left c) -> case (fromException c :: Maybe SomeAsyncException) of Just _ -> throwIO c; Nothing -> pure (Left OsFailure)
     _ -> pure (Left OsFailure)
 where
  consume readFd _ = mask $ \_ -> do
   fd <- clone readFd
   let publish = do
        accepted <- transition gate $ \s -> case s of Building -> (Pending fd,True); _ -> (s,False)
        if accepted then pure () else ioError (userError "executable pending state changed")
       recover = do
        needsClose <- transition gate $ \s -> case s of
         Pending existing | existing == fd -> (s,False)
         Building -> (Closing fd,True)
         _ -> (s,False)
        if needsClose then do _ <- closeSlot gate fd; pure () else pure ()
   published <- try publish :: IO (Either SomeException ())
   case published of
    Right () -> afterPending
    Left original -> do
     cleanup <- try recover :: IO (Either SomeException ())
     case (fromException original :: Maybe SomeAsyncException,cleanup) of
      (Just _,_) -> throwIO original
      (_,Left other) -> case (fromException other :: Maybe SomeAsyncException) of Just _ -> throwIO other; Nothing -> throwIO original
      _ -> throwIO original

discardPending :: ExecutableLease -> IO (Either LeaseError ())
discardPending (ExecutableLease gate) = mask $ \_ -> do
 chosen <- transition gate $ \s -> case s of
  Building -> (Closed,Right Nothing)
  Pending fd -> (Closing fd,Right (Just fd))
  Unknown _ -> (s,Left LeaseCloseUncertain)
  _ -> (s,Left LeaseBusy)
 case chosen of
  Left e -> pure (Left e)
  Right Nothing -> pure (Right ())
  Right (Just fd) -> closeSlot gate fd
closeSlot :: MVar Slot -> Fd -> IO (Either LeaseError ())
closeSlot gate fd = do
 result <- try (closeFd fd) :: IO (Either SomeException ())
 _ <- transition gate $ \_ -> case result of Right () -> (Closed,()); Left _ -> (Unknown fd,())
 case result of
  Right () -> pure (Right ())
  Left e -> case (fromException e :: Maybe SomeAsyncException) of Just _ -> throwIO e; Nothing -> pure (Left LeaseCloseUncertain)
retireExecutableLease :: ExecutableLease -> IO (Either LeaseError ())
retireExecutableLease (ExecutableLease gate) = mask $ \_ -> do
 chosen <- transition gate $ \s -> case s of
  Empty -> (Closed,Right Nothing)
  Ready fd _ _ -> (Closing fd,Right (Just (Left fd)))
  Moved held -> (s,Right (Just (Right held)))
  Unknown _ -> (s,Left LeaseCloseUncertain); Closed -> (s,Left LeaseClosed)
  _ -> (s,Left LeaseBusy)
 case chosen of
  Left e -> pure (Left e)
  Right Nothing -> pure (Right ())
  Right (Just (Left fd)) -> closeSlot gate fd
  Right (Just (Right held)) -> do
   outcome <- retireHeld held
   case outcome of
    Right () -> do _ <- transition gate (\_ -> (Closed,())); pure ()
    _ -> pure ()
   pure outcome

-- Holder cell allocation occurs before ownership transfer. Failure restores Ready.
issueReadyExecutable :: ExecutableLease -> IO (Maybe (HeldExecutable,Resolution,LeaseRole))
issueReadyExecutable (ExecutableLease gate) = mask $ \_ -> do
 holder <- newMVar (Live 0)
 transition gate $ \s -> case s of
  Ready fd receipt role -> let held = HeldExecutable fd holder role in (Moved held,Just (held,receipt,role))
  _ -> (s,Nothing)

-- Checked data snapshot only; this does not create a borrow or authority.
observeHeldRole :: HeldExecutable -> IO (Either LeaseError LeaseRole)
observeHeldRole (HeldExecutable _ gate role) = observe gate $ \state -> case state of
 Live _ -> Right role
 HeldClosing -> Left LeaseBusy
 HeldClosed -> Left LeaseClosed
 HeldUnknown -> Left LeaseCloseUncertain

borrowHeld :: HeldExecutable -> IO (Either LeaseError (FilePath,IO ()))
borrowHeld held = mask $ \_ -> do
 result <- borrowHeldInterruptible held
 case result of
  Left err -> pure (Left err)
  Right (path,_,release) -> pure (Right (path,release)) `onException` release

-- Adds an interruptible release action that blocks on the state MVar under
-- normal mask (interruptible by System.Timeout.timeout while contended) and
-- commits Live (n-1) + released=True atomically once acquired, restoring
-- released=False without mutating Live n if interrupted while waiting.
-- Both routes share exactly one sticky release implementation. Acquisition
-- callbacks run only while the held-state gate is full, never under that gate.
-- Only the internal acquisition can construct this exact per-borrow capability.
-- The normal legacy operation and the nonblocking operation share its one state.
releaseHeldNow :: HeldBorrow -> IO Bool
releaseHeldNow (HeldBorrow _ released gate) = mask $ \_ -> do
 state <- takeMVar released
 case state of
  BorrowReleased -> putMVar released BorrowReleased >> pure True
  BorrowUnknown -> putMVar released BorrowUnknown >> pure False
  BorrowNew -> putMVar released BorrowNew >> pure False
  BorrowActivating -> putMVar released BorrowActivating >> pure False
  BorrowNotAcquired -> putMVar released BorrowNotAcquired >> pure False
  BorrowPending -> do
   ownerState <- takeMVar gate `onException` putMVar released BorrowPending
   uninterruptibleMask_ $ case ownerState of
    Live n | n > 0 -> do
     putMVar gate (Live (n - 1))
     putMVar released BorrowReleased
     pure True
    _ -> do
     putMVar gate HeldUnknown
     putMVar released BorrowUnknown
     pure False

-- Legacy cleanup only. This can block; it must never be invoked while holding
-- the owner stop gate or treated as bounded by a timeout.
releaseHeldBorrow :: HeldBorrow -> IO ()
releaseHeldBorrow capability = uninterruptibleMask_ (releaseHeldNow capability >> pure ())

-- Owner may call this while it holds its own stop gate and has checked its
-- original deadline. Nothing means this release attempt made no decrement;
-- an in-flight activation may still commit, so Nothing is not a no-borrow
-- receipt. Just False is sticky uncertainty; Just True is only this exact
-- capability's release receipt.
tryReleaseHeld :: HeldBorrow -> IO (Maybe Bool)
tryReleaseHeld (HeldBorrow _ released gate) = mask $ \_ -> do
 claim <- tryTakeMVar released
 case claim of
  Nothing -> pure Nothing
  Just BorrowReleased -> putMVar released BorrowReleased >> pure (Just True)
  Just BorrowUnknown -> putMVar released BorrowUnknown >> pure (Just False)
  Just BorrowNew -> putMVar released BorrowNew >> pure Nothing
  Just BorrowActivating -> putMVar released BorrowActivating >> pure Nothing
  Just BorrowNotAcquired -> putMVar released BorrowNotAcquired >> pure Nothing
  Just BorrowPending -> do
   ownerState <- tryTakeMVar gate `onException` putMVar released BorrowPending
   case ownerState of
    Nothing -> putMVar released BorrowPending >> pure Nothing
    Just state -> uninterruptibleMask_ $ case state of
     Live n | n > 0 -> do
      putMVar gate (Live (n - 1))
      putMVar released BorrowReleased
      pure (Just True)
     _ -> do
      putMVar gate HeldUnknown
      putMVar released BorrowUnknown
      pure (Just False)

-- Allocate the unique owner-retainable capability BEFORE any borrow count
-- changes. Owner must retain it before calling activateHeldBorrowWhile.
prepareHeldBorrow :: HeldExecutable -> IO HeldBorrow
prepareHeldBorrow (HeldExecutable fd gate _) = HeldBorrow fd <$> newMVar BorrowNew <*> pure gate

-- True is a terminal receipt for this exact capability: activation returned
-- without acquiring. Busy, new, in-flight, successful and uncertain are False.
tryHeldBorrowNotAcquired :: HeldBorrow -> IO Bool
tryHeldBorrowNotAcquired (HeldBorrow _ released _) = do
 state <- tryReadMVar released
 pure $ case state of Just BorrowNotAcquired -> True; _ -> False

-- Single-use acquisition for an already owner-retained capability. All
-- cancellation observations and waits occur outside held/release locks.
-- A thrown exception retains the capability; no cleanup or no-borrow receipt
-- is inferred. The owner still rechecks its original start/stop before spawn.
activateHeldBorrowWhile :: HeldBorrow -> IO Bool -> IO () -> IO (Maybe (Either LeaseError FilePath))
activateHeldBorrowWhile (HeldBorrow (Fd fd) released gate) cancelled pause = mask $ \_ -> do
 pid <- getProcessID
 let path = "/proc/" ++ show pid ++ "/fd/" ++ show fd
 started <- tryTakeMVar released
 case started of
  Nothing -> pure (Just (Left LeaseBusy))
  Just BorrowNew -> do
   putMVar released BorrowActivating
   let markStopped = do
        state <- tryTakeMVar released
        case state of
         Just BorrowActivating -> putMVar released BorrowNotAcquired >> pure Nothing
         Just other -> putMVar released other >> pure (Just (Left LeaseBusy))
         Nothing -> pure (Just (Left LeaseBusy))
       loop = do
        stopped <- cancelled
        if stopped then markStopped else do
         state <- tryTakeMVar released
         case state of
          Nothing -> pause >> loop
          Just BorrowActivating -> do
           slot <- tryTakeMVar gate `onException` putMVar released BorrowActivating
           case slot of
            Nothing -> putMVar released BorrowActivating >> pause >> loop
            Just heldState -> uninterruptibleMask_ $ case heldState of
             Live n -> do
              putMVar gate (Live (n+1))
              putMVar released BorrowPending
              pure (Just (Right path))
             _ -> do
              putMVar gate heldState
              putMVar released BorrowNotAcquired
              pure (Just (Left LeaseClosed))
          Just other -> putMVar released other >> pure (Just (Left LeaseBusy))
   loop
  Just other -> putMVar released other >> pure (Just (Left LeaseBusy))

borrowHeldWith :: (MVar HeldState -> IO (Maybe Bool)) -> HeldExecutable
 -> IO (Maybe (Either LeaseError (FilePath,IO Bool,IO (),HeldBorrow)))
borrowHeldWith acquire (HeldExecutable (Fd fd) gate _) = mask $ \_ -> do
 released <- newMVar BorrowPending
 pid <- getProcessID
 let capability = HeldBorrow (Fd fd) released gate
     releaseNow = releaseHeldNow capability
     release = releaseHeldBorrow capability
     path = "/proc/" ++ show pid ++ "/fd/" ++ show fd
 accepted <- acquire gate
 case accepted of
  Nothing -> pure Nothing
  Just False -> pure (Just (Left LeaseClosed))
  Just True -> pure (Just (Right (path,releaseNow,release,capability))) `onException` release

borrowHeldInterruptible :: HeldExecutable -> IO (Either LeaseError (FilePath,IO Bool,IO ()))
borrowHeldInterruptible held = mask $ \_ -> do
 result <- borrowHeldWith (\gate -> Just <$> transition gate (\s -> case s of
  Live n -> (Live (n+1),True); _ -> (s,False))) held
 case result of
  Just (Left err) -> pure (Left err)
  Just (Right (path,releaseNow,release,_)) -> pure (Right (path,releaseNow,release))
  Nothing -> pure (Left LeaseClosed)

-- Nothing proves this invocation did not increment the held borrow count.
-- Caller stays masked until the returned release capability is retained.
-- cancelled/pause are trusted non-authoritative scheduler observations: the
-- owning caller rechecks the same original start and stop state before spawn.
borrowHeldWhile :: HeldExecutable -> IO Bool -> IO ()
 -> IO (Maybe (Either LeaseError (FilePath,IO Bool,IO (),HeldBorrow)))
borrowHeldWhile held cancelled pause = borrowHeldWith acquire held
 where
  acquire gate = mask $ \_ -> let
   loop = do
    stopped <- cancelled
    if stopped then pure Nothing else do
     slot <- tryTakeMVar gate
     case slot of
      Nothing -> pause >> loop
      Just st -> case st of
       Live n -> putMVar gate (Live (n+1)) >> pure (Just True)
       _ -> putMVar gate st >> pure (Just False)
   in loop

retireHeld :: HeldExecutable -> IO (Either LeaseError ())
retireHeld (HeldExecutable fd gate _) = mask $ \_ -> do
 chosen <- transition gate $ \s -> case s of
  Live 0 -> (HeldClosing,Right ()); Live _ -> (s,Left LeaseBusy)
  HeldUnknown -> (s,Left LeaseCloseUncertain); HeldClosed -> (s,Left LeaseClosed)
  HeldClosing -> (s,Left LeaseBusy)
 case chosen of
  Left e -> pure (Left e)
  Right () -> do
   result <- try (closeFd fd) :: IO (Either SomeException ())
   _ <- transition gate $ \_ -> case result of Right () -> (HeldClosed,()); Left _ -> (HeldUnknown,())
   case result of Right () -> pure (Right ()); Left e -> case (fromException e :: Maybe SomeAsyncException) of Just _ -> throwIO e; Nothing -> pure (Left LeaseCloseUncertain)
