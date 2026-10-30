port module ReceiptOutputLifecycleReplay exposing (main)

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

counter text = D.decodeValue UInt64.decoder (E.string text) |> Result.withDefault UInt64.zero
shell model = (Fixture.desktop model).windows.shell
transaction model = (shell model).effects.transaction
status model = transaction model |> Maybe.map (.status >> Effects.statusName) |> Maybe.withDefault "none"
unresolved model = (shell model).effects.unresolved
wireStatus intent value = E.object
    [ ("protocolVersion", E.int 3), ("kind", E.string "effect-outcome")
    , ("effectProtocol", E.int 1), ("binding", Fixture.bound)
    , ("intent", Effects.encodeIntent intent), ("status", E.string value)
    , ("reason", E.string "applied"), ("revision", E.string "2")
    , ("outputGeneration", E.string "1") ]
windowEffect effect = case effect of
    Controller.DesktopEffect (Desktop.WindowEffect (Shell.Send raw)) ->
        D.decodeValue (D.field "kind" D.string) raw == Ok "window-effect"
    _ -> False
countWrites = List.filter windowEffect >> List.length
step event model = Outputs.update event model
receive raw model = step (Outputs.Interaction (Desktop.Incoming raw)) model

result =
    let
        ready = Fixture.base [("1",Fixture.left),("2",Fixture.right)]
        act = Shell.capture (shell ready)
            |> Maybe.map (\stamp -> step (Outputs.Interaction (Desktop.Window (TaskbarShell.Native (Shell.Act stamp Effects.Minimize (counter "1"))))) ready)
            |> Maybe.withDefault (ready,[])
        (pending,issuedEffects) = act
        intent = transaction pending |> Maybe.map .intent
        sameReceipt = intent |> Maybe.map (\i -> receive (wireStatus i "Committed") pending) |> Maybe.withDefault (pending,[])
        (retired,retirementEffects) = step (Outputs.Topology (Fixture.topology "2" [("2",Fixture.right)])) pending
        projected = Fixture.reconcile "2" retired
        wrongReceipt = intent |> Maybe.map (\i -> receive (wireStatus {i | request=counter "99"} "Committed") projected) |> Maybe.withDefault (projected,[])
        (late,lateEffects) = intent |> Maybe.map (\i -> receive (wireStatus i "Committed") projected) |> Maybe.withDefault (projected,[])
        cancellationGate = intent |> Maybe.map (\i -> NativeOutcome.valid (wireStatus i "Cancelled")) |> Maybe.withDefault False
        ids model = E.list (\entry -> E.object [("intent",Effects.encodeIntent entry.intent),("status",E.string (Effects.statusName entry.status)),("protocol",E.int entry.effectProtocol)]) (unresolved model)
        snapshot model = E.object [("status",E.string (status model)),("unresolved",ids model),("issued",E.int (List.length (shell model).issued)),("expected",(shell model).expected |> Maybe.map (UInt64.string >> E.string) |> Maybe.withDefault E.null)]
        checks =
            [ ("validReadyAndOneActuallyEmittedEffect",Shell.available (shell ready) && countWrites issuedEffects==1 && status pending=="Pending" && intent/=Nothing)
            , ("sameAuthorityExactReceiptCommits",status (Tuple.first sameReceipt)=="Committed")
            , ("retirementActuallyRequestedProjection",(shell retired).expected/=Nothing)
            , ("newOutputActuallyAdmitted",(shell projected).effects.observed |> Maybe.map (\s -> s.context.output==counter "2") |> Maybe.withDefault False)
            , ("mismatchedReceiptPreservesCorrelatedState",(shell (Tuple.first wrongReceipt)).effects==(shell projected).effects)
            , ("noNewWindowEffectOnTopologyOrLateReceipt",countWrites retirementEffects==0 && countWrites lateEffects==0)
            ]
    in E.object
        [ ("checks", E.object (List.map (Tuple.mapSecond E.bool) checks))
        , ("pending",snapshot pending), ("projected",snapshot projected), ("lateExactCommitted",snapshot late)
        , ("cancelledPassesNativeOutcomeShape",E.bool cancellationGate)
        , ("note",E.string "Report actual states; a matching late native outcome after output change must be independently judged against the original correlation contract.") ]

main : Program () () Never
main = Platform.worker {init=\_ -> ((),outgoing result),update=\_ model -> (model,Cmd.none),subscriptions=\_ -> Sub.none}
