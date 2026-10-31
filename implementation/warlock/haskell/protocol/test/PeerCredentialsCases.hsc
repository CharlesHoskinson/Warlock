{-# LANGUAGE ForeignFunctionInterface #-}
{-# LANGUAGE OverloadedStrings #-}
#define _GNU_SOURCE 1
#include <sys/socket.h>
#include <sys/uio.h>
#include <unistd.h>
#include <fcntl.h>
module Main (main) where
import Control.Exception (AsyncException(..), SomeException, SomeAsyncException, bracket, fromException, toException, throwIO, try)
import Control.Monad (unless)
import Data.IORef (newIORef, modifyIORef', readIORef)
import Foreign
import Foreign.C
import qualified Data.ByteString as B
import qualified Network.Socket as S
import qualified Network.Socket.ByteString as N
import System.Posix.IO (createPipe, closeFd)
import System.Posix.Process (forkProcess, getProcessID, getProcessStatus, exitImmediately)
import System.Exit (ExitCode(..))
import System.Posix.Types (Fd(..))
import System.Posix.User (getRealUserID, getRealGroupID)
import Warlock.Transport.PeerCredentials
foreign import ccall unsafe "sendmsg" sendMsg :: CInt -> Ptr () -> CInt -> IO (#{type ssize_t})
foreign import ccall unsafe "close" closeOne :: CInt -> IO CInt
foreign import ccall unsafe "fcntl" fcntlGet :: CInt -> CInt -> IO CInt
check :: Bool -> String -> IO ()
check value message = unless value (ioError (userError message))
withPair :: ((S.Socket,S.Socket) -> IO a) -> IO a
withPair = bracket (S.socketPair S.AF_UNIX S.Stream S.defaultProtocol) (\(a,b) -> S.close a >> S.close b)

-- Real kernel rights frame, generated in Haskell with the host headers.
sendRight :: S.Socket -> Fd -> IO ()
sendRight socket (Fd right) = S.withFdSocket socket $ \socketFd ->
  allocaBytes 1 $ \byte -> allocaBytes #{size struct iovec} $ \iov ->
  allocaBytes #{size struct msghdr} $ \message -> allocaBytes #{const CMSG_SPACE(sizeof(int))} $ \control -> do
    fillBytes iov 0 #{size struct iovec}; fillBytes message 0 #{size struct msghdr}
    fillBytes control 0 #{const CMSG_SPACE(sizeof(int))}; poke byte (120 :: Word8)
    #{poke struct iovec, iov_base} iov (castPtr byte :: Ptr ())
    #{poke struct iovec, iov_len} iov (1 :: CSize)
    #{poke struct msghdr, msg_iov} message (castPtr iov :: Ptr ())
    #{poke struct msghdr, msg_iovlen} message (1 :: CSize)
    #{poke struct msghdr, msg_control} message (castPtr control :: Ptr ())
    #{poke struct msghdr, msg_controllen} message (fromIntegral (#{const CMSG_SPACE(sizeof(int))} :: Int) :: CSize)
    #{poke struct cmsghdr, cmsg_len} control (fromIntegral (#{const CMSG_LEN(sizeof(int))} :: Int) :: CSize)
    #{poke struct cmsghdr, cmsg_level} control (#{const SOL_SOCKET} :: CInt)
    #{poke struct cmsghdr, cmsg_type} control (#{const SCM_RIGHTS} :: CInt)
    pokeByteOff control #{const CMSG_LEN(0)} right
    n <- sendMsg socketFd (castPtr message) 0
    check (n == 1) "sendmsg"

sendTwoRights :: S.Socket -> Fd -> Fd -> IO ()
sendTwoRights socket (Fd right) (Fd other) = S.withFdSocket socket $ \socketFd ->
  allocaBytes 1 $ \byte -> allocaBytes #{size struct iovec} $ \iov ->
  allocaBytes #{size struct msghdr} $ \message -> allocaBytes #{const CMSG_SPACE(2*sizeof(int))} $ \control -> do
    fillBytes iov 0 #{size struct iovec}; fillBytes message 0 #{size struct msghdr}
    fillBytes control 0 #{const CMSG_SPACE(2*sizeof(int))}; poke byte (120 :: Word8)
    #{poke struct iovec, iov_base} iov (castPtr byte :: Ptr ())
    #{poke struct iovec, iov_len} iov (1 :: CSize)
    #{poke struct msghdr, msg_iov} message (castPtr iov :: Ptr ())
    #{poke struct msghdr, msg_iovlen} message (1 :: CSize)
    #{poke struct msghdr, msg_control} message (castPtr control :: Ptr ())
    #{poke struct msghdr, msg_controllen} message (fromIntegral (#{const CMSG_SPACE(2*sizeof(int))} :: Int) :: CSize)
    #{poke struct cmsghdr, cmsg_len} control (fromIntegral (#{const CMSG_LEN(2*sizeof(int))} :: Int) :: CSize)
    #{poke struct cmsghdr, cmsg_level} control (#{const SOL_SOCKET} :: CInt)
    #{poke struct cmsghdr, cmsg_type} control (#{const SCM_RIGHTS} :: CInt)
    pokeByteOff control #{const CMSG_LEN(0)} right
    pokeByteOff control (#{const CMSG_LEN(0)} + sizeOf right) other
    n <- sendMsg socketFd (castPtr message) 0
    check (n == 1) "sendmsg"

-- Constructed ancillary bytes: these cases exercise parser refusal only, not
-- an assertion that a conforming kernel delivers corrupted records.
syntheticControls :: IO ()
syntheticControls = do
  malformed <- scanForTest (B.singleton 1)
  check (case malformed of (Left InvalidControl,True,[]) -> True; _ -> False) "synthetic truncated header"
  allocaBytes #{const CMSG_SPACE(sizeof(struct ucred))} $ \raw -> do
    let cap = #{const CMSG_SPACE(sizeof(struct ucred))}
    fillBytes raw 0 cap
    #{poke struct cmsghdr, cmsg_len} raw (fromIntegral (#{const CMSG_LEN(sizeof(struct ucred))} :: Int) :: CSize)
    #{poke struct cmsghdr, cmsg_level} raw (#{const SOL_SOCKET} :: CInt)
    #{poke struct cmsghdr, cmsg_type} raw (12345 :: CInt)
    bytes <- B.packCStringLen (castPtr raw,cap)
    result <- scanForTest bytes
    check (case result of (Left UnexpectedControl,False,[]) -> True; _ -> False) "synthetic unknown control"
  allocaBytes (2 * #{const CMSG_SPACE(sizeof(struct ucred))}) $ \raw -> do
    let stride = #{const CMSG_SPACE(sizeof(struct ucred))}; cap = 2*stride
        writeOne offset pid = do
          let entry = raw `plusPtr` offset; value = entry `plusPtr` #{const CMSG_LEN(0)}
          #{poke struct cmsghdr, cmsg_len} entry (fromIntegral (#{const CMSG_LEN(sizeof(struct ucred))} :: Int) :: CSize)
          #{poke struct cmsghdr, cmsg_level} entry (#{const SOL_SOCKET} :: CInt)
          #{poke struct cmsghdr, cmsg_type} entry (#{const SCM_CREDENTIALS} :: CInt)
          #{poke struct ucred, pid} value (pid :: #{type pid_t})
          #{poke struct ucred, uid} value (1 :: #{type uid_t})
          #{poke struct ucred, gid} value (1 :: #{type gid_t})
    fillBytes raw 0 cap
    writeOne 0 12; writeOne stride 13
    bytes <- B.packCStringLen (castPtr raw,cap)
    result <- scanForTest bytes
    check (case result of (Left MultipleCredentials,False,[]) -> True; _ -> False) "synthetic contradictory credentials"

mixedExceptions :: SomeException -> SomeException -> SomeException -> IO ()
mixedExceptions original cleanup expected = withPair $ \(readerSock, writer) -> do
  seen <- newIORef ([] :: [CInt])
  reader <- newCredentialReaderWithHooksForTest
    (\fd -> modifyIORef' seen (fd:) >> closeOne fd >> throwIO cleanup)
    (\_ -> throwIO original) (pure ())
  enablePassCredentials readerSock
  bracket createPipe (\(a,b) -> closeFd a >> closeFd b) $ \(readEnd,_) -> sendRight writer readEnd
  result <- try (receiveCredentialChunk reader readerSock 1) :: IO (Either SomeException (Either CredentialError CredentialChunk))
  allErrors <- readerExceptions reader
  descriptors <- readIORef seen
  current <- credentialReaderStatus reader
  closed <- case descriptors of [fd] -> (== (-1)) <$> fcntlGet fd #{const F_GETFD}; _ -> pure False
  check (case result of Left e -> show e == show expected; _ -> False) "exception priority"
  check (map show allErrors == map show [original,cleanup]) "both diagnostic exceptions retained"
  check (closed && case current of ReaderQuarantined [Uncertain _] True -> True; _ -> False) "unknown and close custody"

main :: IO ()
main = do
  syntheticControls
  let syncA = toException (userError "original-sync") :: SomeException
      syncB = toException (userError "cleanup-sync") :: SomeException
      asyncA = toException ThreadKilled :: SomeException
      asyncB = toException UserInterrupt :: SomeException
      selected original cleanup = maybe "none" show (preferExceptionForTest original cleanup)
      asyncSelected original cleanup = case preferExceptionForTest original cleanup of
        Just e -> case fromException e :: Maybe SomeAsyncException of Just _ -> True; Nothing -> False
        Nothing -> False
  check (selected (Just asyncA) [syncB] == show asyncA) "original async wins cleanup sync"
  check (selected (Just syncA) [asyncA] == show asyncA) "cleanup async wins original sync"
  check (selected Nothing [syncA,asyncB] == show asyncB) "later cleanup async wins earlier sync"
  check (selected (Just asyncA) [asyncB] == show asyncA && asyncSelected (Just asyncA) [asyncB]) "original async wins cleanup async"
  mixedExceptions asyncA syncB asyncA
  mixedExceptions syncA asyncA asyncA
  mixedExceptions asyncA asyncB asyncA
  withPair $ \(readerSock, writer) -> do
    reader <- newCredentialReader
    enablePassCredentials readerSock
    pid <- getProcessID
    uid <- getRealUserID
    gid <- getRealGroupID
    invalid <- receiveCredentialChunk reader readerSock 0
    check (invalid == Left InvalidLimit) "finite chunk bound"
    N.sendAll writer "a"
    first <- receiveCredentialChunk reader readerSock 1
    check (case first of Right (CredentialChunk b c) -> b == "a" && fromIntegral (peerPid c) == pid && fromIntegral (peerUid c) == uid && fromIntegral (peerGid c) == gid; _ -> False) "default credential"
    N.sendAll writer "bc"
    second <- receiveCredentialChunk reader readerSock 1
    third <- receiveCredentialChunk reader readerSock 1
    check (case (second,third) of (Right (CredentialChunk b _),Right (CredentialChunk c _)) -> B.concat [b,c] == "bc"; _ -> False) "split receive"
    child <- forkProcess (N.sendAll writer "z" >> exitImmediately ExitSuccess)
    childChunk <- receiveCredentialChunk reader readerSock 1
    check (case childChunk of Right (CredentialChunk b c) -> b == "z" && fromIntegral (peerPid c) == child; _ -> False) "sender pid not creator pid"
    _ <- getProcessStatus True False child
    S.shutdown writer S.ShutdownSend
    eof <- receiveCredentialChunk reader readerSock 1
    check (eof == Right EndOfStream) "EOF"
  withPair $ \(readerSock, writer) -> do
    reader <- newCredentialReader
    N.sendAll writer "x"
    noCred <- receiveCredentialChunk reader readerSock 1
    check (noCred == Left MissingCredential) "passcred required"
  withPair $ \(readerSock, writer) -> do
    calls <- newIORef ([] :: [CInt])
    reader <- newCredentialReaderWithCloseForTest (\fd -> modifyIORef' calls (fd:) >> closeOne fd)
    enablePassCredentials readerSock
    bracket createPipe (\(a,b) -> closeFd a >> closeFd b) $ \(readEnd,_) -> sendRight writer readEnd
    got <- receiveCredentialChunk reader readerSock 1
    observed <- readIORef calls
    state <- credentialReaderStatus reader
    check (got == Left RightsRefused && length observed == 1 && state == ReaderReady) "rights refusal and delivered close"
  withPair $ \(readerSock, writer) -> do
    calls <- newIORef ([] :: [CInt])
    reader <- newCredentialReaderWithCloseForTest (\fd -> modifyIORef' calls (fd:) >> closeOne fd >> pure (-1))
    enablePassCredentials readerSock
    bracket createPipe (\(a,b) -> closeFd a >> closeFd b) $ \(readEnd,_) -> sendRight writer readEnd
    got <- receiveCredentialChunk reader readerSock 1
    again <- receiveCredentialChunk reader readerSock 1
    observed <- readIORef calls
    state <- credentialReaderStatus reader
    check (got == Left CloseUncertain && again == Left ReaderUnavailable && length observed == 1 && case state of ReaderQuarantined [Uncertain _] False -> True; _ -> False) "uncertain close retained and never retried"

  withPair $ \(readerSock, writer) -> do
    calls <- newIORef ([] :: [CInt])
    reader <- newCredentialReaderWithHooksForTest (\fd -> modifyIORef' calls (fd:) >> closeOne fd) (\_ -> throwIO (userError "scan injected")) (pure ())
    enablePassCredentials readerSock
    bracket createPipe (\(a,b) -> closeFd a >> closeFd b) $ \(readEnd,_) -> sendRight writer readEnd
    result <- try (receiveCredentialChunk reader readerSock 1) :: IO (Either SomeException (Either CredentialError CredentialChunk))
    seen <- readIORef calls
    current <- credentialReaderStatus reader
    evidence <- quarantineEvidence reader
    closed <- case seen of [fd] -> (== (-1)) <$> fcntlGet fd #{const F_GETFD}; _ -> pure False
    check (case result of Left _ -> True; _ -> False) "scan exception propagated"
    check (closed && case current of ReaderQuarantined [Closed _] True -> True; _ -> False) "known published FD closed and unknown retained"
    check (case evidence of Just (_,raw,_) -> not (B.null raw); _ -> False) "retained raw ancillary"
    again <- receiveCredentialChunk reader readerSock 1
    check (again == Left ReaderUnavailable) "quarantine cannot be reused"
  withPair $ \(readerSock, writer) -> do
    reader <- newCredentialReaderWithHooksForTest closeOne (const (pure ())) (throwIO ThreadKilled)
    enablePassCredentials readerSock
    N.sendAll writer "x"
    result <- try (receiveCredentialChunk reader readerSock 1) :: IO (Either SomeException (Either CredentialError CredentialChunk))
    current <- credentialReaderStatus reader
    let asyncThrown = case result of
          Left e -> case fromException e :: Maybe SomeAsyncException of Just _ -> True; Nothing -> False
          Right _ -> False
    check asyncThrown "post recv async propagated"
    check (case current of ReaderQuarantined [] True -> True; _ -> False) "post recv custody retained"

  withPair $ \(readerSock, writer) -> do
    calls <- newIORef ([] :: [CInt])
    reader <- newCredentialReaderWithCloseForTest $ \fd -> do
      previous <- readIORef calls
      modifyIORef' calls (fd:)
      result <- closeOne fd
      pure (if null previous then (-1) else result)
    enablePassCredentials readerSock
    bracket createPipe (\(a,b) -> closeFd a >> closeFd b) $ \(a,b) -> sendTwoRights writer a b
    got <- receiveCredentialChunk reader readerSock 1
    seen <- readIORef calls
    current <- credentialReaderStatus reader
    closed <- mapM (\fd -> (== (-1)) <$> fcntlGet fd #{const F_GETFD}) seen
    check (got == Left CloseUncertain && length seen == 2 && and closed) "independent close attempts and fd identity"
    check (case current of ReaderQuarantined [Uncertain _,Closed _] False -> True; _ -> False) "exact close outcomes retained"
