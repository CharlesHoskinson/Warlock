{-# LANGUAGE OverloadedStrings #-}
-- All input claims below are trusted component premises, not GUI/native proof.
module Main (main) where
import Control.Concurrent (forkFinally, killThread, newEmptyMVar, putMVar, takeMVar, threadDelay)
import Control.Exception (AsyncException(..), try, throwIO)
import Control.Monad (forM_, unless)
import Data.Bits ((.&.))
import Data.IORef (newIORef, readIORef, writeIORef)
import qualified Data.ByteString as B
import qualified Data.ByteString.Char8 as C
import qualified Data.Text as T
import qualified Data.Text.Encoding as TE
import System.Directory (listDirectory)
import System.Environment (getArgs)
import System.FilePath ((</>))
import System.Posix.Directory (createDirectory)
import System.Posix.Files (deviceID, fileID, fileMode, fileOwner, getFdStatus, getFileStatus, linkCount, setFileMode)
import System.Posix.IO (OpenMode(ReadOnly), closeFd, defaultFileFlags, openFd)
import System.Posix.User (getEffectiveUserID)
import System.Timeout (timeout)
import qualified Warlock.Native.Cancellation.HostGuard as G
import qualified Warlock.Native.Cancellation.Selection as S
import Warlock.Native.Cancellation.PairStore
import Warlock.Protocol.Custody (Intent, Operation(..), intent)
import Warlock.Protocol.Identity (Binding, Counter, addCounter, binding, context, frontend, lifetime, parseCounter, renderCounter)

check :: String -> Bool -> IO ()
check label value = unless value (ioError (userError label))
right :: Show e => Either e a -> IO a
right = either (ioError . userError . show) pure
n :: Integer -> IO Counter
n i = right (parseCounter False (T.pack (show i)))
inputs :: IO (Counter,Binding,Intent)
inputs = do
 initial <- n 1; l <- n 2; s <- n 3; f <- n 4
 b <- right (binding l s f)
 r <- n 6; g <- n 7; i <- n 8; o <- n 9; v <- n 10
 ctx <- right (context b (lifetime b) (frontend b) o v)
 action <- right (intent b r g i ctx Restore)
 pure (initial,b,action)
mkdir :: FilePath -> IO ()
mkdir p = createDirectory p 0o700
prepare :: FilePath -> IO (PairStore,Binding,Intent)
prepare path = do
 mkdir path
 (initial,b,action) <- inputs
 p <- newPairStore initial b
 fd <- openFd path ReadOnly defaultFileFlags
 offerNamespace p fd >>= check "namespace offered"
 initializePairStore p >>= right
 pure (p,b,action)
claimView :: PairStore -> Intent -> Integer -> IO S.ViewClaim
claimView p action publication = do
 a <- n 11; b <- n 12; c <- n publication; d <- n 14
 installView p a b c d "restore-control" action >>= right
capture :: PairStore -> Intent -> IO S.Selection
capture p action = claimView p action 13 >>= captureSelection p >>= right
files :: FilePath -> IO ([FilePath],[FilePath])
files p = (,) <$> listDirectory (p </> "admissions-v1") <*> listDirectory (p </> "cancellation-admissions-v1")
metadata :: FilePath -> IO ()
metadata path = do
 uid <- getEffectiveUserID
 st <- getFileStatus path
 fd <- openFd path ReadOnly defaultFileFlags
 held <- getFdStatus fd
 closeFd fd
 check "file uid mode links" (fileOwner st==uid && fileMode st .&. 0o7777==0o600 && linkCount st==1)
 check "name descriptor identity" (deviceID st==deviceID held && fileID st==fileID held)
close :: PairStore -> IO ()
close p = closeStorage p >>= \v -> check "normal close" (v==Right ())
closeAfterFault :: PairStore -> IO ()
closeAfterFault p = do
 outcome <- closeStorage p
 case outcome of
  Right () -> putStrLn "storage close returned success; native retirement remains unproved"
  Left _ -> ioError (userError "storage close refused; retained custody requires root handling")

positive :: FilePath -> IO ()
positive root = do
 let path=root </> "positive"
 mkdir path
 (initial,b,action) <- inputs
 reserved <- newIORef Nothing
 p <- newPairStoreWithHooks initial b (\stage ->
  if stage == "creating-temp"
  then do
   names <- listDirectory (path </> "cancellation-admissions-v1")
   case names of
    [entry] -> B.readFile (path </> "cancellation-admissions-v1" </> entry) >>= writeIORef reserved . Just
    _ -> ioError (userError "reserved snapshot missing")
  else pure ()) (const (pure ()))
 fd <- openFd path ReadOnly defaultFileFlags
 offerNamespace p fd >>= check "positive offer"
 initializePairStore p >>= right
 selected <- capture p action
 deadline <- right (addCounter (S.selectionAccepted selected) 2000000000)
 check "original deadline" (S.selectionDeadline selected==deadline)
 publishCaptured p selected >>= \v -> check "three writes queued" (v==Right ())
 st <- pairStatus p
 check "queued phase" (pairPhase st==Available && map snd (transactions st)==[Queued])
 (a,c) <- files path
 check "one pair" (length a==1 && a==c)
 case a of
  [entry] -> do
   let admission=path </> "admissions-v1" </> entry; companion=path </> "cancellation-admissions-v1" </> entry
   metadata admission; metadata companion
   oldA <- B.readFile admission; oldC <- B.readFile companion
   check "disk bytes nonempty" (not (B.null oldA) && not (B.null oldC))
   publishCaptured p selected >>= \v -> check "duplicate refused" (case v of Left _ -> True; _ -> False)
   B.readFile admission >>= check "duplicate admission intact" . (==oldA)
   B.readFile companion >>= check "duplicate companion intact" . (==oldC)
   candidate <- claimPreparedWork p >>= right
   work <- maybe (ioError (userError "missing work")) pure candidate
   check "work original intent and deadline" (workIntent work==action && workDeadline work==deadline)
   check "work key matches filename" (C.unpack (workKey work) ++ ".json" == entry)
   again <- claimPreparedWork p >>= right
   check "one claim" (case again of Nothing -> True; Just _ -> False)
   -- Independently checked by root's unchanged Python reader, never by this fixture.
   B.writeFile (root </> "actual-key.txt") (workKey work)
   B.writeFile (root </> "actual-deadline.txt") (TE.encodeUtf8 (renderCounter deadline))
   witness <- readIORef reserved >>= maybe (ioError (userError "reserved snapshot absent")) pure
   B.writeFile (root </> "actual-reserved.json") witness
  _ -> ioError (userError "pair filename")
 close p

holder :: FilePath -> Counter -> IO G.HostGuard
holder path initial = do
 g <- G.newHostGuard initial
 fd <- openFd path ReadOnly defaultFileFlags
 G.offerNamespace g fd >>= check "holder namespace"
 pure g
busy :: FilePath -> IO ()
busy root = do
 let path=root </> "busy"
 mkdir path
 (initial,b,action) <- inputs
 p <- newPairStore initial b
 fd <- openFd path ReadOnly defaultFileFlags
 offerNamespace p fd >>= check "busy offer"
 g <- holder path initial
 locked <- G.withHostGuard g $ \_ -> initializePairStore p
 check "independent open-description init busy" (locked==Right (Left (GuardFailure G.Busy)))
 initializePairStore p >>= right
 selected <- capture p action
 blocked <- G.withHostGuard g $ \_ -> publishCaptured p selected
 check "independent open-description publish busy" (blocked==Right (Left (GuardFailure G.Busy)))
 status <- pairStatus p
 check "busy did not reserve" (null (transactions status) && pairPhase status==Available)
 publishCaptured p selected >>= \v -> check "same capture usable after unlock" (v==Right ())
 candidate <- claimPreparedWork p >>= right
 check "busy retry actual work" (case candidate of Just w -> workDeadline w==S.selectionDeadline selected; Nothing -> False)
 close p
 _ <- G.retireHostGuard g >>= right
 pure ()

inventory :: FilePath -> IO ()
inventory root = do
 let path=root </> "inventory"
 (p,_,action) <- prepare path
 selected <- capture p action
 B.writeFile (path </> "admissions-v1" </> "debris") "invalid"
 result <- publishCaptured p selected
 check "unrelated invalid entry refused" (case result of Left _ -> True; _ -> False)
 st <- pairStatus p
 check "no queued work on invalid inventory" (all ((/=Queued) . snd) (transactions st))
 claim <- claimPreparedWork p
 check "no prepared work" (case claim of Right Nothing -> True; Left _ -> True; _ -> False)
 (_,c) <- files path
 check "no companion created" (null c)
 close p

malformed :: FilePath -> IO ()
malformed root = do
 let path=root </> "malformed"
 (p,_,action) <- prepare path
 selected <- capture p action
 let malformedFile=path </> "cancellation-admissions-v1" </> replicate 64 'a' ++ ".json"
 B.writeFile malformedFile "{}"
 setFileMode malformedFile 0o600
 result <- publishCaptured p selected
 check "unrelated malformed companion refused by record validation" (result==Left InvalidInventory)
 (a,_) <- files path
 check "malformed inventory no pending" (null a)
 work <- claimPreparedWork p
 check "malformed inventory no work" (case work of Right Nothing -> True; Left _ -> True; _ -> False)
 closeAfterFault p

stale :: FilePath -> IO ()
stale root = do
 let path=root </> "stale"
 (p,_,action) <- prepare path
 old <- capture p action
 _ <- claimView p action 99
 _ <- claimView p action 13
 invalid <- publishCaptured p old
 check "view ABA cannot publish" (case invalid of Left _ -> True; _ -> False)
 (a,c) <- files path
 check "stale no files" (null a && null c)
 closeAfterFault p

staleClaim :: FilePath -> IO ()
staleClaim root = do
 let path=root </> "stale-claim"
 (p,_,action) <- prepare path
 selected <- capture p action
 publishCaptured p selected >>= \v -> check "stale-claim setup queued" (v==Right ())
 _ <- claimView p action 99
 result <- claimPreparedWork p
 check "stale view cannot claim" (case result of Left _ -> True; Right Nothing -> True; _ -> False)
 st <- pairStatus p
 check "stale view cannot remain queued" (all ((/=Queued) . snd) (transactions st))
 closeAfterFault p

viewFields :: FilePath -> IO ()
viewFields root = do
 let path=root </> "view-fields"
 (p,_,action) <- prepare path
 scopeN <- n 11; generationN <- n 12; publicationN <- n 13; leaseN <- n 14
 forM_ ["", "bad\0control", T.replicate 257 "é"] $ \control -> do
  invalid <- installView p scopeN generationN publicationN leaseN control action
  check "invalid control refused" (case invalid of Left _ -> True; Right _ -> False)
 forM_ [(21,12,13,14,"restore-control"),(11,22,13,14,"restore-control"),
        (11,12,23,14,"restore-control"),(11,12,13,24,"restore-control"),
        (11,12,13,14,"other-control")] $ \(scope,generation,publication,lease,control) -> do
  selected <- capture p action
  a <- n scope; b <- n generation; c <- n publication; d <- n lease
  _ <- installView p a b c d control action >>= right
  result <- publishCaptured p selected
  check "changed view refuses publish" (case result of Left _ -> True; _ -> False)
  (admissions,companions) <- files path
  check "view mismatch no disk writes" (null admissions && null companions)
  status <- pairStatus p
  check "view mismatch no queued work" (all ((/=Queued) . snd) (transactions status))
 -- A valid current selection must still succeed after rejected stale ones.
 current <- capture p action
 publishCaptured p current >>= \result -> check "current after mismatches" (result==Right ())
 close p

foreignCase :: FilePath -> IO ()
foreignCase root = do
 let path=root </> "local"; otherPath=root </> "foreign"
 (p,_,action) <- prepare path
 mkdir otherPath
 (initial,_,_) <- inputs
 l <- n 2; s <- n 31; f <- n 4
 otherBinding <- right (binding l s f)
 r <- n 6; g <- n 7; i <- n 8; o <- n 9; v <- n 10
 ctx <- right (context otherBinding (lifetime otherBinding) (frontend otherBinding) o v)
 otherAction <- right (intent otherBinding r g i ctx Restore)
 other <- newPairStore initial otherBinding
 otherFd <- openFd otherPath ReadOnly defaultFileFlags
 offerNamespace other otherFd >>= check "foreign namespace offer"
 initializePairStore other >>= right
 alien <- capture other otherAction
 publishCaptured p alien >>= \result -> check "foreign binding refused" (case result of Left _ -> True; _ -> False)
 (a,c) <- files path
 check "foreign no mutation" (null a && null c)
 local <- capture p action
 publishCaptured p local >>= \result -> check "local after foreign succeeds" (result==Right ())
 close p
 close other

wrongThread :: FilePath -> IO ()
wrongThread root = do
 let path=root </> "wrong-thread"
 (p,_,action) <- prepare path
 selected <- capture p action
 result <- newEmptyMVar
 worker <- forkFinally (publishCaptured p selected) (putMVar result)
 response <- timeout 1000000 (takeMVar result)
 case response of
  Nothing -> do
   killThread worker
   joined <- timeout 1000000 (takeMVar result)
   check "wrong-thread worker joined" (case joined of Just _ -> True; Nothing -> False)
   ioError (userError "wrong-thread worker timed out")
  Just (Right (Left WrongThread)) -> pure ()
  _ -> ioError (userError "other thread was not refused")
 publishCaptured p selected >>= \v -> check "owner still can publish" (v==Right ())
 close p

expiry :: FilePath -> IO ()
expiry root = do
 let path=root </> "expiry"
 (p,_,action) <- prepare path
 selected <- capture p action
 threadDelay 2100000
 result <- publishCaptured p selected
 check "original deadline refused" (case result of Left _ -> True; _ -> False)
 (a,c) <- files path
 check "expiry no file" (null a && null c)
 closeAfterFault p

reservedCut :: FilePath -> IO ()
reservedCut root = do
 let path=root </> "cut"
 mkdir path
 (initial,b,action) <- inputs
 -- Actual admissions SlotStore hook runs after the Reserved companion write.
 p <- newPairStoreWithHooks initial b (\stage -> if stage=="creating-temp" then throwIO ThreadKilled else pure ()) (const (pure ()))
 fd <- openFd path ReadOnly defaultFileFlags
 offerNamespace p fd >>= check "cut offer"
 initializePairStore p >>= right
 selected <- capture p action
 result <- try (publishCaptured p selected) :: IO (Either AsyncException (Either PairError ()))
 check "original async" (case result of Left ThreadKilled -> True; _ -> False)
 st <- pairStatus p
 check "quarantined after reserved" (pairPhase st==Quarantined && any ((==ReservedStored) . snd) (transactions st))
 (a,c) <- files path
 check "reserved only" (null a && length c==1)
 work <- claimPreparedWork p
 check "no work after cut" (case work of Left _ -> True; Right Nothing -> True; _ -> False)
 -- Separate guard is a genuine independently opened lock description.
 g <- holder path initial
 unlocked <- G.withHostGuard g (\_ -> pure ())
 check "real host lock released" (unlocked==Right ())
 _ <- G.retireHostGuard g >>= right
 closeAfterFault p

laterCut :: FilePath -> Bool -> IO ()
laterCut root submitted = do
 let path=root </> if submitted then "submitted-cut" else "pending-sync-cut"
 mkdir path
 (initial,b,action) <- inputs
 count <- newIORef (0 :: Int)
 let admissionHook stage = if not submitted && stage == "directory-sync" then throwIO ThreadKilled else pure ()
     companionHook stage =
      if stage == "creating-temp"
      then do
       old <- readIORef count
       writeIORef count (old+1)
       if submitted && old==1 then throwIO ThreadKilled else pure ()
      else pure ()
 p <- newPairStoreWithHooks initial b admissionHook companionHook
 fd <- openFd path ReadOnly defaultFileFlags
 offerNamespace p fd >>= check "later cut offer"
 initializePairStore p >>= right
 selected <- capture p action
 outcome <- try (publishCaptured p selected) :: IO (Either AsyncException (Either PairError ()))
 check "later cut original async" (case outcome of Left ThreadKilled -> True; _ -> False)
 st <- pairStatus p
 check "later cut quarantined" (pairPhase st==Quarantined)
 work <- claimPreparedWork p
 check "later cut no queue" (case work of Left _ -> True; Right Nothing -> True; _ -> False)
 (a,c) <- files path
 check "later cut retains companion" (length c==1)
 check "later cut pending visible but not confirmed by stage" (length a==1)
 closeAfterFault p

main :: IO ()
main = do
 args <- getArgs
 case args of
  ["positive",root] -> positive root
  ["busy",root] -> busy root
  ["inventory",root] -> inventory root
  ["malformed",root] -> malformed root
  ["stale",root] -> stale root
  ["stale-claim",root] -> staleClaim root
  ["view-fields",root] -> viewFields root
  ["foreign",root] -> foreignCase root
  ["wrong-thread",root] -> wrongThread root
  ["expiry",root] -> expiry root
  ["reserved-cut",root] -> reservedCut root
  ["pending-sync-cut",root] -> laterCut root False
  ["submitted-cut",root] -> laterCut root True
  _ -> ioError (userError "expected mode and owned empty root")
