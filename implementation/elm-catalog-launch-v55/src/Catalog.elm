module Catalog exposing (Snapshot, Entry, EntryId, decode, entries, id, lookup, intent)
import Dict exposing (Dict)
import Json.Decode as D
import Json.Encode as E
import UInt64 exposing (Counter)
type EntryId = EntryId String
type alias Entry = { identity : EntryId, name : String, iconHint : String, wmclass : String }
type Snapshot = Snapshot Counter Counter (Dict String Entry)
id (EntryId value) = value
strict names decoder = D.keyValuePairs D.value |> D.andThen (\fields -> if List.sort (List.map Tuple.first fields)==List.sort names then decoder else D.fail "Unexpected catalog fields")
positive = UInt64.decoder |> D.andThen (\value -> if value/=UInt64.zero then D.succeed value else D.fail "Zero catalog authority")
text limit nonempty = D.string |> D.andThen (\value -> if String.length value<=limit && (not nonempty || not (String.isEmpty value)) && not (String.any (\c -> Char.toCode c<32) value) then D.succeed value else D.fail "Catalog text")
entryDecoder = strict ["id","name","iconHint","wmclass"] (D.map4 Entry (D.field "id" (D.map EntryId (text 256 True))) (D.field "name" (text 512 False)) (D.field "iconHint" (text 512 False)) (D.field "wmclass" (text 512 False)))
entries (Snapshot _ _ values) = Dict.values values
lookup value (Snapshot _ _ values) = Dict.get value values
intent request entry (Snapshot lifetime generation values) =
    if request==UInt64.zero || not (Dict.member (id entry) values) then Nothing else
        Just (E.object [("request",E.string (UInt64.string request)),("lifetime",E.string (UInt64.string lifetime)),("generation",E.string (UInt64.string generation)),("entry",E.string (id entry))])
decode raw =
    let
        protocol = D.field "catalogProtocol" D.int |> D.andThen (\value -> if value==1 then D.succeed () else D.fail "Catalog version")
        entryList = D.list D.value |> D.andThen (\values -> if List.length values<=2048 then D.list entryDecoder else D.fail "Catalog capacity")
        decoder = strict ["catalogProtocol","lifetime","generation","entries"] (D.map4 (\_ lifetime generation values -> (lifetime,generation,values)) protocol (D.field "lifetime" positive) (D.field "generation" positive) (D.field "entries" entryList))
    in D.decodeValue decoder raw |> Result.mapError D.errorToString |> Result.andThen (\(lifetime,generation,values) ->
        let dict = Dict.fromList (List.map (\entry -> (id entry.identity,entry)) values)
        in if Dict.size dict/=List.length values then Err "Duplicate desktop identity" else Ok (Snapshot lifetime generation dict))
