port module LaunchReplay exposing (main)

import Array exposing (Array)
import Json.Decode as D
import Json.Encode as E
import Launch
import Platform

port incoming : (D.Value -> msg) -> Sub msg
port outgoing : E.Value -> Cmd msg

type Msg = Run D.Value
type alias State = { model : Launch.Model, selections : Array Launch.Selection }

main : Program () () Msg
main =
    Platform.worker
        { init = \_ -> ( (), Cmd.none )
        , subscriptions = \_ -> incoming Run
        , update = \(Run raw) _ ->
            let
                events = D.decodeValue (D.list D.value) raw |> Result.withDefault []
                (_, rows) = List.foldl apply ({ model = Launch.init, selections = Array.empty }, []) events
            in
            ( (), outgoing (E.list identity (List.reverse rows)) )
        }

apply : D.Value -> ( State, List E.Value ) -> ( State, List E.Value )
apply raw (state, rows) =
    let
        string name = D.decodeValue (D.field name D.string) raw |> Result.withDefault ""
        value name = D.decodeValue (D.field name D.value) raw |> Result.withDefault E.null
        (model, selections, wire) =
            case string "kind" of
                "bind" -> (Launch.bind (string "host") state.model, state.selections, Nothing)
                "catalog" -> (Launch.catalog (value "snapshot") state.model, state.selections, Nothing)
                "select" ->
                    case Launch.select (string "entry") state.model of
                        Just selection -> (state.model, Array.push selection state.selections, Nothing)
                        Nothing -> (state.model, state.selections, Nothing)
                "start" ->
                    let index = D.decodeValue (D.field "index" D.int) raw |> Result.withDefault -1
                    in case Array.get index state.selections of
                        Just selection ->
                            let (next, intent) = Launch.start selection state.model
                            in (next, state.selections, intent)
                        Nothing -> (state.model, state.selections, Nothing)
                "receipt" -> (Launch.receive (string "host") (value "receipt") state.model, state.selections, Nothing)
                "timeout" -> (Launch.timeout state.model, state.selections, Nothing)
                "disconnect" -> (Launch.disconnect state.model, state.selections, Nothing)
                "acknowledge" -> (Launch.acknowledgeUnknown state.model, state.selections, Nothing)
                _ -> (state.model, state.selections, Nothing)
        next = { model = model, selections = selections }
        row = E.object [("status", E.string (Launch.status model)), ("selections", E.int (Array.length selections)), ("intent", Maybe.withDefault E.null wire)]
    in (next, row :: rows)
