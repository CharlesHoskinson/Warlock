port module Tests exposing (main)

import Domain exposing (Effect(..), Msg(..), State(..))
import Json.Decode as D
import Json.Encode as E
import Platform
import Protocol exposing (Event(..))


port results : E.Value -> Cmd msg


value : String -> D.Value
value raw =
    Result.withDefault E.null (D.decodeString D.value raw)


valid : String
valid =
    "{\"protocolVersion\":1,\"kind\":\"fixture-snapshot\",\"source\":\"fixture\",\"epoch\":\"1\",\"windows\":[{\"incarnation\":\"9007199254740993\",\"label\":\"A\",\"minimized\":false},{\"incarnation\":\"9007199254740994\",\"label\":\"B\",\"minimized\":true}]}"


rejected : String -> Bool
rejected raw =
    case Protocol.decode (value raw) of
        Err _ -> True
        Ok _ -> False


check : String -> Bool -> E.Value
check name passed =
    E.object [ ( "name", E.string name ), ( "passed", E.bool passed ) ]


main : Program () () Never
main =
    Platform.worker
        { init = \_ ->
            let
                ( accepted, noEffects ) = Domain.update (Native (value valid)) Domain.initial
                ( refused, refusalEffects ) = Domain.update (Native (value "{}")) accepted
                ( refreshing, refreshEffects ) = Domain.update Refresh accepted
                distinct =
                    case Protocol.decode (value valid) of
                        Ok (FixtureSnapshot _ windows) -> List.map (.incarnation >> Protocol.idString) windows == [ "9007199254740993", "9007199254740994" ]
                        _ -> False
                exactMax = not (rejected (String.replace "9007199254740994" "18446744073709551615" valid))
            in
            ( (), results (E.list identity
                [ check "fixture-decodes-with-lossless-identities" distinct
                , check "observations-do-not-emit-effects" (List.isEmpty noEffects)
                , check "malformed-preserves-observations" (refused.state == accepted.state && List.isEmpty refusalEffects)
                , check "unsupported-version-refused" (rejected (String.replace "\"protocolVersion\":1" "\"protocolVersion\":2" valid))
                , check "numeric-identity-refused" (rejected (String.replace "\"9007199254740993\"" "9007199254740993" valid))
                , check "noncanonical-zero-refused" (rejected (String.replace "9007199254740993" "01" valid))
                , check "negative-identity-refused" (rejected (String.replace "9007199254740993" "-1" valid))
                , check "u64-overflow-refused" (rejected (String.replace "9007199254740993" "18446744073709551616" valid))
                , check "u64-maximum-decodes" exactMax
                , check "duplicate-incarnation-refused" (rejected (String.replace "9007199254740994" "9007199254740993" valid))
                , check "production-observation-refused" (rejected (String.replace "\"source\":\"fixture\"" "\"source\":\"native\"" valid))
                , check "unrecognized-kind-refused" (rejected (String.replace "fixture-snapshot" "effect-committed" valid))
                , check "refresh-is-read-only" (refreshing.state == accepted.state && refreshEffects == [ RequestSnapshot ])
                , check "deterministic-replay" (Domain.update (Native (value valid)) Domain.initial == Domain.update (Native (value valid)) Domain.initial)
                ]))
        , update = \impossible _ -> never impossible
        , subscriptions = \_ -> Sub.none
        }
