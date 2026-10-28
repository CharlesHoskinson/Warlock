port module LosslessBridgeReplay exposing (main)

import ActionProjection
import Effects
import Json.Decode as D
import Json.Encode as E
import Platform
import UInt64

port incoming : (D.Value -> msg) -> Sub msg
port outgoing : E.Value -> Cmd msg

type Msg = Receive D.Value

main : Program () () Msg
main =
    Platform.worker
        { init = \_ -> ( (), Cmd.none )
        , update = \(Receive raw) model -> ( model, outgoing (inspect raw) )
        , subscriptions = \_ -> incoming Receive
        }

inspect : D.Value -> E.Value
inspect raw =
    let
        intent = D.decodeValue (D.field "intent" Effects.intentDecoder) raw
        scene = D.decodeValue (D.field "scene" D.value) raw |> Result.mapError D.errorToString |> Result.andThen ActionProjection.decode
    in
    E.object
        [ ( "intent", Result.withDefault E.null (Result.map Effects.encodeIntent intent) )
        , ( "scene", scene |> Result.map (ActionProjection.windows >> List.map (.incarnation >> UInt64.string) >> E.list E.string) |> Result.withDefault E.null )
        , ( "intentAccepted", E.bool (Result.toMaybe intent /= Nothing) )
        , ( "sceneAccepted", E.bool (Result.toMaybe scene /= Nothing) )
        ]
