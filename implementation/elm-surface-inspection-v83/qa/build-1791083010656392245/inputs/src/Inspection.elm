module Inspection exposing (packet)
import Desktop
import Effects
import Json.Decode as D
import Json.Encode as E
import Shell
import SurfaceController as Controller
import TaskbarShell
import UInt64

packet : Controller.Model -> E.Value
packet controller =
    let
        desktop = Controller.desktop controller
        model = desktop.windows
        shell = model.shell
        frame = Controller.frame controller
        stamp = Shell.capture shell |> Maybe.map Shell.stampKey |> Maybe.withDefault "detached"
        group item = E.object [("key",E.string item.key),("domId",E.string ("group:" ++ stamp ++ ":" ++ item.key)),("title",E.string (item.families |> List.head |> Maybe.map .label |> Maybe.withDefault "Windows")),("active",E.bool (List.any .active item.families)),("expanded",E.bool (model.picker |> Maybe.map (\picker -> picker.key==item.key) |> Maybe.withDefault False))]
        picker current =
            let family item = E.object [("incarnation",E.string (UInt64.string item.root)),("title",E.string item.label),("state",E.string (if item.minimized then "Minimized" else "Open")),("domId",E.string ("picker:" ++ Shell.stampKey current.scope ++ ":" ++ UInt64.string current.generation ++ ":" ++ UInt64.string item.root))]
            in E.object [("generation",E.string (UInt64.string current.generation)),("closeId",E.string ("picker-close:" ++ Shell.stampKey current.scope ++ ":" ++ UInt64.string current.generation)),("selections",E.list family (TaskbarShell.groups model |> List.filter (\item -> item.key==current.key) |> List.concatMap .families))]
        field name = D.decodeValue (D.field name D.value) frame |> Result.withDefault E.null
        phase = case shell.phase of
            Shell.Ready -> "Coherent"
            Shell.Detached -> "Detached"
            Shell.Reconciling -> "Awaiting"
            Shell.Exhausted -> "Exhausted"
    in E.object [("surfaceProtocol",E.int 2),("kind",E.string "surface-inspection"),("publication",field "publication"),("lease",field "lease"),("body",E.object [("phase",E.string phase),("transaction",E.string (shell.effects.transaction |> Maybe.map (.status >> Effects.statusName) |> Maybe.withDefault "Idle")),("groups",E.list group (TaskbarShell.groups model)),("picker",model.picker |> Maybe.map picker |> Maybe.withDefault E.null),("openerId",E.string (Desktop.key desktop "control:opener")),("reconnectId",E.string "reconnect")])]
