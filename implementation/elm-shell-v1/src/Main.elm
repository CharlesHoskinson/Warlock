port module Main exposing (main)

import Browser
import Domain exposing (Effect(..), Model, Msg(..), State(..))
import Html exposing (Html, button, div, h1, h2, li, p, span, text, ul)
import Html.Attributes exposing (attribute, class, disabled, id)
import Html.Events exposing (onClick)
import Json.Decode as D
import Json.Encode as E
import Protocol


port nativeEvents : (D.Value -> msg) -> Sub msg
port nativeRequests : E.Value -> Cmd msg


effects : List Effect -> Cmd Msg
effects items =
    -- Only independent snapshot requests exist in this inspection slice.
    Cmd.batch (List.map (\_ -> nativeRequests (Protocol.encodeRequest "snapshot-request")) items)


update : Msg -> Model -> ( Model, Cmd Msg )
update msg model =
    let
        ( next, intents ) = Domain.update msg model
    in
    ( next, effects intents )


view : Model -> Html Msg
view model =
    div [ class "shell", id "shell-root" ]
        [ h1 [] [ text "Elm shell" ]
        , p [ class "scope" ] [ text "Native host experiment · fixture data" ]
        , p [ attribute "role" "status", attribute "aria-live" "polite", id "connection-status" ] [ text model.status ]
        , button [ onClick Refresh ] [ text "Refresh observations" ]
        , case model.state of
            Connecting -> p [] [ text "Waiting for the host" ]
            Inspecting epoch windows ->
                div []
                    [ h2 [] [ text "Application families" ]
                    , p [] [ text ("Host epoch " ++ Protocol.idString epoch) ]
                    , ul [ class "families" ]
                        (List.map
                            (\window -> li [ attribute "data-incarnation" (Protocol.idString window.incarnation) ]
                                [ span [] [ text window.label ]
                                , span [ class "state" ] [ text (if window.minimized then "Minimized · fixture" else "Visible · fixture") ]
                                , button [ disabled True, attribute "aria-label" ("Activate " ++ window.label ++ " — native authority not connected") ] [ text "Activate unavailable" ]
                                ]) windows)
                    ]
        ]


main : Program () Model Msg
main =
    Browser.element
        { init = \_ -> ( Domain.initial, nativeRequests (Protocol.encodeRequest "snapshot-request") )
        , update = update
        , view = view
        , subscriptions = \_ -> nativeEvents Native
        }
