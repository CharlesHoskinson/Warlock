port module ThreeGroupReplay exposing (main)

import ActionProjection as Scene
import Binding
import Desktop
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
bound = E.object [("lifetime",E.string "1"),("session",E.string "1"),("frontend",E.string "1")]
binding = D.decodeValue Binding.decoder bound |> Result.toMaybe
window id = E.object [("incarnation",E.string id),("label",E.string ("Document "++id)),("application",E.string "documents"),("owner",E.null),("minimized",E.bool False),("available",E.bool True)]
sceneValue = E.object [("revision",E.string "1"),("focused",E.string "1"),("windows",E.list window ["1","2","3"])]
context = {lifetime=one,epoch=one,output=one,revision=one}
base =
    let initial=Desktop.initial
        windows=initial.windows
        shell=windows.shell
        effects=shell.effects
        scene=Scene.decode sceneValue |> Result.toMaybe
    in NativePointerFixture.ready {initial | windows={windows | shell={shell | binding=binding,phase=Shell.Ready,effects={effects | connected=True,observed=scene |> Maybe.map (\value -> {context=context,scene=value})}}}}
apply message model = Desktop.update message model
open model = Shell.capture model.windows.shell |> Maybe.map (\scope -> apply (Desktop.Window (TaskbarShell.Primary scope "application:documents")) model) |> Maybe.withDefault (model,[])
control id model = Surface.controls model |> List.filter (\c -> c.id==id) |> List.head
select id model = control id model |> Maybe.andThen .message |> Maybe.map (\message -> apply message model) |> Maybe.withDefault (model,[])
frame request = E.object [("protocolVersion",E.int 3),("kind",E.string "action-projection"),("binding",bound),("requestId",E.string (UInt64.string request)),("context",E.object [("lifetime",E.string "1"),("epoch",E.string "1"),("output",E.string "1"),("revision",E.string "1")]),("scene",sceneValue)]
resume model = model.windows.shell.expected |> Maybe.map (\request -> apply (Desktop.Window (TaskbarShell.Native (Shell.Incoming (frame request)))) model) |> Maybe.withDefault (model,[])
wires effects = effects |> List.filterMap (\effect -> case effect of
    Desktop.Send wire -> Just wire
    Desktop.WindowEffect (Shell.Send wire) -> Just wire
    _ -> Nothing)
kind wire = D.decodeValue (D.field "kind" D.string) wire |> Result.withDefault "invalid"
mutations effects = wires effects |> List.filter (kind >> (\x -> x=="window-effect" || x=="application-launch"))
staleScope = D.decodeValue Shell.stampDecoder (E.object [("binding",bound),("output",E.string "1"),("revision",E.string "2")]) |> Result.toMaybe
stale model = Maybe.map2 (\scope picker -> apply (Desktop.Window (TaskbarShell.Choose scope picker.generation (counter "2"))) model) staleScope model.windows.picker |> Maybe.withDefault (model,[])
main : Program () () Never
main = Platform.worker {init=\_ -> ((),outgoing result),update=\_ m -> (m,Cmd.none),subscriptions=\_ -> Sub.none}
result =
    let (opened,openEffects)=open base
        familyRows=Surface.controls opened |> List.filter (\c -> String.startsWith "family:" c.id)
        (staleModel,staleEffects)=stale opened
        (pending,selectEffects)=select "family:2" opened
        (committed,commitEffects)=resume pending
        (duplicate,duplicateEffects)=resume committed
        allWires=wires (openEffects++staleEffects++selectEffects++commitEffects++duplicateEffects)
        actionWires=List.filter (kind >> (==) "window-effect") allWires
        checks=[("pickerOpensWithoutEffect",opened.windows.picker/=Nothing && List.isEmpty (mutations openEffects))
            ,("threeDistinctSelectableRoots",List.map .id familyRows==["family:1","family:2","family:3"] && List.all (\c -> c.enabled && c.message/=Nothing) familyRows)
            ,("staleScopeDoesNotChoose",staleModel==opened && List.isEmpty staleEffects)
            ,("selectionRequestsFreshProjection",pending.choice/=Nothing && List.isEmpty (mutations selectEffects) && List.any (kind >> (==) "projection-request") (wires selectEffects))
            ,("exactOneSelectedActivation",List.length actionWires==1 && (List.head actionWires |> Maybe.map (\w -> D.decodeValue (D.at ["intent","incarnation"] D.string) w==Ok "2" && D.decodeValue (D.at ["intent","operation"] D.string) w==Ok "activate") |> Maybe.withDefault False))
            ,("noLaunch",not (List.any (kind >> (==) "application-launch") allWires))
            ,("noAutomaticReplay",committed.choice==Nothing && duplicate==committed && List.isEmpty (mutations duplicateEffects))]
    in E.object [("checks",E.object (List.map (\(name,ok) -> (name,E.bool ok)) checks)),("familyIds",E.list (\c -> E.string c.id) familyRows),("wires",E.list identity allWires),("scope",E.string "Synthetic admitted scene; actual Desktop and Surface handlers; no native or GUI acceptance")]
