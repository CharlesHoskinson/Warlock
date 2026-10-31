{-# LANGUAGE OverloadedStrings #-}
-- Source fixture only: Root runs under protected containment. The test hooks
-- pause before acquisition, never during a syscall or under the state lock.
module Main (main) where
import Control.Concurrent
import Control.Exception
import Control.Monad (unless)
import Data.IORef
import GHC.Conc (BlockReason(..), ThreadStatus(..), threadStatus)
import System.Timeout (timeout)
import Warlock.Bootstrap.SocketOwner
import Warlock.Capture.Process.Transfer (newTransferTicket, closeCallerTransfer)
import Warlock.Protocol.CredentialIngress
import Warlock.Protocol.Ingress.Internal (Direction(..), ingressBinding, OwnerStatus(..))

check :: Bool -> String -> IO ()
check value message = unless value (ioError (userError message))
bounded :: String -> IO a -> IO a
bounded name action = do
 answer <- timeout 5000000 action
 maybe (ioError (userError ("timeout: " ++ name))) pure answer
waitFlag :: IORef Bool -> IO ()
waitFlag ref = bounded "publication marker" $ do
 let loop = readIORef ref >>= \done -> unless done (threadDelay 1000 >> loop)
 loop
waitQueued :: ThreadId -> IO ()
waitQueued tid = bounded "queued ThreadKilled" $ do
 let loop = do
      status <- threadStatus tid
      case status of
       ThreadBlocked BlockedOnException -> pure ()
       ThreadFinished -> ioError (userError "throwTo finished too early")
       ThreadDied -> ioError (userError "throwTo died")
       _ -> threadDelay 1000 >> loop
 loop
newIngress :: IO CredentialIngress
newIngress = case ingressBinding "1" "2" "3" of
 Left err -> ioError (userError (show err))
 Right b -> newCredentialIngress b FromElm (const (pure ())) (const (pure ()))

-- The worker publishes its result under an uninterruptible, finite put after
-- try catches the original async exception. The driver queues throwTo only
-- after the actual socketpair / dup / accepted-offer result is marked.
contend :: SocketOwner -> (PublicationProbe -> IO a) -> IO (Either SomeException a)
contend owner operation = bounded "contended publication" $ do
 before <- newEmptyMVar
 proceed <- newEmptyMVar
 holderEntered <- newEmptyMVar
 holderRelease <- newEmptyMVar
 marker <- newIORef False
 result <- newEmptyMVar
 let probe = PublicationProbe (putMVar before () >> takeMVar proceed) marker
 worker <- forkIO $ mask $ \restore -> do
  observed <- try (restore (operation probe))
  uninterruptibleMask_ (putMVar result observed)
 takeMVar before
 _ <- forkIO (holdStateForTest owner holderEntered holderRelease)
 takeMVar holderEntered
 putMVar proceed ()
 waitFlag marker
 sender <- forkIO (throwTo worker ThreadKilled)
 waitQueued sender
 putMVar holderRelease ()
 takeMVar result

killed :: Either SomeException a -> IO ()
killed result = case result of
 Left exception -> check (fromException exception == Just ThreadKilled) "original ThreadKilled not rethrown"
 Right _ -> ioError (userError "worker unexpectedly completed")

main :: IO ()
main = do
 -- Real socketpair acquired; async is queued while its publication is blocked.
 pair <- newSocketOwner
 pairResult <- contend pair (\probe -> acquireSocketOwnerProbed pair (Just probe))
 killed pairResult
 (hostBefore,peerBefore,_) <- socketStatus pair
 check (not hostBefore && not peerBefore) "acquired endpoints not retained"
 rawPairOpenForTest pair >>= \ok -> check ok "published pair descriptors not open"
 retireSocketOwner pair >>= \ok -> check ok "acquired endpoints not closed"
 retireSocketOwner pair >>= \ok -> check ok "confirmed pair close is not idempotent"

 -- Actual transfer accepted, with shell retained before transfer can publish.
 offerPair <- newSocketOwner
 acquireSocketOwner offerPair >>= \ok -> check ok "offer pair"
 ingress <- newIngress
 offerResult <- contend offerPair (\probe -> withEndpointsProbed NoFault offerPair ingress (Just probe) Nothing (\_ _ -> pure ()))
 killed offerResult
 (retainedHost,retainedPeer,_) <- custodyForTest offerPair
 check (retainedHost && retainedPeer) "accepted ingress or peer reference lost"
 (observed,_) <- credentialIngressStatus ingress
 check (accepted observed) "accepted ingress shell lost"
 _ <- retireSocketOwner offerPair
 (_,peerClosed,_) <- socketStatus offerPair
 check peerClosed "known peer not independently retired after offer"
 _ <- retireSocketOwner offerPair

 -- Real F_DUPFD_CLOEXEC completed; its ownership must survive queued async.
 dupPair <- newSocketOwner
 acquireSocketOwner dupPair >>= \ok -> check ok "dup pair"
 ingress2 <- newIngress
 dupResult <- contend dupPair (\probe -> withEndpointsProbed NoFault dupPair ingress2 Nothing (Just probe) (\_ _ -> pure ()))
 killed dupResult
 (_,retainedDupPeer,retainedDup) <- custodyForTest dupPair
 check (retainedDupPeer && retainedDup) "duplicate custody reference lost"
 (_,_,transferClear) <- socketStatus dupPair
 check (not transferClear) "duplicated descriptor or its uncertainty lost"
 _ <- retireSocketOwner dupPair
 (hostClosed,peerClosed2,_) <- socketStatus dupPair
 check (hostClosed && peerClosed2) "known host/peer not independently retired"
 _ <- retireSocketOwner dupPair

 -- Ordinary accepted path: exactly one guarded ticket closes the transferred
 -- duplicate, then the pair retires its independent host and peer endpoints.
 ordinary <- newSocketOwner
 acquireSocketOwner ordinary >>= \ok -> check ok "ordinary pair"
 ingress3 <- newIngress
 normal <- withEndpoints ordinary ingress3 $ \_ handle -> do
  ticket <- newTransferTicket handle
  moved <- claimTransfer ordinary
  result <- closeCallerTransfer ticket
  pure (moved && result == Right ())
 check (normal == Just True) "ordinary ticket transfer"
 retireSocketOwner ordinary >>= \ok -> check ok "ordinary cleanup"

 -- A test-injected post-close host fault is uncertain, yet the independent
 -- actual peer still retires; a second retirement never retries the host FD.
 faultPair <- newSocketOwner
 acquireSocketOwner faultPair >>= \ok -> check ok "host fault pair"
 ingress4 <- newIngress
 rejected <- withEndpointsFault HostPostClose faultPair ingress4 (\_ _ -> pure ())
 check (rejected == Nothing) "host fault refusal"
 first <- retireSocketOwner faultPair
 (_,peerClosed3,_) <- socketStatus faultPair
 second <- retireSocketOwner faultPair
 check (not first && not second && peerClosed3) "uncertain host/independent peer"
 pure ()
