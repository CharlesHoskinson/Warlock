port module ReceiptOutputLifecycleReplay exposing (main)

import Binding
import Desktop
import Effects
import Json.Decode as D
import Json.Encode as E
import NativeOutcome
import OutputController as Outputs
import OutputRetirementReplay as Fixture
import Platform
import Shell
import SurfaceController as Controller
import TaskbarShell
import UInt64

port outgoing : E.Value -> Cmd msg
counter s = D.decodeValue UInt64.decoder (E.string s) |> Result.withDefault UInt64.zero
shell m = (Fixture.desktop m).windows.shell
effects m = (shell m).effects
transaction m = (effects m).transaction
status m = transaction m |> Maybe.map (.status >> Effects.statusName) |> Maybe.withDefault "none"
step e m = Outputs.update e m
receive raw m = step (Outputs.Interaction (Desktop.Incoming raw)) m
act incarnation m = Shell.capture (shell m)
    |> Maybe.map (\stamp -> step (Outputs.Interaction (Desktop.Window (TaskbarShell.Native (Shell.Act stamp Effects.Minimize (counter incarnation))))) m)
    |> Maybe.withDefault (m,[])
write e = case e of
    Controller.DesktopEffect (Desktop.WindowEffect (Shell.Send raw)) -> D.decodeValue (D.field "kind" D.string) raw == Ok "window-effect"
    _ -> False
writes = List.filter write >> List.length
wire binding protocol intent result extra = E.object
    ([ ("protocolVersion",E.int 3), ("kind",E.string "effect-outcome"), ("effectProtocol",E.int protocol)
     , ("binding",binding), ("intent",Effects.encodeIntent intent), ("status",E.string result)
     , ("reason",E.string "applied"), ("revision",E.string "2"), ("outputGeneration",E.string "1") ] ++ extra)
exact intent result = wire Fixture.bound 1 intent result []
common before after = (effects before).observed == (effects after).observed
    && (effects before).request == (effects after).request && (effects before).generation == (effects after).generation
quiet before (after,emitted) = common before after && writes emitted == 0
sameCorrelation before after = effects before == effects after && (shell before).issued == (shell after).issued
hasOld intent m = List.any (\t -> t.intent == intent && t.effectProtocol == 1) (effects m).unresolved
hasIssued intent m = List.any (\t -> t.intent == intent && t.protocol == 1) (shell m).issued
oldStatus intent m = (effects m).unresolved |> List.filter (\t -> t.intent == intent && t.effectProtocol == 1) |> List.head |> Maybe.map (.status >> Effects.statusName) |> Maybe.withDefault "none"
otherUnresolved intent m = List.filter (\t -> not (t.intent == intent && t.effectProtocol == 1)) (effects m).unresolved
otherIssued intent m = List.filter (\t -> not (t.intent == intent && t.protocol == 1)) (shell m).issued
recordState m = E.object
    [ ("transaction",transaction m |> Maybe.map (\t -> E.object [("intent",Effects.encodeIntent t.intent),("status",E.string (Effects.statusName t.status)),("protocol",E.int t.effectProtocol)]) |> Maybe.withDefault E.null)
    , ("unresolved", E.list (\t -> E.object [("intent",Effects.encodeIntent t.intent),("status",E.string (Effects.statusName t.status)),("protocol",E.int t.effectProtocol)]) (effects m).unresolved)
    , ("issued",E.list (\t -> E.object [("intent",Effects.encodeIntent t.intent),("protocol",E.int t.protocol),("binding",Binding.encode t.binding)]) (shell m).issued)
    , ("request",E.string (UInt64.string (effects m).request)), ("generation",E.string (UInt64.string (effects m).generation))
    , ("observed",Effects.encode (effects m)), ("decoderRefusal",(shell m).decoderRefusal |> Maybe.map E.string |> Maybe.withDefault E.null) ]
check name value = (name,E.bool value)
result seed =
    let ready = Fixture.base [("1",Fixture.left),("2",Fixture.right)]
        (pending,emitted) = act "1" ready
        intent = transaction pending |> Maybe.map .intent
        (retired,retirementEffects) = step (Outputs.Topology (Fixture.topology "2" [("2",Fixture.right)])) pending
        projected = Fixture.reconcile "2" retired
        (newer,newEffects) = act "2" projected
        (disconnected,disconnectedEffects) = receive (E.object [("protocolVersion",E.int 3),("kind",E.string "host-disconnected")]) pending
        test i =
            let receiptCases name =
                    let (same,sameEffects) = receive (exact i name) pending
                        (late,lateEffects) = receive (exact i name) projected
                        (oldAfterNew,newReceiptEffects) = receive (exact i name) newer
                        (duplicate,duplicateEffects) = receive (exact i name) late
                        keeps = name=="Unknown"
                        sameOk = status same==name && hasOld i same==keeps && hasIssued i same==keeps && quiet pending (same,sameEffects)
                        lateOk = status late==name && hasOld i late==keeps && hasIssued i late==keeps && (not keeps || oldStatus i late=="Unknown") && quiet projected (late,lateEffects)
                        newOk = transaction oldAfterNew==transaction newer && otherUnresolved i oldAfterNew==otherUnresolved i newer && otherIssued i oldAfterNew==otherIssued i newer && hasOld i oldAfterNew==keeps && hasIssued i oldAfterNew==keeps && (not keeps || oldStatus i oldAfterNew=="Unknown") && quiet newer (oldAfterNew,newReceiptEffects)
                        duplicateOk = if keeps then True else sameCorrelation late duplicate && quiet late (duplicate,duplicateEffects)
                    in (name,E.object [("wire",exact i name),("sameAuthority",recordState same),("afterOutput",recordState late),("afterNewTransaction",recordState oldAfterNew), ("checks",E.object [check "sameExactStatusAndOwnership" sameOk,check "lateExactStatusAndOwnership" lateOk,check "newTransactionAndOtherRecordsPreserved" newOk,check "terminalDuplicateNoop" duplicateOk])])
                unknownFrame = E.object [("protocolVersion",E.int 3),("kind",E.string "host-reservation-unknown"),("binding",Fixture.bound),("record",E.object [("schema",E.int 2),("effectProtocol",E.int 1),("binding",Fixture.bound),("intent",Effects.encodeIntent i),("status",E.string "Unknown")])]
                (recovered,recoveryEffects) = receive unknownFrame projected
                context = i.context
                variant = counter (String.fromInt (100 + modBy 100000 seed))
                foreignBinding = E.object [("lifetime",E.string "1"),("session",E.string "99"),("frontend",E.string "1")]
                invalid =
                    [ ("binding",wire foreignBinding 1 i "Committed" [])
                    , ("request",exact {i|request=variant} "Committed")
                    , ("generation",exact {i|generation=variant} "Committed")
                    , ("incarnation",exact {i|incarnation=variant} "Committed")
                    , ("operation",exact {i|operation=Effects.Restore} "Committed")
                    , ("lifetime",exact {i|context={context|lifetime=variant}} "Committed")
                    , ("epoch",exact {i|context={context|epoch=variant}} "Committed")
                    , ("output",exact {i|context={context|output=variant}} "Committed")
                    , ("revision",exact {i|context={context|revision=variant}} "Committed")
                    , ("protocol",wire Fixture.bound 2 i "Committed" [])
                    , ("malformed",wire Fixture.bound 1 i "Committed" [("unexpected",E.bool True)]) ]
                negative (name,raw) =
                    let (after,out) = receive raw newer
                    in (name,E.object [("input",raw),("after",recordState after),check "unchangedCorrelationNoMutation" (sameCorrelation newer after && quiet newer (after,out))])
            in E.object
                [ ("inputIntent",Effects.encodeIntent i)
                , ("checks",E.object
                    [check "readyPendingActuallyEmitsOne" (Shell.available (shell ready) && writes emitted==1 && status pending=="Pending" && hasOld i pending && hasIssued i pending)
                    ,check "topologyAdmitsNewOutput" ((shell retired).expected/=Nothing && ((effects projected).observed |> Maybe.map (\s -> s.context.output==counter "2") |> Maybe.withDefault False) && writes retirementEffects==0)
                    ,check "newerDifferentIncarnationActuallyPending" (writes newEffects==1 && status newer=="Pending" && (transaction newer |> Maybe.map (\t -> t.intent.incarnation==counter "2" && t.intent/=i) |> Maybe.withDefault False) && hasOld i newer && hasIssued i newer)
                    ,check "disconnectMakesUnknownWithoutEffect" (status disconnected=="Unknown" && oldStatus i disconnected=="Unknown" && writes disconnectedEffects==0)
                    ,check "validatedUnknownRecordNormalizesMatchingReservation" (oldStatus i recovered=="Unknown" && hasIssued i recovered && quiet projected (recovered,recoveryEffects)) ])
                , ("initialProjection",Fixture.projection),("topology",Fixture.topology "2" [("2",Fixture.right)]),("pending",recordState pending),("projected",recordState projected),("newer",recordState newer),("disconnected",recordState disconnected),("unknownRecoveryInput",unknownFrame),("recovered",recordState recovered)
                , ("receipts",E.object (List.map (\s -> (s,receiptCases s)) (if modBy 2 seed==0 then ["Committed","Refused","Unknown"] else ["Unknown","Refused","Committed"])))
                , ("foreign",E.object (List.map negative invalid))
                , ("cancelledShapeDiagnosticOnly",E.bool (NativeOutcome.valid (exact i "Cancelled"))) ]
    in E.object [("seed",E.int seed),("case",intent |> Maybe.map test |> Maybe.withDefault (E.object [check "intentCreated" False]))]
main : Program Int () Never
main = Platform.worker {init=\seed -> ((),outgoing (result seed)),update=\_ model -> (model,Cmd.none),subscriptions=\_ -> Sub.none}
