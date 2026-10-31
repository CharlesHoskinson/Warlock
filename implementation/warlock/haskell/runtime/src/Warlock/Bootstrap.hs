-- Trusted application bootstrap. Approval is not native-effect authorization.
module Warlock.Bootstrap
  (BootstrapOwner, BootstrapResult(..), AuthObservation(..), newBootstrapOwner,
   runBootstrap, bootstrapAuthObservation, bootstrapCredentialTrace, bootstrapSelectedPid, retireBootstrap,
   CredentialStage(..), CredentialObservation(..),
   CurrentSessions, Registration, newCurrentSessions, newRegistration,
   withApprovedOwnedPeer, retireRegistration, Scope, ScopeStatus(..), PeerRefusal(..),
   retireScope, guardForScope) where
import Warlock.Bootstrap.Aggregate
import Warlock.Bootstrap.CurrentSessions
import Warlock.Bootstrap.ScopedPeer (Scope, ScopeStatus(..), PeerRefusal(..), retireScope)
import Warlock.Bootstrap.CredentialScopeGuard (guardForScope, CredentialStage(..), CredentialObservation(..))
