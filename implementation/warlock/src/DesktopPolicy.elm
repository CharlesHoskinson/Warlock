module DesktopPolicy exposing (Model, Msg(..), Effect(..), initial, update)

import Desktop
import Json.Decode as D
import Json.Encode as E
import Shell
import SurfaceController as Controller
import TaskbarShell
import OutputController as Outputs

type alias Model = {controller : Outputs.Model}

type Msg = Incoming D.Value | Deadline Desktop.Msg | TransportLost

type Effect = Publish E.Value | Delay Float Desktop.Msg

initial : Model
initial = {controller=Outputs.initial}

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

effectsFor : Maybe E.Value -> List Controller.Effect -> List Effect
effectsFor packet effects =
    let timers = List.filterMap (\effect -> case effect of
            Controller.DesktopEffect (Desktop.WindowEffect (Shell.ArmPrepared token)) -> Just (Delay 2000 (Desktop.Window (TaskbarShell.ExpirePrepared token)))
            Controller.DesktopEffect (Desktop.ArmWorkspaceNavigation intent) -> Just (Delay 2000 (Desktop.WorkspaceNavigationDeadline intent))
            Controller.DesktopEffect (Desktop.ArmChoice token) -> Just (Delay 2000 (Desktop.ChoiceDeadline token))
            Controller.DesktopEffect (Desktop.Arm token) -> Just (Delay 10000 (Desktop.Deadline token))
            _ -> Nothing) effects
    in (packet |> Maybe.map (Publish >> List.singleton) |> Maybe.withDefault [])++timers

update : Msg -> Model -> (Model,List Effect)
update message model =
    let event = case message of
            Incoming raw -> incomingEvent raw
            Deadline value -> Just (Outputs.Interaction value)
            TransportLost -> Just (Outputs.Interaction (Desktop.Incoming (E.object [("protocolVersion",E.int 3),("kind",E.string "host-disconnected")])))
    in case event of
        Nothing -> (model,[])
        Just value ->
            let (updated,effects) = Outputs.update value model.controller
                (next,packet) = Outputs.register effects updated
            in ({model | controller=next},effectsFor packet effects)

