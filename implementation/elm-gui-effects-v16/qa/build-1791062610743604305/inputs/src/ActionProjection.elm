module ActionProjection exposing (Admitted, Window, decode, revision, actionable, minimized, windows)

import Json.Decode as D
import UInt64 exposing (Counter)

-- Window action enumeration only. This is not a canonical paint/input scene.
type Admitted = Admitted Counter (List Window)
type alias Window = { incarnation : Counter, label : String, minimized : Bool }
strict fields decoder = D.keyValuePairs D.value |> D.andThen (\pairs -> if List.sort (List.map Tuple.first pairs) == List.sort fields then decoder else D.fail "Unexpected fields")
nonzero = UInt64.decoder |> D.andThen (\v -> if v == UInt64.zero then D.fail "Zero identity" else D.succeed v)
windowDecoder = strict ["incarnation","label","minimized"] (D.map3 Window (D.field "incarnation" nonzero) (D.field "label" D.string) (D.field "minimized" D.bool))
decode value =
    D.decodeValue (strict ["revision","windows"] (D.map2 Admitted (D.field "revision" nonzero) (D.field "windows" (D.list windowDecoder)))) value
        |> Result.mapError D.errorToString
        |> Result.andThen (\((Admitted _ rows) as projection) ->
            if List.length rows > 256 || List.length (List.foldl (\row seen -> if List.member row.incarnation seen then seen else row.incarnation :: seen) [] rows) /= List.length rows || List.any (\row -> String.length row.label > 256 || String.any (\c -> Char.toCode c < 32) row.label) rows then Err "Invalid window enumeration" else Ok projection)
revision (Admitted value _) = value
windows (Admitted _ rows) = rows
minimized identity (Admitted _ rows) = rows |> List.filter (\row -> row.incarnation == identity) |> List.head |> Maybe.map .minimized
actionable identity projection = minimized identity projection /= Nothing
