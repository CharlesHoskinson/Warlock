{-# LANGUAGE ForeignFunctionInterface #-}
-- Private storage primitive only. A completed write is NOT an ACK receipt.
-- Directory is an exclusive caller-supplied held descriptor whose ancestry and
-- private ownership must already be established by the trusted runtime.
module Warlock.Native.Cancellation.Storage
 (Storage, Stage(..), HandleStatus(..), StorageStatus(..), newStorage, newStorageWithHookForTest, offerDirectory,
  persistBytes, storageStatus, withStorageLease, retireStorage) where
#define _GNU_SOURCE 1
#include <sys/types.h>
#include <sys/stat.h>
#include <fcntl.h>
#include <unistd.h>
#include <stdio.h>
import Control.Concurrent.MVar
import Control.Exception (SomeAsyncException,SomeException,finally,fromException,mask,throwIO,try)
import Data.Bits ((.|.),(.&.))
import Data.Int (Int64)
import Data.Word (Word32)
import Data.IORef (IORef,atomicModifyIORef',newIORef,readIORef)
import qualified Data.ByteString as B
import Foreign.C.Error (throwErrnoIfMinus1, throwErrnoIfMinus1_)
import Foreign.C.String (CString,withCString)
import Foreign.C.Types (CInt(..),CSize(..),CUInt(..))
import Foreign.Ptr (Ptr,castPtr,plusPtr)
import Foreign.Marshal.Alloc (allocaBytes)
import System.Posix.Files (FileStatus,getFdStatus,isDirectory,isRegularFile,fileOwner,fileMode,fileSize,deviceID,fileID,linkCount)
import System.Posix.Types (Fd(..))
import System.Posix.User (getEffectiveUserID)

foreign import ccall safe "openat" c_openat :: CInt -> CString -> CInt -> #{type mode_t} -> IO CInt
foreign import ccall safe "write" c_write :: CInt -> Ptr () -> CSize -> IO #{type ssize_t}
foreign import ccall safe "pread" c_pread :: CInt -> Ptr () -> CSize -> #{type off_t} -> IO #{type ssize_t}
foreign import ccall safe "fsync" c_fsync :: CInt -> IO CInt
foreign import ccall safe "renameat2" c_renameat2 :: CInt -> CString -> CInt -> CString -> CUInt -> IO CInt
foreign import ccall safe "close" c_close :: CInt -> IO CInt

data Stage = Empty | Offered | Creating | Writing | ReadingBack | SyncingFile | FileSynced | Renaming | Renamed | DirectorySynced | ClosingEntry | ClosingFile | ClosingDirectory | Poisoned !Stage deriving (Eq,Show)
data Hold = Live !Fd | Closing !Fd | Closed | Uncertain !Fd deriving (Eq,Show)
data State = State !Stage !(Maybe Hold) !(Maybe Hold) ![String]
data HandleStatus = HandleAbsent | HandleOwned | HandleClosing | HandleClosed | HandleUncertain deriving (Eq,Show)
data StorageStatus = StorageStatus { storageStage :: !Stage, directoryStatus :: !HandleStatus, fileStatus :: !HandleStatus, directoryIdentity :: !(Maybe (Integer,Integer)), fileIdentity :: !(Maybe (Integer,Integer)), entryStatus :: !HandleStatus, storageFailures :: ![String] } deriving (Eq,Show)
data Storage = Storage !(IORef State) !(MVar ()) !(Stage -> IO ()) !(IORef (Maybe (Integer,Integer),Maybe (Integer,Integer))) !(IORef (Maybe Hold))
newStorage :: IO Storage
newStorage = newStorageWithHookForTest (const (pure ()))
-- Same production route with an injected fault point; private test unit only.
newStorageWithHookForTest :: (Stage -> IO ()) -> IO Storage
newStorageWithHookForTest hook = Storage <$> newIORef (State Empty Nothing Nothing []) <*> newMVar () <*> pure hook <*> newIORef (Nothing,Nothing) <*> newIORef Nothing

-- One exclusive offer; False leaves the candidate with its original caller.
-- True publishes the actual descriptor before any validation can fail.
offerDirectory :: Storage -> Fd -> IO Bool
offerDirectory (Storage state _ _ _ _) fd = mask $ \_ -> atomicModifyIORef' state $ \current@(State stage _ _ _) ->
 if stage == Empty then (State Offered (Just (Live fd)) Nothing [],True) else (current,False)

storageStatus :: Storage -> IO StorageStatus
storageStatus (Storage state _ _ identities entry) = do
 State stage directory file diagnostic <- readIORef state
 (directoryId,fileId) <- readIORef identities
 entryHold <- readIORef entry
 pure (StorageStatus stage (status directory) (status file) directoryId fileId (status entryHold) diagnostic)
 where
  status Nothing = HandleAbsent
  status (Just (Live _)) = HandleOwned
  status (Just (Closing _)) = HandleClosing
  status (Just Closed) = HandleClosed
  status (Just (Uncertain _)) = HandleUncertain

-- This is raw byte storage, not a terminal-ticket API. No caller can derive a
-- DurableReceipt from it; exact owner and host-retirement integration remains.
-- Status alone is diagnostic. Keep this lease through every correlated owner
-- check or state transition that depends on the retained handles. Retirement
-- and persistence use the same gate. Busy never waits or borrows that custody.
withStorageLease :: Storage -> (StorageStatus -> IO a) -> IO (Maybe a)
withStorageLease store@(Storage _ gate _ _ _) action = mask $ \restore -> do
 acquired <- tryTakeMVar gate
 case acquired of
  Nothing -> pure Nothing
  Just () -> (Just <$> (storageStatus store >>= restore . action)) `finally` putMVar gate ()

persistBytes :: Storage -> B.ByteString -> IO (Either String ())
persistBytes store@(Storage state gate _ _ _) bytes = mask $ \restore -> do
 acquired <- tryTakeMVar gate
 case acquired of
  Nothing -> pure (Left "storage busy")
  Just () -> do
   result <- try (restore (writeTransaction store bytes)) :: IO (Either SomeException ())
   case result of
    Right () -> putMVar gate () >> pure (Right ())
    Left err -> do
     update state $ \(State prior directory file diagnostics) -> State (Poisoned prior) directory file (take 8 (show err:diagnostics))
     putMVar gate ()
     case fromException err :: Maybe SomeAsyncException of
      Just _ -> throwIO err
      Nothing -> pure (Left (show err))

writeTransaction :: Storage -> B.ByteString -> IO ()
writeTransaction (Storage state _ hook identities entry) bytes = mask $ \restore -> do
 if B.null bytes || B.length bytes > 65536 then ioError (userError "invalid bounded record") else pure ()
 selected <- atomicModifyIORef' state $ \current@(State stage directory file diagnostic) -> case (stage,directory,file) of
  (Offered,Just (Live fd),Nothing) -> (State Creating directory Nothing diagnostic,Just fd)
  _ -> (current,Nothing)
 directory <- maybe (ioError (userError "directory unavailable")) pure selected
 restore (hook Creating)
 dst <- restore (getFdStatus directory)
 uid <- restore getEffectiveUserID
 if not (isDirectory dst) || fileOwner dst /= uid || not (privateMode dst)
  then ioError (userError "directory identity or mode") else pure ()
 let directoryId = fileIdentityOf dst
 atomicModifyIORef' identities $ \(_,fileId) -> ((Just directoryId,fileId),())
 let Fd dir = directory
 -- O_EXCL and O_NOFOLLOW avoid replacement of an existing name. The name is
 -- fixed, never an untrusted path; preexisting content is not overwritten.
 raw <- withCString ".warlock-cancel-terminal.tmp" $ \name -> throwErrnoIfMinus1 "openat" (c_openat dir name (#{const O_RDWR} .|. #{const O_CREAT} .|. #{const O_EXCL} .|. #{const O_NOFOLLOW} .|. #{const O_CLOEXEC}) 0o600)
 let file = Fd raw
 update state $ \(State _ d _ e) -> State Writing d (Just (Live file)) e
 restore (hook Writing)
 before <- restore (getFdStatus file)
 if not (isRegularFile before) || fileOwner before /= uid || linkCount before /= 1 || not (privateFileMode before) || fileSize before /= 0
  then ioError (userError "staging type, owner, link count or mode") else pure ()
 let selectedFileId = fileIdentityOf before
 atomicModifyIORef' identities $ \(directoryId',_) -> ((directoryId',Just selectedFileId),())
 restore (B.useAsCStringLen bytes (\(ptr,len) -> writeAll hook raw (castPtr ptr) len))
 after <- restore (getFdStatus file)
 if not (isRegularFile after) || fileOwner after /= uid || linkCount after /= 1 || not (privateFileMode after) || fileIdentityOf after /= selectedFileId || toInteger (fileSize after) /= toInteger (B.length bytes)
  then ioError (userError "staging identity or length changed") else pure ()
 update state $ \(State _ d f e) -> State ReadingBack d f e
 restore (hook ReadingBack)
 restore (verifyExact raw bytes)
 update state $ \(State _ d f e) -> State SyncingFile d f e
 restore (hook SyncingFile)
 restore (throwErrnoIfMinus1_ "fsync terminal" (c_fsync raw))
 update state $ \(State _ d f e) -> State FileSynced d f e
 restore (hook FileSynced)
 update state $ \(State _ d f e) -> State Renaming d f e
 restore (hook Renaming)
 restore $ withCString ".warlock-cancel-terminal.tmp" $ \old -> withCString "warlock-cancel-terminal.v1" $ \new ->
  throwErrnoIfMinus1_ "renameat2 terminal" (c_renameat2 dir old dir new #{const RENAME_NOREPLACE})
 update state $ \(State _ d f e) -> State Renamed d f e
 restore (hook Renamed)
 restore (throwErrnoIfMinus1_ "fsync directory" (c_fsync dir))
 -- Retain the final directory entry itself before any fallible fstat.  O_PATH
 -- follows no caller-provided symlink. This checks the name-to-inode join at
 -- this instant, under the private directory/exclusive writer premise.
 entryRaw <- withCString "warlock-cancel-terminal.v1" $ \name -> throwErrnoIfMinus1 "openat final" (c_openat dir name (#{const O_PATH} .|. #{const O_NOFOLLOW} .|. #{const O_CLOEXEC}) 0)
 let entryFd = Fd entryRaw
 atomicModifyIORef' entry $ \_ -> (Just (Live entryFd),())
 finalEntry <- restore (getFdStatus entryFd)
 finalDirectory <- restore (getFdStatus directory)
 finalFile <- restore (getFdStatus file)
 if not (isRegularFile finalEntry) || fileOwner finalEntry /= uid || linkCount finalEntry /= 1 || not (privateFileMode finalEntry) || fileIdentityOf finalEntry /= selectedFileId ||
    not (isDirectory finalDirectory) || fileOwner finalDirectory /= uid || not (privateMode finalDirectory) || fileIdentityOf finalDirectory /= directoryId ||
    not (isRegularFile finalFile) || fileOwner finalFile /= uid || linkCount finalFile /= 1 || not (privateFileMode finalFile) || fileIdentityOf finalFile /= selectedFileId || toInteger (fileSize finalFile) /= toInteger (B.length bytes)
  then ioError (userError "post-publication identity changed") else pure ()
 update state $ \(State _ d f e) -> State DirectorySynced d f e
 restore (hook DirectorySynced)

fileIdentityOf :: FileStatus -> (Integer,Integer)
fileIdentityOf value = (toInteger (deviceID value),toInteger (fileID value))
privateMode :: FileStatus -> Bool
privateMode value = fileMode value .&. fromIntegral (#{const S_IRWXU} .|. #{const S_IRWXG} .|. #{const S_IRWXO} .|. #{const S_ISUID} .|. #{const S_ISGID} .|. #{const S_ISVTX} :: CInt) == fromIntegral (#{const S_IRWXU} :: CInt)
privateFileMode :: FileStatus -> Bool
privateFileMode value = fileMode value .&. fromIntegral (#{const S_IRWXU} .|. #{const S_IRWXG} .|. #{const S_IRWXO} .|. #{const S_ISUID} .|. #{const S_ISGID} .|. #{const S_ISVTX} :: CInt) == fromIntegral (#{const S_IRUSR} .|. #{const S_IWUSR} :: CInt)

writeAll :: (Stage -> IO ()) -> CInt -> Ptr () -> Int -> IO ()
writeAll _ _ _ 0 = pure ()
writeAll hook fd ptr remaining = do
 hook Writing
 written <- throwErrnoIfMinus1 "write terminal" (c_write fd ptr (fromIntegral remaining))
 if written <= 0 || toInteger written > toInteger remaining then ioError (userError "short write invalid")
  else let used = fromIntegral written in writeAll hook fd (ptr `plusPtr` used) (remaining-used)

-- Read back the same held regular file and compare actual bytes before fsync.
-- This is a snapshot check, not a hostile-same-UID future immutability proof.
verifyExact :: CInt -> B.ByteString -> IO ()
verifyExact fd expected = allocaBytes (B.length expected) $ \buffer -> do
 let go offset remaining
      | remaining == 0 = pure ()
      | otherwise = do
         got <- throwErrnoIfMinus1 "pread terminal" (c_pread fd (buffer `plusPtr` offset) (fromIntegral remaining) (fromIntegral offset))
         if got <= 0 || toInteger got > toInteger remaining
          then ioError (userError "readback incomplete")
          else let count = fromIntegral got in go (offset+count) (remaining-count)
 go 0 (B.length expected)
 actual <- B.packCStringLen (castPtr buffer,B.length expected)
 if actual == expected then pure () else ioError (userError "readback differs")

-- Each independently claimed close is attempted once. A failed/async close
-- retains the descriptor identity as Uncertain and is never numerically retried.
retireStorage :: Storage -> IO StorageStatus
retireStorage store@(Storage state gate hook _ entry) = mask $ \restore -> do
 acquired <- tryTakeMVar gate
 case acquired of
  Nothing -> storageStatus store
  Just () -> do
   entryResult <- closeEntry state entry hook restore
   fileResult <- closeOne state False hook restore
   dirResult <- closeOne state True hook restore
   putMVar gate ()
   let asyncs = [e | Left e <- [entryResult,fileResult,dirResult], isAsync e]
   case asyncs of e:_ -> throwIO e; [] -> storageStatus store
 where isAsync e = case fromException e :: Maybe SomeAsyncException of Just _ -> True; Nothing -> False

update :: IORef State -> (State -> State) -> IO ()
update state change = atomicModifyIORef' state (\old -> (change old,()))

closeOne :: IORef State -> Bool -> (Stage -> IO ()) -> (IO () -> IO ()) -> IO (Either SomeException ())
closeOne state directory hook restore = do
 selected <- atomicModifyIORef' state $ \(State stage d f diagnostics) ->
  let chosen = if directory then d else f in case chosen of
   Just (Live fd) -> (if directory then State stage (Just (Closing fd)) f diagnostics else State stage d (Just (Closing fd)) diagnostics,Just fd)
   _ -> (State stage d f diagnostics,Nothing)
 case selected of
  Nothing -> pure (Right ())
  Just fd@(Fd raw) -> do
   result <- try (restore (hook (if directory then ClosingDirectory else ClosingFile) >> throwErrnoIfMinus1_ "close storage" (c_close raw)))
   update state $ \(State stage d f diagnostics) ->
    let held = case result of Right () -> Closed; Left _ -> Uncertain fd
        next = case result of Right () -> diagnostics; Left err -> take 8 (show (err :: SomeException):diagnostics)
    in if directory then State stage (Just held) f next else State stage d (Just held) next
   pure result

-- The final-entry descriptor is a distinct owned handle, never merged with
-- the file descriptor merely because they describe the same inode.
closeEntry :: IORef State -> IORef (Maybe Hold) -> (Stage -> IO ()) -> (IO () -> IO ()) -> IO (Either SomeException ())
closeEntry state entry hook restore = do
 selected <- atomicModifyIORef' entry $ \held -> case held of
  Just (Live fd) -> (Just (Closing fd),Just fd)
  _ -> (held,Nothing)
 case selected of
  Nothing -> pure (Right ())
  Just fd@(Fd raw) -> do
   result <- try (restore (hook ClosingEntry >> throwErrnoIfMinus1_ "close final entry" (c_close raw)))
   atomicModifyIORef' entry $ \_ -> (Just (case result of Right () -> Closed; Left _ -> Uncertain fd),())
   case result of
    Left err -> update state $ \(State stage d f diagnostics) -> State stage d f (take 8 (show (err :: SomeException):diagnostics))
    Right () -> pure ()
   pure result
