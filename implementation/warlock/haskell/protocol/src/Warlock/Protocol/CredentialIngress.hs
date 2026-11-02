-- Owned credential transport only; not a native grant or peer provenance claim.
module Warlock.Protocol.CredentialIngress
 (CredentialIngress, CredentialIngressT, CredentialIngressResult(..), PersistentIngressResult(..), PersistentSendResult(..), CredentialFrameError(..), FrameDeadline, frameDeadlineNs,
  CredentialError(..), ReaderStatus(..), CredentialGuard(..),
  newCredentialIngress, newDesktopCredentialIngress, newDesktopCredentialIngressWithContext, transferCredentialSocket, activateCredentialIngress,
  receiveCredentialIngress, receiveDesktopCredentialIngressAfterIdle, receivePersistentCredentialIngress, receivePersistentCredentialIngressOwned, sendPersistentCredentialIngress, retireCredentialIngress, credentialIngressStatus,
  enqueueCredentialIngress, sendCredentialIngress, retainedCredentialIngressFrames) where
import Warlock.Protocol.Ingress.Internal
import Warlock.Transport.Channel (CredentialFrameError(..), FrameDeadline, frameDeadlineNs)
import Warlock.Transport.PeerCredentials (CredentialError(..), ReaderStatus(..))
import Warlock.Protocol.CredentialGuard (CredentialGuard(..))
