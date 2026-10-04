port module GeometryPolicyWorker exposing (main)

import Json.Decode as D
import Json.Encode as E
import Platform
import WindowGeometry as W


port request : (D.Value -> msg) -> Sub msg


port response : E.Value -> Cmd msg


type Msg
    = Request D.Value


main : Program () () Msg
main =
    Platform.worker
        { init = \_ -> ( (), Cmd.none )
        , update = \(Request value) model -> ( model, response (run value) )
        , subscriptions = \_ -> request Request
        }


mode : D.Decoder W.NativeMode
mode =
    D.string
        |> D.andThen
            (\s ->
                case s of
                    "ordinary" -> D.succeed W.Ordinary
                    "maximized" -> D.succeed W.Maximized
                    "fullscreen" -> D.succeed W.Fullscreen
                    _ -> D.fail "invalid mode"
            )


resolution : D.Decoder W.Resolution
resolution =
    D.string
        |> D.andThen
            (\s ->
                case s of
                    "ready" -> D.succeed W.Ready
                    "pending" -> D.succeed W.Pending
                    "unknown" -> D.succeed W.Unknown
                    _ -> D.fail "invalid resolution"
            )


capabilities : D.Decoder W.Capabilities
capabilities =
    D.map8 W.Capabilities
        (D.field "restoreMinimized" D.bool)
        (D.field "restoreGeometry" D.bool)
        (D.field "move" D.bool)
        (D.field "size" D.bool)
        (D.field "minimize" D.bool)
        (D.field "maximize" D.bool)
        (D.field "close" D.bool)
        (D.field "exitFullscreen" D.bool)


facts : D.Decoder W.Facts
facts =
    D.map6 W.Facts
        (D.field "mode" mode)
        (D.field "minimized" D.bool)
        (D.field "fixedSize" D.bool)
        (D.field "geometryEligible" D.bool)
        (D.field "resolution" resolution)
        (D.field "capabilities" capabilities)


actionName : W.Action -> String
actionName action =
    case action of
        W.RestoreMinimized -> "restore-minimized"
        W.RestoreGeometry -> "restore-geometry"
        W.Move -> "move"
        W.Size -> "size"
        W.Minimize -> "minimize"
        W.Maximize -> "maximize"
        W.Close -> "close"
        W.ExitFullscreen -> "exit-fullscreen"


encodeItem : W.Item -> E.Value
encodeItem item =
    E.object
        [ ( "label", E.string item.label )
        , ( "action", E.string (actionName item.action) )
        , ( "enabled", E.bool item.enabled )
        ]


run : D.Value -> E.Value
run value =
    case D.decodeValue facts value of
        Err _ -> E.object [ ( "error", E.bool True ) ]
        Ok input ->
            E.object
                [ ( "rows", E.list encodeItem (W.items input) )
                , ( "exitFullscreen", Maybe.map encodeItem (W.exitFullscreen input) |> Maybe.withDefault E.null )
                , ( "authorized", E.list (\action -> E.string (actionName action))
                    (List.filter (\action -> W.authorize action input)
                        [ W.RestoreMinimized, W.RestoreGeometry, W.Move, W.Size, W.Minimize, W.Maximize, W.Close, W.ExitFullscreen ]) )
                ]
