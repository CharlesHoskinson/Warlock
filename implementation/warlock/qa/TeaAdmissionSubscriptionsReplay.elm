port module TeaAdmissionSubscriptionsReplay exposing (main)

{-| QA-only single-root observer for NativePreviewAdmission ELM-TEA-004.
Imports only NativePreviewAdmission among port-owning roots so Elm 0.19 port
names stay disjoint. Complete Presentation.Model, complete subscriptionPlan,
and complete action dispatch effects pass unchanged through one Debug.log point.
All inputs are fixture data; native, browser, and release behavior are separate.
-}

import Json.Decode as D
import Json.Encode as E
import NativePreviewAdmission as Admission
import Platform
import Presentation


port incoming : (D.Value -> msg) -> Sub msg


port outgoing : E.Value -> Cmd msg


type alias ObservedState =
    { model : Presentation.Model
    , subscriptions : List Admission.Subscription
    }


type StepEffects
    = ResetEffects
    | AdmissionEffects (Maybe E.Value)


type Msg
    = Input D.Value


type Command
    = Reset
    | AdmissionPresent D.Value
    | AdmissionAction E.Value


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

                    "admission-present" ->
                        request [ "value" ] (D.map AdmissionPresent (D.field "value" D.value))

                    "admission-action" ->
                        request [ "value" ] (D.map AdmissionAction (D.field "value" D.value))

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


observe : Request -> Presentation.Model -> StepEffects -> ( Presentation.Model, Cmd Msg )
observe request model effects =
    let
        observed : ObservedState
        observed =
            { model = model
            , subscriptions = Admission.subscriptionPlan model
            }

        ( capturedState, _ ) =
            Debug.log "TEA_SUBSCRIPTIONS_OBSERVE_V1" ( observed, effects )
    in
    ( capturedState.model, ack request.caseId request.step True "" )


update : Msg -> Presentation.Model -> ( Presentation.Model, Cmd Msg )
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
                    observe request Presentation.initial ResetEffects

                AdmissionPresent value ->
                    observe request (Presentation.accept value model) (AdmissionEffects Nothing)

                AdmissionAction value ->
                    observe request model (AdmissionEffects (Presentation.dispatch True value model))


main : Program () Presentation.Model Msg
main =
    Platform.worker
        { init = \_ -> ( Presentation.initial, Cmd.none )
        , update = update
        , subscriptions = \_ -> incoming Input
        }
