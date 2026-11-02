port module TeaRendererSubscriptionsReplay exposing (main)

{-| QA-only single-root observer for NativePreviewRenderer ELM-TEA-004.
Imports only NativePreviewRenderer among port-owning roots so Elm 0.19 port
names stay disjoint. Complete Receiver.Model, complete subscriptionPlan, and
complete acceptedSnapshots/surfaceActions effects pass unchanged through one
pre-format Debug.log point.
All inputs are fixture data; native, browser, and release behavior are separate.
-}

import Json.Decode as D
import Json.Encode as E
import NativePreviewReceiver as Receiver
import NativePreviewRenderer as Renderer
import Platform


port incoming : (D.Value -> msg) -> Sub msg


port outgoing : E.Value -> Cmd msg


type alias ObservedState =
    { model : Receiver.Model
    , subscriptions : List Renderer.Subscription
    }


type StepEffects
    = ResetEffects
    | ReceiverEffects (Maybe E.Value)


type Msg
    = Input D.Value


type Command
    = Reset
    | RendererInit D.Value
    | RendererSnapshot D.Value
    | RendererAction String


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

                    "renderer-init" ->
                        request [ "value" ] (D.map RendererInit (D.field "value" D.value))

                    "renderer-snapshot" ->
                        request [ "value" ] (D.map RendererSnapshot (D.field "value" D.value))

                    "renderer-action" ->
                        request [ "id" ] (D.map RendererAction (D.field "id" D.string))

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


observe : Request -> Receiver.Model -> StepEffects -> ( Receiver.Model, Cmd Msg )
observe request model effects =
    let
        observed : ObservedState
        observed =
            { model = model
            , subscriptions = Renderer.subscriptionPlan model
            }

        ( capturedState, _ ) =
            Debug.log "TEA_SUBSCRIPTIONS_OBSERVE_V1" ( observed, effects )
    in
    ( capturedState.model, ack request.caseId request.step True "" )


update : Msg -> Receiver.Model -> ( Receiver.Model, Cmd Msg )
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
                    observe request (Receiver.init E.null) ResetEffects

                RendererInit value ->
                    observe request (Receiver.init value) (ReceiverEffects Nothing)

                RendererSnapshot value ->
                    let
                        ( nextReceiver, receipt ) =
                            Receiver.receive value model
                    in
                    observe request nextReceiver (ReceiverEffects receipt)

                RendererAction value ->
                    observe request model (ReceiverEffects (Receiver.action value model))


main : Program () Receiver.Model Msg
main =
    Platform.worker
        { init = \_ -> ( Receiver.init E.null, Cmd.none )
        , update = update
        , subscriptions = \_ -> incoming Input
        }
