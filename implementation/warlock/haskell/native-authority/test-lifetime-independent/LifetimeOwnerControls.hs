{-# LANGUAGE OverloadedStrings #-}
module Main (main) where

import Control.Concurrent (forkIO,newEmptyMVar,putMVar,takeMVar)
import Control.Exception (AsyncException(ThreadKilled),IOException,SomeException,bracket,fromException,throwIO,try)
import Control.Monad (forM,unless,void)
import Data.IORef (newIORef,readIORef,writeIORef)
import Data.Maybe (catMaybes)
import System.Directory (createDirectory,listDirectory,renameFile)
import System.Environment (getArgs)
import System.FilePath ((</>))
import System.Posix.Files (FileStatus,createLink,createSymbolicLink,deviceID,fileID,getFdStatus,getFileStatus,setFileMode)
import System.Posix.IO (OpenMode(ReadOnly,ReadWrite),closeFd,defaultFileFlags,openFd)
import System.Posix.Types (Fd(..))
import Text.Read (readMaybe)
import qualified Warlock.Native.Cancellation.HostGuard as G
import qualified Warlock.Native.Cancellation.LifetimeOwner as L
import Warlock.Protocol.Identity (parseCounter)

check :: String -> Bool -> IO ()
check label value = unless value (ioError (userError label))
right :: Show e => Either e a -> IO a
right = either (ioError . userError . show) pure
identity :: Fd -> IO (Integer,Integer)
identity fd = do
 s <- getFdStatus fd
 pure (toInteger (deviceID s),toInteger (fileID s))
privateDir :: FilePath -> IO ()
privateDir path = createDirectory path >> setFileMode path 0o700
withDir :: FilePath -> (Fd -> IO a) -> IO a
withDir path = bracket (openFd path ReadOnly defaultFileFlags) closeFd
lockFile :: FilePath -> IO ()
lockFile path = writeFile path "" >> setFileMode path 0o600

-- Inspect only proc entries referring to this fixture's uniquely identified
-- lock inode. Never close any enumerated descriptor. The normal path has one
-- such descriptor; a transient proc-directory entry may disappear.
findLockFd :: FilePath -> IO Fd
findLockFd path = do
 s <- getFileStatus path
 names <- listDirectory "/proc/self/fd"
 check "bounded fd observation" (length names <= 4096)
 found <- forM names $ \name -> case readMaybe name of
  Nothing -> pure Nothing
  Just n -> do
   let fd = Fd n
   observed <- try (getFdStatus fd) :: IO (Either IOException FileStatus)
   pure $ case observed of
    Right x | deviceID x == deviceID s && fileID x == fileID s -> Just fd
    _ -> Nothing
 case catMaybes found of
  [fd] -> pure fd
  _ -> ioError (userError "expected exactly one owned fixture lock descriptor")

ordinary :: FilePath -> IO ()
ordinary path = withDir path $ \parent -> do
 before <- identity parent
 a <- L.newLifetimeOwner
 b <- L.newLifetimeOwner
 L.acquireLifetimeOwner a parent >>= right
 L.acquireLifetimeOwner a parent >>= right
 L.validateLifetimeOwner a parent >>= right
 check "independent owner kernel contention" . (== Left L.Busy) =<< L.acquireLifetimeOwner b parent
 zero <- right (parseCounter True "0")
 guard <- G.newHostGuard zero
 fd <- openFd path ReadOnly defaultFileFlags
 accepted <- G.offerNamespace guard fd
 unless accepted (closeFd fd >> ioError (userError "guard did not adopt its own namespace"))
 G.withHostGuard guard (\_ -> pure ()) >>= right
 check "writer unlock preserves lifetime exclusivity" . (== Left L.Busy) =<< L.acquireLifetimeOwner b parent
 _ <- G.retireHostGuard guard >>= right
 L.retireLifetimeOwner a >>= right
 L.acquireLifetimeOwner b parent >>= right
 L.validateLifetimeOwner b parent >>= right
 L.retireLifetimeOwner b >>= right
 L.retireLifetimeOwner b >>= right
 after <- identity parent
 check "borrowed parent remains open and same inode" (before == after)

replacement :: FilePath -> IO ()
replacement path = withDir path $ \parent -> do
 owner <- L.newLifetimeOwner
 L.acquireLifetimeOwner owner parent >>= right
 let original = path </> "host-owner.lock"
 renameFile original (path </> "old-owner")
 lockFile original
 replacementId <- getFileStatus original
 result <- L.validateLifetimeOwner owner parent
 check "replacement rejected" (result == Left L.IdentityChanged)
 status <- L.ownerStatus owner
 check "old descriptor quarantined" (L.ownerPhase status == L.Quarantined && L.ownerDescriptorRetained status)
 L.retireLifetimeOwner owner >>= right
 after <- getFileStatus original
 check "replacement untouched" (deviceID after == deviceID replacementId && fileID after == fileID replacementId)

refused :: FilePath -> String -> (FilePath -> IO ()) -> IO ()
refused root label setup = do
 let path = root </> label
 privateDir path
 setup (path </> "host-owner.lock")
 withDir path $ \parent -> do
  owner <- L.newLifetimeOwner
  result <- L.acquireLifetimeOwner owner parent
  check (label ++ " refuses") (case result of Left _ -> True; Right () -> False)
  L.retireLifetimeOwner owner >>= right
  void (identity parent)

invalidCases :: FilePath -> IO ()
invalidCases root = do
 refused root "mode" $ \p -> lockFile p >> setFileMode p 0o644
 refused root "directory" privateDir
 refused root "symlink" $ \p -> createSymbolicLink "missing" p
 refused root "hardlink" $ \p -> lockFile p >> createLink p (p ++ ".other")
 let path = root </> "parent-mode"
 privateDir path
 setFileMode path 0o755
 withDir path $ \parent -> do
  owner <- L.newLifetimeOwner
  check "invalid parent" . (== Left L.InvalidNamespace) =<< L.acquireLifetimeOwner owner parent
  L.retireLifetimeOwner owner >>= right

threadAndReentry :: FilePath -> IO ()
threadAndReentry path = withDir path $ \parent -> do
 slot <- newIORef Nothing
 seen <- newIORef False
 let hook stage = if stage /= "opened" then pure () else do
      candidate <- readIORef slot
      case candidate of
       Nothing -> ioError (userError "missing owner in hook")
       Just owner -> do
        x <- L.retireLifetimeOwner owner
        y <- L.validateLifetimeOwner owner parent
        writeIORef seen (x == Left L.Busy && y == Left L.Busy)
 owner <- L.newLifetimeOwnerWithHookForTest hook
 writeIORef slot (Just owner)
 L.acquireLifetimeOwner owner parent >>= right
 check "reentrant calls refused" =<< readIORef seen
 result <- newEmptyMVar
 _ <- forkIO (do
  x <- L.validateLifetimeOwner owner parent
  y <- L.retireLifetimeOwner owner
  putMVar result (x,y))
 pair <- takeMVar result
 check "wrong thread validate and retirement refused" (pair == (Left L.WrongThread,Left L.WrongThread))
 L.validateLifetimeOwner owner parent >>= right
 L.retireLifetimeOwner owner >>= right

interruptAt :: FilePath -> String -> IO ()
interruptAt path stage = withDir path $ \parent -> do
 owner <- L.newLifetimeOwnerWithHookForTest (\s -> if s == stage then throwIO ThreadKilled else pure ())
 attempt <- try (L.acquireLifetimeOwner owner parent) :: IO (Either SomeException (Either L.OwnerError ()))
 check (stage ++ " async propagated") (case attempt of
  Left e -> case fromException e of Just ThreadKilled -> True; _ -> False
  Right _ -> False)
 status <- L.ownerStatus owner
 check (stage ++ " retained") (L.ownerPhase status == L.Quarantined && L.ownerDescriptorRetained status && L.ownerExceptionCount status > 0)
 L.retireLifetimeOwner owner >>= right
 void (identity parent)

closedFault :: FilePath -> IO ()
closedFault path = withDir path $ \parent -> do
 captured <- newIORef Nothing
 owner <- L.newLifetimeOwnerWithHookForTest $ \stage -> case stage of
  "opened" -> findLockFd (path </> "host-owner.lock") >>= writeIORef captured . Just
  "closed" -> ioError (userError "injected post-close failure")
  _ -> pure ()
 L.acquireLifetimeOwner owner parent >>= right
 old <- readIORef captured >>= maybe (ioError (userError "no captured fd")) pure
 first <- L.retireLifetimeOwner owner
 check "post-close fault reported" (first == Left L.OperationFailed)
 status <- L.ownerStatus owner
 check "post-close uncertainty retained" (L.ownerCloseUncertain status && L.ownerExceptionCount status > 0)
 let sentinelPath = path </> "sentinel"
 lockFile sentinelPath
 bracket (openFd sentinelPath ReadWrite defaultFileFlags) closeFd $ \sentinel -> do
  check "actual closed descriptor number reused by owned sentinel" (sentinel == old)
  before <- identity sentinel
  again <- L.retireLifetimeOwner owner
  check "uncertain number not retried" (again == Left L.CloseUncertain)
  after <- identity sentinel
  check "sentinel still open and same inode" (before == after)
 void (identity parent)

closingFault :: FilePath -> IO ()
closingFault path = withDir path $ \parent -> do
 owner <- L.newLifetimeOwnerWithHookForTest (\s -> if s == "closing" then ioError (userError "injected pre-close failure") else pure ())
 L.acquireLifetimeOwner owner parent >>= right
 first <- L.retireLifetimeOwner owner
 check "pre-close fault reported" (first == Left L.OperationFailed)
 status <- L.ownerStatus owner
 check "pre-close unknown retained" (L.ownerCloseUncertain status && L.ownerDescriptorRetained status)
 check "pre-close number not retried" . (== Left L.CloseUncertain) =<< L.retireLifetimeOwner owner
 -- Intentionally retained: no blind retry after an uncertain close. Process
 -- exit releases this fixture FD; this is not a normal-retirement proof.
 void (identity parent)

separateFaults :: FilePath -> IO ()
separateFaults path = withDir path $ \parent -> do
 owner <- L.newLifetimeOwnerWithHookForTest $ \stage -> case stage of
  "opened" -> ioError (userError "synchronous setup fault")
  "closing" -> throwIO ThreadKilled
  _ -> pure ()
 first <- L.acquireLifetimeOwner owner parent
 check "setup synchronous fault reported" (first == Left L.OperationFailed)
 attempt <- try (L.retireLifetimeOwner owner) :: IO (Either SomeException (Either L.OwnerError ()))
 check "later cleanup async propagated" (case attempt of
  Left e -> case fromException e of Just ThreadKilled -> True; _ -> False
  Right _ -> False)
 status <- L.ownerStatus owner
 check "both sequential fault facts retained" (L.ownerExceptionCount status == 2 && L.ownerCloseUncertain status)
 check "no retry after cleanup interruption" . (== Left L.CloseUncertain) =<< L.retireLifetimeOwner owner
 void (identity parent)

main :: IO ()
main = do
 args <- getArgs
 root <- case args of [p] -> pure p; _ -> ioError (userError "provide a fresh owned 0700 fixture root")
 let fresh name = do
      let p = root </> name
      privateDir p
      pure p
 fresh "ordinary" >>= ordinary
 fresh "replacement" >>= replacement
 fresh "invalid" >>= invalidCases
 fresh "threads" >>= threadAndReentry
 fresh "opened" >>= \p -> interruptAt p "opened"
 fresh "locked" >>= \p -> interruptAt p "locked"
 fresh "closed-fault" >>= closedFault
 fresh "closing-fault" >>= closingFault
 fresh "separate-faults" >>= separateFaults
 putStrLn "LifetimeOwner independent source controls complete"
