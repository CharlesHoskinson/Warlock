port module TaskViewReplay exposing (main)

import ActionProjection as Scene
import Binding
import Desktop
import Effects
import WorkspaceInventory
import NativePointerFixture
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
    in NativePointerFixture.ready {initial | windows={windows | shell={shell | binding=binding,phase=Shell.Ready,effects={effects | connected=True,observed=scene |> Maybe.map (\s -> {context=context,scene=s})},geometry=geometry}}}

apply message model = Desktop.update message model
scoped make model = Desktop.capture model |> Maybe.map (\stamp -> apply (make stamp) model) |> Maybe.withDefault (model,[])
restorableBase =
    let windows=base.windows
        shell=windows.shell
        effects=shell.effects
        restorableScene=Scene.decode (E.object [("revision",E.string "1"),("focused",E.string "1"),("windows",E.list identity [window "1" "Editor" True,windowState "2" "Files" True True])]) |> Result.toMaybe
    in NativePointerFixture.ready {base | windows={windows | shell={shell | effects={effects | observed=restorableScene |> Maybe.map (\s -> {context=context,scene=s})},geometry=Maybe.map (\g -> {g | windows=List.map (\w -> if w.incarnation==two then {w | minimized=True} else w) g.windows}) shell.geometry}}}
projection request rows = projectionAt request "1" rows
projectionAt request revision rows =
    binding |> Maybe.map (\b -> E.object [("protocolVersion",E.int 3),("kind",E.string "action-projection"),("binding",Binding.encode b),("requestId",E.string (UInt64.string request)),("context",E.object [("lifetime",E.string "1"),("epoch",E.string "1"),("output",E.string "1"),("revision",E.string revision)]),("scene",E.object [("revision",E.string revision),("focused",E.string "1"),("windows",E.list identity rows)])]) |> Maybe.withDefault E.null
incoming raw = Desktop.Window (TaskbarShell.Native (Shell.Incoming raw))
mutations effects = List.filter (\effect -> case effect of
    Desktop.Send wire -> D.decodeValue (D.field "kind" D.string) wire |> Result.map (\kind -> List.member kind ["window-effect","application-launch","taskbar-pins-write"]) |> Result.withDefault False
    Desktop.WindowEffect (Shell.Send wire) -> D.decodeValue (D.field "kind" D.string) wire==Ok "window-effect"
    _ -> False) effects

outcome status intent =
    binding |> Maybe.map (\b -> E.object [("protocolVersion",E.int 3),("kind",E.string "effect-outcome"),("effectProtocol",E.int 1),("binding",Binding.encode b),("intent",Effects.encodeIntent intent),("status",E.string status),("reason",E.string "implicit-transfer-required"),("revision",E.string "1"),("outputGeneration",E.string "1")]) |> Maybe.withDefault E.null
receiveOutcome status model =
    model.windows.shell.effects.transaction |> Maybe.map (\t -> apply (incoming (outcome status t.intent)) model) |> Maybe.withDefault (model,[])
refreshAfterOutcome model =
    model.windows.shell.expected |> Maybe.map (\request -> apply (incoming (projection request [window "1" "Editor" True,windowState "2" "Files" True True])) model) |> Maybe.withDefault (model,[])
inventoryRow workspace generation = E.object [("identity",E.string workspace),("generation",E.string generation),("monitor",E.string "0"),("outputOwnershipGeneration",E.string "1")]
inventoryFrame request active rows =
    binding |> Maybe.map (\b -> E.object [("protocolVersion",E.int 3),("kind",E.string "geometry-facts"),("geometryProtocol",E.int 3),("binding",Binding.encode b),("requestId",E.string request),("sequence",E.string "1"),("revision",E.string "1"),("outputGeneration",E.string "1"),("facts",E.object [("focused",E.null),("inputBlocked",E.bool False),("windows",E.list identity []),("workspaces",E.list identity rows),("activeWorkspace",active)])]) |> Maybe.withDefault E.null
emptyBase =
    let windows=base.windows
        shell=windows.shell
        effects=shell.effects
        empty=Scene.decode (E.object [("revision",E.string "1"),("focused",E.null),("windows",E.list identity [])]) |> Result.toMaybe
    in {base | windows={windows | shell={shell | geometry=Nothing,geometryCaps=Just {effects=False,operations=[]},geometryExpected=Just one,effects={effects | observed=empty |> Maybe.map (\emptyScene -> {context=context,scene=emptyScene})}}}}

focuses effects = effects |> List.filterMap (\effect -> case effect of
    Desktop.Focus target -> Just target
    _ -> Nothing)

main : Program () () Never
main = Platform.worker {init=\_ -> ((),outgoing result),update=\_ state -> (state,Cmd.none),subscriptions=\_ -> Sub.none}

result =
    let opened=scoped Desktop.OpenOverview base
        model=Tuple.first opened
        groups=TaskView.groups model.windows.shell |> Maybe.withDefault []
        filtered=scoped (\stamp -> Desktop.OverviewWorkspace stamp (Just "2")) model
        filterStates current = Surface.packet one one current |> D.decodeValue (D.field "popup" (D.list (D.map2 Tuple.pair (D.field "id" D.string) (D.maybe (D.field "checked" D.bool))))) |> Result.withDefault [] |> List.filter (\(id,_) -> id=="overview:all" || String.startsWith "overview:workspace:" id)
        stale=Desktop.capture model |> Maybe.map (\stamp -> apply (Desktop.OverviewChoose stamp one) (Tuple.first filtered)) |> Maybe.withDefault filtered
        selected=scoped (\stamp -> Desktop.OverviewChoose stamp one) model
        duplicate=scoped (\stamp -> Desktop.OverviewChoose stamp one) (Tuple.first selected)
        unavailable=scoped (\stamp -> Desktop.OverviewChoose stamp two) model
        retired=scoped (\stamp -> Desktop.OverviewChoose stamp (counter "99")) model
        closed=scoped Desktop.CloseOverview model
        windows=model.windows
        shell=windows.shell
        effects=shell.effects
        independentRevision={model | windows={windows | shell={shell | geometry=Maybe.map (\g -> {g | context={context | revision=two}}) shell.geometry}}}
        wrongOutput={model | windows={windows | shell={shell | geometry=Maybe.map (\g -> {g | context={context | output=two}}) shell.geometry}}}
        wrongFocus={model | windows={windows | shell={shell | geometry=Maybe.map (\g -> {g | focused=Just two}) shell.geometry}}}
        wrongState={model | windows={windows | shell={shell | geometry=Maybe.map (\g -> {g | windows=List.map (\w -> {w | minimized=True}) g.windows}) shell.geometry}}}
        transferInventory=binding |> Maybe.map (\b -> {binding=b,request=one,sequence=one,revision=one,output=one,active=Just "1",rows=[{identity="1",generation=one,monitor=UInt64.zero,outputOwnershipGeneration=one},{identity="2",generation=two,monitor=UInt64.zero,outputOwnershipGeneration=one}]})
        transferOrigin={model | overviewWorkspace=Just "2",overviewTransfer=Just two,workspaceInventory=transferInventory}
        remainingScene=Scene.decode (E.object [("revision",E.string "1"),("focused",E.string "1"),("windows",E.list identity [window "1" "Editor" True])]) |> Result.toMaybe
        retiredTransfer={transferOrigin | windows={windows | shell={shell | effects={effects | observed=remainingScene |> Maybe.map (\s -> {context=context,scene=s})},geometry=Maybe.map (\g -> {g | windows=[geometryWindow one "1"]}) shell.geometry}}}
        retirementTick current=scoped (\stamp -> Desktop.SearchQuery stamp "") current
        retiredTransferResult=retirementTick retiredTransfer
        retiredTransferModel=Tuple.first retiredTransferResult
        duplicateRetirement=retirementTick retiredTransferModel
        wholeWorkspaceRetired=retirementTick {retiredTransfer | workspaceInventory=Nothing}
        incoherentTransfer=retirementTick {retiredTransfer | windows={windows | shell={shell | effects={effects | observed=remainingScene |> Maybe.map (\s -> {context=context,scene=s})},geometry=Maybe.map (\g -> {g | context={context | output=two},windows=[geometryWindow one "1"]}) shell.geometry}}}
        existingTransfer=retirementTick transferOrigin
        closedTransfer=retirementTick {retiredTransfer | overview=False}
        replacementScene=Scene.decode (E.object [("revision",E.string "1"),("focused",E.string "1"),("windows",E.list identity [window "1" "Editor" True,window "3" "Files" True])]) |> Result.toMaybe
        replacementGeometry=geometryWindow (counter "3") "2"
        replacementTransfer=retirementTick {transferOrigin | windows={windows | shell={shell | effects={effects | observed=replacementScene |> Maybe.map (\s -> {context=context,scene=s})},geometry=Maybe.map (\g -> {g | windows=[geometryWindow one "1",{replacementGeometry | workspaceGeneration=Just two}]}) shell.geometry}}}
        retirementChecks=[("retiredTransferReturnsCurrentRetainedWorkspaceFocus",retiredTransferModel.overview && retiredTransferModel.overviewTransfer==Nothing && retiredTransferModel.overviewWorkspace==Just "2" && focuses (Tuple.second retiredTransferResult)==[Desktop.key retiredTransferModel "overview:workspace:2"] && List.isEmpty (mutations (Tuple.second retiredTransferResult))),
            ("retiredTransferChooserHasVisibleBrowseAndDismissal",Surface.controls retiredTransferModel |> List.any (\control -> control.ariaLabel=="Close Task View and return to windows" && control.enabled)),
            ("retiredTransferDoesNotRepeatFocus",List.isEmpty (focuses (Tuple.second duplicateRetirement)) && List.isEmpty (mutations (Tuple.second duplicateRetirement))),
            ("retiredTransferAndWorkspaceReturnAll",(Tuple.first wholeWorkspaceRetired).overviewTransfer==Nothing && (Tuple.first wholeWorkspaceRetired).overviewWorkspace==Nothing && focuses (Tuple.second wholeWorkspaceRetired)==[Desktop.key (Tuple.first wholeWorkspaceRetired) "overview:all"]),
            ("incoherentTransferObservationCannotRetireSelection",(Tuple.first incoherentTransfer).overviewTransfer==Just two && List.isEmpty (focuses (Tuple.second incoherentTransfer)) && List.isEmpty (mutations (Tuple.second incoherentTransfer))),
            ("existingUnavailableExactMemberKeepsTransferChooser",(Tuple.first existingTransfer).overviewTransfer==Just two && List.isEmpty (focuses (Tuple.second existingTransfer))),
            ("closedTransferNeverRefocuses",List.isEmpty (focuses (Tuple.second closedTransfer)) && List.isEmpty (mutations (Tuple.second closedTransfer))),
            ("sameApplicationNewIncarnationNeverSubstitutes",(Tuple.first replacementTransfer).overviewTransfer==Nothing && (Tuple.first replacementTransfer).choice==Nothing && List.isEmpty (mutations (Tuple.second replacementTransfer)) && focuses (Tuple.second replacementTransfer)==[Desktop.key (Tuple.first replacementTransfer) "overview:workspace:2"])]
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
        recoveryFiltered=scoped (\stamp -> Desktop.OverviewWorkspace stamp (Just "2")) navigationOpened |> Tuple.first
        recoveryChosen=scoped (\stamp -> Desktop.OverviewChoose stamp two) recoveryFiltered |> Tuple.first
        recoveryIssued=apply (incoming (projection (recoveryChosen.windows.shell.expected |> Maybe.withDefault UInt64.zero) restorableRows)) recoveryChosen
        recoveryPending=Tuple.first recoveryIssued
        refused=receiveOutcome "Refused" recoveryPending
        restored=refreshAfterOutcome (Tuple.first refused)
        restoredModel=Tuple.first restored
        repeated=receiveOutcome "Refused" restoredModel
        committed=receiveOutcome "Committed" recoveryPending |> Tuple.first |> refreshAfterOutcome
        unknown=receiveOutcome "Unknown" recoveryPending |> Tuple.first |> refreshAfterOutcome
        foreign=recoveryPending.windows.shell.effects.transaction |> Maybe.map (\t -> apply (incoming (outcome "Refused" (let original=t.intent in {original | incarnation=counter "99"}))) recoveryPending) |> Maybe.withDefault (recoveryPending,[])
        busy=Tuple.first refused
        otherInterface=refreshAfterOutcome {busy | open=True}
        otherModel=Tuple.first otherInterface
        dismissedOther=refreshAfterOutcome {otherModel | open=False}
        replacedWindows=busy.windows
        replacedShell=replacedWindows.shell
        replacedBinding=D.decodeValue Binding.decoder (E.object [("lifetime",E.string "1"),("session",E.string "1"),("frontend",E.string "2")]) |> Result.toMaybe
        replaced=refreshAfterOutcome {busy | windows={replacedWindows | shell={replacedShell | binding=replacedBinding}}}
        retiredGeometry={busy | windows={replacedWindows | shell={replacedShell | geometry=Maybe.map (\g -> {g | context={context | revision=two},windows=[geometryWindow one "1"]}) replacedShell.geometry}}}
        missingWindow=apply (incoming (projectionAt (busy.windows.shell.expected |> Maybe.withDefault UInt64.zero) "2" [window "1" "Editor" True])) retiredGeometry
        recoveryChecks=[("matchedRefusalWaitsForFreshRead",not (Tuple.first refused).overview && (Tuple.first refused).windows.shell.expected/=Nothing && List.isEmpty (mutations (Tuple.second refused))),
            ("exactRefusalRestoresFilteredOverview",restoredModel.overview && restoredModel.overviewWorkspace==Just "2" && List.isEmpty (mutations (Tuple.second restored))),
            ("restoredEligibleFamilyGetsCurrentFocus",focuses (Tuple.second restored)==[Desktop.key restoredModel "overview:family:2"]),
            ("duplicateRefusalCannotReopenOrReplay",Tuple.first repeated==restoredModel && List.isEmpty (Tuple.second repeated)),
            ("committedChoiceStaysClosed",not (Tuple.first committed).overview && List.isEmpty (mutations (Tuple.second committed))),
            ("unknownChoiceStaysClosedWithoutReplay",not (Tuple.first unknown).overview && List.isEmpty (mutations (Tuple.second unknown))),
            ("foreignIntentCannotReturn",Tuple.first foreign==recoveryPending && List.isEmpty (Tuple.second foreign)),
            ("anotherInterfaceCancelsReturn",not (Tuple.first otherInterface).overview && not (Tuple.first dismissedOther).overview && List.isEmpty (mutations (Tuple.second otherInterface))),
            ("replacementAuthorityCannotReturn",not (Tuple.first replaced).overview && List.isEmpty (mutations (Tuple.second replaced))),
            ("retiredFamilyReturnsToAllWindows",(Tuple.first missingWindow).overview && (Tuple.first missingWindow).overviewWorkspace==Nothing && focuses (Tuple.second missingWindow)==[Desktop.key (Tuple.first missingWindow) "overview:all"])]
        emptyFrame=inventoryFrame "1" (E.string "3") [inventoryRow "1" "1",inventoryRow "3" "3"]
        observedEmpty=apply (incoming emptyFrame) emptyBase
        openEmpty=scoped Desktop.OpenOverview (Tuple.first observedEmpty)
        browseEmpty=scoped (\stamp -> Desktop.OverviewWorkspace stamp (Just "3")) (Tuple.first openEmpty)
        emptyModel=Tuple.first browseEmpty
        emptyGroups=Desktop.taskViewGroups emptyModel |> Maybe.withDefault []
        emptyClosed=scoped Desktop.CloseOverview emptyModel
        foreignEmpty=apply (incoming (inventoryFrame "99" (E.string "3") [inventoryRow "3" "3"])) emptyBase
        malformedEmpty=apply (incoming (inventoryFrame "1" (E.string "3") [inventoryRow "3" "3",inventoryRow "3" "4"])) emptyBase
        staleInventory={emptyModel | workspaceInventory=emptyModel.workspaceInventory |> Maybe.map (\inventory -> {inventory | sequence=two})}
        retiredInventory={emptyModel | workspaceInventory=emptyModel.workspaceInventory |> Maybe.map (\inventory -> {inventory | active=Just "1",rows=List.filter (\row -> row.identity=="1") inventory.rows})}
        retiredEmpty=apply Desktop.RetryWindows retiredInventory
        transferWindows=base.windows
        transferShell=transferWindows.shell
        transferEffects=transferShell.effects
        transferIntent={request=one,generation=one,incarnation=one,operation=Effects.TransferWorkspace {source="4",sourceGeneration=counter "4",destination="1"},context=context}
        transferModel={base | workspaceInventory=binding |> Maybe.map (\b -> {binding=b,request=one,sequence=one,revision=one,output=one,active=Just "1",rows=[{identity="1",generation=one,monitor=UInt64.zero,outputOwnershipGeneration=one},{identity="2",generation=two,monitor=UInt64.zero,outputOwnershipGeneration=one}]}),windows={transferWindows | shell={transferShell | effects={transferEffects | unresolved=[{intent=transferIntent,status=Effects.Unknown,effectProtocol=2}]}}}}
        inventoryChecks=[("unconfirmedTransferRetainsSourceFamilyWithoutInventingNativeOwner",Desktop.taskViewGroups transferModel |> Maybe.map (List.filter (\group -> group.identity=="4") >> List.concatMap .windows >> List.map .root >> (==) [one]) |> Maybe.withDefault False),
            ("emptyInventoryComesThroughExactRootReceipt",(Tuple.first observedEmpty).workspaceInventory/=Nothing && List.map .identity emptyGroups==["1","3"]),
            ("nativeActiveEmptyMarkerDoesNotNeedFocusedWindow",List.filter .active emptyGroups |> List.map .identity |> (==) ["3"]),
            ("emptyWorkspaceOpensAndBrowsesWithoutEffects",emptyModel.overview && emptyModel.overviewWorkspace==Just "3" && List.all (List.isEmpty << .windows) emptyGroups && List.isEmpty (mutations (Tuple.second openEmpty++Tuple.second browseEmpty))),
            ("emptyWorkspaceKeepsVisibleDismissal",Surface.controls emptyModel |> List.any (\control -> control.enabled && control.ariaLabel=="Close Task View and return to windows")),
            ("emptySelectionHasExplicitNotice",D.decodeValue (D.field "status" D.string) (Surface.packet one one emptyModel) |> Result.map (String.contains "no windows") |> Result.withDefault False),
            ("emptyWorkspaceDismissalIsReadOnly",not (Tuple.first emptyClosed).overview && List.isEmpty (mutations (Tuple.second emptyClosed))),
            ("foreignGeometryCannotInventEmptyWorkspace",(Tuple.first foreignEmpty).workspaceInventory==Nothing && (Tuple.first foreignEmpty).windows.shell.geometry==Nothing),
            ("duplicateWorkspacePacketRejectedByRoot",(Tuple.first malformedEmpty).workspaceInventory==Nothing && (Tuple.first malformedEmpty).windows.shell.geometry==Nothing),
            ("differentGeometrySequenceCannotJoinInventory",Desktop.taskViewGroups staleInventory==Nothing),
            ("retiredEmptySelectionFallsBackToAll",(Tuple.first retiredEmpty).overviewWorkspace==Nothing && focuses (Tuple.second retiredEmpty)==[Desktop.key (Tuple.first retiredEmpty) "overview:all"])]
        checks=[("groupsMatchMembership",List.map (\g -> (g.identity,List.map (.root >> UInt64.string) g.windows)) groups==[("1",["1"]),("2",["2"])]),
            ("activeWorkspaceNamed",TaskView.activeWorkspace model.windows.shell==Just "1"),
            ("openingIsObservationOnly",model.overview && List.isEmpty (mutations (Tuple.second opened))),
            ("workspaceBrowseIsLocal",(Tuple.first filtered).overviewWorkspace==Just "2" && List.isEmpty (mutations (Tuple.second filtered))),
            ("overviewInitialAccessibleFilterSelection",filterStates model==[("overview:all",Just True),("overview:workspace:1",Just False),("overview:workspace:2",Just False)]),
            ("overviewAccessibleFilterFollowsReadOnlyBrowse",filterStates (Tuple.first filtered)==[("overview:all",Just False),("overview:workspace:1",Just False),("overview:workspace:2",Just True)] && List.isEmpty (mutations (Tuple.second filtered))),
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
    in E.object [("checks",E.object (List.map (\(name,passed) -> (name,E.bool passed)) (checks++recoveryChecks++inventoryChecks++retirementChecks))),("frame",frame)]
