{-# LANGUAGE OverloadedStrings #-}
-- Source-only controls; run only in Root's protected private execution scope.
module Main (main) where
import Control.Monad (unless)
import Warlock.Bootstrap.SocketOwner
import Warlock.Protocol.Ingress.Internal
import Warlock.Protocol.CredentialIngress
import Warlock.Transport.PeerCredentials (ReaderStatus(..))

owner :: IO CredentialIngress
owner = case ingressBinding "1" "2" "3" of
 Left err -> ioError (userError (show err))
 Right binding -> newCredentialIngress binding FromElm (const (pure ())) (const (pure ()))

check :: Bool -> String -> IO ()
check yes message = unless yes (ioError (userError message))

main :: IO ()
main = do
 good <- newSocketOwner
 ingress <- owner
 acquireSocketOwner good >>= \ok -> check ok "pair acquisition"
 offered <- withEndpoints good ingress $ \_ _ -> do
  (report,reader) <- credentialIngressStatus ingress
  pure (phase report == OwnerLive && endpoint report == Just EndpointOpen && reader == ReaderReady)
 check (offered == Just True) "one owned activated ingress"
 retired <- retireSocketOwner good
 check retired "normal independent cleanup"
 (report,reader) <- credentialIngressStatus ingress
 check (phase report == OwnerRetired && endpoint report == Just EndpointConfirmed && reader == ReaderReady) "ingress owns close"
 second <- retireSocketOwner good
 check second "confirmed repeat"

 badHost <- newSocketOwner
 ingress2 <- owner
 acquireSocketOwner badHost >>= \ok -> check ok "host-fault setup"
 rejected <- withEndpointsFault HostPostClose badHost ingress2 (\_ _ -> pure ())
 check (rejected == Nothing) "host conversion fault rejected"
 hostClean <- retireSocketOwner badHost
 (_,peerClean,transferClean) <- socketStatus badHost
 check (not hostClean && peerClean && transferClean) "peer retired despite host uncertainty"

 badTransfer <- newSocketOwner
 ingress3 <- owner
 acquireSocketOwner badTransfer >>= \ok -> check ok "transfer-fault setup"
 rejectedTransfer <- withEndpointsFault TransferPostClose badTransfer ingress3 (\_ _ -> pure ())
 check (rejectedTransfer == Nothing) "transfer conversion fault rejected"
 transferCleanAll <- retireSocketOwner badTransfer
 (hostClean,peerClean2,_) <- socketStatus badTransfer
 check (not transferCleanAll && hostClean && peerClean2) "known host and peer retired despite transfer uncertainty"
