{-# LANGUAGE OverloadedStrings #-}
-- PREPARATION DRAFT ONLY. Untested, uncompiled, no custody or native authority.
-- The caller owns authenticated, bounded, deadline-aware transport and poisons
-- the session on any Left/exception or uncertain send. No adapter lock is held.
module Warlock.Ui.EngineAdapter
  ( serveRequest, clientEndpoints, emitEvent ) where

import Control.Exception (SomeAsyncException, SomeException, fromException, throwIO, try)
import Data.Text (Text)
import qualified Warlock.Ui.EngineProtocol as P
import Warlock.Ui.Owner (UiEndpoints(..), TrustedOwnerEvent(..))

-- Used only for the exact, well-formed, nonfatal Owner projection refusal.
stale :: Text
stale = "stale native UI projection"

-- Reject asynchronous exceptions to the caller unchanged. All other callback
-- failures become a bounded protocol failure; transport must poison and retain
-- its original deadline and unknown/cleanup state, never manufacture a reply.
safeCallback :: IO a -> IO (Either P.ProtocolError a)
safeCallback action = do
  result <- try action
  case result of
    Right value -> pure (Right value)
    Left problem -> case fromException problem :: Maybe SomeAsyncException of
      Just _ -> throwIO (problem :: SomeException)
      Nothing -> pure (Left P.InvalidState)

-- Broker-side dispatch. This function does no framing, authentication or lock
-- management. Caller must validate the session/frame before entry and must not
-- hold its protocol lock while invoking it. Projection comes solely from the
-- existing owner callback. The owner callback revalidates every typed event.
serveRequest :: UiEndpoints -> (TrustedOwnerEvent -> IO (Either Text ()))
             -> P.Request -> IO (Either P.ProtocolError P.Reply)
serveRequest endpoints owner request = safeCallback $ case request of
  P.GetStop -> P.StopReply <$> uiShouldStop endpoints
  P.GetRemaining -> do
    value <- uiRemainingMicros endpoints
    if value < 0 then ioError (userError "negative remaining time")
      else pure (P.RemainingReply value)
  P.GetLastProjection -> do
    current <- uiLastProjection endpoints
    encoded <- case current of
      Nothing -> pure Nothing
      Just value -> case P.projection value of
        Left _ -> ioError (userError "invalid owner projection")
        Right value' -> pure (Just value')
    pure (P.ProjectionReply encoded)
  P.OwnerEvent event -> do
    result <- owner (toOwnerEvent event)
    pure (P.EventReply (classify event result))
  where
    classify _ (Right ()) = P.Accepted
    classify event (Left reason)
      | reason == stale && isProjectionEvent event = P.Stale
      | otherwise = P.Refused

isProjectionEvent :: P.Event -> Bool
isProjectionEvent (P.Topology _ _) = False
isProjectionEvent _ = True

toOwnerEvent :: P.Event -> TrustedOwnerEvent
toOwnerEvent event = case event of
  P.Topology _ _ -> OwnerTopology payload
  P.Dismiss _ _ -> OwnerDismiss payload
  P.Escape _ _ _ -> OwnerEscape payload
  P.Reflow _ _ -> OwnerReflow payload
  where payload = P.eventJson event

-- Engine-side callback capability. The injected RPC implementation must not
-- hold a protocol/session mutex while waiting on transport or owner IO; it must
-- correlate/authenticate every reply, fail closed, and enforce original D.
-- Exceptions on bad/missing replies are deliberate: absence is not a value.
type Rpc = P.Request -> IO (Either P.ProtocolError P.Reply)

rpcReply :: Rpc -> P.Request -> IO P.Reply
rpcReply rpc request = do
  result <- rpc request
  case result of
    Right reply -> pure reply
    Left _ -> ioError (userError "engine RPC unavailable")

clientEndpoints :: P.Startup -> Rpc -> UiEndpoints
clientEndpoints startup rpc = UiEndpoints controller bar popup stopping remaining lastProjection
  where
    (controller,bar,popup) = P.startupOrigins startup
    stopping = do
      reply <- rpcReply rpc P.GetStop
      case reply of P.StopReply value -> pure value
                    _ -> ioError (userError "wrong stop reply")
    remaining = do
      reply <- rpcReply rpc P.GetRemaining
      case reply of P.RemainingReply value | value >= 0 -> pure value
                    _ -> ioError (userError "wrong remaining reply")
    lastProjection = do
      reply <- rpcReply rpc P.GetLastProjection
      case reply of P.ProjectionReply value -> pure (fmap P.projectionJson value)
                    _ -> ioError (userError "wrong projection reply")

-- The original engine producer supplies one of the four owner constructors.
-- Only typed, exact source-producer payloads cross the RPC boundary. Transport
-- failures are exceptions; they cannot be confused with stale GUI projection.
emitEvent :: Rpc -> TrustedOwnerEvent -> IO (Either Text ())
emitEvent rpc source = do
  event <- case parseSourceEvent source of
    Left _ -> ioError (userError "invalid engine owner event")
    Right value -> pure value
  reply <- rpcReply rpc (P.OwnerEvent event)
  case reply of
    P.EventReply P.Accepted -> pure (Right ())
    P.EventReply P.Stale | isProjectionEvent event -> pure (Left stale)
    P.EventReply P.Refused -> pure (Left "UI owner event refused")
    _ -> ioError (userError "wrong owner event reply")

-- Shared canonical producer parser; Owner performs its own revalidation.
parseSourceEvent :: TrustedOwnerEvent -> Either P.ProtocolError P.Event
parseSourceEvent source = case source of
  OwnerTopology value -> P.parseEvent P.OwnerTopology value
  OwnerDismiss value -> P.parseEvent P.OwnerDismiss value
  OwnerEscape value -> P.parseEvent P.OwnerEscape value
  OwnerReflow value -> P.parseEvent P.OwnerReflow value
