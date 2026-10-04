port module ShellReplay exposing (main)
import Effects
import Json.Decode as D
import Json.Encode as E
import Platform
import Shell
import UInt64
port incoming : (D.Value -> msg) -> Sub msg
port outgoing : E.Value -> Cmd msg
type Msg = Run D.Value
displayedStamp model =
    D.keyValuePairs D.value |> D.andThen (\fields ->
        if List.any (\(name,_) -> name == "stamp") fields then D.field "stamp" Shell.stampDecoder
        else Shell.capture model |> Maybe.map D.succeed |> Maybe.withDefault (D.fail "Missing displayed scope"))
message model value =
    case D.decodeValue (D.field "kind" D.string) value of
        Ok "user-reconnect" -> Shell.Reconnect
        Ok "user-refresh" -> Shell.Refresh
        Ok "user-action" ->
            case D.decodeValue (D.map3 Shell.Act (displayedStamp model) (D.field "operation" Effects.operationDecoder) (D.field "incarnation" UInt64.decoder)) value of
                Ok msg -> msg
                Err _ -> Shell.Incoming E.null
        _ -> Shell.Incoming value
main : Program () () Msg
main = Platform.worker
    {init = \_ -> ((),Cmd.none),subscriptions = \_ -> incoming Run
    ,update = \(Run value) _ ->
        let result = D.decodeValue (D.list D.value) value |> Result.map (\messages ->
                List.foldl (\raw (model,rows) ->
                    let (next,effects) = Shell.update (message model raw) model
                        effect command = case command of
                            Shell.Send frame -> frame
                            Shell.RestartBackend -> E.object [("kind",E.string "host-reconnect")]
                    in (next,rows ++ [E.object [("model",Shell.encode next),("commands",E.list effect effects)]])) (Shell.initial,[]) messages |> Tuple.second)
        in ((),outgoing (case result of
            Ok rows -> E.list identity rows
            Err error -> E.object [("error",E.string (D.errorToString error))]))}
