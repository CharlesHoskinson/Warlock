{-# LANGUAGE OverloadedStrings #-}
{-# LANGUAGE RankNTypes #-}
-- Internal source fixture only: Provider values are test doubles, not native proof.
module Main (main) where
import Control.Monad (foldM,forM_,unless)
import Control.Concurrent (forkFinally,killThread,newEmptyMVar,putMVar,takeMVar)
import System.Timeout (timeout)
import Control.Exception (AsyncException(ThreadKilled),SomeException,fromException,throw,throwIO,try)
import qualified Data.ByteString.Char8 as B
import Data.IORef (IORef,modifyIORef',newIORef,readIORef)
import qualified Data.Text as T
import Warlock.Native.Cancellation.Internal
import Warlock.Protocol.Identity (Counter,parseCounter,binding,context)
import Warlock.Protocol.Custody (Operation(..),intent)

check :: String -> Bool -> IO ()
check name ok = unless ok (ioError (userError name))
right :: Show e => Either e a -> IO a
right = either (ioError . userError . show) pure
number :: Integer -> IO Counter
number n = right (parseCounter True (T.pack (show n)))

-- All fields are built through the current canonical checked constructors.
makeKey :: Integer -> Integer -> Integer -> Integer -> Integer -> Integer -> Integer -> Integer -> Integer -> Integer -> IO Key
makeKey peer start life sess front req gen inc output rev = do
 p <- number peer; s <- number start; l <- number life; se <- number sess
 f <- number front; r <- number req; g <- number gen; i <- number inc
 o <- number output; v <- number rev
 b <- right (binding l se f)
 c <- right (context b l f o v)
 action <- right (intent b r g i c Restore)
 who <- right (ownerId p s b)
 right (key who 1 action)

facts :: IO Facts
facts = do rev <- number 10; out <- number 9; pure (Facts rev out Applied)
formatNormal :: Format
formatNormal s = Right (B.pack (show (snapshotPhase s)))
newHarness :: Format -> (IORef Int -> IO (Progress,ProviderResult)) -> IO () -> IO (Owner,IORef Int)
newHarness formatter execute onRetire = do
 calls <- newIORef 0
 initial <- number 0
 owner <- newOwner initial formatter (Provider (\_ -> modifyIORef' calls (+1) >> execute calls)) (\_ -> onRetire) >>= right
 pure (owner,calls)
prepareOne :: Owner -> Key -> IO (Snapshot,Deadline)
prepareOne owner k = do
 end <- number 10 >>= right . deadline
 now <- number 1
 z <- number 0
 snap <- prepare owner k end now z z >>= right
 pure (snap,end)

main :: IO ()
main = do
 f <- facts
 let unknownFacts = f {factsReason=Unproven}; refusedFacts = f {factsReason=NativeRefusal}
 k <- makeKey 1 2 3 4 5 6 7 8 9 10
 now <- number 1
 retired <- newIORef (0 :: Int)
 calls <- newIORef (0 :: Int)
 zeroInitial <- number 0
 owner <- newOwner zeroInitial formatNormal
  (Provider (\permit -> do check "permit bound to key" (permitMatches permit k); expectedD <- number 10 >>= right . deadline; check "permit preserves original deadline" (permitDeadline permit == expectedD); modifyIORef' calls (+1); pure (MutationEntered,CommittedObserved f)))
  (\_ -> modifyIORef' retired (+1)) >>= right
 (prepared,d) <- prepareOne owner k
 zero <- number 0
 retry <- prepare owner k d now zero zero >>= right
 check "exact prepare retry stable" (retry == prepared)
 q <- query owner k (snapshotId prepared) d >>= right
 check "prepared query exact" (q == prepared && snapshotPhase q == Prepared)
 pendingPrerequisite <- prerequisiteCommitted owner k (snapshotId prepared) d >>= right
 check "prepared prerequisite blocked" (not pendingPrerequisite)
 wrongThreadDone <- newEmptyMVar
 worker <- forkFinally (query owner k (snapshotId prepared) d) (putMVar wrongThreadDone)
 workerResult <- timeout 1000000 (takeMVar wrongThreadDone)
 case workerResult of
  Nothing -> do killThread worker; _ <- timeout 1000000 (takeMVar wrongThreadDone); ioError (userError "owned worker timeout")
  Just value -> check "wrong thread refused" (case value of Right (Left WrongThread) -> True; _ -> False)
 stillPrepared <- query owner k (snapshotId prepared) d >>= right
 check "wrong thread left state intact" (stillPrepared == prepared)
 terminal <- commit owner k (snapshotId prepared) d now f >>= right
 again <- commit owner k (snapshotId prepared) d now f >>= right
 count <- readIORef calls
 closes <- readIORef retired
 check "one provider callback and immutable commit" (snapshotPhase terminal == Committed && again == terminal && count == 1 && closes == 1)
 lateTerminal <- lateDecision owner k (snapshotId prepared) d >>= right
 check "late decision exact original terminal" (lateTerminal == terminal)
 dependency <- prerequisiteCommitted owner k (snapshotId prepared) d >>= right
 check "committed prerequisite" dependency
 wrongKeyControls owner k prepared d
 validationControls

 (cancelOwner,cancelCalls) <- newHarness formatNormal (\_ -> pure (MutationEntered,CommittedObserved f)) (pure ())
 (p2,d2) <- prepareOne cancelOwner k
 canceled <- cancel cancelOwner k (snapshotId p2) d2 f >>= right
 late <- commit cancelOwner k (snapshotId p2) d2 now f >>= right
 nc <- readIORef cancelCalls
 check "cancel first fences provider" (snapshotPhase canceled == Cancelled && late == canceled && nc == 0)
 blocked <- prerequisiteCommitted cancelOwner k (snapshotId p2) d2 >>= right
 check "cancelled prerequisite blocked" (not blocked)
 let cancelFormat snap = if snapshotPhase snap == Cancelled then Left ResourceFailure else formatNormal snap
 (cancelFaultOwner,cancelFaultCalls) <- newHarness cancelFormat (\_ -> pure (MutationEntered,CommittedObserved f)) (pure ())
 (pc,dc) <- prepareOne cancelFaultOwner k
 lostCancel <- cancel cancelFaultOwner k (snapshotId pc) dc f
 blockedCommit <- commit cancelFaultOwner k (snapshotId pc) dc now f
 cancelFaultCount <- readIORef cancelFaultCalls
 check "cancel before formatting still fences" (lostCancel == Left ResourceFailure && blockedCommit == Left ResourceFailure && cancelFaultCount == 0)

 (expiryOwner,expiryCalls) <- newHarness formatNormal (\_ -> pure (MutationEntered,CommittedObserved f)) (pure ())
 (p3,d3) <- prepareOne expiryOwner k
 end <- number 10
 expSnap <- commit expiryOwner k (snapshotId p3) d3 end f >>= right
 ec <- readIORef expiryCalls
 check "deadline equality refuses" (snapshotPhase expSnap == Refused && ec == 0)

 let faultFormat snap = if snapshotPhase snap == Committed then Left ResourceFailure else formatNormal snap
 (faultOwner,faultCalls) <- newHarness faultFormat (\_ -> pure (MutationEntered,CommittedObserved f)) (pure ())
 (p4,d4) <- prepareOne faultOwner k
 fault <- commit faultOwner k (snapshotId p4) d4 now f >>= right
 fault2 <- commit faultOwner k (snapshotId p4) d4 now f >>= right
 fc <- readIORef faultCalls
 check "proof survives postexecution format fault" (snapshotPhase fault == ExecutionUnknown && snapshotProof fault == Just (Committed,f) && fault2 == fault && fc == 1)

 (unknownOwner,unknownCalls) <- newHarness formatNormal (\_ -> pure (MutationEntered,Uncertain unknownFacts)) (pure ())
 (p5,d5) <- prepareOne unknownOwner k
 unknown <- commit unknownOwner k (snapshotId p5) d5 now f >>= right
 unknown2 <- commit unknownOwner k (snapshotId p5) d5 now f >>= right
 uc <- readIORef unknownCalls
 check "unknown never replays" (snapshotPhase unknown == ExecutionUnknown && unknown2 == unknown && uc == 1)
 unknownPrerequisite <- prerequisiteCommitted unknownOwner k (snapshotId p5) d5 >>= right
 check "unknown prerequisite blocked" (not unknownPrerequisite)
 life <- number 3; sess <- number 4; front <- number 5
 bind <- right (binding life sess front)
 peer <- number 1; start <- number 2
 who <- right (ownerId peer start bind)
 retiredUnknown <- retireOwner unknownOwner who f
 stillBusy <- busy unknownOwner who >>= right
 check "unknown remains retained after owner retirement" (retiredUnknown == Right () && stillBusy)

 (throwOwner,throwCalls) <- newHarness formatNormal (\_ -> ioError (userError "injected provider failure")) (pure ())
 (pt,dt) <- prepareOne throwOwner k
 thrown <- commit throwOwner k (snapshotId pt) dt now f >>= right
 tc <- readIORef throwCalls
 check "provider failure retains unknown" (snapshotPhase thrown == ExecutionUnknown && not (B.null (snapshotReply thrown)) && tc == 1)
 (asyncOwner,asyncCalls) <- newHarness formatNormal (\_ -> throwIO ThreadKilled) (pure ())
 (pa,da) <- prepareOne asyncOwner k
 interrupted <- try (commit asyncOwner k (snapshotId pa) da now f) :: IO (Either SomeException (Either Error Snapshot))
 recovered <- query asyncOwner k (snapshotId pa) da >>= right
 ac <- readIORef asyncCalls
 check "async provider leaves complete unknown" (case interrupted of
  Left e -> (fromException e :: Maybe AsyncException) == Just ThreadKilled && snapshotPhase recovered == ExecutionUnknown && not (B.null (snapshotReply recovered)) && ac == 1
  Right _ -> False)
 (lazyOwner,lazyCalls) <- newHarness formatNormal (\_ -> pure (MutationEntered,throw (userError "deferred provider proof"))) (pure ())
 (lazyPrepared,lazyD) <- prepareOne lazyOwner k
 lazyOutcome <- commit lazyOwner k (snapshotId lazyPrepared) lazyD now f >>= right
 lazyRepeated <- commit lazyOwner k (snapshotId lazyPrepared) lazyD now f >>= right
 lazyCount <- readIORef lazyCalls
 check "deferred provider result retains unknown without replay" (snapshotPhase lazyOutcome == ExecutionUnknown && snapshotExecution lazyOutcome == Nothing && not (B.null (snapshotReply lazyOutcome)) && lazyRepeated == lazyOutcome && lazyCount == 1)
 (refusedOwner,refusedCalls) <- newHarness formatNormal (\_ -> pure (NoMutation,RefusedBefore refusedFacts)) (pure ())
 (pr,dr) <- prepareOne refusedOwner k
 rejected <- commit refusedOwner k (snapshotId pr) dr now f >>= right
 rc <- readIORef refusedCalls
 check "provider refusal retained" (snapshotPhase rejected == Refused && rc == 1)
 check "no-mutation execution evidence retained" (case snapshotExecution rejected of
  Just evidence -> executionProgress evidence == NoMutation && executionResult evidence == RefusedBefore refusedFacts
  Nothing -> False)
 (compensatedOwner,_) <- newHarness formatNormal (\_ -> pure (MutationEntered,RefusedCompensated refusedFacts)) (pure ())
 (compensatedPrepared,compensatedD) <- prepareOne compensatedOwner k
 compensated <- commit compensatedOwner k (snapshotId compensatedPrepared) compensatedD now f >>= right
 check "compensation evidence survives terminal publication" (snapshotPhase compensated == Refused && snapshotProof compensated == Nothing && case snapshotExecution compensated of
  Just evidence -> executionProgress evidence == MutationEntered && executionResult evidence == RefusedCompensated refusedFacts
  Nothing -> False)
 refusedPrerequisite <- prerequisiteCommitted refusedOwner k (snapshotId pr) dr >>= right
 check "refused prerequisite blocked" (not refusedPrerequisite)
 let fallbackFault s = if snapshotPhase s == ExecutionUnknown then Left ResourceFailure else formatNormal s
 (beforeOwner,beforeCalls) <- newHarness fallbackFault (\_ -> pure (MutationEntered,CommittedObserved f)) (pure ())
 (pb,db) <- prepareOne beforeOwner k
 noFallback <- commit beforeOwner k (snapshotId pb) db now f
 beforeCount <- readIORef beforeCalls
 check "fallback failure fences provider" (noFallback == Left ResourceFailure && beforeCount == 0)

 closeCalls <- newIORef (0 :: Int)
 (closeOwner,_) <- newHarness formatNormal (\_ -> pure (MutationEntered,CommittedObserved f)) (modifyIORef' closeCalls (+1) >> ioError (userError "injected physical close failure"))
 (p6,d6) <- prepareOne closeOwner k
 uncertain <- cancel closeOwner k (snapshotId p6) d6 f >>= right
 uncertainAgain <- cancel closeOwner k (snapshotId p6) d6 f >>= right
 closeCount <- readIORef closeCalls
 check "close uncertainty retained without retry" (snapshotPhase uncertain == Cancelled && snapshotResource uncertain == TokenUncertain && uncertainAgain == uncertain && closeCount == 1)
 allocationControls f
 capacityControls f
 exhaustionControls f k
 sequenceControls f k
 peerSequenceControls f
 B.putStrLn "cancellation fixture complete"

wrongKeyControls :: Owner -> Key -> Snapshot -> Deadline -> IO ()
wrongKeyControls owner original prepared d = do
 let changes = [(11,2,3,4,5,6,7,8,9,10),(1,12,3,4,5,6,7,8,9,10),
       (1,2,13,4,5,6,7,8,9,10),(1,2,3,14,5,6,7,8,9,10),
       (1,2,3,4,15,6,7,8,9,10),(1,2,3,4,5,16,7,8,9,10),
       (1,2,3,4,5,6,17,8,9,10),(1,2,3,4,5,6,7,18,9,10),
       (1,2,3,4,5,6,7,8,19,10),(1,2,3,4,5,6,7,8,9,20)]
 forM_ changes $ \(a,b,c,e,g,h,i,j,l,m) -> do
  changed <- makeKey a b c e g h i j l m
  result <- query owner changed (snapshotId prepared) d
  check "valid different key refuses" (result == Left Foreign)
  prerequisite <- prerequisiteCommitted owner changed (snapshotId prepared) d
  check "different key cannot release prerequisite" (prerequisite == Left Foreign)
 another <- makeKey 99 2 3 4 5 6 7 8 9 10
 otherPrepared <- prepareOne owner another >>= pure . fst
 wrongP <- query owner original (snapshotId otherPrepared) d
 check "prepared id mismatch refuses" (wrongP == Left Foreign)
 otherD <- number 11 >>= right . deadline
 wrongD <- query owner original (snapshotId prepared) otherD
 check "deadline mismatch refuses" (wrongD == Left Foreign)
 intact <- query owner original (snapshotId prepared) d >>= right
 check "mismatch did not mutate" (snapshotPhase intact == Committed)

-- These are valid canonical inputs but the actual v29 key smart constructor
-- intentionally refuses unsupported protocol and non-Restore operations.
validationControls :: IO ()
validationControls = do
 l <- number 3; se <- number 4; front <- number 5
 b <- right (binding l se front)
 output <- number 9; revision <- number 10
 c <- right (context b l front output revision)
 req <- number 6; generation <- number 7; incarnation <- number 8
 peer <- number 1; start <- number 2
 who <- right (ownerId peer start b)
 restoreIntent <- right (intent b req generation incarnation c Restore)
 minimizeIntent <- right (intent b req generation incarnation c Minimize)
 check "unsupported protocol refused" (case key who 2 restoreIntent of Left Invalid -> True; _ -> False)
 check "unsupported operation refused" (case key who 1 minimizeIntent of Left Invalid -> True; _ -> False)

-- Compare the actual issued identifier with a clean owner's first identifier;
-- formatter and deadline refusals must not consume a prepared-ID allocation.
allocationControls :: Facts -> IO ()
allocationControls f = do
 bad <- makeKey 77 2 3 4 5 6 7 8 9 10
 good <- makeKey 78 2 3 4 5 6 7 8 9 10
 let selective snap = if snapshotKey snap == bad then Left ResourceFailure else formatNormal snap
 (owner,_) <- newHarness selective (\_ -> pure (MutationEntered,CommittedObserved f)) (pure ())
 (reference,_) <- newHarness formatNormal (\_ -> pure (MutationEntered,CommittedObserved f)) (pure ())
 ending <- number 10 >>= right . deadline; now <- number 1; equalD <- number 10; z <- number 0
 formatFailure <- prepare owner bad ending now z z
 deadlineFailure <- prepare owner good ending equalD z z
 check "format failure" (formatFailure == Left ResourceFailure)
 check "prepare at D refuses" (deadlineFailure == Left Expired)
 after <- prepare owner good ending now z z >>= right
 fresh <- prepare reference good ending now z z >>= right
 check "failed admissions do not advance prepared id" (snapshotId after == snapshotId fresh)

capacityControls :: Facts -> IO ()
capacityControls f = do
 (owner,calls) <- newHarness formatNormal (\_ -> pure (MutationEntered,CommittedObserved f)) (pure ())
 end <- number 10 >>= right . deadline; now <- number 1; z <- number 0
 forM_ [1..64] $ \n -> do
  k <- makeKey n 2 3 4 5 6 7 8 9 10
  result <- prepare owner k end now z z
  check "one of 64 slots admitted" (case result of Right snap -> snapshotPhase snap == Prepared; Left _ -> False)
 k65 <- makeKey 65 2 3 4 5 6 7 8 9 10
 overflow <- prepare owner k65 end now z z
 count <- readIORef calls
 check "65th refused" (overflow == Left Capacity && count == 0)

exhaustionControls :: Facts -> Key -> IO ()
exhaustionControls f k = do
 lastId <- right (parseCounter True "18446744073709551615")
 owner <- newOwner lastId formatNormal (Provider (\_ -> pure (MutationEntered,CommittedObserved f))) (\_ -> pure ()) >>= right
 end <- number 10 >>= right . deadline; now <- number 1; z <- number 0
 result <- prepare owner k end now z z
 check "prepared id cannot wrap" (result == Left Exhausted)

-- Each seeded trajectory uses a fresh real owner; every step checks actual
-- retained phase and provider count against a small reference transition.
sequenceControls :: Facts -> Key -> IO ()
sequenceControls f k = forM_ [False,True] $ \uncertainResult -> forM_ [1..16 :: Integer] $ \seed -> do
 let providerResult = if uncertainResult then Uncertain (f {factsReason=Unproven}) else CommittedObserved f
 (owner,calls) <- newHarness formatNormal (\_ -> pure (MutationEntered,providerResult)) (pure ())
 (p,d) <- prepareOne owner k
 now <- number 1; ending <- number 10; z <- number 0
 life <- number 3; sess <- number 4; front <- number 5
 bind <- right (binding life sess front)
 peer <- number 1; start <- number 2
 who <- right (ownerId peer start bind)
 let step (state,phase,expectedCalls) _ = do
      let state' = (state * 1103515245 + 12345) `mod` 2147483648
          op = state' `mod` 6
      actual <- case op of
       0 -> query owner k (snapshotId p) d >>= right
       1 -> cancel owner k (snapshotId p) d f >>= right
       2 -> commit owner k (snapshotId p) d now f >>= right
       3 -> prepare owner k d now z z >>= right
       4 -> expire owner k (snapshotId p) d ending f >>= right
       _ -> retireOwner owner who f >>= right >> (query owner k (snapshotId p) d >>= right)
      let nextPhase = if phase /= Prepared then phase else case op of
           1 -> Cancelled
           2 -> if uncertainResult then ExecutionUnknown else Committed
           4 -> Refused
           5 -> Cancelled
           _ -> Prepared
          nextCalls = expectedCalls + (if phase == Prepared && op == 2 then 1 else 0)
      count <- readIORef calls
      released <- prerequisiteCommitted owner k (snapshotId p) d >>= right
      check "sequence phase/nonreplay/prerequisite" (snapshotPhase actual == nextPhase && count == nextCalls && released == (nextPhase == Committed))
      pure (state',nextPhase,nextCalls)
 _ <- foldM step (seed,Prepared,0 :: Int) [1..48 :: Int]
 pure ()

-- Independent owners share one actual owner table. Each trace proves one
-- peer's terminal action leaves the other peer's exact state unchanged.
peerSequenceControls :: Facts -> IO ()
peerSequenceControls f = forM_ [1..16 :: Integer] $ \generation -> do
 (owner,calls) <- newHarness formatNormal (\_ -> pure (MutationEntered,CommittedObserved f)) (pure ())
 a <- makeKey 1 2 3 4 5 6 generation 8 9 10
 b <- makeKey 2 2 3 4 5 6 generation 8 9 10
 (pa,da) <- prepareOne owner a
 (pb,db) <- prepareOne owner b
 now <- number 1
 if even generation then do
  ca <- cancel owner a (snapshotId pa) da f >>= right
  beforeB <- query owner b (snapshotId pb) db >>= right
  cb <- commit owner b (snapshotId pb) db now f >>= right
  afterA <- lateDecision owner a (snapshotId pa) da >>= right
  check "cancel A cannot change prepared B or replay A" (snapshotPhase ca == Cancelled && snapshotPhase beforeB == Prepared && snapshotPhase cb == Committed && afterA == ca)
 else do
  cb <- commit owner b (snapshotId pb) db now f >>= right
  beforeA <- query owner a (snapshotId pa) da >>= right
  ca <- cancel owner a (snapshotId pa) da f >>= right
  afterB <- lateDecision owner b (snapshotId pb) db >>= right
  check "commit B cannot change prepared A or replay B" (snapshotPhase cb == Committed && snapshotPhase beforeA == Prepared && snapshotPhase ca == Cancelled && afterB == cb)
 count <- readIORef calls
 check "peer isolation exactly one callback" (count == 1)
