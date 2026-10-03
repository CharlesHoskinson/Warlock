port module Main exposing (main)

import ActionProjection
import Binding
import Browser
import Browser.Dom as Dom
import Effects
import Html exposing (Html, button, div, h1, li, p, span, text)
import Html.Attributes exposing (attribute, class, disabled, id, tabindex)
import Html.Events exposing (custom, onClick, onFocus, onMouseEnter)
import Json.Decode as D
import Json.Encode as E
import Menu
import Shell
import Task
import UInt64 exposing (Counter)

port nativeEvents : (D.Value -> msg) -> Sub msg
port nativeRequests : E.Value -> Cmd msg

type alias Model =
    { shell : Shell.Model
    , menu : Menu.Model
    , target : Maybe Counter
    , pressed : Maybe { incarnation : Counter, binding : Menu.Binding, x : Float, y : Float }
    , wire : Maybe (Menu.IntentId, Counter)
    }

type Msg
    = Native D.Value
    | Refresh
    | Reconnect
    | Press Counter Int Int Float Float
    | Release Counter Int Int Float Float
    | OpenKeyboard Counter
    | CycleFocus Menu.MenuId Bool String
    | Navigate Menu.MenuId Menu.Navigation
    | Select Menu.MenuId Menu.Binding Int
    | Activate Menu.MenuId Menu.Binding Int
    | Dismiss Menu.MenuId
    | NoOp

initial : Model
initial = { shell = Shell.initial, menu = Menu.init, target = Nothing, pressed = Nothing, wire = Nothing }

rows model = model.shell.effects.observed |> Maybe.map (.scene >> ActionProjection.windows) |> Maybe.withDefault []

targetBinding : Counter -> Model -> Maybe Menu.Binding
targetBinding incarnation model =
    case (model.shell.binding, model.shell.effects.observed) of
        (Just native, Just observed) ->
            if List.any (\row -> row.incarnation == incarnation) (rows model) then
                let authority = E.encode 0 (Binding.encode native)
                in Just (Menu.binding { authority = authority, revision = UInt64.string observed.context.revision, output = Menu.outputId "native-output-set", outputGeneration = UInt64.string observed.context.output, target = Menu.Window (Menu.windowId (Binding.authorityIdentity native) (UInt64.string incarnation)) })
            else Nothing
        _ -> Nothing

menuCommand : Shell.Effect -> Cmd Msg
menuCommand effect =
    case effect of
        Shell.Send value -> nativeRequests value
        Shell.RestartBackend -> nativeRequests (E.object [("protocolVersion", E.int 3), ("kind", E.string "host-reconnect")])

focusSelected : Menu.Model -> Cmd Msg
focusSelected model =
    case (Menu.snapshot model).menu |> Maybe.andThen .selected of
        Just index -> Dom.focus ("context-action-" ++ String.fromInt index) |> Task.attempt (\_ -> NoOp)
        Nothing -> Dom.focus "context-menu" |> Task.attempt (\_ -> NoOp)

open : Counter -> Model -> (Model, Cmd Msg)
open incarnation model =
    case (targetBinding incarnation model, List.head (List.filter (\row -> row.incarnation == incarnation) (rows model))) of
        (Just binding, Just row) ->
            if not (Shell.available model.shell) then (model, Cmd.none) else
                let items = [{label="Restore",enabled=row.minimized,action=Menu.Restore},{label="Minimize",enabled=not row.minimized,action=Menu.Minimize}]
                    (menu, _) = Menu.update (Menu.Open binding items) model.menu
                in ({model | menu=menu, target=Just incarnation, pressed=Nothing}, focusSelected menu)
        _ -> (model, Cmd.none)

menuUpdate : Menu.Msg -> Model -> (Model, Cmd Msg)
menuUpdate message model =
    let (menu, effects) = Menu.update message model.menu
        next = {model | menu=menu}
    in case effects of
        [Menu.Dispatch intent binding action] ->
            case (model.target, action) of
                (Just incarnation, Menu.Minimize) -> dispatch intent binding Effects.Minimize incarnation next
                (Just incarnation, Menu.Restore) -> dispatch intent binding Effects.Restore incarnation next
                _ ->
                    let (refused, _) = Menu.update (Menu.Receive intent (Menu.Refusal "Operation unavailable")) menu
                    in ({next | menu=refused}, Cmd.none)
        _ -> (next, Cmd.none)

dispatch intent binding operation incarnation model =
    if not (Shell.available model.shell) || targetBinding incarnation model /= Just binding then
        let (menu, _) = Menu.update (Menu.Receive intent (Menu.Refusal "Window information changed")) model.menu
        in ({model | menu=menu}, Cmd.none)
    else
        let (shell, effects) = Shell.update (Shell.Act operation incarnation) model.shell
        in case (effects, shell.effects.transaction) of
            ([], _) ->
                let (menu, _) = Menu.update (Menu.Receive intent (Menu.Refusal "Native operation unavailable")) model.menu
                in ({model | shell=shell, menu=menu}, Cmd.none)
            (_, Just transaction) -> ({model | shell=shell, wire=Just (intent,transaction.intent.request)}, Cmd.batch (List.map menuCommand effects))
            _ -> (model, Cmd.none)

update : Msg -> Model -> (Model, Cmd Msg)
update message model =
    case message of
        NoOp -> (model, Cmd.none)
        Press incarnation logical buttons x y ->
            ({model | pressed=if logical==2 && buttons==2 then targetBinding incarnation model |> Maybe.map (\binding -> {incarnation=incarnation,binding=binding,x=x,y=y}) else Nothing}, Cmd.none)
        Release incarnation logical buttons x y ->
            case model.pressed of
                Just pressed ->
                    if logical==2 && buttons==0 && pressed.incarnation==incarnation && targetBinding incarnation model==Just pressed.binding && abs (x-pressed.x)<=5 && abs (y-pressed.y)<=5 then open incarnation {model | pressed=Nothing}
                    else ({model | pressed=Nothing},Cmd.none)
                Nothing -> (model,Cmd.none)
        OpenKeyboard incarnation -> open incarnation model
        CycleFocus menu backwards focused ->
            case (Menu.snapshot model.menu).menu of
                Just current ->
                    if current.id /= menu then (model,Cmd.none) else
                        let ready = Shell.available model.shell && (case current.status of
                                Menu.Ready -> True
                                Menu.Refused _ -> True
                                Menu.Cancelled -> True
                                _ -> False)
                            enabled = if ready then List.indexedMap (\index entry -> if entry.enabled then Just ("context-action-" ++ String.fromInt index) else Nothing) current.items |> List.filterMap identity else []
                            order = enabled ++ ["context-dismiss"]
                            sequence = if backwards then List.reverse order else order
                            after = List.indexedMap Tuple.pair sequence |> List.filter (\(_,item) -> item==focused) |> List.head |> Maybe.map (\(index,_) -> List.drop (index+1) sequence |> List.head) |> Maybe.withDefault Nothing
                            target = after |> Maybe.withDefault (List.head sequence |> Maybe.withDefault "context-menu")
                        in (model,Dom.focus target |> Task.attempt (\_ -> NoOp))
                Nothing -> (model,Cmd.none)
        Navigate menu direction ->
            let (next, _) = menuUpdate (Menu.Navigate menu direction) model
            in (next,focusSelected next.menu)
        Select menu binding index -> menuUpdate (Menu.Select menu binding index) model
        Activate menu binding index -> menuUpdate (Menu.Activate menu binding index) model
        Dismiss menu ->
            case (Menu.snapshot model.menu).menu of
                Just current ->
                    if current.id /= menu then (model,Cmd.none) else
                        let (next, _) = menuUpdate (Menu.Dismiss menu) model
                            focus = model.target |> Maybe.andThen (\inc -> if targetBinding inc model==Just current.binding then Just inc else Nothing) |> Maybe.map (\inc -> Dom.focus ("window-" ++ UInt64.string inc) |> Task.attempt (\_ -> NoOp)) |> Maybe.withDefault Cmd.none
                        in ({next | pressed=Nothing},focus)
                Nothing -> (model,Cmd.none)
        Refresh -> shellUpdate Shell.Refresh model
        Reconnect -> shellUpdate Shell.Reconnect model
        Native value -> shellUpdate (Shell.Incoming value) model

shellUpdate message model =
    let (shell,effects) = Shell.update message model.shell
        next = {model | shell=shell}
        reconciled = case (model.wire, shell.effects.transaction) of
            (Just (intent, request), Just transaction) ->
                if request /= transaction.intent.request || transaction.status==Effects.Pending then next else
                    let outcome = case transaction.status of
                            Effects.Committed -> Menu.Committed
                            Effects.Refused -> Menu.Refusal "Native operation refused"
                            Effects.Cancelled -> Menu.Cancellation
                            _ -> Menu.Uncertain
                        (menu,_) = Menu.update (Menu.Receive intent outcome) next.menu
                    in {next | menu=menu, wire=if outcome==Menu.Uncertain then model.wire else Nothing}
            _ -> next
        checked = case (Menu.snapshot reconciled.menu).menu of
            Just menu ->
                if shell.phase==Shell.Detached || (shell.phase==Shell.Ready && (reconciled.target |> Maybe.andThen (\target -> targetBinding target reconciled)) /= Just menu.binding) then
                    let (invalid,_) = Menu.update (Menu.Invalidate menu.binding) reconciled.menu
                    in {reconciled | menu=invalid, pressed=Nothing}
                else reconciled
            Nothing -> reconciled
    in (checked, Cmd.batch (List.map menuCommand effects))

ignoreContext = custom "contextmenu" (D.succeed {message=NoOp,stopPropagation=True,preventDefault=True})
mouse decoder constructor = custom decoder (D.map4 (\logical buttons x y -> {message=constructor logical buttons x y,stopPropagation=True,preventDefault=logical==2}) (D.field "button" D.int) (D.field "buttons" D.int) (D.field "clientX" D.float) (D.field "clientY" D.float))
keyHandler decode = custom "keydown" (D.map2 decode (D.field "key" D.string) (D.field "shiftKey" D.bool))
menuKeyHandler decode = custom "keydown" (D.map3 decode (D.field "key" D.string) (D.field "shiftKey" D.bool) (D.at ["target","id"] D.string))

view : Model -> Html Msg
view model =
    let pending = Effects.pending model.shell.effects
        live = model.shell.phase==Shell.Ready
        phase = if live then "Coherent" else if model.shell.phase==Shell.Detached then "Detached" else "Awaiting"
        item row =
            li [attribute "data-incarnation" (UInt64.string row.incarnation), id ("window-" ++ UInt64.string row.incarnation), tabindex 0, ignoreContext,
                mouse "mousedown" (Press row.incarnation), mouse "mouseup" (Release row.incarnation),
                keyHandler (\key shifted -> let owned=key=="ContextMenu" || (key=="F10" && shifted) in {message=if owned then OpenKeyboard row.incarnation else NoOp,stopPropagation=owned,preventDefault=owned})]
                [span [class "window-title"] [text row.label], span [class "state"] [text (if row.minimized then "Minimized" else "Open")],span [class "context-hint"] [text "Right-click for actions"]]
        menuView = case (Menu.snapshot model.menu).menu of
            Nothing -> text ""
            Just menu ->
                let ready = Shell.available model.shell && (case menu.status of
                        Menu.Ready -> True
                        Menu.Refused _ -> True
                        Menu.Cancelled -> True
                        _ -> False)
                    action index entry = button [id ("context-action-" ++ String.fromInt index),attribute "role" "menuitem",disabled (not entry.enabled || not ready),attribute "data-index" (String.fromInt index),onFocus (Select menu.id menu.binding index),onMouseEnter (Select menu.id menu.binding index),onClick (Activate menu.id menu.binding index)] [text entry.label]
                    keyboard key shifted focused =
                        let command = case key of
                                "Tab" -> CycleFocus menu.id shifted focused
                                "ArrowDown" -> Navigate menu.id Menu.Down
                                "ArrowUp" -> Navigate menu.id Menu.Up
                                "Home" -> Navigate menu.id Menu.Home
                                "End" -> Navigate menu.id Menu.End
                                "Escape" -> Dismiss menu.id
                                "Enter" -> menu.selected |> Maybe.map (Activate menu.id menu.binding) |> Maybe.withDefault NoOp
                                " " -> menu.selected |> Maybe.map (Activate menu.id menu.binding) |> Maybe.withDefault NoOp
                                _ -> NoOp
                        in {message=command,stopPropagation=List.member key ["Tab","ArrowDown","ArrowUp","Home","End","Escape","Enter"," "],preventDefault=List.member key ["Tab","ArrowDown","ArrowUp","Home","End","Escape","Enter"," "]}
                    status = case menu.status of
                        Menu.Pending _ -> "Applying…"
                        Menu.Unknown _ -> "Result unknown; awaiting reconciliation."
                        Menu.Refused reason -> reason
                        Menu.Cancelled -> "Cancelled"
                        _ -> "Choose a window action"
                in div [class "context-menu",id "context-menu",attribute "role" "menu",attribute "aria-label" "Window actions",tabindex -1, attribute "data-menu-id" (String.fromInt (Menu.menuNumber menu.id)),menuKeyHandler keyboard,ignoreContext]
                    (List.indexedMap action menu.items ++ [p [attribute "role" "status"] [text status],button [id "context-dismiss",onClick (Dismiss menu.id),keyHandler (\key _ -> let owned=key=="Enter" || key==" " in {message=if owned then Dismiss menu.id else NoOp,stopPropagation=owned,preventDefault=owned})] [text "Dismiss"]])
    in div [class "shell",id "shell-root",attribute "data-phase" phase,attribute "data-transaction" (model.shell.effects.transaction |> Maybe.map (.status >> Effects.statusName) |> Maybe.withDefault "Idle")]
        [h1 [] [text "Windows"],p [id "connection-status",attribute "role" "status",attribute "aria-live" "polite"] [text (Shell.status model.shell)],
        if model.shell.phase==Shell.Detached then button [id "reconnect",onClick Reconnect,disabled model.shell.reconnecting] [text "Reconnect"] else button [onClick Refresh,disabled pending] [text "Refresh"],
        Html.ul [class "windows"] (List.map item (rows model)),menuView]

main : Program () Model Msg
main = Browser.element {init=\_ -> (initial,Cmd.none),update=update,view=view,subscriptions=\_ -> nativeEvents Native}
