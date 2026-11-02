{-# LANGUAGE ForeignFunctionInterface #-}
{-# LANGUAGE ScopedTypeVariables #-}
-- Native-selected fixed-root IO. No bridge value is a path or descriptor.
module Warlock.Backend.Store
 (DirectoryPin(..),StoreOwner,newStoreOwner,runOwned,retireStoreOwner,retireStoreOwnerIfSettled,
  withPinnedDirectory,withChildDirectory,listNames,entryDirectory,directoryStamp,readRegular,withPinLock,
  replacePins,readStartupFile) where
#define _GNU_SOURCE 1
#include <sys/types.h>
#include <sys/stat.h>
#include <sys/file.h>
#include <fcntl.h>
#include <unistd.h>
#include <stdio.h>
import Control.Concurrent.MVar
import Control.Exception (IOException,SomeException,SomeAsyncException,fromException,mask,mask_,onException,throwIO,try)
import Control.Monad (unless,when)
import Data.Bits ((.|.),(.&.))
import qualified Data.ByteString as B
import qualified Data.ByteString.Char8 as C
import Data.IORef
import Data.Int (Int64)
import Data.Word (Word32,Word64)
import Foreign.C.Error (getErrno,errnoToIOError,throwErrnoIfMinus1,throwErrnoIfMinus1_)
import Foreign.C.String (CString)
import Foreign.C.Types (CInt(..),CSize(..))
import Foreign.Marshal.Alloc (allocaBytes)
import Foreign.Ptr (Ptr,castPtr,plusPtr)
import GHC.Clock (getMonotonicTimeNSec)
import qualified System.Posix.Directory.ByteString as Dir
import qualified System.Posix.Files.ByteString as Files
import System.Posix.Files (FileStatus,getFdStatus,isDirectory,isRegularFile,isSymbolicLink,fileOwner,fileMode,linkCount,fileSize,deviceID,fileID,modificationTimeHiRes,statusChangeTimeHiRes)
import System.Posix.Process (getProcessID)
import System.Posix.Types (Fd(..))
import System.Posix.User (getEffectiveUserID)
import System.IO.Error (isDoesNotExistError)
import qualified Data.Text as T
import qualified Data.Text.Encoding as TE

foreign import ccall safe "open" c_open :: CString -> CInt -> IO CInt
foreign import ccall safe "openat" c_openat :: CInt -> CString -> CInt -> #{type mode_t} -> IO CInt
foreign import ccall safe "close" c_close :: CInt -> IO CInt
foreign import ccall safe "pread" c_pread :: CInt -> Ptr () -> CSize -> #{type off_t} -> IO #{type ssize_t}
foreign import ccall safe "write" c_write :: CInt -> Ptr () -> CSize -> IO #{type ssize_t}
foreign import ccall safe "fsync" c_fsync :: CInt -> IO CInt
foreign import ccall safe "flock" c_flock :: CInt -> CInt -> IO CInt
foreign import ccall safe "renameat" c_renameat :: CInt -> CString -> CInt -> CString -> IO CInt
foreign import ccall safe "unlinkat" c_unlinkat :: CInt -> CString -> CInt -> IO CInt

data DirectoryPin = DirectoryPin {directoryPath :: FilePath,directoryDevice :: Integer,directoryInode :: Integer} deriving (Eq,Show)
data CloseState = Acquiring | Open | Closing | Closed | Uncertain deriving Eq
-- Only an explicit negative acquisition receipt may mean no resource exists.
-- An exception from generic acquisition is never such a receipt.
data Acquisition a = Acquired a | NotAcquired IOException
data Resource = Resource (IORef CloseState) (IO ())
data StoreOwner = StoreOwner (MVar Bool) (IORef [Resource])

newStoreOwner :: IO StoreOwner
newStoreOwner = StoreOwner <$> newMVar False <*> newIORef []
require :: Bool -> String -> IO ()
require good reason = unless good (ioError (userError reason))

-- Only one owner operation may use these retained resources. Retirement never
-- guesses whether an in-flight close succeeded or retries an uncertain close.
runOwned :: StoreOwner -> IO a -> IO a
runOwned (StoreOwner gate resources) action = mask $ \restore -> do
 selected <- tryTakeMVar gate
 case selected of
  Nothing -> ioError (userError "backend store busy")
  Just retired | retired -> putMVar gate True >> ioError (userError "backend store retired")
  Just _ -> do
   result <- try (restore action)
   retained <- readIORef resources
   states <- mapM (\(Resource cell _) -> readIORef cell) retained
   -- One uncertain operation poisons this owner; repeated requests cannot
   -- accumulate additional uncertain descriptors or replay storage work.
   putMVar gate (any (/=Closed) states)
   case result of Left (problem :: SomeException) -> throwIO problem; Right answer -> pure answer

closeResource :: Resource -> IO ()
closeResource (Resource cell closeAction) = mask_ $ do
 state <- readIORef cell
 case state of
  Open -> do
   writeIORef cell Closing
   result <- try closeAction
   writeIORef cell (case result of Right () -> Closed; Left (_ :: SomeException) -> Uncertain)
   either throwIO pure result
  Closed -> pure ()
  _ -> ioError (userError "backend close uncertain")

retireStoreOwner :: StoreOwner -> IO Bool
retireStoreOwner (StoreOwner gate resources) = mask_ $ do
 selected <- tryTakeMVar gate
 case selected of
  Nothing -> pure False
  Just _ -> do
   rows <- readIORef resources
   _ <- mapM (\entry -> try (closeResource entry) :: IO (Either SomeException ())) rows
   settled <- mapM (\(Resource cell _) -> (==Closed) <$> readIORef cell) rows
   putMVar gate True
   pure (and settled)

-- No physical close is started here. Seal the SAME operation gate and return
-- True only if every retained acquisition/close record is affirmatively Closed.
-- Acquiring/Open/Closing/Uncertain and Busy are unconfirmed, never cleanup proof.
-- Original StopD and aggregate result publication belong to the Backend caller.
retireStoreOwnerIfSettled :: StoreOwner -> IO Bool
retireStoreOwnerIfSettled (StoreOwner gate resources) = mask_ $ do
 selected <- tryTakeMVar gate
 case selected of
  Nothing -> pure False
  Just _ -> do
   settled <- (do
     rows <- readIORef resources
     and <$> mapM (\(Resource cell _) -> (==Closed) <$> readIORef cell) rows)
      `onException` putMVar gate True
   -- Unsettled or failed observation must not allow a later runOwned/replay.
   -- Resource records and their once-only close rights remain untouched.
   putMVar gate True
   pure settled

tracked :: StoreOwner -> IO (Acquisition a) -> (a -> IO ()) -> (a -> IO b) -> IO b
tracked (StoreOwner _ resources) acquire release action = mask $ \restore -> do
 -- Allocate and publish the unconfirmed record BEFORE acquisition. Allocation
 -- or publication failure here precedes any resource acquisition by this call.
 cell <- newIORef Acquiring
 valueCell <- newIORef Nothing
 let closeRetained = do
      selected <- readIORef valueCell
      case selected of
       Nothing -> ioError (userError "backend acquisition unconfirmed")
       Just value -> release value
     resource=Resource cell closeRetained
 previous <- readIORef resources
 live <- filterMResource previous
 writeIORef resources (resource:live)
 acquired <- acquire
 value <- case acquired of
  -- Only a source-proven no-resource result makes this record Closed.
  NotAcquired problem -> writeIORef cell Closed >> ioError problem
  Acquired selected -> do
   -- Any interruption/failure before both writes leaves Acquiring, not Closed.
   -- Publish the actual retained value before making its close right usable.
   writeIORef valueCell (Just selected)
   writeIORef cell Open
   pure selected
 result <- try (restore (action value))
 cleanup <- try (closeResource resource)
 case result of
  Left (problem :: SomeException) -> case fromException problem :: Maybe SomeAsyncException of
   Just _ -> throwIO problem
   Nothing -> case cleanup of Left (other :: SomeException) -> throwIO other; Right () -> throwIO problem
  Right answer -> case cleanup of Left (problem :: SomeException) -> throwIO problem; Right () -> pure answer
 where
  filterMResource [] = pure []
  filterMResource (entry@(Resource cell _):rest) = do
   state <- readIORef cell
   remaining <- filterMResource rest
   pure (if state==Closed then remaining else entry:remaining)

number :: Fd -> CInt
number (Fd fd) = fd
closeFdOnce :: Fd -> IO ()
closeFdOnce fd = throwErrnoIfMinus1_ "backend close" (c_close (number fd))
directoryFlags :: CInt
directoryFlags = #{const O_RDONLY} .|. #{const O_DIRECTORY} .|. #{const O_NOFOLLOW} .|. #{const O_CLOEXEC}
fileFlags :: CInt
fileFlags = #{const O_RDONLY} .|. #{const O_NONBLOCK} .|. #{const O_NOFOLLOW} .|. #{const O_CLOEXEC}
nameValid :: B.ByteString -> Bool
nameValid name = not (B.null name) && B.length name<=255 && name/=C.pack "." && name/=C.pack ".." && not (B.any (\byte -> byte==0 || byte==47) name)
-- Cache errno at the actual negative syscall receipt. Exceptions before a
-- receipt reaches tracked remain Acquiring/Unknown; never guess from a name.
acquireFd :: String -> IO CInt -> IO (Acquisition Fd)
acquireFd label syscall = do
 raw <- syscall
 if raw == -1 then do
  problem <- getErrno
  pure (NotAcquired (errnoToIOError label problem Nothing Nothing))
 else if raw >= 0 then pure (Acquired (Fd raw))
 else ioError (userError "unsupported backend descriptor result")

openAt :: Fd -> B.ByteString -> CInt -> #{type mode_t} -> IO (Acquisition Fd)
openAt parent name flags mode =
 if not (nameValid name) then pure (NotAcquired (userError "invalid native-selected filename"))
 else B.useAsCString name $ \text -> acquireFd "backend openat" (c_openat (number parent) text flags mode)

withPinnedDirectory :: StoreOwner -> Bool -> DirectoryPin -> (Fd -> IO a) -> IO a
withPinnedDirectory owner private pin action = do
 let raw=TE.encodeUtf8 (T.pack (directoryPath pin))
     parts=filter (not . B.null) (B.split 47 raw)
 require (not (B.null raw) && B.head raw==47 && length parts<=64 && all nameValid parts && directoryDevice pin>=0 && directoryInode pin>0) "invalid trusted root pin"
 tracked owner (B.useAsCString (C.pack "/") (\name -> acquireFd "backend root" (c_open name directoryFlags))) closeFdOnce $ \root ->
  walk root parts
 where
  walk fd [] = do
   status <- getFdStatus fd
   require (isDirectory status && toInteger (deviceID status)==directoryDevice pin && toInteger (fileID status)==directoryInode pin) "backend root identity changed"
   when private (privateDirectory status)
   action fd
  walk fd (part:rest) = tracked owner (openAt fd part directoryFlags 0) closeFdOnce (\next -> walk next rest)

privateDirectory :: FileStatus -> IO ()
privateDirectory status = do
 uid <- getEffectiveUserID
 require (isDirectory status && fileOwner status==uid && fileMode status .&. 0o7777==0o700) "backend directory must be owned0700"
privateFile :: FileStatus -> IO ()
privateFile status = do
 uid <- getEffectiveUserID
 require (isRegularFile status && fileOwner status==uid && fileMode status .&. 0o7777==0o600 && linkCount status==1) "backend file must be owned0600 single-link regular"

withChildDirectory :: StoreOwner -> Fd -> B.ByteString -> (Fd -> IO a) -> IO a
withChildDirectory owner parent name = tracked owner (openAt parent name directoryFlags 0) closeFdOnce

listNames :: StoreOwner -> Fd -> IO [B.ByteString]
listNames owner fd = tracked owner (Acquired <$> Dir.openDirStream (C.pack ("/proc/self/fd/"++show (number fd)))) Dir.closeDirStream $ \stream ->
 let collect count acc = do
      name <- Dir.readDirStream stream
      if B.null name then pure (reverse acc) else if name==C.pack "." || name==C.pack ".." then collect count acc else do
       require (count<8192 && nameValid name) "catalog directory bound"
       collect (count+1) (name:acc)
 in collect (0 :: Int) []

fingerprint :: FileStatus -> (Integer,Integer,Integer,Integer,Integer)
fingerprint status = (toInteger (deviceID status),toInteger (fileID status),toInteger (fileSize status),floor (modificationTimeHiRes status*1000000000),floor (statusChangeTimeHiRes status*1000000000))

directoryStamp :: Fd -> IO (Integer,Integer,Integer,Integer,Integer)
directoryStamp fd = fingerprint <$> getFdStatus fd

entryDirectory :: Fd -> B.ByteString -> IO Bool
entryDirectory fd name = do
 require (nameValid name) "invalid catalog name"
 status <- Files.getSymbolicLinkStatus (C.pack ("/proc/self/fd/"++show (number fd)++"/")<>name)
 require (not (isSymbolicLink status)) "catalog symlink refused"
 pure (isDirectory status)

readRegular :: StoreOwner -> Bool -> Fd -> B.ByteString -> Int -> IO (Maybe B.ByteString)
readRegular owner private parent name limit = do
 result <- try $ tracked owner (openAt parent name fileFlags 0) closeFdOnce $ \fd -> do
  before <- getFdStatus fd
  require (isRegularFile before && fileSize before>=0 && toInteger (fileSize before)<=toInteger limit) "backend file bound/type"
  when private (privateFile before)
  bytes <- readFd fd limit
  after <- getFdStatus fd
  require (fingerprint before==fingerprint after && toInteger (B.length bytes)==toInteger (fileSize after)) "backend file changed during read"
  pure bytes
 case result of
  Left err | isDoesNotExistError err -> pure Nothing
  Left err -> ioError err
  Right bytes -> pure (Just bytes)

readFd :: Fd -> Int -> IO B.ByteString
readFd fd limit = allocaBytes (limit+1) $ \memory ->
 let loop offset = do
      amount <- throwErrnoIfMinus1 "backend pread" (c_pread (number fd) (castPtr (memory `plusPtr` offset)) (fromIntegral (limit+1-offset)) (fromIntegral offset))
      if amount==0 then B.packCStringLen (castPtr memory,offset) else do
       let used=fromIntegral amount
       require (used>0 && used<=limit+1-offset && offset+used<=limit) "backend file too large"
       loop (offset+used)
 in loop 0

withPinLock :: StoreOwner -> Fd -> IO a -> IO a
withPinLock owner parent action = tracked owner (openAt parent (C.pack "taskbar.lock") (#{const O_RDWR} .|. #{const O_CREAT} .|. #{const O_NONBLOCK} .|. #{const O_NOFOLLOW} .|. #{const O_CLOEXEC}) 0o600) closeFdOnce $ \fd -> do
 privateFile =<< getFdStatus fd
 throwErrnoIfMinus1_ "backend pin lock" (c_flock (number fd) (#{const LOCK_EX} .|. #{const LOCK_NB}))
 action -- Closing this independently owned descriptor releases only this lock.

-- The marker is set BEFORE the rename syscall. Any failure after that point
-- is conservatively unconfirmed, including uncertain close/readback failure.
replacePins :: StoreOwner -> Fd -> IORef Bool -> B.ByteString -> IO ()
replacePins owner directory published bytes = do
 require (not (B.null bytes) && B.length bytes<=16384) "pin storage bound"
 pid <- getProcessID
 clock <- getMonotonicTimeNSec
 let temporary=C.pack (".taskbar-"++show pid++"-"++show (clock :: Word64)++".tmp")
 renamed <- newIORef False
 let release fd = mask_ $ do
      cleaned <- try $ do
       moved <- readIORef renamed
       unless moved $ do
        selected <- getFdStatus fd
        existing <- readRegular owner True directory temporary 16384
        case existing of
         Nothing -> pure ()
         Just _ -> tracked owner (openAt directory temporary fileFlags 0) closeFdOnce $ \namedFd -> do
          namedStatus <- getFdStatus namedFd
          require (deviceID namedStatus==deviceID selected && fileID namedStatus==fileID selected) "pin temporary identity changed"
          B.useAsCString temporary $ \name -> throwErrnoIfMinus1_ "backend unlink own temporary" (c_unlinkat (number directory) name 0)
      closed <- try (closeFdOnce fd)
      case cleaned of
       Left (problem :: SomeException) -> throwIO problem
       Right () -> either (throwIO :: SomeException -> IO ()) pure closed
 tracked owner (openAt directory temporary (#{const O_RDWR} .|. #{const O_CREAT} .|. #{const O_EXCL} .|. #{const O_NOFOLLOW} .|. #{const O_CLOEXEC}) 0o600) release $ \fd -> do
  selected <- getFdStatus fd
  privateFile selected
  B.useAsCStringLen bytes $ \(pointer,size) -> writeAll fd (castPtr pointer) size
  throwErrnoIfMinus1_ "backend fsync pin file" (c_fsync (number fd))
  actual <- readFd fd 16384
  require (actual==bytes) "pin staged readback differs"
  -- The fixed target is checked while the sole cooperating writer lock is held.
  _ <- readRegular owner True directory (C.pack "taskbar.json") 16384
  writeIORef published True
  B.useAsCString temporary $ \from -> B.useAsCString (C.pack "taskbar.json") $ \to ->
   throwErrnoIfMinus1_ "backend atomic pin rename" (c_renameat (number directory) from (number directory) to)
  writeIORef renamed True
  throwErrnoIfMinus1_ "backend fsync pin directory" (c_fsync (number directory))
  committed <- readRegular owner True directory (C.pack "taskbar.json") 16384
  require (committed==Just bytes) "pin active readback differs"
 where
  writeAll _ _ 0 = pure ()
  writeAll fd pointer remaining = do
   amount <- throwErrnoIfMinus1 "backend pin write" (c_write (number fd) pointer (fromIntegral remaining))
   require (amount>0 && toInteger amount<=toInteger remaining) "backend pin write progress"
   let used=fromIntegral amount
   writeAll fd (pointer `plusPtr` used) (remaining-used)

readStartupFile :: StoreOwner -> FilePath -> IO B.ByteString
readStartupFile owner path = runOwned owner $ do
 let raw=TE.encodeUtf8 (T.pack path)
     parts=filter (not . B.null) (B.split 47 raw)
 require (not (B.null raw) && B.head raw==47 && not (null parts) && all nameValid parts && length parts<=64) "invalid trusted startup path"
 tracked owner (B.useAsCString (C.pack "/") (\name -> acquireFd "backend startup root" (c_open name directoryFlags))) closeFdOnce $ \root ->
  walk root parts
 where
  walk _ [] = ioError (userError "startup file missing")
  walk fd [name] = readRegular owner True fd name 131072 >>= maybe (ioError (userError "startup file missing")) pure
  walk fd (name:rest) = withChildDirectory owner fd name (\child -> walk child rest)
