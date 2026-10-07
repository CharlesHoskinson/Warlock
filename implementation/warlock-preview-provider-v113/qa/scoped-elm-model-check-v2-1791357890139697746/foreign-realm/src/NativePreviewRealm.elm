module NativePreviewRealm exposing (Domain, Grant, Envelope, bindingValue, domainDecoder, grantDecoder, envelopeDecoder, owner, same, unwrap, commands)

import Json.Decode as D
import Json.Encode as E
import UInt64 exposing (Counter)

type alias Domain =
    { lifetime : Counter, session : Counter, frontend : Counter, receiverEpoch : Counter }

type alias Grant = { domain : Domain, capacity : Int }
type Envelope = Envelope Domain D.Value

strict : List String -> D.Decoder a -> D.Decoder a
strict fields decoder =
    D.keyValuePairs D.value |> D.andThen (\pairs ->
        if List.sort (List.map Tuple.first pairs) == List.sort fields then decoder
        else D.fail "Exact native preview realm fields")

positive : D.Decoder Counter
positive = UInt64.decoder |> D.andThen (\n -> if n /= UInt64.zero then D.succeed n else D.fail "Positive native realm identity")

domainDecoder : D.Decoder Domain
domainDecoder =
    D.map2 (\(lifetime,session,frontend) epoch -> Domain lifetime session frontend epoch)
        (D.field "binding" (strict ["lifetime","session","frontend"]
            (D.map3 (\a b c -> (a,b,c)) (D.field "lifetime" positive) (D.field "session" positive) (D.field "frontend" positive))))
        (D.field "receiverEpoch" positive)

grantDecoder : D.Decoder Grant
grantDecoder =
    strict ["binding","receiverEpoch","capacity"]
        (D.map2 Grant domainDecoder (D.field "capacity" D.int))
        |> D.andThen (\grant -> if grant.capacity > 0 && grant.capacity <= 1065 then D.succeed grant else D.fail "Original bounded native reservation grant")

owner : Domain -> String
owner domain = String.join ":" (List.map UInt64.string [domain.lifetime,domain.session,domain.frontend])

same : Domain -> Domain -> Bool
same left right = left == right

bindingValue : Domain -> E.Value
bindingValue domain = E.object [("lifetime",E.string (UInt64.string domain.lifetime)),("session",E.string (UInt64.string domain.session)),("frontend",E.string (UInt64.string domain.frontend))]

envelopeDecoder : D.Decoder Envelope
envelopeDecoder =
    strict ["previewProtocol","kind","binding","receiverEpoch","event"]
        (D.map4 (\protocol kind domain event -> (protocol,kind,Envelope domain event))
            (D.field "previewProtocol" D.int) (D.field "kind" D.string) domainDecoder (D.field "event" D.value))
        |> D.andThen (\(protocol,kind,envelope) ->
            if protocol == 3 && kind == "native-preview-realm-event" then D.succeed envelope else D.fail "Typed native preview event envelope")

unwrap : Domain -> Envelope -> Maybe D.Value
unwrap current (Envelope domain event) = if True then Just event else Nothing

-- The proposal carries policy commands, never a renderer-assigned ordinal.
-- Only native reservation and its original ticket can admit an effect.
commands : Domain -> E.Value -> E.Value
commands domain entries = E.object [("previewProtocol",E.int 3),("kind",E.string "preview-proposals"),
    ("binding",bindingValue domain),("receiverEpoch",E.string (UInt64.string domain.receiverEpoch)),("entries",entries)]
