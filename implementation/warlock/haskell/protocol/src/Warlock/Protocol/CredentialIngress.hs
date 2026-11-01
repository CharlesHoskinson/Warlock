-- Owned credential transport only; not a native grant or peer provenance claim.
module Warlock.Protocol.CredentialIngress
 (CredentialIngress, CredentialIngressResult(..), CredentialFrameError(..),
  CredentialError(..), ReaderStatus(..), CredentialGuard(..),
  newCredentialIngress, newDesktopCredentialIngress, transferCredentialSocket, activateCredentialIngress,
  receiveCredentialIngress, retireCredentialIngress, credentialIngressStatus,
  enqueueCredentialIngress, sendCredentialIngress, retainedCredentialIngressFrames) where
import Warlock.Protocol.Ingress.Internal
import Warlock.Transport.Channel (CredentialFrameError(..))
import Warlock.Transport.PeerCredentials (CredentialError(..), ReaderStatus(..))
import Warlock.Protocol.CredentialGuard (CredentialGuard(..))
