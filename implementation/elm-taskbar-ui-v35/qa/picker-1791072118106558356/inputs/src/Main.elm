port module Main exposing (main)
import Browser
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
    in (next,Cmd.batch (List.map command effects))
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
            in (group.key,button [class (if active then "taskbar-group active" else "taskbar-group"),disabled (not available || blocked),onClick (scoped (\scope -> Primary scope group.key)),attribute "data-group" group.key,attribute "aria-label" (operation ++ name),attribute "aria-expanded" (if expanded then "true" else "false")]
                [span [] [text name],span [class "state"] [text (if count > 1 then String.fromInt count ++ " windows" else if active then "Active" else "")]])
        pickerView = case model.picker of
            Nothing -> text ""
            Just picker ->
                let
                    families = TaskbarShell.groups model |> List.filter (\group -> group.key == picker.key) |> List.concatMap .families
                    close = Close picker.scope picker.generation
                    escape = D.field "key" D.string |> D.andThen (\key -> if key == "Escape" then D.succeed close else D.fail "Unrelated key")
                    familyView family = (UInt64.string family.root,button [disabled (not available || not family.available),onClick (Choose picker.scope picker.generation family.root),attribute "data-incarnation" (UInt64.string family.root),attribute "aria-label" ((if family.minimized then "Restore " else "Activate ") ++ family.label)]
                        [text family.label,span [class "state"] [text (if family.minimized then "Minimized" else if family.active then "Active" else "Open")]])
                in div [id "window-picker",attribute "role" "region",attribute "aria-label" "Choose a window",on "keydown" escape]
                    [p [] [text "Choose a window"],Keyed.node "div" [class "picker-windows"] (List.map familyView families),button [onClick close] [text "Close"]]
        pending = Effects.pending shell.effects
    in div [id "shell-root",class "shell",attribute "aria-busy" (if pending || shell.phase == Shell.Reconciling then "true" else "false")]
        [h1 [] [text "Windows"],p [id "connection-status",attribute "role" "status",attribute "aria-live" "polite"] [text (Shell.status shell)]
        ,if shell.phase == Shell.Detached then button [id "reconnect",onClick (Native Shell.Reconnect),disabled shell.reconnecting] [text "Reconnect"] else button [onClick (Native Shell.Refresh),disabled pending] [text "Refresh"]
        ,Keyed.node "div" [class "taskbar",attribute "role" "group",attribute "aria-label" "Application windows"] (List.map groupView (TaskbarShell.groups model))
        ,pickerView]
main : Program () Model Msg
main = Browser.element {init = \_ -> (TaskbarShell.initial,Cmd.none),update = update,view = view,subscriptions = \_ -> nativeEvents (Shell.Incoming >> Native)}
