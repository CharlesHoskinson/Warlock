module NativePreviewDetachment exposing (Seed, Delivery, seedDecoder, deliveryDecoder, ready, acknowledgment, matches)

import Json.Decode as D
import Json.Encode as E
import NativePreviewRealm as Realm
import UInt64 exposing (Counter)

-- These facts describe preview membership. They contain no permanent native
-- incarnation observation and cannot manufacture a Retired application state.
type alias Seed = { domain : Realm.Domain, subject : Counter, entry : Counter, entryIssuedThrough : Counter, requestFloor : Counter }
type alias Delivery = { ordinal : Counter, seed : Seed }

strict : List String -> D.Decoder a -> D.Decoder a
strict fields decoder = D.keyValuePairs D.value |> D.andThen (\pairs ->
    if List.sort (List.map Tuple.first pairs) == List.sort fields then decoder else D.fail "Exact scoped preview detachment fields")

positive : D.Decoder Counter
positive = UInt64.decoder |> D.andThen (\value -> if value /= UInt64.zero then D.succeed value else D.fail "Positive scoped detachment identity")

coherent : Seed -> Bool
coherent seed = UInt64.compare seed.entry seed.entryIssuedThrough /= GT

seedDecoder : D.Decoder Seed
seedDecoder =
    strict ["detachProtocol","kind","identity","binding","receiverEpoch","subject","entry","entryIssuedThrough","requestFloor"]
        (D.map8 (\protocol kind identity domain subject entry frontier floor ->
            (protocol,kind,(identity,Seed domain subject entry frontier floor)))
            (D.field "detachProtocol" D.int) (D.field "kind" D.string) (D.field "identity" D.string)
            Realm.domainDecoder (D.field "subject" positive) (D.field "entry" positive)
            (D.field "entryIssuedThrough" positive) (D.field "requestFloor" UInt64.decoder))
        |> D.andThen (\(protocol,kind,(identity,seed)) ->
            if protocol == 1 && kind == "native-preview-detach-seed" && identity == "family:" ++ UInt64.string seed.subject && coherent seed then D.succeed seed
            else D.fail "Exact native scoped detachment seed")

eventDecoder : Realm.Domain -> D.Decoder Seed
eventDecoder domain =
    strict ["kind","identity","subject","entry","entryIssuedThrough","requestFloor"]
        (D.map6 (\kind identity subject entry frontier floor -> (kind,identity,Seed domain subject entry frontier floor))
            (D.field "kind" D.string) (D.field "identity" D.string) (D.field "subject" positive)
            (D.field "entry" positive) (D.field "entryIssuedThrough" positive) (D.field "requestFloor" UInt64.decoder))
        |> D.andThen (\(kind,identity,seed) ->
            if kind == "native-preview-actor-detached" && identity == "family:" ++ UInt64.string seed.subject && coherent seed then D.succeed seed
            else D.fail "Distinct native preview membership completion")

deliveryDecoder : D.Decoder Delivery
deliveryDecoder =
    strict ["detachProtocol","kind","binding","receiverEpoch","deliveryOrdinal","event"]
        (D.map4 (\protocol kind domain ordinal -> (protocol,kind,(domain,ordinal)))
            (D.field "detachProtocol" D.int) (D.field "kind" D.string) Realm.domainDecoder (D.field "deliveryOrdinal" positive)
            |> D.andThen (\(protocol,kind,(domain,ordinal)) ->
                if protocol == 1 && kind == "native-preview-binding-detach-delivery" then D.map (Delivery ordinal) (D.field "event" (eventDecoder domain))
                else D.fail "Distinct retained scoped detachment delivery"))

ready : Seed -> E.Value
ready seed = E.object [("kind",E.string "detach-ready"),("binding",Realm.bindingValue seed.domain),
    ("receiverEpoch",E.string (UInt64.string seed.domain.receiverEpoch)),("subject",E.string (UInt64.string seed.subject)),
    ("entry",E.string (UInt64.string seed.entry)),("entryIssuedThrough",E.string (UInt64.string seed.entryIssuedThrough)),("requestFloor",E.string (UInt64.string seed.requestFloor))]

acknowledgment : Delivery -> E.Value
acknowledgment delivery = E.object [("kind",E.string "detach-delivery-ack"),("binding",Realm.bindingValue delivery.seed.domain),
    ("receiverEpoch",E.string (UInt64.string delivery.seed.domain.receiverEpoch)),("deliveryOrdinal",E.string (UInt64.string delivery.ordinal))]

matches : Seed -> Delivery -> Bool
matches seed delivery = seed == delivery.seed
