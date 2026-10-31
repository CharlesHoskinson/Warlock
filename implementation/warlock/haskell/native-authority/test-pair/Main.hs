{-# LANGUAGE OverloadedStrings #-}
module Main (main) where
import Control.Exception (AsyncException(ThreadKilled),SomeException,fromException,mask_,throwIO,try)
import Control.Monad (unless)
import qualified Data.ByteString as B
import qualified Data.ByteString.Char8 as C
import qualified Data.Text as T
import System.Directory (createDirectory,listDirectory)
import System.Environment (getArgs)
import System.FilePath ((</>))
import System.Posix.Files (setFileMode)
import System.Posix.IO (OpenMode(ReadOnly),openFd,defaultFileFlags,closeFd)
import qualified Warlock.Native.Cancellation.PairStore as P
import qualified Warlock.Native.Cancellation.HostGuard as G
import qualified Warlock.Native.Cancellation.Selection as S
import qualified Warlock.Native.Cancellation.AdmissionShape as A
import Warlock.Protocol.Identity (Binding,Counter,parseCounter,binding,context)
import Warlock.Protocol.Custody (Intent,Operation(Restore),intent)

check :: String -> Bool -> IO ()
check label ok = unless ok (ioError (userError label))
right :: Show e => Either e a -> IO a
right = either (ioError . userError . show) pure
number :: Integer -> IO Counter
number n = right (parseCounter True (T.pack (show n)))
prepare :: FilePath -> String -> (String -> IO ()) -> IO (P.PairStore,Binding,Intent,S.Selection,FilePath)
prepare root label fault = prepareWithHooks root label fault (\_ -> pure ())
prepareWithHooks :: FilePath -> String -> (String -> IO ()) -> (String -> IO ()) -> IO (P.PairStore,Binding,Intent,S.Selection,FilePath)
prepareWithHooks root label admissionsFault companionsFault = mask_ $ do
 let directory=root </> label
 createDirectory directory
 setFileMode directory 0o700
 zero <- number 0; one <- number 1; two <- number 2; three <- number 3
 scope <- number 5; generation <- number 6; publication <- number 7; lease <- number 8
 req <- number 11; gen <- number 12; inc <- number 13; output <- number 14; revision <- number 15
 bound <- right (binding one two three)
 ctx <- right (context bound one three output revision)
 action <- right (intent bound req gen inc ctx Restore)
 store <- P.newPairStoreWithHooks zero bound admissionsFault companionsFault
 fd <- openFd directory ReadOnly defaultFileFlags
 accepted <- P.offerNamespace store fd
 unless accepted (closeFd fd >> ioError (userError "namespace not adopted"))
 P.initializePairStore store >>= right
 view <- P.installView store scope generation publication lease "restore-control" action >>= right
 captured <- P.captureSelection store view >>= right
 pure (store,bound,action,captured,directory)
main :: IO ()
main = do
 args <- getArgs
 root <- case args of [p] -> pure p; _ -> ioError (userError "owned empty fixture root required")
 (store,_,action,captured,path) <- prepare root "positive" (\_ -> pure ())
 P.publishCaptured store captured >>= right
 queued <- P.pairStatus store
 check "actual queue insertion after writes" (map snd (P.transactions queued)==[P.Queued])
 duplicate <- P.publishCaptured store captured
 check "duplicate is refused" (duplicate==Left P.InvalidSelection)
 unchanged <- P.pairStatus store
 check "duplicate preserves original queued work" (unchanged==queued)
 first <- P.claimPreparedWork store >>= right
 work <- case first of Just value -> pure value; Nothing -> ioError (userError "no queued work")
 check "exact original intent and deadline" (P.workIntent work==action && P.workDeadline work==S.selectionDeadline captured)
 let name=C.unpack (P.workKey work) ++ ".json"
 pending <- B.readFile (path </> "admissions-v1" </> name)
 companion <- B.readFile (path </> "cancellation-admissions-v1" </> name)
 check "actual persisted Pending" ("\"status\":\"Pending\"" `B.isInfixOf` pending)
 check "actual persisted Submitted" ("\"state\":\"Submitted\"" `B.isInfixOf` companion)
 second <- P.claimPreparedWork store >>= right
 check "one queue claim only" (case second of Nothing -> True; Just _ -> False)
 P.closeStorage store >>= right
 checkPending <- B.readFile (path </> "admissions-v1" </> name)
 check "storage close preserves durable Pending" (checkPending==pending)

 (busyStore,_,_,busyCapture,busyPath) <- prepare root "kernel-busy" (\_ -> pure ())
 zero <- number 0
 other <- G.newHostGuard zero
 fd <- openFd busyPath ReadOnly defaultFileFlags
 accepted <- G.offerNamespace other fd
 unless accepted (closeFd fd >> ioError (userError "other guard not adopted"))
 blocked <- G.withHostGuard other (\_ -> P.publishCaptured busyStore busyCapture)
 check "actual kernel contention before spend" (blocked==Right (Left (P.GuardFailure G.Busy)))
 P.publishCaptured busyStore busyCapture >>= right
 P.closeStorage busyStore >>= right
 _ <- G.retireHostGuard other >>= right

 (badStore,_,_,badCapture,badPath) <- prepare root "corrupt-inventory" (\_ -> pure ())
 let unrelated=badPath </> "admissions-v1" </> "unexpected"
 B.writeFile unrelated "retained corruption"
 refused <- P.publishCaptured badStore badCapture
 check "full inventory refuses unrelated corruption" (case refused of Left (P.StorageFailure _) -> True; _ -> False)
 badStatus <- P.pairStatus badStore
 check "corruption cannot enqueue" (null (P.transactions badStatus) && P.pairPhase badStatus==P.Quarantined)
 P.closeStorage badStore >>= right
 retained <- B.readFile unrelated
 check "corrupt evidence preserved" (retained=="retained corruption")

 (legacyStore,_,_,legacyCapture,legacyPath) <- prepare root "schema1-inventory" (\_ -> pure ())
 let legacyRaw="{\"schema\":1,\"binding\":{\"lifetime\":\"1\",\"session\":\"2\",\"frontend\":\"3\"},\"intent\":{\"request\":\"111\",\"generation\":\"112\",\"incarnation\":\"99\",\"operation\":\"restore\",\"context\":{\"lifetime\":\"1\",\"epoch\":\"3\",\"output\":\"14\",\"revision\":\"15\"}},\"status\":\"Pending\"}"
 legacyInfo <- right (A.decodeAdmission legacyRaw)
 check "legacy schema remains informationally recognizable" (A.admissionSchema legacyInfo==1)
 let legacyFile=legacyPath </> "admissions-v1" </> (C.unpack (A.admissionKey legacyInfo) ++ ".json")
 B.writeFile legacyFile legacyRaw
 setFileMode legacyFile 0o600
 legacyRefused <- P.publishCaptured legacyStore legacyCapture
 check "active directory still requires schema2 Pending" (legacyRefused==Left P.InvalidInventory)
 legacyStatus <- P.pairStatus legacyStore
 check "schema1 cannot authorize a queue claim" (null (P.transactions legacyStatus) && P.pairPhase legacyStatus==P.Quarantined)
 P.closeStorage legacyStore >>= right
 preservedLegacy <- B.readFile legacyFile
 check "legacy evidence remains byte-exact" (preservedLegacy==legacyRaw)

 (faultStore,_,_,faultCapture,faultPath) <- prepare root "after-reserved" (\stage -> if stage=="creating-temp" then throwIO ThreadKilled else pure ())
 interrupted <- try (P.publishCaptured faultStore faultCapture) :: IO (Either SomeException (Either P.PairError ()))
 check "original async propagated" (case interrupted of
  Left err -> case fromException err of Just ThreadKilled -> True; _ -> False
  Right _ -> False)
 faultStatus <- P.pairStatus faultStore
 check "partial durable transaction retained" (P.pairPhase faultStatus==P.Quarantined && map snd (P.transactions faultStatus)==[P.ReservedStored] && P.exceptionCount faultStatus>0)
 escaped <- P.claimPreparedWork faultStore
 check "no work after interrupted publication" (case escaped of Left P.Poisoned -> True; _ -> False)
 contender <- G.newHostGuard zero
 contenderFd <- openFd faultPath ReadOnly defaultFileFlags
 adopted <- G.offerNamespace contender contenderFd
 unless adopted (closeFd contenderFd >> ioError (userError "contender not adopted"))
 released <- G.withHostGuard contender (\_ -> pure True)
 check "interrupted transaction released actual kernel lock" (released==Right True)
 P.closeStorage faultStore >>= right
 _ <- G.retireHostGuard contender >>= right

 (syncStore,_,_,syncCapture,syncPath) <- prepare root "sync-after-reserved" (\stage -> if stage=="creating-temp" then ioError (userError "synchronous pending failure") else pure ())
 syncResult <- P.publishCaptured syncStore syncCapture
 check "ordinary pending failure returns explicit error" (case syncResult of Left _ -> True; Right _ -> False)
 syncStatus <- P.pairStatus syncStore
 print syncStatus
 check "ordinary failure preserves confirmed Reserved stage" (P.pairPhase syncStatus==P.Quarantined && map snd (P.transactions syncStatus)==[P.ReservedStored])
 syncAdmissions <- listDirectory (syncPath </> "admissions-v1")
 syncCompanions <- listDirectory (syncPath </> "cancellation-admissions-v1")
 check "ordinary failure retains actual partial pair" (null syncAdmissions && length syncCompanions==1)
 syncWork <- P.claimPreparedWork syncStore
 check "ordinary failure cannot yield work" (case syncWork of Left P.Poisoned -> True; _ -> False)
 P.closeStorage syncStore >>= right

 let submittedPath=root </> "sync-after-pending"
     failSubmitted stage = if stage/="creating-temp" then pure () else do
      names <- listDirectory (submittedPath </> "admissions-v1")
      unless (null names) (ioError (userError "synchronous Submitted failure"))
 (submittedStore,_,_,submittedCapture,_) <- prepareWithHooks root "sync-after-pending" (\_ -> pure ()) failSubmitted
 submittedResult <- P.publishCaptured submittedStore submittedCapture
 check "ordinary Submitted failure returns explicit error" (case submittedResult of Left _ -> True; Right _ -> False)
 submittedStatus <- P.pairStatus submittedStore
 print submittedStatus
 check "ordinary failure preserves confirmed Pending stage" (P.pairPhase submittedStatus==P.Quarantined && map snd (P.transactions submittedStatus)==[P.PendingStored])
 actualPending <- listDirectory (submittedPath </> "admissions-v1")
 actualCompanion <- listDirectory (submittedPath </> "cancellation-admissions-v1")
 check "later ordinary failure retains both actual records" (length actualPending==1 && actualPending==actualCompanion)
 P.closeStorage submittedStore >>= right
 putStrLn "pair store component smoke controls complete"
