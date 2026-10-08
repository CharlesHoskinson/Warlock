module Transfer exposing (Proposal, propose, matches, decoder, encode, destinations)

import Char
import GeometryProjection as Geometry
import Json.Decode as D
import Json.Encode as E
import UInt64 exposing (Counter)

type alias Proposal = { source : String, sourceGeneration : Counter, destination : String }

ordinary value =
    not (String.isEmpty value) && not (String.startsWith "0" value)
        && String.all Char.isDigit value
        && (String.length value<19 || (String.length value==19 && value<="9223372036854775807"))

decoder : D.Decoder Proposal
decoder = D.keyValuePairs D.value |> D.andThen (\pairs ->
    if List.sort (List.map Tuple.first pairs)/=["destination","source","sourceGeneration"] then D.fail "Transfer fields" else
    D.map3 Proposal (D.field "source" D.string) (D.field "sourceGeneration" UInt64.decoder) (D.field "destination" D.string)
        |> D.andThen (\p -> if ordinary p.source && ordinary p.destination && p.source/=p.destination && p.sourceGeneration/=UInt64.zero then D.succeed p else D.fail "Transfer workspace identity"))

propose : Geometry.Snapshot -> Counter -> String -> Maybe Proposal
propose snapshot root destination =
    Geometry.window root snapshot |> Maybe.andThen (\w ->
        case (w.workspace,w.workspaceGeneration) of
            (Just source,Just generation) ->
                if snapshot.blocked || w.owner/=Nothing || w.grouped || not (ordinary source && ordinary destination) || source==destination then Nothing
                else Just {source=source,sourceGeneration=generation,destination=destination}
            _ -> Nothing)

matches : Geometry.Snapshot -> Counter -> Proposal -> Bool
matches snapshot root p = propose snapshot root p.destination==Just p

destinations : Geometry.Snapshot -> List String
destinations snapshot =
    List.foldl (\w ids -> case w.workspace of
        Just id -> if ordinary id && not (List.member id ids) then ids++[id] else ids
        Nothing -> ids) (List.range 1 10 |> List.map String.fromInt) snapshot.windows

encode : Proposal -> E.Value
encode p = E.object [("source",E.string p.source),("sourceGeneration",E.string (UInt64.string p.sourceGeneration)),("destination",E.string p.destination)]
