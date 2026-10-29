port module DecoderReplay exposing (main)

import Binding
import Json.Decode as D
import Json.Encode as E
import Platform
import Shell

port incoming : (D.Value -> msg) -> Sub msg
port outgoing : E.Value -> Cmd msg

type Msg = Run D.Value

main : Program () () Msg
main =
    Platform.worker
        { init = \_ -> ( (), Cmd.none )
        , subscriptions = \_ -> incoming Run
        , update = \(Run raw) _ ->
            let
                binding = E.object [("lifetime", E.string "17"), ("session", E.string "3"), ("frontend", E.string "1")]
                attached = E.object [("kind", E.string "attached"), ("protocolVersion", E.int 3), ("binding", binding)]
                ( prior, setupCommands ) = Shell.update (Shell.Incoming attached) Shell.initial
                ( after, commands ) = Shell.update (Shell.Incoming raw) prior
                bindingValue model = model.binding |> Maybe.map Binding.encode |> Maybe.withDefault E.null
                row = E.object
                    [ ("prior", Shell.encode prior), ("after", Shell.encode after)
                    , ("priorBinding", bindingValue prior), ("afterBinding", bindingValue after)
                    , ("sameModel", E.bool (prior == after))
                    , ("sameAuthority", E.bool (prior.binding == after.binding && prior.effects == after.effects))
                    , ("priorNotice", E.string prior.notice), ("afterNotice", E.string after.notice)
                    , ("setupCommandCount", E.int (List.length setupCommands)), ("commandCount", E.int (List.length commands))
                    ]
            in
            ( (), outgoing row )
        }
