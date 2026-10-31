{-# LANGUAGE ForeignFunctionInterface #-}
{-# LANGUAGE RankNTypes #-}
{-# LANGUAGE ScopedTypeVariables #-}
-- Private host-writer custody. A guard lease is not native execution authority.
module Warlock.Native.Cancellation.HostGuard
 (HostGuard, GuardLease, GuardError(..), GuardPhase(..), HandleState(..), FailureOrigin(..), GuardStatus(..),
  newHostGuard, offerNamespace, withHostGuard, withNamespace, guardGeneration, guardNamespaceIdentity,
  guardStatus, guardFailures, retireHostGuard) where
#define _GNU_SOURCE 1
#include <sys/types.h>
#include <sys/stat.h>
#include <sys/file.h>
#include <fcntl.h>
#include <unistd.h>
import Control.Concurrent (ThreadId,myThreadId)
import Control.Concurrent.MVar (MVar,newMVar,tryTakeMVar,putMVar)
import Control.Exception (SomeException,SomeAsyncException,fromException,mask,try,throwIO,finally)
import Data.Bits ((.&.),(.|.))
import Data.IORef (IORef,newIORef,readIORef,atomicModifyIORef')
import Data.Word (Word32,Word64)
import Foreign.C.Error (getErrno,eAGAIN,eWOULDBLOCK,throwErrno,throwErrnoIfMinus1,throwErrnoIfMinus1_)
import Foreign.C.String (CString,withCString)
import Foreign.C.Types (CInt(..))
import Foreign.Marshal.Alloc (allocaBytesAligned)
import Foreign.Ptr (Ptr)
import Foreign.Storable (peekByteOff)
import System.Posix.Files (FileStatus,getFdStatus,isDirectory,isRegularFile,fileMode,fileOwner,linkCount,deviceID,fileID)
import System.Posix.Types (Fd(..),FileMode)
import System.Posix.User (getEffectiveUserID)
import Warlock.Protocol.Identity (Counter,addCounter)

foreign import ccall safe "openat" c_openat :: CInt -> CString -> CInt -> #{type mode_t} -> IO CInt
foreign import ccall safe "flock" c_flock :: CInt -> CInt -> IO CInt
foreign import ccall safe "fstatat" c_fstatat :: CInt -> CString -> Ptr () -> CInt -> IO CInt
foreign import ccall safe "close" c_close :: CInt -> IO CInt

data GuardError = Busy | WrongThread | Unavailable | InvalidNamespace | InvalidGuard | IdentityChanged | Exhausted | OperationFailed | GuardUncertain deriving (Eq,Show)
data GuardPhase = Vacant | Ready | Quarantined | Retired deriving (Eq,Show)
data Hold = Owned !Fd | Closed | Uncertain !Fd
data HandleState = Absent | Retained | ConfirmedClosed | CloseUncertain deriving (Eq,Show)
data LockState = Unlocked | Acquiring | Locked | Releasing | LockUnknown deriving (Eq)
data FailureOrigin = OperationFailure | UnlockFailure | LockCloseFailure | NamespaceCloseFailure deriving (Eq,Show)
data State = State !GuardPhase !(Maybe Hold) !(Maybe Hold) !LockState !Counter ![(FailureOrigin,SomeException)]
data HostGuard = HostGuard !ThreadId !(IORef State) !(MVar ())
data GuardLease scope = GuardLease !HostGuard !Counter !(Integer,Integer)
data GuardStatus = GuardStatus {guardPhase :: !GuardPhase, namespaceState :: !HandleState,
 lockHandleState :: !HandleState, lockHeld :: !Bool, generation :: !Counter,
 failureOrigins :: ![FailureOrigin]} deriving (Eq,Show)

newHostGuard :: Counter -> IO HostGuard
newHostGuard initial = HostGuard <$> myThreadId <*> newIORef (State Vacant Nothing Nothing Unlocked initial []) <*> newMVar ()
-- False leaves the offered descriptor with its caller. True publishes custody
-- before any validation or interruptible work; even an invalid FD stays owned.
offerNamespace :: HostGuard -> Fd -> IO Bool
offerNamespace (HostGuard _ state _) fd = mask $ \_ -> atomicModifyIORef' state $ \old@(State phase _ _ _ n failures) ->
 if phase == Vacant then (State Ready (Just (Owned fd)) Nothing Unlocked n failures,True) else (old,False)
guardGeneration :: GuardLease scope -> Counter
guardGeneration (GuardLease _ n _) = n
guardNamespaceIdentity :: GuardLease scope -> (Integer,Integer)
guardNamespaceIdentity (GuardLease _ _ identity) = identity
-- A borrowed namespace may be used only inside the current owning-thread
-- guard callback. Callers must publish any newly opened child FD to its own
-- preallocated owner before restoring exceptions; they must never close this FD.
withNamespace :: GuardLease scope -> (Fd -> IO a) -> IO (Either GuardError a)
withNamespace (GuardLease (HostGuard owner state _) expected _) action = do
 thread <- myThreadId
 State phase root _ held n _ <- readIORef state
 if thread /= owner then pure (Left WrongThread) else case (phase,root,held) of
  (Ready,Just (Owned directory),Locked) | n == expected -> Right <$> action directory
  _ -> pure (Left Unavailable)
guardStatus :: HostGuard -> IO GuardStatus
guardStatus (HostGuard _ state _) = do
 State phase root file held n failures <- readIORef state
 pure (GuardStatus phase (view root) (view file) (held /= Unlocked) n (map fst failures))
 where
  view Nothing = Absent
  view (Just (Owned _)) = Retained
  view (Just Closed) = ConfirmedClosed
  view (Just (Uncertain _)) = CloseUncertain
guardFailures :: HostGuard -> IO [(FailureOrigin,SomeException)]
guardFailures (HostGuard _ state _) = do State _ _ _ _ _ failures <- readIORef state; pure failures
change :: IORef State -> (State -> State) -> IO ()
change state f = atomicModifyIORef' state (\s -> (f s,()))
identityOf :: FileStatus -> (Integer,Integer)
identityOf status = (toInteger (deviceID status),toInteger (fileID status))
privateMode :: FileStatus -> FileMode -> Bool
privateMode status wanted = fileMode status .&. 0o7777 == wanted
isAsync :: SomeException -> Bool
isAsync err = case fromException err :: Maybe SomeAsyncException of Just _ -> True; Nothing -> False
remember :: IORef State -> FailureOrigin -> SomeException -> IO ()
remember state origin err = change state $ \(State _ root file held n failures) ->
 State Quarantined root file held n (take 8 ((origin,err):failures))

-- Called only while the nonblocking gate is owned and async exceptions masked.
-- No user callback runs here. The fixed-name entry must still identify the
-- same actual open file that the kernel lock will protect.
prepare :: HostGuard -> IO (Either GuardError (GuardLease scope))
prepare guard@(HostGuard _ state _) = do
 State phase root file _ n _ <- readIORef state
 case (phase,root) of
  (Ready,Just (Owned directory@(Fd dir))) -> do
   uid <- getEffectiveUserID
   rootStat <- getFdStatus directory
   if not (isDirectory rootStat) || fileOwner rootStat /= uid || not (privateMode rootStat 0o700)
    then pure (Left InvalidNamespace)
    else case addCounter n 1 of
     Left _ -> pure (Left Exhausted)
     Right next -> do
      selected <- case file of
       Nothing -> do
        raw <- withCString "host-writer.lock" $ \name -> throwErrnoIfMinus1 "openat host guard" (c_openat dir name (#{const O_RDWR} .|. #{const O_CREAT} .|. #{const O_NOFOLLOW} .|. #{const O_CLOEXEC}) 0o600)
        let fd = Fd raw
        change state $ \(State p r _ held counter failures) -> State p r (Just (Owned fd)) held counter failures
        pure (Just fd)
       Just (Owned fd) -> pure (Just fd)
       _ -> pure Nothing
      case selected of
       Nothing -> pure (Left Unavailable)
       Just descriptor@(Fd raw) -> do
        status <- getFdStatus descriptor
        if not (isRegularFile status) || fileOwner status /= uid || linkCount status /= 1 || not (privateMode status 0o600)
         then pure (Left InvalidGuard)
         else do
          change state $ \(State p r f _ counter failures) -> State p r f Acquiring counter failures
          result <- c_flock raw (#{const LOCK_EX} .|. #{const LOCK_NB})
          if result /= 0 then do
           errno <- getErrno
           if errno == eAGAIN || errno == eWOULDBLOCK
            then do
             change state $ \(State p r f _ counter failures) -> State p r f Unlocked counter failures
             pure (Left Busy)
            else throwErrno "flock host guard"
           else do
            change state $ \(State p r f _ counter failures) -> State p r f Locked counter failures
            same <- withCString "host-writer.lock" $ \name -> allocaBytesAligned #{size struct stat} #{alignment struct stat} $ \buffer -> do
             throwErrnoIfMinus1_ "fstatat host guard" (c_fstatat dir name buffer #{const AT_SYMLINK_NOFOLLOW})
             dev <- #{peek struct stat, st_dev} buffer :: IO #{type dev_t}
             ino <- #{peek struct stat, st_ino} buffer :: IO #{type ino_t}
             mode <- #{peek struct stat, st_mode} buffer :: IO #{type mode_t}
             owner <- #{peek struct stat, st_uid} buffer :: IO #{type uid_t}
             links <- #{peek struct stat, st_nlink} buffer :: IO #{type nlink_t}
             pure ((toInteger dev,toInteger ino) == identityOf status && mode .&. #{const S_IFMT} == #{const S_IFREG} && mode .&. 0o7777 == 0o600 && toInteger owner == toInteger uid && links == 1)
            if not same then pure (Left IdentityChanged) else do
             change state $ \(State p r f held _ failures) -> State p r f held next failures
             pure (Right (GuardLease guard next (identityOf rootStat)))
  _ -> pure (Left Unavailable)

unlock :: HostGuard -> IO (Either SomeException ())
unlock (HostGuard _ state _) = do
 State _ _ file held _ _ <- readIORef state
 case (file,held) of
  (Just (Owned (Fd raw)),phase) | phase /= Unlocked -> do
   change state $ \(State p r f _ n failures) -> State p r f Releasing n failures
   outcome <- try (throwErrnoIfMinus1_ "unlock host guard" (c_flock raw #{const LOCK_UN}))
   case outcome of
    Right () -> change state $ \(State p r f _ n failures) -> State p r f Unlocked n failures
    Left err -> do
     remember state UnlockFailure err
     change state $ \(State p r f _ n failures) -> State p r f LockUnknown n failures
   pure outcome
  _ -> pure (Right ())

withHostGuard :: forall a. HostGuard -> (forall scope. GuardLease scope -> IO a) -> IO (Either GuardError a)
withHostGuard guard@(HostGuard owner state gate) action = mask $ \restore -> do
 thread <- myThreadId
 if thread /= owner then pure (Left WrongThread) else do
  acquired <- tryTakeMVar gate
  case acquired of
   Nothing -> pure (Left Busy)
   Just () -> (do
    outcome <- try (do
     prepared <- prepare guard
     case prepared of Left err -> pure (Left err); Right lease -> Right <$> restore (action lease)) :: IO (Either SomeException (Either GuardError a))
    case outcome of Left err -> remember state OperationFailure err; Right _ -> pure ()
    released <- unlock guard
    case outcome of
     Left err | isAsync err -> throwIO err
     _ -> case released of
      Left err | isAsync err -> throwIO err
      Left _ -> pure (Left GuardUncertain)
      Right () -> case outcome of Left _ -> pure (Left OperationFailed); Right value -> pure value
    ) `finally` putMVar gate ()

-- Retirement cannot run during a borrowed guard. Each actual close is claimed
-- once under the gate; every failed close retains its exact FD as uncertain.
retireHostGuard :: HostGuard -> IO (Either GuardError GuardStatus)
retireHostGuard guard@(HostGuard _ state gate) = mask $ \_ -> do
 acquired <- tryTakeMVar gate
 case acquired of
  Nothing -> pure (Left Busy)
  Just () -> (do
   released <- unlock guard
   closeOne False
   closeOne True
   change state $ \(State _ root file held n failures) -> State Retired root file held n failures
   status <- guardStatus guard
   case released of
    Left err | isAsync err -> throwIO err
    Left _ -> pure (Left GuardUncertain)
    Right () | namespaceState status == CloseUncertain || lockHandleState status == CloseUncertain -> pure (Left GuardUncertain)
    Right () -> pure (Right status)
   ) `finally` putMVar gate ()
 where
  closeOne namespace = do
   selected <- atomicModifyIORef' state $ \old@(State p root file held n failures) ->
    let candidate = if namespace then root else file in case candidate of
     Just (Owned fd) -> (if namespace then State p (Just (Uncertain fd)) file held n failures else State p root (Just (Uncertain fd)) held n failures,Just fd)
     _ -> (old,Nothing)
   case selected of
    Nothing -> pure ()
    Just (Fd raw) -> do
     outcome <- try (throwErrnoIfMinus1_ "close host guard" (c_close raw)) :: IO (Either SomeException ())
     case outcome of
      Left err -> remember state (if namespace then NamespaceCloseFailure else LockCloseFailure) err
      Right () -> change state $ \(State p root file held n failures) ->
       if namespace then State p (Just Closed) file held n failures else State p root (Just Closed) held n failures
