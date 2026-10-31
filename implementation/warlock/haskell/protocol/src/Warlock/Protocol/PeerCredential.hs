-- Read-only kernel observations. No constructor or record labels are exported.
module Warlock.Protocol.PeerCredential
  (PeerCredential, credentialPid, credentialUid, credentialGid) where
import Warlock.Transport.PeerCredentials (PeerCredential)
import qualified Warlock.Transport.PeerCredentials as P
credentialPid :: PeerCredential -> Integer
credentialPid = toInteger . P.peerPid
credentialUid :: PeerCredential -> Integer
credentialUid = toInteger . P.peerUid
credentialGid :: PeerCredential -> Integer
credentialGid = toInteger . P.peerGid
