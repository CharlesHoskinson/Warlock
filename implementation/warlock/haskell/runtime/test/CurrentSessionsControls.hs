{-# LANGUAGE CPP #-}
-- Root harness must supply actual concurrently live runSelectedDetailed
-- Sessions, resolver identities, endpoint FDs and actual recvmsg credentials.
-- No fake Session or constructed credential is a positive control.
module CurrentSessionsControls (singleSession, oldSide, oldDrainingSide, newSide, exhaustion, delayedOldReservation, foreignEndpoint, expiredSession) where
import Control.Concurrent.MVar (MVar,putMVar,takeMVar)
import Control.Exception (finally,try,throwIO,SomeException,AsyncException(ThreadKilled),fromException)
import Control.Monad (unless)
import Data.IORef (newIORef,readIORef,modifyIORef',writeIORef)
import System.Posix.Types (Fd)
import Warlock.Bootstrap.CurrentSessions
import Warlock.Bootstrap.ScopedPeer (PeerRefusal(..),ScopeStatus(..),authenticateFragment,withAdmission)
import Warlock.Capture.Process (Session)
import Warlock.Platform.Resolver.Internal (Identity,LeaseRole)
import Warlock.Transport.PeerCredentials (PeerCredential(..))

check :: String -> Bool -> IO ()
check label yes = unless yes (ioError (userError label))

singleSession :: Session -> Fd -> Identity -> LeaseRole -> PeerCredential -> IO ()
singleSession session fd ident role credential = do
 authority <- newCurrentSessions
 dead <- newRegistration authority
 _ <- retireRegistration dead
 called <- newIORef False
 refused <- withApprovedOwnedPeer dead session fd ident role (\_ -> writeIORef called True)
 wasCalled <- readIORef called
 check "retire before install" (refused == Left ScopeClosed && not wasCalled)
#ifdef CURRENT_SESSIONS_TEST
 late <- newRegistration authority
 lateCalled <- newIORef False
 lateResult <- withApprovedBeforeInstallForTest late session fd ident role
  (retireRegistration late >> pure ()) (\_ -> writeIORef lateCalled True)
 lateRan <- readIORef lateCalled
 check "retire after scope construction before install" (lateResult == Left ScopeClosed && not lateRan)
 killed <- newRegistration authority
 interrupted <- try (withApprovedBeforeInstallForTest killed session fd ident role
  (throwIO ThreadKilled) (\_ -> pure ())) :: IO (Either SomeException (Either PeerRefusal ()))
 again <- withApprovedOwnedPeer killed session fd ident role (\_ -> pure ())
 check "async before install retained and registration retired" (case interrupted of
  Left e -> (fromException e :: Maybe AsyncException) == Just ThreadKilled && again == Left ScopeClosed
  Right _ -> False)
#endif
 reg <- newRegistration authority
 effects <- newIORef (0 :: Int)
 retained <- newIORef Nothing
 result <- withApprovedOwnedPeer reg session fd ident role $ \scope -> do
  writeIORef retained (Just scope)
  good <- authenticateFragment scope credential
  check "actual current sender" (good == Right ())
  wrongPid <- authenticateFragment scope (credential {peerPid = 0})
  wrongUid <- authenticateFragment scope (credential {peerUid = if peerUid credential == 0 then 1 else 0})
  check "foreign sender refused" (wrongPid == Left ForeignProcess && wrongUid == Left ForeignUser)
  duplicate <- withApprovedOwnedPeer reg session fd ident role (\_ -> modifyIORef' effects (+100))
  check "duplicate refuses without retiring original" (duplicate == Left ScopeClosed)
  accepted <- withAdmission scope credential (modifyIORef' effects (+1))
  check "real admitted callback" (accepted == Right ())
 check "scope returned" (result == Right ())
 previous <- readIORef retained
 case previous of
  Nothing -> ioError (userError "scope missing")
  Just scope -> do
   later <- withAdmission scope credential (modifyIORef' effects (+100))
   check "retired scope refuses" (later == Left ScopeClosed)
 count <- readIORef effects
 check "exactly once" (count == 1)

-- The root harness runs each side *inside its own actual selected child
-- conversation*, with its own live Session/peer/credential. It must bound and
-- join both workers and retain both Sessions/owners until the callbacks return.
oldSide :: Registration -> Session -> Fd -> Identity -> LeaseRole -> PeerCredential
        -> MVar () -> MVar () -> MVar () -> IO ()
oldSide old session fd ident role credential oldChecked newPublished oldDone =
 (do result <- withApprovedOwnedPeer old session fd ident role $ \scope -> do
       authenticated <- authenticateFragment scope credential
       check "old initially authenticated" (authenticated == Right ())
       putMVar oldChecked ()
       takeMVar newPublished
       after <- withAdmission scope credential (ioError (userError "stale callback executed") :: IO ())
       check "replacement revoked old admission" (after == Left ScopeClosed || after == Left ForeignSession)
     check "old wrapper" (result == Right ())) `finally` putMVar oldDone ()

-- Alternate old side: admission begins before replacement; its callback is
-- allowed to drain exactly once while its original Session remains retained.
oldDrainingSide :: Registration -> Session -> Fd -> Identity -> LeaseRole -> PeerCredential
                -> MVar () -> MVar () -> MVar () -> IO ()
oldDrainingSide old session fd ident role credential oldChecked newPublished oldDone =
 (do effects <- newIORef (0 :: Int)
     result <- withApprovedOwnedPeer old session fd ident role $ \scope -> do
       admitted <- withAdmission scope credential $ do
        putMVar oldChecked ()
        takeMVar newPublished
        state <- retireRegistration old
        check "retired admitted callback drains" (state == ScopeDraining 1)
        modifyIORef' effects (+1)
       check "old admitted callback completes" (admitted == Right ())
     check "old draining wrapper" (result == Right ())
     count <- readIORef effects
     check "old drain exactly once" (count == 1)) `finally` putMVar oldDone ()

newSide :: Registration -> Registration -> Session -> Fd -> Identity -> LeaseRole -> PeerCredential
        -> MVar () -> MVar () -> MVar () -> IO ()
newSide old new session fd ident role credential oldChecked newPublished oldDone = do
 takeMVar oldChecked
 result <- withApprovedOwnedPeer new session fd ident role $ \scope -> do
  putMVar newPublished ()
  takeMVar oldDone
  _ <- retireRegistration old
  accepted <- withAdmission scope credential (pure ())
  check "old cleanup leaves newer admission" (accepted == Right ())
 check "new wrapper" (result == Right ())

-- Compiled only for the internal fixture build; production export omits the
-- test seed. Caller still supplies a genuinely live selected Session.
exhaustion :: Session -> Fd -> Identity -> LeaseRole -> IO ()
#ifdef CURRENT_SESSIONS_TEST
exhaustion session fd ident role = do
 authority <- newCurrentSessionsAtForTest maxBound
 lastReg <- newRegistration authority
 first <- withApprovedOwnedPeer lastReg session fd ident role (\_ -> pure ())
 check "last generation usable" (first == Right ())
 next <- newRegistration authority
 refused <- withApprovedOwnedPeer next session fd ident role (\_ -> pure ())
 check "generation exhaustion refuses" (refused == Left ScopeClosed)
#else
exhaustion _ _ _ _ = ioError (userError "fixture test macro required")
#endif

-- Both Sessions and both real credentials must remain live; the newer callback
-- completes first, leaving current empty. An older reserved generation must
-- still be refused by the publication high watermark.
delayedOldReservation :: Session -> Fd -> Identity -> LeaseRole
                      -> Session -> Fd -> Identity -> LeaseRole -> PeerCredential -> IO ()
#ifdef CURRENT_SESSIONS_TEST
delayedOldReservation older oldFd oldIdentity oldRole newer newFd newIdentity newRole credential = do
 authority <- newCurrentSessions
 old <- newRegistration authority
 new <- newRegistration authority
 called <- newIORef False
 result <- withApprovedBeforeInstallForTest old older oldFd oldIdentity oldRole
  (do newerResult <- withApprovedOwnedPeer new newer newFd newIdentity newRole $ \scope -> do
        accepted <- withAdmission scope credential (pure ())
        check "newer generation admitted" (accepted == Right ())
      check "newer generation complete" (newerResult == Right ()))
  (\_ -> writeIORef called True)
 wasCalled <- readIORef called
 check "delayed older generation cannot publish" (result == Left ScopeClosed && not wasCalled)
#else
delayedOldReservation _ _ _ _ _ _ _ _ _ = ioError (userError "fixture test macro required")
#endif

-- Root supplies an unrelated real held FD; no synthetic credential is a
-- positive. Authentication callback must refuse before any policy handler.
foreignEndpoint :: Session -> Fd -> Identity -> LeaseRole -> PeerCredential -> IO ()
foreignEndpoint session unrelatedFd ident role credential = do
 authority <- newCurrentSessions
 reg <- newRegistration authority
 result <- withApprovedOwnedPeer reg session unrelatedFd ident role $ \scope ->
  withAdmission scope credential (ioError (userError "foreign endpoint effect executed") :: IO ())
 check "foreign endpoint refused" (result == Right (Left EndpointChanged))

-- Called after root has closed the actual original Session scope; retain the
-- Session value solely to verify that it cannot authorize another callback.
expiredSession :: Session -> Fd -> Identity -> LeaseRole -> IO ()
expiredSession expired fd ident role = do
 authority <- newCurrentSessions
 reg <- newRegistration authority
 called <- newIORef False
 result <- withApprovedOwnedPeer reg expired fd ident role (\_ -> writeIORef called True)
 ran <- readIORef called
 check "expired Session refused" (result == Left ScopeUnavailable && not ran)
