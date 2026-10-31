{-# LANGUAGE ScopedTypeVariables #-}
module Warlock.Platform.Executable.Internal
 (ExecutableLease, HeldExecutable, LeaseRole(..), LeaseState(..), LeaseError(..)
 ,newExecutableLease, acquireExecutableLease, acquireExecutableLeaseWithHooks, issueReadyExecutable, retireExecutableLease
 ,executableLeaseState, borrowHeld, retireHeld) where

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
-- Exactly one package-private owner; no external constructor from an FD.
data HeldExecutable = HeldExecutable Fd (MVar HeldState)

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
  Ready fd receipt role -> let held = HeldExecutable fd holder in (Moved held,Just (held,receipt,role))
  _ -> (s,Nothing)

borrowHeld :: HeldExecutable -> IO (Either LeaseError (FilePath,IO ()))
borrowHeld held@(HeldExecutable (Fd fd) gate) = mask $ \_ -> do
 released <- newMVar False
 pid <- getProcessID
 let release = uninterruptibleMask_ $ modifyMVar_ released $ \done ->
      if done then pure True else case held of
       HeldExecutable _ owner -> do
        modifyMVar_ owner $ \s -> case s of Live n | n > 0 -> pure (Live (n-1)); _ -> pure HeldUnknown
        pure True
     path = "/proc/" ++ show pid ++ "/fd/" ++ show fd
 accepted <- transition gate $ \s -> case s of Live n -> (Live (n+1),True); _ -> (s,False)
 if not accepted then pure (Left LeaseClosed) else pure (Right (path,release)) `onException` release

retireHeld :: HeldExecutable -> IO (Either LeaseError ())
retireHeld (HeldExecutable fd gate) = mask $ \_ -> do
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
