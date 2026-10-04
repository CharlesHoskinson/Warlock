port module Bar exposing (main)

import Browser
import Html exposing (text)
import Json.Decode as D
import Json.Encode as E
import Presentation
import SurfaceRenderer

port presentation : (D.Value -> msg) -> Sub msg
port actions : E.Value -> Cmd msg

type Msg = Present D.Value | Action E.Value

-- A display owns only a presentation cache. It cannot run Desktop.update.
main : Program () Presentation.Model Msg
main = Browser.element
    { init=\_ -> (Presentation.initial,Cmd.none)
    , subscriptions=\_ -> presentation Present
    , view=\model -> Presentation.current model |> Maybe.map (SurfaceRenderer.view False Action) |> Maybe.withDefault (text "")
    , update=\message model -> case message of
        Action value -> (model,Presentation.dispatch False value model |> Maybe.map actions |> Maybe.withDefault Cmd.none)
        Present raw -> (Presentation.accept raw model,Cmd.none)
    }
