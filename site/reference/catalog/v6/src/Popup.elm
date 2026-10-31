port module Popup exposing (main)

import Browser
import Html exposing (div, text)
import Html.Events exposing (on)
import Json.Decode as D
import Json.Encode as E
import PreviewPresenter as Preview
import Presentation
import SurfaceRenderer
import UInt64

port presentation : (D.Value -> msg) -> Sub msg
port requestAction : (D.Value -> msg) -> Sub msg
port actions : E.Value -> Cmd msg

port nativePreviews : (D.Value -> msg) -> Sub msg
port previewCommands : E.Value -> Cmd msg

type Msg = Present D.Value | Action E.Value | NativePreview D.Value
type alias Model = { presentation : Presentation.Model, previews : Preview.Model }

main : Program () Model Msg
main = Browser.element
    { init=\_ -> ({presentation=Presentation.initial,previews=Preview.initial},Cmd.none)
    , subscriptions=\_ -> Sub.batch [presentation Present,requestAction Action,nativePreviews NativePreview]
    , view=\model -> Presentation.current model.presentation |> Maybe.map (\snapshot -> SurfaceRenderer.viewWithPreview (\identity -> Preview.image snapshot identity model.previews) True Action snapshot) |> Maybe.withDefault (text "")
    , update=\message model -> case message of
        Action value -> (model,Presentation.dispatch True value model.presentation |> Maybe.map actions |> Maybe.withDefault Cmd.none)
        Present raw ->
            let acceptedPresentation = Presentation.accept raw model.presentation
                (previews,commands) = Preview.present (Presentation.current acceptedPresentation) model.previews
            in ({presentation=acceptedPresentation,previews=previews},previewCommands commands)
        NativePreview raw ->
            let (previews,commands) = Preview.receive (Presentation.current model.presentation) raw model.previews
            in ({model | previews=previews},previewCommands commands)
    }
