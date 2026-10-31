module ProtocolLateCancelProperties exposing (tests)

-- PRIVATE source proposal: imports actual T3 session; no native execution.
import Protocol.Authority as A
import Expect
import Fuzz
import Json.Decode as D
import Json.Encode as E
import Protocol.Session as Session
import Test exposing (Test, describe, fuzz, test)
import Protocol.Wire as Wire

binding frontend = E.object [("lifetime",E.string "1"),("session",E.string "2"),("frontend",E.string frontend)]
intent = E.object [("request",E.string "6"),("generation",E.string "7"),("incarnation",E.string "9007199254740993"),("operation",E.string "restore"),("context",E.object [("lifetime",E.string "1"),("epoch",E.string "3"),("output",E.string "4"),("revision",E.string "5")])]
selection = E.object [("selectionId",E.string (String.repeat 32 "a")),("scope",E.object [("id",E.string "1"),("generation",E.string "2")]),("publication",E.string "3"),("lease",E.string "4"),("controlId",E.string "restore"),("clock",E.string "CLOCK_MONOTONIC"),("acceptedMonotonicNs",E.string "1"),("deadlineMonotonicNs",E.string "2000000001")]
frame kind body = Wire.encodeEnvelope kind body
hello = frame "hello" (E.object [("binding",binding "3")])
capability request = frame "capabilities" (E.object [("binding",binding "3"),("requestId",E.string request),("operations",E.list E.string ["restore"]),("maxPreparedPerSession",E.int 1),("maxPreparedGlobal",E.int 64),("deadlineClock",E.string "CLOCK_MONOTONIC")])
selected = frame "selection" (E.object [("binding",binding "3"),("selection",selection)])
prepared frontend = frame "prepared" (E.object [("binding",binding frontend),("intent",intent),("selectionId",E.string (String.repeat 32 "a")),("deadlineMonotonicNs",E.string "2000000001"),("preparedId",E.string "8")])
lateCommitted = frame "outcome" (E.object [("binding",binding "3"),("intent",intent),("selectionId",E.string (String.repeat 32 "a")),("deadlineMonotonicNs",E.string "2000000001"),("preparedId",E.string "8"),("status",E.string "Committed"),("reason",E.string "applied"),("revision",E.string "9"),("outputGeneration",E.string "10")])
batchFields batchId request = [("binding",binding "3"),("batchId",E.string batchId),("packetSHA256",E.string (String.repeat 64 "b")),("members",E.list identity [E.object [("kind",E.string "negotiate"),("requestId",E.string request)]])]
registered request = frame "batch-registered" (E.object (batchFields (String.repeat 32 "a") request))
disposition batchId request = frame "batch-disposition" (E.object (batchFields batchId request ++ [("disposition",E.string "preflight-unsent")]))
apply msg state = Session.update msg state |> Tuple.first

withPrepared n assertion =
    case (D.decodeValue A.counterDecoder (E.string (String.fromInt n)),D.decodeValue A.intentDecoder intent,D.decodeValue A.selectionDecoder selection) of
        (Ok request,Ok target,Ok token) ->
            let attached=apply (Session.Backend hello) Session.initial
                pending=apply (Session.StartNegotiation request) attached
                capable=apply (Session.Backend (capability (String.fromInt n))) pending
                viewed=apply (Session.SetView token.scope token.publication token.lease) capable
                loaded=apply (Session.Backend selected) viewed
                choosing=apply (Session.Choose target "restore") loaded
                ready=apply (Session.Backend (prepared "3")) choosing
            in assertion ready
        _ -> Expect.fail "valid original authority fixtures rejected"

cancelDecision value = D.decodeValue (D.field "body" (D.field "decision" D.string)) value
deadline value = D.decodeValue (D.field "body" (D.field "deadlineMonotonicNs" D.string)) value

tests : Test
tests = describe "Original ARC012 late cancellation control, not native acceptance"
    [ fuzz (Fuzz.intRange 10 10000) "commit sent remains cancellable exactly once without replay or renewed deadline" <| \n ->
        withPrepared n <| \ready ->
            let (sent,commitFx)=Session.update (Session.Decide "commit") ready
                (cancelled,cancelFx)=Session.update (Session.Decide "cancel") sent
                (_,duplicateCancel)=Session.update (Session.Decide "cancel") cancelled
                (_,duplicateCommit)=Session.update (Session.Decide "commit") cancelled
            in Expect.equal
                {prepared=Just Session.Prepared,commit=1,cancel=1,decisions=[Ok "cancel"],deadlines=[Ok "2000000001"],replayCancel=0,replayCommit=0}
                {prepared=(Session.snapshot ready).status,commit=List.length commitFx,cancel=List.length cancelFx,decisions=List.map cancelDecision cancelFx,deadlines=List.map deadline cancelFx,replayCancel=List.length duplicateCancel,replayCommit=List.length duplicateCommit}
    , fuzz (Fuzz.intRange 10 10000) "known committed receipt survives explicit late cancellation control" <| \n ->
        withPrepared n <| \ready ->
            let sent=apply (Session.Decide "commit") ready
                committed=apply (Session.Backend lateCommitted) sent
                (after,cancelFx)=Session.update (Session.Decide "cancel") committed
            in Expect.equal
                {before=Just (Session.Done Wire.Committed),after=Just (Session.Done Wire.Committed),cancel=1,decision=[Ok "cancel"],deadline=[Ok "2000000001"]}
                {before=(Session.snapshot committed).status,after=(Session.snapshot after).status,cancel=List.length cancelFx,decision=List.map cancelDecision cancelFx,deadline=List.map deadline cancelFx}
    , fuzz (Fuzz.intRange 10 10000) "old grant cannot dispatch late control after a new frontend attaches" <| \n ->
        withPrepared n <| \ready ->
            let sent=apply (Session.Decide "commit") ready
                detached=apply Session.Disconnect sent
                other=apply (Session.Backend (frame "hello" (E.object [("binding",binding "4")]))) detached
                (_,cancelFx)=Session.update (Session.Decide "cancel") other
            in Expect.equal [] cancelFx
    ]
