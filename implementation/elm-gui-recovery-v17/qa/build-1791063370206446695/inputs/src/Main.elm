port module Main exposing (main)

import ActionProjection
import Binding
import Browser
import Effects
import Html exposing (Html, button, div, h1, li, p, span, text)
import Html.Attributes exposing (attribute, class, disabled, id)
import Html.Events exposing (onClick)
import Html.Keyed as Keyed
import Json.Decode as D
import Json.Encode as E
import Shell exposing (Effect(..), Model, Msg(..), Phase(..))
import UInt64

port nativeEvents : (D.Value -> msg) -> Sub msg
port nativeRequests : E.Value -> Cmd msg
update : Msg -> Model -> (Model,Cmd Msg)
update msg model =
    let (next,effects) = Shell.update msg model
        command effect = case effect of
            Send value -> nativeRequests value
            RestartBackend -> nativeRequests (E.object [("protocolVersion",E.int 3),("kind",E.string "host-reconnect")])
    in (next,Cmd.batch (List.map command effects))
view : Model -> Html Msg
view model =
    let rows = model.effects.observed |> Maybe.map (.scene >> ActionProjection.windows) |> Maybe.withDefault []
        pending = Effects.pending model.effects
        live = model.phase == Ready
        prefix = model.binding |> Maybe.map (\binding -> E.encode 0 (Binding.encode binding)) |> Maybe.withDefault "detached"
        item row =
            (prefix ++ ":" ++ UInt64.string row.incarnation, li [attribute "data-incarnation" (UInt64.string row.incarnation)]
                [ span [class "window-title"] [text row.label]
                , span [class "state"] [text ((if live then "" else "Last known: ") ++ (if row.minimized then "Minimized" else "Open"))]
                , button [disabled (not (Shell.available model)), onClick (Act (if row.minimized then "restore" else "minimize") row.incarnation), attribute "aria-label" ((if row.minimized then "Restore " else "Minimize ") ++ row.label)] [text (if row.minimized then "Restore" else "Minimize")]
                ])
        phase = case model.phase of
            Ready -> "Coherent"
            Detached -> "Detached"
            Reconciling -> "Awaiting"
            Exhausted -> "Exhausted"
        transaction = model.effects.transaction |> Maybe.map (.status >> Effects.statusName) |> Maybe.withDefault "Idle"
    in div [class "shell",id "shell-root",attribute "data-phase" phase,attribute "data-transaction" transaction,attribute "aria-busy" (if pending || model.phase == Reconciling then "true" else "false")]
        [h1 [] [text "Windows"],p [id "connection-status",attribute "role" "status",attribute "aria-live" "polite"] [text (Shell.status model)]
        , if model.phase == Detached then button [id "reconnect",onClick Reconnect,disabled model.reconnecting] [text "Reconnect"] else button [onClick Refresh,disabled (model.phase == Exhausted || pending)] [text "Refresh"]
        , Keyed.node "ul" [class "families"] (List.map item rows)]
main : Program () Model Msg
main = Browser.element {init = \_ -> (Shell.initial,Cmd.none),update = update,view = view,subscriptions = \_ -> nativeEvents Incoming}
