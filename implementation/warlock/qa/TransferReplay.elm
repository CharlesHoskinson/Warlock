port module TransferReplay exposing (main)

import Binding
import Desktop
import Effects
import Json.Decode as D
import Json.Encode as E
import Platform
import Shell
import SnapReplay as Fixture
import Surface
import TaskView
import Transfer
import UInt64

port outgoing : E.Value -> Cmd msg

one = Fixture.counter "1"
scoped make model = Desktop.capture model |> Maybe.map (\stamp -> Desktop.update (make stamp) model) |> Maybe.withDefault (model,[])
withShell shell model = let windows=model.windows in {model|windows={windows|shell=shell}}
membership shell = TaskView.groups shell |> Maybe.withDefault [] |> List.map .identity
receipt intent status = E.object [("kind",E.string "receipt"),("effectProtocol",E.int 2),("intent",Effects.encodeIntent intent),("status",E.string status)]

result binding =
    let initial=Fixture.readyFor binding
        baseShell=initial.windows.shell
        caps={effects=True,operations=["maximize","restore-geometry","snap","transfer-workspace"]}
        shell={baseShell|geometryCaps=Just caps}
        base=withShell shell initial
        geometry=Fixture.geometryFor binding
        p={source="1",sourceGeneration=Fixture.counter "4",destination="2"}
        (begun,wire,error)=Effects.beginGeometry caps geometry (Effects.TransferWorkspace p) one shell.effects
        intent=begun.transaction |> Maybe.map .intent
        settle status state = intent |> Maybe.map (\i -> Effects.apply (receipt i status) state |> (\(next,_,_) -> next)) |> Maybe.withDefault state
        wrong= intent |> Maybe.map (\i -> Effects.apply (receipt {i|operation=Effects.TransferWorkspace {p|destination="3"}} "Committed") begun |> (\(next,_,_) -> next)) |> Maybe.withDefault begun
        raced={geometry|windows=List.map (\w -> {w|workspace=Just "2",workspaceGeneration=Just (Fixture.counter "5")}) geometry.windows}
        pendingShell={shell|effects=begun,geometry=Just raced}
        committed=settle "Committed" begun
        refused=settle "Refused" begun
        unknown=settle "Unknown" begun
        opened=scoped Desktop.OpenOverview base |> Tuple.first
        chooser=scoped (\stamp -> Desktop.OpenOverviewTransfer stamp one) opened |> Tuple.first
        cancelled=scoped Desktop.CancelOverviewTransfer chooser
        selected=scoped (\stamp -> Desktop.OverviewTransfer stamp one "2") chooser
        stale=Desktop.capture opened |> Maybe.map (\stamp -> Desktop.update (Desktop.OverviewTransfer stamp one "2") chooser) |> Maybe.withDefault (chooser,[])
        ordinary=Surface.controls opened
        destinations=Surface.controls chooser
        duplicate=Effects.beginGeometry caps geometry (Effects.TransferWorkspace p) one begun
        unnegotiated=Effects.beginGeometry {caps|operations=["snap"]} geometry (Effects.TransferWorkspace p) one shell.effects
        invalid=Transfer.propose geometry one "-99"
        cancelledNoEffect=not (List.any (\e -> case e of
            Desktop.WindowEffect (Shell.Send w) -> D.decodeValue (D.field "kind" D.string) w==Ok "window-effect"
            _ -> False) (Tuple.second cancelled))
        checks=
            [("sharedAllocatorCreatesOneTypedTransfer",error==Nothing && wire/=Nothing && begun.request==one && List.length begun.unresolved==1)
            ,("intentStrictRoundtrip",intent |> Maybe.map (\i -> D.decodeValue Effects.intentDecoder (Effects.encodeIntent i)==Ok i) |> Maybe.withDefault False)
            ,("pendingNativeObservationCannotMoveMembership",membership pendingShell==["1"])
            ,("wrongDestinationReceiptCannotMoveMembership",membership {pendingShell|effects=wrong}==["1"] && wrong==begun)
            ,("matchingCommittedReceiptReleasesMembership",membership {pendingShell|effects=committed}==["2"] && List.isEmpty committed.unresolved)
            ,("refusalKeepsOriginalObservedWorkspace",membership {shell|effects=refused}==["1"])
            ,("unknownKeepsMembershipAndCustody",membership {pendingShell|effects=unknown}==["1"] && List.length unknown.unresolved==1)
            ,("duplicateCannotSubmitAgain",let (_,sent,_) = duplicate in sent==Nothing)
            ,("unnegotiatedCannotSubmit",let (_,sent,_) = unnegotiated in sent==Nothing)
            ,("specialAndSameWorkspaceRejected",invalid==Nothing && Transfer.propose geometry one "1"==Nothing)
            ,("taskViewExposesMoveAction",List.any (\c -> c.id=="overview:transfer:1" && c.enabled) ordinary)
            ,("emptyWorkspaceDestinationAvailable",List.any (\c -> c.id=="overview:destination:2" && c.enabled) destinations)
            ,("cancelReturnsToOverviewWithoutEffect",(Tuple.first cancelled).overviewTransfer==Nothing && (Tuple.first cancelled).overview && cancelledNoEffect)
            ,("selectionRequiresFreshObservations",(Tuple.first selected).choice/=Nothing && (Tuple.first selected).windows.shell.geometryExpected/=Nothing && not (Tuple.first selected).overview)
            ,("staleViewCannotChooseDestination",(Tuple.first stale).choice==Nothing)
            ,("duplicateTerminalReceiptDoesNotReplay",settle "Committed" committed==committed)]
    in E.object [("checks",E.object (List.map (\(name,ok) -> (name,E.bool ok)) checks)),("frame",Surface.packet one one opened),("chooserFrame",Surface.packet one one chooser),("intent",intent |> Maybe.map Effects.encodeIntent |> Maybe.withDefault E.null)]

main : Program () () Never
main = Platform.worker {init=\_ -> ((),outgoing (D.decodeValue Binding.decoder Fixture.bound |> Result.map result |> Result.withDefault E.null)),update=\_ state -> (state,Cmd.none),subscriptions=\_ -> Sub.none}
