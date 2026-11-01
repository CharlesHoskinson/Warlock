{-# LANGUAGE OverloadedStrings #-}
{-# LANGUAGE ScopedTypeVariables #-}
-- SOURCE-ONLY TEST DRAFT, NOT COMPILED OR EXECUTED.
-- Root may integrate as a dedicated VM-only, non-GUI test executable after
-- reviewing the actual current source and flags. It calls real EngineCustody,
-- real prepareEngine and actual exec of THIS HELD TEST EXECUTABLE with exactly
-- --engine-only RPC LIFE D S UID GID. No backend binding, native operations,
-- synthetic grants, WebDriver, GTK invocation, original acceptance or release
-- verdict is provided. The test observer is not the production EngineBroker.
--
-- Build an ordinary variant without -threaded and with the reviewed -V0 RTS;
-- the positive tests fail unless /proc/self/task actually contains one task.
-- Separately build the SAME source as a threaded guard-control variant and run
-- only --threaded-guard there, with an actual forkOS task observed. These are
-- distinct test binary hashes; record both. Child entry is selected only by
-- the exact production argv shape, not by a new production hook.
--
-- All unshares/forks, pidfd observations and kills below are isolated fixture
-- processes in a root-owned private VM. Root alone decides when to execute and
-- retains failure evidence outside the repository. Preserve the original
-- 4.5-second D throughout each individual scenario, including parent death;
-- outer timeouts are safety bounds, never a deadline reset or success receipt.
module Main (main) where

import Control.Concurrent (forkOS, newEmptyMVar, putMVar, takeMVar, threadDelay, rtsSupportsBoundThreads)
import Control.Exception (IOException, SomeException, bracket, displayException, finally, onException, try)
import Control.Monad (unless, void, when)
import qualified Crypto.Hash.SHA256 as SHA256
import qualified Data.ByteString as B
import qualified Data.ByteString.Char8 as C
import Data.Char (isDigit)
import Data.IORef (IORef, atomicModifyIORef', newIORef, readIORef, writeIORef)
import Data.List (isInfixOf)
import Data.Word (Word64)
import Foreign.C.Error (Errno(..), eBADF)
import GHC.Conc (threadWaitRead)
import GHC.IO.Exception (ioe_errno)
import Foreign.Marshal.Alloc (allocaBytes)
import Foreign.Ptr (castPtr)
import qualified Network.Socket as S
import qualified Network.Socket.ByteString as N
import System.Directory (listDirectory)
import System.Environment (getArgs)
import System.Exit (ExitCode(..), exitFailure)
import System.IO (hFlush, stderr, stdout)
import System.Posix.Files (FileStatus, deviceID, fileID, fileSize, getFdStatus, getFileStatus)
import System.Posix.IO (FdOption(CloseOnExec,NonBlockingRead), closeFd, createPipe, fdReadBuf, fdWriteBuf, setFdOption)
import System.Posix.Process (ProcessStatus(..), exitImmediately, forkProcess,
                             getProcessID, getProcessStatus)
import System.Posix.Signals (sigKILL, signalProcess)
import System.Posix.Types (Fd(..), ProcessID)
import System.Timeout (timeout)
import Warlock.Capture.Process.Bootstrap (AdmissionDeadline, deadlineAfter, remainingMicros)
import Warlock.Protocol.CredentialGuard (CredentialGuard(..))
import qualified Warlock.Protocol.EngineTransport as Transport
import qualified Warlock.Protocol.PeerCredential as Cred
import Warlock.Ui.EngineCustody
  ( EngineProcess, ImageFacts(..), engineCredentialGuard, engineExpectedIds
  , engineImageFacts, engineLiveChild, enginePid, openPidfd, pidfdExited
  , startUnreadyEngine, stopEngineProcess, takeEngineChannel )
import Warlock.Ui.EngineEntrypoint (Mode(..), classifyMode, prepareEngine)
import Warlock.Ui.PrivateNetwork (enterPrivateNetwork)

ensure :: String -> Bool -> IO ()
ensure label good = unless good (ioError (userError label))

must :: Show e => Either e a -> IO a
must = either (ioError . userError . show) pure

-- ASCII fixture plumbing; no partial locale decoding through deprecated fdRead.
readPipe :: Fd -> Int -> IO (String,Int)
readPipe fd requested = allocaBytes requested $ \buffer -> do
  count <- fdReadBuf fd buffer (fromIntegral requested)
  bytes <- B.packCStringLen (castPtr buffer,fromIntegral count)
  pure (C.unpack bytes,fromIntegral count)

writePipe :: Fd -> String -> IO Int
writePipe fd value = C.useAsCStringLen (C.pack value) $ \(buffer,count) ->
  fromIntegral <$> fdWriteBuf fd (castPtr buffer) (fromIntegral count)

originalDeadline :: IO AdmissionDeadline
originalDeadline = deadlineAfter 4500000 >>= must

-- An actual missing fd must be EBADF, not an arbitrary IO/proc failure.
fdAbsent :: Int -> IO Bool
fdAbsent n = do
  result <- try (getFdStatus (Fd (fromIntegral n))) :: IO (Either IOException FileStatus)
  case result of
    Right _ -> pure False
    Left problem -> let Errno bad = eBADF in pure (ioe_errno problem == Just bad)

sameIdentity :: FileStatus -> FileStatus -> Bool
sameIdentity a b = deviceID a == deviceID b && fileID a == fileID b
                && fileSize a == fileSize b

-- listDirectory briefly opens the proc-fd directory. That one enumeration FD
-- may disappear before getFdStatus; any other still-open FD outside the exact
-- child manifest fails. Require the visible stdio to have been replaced by
-- /dev/null, and RPC/lifeline are the actual explicitly received numbers.
checkExecFdCensus :: Int -> Int -> IO ()
checkExecFdCensus rpc life = do
  names <- listDirectory "/proc/self/fd"
  let numeric = [read n :: Int | n <- names, not (null n), all isDigit n]
      extras = filter (`notElem` [0,1,2,rpc,life]) numeric
  states <- mapM fdAbsent extras
  ensure "unexpected live inherited descriptor" (and states && length extras <= 1)
  nullStatus <- getFileStatus "/dev/null"
  stdio <- mapM (getFdStatus . Fd . fromIntegral) [0,1,2 :: Int]
  ensure "stdio not harmless /dev/null" (all (sameIdentity nullStatus) stdio)
  void (getFdStatus (Fd (fromIntegral rpc)))
  void (getFdStatus (Fd (fromIntegral life)))

-- A ready proof is intentionally a short private test marker, never the
-- production ready frame. The actual selected child sends it only AFTER real
-- prepareEngine PID1/capability/no_new_privs/deadline/lifeline checks, a real
-- private proc-view cross-check, and the FD census above. The broker parent
-- authenticates *every actual recvmsg fragment* via engineCredentialGuard.
probeMarker :: B.ByteString
probeMarker = "owned-engine-probe-v1"

engineProbe :: [String] -> IO ()
engineProbe args@["--engine-only",rpcText,lifeText,_d,_session,_uid,_gid] = do
  rpc <- case reads rpcText of [(x,"")] | x >= 3 -> pure x; _ -> ioError (userError "bad RPC FD")
  life <- case reads lifeText of [(x,"")] | x >= 3 && x /= rpc -> pure x; _ -> ioError (userError "bad life FD")
  -- This check happens before prepareEngine fills stdio. An ELF loader/RTS
  -- which opened an fd before main makes the test FAIL rather than hide it.
  closed <- mapM fdAbsent [0,1,2]
  ensure "inherited stdio or loader/RTS opened stdio" (and closed)
  case classifyMode args of
    EngineOnly admitted -> do
      deadline <- prepareEngine admitted >>= must
      pid <- getProcessID
      ensure "engine is not namespace PID1" (pid == 1)
      -- If proc still refers to the host PID namespace, its PID 1 is a
      -- different image. This is an independent cross-check, not complete
      -- mount provenance; protected acceptance still needs namespace evidence.
      own <- getFileStatus "/proc/self/exe"
      localOne <- getFileStatus "/proc/1/exe"
      ensure "proc PID1 is not current held image" (sameIdentity own localOne)
      checkExecFdCensus rpc life
      socket <- S.mkSocket (fromIntegral rpc)
      (do
        Transport.configureSocketFlags socket
        left <- remainingMicros deadline
        ensure "probe deadline expired" (left > 0)
        sent <- timeout left (N.sendAll socket probeMarker)
        ensure "probe send deadline" (sent == Just ())
        -- Stay live for the owner's stop or parent-death observation. This
        -- waits on the actual inherited pipe; no extra fake success marker.
        waitLeft <- remainingMicros deadline
        ensure "probe deadline expired before life wait" (waitLeft > 0)
        _ <- timeout waitLeft (threadWaitRead (Fd (fromIntegral life)))
        ioError (userError "engine lifeline closed or deadline reached")
        ) `finally` S.close socket
    _ -> ioError (userError "actual engine argument classifier refused")
engineProbe _ = ioError (userError "not the exact engine-only argv")

-- Read one literal marker, bounded by the actual original D, and require a
-- kernel credential on EACH fragment before accepting any bytes. The guard
-- binds the actual selected host PID, sampled UID/GID, owned live pidfd and D.
-- No page-provided or parent-generated PID is taken as browser/native proof.
readProof :: AdmissionDeadline -> EngineProcess -> S.Socket -> IO Cred.PeerCredential
readProof deadline process socket = do
  reader <- Transport.newCredentialReader
  let guard = engineCredentialGuard process
      go remaining first parts
        | remaining == 0 = do
            credential <- maybe (ioError (userError "missing SCM credentials")) pure first
            ensure "probe marker differs" (B.concat (reverse parts) == probeMarker)
            admitted <- withCredentialAdmission guard credential (pure ())
            void (must admitted)
            pure credential
        | otherwise = do
            left <- remainingMicros deadline
            ensure "proof deadline" (left > 0)
            received <- timeout left (Transport.receiveCredentialChunk reader socket remaining)
            chunk <- maybe (ioError (userError "proof receive deadline")) must received
            case chunk of
              Transport.CredentialChunk bytes credential -> do
                ensure "empty/oversize credential fragment" (not (B.null bytes) && B.length bytes <= remaining)
                void (checkFragment guard credential >>= must)
                ensure "SCM PID differs from owned child" (Cred.credentialPid credential == toInteger (enginePid process))
                let (uid,gid) = engineExpectedIds process
                ensure "SCM UID/GID differs" (Cred.credentialUid credential == uid && Cred.credentialGid credential == gid)
                ensure "SCM credentials changed during proof" (maybe True (== credential) first)
                go (remaining-B.length bytes) (Just credential) (bytes:parts)
              _ -> ioError (userError "EOF before probe marker")
  go (B.length probeMarker) Nothing []

-- Independently compare the actual selected process image to the held-self
-- pin. Access to /proc/<pid>/exe can legitimately be denied after userns or
-- cap changes; that is a FAIL/unknown observation, never an inferred match.
checkActualImage :: EngineProcess -> IO ()
checkActualImage process = do
  let ImageFacts dev ino size digest = engineImageFacts process
      path = "/proc/" ++ show (enginePid process) ++ "/exe"
  st <- getFileStatus path
  ensure "selected executable inode mismatch" (toInteger (deviceID st) == dev && toInteger (fileID st) == ino && toInteger (fileSize st) == size)
  bytes <- B.readFile path
  ensure "selected executable bytes mismatch" (toInteger (B.length bytes) == size && SHA256.hash bytes == digest)
  stillOwned <- engineLiveChild process (enginePid process)
  ensure "selected child not live after image observation" stillOwned

-- These helpers concern only a fixture's own direct child, never the selected
-- engine. Check it remains an unreaped direct child before signalling the
-- recorded PID, and do not signal on ECHILD/unknown ownership.
retireDirectFixture :: IORef Bool -> ProcessID -> IO ()
retireDirectFixture done pid = do
  finished <- readIORef done
  unless finished $ do
    current <- try (getProcessStatus False False pid) :: IO (Either IOException (Maybe ProcessStatus))
    case current of
      Left _ -> pure () -- unknown: do not signal an unowned/reused number
      Right (Just _) -> writeIORef done True
      Right Nothing -> do
        signalProcess sigKILL pid
        _ <- getProcessStatus True False pid
        writeIORef done True

closeFdCell :: IORef (Maybe Fd) -> IO ()
closeFdCell cell = do
  owned <- atomicModifyIORef' cell (\old -> (Nothing,old))
  maybe (pure ()) closeFd owned

-- Ordinary source path; no native fd0 fixture, browser, fake grant or Owner
-- event. The independently bound unrelated child must remain alive until
-- released and be reaped by this fixture, never by EngineCustody's PID1 wait.
ownedExecCase :: Word64 -> AdmissionDeadline -> IO ()
ownedExecCase session deadline = do
  tasks <- listDirectory "/proc/self/task"
  ensure "positive executable is not single OS thread" (length tasks == 1)
  (unrelatedRead,unrelatedWrite) <- createPipe
  setFdOption unrelatedRead CloseOnExec True
  setFdOption unrelatedWrite CloseOnExec True
  unrelated <- forkProcess $ do
    closeFd unrelatedWrite
    (byte,_) <- readPipe unrelatedRead 1
    exitImmediately (if byte == "x" then ExitFailure 42 else ExitFailure 43)
  closeFd unrelatedRead
  unrelatedDone <- newIORef False
  writeCell <- newIORef (Just unrelatedWrite)
  let cleanFixture = closeFdCell writeCell `finally` retireDirectFixture unrelatedDone unrelated
  (do
    enterPrivateNetwork
    -- Listener must be absent in selected exec. The child census rejects every
    -- extra FD; no connection is used as fake engine/native proof.
    bracket (S.socket S.AF_INET S.Stream S.defaultProtocol) S.close $ \listener -> do
      S.bind listener (S.SockAddrInet 0 (S.tupleToHostAddress (127,0,0,1)))
      S.listen listener 1
      process <- startUnreadyEngine deadline session []
      let retireEngine = void (stopEngineProcess process)
      channel <- takeEngineChannel process `onException` retireEngine
      (do
        credential <- readProof deadline process channel
        checkActualImage process
        checkFragment (engineCredentialGuard process) credential >>= must
        before <- getProcessStatus False False unrelated
        case before of
          Nothing -> pure ()
          Just _ -> writeIORef unrelatedDone True >> ioError (userError "unrelated child exited")
        stopped <- stopEngineProcess process
        ensure "owned PID1 did not stop and reap under D" stopped
        stoppedAgain <- stopEngineProcess process
        ensure "second stop falsely claimed another reap" (not stoppedAgain)
        live <- engineLiveChild process (enginePid process)
        ensure "retired process remained live" (not live)
        after <- checkFragment (engineCredentialGuard process) credential
        ensure "retired credential remained admitted" (case after of Left _ -> True; _ -> False)
        count <- writePipe unrelatedWrite "x"
        ensure "unrelated fixture release failed" (count == 1)
        observed <- getProcessStatus True False unrelated
        writeIORef unrelatedDone True
        ensure "unrelated direct child status was stolen" (observed == Just (Exited (ExitFailure 42)))
        ) `finally` (S.close channel `finally` retireEngine)
    ) `finally` cleanFixture

-- Parent-death supervisor opens pidfd for the real selected PID1 BEFORE
-- killing its direct parent. The executor reports the selected host pid after
-- either authenticated test proof or an explicitly phase-unknown early point.
-- This pidfd is OBSERVATION
-- ONLY: it never signals or reaps the engine (EngineCustody remains sole
-- reaper). Parent SIGKILL is sent only to the supervisor's owned direct child.
readLineBy :: AdmissionDeadline -> Fd -> IO String
readLineBy deadline fd = do
  setFdOption fd NonBlockingRead True
  let go acc = do
        ensure "supervisor line too long" (length acc < 32)
        left <- remainingMicros deadline
        ensure "supervisor line deadline" (left > 0)
        result <- timeout left $ do
          threadWaitRead fd
          readPipe fd 1
        (byte,_) <- maybe (ioError (userError "supervisor line timeout")) pure result
        if byte == "\n" then pure (reverse acc)
        else if length byte == 1 then go (head byte:acc)
        else ioError (userError "supervisor pipe EOF")
  go []

waitPidfdExit :: AdmissionDeadline -> Fd -> IO ()
waitPidfdExit deadline (Fd number) = do
  left <- remainingMicros deadline
  ensure "pidfd exit not observed by original deadline" (left > 0)
  exited <- pidfdExited number
  unless exited (threadDelay (min 1000 left) >> waitPidfdExit deadline (Fd number))

parentDeathCase :: Bool -> AdmissionDeadline -> IO ()
parentDeathCase waitForProof deadline = do
  (reportRead,reportWrite) <- createPipe
  setFdOption reportRead CloseOnExec True
  setFdOption reportWrite CloseOnExec True
  executor <- forkProcess $ do
    closeFd reportRead
    result <- try $ do
      enterPrivateNetwork
      process <- startUnreadyEngine deadline 1 []
      channel <- takeEngineChannel process
      when waitForProof $ do
        _ <- readProof deadline process channel
        checkActualImage process
      let line = show (enginePid process) ++ "\n"
      n <- writePipe reportWrite line
      ensure "selected PID report short" (fromIntegral n == length line)
      -- When waitForProof is False this stimulus occurs immediately after the
      -- owner returns but its precise child exec/PDEATHSIG phase is UNKNOWN.
      -- Independent root tracing is needed to establish a specific race phase.
      -- Channel remains open so the real death/lifeline path is exercised.
      threadDelay 10000000
    case (result :: Either SomeException ()) of
      Left _ -> exitImmediately (ExitFailure 90)
      Right () -> exitImmediately (ExitFailure 91)
  closeFd reportWrite
  executorDone <- newIORef False
  (do
    textPid <- readLineBy deadline reportRead `finally` closeFd reportRead
    selected <- case reads textPid of
      [(number,"")] | number > (0 :: Int) -> pure number
      _ -> ioError (userError "bad selected PID report")
    pidfdNumber <- openPidfd (fromIntegral selected)
    let pidfd = Fd pidfdNumber
    (do
      alreadyExited <- pidfdExited pidfdNumber
      ensure "engine exited before parent death stimulus" (not alreadyExited)
      signalProcess sigKILL executor
      parentStatus <- getProcessStatus True False executor
      writeIORef executorDone True
      ensure "direct executor was not killed" (case parentStatus of Just (Terminated signal _) -> signal == sigKILL; _ -> False)
      waitPidfdExit deadline pidfd
      -- pidfd readability establishes exit, not reaping/clean shutdown. The
      -- dead parent cannot provide an EngineCustody retirement receipt.
      ) `finally` closeFd pidfd
    ) `finally` retireDirectFixture executorDone executor

-- This separate build of the SAME test source uses -threaded and forkOS to
-- establish an actual extra OS thread. The tested production guard runs
-- before namespace entry; an arbitrary startup failure is not sufficient.
threadedGuard :: IO ()
threadedGuard = do
  ensure "threaded guard control requires threaded RTS" rtsSupportsBoundThreads
  ready <- newEmptyMVar
  stop <- newEmptyMVar
  done <- newEmptyMVar
  _ <- forkOS (putMVar ready () >> takeMVar stop >> putMVar done ())
  takeMVar ready
  tasks <- listDirectory "/proc/self/task"
  ensure "extra OS thread not observed" (length tasks > 1)
  deadline <- originalDeadline
  result <- try (startUnreadyEngine deadline 1 []) :: IO (Either IOException EngineProcess)
  putMVar stop ()
  takeMVar done
  case result of
    Left problem -> ensure "wrong refusal path" ("custody requires a single OS thread" `isInfixOf` displayException problem)
    Right process -> do
      _ <- stopEngineProcess process
      ioError (userError "threaded custody unexpectedly admitted")

-- Boundary refusal on the actual production path: zero is never a valid
-- session. Verify that refusal occurs before CLONE_NEWPID changes the calling
-- process's namespace-for-children, rather than accepting an unrelated error.
zeroSessionCase :: AdmissionDeadline -> IO ()
zeroSessionCase deadline = do
  before <- getFileStatus "/proc/thread-self/ns/pid_for_children"
  result <- try (startUnreadyEngine deadline 0 []) :: IO (Either IOException EngineProcess)
  case result of
    Left problem -> ensure "zero session wrong refusal" ("engine session must be positive" `isInfixOf` displayException problem)
    Right process -> do
      _ <- stopEngineProcess process
      ioError (userError "zero session unexpectedly admitted")
  after <- getFileStatus "/proc/thread-self/ns/pid_for_children"
  ensure "zero session changed pid-for-children" (sameIdentity before after)

-- Isolate every positive case in its own process. startUnreadyEngine calls
-- unshare(CLONE_NEWPID), which changes pid_for_children irreversibly for that
-- process. Never launch another test slice in the same child afterward.
waitDirect :: AdmissionDeadline -> ProcessID -> IO ProcessStatus
waitDirect deadline pid = do
  current <- getProcessStatus False False pid
  case current of
    Just result -> do
      left <- remainingMicros deadline
      ensure "isolated result arrived after original deadline" (left > 0)
      pure result
    Nothing -> do
      left <- remainingMicros deadline
      if left <= 0 then do
        signalProcess sigKILL pid
        _ <- getProcessStatus True False pid
        ioError (userError "isolated test deadline expired; cleanup unknown")
      else threadDelay (min 1000 left) >> waitDirect deadline pid

isolated :: String -> (AdmissionDeadline -> IO ()) -> IO ()
isolated label action = do
  deadline <- originalDeadline
  child <- forkProcess $ do
    outcome <- try (action deadline) :: IO (Either SomeException ())
    case outcome of
      Right () -> exitImmediately ExitSuccess
      Left problem -> C.hPutStrLn stderr (C.pack (label ++ ": " ++ displayException problem)) >> exitImmediately (ExitFailure 1)
  status <- waitDirect deadline child
  ensure (label ++ " failed: " ++ show status) (status == Exited ExitSuccess)
  putStrLn (label ++ "=PASS (bounded source control; not GUI/native acceptance)")
  hFlush stdout

main :: IO ()
main = do
  args <- getArgs
  case args of
    ("--engine-only":_) -> do
      result <- try (engineProbe args) :: IO (Either SomeException ())
      case result of Left _ -> exitImmediately (ExitFailure 120); Right () -> exitImmediately ExitSuccess
    ["--threaded-guard"] -> threadedGuard
    [] -> do
      ensure "positive variant needs nonthreaded RTS" (not rtsSupportsBoundThreads)
      isolated "zero-session-refused-before-namespace" zeroSessionCase
      isolated "held-exec-session-1-and-sole-reap" (ownedExecCase 1)
      isolated "held-exec-session-max-and-sole-reap" (ownedExecCase maxBound)
      isolated "post-proof-parent-death" (parentDeathCase True)
      isolated "early-parent-death-phase-unknown" (parentDeathCase False)
    _ -> C.hPutStrLn stderr "usage: EngineExecControls [--threaded-guard]" >> exitFailure
