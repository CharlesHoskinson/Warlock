{-# LANGUAGE ForeignFunctionInterface #-}
{-# LANGUAGE OverloadedStrings #-}
{-# LANGUAGE ScopedTypeVariables #-}
#define _GNU_SOURCE
#include <sys/wait.h>
#include <signal.h>
#include <sys/types.h>
-- Linux-specific source proposal: independent process/library review required.
module Warlock.Capture.Process.Internal
 (Tool(..),ToolError(..),Captured(..),Owner,OwnerStatus(..),newOwner,status,runTool,runFixture,runFixturePinned,runFixtureWithHook, selectedFixture, selectedTicketFixture, SelectedSpawn, HeldExecutable, SelectedResult(..), Session, selectedHeld, awaitLeader, runSelected, AdmissionDeadline, deadlineAfter, remainingMicros, runSelectedUntil, runSelectedDetailed, SelectedOutcome(..), Containment(..), SessionObservation(..), observeSession, runSelectedFixtureHook) where
import Control.Concurrent (MVar, ThreadId, forkFinally, killThread, newEmptyMVar, newMVar, putMVar, readMVar, threadDelay, withMVar)
import Control.Exception (IOException, SomeAsyncException, SomeException, bracket, fromException, mask, onException, try, throwIO)
import qualified Data.Text as T
import Warlock.Capture.Process.Owner (Owner,OwnerStatus(..),newOwner,status,begin,abortBegin,publish,quarantine,failUnsettled,settle,newChild,setPid,retainPipe,retainReader,retainBorrow,releaseBorrows,retainTransfer,clearTransfers,retainTicket,clearTickets,retainCore,clearCore,recordStartupFailure)
import Control.Monad (unless, void)
import Data.IORef (IORef, newIORef, readIORef, writeIORef, atomicWriteIORef, atomicModifyIORef')
import GHC.Clock (getMonotonicTimeNSec)
import Warlock.Capture.Process.Lease (HeldExecutable, borrowHeld)
import Warlock.Capture.Process.Transfer (TransferTicket)
import Warlock.Capture.Process.Transfer.Internal (newOwnerToken, claimTransferWhen, coreHandle, coreCloseDiagnostic, closeCoreTransfer, TransferError(DeadlineExpired))
import qualified Crypto.Hash.SHA256 as SHA
import qualified Data.ByteString as B
import qualified Data.ByteString.Char8 as C
import Data.Bits ((.|.), (.&.))
import Foreign.C.Error (eSRCH, getErrno, throwErrnoIfMinus1Retry)
import Foreign.C.Types (CInt(..), CUInt(..))
import Foreign.Marshal.Alloc (allocaBytes)
import Foreign.Marshal.Utils (fillBytes)
import Foreign.Ptr (Ptr)
import Foreign.Storable (peekByteOff)
import Numeric (showHex)
import System.Exit (ExitCode(..))
import System.IO (Handle, IOMode(ReadMode), hClose, openBinaryFile)
import System.Posix.Files (fileMode, fileOwner, getSymbolicLinkStatus, isDirectory, isRegularFile, readSymbolicLink)
import System.Posix.Types (ProcessID)
import System.Posix.Signals (sigKILL)
import System.Process (CreateProcess(..), StdStream(..), createProcess_, getPid, proc, waitForProcess)
import System.Timeout (timeout)

foreign import ccall unsafe "waitid" c_waitid :: CInt -> CUInt -> Ptr () -> CInt -> IO CInt
foreign import ccall unsafe "getpgid" c_getpgid :: CInt -> IO CInt
foreign import ccall unsafe "kill" c_kill :: CInt -> CInt -> IO CInt

data Tool = Pactree FilePath | Readelf FilePath deriving (Eq,Show)
data ToolError = ToolHashMismatch | BadArguments | SpawnOrIO | TimedOut | OutputLimit | Unsuccessful Int | CleanupUncertain | OwnerBusy | OutputUnavailable | SessionClosed | TransferUnavailable deriving (Eq,Show)
-- Relative convenience creates exactly one absolute deadline. It is not
-- a renewable timeout and must also be passed to the channel implementation.
newtype AdmissionDeadline = AdmissionDeadline Integer deriving (Eq,Show)
deadlineAfter :: Int -> IO (Either ToolError AdmissionDeadline)
deadlineAfter micros
 | micros <= 0 || micros > 30000000 = pure (Left BadArguments)
 | otherwise = do
  now <- getMonotonicTimeNSec
  pure (Right (AdmissionDeadline (toInteger now + toInteger micros * 1000)))
remainingMicros :: AdmissionDeadline -> IO Int
remainingMicros (AdmissionDeadline end) = do
 now <- getMonotonicTimeNSec
 let left = end - toInteger now
 pure (fromInteger (max 0 (min 30000000 ((left + 999) `div` 1000))))

data SelectedInput = FixtureInput Handle | TicketInput TransferTicket
data SelectedSpawn = SelectedSpawn FilePath [String] (Maybe SelectedInput) [(String,String)] (Maybe HeldExecutable)
data Containment = BeforeSignalLeaderExited | BeforeSignalLeaderAlive | SignalStateUnknown deriving (Eq,Show)
data SelectedOutcome = SelectedOutcome { selectedOperation :: Either ToolError Captured, selectedContainment :: Containment, selectedCustody :: OwnerStatus } deriving (Eq,Show)
data SelectedResult = SelectedResult { selectedCapture :: Captured, groupContainmentAttempted :: Bool, leaderExitedBeforeContainment :: Bool } deriving (Eq,Show)
selectedFixture :: FilePath -> [String] -> Handle -> SelectedSpawn
selectedFixture exe args input = SelectedSpawn exe args (Just (FixtureInput input)) [("LC_ALL","C"),("LANG","C"),("PATH","/usr/bin")] Nothing
-- Fixture seam for actual ticket integration, never exported by public facade.
selectedTicketFixture :: FilePath -> [String] -> TransferTicket -> SelectedSpawn
selectedTicketFixture exe args ticket = SelectedSpawn exe args (Just (TicketInput ticket)) [("LC_ALL","C"),("LANG","C"),("PATH","/usr/bin")] Nothing
data SessionObservation = SessionObservation { observedPid :: ProcessID, observedStart :: B.ByteString, observedExecutable :: FilePath } deriving (Eq,Show)
-- Close admission atomically before draining the observation mutex. A timeout
-- while draining preserves quarantine: signaling/reaping cannot safely start.
data SessionScope = SessionScope (IORef Bool) (MVar ())
newSessionScope :: IO SessionScope
newSessionScope = SessionScope <$> newIORef True <*> newMVar ()
closeSessionScope :: SessionScope -> IO ()
closeSessionScope (SessionScope live _) = atomicWriteIORef live False
drainSessionScope :: SessionScope -> IO ()
drainSessionScope (SessionScope _ gate) = withMVar gate (const (pure ()))

-- No client callback or loop executes in this critical section; only one
-- nonreaping kernel/proc observation and its deadline checks do so.
inScope :: SessionScope -> AdmissionDeadline -> IO (Either ToolError a) -> IO (Either ToolError a)
inScope (SessionScope live gate) deadline action = do
 initial <- atomicModifyIORef' live (\v -> (v,v))
 budget <- remainingMicros deadline
 if not initial then pure (Left SessionClosed)
 else if budget == 0 then pure (Left TimedOut)
 else do
  finished <- timeout budget $ withMVar gate $ \_ -> do
   active <- atomicModifyIORef' live (\v -> (v,v))
   remaining <- remainingMicros deadline
   if not active then pure (Left SessionClosed)
   else if remaining == 0 then pure (Left TimedOut)
   else do
    result <- action
    activeAfter <- atomicModifyIORef' live (\v -> (v,v))
    after <- remainingMicros deadline
    if not activeAfter then pure (Left SessionClosed)
    else if after == 0 then pure (Left TimedOut) else pure result
  case finished of
   Just result -> pure result
   Nothing -> do
    active <- atomicModifyIORef' live (\v -> (v,v))
    pure (Left (if active then TimedOut else SessionClosed))

data Session = Session (IO (Either ToolError ())) (IO (Either ToolError SessionObservation))
awaitLeader :: Session -> IO (Either ToolError ())
awaitLeader (Session action _) = action
observeSession :: Session -> IO (Either ToolError SessionObservation)
observeSession (Session _ action) = action

-- Evidence only. Endpoint identity remains the channel owner's observation.
observeChild :: AdmissionDeadline -> ProcessID -> IO (Either ToolError SessionObservation)
observeChild deadline pid = do
 remaining <- remainingMicros deadline
 if remaining == 0 then pure (Left TimedOut) else do
  result <- try $ do
   let prefix = "/proc/" ++ show pid
   statBytes <- bracket (openBinaryFile (prefix ++ "/stat") ReadMode) hClose (\h -> B.hGet h 8193)
   unless (B.length statBytes <= 8192) (ioError (userError "proc stat too large"))
   executable <- readSymbolicLink (prefix ++ "/exe")
   let (_,afterName) = C.breakEnd (== ')') statBytes
   case drop 19 (C.words afterName) of
    start:_ | not (B.null start) && B.all (\c -> c >= 48 && c <= 57) start -> pure (SessionObservation pid start executable)
    _ -> ioError (userError "bad proc stat")
  pure (either (const (Left SpawnOrIO)) Right (result :: Either IOException SessionObservation))

selectedHeld :: HeldExecutable -> [String] -> TransferTicket -> [(String,String)] -> Either ToolError SelectedSpawn
selectedHeld lease args input environment =
 let safe (key,value) = not (null key) && all (`notElem` ['=', '\0']) key && '\0' `notElem` value
 in if all safe environment then Right (SelectedSpawn "/" args (Just (TicketInput input)) environment (Just lease)) else Left BadArguments

data Captured = Captured { output :: B.ByteString, diagnostics :: B.ByteString } deriving (Eq,Show)
toolSpec :: Tool -> (FilePath,B.ByteString,[String])
toolSpec (Pactree db) = ("/usr/bin/pactree","bc027d40a55f9bae8b833ee8ed3d23bf492830b4ac4dfce21c7eced1cb8e8e2c",["--dbpath",db,"--graph","--depth","1"])
toolSpec (Readelf staged) = ("/usr/bin/readelf","a72f12f3dd8c560554a3ba818bcecbda9178db5befbcc64d91bbb6a241fc21bc",["--wide","--file-header","--program-headers","--dynamic","--version-info","--notes","--",staged])

runTool :: Owner -> Tool -> [String] -> Int -> Int -> IO (Either ToolError Captured)
runTool owner tool suffix maxBytes micros = do
 let (exe,want,prefix) = toolSpec tool
 if not (valid tool suffix maxBytes micros) then pure (Left BadArguments) else do
  outcome <- try (do
   trustedTool exe
   bytes <- readTool exe
   if hexDigest (SHA.hash bytes) /= want then pure (Left ToolHashMismatch) else do
    result <- runOwned owner exe (prefix ++ suffix) maxBytes micros
    trustedTool exe
    after <- readTool exe
    pure (if hexDigest (SHA.hash after) /= want then Left ToolHashMismatch else result)) :: IO (Either IOException (Either ToolError Captured))
  result <- pure (either (const (Left SpawnOrIO)) id outcome)
  current <- status owner
  pure $ case current of Available -> result; _ -> Left CleanupUncertain
 where
  valid (Pactree db) [pkg] n t = absolute db && not (null pkg) && head pkg /= '-' && all safe pkg && bounds n t
  valid (Readelf staged) [] n t = absolute staged && bounds n t
  valid _ _ _ _ = False
  bounds n t = n > 0 && n <= 4194304 && t > 0 && t <= 30000000
  safe c = c `elem` (['a'..'z'] ++ ['0'..'9'] ++ "@._+-")
  absolute x = not (null x) && head x == '/' && not ('\0' `elem` x)

-- Only these two exact ordinary regular tool paths are supported at present.
-- Symlinks are refused, not followed: review must decide a pinned chain API.
-- Root-owned /usr ancestors plus separately reviewed ACL and trusted root are
-- prerequisites. Mode checks alone do NOT prove the absence of ACL grants.
trustedTool :: FilePath -> IO ()
trustedTool exe = do
 mapM_ directory ["/","/usr","/usr/bin"]
 st <- getSymbolicLinkStatus exe
 unless (fileOwner st == 0 && isRegularFile st && fileMode st .&. 0o022 == 0) (ioError (userError "untrusted tool"))
 where
  directory path = do
   st <- getSymbolicLinkStatus path
   unless (fileOwner st == 0 && isDirectory st && fileMode st .&. 0o022 == 0) (ioError (userError "untrusted ancestor"))

readTool :: FilePath -> IO B.ByteString
readTool path = bracket (openBinaryFile path ReadMode) hClose $ \h -> do
 result <- readBound h (64*1024*1024)
 case result of Left _ -> ioError (userError "tool bound"); Right bytes -> pure bytes

-- Fixture endpoints exist only in Internal, never in the public facade.
runFixture :: Owner -> FilePath -> [String] -> Int -> Int -> IO (Either ToolError Captured)
runFixture = runOwned
-- Controlled source test seam; production facade never exports it.
runFixtureWithHook :: Owner -> FilePath -> [String] -> Int -> Int -> (String -> IO ()) -> IO (Either ToolError Captured)
runFixtureWithHook = runOwnedHook
runFixturePinned :: Owner -> FilePath -> B.ByteString -> [String] -> Int -> Int -> IO (Either ToolError Captured)
runFixturePinned owner exe want args n us = do
 bytes <- try (readTool exe) :: IO (Either IOException B.ByteString)
 case bytes of Left _ -> pure (Left SpawnOrIO); Right b | hexDigest (SHA.hash b) /= want -> pure (Left ToolHashMismatch); Right _ -> runOwned owner exe args n us

-- Requires sole child-reaper ownership: no background library/SIGCHLD reaper
-- and no tool escaping its created process group. The zombie leader protects
-- the PGID against reuse until group signal and final waitForProcess.
leaderExited :: ProcessID -> IO Bool
leaderExited pid = allocaBytes #{size siginfo_t} $ \info -> do
 fillBytes info 0 #{size siginfo_t}
 _ <- throwErrnoIfMinus1Retry "waitid" (c_waitid #{const P_PID} (fromIntegral pid) info (#{const WEXITED} .|. #{const WNOHANG} .|. #{const WNOWAIT}))
 observed <- peekByteOff info #{offset siginfo_t, si_pid} :: IO CInt
 pure (observed /= 0)

killGroup :: Bool -> ProcessID -> IO ()
killGroup leaderDead pid = do
 result <- c_kill (negate (fromIntegral pid)) (fromIntegral sigKILL)
 if result == 0 then pure () else do
  err <- getErrno
  unless (err == eSRCH && leaderDead) (ioError (userError "owned process-group signal failed"))

readBound :: Handle -> Int -> IO (Either ToolError B.ByteString)
readBound h cap = go [] 0
 where
  go chunks count = do
   bytes <- B.hGetSome h 32768
   let total = count + B.length bytes
   if total > cap then pure (Left OutputLimit)
   else if B.null bytes then pure (Right (B.concat (reverse chunks)))
   else go (bytes:chunks) total

type ReaderResult = Either SomeException (Either ToolError B.ByteString)
spawnReader :: Handle -> Int -> IO (ThreadId, IO ReaderResult)
spawnReader h cap = do
 done <- newEmptyMVar
 tid <- forkFinally (readBound h cap) (putMVar done)
 pure (tid,readMVar done)

-- Preserve the initiating exception and cleanup diagnostic independently.
-- The caller's surrounding mask covers the capability handoff and retention.
startupAction :: forall a. Owner -> IO a -> IO () -> IO a
startupAction owner action cleanup = do
 first <- try action :: IO (Either SomeException a)
 case first of
  Right value -> pure value
  Left original -> do
   second <- try cleanup :: IO (Either SomeException ())
   let cleanupException = either Just (const Nothing) second
   recordStartupFailure owner original cleanupException
   case (fromException original :: Maybe SomeAsyncException) of
    Just _ -> throwIO original
    Nothing -> case cleanupException of
     Just ex -> case (fromException ex :: Maybe SomeAsyncException) of
      Just _ -> throwIO ex
      Nothing -> throwIO original
     Nothing -> throwIO original

runOwned :: Owner -> FilePath -> [String] -> Int -> Int -> IO (Either ToolError Captured)
runOwned owner exe args cap micros = runOwnedHook owner exe args cap micros (const (pure ()))

runOwnedHook :: Owner -> FilePath -> [String] -> Int -> Int -> (String -> IO ()) -> IO (Either ToolError Captured)
runOwnedHook owner exe args cap micros hook = do
 deadline <- deadlineAfter micros
 case deadline of
  Left err -> pure (Left err)
  Right d -> runSelectedHook owner (SelectedSpawn exe args Nothing [("LC_ALL","C"),("LANG","C"),("PATH","/usr/bin")] Nothing) cap d awaitLeader hook Nothing

-- One scoped admission and one cleanup path. The callback receives no raw
-- process handle and cannot reap or signal the selected process through it.
runSelected :: Owner -> SelectedSpawn -> Int -> Int -> (Session -> IO (Either ToolError ())) -> IO (Either ToolError SelectedResult)
runSelected owner selection cap micros conversation = do
 deadline <- deadlineAfter micros
 case deadline of
  Left err -> pure (Left err)
  Right d -> runSelectedUntil owner selection cap d conversation

runSelectedUntil :: Owner -> SelectedSpawn -> Int -> AdmissionDeadline -> (Session -> IO (Either ToolError ())) -> IO (Either ToolError SelectedResult)
runSelectedUntil owner selection cap deadline conversation = do
 outcome <- runSelectedDetailed owner selection cap deadline conversation
 pure $ case (selectedOperation outcome,selectedContainment outcome) of
  (Right captured,BeforeSignalLeaderExited) -> Right (SelectedResult captured True True)
  (Right captured,BeforeSignalLeaderAlive) -> Right (SelectedResult captured True False)
  (Right _,SignalStateUnknown) -> Left CleanupUncertain
  (Left err,_) -> Left err

-- Distinguishes the observation made immediately before the group signal
-- from both the operation result and the retained custody state.
runSelectedDetailed :: Owner -> SelectedSpawn -> Int -> AdmissionDeadline -> (Session -> IO (Either ToolError ())) -> IO SelectedOutcome
runSelectedDetailed owner selection cap deadline conversation = do
 observedExit <- newIORef Nothing
 result <- runSelectedHook owner selection cap deadline conversation (const (pure ())) (Just observedExit)
 exited <- readIORef observedExit
 state <- status owner
 let containment = case exited of Just True -> BeforeSignalLeaderExited; Just False -> BeforeSignalLeaderAlive; Nothing -> SignalStateUnknown
 pure (SelectedOutcome result containment state)

-- Source-fixture seam only; hooks run at actual lifecycle points.
runSelectedFixtureHook :: Owner -> SelectedSpawn -> Int -> AdmissionDeadline -> (Session -> IO (Either ToolError ())) -> (String -> IO ()) -> IO (Either ToolError Captured)
runSelectedFixtureHook owner selection cap deadline conversation hook = runSelectedHook owner selection cap deadline conversation hook Nothing

runSelectedHook :: Owner -> SelectedSpawn -> Int -> AdmissionDeadline -> (Session -> IO (Either ToolError ())) -> (String -> IO ()) -> Maybe (IORef (Maybe Bool)) -> IO (Either ToolError Captured)
runSelectedHook owner (SelectedSpawn exe args selectedInput selectedEnv selectedLease) cap deadline conversation hook exitObservation
 | null exe || head exe /= '/' || cap <= 0 || cap > 4194304 = pure (Left BadArguments)
 | otherwise = mask $ \restore -> do
  available <- remainingMicros deadline
  if available == 0 then pure (Left TimedOut) else do
   admitted <- begin owner
   if not admitted then pure (Left OwnerBusy) else do
    outcome <- (try (do
     selectedPath <- case selectedLease of
      Nothing -> pure exe
      Just lease -> do
       borrowed <- borrowHeld lease
       case borrowed of
        Left _ -> ioError (userError "executable lease unavailable")
        Right (path,release) -> retainBorrow owner release >> pure path
     claimBudget <- remainingMicros deadline
     if claimBudget == 0 then releaseBorrows owner >> abortBegin owner >> pure (Left TimedOut) else do
      prepared <- case selectedInput of
       Nothing -> pure (Right (Nothing,pure ()))
       Just (FixtureInput h) -> pure (Right (Just h,hClose h))
       Just (TicketInput ticket) -> do
        retainTicket owner ticket
        token <- newOwnerToken
        claimed <- claimTransferWhen ((> 0) <$> remainingMicros deadline) token ticket
        case claimed of
         Left DeadlineExpired -> pure (Left TimedOut)
         Left _ -> pure (Left TransferUnavailable)
         Right core -> do
          -- The surrounding mask makes claim -> owner capability publication
          -- one handoff; no further fallible work precedes this retention.
          retainCore owner core
          borrowedHandle <- coreHandle core
          case borrowedHandle of
           Left _ -> pure (Left CleanupUncertain)
           Right h -> pure (Right (Just h, do
            result <- closeCoreTransfer core
            case result of
             Left _ -> do
              cause <- coreCloseDiagnostic core
              case cause of Just ex -> throwIO ex; Nothing -> ioError (userError "selected transfer close uncertain")
             Right () -> pure ()))
      case prepared of
       Left problem -> do
        if problem == CleanupUncertain then failUnsettled owner "claimed-ticket-state-uncertain" else do
         releaseBorrows owner
         clearTickets owner
         abortBegin owner
        pure (Left problem)
       Right (selectedHandle,closeInput) -> do
        beforeSpawn <- startupAction owner (hook "before-spawn" >> remainingMicros deadline) closeInput
        if beforeSpawn == 0 then do
         closeInput
         releaseBorrows owner
         clearCore owner
         clearTickets owner
         abortBegin owner
         pure (Left TimedOut)
        else do
         case selectedInput of Just (FixtureInput h) -> retainTransfer owner h; _ -> pure ()
         (out,err,ph,pid,child) <- startupAction owner (spawn selectedPath selectedHandle) closeInput
         -- Every successful reader acquisition is recorded before unmasking.
         (outThread,outResult) <- spawnReader out cap `onException` (cleanupStart closeInput child out err ph pid Nothing)
         retainReader child outThread (void outResult)
         (errThread,errResult) <- spawnReader err cap `onException` (cleanupStart closeInput child out err ph pid (Just (outThread,outResult)))
         retainReader child errThread (void errResult)
         -- Transfer close happens only after publication and both reader registrations.
         -- A failed close is retained as uncertainty; never run the conversation.
         transfer <- try (hook "transfer-close" >> closeInput) :: IO (Either SomeException ())
         scope <- newSessionScope
         remaining <- remainingMicros deadline
         observed <- case transfer of
          Left ex -> pure (Left ex)
          Right () -> try (do
           result <- restore (timeout remaining (conversation (Session (poll scope pid outResult errResult) (inScope scope deadline (do hook "scope-observation"; value <- observeChild deadline pid; hook "scope-observation-complete"; pure value)))))
           hook "after-conversation"
           pure result) :: IO (Either SomeException (Maybe (Either ToolError ())))
         afterConversation <- remainingMicros deadline
         let admissionObserved = case observed of
              Right (Just (Right ())) | afterConversation == 0 -> Right Nothing
              _ -> observed
         -- Refuse new observations before waiting for any existing observation.
         closeSessionScope scope
         drained <- bounded (hook "scope-invalidate" >> drainSessionScope scope)
         if not (completed drained) then do
          quarantine owner (Just child) ["session-observation-not-drained"]
          case asyncErrors observed ++ asyncErrors drained of
           first:_ -> throwIO first
           [] -> pure (Left CleanupUncertain)
         else do
          -- Signal the still-owned group while leader remains unreaped. Reader
          -- results are awaited before closing pipe handles to preserve final bytes.
          reaped <- try (terminateReap ph pid) :: IO (Either SomeException ExitCode)
          captured <- bounded (hook "capture" >> ((,) <$> outResult <*> errResult))
          killedA <- bounded (hook "stop-out" >> killThread outThread)
          killedB <- bounded (hook "stop-err" >> killThread errThread)
          joinedA <- bounded (hook "join-out" >> outResult)
          joinedB <- bounded (hook "join-err" >> errResult)
          closeA <- if completed joinedA then bounded (hook "close-out" >> hClose out) else pure (Right Nothing)
          closeB <- if completed joinedB then bounded (hook "close-err" >> hClose err) else pure (Right Nothing)
          let failures = [T.pack label | (label,failed) <- [("group-or-reap",either (const True) (const False) reaped),("stdout-join",not (completed joinedA)),("stderr-join",not (completed joinedB)),("stdout-close",not (completed closeA)),("stderr-close",not (completed closeB))], failed]
          let transferFailures = either (const ["selected-stdin-close"]) (const []) transfer
              allFailures = failures ++ transferFailures
          if null allFailures then releaseBorrows owner >> clearTransfers owner >> clearCore owner >> clearTickets owner >> settle owner else quarantine owner (Just child) allFailures
          let deferred = asyncErrors observed ++ asyncErrors transfer ++ asyncErrors reaped ++ asyncErrors captured ++ asyncErrors killedA ++ asyncErrors killedB ++ asyncErrors joinedA ++ asyncErrors joinedB ++ asyncErrors closeA ++ asyncErrors closeB
          case deferred of first:_ -> throwIO first; [] -> pure ()
          case (admissionObserved,reaped,captured,allFailures) of
           (Left ex,_,_,_) -> throwIO ex
           (_,_,_,_ : _) -> pure (Left CleanupUncertain)
           (_,_,_,[]) | not (completed killedA && completed killedB) -> pure (Left OutputUnavailable)
           (Right Nothing,_,_,[]) -> pure (Left TimedOut)
           (Right (Just (Left e)),_,_,[]) -> pure (Left e)
           (Right (Just (Right ())),_,_,[]) | not (completed captured) -> pure (Left OutputUnavailable)
           (Right (Just (Right ())),Right exitStatus,Right (Just (a,b)),[]) -> case exitStatus of
            ExitFailure n -> pure (Left (Unsuccessful n))
            ExitSuccess -> pure $ case (a,b) of (Right (Right x),Right (Right y)) -> Right (Captured x y); (Right (Left e),_) -> Left e; (_,Right (Left e)) -> Left e; _ -> Left SpawnOrIO
           _ -> pure (Left CleanupUncertain)
     ) :: IO (Either IOException (Either ToolError Captured))) `onException` failUnsettled owner "interrupted"
    case outcome of
     Left _ -> do
      failUnsettled owner "spawn-or-io"
      ownerState <- status owner
      pure (if ownerState == Available then Left SpawnOrIO else Left CleanupUncertain)
     Right value -> pure value
 where
  spawn selectedPath selectedHandle = do
   (input,out,err,ph) <- createProcess_ "warlock-owned-selected" (proc selectedPath args) { env=Just selectedEnv, std_in=maybe NoStream UseHandle selectedHandle, std_out=CreatePipe, std_err=CreatePipe, close_fds=True, create_group=True }
   child <- newChild ph
   publish owner child
   mapM_ (retainPipe child) [h | Just h <- [input,out,err]]
   case (input,out,err) of
    (Nothing,Just o,Just e) -> do
     identity <- getPid ph
     case identity of
      Just pid | pid > 0 -> do
       setPid child pid
       group <- c_getpgid (fromIntegral pid)
       if group == fromIntegral pid then pure (o,e,ph,pid,child)
       else quarantine owner (Just child) ["unconfirmed-owned-group"] >> ioError (userError "unconfirmed owned group")
      _ -> quarantine owner (Just child) ["missing-owned-pid"] >> ioError (userError "missing owned pid")
    _ -> quarantine owner (Just child) ["missing-owned-pipes"] >> ioError (userError "missing owned pipes")
  poll scope pid getOut getErr = do
   -- Only one WNOWAIT/readers check per gate acquisition. Sleeps are outside.
   step <- inScope scope deadline $ do
    hook "scope-poll"
    a <- nonblocking getOut
    b <- nonblocking getErr
    case (a,b) of
     (Just (Right (Left x)),_) -> pure (Left x)
     (_,Just (Right (Left x))) -> pure (Left x)
     (Just (Left _),_) -> pure (Left SpawnOrIO)
     (_,Just (Left _)) -> pure (Left SpawnOrIO)
     _ -> Right <$> leaderExited pid
   case step of
    Left err -> pure (Left err)
    Right True -> pure (Right ())
    Right False -> do
     remaining <- remainingMicros deadline
     if remaining == 0 then pure (Left TimedOut)
     else threadDelay (min 10000 remaining) >> poll scope pid getOut getErr
  nonblocking reader = timeout 1 reader
  asyncErrors :: Either SomeException a -> [SomeException]
  asyncErrors result = case result of
   Left ex -> case (fromException ex :: Maybe SomeAsyncException) of Just _ -> [ex]; Nothing -> []
   Right _ -> []
  bounded :: IO a -> IO (Either SomeException (Maybe a))
  bounded action = try (timeout 2000000 action)
  completed result = case result of Right (Just _) -> True; _ -> False
  cleanupStart closeInput child out err ph pid reader = do
   -- Publish custody first; each independent action has its own bound.
   quarantine owner (Just child) ["startup-cleanup-pending"]
   stop <- bounded (terminateReap ph pid)
   cancel <- case reader of Nothing -> pure (Right (Just ())); Just (tid,_) -> bounded (killThread tid)
   joinedResult <- case reader of Nothing -> pure (Right (Just ())); Just (_,result) -> fmap (fmap (fmap (const ()))) (bounded result)
   let joined = completed joinedResult
   firstClose <- if joined then bounded (hook "close-out" >> hClose out) else pure (Right Nothing)
   secondClose <- bounded (hClose err)
   transferClose <- bounded closeInput
   let failures = [T.pack name | (name,bad) <- [("startup-group-reap",not (completed stop)),("startup-reader-stop",not (completed cancel)),("startup-reader-join",not joined),("startup-stdout-close",not (completed firstClose)),("startup-stderr-close",not (completed secondClose)),("startup-transfer-close",not (completed transferClose))], bad]
   quarantine owner (Just child) (if null failures then ["startup-review-required"] else failures)
   case asyncErrors stop ++ asyncErrors cancel ++ asyncErrors joinedResult ++ asyncErrors firstClose ++ asyncErrors secondClose ++ asyncErrors transferClose of
    first:_ -> throwIO first
    [] -> pure ()

  terminateReap ph pid = do
   -- Confirm owned child is still observable and unreaped before any signal.
   wasDead <- leaderExited pid
   mapM_ (\ref -> writeIORef ref (Just wasDead)) exitObservation
   killGroup wasDead pid
   result <- timeout 2000000 (waitForProcess ph)
   maybe (ioError (userError "owned child reap timed out")) pure result

hexDigest :: B.ByteString -> B.ByteString
hexDigest = C.pack . concatMap format . B.unpack
 where format n = let h = showHex n "" in if length h == 1 then '0':h else h
