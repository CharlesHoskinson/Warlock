port module Main exposing (main)
import Browser
import Browser.Dom
import Task
import Effects
import Html exposing (Html,button,div,h1,p,span,text)
import Html.Attributes exposing (attribute,class,disabled,id)
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
            in (group.key,button [id (Shell.capture shell |> Maybe.map (\scope -> groupId scope group.key) |> Maybe.withDefault "detached-group"),attribute "aria-controls" "window-picker",class (if active then "taskbar-group active" else "taskbar-group"),disabled (not available || blocked),onClick (scoped (\scope -> Primary scope group.key)),attribute "data-group" group.key,attribute "data-title" name,attribute "aria-label" (operation ++ name),attribute "aria-expanded" (if expanded then "true" else "false")]
                [span [] [text name],span [class "state"] [text (if count > 1 then String.fromInt count ++ " windows" else if active then "Active" else "")]])
        pickerView = case model.picker of
            Nothing -> text ""
            Just picker ->
                let
                    families = TaskbarShell.groups model |> List.filter (\group -> group.key == picker.key) |> List.concatMap .families
                    close = Close picker.scope picker.generation
                    escape = D.map2 Tuple.pair (D.field "key" D.string) (D.field "isComposing" D.bool) |> D.andThen (\(key,composing) -> if key == "Escape" && not composing then D.succeed close else D.fail "Unrelated or composing key")
                    familyView family = (UInt64.string family.root,button [id (pickerId picker family.root),disabled (not available || not family.available),onClick (Choose picker.scope picker.generation family.root),attribute "data-incarnation" (UInt64.string family.root),attribute "data-title" family.label,attribute "aria-label" ((if family.minimized then "Restore " else "Activate ") ++ family.label)]
                        [text family.label,span [class "state"] [text (if family.minimized then "Minimized" else if family.active then "Active" else "Open")]])
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
main : Program () Model Msg
main = Browser.element {init = \_ -> (TaskbarShell.initial,Cmd.none),update = update,view = view,subscriptions = \_ -> nativeEvents (Shell.Incoming >> Native)}
