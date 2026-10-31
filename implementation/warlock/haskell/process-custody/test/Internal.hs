{-# LANGUAGE OverloadedStrings #-}
module Main (main) where
import Control.Concurrent (threadDelay, forkIO, newEmptyMVar, putMVar, takeMVar)
import Control.Exception (IOException, SomeAsyncException, SomeException, bracket, fromException, throwIO, try, toException, displayException, AsyncException(ThreadKilled,UserInterrupt))
import Data.IORef (newIORef, modifyIORef', readIORef)
import Control.Monad (unless)
import qualified Data.ByteString.Char8 as C
import qualified Data.ByteString as B
import qualified Crypto.Hash.SHA256 as SHA
import Numeric (showHex)
import System.Directory (createDirectory, doesFileExist, getTemporaryDirectory, removeFile, removePathForcibly)
import System.FilePath ((</>))
import System.IO (hClose, openTempFile, openBinaryFile, IOMode(ReadMode))
import VerifiedFixture (validatedFixtureLease)
import qualified Warlock.Capture.Process.Lease as Lease
import System.Environment (getArgs)
import System.Exit (exitFailure)
import qualified Warlock.Capture.Process.Owner as OwnerCore
import qualified Warlock.Capture.Process.Transfer as Transfer
import qualified Warlock.Capture.Process.Transfer.Internal as TransferInternal
import Warlock.Capture.Process.Internal
check :: String -> Bool -> IO ()
check name yes = unless yes (putStrLn (name ++ ": FAIL") >> exitFailure)
main :: IO ()
main = do
 args <- getArgs
 case args of
  [exe] -> do
   owner <- newOwner
   ok <- runFixture owner exe ["--fixture","ok"] 4096 2000000
   check "owned child output and reap" (ok == Right (Captured "fixture-ok" ""))
   let hex bytes = concatMap (\n -> let h=showHex n "" in if length h==1 then '0':h else h) (B.unpack bytes)
   fixtureHash <- C.pack . hex . SHA.hash <$> B.readFile exe
   failure <- runFixturePinnedObserved owner exe fixtureHash ["--fixture","diagnostic-exit7"] 4096 2000000
   check "failed operation retains bounded diagnostics" (failure==ToolObservation (Left (Unsuccessful 7)) (Just (Captured "fixture-out" "fixture-error")))
   legacy <- runFixturePinned owner exe fixtureHash ["--fixture","diagnostic-exit7"] 4096 2000000
   check "legacy API preserves failure" (legacy==Left (Unsuccessful 7))
   success <- runFixturePinnedObserved owner exe fixtureHash ["--fixture","ok"] 4096 2000000
   check "success diagnostic observation" (success==ToolObservation (Right (Captured "fixture-ok" "")) (Just (Captured "fixture-ok" "")))
   noCapture <- runFixturePinnedObserved owner exe fixtureHash ["--fixture","overflow"] 1024 2000000
   check "overflow never claims complete capture" (operation noCapture==Left OutputLimit && capturedOutput noCapture==Nothing)
   late <- runFixturePinnedObserved owner exe fixtureHash ["--fixture","hang"] 4096 100000
   check "timeout never claims complete capture" (operation late==Left TimedOut && capturedOutput late==Nothing)
   stale <- runFixturePinnedObserved owner exe "0000000000000000000000000000000000000000000000000000000000000000" ["--fixture","ok"] 4096 2000000
   check "invocation cannot reuse prior diagnostics" (stale==ToolObservation (Left ToolHashMismatch) Nothing)
   overflow <- runFixture owner exe ["--fixture","overflow"] 1024 2000000
   check "output limit" (overflow == Left OutputLimit)
   stalled <- runFixture owner exe ["--fixture","hang"] 4096 100000
   check "deadline and cleanup" (stalled == Left TimedOut)
   bracket tempRoot removePathForcibly $ \root -> do
    C.writeFile (root </> "selected-input") ""
    selectedIn <- openBinaryFile (root </> "selected-input") ReadMode
    selectedResult <- runSelected owner (selectedFixture exe ["--fixture","ok"] selectedIn) 4096 2000000 awaitLeader
    selectedState <- status owner
    check "selected session normal" (selectedResult == Right (SelectedResult (Captured "fixture-ok" "") True True) && selectedState == Available)
    failureIn <- openBinaryFile (root </> "selected-input") ReadMode
    callbackResult <- runSelected owner (selectedFixture exe ["--fixture","hang"] failureIn) 4096 2000000 (\_ -> ioError (userError "fixture conversation failure"))
    callbackState <- status owner
    check "selected callback failure settles" (callbackResult == Left SpawnOrIO && callbackState == Available)
    timeoutIn <- openBinaryFile (root </> "selected-input") ReadMode
    selectedTimeout <- runSelected owner (selectedFixture exe ["--fixture","hang"] timeoutIn) 4096 100000 awaitLeader
    timeoutState <- status owner
    check "selected deadline settles" (selectedTimeout == Left TimedOut && timeoutState == Available)
    earlyIn <- openBinaryFile (root </> "selected-input") ReadMode
    early <- runSelected owner (selectedFixture exe ["--fixture","exit7"] earlyIn) 4096 2000000 awaitLeader
    earlyState <- status owner
    check "selected early exit" (early == Left (Unsuccessful 7) && earlyState == Available)
    floodIn <- openBinaryFile (root </> "selected-input") ReadMode
    flood <- runSelected owner (selectedFixture exe ["--fixture","overflow"] floodIn) 1024 2000000 awaitLeader
    floodState <- status owner
    check "selected output cap" (flood == Left OutputLimit && floodState == Available)
    expiredInput <- openBinaryFile (root </> "selected-input") ReadMode
    expiredDeadline <- deadlineAfter 1000
    threadDelay 10000
    case expiredDeadline of
     Left _ -> check "deadline construction" False
     Right d -> do
      expired <- runSelectedUntil owner (selectedFixture exe ["--fixture","ok"] expiredInput) 4096 d awaitLeader
      ownerAfterExpiry <- status owner
      check "expired before admission leaves caller transfer" (expired == Left TimedOut && ownerAfterExpiry == Available)
      hClose expiredInput
    budgetInput <- openBinaryFile (root </> "selected-input") ReadMode
    budgetDeadline <- deadlineAfter 10000
    case budgetDeadline of
     Left _ -> check "setup budget deadline" False
     Right d -> do
      budget <- runSelectedFixtureHook owner (selectedFixture exe ["--fixture","ok"] budgetInput) 4096 d awaitLeader (\stage -> if stage == "before-spawn" then threadDelay 30000 else pure ())
      budgetState <- status owner
      check "setup consumes admission budget" (budget == Left TimedOut && budgetState == Available)
      hClose budgetInput
    splitInput <- openBinaryFile (root </> "selected-input") ReadMode
    splitDeadline <- deadlineAfter 100000
    case splitDeadline of
     Left _ -> check "split budget deadline" False
     Right d -> do
      splitResult <- runSelectedFixtureHook owner (selectedFixture exe ["--fixture","hang"] splitInput) 4096 d (\_ -> threadDelay 70000 >> pure (Right ())) (\stage -> if stage == "before-spawn" then threadDelay 70000 else pure ())
      splitState <- status owner
      check "one deadline covers setup and conversation" (splitResult == Left TimedOut && splitState == Available)
    observationInput <- openBinaryFile (root </> "selected-input") ReadMode
    observed <- newIORef False
    observedResult <- runSelected owner (selectedFixture exe ["--fixture","hang"] observationInput) 4096 100000 (\session -> do
     info <- observeSession session
     case info of Right _ -> modifyIORef' observed (const True); Left _ -> pure ()
     awaitLeader session)
    didObserve <- readIORef observed
    check "scoped live child observation" (observedResult == Left TimedOut && didObserve)
    escapedInput <- openBinaryFile (root </> "selected-input") ReadMode
    savedSession <- newEmptyMVar
    liveResult <- newEmptyMVar
    escapedRun <- runSelected owner (selectedFixture exe ["--fixture","hang"] escapedInput) 4096 2000000 (\session -> do
     putMVar savedSession session
     observeSession session >>= putMVar liveResult
     pure (Right ()))
    live <- takeMVar liveResult
    sessionAfter <- takeMVar savedSession
    afterObservation <- observeSession sessionAfter
    afterPoll <- awaitLeader sessionAfter
    check "live observation before session close" (case live of Right _ -> True; _ -> False)
    check "escaped session closed after cleanup" (afterObservation == Left SessionClosed && afterPoll == Left SessionClosed && case escapedRun of Left (Unsuccessful _) -> True; _ -> False)
    fixtureLease <- validatedFixtureLease root "selected-input"
    borrow <- Lease.borrowHeld fixtureLease
    case borrow of
     Left _ -> check "lease fixture borrow" False
     Right (_,release) -> do
      busyLease <- Lease.retireHeld fixtureLease
      check "lease cannot retire while borrowed" (busyLease == Left Lease.LeaseBusy)
      release
      release
      retiredLease <- Lease.retireHeld fixtureLease
      secondRetire <- Lease.retireHeld fixtureLease
      check "lease release idempotent and retire once" (retiredLease == Right () && secondRetire == Left Lease.LeaseClosed)
    ticketCount <- newIORef (0 :: Int)
    ticketInput <- openBinaryFile (root </> "selected-input") ReadMode
    ticket <- TransferInternal.fixtureTicketWithClose ticketInput (modifyIORef' ticketCount (+1) >> hClose ticketInput)
    beforeDeadline <- deadlineAfter 1000
    threadDelay 10000
    case beforeDeadline of
     Left _ -> check "ticket preclaim deadline" False
     Right d -> do
      let preclaimMarker = root </> "preclaim-child"
      beforeResult <- runSelectedFixtureHook owner (selectedTicketFixture exe ["--fixture","marker",preclaimMarker] ticket) 4096 d awaitLeader (const (pure ()))
      callerClosed <- Transfer.closeCallerTransfer ticket
      callerRepeat <- Transfer.closeCallerTransfer ticket
      beforeCount <- readIORef ticketCount
      preclaimSpawned <- doesFileExist preclaimMarker
      beforeState <- status owner
      check "preclaim expiry retains caller and closes once" (beforeResult == Left TimedOut && callerClosed == Right () && callerRepeat == Right () && beforeCount == 1 && not preclaimSpawned && beforeState == Available)
    postCount <- newIORef (0 :: Int)
    postInput <- openBinaryFile (root </> "selected-input") ReadMode
    postTicket <- TransferInternal.fixtureTicketWithClose postInput (modifyIORef' postCount (+1) >> hClose postInput)
    afterDeadline <- deadlineAfter 10000
    postMarker <- newIORef False
    case afterDeadline of
     Left _ -> check "ticket afterclaim deadline" False
     Right d -> do
      let postclaimMarker = root </> "postclaim-child"
      afterResult <- runSelectedFixtureHook owner (selectedTicketFixture exe ["--fixture","marker",postclaimMarker] postTicket) 4096 d (\_ -> modifyIORef' postMarker (const True) >> pure (Right ())) (\stage -> if stage == "before-spawn" then threadDelay 30000 else pure ())
      afterCaller <- Transfer.closeCallerTransfer postTicket
      afterDisposition <- Transfer.transferDisposition postTicket
      afterCount <- readIORef postCount
      postclaimSpawned <- doesFileExist postclaimMarker
      callbackAfter <- readIORef postMarker
      check "postclaim expiry core closes exactly once" (afterResult == Left TimedOut && afterCaller == Left Transfer.WrongOwner && afterDisposition == Transfer.TransferClosed && afterCount == 1 && not postclaimSpawned && not callbackAfter)
    callerWinCount <- newIORef (0 :: Int)
    callerWinInput <- openBinaryFile (root </> "selected-input") ReadMode
    callerWin <- TransferInternal.fixtureTicketWithClose callerWinInput (modifyIORef' callerWinCount (+1) >> hClose callerWinInput)
    callerWinToken <- TransferInternal.newOwnerToken
    claimAllowed <- newEmptyMVar
    callerClaimDone <- newEmptyMVar
    _ <- forkIO (takeMVar claimAllowed >> TransferInternal.claimTransfer callerWinToken callerWin >>= putMVar callerClaimDone)
    callerClose <- Transfer.closeCallerTransfer callerWin
    putMVar claimAllowed ()
    claimAfterClose <- takeMVar callerClaimDone
    callerWinN <- readIORef callerWinCount
    check "caller close wins claim ordering" (callerClose == Right () && case claimAfterClose of Left Transfer.AlreadyClaimed -> callerWinN == 1; _ -> False)
    coreWinCount <- newIORef (0 :: Int)
    coreWinInput <- openBinaryFile (root </> "selected-input") ReadMode
    coreWin <- TransferInternal.fixtureTicketWithClose coreWinInput (modifyIORef' coreWinCount (+1) >> hClose coreWinInput)
    coreWinToken <- TransferInternal.newOwnerToken
    closeAllowed <- newEmptyMVar
    coreCallerDone <- newEmptyMVar
    _ <- forkIO (takeMVar closeAllowed >> Transfer.closeCallerTransfer coreWin >>= putMVar coreCallerDone)
    coreClaim <- TransferInternal.claimTransfer coreWinToken coreWin
    putMVar closeAllowed ()
    coreCallerResult <- takeMVar coreCallerDone
    case coreClaim of
     Left _ -> check "core claim wins close ordering" False
     Right capability -> do
      let callerDenied = coreCallerResult
      duplicate <- TransferInternal.claimTransfer coreWinToken coreWin
      coreClose <- TransferInternal.closeCoreTransfer capability
      coreAgain <- TransferInternal.closeCoreTransfer capability
      coreWinN <- readIORef coreWinCount
      check "core claim wins close ordering" (callerDenied == Left Transfer.WrongOwner && case duplicate of Left Transfer.AlreadyClaimed -> coreClose == Right () && coreAgain == Right () && coreWinN == 1; _ -> False)
    retainedOwner <- newOwner
    retainedCount <- newIORef (0 :: Int)
    retainedInput <- openBinaryFile (root </> "selected-input") ReadMode
    retainedTicket <- TransferInternal.fixtureTicketWithClose retainedInput (modifyIORef' retainedCount (+1) >> hClose retainedInput)
    retainedToken <- TransferInternal.newOwnerToken
    claimed <- TransferInternal.claimTransfer retainedToken retainedTicket
    case claimed of
     Left _ -> check "retained core recovery claim" False
     Right capability -> do
      OwnerCore.retainCore retainedOwner capability
      OwnerCore.quarantine retainedOwner Nothing ["fixture-recovery"]
      closed <- OwnerCore.closeRetainedCore retainedOwner
      again <- OwnerCore.closeRetainedCore retainedOwner
      count <- readIORef retainedCount
      retainedState <- status retainedOwner
      check "guarded retained close under quarantine" (closed == Just (Right ()) && again == Just (Right ()) && count == 1 && case retainedState of Quarantined _ -> True; _ -> False)
    uncertainCount <- newIORef (0 :: Int)
    uncertainInput <- openBinaryFile (root </> "selected-input") ReadMode
    uncertainTicket <- TransferInternal.fixtureTicketWithClose uncertainInput (modifyIORef' uncertainCount (+1) >> hClose uncertainInput >> ioError (userError "fixture close failed after close"))
    uncertainFirst <- Transfer.closeCallerTransfer uncertainTicket
    uncertainAgain <- Transfer.closeCallerTransfer uncertainTicket
    uncertainState <- Transfer.transferDisposition uncertainTicket
    uncertainN <- readIORef uncertainCount
    check "uncertain close never retried" (uncertainFirst == Left Transfer.CloseFailed && uncertainAgain == Left Transfer.ClosingOrUncertain && uncertainState == Transfer.TransferUncertain && uncertainN == 1)
    asyncCloseCount <- newIORef (0 :: Int)
    asyncCloseInput <- openBinaryFile (root </> "selected-input") ReadMode
    asyncCloseTicket <- TransferInternal.fixtureTicketWithClose asyncCloseInput (modifyIORef' asyncCloseCount (+1) >> hClose asyncCloseInput >> throwIO ThreadKilled)
    asyncCloseResult <- try (Transfer.closeCallerTransfer asyncCloseTicket) :: IO (Either SomeException (Either Transfer.TransferError ()))
    asyncCloseState <- Transfer.transferDisposition asyncCloseTicket
    asyncCloseAgain <- Transfer.closeCallerTransfer asyncCloseTicket
    asyncCloseN <- readIORef asyncCloseCount
    check "async close records uncertainty before rethrow" (isAsyncResult asyncCloseResult && asyncCloseState == Transfer.TransferUncertain && asyncCloseAgain == Left Transfer.ClosingOrUncertain && asyncCloseN == 1)
    faultOriginalAsync <- startupFault exe root (toException ThreadKilled) (toException (userError "cleanup sync")) (toException ThreadKilled)
    check "startup original async beats cleanup sync" faultOriginalAsync
    faultBothAsync <- startupFault exe root (toException ThreadKilled) (toException UserInterrupt) (toException ThreadKilled)
    check "startup original async beats cleanup async" faultBothAsync
    faultCleanupAsync <- startupFault exe root (toException (userError "startup sync")) (toException ThreadKilled) (toException ThreadKilled)
    check "startup cleanup async beats original sync" faultCleanupAsync
  _ -> exitFailure
tempRoot :: IO FilePath
tempRoot = do
 base <- getTemporaryDirectory
 (path,h) <- openTempFile base "warlock-custody-"
 hClose h
 removeFile path
 createDirectory path
 pure path
isAsyncResult :: Either SomeException a -> Bool
isAsyncResult value = case value of
 Left err -> case (fromException err :: Maybe SomeAsyncException) of Just _ -> True; Nothing -> False
 Right _ -> False

startupFault :: FilePath -> FilePath -> SomeException -> SomeException -> SomeException -> IO Bool
startupFault exe root original cleanup expected = do
 faultOwner <- newOwner
 count <- newIORef (0 :: Int)
 input <- openBinaryFile (root </> "selected-input") ReadMode
 ticket <- TransferInternal.fixtureTicketWithClose input (modifyIORef' count (+1) >> hClose input >> throwIO cleanup)
 deadline <- deadlineAfter 2000000
 case deadline of
  Left _ -> pure False
  Right d -> do
   result <- try (runSelectedFixtureHook faultOwner (selectedTicketFixture exe ["--fixture","ok"] ticket) 4096 d awaitLeader (\stage -> if stage == "before-spawn" then throwIO original else pure ())) :: IO (Either SomeException (Either ToolError Captured))
   faults <- OwnerCore.startupFailures faultOwner
   state <- status faultOwner
   disposition <- Transfer.transferDisposition ticket
   callerClose <- Transfer.closeCallerTransfer ticket
   retained <- OwnerCore.closeRetainedCore faultOwner
   attempts <- readIORef count
   let originalMatches = case result of Left ex -> sameExceptionKind expected ex; Right _ -> False
       bothRetained = case faults of (one,Just two):_ -> sameExceptionKind original one && sameExceptionKind cleanup two; _ -> False
       quarantined = case state of Quarantined _ -> True; _ -> False
   pure (originalMatches && bothRetained && quarantined && disposition == Transfer.TransferUncertain && callerClose == Left Transfer.ClosingOrUncertain && retained == Just (Left Transfer.ClosingOrUncertain) && attempts == 1)

sameExceptionKind :: SomeException -> SomeException -> Bool
sameExceptionKind expected actual = case (fromException expected :: Maybe AsyncException, fromException actual :: Maybe AsyncException) of
 (Just first,Just second) -> first == second
 (Nothing,Nothing) -> case (fromException expected :: Maybe IOException, fromException actual :: Maybe IOException) of (Just first,Just second) -> displayException first == displayException second; _ -> False
 _ -> False
