module UInt64 exposing (Counter, compare, decoder, next, string, zero)

import Json.Decode as D


-- Authority-bearing values never pass through JavaScript numbers.
type Counter
    = Counter String


zero : Counter
zero =
    Counter "0"


string : Counter -> String
string (Counter value) =
    value


decoder : D.Decoder Counter
decoder =
    D.string
        |> D.andThen
            (\value ->
                if not (String.isEmpty value) && String.all (\c -> c >= '0' && c <= '9') value && (value == "0" || not (String.startsWith "0" value)) && String.length value <= 20 && (String.length value < 20 || value <= "18446744073709551615") then
                    D.succeed (Counter value)

                else
                    D.fail "Expected canonical uint64 string"
            )


compare : Counter -> Counter -> Order
compare (Counter left) (Counter right) =
    case Basics.compare (String.length left) (String.length right) of
        EQ -> Basics.compare left right
        order -> order


next : Counter -> Maybe Counter
next (Counter value) =
    let
        add digits =
            case digits of
                [] -> [ '1' ]
                '9' :: rest -> '0' :: add rest
                digit :: rest -> Char.fromCode (Char.toCode digit + 1) :: rest
    in
    if value == "18446744073709551615" then
        Nothing

    else
        Just (Counter (value |> String.toList |> List.reverse |> add |> List.reverse |> String.fromList))
