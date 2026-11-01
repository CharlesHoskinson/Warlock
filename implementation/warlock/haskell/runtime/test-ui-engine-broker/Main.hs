{-# LANGUAGE OverloadedStrings #-}
{-# LANGUAGE RankNTypes #-}
-- PREPARATION DRAFT. Source tests exercise a real AF_UNIX socketpair,
-- SO_PASSCRED/recvmsg and the imported EngineBroker. The peer is this test
-- process and the public CredentialGuard is deliberately a fixture: this is
-- NOT evidence of an owned engine child, pidfd, namespace, reaper or GTK.
module Main (main) where

import Control.Exception (finally, onException)
import Control.Monad (unless, void, when)
import qualified Data.ByteString as B
import qualified Data.ByteString.Char8 as C
import Data.Bits (shiftR)
import Data.IORef (IORef, modifyIORef', newIORef, readIORef)
import qualified Data.Text as T
import qualified Network.Socket as S
import qualified Network.Socket.ByteString as N
import System.Exit (ExitCode(..))
import System.Posix.Process (ProcessStatus(..), exitImmediately, forkProcess, getProcessID, getProcessStatus)
import System.Posix.User (getRealGroupID, getRealUserID)
import System.Timeout (timeout)
import Warlock.Capture.Process.Bootstrap (AdmissionDeadline, deadlineAbsoluteNs, deadlineAfter, remainingMicros)
import Warlock.Protocol.CredentialGuard (CredentialGuard(..))
import qualified Warlock.Protocol.EngineTransport as Transport
import Warlock.Protocol.Identity (parseCounter)
import Warlock.Protocol.PeerCredential (PeerCredential, credentialPid, credentialUid, credentialGid)
import qualified Warlock.Protocol.StrictJson as J
import qualified Warlock.Ui.EngineBroker as Broker
import qualified Warlock.Ui.EngineProtocol as P
import Warlock.Ui.Owner (UiEndpoints(..), TrustedOwnerEvent(..))
import Warlock.Ui.Policy (makeOrigin)

check :: String -> Bool -> IO ()
check label valid = unless valid (ioError (userError ("broker control failed: " ++ label)))
must :: Show e => Either e a -> IO a
must = either (ioError . userError . show) pure

-- These checks observe credentials actually attached to recvmsg fragments.
-- They deliberately compare against this fixture's PID/UID/GID, not an owned
-- child or pidfd. The final admission callback is a mock, never native proof.
data GuardMode = ParentOnly | WrongParent | FixtureSameUser deriving (Eq,Show)

fixtureGuard :: GuardMode -> IORef Int -> IORef Int -> IO (CredentialGuard T.Text)
fixtureGuard mode fragments admissions = do
  pid <- toInteger <$> getProcessID
  uid <- toInteger <$> getRealUserID
  gid <- toInteger <$> getRealGroupID
  let expectedPid = if mode == WrongParent then pid + 1 else pid
      verify credential = (mode == FixtureSameUser || credentialPid credential == expectedPid)
        && credentialUid credential == uid && credentialGid credential == gid
      fragment credential = do
        modifyIORef' fragments (+1)
        pure (if verify credential then Right () else Left "fixture credential refused")
      admission :: PeerCredential -> IO a -> IO (Either T.Text a)
      admission credential action = do
        modifyIORef' admissions (+1)
        if verify credential then Right <$> action else pure (Left "fixture admission refused")
  pure (CredentialGuard fragment admission)

data Fixture = Fixture
  { fixturePeer :: S.Socket
  , fixtureBroker :: Broker.Broker T.Text
  , fixtureStartup :: P.Startup
  , fixtureDeadline :: AdmissionDeadline
  , fixtureCalls :: IORef [T.Text]
  , fixtureEvents :: IORef [TrustedOwnerEvent]
  , fixtureFragments :: IORef Int
  , fixtureAdmissions :: IORef Int
  }

withFixture :: GuardMode -> (Fixture -> IO a) -> IO a
withFixture mode action = do
  deadline <- deadlineAfter 5000000 >>= must
  sid <- must (P.sessionId "42")
  startup <- must (P.startup 21101 21102 21103 (T.pack (deadlineAbsoluteNs deadline)) sid)
  controller <- must (makeOrigin 21101)
  bar <- must (makeOrigin 21102)
  popup <- must (makeOrigin 21103)
  calls <- newIORef []
  events <- newIORef []
  fragments <- newIORef 0
  admissions <- newIORef 0
  guard <- fixtureGuard mode fragments admissions
  let record name = modifyIORef' calls (name:)
      projection = J.JObject [("fixture",J.JString "owner snapshot")]
      endpoints = UiEndpoints controller bar popup
        (record "stop" >> pure False)
        (record "remaining" >> pure 1000000)
        (record "projection" >> pure (Just projection))
      owner event = record "event" >> modifyIORef' events (event:) >> pure (Right ())
  (owned,peer) <- S.socketPair S.AF_UNIX S.Stream S.defaultProtocol
  prepared <- Broker.prepareBroker owned deadline startup endpoints owner `onException` S.close peer
  broker <- Broker.attachBroker prepared guard `onException` (void (Broker.closePrepared prepared) >> S.close peer)
  let fixture = Fixture peer broker startup deadline calls events fragments admissions
  action fixture `finally` (void (Broker.closeBroker broker) >> S.close peer)

readyPayload :: P.Startup -> B.ByteString
readyPayload startup = C.pack ("{\"engineReady\":1,\"deadline\":\"" ++ T.unpack (P.startupDeadline startup) ++ "\",\"incarnation\":\"42\"}")

readExact :: S.Socket -> Int -> IO B.ByteString
readExact peer count = go count []
  where
    go 0 chunks = pure (B.concat (reverse chunks))
    go n chunks = do
      chunk <- N.recv peer n
      if B.null chunk then ioError (userError "test peer received EOF")
        else go (n - B.length chunk) (chunk:chunks)

readBoundedFrame :: AdmissionDeadline -> (B.ByteString -> Either e Int) -> S.Socket -> IO B.ByteString
readBoundedFrame deadline decode peer = do
  left <- remainingMicros deadline
  when (left <= 0) (ioError (userError "test original deadline expired"))
  timed <- timeout left $ do
    header <- readExact peer 4
    size <- either (const (ioError (userError "test reply frame invalid"))) pure (decode header)
    readExact peer size
  after <- remainingMicros deadline
  case timed of
    Just value | after > 0 -> pure value
    _ -> ioError (userError "test peer reply deadline")

sendStartupReady :: Fixture -> IO ()
sendStartupReady fixture = do
  ready <- must (Transport.startupPrefix (readyPayload (fixtureStartup fixture)))
  N.sendAll (fixturePeer fixture) ready

startFixture :: Fixture -> IO ()
startFixture fixture = do
  before <- Broker.serveBrokerOnce (fixtureBroker fixture)
  check "ordinary request unavailable before ready" (before == Broker.NotReady)
  sendStartupReady fixture
  result <- Broker.completeStartup (fixtureBroker fixture)
  check "actual startup frame delivered through mock guard" (result == Broker.StartupWrittenLocally)
  startupBytes <- readBoundedFrame (fixtureDeadline fixture) Transport.startupHeaderLength (fixturePeer fixture)
  parsed <- must (P.decodeStartup startupBytes)
  check "startup immutable" (parsed == fixtureStartup fixture)
  calls <- readIORef (fixtureCalls fixture)
  check "startup does not call owner endpoints" (null calls)

roundTrip :: Fixture -> (P.Session,[(P.Request,P.Reply)]) -> IO (P.Session,[(P.Request,P.Reply)])
roundTrip _ (session,[]) = pure (session,[])
roundTrip fixture (session,(request,expected):rest) = do
  let (pending,encoded) = P.beginRequest session request
  inner <- must encoded
  framed <- must (Transport.enginePrefix inner)
  N.sendAll (fixturePeer fixture) framed
  outcome <- Broker.serveBrokerOnce (fixtureBroker fixture)
  check "one reply written locally" (outcome == Broker.ReplyWrittenLocally)
  raw <- readBoundedFrame (fixtureDeadline fixture) Transport.engineHeaderLength (fixturePeer fixture)
  let (next,reply) = P.acceptReply pending raw
  actual <- must reply
  check "reply value" (actual == expected && not (P.isPoisoned next))
  roundTrip fixture (next,rest)

positiveControls :: IO ()
positiveControls = withFixture ParentOnly $ \fixture -> do
  startFixture fixture
  rev <- must (parseCounter False "7")
  pub <- must (parseCounter False "9")
  lease <- must (parseCounter True "0")
  ident <- must (P.scope "2" "3")
  projected <- must (P.projection (J.JObject [("fixture",J.JString "owner snapshot")]))
  let requests =
        [(P.GetStop,P.StopReply False),
         (P.GetRemaining,P.RemainingReply 1000000),
         (P.GetLastProjection,P.ProjectionReply (Just projected)),
         (P.OwnerEvent (P.Topology rev Nothing),P.EventReply P.Accepted),
         (P.OwnerEvent (P.Dismiss ident lease),P.EventReply P.Accepted),
         (P.OwnerEvent (P.Escape ident pub lease),P.EventReply P.Accepted),
         (P.OwnerEvent (P.Reflow ident lease),P.EventReply P.Accepted)]
  (_,left) <- roundTrip fixture (P.newSession (fixtureStartup fixture),requests)
  check "all seven operations completed" (null left)
  calls <- reverse <$> readIORef (fixtureCalls fixture)
  check "exact callback order" (calls == ["stop","remaining","projection","event","event","event","event"])
  events <- reverse <$> readIORef (fixtureEvents fixture)
  check "four owner event classes" (case events of
    [OwnerTopology _,OwnerDismiss _,OwnerEscape _,OwnerReflow _] -> True
    _ -> False)
  fragments <- readIORef (fixtureFragments fixture)
  admissions <- readIORef (fixtureAdmissions fixture)
  check "real credential observations for every frame" (fragments >= 16 && admissions == 8)

-- Fixture mismatch tests an authentic credential refused by a mock expected-PID
-- guard. It does not impersonate an actual foreign child or test pidfd ownership.
credentialRefusal :: IO ()
credentialRefusal = withFixture WrongParent $ \fixture -> do
  sendStartupReady fixture
  result <- Broker.completeStartup (fixtureBroker fixture)
  check "wrong expected identity refused" (result == Broker.Indeterminate)
  fragments <- readIORef (fixtureFragments fixture)
  calls <- readIORef (fixtureCalls fixture)
  check "credential checked and no callback" (fragments > 0 && null calls)
  later <- Broker.serveBrokerOnce (fixtureBroker fixture)
  check "credential refusal retires" (later == Broker.Closed)

-- Real mixed-writer credentials: the parent writes the outer header, then
-- its exact forked child writes the body through the same socket endpoint.
-- ParentOnly rejects the child via the guard; FixtureSameUser accepts both
-- genuine credentials so the broker's cross-fragment comparison must reject.
-- The body is a valid GetStop request, so a missing comparison reaches a real
-- callback instead of failing due to malformed JSON. This is not an
-- owned-engine spawn, namespace or pidfd custody fixture.
mixedWriters :: GuardMode -> IO ()
mixedWriters mode = withFixture mode $ \fixture -> do
  startFixture fixture
  before <- readIORef (fixtureFragments fixture)
  let peer = fixturePeer fixture
      (_,encoded) = P.beginRequest (P.newSession (fixtureStartup fixture)) P.GetStop
  validRequest <- must encoded
  N.sendAll peer (word32 (B.length validRequest))
  child <- forkProcess (N.sendAll peer validRequest >> exitImmediately ExitSuccess)
  status <- getProcessStatus True False child
  check "exact fixture child exited" (status == Just (Exited ExitSuccess))
  result <- Broker.serveBrokerOnce (fixtureBroker fixture)
  after <- readIORef (fixtureFragments fixture)
  calls <- readIORef (fixtureCalls fixture)
  check "different writer refused before callback" (result == Broker.Indeterminate && after >= before + 2 && null calls)
  retired <- Broker.serveBrokerOnce (fixtureBroker fixture)
  check "mixed writer failure retires" (retired == Broker.Closed)

word32 :: Int -> B.ByteString
word32 n = B.pack [fromIntegral (n `shiftR` 24),fromIntegral (n `shiftR` 16),fromIntegral (n `shiftR` 8),fromIntegral n]

negativeAfterStartup :: String -> (S.Socket -> IO ()) -> IO ()
negativeAfterStartup label inject = withFixture ParentOnly $ \fixture -> do
  startFixture fixture
  inject (fixturePeer fixture)
  result <- Broker.serveBrokerOnce (fixtureBroker fixture)
  check (label ++ " refuses") (result == Broker.Indeterminate)
  calls <- readIORef (fixtureCalls fixture)
  events <- readIORef (fixtureEvents fixture)
  check (label ++ " no callbacks") (null calls && null events)
  after <- Broker.serveBrokerOnce (fixtureBroker fixture)
  check (label ++ " retires") (after == Broker.Closed)

negativeControls :: IO ()
negativeControls = do
  credentialRefusal
  mixedWriters ParentOnly
  mixedWriters FixtureSameUser
  negativeAfterStartup "EOF" (\peer -> S.shutdown peer S.ShutdownSend)
  negativeAfterStartup "truncated header" (\peer -> N.sendAll peer (B.pack [0,1]) >> S.shutdown peer S.ShutdownSend)
  negativeAfterStartup "truncated body" (\peer -> N.sendAll peer (word32 20 <> "{}") >> S.shutdown peer S.ShutdownSend)
  negativeAfterStartup "oversize length" (\peer -> N.sendAll peer (word32 (P.maxFrameBytes + 1)))
  negativeAfterStartup "malformed protocol" (\peer -> do frame <- must (Transport.enginePrefix "not-json"); N.sendAll peer frame)
  withFixture ParentOnly $ \fixture -> do
    startFixture fixture
    close <- Broker.closeBroker (fixtureBroker fixture)
    check "socket retirement" (close == Broker.CloseConfirmed)
    result <- Broker.serveBrokerOnce (fixtureBroker fixture)
    calls <- readIORef (fixtureCalls fixture)
    check "retired broker never calls owner" (result == Broker.Closed && null calls)

main :: IO ()
main = do
  positiveControls
  negativeControls
  putStrLn "engine broker socketpair controls passed; mock guard is not owned-process evidence"
