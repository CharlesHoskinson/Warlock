module Surface exposing (Control, controls, mode, packet, resolve)

import Menu
import MenuBridge
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
    { id : String, domId : String, label : String, ariaLabel : String, detail : String, enabled : Bool, message : Maybe Desktop.Msg }

mode : Desktop.Model -> String
mode model =
    if model.open then "applications"
    else if (MenuBridge.menuSnapshot model.windows.menus).menu/=Nothing then "menu"
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
                in {id="entry:" ++ Catalog.id entry.identity,domId=Desktop.key model ("entry:" ++ Catalog.id entry.identity),label="Open " ++ entry.name,ariaLabel="Open " ++ entry.name,detail="",enabled=choice/=Nothing,message=choice}
            acknowledge = Launch.uncertain model.launch |> Maybe.map (\token -> {id="control:acknowledge",domId=Desktop.key model "control:acknowledge",label="I checked; allow another launch",ariaLabel="I checked; allow another launch",detail="",enabled=True,message=Just (Desktop.Acknowledge token)}) |> Maybe.map List.singleton |> Maybe.withDefault []
        in [ {id="control:close",domId=Desktop.key model "control:close",label="Windows",ariaLabel="Close applications and return to windows",detail="",enabled=True,message=scoped Desktop.CloseApplications}
           , {id="control:refresh",domId=Desktop.key model "control:refresh",label="Refresh",ariaLabel="Refresh applications",detail="",enabled=True,message=scoped Desktop.OpenApplications}
           ] ++ acknowledge ++ List.map entryControl entries
    else if (MenuBridge.menuSnapshot model.windows.menus).menu/=Nothing then
        case (MenuBridge.menuSnapshot model.windows.menus).menu of
            Nothing -> []
            Just menu ->
                let prefix="menu:" ++ String.fromInt (Menu.menuNumber menu.id) ++ ":"
                    ready=case menu.status of
                        Menu.Pending _ -> False
                        Menu.Unknown _ -> False
                        _ -> True
                    row index item =
                        {id=prefix ++ String.fromInt index,domId=prefix ++ String.fromInt index,label=item.label,ariaLabel=item.label,detail=if menu.selected==Just index then "Selected" else "",enabled=ready && item.enabled,message=if ready && item.enabled then Just (Desktop.Window (TaskbarShell.MenuEvent (Menu.Activate menu.id menu.binding index))) else Nothing}
                in {id="control:menu-close",domId=prefix ++ "close",label="Close",ariaLabel="Close window actions",detail="",enabled=True,message=Just (Desktop.Window (TaskbarShell.MenuEvent (Menu.Dismiss menu.id)))} :: List.indexedMap row menu.items
    else
        case model.windows.picker of
            Just picker ->
                let families = TaskbarShell.groups model.windows |> List.filter (\group -> group.key==picker.key) |> List.concatMap .families
                    familyControl family =
                        let ready = Shell.available model.windows.shell && family.available && Shell.capture model.windows.shell==Just picker.scope
                        in {id="family:" ++ UInt64.string family.root,domId="picker:" ++ Shell.stampKey picker.scope ++ ":" ++ UInt64.string picker.generation ++ ":" ++ UInt64.string family.root,label=(if family.minimized then "Restore " else "Activate ") ++ family.label,ariaLabel=(if family.minimized then "Restore " else "Activate ") ++ family.label,detail=if family.minimized then "Minimized" else "Open",enabled=ready,message=if ready then Just (Desktop.Window (TaskbarShell.Choose picker.scope picker.generation family.root)) else Nothing}
                in {id="control:close",domId="picker-close:" ++ Shell.stampKey picker.scope ++ ":" ++ UInt64.string picker.generation,label="Close",ariaLabel="Close window picker",detail="",enabled=True,message=Just (Desktop.Window (TaskbarShell.Close picker.scope picker.generation))} :: List.map familyControl families
            Nothing -> []

barControls : Desktop.Model -> List Control
barControls model =
    let
        application = {id="bar:applications",domId=Desktop.key model "control:opener",label="Applications",ariaLabel="Open applications",detail="",enabled=model.windows.shell.phase/=Shell.Detached,message=Desktop.capture model |> Maybe.map Desktop.OpenApplications}
        groupControl group =
            let scoped = Shell.capture model.windows.shell
                ready = Shell.available model.windows.shell && Taskbar.primary False group.families/=Taskbar.Unavailable
                operation = case Taskbar.primary False group.families of
                    Taskbar.Apply Effects.Minimize _ -> "Minimize "
                    Taskbar.Apply Effects.Restore _ -> "Restore "
                    Taskbar.Apply Effects.Activate _ -> "Activate "
                    Taskbar.Picker -> "Choose a window from "
                    _ -> "Unavailable "
                label = group.families |> List.head |> Maybe.map .label |> Maybe.withDefault "Windows"
            in {id="bar:group:" ++ group.key,domId=scoped |> Maybe.map (\stamp -> "group:" ++ Shell.stampKey stamp ++ ":" ++ group.key) |> Maybe.withDefault "detached-group",label=label,ariaLabel=operation ++ label,detail=String.fromInt (List.length group.families),enabled=ready,message=if ready then scoped |> Maybe.map (\stamp -> Desktop.Window (TaskbarShell.Primary stamp group.key)) else Nothing}
        reconnect = {id="bar:reconnect",domId="reconnect",label="Reconnect",ariaLabel="Reconnect to the window system",detail="",enabled=not model.windows.shell.reconnecting,message=Just (Desktop.Window (TaskbarShell.Native Shell.Reconnect))}
        retry = {id="bar:refresh-windows",domId=Desktop.key model "refresh-windows",label="Refresh windows",ariaLabel="Refresh windows",detail="",enabled=model.choice==Nothing,message=Just Desktop.RetryWindows}
    in (if model.windows.shell.phase==Shell.Detached then reconnect else application) :: List.map groupControl (TaskbarShell.groups model.windows) ++ (if not (String.isEmpty model.choiceNotice) && model.windows.shell.phase/=Shell.Detached then [retry] else [])

notice : Desktop.Model -> String
notice model =
    if mode model=="menu" then
        case (MenuBridge.menuSnapshot model.windows.menus).menu |> Maybe.map .status of
            Just (Menu.Refused reason) -> reason
            Just (Menu.Unknown _) -> "The operation could not be confirmed."
            Just (Menu.Pending _) -> "Working…"
            _ -> "Window actions"
    else if model.choice/=Nothing then "Updating your window choice…" else if not (String.isEmpty model.choiceNotice) then model.choiceNotice else
    case Launch.status model.launch of
        "Pending" -> "Opening application…"
        "Unknown" -> "The launch could not be confirmed. Check your windows before opening it again."
        "Submitted" -> "Launch submitted."
        "Refused" -> "The application changed or could not be launched. Refresh and choose again."
        _ -> if model.open then (if model.expected/=Nothing then "Loading applications…" else if model.applications==Nothing then "Application list unavailable. Refresh to try again." else "Choose an application.") else Shell.status model.windows.shell

packet : Counter -> Counter -> Desktop.Model -> E.Value
packet publication lease model =
    let
        encode control = E.object [("id",E.string control.id),("domId",E.string control.domId),("label",E.string control.label),("ariaLabel",E.string control.ariaLabel),("detail",E.string control.detail),("enabled",E.bool (control.enabled && control.message/=Nothing))]
    in E.object [("surfaceProtocol",E.int 2),("publication",E.string (UInt64.string publication)),("lease",E.string (UInt64.string lease)),("mode",E.string (mode model)),("status",E.string (notice model)),("bar",E.list encode (barControls model)),("popup",E.list encode (controls model))]

resolveAction : Counter -> Counter -> D.Value -> Desktop.Model -> Maybe Desktop.Msg
resolveAction publication lease raw model =
    let
        strict child = D.keyValuePairs D.value |> D.andThen (\pairs -> if List.sort (List.map Tuple.first pairs)==["id","kind","lease","publication","surface","surfaceProtocol"] then child else D.fail "Surface action fields")
        decoder = strict (D.map6 (\version kind shown scoped identity role -> {version=version,kind=kind,shown=shown,scoped=scoped,identity=identity,role=role}) (D.field "surfaceProtocol" D.int) (D.field "kind" D.string) (D.field "publication" UInt64.decoder) (D.field "lease" UInt64.decoder) (D.field "id" D.string) (D.field "surface" D.string))
    in case D.decodeValue decoder raw of
        Ok event ->
            if event.version/=2 || event.kind/="surface-action" || event.shown/=publication || event.scoped/=lease then Nothing else
                (if event.role=="bar" then barControls model else if event.role=="popup" then controls model else []) |> List.filter (\control -> control.id==event.identity && control.enabled) |> List.head |> Maybe.andThen .message
        Err _ -> Nothing

resolve : Counter -> Counter -> D.Value -> Desktop.Model -> Maybe Desktop.Msg
resolve publication lease raw model =
    let strict fields child = D.keyValuePairs D.value |> D.andThen (\pairs -> if List.sort (List.map Tuple.first pairs)==List.sort fields then child else D.fail "Surface event fields")
        scopes child = D.map4 (\version shown scoped role -> (version==2 && shown==publication && scoped==lease,role)) (D.field "surfaceProtocol" D.int) (D.field "publication" UInt64.decoder) (D.field "lease" UInt64.decoder) (D.field "surface" D.string) |> D.andThen (\(valid,role) -> if valid then child role else D.fail "Stale surface event")
        context = strict ["surfaceProtocol","kind","surface","publication","lease","id","trigger","x","y"] (scopes (\role -> D.map4 (\identity trigger x y -> (role,identity,trigger)) (D.field "id" D.string) (D.field "trigger" D.string) (D.field "x" D.int) (D.field "y" D.int)))
        navigation = strict ["surfaceProtocol","kind","surface","publication","lease","key"] (scopes (\role -> if role=="popup" && mode model=="menu" then D.field "key" D.string else D.fail "No menu"))
        menuMessage key =
            (MenuBridge.menuSnapshot model.windows.menus).menu |> Maybe.andThen (\menu ->
                let send = Just << Desktop.Window << TaskbarShell.MenuEvent
                in case key of
                    "Escape" -> send (Menu.Dismiss menu.id)
                    "ArrowUp" -> send (Menu.Navigate menu.id Menu.Up)
                    "ArrowDown" -> send (Menu.Navigate menu.id Menu.Down)
                    "Home" -> send (Menu.Navigate menu.id Menu.Home)
                    "End" -> send (Menu.Navigate menu.id Menu.End)
                    "Enter" -> menu.selected |> Maybe.map (\index -> Desktop.Window (TaskbarShell.MenuEvent (Menu.Activate menu.id menu.binding index)))
                    _ -> Nothing)
    in case D.decodeValue (D.field "kind" D.string) raw of
        Ok "surface-action" -> resolveAction publication lease raw model
        Ok "surface-menu-navigation" -> D.decodeValue navigation raw |> Result.toMaybe |> Maybe.andThen menuMessage
        Ok "surface-context" ->
            D.decodeValue context raw |> Result.toMaybe |> Maybe.andThen (\(role,identity,trigger) ->
                if not (List.member trigger ["pointer","keyboard"]) || model.choice/=Nothing then Nothing else
                Shell.capture model.windows.shell |> Maybe.andThen (\stamp ->
                    if role=="bar" then
                        TaskbarShell.groups model.windows |> List.filter (\group -> "bar:group:" ++ group.key==identity) |> List.head |> Maybe.andThen (\group ->
                            case group.families of
                                [family] -> if family.available then Just (Desktop.OpenWindowMenu stamp family.root) else Nothing
                                _ -> if Taskbar.primary False group.families==Taskbar.Picker then Just (Desktop.Window (TaskbarShell.Primary stamp group.key)) else Nothing)
                    else if role=="popup" && mode model=="picker" then
                        model.windows.picker |> Maybe.andThen (\picker ->
                            if picker.scope/=stamp then Nothing else
                            TaskbarShell.groups model.windows |> List.filter (\group -> group.key==picker.key) |> List.concatMap .families |> List.filter (\family -> "family:" ++ UInt64.string family.root==identity && family.available) |> List.head |> Maybe.map (\family -> Desktop.OpenWindowMenu stamp family.root))
                    else Nothing))
        _ -> Nothing
