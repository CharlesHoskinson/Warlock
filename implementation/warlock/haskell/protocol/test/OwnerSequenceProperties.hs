{-# LANGUAGE OverloadedStrings #-}
-- Root-owned deterministic sequence properties over the actual socket owner.
module Main (main) where
import Control.Monad (unless,void)
import Control.Exception (bracket,finally,mask)
import qualified Data.ByteString.Char8 as B
import Data.IORef (newIORef,modifyIORef',readIORef)
import qualified Network.Socket as S
import qualified Network.Socket.ByteString as N
import Warlock.Protocol.Ingress.Internal
import qualified Warlock.Transport.SocketFlags as F

data Expected = PendingExpected | LiveExpected | RetiredExpected deriving (Eq,Show)
data Action = Activate | Retire | OfferAgain | Enqueue deriving (Eq,Show)

steps :: Integer -> Int -> [Action]
steps _ 0 = []
steps seed count = action : steps next (count - 1)
  where
    next = (1664525 * seed + 1013904223) `mod` 4294967296
    action = case (next `div` 65536) `mod` 4 of
      0 -> Activate
      1 -> Retire
      2 -> OfferAgain
      _ -> Enqueue

check :: Integer -> [Action] -> String -> Bool -> IO ()
check seed trace label ok = unless ok (ioError (userError (label ++ "; seed=" ++ show seed ++ "; trace=" ++ show trace)))

oneCase :: Integer -> IO Bool
oneCase seed = do
  bindingValue <- either (ioError . userError . show) pure (ingressBinding "1" "2" "3")
  closes <- newIORef (0::Int)
  effects <- newIORef (0::Int)
  let recordEffect _ = modifyIORef' effects (+1)
      closer socket = modifyIORef' closes (+1) >> S.close socket
      trace = steps seed 24
      assert = check seed trace
  owner <- newIngressOwnerWithHooks bindingValue FromElm recordEffect recordEffect F.configureSocketFlags closer
  -- The socket-free owner is retained before any socket transfer. Cleanup
  -- retires through that owner; it never retries its accepted raw socket.
  extraTransferred <- newIORef False
  let pair = S.socketPair S.AF_UNIX S.Stream S.defaultProtocol
      releaseOwned (socket,peerSocket) =
        (do status <- ingressStatus owner
            if accepted status then void (retireIngress owner) else S.close socket)
        `finally` S.close peerSocket
      releaseExtra (socket,peerSocket) =
        (do consumed <- readIORef extraTransferred
            unless consumed (S.close socket))
        `finally` S.close peerSocket
  bracket pair releaseOwned $ \(owned,_) ->
    bracket pair releaseExtra $ \(extra,extraPeer) -> do
      offered <- transferSocket owner owned
      assert "initial ownership transfer" (offered==OfferAccepted)
      let loop expected everLive [] = pure (expected,everLive)
          loop expected everLive (action:rest) = do
            next <- case action of
              Activate -> do
                outcome <- activateIngress owner
                let wanted = if expected==PendingExpected then ActivationLive else ActivationUnavailable
                assert "activation contract" (outcome==wanted)
                pure (if expected==PendingExpected then LiveExpected else expected)
              Retire -> retireIngress owner >> pure RetiredExpected
              OfferAgain -> do
                outcome <- mask $ \_ -> do
                  result <- transferSocket owner extra
                  modifyIORef' extraTransferred (\old -> old || result==OfferAccepted)
                  pure result
                assert "second socket remains unconsumed" (outcome==OfferRefused)
                pure expected
              Enqueue -> do
                outcome <- enqueueIngress owner Ordinary (B.pack "{}")
                -- These bytes are deliberately unvalidated outbound data. Failure
                -- must not create authority, close custody or invoke a handler.
                assert "invalid outbound admission is refused without losing custody" (if expected==LiveExpected then case outcome of Left (InvalidPayload _) -> True; _ -> False else outcome==Left Closed)
                pure expected
            status <- ingressStatus owner
            count <- readIORef closes
            let wantedPhase = case next of PendingExpected -> OwnerPending; LiveExpected -> OwnerLive; RetiredExpected -> OwnerRetired
                wantedEndpoint = if next==RetiredExpected then EndpointConfirmed else EndpointOpen
            assert "monotone accepted custody and observable endpoint" (accepted status && phase status==wantedPhase && endpoint status==Just wantedEndpoint)
            assert "one closer after retirement only" (count == if next==RetiredExpected then 1 else 0)
            loop next (everLive || next==LiveExpected) rest
      (_,reachedLive) <- loop PendingExpected False trace
      final <- retireIngress owner
      count <- readIORef closes
      seen <- readIORef effects
      assert "final resource retirement exactly once without effects" (phase final==OwnerRetired && endpoint final==Just EndpointConfirmed && count==1 && seen==0)
      N.sendAll extra "x"
      observed <- N.recv extraPeer 1
      assert "unconsumed second socket remains usable" (observed=="x")
      pure reachedLive
main :: IO ()
main = do
  positives <- mapM oneCase [20261031..20261286]
  unless (or positives) (ioError (userError "no live owner reached by generated sequences"))
  putStrLn ("PASS owner sequences seed20261031 cases256 actions24; live-positive cases=" ++ show (length (filter id positives)))
