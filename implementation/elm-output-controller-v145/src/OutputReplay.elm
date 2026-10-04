port module OutputReplay exposing (main)

import Desktop
import Json.Decode as D
import Json.Encode as E
import OutputController as Outputs
import Platform
import Shell
import SurfaceController as Controller

port incoming : (D.Value -> msg) -> Sub msg
port outgoing : E.Value -> Cmd msg

type Msg = Run D.Value

main : Program () () Msg
main = Platform.worker {init=\_ -> ((),Cmd.none),subscriptions=\_ -> incoming Run,update=\(Run raw) _ ->
    let events=D.decodeValue (D.list D.value) raw |> Result.withDefault []
        (_,rows)=List.foldl apply (Outputs.initial,[]) events
    in ((),outgoing (E.list identity (List.reverse rows)))}

apply : D.Value -> (Outputs.Model,List E.Value) -> (Outputs.Model,List E.Value)
apply raw (model,rows) =
    let value name=D.decodeValue (D.field name D.value) raw |> Result.withDefault E.null
        event=case D.decodeValue (D.field "kind" D.string) raw |> Result.withDefault "" of
            "topology" -> Just (Outputs.Topology (value "frame"))
            "native" -> Just (Outputs.Interaction (Desktop.Incoming (value "frame")))
            "action" -> Just (Outputs.Renderer (value "frame"))
            "dismiss" -> Just (Outputs.Dismiss (value "frame"))
            "reflow" -> Just (Outputs.Reflow (value "frame"))
            _ -> Nothing
        (next,effects)=event |> Maybe.map (\message -> Outputs.update message model) |> Maybe.withDefault (model,[])
        requests=List.filterMap (\effect -> case effect of
            Controller.DesktopEffect (Desktop.Send wire) -> Just wire
            Controller.DesktopEffect (Desktop.WindowEffect (Shell.Send wire)) -> Just wire
            Controller.DesktopEffect (Desktop.WindowEffect Shell.RestartBackend) -> Just (E.object [("protocolVersion",E.int 3),("kind",E.string "host-reconnect")])
            _ -> Nothing) effects
        focus=List.filterMap (\effect -> case effect of
            Controller.DesktopEffect (Desktop.Focus target) -> Just (E.string target)
            _ -> Nothing) effects
        row=E.object [("projection",Outputs.frame next),("requests",E.list identity requests),("focus",E.list identity focus),("effects",E.int (List.length effects))]
    in (next,row::rows)
