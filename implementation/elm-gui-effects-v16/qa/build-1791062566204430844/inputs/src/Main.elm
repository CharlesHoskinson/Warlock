port module Main exposing (main)

import ActionProjection
import Browser
import Effects
import Html exposing (Html, button, div, h1, li, p, span, text)
import Html.Attributes exposing (attribute, class, disabled, id)
import Html.Events exposing (onClick)
import Html.Keyed as Keyed
import Json.Decode as D
import Json.Encode as E
import UInt64

port nativeEvents : (D.Value -> msg) -> Sub msg
port nativeRequests : E.Value -> Cmd msg

type Msg = Incoming D.Value | Refresh | Act String UInt64.Counter
type alias Model = { effects : Effects.Model, binding : Maybe D.Value, request : UInt64.Counter, ready : Bool, notice : String }
initial = { effects = Effects.empty, binding = Nothing, request = UInt64.zero, ready = False, notice = "Connecting…" }
refresh model =
    case ( model.binding, UInt64.next model.request ) of
        ( Just binding, Just request ) ->
            ( { model | request = request, ready = False }, nativeRequests (E.object [("protocolVersion",E.int 3),("kind",E.string "projection-request"),("binding",binding),("requestId",E.string (UInt64.string request))]) )
        _ -> ( { model | ready = False }, Cmd.none )
apply raw model =
    let ( changed, effect, error ) = Effects.apply raw model.effects
        next = { model | effects = changed, notice = Maybe.withDefault model.notice error }
        command = case (effect,model.binding) of
            (Just value,Just binding) ->
                case D.decodeValue (D.field "intent" D.value) value of
                    Ok intent -> nativeRequests (E.object [("protocolVersion",E.int 3),("kind",E.string "window-effect"),("effectProtocol",E.int 1),("binding",binding),("intent",intent)])
                    Err _ -> Cmd.none
            _ -> Cmd.none
    in (next,command)
update msg model =
    case msg of
        Refresh -> refresh model
        Act operation incarnation ->
            if not model.ready then (model,Cmd.none) else
                apply (E.object [("kind",E.string "begin"),("operation",E.string operation),("incarnation",E.string (UInt64.string incarnation))]) model
        Incoming raw ->
            case D.decodeValue (D.field "kind" D.string) raw of
                Ok "attached" ->
                    case D.decodeValue (D.field "binding" D.value) raw of
                        Ok binding -> refresh { model | binding = Just binding, ready = False }
                        Err _ -> (model,Cmd.none)
                Ok "host-refresh" -> refresh model
                Ok "host-disconnected" ->
                    let (changed,_) = apply (E.object [("kind",E.string "disconnect")]) model
                    in ({changed | binding = Nothing, ready = False, notice = "Connection lost. Reconnect to continue."},Cmd.none)
                Ok "snapshot" ->
                    let (changed,command) = apply raw model
                    in ({changed | ready = changed.effects.connected, notice = "Connected"},command)
                Ok "receipt" ->
                    let (changed,_) = apply raw model
                    in refresh changed
                _ -> (model,Cmd.none)
view model =
    let rows = model.effects.observed |> Maybe.map (.scene >> ActionProjection.windows) |> Maybe.withDefault []
        pending = Effects.pending model.effects
        item row =
            (UInt64.string row.incarnation, li [attribute "data-incarnation" (UInt64.string row.incarnation)]
                [ span [class "window-title"] [text row.label]
                , span [class "state"] [text (if row.minimized then "Minimized" else "Open")]
                , button [disabled (not model.ready || pending), onClick (Act (if row.minimized then "restore" else "minimize") row.incarnation), attribute "aria-label" ((if row.minimized then "Restore " else "Minimize ") ++ row.label)] [text (if row.minimized then "Restore" else "Minimize")]
                ])
        outcome = model.effects.transaction |> Maybe.map (.status >> Effects.statusName) |> Maybe.withDefault ""
    in div [class "shell",id "shell-root",attribute "data-phase" (if model.ready then "Coherent" else "Awaiting")]
        [h1 [] [text "Windows"],p [attribute "role" "status",attribute "aria-live" "polite"] [text (model.notice ++ " " ++ outcome)],button [onClick Refresh,disabled (model.binding == Nothing || pending)] [text "Refresh"],Keyed.node "ul" [class "families"] (List.map item rows)]
main = Browser.element {init = \_ -> (initial,Cmd.none),update = update,view = view,subscriptions = \_ -> nativeEvents Incoming}
