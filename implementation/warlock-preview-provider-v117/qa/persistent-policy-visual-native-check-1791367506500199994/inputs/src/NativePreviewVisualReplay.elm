port module NativePreviewVisualReplay exposing (main)

import Json.Decode as D
import Json.Encode as E
import NativePreviewRealm as Realm
import NativePreviewVisual as Visual
import PreviewVisual
import Platform

port incoming : (D.Value -> msg) -> Sub msg
port outgoing : E.Value -> Cmd msg
type Msg = Run D.Value
main : Program () () Msg
main = Platform.worker {init=\_ -> ((),Cmd.none),subscriptions=\_ -> incoming Run,update=\(Run raw) model ->
    let result = case D.decodeValue (D.field "kind" D.string) raw of
            Ok "visual" -> D.decodeValue (D.field "value" PreviewVisual.decoder) raw |> Result.map PreviewVisual.encode
            Ok "projection" -> D.decodeValue (D.field "domain" Realm.domainDecoder) raw |> Result.andThen (\authority -> D.decodeValue (D.field "value" (Visual.decoder authority)) raw) |> Result.map Visual.encode
            _ -> Err "Closed visual replay kind"
    in (model,outgoing (E.object [("accepted",E.bool (Result.toMaybe result/=Nothing)),("value",Result.withDefault E.null result)]))}
