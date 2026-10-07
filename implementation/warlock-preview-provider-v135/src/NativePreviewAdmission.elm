port module NativePreviewAdmission exposing (main)

import Browser
import Html exposing (text)
import Json.Decode as D
import Json.Encode as E
import Presentation
import SurfaceRenderer

-- Original GTK presentation/focus admission, with no preview/window policy.
port presentation : (D.Value -> msg) -> Sub msg
port requestAction : (D.Value -> msg) -> Sub msg
port actions : E.Value -> Cmd msg

type Msg = Present D.Value | Action E.Value

main : Program () Presentation.Model Msg
main = Browser.element
    { init = \_ -> (Presentation.initial, Cmd.none)
    , subscriptions = \_ -> Sub.batch [presentation Present, requestAction Action]
    , view = \model -> Presentation.current model
        |> Maybe.map (SurfaceRenderer.view True Action)
        |> Maybe.withDefault (text "")
    , update = \message model -> case message of
        Present raw -> (Presentation.accept raw model, Cmd.none)
        Action raw -> (model, Presentation.dispatch True raw model
            |> Maybe.map actions |> Maybe.withDefault Cmd.none)
    }
