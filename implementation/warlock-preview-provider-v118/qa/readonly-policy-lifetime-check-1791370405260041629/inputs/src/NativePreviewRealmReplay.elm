port module NativePreviewRealmReplay exposing (main)

import Json.Decode as D
import Json.Encode as E
import NativePreviewRealm as Realm
import NativePreviewDetachment as Detachment
import Platform
import UInt64

port incoming : (D.Value -> msg) -> Sub msg
port outgoing : E.Value -> Cmd msg

result : D.Value -> E.Value
result raw =
    let accepted body = E.object [("accepted",E.bool True),("body",body)]
        rejected = E.object [("accepted",E.bool False)]
        decode decoder = D.decodeValue (D.field "value" decoder) raw
    in case D.decodeValue (D.field "op" D.string) raw of
        Ok "grant" -> case decode Realm.grantDecoder of
            Ok grant -> accepted (E.object [("binding",Realm.bindingValue grant.domain),("receiverEpoch",E.string (UInt64.string grant.domain.receiverEpoch)),("capacity",E.int grant.capacity)])
            Err _ -> rejected
        Ok "seed" -> case decode Detachment.seedDecoder of
            Ok seed -> accepted (Detachment.ready seed)
            Err _ -> rejected
        Ok "delivery" -> case decode Detachment.deliveryDecoder of
            Ok delivery -> accepted (Detachment.acknowledgment delivery)
            Err _ -> rejected
        Ok "envelope" -> case (D.decodeValue (D.field "grant" Realm.grantDecoder) raw,decode Realm.envelopeDecoder) of
            (Ok grant,Ok envelope) -> Realm.unwrap grant.domain envelope |> Maybe.map accepted |> Maybe.withDefault rejected
            _ -> rejected
        _ -> rejected

main : Program () () D.Value
main = Platform.worker {init=\_ -> ((),Cmd.none),subscriptions=\_ -> incoming identity,update=\raw _ -> ((),outgoing (result raw))}
