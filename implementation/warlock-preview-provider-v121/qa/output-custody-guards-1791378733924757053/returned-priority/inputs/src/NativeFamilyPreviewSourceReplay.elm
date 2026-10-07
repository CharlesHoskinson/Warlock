port module NativeFamilyPreviewSourceReplay exposing (main)

import Json.Decode as D
import Json.Encode as E
import NativeFamilyPreviewSource
import Platform

port incoming : (D.Value -> msg) -> Sub msg
port outgoing : E.Value -> Cmd msg

type Msg = Decode D.Value

main : Program () () Msg
main = Platform.worker
    { init=\_ -> ((),Cmd.none)
    , subscriptions=\_ -> incoming Decode
    , update=\(Decode value) model -> (model,outgoing (case D.decodeValue NativeFamilyPreviewSource.decoder value of
        Ok observation -> E.object [ ("accepted",E.bool True), ("observation",NativeFamilyPreviewSource.summary observation) ]
        Err _ -> E.object [ ("accepted",E.bool False) ]))
    }
