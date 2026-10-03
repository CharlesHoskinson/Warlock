port module Main exposing (main)

import Browser
import Html exposing (Html, button, div, h1, li, p, span, text)
import Html.Attributes exposing (attribute, class, disabled, id)
import Html.Events exposing (onClick)
import Html.Keyed as Keyed
import Json.Decode as D
import Json.Encode as E
import Observation
import Observer exposing (Effect(..), Model, Phase(..))
import UInt64

port nativeEvents : (D.Value -> msg) -> Sub msg
port nativeRequests : E.Value -> Cmd msg

type Msg = Incoming D.Value | Refresh

encode : Effect -> E.Value
encode (RequestSnapshot binding requestId floor) =
    E.object
        [ ( "protocolVersion", E.int 3 ), ( "kind", E.string "snapshot-request" )
        , ( "binding", Observation.encodeBinding binding )
        , ( "requestId", E.string (UInt64.string requestId) )
        , ( "minimumWatermark", E.string (UInt64.string floor) )
        ]

hostEvent : D.Value -> Observer.Msg
hostEvent raw =
    case D.decodeValue (D.field "kind" D.string) raw of
        Ok "attached" ->
            case D.decodeValue (D.field "binding" Observation.bindingDecoder) raw of
                Ok binding -> Observer.Attach binding
                Err _ -> Observer.Disconnect
        Ok "host-disconnected" -> Observer.Disconnect
        Ok "host-refresh" -> Observer.Refresh
        _ -> Observer.Observe raw

update : Msg -> Model -> ( Model, Cmd Msg )
update msg model =
    let
        observation = case msg of
            Incoming raw -> hostEvent raw
            Refresh -> Observer.Refresh
        ( changed, effects ) = Observer.update observation model
    in
    ( changed, Cmd.batch (List.map (encode >> nativeRequests) effects) )

status : Phase -> String
status phase =
    case phase of
        Detached -> "Window information is unavailable."
        Awaiting -> "Updating window information…"
        Coherent -> "Connected"
        Gap -> "Updating after a connection interruption…"
        Exhausted -> "Reconnect the shell to update window information."

phaseName : Phase -> String
phaseName phase =
    case phase of
        Detached -> "Detached"
        Awaiting -> "Awaiting"
        Coherent -> "Coherent"
        Gap -> "Gap"
        Exhausted -> "Exhausted"

view : Model -> Html Msg
view model =
    let
        prefix = Maybe.map (Observation.encodeBinding >> E.encode 0) model.binding |> Maybe.withDefault "disconnected"
        windows = Maybe.map .windows model.projection |> Maybe.withDefault []
        item window =
            ( prefix ++ ":" ++ Observation.incarnationString window.incarnation
            , li [ attribute "data-incarnation" (Observation.incarnationString window.incarnation) ]
                [ span [ class "window-title" ] [ text window.label ]
                , span [ class "state" ] [ text (case window.minimized of
                    Just True -> "Minimized"
                    Just False -> "Open"
                    Nothing -> "Window state unavailable") ]
                , button [ disabled True, attribute "aria-label" ("Activate " ++ window.label ++ ": unavailable") ] [ text "Activate unavailable" ]
                ]
            )
    in
    div [ class "shell", id "shell-root", attribute "data-phase" (phaseName model.phase) ]
        [ h1 [] [ text "Windows" ]
        , p [ attribute "role" "status", attribute "aria-live" "polite", id "connection-status" ] [ text (status model.phase) ]
        , button [ onClick Refresh, disabled (model.phase == Detached || model.phase == Exhausted) ] [ text "Refresh" ]
        , if List.isEmpty windows then p [] [ text "No window information to show." ] else Keyed.node "ul" [ class "families" ] (List.map item windows)
        ]

main : Program () Model Msg
main =
    Browser.element
        { init = \_ -> ( Observer.initial, Cmd.none )
        , update = update
        , view = view
        , subscriptions = \_ -> nativeEvents Incoming
        }
