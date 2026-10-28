port module Workspace2IconReplay exposing (main)

import ActionProjection as Scene
import Binding
import Desktop
import GeometryProjection as Geometry
import Json.Decode as D
import Json.Encode as E
import NativePointerFixture
import Platform
import Shell
import Surface
import TaskbarShell
import UInt64

port outgoing : E.Value -> Cmd msg
counter s = D.decodeValue UInt64.decoder (E.string s) |> Result.withDefault UInt64.zero
one = counter "1"
two = counter "2"
bound = E.object [("lifetime",E.string "1"),("session",E.string "1"),("frontend",E.string "1")]
binding = D.decodeValue Binding.decoder bound |> Result.toMaybe
window id minimized = E.object [("incarnation",E.string id),("label",E.string ("Document "++id)),("application",E.string "documents"),("owner",E.null),("minimized",E.bool minimized),("available",E.bool True)]
rows=[window "1" False,window "2" True]
sceneValue = E.object [("revision",E.string "1"),("focused",E.string "1"),("windows",E.list identity rows)]
context = {lifetime=one,epoch=one,output=one,revision=one}
geometryWindow identity workspace minimized =
    {incarnation=identity,owner=Nothing,workspace=Just workspace,workspaceGeneration=Just identity,monitor=Just UInt64.zero,outputOwnershipGeneration=Just one,workAreaRevision=Just one,workArea=Just [0,0,800,552],logicalGeometry=[40,100,320,240],visualGeometry=[40,100,320,240],nativeMode=Geometry.Ordinary,clientMode=Geometry.Ordinary,minimized=minimized,floating=True,grouped=False,fixedSize=False,constrainedSize=False,eligible=False,pin=Nothing,placementKnown=False,maximize=False,restoreGeometry=False,sizePolicy=Nothing}
base =
    let initial=Desktop.initial
        windows=initial.windows
        shell=windows.shell
        effects=shell.effects
        scene=Scene.decode sceneValue |> Result.toMaybe
        geometry=binding |> Maybe.map (\b -> {binding=b,request=one,sequence=one,context=context,focused=Just one,blocked=False,windows=[geometryWindow one "1" False,geometryWindow two "2" True]})
    in NativePointerFixture.ready {initial | windows={windows | shell={shell | binding=binding,phase=Shell.Ready,geometry=geometry,effects={effects | connected=True,observed=scene |> Maybe.map (\value -> {context=context,scene=value})}}}}
action role id trigger publication = E.object [("surfaceProtocol",E.int 2),("kind",E.string "surface-action"),("surface",E.string role),("publication",E.string publication),("lease",E.string "1"),("id",E.string id),("trigger",E.string trigger)]
dispatch role id trigger publication model = Surface.resolve one one (action role id trigger publication) model |> Maybe.map (\msg -> Desktop.update msg model) |> Maybe.withDefault (model,[])
frame request = E.object [("protocolVersion",E.int 3),("kind",E.string "action-projection"),("binding",bound),("requestId",E.string (UInt64.string request)),("context",E.object [("lifetime",E.string "1"),("epoch",E.string "1"),("output",E.string "1"),("revision",E.string "1")]),("scene",sceneValue)]
incoming raw model = Desktop.update (Desktop.Window (TaskbarShell.Native (Shell.Incoming raw))) model
wires effects = effects |> List.filterMap (\effect -> case effect of
    Desktop.Send wire -> Just wire
    Desktop.WindowEffect (Shell.Send wire) -> Just wire
    _ -> Nothing)
kind wire = D.decodeValue (D.field "kind" D.string) wire |> Result.withDefault "invalid"
mutations effects = wires effects |> List.filter (kind >> (\x -> x=="window-effect" || x=="application-launch" || x=="workspace-navigation"))
member model = model.windows.shell.geometry |> Maybe.andThen (\g -> g.windows |> List.filter (\w -> w.incarnation==two) |> List.head) |> Maybe.andThen .workspace
main : Program () () Never
main = Platform.worker {init=\_ -> ((),outgoing result),update=\_ m -> (m,Cmd.none),subscriptions=\_ -> Sub.none}
result =
    let (opened,openEffects)=dispatch "bar" "bar:group:application:documents" "pointer" "1" base
        (stale,staleEffects)=dispatch "popup" "family:2" "keyboard" "2" opened
        (pending,selectEffects)=dispatch "popup" "family:2" "keyboard" "1" opened
        request=pending.windows.shell.expected |> Maybe.withDefault UInt64.zero
        (ignored,ignoredEffects)=incoming (frame (counter "99")) pending
        (issued,issuedEffects)=incoming (frame request) pending
        (duplicate,duplicateEffects)=incoming (frame request) issued
        oldWindows=base.windows
        oldShell=oldWindows.shell
        oldEffects=oldShell.effects
        singleScene=Scene.decode (E.object [("revision",E.string "1"),("focused",E.null),("windows",E.list identity [window "2" True])]) |> Result.toMaybe
        single={base | windows={oldWindows | shell={oldShell | effects={oldEffects | observed=singleScene |> Maybe.map (\value -> {context=context,scene=value})},geometry=oldShell.geometry |> Maybe.map (\g -> {g | focused=Nothing,windows=[geometryWindow two "2" True]})}}}
        (singleIssued,singleEffects)=dispatch "bar" "bar:group:application:documents" "pointer" "1" single
        allWires=wires (openEffects++staleEffects++selectEffects++ignoredEffects++issuedEffects++duplicateEffects)
        effects=List.filter (kind >> (==) "window-effect") allWires
        checks=[("minimizedWorkspaceTwoFixture",member base==Just "2" && (base.windows.shell.geometry |> Maybe.map (\g -> List.any (\w -> w.incarnation==two && w.minimized) g.windows) |> Maybe.withDefault False))
            ,("barIconOpensGroupWithoutMutation",opened.windows.picker/=Nothing && List.isEmpty (mutations openEffects))
            ,("stalePublicationRejected",stale==opened && List.isEmpty staleEffects)
            ,("selectedMemberWaitsForFreshProjection",pending.choice/=Nothing && List.isEmpty (mutations selectEffects) && List.any (kind >> (==) "projection-request") (wires selectEffects))
            ,("wrongProjectionCannotSelect",ignored==pending && List.isEmpty (mutations ignoredEffects))
            ,("exactRestoreOnce",List.length effects==1 && (List.head effects |> Maybe.map (\w -> D.decodeValue (D.at ["intent","incarnation"] D.string) w==Ok "2" && D.decodeValue (D.at ["intent","operation"] D.string) w==Ok "restore") |> Maybe.withDefault False))
            ,("localMembershipNotRewritten",member opened==Just "2" && member pending==Just "2" && member issued==Just "2")
            ,("noTransferOrLaunch",not (List.any (kind >> (\x -> x=="application-launch" || x=="workspace-navigation")) allWires) && List.all (\w -> D.decodeValue (D.at ["intent","operation"] D.string) w/=Ok "transfer-workspace") effects)
            ,("duplicateProjectionNoReplay",duplicate==issued && List.isEmpty (mutations duplicateEffects))
            ,("singleIconRestoresExactRoot",case mutations singleEffects of
                [wire] -> kind wire=="window-effect" && D.decodeValue (D.at ["intent","incarnation"] D.string) wire==Ok "2" && D.decodeValue (D.at ["intent","operation"] D.string) wire==Ok "restore" && member singleIssued==Just "2"
                _ -> False)]
    in E.object [("checks",E.object (List.map (\(name,ok) -> (name,E.bool ok)) checks)),("wires",E.list identity allWires),("singletonWires",E.list identity (wires singleEffects)),("scope",E.string "Synthetic workspace metadata and projection; actual Desktop and Surface handlers, no native membership or receipt claim")]
