{-# LANGUAGE CPP #-}
-- Trusted bootstrap internal authority. No wire constructor or native grant.
module Warlock.Bootstrap.CurrentSessions
 (CurrentSessions, Registration, newCurrentSessions, newRegistration,
  withApprovedOwnedPeer, retireRegistration
#ifdef CURRENT_SESSIONS_TEST
  , newCurrentSessionsAtForTest, withApprovedBeforeInstallForTest
#endif
 ) where

import Control.Concurrent.MVar (MVar, modifyMVar, newMVar, readMVar)
import Control.Exception (finally, mask, uninterruptibleMask_)
import Data.Word (Word64)
import System.Posix.Types (Fd)
import Warlock.Bootstrap.ScopedPeer (Scope, ScopeStatus(..), PeerRefusal(..), retireScope, withScopedOwnedPeer)
import Warlock.Capture.Process (Session)
import Warlock.Platform.Resolver (Identity)
import Warlock.Platform.Executable (LeaseRole)

data RegState = Empty | Reserved !Word64 | Published !Word64 !Scope | Retired !(Maybe (Word64,Scope))
data Authority = Authority !(Maybe Word64) !Word64 !(Maybe (MVar RegState,Word64,Scope))
newtype CurrentSessions = CurrentSessions (MVar Authority)
data Registration = Registration !CurrentSessions !(MVar RegState)

newCurrentSessions :: IO CurrentSessions
newCurrentSessions = CurrentSessions <$> newMVar (Authority (Just 1) 0 Nothing)
#ifdef CURRENT_SESSIONS_TEST
-- Test-only exhaustion seam; not present in the production module export.
newCurrentSessionsAtForTest :: Word64 -> IO CurrentSessions
newCurrentSessionsAtForTest n = CurrentSessions <$> newMVar (Authority (Just n) 0 Nothing)
#endif
newRegistration :: CurrentSessions -> IO Registration
newRegistration authority = Registration authority <$> newMVar Empty

-- MVar identity is private and retained, so a live registration cannot alias a
-- later one. Generations are consumed even on aborted setup and never reused.
reserve :: Registration -> IO (Either PeerRefusal Word64)
reserve (Registration (CurrentSessions authority) cell) = uninterruptibleMask_ $
 modifyMVar authority $ \a@(Authority next high current) ->
  modifyMVar cell $ \r -> case (r,next) of
   (Empty,Just generation) ->
    let following = if generation == maxBound then Nothing else Just (generation + 1)
    in pure (Reserved generation,(Authority following high current,Right generation))
   _ -> pure (r,(a,Left ScopeClosed))

-- Private epoch source: zero is never a generated epoch. Reading the current
-- authority occurs before ScopedPeer takes its finite admission lock.
epochSource :: CurrentSessions -> IO Word64
epochSource (CurrentSessions authority) = do
 Authority _ _ current <- readMVar authority
 pure $ case current of Nothing -> 0; Just (_,generation,_) -> generation

-- All multi-cell transitions use authority -> registration -> Scope. No
-- callback, socket or Session IO is performed under either owner lock.
install :: Registration -> Word64 -> Scope -> IO Bool
install (Registration (CurrentSessions authority) cell) generation scope = uninterruptibleMask_ $
 modifyMVar authority $ \a@(Authority next high current) ->
  modifyMVar cell $ \r -> case r of
   Reserved g | g == generation && generation > high -> do
    case current of Nothing -> pure (); Just (_,_,old) -> do _ <- retireScope old; pure ()
    pure (Published generation scope,(Authority next generation (Just (cell,generation,scope)),True))
   _ -> pure (r,(a,False))

-- This is admission retirement only; it does not certify socket or child exit.
retireRegistration :: Registration -> IO ScopeStatus
retireRegistration (Registration (CurrentSessions authority) cell) = uninterruptibleMask_ $
 modifyMVar authority $ \(Authority next high current) ->
  modifyMVar cell $ \r -> do
   let held = case r of Published g s -> Just (g,s); Retired x -> x; _ -> Nothing
   disposition <- case held of Nothing -> pure ScopeRetired; Just (_,scope) -> retireScope scope
   let current' = case (current,held) of
        (Just (owner,g,_),Just (mine,_)) | owner == cell && g == mine -> Nothing
        _ -> current
   pure (Retired held,(Authority next high current',disposition))

withApprovedOwnedPeer :: Registration -> Session -> Fd -> Identity -> LeaseRole
                      -> (Scope -> IO a) -> IO (Either PeerRefusal a)
withApprovedOwnedPeer registration session peer identity role action =
 runApproved registration session peer identity role (pure ()) action

#ifdef CURRENT_SESSIONS_TEST
-- Outside all locks, after Scope construction and before publication.
withApprovedBeforeInstallForTest :: Registration -> Session -> Fd -> Identity -> LeaseRole
                                 -> IO () -> (Scope -> IO a) -> IO (Either PeerRefusal a)
withApprovedBeforeInstallForTest = runApproved
#endif
runApproved :: Registration -> Session -> Fd -> Identity -> LeaseRole -> IO ()
            -> (Scope -> IO a) -> IO (Either PeerRefusal a)
runApproved registration@(Registration authority _) session peer identity role beforeInstall action = mask $ \restore -> do
 allocated <- reserve registration
 case allocated of
  Left refusal -> pure (Left refusal)
  Right generation -> (do
   scoped <- restore (withScopedOwnedPeer session peer identity role generation (epochSource authority) $ \scope -> do
     beforeInstall
     accepted <- install registration generation scope
     if accepted then Right <$> action scope else do
      _ <- retireScope scope
      pure (Left ScopeClosed))
   pure $ case scoped of Left refusal -> Left refusal; Right value -> value)
   `finally` (retireRegistration registration >> pure ())
