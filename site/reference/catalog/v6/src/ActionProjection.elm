module ActionProjection exposing (Admitted, Window, decode, revision, actionable, minimized, windows, sameState, focused, rootOf)

import Dict exposing (Dict)
import Json.Decode as D
import UInt64 exposing (Counter)

-- Coherent window-action facts only; never canonical paint/input admission.
type Admitted = Admitted Counter (Maybe Counter) (List Window) (Dict String Counter)
type alias Window = { incarnation : Counter, label : String, minimized : Bool, owner : Maybe Counter, application : String, available : Bool }
strict fields decoder = D.keyValuePairs D.value |> D.andThen (\pairs -> if List.sort (List.map Tuple.first pairs) == List.sort fields then decoder else D.fail "Unexpected projection fields")
nonzero = UInt64.decoder |> D.andThen (\v -> if v == UInt64.zero then D.fail "Zero identity" else D.succeed v)
bounded = D.value |> D.andThen (\v -> case D.decodeValue (D.index 256 D.value) v of
    Ok _ -> D.fail "Window bound"
    Err _ -> D.list windowDecoder)
windowDecoder = strict ["incarnation","label","minimized","owner","application","available"] (D.map6 Window (D.field "incarnation" nonzero) (D.field "label" D.string) (D.field "minimized" D.bool) (D.field "owner" (D.nullable nonzero)) (D.field "application" D.string) (D.field "available" D.bool))
find identity rows = rows |> List.filter (\w -> w.incarnation == identity) |> List.head
rootIn fuel identity rows =
    if fuel <= 0 then Nothing else
    Dict.get (UInt64.string identity) rows |> Maybe.andThen (\w -> case w.owner of
        Nothing -> Just w.incarnation
        Just parent -> rootIn (fuel - 1) parent rows)
validText value = String.length value <= 256 && not (String.any (\c -> Char.toCode c < 32) value)
decode value =
    D.decodeValue (strict ["revision","focused","windows"] (D.map3 (\revision_ focus_ rows_ -> Admitted revision_ focus_ rows_ Dict.empty) (D.field "revision" nonzero) (D.field "focused" (D.nullable nonzero)) (D.field "windows" bounded))) value
        |> Result.mapError D.errorToString
        |> Result.andThen (\((Admitted revision_ focus rows _) as projection) ->
            let table = Dict.fromList (List.map (\w -> (UInt64.string w.incarnation,w)) rows)
                roots = List.foldl (\w accumulated -> Maybe.map2 (\cache root -> Dict.insert (UInt64.string w.incarnation) root cache) accumulated (rootIn 256 w.incarnation table)) (Just Dict.empty) rows
                unique = List.foldl (\w seen -> if List.member w.incarnation seen then seen else w.incarnation :: seen) [] rows
                validFamily w = roots |> Maybe.andThen (Dict.get (UInt64.string w.incarnation)) |> Maybe.andThen (\root -> Dict.get (UInt64.string root) table) |> Maybe.map (\root -> root.minimized == w.minimized) |> Maybe.withDefault False
                validFocus = focus |> Maybe.map (\identity -> find identity rows |> Maybe.map (\w -> not w.minimized) |> Maybe.withDefault False) |> Maybe.withDefault True
            in if List.length unique /= List.length rows || not validFocus || List.any (\w -> not (validText w.label && validText w.application && validFamily w)) rows then Err "Incoherent ownership/focus projection" else case roots of
                Just cache -> Ok (Admitted revision_ focus rows cache)
                Nothing -> Err "Invalid ownership graph")
revision (Admitted value _ _ _) = value
windows (Admitted _ _ rows _) = rows
focused (Admitted _ focus _ _) = focus
rootOf identity (Admitted _ _ _ cache) = Dict.get (UInt64.string identity) cache
minimized identity projection = find identity (windows projection) |> Maybe.map .minimized
actionable identity projection = find identity (windows projection) |> Maybe.map .available |> Maybe.withDefault False
sameState left right =
    let state projection = windows projection |> List.sortWith (\a b -> UInt64.compare a.incarnation b.incarnation) |> List.map (\w -> ( w.incarnation, (w.minimized,w.owner), (w.application,w.available) ))
    in focused left == focused right && state left == state right
