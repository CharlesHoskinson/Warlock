port module OutputSurfaceReplay exposing (main)

import Desktop
import Shell
import Json.Decode as D
import Json.Encode as E
import SurfaceController as Controller
import SurfaceRenderer
import UInt64
import Platform

port incoming : (D.Value -> msg) -> Sub msg
port outgoing : E.Value -> Cmd msg
type Msg = Run D.Value

main : Program () () Msg
main = Platform.worker {init=\_ -> ((),Cmd.none),subscriptions=\_ -> incoming Run,update=\(Run raw) _ ->
    let events = D.decodeValue (D.list D.value) raw |> Result.withDefault []
        (_,rows,_) = List.foldl apply (Controller.initial,[],Nothing) events
    in ((),outgoing (E.list identity (List.reverse rows)))}

apply : D.Value -> (Controller.Model,List E.Value,Maybe Desktop.ChoiceToken) -> (Controller.Model,List E.Value,Maybe Desktop.ChoiceToken)
apply raw (model,rows,saved) =
    let
        value name = D.decodeValue (D.field name D.value) raw |> Result.withDefault E.null
        kind = D.decodeValue (D.field "kind" D.string) raw |> Result.withDefault ""
        event = case kind of
            "saved-deadline" -> saved |> Maybe.map (Desktop.ChoiceDeadline >> Controller.Interaction)
            "choice-deadline" -> Desktop.choiceToken (Controller.desktop model) |> Maybe.map (Desktop.ChoiceDeadline >> Controller.Interaction)
            "native" -> Just (Controller.Interaction (Desktop.Incoming (value "frame")))
            "action" -> Just (Controller.Renderer (value "action"))
            "dismiss" -> D.decodeValue (D.field "lease" UInt64.decoder) raw |> Result.toMaybe |> Maybe.map Controller.NativeDismiss
            "open" -> Desktop.capture (Controller.desktop model) |> Maybe.map (Desktop.OpenApplications >> Controller.Interaction)
            _ -> Nothing
        (next,effects) = event |> Maybe.map (\message -> Controller.update message model) |> Maybe.withDefault (model,[])
        wires = List.filterMap (\effect -> case effect of
            Controller.DesktopEffect (Desktop.Send wire) -> Just wire
            Controller.DesktopEffect (Desktop.WindowEffect (Shell.Send wire)) -> Just wire
            Controller.DesktopEffect (Desktop.WindowEffect Shell.RestartBackend) -> Just (E.object [("protocolVersion",E.int 3),("kind",E.string "host-reconnect")])
            _ -> Nothing) effects
        packet = Controller.frame next
        valid = SurfaceRenderer.decode (if kind=="validate" then value "frame" else packet) |> Result.map (\_ -> True) |> Result.withDefault False
        order = List.map (\effect -> case effect of
            Controller.Publish _ -> "publish"
            Controller.DesktopEffect (Desktop.Send _) -> "send"
            _ -> "local") effects
        focus = List.filterMap (\effect -> case effect of
            Controller.DesktopEffect (Desktop.Focus target) -> Just target
            _ -> Nothing) effects
        row = E.object [("focus",E.list E.string focus),("order",E.list E.string order),("frame",packet),("rendererAdmitted",E.bool valid),("requests",E.list identity wires)]
    in (next,row::rows,if kind=="save-deadline" then Desktop.choiceToken (Controller.desktop model) else saved)
