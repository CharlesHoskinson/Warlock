{-# LANGUAGE CPP #-}
{-# LANGUAGE ScopedTypeVariables #-}
{-# LANGUAGE ForeignFunctionInterface #-}
-- Host-side lifetime exclusivity, distinct from the adapter's writer.lock.
-- This module grants neither journal eligibility nor native mutation authority.
module Warlock.Native.Cancellation.LifetimeOwner
 (LifetimeOwner,OwnerError(..),OwnerPhase(..),OwnerStatus(..),
  newLifetimeOwner,acquireLifetimeOwner,validateLifetimeOwner,retireLifetimeOwner,ownerStatus
#ifdef SLOTSTORE_TESTING
  ,newLifetimeOwnerWithHookForTest
#endif
 ) where
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
import Data.Word (Word32,Word64)
import Data.IORef (IORef,newIORef,readIORef,atomicModifyIORef')
import Foreign.C.Error (getErrno,eAGAIN,eWOULDBLOCK,throwErrno,throwErrnoIfMinus1,throwErrnoIfMinus1_)
import Foreign.C.String (CString,withCString)
import Foreign.C.Types (CInt(..))
import Foreign.Marshal.Alloc (allocaBytesAligned)
import Foreign.Ptr (Ptr)
import Foreign.Storable (peekByteOff)
import System.Posix.Files (FileStatus,getFdStatus,isDirectory,isRegularFile,fileMode,fileOwner,linkCount,deviceID,fileID)
import System.Posix.Types (Fd(..),FileMode)
import System.Posix.User (getEffectiveUserID)

foreign import ccall safe "openat" c_openat :: CInt -> CString -> CInt -> #{type mode_t} -> IO CInt
foreign import ccall safe "flock" c_flock :: CInt -> CInt -> IO CInt
foreign import ccall safe "fstatat" c_fstatat :: CInt -> CString -> Ptr () -> CInt -> IO CInt
foreign import ccall safe "close" c_close :: CInt -> IO CInt

data OwnerError = Busy | WrongThread | NotHeld | Unavailable | InvalidNamespace | InvalidLock | IdentityChanged | OperationFailed | CloseUncertain deriving (Eq,Show)
data OwnerPhase = Vacant | Open | Held | Quarantined | Retired deriving (Eq,Show)
data Handle = Owned !Fd | Uncertain !Fd | Closed
-- The namespace is borrowed, never closed or retained as a numeric alias.
data State = State !OwnerPhase !(Maybe Handle) !(Maybe (Integer,Integer)) ![SomeException]
data LifetimeOwner = LifetimeOwner !ThreadId !(IORef State) !(MVar ()) !(String -> IO ())
data OwnerStatus = OwnerStatus {ownerPhase :: !OwnerPhase,ownerDescriptorRetained :: !Bool,ownerCloseUncertain :: !Bool,ownerExceptionCount :: !Int} deriving (Eq,Show)

newLifetimeOwner :: IO LifetimeOwner
newLifetimeOwner = allocate (const (pure ()))
allocate :: (String -> IO ()) -> IO LifetimeOwner
allocate hook = LifetimeOwner <$> myThreadId <*> newIORef (State Vacant Nothing Nothing []) <*> newMVar () <*> pure hook
#ifdef SLOTSTORE_TESTING
newLifetimeOwnerWithHookForTest :: (String -> IO ()) -> IO LifetimeOwner
newLifetimeOwnerWithHookForTest = allocate
#endif
ownerStatus :: LifetimeOwner -> IO OwnerStatus
ownerStatus (LifetimeOwner _ state _ _) = do
 State phase handle _ errors <- readIORef state
 pure (OwnerStatus phase (case handle of Just (Owned _) -> True; Just (Uncertain _) -> True; _ -> False) (case handle of Just (Uncertain _) -> True; _ -> False) (length errors))
change :: IORef State -> (State -> State) -> IO ()
change state f = atomicModifyIORef' state (\old -> (f old,()))
isAsync :: SomeException -> Bool
isAsync err = case fromException err :: Maybe SomeAsyncException of Just _ -> True; Nothing -> False
quarantine :: IORef State -> IO ()
quarantine state = change state (\(State _ handle identity errors) -> State Quarantined handle identity errors)
withActor :: forall a. LifetimeOwner -> IO (Either OwnerError a) -> IO (Either OwnerError a)
withActor (LifetimeOwner thread state gate _) action = mask $ \_ -> do
 current <- myThreadId
 if current/=thread then pure (Left WrongThread) else do
  acquired <- tryTakeMVar gate
  case acquired of
   Nothing -> pure (Left Busy)
   Just () -> (do
    outcome <- try action :: IO (Either SomeException (Either OwnerError a))
    case outcome of
     Right value -> pure value
     Left err -> do
      change state (\(State _ handle identity errors) -> State Quarantined handle identity (take 8 (err:errors)))
      if isAsync err then throwIO err else pure (Left OperationFailed)
    ) `finally` putMVar gate ()
identityOf :: FileStatus -> (Integer,Integer)
identityOf status = (toInteger (deviceID status),toInteger (fileID status))
privateMode :: FileStatus -> FileMode -> Bool
privateMode status wanted = fileMode status .&. 0o7777 == wanted
namespace :: Fd -> IO (Either OwnerError (Integer,Integer))
namespace directory = do
 status <- getFdStatus directory
 uid <- getEffectiveUserID
 pure (if isDirectory status && fileOwner status==uid && privateMode status 0o700 then Right (identityOf status) else Left InvalidNamespace)
-- Validate both held metadata and the exact non-followed name. The caller's
-- namespace identity must remain the one observed before opening our lock.
validateHandle :: Fd -> Fd -> IO (Either OwnerError ())
validateHandle (Fd parent) descriptor = do
 status <- getFdStatus descriptor
 uid <- getEffectiveUserID
 if not (isRegularFile status && fileOwner status==uid && linkCount status==1 && privateMode status 0o600) then pure (Left InvalidLock) else
  withCString "host-owner.lock" $ \name -> allocaBytesAligned #{size struct stat} #{alignment struct stat} $ \buffer -> do
   throwErrnoIfMinus1_ "fstatat lifetime owner" (c_fstatat parent name buffer #{const AT_SYMLINK_NOFOLLOW})
   dev <- #{peek struct stat, st_dev} buffer :: IO #{type dev_t}
   ino <- #{peek struct stat, st_ino} buffer :: IO #{type ino_t}
   mode <- #{peek struct stat, st_mode} buffer :: IO #{type mode_t}
   owner <- #{peek struct stat, st_uid} buffer :: IO #{type uid_t}
   links <- #{peek struct stat, st_nlink} buffer :: IO #{type nlink_t}
   pure (if (toInteger dev,toInteger ino)==identityOf status && mode .&. #{const S_IFMT} == #{const S_IFREG} && mode .&. 0o7777==0o600 && toInteger owner==toInteger uid && links==1 then Right () else Left IdentityChanged)

acquireLifetimeOwner :: LifetimeOwner -> Fd -> IO (Either OwnerError ())
acquireLifetimeOwner owner@(LifetimeOwner _ state _ hook) directory@(Fd parent) = withActor owner $ do
 State phase handle expected errors <- readIORef state
 if phase `elem` [Quarantined,Retired] then pure (Left Unavailable) else do
  current <- namespace directory
  case current of
   Left err -> quarantine state >> pure (Left err)
   Right identity | maybe False (/=identity) expected -> quarantine state >> pure (Left IdentityChanged)
   Right identity -> do
    selected <- case handle of
     Nothing -> do
      raw <- withCString "host-owner.lock" $ \name -> throwErrnoIfMinus1 "openat lifetime owner" (c_openat parent name (#{const O_RDWR} .|. #{const O_CREAT} .|. #{const O_NONBLOCK} .|. #{const O_NOFOLLOW} .|. #{const O_CLOEXEC}) 0o600)
      let fd=Fd raw
      change state (\_ -> State Open (Just (Owned fd)) (Just identity) errors)
      hook "opened"
      pure (Just fd)
     Just (Owned fd) -> pure (Just fd)
     _ -> pure Nothing
    case selected of
     Nothing -> pure (Left Unavailable)
     Just descriptor@(Fd raw) -> do
      valid <- validateHandle directory descriptor
      case valid of
       Left err -> quarantine state >> pure (Left err)
       Right () | phase==Held -> pure (Right ())
       Right () -> do
        result <- c_flock raw (#{const LOCK_EX} .|. #{const LOCK_NB})
        if result/=0 then do
         errno <- getErrno
         if errno==eAGAIN || errno==eWOULDBLOCK then pure (Left Busy) else throwErrno "flock lifetime owner"
        else do
         change state (\(State _ file root failures) -> State Held file root failures)
         hook "locked"
         checked <- validateHandle directory descriptor
         case checked of Left _ -> quarantine state; Right () -> pure ()
         pure checked

validateLifetimeOwner :: LifetimeOwner -> Fd -> IO (Either OwnerError ())
validateLifetimeOwner owner@(LifetimeOwner _ state _ _) directory = withActor owner $ do
 State phase handle expected _ <- readIORef state
 case (phase,handle,expected) of
  (Held,Just (Owned descriptor),Just identity) -> do
   root <- namespace directory
   checked <- case root of Right current | current==identity -> validateHandle directory descriptor; Left err -> pure (Left err); _ -> pure (Left IdentityChanged)
   case checked of Left _ -> quarantine state; Right () -> pure ()
   pure checked
  (Quarantined,_,_) -> pure (Left Unavailable)
  (Retired,_,_) -> pure (Left Unavailable)
  _ -> pure (Left NotHeld)

-- Claim the close before attempting it. Any failure, including a test hook
-- after successful kernel close, retains uncertainty and never retries the FD.
retireLifetimeOwner :: LifetimeOwner -> IO (Either OwnerError ())
retireLifetimeOwner owner@(LifetimeOwner _ state _ hook) = withActor owner $ do
 selected <- atomicModifyIORef' state $ \old@(State _ handle identity errors) -> case handle of
  Just (Owned fd) -> (State Retired (Just (Uncertain fd)) identity errors,Just fd)
  _ -> (old,Nothing)
 case selected of
  Nothing -> do
   State _ handle _ _ <- readIORef state
   case handle of
    Just (Uncertain _) -> pure (Left CloseUncertain)
    _ -> change state (\(State _ file root errors) -> State Retired file root errors) >> pure (Right ())
  Just (Fd raw) -> do
   hook "closing"
   throwErrnoIfMinus1_ "close lifetime owner" (c_close raw)
   hook "closed"
   change state (\(State _ _ identity errors) -> State Retired (Just Closed) identity errors)
   pure (Right ())
