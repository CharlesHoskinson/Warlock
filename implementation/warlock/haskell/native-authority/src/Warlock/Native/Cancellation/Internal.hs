{-# LANGUAGE OverloadedStrings #-}
{-# LANGUAGE RankNTypes #-}
-- Private native-event-thread owner; constructors are not wire authority.
module Warlock.Native.Cancellation.Internal
 ( Owner, OwnerId, Key, PreparedId, Deadline, Phase(..), Reason(..), Facts(..)
 , Snapshot(..), Error(..), Resource(..), ProviderResult(..), Progress(..)
 , Format, Provider(..), CommitPermit, permitMatches, permitDeadline, Retire, DurableReceipt
 , ExecutionEvidence, executionProgress, executionResult
 , newOwner, ownerId, ownerPeer, ownerStart, ownerBinding, key, keyOwner, keyProtocol, keyIntent, preparedCounter, deadlineCounter, deadline, prepare, query, cancel, expire, commit
 , acknowledge, retireOwner, lateDecision, prerequisiteCommitted, TerminalTicket, TerminalReceipt, selectTerminalTicket, persistTerminalTicket, terminalReceiptCurrent, busy ) where

import Control.Concurrent (ThreadId, myThreadId)
import Control.Exception (SomeAsyncException, SomeException, evaluate, fromException, mask, throwIO, try)
import qualified Data.ByteString as B
import qualified Data.ByteString.Char8 as BC
import qualified Data.Text.Encoding as TE
import qualified Warlock.Native.Cancellation.Storage as Storage
import Data.IORef (IORef, atomicModifyIORef', newIORef, readIORef)
import Data.Word (Word8)
import Warlock.Protocol.Identity (Binding,Counter,addCounter,isZero,lifetime,session,frontend,contextLifetime,contextEpoch,contextOutput,contextRevision,renderCounter)
import Warlock.Protocol.Custody (Intent,Operation(..),intentBinding,intentRequest,intentGeneration,intentIncarnation,intentContext,intentOperation)

data OwnerId = OwnerId !Counter !Counter !Binding deriving (Eq,Show)
data Key = Key !OwnerId !Word8 !Intent deriving (Eq,Show)
newtype PreparedId = PreparedId Counter deriving (Eq,Ord,Show)
newtype Deadline = Deadline Counter deriving (Eq,Ord,Show)
data Phase = Prepared | Committed | Refused | Cancelled | ExecutionUnknown deriving (Eq,Show)
data Reason = Applied | NativeRefusal | DeadlineReached | CancelledByOwner | Unproven deriving (Eq,Show)
data Facts = Facts { factsRevision :: !Counter, factsOutputGeneration :: !Counter, factsReason :: !Reason } deriving (Eq,Show)
data Resource = TokenLive | TokenRetiring | TokenRetired | TokenUncertain deriving (Eq,Show)
data Error = Invalid | Expired | Busy | Capacity | Exhausted | Foreign | ResourceFailure | NotAcknowledgeable | WrongThread deriving (Eq,Show)
data Progress = NoMutation | MutationEntered deriving (Eq,Show)
-- Only the trusted provider module may construct these; never parse them from wire.
data ProviderResult = RefusedBefore !Facts | RefusedCompensated !Facts | CommittedObserved !Facts | Uncertain !Facts deriving (Eq,Show)
data ExecutionEvidence = ExecutionEvidence !Progress !ProviderResult deriving (Eq,Show)
executionProgress :: ExecutionEvidence -> Progress
executionProgress (ExecutionEvidence progress _) = progress
executionResult :: ExecutionEvidence -> ProviderResult
executionResult (ExecutionEvidence _ result) = result

data Snapshot = Snapshot { snapshotKey :: !Key, snapshotId :: !PreparedId, snapshotDeadline :: !Deadline,
 snapshotPhase :: !Phase, snapshotFacts :: !(Maybe Facts), snapshotReply :: !B.ByteString,
 snapshotProof :: !(Maybe (Phase,Facts)), snapshotResource :: !Resource, snapshotExecution :: !(Maybe ExecutionEvidence) } deriving (Eq,Show)
data Record = Record !Snapshot deriving (Eq)
-- This is deliberately unconstructible from the public facade. The actual
-- journal must supply a matching receipt only after durable retention.
data DurableReceipt = DurableReceipt !Key !PreparedId !Deadline !Phase

type Format = Snapshot -> Either Error B.ByteString
-- The constructor is private to the owner. A provider cannot manufacture an
-- execution permit from a decoded status, Key, or frontend data.
data CommitPermit scope = CommitPermit !Key !Deadline
permitMatches :: CommitPermit scope -> Key -> Bool
permitMatches (CommitPermit expected _) candidate = expected == candidate
permitDeadline :: CommitPermit scope -> Deadline
permitDeadline (CommitPermit _ original) = original
newtype Provider = Provider { runProvider :: forall scope. CommitPermit scope -> IO (Progress,ProviderResult) }
type Retire = Key -> IO ()
data State = State !Counter ![(OwnerId,Record)] ![(OwnerId,Record)]
data Owner = Owner !ThreadId !(IORef State) !Format !Provider !Retire

ownerId :: Counter -> Counter -> Binding -> Either Error OwnerId
ownerId peer start bindingValue
 | isZero peer || isZero start = Left Invalid
 | otherwise = Right (OwnerId peer start bindingValue)
key :: OwnerId -> Word8 -> Intent -> Either Error Key
key owner@(OwnerId _ _ bindingValue) protocol intentValue
 | protocol /= 1 || intentBinding intentValue /= bindingValue = Left Invalid
 | any isZero [intentRequest intentValue,intentGeneration intentValue,intentIncarnation intentValue] = Left Invalid
 | contextLifetime (intentContext intentValue) /= lifetime bindingValue = Left Invalid
 | contextEpoch (intentContext intentValue) /= frontend bindingValue = Left Invalid
 | intentOperation intentValue /= Restore = Left Invalid
 | otherwise = Right (Key owner protocol intentValue)
ownerPeer, ownerStart :: OwnerId -> Counter
ownerPeer (OwnerId peer _ _) = peer
ownerStart (OwnerId _ start _) = start
ownerBinding :: OwnerId -> Binding
ownerBinding (OwnerId _ _ bound) = bound
keyOwner :: Key -> OwnerId
keyOwner (Key owner _ _) = owner
keyProtocol :: Key -> Word8
keyProtocol (Key _ protocol _) = protocol
keyIntent :: Key -> Intent
keyIntent (Key _ _ value) = value
preparedCounter :: PreparedId -> Counter
preparedCounter (PreparedId value) = value
deadlineCounter :: Deadline -> Counter
deadlineCounter (Deadline value) = value
deadline :: Counter -> Either Error Deadline
deadline n = if isZero n then Left Invalid else Right (Deadline n)

newOwner :: Counter -> Format -> Provider -> Retire -> IO (Either Error Owner)
newOwner initial formatter provider retire = do
 thread <- myThreadId
 state <- newIORef (State initial [] [])
 pure (Right (Owner thread state formatter provider retire))
ensureThread :: Owner -> IO (Either Error ())
ensureThread (Owner expected _ _ _ _) = do actual <- myThreadId; pure (if actual == expected then Right () else Left WrongThread)
lookupRecord :: OwnerId -> [(OwnerId,Record)] -> Maybe Record
lookupRecord _ [] = Nothing
lookupRecord owner ((candidate,value):rest) | owner == candidate = Just value | otherwise = lookupRecord owner rest
ownerOf :: Key -> OwnerId
ownerOf (Key owner _ _) = owner
replace :: OwnerId -> Record -> [(OwnerId,Record)] -> [(OwnerId,Record)]
replace owner value records = (owner,value) : filter ((/=owner) . fst) records
same :: Key -> PreparedId -> Deadline -> Snapshot -> Bool
same k p d s = snapshotKey s == k && snapshotId s == p && snapshotDeadline s == d
validBytes :: B.ByteString -> Bool
validBytes bytes = not (B.null bytes) && B.length bytes <= 4096

-- Strictly force a complete bounded reply before publishing it. A synchronous
-- formatter exception is ResourceFailure; asynchronous exceptions propagate.
encode :: Format -> Snapshot -> IO (Either Error B.ByteString)
encode formatter record = do
 result <- try (evaluate (case formatter record of Left e -> Left e; Right bytes -> if validBytes bytes then Right bytes else Left ResourceFailure))
 case result of
  Right value -> pure value
  Left exception -> case fromException exception :: Maybe SomeAsyncException of
   Just _ -> throwIO (exception :: SomeException)
   Nothing -> pure (Left ResourceFailure)

busy :: Owner -> OwnerId -> IO (Either Error Bool)
busy owner@(Owner _ state _ _ _) who = do
 checked <- ensureThread owner
 case checked of Left err -> pure (Left err); Right () -> do State _ records _ <- readIORef state; pure (Right (maybe False (const True) (lookupRecord who records)))

staleHistory :: Maybe Record -> Intent -> Bool
staleHistory Nothing _ = False
staleHistory (Just (Record prior)) next =
 let old = keyIntent (snapshotKey prior)
 in intentRequest next <= intentRequest old || intentGeneration next <= intentGeneration old

-- Cursor/watermark are supplied by the trusted existing native admission owner;
-- capacity and ID are reserved only after the prepared reply is complete.
prepare :: Owner -> Key -> Deadline -> Counter -> Counter -> Counter -> IO (Either Error Snapshot)
prepare owner@(Owner _ state formatter _ _) k d@(Deadline expiry) now watermark generation = mask $ \restore -> do
 checked <- ensureThread owner
 case checked of
  Left err -> pure (Left err)
  Right () -> do
   State next records history <- readIORef state
   case lookupRecord (ownerOf k) records of
    Just (Record old) -> pure (if snapshotKey old == k && snapshotDeadline old == d then Right old else Left Busy)
    Nothing -> case lookupRecord (ownerOf k) history of
     Just (Record previous) | snapshotKey previous == k && snapshotDeadline previous == d -> pure (Right previous)
     previous -> case k of
      Key _ _ intentValue
       | isZero now || now >= expiry || intentRequest intentValue <= watermark || intentGeneration intentValue <= generation || staleHistory previous intentValue -> pure (Left Expired)
       | length records >= 64 -> pure (Left Capacity)
       | otherwise -> case addCounter next 1 of
        Left _ -> pure (Left Exhausted)
        Right nextId -> do
         let candidate = Snapshot k (PreparedId nextId) d Prepared Nothing B.empty Nothing TokenLive Nothing
         formatted <- restore (encode formatter candidate)
         case formatted of
          Left err -> pure (Left err)
          Right bytes -> atomicModifyIORef' state $ \current@(State currentNext currentRecords currentHistory) ->
           if currentNext /= next || length currentRecords >= 64 || maybe False (const True) (lookupRecord (ownerOf k) currentRecords) || currentHistory /= history
            then (current,Left Busy)
            else let value = candidate {snapshotReply=bytes} in (State nextId (replace (ownerOf k) (Record value) currentRecords) (filter ((/=ownerOf k) . fst) currentHistory),Right value)

peek :: Owner -> Key -> PreparedId -> Deadline -> IO (Either Error Snapshot)
peek owner@(Owner _ state _ _ _) k p d = do
 checked <- ensureThread owner
 case checked of
  Left err -> pure (Left err)
  Right () -> do
   State _ records history <- readIORef state
   let selected = case lookupRecord (ownerOf k) records of Just value -> Just value; Nothing -> lookupRecord (ownerOf k) history
   pure $ case selected of Just (Record value) | same k p d value -> Right value; _ -> Left Foreign

-- Query may finish encoding an already-proven terminal, never execute again.
query :: Owner -> Key -> PreparedId -> Deadline -> IO (Either Error Snapshot)
query owner@(Owner _ _ formatter _ _) k p d = do
 current <- peek owner k p d
 case current of
  Left err -> pure (Left err)
  Right value -> case snapshotProof value of
   Just (phase,facts) -> do
    let terminal = value {snapshotPhase=phase,snapshotFacts=Just facts,snapshotProof=Nothing}
    formatted <- encode formatter terminal
    case formatted of
     Left _ -> pure (Right value)
     Right bytes -> transition owner k p d $ \s ->
      if snapshotProof s == Just (phase,facts) then Right terminal {snapshotReply=bytes,snapshotResource=snapshotResource s} else Left Busy
   Nothing | B.null (snapshotReply value) -> publish owner value
   Nothing -> pure (Right value)

-- Atomic semantic transition. Caller cannot revive a terminal or Unknown.
transition :: Owner -> Key -> PreparedId -> Deadline -> (Snapshot -> Either Error Snapshot) -> IO (Either Error Snapshot)
transition owner@(Owner _ state _ _ _) k p d change = do
 checked <- ensureThread owner
 case checked of
  Left err -> pure (Left err)
  Right () -> atomicModifyIORef' state $ \current@(State n records history) -> case lookupRecord (ownerOf k) records of
   Just (Record old) | same k p d old -> case change old of
    Left err -> (current,Left err)
    Right value -> (State n (replace (ownerOf k) (Record value) records) history,Right value)
   _ -> (current,Left Foreign)

-- A claimed retirement is never repeated, even when its outcome is uncertain.
retireToken :: Owner -> Key -> PreparedId -> Deadline -> IO ()
retireToken owner@(Owner _ _ _ _ retire) k p d = mask $ \restore -> do
 selected <- transition owner k p d $ \s -> if snapshotResource s == TokenLive then Right s {snapshotResource=TokenRetiring} else Left ResourceFailure
 case selected of
  Left _ -> pure ()
  Right _ -> do
   outcome <- try (restore (retire k)) :: IO (Either SomeException ())
   _ <- transition owner k p d $ \s -> Right s {snapshotResource=case outcome of Right () -> TokenRetired; Left _ -> TokenUncertain}
   case outcome of
    Left err -> case fromException err :: Maybe SomeAsyncException of
     Just _ -> throwIO err
     Nothing -> pure ()
    Right () -> pure ()

publish :: Owner -> Snapshot -> IO (Either Error Snapshot)
publish owner@(Owner _ _ formatter _ _) value = do
 result <- encode formatter value
 case result of
  Left err -> pure (Left err)
  Right bytes -> transition owner (snapshotKey value) (snapshotId value) (snapshotDeadline value) $ \current ->
   if snapshotPhase current == snapshotPhase value && snapshotProof current == snapshotProof value
    then Right current {snapshotReply=bytes} else Left Foreign

cancel :: Owner -> Key -> PreparedId -> Deadline -> Facts -> IO (Either Error Snapshot)
cancel owner k p d facts = mask $ \restore -> do
 result <- transition owner k p d $ \old -> if snapshotPhase old /= Prepared then Right old else
  Right old {snapshotPhase=Cancelled,snapshotFacts=Just (facts {factsReason=CancelledByOwner}),snapshotReply=B.empty}
 case result of
  Right value | snapshotPhase value == Cancelled && B.null (snapshotReply value) -> do
   retireToken owner k p d
   current <- query owner k p d
   case current of Right s -> restore (publish owner s); Left err -> pure (Left err)
  _ -> pure result

expire :: Owner -> Key -> PreparedId -> Deadline -> Counter -> Facts -> IO (Either Error Snapshot)
expire owner k p d@(Deadline end) now facts
 | isZero now = pure (Left Invalid)
 | now < end = pure (Left Invalid)
 | otherwise = mask $ \restore -> do
   result <- transition owner k p d $ \old -> if snapshotPhase old /= Prepared then Right old else
    Right old {snapshotPhase=Refused,snapshotFacts=Just (facts {factsReason=DeadlineReached}),snapshotReply=B.empty}
   case result of
    Right value | snapshotPhase value == Refused && B.null (snapshotReply value) -> do
     retireToken owner k p d
     current <- query owner k p d
     case current of Right s -> restore (publish owner s); Left err -> pure (Left err)
    _ -> pure result

-- Trusted service MUST serialize this whole call on the native event thread;
-- provider does final live checks and first mutation without yielding. The
-- owner preinstalls Unknown before invoking it and never holds a global lock.
commit :: Owner -> Key -> PreparedId -> Deadline -> Counter -> Facts -> IO (Either Error Snapshot)
commit owner@(Owner _ _ formatter provider _) k p d@(Deadline end) now facts = mask $ \restore -> do
 current <- query owner k p d
 case current of
  Left err -> pure (Left err)
  Right old | snapshotPhase old /= Prepared -> pure (Right old)
  Right _ | isZero now -> pure (Left Invalid)
  Right _ | now >= end -> expire owner k p d now facts
  Right old -> do
   let fallback = old {snapshotPhase=ExecutionUnknown,snapshotFacts=Just (facts {factsReason=Unproven}),snapshotProof=Nothing}
   encoded <- restore (encode formatter fallback)
   case encoded of
    Left err -> pure (Left err)
    Right bytes -> do
     installed <- transition owner k p d $ \s -> if snapshotPhase s == Prepared then Right fallback {snapshotReply=bytes} else Left Busy
     case installed of
      Left err -> pure (Left err)
      Right unknown -> do
       native <- try (restore (do
        result@(progress,proof) <- runProvider provider (CommitPermit k d)
        _ <- evaluate progress
        _ <- evaluate proof
        pure result)) :: IO (Either SomeException (Progress,ProviderResult))
       case native of
        Left err -> case fromException err :: Maybe SomeAsyncException of
         Just _ -> throwIO err
         Nothing -> pure (Right unknown)
        Right (progress,proof) -> do
         observed <- transition owner k p d $ \currentState ->
          if snapshotPhase currentState == ExecutionUnknown && snapshotProof currentState == Nothing
           then Right currentState {snapshotExecution=Just (ExecutionEvidence progress proof)} else Left Busy
         case observed of
          Left err -> pure (Left err)
          Right retained -> case (progress,proof) of
           (NoMutation,RefusedBefore realFacts) -> finish Refused realFacts
           (MutationEntered,RefusedCompensated realFacts) -> finish Refused realFacts
           (MutationEntered,CommittedObserved realFacts) -> finish Committed realFacts
           _ -> pure (Right retained)
 where
  finish phase realFacts = do
   recorded <- transition owner k p d $ \s -> if snapshotPhase s == ExecutionUnknown && snapshotProof s == Nothing
    then Right s {snapshotProof=Just (phase,realFacts)} else Left Busy
   case recorded of
    Left err -> pure (Left err)
    Right _ -> do
     retireToken owner k p d
     -- query owns terminal publication and clears the proof exactly once.
     -- Publishing again after that would turn a successful commit into Busy.
     query owner k p d

-- The journal type is private and has no public constructor. No in-memory Bool
-- can prove durability. Root's real journal adapter must issue matching receipt.
acknowledge :: Owner -> Key -> PreparedId -> Deadline -> DurableReceipt -> IO (Either Error Snapshot)
acknowledge owner@(Owner _ state _ _ _) k p d (DurableReceipt rk rp rd phase) = do
 checked <- ensureThread owner
 case checked of
  Left err -> pure (Left err)
  Right () -> atomicModifyIORef' state $ \current@(State n records history) -> case lookupRecord (ownerOf k) records of
   Just (Record value) | same k p d value && (rk,rp,rd)==(k,p,d) && phase==snapshotPhase value && phase `elem` [Committed,Refused,Cancelled] && not (B.null (snapshotReply value)) && snapshotResource value == TokenRetired ->
    if length history >= 64 && maybe True (const False) (lookupRecord (ownerOf k) history)
     then (current,Left Capacity)
     else (State n (filter ((/=ownerOf k) . fst) records) (replace (ownerOf k) (Record value) history),Right value)
   _ -> (current,Left NotAcknowledgeable)

-- Owner retirement is a local fence, not a durable acknowledgement. An
-- unexecuted preparation is cancelled and its own resource retired; unknown or
-- terminal records remain available for journal reconciliation.
retireOwner :: Owner -> OwnerId -> Facts -> IO (Either Error ())
retireOwner owner@(Owner _ state _ _ _) who facts = do
 checked <- ensureThread owner
 case checked of
  Left err -> pure (Left err)
  Right () -> do
   State _ records _ <- readIORef state
   case lookupRecord who records of
    Just (Record value) | snapshotPhase value == Prepared -> do
     result <- cancel owner (snapshotKey value) (snapshotId value) (snapshotDeadline value) facts
     pure (case result of Left err -> Left err; Right _ -> Right ())
    _ -> pure (Right ())

-- A late decision is an exact read of the retained original key, never an
-- externally supplied replacement status or a new execution request.
lateDecision :: Owner -> Key -> PreparedId -> Deadline -> IO (Either Error Snapshot)
lateDecision = query
prerequisiteCommitted :: Owner -> Key -> PreparedId -> Deadline -> IO (Either Error Bool)
prerequisiteCommitted owner k p d = do
 result <- query owner k p d
 pure (fmap ((== Committed) . snapshotPhase) result)

-- Ticket and receipt constructors never leave this trusted component. The
-- retained Owner and Storage identities bind this in-process observation;
-- no restart generation or host ACK witness is implied.
data TerminalTicket = TerminalTicket !Owner !Snapshot
data TerminalReceipt = TerminalReceipt !Storage.Storage !TerminalTicket

selectTerminalTicket :: Owner -> Key -> PreparedId -> Deadline -> IO (Either Error TerminalTicket)
selectTerminalTicket owner k p d = do
 selected <- peek owner k p d
 pure $ case selected of
  Left err -> Left err
  Right original
   | snapshotPhase original `notElem` [Committed,Refused,Cancelled] -> Left NotAcknowledgeable
   | snapshotResource original /= TokenRetired || snapshotProof original /= Nothing || B.null (snapshotReply original) -> Left NotAcknowledgeable
   | otherwise -> Right (TerminalTicket owner original)

persistTerminalTicket :: Storage.Storage -> TerminalTicket -> IO (Either Error TerminalReceipt)
persistTerminalTicket storage ticket@(TerminalTicket owner original) = do
 before <- peek owner (snapshotKey original) (snapshotId original) (snapshotDeadline original)
 case before of
  Right current | current == original -> case terminalBytes original of
   Nothing -> pure (Left ResourceFailure)
   Just bytes -> do
    result <- Storage.persistBytes storage bytes
    case result of
     Left _ -> pure (Left ResourceFailure)
     Right () -> do
      let receipt = TerminalReceipt storage ticket
      verified <- terminalReceiptCurrent receipt
      pure (case verified of Right () -> Right receipt; Left err -> Left err)
  _ -> pure (Left Foreign)

-- Rechecks the exact owner record and the SAME retained storage object.  The
-- storage status cannot prove host unlink, AckPending or durable ACK.
terminalReceiptCurrent :: TerminalReceipt -> IO (Either Error ())
terminalReceiptCurrent (TerminalReceipt storage (TerminalTicket owner original)) = do
 status <- Storage.storageStatus storage
 after <- peek owner (snapshotKey original) (snapshotId original) (snapshotDeadline original)
 pure $ case after of
  Right current | current == original && Storage.storageStage status == Storage.DirectorySynced &&
   Storage.directoryStatus status == Storage.HandleOwned && Storage.fileStatus status == Storage.HandleOwned &&
   Storage.entryStatus status == Storage.HandleOwned -> Right ()
  _ -> Left Foreign

-- Length-prefixed reply follows fixed, bounded numeric/enum fields. A reader,
-- crash recovery and durable tombstone format are NOT yet implemented.
terminalBytes :: Snapshot -> Maybe B.ByteString
terminalBytes value = do
 facts <- snapshotFacts value
 let k = snapshotKey value
     who = keyOwner k
     bound = ownerBinding who
     action = keyIntent k
     ctx = intentContext action
     n = TE.encodeUtf8 . renderCounter
     linesOf = ["WCAN1", n (ownerPeer who), n (ownerStart who), n (lifetime bound),
      n (session bound), n (frontend bound), BC.pack (show (keyProtocol k)),
      n (intentRequest action), n (intentGeneration action), n (intentIncarnation action),
      n (contextLifetime ctx), n (contextEpoch ctx), n (contextOutput ctx), n (contextRevision ctx),
      "Restore", n (preparedCounter (snapshotId value)), n (deadlineCounter (snapshotDeadline value)),
      BC.pack (show (snapshotPhase value)), n (factsRevision facts), n (factsOutputGeneration facts),
      BC.pack (show (factsReason facts)), BC.pack (show (snapshotExecution value)),
      BC.pack (show (B.length (snapshotReply value)))]
     prefix = B.intercalate "\n" linesOf <> "\n"
 pure (prefix <> snapshotReply value)
