{-# LANGUAGE CPP #-}
{-# LANGUAGE OverloadedStrings #-}
{-# LANGUAGE ScopedTypeVariables #-}
-- Private prequeue owner. No disk observation or returned work is a native ACK.
module Warlock.Native.Cancellation.PairStore
 (PairStore,PairError(..),PairPhase(..),TransactionPhase(..),PairStatus(..),PreparedWork,
  newPairStore,offerNamespace,initializePairStore,installView,captureSelection,
  publishCaptured,claimPreparedWork,workIntent,workDeadline,workKey,pairStatus,closeStorage
#ifdef SLOTSTORE_TESTING
  ,newPairStoreWithHooks
#endif
  ) where
import Control.Concurrent (ThreadId,myThreadId)
import Control.Concurrent.MVar (MVar,newMVar,tryTakeMVar,putMVar)
import Control.Exception (SomeException,SomeAsyncException,fromException,mask,try,throwIO,finally)
import Control.Monad (unless,when)
import Control.Monad.Trans.Except (ExceptT(..),runExceptT,throwE)
import Control.Monad.Trans.Class (lift)
import qualified Data.ByteString as B
import Data.IORef (IORef,newIORef,readIORef,atomicModifyIORef')
import Data.List (find,nub)
import qualified Data.Text as T
import System.Posix.Types (Fd)
import qualified Warlock.Native.Cancellation.HostGuard as G
import qualified Warlock.Native.Cancellation.Selection as S
import qualified Warlock.Native.Cancellation.SlotStore as F
import qualified Warlock.Native.Cancellation.AdmissionBytes as Bytes
import Warlock.Native.Cancellation.AdmissionShape
import Warlock.Protocol.Identity (Binding,Counter,lifetime)
import Warlock.Protocol.Custody (Intent,intentIncarnation)

data PairError = WrongThread | Busy | NotReady | Poisoned | Capacity | Occupied | InvalidInventory | InvalidSelection
 | GuardFailure G.GuardError | SelectionFailure S.SelectionError | StorageFailure F.SlotError | EncodingFailure Bytes.PairError deriving (Eq,Show)
data PairPhase = Uninitialized | Available | Quarantined | Closed deriving (Eq,Show)
data TransactionPhase = QueueReserved | Spent | ReservedStored | PendingStored | SubmittedStored | Queued | Claimed | Failed deriving (Eq,Show)
data Transaction = Transaction !S.Selection !(Maybe Bytes.PairBytes) !TransactionPhase
data State = State !PairPhase ![Transaction] ![SomeException]
data PairStore = PairStore !ThreadId !Binding !G.HostGuard !S.SelectionRegistry !F.SlotStore !F.SlotStore !(IORef State) !(MVar ())
data PairStatus = PairStatus {pairPhase :: !PairPhase, transactions :: ![(T.Text,TransactionPhase)], exceptionCount :: !Int} deriving (Eq,Show)
data PreparedWork = PreparedWork !S.Selection !B.ByteString
workIntent :: PreparedWork -> Intent
workIntent (PreparedWork selected _) = S.selectionIntent selected
workDeadline :: PreparedWork -> Counter
workDeadline (PreparedWork selected _) = S.selectionDeadline selected
workKey :: PreparedWork -> B.ByteString
workKey (PreparedWork _ key) = key

newPairStore :: Counter -> Binding -> IO PairStore
newPairStore initial bound = allocate initial bound F.newSlotStore F.newSlotStore
allocate :: Counter -> Binding -> IO F.SlotStore -> IO F.SlotStore -> IO PairStore
allocate initial bound admissions companions = PairStore <$> myThreadId <*> pure bound <*> G.newHostGuard initial <*> S.newSelectionRegistry <*> admissions <*> companions <*> newIORef (State Uninitialized [] []) <*> newMVar ()
#ifdef SLOTSTORE_TESTING
newPairStoreWithHooks :: Counter -> Binding -> (String -> IO ()) -> (String -> IO ()) -> IO PairStore
newPairStoreWithHooks initial bound admissions companions = allocate initial bound (F.newSlotStoreWithHookForTest admissions) (F.newSlotStoreWithHookForTest companions)
#endif
pairStatus :: PairStore -> IO PairStatus
pairStatus (PairStore _ _ _ _ _ _ state _) = do
 State phase entries errors <- readIORef state
 pure (PairStatus phase [(S.selectionId s,p) | Transaction s _ p <- entries] (length errors))
change :: IORef State -> (State -> State) -> IO ()
change state f = atomicModifyIORef' state (\old -> (f old,()))
isAsync :: SomeException -> Bool
isAsync err = case fromException err :: Maybe SomeAsyncException of Just _ -> True; Nothing -> False
withActor :: forall a. PairStore -> IO (Either PairError a) -> IO (Either PairError a)
withActor (PairStore owner _ _ _ _ _ state gate) action = mask $ \restore -> do
 thread <- myThreadId
 if thread/=owner then pure (Left WrongThread) else do
  held <- tryTakeMVar gate
  case held of
   Nothing -> pure (Left Busy)
   Just () -> (do
    result <- try (restore action) :: IO (Either SomeException (Either PairError a))
    case result of
     Right value -> pure value
     Left err -> do
      change state $ \(State _ entries errors) -> State Quarantined entries (take 8 (err:errors))
      if isAsync err then throwIO err else pure (Left Poisoned)
    ) `finally` putMVar gate ()
ready :: IORef State -> ExceptT PairError IO ()
ready state = do
 State phase _ _ <- lift (readIORef state)
 unless (phase==Available) (throwE (if phase==Quarantined then Poisoned else NotReady))
slot :: IO (Either F.SlotError a) -> ExceptT PairError IO a
slot = ExceptT . fmap (either (Left . StorageFailure) Right)
selection :: IO (Either S.SelectionError a) -> ExceptT PairError IO a
selection = ExceptT . fmap (either (Left . SelectionFailure) Right)
encoding :: Either Bytes.PairError a -> ExceptT PairError IO a
encoding = ExceptT . pure . either (Left . EncodingFailure) Right
shape :: Either ShapeError a -> ExceptT PairError IO a
shape = ExceptT . pure . either (const (Left InvalidInventory)) Right
fromGuard :: Either G.GuardError (Either PairError a) -> Either PairError a
fromGuard = either (Left . GuardFailure) id

-- A rejected offer leaves the descriptor with the caller. All child store
-- objects were allocated above and remain private for their entire lifetime.
offerNamespace :: PairStore -> Fd -> IO Bool
offerNamespace store@(PairStore _ _ guard _ _ _ state _) fd = do
 result <- withActor store $ do
  State phase _ _ <- readIORef state
  if phase/=Uninitialized then pure (Right False) else Right <$> G.offerNamespace guard fd
 pure (case result of Right accepted -> accepted; Left _ -> False)
initializePairStore :: PairStore -> IO (Either PairError ())
initializePairStore store@(PairStore _ _ guard _ admissions companions state _) = withActor store $ do
 State phase _ _ <- readIORef state
 if phase/=Uninitialized then pure (Left NotReady) else do
  guarded <- G.withHostGuard guard $ \lease -> G.withNamespace lease $ \parent -> runExceptT $ do
   slot (F.offerChildDirectory admissions parent F.Admissions)
   slot (F.offerChildDirectory companions parent F.Companions)
  let result=fromGuard (fmap fromGuard guarded)
  change state $ \(State _ entries errors) -> State (case result of Right () -> Available; Left (GuardFailure G.Busy) -> Uninitialized; Left _ -> Quarantined) entries errors
  pure result

-- Only the authenticated current host event producer may supply these view
-- fields. This API validates correlation; it does not authenticate GUI input.
installView :: PairStore -> Counter -> Counter -> Counter -> Counter -> T.Text -> Intent -> IO (Either PairError S.ViewClaim)
installView store@(PairStore _ bound _ registry _ _ state _) scope generation publication lease control action = withActor store $ runExceptT $ do
 ready state
 claim <- ExceptT (pure (either (Left . SelectionFailure) Right (S.viewClaim bound scope generation publication lease control action)))
 selection (S.installCurrentView registry claim)
 pure claim
captureSelection :: PairStore -> S.ViewClaim -> IO (Either PairError S.Selection)
captureSelection store@(PairStore _ _ _ registry _ _ state _) claim = withActor store $ runExceptT $ ready state >> selection (S.captureSelection registry claim)

nameFor :: B.ByteString -> ExceptT PairError IO F.SlotName
nameFor key = ExceptT (pure (either (Left . StorageFailure) Right (F.slotName (key <> ".json"))))
inventory :: Binding -> F.SlotStore -> F.SlotStore -> S.Selection -> B.ByteString -> ExceptT PairError IO ()
inventory expected admissions companions selected candidateKey = do
 records <- slot (F.scanSlots admissions)
 witnesses <- slot (F.scanSlots companions)
 legacy <- mapM (\(name,raw) -> do
  record <- shape (decodeAdmission raw)
  wanted <- nameFor (admissionKey record)
  unless (admissionSchema record==2 && name==wanted && lifetime (admissionBinding record)==lifetime expected) (throwE InvalidInventory)
  pure record) records
 paired <- mapM (\(name,raw) -> do
  witness <- shape (decodeCompanion raw)
  let record=companionAdmission witness
  wanted <- nameFor (admissionKey record)
  unless (name==wanted && lifetime (admissionBinding record)==lifetime expected) (throwE InvalidInventory)
  pure witness) witnesses
 let targets=map admissionTarget legacy
     ids=map companionSelection paired
     candidateTarget=intentIncarnation (S.selectionIntent selected)
 unless (length targets==length (nub targets) && length ids==length (nub ids)) (throwE InvalidInventory)
 when (length legacy>=64 || length paired>=64) (throwE Capacity)
 -- No unsupported cache/tombstone is treated as permission to release a fence.
 -- Certified retirement/cache integration is still required for target reuse.
 when (S.selectionId selected `elem` ids || any (\r -> admissionTarget r==candidateTarget || admissionKey r==candidateKey) (legacy ++ map companionAdmission paired)) (throwE Occupied)

transactionId :: Transaction -> T.Text
transactionId (Transaction selected _ _) = S.selectionId selected
setTransaction :: IORef State -> S.Selection -> Maybe Bytes.PairBytes -> TransactionPhase -> IO ()
setTransaction state selected bytes phase = change state $ \(State status entries errors) ->
 State status (map (\old -> if transactionId old==S.selectionId selected then Transaction selected bytes phase else old) entries) errors
sameSelection :: S.Selection -> S.Selection -> Bool
sameSelection a b = S.selectionId a==S.selectionId b && S.selectionBinding a==S.selectionBinding b && S.selectionScope a==S.selectionScope b && S.selectionPublication a==S.selectionPublication b && S.selectionLease a==S.selectionLease b && S.selectionControl a==S.selectionControl b && S.selectionIntent a==S.selectionIntent b && S.selectionAccepted a==S.selectionAccepted b && S.selectionDeadline a==S.selectionDeadline b
publishCaptured :: PairStore -> S.Selection -> IO (Either PairError ())
publishCaptured store@(PairStore _ bound guard registry admissions companions state _) captured = withActor store $ do
 State _ before _ <- readIORef state
 let duplicateBefore=any ((==S.selectionId captured) . transactionId) before
 result <- runExceptT $ do
  ready state
  unless (S.selectionPhase captured==S.Captured && S.selectionBinding captured==bound) (throwE InvalidSelection)
  State _ entries _ <- lift (readIORef state)
  let queuePhases=[QueueReserved,Spent,ReservedStored,PendingStored,SubmittedStored,Queued]
  when (length entries>=64 || length [() | Transaction _ _ p <- entries,p `elem` queuePhases]>=16) (throwE Capacity)
  when (any ((==S.selectionId captured) . transactionId) entries) (throwE InvalidSelection)
  (key,_) <- encoding (Bytes.pendingFor (S.selectionIntent captured))
  lift (change state (\(State phase previous errors) -> State phase (previous ++ [Transaction captured Nothing QueueReserved]) errors))
  guarded <- lift $ G.withHostGuard guard $ \_ -> runExceptT $ do
   inventory bound admissions companions captured key
   spent <- selection (S.spendSelection registry (S.selectionId captured) bound (S.selectionIntent captured))
   lift (setTransaction state spent Nothing Spent)
   unless (sameSelection captured spent) (throwE InvalidSelection)
   pair <- encoding (Bytes.encodePair spent (S.selectionIntent spent))
   unless (Bytes.pairKey pair==key) (throwE InvalidSelection)
   lift (setTransaction state spent (Just pair) Spent)
   name <- nameFor key
   slot (F.publishSlot companions name Nothing (Bytes.reservedBytes pair))
   lift (setTransaction state spent (Just pair) ReservedStored)
   slot (F.publishSlot admissions name Nothing (Bytes.pendingBytes pair))
   lift (setTransaction state spent (Just pair) PendingStored)
   slot (F.publishSlot companions name (Just (Bytes.reservedBytes pair)) (Bytes.submittedBytes pair))
   lift (setTransaction state spent (Just pair) SubmittedStored)
   selection (S.validateSpentCurrent registry spent)
   pure (spent,pair)
  (spent,pair) <- ExceptT (pure (fromGuard guarded))
  -- Unlock failure grants no enqueue. The parent gate and owning event thread
  -- serialize this final currentness check with the actual queue transition.
  selection (S.validateSpentCurrent registry spent)
  lift (setTransaction state spent (Just pair) Queued)
 case result of
  Right () -> pure (Right ())
  Left err -> do
   unless duplicateBefore $ change state $ \(State phase entries errors) ->
    let after old@(Transaction _ _ p)
         | transactionId old/=S.selectionId captured = Just old
         | p==QueueReserved = Nothing
         | otherwise = Just old
        spentFailure=any (\old@(Transaction _ _ p) -> transactionId old==S.selectionId captured && p/=QueueReserved) entries
        corrupt=case err of InvalidInventory -> True; StorageFailure _ -> True; GuardFailure G.Busy -> False; GuardFailure _ -> True; _ -> False
    in State (if spentFailure || corrupt then Quarantined else phase) [entry | Just entry <- map after entries] errors
   pure (Left err)

claimPreparedWork :: PairStore -> IO (Either PairError (Maybe PreparedWork))
claimPreparedWork store@(PairStore _ _ _ registry _ _ state _) = withActor store $ runExceptT $ do
 ready state
 State _ entries _ <- lift (readIORef state)
 case find (\(Transaction _ _ phase) -> phase==Queued) entries of
  Nothing -> pure Nothing
  Just (Transaction selected (Just pair) _) -> do
   current <- lift (S.validateSpentCurrent registry selected)
   case current of
    Left err -> do
     lift (setTransaction state selected (Just pair) Failed)
     lift (change state (\(State _ values errors) -> State Quarantined values errors))
     throwE (SelectionFailure err)
    Right () -> do
     lift (setTransaction state selected (Just pair) Claimed)
     pure (Just (PreparedWork selected (Bytes.pairKey pair)))
  Just _ -> throwE InvalidSelection

-- Storage shutdown only. It retains on-disk Pending/certificates and confers
-- no native cancellation, ACK or physical-effect retirement observation.
closeStorage :: PairStore -> IO (Either PairError ())
closeStorage store@(PairStore _ _ guard registry admissions companions state _) = withActor store $ mask $ \restore -> do
 view <- try (restore (S.retireCurrentView registry)) :: IO (Either SomeException (Either S.SelectionError ()))
 first <- try (restore (F.retireSlotStore admissions)) :: IO (Either SomeException F.SlotStatus)
 second <- try (restore (F.retireSlotStore companions)) :: IO (Either SomeException F.SlotStatus)
 third <- try (restore (G.retireHostGuard guard)) :: IO (Either SomeException (Either G.GuardError G.GuardStatus))
 let exceptions=[err | Left err <- [fmap (const ()) view,fmap (const ()) first,fmap (const ()) second,fmap (const ()) third]]
 change state $ \(State _ entries errors) -> State Closed entries (take 8 (exceptions ++ errors))
 case filter isAsync exceptions of
  err:_ -> throwIO err
  [] -> case (view,first,second,third) of
   (Right (Right ()),Right a,Right b,Right (Right _)) | not (F.slotBusy a || F.slotBusy b) && F.slotUncertain a==0 && F.slotUncertain b==0 -> pure (Right ())
   _ -> pure (Left Poisoned)
