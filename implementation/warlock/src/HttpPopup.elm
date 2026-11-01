module HttpPopup exposing (main)

import Browser
import Browser.Dom
import Html exposing (div, input, label, text)
import Html.Attributes exposing (attribute, for, id, readonly, type_, value)
import Json.Decode as D
import Popup
import Presentation
import SurfaceRenderer
import Task
import UiHttp

type alias Model = {popup : Popup.Model,http : UiHttp.Model}
type Msg = View Popup.Msg | Transport UiHttp.Msg | Focused

-- No native preview producer is qualified for this HTTP profile. Empty
-- descriptions are inert; a real command remains unconfirmed and fails closed.
supported : Popup.Effect -> Bool
supported effect =
    case effect of
        Popup.Dispatch _ -> True
        Popup.PreviewCommand raw -> D.decodeValue (D.list D.value) raw |> Result.map List.isEmpty |> Result.withDefault False
        Popup.PaintRequest raw -> D.decodeValue (D.list D.value) raw |> Result.map List.isEmpty |> Result.withDefault False

update : Msg -> Model -> (Model,Cmd Msg)
update message model =
    case message of
        Focused -> (model,Cmd.none)
        View value ->
            let (popup,descriptions)=Popup.transition value model.popup
                next={model | popup=popup}
            in if not (List.all supported descriptions) then
                let (stopped,cancel,_)=UiHttp.stop "Native previews are unavailable in this HTTP profile. No preview command was sent." next.http
                in ({next | http=stopped},Cmd.map Transport cancel)
            else
                let step description (current,queuedCommands) =
                        case description of
                            Popup.Dispatch wire ->
                                let (http,command,_)=UiHttp.enqueue wire current.http
                                in ({current | http=http},Cmd.map Transport command::queuedCommands)
                            _ -> (current,queuedCommands)
                    (result,foldedCommands)=List.foldl step (next,[]) descriptions
                in (result,Cmd.batch (List.reverse foldedCommands))
        Transport value ->
            let (http,command,event)=UiHttp.update value model.http
                current={model | http=http}
            in case event of
                Just (UiHttp.Incoming raw) ->
                    case UiHttp.gateway raw of
                        Just ("presentation",payload) -> apply (Popup.Present payload) command current
                        Just ("announcements",payload) -> apply (Popup.Announce payload) command current
                        Just ("focus",payload) ->
                            let target=if current.popup.composition==Popup.Idle then Presentation.focusTarget True payload current.popup.presentation else Nothing
                                focus=
                                    case (Presentation.current current.popup.presentation,target) of
                                        (Just snapshot,Just domId) -> Browser.Dom.focus (SurfaceRenderer.controlDomId snapshot domId) |> Task.attempt (\_ -> Focused)
                                        _ -> Cmd.none
                            in (current,Cmd.batch [Cmd.map Transport command,focus])
                        _ ->
                            let (stopped,cancel,_)=UiHttp.stop "Unexpected popup event." http
                            in ({current | http=stopped},Cmd.map Transport cancel)
                _ -> (current,Cmd.map Transport command)

apply : Popup.Msg -> Cmd UiHttp.Msg -> Model -> (Model,Cmd Msg)
apply message command model =
    let (next,emitted)=update (View message) model
    in (next,Cmd.batch [Cmd.map Transport command,emitted])

retainedField : Popup.Model -> List (Html.Html Msg)
retainedField popup =
    case Presentation.current popup.presentation of
        Just snapshot ->
            if List.member (SurfaceRenderer.mode snapshot) ["applications","files"] then
                let fieldId = SurfaceRenderer.fieldIdentity snapshot
                    noun = if SurfaceRenderer.mode snapshot=="files" then "folder path" else "search query"
                    renderField stateTag fieldLabel retained =
                        [ label [for "http-popup-retained-query"] [text fieldLabel]
                        , input [id "http-popup-retained-query",type_ "text",readonly True,value retained,attribute "aria-readonly" "true",attribute "aria-label" fieldLabel,attribute "data-retained-surface-field" fieldId,attribute "data-retained-query-state" stateTag] []
                        ]
                in case (popup.pendingQuery,SurfaceRenderer.queryValue snapshot) of
                    (Just draft,_) ->
                        renderField "unconfirmed-draft" ("Unconfirmed draft " ++ noun ++ " (read-only; not confirmed by desktop)") draft
                    (Nothing,Just confirmed) ->
                        renderField "confirmed" ("Last confirmed " ++ noun ++ " (read-only)") confirmed
                    (Nothing,Nothing) ->
                        []
            else []
        Nothing -> []

view : Model -> Html.Html Msg
view model =
    case UiHttp.problem model.http of
        Nothing -> Html.map View (Popup.view model.popup)
        Just reason ->
            let alert = div [attribute "role" "alert"] [text (reason++" Restart this view to reconnect.")]
            in case retainedField model.popup of
                [] -> alert
                retained -> div [attribute "data-transport-stopped" "true"] (alert :: retained)

main : Program () Model Msg
main = Browser.element
    {init=\_ -> let (http,command)=UiHttp.renderer in ({popup=Popup.initial,http=http},Cmd.map Transport command)
    ,update=update,view=view,subscriptions=\_ -> Sub.none}
