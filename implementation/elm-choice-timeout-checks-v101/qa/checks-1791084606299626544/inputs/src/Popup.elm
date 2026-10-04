port module Popup exposing (main)

import Browser
import Html exposing (div, text)
import Html.Events exposing (on)
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
    , view=\model -> Presentation.current model |> Maybe.map (\snapshot ->
        let escape = D.map2 Tuple.pair (D.field "key" D.string) (D.field "isComposing" D.bool) |> D.andThen (\(key,composing) ->
                if key=="Escape" && not composing then SurfaceRenderer.action True "control:close" snapshot |> Maybe.map (Action >> D.succeed) |> Maybe.withDefault (D.fail "No current close") else D.fail "Unrelated or composing")
        in div [on "keydown" escape] [SurfaceRenderer.view True Action snapshot]) |> Maybe.withDefault (text "")
    , update=\message model -> case message of
        Action value -> (model,Presentation.dispatch True value model |> Maybe.map actions |> Maybe.withDefault Cmd.none)
        Present raw -> (Presentation.accept raw model,Cmd.none)
    }
