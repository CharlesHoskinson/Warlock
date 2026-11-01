{-# LANGUAGE OverloadedStrings #-}
{-# LANGUAGE RankNTypes #-}
-- PREPARATION DRAFT ONLY. No compile/test has been run. This exercises the
-- proposed public after-idle ingress API on real Unix sockets and actual kernel
-- SCM credentials with a same-process PID/UID/GID guard. It does not prove a
-- real selected child, held-pidfd guard, production bootstrap, native effect,
-- VM, GUI, original scenario or release. Run only through root's protected QA.
-- Targets the public receiveDesktopCredentialIngressAfterIdle production route.
-- Tests intentionally detect a partial frame crossing original D.
module DesktopIdleControls (run) where

import Control.Concurrent (forkIO, forkFinally, killThread, newEmptyMVar, putMVar, takeMVar, threadDelay)
import Control.Exception (SomeException, bracket, finally, onException)
import Control.Monad (forM_, unless, void)
import Data.IORef (IORef, modifyIORef', newIORef, readIORef, writeIORef)
import qualified Data.ByteString as B
import GHC.Clock (getMonotonicTimeNSec)
import qualified Network.Socket as S
import qualified Network.Socket.ByteString as N
import System.Posix.Process (getProcessID)
import System.Posix.User (getEffectiveGroupID, getEffectiveUserID)
import System.Timeout (timeout)
import Warlock.Protocol.CredentialIngress
import Warlock.Protocol.Ingress (ingressBinding, Direction(..), OfferResult(..), ActivationResult(..), ChannelError(..))
import qualified Warlock.Protocol.PeerCredential as P
import qualified Warlock.Protocol.Framing as F

check :: String -> Bool -> IO ()
check name ok = unless ok (ioError (userError name))
must :: Show e => Either e a -> IO a
must = either (ioError . userError . show) pure
now :: IO Integer
now = toInteger <$> getMonotonicTimeNSec

data Refusal = Foreign | Revoked deriving (Eq, Show)
data Fixture = Fixture CredentialIngress S.Socket (IORef Int) (IORef Int) (IORef Bool) (CredentialGuard Refusal)

-- The real recvmsg credential must match this process and the synchronous
-- guard checks it again at final dispatch. This deliberately does NOT pretend
-- to authenticate a selected child or establish a pidfd-backed custody scope.
fixtureGuard :: Integer -> Integer -> Integer -> IORef Int -> IORef Bool -> CredentialGuard Refusal
fixtureGuard pid uid gid seen revoked = CredentialGuard fragment admit
 where
  matches c = P.credentialPid c == pid && P.credentialUid c == uid && P.credentialGid c == gid
  fragment c = do
   modifyIORef' seen (+1)
   stopped <- readIORef revoked
   pure (if stopped then Left Revoked else if matches c then Right () else Left Foreign)
  admit c action = do
   stopped <- readIORef revoked
   if stopped then pure (Left Revoked) else if not (matches c) then pure (Left Foreign) else Right <$> action

withFixture :: Bool -> (Fixture -> IO ()) -> IO ()
withFixture desktop action = do
 owner <- must (ingressBinding "1" "2" "3")
 pid <- toInteger <$> getProcessID
 uid <- toInteger <$> getEffectiveUserID
 gid <- toInteger <$> getEffectiveGroupID
 calls <- newIORef 0
 observed <- newIORef 0
 revoked <- newIORef False
 let callback _ = modifyIORef' calls (+1)
 ingress <- (if desktop then newDesktopCredentialIngress else newCredentialIngress) owner FromElm callback callback
 (incoming,peer) <- S.socketPair S.AF_UNIX S.Stream S.defaultProtocol
 let closeBoth = void (retireCredentialIngress ingress) >> S.close peer
 offered <- transferCredentialSocket ingress incoming `onException` S.close peer
 check "socket offered" (offered == OfferAccepted)
 active <- activateCredentialIngress ingress `onException` closeBoth
 check "socket active" (active == ActivationLive)
 action (Fixture ingress peer calls observed revoked (fixtureGuard pid uid gid observed revoked)) `finally` closeBoth

-- One independent well-formed whole desktop commit, valid through the actual
-- desktop checked codec and matching the fixture's immutable binding.
desktopFrame :: B.ByteString -> IO B.ByteString
desktopFrame requestId = must $ F.desktopCommitPrefix $
 "{\"viewProtocol\":1,\"kind\":\"view-commit\",\"projection\":{\"viewProtocol\":1,\"kind\":\"view-frame\",\"revision\":\"1\",\"views\":[],\"focusOwner\":null,\"popupOwner\":null,\"frame\":{\"surfaceProtocol\":2,\"publication\":\"1\",\"lease\":\"0\",\"mode\":\"closed\",\"status\":\"controlled QA transport projection\",\"bar\":[{\"id\":\"qa:focus-valid\",\"domId\":\"focus-valid\",\"label\":\"QA control\",\"ariaLabel\":\"QA control\",\"detail\":\"\",\"enabled\":true,\"focusOnly\":false}],\"popup\":[]},\"announcer\":null,\"announcement\":null},\"requests\":[{\"protocolVersion\":3,\"kind\":\"catalog-request\",\"binding\":{\"lifetime\":\"1\",\"session\":\"2\",\"frontend\":\"3\"},\"requestId\":\"" <> requestId <> "\"}],\"focus\":[]}"

nativeFrame :: IO B.ByteString
nativeFrame = must $ F.prefix
 "{\"version\":1,\"kind\":\"negotiate\",\"body\":{\"binding\":{\"lifetime\":\"1\",\"session\":\"2\",\"frontend\":\"3\"},\"requestId\":\"8\"}}"

seedFirst :: Fixture -> Integer -> B.ByteString -> IO ()
seedFirst (Fixture ingress peer calls _ _ guard) originalD frame = do
 before <- now
 check "original D live before first frame" (before < originalD)
 N.sendAll peer frame
 let leftMicros = fromInteger (min 5000000 ((originalD-before) `div` 1000))
 first <- bounded "first frame under original D" leftMicros (receiveCredentialIngress ingress guard)
 after <- now
 count <- readIORef calls
 check "first real credential frame delivered under same D" (first == CredentialDelivered && count == 1 && after < originalD)

-- One immutable absolute monotonic D per fresh independent test fixture.
-- Deadlines here are test inputs, never replacements for a production D.
deadlineAfterSeconds :: Integer -> IO Integer
deadlineAfterSeconds secs = (+ (secs * 1000000000)) <$> now

-- Internal watchdog only fails a stuck control; it is never used as the
-- product deadline and no uncertain outcome is retried or treated as pass.
bounded :: String -> Int -> IO a -> IO a
bounded label micros action = do
 result <- timeout micros action
 maybe (ioError (userError (label ++ " watchdog"))) pure result

withSender :: IO () -> IO a -> IO a
withSender send action = bracket (forkIO send) killThread (const action)

-- Exercise the actual public desktop-only API, preserving its absolute D.
receiveCredentialIngressAfterIdle :: CredentialIngress -> CredentialGuard refusal -> Integer -> IO (CredentialIngressResult refusal)
receiveCredentialIngressAfterIdle ingress guard deadline = receiveDesktopCredentialIngressAfterIdle deadline ingress guard

expectTimeout :: String -> Fixture -> Integer -> IO ()
expectTimeout label (Fixture ingress _ calls _ _ guard) absoluteD = do
 result <- bounded label 9000000 (receiveCredentialIngressAfterIdle ingress guard absoluteD)
 count <- readIORef calls
 check (label ++ " times out with no further callback")
  (result == CredentialFrameRejected (CredentialTransport TimedOut) && count == 1)

run :: IO ()
run = do
 desktopFirst <- desktopFrame "7"
 desktopSecond <- desktopFrame "8"
 native <- nativeFrame
 -- First desktop receive is unchanged: no frame at all must time out on the
 -- original five-second transport path. Its fixture D was created first.
 withFixture True $ \(Fixture ingress _ calls _ _ guard) -> do
  originalD <- deadlineAfterSeconds 12
  started <- now
  result <- bounded "first frame timeout" 8500000 (receiveCredentialIngress ingress guard)
  finished <- now
  count <- readIORef calls
  check "first frame unchanged timeout" (result == CredentialFrameRejected (CredentialTransport TimedOut) && count == 0 && finished < originalD && finished-started >= 4500000000 && finished-started < 8500000000)
 -- Exactly one valid frame after genuinely more than five seconds of silence;
 -- first byte has real kernel SCM credentials and final guard admission.
 withFixture True $ \fixture@(Fixture ingress peer calls fragments _ guard) -> do
  originalD <- deadlineAfterSeconds 15
  seedFirst fixture originalD desktopFirst
  started <- now
  withSender (threadDelay 5300000 >> N.sendAll peer desktopSecond) $ do
   result <- bounded "healthy idle" 12000000 (receiveCredentialIngressAfterIdle ingress guard originalD)
   completed <- now
   count <- readIORef calls
   seen <- readIORef fragments
   check "idle >5s then authenticated frame delivers once" (completed-started >= 5000000000 && completed < originalD && result == CredentialDelivered && count == 2 && seen >= 2)
 -- Seeded actual-socket fragmentation sequences exercise the production
 -- frame/SCM/decoder/admission path. Splits include header/body boundaries;
 -- each fresh session has its own immutable D and exactly two callbacks.
 let seed = 20261101 :: Integer
     seeds = take 32 (tail (iterate (\n -> (1103515245*n+12345) `mod` 2147483648) seed))
 forM_ (zip [0 :: Int ..] seeds) $ \(index,value) ->
  withFixture True $ \fixture@(Fixture ingress peer calls _ _ guard) -> do
   originalD <- deadlineAfterSeconds 5
   seedFirst fixture originalD desktopFirst
   let split = if index < 5 then index+1 else 1 + fromInteger (value `mod` toInteger (B.length desktopSecond-1))
   withSender (N.sendAll peer (B.take split desktopSecond) >> threadDelay 1000 >> N.sendAll peer (B.drop split desktopSecond)) $ do
    result <- bounded "seeded fragmented desktop frame" 3000000 (receiveCredentialIngressAfterIdle ingress guard originalD)
    count <- readIORef calls
    check ("seed20261101 fragment " ++ show index ++ " split " ++ show split) (result == CredentialDelivered && count == 2)
 withFixture True $ \(Fixture ingress peer calls _ _ guard) -> do
  originalD <- deadlineAfterSeconds 5
  N.sendAll peer (desktopFirst <> desktopSecond)
  first <- bounded "coalesced first" 3000000 (receiveCredentialIngress ingress guard)
  second <- bounded "coalesced second" 3000000 (receiveCredentialIngressAfterIdle ingress guard originalD)
  count <- readIORef calls
  check "coalesced frames retain exactly two callbacks" (first == CredentialDelivered && second == CredentialDelivered && count == 2)
 -- Partial HEADER and BODY use the existing 5-second whole-frame budget.
 -- Wall-clock upper tolerance is scheduler grace, not a claim that a longer
 -- transport deadline is permitted; exact timer arithmetic needs its own seam.
 withFixture True $ \fixture@(Fixture _ peer _ _ _ _) -> do
  originalD <- deadlineAfterSeconds 12
  seedFirst fixture originalD desktopFirst
  N.sendAll peer (B.take 2 desktopSecond)
  started <- now
  expectTimeout "partial header" fixture originalD
  finished <- now
  check "partial header kept five-second bound" (finished-started >= 4500000000 && finished-started < 8500000000)
 withFixture True $ \fixture@(Fixture _ peer _ _ _ _) -> do
  originalD <- deadlineAfterSeconds 12
  seedFirst fixture originalD desktopFirst
  N.sendAll peer (B.take 5 desktopSecond)
  started <- now
  expectTimeout "partial body" fixture originalD
  finished <- now
  check "partial body kept five-second bound" (finished-started >= 4500000000 && finished-started < 8500000000)
 -- EOF is a readable condition; unchanged receive must report it, not spin or
 -- manufacture a delivered message.
 withFixture True $ \fixture@(Fixture ingress peer calls _ _ guard) -> do
  originalD <- deadlineAfterSeconds 5
  seedFirst fixture originalD desktopFirst
  S.shutdown peer S.ShutdownSend
  result <- bounded "EOF" 3000000 (receiveCredentialIngressAfterIdle ingress guard originalD)
  count <- readIORef calls
  check "EOF fails closed without callback" (result == CredentialFrameRejected (CredentialTransport StreamEOF) && count == 1)
 -- Revocation happens before the next actual SCM-bearing write and is checked
 -- by the production receive/admission hooks, not by an invented success.
 withFixture True $ \fixture@(Fixture ingress peer calls _ revoked guard) -> do
  originalD <- deadlineAfterSeconds 5
  seedFirst fixture originalD desktopFirst
  writeIORef revoked True
  N.sendAll peer desktopSecond
  result <- bounded "revocation" 3000000 (receiveCredentialIngressAfterIdle ingress guard originalD)
  count <- readIORef calls
  check "revoked guard refuses without callback" (result == CredentialFrameRejected (CredentialPeer Revoked) && count == 1)
 -- Concurrent retirement while idle must unblock the existing receive and
 -- must not admit a second callback. No new descriptor/close right is made.
 withFixture True $ \fixture@(Fixture ingress _ calls _ _ guard) -> do
  originalD <- deadlineAfterSeconds 10
  seedFirst fixture originalD desktopFirst
  retired <- newEmptyMVar
  _ <- forkFinally (threadDelay 100000 >> retireCredentialIngress ingress) (putMVar retired)
  result <- bounded "idle retirement" 3000000 (receiveCredentialIngressAfterIdle ingress guard originalD)
  retirement <- bounded "retirement completion" 3000000 (takeMVar retired)
  count <- readIORef calls
  case retirement of Left problem -> ioError (userError ("retirement failed: " ++ show (problem :: SomeException))); Right _ -> pure ()
  check "retired idle channel never dispatches" (result /= CredentialDelivered && count == 1)
 -- Recycle descriptors only after the old endpoint reports retirement.
 -- The new unrelated socket must retain its bytes; readiness is no reader.
 withFixture True $ \fixture@(Fixture ingress _ calls _ _ guard) -> do
  originalD <- deadlineAfterSeconds 4
  seedFirst fixture originalD desktopFirst
  waiting <- newEmptyMVar
  _ <- forkFinally (receiveCredentialIngressAfterIdle ingress guard originalD) (putMVar waiting)
  threadDelay 100000
  _ <- retireCredentialIngress ingress
  bracket (S.socketPair S.AF_UNIX S.Stream S.defaultProtocol)
    (\(a,b) -> S.close a >> S.close b) $ \(freshRead,freshWrite) -> do
     let unrelated = "unrelated bytes must remain unread"
     N.sendAll freshWrite unrelated
     received <- bounded "unrelated read" 1000000 (N.recv freshRead (B.length unrelated))
     completed <- bounded "retired waiter joins by original D" 5000000 (takeMVar waiting)
     count <- readIORef calls
     check "retired waiter did not consume unrelated bytes" (received == unrelated && count == 1)
     case completed of
      Left _ -> pure () -- explicit failure, never an authenticated delivery
      Right result -> check "retired waiter cannot deliver" (result /= CredentialDelivered)
 -- An idle D expires without bytes and does not become a new five-second D.
 withFixture True $ \fixture@(Fixture ingress _ calls _ _ guard) -> do
  started <- now
  let originalD = started + 2000000000
  seedFirst fixture originalD desktopFirst
  result <- bounded "idle original D" 3000000 (receiveCredentialIngressAfterIdle ingress guard originalD)
  finished <- now
  count <- readIORef calls
  check "idle original D is honored" (result == CredentialFrameRejected (CredentialTransport TimedOut) && count == 1 && finished < originalD + 1500000000)
 -- A partial header that becomes readable before D must not receive a fresh
 -- five-second lifetime after D. This is expected to expose an implementation
 -- that limits readiness only; actual outer owner cancellation is separate.
 withFixture True $ \fixture@(Fixture ingress peer calls _ _ guard) -> do
  started <- now
  let originalD = started + 2000000000
  seedFirst fixture originalD desktopFirst
  N.sendAll peer (B.take 2 desktopSecond)
  result <- bounded "partial original D" 3000000 (receiveCredentialIngressAfterIdle ingress guard originalD)
  finished <- now
  count <- readIORef calls
  check "partial frame cannot extend original D" (result == CredentialFrameRejected (CredentialTransport TimedOut) && count == 1 && finished < originalD + 1500000000)
 -- Delay the real credential-admission continuation beyond the same D.
 -- The callback must not begin after expiration, regardless of which
 -- fail-closed result represents the elapsed deadline.
 withFixture True $ \fixture@(Fixture ingress peer calls _ _ guard) -> do
  started <- now
  let originalD = started + 2000000000
      delayedGuard = CredentialGuard (checkFragment guard)
        (\credential action -> threadDelay 2500000 >> withCredentialAdmission guard credential action)
  seedFirst fixture originalD desktopFirst
  N.sendAll peer desktopSecond
  result <- bounded "admission crosses D" 4000000 (receiveCredentialIngressAfterIdle ingress delayedGuard originalD)
  finished <- now
  count <- readIORef calls
  check "expired admission invokes no callback" (finished >= originalD && result /= CredentialDelivered && count == 1)
 -- The native profile must keep its legacy immediate 5-second read behavior.
 withFixture False $ \fixture@(Fixture _ _ _ _ _ _) -> do
  originalD <- deadlineAfterSeconds 12
  seedFirst fixture originalD native
  started <- now
  expectTimeout "native unchanged idle" fixture originalD
  finished <- now
  check "native timeout remains five seconds" (finished-started >= 4500000000 && finished-started < 8500000000)
 putStrLn "desktop idle transport controls: same-process SCM fixture; no native acceptance"
