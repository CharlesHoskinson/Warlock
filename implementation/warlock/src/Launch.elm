module Launch exposing (refusal, Acknowledgement, Model, PendingToken, Selection, acknowledgeUnknown, bind, catalog, disconnect, init, receive, select, start, status, timeout, pending, uncertain)

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


type PendingToken
    = PendingToken String Intent


type Acknowledgement
    = Acknowledgement Intent


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
    let snapshot = Catalog.decode raw |> Result.toMaybe
        phase = case (snapshot,model.phase) of
            (Just _,Settled _ Refused) -> Idle
            (Just _,Settled _ Submitted) -> Idle
            _ -> model.phase
    in advance (Model { model | snapshot = snapshot, phase = phase })


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
        (D.map5 (\version kind intent state reason -> { version = version, kind = kind, intent = intent, state = state, reason = reason })
            (D.field "catalogProtocol" D.int)
            (D.field "kind" D.string)
            (D.field "intent" intentDecoder)
            (D.field "status" D.string)
            (D.field "reason" D.string)
        )
        |> D.andThen
            (\receipt ->
                if receipt.version /= 1 || receipt.kind /= "launch-outcome" then
                    D.fail "Launch receipt version/kind"

                else if receipt.state == "Submitted" && receipt.reason == "native-submission-accepted" then
                    D.succeed ( receipt.intent, Submitted )

                else if receipt.state == "Unknown" && receipt.reason == "submission-not-confirmed" then
                    D.succeed ( receipt.intent, Unknown )

                else if receipt.state == "Refused" && List.member receipt.reason [ "retired-authority", "request-reuse", "retired-request", "catalog-unavailable", "stale-catalog", "removed-entry", "native-entry-unavailable", "desktop-entry-raced" ] then
                    D.succeed ( receipt.intent, Refused )

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


pending : Model -> Maybe PendingToken
pending (Model model) =
    case model.phase of
        Pending host intent ->
            Just (PendingToken host intent)

        _ ->
            Nothing


uncertain : Model -> Maybe Acknowledgement
uncertain (Model model) =
    case model.phase of
        Settled intent Unknown ->
            Just (Acknowledgement intent)

        _ ->
            Nothing


timeout : PendingToken -> Model -> Model
timeout (PendingToken host intent) ((Model model) as current) =
    case model.phase of
        Pending owner active ->
            if owner == host && active == intent then
                advance (Model { model | phase = Settled intent Unknown })

            else
                current

        _ ->
            current


disconnect : Model -> Model
disconnect current =
    let
        (Model model) =
            pending current |> Maybe.map (\token -> timeout token current) |> Maybe.withDefault current
    in
    advance (Model { model | host = Nothing, snapshot = Nothing })


acknowledgeUnknown : Acknowledgement -> Model -> Model
acknowledgeUnknown (Acknowledgement intent) ((Model model) as current) =
    case model.phase of
        Settled active Unknown ->
            if active == intent then
                advance (Model { model | phase = Idle })

            else
                current

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


-- A settled native refusal, including the exact intent identity. This getter
-- neither reconstructs a selection nor permits another launch.
refusal : Model -> Maybe { intent : E.Value, entry : String }
refusal (Model model) = case model.phase of
    Settled intent Refused -> Just {intent=E.object [("request",E.string (UInt64.string intent.request)),("lifetime",E.string (UInt64.string intent.lifetime)),("generation",E.string (UInt64.string intent.generation)),("entry",E.string intent.entry)],entry=intent.entry}
    _ -> Nothing
