port module Probe exposing (main)
import Desktop
import Shell
import TaskbarShell
import SurfaceController as Controller
import Json.Decode as D
import Json.Encode as E
import Platform
import UInt64
port incoming : (D.Value -> msg) -> Sub msg
port outgoing : E.Value -> Cmd msg
type Msg = Run D.Value
main : Program () () Msg
main = Platform.worker {init=\_ -> ((),Cmd.none),subscriptions=\_ -> incoming Run,update=\(Run raw) _ ->
    let events=D.decodeValue (D.list D.value) raw |> Result.withDefault []
        (_,rows)=List.foldl apply (Controller.initial,[]) events
    in ((),outgoing (E.list identity (List.reverse rows)))}
apply raw (model,rows) =
    let current=Controller.desktop model
        kind=D.decodeValue (D.field "kind" D.string) raw |> Result.withDefault ""
        value name=D.decodeValue (D.field name D.value) raw |> Result.withDefault E.null
        event=case kind of
            "native" -> Just (Controller.Interaction (Desktop.Incoming (value "frame")))
            "primary" -> Shell.capture current.windows.shell |> Maybe.map (\scope -> Controller.Interaction (Desktop.Window (TaskbarShell.Primary scope "application:GTK Application")))
            "choose" -> case (current.windows.picker,D.decodeValue (D.field "root" UInt64.decoder) raw |> Result.toMaybe) of
                (Just picker,Just root) -> Just (Controller.Interaction (Desktop.Window (TaskbarShell.Choose picker.scope picker.generation root)))
                _ -> Nothing
            "close" -> current.windows.picker |> Maybe.map (\p -> Controller.Interaction (Desktop.Window (TaskbarShell.Close p.scope p.generation)))
            "deadline" -> Desktop.choiceToken current |> Maybe.map (Desktop.ChoiceDeadline >> Controller.Interaction)
            _ -> Nothing
        (next,effects)=event |> Maybe.map (\e -> Controller.update e model) |> Maybe.withDefault (model,[])
        desktop=Controller.desktop next
        shell=desktop.windows.shell
        wires=List.filterMap (\effect -> case effect of
            Controller.DesktopEffect (Desktop.WindowEffect (Shell.Send wire)) -> Just wire
            Controller.DesktopEffect (Desktop.Send wire) -> Just wire
            _ -> Nothing) effects
        focus=List.filterMap (\effect -> case effect of
            Controller.DesktopEffect (Desktop.Focus target) -> Just target
            _ -> Nothing) effects
        counter value_=value_ |> Maybe.map (UInt64.string >> E.string) |> Maybe.withDefault E.null
        row=E.object [("kind",E.string kind),("available",E.bool (Shell.available shell)),("pendingChoice",E.bool (Desktop.choiceToken desktop/=Nothing)),("returnFocus",E.bool (desktop.returnFocus/=Nothing)),("choiceNotice",E.string desktop.choiceNotice),("expected",counter shell.expected),("geometryExpected",counter shell.geometryExpected),("geometryRequest",counter (shell.geometry |> Maybe.map .request)),("geometrySequence",counter (shell.geometry |> Maybe.map .sequence)),("picker",E.bool (desktop.windows.picker/=Nothing)),("requests",E.list identity wires),("focus",E.list E.string focus),("frame",Controller.frame next),("shell",Shell.encode shell)]
    in (next,row::rows)
