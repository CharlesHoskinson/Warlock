port module Popup exposing (main)

import Browser
import Html exposing (text)
import Json.Decode as D
import Json.Encode as E
import SurfaceRenderer
import UInt64

port presentation : (D.Value -> msg) -> Sub msg
port actions : E.Value -> Cmd msg

type Msg = Present D.Value | Action E.Value
type alias Model = { last : UInt64.Counter, lease : UInt64.Counter, snapshot : Maybe SurfaceRenderer.Snapshot }

main : Program () Model Msg
main = Browser.element
    { init=\_ -> ({last=UInt64.zero,lease=UInt64.zero,snapshot=Nothing},Cmd.none)
    , subscriptions=\_ -> presentation Present
    , view=\model -> model.snapshot |> Maybe.map (SurfaceRenderer.view True Action) |> Maybe.withDefault (text "")
    , update=\message model -> case message of
        Action value -> (model,actions value)
        Present raw ->
            case SurfaceRenderer.decode raw of
                Err _ -> ({model | snapshot=Nothing},Cmd.none)
                Ok snapshot ->
                    if UInt64.compare (SurfaceRenderer.publication snapshot) model.last/=GT || UInt64.compare (SurfaceRenderer.lease snapshot) model.lease==LT then (model,Cmd.none)
                    else ({last=SurfaceRenderer.publication snapshot,lease=SurfaceRenderer.lease snapshot,snapshot=Just snapshot},Cmd.none)
    }
