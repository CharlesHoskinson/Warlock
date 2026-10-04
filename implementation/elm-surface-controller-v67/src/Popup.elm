port module Popup exposing (main)

import Browser
import Html exposing (text)
import Json.Decode as D
import Json.Encode as E
import Presentation
import SurfaceRenderer
import UInt64

port presentation : (D.Value -> msg) -> Sub msg
port actions : E.Value -> Cmd msg

type Msg = Present D.Value | Action E.Value

main : Program () Presentation.Model Msg
main = Browser.element
    { init=\_ -> (Presentation.initial,Cmd.none)
    , subscriptions=\_ -> presentation Present
    , view=\model -> Presentation.current model |> Maybe.map (SurfaceRenderer.view True Action) |> Maybe.withDefault (text "")
    , update=\message model -> case message of
        Action value -> (model,Presentation.dispatch True value model |> Maybe.map actions |> Maybe.withDefault Cmd.none)
        Present raw -> (Presentation.accept raw model,Cmd.none)
    }
