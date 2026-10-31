{-# LANGUAGE OverloadedStrings #-}
module Main (main) where
import Control.Exception (mask_)
import Control.Monad (foldM,unless)
import qualified Data.Text as T
import System.Directory (listDirectory)
import System.Environment (getArgs)
import System.FilePath ((</>))
import System.Posix.Directory (createDirectory)
import System.Posix.IO (OpenMode(ReadOnly),openFd,closeFd,defaultFileFlags)
import qualified Warlock.Native.Cancellation.PairStore as P
import qualified Warlock.Native.Cancellation.Selection as S
import Warlock.Protocol.Identity (Counter,Binding,parseCounter,binding,context)
import Warlock.Protocol.Custody (Intent,Operation(Restore),intent)

check :: String -> Bool -> IO ()
check label ok = unless ok (ioError (userError label))
right :: Show e => Either e a -> IO a
right = either (ioError . userError . show) pure
number :: Integer -> IO Counter
number value = right (parseCounter True (T.pack (show value)))
data Witness = Witness !Integer !Integer !Integer !Integer !Integer deriving Show
plus :: Witness -> Witness -> Witness
plus (Witness a b c d e) (Witness f g h i j) = Witness (a+f) (b+g) (c+h) (d+i) (e+j)
zero :: Witness
zero= Witness 0 0 0 0 0
next :: Integer -> Integer
next value=(value*1103515245+12345) `mod` 2147483648
actionFor :: Binding -> Integer -> IO Intent
actionFor bound step = do
 request <- number (100+step); generation <- number (200+step); incarnation <- number (300+step)
 life <- number 2; epoch <- number 4; output <- number 9; revision <- number 10
 ctx <- right (context bound life epoch output revision)
 right (intent bound request generation incarnation ctx Restore)
viewFor :: P.PairStore -> Intent -> Integer -> IO S.ViewClaim
viewFor store action publication = do
 scope <- number 11; generation <- number 12; pub <- number publication; lease <- number 14
 P.installView store scope generation pub lease "restore-control" action >>= right
emptyClaim :: P.PairStore -> IO ()
emptyClaim store = do
 result <- P.claimPreparedWork store >>= right
 check "no unmodelled queued work" (case result of Nothing -> True; Just _ -> False)
verify :: P.PairStore -> FilePath -> Integer -> IO ()
verify store path expected = do
 status <- P.pairStatus store
 admissions <- listDirectory (path </> "admissions-v1")
 companions <- listDirectory (path </> "cancellation-admissions-v1")
 check "actor remains available" (P.pairPhase status==P.Available)
 check "filesystem and model transaction counts agree" (toInteger (length admissions)==expected && toInteger (length companions)==expected && toInteger (length (P.transactions status))==expected)
 check "every successful action claimed exactly once" (all ((==P.Claimed) . snd) (P.transactions status))
 emptyClaim store
trace :: FilePath -> Integer -> IO Witness
trace root initial = do
 let path=root </> ("seed-" ++ show initial)
 createDirectory path 0o700
 first <- number 1; life <- number 2; sessionValue <- number 3; front <- number 4
 bound <- right (binding life sessionValue front)
 store <- P.newPairStore first bound
 mask_ $ do
  fd <- openFd path ReadOnly defaultFileFlags
  accepted <- P.offerNamespace store fd
  unless accepted (closeFd fd >> ioError (userError "namespace offer refused"))
 P.initializePairStore store >>= right
 let loop step rng count previous witnessed
      | step==12 = do
         verify store path count
         P.closeStorage store >>= right
         admissions <- listDirectory (path </> "admissions-v1")
         check "storage close preserves all pending evidence" (toInteger (length admissions)==count)
         pure witnessed
      | otherwise = do
         let randomValue=next rng; operation=randomValue `mod` 6
         putStrLn ("seed=" ++ show initial ++ " step=" ++ show step ++ " operation=" ++ show operation)
         before <- P.pairStatus store
         action <- actionFor bound step
         (newCount,newPrevious,observed) <- case operation of
          1 -> positive step action count previous
          2 -> positive step action count previous
          3 -> case previous of
           Nothing -> emptyClaim store >> pure (count,previous,Witness 0 0 0 0 1)
           Just captured -> do
            result <- P.publishCaptured store captured
            check "duplicate refuses without destroying retained work" (result==Left P.InvalidSelection)
            after <- P.pairStatus store
            check "duplicate preserves model state" (after==before)
            pure (count,previous,Witness 0 1 0 0 0)
          4 -> do
           scope <- number 11; generation <- number 12; pub <- number (1000+step); lease <- number 14
           invalid <- P.installView store scope generation pub lease "bad\0control" action
           check "invalid view cannot install" (case invalid of Left _ -> True; Right _ -> False)
           after <- P.pairStatus store
           check "invalid input preserves model state" (after==before)
           pure (count,previous,Witness 0 0 1 0 0)
          5 -> do
           claim <- viewFor store action (1000+step)
           captured <- P.captureSelection store claim >>= right
           _ <- viewFor store action (2000+step)
           refused <- P.publishCaptured store captured
           check "stale selection cannot publish" (case refused of Left _ -> True; Right _ -> False)
           after <- P.pairStatus store
           check "stale selection adds no transaction" (after==before)
           pure (count,previous,Witness 0 0 0 1 0)
          _ -> emptyClaim store >> pure (count,previous,Witness 0 0 0 0 1)
         verify store path newCount
         loop (step+1) randomValue newCount newPrevious (plus witnessed observed)
     positive step action count _ = do
      claim <- viewFor store action (1000+step)
      captured <- P.captureSelection store claim >>= right
      P.publishCaptured store captured >>= right
      queued <- P.pairStatus store
      check "one queued transition" (toInteger (length [() | (_,phase) <- P.transactions queued,phase==P.Queued])==1)
      work <- P.claimPreparedWork store >>= right
      case work of
       Just value -> check "claimed original intent and deadline" (P.workIntent value==action && P.workDeadline value==S.selectionDeadline captured)
       Nothing -> ioError (userError "positive work missing")
      pure (count+1,Just captured,Witness 1 0 0 0 0)
 loop (0 :: Integer) initial 0 Nothing zero
main :: IO ()
main = do
 args <- getArgs
 root <- case args of [path] -> pure path; _ -> ioError (userError "owned empty fixture parent required")
 witnessed <- foldM (\allSeen seed -> plus allSeen <$> trace root seed) zero [20261031..20261038]
 let Witness positive duplicate invalid stale empty = witnessed
 check "all operation classes actually witnessed" (all (>0) [positive,duplicate,invalid,stale,empty])
 putStrLn ("eight seeded traces of twelve steps complete: " ++ show witnessed)
