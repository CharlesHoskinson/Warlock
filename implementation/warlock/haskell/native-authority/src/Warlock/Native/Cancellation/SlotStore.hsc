{-# LANGUAGE CPP #-}
{-# LANGUAGE ForeignFunctionInterface #-}
{-# LANGUAGE OverloadedStrings #-}
#define _GNU_SOURCE 1
#include <sys/types.h>
#include <sys/stat.h>
#include <dirent.h>
#include <fcntl.h>
#include <unistd.h>
#include <stdio.h>
-- Relative bounded storage; no native-effect, receipt, or authentication authority.
module Warlock.Native.Cancellation.SlotStore
 (SlotStore,SlotName,SlotError(..),SlotStatus(..),SlotResource(..),ChildDirectory(..),newSlotStore,slotName,offerDirectory,offerChildDirectory
 ,readSlot,scanSlots,publishSlot,removeSlot,slotStatus,retireSlotStore
#ifdef SLOTSTORE_TESTING
 ,newSlotStoreWithHookForTest
#endif
 ) where
import Control.Concurrent (runInBoundThread)
import Control.Concurrent.MVar (MVar,newMVar,tryTakeMVar,putMVar)
import Control.Exception (IOException,Exception,SomeAsyncException,SomeException,finally,fromException,mask,throwIO,try)
import Control.Monad (unless,when,foldM)
import Data.Bits ((.&.),(.|.))
import qualified Data.ByteString as B
import System.IO.Error (isDoesNotExistError,isAlreadyExistsError)
import Data.List (nub)
import Data.Int (Int64)
import Data.Word (Word8,Word32,Word64)
import Data.IORef (IORef,atomicModifyIORef',newIORef,readIORef)
import Foreign.C.Error (throwErrnoIfMinus1,throwErrnoIfMinus1_)
import Foreign.C.String (CString)
import Foreign.C.Types (CInt(..),CSize(..),CUInt(..),CUShort(..))
import Foreign.Marshal.Alloc (allocaBytes)
import Foreign.Marshal.Array (peekArray)
import Foreign.Ptr (Ptr,castPtr,nullPtr,plusPtr)
import Foreign.ForeignPtr (ForeignPtr,mallocForeignPtrArray,withForeignPtr)
import Foreign.Storable (peek,poke,peekByteOff,peekElemOff,pokeElemOff)
import System.Posix.Files (FileStatus,deviceID,fileID,fileMode,fileOwner,fileSize,getFdStatus,isDirectory,isRegularFile,linkCount,modificationTimeHiRes,statusChangeTimeHiRes)
import System.Posix.Types (Fd(..))
import System.Posix.User (getEffectiveUserID,getRealUserID)

foreign import ccall safe "mkdirat" c_mkdirat :: CInt -> CString -> #{type mode_t} -> IO CInt
foreign import ccall safe "fstatat" c_fstatat :: CInt -> CString -> Ptr () -> CInt -> IO CInt
foreign import ccall safe "openat" c_openat :: CInt -> CString -> CInt -> #{type mode_t} -> IO CInt
foreign import ccall safe "pread" c_pread :: CInt -> Ptr () -> CSize -> #{type off_t} -> IO #{type ssize_t}
foreign import ccall safe "write" c_write :: CInt -> Ptr () -> CSize -> IO #{type ssize_t}
foreign import ccall safe "fsync" c_fsync :: CInt -> IO CInt
foreign import ccall safe "renameat2" c_renameat2 :: CInt -> CString -> CInt -> CString -> CUInt -> IO CInt
foreign import ccall safe "unlinkat" c_unlinkat :: CInt -> CString -> CInt -> IO CInt
foreign import ccall safe "close" c_close :: CInt -> IO CInt
foreign import ccall safe "fdopendir" c_fdopendir :: CInt -> IO (Ptr ())
foreign import ccall safe "closedir" c_closedir :: Ptr () -> IO CInt
foreign import ccall safe "readdir" c_readdir :: Ptr () -> IO (Ptr ())
foreign import ccall unsafe "__errno_location" c_errno :: IO (Ptr CInt)

data ChildDirectory = Admissions | Companions deriving (Eq,Show)
newtype SlotName = SlotName B.ByteString deriving (Eq,Ord,Show)
data SlotError = InvalidName | Busy | Unavailable | Corrupt | QuotaExceeded | Mismatch | IoFailure | Uncertain deriving (Eq,Show)
data Refuse = Refuse SlotError deriving Show
instance Exception Refuse
refuse :: SlotError -> IO a
refuse = throwIO . Refuse
data SlotResource = ResourceReserved | ResourceFD Fd | ResourceStream (Ptr ()) | ResourceClosingFD Fd | ResourceClosingStream (Ptr ()) | ResourceClosed | ResourceUnknownFD Fd | ResourceUnknownStream (Ptr ()) deriving (Eq,Show)
data SlotStatus = SlotStatus { slotBusy :: !Bool, slotOffered :: !Bool, slotPoisoned :: !Bool, slotRetired :: !Bool, slotUncertain :: !Int, slotStage :: !String, slotRetainedFDs :: ![Fd], slotRetainedStreams :: ![Ptr ()], slotResources :: ![(Int,SlotResource)], slotFailures :: ![SomeException] } deriving Show
data Hold = Reserved | Owned Fd | Stream (Ptr ()) | ClosingFd Fd | ClosingStream (Ptr ()) | Closed | UnknownFd Fd | UnknownStream (Ptr ()) deriving (Eq,Show)
data Cell = Cell !(ForeignPtr CInt) !(ForeignPtr (Ptr ()))
data State = State { directory :: !(Maybe Fd), offered :: !Bool, poisoned :: !Bool, retired :: !Bool, stage :: !String, holds :: ![(Int,Cell)], nextKey :: !Int, failures :: ![SomeException], faultHook :: !(String -> IO ()) }
data SlotStore = SlotStore !(IORef State) !(MVar ())
newSlotStore :: IO SlotStore
newSlotStore = makeStore (const (pure ()))
makeStore :: (String -> IO ()) -> IO SlotStore
makeStore hook = SlotStore <$> newIORef (State Nothing False False False "empty" [] 0 [] hook) <*> newMVar ()
#ifdef SLOTSTORE_TESTING
newSlotStoreWithHookForTest :: (String -> IO ()) -> IO SlotStore
newSlotStoreWithHookForTest = makeStore
#endif
change :: IORef State -> (State -> State) -> IO ()
change ref f = atomicModifyIORef' ref (\s -> (f s,()))
slotName :: B.ByteString -> Either SlotError SlotName
slotName x | x == "envelope-v1.json" = Right (SlotName x)
           | B.length x == 69 && B.drop 64 x == ".json" && B.all (\c -> (c>=48 && c<=57) || (c>=97 && c<=102)) (B.take 64 x) = Right (SlotName x)
           | otherwise = Left InvalidName
-- A second offer is not consumed. Ownership publication is the first action.
offerDirectory :: SlotStore -> Fd -> IO Bool
offerDirectory (SlotStore ref gate) fd = mask $ \_ -> do
 acquired <- tryTakeMVar gate
 case acquired of
  Nothing -> pure False
  Just () -> (atomicModifyIORef' ref $ \s ->
   if offered s || retired s then (s,False) else (s {directory=Just fd,offered=True,stage="offered"},True)) `finally` putMVar gate ()
-- Borrowed parent; caller retains the original host guard through the entire
-- multi-directory transaction. There is no authority predicate in this API.
offerChildDirectory :: SlotStore -> Fd -> ChildDirectory -> IO (Either SlotError ())
offerChildDirectory (SlotStore ref gate) parent child = mask $ \restore -> do
 acquired <- tryTakeMVar gate
 case acquired of
  Nothing -> pure (Left Busy)
  Just () -> (do
   claimed <- atomicModifyIORef' ref $ \s ->
    if offered s || retired s || poisoned s then (s,False)
    else (s {offered=True,poisoned=True,stage="child-claimed"},True)
   if not claimed then pure (Left Unavailable) else do
    result <- try (do
      fd <- restore (acquireChild ref parent child)
      -- Child is already owned by a prepublished cell. Publishing this alias
      -- never transfers or closes the borrowed parent.
      change ref (\s -> s {directory=Just fd,poisoned=False,stage="child-ready"})) :: IO (Either SomeException ())
    case result of
     Right () -> pure (Right ())
     Left err -> do
      change ref (\s -> s {failures=err:failures s,poisoned=True})
      case fromException err :: Maybe SomeAsyncException of
       Just _ -> throwIO err
       Nothing -> case fromException err of
        Just (Refuse why) -> pure (Left why)
        Nothing -> pure (Left IoFailure)
   ) `finally` putMVar gate ()

childName :: ChildDirectory -> B.ByteString
childName Admissions = "admissions-v1"
childName Companions = "cancellation-admissions-v1"

-- The original uid contract is real uid (the host is not assumed setuid).
validRealDirectory :: Fd -> IO FileStatus
validRealDirectory fd = do
 value <- getFdStatus fd
 uid <- getRealUserID
 effective <- getEffectiveUserID
 unless (uid == effective && isDirectory value && fileOwner value == uid && fileMode value .&. fromIntegral modeMask == 0o700) (refuse Corrupt)
 pure value

-- fstatat observes the actual parent-relative name without following links.
checkChildName :: Fd -> B.ByteString -> FileStatus -> IO ()
checkChildName parent name held = allocaBytes #{size struct stat} $ \buffer -> B.useAsCString name $ \n -> do
 _ <- throwErrnoIfMinus1 "fstatat child" (c_fstatat (fdRaw parent) n buffer #{const AT_SYMLINK_NOFOLLOW})
 dev <- #{peek struct stat, st_dev} buffer :: IO (#{type dev_t})
 ino <- #{peek struct stat, st_ino} buffer :: IO (#{type ino_t})
 mode <- #{peek struct stat, st_mode} buffer :: IO (#{type mode_t})
 uid <- #{peek struct stat, st_uid} buffer :: IO (#{type uid_t})
 actualUid <- getRealUserID
 unless (toInteger dev == toInteger (deviceID held) && toInteger ino == toInteger (fileID held)
  && (mode .&. fromIntegral (#{const S_IFMT} :: CInt)) == fromIntegral (#{const S_IFDIR} :: CInt)
  && mode .&. fromIntegral modeMask == 0o700 && toInteger uid == toInteger actualUid) (refuse Corrupt)

acquireChild :: IORef State -> Fd -> ChildDirectory -> IO Fd
acquireChild ref parent which = do
 mark ref "child-parent-check"
 parentBefore <- validRealDirectory parent
 let name = childName which
 mark ref "child-mkdir"
 createdResult <- try (B.useAsCString name $ \n -> throwErrnoIfMinus1_ "mkdirat child" (c_mkdirat (fdRaw parent) n 0o700)) :: IO (Either IOException ())
 created <- case createdResult of
  Right () -> pure True
  Left err | isAlreadyExistsError err -> pure False
  Left err -> throwIO err
 mark ref (if created then "child-created" else "child-existing")
 -- openRelative publishes the acquired FD to a preowned native cell before
 -- any subsequent stat, test hook, or name observation can run.
 (_,child) <- openRelative ref parent name (#{const O_RDONLY} .|. #{const O_DIRECTORY} .|. #{const O_NOFOLLOW} .|. #{const O_CLOEXEC}) 0
 mark ref "child-opened"
 childBefore <- validRealDirectory child
 mark ref "child-name-check"
 checkChildName parent name childBefore
 when created $ do
  mark ref "child-parent-fsync"
  syncFd parent
  mark ref "child-parent-synced"
 parentAfter <- validRealDirectory parent
 childAfter <- validRealDirectory child
 unless (identity parentBefore == identity parentAfter && identity childBefore == identity childAfter) (refuse Corrupt)
 checkChildName parent name childAfter
 mark ref "child-validated"
 pure child

slotStatus :: SlotStore -> IO SlotStatus
slotStatus (SlotStore ref gate) = mask $ \_ -> do
 available <- tryTakeMVar gate
 s <- readIORef ref
 case available of
  Nothing -> pure (SlotStatus True (offered s) (poisoned s) (retired s) (-1) (stage s) [] [] [] (failures s))
  Just () -> (do
   values <- mapM (readCell . snd) (holds s)
   let uncertain h = case h of UnknownFd _ -> True; UnknownStream _ -> True; ClosingFd _ -> True; ClosingStream _ -> True; Owned _ -> retired s; Stream _ -> retired s; _ -> False
       fdOf h = case h of Owned fd -> [fd]; ClosingFd fd -> [fd]; UnknownFd fd -> [fd]; _ -> []
       streamOf h = case h of Stream ptr -> [ptr]; ClosingStream ptr -> [ptr]; UnknownStream ptr -> [ptr]; _ -> []
       resource h = case h of Reserved -> ResourceReserved; Owned fd -> ResourceFD fd; Stream ptr -> ResourceStream ptr; ClosingFd fd -> ResourceClosingFD fd; ClosingStream ptr -> ResourceClosingStream ptr; Closed -> ResourceClosed; UnknownFd fd -> ResourceUnknownFD fd; UnknownStream ptr -> ResourceUnknownStream ptr
   let transferUnknown = retired s && stage s == "closing-directory" && case directory s of Just _ -> True; Nothing -> False
   pure (SlotStatus False (offered s) (poisoned s || transferUnknown) (retired s) (length (filter uncertain values) + if transferUnknown then 1 else 0) (stage s) (nub (maybe [] (:[]) (directory s) ++ concatMap fdOf values)) (concatMap streamOf values) (zip (map fst (holds s)) (map resource values)) (failures s))) `finally` putMVar gate ()

-- Every cell is allocated and installed into the store before its syscall.
-- FD/pointer publication writes directly to fixed storage while masked.
reserve :: IORef State -> IO Int
reserve ref = do
 current <- readIORef ref
 free <- findReusable (holds current)
 case free of
  Just (key,cell) -> setCell cell Reserved >> pure key
  Nothing -> do
   ints <- mallocForeignPtrArray 2
   ptrs <- mallocForeignPtrArray 1
   withForeignPtr ints $ \p -> pokeElemOff p 0 0 >> pokeElemOff p 1 0
   withForeignPtr ptrs $ \p -> pokeElemOff p 0 nullPtr
   atomicModifyIORef' ref $ \s -> let k=nextKey s in (s {nextKey=k+1,holds=(k,Cell ints ptrs):holds s},k)
 where
  findReusable [] = pure Nothing
  findReusable ((key,cell):rest) = do
   value <- readCell cell
   case value of Closed -> pure (Just (key,cell)); Reserved -> pure (Just (key,cell)); _ -> findReusable rest

cellFor :: IORef State -> Int -> IO Cell
cellFor ref key = do
 s <- readIORef ref
 maybe (ioError (userError "missing custody cell")) pure (lookup key (holds s))
setCell :: Cell -> Hold -> IO ()
setCell (Cell ints ptrs) value = withForeignPtr ints $ \ip -> withForeignPtr ptrs $ \pp -> case value of
 Reserved -> pokeElemOff ip 0 0
 Owned (Fd raw) -> pokeElemOff ip 1 raw >> pokeElemOff ip 0 1
 Stream ptr -> pokeElemOff pp 0 ptr >> pokeElemOff ip 0 2
 ClosingFd (Fd raw) -> pokeElemOff ip 1 raw >> pokeElemOff ip 0 3
 ClosingStream ptr -> pokeElemOff pp 0 ptr >> pokeElemOff ip 0 4
 Closed -> pokeElemOff ip 0 5
 UnknownFd (Fd raw) -> pokeElemOff ip 1 raw >> pokeElemOff ip 0 6
 UnknownStream ptr -> pokeElemOff pp 0 ptr >> pokeElemOff ip 0 7
publishFd :: Cell -> CInt -> IO ()
publishFd (Cell ints _) raw = withForeignPtr ints $ \p -> pokeElemOff p 1 raw >> pokeElemOff p 0 1
publishStream :: Cell -> Ptr () -> IO ()
publishStream (Cell ints ptrs) stream = withForeignPtr ints $ \ip -> withForeignPtr ptrs $ \pp -> pokeElemOff pp 0 stream >> pokeElemOff ip 0 2

readCell :: Cell -> IO Hold
readCell (Cell ints ptrs) = withForeignPtr ints $ \ip -> withForeignPtr ptrs $ \pp -> do
 tag <- peekElemOff ip 0
 case tag of
  0 -> pure Reserved
  1 -> Owned . Fd <$> peekElemOff ip 1
  2 -> Stream <$> peekElemOff pp 0
  3 -> ClosingFd . Fd <$> peekElemOff ip 1
  4 -> ClosingStream <$> peekElemOff pp 0
  5 -> pure Closed
  6 -> UnknownFd . Fd <$> peekElemOff ip 1
  7 -> UnknownStream <$> peekElemOff pp 0
  _ -> ioError (userError "invalid custody tag")
fdRaw :: Fd -> CInt
fdRaw (Fd x) = x
openRelative :: IORef State -> Fd -> B.ByteString -> CInt -> CInt -> IO (Int,Fd)
openRelative ref dir name flags mode = mask $ \_ -> do
 k <- reserve ref
 cell <- cellFor ref k
 raw <- B.useAsCString name $ \p -> throwErrnoIfMinus1 "openat" (c_openat (fdRaw dir) p flags (fromIntegral mode))
 publishFd cell raw
 pure (k,Fd raw)

-- Claims each close before syscall. A failed close is never retried; its exact
-- fd or DIR pointer remains in the owning store rather than a local list.
closeKey :: IORef State -> Int -> IO (Maybe SomeException)
closeKey ref key = mask $ \restore -> do
 cell <- cellFor ref key
 prior <- readCell cell
 case prior of
  Owned fd -> do
   setCell cell (ClosingFd fd)
   finish cell prior (restore (throwErrnoIfMinus1_ "close" (c_close (fdRaw fd))))
  Stream ptr -> do
   setCell cell (ClosingStream ptr)
   finish cell prior (restore (throwErrnoIfMinus1_ "closedir" (c_closedir ptr)))
  _ -> pure Nothing
 where
  finish cell prior action = do
   s <- readIORef ref
   result <- try (faultHook s "close-before" >> action >> faultHook s "close-after") :: IO (Either SomeException ())
   let after = case (prior,result) of (_,Right ()) -> Closed; (Owned fd,Left _) -> UnknownFd fd; (Stream p,Left _) -> UnknownStream p; _ -> Closed
   setCell cell after
   case result of Left e -> change ref (\current -> current {failures=e:failures current,poisoned=True}) >> pure (Just e); Right () -> pure Nothing

cleanup :: IORef State -> IO [SomeException]
cleanup ref = do
 s <- readIORef ref
 results <- mapM (\(key,cell) -> try (do
  held <- readCell cell
  case held of
   Owned fd | directory s == Just fd -> pure Nothing
   _ -> closeKey ref key) :: IO (Either SomeException (Maybe SomeException))) (holds s)
 let unexpected = [e | Left e <- results]
 mapM_ (\e -> change ref (\old -> old {failures=e:failures old,poisoned=True})) unexpected
 pure (concatMap (either (:[]) (maybe [] (:[]))) results)
isAsync :: SomeException -> Bool
isAsync e = case fromException e :: Maybe SomeAsyncException of Just _ -> True; Nothing -> False
chooseException :: Maybe SomeException -> [SomeException] -> Maybe SomeException
chooseException original rest = case original of
 Just e | isAsync e -> Just e
 _ -> case filter isAsync rest of e:_ -> Just e; [] -> case original of Just e -> Just e; Nothing -> case rest of e:_ -> Just e; [] -> Nothing
withGate :: SlotStore -> Bool -> (IORef State -> Fd -> IO (Either SlotError a)) -> IO (Either SlotError a)
withGate (SlotStore ref gate) mutating operation = mask $ \restore -> do
 acquired <- tryTakeMVar gate
 case acquired of
  Nothing -> pure (Left Busy)
  Just () -> (do
   s <- readIORef ref
   case directory s of
    Nothing -> pure (Left Unavailable)
    Just dir | retired s -> pure (Left Unavailable)
             | mutating && poisoned s -> pure (Left Uncertain)
             | otherwise -> do
       outcome <- try (restore (operation ref dir))
       extras <- cleanup ref
       current <- readIORef ref
       let mutationUncertain = mutating && stage current `elem` ["creating-temp","writing-temp","file-sync","file-synced","rename-started","renamed","unlink-started","unlinked","directory-sync","directory-synced"]
       when mutationUncertain (change ref (\x -> x {poisoned=True}))
       case outcome of Left e -> change ref (\x -> x {failures=e:failures x}); Right _ -> pure ()
       case chooseException (either Just (const Nothing) outcome) extras of
        Just e | isAsync e -> throwIO e
        _ | not (null extras) || mutationUncertain -> pure (Left Uncertain)
        _ -> case outcome of
          Left e -> case fromException e of Just (Refuse reason) -> pure (Left reason); Nothing -> pure (Left IoFailure)
          Right value -> pure value
   ) `finally` putMVar gate ()

identity :: FileStatus -> (Integer,Integer)
identity s = (toInteger (deviceID s),toInteger (fileID s))
modeMask :: CInt
modeMask = #{const S_IRWXU} .|. #{const S_IRWXG} .|. #{const S_IRWXO} .|. #{const S_ISUID} .|. #{const S_ISGID} .|. #{const S_ISVTX}
validDir :: Fd -> IO FileStatus
validDir fd = do
 s <- getFdStatus fd; uid <- getEffectiveUserID
 unless (isDirectory s && fileOwner s == uid && fileMode s .&. fromIntegral modeMask == 0o700) (refuse Corrupt)
 pure s
validFile :: Fd -> IO FileStatus
validFile fd = do
 s <- getFdStatus fd; uid <- getEffectiveUserID
 unless (isRegularFile s && fileOwner s == uid && linkCount s == 1 && fileMode s .&. fromIntegral modeMask == 0o600 && fileSize s >= 0 && fileSize s <= 1048576) (refuse Corrupt)
 pure s
sameStat :: FileStatus -> FileStatus -> Bool
sameStat x y = identity x == identity y && fileSize x == fileSize y && modificationTimeHiRes x == modificationTimeHiRes y && statusChangeTimeHiRes x == statusChangeTimeHiRes y
readExact :: Fd -> Int -> IO B.ByteString
readExact (Fd fd) size = allocaBytes (max 1 size) $ \buffer -> do
 let loop off | off == size = pure ()
              | otherwise = do
        n <- throwErrnoIfMinus1 "pread" (c_pread fd (buffer `plusPtr` off) (fromIntegral (size-off)) (fromIntegral off))
        when (n <= 0 || toInteger n > toInteger (size-off)) (refuse Corrupt)
        loop (off+fromIntegral n)
 loop 0
 B.packCStringLen (castPtr buffer,size)
writeExact :: Fd -> B.ByteString -> IO ()
writeExact (Fd fd) bytes = B.useAsCStringLen bytes $ \(start,size) -> let
 go off | off == size = pure ()
        | otherwise = do
    n <- throwErrnoIfMinus1 "write" (c_write fd (castPtr start `plusPtr` off) (fromIntegral (size-off)))
    when (n <= 0 || toInteger n > toInteger (size-off)) (refuse IoFailure)
    go (off+fromIntegral n)
 in go 0
readFlags, entryFlags :: CInt
readFlags = #{const O_RDONLY} .|. #{const O_NOFOLLOW} .|. #{const O_CLOEXEC} .|. #{const O_NONBLOCK}
entryFlags = #{const O_PATH} .|. #{const O_NOFOLLOW} .|. #{const O_CLOEXEC}
-- A final O_PATH entry is independently retained and joined to the read FD.
readEntry :: IORef State -> Fd -> SlotName -> IO (Maybe (B.ByteString,(Integer,Integer)))
readEntry ref dir (SlotName name) = do
 opened <- try (openRelative ref dir name readFlags 0) :: IO (Either IOException (Int,Fd))
 case opened of
  Left e | isDoesNotExistError e -> pure Nothing
         | otherwise -> throwIO e
  Right (_,fd) -> do
   before <- validFile fd
   bytes <- readExact fd (fromIntegral (fileSize before))
   after <- validFile fd
   unless (sameStat before after) (refuse Corrupt)
   (_,entry) <- openRelative ref dir name entryFlags 0
   entryStat <- validFile entry
   unless (sameStat after entryStat) (refuse Corrupt)
   pure (Just (bytes,identity after))
readSlot :: SlotStore -> SlotName -> IO (Either SlotError (Maybe B.ByteString))
readSlot store name = withGate store False $ \ref dir -> do
 _ <- validDir dir
 found <- readEntry ref dir name
 pure (Right (fmap fst found))

-- Independent open file description acquired relative to held directory.
-- The stream adopts exactly that fd. State is published under mask before
-- readdir. The bound thread keeps errno observation on the same OS thread.
names :: IORef State -> Fd -> IO [B.ByteString]
names ref dir = mask $ \restore -> do
 (key,fd) <- openRelative ref dir "." (#{const O_RDONLY} .|. #{const O_DIRECTORY} .|. #{const O_NOFOLLOW} .|. #{const O_CLOEXEC}) 0
 cell <- cellFor ref key
 stream <- c_fdopendir (fdRaw fd)
 when (stream == nullPtr) (ioError (userError "fdopendir failed"))
 publishStream cell stream
 restore $ runInBoundThread $ let
  go count found | count > 66 = refuse QuotaExceeded
                 | otherwise = do
    errnoPtr <- c_errno; poke errnoPtr 0
    entry <- c_readdir stream
    if entry == nullPtr then do
      err <- peek errnoPtr
      if err == 0 then pure (reverse found) else ioError (userError "readdir failed")
    else do
      recordLength <- #{peek struct dirent, d_reclen} entry :: IO CUShort
      let available = fromIntegral recordLength - (#{offset struct dirent, d_name} :: Int)
          limit = (#{size struct dirent} - #{offset struct dirent, d_name}) :: Int
      when (available <= 0 || available > limit) (refuse Corrupt)
      chars <- peekArray available (castPtr (entry `plusPtr` #{offset struct dirent, d_name}) :: Ptr Word8)
      let (prefix,tailBytes) = break (==0) chars
      when (null tailBytes) (refuse Corrupt)
      let name = B.pack prefix
      if name == "." || name == ".." then go (count+1) found else go (count+1) (name:found)
  in go (0 :: Int) []
scanInner :: IORef State -> Fd -> IO [(SlotName,B.ByteString,(Integer,Integer))]
scanInner ref dir = do
 _ <- validDir dir
 entries <- names ref dir
 when (length entries > 64) (refuse QuotaExceeded)
 parsed <- mapM (either refuse pure . slotName) entries
 when (length parsed /= length (unique parsed)) (refuse Corrupt)
 (_,reversed) <- foldM (\(total,acc) name -> do
  row <- readEntry ref dir name
  case row of
   Nothing -> refuse Corrupt
   Just (bytes,ident) -> do
    let next = total + toInteger (B.length bytes)
    when (next > 1048576) (refuse QuotaExceeded)
    pure (next,(name,bytes,ident):acc)) (0,[]) parsed
 pure (reverse reversed)
 where unique = foldr (\x acc -> if x `elem` acc then acc else x:acc) []
scanSlots :: SlotStore -> IO (Either SlotError [(SlotName,B.ByteString)])
scanSlots store = withGate store False $ \ref dir -> do
 rows <- scanInner ref dir
 pure (Right [(name,bytes) | (name,bytes,_) <- rows])

mark :: IORef State -> String -> IO ()
mark ref value = do
 change ref (\s -> s {stage=value})
 s <- readIORef ref
 faultHook s value
lookupRow :: SlotName -> [(SlotName,B.ByteString,(Integer,Integer))] -> Maybe (B.ByteString,(Integer,Integer))
lookupRow wanted rows = case [(bytes,ident) | (name,bytes,ident) <- rows, name == wanted] of
 [] -> Nothing
 [row] -> Just row
 _ -> Nothing
requireOld :: Maybe B.ByteString -> Maybe (B.ByteString,(Integer,Integer)) -> IO ()
requireOld Nothing Nothing = pure ()
requireOld (Just expected) (Just (actual,_)) | expected == actual = pure ()
requireOld _ _ = refuse Mismatch
sameDirectory :: FileStatus -> Fd -> IO ()
sameDirectory before dir = do
 after <- validDir dir
 unless (identity before == identity after) (refuse Corrupt)
syncFd :: Fd -> IO ()
syncFd (Fd raw) = throwErrnoIfMinus1_ "fsync" (c_fsync raw)
renameRelative :: Fd -> B.ByteString -> B.ByteString -> CUInt -> IO ()
renameRelative (Fd raw) old new flags = B.useAsCString old $ \a -> B.useAsCString new $ \b ->
 throwErrnoIfMinus1_ "renameat2" (c_renameat2 raw a raw b flags)
unlinkRelative :: Fd -> B.ByteString -> IO ()
unlinkRelative (Fd raw) name = B.useAsCString name $ \p -> throwErrnoIfMinus1_ "unlinkat" (c_unlinkat raw p 0)

publishSlot :: SlotStore -> SlotName -> Maybe B.ByteString -> B.ByteString -> IO (Either SlotError ())
publishSlot store name@(SlotName target) expected bytes = withGate store True $ \ref dir -> do
 when (B.length bytes > 1048576 || maybe False ((> 1048576) . B.length) expected) (refuse QuotaExceeded)
 initialDir <- validDir dir
 rows <- scanInner ref dir
 let old = lookupRow name rows
 requireOld expected old
 let projectedCount = length rows + case old of Nothing -> 1; Just _ -> 0
     projectedSize = sum [toInteger (B.length value) | (_,value,_) <- rows] - maybe 0 (toInteger . B.length . fst) old + toInteger (B.length bytes)
 when (projectedCount > 64 || projectedSize > 1048576) (refuse QuotaExceeded)
 mark ref "creating-temp"
 (_,temp) <- openRelative ref dir ".warlock-slot.tmp" (#{const O_RDWR} .|. #{const O_CREAT} .|. #{const O_EXCL} .|. #{const O_NOFOLLOW} .|. #{const O_CLOEXEC} .|. #{const O_NONBLOCK}) 0o600
 tempBefore <- validFile temp
 unless (fileSize tempBefore == 0) (refuse Corrupt)
 mark ref "writing-temp"
 writeExact temp bytes
 written <- validFile temp
 unless (identity written == identity tempBefore && toInteger (fileSize written) == toInteger (B.length bytes)) (refuse Corrupt)
 actual <- readExact temp (B.length bytes)
 unless (actual == bytes) (refuse Corrupt)
 verified <- validFile temp
 unless (sameStat written verified) (refuse Corrupt)
 mark ref "file-sync"
 syncFd temp
 mark ref "file-synced"
 current <- readEntry ref dir name
 unless (current == old) (refuse Mismatch)
 sameDirectory initialDir dir
 mark ref "rename-started"
 renameRelative dir ".warlock-slot.tmp" target (case old of Nothing -> #{const RENAME_NOREPLACE}; Just _ -> 0)
 mark ref "renamed"
 mark ref "directory-sync"
 syncFd dir
 mark ref "directory-synced"
 final <- readEntry ref dir name
 case final of
  Just (finalBytes,ident) | finalBytes == bytes && ident == identity tempBefore -> pure ()
  _ -> refuse Corrupt
 sameDirectory initialDir dir
 mark ref "complete"
 pure (Right ())

removeSlot :: SlotStore -> SlotName -> B.ByteString -> IO (Either SlotError ())
removeSlot store name@(SlotName target) expected = withGate store True $ \ref dir -> do
 when (B.length expected > 1048576) (refuse QuotaExceeded)
 initialDir <- validDir dir
 rows <- scanInner ref dir
 let original = lookupRow name rows
 requireOld (Just expected) original
 current <- readEntry ref dir name
 unless (current == original) (refuse Mismatch)
 sameDirectory initialDir dir
 mark ref "unlink-started"
 unlinkRelative dir target
 mark ref "unlinked"
 mark ref "directory-sync"
 syncFd dir
 mark ref "directory-synced"
 after <- readEntry ref dir name
 unless (after == Nothing) (refuse Corrupt)
 sameDirectory initialDir dir
 mark ref "complete"
 pure (Right ())

-- Busy retirement never races current IO; no current owner is closed on Busy.
retireSlotStore :: SlotStore -> IO SlotStatus
retireSlotStore store@(SlotStore ref gate) = mask $ \_ -> do
 acquired <- tryTakeMVar gate
 case acquired of
  Nothing -> do observed <- slotStatus store; pure (observed {slotBusy=True})
  Just () -> do
   deferred <- (do
    extras <- cleanup ref
    before <- readIORef ref
    closed <- case directory before of
     Nothing -> do
      change ref (\s -> s {retired=True,stage="retired"})
      pure Nothing
     Just fd -> do
      match <- findDirectoryCell fd (holds before)
      key <- case match of
       Just existing -> pure existing
       Nothing -> do
        fresh <- reserve ref
        cell <- cellFor ref fresh
        publishFd cell (fdRaw fd)
        pure fresh
      -- The cell owns the very same descriptor before this atomic handoff.
      change ref (\s -> s {directory=Nothing,retired=True,stage="closing-directory"})
      closeKey ref key
    pure (chooseException Nothing (extras ++ maybe [] (:[]) closed))) `finally` putMVar gate ()
   case deferred of
    Just e | isAsync e -> throwIO e
    _ -> slotStatus store
 where
  findDirectoryCell _ [] = pure Nothing
  findDirectoryCell target ((key,cell):rest) = do
   value <- readCell cell
   case value of Owned fd | fd == target -> pure (Just key); _ -> findDirectoryCell target rest
