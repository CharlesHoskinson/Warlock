module Catalog exposing (Snapshot, Entry, EntryId, decode, entries, id, lookup, intent, scope, search)
import Dict exposing (Dict)
import SearchFold
import Json.Decode as D
import Json.Encode as E
import UInt64 exposing (Counter)
type EntryId = EntryId String
type alias Entry = { identity : EntryId, name : String, iconHint : String, wmclass : String, genericName : String, keywords : List String }
type Snapshot = Snapshot Counter Counter (Dict String Entry)
id (EntryId value) = value
strict names decoder = D.keyValuePairs D.value |> D.andThen (\fields -> if List.sort (List.map Tuple.first fields)==List.sort names then decoder else D.fail "Unexpected catalog fields")
positive = UInt64.decoder |> D.andThen (\value -> if value/=UInt64.zero then D.succeed value else D.fail "Zero catalog authority")
text limit nonempty = D.string |> D.andThen (\value -> if String.length value<=limit && (not nonempty || not (String.isEmpty value)) && not (String.any (\c -> Char.toCode c<32) value) then D.succeed value else D.fail "Catalog text")
entryDecoder = strict ["id","name","iconHint","wmclass"] (D.map4 (\identity name iconHint wmclass -> Entry identity name iconHint wmclass "" []) (D.field "id" (D.map EntryId (text 256 True))) (D.field "name" (text 512 False)) (D.field "iconHint" (text 512 False)) (D.field "wmclass" (text 512 False)))
entryDecoder2 = strict ["id","name","iconHint","wmclass","genericName","keywords"] (D.map6 Entry (D.field "id" (D.map EntryId (text 256 True))) (D.field "name" (text 512 False)) (D.field "iconHint" (text 512 False)) (D.field "wmclass" (text 512 False)) (D.field "genericName" (text 512 False)) (D.field "keywords" (D.list (text 128 False) |> D.andThen (\values -> if List.length values<=64 then D.succeed values else D.fail "Keyword capacity"))))

search : String -> Snapshot -> List Entry
search raw snapshot =
    let query = SearchFold.fold (String.trim raw)
        words = String.words query
        rank entry =
            let name = SearchFold.fold entry.name
                tokens = (entry.name :: entry.genericName :: entry.keywords) |> List.concatMap (SearchFold.fold >> String.words)
            in if String.isEmpty query then Just 0 else if name==query then Just 0 else if String.startsWith query name then Just 1 else if List.all (\word -> List.any (String.startsWith word) tokens) words then Just 2 else Nothing
        compare (aRank,a) (bRank,b) = case Basics.compare aRank bRank of
            EQ -> Basics.compare (id a.identity) (id b.identity)
            order -> order
    in entries snapshot |> List.filterMap (\entry -> rank entry |> Maybe.map (\value -> (value,entry))) |> List.sortWith compare |> List.map Tuple.second

entries (Snapshot _ _ values) = Dict.values values
lookup value (Snapshot _ _ values) = Dict.get value values
intent request entry (Snapshot lifetime generation values) =
    if request==UInt64.zero || not (Dict.member (id entry) values) then Nothing else
        Just (E.object [("request",E.string (UInt64.string request)),("lifetime",E.string (UInt64.string lifetime)),("generation",E.string (UInt64.string generation)),("entry",E.string (id entry))])
decode raw =
    let
        protocol = D.field "catalogProtocol" D.int |> D.andThen (\value -> if List.member value [1,2] then D.succeed value else D.fail "Catalog version")
        entryList version = D.list D.value |> D.andThen (\values -> if List.length values<=2048 then D.list (if version==2 then entryDecoder2 else entryDecoder) else D.fail "Catalog capacity")
        decoder = protocol |> D.andThen (\value -> strict ["catalogProtocol","lifetime","generation","entries"] (D.map3 (\lifetime generation values -> (lifetime,generation,values)) (D.field "lifetime" positive) (D.field "generation" positive) (D.field "entries" (entryList value))))
    in D.decodeValue decoder raw |> Result.mapError D.errorToString |> Result.andThen (\(lifetime,generation,values) ->
        let dict = Dict.fromList (List.map (\entry -> (id entry.identity,entry)) values)
        in if Dict.size dict/=List.length values then Err "Duplicate desktop identity" else Ok (Snapshot lifetime generation dict))

scope : Snapshot -> { lifetime : Counter, generation : Counter }
scope (Snapshot lifetime generation _) = { lifetime = lifetime, generation = generation }
