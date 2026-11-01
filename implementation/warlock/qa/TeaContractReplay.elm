port module TeaContractReplay exposing (main)

{-| QA-only driver for the actual controller route. The policy model and the
complete effects from its latest transition remain Elm values. The single
debug observation point passes those values unchanged to a separately reviewed,
non-optimised compiled-fixture observer; its printed representation is not an
oracle. Incoming events are fixture data; they do not establish native,
browser, or acceptance observations.

Deadline commands refer to actual messages previously returned by the policy,
not decoded or reconstructed authority tokens. The retained list is append-only
so a fixture can deliberately deliver an old deadline after a later transition.
An explicit prelude folds literal incoming events from Policy.initial. Its final
complete model and final effects must be independently asserted; intermediate
setup steps are not counted as verified transitions.
-}

import Desktop
import DesktopPolicy as Policy
import Json.Decode as D
import Json.Encode as E
import Platform


port incoming : (D.Value -> msg) -> Sub msg


port outgoing : E.Value -> Cmd msg


type alias Model =
    { policy : Policy.Model
    , lastEffects : List Policy.Effect
    , deadlines : List Desktop.Msg
    }


type Msg
    = Input D.Value


type Command
    = Reset
    | Incoming D.Value
    | Deadline Int
    | TransportLost
    | Prelude (List D.Value)


type alias Request =
    { caseId : String
    , step : Int
    , command : Command
    }


initial : Model
initial =
    { policy = Policy.initial, lastEffects = [], deadlines = [] }


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
            D.int |> D.andThen (\value -> if value >= 0 then D.succeed value else D.fail "negative number")

        caseId =
            D.string |> D.andThen (\value -> if String.isEmpty value then D.fail "empty case id" else D.succeed value)

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

                    "incoming" ->
                        request [ "value" ] (D.map Incoming (D.field "value" D.value))

                    "deadline" ->
                        request [ "index" ] (D.map Deadline (D.field "index" nonnegative))

                    "transportLost" ->
                        request [] (D.succeed TransportLost)

                    "prelude" ->
                        request [ "values" ]
                            (D.field "values" (D.list D.value)
                                |> D.andThen
                                    (\values ->
                                        if List.isEmpty values then
                                            D.fail "empty prelude"

                                        else
                                            D.succeed (Prelude values)
                                    )
                            )

                    _ ->
                        D.fail "unsupported command"
            )


remember : Policy.Effect -> Maybe Desktop.Msg
remember effect =
    case effect of
        Policy.Delay _ message ->
            Just message

        Policy.Publish _ ->
            Nothing


ack : Request -> Bool -> String -> Int -> Cmd Msg
ack request ok reason timers =
    outgoing
        (E.object
            [ ( "caseId", E.string request.caseId )
            , ( "step", E.int request.step )
            , ( "ok", E.bool ok )
            , ( "error", E.string reason )
            , ( "timers", E.int timers )
            ]
        )


observe : Request -> Model -> ( Model, Cmd Msg )
observe request model =
    let
        -- The complete tuple is captured before Debug's textual formatting.
        -- The observer must fail closed if its instrumentation is absent.
        ( policy, effects ) =
            Debug.log "TEA_CONTRACT_OBSERVE_V1" ( model.policy, model.lastEffects )

        retained =
            { model | policy = policy, lastEffects = effects }
    in
    ( retained, ack request True "" (List.length retained.deadlines) )


apply : Request -> Policy.Msg -> Model -> ( Model, Cmd Msg )
apply request message model =
    let
        ( policy, effects ) =
            Policy.update message model.policy
    in
    observe request
        { policy = policy
        , lastEffects = effects
        , deadlines = model.deadlines ++ List.filterMap remember effects
        }


update : Msg -> Model -> ( Model, Cmd Msg )
update (Input raw) model =
    case D.decodeValue requestDecoder raw of
        Err _ ->
            ( model
            , outgoing (E.object [ ( "ok", E.bool False ), ( "error", E.string "invalid command" ) ])
            )

        Ok request ->
            case request.command of
                Reset ->
                    observe request initial

                Incoming value ->
                    apply request (Policy.Incoming value) model

                TransportLost ->
                    apply request Policy.TransportLost model

                Prelude values ->
                    let
                        step value current =
                            let
                                ( policy, effects ) =
                                    Policy.update (Policy.Incoming value) current.policy
                            in
                            { policy = policy
                            , lastEffects = effects
                            , deadlines = current.deadlines ++ List.filterMap remember effects
                            }
                    in
                    observe request (List.foldl step initial values)

                Deadline index ->
                    case List.head (List.drop index model.deadlines) of
                        Just message ->
                            apply request (Policy.Deadline message) model

                        Nothing ->
                            ( model, ack request False "unknown deadline index" (List.length model.deadlines) )


main : Program () Model Msg
main =
    Platform.worker
        { init = \_ -> ( initial, Cmd.none )
        , update = update
        , subscriptions = \_ -> incoming Input
        }
