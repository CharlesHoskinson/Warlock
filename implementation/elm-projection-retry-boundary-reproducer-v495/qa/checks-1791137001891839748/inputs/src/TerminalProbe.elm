port module TerminalProbe exposing (main)
import Binding
import Json.Decode as D
import Json.Encode as E
import Platform
import Shell
import UInt64
port incoming : (D.Value -> msg) -> Sub msg
port outgoing : E.Value -> Cmd msg
type Msg = Run D.Value
main : Program () () Msg
main = Platform.worker {init=\_ -> ((),Cmd.none),subscriptions=\_ -> incoming Run,update=\(Run raw) _ ->
 let decoded=D.decodeValue (D.map2 Tuple.pair (D.at ["request","binding"] Binding.decoder) (D.at ["request","requestId"] UInt64.decoder)) raw
 in case decoded of
  Err _ -> ((),outgoing E.null)
  Ok (binding,request) ->
   let base=Shell.initial
       current=D.decodeValue (D.field "counter" UInt64.decoder) raw |> Result.withDefault (UInt64.next request |> Maybe.withDefault request)
       bool name=D.decodeValue (D.field name D.bool) raw |> Result.withDefault False
       pending={base|binding=Just binding,request=current,expected=Just request,geometryExpected=Just current,phase=Shell.Reconciling,reconnecting=False,transportRefused=bool "transport",deferNotifications=bool "defer"}
       notice=D.decodeValue (D.field "frame" D.value) raw |> Result.withDefault E.null
       apply _ (model,count)=let (next,stepCommands)=Shell.update (Shell.Incoming notice) model in (next,count+List.length stepCommands)
       (final,commands)=List.foldl apply (pending,0) (List.range 1 (D.decodeValue (D.field "repetitions" D.int) raw |> Result.withDefault 100))
   in ((),outgoing (E.object [("phase",E.string (case final.phase of
          Shell.Detached -> "detached"
          Shell.Reconciling -> "reconciling"
          Shell.Ready -> "ready"
          Shell.Exhausted -> "exhausted")),("model",Shell.encode final),("expected",Maybe.map (UInt64.string >> E.string) final.expected |> Maybe.withDefault E.null),("geometryExpected",Maybe.map (UInt64.string >> E.string) final.geometryExpected |> Maybe.withDefault E.null),("retry",E.bool final.projectionRetryQueued),("effectsPreserved",E.bool (final.effects==pending.effects)),("commands",E.int commands)]))}
