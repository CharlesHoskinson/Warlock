{-# LANGUAGE ForeignFunctionInterface #-}
#define _GNU_SOURCE
#include <spawn.h>
#include <signal.h>
#include <fcntl.h>
#include <sys/types.h>
-- PRIVATE SOURCE PROPOSAL. The caller must first retain Pending in the same
-- Owner that will own the child; this module is not a public FD issuer.
module Warlock.Capture.Process.Whitelist
 (SelectedFDPlan, trustedBorrowedPlan, childDestinations, spawnWhitelisted) where
import Control.Exception (SomeException, SomeAsyncException, fromException, mask_, onException, throwIO, try)
import Control.Monad (forM, forM_, unless, when)
import Data.IORef
import Data.List (nub)
import Foreign.C.String (CString, withCString)
import Foreign.C.Error (throwErrno, throwErrnoIfMinus1_)
import Foreign.C.Types (CInt(..), CShort(..))
import Foreign.Marshal.Alloc (allocaBytesAligned, mallocBytes, free)
import Foreign.Marshal.Array (withArray0)
import Foreign.Marshal.Utils (withMany)
import Foreign.Ptr (Ptr, nullPtr, castPtr, alignPtr)
import Foreign.Storable (peek)
import System.Posix.IO (closeFd)
import System.Posix.Files (getFdStatus, deviceID, fileID)
import System.Posix.Types (CPid(..), Fd(..))
import System.Process (ProcessHandle)
import System.Process.Internals (mkProcessHandle)
import Warlock.Capture.Process.Owner (Pending, pendingStart, pendingRecordFD, pendingIdentityFD, FDIdentity(..), pendingMarkFD, pendingRecordPid, pendingRecordHandle, pendingRecordIssue, NativePhase(..), pendingNativeRecord, pendingNativeMark, pendingNativeTakeFreeable)

data SelectedFDPlan = SelectedFDPlan [Fd]
-- This constructor belongs only in the trusted internal bridge. T3 must hold
-- every borrowed source lease across this call and the resulting publication.
trustedBorrowedPlan :: [Fd] -> Either String SelectedFDPlan
trustedBorrowedPlan fds
 | null fds || length fds > 256 = Left "selected count outside bounds"
 | any (\(Fd fd) -> fd < 0) fds = Left "negative source descriptor"
 | length (nub fds) /= length fds = Left "duplicate source descriptor"
 | otherwise = Right (SelectedFDPlan fds)
childDestinations :: SelectedFDPlan -> [Int]
childDestinations (SelectedFDPlan fds) = [3 .. length fds + 2]

foreign import ccall safe "posix_spawn" c_spawn :: Ptr CPid -> CString -> Ptr () -> Ptr () -> Ptr CString -> Ptr CString -> IO CInt
foreign import ccall unsafe "posix_spawn_file_actions_init" c_actionsInit :: Ptr () -> IO CInt
foreign import ccall unsafe "posix_spawn_file_actions_destroy" c_actionsDestroy :: Ptr () -> IO CInt
foreign import ccall unsafe "posix_spawn_file_actions_adddup2" c_dup2 :: Ptr () -> CInt -> CInt -> IO CInt
foreign import ccall unsafe "posix_spawn_file_actions_addclosefrom_np" c_closefrom :: Ptr () -> CInt -> IO CInt
foreign import ccall unsafe "posix_spawnattr_init" c_attrInit :: Ptr () -> IO CInt
foreign import ccall unsafe "posix_spawnattr_destroy" c_attrDestroy :: Ptr () -> IO CInt
foreign import ccall unsafe "posix_spawnattr_setpgroup" c_pgroup :: Ptr () -> CPid -> IO CInt
foreign import ccall unsafe "posix_spawnattr_setflags" c_flags :: Ptr () -> CShort -> IO CInt
foreign import ccall unsafe "sigemptyset" c_sigempty :: Ptr () -> IO CInt
foreign import ccall unsafe "sigaddset" c_sigadd :: Ptr () -> CInt -> IO CInt
foreign import ccall unsafe "posix_spawnattr_setsigmask" c_sigmask :: Ptr () -> Ptr () -> IO CInt
foreign import ccall unsafe "posix_spawnattr_setsigdefault" c_sigdefault :: Ptr () -> Ptr () -> IO CInt
foreign import ccall unsafe "getpgid" c_getpgid :: CInt -> IO CInt
foreign import ccall unsafe "fcntl" c_fcntlDup :: CInt -> CInt -> CInt -> IO CInt

-- POSIX spawn family returns an error number directly. fcntl alone uses -1.
checkCode :: String -> IO CInt -> IO ()
checkCode label action = do
 result <- action
 unless (result == 0) (ioError (userError (label ++ " returned " ++ show result)))

-- stdio source descriptors, like selected sources, must be held by the caller.
-- Spawn receives fixed argv/environment, never a shell. Success returns a
-- ProcessHandle ONLY after its PID was recorded. No waiter or signal is started.
-- Caller must publish the handle into the already-retained Owner, retain Pending
-- on every exception, and run its existing sole-reaper/group-before-wait path.
spawnWhitelisted :: Pending -> IO Bool -> (ProcessHandle -> IO ()) -> FilePath -> [String] -> [(String,String)] -> (Fd,Fd,Fd) -> SelectedFDPlan -> IO ProcessHandle
spawnWhitelisted pending deadlineValid publish exe argv environment (input,output,errorOutput) (SelectedFDPlan selected) = mask_ $ do
 firstAdmission <- pendingStart pending
 unless firstAdmission (ioError (userError "pending spawn already used"))
 let validEnvironment (key,value) = not (null key) && all (`notElem` ['=', '\0']) key && '\0' `notElem` value
 when (null exe || head exe /= '/' || '\0' `elem` exe || any (elem '\0') argv || not (all validEnvironment environment) || length (nub (map fst environment)) /= length environment) (ioError (userError "invalid fixed argv/environment"))
 let sources = [input,output,errorOutput] ++ selected
     floorFd = fromIntegral (length selected + 3)
     targets = [0,1,2] ++ map fromIntegral [3 .. length selected + 2]
 let allocate size alignment = do
      base <- mallocBytes (size + alignment - 1)
      let aligned = alignPtr base alignment
      pendingNativeRecord pending base aligned
      pure aligned
     freeReady = pendingNativeTakeFreeable pending >>= mapM_ free
 actions <- allocate #{size posix_spawn_file_actions_t} #{alignment posix_spawn_file_actions_t}
 attributes <- allocate #{size posix_spawnattr_t} #{alignment posix_spawnattr_t} `onException` freeReady
 final <- try $
  allocaBytesAligned #{size sigset_t} #{alignment sigset_t} $ \maskSet ->
   allocaBytesAligned #{size sigset_t} #{alignment sigset_t} $ \defaultSet -> do
     -- Scratch descriptors are acquired and closed independently; no source FD
     -- is modified. A failed close is recorded and never blindly retried.
     scratchRef <- newIORef []
     let closeScratch = do
          scratches <- readIORef scratchRef
          failures <- forM scratches $ \fd -> do
           pendingMarkFD pending fd False
           closed <- try (closeFd fd) :: IO (Either SomeException ())
           case closed of Left _ -> pure (); Right () -> pendingMarkFD pending fd True
           pure closed
          writeIORef scratchRef []
          pure [ex | Left ex <- failures]
     outcome <- try $ do
      scratches <- forM sources $ \(Fd fd) -> do
       dup <- c_fcntlDup fd #{const F_DUPFD_CLOEXEC} floorFd
       when (dup < 0) (throwErrno "F_DUPFD_CLOEXEC")
       let owned = Fd dup
       modifyIORef' scratchRef (owned:)
       pendingRecordFD pending owned
       descriptorStatus <- getFdStatus owned
       pendingIdentityFD pending owned (FDIdentity (toInteger (deviceID descriptorStatus)) (toInteger (fileID descriptorStatus)))
       pure dup
      checkCode "file-actions-init" (c_actionsInit actions)
      pendingNativeMark pending actions NativeInitialized
      actionResult <- try $ do
       forM_ (zip scratches targets) $ \(source,target) -> checkCode "adddup2" (c_dup2 actions source target)
       checkCode "addclosefrom" (c_closefrom actions floorFd)
       checkCode "attr-init" (c_attrInit attributes)
       pendingNativeMark pending attributes NativeInitialized
       attrResult <- try $ do
        checkCode "setpgroup" (c_pgroup attributes 0)
        throwErrnoIfMinus1_ "empty signal mask" (c_sigempty maskSet)
        throwErrnoIfMinus1_ "empty signal defaults" (c_sigempty defaultSet)
        forM_ [#{const SIGPIPE},#{const SIGINT},#{const SIGQUIT},#{const SIGHUP},#{const SIGTERM}] $ \sig -> throwErrnoIfMinus1_ "signal default" (c_sigadd defaultSet sig)
        checkCode "set signal mask" (c_sigmask attributes maskSet)
        checkCode "set signal defaults" (c_sigdefault attributes defaultSet)
        checkCode "setflags" (c_flags attributes (#{const POSIX_SPAWN_SETPGROUP} + #{const POSIX_SPAWN_SETSIGMASK} + #{const POSIX_SPAWN_SETSIGDEF}))
        withCString exe $ \cExe -> withMany withCString (exe:argv) $ \argStrings ->
         withMany withCString (map (\(key,value) -> key ++ "=" ++ value) environment) $ \envStrings -> withArray0 nullPtr argStrings $ \argp ->
          withArray0 nullPtr envStrings $ \envp -> allocaBytesAligned #{size pid_t} #{alignment pid_t} $ \pidStorage -> do
           let pidPtr = castPtr pidStorage :: Ptr CPid
           allowed <- deadlineValid
           unless allowed (ioError (userError "selected admission deadline expired"))
           checkCode "posix_spawn" (c_spawn pidPtr cExe actions attributes argp envp)
           pid <- peek pidPtr
           when (pid <= 0) (pendingRecordIssue pending "nonpositive-spawned-pid" >> ioError (userError "nonpositive spawned PID"))
           recorded <- pendingRecordPid pending pid
           unless recorded (ioError (userError "pending PID already recorded"))
           group <- c_getpgid (fromIntegral pid)
           unless (group == fromIntegral pid) (ioError (userError "spawned group unconfirmed"))
           ph <- mkProcessHandle pid False
           stored <- pendingRecordHandle pending ph
           unless stored (ioError (userError "pending handle already recorded"))
           publish ph
           pure ph
       attrClose <- c_attrDestroy attributes
       pendingNativeMark pending attributes (if attrClose == 0 then NativeDestroyed else NativeUncertain)
       when (attrClose /= 0) (pendingRecordIssue pending ("attr-destroy:" ++ show attrClose))
       case (attrResult :: Either SomeException ProcessHandle) of
        Left ex -> throwIO ex
        Right ph | attrClose == 0 -> pure ph
                 | otherwise -> ioError (userError "attribute destruction failed")
      actionClose <- c_actionsDestroy actions
      pendingNativeMark pending actions (if actionClose == 0 then NativeDestroyed else NativeUncertain)
      when (actionClose /= 0) (pendingRecordIssue pending ("actions-destroy:" ++ show actionClose))
      case (actionResult :: Either SomeException ProcessHandle) of
       Left ex -> throwIO ex
       Right ph | actionClose == 0 -> pure ph
                | otherwise -> ioError (userError "file-actions destruction failed")
     closeFailures <- closeScratch
     let original = outcome :: Either SomeException ProcessHandle
         asyncs = [ex | ex <- closeFailures, Just _ <- [fromException ex :: Maybe SomeAsyncException]]
     case original of
      Left ex -> case (fromException ex :: Maybe SomeAsyncException, asyncs) of
       (Just _,_) -> throwIO ex
       (Nothing,first:_) -> throwIO first
       (Nothing,[]) -> throwIO ex
      Right ph -> case asyncs of
       first:_ -> throwIO first
       [] -> case closeFailures of [] -> pure ph; first:_ -> throwIO first

 freeReady
 either throwIO pure (final :: Either SomeException ProcessHandle)
