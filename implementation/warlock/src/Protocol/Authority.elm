module Protocol.Authority exposing (Counter, compareCounter, Binding, Context, Intent, Scope, Selection, bindingDecoder, contextDecoder, counterDecoder, counterString, encodeBinding, encodeIntent, encodeSelection, intentDecoder, selectionDecoder, strict)

import Json.Decode as D
import Json.Encode as E

type Counter = Counter String
counterString (Counter value) = value
compareCounter (Counter left) (Counter right) = case Basics.compare (String.length left) (String.length right) of
    EQ -> Basics.compare left right
    order -> order
counterDecoder : D.Decoder Counter
counterDecoder = D.string |> D.andThen (\v ->
    if String.length v > 0 && String.length v <= 20 && String.all (\c -> c >= '0' && c <= '9') v && not (String.startsWith "0" v) && (String.length v < 20 || v <= "18446744073709551615") then D.succeed (Counter v) else D.fail "noncanonical positive uint64")
strict fields child = D.keyValuePairs D.value |> D.andThen (\pairs -> if List.sort (List.map Tuple.first pairs) == List.sort fields then child else D.fail "unexpected fields")
type alias Binding = { lifetime : Counter, session : Counter, frontend : Counter }
type alias Context = { lifetime : Counter, epoch : Counter, output : Counter, revision : Counter }
type alias Intent = { request : Counter, generation : Counter, incarnation : Counter, operation : String, context : Context }
type alias Scope = { id : Counter, generation : Counter }
type alias Selection = { selectionId : String, scope : Scope, publication : Counter, lease : Counter, controlId : String, acceptedMonotonicNs : Counter, deadlineMonotonicNs : Counter }

bindingDecoder = strict ["lifetime","session","frontend"] (D.map3 Binding (D.field "lifetime" counterDecoder) (D.field "session" counterDecoder) (D.field "frontend" counterDecoder))
contextDecoder = strict ["lifetime","epoch","output","revision"] (D.map4 Context (D.field "lifetime" counterDecoder) (D.field "epoch" counterDecoder) (D.field "output" counterDecoder) (D.field "revision" counterDecoder))
intentDecoder = strict ["request","generation","incarnation","operation","context"] (D.map5 Intent (D.field "request" counterDecoder) (D.field "generation" counterDecoder) (D.field "incarnation" counterDecoder) (D.field "operation" (D.string |> D.andThen (\x -> if x == "restore" then D.succeed x else D.fail "unsupported operation"))) (D.field "context" contextDecoder))
scopeDecoder = strict ["id","generation"] (D.map2 Scope (D.field "id" counterDecoder) (D.field "generation" counterDecoder))
hex c = (c >= '0' && c <= '9') || (c >= 'a' && c <= 'f')
utf8Bytes = String.foldl (\c n -> let code = Char.toCode c in n + (if code <= 127 then 1 else if code <= 2047 then 2 else if code <= 65535 then 3 else 4)) 0
add xs ys carry = case (xs,ys) of
    ([],[]) -> if carry == 0 then [] else [carry]
    (x::rest,[]) -> let n = x + carry in modBy 10 n :: add rest [] (n // 10)
    ([],y::rest) -> let n = y + carry in modBy 10 n :: add [] rest (n // 10)
    (x::a,y::b) -> let n = x + y + carry in modBy 10 n :: add a b (n // 10)
plusBudget value = String.toList value |> List.reverse |> List.map (\c -> Char.toCode c - Char.toCode '0') |> (\digits -> add digits [0,0,0,0,0,0,0,0,0,2] 0) |> List.reverse |> List.map (\n -> Char.fromCode (n + Char.toCode '0')) |> String.fromList
selectionDecoder = strict ["selectionId","scope","publication","lease","controlId","clock","acceptedMonotonicNs","deadlineMonotonicNs"]
    (D.map8 (\id scope publication lease control clock accepted deadline -> (Selection id scope publication lease control accepted deadline,clock)) (D.field "selectionId" D.string) (D.field "scope" scopeDecoder) (D.field "publication" counterDecoder) (D.field "lease" counterDecoder) (D.field "controlId" D.string) (D.field "clock" D.string) (D.field "acceptedMonotonicNs" counterDecoder) (D.field "deadlineMonotonicNs" counterDecoder))
    |> D.andThen (\(s,clock) -> if String.length s.selectionId == 32 && String.all hex s.selectionId && not (String.isEmpty s.controlId) && utf8Bytes s.controlId <= 512 && not (String.contains "\u{0000}" s.controlId) && clock == "CLOCK_MONOTONIC" && plusBudget (counterString s.acceptedMonotonicNs) == counterString s.deadlineMonotonicNs then D.succeed s else D.fail "invalid selection")
counter = counterString >> E.string
encodeBinding b = E.object [("lifetime",counter b.lifetime),("session",counter b.session),("frontend",counter b.frontend)]
encodeIntent i = E.object [("request",counter i.request),("generation",counter i.generation),("incarnation",counter i.incarnation),("operation",E.string i.operation),("context",E.object [("lifetime",counter i.context.lifetime),("epoch",counter i.context.epoch),("output",counter i.context.output),("revision",counter i.context.revision)])]
encodeSelection s = E.object [("selectionId",E.string s.selectionId),("scope",E.object [("id",counter s.scope.id),("generation",counter s.scope.generation)]),("publication",counter s.publication),("lease",counter s.lease),("controlId",E.string s.controlId),("clock",E.string "CLOCK_MONOTONIC"),("acceptedMonotonicNs",counter s.acceptedMonotonicNs),("deadlineMonotonicNs",counter s.deadlineMonotonicNs)]
