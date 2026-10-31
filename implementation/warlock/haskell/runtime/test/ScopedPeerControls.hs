-- Root-only fixture functions; must run inside an actual selected child
-- conversation with its actual recvmsg credential and borrowed endpoint.
-- Deliberately modified credentials below are internal synthetic negatives,
-- not a claim that a kernel cross-user sender was exercised.
module ScopedPeerControls (exerciseOwnedPeer, exerciseForeignInputs) where
import Control.Concurrent (forkIO, newEmptyMVar, putMVar, takeMVar)
import Control.Monad (unless)
import Data.Word (Word64)
import Data.IORef (newIORef, readIORef, writeIORef, modifyIORef')
import System.Posix.Types (Fd)
import Warlock.Bootstrap.ScopedPeer
import Warlock.Capture.Process (Session)
import Warlock.Platform.Resolver.Internal (Identity(..),LeaseRole)
import Warlock.Transport.PeerCredentials (PeerCredential(..))

exerciseOwnedPeer :: Session -> Fd -> Identity -> LeaseRole -> Word64 -> IO Word64 -> PeerCredential -> IO ()
exerciseOwnedPeer session peer identity role epoch epochSource credential = do
 retained <- newIORef Nothing
 effects <- newIORef (0 :: Int)
 result <- withScopedOwnedPeer session peer identity role epoch epochSource $ \scope -> do
  writeIORef retained (Just scope)
  good <- authenticateFragment scope credential
  unless (good == Right ()) (ioError (userError "current real sender rejected"))
  let foreignPid = credential {peerPid = 0}
      foreignUid = credential {peerUid = if peerUid credential == 0 then 1 else 0}
  wrongPid <- authenticateFragment scope foreignPid
  wrongUid <- authenticateFragment scope foreignUid
  unless (wrongPid == Left ForeignProcess && wrongUid == Left ForeignUser)
    (ioError (userError "foreign identity accepted"))
  done <- newEmptyMVar
  _ <- forkIO (authenticateFragment scope credential >>= putMVar done)
  wrongThread <- takeMVar done
  unless (wrongThread == Left WrongThread) (ioError (userError "scope escaped thread"))
  positive <- withAdmission scope credential $ do
   -- Actual admission is already reserved: retirement must drain this one
   -- while refusing any later fragment or callback.
   retired <- newEmptyMVar
   _ <- forkIO (retireScope scope >>= putMVar retired)
   retirement <- takeMVar retired
   unless (retirement == ScopeDraining 1) (ioError (userError "in-flight drain"))
   blocked <- authenticateFragment scope credential
   unless (blocked == Left ScopeClosed) (ioError (userError "post-retirement fragment"))
   modifyIORef' effects (+1)
  unless (positive == Right ()) (ioError (userError "live admission refused"))
 case result of Left _ -> ioError (userError "live scope unavailable"); Right () -> pure ()
 saved <- readIORef retained
 case saved of
  Nothing -> ioError (userError "fixture did not retain observation")
  Just old -> do
   stale <- withAdmission old credential (modifyIORef' effects (+1))
   unless (stale == Left ScopeClosed) (ioError (userError "expired scope admitted"))
 count <- readIORef effects
 unless (count == 1) (ioError (userError "policy callback count"))

-- Inside the real selected-child callback, the first identity and endpoint are
-- resolver/owner observations. The deliberately changed inputs are test-only;
-- this does not claim a real cross-user or foreign-session kernel trace.
exerciseForeignInputs :: Session -> Fd -> Fd -> Identity -> LeaseRole -> Word64 -> PeerCredential -> IO ()
exerciseForeignInputs session peer wrongEndpoint (Identity dev inode) role epoch credential = do
 let changed = Identity dev (inode + 1)
 wrongExe <- withScopedOwnedPeer session peer changed role epoch (pure epoch) $ \scope -> authenticateFragment scope credential
 unless (wrongExe == Right (Left ExecutableChanged)) (ioError (userError "wrong executable accepted"))
 wrongFd <- withScopedOwnedPeer session wrongEndpoint (Identity dev inode) role epoch (pure epoch) $ \scope -> authenticateFragment scope credential
 unless (wrongFd == Right (Left EndpointChanged)) (ioError (userError "wrong endpoint accepted"))
 wrongEpoch <- withScopedOwnedPeer session peer (Identity dev inode) role epoch (pure (epoch + 1)) $ \scope -> authenticateFragment scope credential
 unless (wrongEpoch == Right (Left ForeignSession)) (ioError (userError "old session accepted"))
