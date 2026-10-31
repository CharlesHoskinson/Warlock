{-# LANGUAGE OverloadedStrings #-}
-- Root-only actual socketpair controls; no peer authentication is established.
module Main (main) where
import Control.Concurrent (ThreadId,forkIO,isEmptyMVar,killThread,newEmptyMVar,putMVar,takeMVar,threadDelay)
import Control.Exception (AsyncException(ThreadKilled),SomeException,fromException,mask,throwIO,try)
import Control.Monad (unless,void)
import qualified Data.ByteString as B
import Data.IORef (newIORef,modifyIORef',readIORef,writeIORef)
import GHC.Conc (BlockReason(..),ThreadStatus(..),threadStatus)
import qualified Network.Socket as S
import qualified Network.Socket.ByteString as N
import System.Environment (getArgs)
import System.FilePath ((</>))
import Warlock.Protocol.Ingress.Internal
import Warlock.Protocol.Codec (CheckedClient,CheckedServer)
import qualified Warlock.Protocol.Codec as Codec
import qualified Warlock.Protocol.Boundary.Internal as G
import qualified Warlock.Transport.SocketFlags as F
import Warlock.Transport.Frame (prefix)

check :: String -> Bool -> IO ()
check label ok = unless ok (ioError (userError label)) >> putStrLn ("PASS " ++ label)
makeBinding :: IO IngressBinding
makeBinding = either (ioError . userError . show) pure (ingressBinding "1" "2" "3")
noopClient :: CheckedClient -> IO ()
noopClient _ = pure ()
noopServer :: CheckedServer -> IO ()
noopServer _ = pure ()
waitBlocked :: ThreadId -> Int -> IO ()
waitBlocked _ 0 = ioError (userError "worker did not block")
waitBlocked tid n = do
 state <- threadStatus tid
 case state of ThreadBlocked _ -> pure (); _ -> threadDelay 10000 >> waitBlocked tid (n-1)
waitThrowBlocked :: ThreadId -> Int -> IO ()
waitThrowBlocked _ 0 = ioError (userError "throwTo did not block")
waitThrowBlocked tid n = do
 state <- threadStatus tid
 case state of ThreadBlocked BlockedOnException -> pure (); _ -> threadDelay 10000 >> waitThrowBlocked tid (n-1)
readExactTest :: S.Socket -> Int -> IO B.ByteString
readExactTest sock count = if count==0 then pure B.empty else do
 bytes <- N.recv sock count
 if B.null bytes then ioError (userError "unexpected EOF") else (bytes <>) <$> readExactTest sock (count-B.length bytes)

main :: IO ()
main = do
 args <- getArgs
 base <- case args of [path] -> pure path; _ -> ioError (userError "fixture directory")
 bytes <- B.readFile (base </> "valid-negotiate.bin")
 helloOne <- B.readFile (base </> "valid-hello.bin")
 frame <- either (ioError . userError . show) pure (prefix bytes)
 bindingValue <- makeBinding
 -- Socket-free preparation failure never takes the already-existing socket.
 (unoffered,peer0) <- S.socketPair S.AF_UNIX S.Stream S.defaultProtocol
 prepareResult <- try (newIngressOwnerWithPrepareHook (ioError (userError "prepare fault")) bindingValue FromElm noopClient noopServer F.configureSocketFlags S.close) :: IO (Either SomeException IngressOwner)
 N.sendAll unoffered "x"
 stillOpen <- N.recv peer0 1
 check "prepare failure leaves caller socket live" (case prepareResult of Left _ -> stillOpen=="x"; Right _ -> False)
 S.close unoffered
 S.close peer0
 (beforeSock,beforePeer) <- S.socketPair S.AF_UNIX S.Stream S.defaultProtocol
 beforeOwner <- newIngressOwner bindingValue FromElm noopClient noopServer
 beforeThrow <- try (transferSocketWithHooks (throwIO ThreadKilled) (pure ()) beforeOwner beforeSock) :: IO (Either SomeException OfferResult)
 beforeStatus <- ingressStatus beforeOwner
 N.sendAll beforeSock "b"
 beforeByte <- N.recv beforePeer 1
 check "interruption before publication retains caller ownership" (case beforeThrow of Left _ -> not (accepted beforeStatus) && beforeByte=="b"; Right _ -> False)
 S.close beforeSock
 S.close beforePeer
 (afterSock,afterPeer) <- S.socketPair S.AF_UNIX S.Stream S.defaultProtocol
 afterOwner <- newIngressOwner bindingValue FromElm noopClient noopServer
 afterThrow <- try (transferSocketWithHooks (pure ()) (throwIO ThreadKilled) afterOwner afterSock) :: IO (Either SomeException OfferResult)
 afterStatus <- ingressStatus afterOwner
 afterRetired <- retireIngress afterOwner
 check "interruption after publication retains shell custody" (case afterThrow of Left _ -> accepted afterStatus && phase afterStatus==OwnerPending && endpoint afterRetired==Just EndpointConfirmed; Right _ -> False)
 S.close afterPeer
 -- Publication precedes actual flag setup, and a second offered socket is not consumed.
 (first,peer1) <- S.socketPair S.AF_UNIX S.Stream S.defaultProtocol
 (second,peer2) <- S.socketPair S.AF_UNIX S.Stream S.defaultProtocol
 callbackCount <- newIORef (0::Int)
 live <- newIngressOwner bindingValue FromElm (\_ -> modifyIORef' callbackCount (+1)) noopServer
 offered <- transferSocket live first
 before <- ingressStatus live
 refused <- transferSocket live second
 N.sendAll second "z"
 independent <- N.recv peer2 1
 activated <- activateIngress live
 flags <- flagsForTest live
 void $ forkIO (N.sendAll peer1 (B.take 2 frame) >> threadDelay 10000 >> N.sendAll peer1 (B.drop 2 frame <> frame))
 delivered <- receiveIngress live
 deliveredAgain <- receiveIngress live
 seen <- readIORef callbackCount
 let hello="{\"version\":2,\"kind\":\"hello\",\"body\":{\"binding\":{\"lifetime\":\"1\",\"session\":\"2\",\"frontend\":\"3\"}}}"
 queuedOrdinary <- enqueueIngress live Ordinary helloOne
 queuedControl <- enqueueIngress live Control hello
 rejectedControl <- enqueueIngress live Control hello
 sentControl <- sendIngress live
 expectedControl <- either (ioError . userError . show) pure (prefix hello)
 readControl <- readExactTest peer1 (B.length expectedControl)
 sentOrdinary <- sendIngress live
 expectedOrdinary <- either (ioError . userError . show) pure (prefix helloOne)
 readOrdinary <- readExactTest peer1 (B.length expectedOrdinary)
 check "reserved control is bounded and sent first" (queuedOrdinary==Right () && queuedControl==Right () && rejectedControl==Left QueueFull && sentControl==Right () && sentOrdinary==Right () && readControl==expectedControl && readOrdinary==expectedOrdinary)
 settled <- retireIngress live
 check "accepted once and independent repeat offer remains caller-owned" (offered==OfferAccepted && accepted before && phase before==OwnerPending && refused==OfferRefused && independent=="z")
 check "split and coalesced frames route and close" (activated==ActivationLive && flags && delivered==Delivered && deliveredAgain==Delivered && seen==2 && gate settled==G.Retired && endpoint settled==Just EndpointConfirmed && phase settled==OwnerRetired)
 S.close peer1
 S.close second
 S.close peer2
 (serverSock,serverPeer) <- S.socketPair S.AF_UNIX S.Stream S.defaultProtocol
 serverEncoded <- newIORef Nothing
 serverOwner <- newIngressOwner bindingValue FromNative noopClient (\value -> writeIORef serverEncoded (Just (Codec.encodeServerChecked value)))
 _ <- transferSocket serverOwner serverSock
 serverActive <- activateIngress serverOwner
 helloFrame <- either (ioError . userError . show) pure (prefix hello)
 N.sendAll serverPeer helloFrame
 serverResult <- receiveIngress serverOwner
 serverRoundtrip <- readIORef serverEncoded
 check "checked v2 server reaches same owner callback" (serverActive==ActivationLive && serverResult==Delivered && case serverRoundtrip of Just (Right raw) -> Codec.decodeServerChecked raw == Codec.decodeServerChecked hello; _ -> False)
 _ <- retireIngress serverOwner
 S.close serverPeer
 (queuedSock,queuedPeer) <- S.socketPair S.AF_UNIX S.Stream S.defaultProtocol
 queuedOwner <- newIngressOwner bindingValue FromElm noopClient noopServer
 _ <- transferSocket queuedOwner queuedSock
 _ <- activateIngress queuedOwner
 enqueued <- enqueueIngress queuedOwner Control hello
 _ <- retireIngress queuedOwner
 kept <- retainedIngressFrames queuedOwner
 expectedKept <- either (ioError . userError . show) pure (prefix hello)
 check "retirement retains queued bytes without replay" (enqueued==Right () && kept==[(Control,expectedKept)])
 S.close queuedPeer
 (callbackSock,callbackPeer) <- S.socketPair S.AF_UNIX S.Stream S.defaultProtocol
 callbackOwner <- newIngressOwner bindingValue FromElm (\_ -> throwIO ThreadKilled) noopServer
 _ <- transferSocket callbackOwner callbackSock
 _ <- activateIngress callbackOwner
 N.sendAll callbackPeer frame
 callbackResult <- try (receiveIngress callbackOwner) :: IO (Either SomeException IngressResult)
 callbackStatus <- ingressStatus callbackOwner
 callbackReasons <- ingressRejections callbackOwner
 let callbackKilled = case callbackResult of
      Left e -> case fromException e of Just ThreadKilled -> True; _ -> False
      Right _ -> False
 check "callback async preserves gate and endpoint cleanup" (callbackKilled && gate callbackStatus==G.Retired && endpoint callbackStatus==Just EndpointConfirmed && callbackReasons==[G.HandlerFailed])
 S.close callbackPeer
 (readingSock,readingPeer) <- S.socketPair S.AF_UNIX S.Stream S.defaultProtocol
 readingOwner <- newIngressOwner bindingValue FromElm noopClient noopServer
 _ <- transferSocket readingOwner readingSock
 _ <- activateIngress readingOwner
 readDone <- newEmptyMVar
 readingThread <- forkIO $ mask $ \restore -> do result <- try (restore (receiveIngress readingOwner)) :: IO (Either SomeException IngressResult); putMVar readDone result
 waitBlocked readingThread 200
 killThread readingThread
 readResult <- takeMVar readDone
 readStatus <- ingressStatus readingOwner
 let readKilled = case readResult of
      Left e -> case fromException e of Just ThreadKilled -> True; _ -> False
      Right _ -> False
 check "blocked receive async preserves independent cleanup" (readKilled && gate readStatus==G.Retired && endpoint readStatus==Just EndpointConfirmed)
 S.close readingPeer
 (drainSock,drainPeer) <- S.socketPair S.AF_UNIX S.Stream S.defaultProtocol
 callbackEntered <- newEmptyMVar
 callbackRelease <- newEmptyMVar
 callbackDone <- newEmptyMVar
 drainingOwner <- newIngressOwner bindingValue FromElm (\_ -> putMVar callbackEntered () >> takeMVar callbackRelease) noopServer
 _ <- transferSocket drainingOwner drainSock
 _ <- activateIngress drainingOwner
 N.sendAll drainPeer frame
 void $ forkIO $ mask $ \restore -> do result <- try (restore (receiveIngress drainingOwner)) :: IO (Either SomeException IngressResult); putMVar callbackDone result
 takeMVar callbackEntered
 draining <- retireIngress drainingOwner
 check "retirement preserves in-flight gate separately" (gate draining==G.Draining 1 && endpoint draining==Just EndpointConfirmed && phase draining==OwnerRetiring)
 putMVar callbackRelease ()
 callbackFinished <- takeMVar callbackDone
 drained <- ingressStatus drainingOwner
 check "callback drains before owner retirement" (case callbackFinished of Right Delivered -> gate drained==G.Retired && phase drained==OwnerRetired; _ -> False)
 S.close drainPeer
 -- Post-publication interruption leaves Live in the retained caller shell.
 (publishedSock,publishedPeer) <- S.socketPair S.AF_UNIX S.Stream S.defaultProtocol
 publishedOwner <- newIngressOwner bindingValue FromElm noopClient noopServer
 _ <- transferSocket publishedOwner publishedSock
 publishedThrow <- try (activateIngressWithHook (throwIO ThreadKilled) publishedOwner) :: IO (Either SomeException ActivationResult)
 publishedStatus <- ingressStatus publishedOwner
 _ <- retireIngress publishedOwner
 check "post-Live async retains caller shell" (case publishedThrow of Left _ -> accepted publishedStatus && phase publishedStatus==OwnerLive && endpoint publishedStatus==Just EndpointOpen; Right _ -> False)
 S.close publishedPeer
 (plainFault,plainPeer) <- S.socketPair S.AF_UNIX S.Stream S.defaultProtocol
 plainOwner <- newIngressOwnerWithHooks bindingValue FromElm noopClient noopServer (\_ -> ioError (userError "setup sync fault")) S.close
 _ <- transferSocket plainOwner plainFault
 plainRaised <- try (activateIngress plainOwner) :: IO (Either SomeException ActivationResult)
 plainStatus <- ingressStatus plainOwner
 check "setup failure and confirmed close remain inspectable" (case plainRaised of Left _ -> accepted plainStatus && phase plainStatus==OwnerFailed && endpoint plainStatus==Just EndpointConfirmed && setupFailure plainStatus/=Nothing; Right _ -> False)
 S.close plainPeer
 -- Configuration failure/close failure retains both facts without retry.
 (failing,peer3) <- S.socketPair S.AF_UNIX S.Stream S.defaultProtocol
 closeCalls <- newIORef (0::Int)
 bad <- newIngressOwnerWithHooks bindingValue FromElm noopClient noopServer (\_ -> ioError (userError "setup fault")) (\s -> modifyIORef' closeCalls (+1) >> S.close s >> ioError (userError "close fault"))
 _ <- transferSocket bad failing
 raised <- try (activateIngress bad) :: IO (Either SomeException ActivationResult)
 failed <- ingressStatus bad
 _ <- try (retireIngress bad) :: IO (Either SomeException OwnerStatus)
 _ <- try (retireIngress bad) :: IO (Either SomeException OwnerStatus)
 badRetired <- ingressStatus bad
 times <- readIORef closeCalls
 check "uncertain setup and close retained once" (case raised of Left _ -> accepted failed && accepted badRetired && phase failed==OwnerFailed && endpoint failed==Just EndpointUncertain && setupFailure failed/=Nothing && closeFailure failed/=Nothing && gate badRetired==G.Retired && endpoint badRetired==Just EndpointUncertain && phase badRetired==OwnerFailed && times==1; Right _ -> False)
 S.close peer3
 (prioritySock,priorityPeer) <- S.socketPair S.AF_UNIX S.Stream S.defaultProtocol
 priorityOwner <- newIngressOwnerWithHooks bindingValue FromElm noopClient noopServer (\_ -> ioError (userError "original sync")) (\s -> S.close s >> throwIO ThreadKilled)
 _ <- transferSocket priorityOwner prioritySock
 priorityResult <- try (activateIngress priorityOwner) :: IO (Either SomeException ActivationResult)
 priorityStatus <- ingressStatus priorityOwner
 let cleanupAsync = case priorityResult of
      Left e -> case fromException e of Just ThreadKilled -> True; _ -> False
      Right _ -> False
 check "cleanup async wins after synchronous setup failure" (cleanupAsync && endpoint priorityStatus==Just EndpointUncertain && setupFailure priorityStatus/=Nothing && closeFailure priorityStatus/=Nothing)
 S.close priorityPeer
 (originalSock,originalPeer) <- S.socketPair S.AF_UNIX S.Stream S.defaultProtocol
 originalOwner <- newIngressOwnerWithHooks bindingValue FromElm noopClient noopServer (\_ -> throwIO ThreadKilled) (\s -> S.close s >> ioError (userError "cleanup sync"))
 _ <- transferSocket originalOwner originalSock
 originalResult <- try (activateIngress originalOwner) :: IO (Either SomeException ActivationResult)
 originalStatus <- ingressStatus originalOwner
 let originalAsync = case originalResult of
      Left e -> case fromException e of Just ThreadKilled -> True; _ -> False
      Right _ -> False
 check "original async wins over cleanup sync" (originalAsync && endpoint originalStatus==Just EndpointUncertain && setupFailure originalStatus/=Nothing && closeFailure originalStatus/=Nothing)
 S.close originalPeer
 -- An activation lease prevents concurrent retirement from closing in-use FD.
 (racing,peer4) <- S.socketPair S.AF_UNIX S.Stream S.defaultProtocol
 entered <- newEmptyMVar
 release <- newEmptyMVar
 done <- newEmptyMVar
 raceCalls <- newIORef (0::Int)
 raceOwner <- newIngressOwnerWithHooks bindingValue FromElm noopClient noopServer (\s -> putMVar entered () >> takeMVar release >> F.configureSocketFlags s) (\s -> modifyIORef' raceCalls (+1) >> S.close s)
 _ <- transferSocket raceOwner racing
 void $ forkIO $ mask $ \restore -> do value <- try (restore (activateIngress raceOwner)) :: IO (Either SomeException ActivationResult); putMVar done value
 takeMVar entered
 during <- retireIngress raceOwner
 beforeClose <- readIORef raceCalls
 check "retirement defers while activation uses socket" (phase during==OwnerRetiring && endpoint during==Just EndpointOpen && beforeClose==0)
 putMVar release ()
 activation <- takeMVar done
 final <- ingressStatus raceOwner
 afterClose <- readIORef raceCalls
 check "one close after activation lease" (case activation of Right ActivationRetired -> phase final==OwnerRetired && endpoint final==Just EndpointConfirmed && afterClose==1; _ -> False)
 S.close peer4
 -- ThreadKilled during setup leaves the pre-held owner inspectable.
 (asyncSock,peer5) <- S.socketPair S.AF_UNIX S.Stream S.defaultProtocol
 asyncEntered <- newEmptyMVar
 never <- newEmptyMVar
 asyncDone <- newEmptyMVar
 asyncOwner <- newIngressOwnerWithHooks bindingValue FromElm noopClient noopServer (\_ -> putMVar asyncEntered () >> takeMVar never) S.close
 _ <- transferSocket asyncOwner asyncSock
 tid <- forkIO $ mask $ \restore -> do result <- try (restore (activateIngress asyncOwner)) :: IO (Either SomeException ActivationResult); putMVar asyncDone result
 takeMVar asyncEntered
 killThread tid
 killed <- takeMVar asyncDone
 afterKill <- ingressStatus asyncOwner
 let isKilled = case killed of
      Left e -> case fromException e of Just ThreadKilled -> True; _ -> False
      Right _ -> False
 check "setup async rethrown after retained state and close" (isKilled && accepted afterKill && phase afterKill==OwnerFailed && endpoint afterKill==Just EndpointConfirmed && setupFailure afterKill/=Nothing)
 S.close peer5
 -- Force the owner lock to be held across actual setup completion, then queue
 -- cancellation before releasing it: publication must complete first.
 (handoffSock,handoffPeer) <- S.socketPair S.AF_UNIX S.Stream S.defaultProtocol
 setupEntered <- newEmptyMVar
 setupRelease <- newEmptyMVar
 setupCompleted <- newEmptyMVar
 lockEntered <- newEmptyMVar
 lockRelease <- newEmptyMVar
 killDone <- newEmptyMVar
 handoffDone <- newEmptyMVar
 handoffOwner <- newIngressOwnerWithHooks bindingValue FromElm noopClient noopServer (\s -> putMVar setupEntered () >> takeMVar setupRelease >> F.configureSocketFlags s >> putMVar setupCompleted ()) S.close
 _ <- transferSocket handoffOwner handoffSock
 handoffThread <- forkIO $ mask $ \restore -> do result <- try (restore (activateIngress handoffOwner)) :: IO (Either SomeException ActivationResult); putMVar handoffDone result
 takeMVar setupEntered
 void $ forkIO (holdOwnerGateForTest handoffOwner lockEntered lockRelease)
 takeMVar lockEntered
 putMVar setupRelease ()
 takeMVar setupCompleted
 waitBlocked handoffThread 200
 sender <- forkIO (killThread handoffThread >> putMVar killDone ())
 waitThrowBlocked sender 200
 queued <- isEmptyMVar killDone
 check "async sender remains blocked during publication handoff" queued
 putMVar lockRelease ()
 handoffResult <- takeMVar handoffDone
 handoffStatus <- ingressStatus handoffOwner
 let handoffKilled = case handoffResult of
      Left e -> case fromException e of Just ThreadKilled -> True; _ -> False
      Right _ -> False
 check "setup completion never strands activation lease" (handoffKilled && phase handoffStatus==OwnerLive && endpoint handoffStatus==Just EndpointOpen)
 _ <- retireIngress handoffOwner
 S.close handoffPeer
 -- Force retirement to wait before the shared closer can claim its one close.
 (retrySock,retryPeer) <- S.socketPair S.AF_UNIX S.Stream S.defaultProtocol
 closeLocked <- newEmptyMVar
 closeUnlock <- newEmptyMVar
 retireDone <- newEmptyMVar
 retryCalls <- newIORef (0::Int)
 retryOwner <- newIngressOwnerWithHooks bindingValue FromElm noopClient noopServer F.configureSocketFlags (\s -> modifyIORef' retryCalls (+1) >> S.close s)
 _ <- transferSocket retryOwner retrySock
 void $ forkIO (holdCloseGateForTest retryOwner closeLocked closeUnlock)
 takeMVar closeLocked
 retireThread <- forkIO $ mask $ \restore -> do result <- try (restore (retireIngress retryOwner)) :: IO (Either SomeException OwnerStatus); putMVar retireDone result
 waitBlocked retireThread 200
 killThread retireThread
 interruptedRetire <- takeMVar retireDone
 putMVar closeUnlock ()
 pendingClose <- ingressStatus retryOwner
 recovered <- retireIngress retryOwner
 finalCalls <- readIORef retryCalls
 check "unclaimed close remains reachable after interrupted retirement" (case interruptedRetire of Left _ -> endpoint pendingClose==Just EndpointOpen && phase pendingClose==OwnerRetiring && endpoint recovered==Just EndpointConfirmed && finalCalls==1; Right _ -> False)
 S.close retryPeer
