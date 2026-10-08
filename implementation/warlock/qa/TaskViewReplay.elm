port module TaskViewReplay exposing (main)

import ActionProjection as Scene
import Binding
import Desktop
import GeometryProjection as Geometry
import Json.Decode as D
import Json.Encode as E
import Platform
import Shell
import Surface
import SurfaceRenderer
import TaskView
import TaskbarShell
import UInt64

port outgoing : E.Value -> Cmd msg

counter text = D.decodeValue UInt64.decoder (E.string text) |> Result.withDefault UInt64.zero
one = counter "1"
two = counter "2"
binding = D.decodeValue Binding.decoder (E.object [("lifetime",E.string "1"),("session",E.string "1"),("frontend",E.string "1")]) |> Result.toMaybe
context = {lifetime=one,epoch=one,output=one,revision=one}
scene = Scene.decode (E.object [("revision",E.string "1"),("focused",E.string "1"),("windows",E.list identity [window "1" "Editor" True,window "2" "Files" False])]) |> Result.toMaybe
window identity label available = windowState identity label available False
windowState identity label available minimized = E.object [("incarnation",E.string identity),("label",E.string label),("owner",E.null),("application",E.string label),("minimized",E.bool minimized),("available",E.bool available)]
geometryWindow identity workspace =
    {incarnation=identity,owner=Nothing,workspace=Just workspace,workspaceGeneration=Just identity,monitor=Just UInt64.zero,outputOwnershipGeneration=Just one,workAreaRevision=Just one,workArea=Just [0,0,800,552],logicalGeometry=[40,100,320,240],visualGeometry=[40,100,320,240],nativeMode=Geometry.Ordinary,clientMode=Geometry.Ordinary,minimized=False,floating=True,grouped=False,fixedSize=False,constrainedSize=False,eligible=False,pin=Nothing,placementKnown=False,maximize=False,restoreGeometry=False,sizePolicy=Nothing}
base =
    let initial=Desktop.initial
        windows=initial.windows
        shell=windows.shell
        effects=shell.effects
        geometry=binding |> Maybe.map (\b -> {binding=b,request=one,sequence=one,context=context,focused=Just one,blocked=False,windows=[geometryWindow one "1",geometryWindow two "2"]})
    in {initial | windows={windows | shell={shell | binding=binding,phase=Shell.Ready,effects={effects | connected=True,observed=scene |> Maybe.map (\s -> {context=context,scene=s})},geometry=geometry}}}

apply message model = Desktop.update message model
scoped make model = Desktop.capture model |> Maybe.map (\stamp -> apply (make stamp) model) |> Maybe.withDefault (model,[])
restorableBase =
    let windows=base.windows
        shell=windows.shell
        effects=shell.effects
        restorableScene=Scene.decode (E.object [("revision",E.string "1"),("focused",E.string "1"),("windows",E.list identity [window "1" "Editor" True,windowState "2" "Files" True True])]) |> Result.toMaybe
    in {base | windows={windows | shell={shell | effects={effects | observed=restorableScene |> Maybe.map (\s -> {context=context,scene=s})},geometry=Maybe.map (\g -> {g | windows=List.map (\w -> if w.incarnation==two then {w | minimized=True} else w) g.windows}) shell.geometry}}}
projection request rows = projectionAt request "1" rows
projectionAt request revision rows =
    binding |> Maybe.map (\b -> E.object [("protocolVersion",E.int 3),("kind",E.string "action-projection"),("binding",Binding.encode b),("requestId",E.string (UInt64.string request)),("context",E.object [("lifetime",E.string "1"),("epoch",E.string "1"),("output",E.string "1"),("revision",E.string revision)]),("scene",E.object [("revision",E.string revision),("focused",E.string "1"),("windows",E.list identity rows)])]) |> Maybe.withDefault E.null
incoming raw = Desktop.Window (TaskbarShell.Native (Shell.Incoming raw))
mutations effects = List.filter (\effect -> case effect of
    Desktop.Send wire -> D.decodeValue (D.field "kind" D.string) wire |> Result.map (\kind -> List.member kind ["window-effect","application-launch","taskbar-pins-write"]) |> Result.withDefault False
    Desktop.WindowEffect (Shell.Send wire) -> D.decodeValue (D.field "kind" D.string) wire==Ok "window-effect"
    _ -> False) effects

main : Program () () Never
main = Platform.worker {init=\_ -> ((),outgoing result),update=\_ state -> (state,Cmd.none),subscriptions=\_ -> Sub.none}

result =
    let opened=scoped Desktop.OpenOverview base
        model=Tuple.first opened
        groups=TaskView.groups model.windows.shell |> Maybe.withDefault []
        filtered=scoped (\stamp -> Desktop.OverviewWorkspace stamp (Just "2")) model
        stale=Desktop.capture model |> Maybe.map (\stamp -> apply (Desktop.OverviewChoose stamp one) (Tuple.first filtered)) |> Maybe.withDefault filtered
        selected=scoped (\stamp -> Desktop.OverviewChoose stamp one) model
        duplicate=scoped (\stamp -> Desktop.OverviewChoose stamp one) (Tuple.first selected)
        unavailable=scoped (\stamp -> Desktop.OverviewChoose stamp two) model
        retired=scoped (\stamp -> Desktop.OverviewChoose stamp (counter "99")) model
        closed=scoped Desktop.CloseOverview model
        windows=model.windows
        shell=windows.shell
        independentRevision={model | windows={windows | shell={shell | geometry=Maybe.map (\g -> {g | context={context | revision=two}}) shell.geometry}}}
        wrongOutput={model | windows={windows | shell={shell | geometry=Maybe.map (\g -> {g | context={context | output=two}}) shell.geometry}}}
        wrongFocus={model | windows={windows | shell={shell | geometry=Maybe.map (\g -> {g | focused=Just two}) shell.geometry}}}
        wrongState={model | windows={windows | shell={shell | geometry=Maybe.map (\g -> {g | windows=List.map (\w -> {w | minimized=True}) g.windows}) shell.geometry}}}
        frame=Surface.packet one one model
        navigationOpened=scoped Desktop.OpenOverview restorableBase |> Tuple.first
        navigationSelected=scoped (\stamp -> Desktop.OverviewChoose stamp two) navigationOpened
        navigationPending=Tuple.first navigationSelected
        requested=navigationPending.windows.shell.expected |> Maybe.withDefault UInt64.zero
        restorableRows=[window "1" "Editor" True,windowState "2" "Files" True True]
        navigationCommitted=apply (incoming (projection requested restorableRows)) navigationPending
        navigationStale=apply (incoming (projection (counter "99") restorableRows)) navigationPending
        navigationRetired=apply (incoming (projectionAt requested "2" [window "1" "Editor" True])) navigationPending
        navigationRepeated=apply (incoming (projection requested restorableRows)) (Tuple.first navigationCommitted)
        issued=mutations (Tuple.second navigationCommitted)
        exactRestore=case issued of
            [Desktop.WindowEffect (Shell.Send wire)] -> D.decodeValue (D.map2 Tuple.pair (D.at ["intent","incarnation"] D.string) (D.at ["intent","operation"] D.string)) wire==Ok ("2","restore")
            _ -> False
        checks=[("groupsMatchMembership",List.map (\g -> (g.identity,List.map (.root >> UInt64.string) g.windows)) groups==[("1",["1"]),("2",["2"])]),
            ("activeWorkspaceNamed",TaskView.activeWorkspace model.windows.shell==Just "1"),
            ("openingIsObservationOnly",model.overview && List.isEmpty (mutations (Tuple.second opened))),
            ("workspaceBrowseIsLocal",(Tuple.first filtered).overviewWorkspace==Just "2" && List.isEmpty (mutations (Tuple.second filtered))),
            ("staleSelectionInert",Tuple.first stale==Tuple.first filtered && List.isEmpty (Tuple.second stale)),
            ("unavailableWorkspaceNeverActivates",Tuple.first unavailable==model && List.isEmpty (Tuple.second unavailable)),
            ("retiredIdentityNeverSubstitutes",Tuple.first retired==model && List.isEmpty (Tuple.second retired)),
            ("selectionRefreshesBeforeEffect",(Tuple.first selected).choice/=Nothing && not (Tuple.first selected).overview && List.isEmpty (mutations (Tuple.second selected))),
            ("duplicateChoiceInert",Tuple.first duplicate==Tuple.first selected && List.isEmpty (Tuple.second duplicate)),
            ("dismissalDoesNotMutate",not (Tuple.first closed).overview && List.isEmpty (mutations (Tuple.second closed))),
            ("dismissalDefersDOMFocusUntilFreshRead",(Tuple.first closed).returnFocus/=Nothing && (Tuple.first closed).windows.shell.expected/=Nothing && not (List.any (\effect -> case effect of
                Desktop.Focus _ -> True
                _ -> False) (Tuple.second closed))),
            ("independentRevisionNamespacesRemainBrowsable",TaskView.groups independentRevision.windows.shell==TaskView.groups model.windows.shell),
            ("mixedOutputMembershipWithheld",TaskView.groups wrongOutput.windows.shell==Nothing),
            ("mixedFocusMembershipWithheld",TaskView.groups wrongFocus.windows.shell==Nothing),
            ("mixedMinimizedMembershipWithheld",TaskView.groups wrongState.windows.shell==Nothing),
            ("ordinaryRendererAcceptsTaskView",SurfaceRenderer.decode frame |> Result.map (SurfaceRenderer.mode >> (==) "overview") |> Result.withDefault False),
            ("offWorkspaceSelectionRequiresFreshObservation",navigationPending.choice/=Nothing && not navigationPending.overview && List.isEmpty (mutations (Tuple.second navigationSelected))),
            ("freshObservationRestoresExactWorkspaceTwoRootOnce",exactRestore && (Tuple.first navigationCommitted).choice==Nothing),
            ("staleNavigationObservationNeverMutates",Tuple.first navigationStale==navigationPending && List.isEmpty (mutations (Tuple.second navigationStale))),
            ("retiredNavigationRootNeverSubstitutes",(Tuple.first navigationRetired).choice==Nothing && List.isEmpty (mutations (Tuple.second navigationRetired))),
            ("duplicateNavigationObservationNeverReplays",List.isEmpty (mutations (Tuple.second navigationRepeated)))]
    in E.object [("checks",E.object (List.map (\(name,passed) -> (name,E.bool passed)) checks)),("frame",frame)]
