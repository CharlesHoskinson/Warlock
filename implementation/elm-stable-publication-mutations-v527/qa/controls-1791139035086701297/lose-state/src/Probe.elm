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
 let name=D.decodeValue D.string raw |> Result.withDefault "invalid"
     (seed,_)=transition (owner "1") C.initial
     before=if name=="startup" then C.initial else if name=="reconnect" then C.update (C.Interaction (Desktop.Incoming (E.object [("kind",E.string "host-disconnected")]))) seed |> Tuple.first else seed
     event=case name of
       "startup" -> C.Interaction (Desktop.PresentationOwner (owner "1"))
       "owner2" -> C.Interaction (Desktop.PresentationOwner (owner "2"))
       "duplicate" -> C.Interaction (Desktop.PresentationOwner (owner "1"))
       "disconnect" -> C.Interaction (Desktop.Incoming (E.object [("kind",E.string "host-disconnected")]))
       "reconnect" -> C.Interaction (Desktop.Window (TaskbarShell.Native Shell.Reconnect))
       "invalid" -> C.Renderer E.null
       "relocateClosed" -> C.NativeRelocate
       _ -> C.Interaction (Desktop.PresentationOwner Nothing)
     step index (model,pubCount,otherCount)=let (next,effects)=transition (owner (if modBy 2 index==0 then "1" else "2")) model
                                         in (next,pubCount+countPublish effects,otherCount+List.length effects-countPublish effects)
     (after,publishes,others)=if name=="many" then List.foldl step (before,0,0) (List.range 1 100) else
       let (next,effects)=C.update event before
       in (next,countPublish effects,List.length effects-countPublish effects)
     expectedOwner=if name=="stable" then Nothing else if name=="owner2" then owner "2" else owner "1"
 in ((),outgoing (E.object [("sameSurface",E.bool (identity (C.frame before)==identity (C.frame after))),("stateChanged",E.bool (C.desktop before/=C.desktop after)),("ownerCorrect",E.bool ((C.desktop after).ownerScope==expectedOwner)),("publishes",E.int publishes),("otherEffects",E.int others),("before",C.frame before),("after",C.frame after)]))}
