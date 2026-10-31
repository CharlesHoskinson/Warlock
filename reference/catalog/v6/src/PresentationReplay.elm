port module PresentationReplay exposing (main)
import Json.Decode as D
import Json.Encode as E
import Platform
import Presentation
import SurfaceRenderer
import UInt64
port incoming : (D.Value -> msg) -> Sub msg
port outgoing : E.Value -> Cmd msg
type Msg = Run D.Value
main : Program () () Msg
main = Platform.worker {init=\_ -> ((),Cmd.none),subscriptions=\_ -> incoming Run,update=\(Run raw) _ ->
    let events = D.decodeValue (D.list D.value) raw |> Result.withDefault []
        (_,rows) = List.foldl apply (Presentation.initial,[]) events
    in ((),outgoing (E.list identity (List.reverse rows)))}
apply raw (model,rows) =
    let value name = D.decodeValue (D.field name D.value) raw |> Result.withDefault E.null
        kind = D.decodeValue (D.field "kind" D.string) raw |> Result.withDefault ""
        next = if kind=="present" then Presentation.accept (value "frame") model else model
        action = if kind=="action" then Presentation.dispatch True (value "action") next else Nothing
        row = E.object [("publication",Presentation.current next |> Maybe.map (SurfaceRenderer.publication >> UInt64.string >> E.string) |> Maybe.withDefault E.null),("action",Maybe.withDefault E.null action)]
    in (next,row::rows)
