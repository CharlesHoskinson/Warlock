port module ShortcutOutputReplay exposing (main)
import Desktop
import Json.Decode as D
import Json.Encode as E
import OutputController as Outputs
import Platform
import Shell
import Shortcuts
import SurfaceController as Controller
import UInt64
port outgoing : E.Value -> Cmd msg
bound=E.object [("lifetime",E.string "1"),("session",E.string "1"),("frontend",E.string "1")]
scope id=E.object [("id",E.string id),("generation",E.string "1")]
left=[0,0,800,600]
right=[800,0,800,600]
topology revision locations=E.object [("viewProtocol",E.int 2),("kind",E.string "view-topology"),("revision",E.string revision),("views",E.list (Tuple.first >> scope) locations),("locations",E.list (\(id,box)->E.object [("scope",scope id),("box",E.list E.int box)]) locations)]
step event model=Outputs.update event model |> Tuple.first
native value model=step (Outputs.Interaction (Desktop.Incoming value)) model
pointer serial state recipient=E.object [("protocolVersion",E.int 3),("kind",E.string "pointer-ownership"),("ownershipProtocol",E.int 1),("binding",bound),("requestId",E.string "1"),("serial",E.string serial),("state",E.string state),("owner",recipient |> Maybe.map E.string |> Maybe.withDefault E.null)]
shortcut binding serial destination=E.object [("protocolVersion",E.int 3),("kind",E.string "shell-shortcuts"),("shortcutProtocol",E.int 2),("binding",binding),("requestId",E.string "1"),("serial",E.string serial),("blocked",E.bool False),("events",if serial=="0" then E.list identity [] else E.list identity [E.object [("serial",E.string serial),("route",E.string "applications"),("output",destination)]])]
attached=E.object [("protocolVersion",E.int 3),("kind",E.string "attached"),("binding",bound)]
row id=E.object [("incarnation",E.string id),("label",E.string ("Document "++id)),("owner",E.null),("application",E.string "documents"),("minimized",E.bool False),("available",E.bool True)]
projection=E.object [("protocolVersion",E.int 3),("kind",E.string "action-projection"),("binding",bound),("requestId",E.string "1"),("context",E.object [("lifetime",E.string "1"),("epoch",E.string "1"),("output",E.string "1"),("revision",E.string "1")]),("scene",E.object [("revision",E.string "1"),("focused",E.string "1"),("windows",E.list identity [row "1",row "2"])])]
base locations=Outputs.initial |> step (Outputs.Topology (topology "1" locations)) |> native attached |> native projection |> native (pointer "1" "idle" Nothing) |> native (shortcut bound "0" E.null)
desktop model=Controller.desktop (Outputs.controller model)
owner model=D.decodeValue (D.field "focusOwner" (D.field "id" D.string)) (Outputs.frame model) |> Result.toMaybe
open model=(desktop model).open
seen model=UInt64.string (desktop model).shortcuts.seen
receive box model=native (shortcut bound "1" box) model
result=
 let ready=base [("1",left),("2",right)]
     opened=receive (E.list E.int right) ready
     duplicate=native (shortcut bound "1" (E.list E.int left)) opened
     absent=receive E.null ready
     recovered=absent |> native (shortcut bound "2" (E.list E.int right))
     ambiguous=base [("1",right),("2",right)] |> receive (E.list E.int right)
     retired=ready |> step (Outputs.Topology (topology "2" [("1",left)])) |> receive (E.list E.int right)
     moved=ready |> step (Outputs.Topology (topology "2" [("1",left),("2",[1600,0,800,600])])) |> receive (E.list E.int right)
     blocked=ready |> native (pointer "2" "move" (Just "1")) |> receive (E.list E.int right)
     released=blocked |> native (pointer "3" "idle" Nothing) |> receive (E.list E.int right)
     scaled=base [("1",left),("2",[800,0,400,300])] |> receive (E.list E.int [800,0,400,300])
     foreign=E.object [("lifetime",E.string "1"),("session",E.string "1"),("frontend",E.string "2")]
     stale=ready |> native (shortcut foreign "1" (E.list E.int right))
     rejected model=not(open model) && owner model==Just "1" && seen model=="1"
     checks=[("ReadyActualRoot",(desktop ready).windows.shell.phase==Shell.Ready), ("CurrentOutputOpens",open opened && owner opened==Just "2"), ("DuplicateCannotMove",owner duplicate==Just "2" && seen duplicate=="1"), ("UnavailableConsumed",rejected absent), ("FreshDestinationClearsOnlyShortcutRefusal",open recovered && (desktop recovered).choiceNotice==""), ("AmbiguousConsumed",rejected ambiguous), ("RemovedConsumed",rejected retired), ("MovedConsumed",rejected moved), ("HeldPointerCannotMove",rejected blocked), ("ReleasedCannotReplay",rejected released), ("LogicalScaleMatch",open scaled && owner scaled==Just "2"), ("ForeignBindingIgnored",not(open stale) && seen stale=="0"), ("NoWindowMutationAuthority",List.all (\m -> List.isEmpty (desktop m).windows.shell.issued) [opened,absent,ambiguous,retired,moved,blocked,released,scaled,stale])]
 in E.object [("checks",E.object (List.map (Tuple.mapSecond E.bool) checks)),("readyFrame",Outputs.frame ready),("openedFrame",Outputs.frame opened),("notice",E.string (desktop absent).choiceNotice)]
main : Program () () Never
main=Platform.worker {init=\_->((),outgoing result),update=\_ state->(state,Cmd.none),subscriptions=\_->Sub.none}
