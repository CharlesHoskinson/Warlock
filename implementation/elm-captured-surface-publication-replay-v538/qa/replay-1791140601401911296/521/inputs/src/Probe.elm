port module Probe exposing (main)
import Desktop
import Json.Decode as D
import Json.Encode as E
import Platform
import Shell
import SurfaceController as C
import TaskbarShell
import UInt64
port incoming : (D.Value -> msg) -> Sub msg
port outgoing : E.Value -> Cmd msg
type Msg = Run D.Value
number text = D.decodeValue UInt64.decoder (E.string text) |> Result.withDefault UInt64.zero
owner text = Just {outputId=number text,providerId=number "1"}
transition own model = C.update (C.Interaction (Desktop.PresentationOwner own)) model
identity frame = D.decodeValue (D.keyValuePairs D.value) frame |> Result.map (List.filter (Tuple.first >> (/=) "publication") >> E.object >> E.encode 0) |> Result.withDefault "invalid"
countPublish effects = List.filter (\effect -> case effect of
 C.Publish _ -> True
 _ -> False) effects |> List.length
main : Program () () Msg
main = Platform.worker {init=\_ -> ((),Cmd.none),subscriptions=\_ -> incoming Run,update=\(Run raw) _ ->
 let frames=D.decodeValue (D.list D.value) raw |> Result.withDefault []
     (seed,_)=transition (owner "1") C.initial
     before=List.foldl (\frame model -> C.update (C.Interaction (Desktop.Incoming frame)) model |> Tuple.first) seed frames
     (after,effects)=transition (owner "2") before
 in ((),outgoing (E.object [("sameSurface",E.bool (identity (C.frame before)==identity (C.frame after))),("stateChanged",E.bool (C.desktop before/=C.desktop after)),("ownerCorrect",E.bool ((C.desktop after).ownerScope==owner "2")),("publishes",E.int (countPublish effects)),("otherEffects",E.int (List.length effects-countPublish effects)),("before",C.frame before),("after",C.frame after)]))}
