module WindowObservation exposing (Snapshot, Row, replyDecoder, groups, fingerprint, rowsFor)

import Binding exposing (Binding)
import Char
import Json.Decode as D
import Json.Encode as E
import Set
import Taskbar
import UInt64 exposing (Counter)

type alias Row = { id : Counter, title : String, appId : String, states : List String, outputs : List Counter, parent : Maybe Counter }
type alias Snapshot = { owner : Counter, revision : Counter, outputs : List Counter, windows : List Row }

strict names decoder = D.keyValuePairs D.value |> D.andThen (\fields -> if List.sort (List.map Tuple.first fields)==List.sort names then decoder else D.fail "Unexpected observation fields")
positive = UInt64.decoder |> D.andThen (\value -> if value==UInt64.zero then D.fail "Zero observation identity" else D.succeed value)
bounded limit decoder = D.value |> D.andThen (\value -> case D.decodeValue (D.index limit D.value) value of
    Ok _ -> D.fail "Observation capacity"
    Err _ -> D.list decoder)
text = D.string |> D.andThen (\value -> if String.length value<=256 && not (String.any (\char -> let n=Char.toCode char in n<32 || n==127 || (n>=55296 && n<=57343)) value) then D.succeed value else D.fail "Observation text")
distinct values = List.length values==Set.size (Set.fromList values)
rowDecoder = strict ["id","title","appId","states","outputs","parent"]
    (D.map6 Row (D.field "id" positive) (D.field "title" text) (D.field "appId" text)
        (D.field "states" (bounded 4 D.string)) (D.field "outputs" (bounded 64 positive)) (D.field "parent" (D.nullable positive)))
root rows seen ident =
    if List.member ident seen then Nothing else
    rows |> List.filter (\row -> row.id==ident) |> List.head |> Maybe.andThen (\row -> case row.parent of
        Nothing -> Just ident
        Just parent -> root rows (ident::seen) parent)
valid snapshot =
    distinct (List.map UInt64.string snapshot.outputs) && distinct (List.map (.id >> UInt64.string) snapshot.windows)
        && List.all (\row -> distinct row.states && List.all (\state -> List.member state ["activated","maximized","minimized","fullscreen"]) row.states
            && distinct (List.map UInt64.string row.outputs) && List.all (\output -> List.member output snapshot.outputs) row.outputs
            && root snapshot.windows [] row.id/=Nothing) snapshot.windows
snapshotDecoder = strict ["owner","revision","view","outputs","windows"]
    (D.map5 (\owner revision _ outputs windows -> {owner=owner,revision=revision,outputs=outputs,windows=windows})
        (D.field "owner" positive) (D.field "revision" positive)
        (D.field "view" (D.string |> D.andThen (\view -> if view=="global" then D.succeed () else D.fail "Observation is global")))
        (D.field "outputs" (bounded 64 positive)) (D.field "windows" (bounded 256 rowDecoder)))
    |> D.andThen (\snapshot -> if valid snapshot then D.succeed snapshot else D.fail "Observation identity or graph")
replyDecoder : D.Decoder { binding : Binding, request : Counter, status : String, snapshot : Maybe Snapshot }
replyDecoder = strict ["protocolVersion","kind","binding","requestId","status","snapshot"]
    (D.map6 (\_ _ binding request status snapshot -> {binding=binding,request=request,status=status,snapshot=snapshot})
        (D.field "protocolVersion" (D.int |> D.andThen (\v -> if v==3 then D.succeed () else D.fail "Observation protocol")))
        (D.field "kind" (D.string |> D.andThen (\v -> if v=="window-observation" then D.succeed () else D.fail "Observation kind")))
        (D.field "binding" Binding.decoder) (D.field "requestId" positive) (D.field "status" D.string) (D.field "snapshot" (D.nullable snapshotDecoder)))
    |> D.andThen (\reply ->
        let owner = D.decodeValue (D.field "frontend" positive) (Binding.encode reply.binding) |> Result.toMaybe
        in if (reply.status=="Observed" && reply.snapshot/=Nothing && Maybe.map .owner reply.snapshot==owner)
            || (List.member reply.status ["Unknown","Unavailable"] && reply.snapshot==Nothing) then D.succeed reply else D.fail "Observation disposition")

groupKey row = "observed:" ++ (if String.isEmpty row.appId then "window:" ++ UInt64.string row.id else "application:" ++ row.appId)
groups : Snapshot -> List Taskbar.Group
groups snapshot =
    let family row = {root=row.id,label=row.title,application=row.appId,minimized=List.member "minimized" row.states,available=False,active=List.member "activated" row.states,attention=False}
        add row result =
            let key=groupKey row in
            if List.any (\group -> group.key==key) result then List.map (\group -> if group.key==key then {group|families=group.families++[family row]} else group) result
            else result++[{key=key,families=[family row]}]
    in snapshot.windows |> List.filter (\row -> row.parent==Nothing) |> List.sortWith (\a b -> UInt64.compare a.id b.id) |> List.foldl add []
rowsFor : String -> Snapshot -> List Row
rowsFor key snapshot =
    let roots=groups snapshot |> List.filter (\group -> group.key==key) |> List.concatMap (.families >> List.map .root)
    in List.filter (\row -> root snapshot.windows [] row.id |> Maybe.map (\ident -> List.member ident roots) |> Maybe.withDefault False) snapshot.windows
fingerprint : String -> Snapshot -> String
fingerprint key snapshot = E.encode 0 (E.object [("owner",E.string (UInt64.string snapshot.owner)),("handles",rowsFor key snapshot |> List.map (.id >> UInt64.string) |> List.sort |> E.list E.string)])
