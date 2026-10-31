{-# LANGUAGE CPP #-}
-- Trusted bootstrap internal module; never expose Scope constructors to wire clients.
-- This only authenticates an owned transport sender, not native authority.
module Warlock.Bootstrap.ScopedPeer
 (Scope, ScopeStatus(..), PeerRefusal(..), withScopedOwnedPeer, authenticateFragment, withAdmission, retireScope
#ifdef WARLOCK_SCOPED_PEER_TESTING
 ,withAdmissionAfterAuthenticationForTest
#endif
 ) where

import Control.Concurrent (ThreadId, myThreadId)
import Control.Concurrent.MVar (MVar, modifyMVar, modifyMVar_, newMVar, readMVar)
import Control.Exception (IOException, finally, mask, try, uninterruptibleMask_)
import Data.Word (Word64)
import System.Posix.Files (deviceID, fileID, fileOwner, getFdStatus, getFileStatus)
import System.Posix.Types (Fd, UserID)
import System.Posix.User (getRealUserID)
import Warlock.Capture.Process (Session, SessionObservation(..), observeSession)
import Warlock.Platform.Resolver (Identity(..))
import Warlock.Platform.Executable (LeaseRole(..))
import Warlock.Protocol.PeerCredential (PeerCredential, credentialPid, credentialUid)

data PeerRefusal = WrongRole | ScopeClosed | WrongThread | ScopeUnavailable | ForeignProcess
 | ForeignUser | ForeignSession | ExecutableChanged | EndpointChanged | ObservationChanged | ObservationFailed
 deriving (Eq,Show)
data ScopeStatus = ScopeLive !Int | ScopeDraining !Int | ScopeRetired deriving (Eq,Show)
data Scope = Scope !ThreadId !(MVar ScopeStatus) !Session !SessionObservation !Fd !Identity !UserID !Word64 !(IO Word64)

-- Only the resolver-selected bootstrap aggregate calls this while inside the
-- runSelectedDetailed conversation. No process or descriptor is adopted here.
-- The scope may not dispatch from another thread, and its lifetime ends before
-- the conversation returns or its exception escapes. This ensures the sole
-- process owner retains the unreaped child throughout synchronous admission.
withScopedOwnedPeer :: Session -> Fd -> Identity -> LeaseRole -> Word64 -> IO Word64
                    -> (Scope -> IO a) -> IO (Either PeerRefusal a)
withScopedOwnedPeer session peer identity role epoch currentEpoch action
 | role /= UiImage = pure (Left WrongRole)
 | epoch == 0 = pure (Left ForeignSession)
 | otherwise = mask $ \restore -> do
    initial <- observeSession session
    case initial of
     Left _ -> pure (Left ScopeUnavailable)
     Right observation -> do
      tid <- myThreadId
      live <- newMVar (ScopeLive 0)
      uid <- getRealUserID
      let scope = Scope tid live session observation peer identity uid epoch currentEpoch
      result <- restore (action scope) `finally` (retireScope scope >> pure ())
      pure (Right result)

-- This is an internal fragment check only; its result is not a durable token.
-- Each credential comes from recvmsg, never JSON, SO_PEERCRED or a caller UID.
authenticateFragment :: Scope -> PeerCredential -> IO (Either PeerRefusal ())
authenticateFragment scope@(Scope _ _ _ initial _ _ uid _ _) credential
 | toInteger (credentialPid credential) /= toInteger (observedPid initial) = pure (Left ForeignProcess)
 | toInteger (credentialUid credential) /= toInteger uid = pure (Left ForeignUser)
 | otherwise = current scope

-- Synchronous checked dispatch only; the caller must use the existing ingress
-- gate, whose retirement serializes admission and drains admitted callbacks.
-- No checked boolean or capability escapes this scope.
withAdmission :: Scope -> PeerCredential -> IO a -> IO (Either PeerRefusal a)
#ifdef WARLOCK_SCOPED_PEER_TESTING
withAdmission = withAdmissionAfterAuthenticationForTest (pure ())
-- Test component only. Runs after the real authentication returned Right and
-- before claiming Scope admission; no Scope/CurrentSessions lock is held.
withAdmissionAfterAuthenticationForTest :: IO () -> Scope -> PeerCredential -> IO a -> IO (Either PeerRefusal a)
withAdmissionAfterAuthenticationForTest afterAuthentication scope@(Scope _ state _ _ _ _ _ _ _) credential action = mask $ \restore -> do
#else
withAdmission scope@(Scope _ state _ _ _ _ _ _ _) credential action = mask $ \restore -> do
#endif
 checked <- restore (authenticateFragment scope credential)
 case checked of
  Left reason -> pure (Left reason)
  Right () -> do
#ifdef WARLOCK_SCOPED_PEER_TESTING
   restore afterAuthentication
#endif
   admitted <- modifyMVar state $ \status -> case status of
    ScopeLive 0 -> pure (ScopeLive 1,True)
    _ -> pure (status,False)
   if not admitted then pure (Left ScopeClosed) else do
    result <- restore action `finally` uninterruptibleMask_ (modifyMVar_ state (\status -> pure $ case status of
      ScopeLive _ -> ScopeLive 0
      ScopeDraining _ -> ScopeRetired
      ScopeRetired -> ScopeRetired))
    pure (Right result)

-- The owning supervisor calls this when the approved lifetime is retired.
-- A callback admitted before retirement may finish; no later admission starts.
retireScope :: Scope -> IO ScopeStatus
retireScope (Scope _ state _ _ _ _ _ _ _) = uninterruptibleMask_ $ modifyMVar state $ \status ->
 let next = case status of ScopeLive 0 -> ScopeRetired; ScopeLive n -> ScopeDraining n; other -> other
 in pure (next,next)

current :: Scope -> IO (Either PeerRefusal ())
current (Scope owner live session initial peer (Identity expectedDevice expectedInode) uid epoch epochSource) = do
 thread <- myThreadId
 status <- readMVar live
 let active = case status of ScopeLive _ -> True; _ -> False
 currentUid <- getRealUserID
 currentEpoch <- epochSource
 if not active then pure (Left ScopeClosed) else if thread /= owner then pure (Left WrongThread) else if currentUid /= uid then pure (Left ForeignUser) else if currentEpoch /= epoch then pure (Left ForeignSession) else do
  observed <- observeSession session
  case observed of
   Left _ -> pure (Left ScopeUnavailable)
   Right before | before /= initial -> pure (Left ObservationChanged)
   Right before -> do
    let prefix = "/proc/" ++ show (observedPid before)
    facts <- (try (do
      executable <- getFileStatus (prefix ++ "/exe")
      process <- getFileStatus prefix
      inherited <- getFileStatus (prefix ++ "/fd/0")
      selected <- getFdStatus peer
      pure (toInteger (deviceID executable) == toInteger expectedDevice && toInteger (fileID executable) == toInteger expectedInode,
            deviceID inherited == deviceID selected && fileID inherited == fileID selected,
            fileOwner process == uid)) :: IO (Either IOException (Bool,Bool,Bool)))
    after <- observeSession session
    statusAfter <- readMVar live
    let stillLive = case statusAfter of ScopeLive _ -> True; _ -> False
    finalEpoch <- epochSource
    pure $ if not stillLive then Left ScopeClosed else if finalEpoch /= epoch then Left ForeignSession else case (facts,after) of
      (Left _,_) -> Left ObservationFailed
      (_,Left _) -> Left ScopeUnavailable
      (Right (exeOk,endpointOk,userOk),Right final)
       | final /= initial -> Left ObservationChanged
       | not exeOk -> Left ExecutableChanged
       | not endpointOk -> Left EndpointChanged
       | not userOk -> Left ForeignUser
       | otherwise -> Right ()
