{-# LANGUAGE OverloadedStrings #-}
-- PREPARATION ONLY. Uncompiled, unexecuted replay of the peer EngineProtocol
-- draft; wire fixtures are literal contract examples, not codec-generated
-- expected values. This exercises protocol decisions and the peer adapter
-- with stand-in callbacks over an in-memory serial RPC, not the real broker,
-- SCM credentials, held exec, real owner callbacks, custody, or GUI behavior.
module Main (main) where

import qualified DesktopIdleControls
import qualified ProtocolBoundary
import Control.Monad (forM_, unless, when)
import Data.Bits (shiftR)
import qualified Data.ByteString as B
import qualified Data.ByteString.Char8 as C
import Data.IORef (IORef, modifyIORef', newIORef, readIORef, writeIORef)
import qualified Data.Text as T
import Data.Word (Word64)
import Warlock.Protocol.Identity (Counter, parseCounter)
import qualified Warlock.Protocol.StrictJson as J
import qualified Warlock.Ui.EngineAdapter as Adapter
import Warlock.Ui.EngineProtocol
import qualified Warlock.Ui.Owner as Owner

assert :: String -> Bool -> IO ()
assert label ok = unless ok (ioError (userError label))
need :: Show e => Either e a -> IO a
need = either (ioError . userError . show) pure

-- Four octets are specified by the transport contract; JSON body strings
-- below are independently authored, including exact expected method names.
frame :: B.ByteString -> B.ByteString -> B.ByteString
frame header body = B.pack [fromIntegral (n `shiftR` 24), fromIntegral (n `shiftR` 16),
                            fromIntegral (n `shiftR` 8), fromIntegral n] <> header <> body
 where n = B.length header

requestHeader, replyHeader :: B.ByteString -> B.ByteString
requestHeader meth = "{\"version\":1,\"direction\":\"request\",\"session\":\"91\",\"request\":\"1\",\"method\":\"" <> meth <> "\"}"
replyHeader meth = "{\"version\":1,\"direction\":\"reply\",\"session\":\"91\",\"request\":\"1\",\"method\":\"" <> meth <> "\"}"

initial :: IO Startup
initial = do
 sid <- need (sessionId "91")
 need (startup 12001 12002 12003 "123456789" sid)

counter :: String -> IO Counter
counter x = need (parseCounter False (T.pack x))

-- The observer is intentionally outside the codec: it counts an attempted
-- dispatch only when acceptRequest returns Right. Production dispatch remains
-- a separate integration obligation, and stale owner event results are not
-- equivalent to stale protocol request IDs.
dispatch :: IORef Int -> Session -> B.ByteString -> IO (Session, Either ProtocolError Request)
dispatch calls session raw = do
 let (next, result) = acceptRequest session raw
 case result of Right _ -> modifyIORef' calls (+1); Left _ -> pure ()
 pure (next, result)

positive :: Startup -> (String, B.ByteString, B.ByteString, Request, B.ByteString, Reply) -> IO ()
positive start (name, meth, payload, req, replyPayload, reply) = do
 let client0 = newSession start
     server0 = newSession start
     literalRequest = frame (requestHeader meth) payload
     literalReply = frame (replyHeader meth) replyPayload
     (client1, generatedRequest) = beginRequest client0 req
 generated <- need generatedRequest
 let (_, generatedAccepted) = acceptRequest server0 generated
 assert (name ++ " generated request accepted") (generatedAccepted == Right req)
 calls <- newIORef 0
 (server1, accepted) <- dispatch calls server0 literalRequest
 assert (name ++ " accepted typed request") (accepted == Right req)
 count <- readIORef calls
 assert (name ++ " one dispatch") (count == 1)
 let (server2, encodedReply) = finishRequest server1 reply
     (client2, decodedReply) = acceptReply client1 literalReply
 encoded <- need encodedReply
 let (_, generatedReply) = acceptReply client1 encoded
 assert (name ++ " generated reply accepted") (generatedReply == Right reply)
 assert (name ++ " client receives typed reply") (decodedReply == Right reply)
 let (server3, confirmed) = confirmReplySent server2
 assert (name ++ " complete reply confirmed") (confirmed == Right ())
 assert (name ++ " sessions remain usable") (not (isPoisoned server3) && not (isPoisoned client2))

-- Drive the actual exported client/server transitions sequentially. Only the
-- latest returned Session is carried forward; the values themselves are
-- copyable, so this does not establish linear ownership in the real broker.
exchange :: String -> Session -> Session -> Request -> Reply -> IO (Session, Session)
exchange label client server request reply = do
 let (clientPending, requestBytes) = beginRequest client request
 requestRaw <- need requestBytes
 let (serverPending, received) = acceptRequest server requestRaw
 assert (label ++ " request delivered") (received == Right request)
 let (serverSending, replyBytes) = finishRequest serverPending reply
 replyRaw <- need replyBytes
 let (clientReady, receivedReply) = acceptReply clientPending replyRaw
 assert (label ++ " reply delivered") (receivedReply == Right reply)
 let (serverReady, confirmed) = confirmReplySent serverSending
 assert (label ++ " write confirmed") (confirmed == Right ())
 assert (label ++ " live after exchange") (not (isPoisoned clientReady) && not (isPoisoned serverReady))
 pure (clientReady, serverReady)

-- A correctly framed application-level stale response is a normal race: the
-- owner can change a projection after it was observed. The pure protocol
-- does not decide whether a projection is actually stale; the real callback
-- and owner route must be exercised in a separate protected integration test.
staleProjectionRace :: Startup -> Scope -> Counter -> Counter -> IO ()
staleProjectionRace start sc oldPublication oldLease = do
 old <- need (projection (J.JObject [("frame", J.JObject [("publication", J.JString "11"), ("lease", J.JString "10")])]))
 new <- need (projection (J.JObject [("frame", J.JObject [("publication", J.JString "12"), ("lease", J.JString "12")])]))
 assert "race projections differ" (old /= new)
 (c1,s1) <- exchange "read old projection" (newSession start) (newSession start)
   GetLastProjection (ProjectionReply (Just old))
 (c2,s2) <- exchange "stale escape is a normal reply" c1 s1
   (OwnerEvent (Escape sc oldPublication oldLease)) (EventReply Stale)
 _ <- exchange "read replacement projection" c2 s2 GetLastProjection (ProjectionReply (Just new))
 pure ()

-- Exercise the peer's real adapter and protocol functions in process, with
-- controlled owner callbacks and a serial in-memory RPC. This is deliberately
-- not a socket/credential/FD/real Owner integration or a concurrency test.
adapterReplay :: Startup -> Scope -> Counter -> Counter -> Counter -> IO ()
adapterReplay start sc revision lease publication = do
 let old = J.JObject [("frame", J.JObject [("publication", J.JString "11"), ("lease", J.JString "10")])]
     new = J.JObject [("frame", J.JObject [("publication", J.JString "12"), ("lease", J.JString "12")])]
 calls <- newIORef ([] :: [String])
 projectionCell <- newIORef (Just old)
 state <- newIORef (newSession start, newSession start)
 let record label action = modifyIORef' calls (++ [label]) >> action
     (controller,bar,popup) = startupOrigins start
     ownerEndpoints = Owner.UiEndpoints controller bar popup
       (record "stop" (pure False)) (record "remaining" (pure 4321))
       (record "projection" (readIORef projectionCell))
     owner event = case event of
       Owner.OwnerTopology _ -> record "topology" (pure (Right ()))
       Owner.OwnerDismiss _ -> record "dismiss" (pure (Right ()))
       Owner.OwnerEscape _ -> record "escape" (pure (Left "stale native UI projection"))
       Owner.OwnerReflow _ -> record "reflow" (pure (Right ()))
     rpc request = do
       (clientState,server) <- readIORef state
       let (clientPending, requestBytes) = beginRequest clientState request
       requestRaw <- need requestBytes
       let (serverPending, requestResult) = acceptRequest server requestRaw
       incoming <- need requestResult
       reply <- Adapter.serveRequest ownerEndpoints owner incoming >>= need
       let (serverSending, replyBytes) = finishRequest serverPending reply
       replyRaw <- need replyBytes
       let (clientReady, replyResult) = acceptReply clientPending replyRaw
       outgoing <- need replyResult
       let (serverReady, confirmed) = confirmReplySent serverSending
       _ <- need confirmed
       writeIORef state (clientReady,serverReady)
       pure (Right outgoing)
     client = Adapter.clientEndpoints start rpc
 stopped <- Owner.uiShouldStop client
 remaining <- Owner.uiRemainingMicros client
 first <- Owner.uiLastProjection client
 assert "adapter stop read" (not stopped)
 assert "adapter deadline read" (remaining == 4321)
 assert "adapter returns actual old projection" (first == Just old)
 let emit make event = Adapter.emitEvent rpc (make (eventJson event))
 topologyResult <- emit Owner.OwnerTopology (Topology revision Nothing)
 dismissResult <- emit Owner.OwnerDismiss (Dismiss sc lease)
 writeIORef projectionCell (Just new)
 escapeResult <- emit Owner.OwnerEscape (Escape sc publication lease)
 reflowResult <- emit Owner.OwnerReflow (Reflow sc lease)
 second <- Owner.uiLastProjection client
 assert "adapter events dispatch" (topologyResult == Right () && dismissResult == Right () && reflowResult == Right ())
 assert "adapter stale race remains nonfatal" (escapeResult == Left "stale native UI projection" && second == Just new)
 observed <- readIORef calls
 assert "each read and event reaches exactly its callback" (observed == ["stop","remaining","projection","topology","dismiss","escape","reflow","projection"])
 (clientReady,serverReady) <- readIORef state
 assert "adapter sequence remains live" (not (isPoisoned clientReady) && not (isPoisoned serverReady))
 -- Invalid raw input must be rejected before invoking this actual adapter.
 let malformed = frame (requestHeader "dismiss") "{\"scope\":{\"id\":\"7\",\"id\":\"7\",\"generation\":\"8\"},\"lease\":\"10\"}"
     (badState,badRequest) = acceptRequest (newSession start) malformed
 case badRequest of
   Left _ -> pure ()
   Right request -> do _ <- Adapter.serveRequest ownerEndpoints owner request; pure ()
 after <- readIORef calls
 assert "malformed frame poisons before adapter callbacks" (isPoisoned badState && after == observed)

-- Deterministically permute cases without inventing random test evidence.
-- This sequence drives only inputs below and prints the reproducible seed.
seed :: Word64
seed = 20261101
nextSeed :: Word64 -> Word64
nextSeed n = n * 6364136223846793005 + 1442695040888963407

refusal :: Startup -> String -> B.ByteString -> IO ()
refusal start label bad = do
 calls <- newIORef 0
 let good = frame (requestHeader "stop") "null"
 (poisoned, result) <- dispatch calls (newSession start) bad
 assert (label ++ " refuses") (case result of Left _ -> True; Right _ -> False)
 assert (label ++ " poisons") (isPoisoned poisoned)
 (stillPoisoned, retry) <- dispatch calls poisoned good
 observed <- readIORef calls
 assert (label ++ " cannot replay after refusal") (retry == Left Poisoned && isPoisoned stillPoisoned)
 assert (label ++ " zero dispatches") (observed == 0)

main :: IO ()
main = do
 DesktopIdleControls.run
 ProtocolBoundary.run
 start <- initial
 let startupLiteral = "{\"version\":1,\"controller\":12001,\"bar\":12002,\"popup\":12003,\"deadline\":\"123456789\",\"incarnation\":\"91\"}"
 assert "literal startup accepted" (decodeStartup startupLiteral == Right start)
 assert "encoded startup remains readable" (decodeStartup (encodeStartup start) == Right start)
 assert "original absolute deadline retained" (startupDeadline start == "123456789")
 assert "startup rejects unknown field" (case decodeStartup "{\"version\":1,\"controller\":12001,\"bar\":12002,\"popup\":12003,\"deadline\":\"123456789\",\"incarnation\":\"91\",\"extra\":0}" of Left _ -> True; _ -> False)
 assert "startup rejects duplicate field" (case decodeStartup "{\"version\":1,\"controller\":12001,\"bar\":12002,\"popup\":12003,\"deadline\":\"123456789\",\"incarnation\":\"91\",\"version\":1}" of Left _ -> True; _ -> False)
 assert "startup refuses duplicate origins" (case sessionId "91" >>= startup 12001 12001 12003 "123456789" of Left _ -> True; _ -> False)
 sc <- need (scope "7" "8")
 revision <- counter "9"
 lease <- counter "10"
 publication <- counter "11"
 let cases =
       [("stop", "stop", "null", GetStop, "false", StopReply False)
       ,("remaining", "remaining", "null", GetRemaining, "4321", RemainingReply 4321)
       ,("projection", "lastProjection", "null", GetLastProjection, "null", ProjectionReply Nothing)
       ,("topology", "topology", "{\"viewProtocol\":1,\"kind\":\"view-topology\",\"revision\":\"9\",\"views\":[]}", OwnerEvent (Topology revision Nothing), "\"accepted\"", EventReply Accepted)
       ,("dismiss", "dismiss", "{\"scope\":{\"id\":\"7\",\"generation\":\"8\"},\"lease\":\"10\"}", OwnerEvent (Dismiss sc lease), "\"stale\"", EventReply Stale)
       ,("escape", "escape", "{\"scope\":{\"id\":\"7\",\"generation\":\"8\"},\"publication\":\"11\",\"lease\":\"10\"}", OwnerEvent (Escape sc publication lease), "\"accepted\"", EventReply Accepted)
       ,("reflow", "reflow", "{\"scope\":{\"id\":\"7\",\"generation\":\"8\"},\"lease\":\"10\"}", OwnerEvent (Reflow sc lease), "\"refused\"", EventReply Refused)]
 forM_ cases (positive start)
 staleProjectionRace start sc publication lease
 adapterReplay start sc revision lease publication
 let headerExtra = "{\"version\":1,\"direction\":\"request\",\"session\":\"91\",\"request\":\"1\",\"method\":\"stop\",\"extra\":0}"
     headerDuplicate = "{\"version\":1,\"direction\":\"request\",\"session\":\"91\",\"request\":\"1\",\"method\":\"stop\",\"session\":\"91\"}"
     headerStale = "{\"version\":1,\"direction\":\"request\",\"session\":\"91\",\"request\":\"2\",\"method\":\"stop\"}"
     headerForeign = "{\"version\":1,\"direction\":\"request\",\"session\":\"92\",\"request\":\"1\",\"method\":\"stop\"}"
     headerZero = "{\"version\":1,\"direction\":\"request\",\"session\":\"91\",\"request\":\"0\",\"method\":\"stop\"}"
     headerOverflow = "{\"version\":1,\"direction\":\"request\",\"session\":\"91\",\"request\":\"18446744073709551616\",\"method\":\"stop\"}"
     badCases = [("unknown", frame headerExtra "null"), ("duplicate", frame headerDuplicate "null"),
                 ("unexpected ID", frame headerStale "null"), ("stale incarnation", frame headerForeign "null"),
                 ("wrapped zero ID", frame headerZero "null"), ("overflow ID", frame headerOverflow "null"),
                 ("oversized", B.replicate (maxFrameBytes + 1) 32),
                 ("oversized payload", frame (requestHeader "stop") (B.replicate (maxPayloadBytes + 1) 32)),
                 ("duplicate nested scope", frame (requestHeader "dismiss") "{\"scope\":{\"id\":\"7\",\"generation\":\"8\",\"id\":\"7\"},\"lease\":\"10\"}"),
                 ("extra nested scope", frame (requestHeader "dismiss") "{\"scope\":{\"id\":\"7\",\"generation\":\"8\",\"extra\":0},\"lease\":\"10\"}"),
                 ("deep payload", frame (requestHeader "stop") (C.replicate 32 '[' <> "null" <> C.replicate 32 ']'))]
 forM_ badCases (uncurry (refusal start))
 forM_ (take 128 (iterate nextSeed seed)) $ \n -> do
   let extra = "{\"version\":1,\"direction\":\"request\",\"session\":\"91\",\"request\":\"1\",\"method\":\"stop\",\"unknown" <> C.pack (show n) <> "\":0}"
       overflow = "{\"version\":1,\"direction\":\"request\",\"session\":\"91\",\"request\":\"" <> C.pack (show (toInteger n + 18446744073709551616)) <> "\",\"method\":\"stop\"}"
       depth = 16 + fromIntegral (n `mod` 48)
       bodySize = maxPayloadBytes + 1 + fromIntegral (n `mod` 64)
       generated = case n `mod` 4 of
         0 -> frame extra "null"
         1 -> frame overflow "null"
         2 -> frame (requestHeader "stop") (C.replicate depth '[' <> "null" <> C.replicate depth ']')
         _ -> frame (requestHeader "stop") (B.replicate bodySize 32)
   refusal start ("generated malformed input seed=" ++ show n) generated
 -- After an actual successful exchange, the old request ID is a replay.
 let (server1, accepted) = acceptRequest (newSession start) (frame (requestHeader "stop") "null")
 assert "first request accepted" (accepted == Right GetStop)
 let (server2, response) = finishRequest server1 (StopReply False)
 assert "first request completed" (case response of Right _ -> True; _ -> False)
 let (unconfirmed, tooEarly) = acceptRequest server2 (frame (requestHeader "stop") "null")
 assert "request before confirmed write poisons" (tooEarly == Left InvalidState && isPoisoned unconfirmed)
 let (afterUncertain, retryUncertain) = acceptRequest (poisonSession server2) (frame (requestHeader "stop") "null")
 assert "uncertain reply write cannot replay" (retryUncertain == Left Poisoned && isPoisoned afterUncertain)
 let (serverReady, confirmation) = confirmReplySent server2
 assert "write confirmation returns server to ready" (confirmation == Right ())
 calls <- newIORef 0
 (server3, replayed) <- dispatch calls serverReady (frame (requestHeader "stop") "null")
 count <- readIORef calls
 assert "old request is refused and poisons" (replayed == Left Replay && isPoisoned server3 && count == 0)
 -- The transport must call poisonSession on EOF; these are the observable
 -- state consequences, not a test that any actual transport detects EOF.
 eofCalls <- newIORef 0
 (afterEof, eofResult) <- dispatch eofCalls (poisonSession (newSession start)) (frame (requestHeader "stop") "null")
 eofCount <- readIORef eofCalls
 assert "EOF-poisoned server refuses without dispatch" (eofResult == Left Poisoned && isPoisoned afterEof && eofCount == 0)
 let (clientAfterEof, clientEofResult) = beginRequest (poisonSession (newSession start)) GetStop
 assert "EOF-poisoned client cannot start" (clientEofResult == Left Poisoned && isPoisoned clientAfterEof)
 -- Validate the full ID-domain boundary without claiming the opaque session
 -- was advanced through 2^64 requests. Exhausted transition needs a reviewed
 -- internal seam or separate model proof, not an exposed arbitrary-ID API.
 assert "max request ID representable" (case requestId "18446744073709551615" of Right _ -> True; _ -> False)
 assert "request ID overflow refused" (case requestId "18446744073709551616" of Left _ -> True; _ -> False)
 let (pending, begun) = beginRequest (newSession start) GetStop
 assert "pending control issued" (case begun of Right _ -> True; _ -> False)
 let (doubled, duplicateBegin) = beginRequest pending GetRemaining
 assert "second outstanding request poisons" (duplicateBegin == Left InvalidState && isPoisoned doubled)
 let badReply = frame (replyHeader "remaining") "1"
     (failed, wrong) = acceptReply pending badReply
 assert "wrong reply method poisons client" (wrong == Left WrongReply && isPoisoned failed)
 when (not (isPoisoned failed)) (ioError (userError "unreachable"))
 putStrLn ("engine protocol replay draft seed=" ++ show seed)
