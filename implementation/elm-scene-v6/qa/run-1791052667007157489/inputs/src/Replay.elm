port module Replay exposing (main)

import Json.Decode as D
import Json.Encode as E
import Platform
import Scene

port incoming : (D.Value -> msg) -> Sub msg
port outgoing : E.Value -> Cmd msg

type Msg = Candidate D.Value

main : Program () () Msg
main = Platform.worker
    { init = \_ -> ( (), Cmd.none )
    , subscriptions = \_ -> incoming Candidate
    , update = \(Candidate value) _ ->
        ( (), outgoing (case Scene.decode value of
            Err message -> E.object [ ( "accepted", E.bool False ), ( "error", E.string message ) ]
            Ok scene -> E.object
                [ ( "accepted", E.bool True )
                , ( "paint", E.list E.string (Scene.paint scene) )
                , ( "hit", Maybe.map E.string (Scene.hit scene) |> Maybe.withDefault E.null )
                , ( "focus", Maybe.map E.string (Scene.focus scene) |> Maybe.withDefault E.null )
                ]) )
    }
