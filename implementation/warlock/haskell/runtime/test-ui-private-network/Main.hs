{-# LANGUAGE OverloadedStrings #-}
{-# LANGUAGE ScopedTypeVariables #-}
-- SourceScope: raw same-UID socket fixture. It does not establish selected-image,
-- backend admission, native/window authority, cross-UID, or original acceptance.
-- This executable and its child must be built without -threaded.
module Main (main) where

import Control.Exception (AsyncException(ThreadKilled), IOException, SomeException, displayException, throwTo, try)
import Control.Concurrent (forkFinally)
import Control.Concurrent.MVar (MVar, newEmptyMVar, putMVar, takeMVar)
import Control.Monad (forM_, replicateM, replicateM_, unless, void)
import qualified Data.ByteString.Char8 as C
import GHC.IO.Exception (IOException(..))
import qualified Network.Socket as S
import qualified Network.Socket.ByteString as N
import System.Exit (ExitCode(..), exitFailure)
import System.IO (hFlush, stdout)
import System.Posix.Files (deviceID, fileID, getFileStatus)
import System.Posix.IO (FdOption(CloseOnExec), closeFd, createPipe, dup, dupTo, fdReadBuf, fdWrite, queryFdOption)
import Foreign (allocaBytes)
import System.Posix.Process (ProcessStatus(..), exitImmediately, forkProcess, getProcessID, getProcessStatus)
import System.Posix.Signals (sigKILL, signalProcess)
import System.Posix.Types (Fd(..), ProcessID)
import System.Posix.User (getRealGroupID, getRealUserID)
import System.Timeout (timeout)
import System.Directory (listDirectory)
import Data.List (isPrefixOf, sort)
import Warlock.Capture.Process.Bootstrap (deadlineAfter)
import Warlock.Protocol.Identity (binding, parseCounter)
import Warlock.Ui.Native (adoptNative, nativePeerPid, retireNative)
import Warlock.Ui.PrivateNetwork (enterPrivateNetwork, verifyPrivateNetwork, withPeerNetwork)

check :: String -> Bool -> IO ()
check name ok = do
 putStrLn (name ++ "=" ++ if ok then "PASS" else "FAIL")
 hFlush stdout
 unless ok (ioError (userError name))

namespace :: String -> IO (Integer,Integer)
namespace who = do
 status <- getFileStatus ("/proc/" ++ who ++ "/ns/net")
 pure (toInteger (deviceID status), toInteger (fileID status))

mapMatches :: Integer -> String -> Bool
mapMatches ident contents = case map words (lines contents) of
 [[inside,outside,count]] -> reads inside == [(ident,"")] && reads outside == [(ident,"")] && reads count == [(1 :: Integer,"")]
 _ -> False

observation :: String -> Either IOException (Integer,Integer) -> IO ()
observation label result = do
 case result of
  Right ident -> putStrLn (label ++ "=ok " ++ show ident)
  Left err -> putStrLn (label ++ "=error errno=" ++ show (ioe_errno err) ++ " detail=" ++ displayException err)
 hFlush stdout

child :: Bool -> ProcessID -> ProcessID -> ProcessID -> S.Socket -> IO ()
child private parent otherPid stale endpoint = do
 result <- try $ do
  S.withFdSocket endpoint $ \raw -> void (dupTo (Fd raw) (Fd 0))
  S.close endpoint
  escaped <- withPeerNetwork $ \witness -> do
   uid <- getRealUserID
   gid <- getRealGroupID
   before <- namespace "self"
   tasks <- listDirectory "/proc/self/task"
   status <- readFile "/proc/self/status"
   beforeUidMap <- readFile "/proc/self/uid_map"
   beforeGidMap <- readFile "/proc/self/gid_map"
   putStrLn ("pre_unshare_tasks=" ++ show tasks ++ " status=" ++ show [line | line <- lines status, any (`isPrefixOf` line) ["Threads:","Uid:","Gid:","NSpid:","NoNewPrivs:","Seccomp:"]])
   putStrLn ("pre_unshare_uid_map=" ++ show beforeUidMap ++ " gid_map=" ++ show beforeGidMap)
   hFlush stdout
   entry <- try (if private then enterPrivateNetwork else pure ()) :: IO (Either IOException ())
   case entry of
    Left err -> do
     putStrLn ("enter_private_network=error errno=" ++ show (ioe_errno err) ++ " detail=" ++ displayException err)
     hFlush stdout
     ioError err
    Right () -> putStrLn "enter_private_network=ok"
   after <- namespace "self"
   putStrLn ("source_scope=owned_socket_fixture selected_backend=false native_authority=false cross_uid=false")
   putStrLn ("self_net_before=" ++ show before ++ " self_net_after=" ++ show after)
   procParent <- try (namespace (show parent)) :: IO (Either IOException (Integer,Integer))
   observation "post_enter_parent_net_stat" procParent
   uidMap <- readFile "/proc/self/uid_map"
   gidMap <- readFile "/proc/self/gid_map"
   dev <- C.readFile "/proc/net/dev"
   putStrLn ("uid_map=" ++ show uidMap ++ " gid_map=" ++ show gidMap ++ " net_dev=" ++ show dev)
   -- A false check is meaningful only after this exact real peer succeeds.
   baseline <- verifyPrivateNetwork witness
   if private then check "witness_valid_before_socket_controls" baseline
              else check "same_network_before_socket_controls" (not baseline)
   -- A fork inherits descriptors but must not inherit the parent's authority.
   -- Require a true parent control first so same-network refusal cannot mask it.
   if private then do
    inherited <- forkProcess $ do
     accepted <- verifyPrivateNetwork witness
     exitImmediately (if accepted then ExitFailure 1 else ExitSuccess)
    rejected <- waitBounded inherited
    check "forked_process_cannot_use_witness" rejected
    stillValid <- verifyPrivateNetwork witness
    check "original_owner_retains_witness" stillValid
   else pure ()
   -- Alternating replacement/missing fd0 and restoration uses the same opaque
   -- witness. The private case checks a successful control on every iteration.
   forM_ [1..8 :: Int] $ \iteration -> do
    saved <- dup (Fd 0)
    (otherLeft,otherRight) <- S.socketPair S.AF_UNIX S.Stream S.defaultProtocol
    S.withFdSocket otherLeft $ \raw -> void (dupTo (Fd raw) (Fd 0))
    swapped <- verifyPrivateNetwork witness
    closeFd (Fd 0)
    missing <- verifyPrivateNetwork witness
    void (dupTo saved (Fd 0))
    closeFd saved
    S.close otherLeft
    S.close otherRight
    restored <- verifyPrivateNetwork witness
    check ("swapped_socket_refused_" ++ show iteration) (not swapped)
    check ("missing_socket_refused_" ++ show iteration) (not missing)
    check ("restored_socket_matches_original_" ++ show iteration) (restored == baseline)
   counter <- either (ioError . userError . show) pure (parseCounter False "1")
   bound <- either (ioError . userError . show) pure (binding counter counter counter)
   deadline <- deadlineAfter 5000000 >>= either (ioError . userError . show) pure
   retained <- dup (Fd 0)
   native <- adoptNative bound deadline
   cloexec <- queryFdOption (Fd 0) CloseOnExec
   let peer = nativePeerPid native
   putStrLn ("so_peercred_pid=" ++ show peer ++ " expected_fixture_parent_pid=" ++ show parent ++ " foreign_pid=" ++ show otherPid ++ " reaped_stale_pid=" ++ show stale ++ " cloexec=" ++ show cloexec)
   same <- verifyPrivateNetwork witness
   putStrLn ("verify_actual_peer_witness=" ++ show same)
   hFlush stdout
   retired <- retireNative native
   void (dupTo retained (Fd 0))
   closeFd retained
   check "socket_peer_is_parent" (peer == fromIntegral parent)
   check "cloexec_before_engine" cloexec
   check "owned_socket_retired" retired
   if private then do
    check "fresh_net_namespace" (before /= after)
    check "own_uid_map" (mapMatches (toInteger uid) uidMap)
    check "own_gid_map" (mapMatches (toInteger gid) gidMap)
    -- The held pre-transition witness is independent of this diagnostic stat.
    check "private_network_verified" same
   else check "same_network_refused" (not same)
   pure witness
  -- The peer socket remains present; fill recently retired descriptor numbers
  -- before attempting to reuse the escaped handle, then close owned pipes.
  pipes <- mapM (const createPipe) [1..8 :: Int]
  escapedAccepted <- verifyPrivateNetwork escaped
  mapM_ (\(r,w) -> closeFd r >> closeFd w) pipes
  check "escaped_retired_witness_refused" (not escapedAccepted)
 case result of
  Right () -> exitImmediately ExitSuccess
  Left (err :: SomeException) -> do
   putStrLn ("child_failure=" ++ displayException err)
   hFlush stdout
   exitImmediately (ExitFailure 1)

waitBounded :: ProcessID -> IO Bool
waitBounded pid = do
 outcome <- timeout 5000000 (getProcessStatus True False pid)
 case outcome of
  Just (Just (Exited ExitSuccess)) -> pure True
  Just status -> putStrLn ("child_status=" ++ show status) >> pure False
  Nothing -> do
   putStrLn "child_status=deadline_expired"
   signalProcess sigKILL pid
   void (getProcessStatus True False pid)
   pure False

runCase :: Bool -> ProcessID -> ProcessID -> IO Bool
runCase private otherPid stale = do
 parent <- getProcessID
 (left,right) <- S.socketPair S.AF_UNIX S.Stream S.defaultProtocol
 putStrLn (if private then "case=fresh_private_network" else "case=no_private_network")
 hFlush stdout
 pid <- forkProcess $ do
  S.close left
  child private parent otherPid stale right
 S.close right
 ok <- waitBounded pid
 S.close left
 pure ok

-- The parent stays alive but closes its endpoint after the private positive.
-- Two pipes synchronize the close, so this checks actual EOF, not peer death.
runClosedPeerCase :: IO Bool
runClosedPeerCase = do
 (left,right) <- S.socketPair S.AF_UNIX S.Stream S.defaultProtocol
 (readyRead,readyWrite) <- createPipe
 (ackRead,ackWrite) <- createPipe
 pid <- forkProcess $ do
  S.close left
  closeFd readyRead
  closeFd ackWrite
  outcome <- try $ do
   S.withFdSocket right $ \raw -> void (dupTo (Fd raw) (Fd 0))
   S.close right
   withPeerNetwork $ \witness -> do
    enterPrivateNetwork
    before <- verifyPrivateNetwork witness
    check "live_peer_before_close" before
    void (fdWrite readyWrite "r")
    received <- timeout 5000000 (allocaBytes 1 (\buffer -> fdReadBuf ackRead buffer 1))
    check "peer_close_synchronized" (received == Just 1)
    after <- verifyPrivateNetwork witness
    check "closed_peer_refused_while_parent_alive" (not after)
   closeFd readyWrite
   closeFd ackRead
  case outcome of
   Right () -> exitImmediately ExitSuccess
   Left (err :: SomeException) -> do
    putStrLn ("closed_peer_fixture_failure=" ++ displayException err)
    hFlush stdout
    exitImmediately (ExitFailure 1)
 S.close right
 closeFd readyWrite
 closeFd ackRead
 ready <- timeout 5000000 (allocaBytes 1 (\buffer -> fdReadBuf readyRead buffer 1))
 S.close left
 if ready == Just 1 then void (fdWrite ackWrite "a") else pure ()
 closeFd readyRead
 closeFd ackWrite
 ok <- waitBounded pid
 pure (ready == Just 1 && ok)

-- Exercise the public callback/verification APIs concurrently; cancellation is
-- asynchronous and never assumes a particular scheduler interleaving.
concurrentRetirement :: IO ()
concurrentRetirement = forM_ [1..4 :: Int] $ \iteration -> do
 before <- sort <$> listDirectory "/proc/self/fd"
 ready <- newEmptyMVar
 blocker <- newEmptyMVar :: IO (MVar ())
 ownerDone <- newEmptyMVar
 owner <- forkFinally (withPeerNetwork $ \witness -> do
  workers <- replicateM 8 newEmptyMVar
  forM_ workers $ \done -> void $ forkFinally
   (replicateM_ 8 (void (verifyPrivateNetwork witness))) (putMVar done)
  putMVar ready (witness,workers)
  takeMVar blocker) (putMVar ownerDone)
 (escaped,workers) <- takeMVar ready
 -- Both senders are joined; either can arrive during retirement or after exit.
 senders <- replicateM 2 newEmptyMVar
 forM_ senders $ \done -> void $ forkFinally (throwTo owner ThreadKilled) (putMVar done)
 outcome <- takeMVar ownerDone
 forM_ senders (void . takeMVar)
 forM_ workers $ \done -> do
  completed <- timeout 5000000 (takeMVar done)
  check ("concurrent_verifier_joined_" ++ show iteration) (case completed of Just (Right ()) -> True; _ -> False)
 accepted <- verifyPrivateNetwork escaped
 check ("concurrent_retired_witness_refused_" ++ show iteration) (not accepted)
 check ("concurrent_owner_did_not_succeed_" ++ show iteration) (case outcome of Left _ -> True; Right _ -> False)
 after <- sort <$> listDirectory "/proc/self/fd"
 check ("concurrent_descriptors_retired_" ++ show iteration) (after == before)

-- Exercise real witness acquisition and both normal/exception bracket exit.
-- This does not enter a namespace, and holds only this fixture's own socket.
runRetirementCase :: IO Bool
runRetirementCase = do
 (left,right) <- S.socketPair S.AF_UNIX S.Stream S.defaultProtocol
 N.sendAll left "witness-sentinel"
 pid <- forkProcess $ do
  S.close left
  outcome <- try $ do
   S.withFdSocket right $ \raw -> void (dupTo (Fd raw) (Fd 0))
   S.close right
   before <- sort <$> listDirectory "/proc/self/fd"
   -- A Unix socket created by this child has self credentials, not the parent.
   saved <- dup (Fd 0)
   (selfLeft,selfRight) <- S.socketPair S.AF_UNIX S.Stream S.defaultProtocol
   S.withFdSocket selfLeft $ \raw -> void (dupTo (Fd raw) (Fd 0))
   selfResult <- try (withPeerNetwork (\_ -> pure ())) :: IO (Either IOException ())
   check "self_created_unix_peer_refused" (case selfResult of Left _ -> True; Right _ -> False)
   (readEnd,writeEnd) <- createPipe
   void (dupTo readEnd (Fd 0))
   pipeResult <- try (withPeerNetwork (\_ -> pure ())) :: IO (Either IOException ())
   check "non_socket_fd_refused" (case pipeResult of Left _ -> True; Right _ -> False)
   void (dupTo saved (Fd 0))
   closeFd saved
   closeFd readEnd
   closeFd writeEnd
   S.close selfLeft
   S.close selfRight
   forM_ [1..8 :: Int] $ \iteration -> do
    withPeerNetwork (\_ -> pure ())
    failed <- try (withPeerNetwork (\_ -> ioError (userError "controlled witness callback failure"))) :: IO (Either IOException ())
    check ("exception_propagates_" ++ show iteration) (case failed of Left _ -> True; Right _ -> False)
    after <- sort <$> listDirectory "/proc/self/fd"
    check ("witness_descriptors_retired_" ++ show iteration) (after == before)
   concurrentRetirement
   _ <- getFileStatus "/proc/self/fd/0"
   copied <- dup (Fd 0)
   let Fd raw = copied
   reader <- S.mkSocket raw
   let readExact 0 = pure C.empty
       readExact remaining = do
        part <- N.recv reader remaining
        unless (not (C.null part)) (ioError (userError "sentinel EOF"))
        rest <- readExact (remaining - C.length part)
        pure (part <> rest)
   bytes <- readExact 16
   S.close reader
   check "witness_checks_do_not_consume_frame" (bytes == "witness-sentinel")
   pure ()
  case outcome of
   Right () -> exitImmediately ExitSuccess
   Left (err :: SomeException) -> do
    putStrLn ("retirement_fixture_failure=" ++ displayException err)
    hFlush stdout
    exitImmediately (ExitFailure 1)
 S.close right
 ok <- waitBounded pid
 S.close left
 pure ok

main :: IO ()
main = S.withSocketsDo $ do
 -- The otherPid process is real, alive and in the parent's network namespace.
 -- A separate already-reaped PID supplies a stale /proc lookup.
 stale <- forkProcess (exitImmediately ExitSuccess)
 status <- getProcessStatus True False stale
 unless (status == Just (Exited ExitSuccess)) (ioError (userError "stale fixture did not exit normally"))
 (readEnd,writeEnd) <- createPipe
 otherPid <- forkProcess $ do
  closeFd writeEnd
  allocaBytes 1 (\buffer -> void (fdReadBuf readEnd buffer 1))
  closeFd readEnd
  exitImmediately ExitSuccess
 closeFd readEnd
 unless (otherPid /= stale) (ioError (userError "stale PID reused by live fixture"))
 retired <- runRetirementCase
 closedPeer <- runClosedPeerCase
 negative <- runCase False otherPid stale
 positive <- runCase True otherPid stale
 void (fdWrite writeEnd "x")
 closeFd writeEnd
 foreignStatus <- getProcessStatus True False otherPid
 let clean = foreignStatus == Just (Exited ExitSuccess)
 putStrLn ("foreign_fixture_cleanup=" ++ show foreignStatus)
 unless (retired && closedPeer && negative && positive && clean) exitFailure
