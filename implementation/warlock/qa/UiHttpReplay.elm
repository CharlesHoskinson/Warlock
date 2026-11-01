port module UiHttpReplay exposing (main)

{-| QA interpreter for the actual production transport and owning pure policy.
No request/result reducer, receipt authority or alternate policy is modeled here.
The JavaScript oracle controls XHR outcomes and checks actual generated commands.
-}

import DesktopPolicy as Policy
import Json.Decode as D
import Json.Encode as E
import OutputController as Outputs
import Platform
import Process
import Task
import UiHttp

port incoming : (D.Value -> msg) -> Sub msg
port outgoing : E.Value -> Cmd msg

type alias Flags = { renderer : Bool }
type alias Model = { http : UiHttp.Model, policy : Policy.Model, renderer : Bool }
type Msg = Control D.Value | Transport UiHttp.Msg | Deadline Policy.Msg

report : String -> Maybe UiHttp.Event -> Model -> Cmd Msg
report label event model =
    outgoing (E.object
        [ ("label",E.string label)
        , ("problem",UiHttp.problem model.http |> Maybe.map E.string |> Maybe.withDefault E.null)
        , ("pendingBatches",E.int (Outputs.pendingBatches model.policy.controller))
        , ("event",case event of
            Nothing -> E.null
            Just (UiHttp.Incoming raw) -> E.object [("kind",E.string "incoming"),("value",raw)]
            Just (UiHttp.Lost reason) -> E.object [("kind",E.string "lost"),("reason",E.string reason)])
        ])

policyEffects : List Policy.Effect -> Model -> (Model,List (Cmd Msg))
policyEffects descriptions initialModel =
    let
        step description (state,queued) =
            case description of
                Policy.Publish wire ->
                    let (http,command,_)=UiHttp.enqueue wire state.http
                    in ({state | http=http},Cmd.map Transport command::queued)
                Policy.Delay duration message ->
                    (state,(Process.sleep duration |> Task.perform (\_ -> Deadline (Policy.Deadline message)))::queued)
        (result,commands)=List.foldl step (initialModel,[]) descriptions
    in (result,List.reverse commands)

policy : Policy.Msg -> Model -> (Model,List (Cmd Msg))
policy message model =
    let (next,descriptions)=Policy.update message model.policy
    in policyEffects descriptions {model | policy=next}

update : Msg -> Model -> (Model,Cmd Msg)
update message model =
    case message of
        Control raw ->
            case D.decodeValue (D.field "kind" D.string) raw of
                Ok "enqueue" ->
                    case D.decodeValue (D.field "value" D.value) raw of
                        Err _ -> (model,report "invalid-control" Nothing model)
                        Ok value ->
                            let (http,command,event)=UiHttp.enqueue value model.http
                                next={model | http=http}
                            in (next,Cmd.batch [Cmd.map Transport command,report "enqueue" event next])
                Ok "stop" ->
                    let (http,command,event)=UiHttp.stop "Explicit fixture stop" model.http
                        next={model | http=http}
                    in (next,Cmd.batch [Cmd.map Transport command,report "stop" event next])
                Ok "policy" ->
                    case D.decodeValue (D.field "value" D.value) raw of
                        Err _ -> (model,report "invalid-control" Nothing model)
                        Ok value ->
                            let (next,commands)=policy (Policy.Incoming value) model
                            in (next,Cmd.batch (report "policy" Nothing next::commands))
                _ -> (model,report "invalid-control" Nothing model)
        Deadline value ->
            let (next,commands)=policy value model
            in (next,Cmd.batch (report "deadline" Nothing next::commands))
        Transport value ->
            let (http,command,event)=UiHttp.update value model.http
                current={model | http=http}
                (next,commands)=case event of
                    Just (UiHttp.Incoming raw) ->
                        if model.renderer then (current,[]) else policy (Policy.Incoming raw) current
                    Just (UiHttp.Lost _) -> policy Policy.TransportLost current
                    Nothing -> (current,[])
            in (next,Cmd.batch (Cmd.map Transport command::report "transport" event next::commands))

main : Program Flags Model Msg
main = Platform.worker
    { init=\flags ->
        let (http,command)=if flags.renderer then UiHttp.renderer else UiHttp.controller
        in ({http=http,policy=Policy.initial,renderer=flags.renderer},Cmd.map Transport command)
    , update=update
    , subscriptions=\_ -> incoming Control
    }
