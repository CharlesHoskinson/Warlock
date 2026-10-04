module Launch exposing (Model, Selection, acknowledgeUnknown, bind, catalog, disconnect, init, receive, select, start, status, timeout)

import Catalog
import Json.Decode as D
import Json.Encode as E
import UInt64 exposing (Counter)


type alias Intent =
    { request : Counter, lifetime : Counter, generation : Counter, entry : String }


type ResultState
    = Submitted
    | Refused
    | Unknown


type Phase
    = Idle
    | Pending String Intent
    | Settled Intent ResultState


type Model
    = Model
        { host : Maybe String
        , snapshot : Maybe Catalog.Snapshot
        , revision : Counter
        , request : Counter
        , phase : Phase
        }


type Selection
    = Selection String Counter Counter Counter Catalog.EntryId


init : Model
init =
    Model { host = Nothing, snapshot = Nothing, revision = UInt64.zero, request = UInt64.zero, phase = Idle }


advance : Model -> Model
advance (Model model) =
    case UInt64.next model.revision of
        Just revision ->
            Model { model | revision = revision }

        Nothing ->
            Model { model | host = Nothing, snapshot = Nothing }


bind : String -> Model -> Model
bind host ((Model model) as current) =
    if String.isEmpty host || String.length host > 256 || String.any (\c -> Char.toCode c < 32) host then
        disconnect current

    else if model.host == Just host then
        current

    else
        let
            (Model retired) =
                disconnect current
        in
        advance (Model { retired | host = Just host })


catalog : D.Value -> Model -> Model
catalog raw (Model model) =
    advance (Model { model | snapshot = Catalog.decode raw |> Result.toMaybe })


select : String -> Model -> Maybe Selection
select identity (Model model) =
    Maybe.map2
        (\host snapshot ->
            Catalog.lookup identity snapshot
                |> Maybe.map
                    (\entry ->
                        let
                            scope =
                                Catalog.scope snapshot
                        in
                        Selection host model.revision scope.lifetime scope.generation entry.identity
                    )
        )
        model.host
        model.snapshot
        |> Maybe.andThen identityFunction


identityFunction : a -> a
identityFunction value =
    value


start : Selection -> Model -> ( Model, Maybe E.Value )
start (Selection host revision lifetime generation entry) ((Model model) as current) =
    let
        ready =
            case model.phase of
                Idle ->
                    True

                Settled _ Unknown ->
                    False

                Settled _ _ ->
                    True

                Pending _ _ ->
                    False
    in
    case ( model.snapshot, UInt64.next model.request ) of
        ( Just snapshot, Just request ) ->
            let
                scope =
                    Catalog.scope snapshot
            in
            if ready && model.host == Just host && model.revision == revision && lifetime == scope.lifetime && generation == scope.generation then
                case Catalog.intent request entry snapshot of
                    Just wire ->
                        ( advance (Model { model | request = request, phase = Pending host { request = request, lifetime = lifetime, generation = generation, entry = Catalog.id entry } }), Just wire )

                    Nothing ->
                        ( current, Nothing )

            else
                ( current, Nothing )

        _ ->
            ( current, Nothing )


strict : List String -> D.Decoder a -> D.Decoder a
strict names decoder =
    D.keyValuePairs D.value
        |> D.andThen
            (\fields ->
                if List.sort (List.map Tuple.first fields) == List.sort names then
                    decoder

                else
                    D.fail "Unexpected launch receipt fields"
            )


positive : D.Decoder Counter
positive =
    UInt64.decoder
        |> D.andThen (\value -> if value == UInt64.zero then D.fail "Zero launch counter" else D.succeed value)


intentDecoder : D.Decoder Intent
intentDecoder =
    strict [ "request", "lifetime", "generation", "entry" ]
        (D.map4 Intent
            (D.field "request" positive)
            (D.field "lifetime" positive)
            (D.field "generation" positive)
            (D.field "entry" D.string |> D.andThen (\value -> if String.isEmpty value || String.length value > 256 || String.any (\c -> Char.toCode c < 32) value then D.fail "Launch identity" else D.succeed value))
        )


receiptDecoder : D.Decoder ( Intent, ResultState )
receiptDecoder =
    strict [ "catalogProtocol", "kind", "intent", "status", "reason" ]
        (D.map5 (\version kind intent state reason -> ( version, kind, intent, state, reason ))
            (D.field "catalogProtocol" D.int)
            (D.field "kind" D.string)
            (D.field "intent" intentDecoder)
            (D.field "status" D.string)
            (D.field "reason" D.string)
        )
        |> D.andThen
            (\( version, kind, intent, state, reason ) ->
                if version /= 1 || kind /= "launch-outcome" then
                    D.fail "Launch receipt version/kind"

                else if state == "Submitted" && reason == "native-submission-accepted" then
                    D.succeed ( intent, Submitted )

                else if state == "Unknown" && reason == "submission-not-confirmed" then
                    D.succeed ( intent, Unknown )

                else if state == "Refused" && List.member reason [ "retired-authority", "request-reuse", "retired-request", "catalog-unavailable", "stale-catalog", "removed-entry", "native-entry-unavailable", "desktop-entry-raced" ] then
                    D.succeed ( intent, Refused )

                else
                    D.fail "Launch receipt outcome"
            )


receive : String -> D.Value -> Model -> Model
receive host raw ((Model model) as current) =
    case ( model.phase, D.decodeValue receiptDecoder raw ) of
        ( Pending owner intent, Ok ( received, result ) ) ->
            if host == owner && model.host == Just owner && received == intent then
                advance (Model { model | phase = Settled intent result })

            else
                current

        _ ->
            current


timeout : Model -> Model
timeout ((Model model) as current) =
    case model.phase of
        Pending _ intent ->
            advance (Model { model | phase = Settled intent Unknown })

        _ ->
            current


disconnect : Model -> Model
disconnect current =
    let
        (Model model) =
            timeout current
    in
    advance (Model { model | host = Nothing, snapshot = Nothing })


acknowledgeUnknown : Model -> Model
acknowledgeUnknown ((Model model) as current) =
    case model.phase of
        Settled _ Unknown ->
            advance (Model { model | phase = Idle })

        _ ->
            current


status : Model -> String
status (Model model) =
    case model.phase of
        Idle ->
            "Idle"

        Pending _ _ ->
            "Pending"

        Settled _ Submitted ->
            "Submitted"

        Settled _ Refused ->
            "Refused"

        Settled _ Unknown ->
            "Unknown"
