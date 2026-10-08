port module Popup exposing (main, Model, Msg(..), Composition(..), initial, update)

import Browser
import Html exposing (div, text)
import Html.Attributes exposing (attribute)
import Json.Decode as D
import Json.Encode as E
import RetainedPreviewPresenter as Preview
import NativePreviewRealm as Realm
import Presentation
import SurfaceRenderer
import UInt64

port presentation : (D.Value -> msg) -> Sub msg
port requestAction : (D.Value -> msg) -> Sub msg
port actions : E.Value -> Cmd msg

port nativePreviews : (D.Value -> msg) -> Sub msg
port previewCommands : E.Value -> Cmd msg
port nativePreviewGrants : (D.Value -> msg) -> Sub msg
port nativePreviewQuarantine : (D.Value -> msg) -> Sub msg
port nativePreviewClosed : (D.Value -> msg) -> Sub msg
port nativePreviewIssued : (D.Value -> msg) -> Sub msg
port nativePreviewRetry : (D.Value -> msg) -> Sub msg
port nativePreviewRetirement : (D.Value -> msg) -> Sub msg

type Msg = Present D.Value | Action E.Value | NativePreview D.Value | NativeGrant D.Value | NativeQuarantine D.Value | NativeClosed D.Value | NativeIssued D.Value | NativeRetry D.Value | NativeRetirement D.Value
type Composition = Idle | Preediting { baseline : String, before : Maybe String }
type alias Model = { presentation : Presentation.Model, previews : Preview.Model, pendingQuery : Maybe String, composition : Composition, lastQuery : Maybe (String, UInt64.Counter, UInt64.Counter) }

initial : Model
initial = {presentation=Presentation.initial,previews=Preview.initial,pendingQuery=Nothing,composition=Idle,lastQuery=Nothing}

isComposing : Model -> Bool
isComposing model = model.composition/=Idle

main : Program () Model Msg
main = Browser.element
    { init=\_ -> (initial,Cmd.none)
    , subscriptions=\_ -> Sub.batch [presentation Present,requestAction Action,nativePreviews NativePreview,nativePreviewGrants NativeGrant,nativePreviewQuarantine NativeQuarantine,nativePreviewClosed NativeClosed,nativePreviewIssued NativeIssued,nativePreviewRetry NativeRetry,nativePreviewRetirement NativeRetirement]
    , view=\model -> div [attribute "data-input-composing" (if isComposing model then "true" else "false")] [Presentation.current model.presentation |> Maybe.map (\snapshot -> SurfaceRenderer.viewWithPreview (\identity -> Preview.image snapshot identity model.previews) True Action (model.pendingQuery |> Maybe.map (\query -> SurfaceRenderer.pendingQuery query snapshot) |> Maybe.withDefault snapshot)) |> Maybe.withDefault (text "")]
    , update=update
    }

update : Msg -> Model -> (Model, Cmd Msg)
update message model =
    case message of
        Action value ->
            let kind=D.decodeValue (D.field "kind" D.string) value |> Result.withDefault ""
                sendQuery query wire current =
                    let key=Presentation.current current.presentation |> Maybe.map (\snapshot -> (query,SurfaceRenderer.publication snapshot,SurfaceRenderer.lease snapshot))
                        unchanged=Presentation.current current.presentation |> Maybe.andThen SurfaceRenderer.queryValue |> (==) (Just query)
                        duplicate=key/=Nothing && key==current.lastQuery
                    in ({current | pendingQuery=if unchanged then Nothing else Just query,lastQuery=key},if unchanged || duplicate then Cmd.none else actions wire)
                before = {baseline=model.pendingQuery |> Maybe.withDefault (Presentation.current model.presentation |> Maybe.andThen SurfaceRenderer.queryValue |> Maybe.withDefault ""),before=model.pendingQuery}
            in if List.member kind ["surface-query","surface-preedit","surface-composition-start","surface-composition-end"] then
                case Presentation.editQuery value model.presentation of
                    Just (query,wire) ->
                        if kind=="surface-composition-start" then
                            ({model | composition=Preediting {baseline=query,before=model.pendingQuery},pendingQuery=Just query},Cmd.none)
                        else if kind=="surface-composition-end" then
                            case model.composition of
                                Idle -> (model,Cmd.none)
                                Preediting held ->
                                    if query==held.baseline then
                                        ({model | composition=Idle,pendingQuery=held.before |> Maybe.andThen (\prior -> if (Presentation.current model.presentation |> Maybe.andThen SurfaceRenderer.queryValue)==Just prior then Nothing else Just prior)},Cmd.none)
                                    else sendQuery query wire {model | composition=Idle}
                        else if kind=="surface-preedit" || isComposing model then
                            ({model | composition=if isComposing model then model.composition else Preediting before,pendingQuery=Just query},Cmd.none)
                        else sendQuery query wire model
                    Nothing -> (model,Cmd.none)
            else if isComposing model || (model.pendingQuery/=Nothing && (D.decodeValue (D.field "id" D.string) value |> Result.map (\identity -> String.startsWith "entry:" identity || identity=="files:open-path" || identity=="files:home" || String.startsWith "files:collection:" identity) |> Result.withDefault False)) then (model,Cmd.none)
            else (model,Presentation.dispatch True value model.presentation |> Maybe.map actions |> Maybe.withDefault Cmd.none)
        Present raw ->
            let acceptedPresentation = Presentation.accept raw model.presentation
                (previews,commands) = Preview.present (Presentation.current acceptedPresentation) model.previews
                sameField = case (Presentation.current model.presentation,Presentation.current acceptedPresentation) of
                    (Just old,Just next) -> List.member (SurfaceRenderer.mode next) ["applications","files"] && SurfaceRenderer.mode old==SurfaceRenderer.mode next && SurfaceRenderer.enabled True (SurfaceRenderer.fieldIdentity next) next
                    _ -> False
                composition = if sameField then model.composition else Idle
                composing = composition/=Idle
                pending = if not sameField then Nothing else if composing then model.pendingQuery else model.pendingQuery |> Maybe.andThen (\query -> case Presentation.current acceptedPresentation of
                    Just snapshot -> if SurfaceRenderer.queryValue snapshot/=Just query then Just query else Nothing
                    Nothing -> Nothing)
                key = pending |> Maybe.andThen (\query -> Presentation.current acceptedPresentation |> Maybe.map (\snapshot -> (query,SurfaceRenderer.publication snapshot,SurfaceRenderer.lease snapshot)))
                queryCommand = if composing || key==model.lastQuery then Cmd.none else pending |> Maybe.andThen (\query -> Presentation.query query acceptedPresentation) |> Maybe.map actions |> Maybe.withDefault Cmd.none
                lastQuery = if not sameField then Nothing else if composing || pending==Nothing then model.lastQuery else key
            in ({presentation=acceptedPresentation,previews=previews,pendingQuery=pending,composition=composition,lastQuery=lastQuery},Cmd.batch [previewCommands commands,queryCommand])
        NativePreview raw ->
            let (previews,commands) =
                    case D.decodeValue Realm.envelopeDecoder raw of
                        Ok _ -> Preview.receiveRealm (Presentation.current model.presentation) raw model.previews
                        Err _ -> Preview.receive (Presentation.current model.presentation) raw model.previews
            in ({model | previews=previews},previewCommands commands)
        NativeRetirement raw ->
            let (previews,commands) = Preview.retireLegacy raw model.previews
            in ({model | previews=previews},previewCommands commands)
        NativeGrant raw ->
            let previews = D.decodeValue Realm.grantDecoder raw |> Result.toMaybe |> Maybe.andThen (\grant -> Preview.enrollRealm grant model.previews) |> Maybe.withDefault model.previews
            in ({model | previews=previews},Cmd.none)
        NativeQuarantine raw ->
            let (previews,commands) = D.decodeValue Realm.domainDecoder raw |> Result.map (\domain -> Preview.quarantineRealm domain model.previews) |> Result.withDefault (model.previews,E.list identity [])
            in ({model | previews=previews},previewCommands commands)
        NativeIssued raw -> ({model | previews=Preview.issued raw model.previews},Cmd.none)
        NativeRetry raw ->
            let (previews,commands) = D.decodeValue Realm.domainDecoder raw |> Result.map (\domain -> Preview.retry domain model.previews) |> Result.withDefault (model.previews,E.list identity [])
            in ({model | previews=previews},previewCommands commands)
        NativeClosed raw ->
            let previews = D.decodeValue Realm.domainDecoder raw |> Result.toMaybe |> Maybe.andThen (\domain -> Preview.closeRealm domain model.previews) |> Maybe.withDefault model.previews
            in ({model | previews=previews},Cmd.none)
