port module GeometryBoundsReplay exposing (main)
import GeometryProjection
import Json.Decode as D
import Json.Encode as E
import Platform
port incoming : (D.Value -> msg) -> Sub msg
port outgoing : E.Value -> Cmd msg
type Msg = Check D.Value
main = Platform.worker {init=\_ -> ((),Cmd.none),update=update,subscriptions=\_ -> incoming Check}
update (Check raw) _ =
    let samples=D.decodeValue (D.list D.value) raw |> Result.withDefault []
        evaluate sample =
            let decoded=D.decodeValue (D.map2 Tuple.pair (D.field "mode" D.string) (D.field "envelope" D.value)) sample
                accepted=case decoded of
                    Ok (mode,envelope) ->
                        let decode=if mode=="legacy" then GeometryProjection.decodeLegacy else GeometryProjection.decode
                        in case decode {effects=True,operations=["maximize","restore-geometry"]} envelope of
                            Ok _ -> True
                            Err _ -> False
                    Err _ -> False
            in E.bool accepted
    in ((),outgoing (E.list evaluate samples))
