port module WorkspaceNavigationReplay exposing (main)

import ActionProjection as Scene
import Binding
import Desktop
import Effects
import WorkspaceNavigation as Navigation
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
row id generation = {identity=id,generation=counter generation,monitor=UInt64.zero,outputOwnershipGeneration=one}
main : Program () () Never
main = Platform.worker {init=\_ -> ((),outgoing result),update=\_ state -> (state,Cmd.none),subscriptions=\_ -> Sub.none}
result =
 let navigation=binding |> Maybe.map (\b -> Navigation.bind b Navigation.initial) |> Maybe.withDefault Navigation.initial
     ready={navigation|ready=True}
     inventory=binding |> Maybe.map (\b -> {binding=b,request=one,sequence=one,revision=one,output=one,active=Just "1",rows=[row "1" "1",row "2" "2",row "3" "3"]})
     opened=scoped Desktop.OpenOverview {base|workspaceNavigation=ready,workspaceInventory=inventory} |> Tuple.first
     selected=scoped (\stamp -> Desktop.OverviewNavigateWorkspace stamp "3") opened
     pending=Tuple.first selected
     repeated=scoped (\stamp -> Desktop.OverviewNavigateWorkspace stamp "3") pending
     current=pending.workspaceNavigation.record
     timeout=current |> Maybe.map (\r -> Navigation.expire r.intent pending.workspaceNavigation) |> Maybe.withDefault ready
     unknown={pending|workspaceNavigation=timeout}
     reopened=scoped Desktop.OpenOverview unknown |> Tuple.first
     dismissed=scoped Desktop.CloseOverview reopened
     receipt outcomeStatus record = E.object [("protocolVersion",E.int 3),("kind",E.string "workspace-navigation-outcome"),("workspaceProtocol",E.int 1),("binding",Binding.encode record.binding),("intent",Navigation.encodeIntent record.intent),("status",E.string outcomeStatus),("reason",E.string (if outcomeStatus=="Committed" then "applied" else "dependency-mismatch"))]
     committed=current |> Maybe.map (\r -> Navigation.receive (receipt "Committed" r) timeout) |> Maybe.withDefault ready
     refused=current |> Maybe.map (\r -> Navigation.receive (receipt "Refused" r) timeout) |> Maybe.withDefault ready
     foreign=current |> Maybe.map (\r -> Navigation.receive (receipt "Committed" {r|intent={request=counter "9",generation=r.intent.generation,source=r.intent.source,destination=r.intent.destination,context=r.intent.context}}) timeout) |> Maybe.withDefault ready
     (recovering,read)=Navigation.recover timeout
     disconnected=Navigation.disconnect pending.workspaceNavigation
     blockedWindow=scoped (\stamp -> Desktop.OverviewChoose stamp one) reopened
     controls=Surface.controls opened
     status model=model.record |> Maybe.map .status
     sends effects=List.filterMap (\effect -> case effect of
         Desktop.Send wire -> D.decodeValue (D.field "kind" D.string) wire |> Result.toMaybe
         Desktop.WindowEffect (Shell.Send wire) -> D.decodeValue (D.field "kind" D.string) wire |> Result.toMaybe
         _ -> Nothing) effects
     checks=[("goEmptyWorkspaceControl",List.any (\c -> c.id=="overview:go:3" && c.enabled && c.message/=Nothing) controls)
         ,("populatedDestinationCannotGo",Desktop.workspaceNavigationIntent opened "2"==Nothing)
         ,("activeDestinationCannotGo",Desktop.workspaceNavigationIntent opened "1"==Nothing)
         ,("oneTypedNavigation",sends (Tuple.second selected)==["workspace-navigation"])
         ,("pendingFeedback",status pending.workspaceNavigation==Just Navigation.Pending && (D.decodeValue (D.field "status" D.string) (Surface.packet one one pending) |> Result.map (String.contains "switching") |> Result.withDefault False))
         ,("duplicateSuppressed",List.isEmpty (Tuple.second repeated))
         ,("deadlineUnknownNoReplay",status timeout==Just Navigation.Unknown && Navigation.blocked timeout)
         ,("unknownCanReopenAndDismiss",reopened.overview && not (Tuple.first dismissed).overview && not (List.member "workspace-navigation" (sends (Tuple.second dismissed))))
         ,("unknownCannotMutateWindow",List.isEmpty (Tuple.second blockedWindow))
         ,("unknownHasReadOnlyRecovery",List.any (\c -> c.id=="overview:workspace-refresh") (Surface.controls reopened) && (Maybe.map (D.decodeValue (D.field "kind" D.string)) read==Just (Ok "workspace-navigation-recover")))
         ,("recoveryDoesNotDuplicateRead",Navigation.recover recovering |> Tuple.second |> (==) Nothing)
         ,("committedExactReceipt",status committed==Just Navigation.Committed && not (Navigation.blocked committed))
         ,("refusedRetainsDestinationContext",status refused==Just Navigation.Refused && refused.returning && refused.origin==Just "3")
         ,("foreignCannotSettle",foreign==timeout)
         ,("disconnectNeverReplays",status disconnected==Just Navigation.Unknown && disconnected.binding==Nothing && not disconnected.ready)
         ]
 in E.object [("checks",E.object (List.map (\(name,value)->(name,E.bool value)) checks))]
