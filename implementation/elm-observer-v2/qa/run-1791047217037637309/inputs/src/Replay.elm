port module Replay exposing (main)

import CounterChecks
import Json.Decode as D
import Json.Encode as E
import Observation
import Observer exposing (Effect(..), Msg(..), Phase(..))
import Platform
import UInt64


port transcripts : (D.Value -> msg) -> Sub msg
port results : E.Value -> Cmd msg

type Msg = Run D.Value


operation : D.Decoder Observer.Msg
operation =
    D.field "op" D.string |> D.andThen
        (\op -> case op of
            "attach" -> D.map Attach (D.field "binding" Observation.bindingDecoder)
            "observe" -> D.map Observe (D.field "event" D.value)
            "disconnect" -> D.succeed Disconnect
            "refresh" -> D.succeed Refresh
            _ -> D.fail "Unknown replay operation"
        )


phase : Phase -> String
phase p =
    case p of
        Detached -> "Detached"
        Awaiting -> "Awaiting"
        Coherent -> "Coherent"
        Gap -> "Gap"
        Exhausted -> "Exhausted"


summary : Observer.Model -> List Effect -> E.Value
summary model effects =
    let
        optional encode value = Maybe.withDefault E.null (Maybe.map encode value)
        projection p = E.object
            [ ( "sequence", E.string (Observation.sequenceString p.sequence) )
            , ( "revision", E.string (Observation.revisionString p.revision) )
            , ( "windows", E.list (\w -> E.object [ ( "incarnation", E.string (Observation.incarnationString w.incarnation) ), ( "label", E.string w.label ), ( "minimized", E.bool w.minimized ) ]) p.windows )
            ]
        effect (RequestSnapshot binding requestId watermark) = E.object
            [ ( "kind", E.string "read-only-snapshot" ), ( "binding", Observation.encodeBinding binding ), ( "requestId", E.string (UInt64.string requestId) ), ( "minimumWatermark", E.string (UInt64.string watermark) ) ]
    in
    E.object
        [ ( "phase", E.string (phase model.phase) )
        , ( "projection", optional projection model.projection )
        , ( "binding", optional Observation.encodeBinding model.binding )
        , ( "floor", E.string (UInt64.string model.floor) )
        , ( "lastRequest", E.string (UInt64.string model.lastRequest) )
        , ( "pending", optional (UInt64.string >> E.string) model.pending )
        , ( "effects", E.list effect effects )
        ]


replay : List Observer.Msg -> E.Value
replay operations =
    let
        step msg ( model, steps ) =
            let ( changed, effects ) = Observer.update msg model in
            ( changed, summary changed effects :: steps )
        ( _, reversed ) = List.foldl step ( Observer.initial, [] ) operations
    in
    E.list identity (List.reverse reversed)


caseDecoder : D.Decoder ( String, List Observer.Msg )
caseDecoder = D.map2 Tuple.pair (D.field "name" D.string) (D.field "operations" (D.list operation))


main : Program () () Msg
main =
    Platform.worker
        { init = \_ -> ( (), Cmd.none )
        , update = \(Run raw) model ->
            case D.decodeValue (D.list caseDecoder) raw of
                Ok cases -> ( model, results (E.object [ ( "counters", CounterChecks.results ), ( "cases", E.list (\( name, ops ) -> E.object [ ( "name", E.string name ), ( "steps", replay ops ) ]) cases ) ]) )
                Err err -> ( model, results (E.object [ ( "error", E.string (D.errorToString err) ) ]) )
        , subscriptions = \_ -> transcripts Run
        }
