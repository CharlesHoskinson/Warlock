port module Main exposing (main)
import Browser
import Catalog
import Desktop
import Launch
import Process
import Browser.Dom
import Task
import Effects
import Html exposing (Html,button,div,h1,p,span,text)
import Html.Attributes exposing (attribute,class,disabled,id,title)
import Html.Events exposing (on,onClick)
import Html.Keyed as Keyed
import Json.Decode as D
import Json.Encode as E
import Shell
import Taskbar
import TaskbarShell exposing (Model,Msg(..))
import UInt64
port nativeEvents : (D.Value -> msg) -> Sub msg
port nativeRequests : E.Value -> Cmd msg
update message model =
    let
        (next,effects) = TaskbarShell.update message model
        command effect = case effect of
            Shell.Send value -> nativeRequests value
            Shell.RestartBackend -> nativeRequests (E.object [("protocolVersion",E.int 3),("kind",E.string "host-reconnect")])
        focus target = Browser.Dom.focus target |> Task.attempt (\_ -> Native Shell.Ignore)
        localFocus = case (model.picker,next.picker) of
            (_,Just picker) ->
                if (model.picker |> Maybe.map .generation) == Just picker.generation then Cmd.none else
                    TaskbarShell.groups next |> List.filter (\group -> group.key == picker.key) |> List.concatMap .families |> List.filter .available |> List.head
                        |> Maybe.map (\family -> focus (pickerId picker family.root)) |> Maybe.withDefault Cmd.none
            (Just picker,Nothing) ->
                case message of
                    Close scope generation ->
                        if picker.scope == scope && picker.generation == generation && Shell.capture next.shell == Just scope then focus (groupId scope picker.key) else Cmd.none
                    _ -> Cmd.none
            _ -> Cmd.none
    in (next,Cmd.batch (localFocus :: List.map command effects))
groupId scope key = "group:" ++ Shell.stampKey scope ++ ":" ++ key
pickerId picker root = "picker:" ++ Shell.stampKey picker.scope ++ ":" ++ UInt64.string picker.generation ++ ":" ++ UInt64.string root
view : Model -> Html Msg
view model =
    let
        shell = model.shell
        available = Shell.available shell
        scoped build = Shell.capture shell |> Maybe.map build |> Maybe.withDefault (Native Shell.Ignore)
        groupView group =
            let
                name = group.families |> List.head |> Maybe.map .label |> Maybe.withDefault "Windows"
                count = List.length group.families
                active = List.any .active group.families
                operation = case Taskbar.primary False group.families of
                    Taskbar.Apply Effects.Minimize _ -> "Minimize "
                    Taskbar.Apply Effects.Restore _ -> "Restore "
                    Taskbar.Apply Effects.Activate _ -> "Activate "
                    Taskbar.Picker -> "Choose a window from "
                    _ -> "Unavailable "
                blocked = Taskbar.primary False group.families == Taskbar.Unavailable
                expanded = model.picker |> Maybe.map (\picker -> picker.key == group.key) |> Maybe.withDefault False
            in (group.key,button [id (Shell.capture shell |> Maybe.map (\scope -> groupId scope group.key) |> Maybe.withDefault "detached-group"),attribute "aria-controls" "window-picker",class (if active then "taskbar-group active" else "taskbar-group"),disabled (not available || blocked),onClick (scoped (\scope -> Primary scope group.key)),attribute "data-group" group.key,title name,attribute "data-title" name,attribute "aria-label" (operation ++ name),attribute "aria-expanded" (if expanded then "true" else "false")]
                [span [class "family-title"] [text name],span [class "state"] [text (if count > 1 then String.fromInt count ++ " windows" else if active then "Active" else "")]])
        pickerView = case model.picker of
            Nothing -> text ""
            Just picker ->
                let
                    families = TaskbarShell.groups model |> List.filter (\group -> group.key == picker.key) |> List.concatMap .families
                    close = Close picker.scope picker.generation
                    escape = D.map2 Tuple.pair (D.field "key" D.string) (D.field "isComposing" D.bool) |> D.andThen (\(key,composing) -> if key == "Escape" && not composing then D.succeed close else D.fail "Unrelated or composing key")
                    familyView family = (UInt64.string family.root,button [id (pickerId picker family.root),disabled (not available || not family.available),onClick (Choose picker.scope picker.generation family.root),attribute "data-incarnation" (UInt64.string family.root),title family.label,attribute "data-title" family.label,attribute "aria-label" ((if family.minimized then "Restore " else "Activate ") ++ family.label)]
                        [span [class "family-title"] [text family.label],span [class "state"] [text (if family.minimized then "Minimized" else if family.active then "Active" else "Open")]])
                in div [id "window-picker",attribute "data-generation" (UInt64.string picker.generation),attribute "role" "region",attribute "aria-label" "Choose a window",on "keydown" escape]
                    [p [] [text "Choose a window"],Keyed.node "div" [class "picker-windows"] (List.map familyView families),button [id "close-picker",onClick close] [text "Close"]]
        pending = Effects.pending shell.effects
    in div [id "shell-root",class "shell",attribute "data-phase" (case shell.phase of
            Shell.Ready -> "Coherent"
            Shell.Detached -> "Detached"
            Shell.Reconciling -> "Awaiting"
            Shell.Exhausted -> "Exhausted"),attribute "data-transaction" (shell.effects.transaction |> Maybe.map (.status >> Effects.statusName) |> Maybe.withDefault "Idle"),attribute "aria-busy" (if pending || shell.phase == Shell.Reconciling then "true" else "false")]
        [h1 [] [text "Windows"],p [id "connection-status",attribute "role" "status",attribute "aria-live" "polite"] [text (Shell.status shell)]
        ,if shell.phase == Shell.Detached then button [id "reconnect",onClick (Native Shell.Reconnect),disabled shell.reconnecting] [text "Reconnect"] else button [onClick (Native Shell.Refresh),disabled pending] [text "Refresh"]
        ,Keyed.node "div" [class "taskbar",attribute "role" "group",attribute "aria-label" "Application windows"] (List.map groupView (TaskbarShell.groups model))
        ,pickerView]
desktopUpdate : Desktop.Msg -> Desktop.Model -> (Desktop.Model, Cmd Desktop.Msg)
desktopUpdate message model =
    let
        (next,effects) = Desktop.update message model
        command effect = case effect of
            Desktop.Send wire -> nativeRequests wire
            Desktop.Focus target -> Browser.Dom.focus target |> Task.attempt (\_ -> Desktop.Window (Native Shell.Ignore))
            Desktop.Arm token -> Process.sleep 10000 |> Task.perform (\_ -> Desktop.Deadline token)
            Desktop.WindowEffect (Shell.Send wire) -> nativeRequests wire
            Desktop.WindowEffect Shell.RestartBackend -> nativeRequests (E.object [("protocolVersion",E.int 3),("kind",E.string "host-reconnect")])
        focus target = Browser.Dom.focus target |> Task.attempt (\_ -> Desktop.Window (Native Shell.Ignore))
        localFocus = case (model.windows.picker,next.windows.picker) of
            (_,Just picker) ->
                if (model.windows.picker |> Maybe.map .generation) == Just picker.generation then Cmd.none else
                    TaskbarShell.groups next.windows |> List.filter (\group -> group.key == picker.key) |> List.concatMap .families |> List.filter .available |> List.head
                        |> Maybe.map (\family -> focus (pickerId picker family.root)) |> Maybe.withDefault Cmd.none
            (Just picker,Nothing) ->
                case message of
                    Desktop.Window (Close scope generation) ->
                        if picker.scope == scope && picker.generation == generation && Shell.capture next.windows.shell == Just scope then focus (groupId scope picker.key) else Cmd.none
                    _ -> Cmd.none
            _ -> Cmd.none
    in (next,Cmd.batch (localFocus :: List.map command effects))

desktopView : Desktop.Model -> Html Desktop.Msg
desktopView model =
    let
        scoped build = Desktop.capture model |> Maybe.map build |> Maybe.withDefault (Desktop.Window (Native Shell.Ignore))
        escape = D.map2 Tuple.pair (D.field "key" D.string) (D.field "isComposing" D.bool) |> D.andThen (\(key,composing) -> if key == "Escape" && not composing then D.succeed (scoped Desktop.CloseApplications) else D.fail "Unrelated or composing key")
    in if model.open then
        let
            entryView entry =
                let selection = Launch.select (Catalog.id entry.identity) model.launch
                    blocked = List.member (Launch.status model.launch) ["Pending","Unknown"] || selection == Nothing
                in button [id (Desktop.key model ("entry:" ++ Catalog.id entry.identity)),disabled blocked,attribute "data-application" (Catalog.id entry.identity),attribute "aria-label" ("Open " ++ entry.name),title entry.name,onClick (selection |> Maybe.map Desktop.Start |> Maybe.withDefault (Desktop.Window (Native Shell.Ignore)))] [text entry.name]
            status = case Launch.status model.launch of
                "Pending" -> "Opening application…"
                "Unknown" -> "The launch could not be confirmed. The application may already have opened. Check your windows before opening it again."
                "Submitted" -> "Launch submitted."
                "Refused" -> "The application changed or could not be launched. Refresh and choose again."
                _ -> if model.expected /= Nothing then "Loading applications…" else if model.applications == Nothing then "Application list unavailable. Refresh to try again." else "Choose an application."
        in div [id "applications",class "shell",attribute "data-launch-status" (Launch.status model.launch),on "keydown" escape]
            [h1 [] [text "Applications"],p [attribute "role" "status",attribute "aria-live" "polite"] [text status]
            ,div [class "launcher-controls"] [button [id (Desktop.key model "control:close"),onClick (scoped Desktop.CloseApplications)] [text "Windows"],button [id (Desktop.key model "control:refresh"),onClick (scoped Desktop.OpenApplications)] [text "Refresh"]]
            ,Launch.uncertain model.launch |> Maybe.map (\token -> button [onClick (Desktop.Acknowledge token)] [text "I checked; allow another launch"]) |> Maybe.withDefault (text "")
            ,div [class "application-list"] (model.applications |> Maybe.map (Catalog.entries >> List.map entryView) |> Maybe.withDefault [])]
    else
        div [class "desktop"] [Html.map Desktop.Window (view model.windows),button [id (Desktop.key model "control:opener"),attribute "data-launcher-opener" "true",class "open-applications",onClick (scoped Desktop.OpenApplications)] [text "Applications"]]

main : Program () Desktop.Model Desktop.Msg
main = Browser.element {init = \_ -> (Desktop.initial,Cmd.none),update = desktopUpdate,view = desktopView,subscriptions = \_ -> nativeEvents Desktop.Incoming}
