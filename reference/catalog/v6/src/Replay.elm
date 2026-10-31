port module Replay exposing (main)
import Effects
import Json.Decode as D
import Json.Encode as E
import Platform
port incoming : (D.Value -> msg) -> Sub msg
port outgoing : E.Value -> Cmd msg
type Msg = Run D.Value
main : Program () () Msg
main = Platform.worker
    { init = \_ -> ((),Cmd.none)
    , subscriptions = \_ -> incoming Run
    , update = \(Run value) _ ->
        let
            results = D.decodeValue (D.list D.value) value |> Result.map (\messages ->
                List.foldl (\message (model,rows) ->
                    let (next,effect,error)=Effects.apply message model
                    in (next, rows ++ [E.object [("model",Effects.encode next),("effect",Maybe.withDefault E.null effect),("error",Maybe.map E.string error |> Maybe.withDefault E.null)]])) (Effects.empty,[]) messages |> Tuple.second)
        in ((),outgoing (case results of
            Ok rows -> E.list identity rows
            Err error -> E.object [("error",E.string (D.errorToString error))]))
    }
