module HttpPopup exposing (main)

import Browser
import Browser.Dom
import Html exposing (div, input, label, text)
import Html.Attributes exposing (attribute, for, id, readonly, type_, value)
import Html.Events
import Json.Decode as D
import Json.Encode as E
import NativePreviewRealm as Realm
import Popup
import Presentation
import SurfaceRenderer
import SurfaceSnapshot
import SurfaceTheme
import Task
import UiHttp
import UInt64

type alias Model = {popup : Popup.Model,http : UiHttp.Model}
type Msg = View Popup.Msg | Transport UiHttp.Msg | Focused | MenuTraverse D.Value

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

-- This boundary admits only the singleton reconciliation emitted by Popup.
reconcilePreview : D.Value -> Bool
reconcilePreview raw =
    let exact fields decoder = D.keyValuePairs D.value |> D.andThen (\pairs ->
            if List.sort (List.map Tuple.first pairs)==List.sort fields then decoder else D.fail "Exact fields")
        command = exact ["kind","binding"] (D.map2 Tuple.pair (D.field "kind" D.string) (D.field "binding" D.value))
        row = exact ["identity","commands"] (D.map2 Tuple.pair (D.field "identity" D.string) (D.field "commands" (D.list command)))
        proposal = exact ["previewProtocol","kind","binding","receiverEpoch","entries"]
            (D.map4 (\version kind domain rows -> {version=version,kind=kind,domain=domain,rows=rows})
                (D.field "previewProtocol" D.int) (D.field "kind" D.string) Realm.domainDecoder (D.field "entries" (D.list row)))
    in case D.decodeValue proposal raw of
        Ok {version,kind,domain,rows} ->
            case rows of
                [(identity,[(commandKind,binding)])] ->
                    version == 3 && kind == "preview-proposals" && commandKind == "reconcile" && identity == "binding:" ++ Realm.owner domain && E.encode 0 binding == E.encode 0 (Realm.bindingValue domain)
                _ -> False
        _ -> False

supported : Bool -> Popup.Effect -> Bool
supported allowReconcile effect =
    case effect of
        Popup.Dispatch _ -> True
        Popup.PreviewCommand raw -> emptyPreview raw || (allowReconcile && reconcilePreview raw)
        Popup.PaintRequest raw -> D.decodeValue (D.list D.value) raw |> Result.map List.isEmpty |> Result.withDefault False
        Popup.TicketConsumed _ -> True

update : Msg -> Model -> (Model,Cmd Msg)
update message model =
    case message of
        Focused -> (model,Cmd.none)
        MenuTraverse instruction ->
            let target =
                    if model.popup.composition==Popup.Idle && UiHttp.problem model.http==Nothing then
                        Presentation.focusTarget True instruction model.popup.presentation
                    else Nothing
            in case (Presentation.current model.popup.presentation,target) of
                (Just snapshot,Just domId) ->
                    if SurfaceRenderer.mode snapshot=="menu" then
                        (model,Browser.Dom.focus (SurfaceRenderer.controlDomId snapshot domId) |> Task.attempt (\_ -> Focused))
                    else (model,Cmd.none)
                _ -> (model,Cmd.none)
        View value -> viewTransition False value model
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
                        Just ("native-preview-issued",payload) -> apply (Popup.NativeIssued payload) command current
                        Just ("native-preview-retry",payload) ->
                            control ["binding","receiverEpoch"] Realm.domainDecoder Popup.NativeRetry payload command current
                        Just ("native-preview-retirement",payload) ->
                            control ["lifetime","session","frontend"] legacyBindingDecoder Popup.NativeRetirement payload command current
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
                Just (UiHttp.TransportConsumedCompleted ticket) -> apply (Popup.ConfirmationTransportCompleted ticket) command current
                _ -> flush current [Cmd.map Transport command]

-- Transport controls may route checked reconciliation proposals. Correlated
-- completions only retire their matching opaque confirmation tickets.
viewTransition : Bool -> Popup.Msg -> Model -> (Model,Cmd Msg)
viewTransition allowReconcile value model =
        let (popup,descriptions)=Popup.transition value model.popup
            next={model | popup=popup}
        in if not (List.all (supported allowReconcile) descriptions) then
            let (stopped,cancel,_)=UiHttp.stop "Native previews are unavailable in this HTTP profile. No preview command was sent." next.http
            in ({next | http=stopped},Cmd.map Transport cancel)
        else
            let step description (current,queuedCommands) =
                    case description of
                        Popup.Dispatch wire ->
                            let (http,command,_)=UiHttp.enqueue wire current.http
                            in ({current | http=http},Cmd.map Transport command::queuedCommands)
                        Popup.PreviewCommand wire ->
                            if emptyPreview wire then (current,queuedCommands) else
                                let (http,command,_)=UiHttp.enqueueProposal wire current.http
                                in ({current | http=http},Cmd.map Transport command::queuedCommands)
                        _ -> (current,queuedCommands)
                (result,foldedCommands)=List.foldl step (next,[]) descriptions
            in flush result (List.reverse foldedCommands)

flush : Model -> List (Cmd Msg) -> (Model,Cmd Msg)
flush model commands =
    let step tickets current queued =
            case tickets of
                [] -> (current,Cmd.batch queued)
                ticket::rest ->
                    let (http,command,result)=UiHttp.tryEnqueueConsumed ticket current.http
                        next={current | http=http}
                        nextCommands=queued ++ [Cmd.map Transport command]
                    in case result of
                        UiHttp.Queued -> step rest next nextCommands
                        UiHttp.AlreadyQueued -> step rest next nextCommands
                        UiHttp.Deferred -> (next,Cmd.batch nextCommands)
                        UiHttp.Stopped -> (next,Cmd.batch nextCommands)
    in step (Popup.pendingConfirmations model.popup) model commands

apply : Popup.Msg -> Cmd UiHttp.Msg -> Model -> (Model,Cmd Msg)
apply message command model =
    let (next,emitted)=viewTransition True message model
    in (next,Cmd.batch [Cmd.map Transport command,emitted])

-- HTTP delivery is transport evidence only. Reuse the existing Popup realm
-- transitions for enrollment, stale-domain refusal and retirement. These
-- controls stay reachable while the presentation is closed.
-- Legacy retirement uses the original raw positive binding, not a realm envelope.
legacyBindingDecoder : D.Decoder ()
legacyBindingDecoder =
    let positive = UInt64.decoder |> D.andThen (\n -> if n /= UInt64.zero then D.succeed () else D.fail "Positive binding")
    in D.map3 (\_ _ _ -> ()) (D.field "lifetime" positive) (D.field "session" positive) (D.field "frontend" positive)

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

-- Menu rows render in snapshot order as buttons. Other modes have distinct
-- grouping, fields and focus-only rules and do not use this traversal policy.
menuTabTarget : SurfaceRenderer.Snapshot -> Bool -> String -> Maybe E.Value
menuTabTarget snapshot backwards renderedId =
    let details = SurfaceSnapshot.details snapshot
        controls = List.filter .enabled details.popup
        count = List.length controls
        position = controls |> List.indexedMap Tuple.pair
            |> List.filter (\(_,menuControl) -> SurfaceRenderer.controlDomId snapshot menuControl.domId==renderedId)
            |> List.head |> Maybe.map Tuple.first
    in if details.mode/="menu" || count==0 then Nothing else
        position |> Maybe.andThen (\index ->
            let next = modBy count (index + (if backwards then count-1 else 1))
            in List.drop next controls |> List.head |> Maybe.map (\menuControl ->
                E.object
                    [("focusProtocol",E.int 1),("kind",E.string "focus"),("surface",E.string "popup")
                    ,("publication",E.string (UInt64.string details.publication))
                    ,("lease",E.string (UInt64.string details.lease)),("domId",E.string menuControl.domId)]))

menuTabDecoder : SurfaceRenderer.Snapshot -> D.Decoder (Msg,Bool)
menuTabDecoder snapshot =
    D.map8 (\key shift ctrl alt meta composing code target ->
        {key=key,shift=shift,ctrl=ctrl,alt=alt,meta=meta,composing=composing,code=code,target=target})
        (D.field "key" D.string) (D.field "shiftKey" D.bool)
        (D.field "ctrlKey" D.bool) (D.field "altKey" D.bool) (D.field "metaKey" D.bool)
        (D.field "isComposing" D.bool) (D.field "keyCode" D.int) (D.at ["target","id"] D.string)
        |> D.andThen (\event ->
            if event.key/="Tab" || event.ctrl || event.alt || event.meta || event.composing || event.code==229 then
                D.fail "Not a menu traversal key"
            else case menuTabTarget snapshot event.shift event.target of
                Just instruction -> D.succeed (MenuTraverse instruction,True)
                Nothing -> D.fail "No current menu traversal target")

-- The native owned Escape route is the single dismissal policy wire. Consume
-- only its current eligible menu DOM event so WebKit cannot replay an unhandled
-- key into a different renderer after the native close changes physical focus.
-- This handler emits no action, HTTP request, local dismissal or focus command.
menuEscapeDecoder : Popup.Model -> SurfaceRenderer.Snapshot -> D.Decoder { message : Msg, stopPropagation : Bool, preventDefault : Bool }
menuEscapeDecoder popupModel snapshot =
    D.map6 (\key modifiers composing code repeated target ->
        {key=key,modifiers=modifiers,composing=composing,code=code,repeated=repeated,target=target})
        (D.field "key" D.string)
        (D.map4 (\shift ctrl alt meta -> shift || ctrl || alt || meta)
            (D.field "shiftKey" D.bool) (D.field "ctrlKey" D.bool) (D.field "altKey" D.bool) (D.field "metaKey" D.bool))
        (D.field "isComposing" D.bool) (D.field "keyCode" D.int)
        (D.field "repeat" D.bool) (D.at ["target","id"] D.string)
        |> D.andThen (\event ->
            let details = SurfaceSnapshot.details snapshot
                closeControls = List.filter (\menuItem -> menuItem.identity=="control:menu-close" && menuItem.enabled) details.popup
                currentTargets = List.filter (\menuItem -> menuItem.enabled && SurfaceRenderer.controlDomId snapshot menuItem.domId==event.target) details.popup
            in if event.key/="Escape" || event.modifiers || event.composing || event.code==229 || event.repeated
                || popupModel.composition/=Popup.Idle || details.mode/="menu" || List.length closeControls/=1 then
                D.fail "Not an owned idle menu Escape"
            else case currentTargets of
                [menuItem] ->
                    let instruction = E.object
                            [("focusProtocol",E.int 1),("kind",E.string "focus"),("surface",E.string "popup")
                            ,("publication",E.string (UInt64.string details.publication))
                            ,("lease",E.string (UInt64.string details.lease)),("domId",E.string menuItem.domId)]
                    in case Presentation.focusTarget True instruction popupModel.presentation of
                        Just _ -> D.succeed {message=Focused,stopPropagation=True,preventDefault=True}
                        Nothing -> D.fail "Menu Escape scope is no longer current"
                _ -> D.fail "Menu Escape target is not uniquely eligible")

view : Model -> Html.Html Msg
view model =
    case UiHttp.problem model.http of
        Nothing ->
            let rendered = Html.map View (Popup.view model.popup)
            in case Presentation.current model.popup.presentation of
                Just snapshot ->
                    if SurfaceRenderer.mode snapshot=="menu" && model.popup.composition==Popup.Idle then
                        div [Html.Events.custom "keydown"
                            (D.field "key" D.string |> D.andThen (\key ->
                                if key=="Tab" then
                                    D.map (\(message,prevent) -> {message=message,stopPropagation=False,preventDefault=prevent}) (menuTabDecoder snapshot)
                                else
                                    menuEscapeDecoder model.popup snapshot))] [rendered]
                    else rendered
                Nothing -> rendered
        Just reason ->
            let alert = div (attribute "role" "alert" :: SurfaceTheme.transportAlertStyles True) [text (reason++" This view has stopped.")]
            in case retainedField model.popup of
                [] -> alert
                retained -> div (attribute "data-transport-stopped" "true" :: SurfaceTheme.transportStoppedRootStyles) (alert :: retained)

main : Program () Model Msg
main = Browser.element
    {init=\_ -> let (http,command)=UiHttp.popup in ({popup=Popup.initial,http=http},Cmd.map Transport command)
    ,update=update,view=view,subscriptions=\_ -> Sub.none}
