{-# LANGUAGE CPP #-}
{-# LANGUAGE OverloadedStrings #-}
{-# LANGUAGE RankNTypes #-}
-- Root-only owned-directory component fixture. This is NOT an ACK or journal
-- recovery test; TerminalReceipt is an in-process storage observation only.
module Main (main) where
import Control.Concurrent (forkIO,newEmptyMVar,putMVar,takeMVar)
import Control.Exception (AsyncException(ThreadKilled),SomeException,fromException,mask_,throwIO,try)
import Control.Monad (forM_,unless)
import Data.Either (isLeft)
import Data.IORef (modifyIORef',newIORef,readIORef)
import qualified Data.ByteString as B
import qualified Data.ByteString.Char8 as C
import qualified Data.Text as T
import System.Directory (createDirectory,doesFileExist)
import System.Environment (getArgs)
import System.FilePath ((</>))
import System.Posix.Files (createLink,createSymbolicLink,deviceID,fileID,getFileStatus,setFileMode)
import System.Posix.IO (OpenMode(ReadOnly),closeFd,defaultFileFlags,dup,openFd)
import SwapControls (verifyNameSwap)
import Warlock.Native.Cancellation.Internal
import qualified Warlock.Native.Cancellation.Storage as S
import Warlock.Protocol.Custody (Operation(..),intent)
import Warlock.Protocol.Identity (Counter,binding,context,parseCounter)

check :: String -> Bool -> IO ()
check label good = unless good (ioError (userError label))
right :: Show e => Either e a -> IO a
right = either (ioError . userError . show) pure
number :: Integer -> IO Counter
number n = right (parseCounter True (T.pack (show n)))
makeKey :: Integer -> IO Key
makeKey peer = do
 p <- number peer; start <- number 2; life <- number 3; sess <- number 4; front <- number 5
 req <- number 6; gen <- number 7; inc <- number 8; output <- number 9; revision <- number 10
 b <- right (binding life sess front)
 c <- right (context b life front output revision)
 i <- right (intent b req gen inc c Restore)
 o <- right (ownerId p start b)
 right (key o 1 i)

-- Provider is a trusted same-package test double; its result is not real
-- compositor/window evidence or a caller-created Snapshot.
makeTerminal :: IO (Owner,Key,PreparedId,Deadline,Snapshot)
makeTerminal = do
 k <- makeKey 1; initial <- number 0; rev <- number 10; out <- number 9
 let facts = Facts rev out Applied
 let fmt s = Right (C.pack (show (snapshotPhase s)))
 owner <- newOwner initial fmt (Provider (\permit -> do
   check "matching provider permit" (permitMatches permit k)
   pure (MutationEntered,CommittedObserved facts))) (\_ -> pure ()) >>= right
 end <- number 10 >>= right . deadline; now <- number 1
 prepared <- prepare owner k end now initial initial >>= right
 terminal <- commit owner k (snapshotId prepared) end now facts >>= right
 check "owner actually committed" (snapshotPhase terminal == Committed && snapshotResource terminal == TokenRetired)
 pure (owner,k,snapshotId prepared,end,terminal)

newOwnedDirectory :: FilePath -> String -> (S.Stage -> IO ()) -> IO (S.Storage,FilePath)
newOwnedDirectory root label hook = mask_ $ do
 let dir = root </> label
 createDirectory dir
 setFileMode dir 0o700
 storage <- S.newStorageWithHookForTest hook
 fd <- openFd dir ReadOnly defaultFileFlags
 accepted <- S.offerDirectory storage fd
 unless accepted (closeFd fd >> ioError (userError "first offer refused"))
 pure (storage,dir)

main :: IO ()
main = do
 args <- getArgs
 root <- case args of [dir] -> pure dir; _ -> ioError (userError "owned empty fixture directory required")
 (owner,k,p,d,terminal) <- makeTerminal
 ticket <- selectTerminalTicket owner k p d >>= right
 (storage,dir) <- newOwnedDirectory root "positive" (\_ -> pure ())
 receipt <- persistTerminalTicket storage ticket >>= right
 current <- terminalReceiptCurrent receipt
 check "actual terminal storage receipt current" (current == Right ())
 status <- S.storageStatus storage
 dirStat <- getFileStatus dir
 fileStat <- getFileStatus (dir </> "warlock-cancel-terminal.v1")
 let identity st = (toInteger (deviceID st),toInteger (fileID st))
 check "file and directory synced and retained" (S.storageStage status == S.DirectorySynced && S.directoryStatus status == S.HandleOwned && S.fileStatus status == S.HandleOwned && S.directoryIdentity status == Just (identity dirStat) && S.fileIdentity status == Just (identity fileStat))
#ifdef WARLOCK_FINAL_ENTRY
 check "final entry retained" (S.entryStatus status == S.HandleOwned)
#endif
 bytes <- B.readFile (dir </> "warlock-cancel-terminal.v1")
 check "actual persisted owner-selected bytes" ("WCAN1\n" `B.isPrefixOf` bytes && snapshotReply terminal `B.isSuffixOf` bytes)
 lateRev <- number 10; lateOut <- number 9
 late <- cancel owner k p d (Facts lateRev lateOut CancelledByOwner) >>= right
 check "late cancellation preserves terminal" (late == terminal)
 stillCurrent <- terminalReceiptCurrent receipt
 check "terminal unchanged while receipt current" (stillCurrent == Right ())
 retiring <- newEmptyMVar
 leased <- S.withStorageLease storage $ \held -> do
  _ <- forkIO (S.retireStorage storage >>= putMVar retiring)
  refusedRetire <- takeMVar retiring
  check "retirement cannot close leased handles" (S.fileStatus refusedRetire == S.HandleOwned && S.directoryStatus refusedRetire == S.HandleOwned && S.entryStatus refusedRetire == S.HandleOwned)
  nested <- terminalReceiptCurrent receipt
  check "nested receipt check refuses borrowed custody" (nested == Left Busy)
  check "leased snapshot retains real handles" (S.fileStatus held == S.HandleOwned)
 check "storage lease acquired" (leased == Just ())
 afterLease <- terminalReceiptCurrent receipt
 check "receipt valid after lease released" (afterLease == Right ())
 interruptedLease <- try (S.withStorageLease storage (\_ -> throwIO ThreadKilled)) :: IO (Either SomeException (Maybe ()))
 check "lease propagates original async exception" (case interruptedLease of
  Left err -> case fromException err of Just ThreadKilled -> True; _ -> False
  Right _ -> False)
 afterInterruptedLease <- terminalReceiptCurrent receipt
 check "async lease releases gate without retiring handles" (afterInterruptedLease == Right ())
 done <- S.retireStorage storage
 check "normal owned descriptors closed" (S.directoryStatus done == S.HandleClosed && S.fileStatus done == S.HandleClosed)
#ifdef WARLOCK_FINAL_ENTRY
 check "final entry independently closed" (S.entryStatus done == S.HandleClosed)
#endif
 stale <- terminalReceiptCurrent receipt
 check "retired storage receipt not current" (stale == Left Foreign)

 wrong <- makeKey 2
 wrongTicket <- selectTerminalTicket owner wrong p d
 check "different full key cannot select terminal" (isLeft wrongTicket)
 otherKey <- makeKey 2
 freshZero <- number 0; freshNow <- number 1
 otherPrepared <- prepare owner otherKey d freshNow freshZero freshZero >>= right
 wrongPrepared <- selectTerminalTicket owner k (snapshotId otherPrepared) d
 check "different prepared id refused" (isLeft wrongPrepared)
 laterD <- number 11 >>= right . deadline
 wrongDeadline <- selectTerminalTicket owner k p laterD
 check "different original deadline refused" (isLeft wrongDeadline)

 -- A fresh real owner with a test provider returning Unknown cannot supply a
 -- terminal ticket; no caller-created receipt or wire terminal is involved.
 zero <- number 0; fRev <- number 10; fOut <- number 9
 let f = Facts fRev fOut Unproven
 unknownOwner <- newOwner zero (\s -> Right (C.pack (show (snapshotPhase s))))
  (Provider (\_ -> pure (MutationEntered,Uncertain f))) (\_ -> pure ()) >>= right
 uD <- number 10 >>= right . deadline; now <- number 1
 up <- prepare unknownOwner k uD now zero zero >>= right
 u <- commit unknownOwner k (snapshotId up) uD now f >>= right
 uTicket <- selectTerminalTicket unknownOwner k (snapshotId up) uD
 check "unknown cannot select terminal" (snapshotPhase u == ExecutionUnknown && isLeft uTicket)

 let cuts = [("cut-create",S.Creating),("cut-write",S.Writing),("cut-readback",S.ReadingBack),
             ("cut-file-sync",S.SyncingFile),("cut-after-file-sync",S.FileSynced),
             ("cut-before-rename",S.Renaming),("cut-after-rename",S.Renamed),
             ("cut-after-directory-sync",S.DirectorySynced)]
 forM_ cuts $ \(label,cut) -> do
  (cutStorage,cutDir) <- newOwnedDirectory root label (\stage -> if stage == cut then ioError (userError "injected stage cut") else pure ())
  failed <- persistTerminalTicket cutStorage ticket
  st <- S.storageStatus cutStorage
  check "stage cut yields no receipt" (isLeft failed && S.storageStage st == S.Poisoned cut && S.directoryStatus st == S.HandleOwned)
  whenRenamed <- if cut == S.Renamed then doesFileExist (cutDir </> "warlock-cancel-terminal.v1") else pure True
  check "rename-visible is not successful receipt" whenRenamed
  cleaned <- S.retireStorage cutStorage
  check "independent normal close after cut" (S.directoryStatus cleaned == S.HandleClosed && S.fileStatus cleaned `elem` [S.HandleAbsent,S.HandleClosed])

 -- Actual permission and hard-link negatives against the production route.
 (badDir,badDirPath) <- newOwnedDirectory root "bad-dir-mode" (\_ -> pure ())
 setFileMode badDirPath 0o755
 invalidDir <- persistTerminalTicket badDir ticket
 check "nonprivate directory refused" (isLeft invalidDir)
 _ <- S.retireStorage badDir
 let modeDir = root </> "bad-file-mode"
 (badFile,_) <- newOwnedDirectory root "bad-file-mode" (\stage -> if stage == S.Writing then setFileMode (modeDir </> ".warlock-cancel-terminal.tmp") 0o644 else pure ())
 invalidFile <- persistTerminalTicket badFile ticket
 check "nonprivate file refused" (isLeft invalidFile)
 _ <- S.retireStorage badFile
 let linkDir = root </> "hard-linked"
 (linked,_) <- newOwnedDirectory root "hard-linked" (\stage -> if stage == S.Writing then createLink (linkDir </> ".warlock-cancel-terminal.tmp") (linkDir </> "extra-link") else pure ())
 invalidLink <- persistTerminalTicket linked ticket
 check "multiple links refused" (isLeft invalidLink)
 _ <- S.retireStorage linked

 verifyNameSwap root ticket

 -- A pre-existing symlink at the exact staging name is never followed.
 (linkStorage,linkPath) <- newOwnedDirectory root "staging-symlink" (\_ -> pure ())
 createSymbolicLink "/dev/null" (linkPath </> ".warlock-cancel-terminal.tmp")
 linkResult <- persistTerminalTicket linkStorage ticket
 check "preexisting staging symlink refused" (isLeft linkResult)
 _ <- S.retireStorage linkStorage

 -- A second application of the same ticket cannot generate another receipt.
 (replay,_) <- newOwnedDirectory root "one-shot-replay" (\_ -> pure ())
 firstReceipt <- persistTerminalTicket replay ticket >>= right
 duplicated <- persistTerminalTicket replay ticket
 check "storage one shot refuses second persistence" (isLeft duplicated)
 oldCurrent <- terminalReceiptCurrent firstReceipt
 check "poisoned storage does not certify prior receipt current" (oldCurrent == Left Foreign)
 _ <- S.retireStorage replay

 -- Async cuts before creation, after FD publication and after directory
 -- fsync must propagate and retain their precise conservative ownership.
 forM_ [("async-create",S.Creating),("async-write",S.Writing),("async-after-dirsync",S.DirectorySynced)] $ \(label,cut) -> do
  (asyncStorage,_) <- newOwnedDirectory root label (\stage -> if stage == cut then throwIO ThreadKilled else pure ())
  interrupted <- try (persistTerminalTicket asyncStorage ticket) :: IO (Either SomeException (Either Error TerminalReceipt))
  asyncState <- S.storageStatus asyncStorage
  let expectedFile = if cut == S.Creating then S.HandleAbsent else S.HandleOwned
  check "async remains async with retained custody" (case interrupted of Left e -> (fromException e :: Maybe AsyncException) == Just ThreadKilled && S.storageStage asyncState == S.Poisoned cut && S.directoryStatus asyncState == S.HandleOwned && S.fileStatus asyncState == expectedFile; Right _ -> False)
#ifdef WARLOCK_FINAL_ENTRY
  check "async final entry custody" (S.entryStatus asyncState == (if cut == S.DirectorySynced then S.HandleOwned else S.HandleAbsent))
#endif
  _ <- S.retireStorage asyncStorage
  pure ()

 -- A failed hook before the actual close is conservatively Uncertain. The
 -- owner never retries the numeric FD; this deliberately retained descriptor
 -- requires the root fixture's bounded owned-process containment.
 closeCalls <- newIORef (0 :: Int)
 (closeStorage,_) <- newOwnedDirectory root "uncertain-close" (\stage -> if stage == S.ClosingFile then modifyIORef' closeCalls (+1) >> ioError (userError "injected close fault") else pure ())
 _ <- persistTerminalTicket closeStorage ticket >>= right
 firstClose <- S.retireStorage closeStorage
 secondClose <- S.retireStorage closeStorage
 attempts <- readIORef closeCalls
 check "uncertain close retained and not retried" (S.fileStatus firstClose == S.HandleUncertain && S.fileStatus secondClose == S.HandleUncertain && S.directoryStatus secondClose == S.HandleClosed && attempts == 1)

#ifdef WARLOCK_FINAL_ENTRY
 check "uncertain-file path still closed final entry" (S.entryStatus secondClose == S.HandleClosed)
#endif
 -- A rejected second directory offer leaves that separate FD with its caller.
 (singleOffer,_) <- newOwnedDirectory root "single-offer" (\_ -> pure ())
 extra <- openFd root ReadOnly defaultFileFlags
 spare <- dup extra
 second <- S.offerDirectory singleOffer spare
 check "second offer refused" (not second)
 closeFd spare
 closeFd extra
 _ <- S.retireStorage singleOffer
 C.putStrLn "terminal storage component fixture complete"
