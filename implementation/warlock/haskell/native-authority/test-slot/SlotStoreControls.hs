{-# LANGUAGE OverloadedStrings #-}
module Main (main) where
import Control.Concurrent (forkIO,newEmptyMVar,putMVar,takeMVar)
import Control.Exception (AsyncException(..),IOException,finally,throwIO,try)
import Control.Monad (forM_,unless)
import Data.IORef (atomicModifyIORef',newIORef)
import Foreign.C.Error (Errno(..),eBADF)
import GHC.IO.Exception (ioe_errno)
import qualified Data.ByteString as B
import qualified Data.ByteString.Char8 as C
import Numeric (showHex)
import System.Directory (renameFile)
import System.Environment (getArgs)
import System.FilePath ((</>))
import System.Posix.Directory (createDirectory)
import System.Posix.Files (FileStatus,createLink,createSymbolicLink,deviceID,fileID,getFdStatus,setFileMode)
import System.Posix.IO (OpenMode(ReadOnly),closeFd,defaultFileFlags,dupTo,openFd)
import Warlock.Native.Cancellation.SlotStore

assert :: Bool -> String -> IO ()
assert value message = unless value (ioError (userError message))
name :: Int -> SlotName
name n = case slotName (C.pack (replicate (64-length h) '0' ++ h ++ ".json")) of
 Right x -> x
 Left e -> error (show e)
 where h = showHex n ""
storeIn :: FilePath -> IO SlotStore
storeIn path = do
 createDirectory path 0o700
 fd <- openFd path ReadOnly defaultFileFlags
 store <- newSlotStore
 accepted <- offerDirectory store fd
 assert accepted "offer"
 pure store
basic :: FilePath -> IO ()
basic root = do
 store <- storeIn (root </> "basic")
 spare <- openFd (root </> "basic") ReadOnly defaultFileFlags
 acceptedAgain <- offerDirectory store spare
 assert (not acceptedAgain) "second offer accepted"
 _ <- getFdStatus spare
 closeFd spare
 assert (slotName "../x" == Left InvalidName && slotName "ABC.json" == Left InvalidName && slotName "envelope-v1.json" /= Left InvalidName) "name grammar"
 a <- publishSlot store (name 1) Nothing "old"; assert (a == Right ()) "create"
 b <- readSlot store (name 1); assert (b == Right (Just "old")) "read"
 c <- publishSlot store (name 1) Nothing "x"; assert (c == Left Mismatch) "no replace"
 d <- publishSlot store (name 1) (Just "bad") "x"; assert (d == Left Mismatch) "mismatch"
 e <- publishSlot store (name 1) (Just "old") "new"; assert (e == Right ()) "replace"
 f <- scanSlots store; assert (f == Right [(name 1,"new")]) "scan"
 g <- removeSlot store (name 1) "bad"; assert (g == Left Mismatch) "remove mismatch"
 h <- removeSlot store (name 1) "new"; assert (h == Right ()) "remove"
 i <- removeSlot store (name 1) "new"; assert (i == Left Mismatch) "remove missing"
 done <- retireSlotStore store; assert (slotRetired done && slotUncertain done == 0) "retire"
quota :: FilePath -> IO ()
quota root = do
 store <- storeIn (root </> "quota")
 forM_ [1..64] $ \i -> publishSlot store (name i) Nothing "x" >>= \r -> assert (r == Right ()) "populate"
 extra <- publishSlot store (name 65) Nothing "x"
 assert (extra == Left QuotaExceeded) "64 quota"
 kept <- scanSlots store; assert (case kept of Right xs -> length xs == 64; _ -> False) "no eviction"
 _ <- retireSlotStore store
 bytes <- storeIn (root </> "bytes")
 a <- publishSlot bytes (name 1) Nothing (B.replicate 1048576 65)
 b <- publishSlot bytes (name 2) Nothing "x"
 assert (a == Right () && b == Left QuotaExceeded) "one MiB quota"
 _ <- retireSlotStore bytes
 pure ()
poison :: FilePath -> IO ()
poison root = do
 let path=root </> "poison"
 createDirectory path 0o700
 fd <- openFd path ReadOnly defaultFileFlags
 store <- newSlotStoreWithHookForTest (\stage -> if stage == "rename-started" then ioError (userError "injected cut") else pure ())
 offered <- offerDirectory store fd; assert offered "offer poison"
 result <- publishSlot store (name 1) Nothing "x"
 after <- slotStatus store
 next <- publishSlot store (name 2) Nothing "y"
 assert (result == Left Uncertain && slotPoisoned after && next == Left Uncertain) "mutation poison"
 _ <- retireSlotStore store
 pure ()
busy :: FilePath -> IO ()
busy root = do
 let path=root </> "busy"
 createDirectory path 0o700
 fd <- openFd path ReadOnly defaultFileFlags
 entered <- newEmptyMVar; release <- newEmptyMVar; done <- newEmptyMVar
 store <- newSlotStoreWithHookForTest (\stage -> if stage == "file-sync" then putMVar entered () >> takeMVar release else pure ())
 accepted <- offerDirectory store fd; assert accepted "offer busy"
 _ <- forkIO (publishSlot store (name 1) Nothing "a" >>= putMVar done)
 takeMVar entered
 other <- publishSlot store (name 2) Nothing "b"
 retirement <- retireSlotStore store
 assert (other == Left Busy && slotBusy retirement) "shared gate"
 putMVar release ()
 completed <- takeMVar done; assert (completed == Right ()) "worker"
 _ <- retireSlotStore store
 pure ()
corruption :: FilePath -> IO ()
corruption root = do
 let path=root </> "corrupt"
 store <- storeIn path
 B.writeFile (path </> "debris") "x"
 a <- scanSlots store; assert (a == Left InvalidName) "unknown file must refuse"
 _ <- retireSlotStore store
 let path2=root </> "hardlink"
 store2 <- storeIn path2
 let file=path2 </> (replicate 63 '0' ++ "1.json")
 B.writeFile file "x"
 setFileMode file 0o600
 createLink file (path2 </> "outside-link")
 b <- readSlot store2 (name 1); assert (b == Left Corrupt) "hardlink refusal"
 _ <- retireSlotStore store2
 pure ()
nameSwap :: FilePath -> IO ()
nameSwap root = do
 let path = root </> "swap"
     file = path </> (replicate 63 '0' ++ "1.json")
 createDirectory path 0o700
 fd <- openFd path ReadOnly defaultFileFlags
 -- Initial publication uses a separate store to avoid firing the fault hook.
 first <- newSlotStore
 ok <- offerDirectory first fd; assert ok "swap initial offer"
 created <- publishSlot first (name 1) Nothing "old"; assert (created == Right ()) "swap create"
 _ <- retireSlotStore first
 secondFd <- openFd path ReadOnly defaultFileFlags
 second <- newSlotStoreWithHookForTest $ \point ->
  if point == "file-sync" then do
   renameFile file (path </> "saved-old")
   B.writeFile file "old"
   setFileMode file 0o600
  else pure ()
 offered <- offerDirectory second secondFd; assert offered "swap second offer"
 replaced <- publishSlot second (name 1) (Just "old") "new"
 status <- slotStatus second
 assert (replaced == Left Uncertain && slotPoisoned status) "name swap or poison was not detected"
 _ <- retireSlotStore second
 pure ()

symlink :: FilePath -> IO ()
symlink root = do
 let path = root </> "symlink"
 store <- storeIn path
 let file = path </> (replicate 63 '0' ++ "1.json")
 createSymbolicLink "missing" file
 result <- readSlot store (name 1)
 assert (case result of Left _ -> True; Right _ -> False) "symlink followed"
 _ <- retireSlotStore store
 pure ()

-- Actual close followed by an injected async uncertainty, then reuse of that
-- exact number for an independent sentinel; a subsequent retire must not close it.
asyncClose :: FilePath -> IO ()
asyncClose root = do
 let path = root </> "close-uncertain"; sentinelPath = root </> "sentinel"
 createDirectory path 0o700
 B.writeFile sentinelPath "sentinel"
 sentinel <- openFd sentinelPath ReadOnly defaultFileFlags
 initial <- getFdStatus sentinel
 directoryFd <- openFd path ReadOnly defaultFileFlags
 fired <- newIORef False
 store <- newSlotStoreWithHookForTest $ \point -> if point /= "close-after" then pure () else do
  first <- atomicModifyIORef' fired (\old -> (True,not old))
  if first then throwIO ThreadKilled else pure ()
 accepted <- offerDirectory store directoryFd; assert accepted "close offer"
 outcome <- try (publishSlot store (name 1) Nothing "data") :: IO (Either AsyncException (Either SlotError ()))
 assert (case outcome of Left ThreadKilled -> True; _ -> False) "async close not propagated"
 snapshot <- slotStatus store
 let unknown = filter (/= directoryFd) (slotRetainedFDs snapshot)
 target <- case unknown of [fd] -> pure fd; _ -> ioError (userError "expected exactly one uncertain fd")
 closed <- try (getFdStatus target) :: IO (Either IOException FileStatus)
 case closed of
  Left e | maybe False (\n -> Errno n == eBADF) (ioe_errno e) -> pure ()
  _ -> ioError (userError "target not confirmed closed")
 _ <- dupTo sentinel target
 let finish = closeFd target >> closeFd sentinel
 (do
   before <- getFdStatus target
   retired <- retireSlotStore store
   after <- getFdStatus target
   assert (slotUncertain retired == 1 && deviceID initial == deviceID before && fileID initial == fileID before && deviceID before == deviceID after && fileID before == fileID after) "stale fd retry closed sentinel"
  ) `finally` finish

main :: IO ()
main = do
 args <- getArgs
 case args of
  [root] -> basic root >> quota root >> poison root >> busy root >> corruption root >> nameSwap root >> symlink root >> asyncClose root
  _ -> ioError (userError "expected isolated private empty fixture parent")
