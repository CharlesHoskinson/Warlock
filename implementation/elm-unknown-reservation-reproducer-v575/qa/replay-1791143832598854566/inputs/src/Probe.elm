port module Probe exposing (main)
import Effects
import Json.Decode as D
import Json.Encode as E
import Platform
import UInt64
port incoming : (D.Value -> msg) -> Sub msg
port outgoing : E.Value -> Cmd msg
type Msg = Run D.Value
number text = D.decodeValue UInt64.decoder (E.string text) |> Result.withDefault UInt64.zero
main : Program () () Msg
main = Platform.worker {init=\_ -> ((),Cmd.none),subscriptions=\_ -> incoming Run,update=\(Run raw) _ ->
 let intent=D.decodeValue (D.field "intent" D.value) raw |> Result.withDefault E.null
     context=D.decodeValue (D.field "projection" (D.field "context" D.value)) raw |> Result.withDefault E.null
     scene=D.decodeValue (D.field "projection" (D.field "scene" D.value)) raw |> Result.withDefault E.null
     (recovered,_,recoverError)=Effects.apply (E.object [("kind",E.string "recover"),("effectProtocol",E.int 1),("intent",intent)]) Effects.empty
     (observed,_,snapshotError)=Effects.apply (E.object [("kind",E.string "snapshot"),("context",context),("scene",scene)]) recovered
     (after,command,refusal)=Effects.apply (E.object [("kind",E.string "begin"),("operation",E.string "minimize"),("incarnation",E.string "2")]) observed
     blocked=observed.observed |> Maybe.map (\snapshot -> Effects.blocked snapshot.context.lifetime (number "2") observed) |> Maybe.withDefault False
 in ((),outgoing (E.object [("recoverError",recoverError |> Maybe.map E.string |> Maybe.withDefault E.null),("snapshotError",snapshotError |> Maybe.map E.string |> Maybe.withDefault E.null),("blocked",E.bool blocked),("connected",E.bool observed.connected),("unresolved",E.int (List.length after.unresolved)),("request",E.string (UInt64.string after.request)),("emitted",E.bool (command/=Nothing)),("refusal",refusal |> Maybe.map E.string |> Maybe.withDefault E.null)]))}
