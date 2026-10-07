port module Popup exposing (main)

import Browser
import Html exposing (div, text)
import Html.Events exposing (on)
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

type Msg = Present D.Value | Action E.Value | NativePreview D.Value | NativeGrant D.Value | NativeQuarantine D.Value | NativeClosed D.Value | NativeIssued D.Value | NativeRetry D.Value
type alias Model = { presentation : Presentation.Model, previews : Preview.Model, pendingQuery : Maybe String, composing : Bool }

main : Program () Model Msg
main = Browser.element
    { init=\_ -> ({presentation=Presentation.initial,previews=Preview.initial,pendingQuery=Nothing,composing=False},Cmd.none)
    , subscriptions=\_ -> Sub.batch [presentation Present,requestAction Action,nativePreviews NativePreview,nativePreviewGrants NativeGrant,nativePreviewQuarantine NativeQuarantine,nativePreviewClosed NativeClosed,nativePreviewIssued NativeIssued,nativePreviewRetry NativeRetry]
    , view=\model -> Presentation.current model.presentation |> Maybe.map (\snapshot -> SurfaceRenderer.viewWithPreview (\identity -> Preview.image snapshot identity model.previews) True Action (model.pendingQuery |> Maybe.map (\query -> SurfaceRenderer.pendingQuery query snapshot) |> Maybe.withDefault snapshot)) |> Maybe.withDefault (text "")
    , update=\message model -> case message of
        Action value ->
            if D.decodeValue (D.field "kind" D.string) value |> Result.map (\kind -> List.member kind ["surface-query","surface-preedit"]) |> Result.withDefault False then
                case Presentation.editQuery value model.presentation of
                    Just (query,wire) ->
                        let composing = D.decodeValue (D.field "kind" D.string) value==Ok "surface-preedit"
                        in ({model | pendingQuery=Just query,composing=composing},if composing then Cmd.none else actions wire)
                    Nothing -> (model,Cmd.none)
            else if (model.pendingQuery/=Nothing || model.composing) && (D.decodeValue (D.field "id" D.string) value |> Result.map (String.startsWith "entry:") |> Result.withDefault False) then (model,Cmd.none)
            else (model,Presentation.dispatch True value model.presentation |> Maybe.map actions |> Maybe.withDefault Cmd.none)
        Present raw ->
            let acceptedPresentation = Presentation.accept raw model.presentation
                (previews,commands) = Preview.present (Presentation.current acceptedPresentation) model.previews
                pending = model.pendingQuery |> Maybe.andThen (\query -> case Presentation.current acceptedPresentation of
                    Just snapshot -> if SurfaceRenderer.mode snapshot=="applications" && SurfaceRenderer.queryValue snapshot/=Just query then Just query else Nothing
                    Nothing -> Nothing)
                composing = model.composing && (Presentation.current acceptedPresentation |> Maybe.map (\snapshot -> SurfaceRenderer.mode snapshot=="applications") |> Maybe.withDefault False)
                queryCommand = if composing then Cmd.none else pending |> Maybe.andThen (\query -> Presentation.query query acceptedPresentation) |> Maybe.map actions |> Maybe.withDefault Cmd.none
            in ({presentation=acceptedPresentation,previews=previews,pendingQuery=pending,composing=composing},Cmd.batch [previewCommands commands,queryCommand])
        NativePreview raw ->
            let (previews,commands) =
                    case D.decodeValue Realm.envelopeDecoder raw of
                        Ok _ -> Preview.receiveRealm (Presentation.current model.presentation) raw model.previews
                        Err _ -> Preview.receive (Presentation.current model.presentation) raw model.previews
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
    }
