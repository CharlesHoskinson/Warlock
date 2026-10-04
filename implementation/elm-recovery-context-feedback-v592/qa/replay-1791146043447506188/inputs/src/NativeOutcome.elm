module NativeOutcome exposing (valid)

{-| Shared protocol-3 outcome shape gate, including ordinary taskbar Activate.
This checks shape only. Shell and ReceiptRouter still check their own exact
operation identities. Callers must use the authenticated bounded native channel.
-}

import Binding
import Json.Decode as D
import UInt64

strict fields child =
    D.keyValuePairs D.value |> D.andThen (\pairs ->
        if List.sort (List.map Tuple.first pairs) == List.sort fields then child
        else D.fail "Outcome schema")

positive = UInt64.decoder |> D.andThen (\value ->
    if value == UInt64.zero then D.fail "Zero outcome identity" else D.succeed value)

exact name child expected = D.field name child |> D.andThen (\value ->
    if value == expected then D.succeed () else D.fail "Outcome protocol")

context = strict ["lifetime","epoch","output","revision"]
    (D.map4 (\_ _ _ _ -> ()) (D.field "lifetime" positive) (D.field "epoch" positive)
        (D.field "output" positive) (D.field "revision" positive))

intent protocolId = strict ["request","generation","incarnation","operation","context"]
    (D.map5 (\_ _ _ _ _ -> ()) (D.field "request" positive) (D.field "generation" positive)
        (D.field "incarnation" positive)
        (D.field "operation" D.string |> D.andThen (\value ->
            if List.member value (if protocolId==1 then ["minimize","restore","activate"] else ["maximize","restore-geometry"]) then D.succeed () else D.fail "Outcome operation"))
        (D.field "context" context))

decoderBody protocolId = strict ["protocolVersion","kind","effectProtocol","binding","intent","status","reason","revision","outputGeneration"]
    (D.map8 (\_ _ _ _ _ _ _ _ -> ())
        (exact "protocolVersion" D.int 3)
        (exact "kind" D.string "effect-outcome")
        (exact "effectProtocol" D.int protocolId)
        (D.field "binding" Binding.decoder)
        (D.field "intent" (intent protocolId))
        (D.field "status" D.string |> D.andThen (\value ->
            if List.member value ["Committed","Refused","Unknown"] then D.succeed () else D.fail "Outcome status"))
        (D.field "reason" D.string |> D.andThen (\value ->
            if String.length value <= 256 then D.succeed () else D.fail "Outcome reason"))
        (D.map2 (\_ _ -> ()) (D.field "revision" positive) (D.field "outputGeneration" positive)))

decoder = D.field "effectProtocol" D.int |> D.andThen (\protocolId -> if List.member protocolId [1,2] then decoderBody protocolId else D.fail "Effect protocol")

valid : D.Value -> Bool
valid value =
    case D.decodeValue decoder value of
        Ok _ -> True
        Err _ -> False
