port module OutputRetirementReplay exposing (main)
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
frameValue field model=D.decodeValue (D.at ["frame",field] D.string) (Outputs.frame model) |> Result.withDefault "0"
dismiss id shown=E.object [("scope",scope id),("lease",E.string (frameValue "lease" shown))]
action id surface identity shown=E.object [("viewProtocol",E.int 1),("kind",E.string "view-action"),("scope",scope id),("action",E.object [("surfaceProtocol",E.int 2),("kind",E.string "surface-action"),("surface",E.string surface),("publication",E.string (frameValue "publication" shown)),("lease",E.string (frameValue "lease" shown)),("id",E.string identity),("trigger",E.string "keyboard")])]
result=
 let ready=base [("1",left),("2",right)]
     opened=receive (E.list E.int right) ready
     removed=step (Outputs.Topology (topology "2" [("1",left)])) opened
     unrelated=step (Outputs.Topology (topology "2" [("2",right)])) opened
     replaced=step (Outputs.Topology (topology "3" [("1",left),("3",right)])) removed
     duplicate=native (shortcut bound "1" (E.list E.int right)) replaced
     reopened=native (shortcut bound "2" (E.list E.int left)) replaced
     oldDismiss=step (Outputs.Dismiss (dismiss "2" opened)) reopened
     staleAction=step (Outputs.Renderer (action "2" "bar" "bar:applications" reopened)) removed
     stalePopup=step (Outputs.Renderer (action "2" "popup" "control:refresh" reopened)) reopened
     empty=step (Outputs.Topology (topology "3" [])) removed
     returned=step (Outputs.Topology (topology "4" [("3",right)])) empty
     returnedDuplicate=native (shortcut bound "1" (E.list E.int right)) returned
     checks=[("FocusedPopupInitiallyOnRight",open opened && owner opened==Just "2"), ("RemovalDismissesToDeclaredSurvivor",not(open removed) && owner removed==Just "1"), ("UnrelatedOutputRemovalPreservesPopup",open unrelated && owner unrelated==Just "2"), ("ReplacementCannotReplayShortcut",not(open duplicate) && owner duplicate==Just "1"), ("FreshSurvivorKeyboardShortcutWorks",open reopened && owner reopened==Just "1"), ("RetiredDismissCannotCloseFreshPopup",open oldDismiss && Outputs.frame oldDismiss==Outputs.frame reopened), ("RetiredBarActionCannotOpenPopup",not(open staleAction) && Outputs.frame staleAction==Outputs.frame removed), ("RetiredPopupActionCannotRefresh",Outputs.frame stalePopup==Outputs.frame reopened), ("AllOutputsGoneHasNoPopupOwner",not(open empty) && owner empty==Nothing), ("ReturnedOutputHasFreshDeclaredScope",owner returned==Just "3" && not(open returnedDuplicate)), ("OutputRetirementCannotIssueWindowMutation",List.all (\m -> List.isEmpty (desktop m).windows.shell.issued) [opened,removed,unrelated,replaced,duplicate,reopened,oldDismiss,staleAction,stalePopup,empty,returned])]
 in E.object [("checks",E.object (List.map (Tuple.mapSecond E.bool) checks)),("removedFrame",Outputs.frame removed),("replacementFrame",Outputs.frame replaced),("returnedFrame",Outputs.frame returned)]
main : Program () () Never
main=Platform.worker {init=\_->((),outgoing result),update=\_ state->(state,Cmd.none),subscriptions=\_->Sub.none}
