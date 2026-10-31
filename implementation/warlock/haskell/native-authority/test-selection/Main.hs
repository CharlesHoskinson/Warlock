{-# LANGUAGE OverloadedStrings #-}
-- Component fixture: trusted claim is an explicit input premise, not physical
-- user input, a persisted AdmissionLease, native authority or ACK evidence.
module Main (main) where
import Control.Concurrent (forkFinally,killThread,newEmptyMVar,putMVar,takeMVar,threadDelay)
import Control.Monad (forM_,unless)
import qualified Data.ByteString as B
import qualified Data.ByteString.Char8 as C
import qualified Data.Text as T
import qualified Data.Text.Encoding as TE
import System.Directory (createDirectory)
import System.Environment (getArgs)
import System.FilePath ((</>))
import System.Timeout (timeout)
import Warlock.Native.Cancellation.Selection
import Warlock.Native.Cancellation.AdmissionBytes
import Warlock.Protocol.Custody (Intent,Operation(..),intent)
import Warlock.Protocol.Identity (Binding,Counter,addCounter,binding,context,frontend,lifetime,parseCounter,renderCounter)

check :: String -> Bool -> IO ()
check label ok = unless ok (ioError (userError label))
right :: Show e => Either e a -> IO a
right = either (ioError . userError . show) pure
number :: Integer -> IO Counter
number n = right (parseCounter False (T.pack (show n)))
makeBinding :: Integer -> Integer -> Integer -> IO Binding
makeBinding life sess front = do l <- number life; s <- number sess; f <- number front; right (binding l s f)
makeIntent :: Binding -> Integer -> Integer -> Integer -> Integer -> Integer -> IO Intent
makeIntent b req gen inc out rev = do
 r <- number req; g <- number gen; i <- number inc; o <- number out; v <- number rev
 c <- right (context b (lifetime b) (frontend b) o v)
 right (intent b r g i c Restore)
makeClaim :: Binding -> Intent -> Integer -> Integer -> Integer -> Integer -> T.Text -> IO ViewClaim
makeClaim b act ident gen pub lease control = do
 i <- number ident; g <- number gen; p <- number pub; l <- number lease
 right (viewClaim b i g p l control act)
newCaptured :: Binding -> Intent -> IO (SelectionRegistry,ViewClaim,Selection)
newCaptured b act = do
 reg <- newSelectionRegistry
 claim <- makeClaim b act 11 12 13 14 "restore-control"
 _ <- installCurrentView reg claim >>= right
 selected <- captureSelection reg claim >>= right
 pure (reg,claim,selected)

-- Each artifact is derived from an independently captured and spent actual
-- selection, never a fabricated Selection or JSON-mutated producer result.
writeVariant :: FilePath -> String -> Binding -> Intent -> ViewClaim -> IO ()
writeVariant output label b action claim = do
 registry <- newSelectionRegistry
 _ <- installCurrentView registry claim >>= right
 selected <- captureSelection registry claim >>= right
 spent <- spendSelection registry (selectionId selected) b action >>= right
 pair <- right (encodePair spent action)
 B.writeFile (output </> (label ++ "-pending.json")) (pendingBytes pair)
 B.writeFile (output </> (label ++ "-submitted.json")) (submittedBytes pair)
 B.writeFile (output </> (label ++ "-reserved.json")) (reservedBytes pair)
 B.writeFile (output </> (label ++ "-key.txt")) (pairKey pair)
 B.writeFile (output </> (label ++ "-deadline.txt")) (TE.encodeUtf8 (renderCounter (selectionDeadline spent)))

main :: IO ()
main = do
 args <- getArgs
 root <- case args of [dir] -> pure dir; _ -> ioError (userError "root-owned empty output directory required")
 b <- makeBinding 1 2 3
 act <- makeIntent b 6 7 8 9 10
 (registry,claim,selected) <- newCaptured b act
 exactD <- right (addCounter (selectionAccepted selected) 2000000000)
 check "actual monotonic A + original two seconds" (selectionDeadline selected == exactD)
 expectedScope <- (,) <$> number 11 <*> number 12
 expectedPublication <- number 13; expectedLease <- number 14
 check "current claim fields" (selectionBinding selected == b && selectionIntent selected == act && selectionPhase selected == Captured && selectionControl selected == "restore-control" && selectionScope selected == expectedScope && selectionPublication selected == expectedPublication && selectionLease selected == expectedLease)
 let ident = selectionId selected
 check "actual selection ID shape" (T.length ident == 32 && T.all (\c -> (c >= '0' && c <= '9') || (c >= 'a' && c <= 'f')) ident)
 check "captured not encodable" (case encodePair selected act of Left WrongSelection -> True; _ -> False)
 alt <- makeIntent b 16 7 8 9 10
 wrong <- spendSelection registry ident b alt
 check "wrong exact intent refuses without consuming" (wrong == Left ForeignSelection)
 spent <- spendSelection registry ident b act >>= right
 check "valid current capture spends" (selectionPhase spent == Spent && selectionDeadline spent == selectionDeadline selected)
 duplicate <- spendSelection registry ident b act
 check "one use" (duplicate == Left AlreadySpent)
 check "spent cannot encode different intent" (case encodePair spent alt of Left WrongSelection -> True; _ -> False)
 pair <- right (encodePair spent act)
 check "legacy key hex length" (B.length (pairKey pair) == 64 && B.all (\w -> (w >= 48 && w <= 57) || (w >= 97 && w <= 102)) (pairKey pair))
 check "pending bounds" (B.length (pendingBytes pair) <= 4096 && B.length (reservedBytes pair) <= 8192 && B.length (submittedBytes pair) <= 8192)
 -- The independent root validator reads these actual producer outputs; it
 -- must check process exit and hash every file before using them.
 let output = root </> "producer-output"
 createDirectory output
 B.writeFile (output </> "key.txt") (pairKey pair)
 B.writeFile (output </> "pending.json") (pendingBytes pair)
 B.writeFile (output </> "reserved.json") (reservedBytes pair)
 B.writeFile (output </> "submitted.json") (submittedBytes pair)
 let expected = C.concat ["{\"binding\":{\"lifetime\":\"1\",\"session\":\"2\",\"frontend\":\"3\"},\"intent\":{\"request\":\"6\",\"generation\":\"7\",\"incarnation\":\"8\",\"operation\":\"restore\",\"context\":{\"lifetime\":\"1\",\"epoch\":\"3\",\"output\":\"9\",\"revision\":\"10\"}},\"deadline\":\"", TE.encodeUtf8 (renderCounter (selectionDeadline spent)),"\"}"]
 B.writeFile (output </> "expected.json") expected
 -- Root can compare each valid typed alternate pair to the original using
 -- its unchanged strict reader; scope/control alternatives are valid records,
 -- not automatically proof of a current view.
 forM_ [("request",16,7,8,9,10),("generation",6,17,8,9,10),("incarnation",6,7,18,9,10),("output",6,7,8,19,10),("revision",6,7,8,9,20)] $ \(label,r,g,i,o,v) -> do
  changed <- makeIntent b r g i o v
  changedClaim <- makeClaim b changed 11 12 13 14 "restore-control"
  writeVariant output label b changed changedClaim
 forM_ [("lifetime",21,2,3),("session",1,22,3),("frontend",1,2,23)] $ \(label,life,sess,front) -> do
  changedBinding <- makeBinding life sess front
  changed <- makeIntent changedBinding 6 7 8 9 10
  changedClaim <- makeClaim changedBinding changed 11 12 13 14 "restore-control"
  writeVariant output label changedBinding changed changedClaim
 forM_ [("scope-id",21,12,13,14,"restore-control"),("scope-generation",11,22,13,14,"restore-control"),("publication",11,12,23,14,"restore-control"),("lease",11,12,13,24,"restore-control"),("control",11,12,13,14,"different-control"),("unicode-control",11,12,13,14,"é-restore")] $ \(label,i,g,pub,lease,control) -> do
  changedClaim <- makeClaim b act i g pub lease control
  writeVariant output label b act changedClaim

 -- Every alternate is a valid canonical Restore intent with exactly one
 -- request/generation/incarnation/output/revision difference.
 forM_ [(16,7,8,9,10),(6,17,8,9,10),(6,7,18,9,10),(6,7,8,19,10),(6,7,8,9,20)] $ \(r,g,i,o,v) -> do
  changed <- makeIntent b r g i o v
  (owner,_,capture) <- newCaptured b act
  rejection <- spendSelection owner (selectionId capture) b changed
  check "different valid intent refuses" (rejection == Left ForeignSelection)
  actual <- spendSelection owner (selectionId capture) b act
  check "refusal retained exact selection" (case actual of Right value -> selectionPhase value == Spent; _ -> False)

 -- All claims are valid; a changed current field invalidates its old capture.
 alternates <- sequence [makeClaim b act 21 12 13 14 "restore-control",makeClaim b act 11 22 13 14 "restore-control",makeClaim b act 11 12 23 14 "restore-control",makeClaim b act 11 12 13 24 "restore-control",makeClaim b act 11 12 13 14 "different-control"]
 forM_ alternates $ \replacement -> do
  (owner,old,capture) <- newCaptured b act
  _ <- installCurrentView owner replacement >>= right
  stale <- spendSelection owner (selectionId capture) b act
  check "changed view refuses old selection" (stale == Left ForeignSelection)
  _ <- installCurrentView owner old >>= right
  revived <- spendSelection owner (selectionId capture) b act
  check "old view ABA cannot revive selection" (revived == Left ForeignSelection)

 foreignBinding <- makeBinding 1 2 30
 foreignAction <- makeIntent foreignBinding 6 7 8 9 10
 (foreignReg,_,foreignCapture) <- newCaptured b act
 foreignResult <- spendSelection foreignReg (selectionId foreignCapture) foreignBinding foreignAction
 check "foreign binding refused" (foreignResult == Left ForeignSelection)
 acceptedAfterForeign <- spendSelection foreignReg (selectionId foreignCapture) b act
 check "foreign attempt did not consume" (case acceptedAfterForeign of Right _ -> True; Left _ -> False)

 i <- number 11; g <- number 12; p <- number 13; l <- number 14
 check "NUL control refused" (viewClaim b i g p l "bad\0control" act == Left InvalidClaim)
 check "empty control refused" (viewClaim b i g p l "" act == Left InvalidClaim)
 check "UTF8 byte-boundary accepted" (case viewClaim b i g p l (T.replicate 256 "é") act of Right _ -> True; _ -> False)
 check "UTF8 bytes above 512 refused" (viewClaim b i g p l (T.replicate 257 "é") act == Left InvalidClaim)
 check "foreign typed intent cannot make claim" (viewClaim b i g p l "control" foreignAction == Left InvalidClaim)

 (retiredReg,_,retired) <- newCaptured b act
 _ <- retireCurrentView retiredReg >>= right
 closed <- spendSelection retiredReg (selectionId retired) b act
 check "retired view cannot spend" (closed == Left ForeignSelection)
 (expiryReg,_,expiring) <- newCaptured b act
 -- Root-run test waits past the already captured original D; it never renews D.
 threadDelay 2100000
 expired <- spendSelection expiryReg (selectionId expiring) b act
 check "original D expires" (expired == Left Expired)

 capacityReg <- newSelectionRegistry
 _ <- installCurrentView capacityReg claim >>= right
 noncurrent <- makeClaim b act 99 12 13 14 "restore-control"
 forM_ [1..20 :: Int] $ \_ -> do
  rejected <- captureSelection capacityReg noncurrent
  check "noncurrent capture refuses" (rejected == Left NoCurrentView)
 captures <- mapM (\_ -> captureSelection capacityReg claim >>= right) [1..16 :: Int]
 check "sixteen actual captures" (length captures == 16)
 overflow <- captureSelection capacityReg claim
 check "seventeenth refused" (overflow == Left Capacity)
 done <- newEmptyMVar
 worker <- forkFinally (captureSelection capacityReg claim) (putMVar done)
 answer <- timeout 1000000 (takeMVar done)
 case answer of
  Nothing -> do killThread worker; _ <- timeout 1000000 (takeMVar done); ioError (userError "owned wrong-thread worker timeout")
  Just (Right (Left WrongThread)) -> pure ()
  _ -> ioError (userError "foreign thread not refused")
 C.putStrLn "selection encoding component controls complete"
