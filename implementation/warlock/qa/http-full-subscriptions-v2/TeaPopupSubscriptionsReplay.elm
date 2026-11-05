port module TeaPopupSubscriptionsReplay exposing (main)

{-| QA-only single-root observer for Popup ELM-TEA-004 (tea-subscriptions).
Imports only Popup among port-owning roots so Elm 0.19 port names stay disjoint.
Complete Popup.Model, complete Popup.subscriptionPlan, and complete typed
Popup.Effect lists pass unchanged through one pre-format Debug.log point.
All inputs are fixture data; native, browser, and release behavior are separate.
-}

import Json.Decode as D
import Json.Encode as E
import Platform
import Popup


port incoming : (D.Value -> msg) -> Sub msg


port outgoing : E.Value -> Cmd msg


type alias ObservedState =
    { model : Popup.Model
    , subscriptions : List Popup.Subscription
    }


type StepEffects
    = ResetEffects
    | PopupEffects (List Popup.Effect)


type Msg
    = Input D.Value


type Command
    = Reset
    | PopupPresent D.Value
    | PopupAction E.Value
    | PopupLocalAction E.Value
    | PopupAnnounce D.Value
    | PopupNativePreview D.Value
    | PopupPreviewPainted D.Value
    | PopupNativeGrant D.Value
    | PopupNativeQuarantine D.Value
    | PopupNativeClosed D.Value
    | PopupNativeIssued D.Value
    | PopupNativeRetry D.Value
    | PopupNativeRetirement D.Value


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

                    "popup-present" ->
                        request [ "value" ] (D.map PopupPresent (D.field "value" D.value))

                    "popup-action" ->
                        request [ "value" ] (D.map PopupAction (D.field "value" D.value))

                    "popup-local-action" ->
                        request [ "value" ] (D.map PopupLocalAction (D.field "value" D.value))

                    "popup-announce" ->
                        request [ "value" ] (D.map PopupAnnounce (D.field "value" D.value))

                    "popup-native-preview" ->
                        request [ "value" ] (D.map PopupNativePreview (D.field "value" D.value))

                    "popup-preview-painted" ->
                        request [ "value" ] (D.map PopupPreviewPainted (D.field "value" D.value))

                    "popup-native-grant" ->
                        request [ "value" ] (D.map PopupNativeGrant (D.field "value" D.value))

                    "popup-native-quarantine" ->
                        request [ "value" ] (D.map PopupNativeQuarantine (D.field "value" D.value))

                    "popup-native-closed" ->
                        request [ "value" ] (D.map PopupNativeClosed (D.field "value" D.value))

                    "popup-native-issued" ->
                        request [ "value" ] (D.map PopupNativeIssued (D.field "value" D.value))

                    "popup-native-retry" ->
                        request [ "value" ] (D.map PopupNativeRetry (D.field "value" D.value))

                    "popup-native-retirement" ->
                        request [ "value" ] (D.map PopupNativeRetirement (D.field "value" D.value))

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


observe : Request -> Popup.Model -> StepEffects -> ( Popup.Model, Cmd Msg )
observe request model effects =
    let
        observed : ObservedState
        observed =
            { model = model
            , subscriptions = Popup.subscriptionPlan model
            }

        ( capturedState, _ ) =
            Debug.log "TEA_SUBSCRIPTIONS_OBSERVE_V1" ( observed, effects )
    in
    ( capturedState.model, ack request.caseId request.step True "" )


applyPopup : Request -> Popup.Msg -> Popup.Model -> ( Popup.Model, Cmd Msg )
applyPopup request message model =
    let
        ( nextPopup, effects ) =
            Popup.transition message model
    in
    observe request nextPopup (PopupEffects effects)


update : Msg -> Popup.Model -> ( Popup.Model, Cmd Msg )
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
                    observe request Popup.initial ResetEffects

                PopupPresent value ->
                    applyPopup request (Popup.Present value) model

                PopupAction value ->
                    applyPopup request (Popup.Action value) model

                PopupLocalAction value ->
                    applyPopup request (Popup.LocalAction value) model

                PopupAnnounce value ->
                    applyPopup request (Popup.Announce value) model

                PopupNativePreview value ->
                    applyPopup request (Popup.NativePreview value) model

                PopupPreviewPainted value ->
                    applyPopup request (Popup.PreviewPainted value) model

                PopupNativeGrant value ->
                    applyPopup request (Popup.NativeGrant value) model

                PopupNativeQuarantine value ->
                    applyPopup request (Popup.NativeQuarantine value) model

                PopupNativeClosed value ->
                    applyPopup request (Popup.NativeClosed value) model

                PopupNativeIssued value ->
                    applyPopup request (Popup.NativeIssued value) model

                PopupNativeRetry value ->
                    applyPopup request (Popup.NativeRetry value) model

                PopupNativeRetirement value ->
                    applyPopup request (Popup.NativeRetirement value) model


main : Program () Popup.Model Msg
main =
    Platform.worker
        { init = \_ -> ( Popup.initial, Cmd.none )
        , update = update
        , subscriptions = \_ -> incoming Input
        }
