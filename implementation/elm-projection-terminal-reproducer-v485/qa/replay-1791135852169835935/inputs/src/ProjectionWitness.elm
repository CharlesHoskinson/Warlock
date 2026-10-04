port module ProjectionWitness exposing (main)
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
 let decoded=D.decodeValue (D.map2 Tuple.pair (D.field "binding" Binding.decoder) (D.field "requestId" UInt64.decoder)) raw
 in case decoded of
  Err _ -> ((),outgoing E.null)
  Ok (binding,request) ->
   let base=Shell.initial
       pending={base|binding=Just binding,request=request,expected=Just request,phase=Shell.Reconciling,reconnecting=False}
       notice=E.object [("protocolVersion",E.int 3),("kind",E.string "host-refresh")]
       apply _ (model,count)=let (next,commands)=Shell.update (Shell.Incoming notice) model in (next,count+List.length commands)
       (final,commands)=List.foldl apply (pending,0) (List.range 1 100)
   in ((),outgoing (E.object [("model",Shell.encode final),("expected",Maybe.map (UInt64.string >> E.string) final.expected |> Maybe.withDefault E.null),("commands",E.int commands)]))}
