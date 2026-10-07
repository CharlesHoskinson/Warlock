port module TaskbarReplay exposing (main)
import ActionProjection
import Effects
import Json.Decode as D
import Json.Encode as E
import Platform
import Taskbar
import UInt64
port incoming : (D.Value -> msg) -> Sub msg
port outgoing : E.Value -> Cmd msg
type Msg = Run D.Value
decision value = case value of
    Taskbar.Launch -> E.object [("kind",E.string "launch")]
    Taskbar.Picker -> E.object [("kind",E.string "picker")]
    Taskbar.Apply operation root -> E.object [("kind",E.string "effect"),("operation",E.string (Effects.operationName operation)),("root",E.string (UInt64.string root))]
    Taskbar.Unavailable -> E.object [("kind",E.string "unavailable")]
main : Program () () Msg
main = Platform.worker { init=\_ -> ((),Cmd.none), subscriptions=\_ -> incoming Run, update=\(Run value) _ ->
    let result = D.decodeValue (D.field "scene" D.value) value |> Result.mapError D.errorToString |> Result.andThen ActionProjection.decode
        resultValue = case result of
            Err error -> E.object [("passed",E.bool False),("error",E.string error)]
            Ok scene ->
                let pinned=D.decodeValue (D.field "pinned" D.bool) value |> Result.withDefault False
                    groupValues=Taskbar.groups scene |> List.map (\g -> E.object [("key",E.string g.key),("primary",decision (Taskbar.primary pinned g.families)),("selections",E.list (Taskbar.selection >> decision) g.families)])
                in E.object [("passed",E.bool True),("groups",Taskbar.encode scene),("decisions",E.list identity groupValues),("zero",decision (Taskbar.primary pinned [])),("canonicalScene",E.bool False)]
    in ((),outgoing resultValue) }
