port module PreviewPaintReplay exposing (main)
import Json.Decode as D
import Json.Encode as E
import Platform
import PreviewPaintGate as Gate
port outgoing : E.Value -> Cmd msg
command kind request owner=E.object [("kind",E.string kind),("job",E.object [("binding",E.string owner),("context",E.string "exact-context"),("request",E.string request),("origin",E.string request),("clock",E.string "1"),("deadline",E.string "5000")])]
batch items=E.list identity [E.object [("identity",E.string "family:1"),("commands",E.list identity items)]]
wire raw=E.encode 0 raw
empty raw=D.decodeValue (D.list D.value) raw |> Result.map List.isEmpty |> Result.withDefault False
ticket requests=D.decodeValue (D.index 0 D.value) requests |> Result.withDefault E.null
result=
 let acquire=command "acquire" "1" "owner-a"
     cancel=command "cancel" "1" "owner-a"
     original=batch [acquire]
     (pending,immediate,requests)=Gate.queue original Gate.initial
     paint=ticket requests
     (sent,forwarded)=Gate.painted paint pending
     (_,duplicate)=Gate.painted paint sent
     (cancelled,control,_)=Gate.queue (batch [cancel]) pending
     (_,late)=Gate.painted paint cancelled
     (otherRequest,_,_)=Gate.queue (batch [command "cancel" "2" "owner-a"]) pending
     (_,keptRequest)=Gate.painted paint otherRequest
     (otherOwner,_,_)=Gate.queue (batch [command "cancel" "1" "owner-b"]) pending
     (_,keptOwner)=Gate.painted paint otherOwner
     (_,_,duplicateRequests)=Gate.queue original pending
     (fresh,_,freshRequests)=Gate.queue (batch [command "acquire" "2" "owner-a"]) cancelled
     (afterOld,oldWire)=Gate.painted paint fresh
     (_,freshWire)=Gate.painted (ticket freshRequests) afterOld
     (_,controls,_)=Gate.queue (batch [command "release" "1" "owner-a",command "ack" "1" "owner-a"]) pending
     invalid raw=Gate.painted raw pending |> Tuple.second |> empty
     checks=[("OriginalAcquireWaitsForPaint",empty immediate && not (empty requests)),
         ("PaintForwardsExactOriginalJobAndDeadline",wire forwarded==wire original),
         ("DuplicatePaintCannotReplayAcquire",empty duplicate),
         ("ExactCancelRetiresUnsentAcquireImmediately",wire control==wire (batch [cancel]) && empty late),
         ("DifferentRequestCannotCancelPendingAcquire",wire keptRequest==wire original),
         ("DifferentBindingCannotCancelPendingAcquire",wire keptOwner==wire original),
         ("RepeatedPendingAcquireDoesNotMintAnotherTicket",empty duplicateRequests),
         ("OldPaintCannotBorrowFreshRequest",empty oldWire && wire freshWire==wire (batch [command "acquire" "2" "owner-a"])),
         ("ReleaseAndAckNeverWaitForPaint",not (empty controls)),
         ("ForeignNumericExtraPaintCannotCapture",invalid (E.object [("ticket",E.string "99")]) && invalid (E.object [("ticket",E.int 1)]) && invalid (E.object [("ticket",E.string "1"),("job",E.string "borrowed")]))]
 in E.object [("checks",E.object (List.map (Tuple.mapSecond E.bool) checks))]
main : Program () () Never
main=Platform.worker {init=\_->((),outgoing result),update=\_ state->(state,Cmd.none),subscriptions=\_->Sub.none}
