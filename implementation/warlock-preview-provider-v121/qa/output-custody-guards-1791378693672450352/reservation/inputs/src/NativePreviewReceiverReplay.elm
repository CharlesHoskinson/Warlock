port module NativePreviewReceiverReplay exposing (main)

import Json.Decode as D
import Json.Encode as E
import NativePreviewReceiver as Receiver
import Platform

port incoming : (D.Value -> msg) -> Sub msg
port outgoing : E.Value -> Cmd msg
type Msg = Receive D.Value

main : Program D.Value Receiver.Model Msg
main = Platform.worker
    { init=\flags -> (Receiver.init flags,Cmd.none)
    , subscriptions=\_ -> incoming Receive
    , update=\(Receive raw) model ->
        let (next,receipt)=Receiver.receive raw model
        in (next,outgoing (E.object [("state",Receiver.inspect next),("receipt",Maybe.withDefault E.null receipt)]))
    }
