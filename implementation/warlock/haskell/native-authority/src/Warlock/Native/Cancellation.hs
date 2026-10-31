-- Observational protocol facade only; owner creation, execution permits,
-- provider proof constructors and journal acknowledgement remain internal.
module Warlock.Native.Cancellation
 (Owner,OwnerId,Key,PreparedId,Deadline,Phase(..),Reason(..),Facts(..),Snapshot,
  Error(..),Resource(..),ownerId,key,deadline,prepare,query,cancel,expire,lateDecision,prerequisiteCommitted,busy,
  snapshotKey,snapshotId,snapshotDeadline,snapshotPhase,snapshotFacts,
  snapshotReply,snapshotProof,snapshotResource,snapshotExecution,ExecutionEvidence) where
import qualified Data.ByteString as B
import Warlock.Native.Cancellation.Internal hiding
 (snapshotKey,snapshotId,snapshotDeadline,snapshotPhase,snapshotFacts,
  snapshotReply,snapshotProof,snapshotResource,snapshotExecution)
import qualified Warlock.Native.Cancellation.Internal as Internal

snapshotKey :: Snapshot -> Key
snapshotKey = Internal.snapshotKey
snapshotId :: Snapshot -> PreparedId
snapshotId = Internal.snapshotId
snapshotDeadline :: Snapshot -> Deadline
snapshotDeadline = Internal.snapshotDeadline
snapshotPhase :: Snapshot -> Phase
snapshotPhase = Internal.snapshotPhase
snapshotFacts :: Snapshot -> Maybe Facts
snapshotFacts = Internal.snapshotFacts
snapshotReply :: Snapshot -> B.ByteString
snapshotReply = Internal.snapshotReply
snapshotProof :: Snapshot -> Maybe (Phase,Facts)
snapshotProof = Internal.snapshotProof
snapshotResource :: Snapshot -> Resource
snapshotResource = Internal.snapshotResource
snapshotExecution :: Snapshot -> Maybe ExecutionEvidence
snapshotExecution = Internal.snapshotExecution
