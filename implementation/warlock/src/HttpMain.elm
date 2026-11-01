module HttpMain exposing (main)

import Browser
import DesktopPolicy as Policy
import Html exposing (text)
import Process
import Task
import UiHttp

type alias Model = {policy : Policy.Model,http : UiHttp.Model}
type Msg = PolicyMessage Policy.Msg | Transport UiHttp.Msg

-- A lost delivery changes knowledge through the same policy reducer. It does
-- not rebind, retry a mutation or turn an HTTP response into a native receipt.
lost : Model -> Model
lost model =
    let (policy,_)=Policy.update Policy.TransportLost model.policy
    in {model | policy=policy}

effects : List Policy.Effect -> Model -> (Model,Cmd Msg)
effects descriptions initialModel =
    let step description (model,queuedCommands) =
            case description of
                Policy.Publish packet ->
                    let (http,command,event)=UiHttp.enqueue packet model.http
                        next={model | http=http}
                        observed=case event of
                            Just (UiHttp.Lost _) -> lost next
                            _ -> next
                    in (observed,Cmd.map Transport command::queuedCommands)
                Policy.Delay duration message ->
                    (model,(Process.sleep duration |> Task.perform (\_ -> PolicyMessage (Policy.Deadline message)))::queuedCommands)
        (foldedModel,foldedCommands)=List.foldl step (initialModel,[]) descriptions
    in (foldedModel,Cmd.batch (List.reverse foldedCommands))

update : Msg -> Model -> (Model,Cmd Msg)
update message model =
    case message of
        PolicyMessage value ->
            let (policy,descriptions)=Policy.update value model.policy
            in effects descriptions {model | policy=policy}
        Transport value ->
            let (http,command,event)=UiHttp.update value model.http
                current={model | http=http}
            in case event of
                Nothing -> (current,Cmd.map Transport command)
                Just (UiHttp.Lost _) -> (lost current,Cmd.map Transport command)
                Just (UiHttp.Incoming raw) ->
                    let (next,emitted)=update (PolicyMessage (Policy.Incoming raw)) current
                    in (next,Cmd.batch [Cmd.map Transport command,emitted])

main : Program () Model Msg
main = Browser.element
    {init=\_ -> let (http,command)=UiHttp.controller in ({policy=Policy.initial,http=http},Cmd.map Transport command)
    ,update=update,view=\_ -> text "",subscriptions=\_ -> Sub.none}
