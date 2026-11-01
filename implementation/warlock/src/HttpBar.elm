module HttpBar exposing (main)

import Bar
import Browser
import Browser.Dom
import Html exposing (div, text)
import Html.Attributes exposing (attribute)
import Presentation
import SurfaceRenderer
import Task
import UiHttp

type alias Model = {bar : Bar.Model,http : UiHttp.Model}
type Msg = View Bar.Msg | Transport UiHttp.Msg | Focused

update : Msg -> Model -> (Model,Cmd Msg)
update message model =
    case message of
        Focused -> (model,Cmd.none)
        View value ->
            let (bar,effects)=Bar.step value model.bar
                next={model | bar=bar}
                applyEffect effect (current,queued) =
                    case effect of
                        Bar.Dispatch wire ->
                            let (http,command,_)=UiHttp.enqueue wire current.http
                            in ({current | http=http},Cmd.map Transport command::queued)
                        Bar.ResetStatusViewport _ _ ->
                            (current,(Bar.localEffect View effect |> Maybe.withDefault Cmd.none)::queued)
                (result,foldedCommands)=List.foldl applyEffect (next,[]) effects
            in (result,Cmd.batch (List.reverse foldedCommands))
        Transport value ->
            let (http,command,event)=UiHttp.update value model.http
                current={model | http=http}
            in case event of
                Just (UiHttp.Incoming raw) ->
                    case UiHttp.gateway raw of
                        Just ("presentation",payload) -> apply (Bar.Present payload) command current
                        Just ("announcements",payload) -> apply (Bar.Announce payload) command current
                        Just ("focus",payload) ->
                            let focus =
                                    case (Presentation.current current.bar.presentation,Presentation.focusTarget False payload current.bar.presentation) of
                                        (Just snapshot,Just target) -> Browser.Dom.focus (SurfaceRenderer.controlDomId snapshot target) |> Task.attempt (\_ -> Focused)
                                        _ -> Cmd.none
                            in (current,Cmd.batch [Cmd.map Transport command,focus])
                        _ ->
                            let (stopped,cancel,_)=UiHttp.stop "Unexpected bar event." http
                            in ({current | http=stopped},Cmd.map Transport cancel)
                _ -> (current,Cmd.map Transport command)

apply : Bar.Msg -> Cmd UiHttp.Msg -> Model -> (Model,Cmd Msg)
apply message command model =
    let (next,emitted)=update (View message) model
    in (next,Cmd.batch [Cmd.map Transport command,emitted])

view : Model -> Html.Html Msg
view model =
    case UiHttp.problem model.http of
        Nothing -> Html.map View (Bar.view model.bar)
        Just reason -> div [attribute "role" "alert"] [text (reason++" Restart this view to reconnect.")]

main : Program () Model Msg
main = Browser.element
    {init=\_ -> let (http,command)=UiHttp.renderer in ({bar=Bar.initial,http=http},Cmd.map Transport command)
    ,update=update,view=view,subscriptions=\_ -> Sub.none}
