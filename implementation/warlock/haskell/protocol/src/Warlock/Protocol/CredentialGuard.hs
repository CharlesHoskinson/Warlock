{-# LANGUAGE RankNTypes #-}
-- A paired synchronous control-flow interface, not authentication or authority.
module Warlock.Protocol.CredentialGuard (CredentialGuard(..)) where
import Warlock.Transport.PeerCredentials (PeerCredential)

data CredentialGuard refusal = CredentialGuard
  { checkFragment :: PeerCredential -> IO (Either refusal ())
  , withCredentialAdmission :: forall a. PeerCredential -> IO a -> IO (Either refusal a)
  }
