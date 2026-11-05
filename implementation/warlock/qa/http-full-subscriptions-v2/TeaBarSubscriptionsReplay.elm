port module TeaBarSubscriptionsReplay exposing (main)

{-| QA-only single-root observer for Bar ELM-TEA-004 (tea-subscriptions).
Imports only Bar among port-owning roots so Elm 0.19 port names stay disjoint.
Complete Bar.Model, complete Bar.subscriptionPlan, and complete typed Bar.Effect
lists pass unchanged through one pre-format Debug.log point.
All inputs are fixture data; native, browser, and release behavior are separate.
-}

import Bar
import Json.Decode as D
import Json.Encode as E
import Platform


port incoming : (D.Value -> msg) -> Sub msg


port outgoing : E.Value -> Cmd msg


type alias ObservedState =
    { model : Bar.Model
    , subscriptions : List Bar.Subscription
    }


type StepEffects
    = ResetEffects
    | BarEffects (List Bar.Effect)


type Msg
    = Input D.Value


type Command
    = Reset
    | BarPresent D.Value
    | BarAction E.Value
    | BarAnnounce D.Value


type alias Request =
    { caseId : String
    , step : Int
    , command : Command
    }


strict : List String -> D.Decoder a -> D.Decoder a
strict fields child =
    D.keyValuePairs D.value
        |> D.andThen
            (\pairs ->
                if List.sort (List.map Tuple.first pairs) == List.sort fields then
                    child

                else
                    D.fail "unexpected command fields"
            )


requestDecoder : D.Decoder Request
requestDecoder =
    let
        nonnegative =
            D.int |> D.andThen (\value -> if value >= 0 then D.succeed value else D.fail "negative step")

        caseId =
            D.string |> D.andThen (\value -> if String.isEmpty value then D.fail "empty caseId" else D.succeed value)

        request fields command =
            strict ("caseId" :: "step" :: "kind" :: fields)
                (D.map3 Request (D.field "caseId" caseId) (D.field "step" nonnegative) command)
    in
    D.field "kind" D.string
        |> D.andThen
            (\kind ->
                case kind of
                    "reset" ->
                        request [] (D.succeed Reset)

                    "bar-present" ->
                        request [ "value" ] (D.map BarPresent (D.field "value" D.value))

                    "bar-action" ->
                        request [ "value" ] (D.map BarAction (D.field "value" D.value))

                    "bar-announce" ->
                        request [ "value" ] (D.map BarAnnounce (D.field "value" D.value))

                    _ ->
                        D.fail "unsupported command"
            )


ack : String -> Int -> Bool -> String -> Cmd Msg
ack caseId step ok reason =
    outgoing
        (E.object
            [ ( "caseId", E.string caseId )
            , ( "step", E.int step )
            , ( "ok", E.bool ok )
            , ( "error", E.string reason )
            ]
        )


observe : Request -> Bar.Model -> StepEffects -> ( Bar.Model, Cmd Msg )
observe request model effects =
    let
        observed : ObservedState
        observed =
            { model = model
            , subscriptions = Bar.subscriptionPlan model
            }

        ( capturedState, _ ) =
            Debug.log "TEA_SUBSCRIPTIONS_OBSERVE_V1" ( observed, effects )
    in
    ( capturedState.model, ack request.caseId request.step True "" )


applyBar : Request -> Bar.Msg -> Bar.Model -> ( Bar.Model, Cmd Msg )
applyBar request message model =
    let
        ( nextBar, effects ) =
            Bar.step message model
    in
    observe request nextBar (BarEffects effects)


update : Msg -> Bar.Model -> ( Bar.Model, Cmd Msg )
update (Input raw) model =
    case D.decodeValue requestDecoder raw of
        Err problem ->
            let
                caseId =
                    D.decodeValue (D.field "caseId" D.string) raw |> Result.withDefault ""

                step =
                    D.decodeValue (D.field "step" D.int) raw |> Result.withDefault -1
            in
            ( model, ack caseId step False (D.errorToString problem) )

        Ok request ->
            case request.command of
                Reset ->
                    observe request Bar.initial ResetEffects

                BarPresent value ->
                    applyBar request (Bar.Present value) model

                BarAction value ->
                    applyBar request (Bar.Action value) model

                BarAnnounce value ->
                    applyBar request (Bar.Announce value) model


main : Program () Bar.Model Msg
main =
    Platform.worker
        { init = \_ -> ( Bar.initial, Cmd.none )
        , update = update
        , subscriptions = \_ -> incoming Input
        }
