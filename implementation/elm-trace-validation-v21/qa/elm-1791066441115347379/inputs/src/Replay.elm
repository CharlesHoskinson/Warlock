port module Replay exposing (main)
import Json.Decode as D
import Json.Encode as E
import Platform
import RenderTrace
port incoming : (D.Value -> msg) -> Sub msg
port outgoing : E.Value -> Cmd msg
type Msg = Run D.Value
main : Program () () Msg
main = Platform.worker { init = \_ -> ((),Cmd.none),subscriptions = \_ -> incoming Run,update = \(Run value) _ -> ((),outgoing (case RenderTrace.decode value of
    Ok trace -> E.object [("passed",E.bool True),("summary",RenderTrace.encodeSummary trace)]
    Err error -> E.object [("passed",E.bool False),("error",E.string error)])) }
