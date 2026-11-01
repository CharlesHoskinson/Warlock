port module Main exposing (main)

import Browser
import Desktop
import Html exposing (text)
import Json.Decode as D
import Json.Encode as E
import Process
import Shell
import SurfaceController as Controller
import Task
import TaskbarShell
import OutputController as Outputs
import UInt64

port incoming : (D.Value -> msg) -> Sub msg

port surfaceCommits : E.Value -> Cmd msg

type alias Model = {controller : Outputs.Model}

type Msg = Incoming D.Value | Deadline Desktop.Msg

-- The trusted Haskell UI owner supplies the source discriminator from its
-- actual transport/handler. Web actions cannot select a native/owner source.
-- Each payload still passes the existing domain decoder before mutation.
incomingEvent : D.Value -> Maybe Outputs.Event
incomingEvent raw =
    let
        version = D.field "bridgeProtocol" D.int |> D.andThen (\value -> if value==1 then D.succeed () else D.fail "Bridge protocol")
        decoder = D.keyValuePairs D.value |> D.andThen (\pairs ->
            if List.sort (List.map Tuple.first pairs)==["bridgeProtocol","kind","payload"] then
                D.map3 (\_ kind payload -> (kind,payload)) version (D.field "kind" D.string) (D.field "payload" D.value)
            else D.fail "Bridge fields")
    in
    case D.decodeValue decoder raw of
        Ok (kind,payload) ->
            case kind of
                "native-event" -> Just (Outputs.Interaction (Desktop.Incoming payload))
                "view-topology" -> Just (Outputs.Topology payload)
                "view-action" -> Just (Outputs.Renderer payload)
                "view-disposition" -> Just (Outputs.Disposition payload)
                "view-dismiss" -> Just (Outputs.Dismiss payload)
                "view-escape" -> Just (Outputs.Escape payload)
                "view-reflow" -> Just (Outputs.Reflow payload)
                _ -> Nothing
        Err _ -> Nothing

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
            Incoming raw -> incomingEvent raw
            Deadline value -> Just (Outputs.Interaction value)
    in case event of
        Nothing -> (model,Cmd.none)
        Just value ->
            let (updated,effects) = Outputs.update value model.controller
                (next,packet) = Outputs.register effects updated
            in ({model | controller=next},commit packet effects)

main : Program () Model Msg
main = Browser.element
    { init=\_ -> ({controller=Outputs.initial},Cmd.none)
    , update=update
    , view=\_ -> text ""
    , subscriptions=\_ -> incoming Incoming
    }
