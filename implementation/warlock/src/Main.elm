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
import TaskbarShell
import OutputController as Outputs
import UInt64

port nativeBatchDispositions : (D.Value -> msg) -> Sub msg
port nativeViews : (D.Value -> msg) -> Sub msg
port nativeEvents : (D.Value -> msg) -> Sub msg
port rendererActions : (D.Value -> msg) -> Sub msg
port nativeReflows : (D.Value -> msg) -> Sub msg
port nativeDismissals : (D.Value -> msg) -> Sub msg
port inspections : E.Value -> Cmd msg

port surfaceCommits : E.Value -> Cmd msg

type alias Model = {controller : Outputs.Model, qa : Bool}

type Msg = Disposition D.Value | Native D.Value | Action D.Value | Dismiss D.Value | Reflow D.Value | Topology D.Value | Deadline Desktop.Msg

commit : Maybe E.Value -> List Controller.Effect -> Cmd Msg
commit packet effects =
    let
        timers = List.filterMap (\effect -> case effect of
            Controller.DesktopEffect (Desktop.WindowEffect (Shell.ArmPrepared token)) -> Just (Process.sleep 2000 |> Task.perform (\_ -> Deadline (Desktop.Window (TaskbarShell.ExpirePrepared token))))
            Controller.DesktopEffect (Desktop.ArmWorkspaceNavigation intent) -> Just (Process.sleep 2000 |> Task.perform (\_ -> Deadline (Desktop.WorkspaceNavigationDeadline intent)))
            Controller.DesktopEffect (Desktop.ArmChoice token) -> Just (Process.sleep 2000 |> Task.perform (\_ -> Deadline (Desktop.ChoiceDeadline token)))
            Controller.DesktopEffect (Desktop.Arm token) -> Just (Process.sleep 10000 |> Task.perform (\_ -> Deadline (Desktop.Deadline token)))
            _ -> Nothing) effects
        atomic = packet |> Maybe.map surfaceCommits |> Maybe.withDefault Cmd.none
    in Cmd.batch (atomic :: timers)

update : Msg -> Model -> (Model,Cmd Msg)
update message model =
    let event = case message of
            Disposition raw -> Just (Outputs.Disposition raw)
            Topology raw -> Just (Outputs.Topology raw)
            Native raw -> Just (Outputs.Interaction (Desktop.Incoming raw))
            Action raw -> Just (Outputs.Renderer raw)
            Deadline value -> Just (Outputs.Interaction value)
            Reflow raw -> Just (Outputs.Reflow raw)
            Dismiss raw -> Just (Outputs.Dismiss raw)
    in case event of
        Nothing -> (model,Cmd.none)
        Just value ->
            let (updated,effects) = Outputs.update value model.controller
                (next,packet) = Outputs.register effects updated
            in ({model | controller=next},Cmd.batch [commit packet effects,if model.qa then inspections (Inspection.packet (Outputs.controller next)) else Cmd.none])

main : Program Bool Model Msg
main = Browser.element
    { init=\qa -> ({controller=Outputs.initial,qa=qa},Cmd.none)
    , update=update
    , view=\_ -> text ""
    , subscriptions=\_ -> Sub.batch [nativeBatchDispositions Disposition,nativeViews Topology,nativeEvents Native,rendererActions Action,nativeDismissals Dismiss,nativeReflows Reflow]
    }
