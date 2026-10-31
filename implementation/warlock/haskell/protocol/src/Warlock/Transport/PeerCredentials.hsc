{-# LANGUAGE CPP #-}
{-# LANGUAGE ForeignFunctionInterface #-}
module Warlock.Transport.PeerCredentials
  ( CredentialReader, ReaderStatus(..), DescriptorState(..), PeerCredential(..)
  , CredentialError(..), CredentialChunk(..), newCredentialReader
  , credentialReaderStatus, quarantineEvidence, readerExceptions, enablePassCredentials, receiveCredentialChunk
#ifdef WARLOCK_CREDENTIAL_TESTING
  , newCredentialReaderWithCloseForTest, newCredentialReaderWithHooksForTest, preferExceptionForTest, scanForTest
#endif
  ) where
#define _GNU_SOURCE 1
#include <sys/types.h>
#include <sys/socket.h>
#include <sys/uio.h>
#include <unistd.h>
import Control.Concurrent.MVar (MVar, newMVar, withMVar)
import Control.Exception (SomeException, SomeAsyncException, fromException, mask, onException, throwIO, try)
import qualified Data.ByteString as B
import Data.IORef (IORef, newIORef, readIORef, writeIORef)
import Foreign
import Foreign.C
import GHC.Conc (threadWaitRead)
import qualified Network.Socket as Socket

foreign import ccall unsafe "setsockopt" setSockOpt :: CInt -> CInt -> CInt -> Ptr CInt -> #{type socklen_t} -> IO CInt
foreign import ccall unsafe "recvmsg" recvMsg :: CInt -> Ptr () -> CInt -> IO (#{type ssize_t})
foreign import ccall unsafe "close" closeFdOnce :: CInt -> IO CInt

data PeerCredential = PeerCredential { peerPid :: !(#{type pid_t}), peerUid :: !(#{type uid_t}), peerGid :: !(#{type gid_t}) } deriving (Eq,Show)
data CredentialError = InvalidLimit | ControlTruncated | UnexpectedControl | MissingCredential | MultipleCredentials | InvalidControl | RightsRefused | CloseUncertain | ReaderUnavailable deriving (Eq,Show)
data CredentialChunk = EndOfStream | CredentialChunk !B.ByteString !PeerCredential deriving (Eq,Show)
data DescriptorState = Pending !CInt | Attempting !CInt | Closed !CInt | Uncertain !CInt deriving (Eq,Show)
data ReaderStatus = ReaderReady | ReaderReceiving | ReaderQuarantined ![DescriptorState] !Bool deriving (Eq,Show)
data CredentialReader = CredentialReader
  { lock :: !(MVar ()), state :: !(IORef ReaderStatus), errors :: !(IORef [SomeException])
  , payloadMemory :: !(ForeignPtr Word8), controlMemory :: !(ForeignPtr Word8)
  , messageMemory :: !(ForeignPtr Word8), iovecMemory :: !(ForeignPtr Word8)
  , ledgerMemory :: !(ForeignPtr CInt), closeOne :: !(CInt -> IO CInt), scanStep :: !(Int -> IO ()), afterRecv :: !(IO ()) }
controlCapacity, maxChunk, ledgerCapacity :: Int
controlCapacity = 4096
maxChunk = 65536
ledgerCapacity = controlCapacity `div` sizeOf (undefined :: CInt)

newCredentialReader :: IO CredentialReader
newCredentialReader = makeReader closeFdOnce (const (pure ())) (pure ())
makeReader :: (CInt -> IO CInt) -> (Int -> IO ()) -> IO () -> IO CredentialReader
makeReader closer hook after = do
  gate <- newMVar (); st <- newIORef ReaderReady; es <- newIORef []
  payload <- mallocForeignPtrBytes maxChunk; control <- mallocForeignPtrBytes controlCapacity
  msg <- mallocForeignPtrBytes #{size struct msghdr}; iov <- mallocForeignPtrBytes #{size struct iovec}
  ledger <- mallocForeignPtrArray (2 * ledgerCapacity)
  withForeignPtr control $ \p -> fillBytes p 0 controlCapacity
  withForeignPtr msg $ \p -> fillBytes p 0 #{size struct msghdr}
  withForeignPtr iov $ \p -> fillBytes p 0 #{size struct iovec}
  withForeignPtr ledger $ \p -> fillBytes p 0 (2 * ledgerCapacity * sizeOf (undefined :: CInt))
  pure (CredentialReader gate st es payload control msg iov ledger closer hook after)
#ifdef WARLOCK_CREDENTIAL_TESTING
newCredentialReaderWithCloseForTest :: (CInt -> IO CInt) -> IO CredentialReader
newCredentialReaderWithCloseForTest closer = makeReader closer (const (pure ())) (pure ())
newCredentialReaderWithHooksForTest :: (CInt -> IO CInt) -> (Int -> IO ()) -> IO () -> IO CredentialReader
newCredentialReaderWithHooksForTest = makeReader
preferExceptionForTest :: Maybe SomeException -> [SomeException] -> Maybe SomeException
preferExceptionForTest = preferred
#endif
credentialReaderStatus :: CredentialReader -> IO ReaderStatus
credentialReaderStatus = readIORef . state
readerExceptions :: CredentialReader -> IO [SomeException]
readerExceptions = readIORef . errors
quarantineEvidence :: CredentialReader -> IO (Maybe (ReaderStatus, B.ByteString, CInt))
quarantineEvidence r = withMVar (lock r) $ \_ -> do
  current <- readIORef (state r)
  case current of
    ReaderQuarantined _ _ -> withForeignPtr (controlMemory r) $ \control -> withForeignPtr (messageMemory r) $ \msg -> do
      used <- #{peek struct msghdr, msg_controllen} msg :: IO CSize
      flags <- #{peek struct msghdr, msg_flags} msg :: IO CInt
      bytes <- B.packCStringLen (castPtr control, fromIntegral (min used (fromIntegral controlCapacity)))
      pure (Just (current,bytes,flags))
    _ -> pure Nothing

enablePassCredentials :: Socket.Socket -> IO ()
enablePassCredentials socket = Socket.withFdSocket socket $ \fd -> alloca $ \value -> do
  poke value (1 :: CInt)
  _ <- throwErrnoIfMinus1 "setsockopt(SO_PASSCRED)" (setSockOpt fd #{const SOL_SOCKET} #{const SO_PASSCRED} value (fromIntegral (sizeOf (undefined :: CInt))))
  pure ()

-- Each pair is (fd, state): zero empty, 1 pending, 2 attempting, 3 closed,
-- 4 uncertain. Storage exists before recvmsg and is retained by the reader.
ledgerStates :: Ptr CInt -> IO [DescriptorState]
ledgerStates ptr = go 0 where
  go i | i == ledgerCapacity = pure []
       | otherwise = do
          kind <- peekElemOff ptr (2*i+1)
          if kind == 0 then pure [] else do
            fd <- peekElemOff ptr (2*i)
            rest <- go (i+1)
            pure $ case kind of 1 -> Pending fd:rest; 2 -> Attempting fd:rest; 3 -> Closed fd:rest; _ -> Uncertain fd:rest

-- Prefer the original async exception, then the first cleanup async exception,
-- then the original synchronous exception, then the first cleanup exception.
preferred :: Maybe SomeException -> [SomeException] -> Maybe SomeException
preferred original cleanup = case original of
  Just e | isAsync e -> Just e
  _ -> case filter isAsync cleanup of
    e:_ -> Just e
    [] -> case original of Just e -> Just e; Nothing -> case cleanup of e:_ -> Just e; [] -> Nothing
  where isAsync e = case fromException e :: Maybe SomeAsyncException of Just _ -> True; Nothing -> False

-- One close per pending descriptor, state is published before the syscall.
-- All independent pending descriptors are attempted even on injected failures.
retireLedger :: CredentialReader -> Ptr CInt -> IO [SomeException]
retireLedger r ptr = go 0 [] where
  go i failures | i == ledgerCapacity = pure (reverse failures)
  go i failures = do
    kind <- peekElemOff ptr (2*i+1)
    if kind /= 1 then go (i+1) failures else do
      fd <- peekElemOff ptr (2*i)
      pokeElemOff ptr (2*i+1) 2
      result <- try (closeOne r fd) :: IO (Either SomeException CInt)
      pokeElemOff ptr (2*i+1) (case result of Right 0 -> 3; _ -> 4)
      case result of Left e -> go (i+1) (e:failures); Right _ -> go (i+1) failures

receiveCredentialChunk :: CredentialReader -> Socket.Socket -> Int -> IO (Either CredentialError CredentialChunk)
receiveCredentialChunk r socket requested
  | requested <= 0 || requested > maxChunk = pure (Left InvalidLimit)
  | otherwise = withMVar (lock r) $ \_ -> Socket.withFdSocket socket loop
  where
    loop fd = mask $ \restore -> do
      current <- readIORef (state r)
      if current /= ReaderReady then pure (Left ReaderUnavailable) else do
        writeIORef (state r) ReaderReceiving
        attempt <- (withForeignPtr (payloadMemory r) $ \payload -> withForeignPtr (controlMemory r) $ \control ->
          withForeignPtr (messageMemory r) $ \msg -> withForeignPtr (iovecMemory r) $ \iov -> withForeignPtr (ledgerMemory r) $ \ledger -> do
            fillBytes ledger 0 (2 * ledgerCapacity * sizeOf (undefined :: CInt))
            fillBytes msg 0 #{size struct msghdr}; fillBytes iov 0 #{size struct iovec}; fillBytes control 0 controlCapacity
            #{poke struct iovec, iov_base} iov (castPtr payload :: Ptr ())
            #{poke struct iovec, iov_len} iov (fromIntegral requested :: CSize)
            #{poke struct msghdr, msg_iov} msg (castPtr iov :: Ptr ())
            #{poke struct msghdr, msg_iovlen} msg (1 :: CSize)
            #{poke struct msghdr, msg_control} msg (castPtr control :: Ptr ())
            #{poke struct msghdr, msg_controllen} msg (fromIntegral controlCapacity :: CSize)
            n <- recvMsg fd (castPtr msg) (#{const MSG_CMSG_CLOEXEC} .|. #{const MSG_DONTWAIT})
            if n < 0 then do
              e <- getErrno
              if e == eAGAIN || e == eWOULDBLOCK then writeIORef (state r) ReaderReady >> pure Nothing else throwErrno "recvmsg"
            else do
              writeIORef (state r) (ReaderQuarantined [] True)
              afterRecv r
              used <- #{peek struct msghdr, msg_controllen} msg :: IO CSize
              flags <- #{peek struct msghdr, msg_flags} msg :: IO CInt
              let actual = fromIntegral (min used (fromIntegral controlCapacity))
                  trunc = used > fromIntegral controlCapacity || flags .&. (#{const MSG_CTRUNC} .|. #{const MSG_TRUNC}) /= 0
              scanned <- try (scanControls control actual ledger (scanStep r)) :: IO (Either SomeException (Either CredentialError PeerCredential,Bool))
              failures <- retireLedger r ledger
              slots <- ledgerStates ledger
              let unknown = case scanned of Left _ -> True; Right (_,bad) -> bad
                  original = either Just (const Nothing) scanned
                  exceptions = maybe [] (:[]) original ++ failures
                  uncertain = any notClosed slots
              writeIORef (errors r) exceptions
              if unknown || uncertain then writeIORef (state r) (ReaderQuarantined slots unknown) else writeIORef (state r) ReaderReady
              case preferred original failures of
                Just exception -> throwIO exception
                Nothing
                  | unknown -> pure (Just (Left InvalidControl))
                  | uncertain -> pure (Just (Left CloseUncertain))
                  | trunc -> pure (Just (Left ControlTruncated))
                  | not (null slots) -> pure (Just (Left RightsRefused))
                  | otherwise -> case scanned of
                      Left _ -> pure (Just (Left InvalidControl))
                      Right (parsed, _) ->
                        if n == 0
                          then pure (Just (eofResult parsed))
                          else case parsed of
                            Left failure -> pure (Just (Left failure))
                            Right credential -> do
                              bytes <- B.packCStringLen (castPtr payload, fromIntegral n)
                              pure (Just (Right (CredentialChunk bytes credential))))
          `onException` (do withForeignPtr (ledgerMemory r) $ \ledger -> do slots <- ledgerStates ledger; writeIORef (state r) (ReaderQuarantined slots True))
        case attempt of Nothing -> restore (threadWaitRead (fromIntegral fd)) >> loop fd; Just value -> pure value
    eofResult parsed = case parsed of
      Left MissingCredential -> Right EndOfStream
      Left failure -> Left failure
      Right _ -> Right EndOfStream
    notClosed (Closed _) = False
    notClosed _ = True

#ifdef WARLOCK_CREDENTIAL_TESTING
-- Synthetic bytes only; this does not represent a kernel delivery and never
-- closes the fake numbers in the returned ledger.
scanForTest :: B.ByteString -> IO (Either CredentialError PeerCredential,Bool,[DescriptorState])
scanForTest bytes = B.useAsCStringLen bytes $ \(base,n) -> allocaArray (2*ledgerCapacity) $ \ledger -> do
  fillBytes ledger 0 (2*ledgerCapacity*sizeOf (undefined :: CInt))
  (result,unknown) <- scanControls (castPtr base) n ledger (const (pure ()))
  entries <- ledgerStates ledger
  pure (result,unknown,entries)
#endif

-- Valid kernel records are walked in order. Publish each fd into the preowned
-- ledger before reading the next. Invalid grammar retains raw bytes as UNKNOWN;
-- no attempt is made to guess the next record boundary.
scanControls :: Ptr Word8 -> Int -> Ptr CInt -> (Int -> IO ()) -> IO (Either CredentialError PeerCredential,Bool)
scanControls base total ledger hook = go 0 0 Nothing Nothing where
  header = #{const CMSG_LEN(0)} :: Int
  cmsgAlignment = #{size size_t} :: Int
  align n = ((n + cmsgAlignment - 1) `div` cmsgAlignment) * cmsgAlignment
  go pos slot credential failure
    | pos == total = pure (maybe (maybe (Left MissingCredential) Right credential) Left failure,False)
    | pos > total || total-pos < #{size struct cmsghdr} = pure (Left InvalidControl,True)
    | otherwise = do
      let item = base `plusPtr` pos
      rawLen <- #{peek struct cmsghdr, cmsg_len} item :: IO CSize
      level <- #{peek struct cmsghdr, cmsg_level} item :: IO CInt
      kind <- #{peek struct cmsghdr, cmsg_type} item :: IO CInt
      if rawLen > fromIntegral (total-pos) || rawLen < fromIntegral header then pure (Left InvalidControl,True) else do
        let len = fromIntegral rawLen; payload = item `plusPtr` header; count = len-header; next = min total (pos + align len)
        if level == #{const SOL_SOCKET} && kind == #{const SCM_RIGHTS} then do
          let width = sizeOf (undefined :: CInt); amount = count `div` width
          if count `mod` width /= 0 || amount > ledgerCapacity-slot then pure (Left InvalidControl,True) else do
            let publish j | j == amount = pure ()
                          | otherwise = do
                              fd <- peekElemOff (castPtr payload :: Ptr CInt) j
                              pokeElemOff ledger (2*(slot+j)) fd
                              pokeElemOff ledger (2*(slot+j)+1) 1
                              hook (slot+j)
                              publish (j+1)
            publish 0
            go next (slot+amount) credential (Just RightsRefused)
        else if level == #{const SOL_SOCKET} && kind == #{const SCM_CREDENTIALS} then
          if count /= #{size struct ucred} then pure (Left InvalidControl,True) else do
            pid <- #{peek struct ucred, pid} payload; uid <- #{peek struct ucred, uid} payload; gid <- #{peek struct ucred, gid} payload
            go next slot (Just (PeerCredential pid uid gid)) (if maybe False (const True) credential then Just MultipleCredentials else failure)
        else go next slot credential (Just UnexpectedControl)
