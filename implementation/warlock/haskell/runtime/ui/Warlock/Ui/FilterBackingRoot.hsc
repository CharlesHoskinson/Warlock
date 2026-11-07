{-# LANGUAGE ExistentialQuantification #-}
{-# LANGUAGE ForeignFunctionInterface #-}
{-# LANGUAGE ScopedTypeVariables #-}
-- Parent-owned, fixed-root filter backing custody. No raw descriptor factory.
module Warlock.Ui.FilterBackingRoot
  ( FilterBackingOwner, newFilterBackingRoot, filterBackingBinding
  , markFilterBackingSpawn, bindFilterBacking, retireFilterBacking
  , inspectFilterBacking, discardUnstartedBacking ) where

#define _GNU_SOURCE 1
#include <fcntl.h>
#include <sys/stat.h>
#include <sys/random.h>
#include <unistd.h>

import Control.Concurrent.MVar (MVar, newMVar, withMVar)
import Control.Exception (IOException, SomeException, SomeAsyncException, bracket, fromException, mask_, onException, throwIO, try)
import Control.Monad (unless, when)
import Data.Bits ((.&.), (.|.))
import qualified Data.ByteString as B
import qualified Data.ByteString.Char8 as C
import Data.IORef (IORef, newIORef, readIORef, writeIORef, atomicModifyIORef')
import Data.List (sort)
import qualified Data.Text as T
import Data.Word (Word8, Word32)
import Foreign.C.Error (throwErrnoIfMinus1, throwErrnoIfMinus1_)
import Foreign.C.String (CString)
import Foreign.C.Types (CInt(..), CSize(..), CUInt(..))
import Foreign.Marshal.Alloc (allocaBytes)
import Foreign.Marshal.Array (peekArray)
import Foreign.Ptr (Ptr)
import Numeric (showHex)
import qualified System.Posix.Directory.ByteString as Dir
import qualified System.Posix.Files.ByteString as Files
import System.Posix.Files
  ( FileStatus, deviceID, fileID, fileMode, fileOwner, fileSize, getFdStatus
  , isDirectory, isRegularFile, isSymbolicLink, linkCount
  , modificationTimeHiRes, statusChangeTimeHiRes )
import System.Posix.Types (Fd(..), CSsize(..))
import System.Posix.User (getEffectiveUserID)
import System.IO.Error (isDoesNotExistError)
import Warlock.Capture.Process.Bootstrap (AdmissionDeadline, deadlineAbsoluteNs, remainingMicros)
import qualified Warlock.Ui.EngineBroker as Broker
import Warlock.Ui.EngineCustody
  ( EngineProcess, EngineExitReceipt, enginePid, engineLiveChild, engineExpectedIds
  , engineNormalExit, engineExitMatches, engineExitFacts )
import qualified Warlock.Ui.EngineProtocol as Protocol

foreign import ccall unsafe "open" openRaw :: CString -> CInt -> IO CInt
foreign import ccall unsafe "openat" openAtRaw :: CInt -> CString -> CInt -> IO CInt
foreign import ccall unsafe "mkdirat" mkdirAtRaw :: CInt -> CString -> #{type mode_t} -> IO CInt
foreign import ccall unsafe "unlinkat" unlinkAtRaw :: CInt -> CString -> CInt -> IO CInt
foreign import ccall unsafe "close" closeRaw :: CInt -> IO CInt
foreign import ccall unsafe "fcntl" flagsRaw :: CInt -> CInt -> IO CInt
foreign import ccall unsafe "getrandom" randomRaw :: Ptr Word8 -> CSize -> CUInt -> IO CSsize

data Pin = Pin !Integer !Integer !Integer deriving (Eq,Show)
data Binding = forall refusal. Binding EngineProcess (Broker.Broker refusal)
data Phase = Fresh | Spawning | Bound Binding | Retiring | Released EngineProcess | Discarded | Retained
data FilterBackingOwner = Owner Fd !B.ByteString !Pin !Pin AdmissionDeadline (MVar ()) (IORef Phase)
type Stamp = (Integer,Integer,Integer,Integer,Integer,Integer,Integer,Integer)
data Node = Node !B.ByteString !Stamp !Bool [Node]

number :: Fd -> CInt
number (Fd fd) = fd

require :: Bool -> String -> IO ()
require value message = unless value (ioError (userError message))

leftNow :: AdmissionDeadline -> IO ()
leftNow deadline = remainingMicros deadline >>= (\left -> require (left > 0) "backing original deadline expired")

dirFlags :: CInt
dirFlags = #{const O_RDONLY} .|. #{const O_DIRECTORY} .|. #{const O_NOFOLLOW}
  .|. #{const O_CLOEXEC} .|. #{const O_NONBLOCK}

closeFd :: Fd -> IO ()
closeFd fd = throwErrnoIfMinus1_ "backing close once" (closeRaw (number fd))

openTmp :: IO Fd
openTmp = C.useAsCString (C.pack "/tmp") $ \path ->
  Fd <$> throwErrnoIfMinus1 "backing fixed tmp" (openRaw path dirFlags)

validName :: B.ByteString -> Bool
validName name = not (B.null name) && B.length name <= 255
  && name /= C.pack "." && name /= C.pack ".." && not (B.elem 0 name || B.elem 47 name)

openAt :: Fd -> B.ByteString -> CInt -> IO Fd
openAt parent name flags = do
  require (validName name) "backing entry name refused"
  B.useAsCString name $ \text -> Fd <$> throwErrnoIfMinus1 "backing openat" (openAtRaw (number parent) text flags)

pin :: FileStatus -> Pin
pin status = Pin (toInteger (deviceID status)) (toInteger (fileID status)) (toInteger (fileOwner status))

stamp :: FileStatus -> Stamp
stamp status = (toInteger (deviceID status),toInteger (fileID status),toInteger (fileOwner status),
  toInteger (fileMode status),toInteger (linkCount status),toInteger (fileSize status),
  floor (modificationTimeHiRes status * 1000000000),floor (statusChangeTimeHiRes status * 1000000000))

named :: Fd -> B.ByteString -> IO FileStatus
named fd name = do
  require (validName name) "backing named entry refused"
  Files.getSymbolicLinkStatus (C.pack ("/proc/self/fd/" ++ show (number fd) ++ "/") <> name)

rootPath :: B.ByteString -> FilePath
rootPath name = "/tmp/" ++ C.unpack name

privateDirectory :: FileStatus -> Pin -> Bool
privateDirectory status expected = isDirectory status && not (isSymbolicLink status)
  && pin status == expected && fileMode status .&. 0o7777 == 0o700

checkRoot :: FilterBackingOwner -> IO ()
checkRoot (Owner fd name parentPin rootPin deadline _ _) = do
  leftNow deadline
  uid <- toInteger <$> getEffectiveUserID
  let Pin _ _ owner = rootPin
  require (uid == owner) "backing owner changed"
  flags <- flagsRaw (number fd) #{const F_GETFD}
  require (flags >= 0 && flags .&. #{const FD_CLOEXEC} /= 0) "backing descriptor no longer close-on-exec"
  actual <- getFdStatus fd
  require (privateDirectory actual rootPin) "backing held directory drift"
  bracket openTmp closeFd $ \parent -> do
    base <- getFdStatus parent
    require (pin base == parentPin && isDirectory base) "backing parent drift"
    entry <- named parent name
    require (privateDirectory entry rootPin) "backing named root drift"
  leftNow deadline

newFilterBackingRoot :: AdmissionDeadline -> IO FilterBackingOwner
newFilterBackingRoot deadline = mask_ $ do
  leftNow deadline
  gate <- newMVar ()
  phase <- newIORef Fresh
  bytes <- allocaBytes 32 $ \buffer -> do
    count <- randomRaw buffer 32 #{const GRND_NONBLOCK}
    require (count == 32) "backing entropy unavailable"
    peekArray 32 buffer
  let hex byte = case showHex byte "" of [one] -> ['0',one]; more -> more
      name = C.pack ("warlock-ui-backing-" ++ concatMap hex bytes)
  bracket openTmp closeFd $ \parent -> do
    base <- getFdStatus parent
    require (isDirectory base && (fileMode base .&. 0o022 == 0 || fileMode base .&. 0o1000 /= 0))
      "backing tmp parent is unsafe"
    leftNow deadline
    -- No EEXIST retry/reuse and no caller-selected root.
    B.useAsCString name $ \text -> throwErrnoIfMinus1_ "backing exclusive mkdir" (mkdirAtRaw (number parent) text 0o700)
    fd <- openAt parent name dirFlags
    (do
      status <- getFdStatus fd
      uid <- toInteger <$> getEffectiveUserID
      require (isDirectory status && fileMode status .&. 0o7777 == 0o700
            && toInteger (fileOwner status) == uid && deviceID status == deviceID base)
        "backing allocated identity refused"
      let owner = Owner fd name (pin base) (pin status) deadline gate phase
      checkRoot owner
      pure owner) `onException` closeFd fd

filterBackingBinding :: FilterBackingOwner -> IO Protocol.BackingRootBinding
filterBackingBinding owner@(Owner _ name _ (Pin dev ino uid) _ gate phase) = withMVar gate $ \_ -> do
  state <- readIORef phase
  case state of
    Retiring -> ioError (userError "backing retirement in progress")
    Released _ -> ioError (userError "backing released")
    Discarded -> ioError (userError "unstarted backing discarded")
    Retained -> ioError (userError "backing custody uncertain")
    _ -> do
      checkRoot owner
      either (ioError . userError . show) pure
        (Protocol.backingRootBinding (T.pack (rootPath name)) dev ino uid)

markFilterBackingSpawn :: FilterBackingOwner -> IO ()
markFilterBackingSpawn owner@(Owner _ _ _ _ _ gate phase) = mask_ $ withMVar gate $ \_ -> do
  checkRoot owner
  state <- readIORef phase
  case state of
    Fresh -> writeIORef phase Spawning
    _ -> ioError (userError "backing spawn already reserved")

bindFilterBacking :: FilterBackingOwner -> EngineProcess -> Broker.Broker refusal -> IO ()
bindFilterBacking owner@(Owner _ _ _ (Pin _ _ uid) _ gate phase) engine broker = mask_ $ withMVar gate $ \_ -> do
  checkRoot owner
  state <- readIORef phase
  case state of
    Spawning -> do
      live <- engineLiveChild engine (enginePid engine)
      require (live && fst (engineExpectedIds engine) == uid) "backing engine owner unavailable"
      writeIORef phase (Bound (Binding engine broker))
    _ -> ioError (userError "backing context already bound or unavailable")

names :: AdmissionDeadline -> Fd -> IO [B.ByteString]
names deadline fd = bracket (Dir.openDirStream (C.pack ("/proc/self/fd/" ++ show (number fd)))) Dir.closeDirStream $ \stream ->
  let loop count result = do
        leftNow deadline
        name <- Dir.readDirStream stream
        if B.null name then pure (sort result) else if name == C.pack "." || name == C.pack ".." then loop count result else do
          require (count < 8192 && validName name) "backing entry bound/name refused"
          loop (count+1) (name:result)
  in loop (0 :: Int) []

snapshot :: FilterBackingOwner -> IO [Node]
snapshot owner@(Owner root _ _ (Pin device _ uid) deadline _ _) = do
  checkRoot owner
  budget <- newIORef (0 :: Int)
  let visit directory depth top = do
        require (depth <= 16) "backing depth bound"
        before <- stamp <$> getFdStatus directory
        entries <- names deadline directory
        when top $ require (all (`elem` map C.pack ["controller","bar","popup"]) entries) "unexpected backing role"
        result <- mapM (\name -> do
          leftNow deadline
          total <- atomicModifyIORef' budget (\count -> (count+1,count+1))
          require (total <= 8192) "backing total entry bound"
          status <- named directory name
          require (not (isSymbolicLink status) && toInteger (fileOwner status) == uid
                && toInteger (deviceID status) == device && fileMode status .&. 0o7022 == 0)
            "backing type/owner/device/mode refused"
          if isDirectory status then do
            when top $ require (fileMode status .&. 0o7777 == 0o700) "backing role not private"
            bracket (openAt directory name dirFlags) closeFd $ \child -> do
              held <- getFdStatus child
              require (stamp held == stamp status) "backing directory changed during open"
              descendants <- visit child (depth+1) False
              pure (Node name (stamp status) True descendants)
          else do
            require (isRegularFile status && linkCount status == 1 && not top) "backing regular file/link refused"
            pure (Node name (stamp status) False [])) entries
        after <- stamp <$> getFdStatus directory
        require (before == after) "backing directory changed during inventory"
        pure result
  visit root (0 :: Int) True

removeTree :: FilterBackingOwner -> IO ()
removeTree owner@(Owner root name parentPin rootPin deadline _ _) = do
  tree <- snapshot owner -- Complete preflight BEFORE the first unlink.
  let remove directory (Node child expected isDir descendants) = do
        leftNow deadline
        status <- named directory child
        require (stamp status == expected) "backing entry drift before removal"
        let flags = if isDir then dirFlags else #{const O_RDONLY} .|. #{const O_NOFOLLOW} .|. #{const O_CLOEXEC} .|. #{const O_NONBLOCK}
        bracket (openAt directory child flags) closeFd $ \held -> do
          actual <- getFdStatus held
          require (stamp actual == expected) "backing held entry drift"
          when isDir $ do
            actualNames <- names deadline held
            require (actualNames == sort [key | Node key _ _ _ <- descendants]) "backing children drift"
            mapM_ (remove held) descendants
            remaining <- names deadline held
            require (null remaining) "backing directory not empty after removal"
          again <- named directory child
          heldNow <- getFdStatus held
          let (_,_,_,expectedMode,_,_,_,_) = expected
          require (pin again == pin heldNow && isDirectory again == isDir
                && toInteger (fileMode again) == expectedMode && not (isSymbolicLink again)) "backing named entry replaced"
          when (not isDir) $ require (stamp again == expected && linkCount heldNow == 1) "backing regular entry changed"
          leftNow deadline
          B.useAsCString child $ \text -> throwErrnoIfMinus1_ "backing owned unlinkat"
            (unlinkAtRaw (number directory) text (if isDir then #{const AT_REMOVEDIR} else 0))
          removed <- getFdStatus held
          require (linkCount removed == 0) "backing removed inode uncertain"
  mapM_ (remove root) tree
  checkRoot owner
  empty <- names deadline root
  require (null empty) "backing root not empty"
  bracket openTmp closeFd $ \parent -> do
    status <- getFdStatus parent
    require (pin status == parentPin) "backing parent replaced before root unlink"
    entry <- named parent name
    require (privateDirectory entry rootPin) "backing root replaced before unlink"
    leftNow deadline
    B.useAsCString name $ \text -> throwErrnoIfMinus1_ "backing root unlinkat" (unlinkAtRaw (number parent) text #{const AT_REMOVEDIR})
    held <- getFdStatus root
    require (linkCount held == 0) "backing root removal unconfirmed"
    absent <- try (named parent name) :: IO (Either IOException FileStatus)
    require (case absent of Left problem -> isDoesNotExistError problem; Right _ -> False) "backing root name reappeared"
  leftNow deadline
  closeFd root -- No retry/reuse after an ambiguous close.
  leftNow deadline

inspectFilterBacking :: FilterBackingOwner -> IO Bool
inspectFilterBacking owner@(Owner _ _ _ _ _ gate phase) = withMVar gate $ \_ -> do
  state <- readIORef phase
  case state of
    Released _ -> pure False
    Discarded -> pure False
    Retained -> pure False
    Retiring -> pure False
    _ -> do
      result <- try (snapshot owner) :: IO (Either IOException [Node])
      case result of Right _ -> pure True; Left _ -> writeIORef phase Retained >> pure False

discardUnstartedBacking :: FilterBackingOwner -> IO ()
discardUnstartedBacking owner@(Owner _ _ _ _ _ gate phase) = mask_ $ withMVar gate $ \_ -> do
  state <- readIORef phase
  case state of
    Discarded -> pure ()
    Fresh -> do
      writeIORef phase Retiring
      result <- try (removeTree owner) :: IO (Either SomeException ())
      case result of
        Right () -> writeIORef phase Discarded
        Left problem -> writeIORef phase Retained >> throwIO problem
    _ -> ioError (userError "backing may have been published to an engine; retain")

retireFilterBacking :: FilterBackingOwner -> EngineExitReceipt -> IO Bool
retireFilterBacking owner@(Owner _ _ _ _ deadline gate phase) receipt = mask_ $ withMVar gate $ \_ -> do
  state <- readIORef phase
  case state of
    Released engine -> pure (engineExitMatches engine receipt && engineNormalExit receipt)
    Discarded -> pure False
    Bound (Binding engine broker) -> do
      writeIORef phase Retiring
      let perform = do
            require (engineExitMatches engine receipt && engineNormalExit receipt) "backing process receipt not same normal engine"
            let (_,_,_,_,_,originalD,_) = engineExitFacts receipt
            require (originalD == deadlineAbsoluteNs deadline) "backing original deadline differs"
            leftNow deadline
            closed <- Broker.closeBroker broker
            require (closed == Broker.CloseConfirmed) "backing broker closure uncertain"
            removeTree owner
      result <- try perform :: IO (Either SomeException ())
      case result of
        Right () -> writeIORef phase (Released engine) >> pure True
        Left problem -> do
          writeIORef phase Retained
          case fromException problem :: Maybe SomeAsyncException of
            Just _ -> throwIO problem
            Nothing -> pure False
    _ -> pure False
