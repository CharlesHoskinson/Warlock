port module TaskbarShellReplay exposing (main)
import Json.Decode as D
import Json.Encode as E
import Platform
import Shell
import TaskbarShell exposing (Msg(..))
import UInt64
port incoming : (D.Value -> msg) -> Sub msg
port outgoing : E.Value -> Cmd msg
type Msg = Run D.Value
message model raw =
    let
        scope = D.keyValuePairs D.value |> D.andThen (\fields -> if List.any (\(name,_) -> name == "scope") fields then D.field "scope" Shell.stampDecoder else Shell.capture model.shell |> Maybe.map D.succeed |> Maybe.withDefault (D.fail "Missing scope"))
        decoder = D.field "kind" D.string |> D.andThen (\kind -> case kind of
            "primary" -> D.map2 Primary scope (D.field "key" D.string)
            "choose" -> D.map3 Choose scope (D.field "generation" UInt64.decoder) (D.field "root" UInt64.decoder)
            "close" -> D.map2 Close scope (D.field "generation" UInt64.decoder)
            "reconnect" -> D.succeed (Native Shell.Reconnect)
            "refresh" -> D.succeed (Native Shell.Refresh)
            _ -> D.succeed (Native (Shell.Incoming raw)))
    in D.decodeValue decoder raw |> Result.withDefault (Native Shell.Ignore)
encode model effects =
    E.object [("shell",Shell.encode model.shell),("generation",E.string (UInt64.string model.generation)),("picker",model.picker |> Maybe.map (\picker -> E.object [("key",E.string picker.key),("generation",E.string (UInt64.string picker.generation))]) |> Maybe.withDefault E.null),("commands",E.list (\effect -> case effect of
        Shell.Send value -> value
        Shell.ArmPrepared token -> E.object [("kind",E.string "prepared-deadline"),("token",E.string (UInt64.string token))]
        Shell.RestartBackend -> E.object [("kind",E.string "host-reconnect")]) effects)]
main : Program () () Msg
main = Platform.worker {init=\_ -> ((),Cmd.none),subscriptions=\_ -> incoming Run,update=\(Run value) _ ->
    let result = D.decodeValue (D.list D.value) value |> Result.map (\messages -> List.foldl (\raw (model,rows) -> let (next,effects)=TaskbarShell.update (message model raw) model in (next,rows ++ [encode next effects])) (TaskbarShell.initial,[]) messages |> Tuple.second)
    in ((),outgoing (result |> Result.withDefault [] |> E.list identity))}
