{-# LANGUAGE ScopedTypeVariables #-}
-- TRUSTED INTERNAL bridge. Issuer must only call issueVerified after the
-- resolver's final checks, with exclusive ownership of the verified FD.
module Warlock.Capture.Process.Lease
 (HeldExecutable, issueVerified, borrowHeld, retireHeld, LeaseError(..)) where
import Control.Concurrent.MVar
import Control.Exception (SomeException, SomeAsyncException, fromException, mask, throwIO, try)
import System.Posix.IO (closeFd)
import System.Posix.Process (getProcessID)
import System.Posix.Types (Fd(..))

data LeaseState = Live Integer | Retired | Uncertain
data HeldExecutable = HeldExecutable Fd (MVar LeaseState)
data LeaseError = LeaseBusy | LeaseClosed | LeaseCloseUncertain deriving (Eq,Show)

-- Internal issuer obligation: fd is the exclusive, post-validation lease;
-- the issuer relinquishes all other close rights on successful issuance.
issueVerified :: Fd -> IO HeldExecutable
issueVerified fd = HeldExecutable fd <$> newMVar (Live 0)

-- Borrow is idempotently releasable. The action retains the lease itself.
borrowHeld :: HeldExecutable -> IO (Either LeaseError (FilePath, IO ()))
borrowHeld held@(HeldExecutable (Fd fd) state) = mask $ \_ -> do
 released <- newMVar False
 pid <- getProcessID
 accepted <- modifyMVar state $ \s -> case s of
  Live n -> pure (Live (n+1), True)
  _ -> pure (s, False)
 if not accepted then pure (Left LeaseClosed) else do
  let release = modifyMVar_ released $ \done -> if done then pure True else do
       case held of
        HeldExecutable _ st -> modifyMVar_ st $ \s -> case s of
         Live n | n > 0 -> pure (Live (n-1))
         _ -> pure Uncertain
       pure True
  pure (Right ("/proc/" ++ show pid ++ "/fd/" ++ show fd, release))

-- EINTR or async interruption may mean that the numeric fd was already closed;
-- never retry a close with the same number after an uncertain result.
retireHeld :: HeldExecutable -> IO (Either LeaseError ())
retireHeld (HeldExecutable fd state) = mask $ \_ -> do
 (result, deferred) <- modifyMVar state $ \s -> case s of
  Live 0 -> do
   closed <- try (closeFd fd) :: IO (Either SomeException ())
   case closed of
    Right () -> pure (Retired,(Right (),Nothing))
    Left ex -> pure (Uncertain,(Left LeaseCloseUncertain,Just ex))
  Live _ -> pure (s,(Left LeaseBusy,Nothing))
  Retired -> pure (s,(Left LeaseClosed,Nothing))
  Uncertain -> pure (s,(Left LeaseCloseUncertain,Nothing))
 case deferred of
  Just ex -> case (fromException ex :: Maybe SomeAsyncException) of
   Just _ -> throwIO ex
   Nothing -> pure result
  Nothing -> pure result
