{-# LANGUAGE OverloadedStrings #-}
-- Socketpair component controls only. Permissive guards below prove no identity.
module Main (main) where
import Control.Concurrent (forkIO, newEmptyMVar, putMVar, takeMVar)
import Control.Monad (unless, void)
import qualified Data.ByteString as B
import Data.IORef (newIORef, readIORef, modifyIORef')
import qualified Network.Socket as S
import qualified Network.Socket.ByteString as N
import System.Environment (getArgs)
import System.FilePath ((</>))
import Warlock.Protocol.Ingress.Internal
import Warlock.Protocol.CredentialGuard
import qualified Warlock.Transport.Channel as C
import qualified Warlock.Transport.PeerCredentials as P
import Warlock.Transport.Frame (prefix)

data Refusal = HeaderDenied | BodyDenied | AdmissionDenied deriving (Eq,Show)
check :: String -> Bool -> IO ()
check name ok = unless ok (ioError (userError name))
frame :: B.ByteString -> IO B.ByteString
frame = either (ioError . userError . show) pure . prefix
bindingValue :: IO IngressBinding
bindingValue = either (ioError . userError . show) pure (ingressBinding "1" "2" "3")

-- Each test gets one owned receiving end and caller-owned peer.
withOwner :: Direction -> (CredentialIngress -> S.Socket -> IORefCount -> IO ()) -> IO ()
withOwner direction action = do
 binding <- bindingValue
 count <- newIORef (0 :: Int)
 owner <- newCredentialIngress binding direction (\_ -> modifyIORef' count (+1)) (\_ -> modifyIORef' count (+1))
 (incoming,peer) <- S.socketPair S.AF_UNIX S.Stream S.defaultProtocol
 offered <- transferCredentialSocket owner incoming
 check "offer" (offered == OfferAccepted)
 active <- activateCredentialIngress owner
 check "credential activation" (active == ActivationLive)
 action owner peer (IORefCount (readIORef count))
 _ <- retireCredentialIngress owner
 (_,reader) <- credentialIngressStatus owner
 check "reader retained after endpoint retirement" (reader == P.ReaderReady)
 S.close peer
newtype IORefCount = IORefCount (IO Int)
countValue :: IORefCount -> IO Int
countValue (IORefCount action) = action

main :: IO ()
main = do
 args <- getArgs
 base <- case args of [path] -> pure path; _ -> ioError (userError "fixture directory")
 client <- B.readFile (base </> "valid-negotiate.bin")
 server <- B.readFile (base </> "valid-hello.bin")
 clientFrame <- frame client
 serverFrame <- frame server
 let acceptGuard = CredentialGuard (\_ -> pure (Right ())) (\_ action -> Right <$> action) :: CredentialGuard Refusal
 withOwner FromElm $ \owner peer calls -> do
  N.sendAll peer clientFrame
  outcome <- receiveCredentialIngress owner acceptGuard
  n <- countValue calls
  (_,reader) <- credentialIngressStatus owner
  check "client through same checked gate" (outcome == CredentialDelivered && n == 1 && reader == P.ReaderReady)
 withOwner FromNative $ \owner peer calls -> do
  N.sendAll peer serverFrame
  outcome <- receiveCredentialIngress owner acceptGuard
  n <- countValue calls
  check "server through same checked gate" (outcome == CredentialDelivered && n == 1)
 withOwner FromElm $ \owner peer calls -> do
  let deny = CredentialGuard (\_ -> pure (Left HeaderDenied)) (\_ action -> Right <$> action)
  N.sendAll peer clientFrame
  outcome <- receiveCredentialIngress owner deny
  n <- countValue calls
  check "header exact typed refusal" (outcome == CredentialFrameRejected (C.CredentialPeer HeaderDenied) && n == 0)
 withOwner FromElm $ \owner peer calls -> do
  seen <- newIORef (0 :: Int)
  headerSeen <- newEmptyMVar
  let checkPart _ = do
       modifyIORef' seen (+1)
       n <- readIORef seen
       if n == 1 then putMVar headerSeen () >> pure (Right ()) else pure (Left BodyDenied)
      denyBody = CredentialGuard checkPart (\_ action -> Right <$> action)
  void $ forkIO (N.sendAll peer (B.take 4 clientFrame) >> takeMVar headerSeen >> N.sendAll peer (B.drop 4 clientFrame))
  outcome <- receiveCredentialIngress owner denyBody
  n <- countValue calls
  check "body exact typed refusal" (outcome == CredentialFrameRejected (C.CredentialPeer BodyDenied) && n == 0)
 withOwner FromElm $ \owner peer calls -> do
  let denyAdmission = CredentialGuard (\_ -> pure (Right ())) (\_ _ -> pure (Left AdmissionDenied))
  N.sendAll peer clientFrame
  outcome <- receiveCredentialIngress owner denyAdmission
  n <- countValue calls
  check "admission exact refusal and no callback" (outcome == CredentialAdmissionRejected AdmissionDenied && n == 0)
 withOwner FromElm $ \owner peer calls -> do
  bad <- frame "{\"version\":true}"
  N.sendAll peer bad
  outcome <- receiveCredentialIngress owner acceptGuard
  n <- countValue calls
  check "invalid schema no callback" (case outcome of CredentialRejected BadSchema -> n == 0; _ -> False)
 -- Legacy owner keeps the original transport-only checked route.
 legacyBinding <- bindingValue
 legacyCount <- newIORef (0 :: Int)
 legacy <- newIngressOwner legacyBinding FromElm (\_ -> modifyIORef' legacyCount (+1)) (\_ -> pure ())
 (legacySocket,legacyPeer) <- S.socketPair S.AF_UNIX S.Stream S.defaultProtocol
 legacyOffer <- transferSocket legacy legacySocket
 legacyLive <- activateIngress legacy
 N.sendAll legacyPeer clientFrame
 legacyResult <- receiveIngress legacy
 legacySeen <- readIORef legacyCount
 check "legacy checked route unchanged" (legacyOffer == OfferAccepted && legacyLive == ActivationLive && legacyResult == Delivered && legacySeen == 1)
 _ <- retireIngress legacy
 S.close legacyPeer
 -- Actual scope, cross-user and native effect authority are outside these controls.
