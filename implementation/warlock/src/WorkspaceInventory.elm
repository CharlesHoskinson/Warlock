module WorkspaceInventory exposing (Row, Snapshot, factsDecoder, decode, coherent)

import Binding
import Char
import Json.Decode as D
import UInt64 exposing (Counter)

type alias Row = { identity : String, generation : Counter, monitor : Counter, outputOwnershipGeneration : Counter }
type alias Snapshot = { binding : Binding.Binding, request : Counter, sequence : Counter, revision : Counter, output : Counter, active : Maybe String, rows : List Row }
strict fields body = D.keyValuePairs D.value |> D.andThen (\pairs -> if List.sort (List.map Tuple.first pairs)==List.sort fields then body else D.fail "Workspace inventory schema")
positive = UInt64.decoder |> D.andThen (\n -> if n/=UInt64.zero then D.succeed n else D.fail "Zero workspace owner")
identityDecoder = D.string |> D.andThen (\s -> if not (String.isEmpty s) && String.all Char.isDigit s && not (String.startsWith "0" s) && (String.length s<19 || (String.length s==19 && s<="9223372036854775807")) then D.succeed s else D.fail "Ordinary workspace identity")
rowDecoder = strict ["identity","generation","monitor","outputOwnershipGeneration"] (D.map4 Row (D.field "identity" identityDecoder) (D.field "generation" positive) (D.field "monitor" UInt64.decoder) (D.field "outputOwnershipGeneration" positive))
factsDecoder = D.map2 Tuple.pair (D.field "activeWorkspace" (D.nullable identityDecoder)) (D.field "workspaces" (D.list rowDecoder)) |> D.andThen (\(active,rows) ->
    let ids=List.map .identity rows
        unique=List.length ids==List.length (List.foldl (\id xs -> if List.member id xs then xs else id::xs) [] ids)
        consistent row=List.all (\other -> row.generation/=other.generation || row.identity==other.identity) rows && List.all (\other -> row.monitor/=other.monitor || row.outputOwnershipGeneration==other.outputOwnershipGeneration) rows
    in if List.length rows<=256 && unique && List.all consistent rows && (active |> Maybe.map (\id -> List.member id ids) |> Maybe.withDefault True) then D.succeed (active,rows) else D.fail "Workspace inventory coherence")
decode raw = D.decodeValue (D.map7 (\binding request sequence revision output _ facts -> {binding=binding,request=request,sequence=sequence,revision=revision,output=output,active=Tuple.first facts,rows=Tuple.second facts})
    (D.field "binding" Binding.decoder) (D.field "requestId" positive) (D.field "sequence" positive) (D.field "revision" positive) (D.field "outputGeneration" positive)
    (D.field "geometryProtocol" D.int |> D.andThen (\n -> if n==3 then D.succeed () else D.fail "Workspace inventory version")) (D.field "facts" factsDecoder)) raw |> Result.toMaybe

-- Inventory and window metadata must belong to the same accepted native receipt.
coherent inventory geometry =
    inventory.binding==geometry.binding && inventory.request==geometry.request && inventory.sequence==geometry.sequence && inventory.revision==geometry.context.revision && inventory.output==geometry.context.output &&
    List.all (\window -> case window.workspace of
        Just workspace -> if String.startsWith "-" workspace || workspace=="0" then True else
            List.any (\row -> row.identity==workspace && Just row.generation==window.workspaceGeneration && Just row.monitor==window.monitor && Just row.outputOwnershipGeneration==window.outputOwnershipGeneration) inventory.rows
        Nothing -> True) geometry.windows
