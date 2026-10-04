port module Main exposing (main)

import Browser
import Desktop
import Inspection
import Html exposing (text)
import Json.Decode as D
import Json.Encode as E
import Process
import Shell
import SurfaceController as Controller
import SurfaceRenderer
import Task
import OutputController as Outputs
import UInt64

port nativeViews : (D.Value -> msg) -> Sub msg
port nativeEvents : (D.Value -> msg) -> Sub msg
port rendererActions : (D.Value -> msg) -> Sub msg
port nativeReflows : (D.Value -> msg) -> Sub msg
port nativeDismissals : (D.Value -> msg) -> Sub msg
port inspections : E.Value -> Cmd msg

port surfaceCommits : E.Value -> Cmd msg

type alias Model = {controller : Outputs.Model, qa : Bool}

type Msg = Native D.Value | Action D.Value | Dismiss D.Value | Reflow D.Value | Topology D.Value | Deadline Desktop.Msg

commit : Outputs.Model -> List Controller.Effect -> Cmd Msg
commit model effects =
    let
        requests = List.filterMap (\effect -> case effect of
            Controller.DesktopEffect (Desktop.Send wire) -> Just wire
            Controller.DesktopEffect (Desktop.WindowEffect (Shell.Send wire)) -> Just wire
            Controller.DesktopEffect (Desktop.WindowEffect Shell.RestartBackend) -> Just (E.object [("protocolVersion",E.int 3),("kind",E.string "host-reconnect")])
            _ -> Nothing) effects
        focus = List.filterMap (\effect -> case effect of
            Controller.DesktopEffect (Desktop.Focus target) -> Just (E.string target)
            _ -> Nothing) effects
        timers = List.filterMap (\effect -> case effect of
            Controller.DesktopEffect (Desktop.ArmChoice token) -> Just (Process.sleep 2000 |> Task.perform (\_ -> Deadline (Desktop.ChoiceDeadline token)))
            Controller.DesktopEffect (Desktop.Arm token) -> Just (Process.sleep 10000 |> Task.perform (\_ -> Deadline (Desktop.Deadline token)))
            _ -> Nothing) effects
        atomic = if List.isEmpty effects then Cmd.none else surfaceCommits (E.object
            [("viewProtocol",E.int 1),("kind",E.string "view-commit"),("projection",Outputs.frame model),("requests",E.list identity requests),("focus",E.list identity focus)])
    in Cmd.batch (atomic :: timers)

update : Msg -> Model -> (Model,Cmd Msg)
update message model =
    let event = case message of
            Topology raw -> Just (Outputs.Topology raw)
            Native raw -> Just (Outputs.Interaction (Desktop.Incoming raw))
            Action raw -> Just (Outputs.Renderer raw)
            Deadline value -> Just (Outputs.Interaction value)
            Reflow raw -> Just (Outputs.Reflow raw)
            Dismiss raw -> Just (Outputs.Dismiss raw)
    in case event of
        Nothing -> (model,Cmd.none)
        Just value -> let (next,effects) = Outputs.update value model.controller in ({model | controller=next},Cmd.batch [commit next effects,if model.qa then inspections (Inspection.packet (Outputs.controller next)) else Cmd.none])

main : Program Bool Model Msg
main = Browser.element
    { init=\qa -> ({controller=Outputs.initial,qa=qa},Cmd.none)
    , update=update
    , view=\_ -> text ""
    , subscriptions=\_ -> Sub.batch [nativeViews Topology,nativeEvents Native,rendererActions Action,nativeDismissals Dismiss,nativeReflows Reflow]
    }
