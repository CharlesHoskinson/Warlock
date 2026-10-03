module CounterChecks exposing (results)

import Json.Decode as D
import Json.Encode as E
import UInt64


results : E.Value
results =
    let
        samples = [ "0", "9", "10", "99", "9007199254740992", "9007199254740993", "9999999999999999999", "10000000000000000000", "18446744073709551614", "18446744073709551615" ]
        decoded = List.filterMap (\raw -> D.decodeValue UInt64.decoder (E.string raw) |> Result.toMaybe) samples
        encodeNext counter = Maybe.map (UInt64.string >> E.string) (UInt64.next counter) |> Maybe.withDefault E.null
        order value = case value of
            LT -> -1
            EQ -> 0
            GT -> 1
    in
    E.object
        [ ( "next", E.list (\counter -> E.object [ ( "value", E.string (UInt64.string counter) ), ( "next", encodeNext counter ) ]) decoded )
        , ( "comparisons", E.list (\left -> E.list (\right -> E.int (order (UInt64.compare left right))) decoded) decoded )
        ]
