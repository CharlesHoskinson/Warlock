-- Root driver must use the canonical reader's test-only failing close hook and
-- send real SCM_RIGHTS over the offered socket; this function does not simulate it.
module QuarantineControls (assertQuarantineRetained) where
import Control.Monad (unless)
import Data.IORef (IORef, readIORef)
import Warlock.Protocol.Ingress.Internal
import Warlock.Protocol.CredentialGuard
import qualified Warlock.Transport.Channel as C
import qualified Warlock.Transport.PeerCredentials as P

assertQuarantineRetained :: CredentialIngress -> CredentialGuard String -> IORef Int -> IO () -> IO ()
assertQuarantineRetained owner guard calls sendRights = do
 before <- readIORef calls
 sendRights
 result <- receiveCredentialIngress owner guard
 after <- readIORef calls
 case result of
  CredentialFrameRejected (C.CredentialAncillary _) -> pure ()
  _ -> ioError (userError "rights did not reach canonical ancillary rejection")
 unless (before == after) (ioError (userError "rights reached callback"))
 (_,beforeRetire) <- credentialIngressStatus owner
 _ <- retireCredentialIngress owner
 (_,afterRetire) <- credentialIngressStatus owner
 case (beforeRetire,afterRetire) of
  (P.ReaderQuarantined _ _, P.ReaderQuarantined _ _) -> pure ()
  _ -> ioError (userError "ancillary uncertainty was lost on endpoint retirement")
