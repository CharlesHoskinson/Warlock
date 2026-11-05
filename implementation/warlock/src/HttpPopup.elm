module HttpPopup exposing (main)

import Browser
import Browser.Dom
import Html exposing (div, input, label, text)
import Html.Attributes exposing (attribute, for, id, readonly, type_, value)
import Json.Decode as D
import NativePreviewRealm as Realm
import Popup
import Presentation
import SurfaceRenderer
import SurfaceTheme
import Task
import UiHttp

type alias Model = {popup : Popup.Model,http : UiHttp.Model}
type Msg = View Popup.Msg | Transport UiHttp.Msg | Focused

-- Native control facts use the existing realm policy. No native preview
-- producer is qualified for this HTTP profile; nonempty proposals and paint
-- requests remain explicit, unconfirmed refusals until their transport exists.
emptyPreview : D.Value -> Bool
emptyPreview raw =
    let realm = D.keyValuePairs D.value |> D.andThen (\pairs ->
            if List.sort (List.map Tuple.first pairs)==["binding","entries","kind","previewProtocol","receiverEpoch"] then
                D.map4 (\protocol kind _ entries -> protocol==3 && kind=="preview-proposals" && List.isEmpty entries)
                    (D.field "previewProtocol" D.int) (D.field "kind" D.string) Realm.domainDecoder (D.field "entries" (D.list D.value))
            else D.fail "Exact empty native proposal fields")
    in case D.decodeValue (D.list D.value) raw of
        Ok entries -> List.isEmpty entries
        Err _ -> D.decodeValue realm raw |> Result.withDefault False

supported : Popup.Effect -> Bool
supported effect =
    case effect of
        Popup.Dispatch _ -> True
        Popup.PreviewCommand raw -> emptyPreview raw
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
                        Just ("native-preview-grant",payload) ->
                            control ["binding","receiverEpoch","capacity"] Realm.grantDecoder Popup.NativeGrant payload command current
                        Just ("native-preview-quarantine",payload) ->
                            control ["binding","receiverEpoch"] Realm.domainDecoder Popup.NativeQuarantine payload command current
                        Just ("native-preview-closed",payload) ->
                            control ["binding","receiverEpoch"] Realm.domainDecoder Popup.NativeClosed payload command current
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

-- HTTP delivery is transport evidence only. Reuse the existing Popup realm
-- transitions for enrollment, stale-domain refusal and retirement. These
-- controls stay reachable while the presentation is closed.
control : List String -> D.Decoder a -> (D.Value -> Popup.Msg) -> D.Value -> Cmd UiHttp.Msg -> Model -> (Model,Cmd Msg)
control fields decoder message payload command model =
    let exact = D.keyValuePairs D.value |> D.andThen (\pairs ->
            if List.sort (List.map Tuple.first pairs)==List.sort fields then decoder
            else D.fail "Exact native preview control fields")
    in case D.decodeValue exact payload of
        Ok _ -> apply (message payload) command model
        Err _ ->
            let (http,cancel,_)=UiHttp.stop "Invalid native preview control." model.http
            in ({model | http=http},Cmd.map Transport cancel)

retainedField : Popup.Model -> List (Html.Html Msg)
retainedField popup =
    case Presentation.current popup.presentation of
        Just snapshot ->
            if List.member (SurfaceRenderer.mode snapshot) ["applications","files"] then
                let fieldId = SurfaceRenderer.fieldIdentity snapshot
                    noun = if SurfaceRenderer.mode snapshot=="files" then "folder path" else "search query"
                    renderField stateTag fieldLabel retained =
                        [ label (for "http-popup-retained-query" :: SurfaceTheme.retainedQueryLabelStyles) [text fieldLabel]
                        , input ([id "http-popup-retained-query",type_ "text",readonly True,value retained,attribute "aria-readonly" "true",attribute "aria-label" fieldLabel,attribute "data-retained-surface-field" fieldId,attribute "data-retained-query-state" stateTag] ++ SurfaceTheme.retainedQueryInputStyles) []
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
            let alert = div (attribute "role" "alert" :: SurfaceTheme.transportAlertStyles True) [text (reason++" This view has stopped.")]
            in case retainedField model.popup of
                [] -> alert
                retained -> div (attribute "data-transport-stopped" "true" :: SurfaceTheme.transportStoppedRootStyles) (alert :: retained)

main : Program () Model Msg
main = Browser.element
    {init=\_ -> let (http,command)=UiHttp.renderer in ({popup=Popup.initial,http=http},Cmd.map Transport command)
    ,update=update,view=view,subscriptions=\_ -> Sub.none}
