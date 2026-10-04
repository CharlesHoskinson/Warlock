module Surface exposing (Control, controls, mode, packet, resolve)

import Catalog
import Desktop
import Effects
import Json.Decode as D
import Json.Encode as E
import Launch
import Shell
import Taskbar
import TaskbarShell
import UInt64 exposing (Counter)

type alias Control =
    { id : String, domId : String, label : String, detail : String, enabled : Bool, message : Maybe Desktop.Msg }

mode : Desktop.Model -> String
mode model =
    if model.open then "applications"
    else if model.windows.picker /= Nothing then "picker"
    else "closed"

controls : Desktop.Model -> List Control
controls model =
    if model.open then
        let
            scoped build = Desktop.capture model |> Maybe.map build
            entries = model.applications |> Maybe.map Catalog.entries |> Maybe.withDefault []
            ready = not (List.member (Launch.status model.launch) ["Pending","Unknown"])
            entryControl entry =
                let choice = if ready then Launch.select (Catalog.id entry.identity) model.launch |> Maybe.map Desktop.Start else Nothing
                in {id="entry:" ++ Catalog.id entry.identity,domId=Desktop.key model ("entry:" ++ Catalog.id entry.identity),label="Open " ++ entry.name,detail="",enabled=choice/=Nothing,message=choice}
            acknowledge = Launch.uncertain model.launch |> Maybe.map (\token -> {id="control:acknowledge",domId=Desktop.key model "control:acknowledge",label="I checked; allow another launch",detail="",enabled=True,message=Just (Desktop.Acknowledge token)}) |> Maybe.map List.singleton |> Maybe.withDefault []
        in [ {id="control:close",domId=Desktop.key model "control:close",label="Windows",detail="",enabled=True,message=scoped Desktop.CloseApplications}
           , {id="control:refresh",domId=Desktop.key model "control:refresh",label="Refresh",detail="",enabled=True,message=scoped Desktop.OpenApplications}
           ] ++ acknowledge ++ List.map entryControl entries
    else
        case model.windows.picker of
            Just picker ->
                let families = TaskbarShell.groups model.windows |> List.filter (\group -> group.key==picker.key) |> List.concatMap .families
                    familyControl family =
                        let ready = Shell.available model.windows.shell && family.available && Shell.capture model.windows.shell==Just picker.scope
                        in {id="family:" ++ UInt64.string family.root,domId="picker:" ++ Shell.stampKey picker.scope ++ ":" ++ UInt64.string picker.generation ++ ":" ++ UInt64.string family.root,label=(if family.minimized then "Restore " else "Activate ") ++ family.label,detail=if family.minimized then "Minimized" else "Open",enabled=ready,message=if ready then Just (Desktop.Window (TaskbarShell.Choose picker.scope picker.generation family.root)) else Nothing}
                in {id="control:close",domId="picker-close:" ++ Shell.stampKey picker.scope ++ ":" ++ UInt64.string picker.generation,label="Close",detail="",enabled=True,message=Just (Desktop.Window (TaskbarShell.Close picker.scope picker.generation))} :: List.map familyControl families
            Nothing -> []

barControls : Desktop.Model -> List Control
barControls model =
    let
        application = {id="bar:applications",domId=Desktop.key model "control:opener",label="Applications",detail="",enabled=model.windows.shell.phase/=Shell.Detached,message=Desktop.capture model |> Maybe.map Desktop.OpenApplications}
        groupControl group =
            let scoped = Shell.capture model.windows.shell
                ready = Shell.available model.windows.shell && Taskbar.primary False group.families/=Taskbar.Unavailable
                label = group.families |> List.head |> Maybe.map .label |> Maybe.withDefault "Windows"
            in {id="bar:group:" ++ group.key,domId=scoped |> Maybe.map (\stamp -> "group:" ++ Shell.stampKey stamp ++ ":" ++ group.key) |> Maybe.withDefault "detached-group",label=label,detail=String.fromInt (List.length group.families),enabled=ready,message=if ready then scoped |> Maybe.map (\stamp -> Desktop.Window (TaskbarShell.Primary stamp group.key)) else Nothing}
    in application :: List.map groupControl (TaskbarShell.groups model.windows)

packet : Counter -> Counter -> Desktop.Model -> E.Value
packet publication lease model =
    let
        encode control = E.object [("id",E.string control.id),("domId",E.string control.domId),("label",E.string control.label),("detail",E.string control.detail),("enabled",E.bool (control.enabled && control.message/=Nothing))]
    in E.object [("surfaceProtocol",E.int 1),("publication",E.string (UInt64.string publication)),("lease",E.string (UInt64.string lease)),("mode",E.string (mode model)),("status",E.string (if model.open then Launch.status model.launch else Shell.status model.windows.shell)),("bar",E.list encode (barControls model)),("popup",E.list encode (controls model))]

resolve : Counter -> Counter -> D.Value -> Desktop.Model -> Maybe Desktop.Msg
resolve publication lease raw model =
    let
        strict child = D.keyValuePairs D.value |> D.andThen (\pairs -> if List.sort (List.map Tuple.first pairs)==["id","kind","lease","publication","surface","surfaceProtocol"] then child else D.fail "Surface action fields")
        decoder = strict (D.map6 (\version kind shown scoped identity role -> {version=version,kind=kind,shown=shown,scoped=scoped,identity=identity,role=role}) (D.field "surfaceProtocol" D.int) (D.field "kind" D.string) (D.field "publication" UInt64.decoder) (D.field "lease" UInt64.decoder) (D.field "id" D.string) (D.field "surface" D.string))
    in case D.decodeValue decoder raw of
        Ok event ->
            if event.version/=1 || event.kind/="surface-action" || event.shown/=publication || event.scoped/=lease then Nothing else
                (if event.role=="bar" then barControls model else if event.role=="popup" then controls model else []) |> List.filter (\control -> control.id==event.identity && control.enabled) |> List.head |> Maybe.andThen .message
        Err _ -> Nothing
