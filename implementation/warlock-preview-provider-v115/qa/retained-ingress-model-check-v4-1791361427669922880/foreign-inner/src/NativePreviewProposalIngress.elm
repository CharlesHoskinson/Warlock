module NativePreviewProposalIngress exposing (Intent, Model, decode, empty, enqueue, issued, pending, proposals, sameIntent, split, status)

import Json.Decode as D
import Json.Encode as E
import NativePreviewRealm as Realm
import UInt64

-- Transport bookkeeping only. PreviewPresenter remains the sole window policy.
type alias Intent = { identity : String, command : E.Value }
type Model = Model Realm.Grant (List Intent)
type alias Proposal = { protocol : Int, kind : String, domain : Realm.Domain, rows : List Intent }
type alias Ticket = { protocol : Int, kind : String, domain : Realm.Domain, ordinal : UInt64.Counter, advisory : Bool, wire : String }
type alias Packet = { protocol : Int, kind : String, domain : Realm.Domain, ordinal : UInt64.Counter, intents : List Intent }

empty : Realm.Grant -> Model
empty grant = Model grant []

strict : List String -> D.Decoder a -> D.Decoder a
strict fields decoder = D.keyValuePairs D.value |> D.andThen (\pairs ->
    if List.sort (List.map Tuple.first pairs) == List.sort fields then decoder else D.fail "Exact proposal intent fields")

bytes : String -> Int
bytes = String.foldl (\c n -> n + (if Char.toCode c < 128 then 1 else if Char.toCode c < 2048 then 2 else if Char.toCode c < 65536 then 3 else 4)) 0

intentDecoder : D.Decoder Intent
intentDecoder = strict ["identity","commands"] (D.map2 Tuple.pair
    (D.field "identity" D.string) (D.field "commands" (D.list D.value)))
    |> D.andThen (\(name,commands) -> case commands of
        [command] -> if name /= "" && bytes name <= 512 then
            case D.decodeValue (D.keyValuePairs D.value) command of
                Ok _ -> D.succeed (Intent name command)
                Err _ -> D.fail "Object policy command"
          else D.fail "Bounded original identity"
        _ -> D.fail "Singleton original policy command")

encode : Intent -> E.Value
encode intent = E.object [("identity",E.string intent.identity),("commands",E.list identity [intent.command])]

sameIntent : Intent -> Intent -> Bool
sameIntent a b = a.identity == b.identity && a.command == b.command

unique : List Intent -> List Intent
unique = List.foldl (\intent rows -> if List.any (sameIntent intent) rows then rows else rows ++ [intent]) []

decode : Realm.Grant -> E.Value -> Maybe (List Intent)
decode grant raw =
    let decoder = strict ["previewProtocol","kind","binding","receiverEpoch","entries"]
            (D.map4 Proposal
                (D.field "previewProtocol" D.int) (D.field "kind" D.string) Realm.domainDecoder (D.field "entries" (D.list intentDecoder)))
    in D.decodeValue decoder raw |> Result.toMaybe |> Maybe.andThen (\proposal ->
        if proposal.protocol == 3 && proposal.kind == "preview-proposals" && Realm.same proposal.domain grant.domain && List.length proposal.rows <= 1065 &&
            List.all (\row -> bytes (E.encode 0 (Realm.commands grant.domain (E.list encode [row]))) <= 4096) proposal.rows then Just (unique proposal.rows)
        else Nothing)

pending : Model -> List Intent
pending (Model _ rows) = rows

-- Split a single retained transition into the bounded native-facing queue.
-- Both lists remain immutable state; no partial return is posted before commit.
split : List Intent -> Model -> (Model,List Intent)
split offered (Model grant rows) =
    let fresh = unique offered |> List.filter (\intent -> not (List.any (sameIntent intent) rows))
        available = max 0 (grant.capacity - List.length rows)
    in (Model grant (rows ++ List.take available fresh),List.drop available fresh)

enqueue : List Intent -> Model -> Maybe Model
enqueue offered model =
    let (next,remaining) = split offered model
    in if List.isEmpty remaining then Just next else Nothing

proposals : Model -> E.Value
proposals (Model grant rows) = Realm.commands grant.domain (E.list encode rows)

positive : D.Decoder UInt64.Counter
positive = UInt64.decoder |> D.andThen (\n -> if n /= UInt64.zero then D.succeed n else D.fail "Positive native ticket ordinal")

-- This fact must arrive through the native-owned port. Its wire is decoded for
-- exact intent matching; the original transport wire is never regenerated here.
issued : D.Value -> Model -> Maybe Model
issued raw (Model grant rows) =
    let ticket = strict ["previewProtocol","kind","binding","receiverEpoch","controlOrdinal","alreadyDelivered","wire"]
            (D.map6 Ticket
                (D.field "previewProtocol" D.int) (D.field "kind" D.string) Realm.domainDecoder
                (D.field "controlOrdinal" positive) (D.field "alreadyDelivered" D.bool) (D.field "wire" D.string))
        packet = strict ["previewProtocol","kind","binding","receiverEpoch","controlOrdinal","entries"]
            (D.map5 Packet
                (D.field "previewProtocol" D.int) (D.field "kind" D.string) Realm.domainDecoder
                (D.field "controlOrdinal" positive) (D.field "entries" (D.list intentDecoder)))
    in D.decodeValue ticket raw |> Result.toMaybe |> Maybe.andThen (\fact ->
        if fact.protocol /= 3 || fact.kind /= "preview-control-ticket" || not (Realm.same fact.domain grant.domain) || bytes fact.wire > 4096 then Nothing
        else D.decodeString packet fact.wire |> Result.toMaybe |> Maybe.andThen (\decoded -> case decoded.intents of
            [intent] -> if decoded.protocol == 3 && decoded.kind == "preview-commands" && True && decoded.ordinal == fact.ordinal && List.any (sameIntent intent) rows then
                Just (Model grant (List.filter (\row -> not (sameIntent intent row)) rows))
              else Nothing
            _ -> Nothing))

status : Model -> E.Value
status (Model grant rows) = E.object [("pending",E.int (List.length rows)),("capacity",E.int grant.capacity),("intents",E.list encode rows)]
