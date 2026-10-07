module Pins exposing (Model, Snapshot, initial, decoder, encode, observe, propose, receive, toggle, move, writable, bytes)

import Json.Decode as D
import Json.Encode as E
import UInt64 exposing (Counter)

type alias Snapshot = { revision : Counter, identities : List String }
type alias Model = { snapshot : Maybe Snapshot, pending : Maybe {request : Counter, identities : List String}, notice : String }
initial : Model
initial = {snapshot=Nothing,pending=Nothing,notice=""}
strict fields child = D.keyValuePairs D.value |> D.andThen (\pairs -> if List.sort (List.map Tuple.first pairs)==List.sort fields then child else D.fail "Pin fields")
identityDecoder = D.string |> D.andThen (\s -> if not (String.isEmpty s) && String.length s<=256 && not (String.any (\c -> Char.toCode c<32 || Char.toCode c==127) s) then D.succeed s else D.fail "Pin identity")
valid values = List.length values<=32 && List.length values==List.length (List.foldl (\s seen -> if List.member s seen then seen else s::seen) [] values) && bytes (E.encode 0 (E.list E.string values))<=3000

decoder : D.Decoder Snapshot
decoder = strict ["revision","identities"] (D.map2 Snapshot (D.field "revision" (UInt64.decoder |> D.andThen (\n -> if n/=UInt64.zero then D.succeed n else D.fail "Pin revision"))) (D.field "identities" (D.list identityDecoder |> D.andThen (\values -> if valid values then D.succeed values else D.fail "Pin bounds"))))
encode : Snapshot -> E.Value
encode snapshot = E.object [("revision",E.string (UInt64.string snapshot.revision)),("identities",E.list E.string snapshot.identities)]
observe : Maybe Snapshot -> Model -> Model
observe snapshot model =
    case snapshot of
        Nothing -> {model | snapshot=Nothing,pending=Nothing,notice="Pin storage unavailable. Refresh applications to try again."}
        Just value ->
            if model.snapshot |> Maybe.map (\old -> UInt64.compare value.revision old.revision==LT) |> Maybe.withDefault False then model else
                {model | snapshot=Just value,pending=Nothing,notice=""}
writable : Model -> Bool
writable model = model.snapshot/=Nothing && model.pending==Nothing
propose : Counter -> List String -> Model -> (Model,Maybe E.Value)
propose request values model =
    case model.snapshot of
        Just snapshot ->
            if not (writable model) || not (valid values) || values==snapshot.identities then (model,Nothing) else
                ({model | pending=Just {request=request,identities=values},notice="Saving pin order…"},Just (encode {snapshot | identities=values}))
        Nothing -> (model,Nothing)
receive : Counter -> String -> Maybe Snapshot -> Model -> Model
receive request status snapshot model =
    case model.pending of
        Just pending ->
            if pending.request/=request then model else
                if status=="Saved" && (snapshot |> Maybe.map (\s -> s.identities==pending.identities && (model.snapshot |> Maybe.map (\old -> UInt64.compare s.revision old.revision==GT) |> Maybe.withDefault False)) |> Maybe.withDefault False) then
                    {model | snapshot=snapshot,pending=Nothing,notice="Pin order saved."}
                else if status=="Refused" then {model | pending=Nothing,notice="Pin change refused. Refresh applications and choose again."}
                else {model | notice="Pin save not confirmed. Refresh applications to read the order; the change will not be repeated."}
        Nothing -> model

toggle : String -> List String -> List String
toggle identity values = if List.member identity values then List.filter ((/=) identity) values else values++[identity]
move : String -> Int -> List String -> List String
move identity direction values =
    let index = List.indexedMap Tuple.pair values |> List.filter (\(_,s) -> s==identity) |> List.head |> Maybe.map Tuple.first
        at n = List.drop n values |> List.head
    in case index of
        Just n ->
            let target=n+direction
            in if not (List.member direction [-1,1]) || target<0 || target>=List.length values then values else
                case at target of
                    Just other -> List.indexedMap (\i s -> if i==n then other else if i==target then identity else s) values
                    Nothing -> values
        Nothing -> values

bytes : String -> Int
bytes = String.foldl (\c total -> total + (if Char.toCode c<=127 then 1 else if Char.toCode c<=2047 then 2 else if Char.toCode c<=65535 then 3 else 4)) 0
