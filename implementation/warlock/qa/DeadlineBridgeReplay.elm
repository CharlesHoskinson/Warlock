port module DeadlineBridgeReplay exposing (main)

import Json.Decode as D
import Json.Encode as E
import Platform
import PreviewLifecycle as Preview

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
        scope = D.decodeValue (D.field "scope" Preview.scopeDecoder) raw
        request = D.decodeValue (D.field "request" Preview.eventDecoder) raw
        clock = D.decodeValue (D.field "clockEvent" Preview.eventDecoder) raw
        open = D.decodeValue Preview.eventDecoder (E.object [ ( "kind", E.string "open" ) ])
        rejected stage = E.object [ ( "accepted", E.bool False ), ( "stage", E.string stage ), ( "commands", E.list identity [] ), ( "clockCommands", E.list identity [] ) ]
    in
    case ( scope, open, ( request, clock ) ) of
        ( Err _, _, _ ) -> rejected "scope"
        ( _, Err _, _ ) -> rejected "open"
        ( _, _, ( Err _, _ ) ) -> rejected "request"
        ( _, _, ( _, Err _ ) ) -> rejected "clockEvent"
        ( Ok acceptedScope, Ok openEvent, ( Ok requestEvent, Ok clockEvent ) ) ->
            let
                ( opened, _ ) = Preview.update openEvent (Preview.init acceptedScope)
                ( requested, commands ) = Preview.update requestEvent opened
                ( _, clockCommands ) = Preview.update clockEvent requested
            in
            E.object [ ( "accepted", E.bool True ), ( "stage", E.string "decoded" ), ( "commands", Preview.encodeCommands commands ), ( "clockCommands", Preview.encodeCommands clockCommands ) ]
