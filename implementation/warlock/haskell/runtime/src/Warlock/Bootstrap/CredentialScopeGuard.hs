-- One scope owns both decisions; observations carry no authority.
module Warlock.Bootstrap.CredentialScopeGuard
  (guardForScope, guardForScopeTracing, CredentialStage(..), CredentialObservation(..)) where
import Data.IORef (IORef, atomicModifyIORef')
import Warlock.Bootstrap.ScopedPeer (Scope, PeerRefusal, authenticateFragment, withAdmission)
import Warlock.Protocol.CredentialGuard (CredentialGuard(..))
import Warlock.Protocol.PeerCredential (credentialPid, credentialUid, credentialGid)

data CredentialStage = FragmentObserved | AdmissionObserved deriving (Eq,Show)
data CredentialObservation = CredentialObservation CredentialStage Integer Integer Integer deriving (Eq,Show)

guardForScope :: Scope -> CredentialGuard PeerRefusal
guardForScope scope = CredentialGuard (authenticateFragment scope) (withAdmission scope)

-- A bounded diagnostic of actual recvmsg facts, outside all admission locks.
-- Retaining 64 rows never turns a complete-trace or credential fact into a grant.
guardForScopeTracing :: IORef [CredentialObservation] -> Scope -> CredentialGuard PeerRefusal
guardForScopeTracing observations scope = CredentialGuard
  (\credential -> record FragmentObserved credential >> authenticateFragment scope credential)
  (\credential action -> record AdmissionObserved credential >> withAdmission scope credential action)
  where
    record stage credential = atomicModifyIORef' observations $ \rows ->
      let next = take 64 (CredentialObservation stage (credentialPid credential) (credentialUid credential) (credentialGid credential) : rows)
          force [] = ()
          force (row:rest) = row `seq` force rest
      in force next `seq` (next, ())
