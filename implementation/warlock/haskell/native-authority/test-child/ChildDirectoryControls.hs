{-# LANGUAGE OverloadedStrings #-}
module Main (main) where
import Control.Exception (AsyncException(..),IOException,finally,throwIO,try)
import Control.Monad (unless,when)
import qualified Data.ByteString as B
import Foreign.C.Error (Errno(..),eBADF)
import GHC.IO.Exception (ioe_errno)
import System.Directory (doesDirectoryExist,renameDirectory)
import System.Environment (getArgs)
import System.FilePath ((</>))
import System.Posix.Directory (createDirectory)
import System.Posix.Files (FileStatus,createSymbolicLink,deviceID,fileID,getFdStatus,getFileStatus,setFileMode)
import System.Posix.IO (OpenMode(ReadOnly),closeFd,defaultFileFlags,dupTo,openFd)
import System.Posix.Types (Fd)
import Warlock.Native.Cancellation.SlotStore

assert :: Bool -> String -> IO ()
assert value message = unless value (ioError (userError message))
parent :: FilePath -> String -> IO (FilePath,Fd)
parent root name = do
 let path = root </> name
 createDirectory path 0o700
 fd <- openFd path ReadOnly defaultFileFlags
 pure (path,fd)
closed :: Fd -> IO Bool
closed fd = do
 outcome <- try (getFdStatus fd) :: IO (Either IOException FileStatus)
 pure $ case outcome of Left e -> maybe False (\v -> Errno v == eBADF) (ioe_errno e); Right _ -> False
identity :: FileStatus -> (Integer,Integer)
identity s = (toInteger (deviceID s),toInteger (fileID s))

fresh :: FilePath -> IO ()
fresh root = do
 (path,borrowed) <- parent root "fresh"
 store <- newSlotStore
 first <- offerChildDirectory store borrowed Admissions
 assert (first == Right ()) "fresh admissions"
 exists <- doesDirectoryExist (path </> "admissions-v1")
 assert exists "exact admissions name"
 snapshot <- slotStatus store
 child <- case slotRetainedFDs snapshot of [fd] -> pure fd; _ -> ioError (userError "expected one owned child")
 duplicate <- offerChildDirectory store borrowed Companions
 assert (duplicate == Left Unavailable) "second offer accepted"
 sentinel <- openFd path ReadOnly defaultFileFlags
 sentinelBefore <- getFdStatus sentinel
 (do
   stopped <- retireSlotStore store
   dead <- closed child
   _ <- getFdStatus borrowed
   assert (slotRetired stopped && slotUncertain stopped == 0 && dead) "retirement or borrowed parent"
   _ <- dupTo sentinel child
   again <- retireSlotStore store
   after <- getFdStatus child
   assert (slotRetired again && identity sentinelBefore == identity after) "retire retried stale child number"
  ) `finally` (do wasClosed <- closed child; unless wasClosed (closeFd child); closeFd sentinel)
 -- Independently opened existing child must be accepted without a parent fsync.
 store2 <- newSlotStoreWithHookForTest (\phase -> when (phase == "child-parent-fsync") (ioError (userError "unexpected existing fsync")))
 existing <- offerChildDirectory store2 borrowed Admissions
 assert (existing == Right ()) "existing directory"
 _ <- retireSlotStore store2
 _ <- getFdStatus borrowed
 closeFd borrowed

companion :: FilePath -> IO ()
companion root = do
 (path,borrowed) <- parent root "companion"
 store <- newSlotStore
 result <- offerChildDirectory store borrowed Companions
 assert (result == Right ()) "companion creation"
 exists <- doesDirectoryExist (path </> "cancellation-admissions-v1")
 assert exists "exact companion name"
 _ <- retireSlotStore store
 _ <- getFdStatus borrowed
 closeFd borrowed

refusals :: FilePath -> IO ()
refusals root = do
 (modePath,modeFd) <- parent root "mode"
 setFileMode modePath 0o755
 modeStore <- newSlotStore
 badMode <- offerChildDirectory modeStore modeFd Admissions
 modeStatus <- slotStatus modeStore
 assert (badMode == Left Corrupt && slotOffered modeStatus && slotPoisoned modeStatus) "bad parent mode"
 retry <- offerChildDirectory modeStore modeFd Admissions
 assert (retry == Left Unavailable) "bad mode retried"
 _ <- retireSlotStore modeStore
 _ <- getFdStatus modeFd; closeFd modeFd
 (childModePath,childModeFd) <- parent root "child-mode"
 createDirectory (childModePath </> "admissions-v1") 0o700
 setFileMode (childModePath </> "admissions-v1") 0o755
 childModeStore <- newSlotStore
 childModeResult <- offerChildDirectory childModeStore childModeFd Admissions
 assert (childModeResult == Left Corrupt) "bad child mode"
 _ <- retireSlotStore childModeStore; _ <- getFdStatus childModeFd; closeFd childModeFd
 (linkPath,linkFd) <- parent root "link"
 createSymbolicLink "missing" (linkPath </> "admissions-v1")
 linkStore <- newSlotStore
 linkResult <- offerChildDirectory linkStore linkFd Admissions
 assert (case linkResult of Left _ -> True; Right _ -> False) "symlink child followed"
 _ <- retireSlotStore linkStore; _ <- getFdStatus linkFd; closeFd linkFd
 (filePath,fileFd) <- parent root "file"
 B.writeFile (filePath </> "admissions-v1") "not a directory"
 fileStore <- newSlotStore
 fileResult <- offerChildDirectory fileStore fileFd Admissions
 assert (case fileResult of Left _ -> True; Right _ -> False) "regular child accepted"
 _ <- retireSlotStore fileStore; _ <- getFdStatus fileFd; closeFd fileFd
 (retiredPath,retiredFd) <- parent root "retired"
 _ <- getFileStatus retiredPath
 retiredStore <- newSlotStore
 _ <- retireSlotStore retiredStore
 afterRetire <- offerChildDirectory retiredStore retiredFd Admissions
 assert (afterRetire == Left Unavailable) "retired shell reused"
 _ <- getFdStatus retiredFd; closeFd retiredFd

nameSwap :: FilePath -> IO ()
nameSwap root = do
 (path,borrowed) <- parent root "swap"
 store <- newSlotStoreWithHookForTest $ \phase -> when (phase == "child-opened") $ do
  renameDirectory (path </> "admissions-v1") (path </> "moved")
  createDirectory (path </> "admissions-v1") 0o700
 result <- offerChildDirectory store borrowed Admissions
 snapshot <- slotStatus store
 assert (result == Left Corrupt && slotPoisoned snapshot && length (slotRetainedFDs snapshot) == 1) "child name swap"
 _ <- retireSlotStore store
 _ <- getFdStatus borrowed; closeFd borrowed

failed :: FilePath -> String -> Bool -> IO ()
failed root point asynchronous = do
 (_,borrowed) <- parent root (if asynchronous then "async" else "fsync")
 store <- newSlotStoreWithHookForTest $ \phase -> when (phase == point) $
  if asynchronous then throwIO ThreadKilled else ioError (userError "parent fsync fault")
 outcome <- try (offerChildDirectory store borrowed Admissions) :: IO (Either AsyncException (Either SlotError ()))
 let expected = if asynchronous
       then case outcome of Left ThreadKilled -> True; _ -> False
       else outcome == Right (Left IoFailure)
 assert expected "fault outcome"
 snapshot <- slotStatus store
 assert (slotOffered snapshot && slotPoisoned snapshot && length (slotRetainedFDs snapshot) == 1) "failed child custody"
 retry <- offerChildDirectory store borrowed Admissions
 assert (retry == Left Unavailable) "partial initialization retried"
 _ <- retireSlotStore store
 _ <- getFdStatus borrowed; closeFd borrowed

main :: IO ()
main = do
 args <- getArgs
 case args of
  [root] -> fresh root >> companion root >> refusals root >> nameSwap root >> failed root "child-opened" True >> failed root "child-parent-fsync" False
  _ -> ioError (userError "expected isolated empty private fixture parent")
