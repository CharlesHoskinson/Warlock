port module AttentionReplay exposing (main)
import ActionProjection as Scene
import Binding
import Desktop
import Effects
import Json.Decode as D
import Json.Encode as E
import Platform
import Shell
import Surface
import SurfaceRenderer
import Taskbar
import UInt64
port outgoing : E.Value -> Cmd msg
counter value=D.decodeValue UInt64.decoder (E.string value) |> Result.withDefault UInt64.zero
one=counter "1"
context={lifetime=one,epoch=one,output=one,revision=one}
bound=E.object [("lifetime",E.string "1"),("session",E.string "1"),("frontend",E.string "1")]
window id name owner minimized attention=E.object [("incarnation",E.string id),("label",E.string name),("application",E.string name),("owner",owner),("minimized",E.bool minimized),("available",E.bool True),("attention",E.bool attention)]
raw revision focus inputRows=E.object [("revision",E.string revision),("focused",focus),("windows",E.list identity inputRows)]
rows requested=[window "1" "Active Window" E.null False False,window "2" "Attention Window" E.null False requested]
base requested focus=
 let initial=Desktop.initial
     windows=initial.windows
     shell=windows.shell
     effects=shell.effects
     scene=Scene.decode (raw "1" focus (rows requested)) |> Result.toMaybe
 in {initial | windows={windows | shell={shell | binding=D.decodeValue Binding.decoder bound |> Result.toMaybe,phase=Shell.Ready,effects={effects | connected=True,observed=scene |> Maybe.map (\s -> {context=context,scene=s})}}}}
result=
 let current=base True (E.string "1")
     ordinary=base False (E.string "1")
     active=base True (E.string "2")
     group name model=Surface.packet one one model |> D.decodeValue (D.field "bar" (D.list (D.map3 (\label ariaLabel detail -> {label=label,ariaLabel=ariaLabel,detail=detail}) (D.field "label" D.string) (D.field "ariaLabel" D.string) (D.field "detail" D.string)))) |> Result.withDefault [] |> List.filter (\c -> c.label==name) |> List.head
     nativeScene=Scene.decode (raw "1" (E.string "1") (rows True))
     legacy=rows False |> List.map (\value -> D.decodeValue (D.keyValuePairs D.value) value |> Result.withDefault [] |> List.filter (Tuple.first >> (/=) "attention") |> E.object)
     malformed=rows True |> List.map (\value -> D.decodeValue (D.keyValuePairs D.value) value |> Result.withDefault [] |> List.map (\(key,v) -> (key,if key=="attention" then E.int 1 else v)) |> E.object)
     effects=current.windows.shell.effects
     (stale,_,failure)=Effects.apply (E.object [("kind",E.string "snapshot"),("context",E.object [("lifetime",E.string "1"),("epoch",E.string "1"),("output",E.string "1"),("revision",E.string "1")]),("scene",raw "1" (E.string "1") (rows False))]) effects
     family=Scene.decode (raw "1" E.null [window "1" "Parent" E.null False False,window "2" "Child" (E.string "1") False True]) |> Result.map Taskbar.groups |> Result.withDefault []
     check name yes=(name,E.bool yes)
     checks=[check "NativeAttentionDecoded" (nativeScene |> Result.map (Scene.windows >> List.any .attention) |> Result.withDefault False)
       ,check "LegacyObservationDefaultsToNoAttention" (Scene.decode (raw "1" (E.string "1") legacy) |> Result.map (Scene.windows >> List.all (.attention >> not)) |> Result.withDefault False)
       ,check "NonBooleanAttentionRefused" (Scene.decode (raw "1" (E.string "1") malformed) |> Result.toMaybe |> (==) Nothing)
       ,check "OriginalAttentionDistinctFromActive" (Maybe.map .detail (group "Attention Window" current)==Just "Attention; Open" && Maybe.map .detail (group "Active Window" current)==Just "Active")
       ,check "AttentionAccessibleStateIsNamed" (group "Attention Window" current |> Maybe.map (\c -> String.contains "Attention" c.ariaLabel) |> Maybe.withDefault False)
       ,check "ActiveAccessibleStateIsNamed" (group "Active Window" current |> Maybe.map (\c -> String.contains "Active" c.ariaLabel) |> Maybe.withDefault False)
       ,check "AttentionClearsOnlyWithObservation" (Maybe.map .detail (group "Attention Window" ordinary)==Just "Open")
       ,check "ActiveIndicatorWinsOverAttention" (Maybe.map .detail (group "Attention Window" active)==Just "Active")
       ,check "ModalAttentionAggregatesOnce" (List.length family==1 && (family |> List.concatMap .families |> List.head |> Maybe.map .attention)==Just True)
       ,check "ContradictorySameRevisionCannotClearAttention" (stale==effects && failure/=Nothing)
       ,check "SameStateIncludesAttention" ((Maybe.map2 (\a b -> Scene.sameState a.scene b.scene) effects.observed ordinary.windows.shell.effects.observed)==Just False)
       ,check "ActualSurfaceRendererAcceptsAttentionFrame" (SurfaceRenderer.decode (Surface.packet one one current) |> Result.map (\_ -> True) |> Result.withDefault False)]
 in E.object [("checks",E.object checks),("frame",Surface.packet one one current),("clearFrame",Surface.packet (counter "2") one ordinary),("activeFrame",Surface.packet (counter "3") one active)]
main=Platform.worker {init=\() -> ((),outgoing result),update=\_ state -> (state,Cmd.none),subscriptions=\_ -> Sub.none}
