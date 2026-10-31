module Protocol.Wire exposing (Event(..), Identity, Outcome, Status(..), Historical, LookupQuery, LookupResult(..), Member(..), Batch, decoder, encodeEnvelope)

{-| Decodes already framed, authenticated Haskell port values. This cannot prove
raw UTF-8, duplicate-key handling or source authentication. -}
import Protocol.Authority as A
import Json.Decode as D
import Json.Encode as E

type alias Identity = { binding : A.Binding, intent : A.Intent, selectionId : String, deadlineMonotonicNs : A.Counter, preparedId : A.Counter }
type Status = Committed | Refused String | Cancelled | Unknown
type alias Outcome = { identity : Identity, status : Status, revision : A.Counter, outputGeneration : A.Counter }
type alias Historical = { deliveryBinding : A.Binding, key : String, originalBinding : A.Binding, intent : A.Intent, selection : A.Selection, preparedId : A.Counter, certificate : Outcome, ackState : String, acknowledgement : Maybe Identity }
type alias LookupQuery = { deliveryBinding : A.Binding, requestId : A.Counter, key : String, originalBinding : A.Binding, intent : A.Intent, selection : A.Selection, preparedId : Maybe A.Counter }
type LookupResult = Absent | LookupUnknown | LookupPrepared A.Counter | SettlementAvailable

type Member = Negotiation A.Counter | Preparation A.Intent String | Decision A.Intent String A.Counter A.Counter String
type alias Batch = { binding : A.Binding, batchId : String, packetSHA256 : String, members : List Member }
type Event = Hello A.Binding | Capabilities A.Binding A.Counter | Selected A.Binding A.Selection | Prepared Identity | Observed Outcome | History Historical | BatchRegistered Batch | BatchDisposition Batch String | LookupResponse LookupQuery LookupResult

exact field fieldDecoder expected = D.field field fieldDecoder |> D.andThen (\value -> if value == expected then D.succeed () else D.fail "unexpected protocol field")
hex c = (c >= '0' && c <= '9') || (c >= 'a' && c <= 'f')
identifier length = D.string |> D.andThen (\value -> if String.length value == length && String.all hex value then D.succeed value else D.fail "invalid opaque id")
identityDecoder = A.strict ["binding","intent","selectionId","deadlineMonotonicNs","preparedId"] (D.map5 Identity (D.field "binding" A.bindingDecoder) (D.field "intent" A.intentDecoder) (D.field "selectionId" (identifier 32)) (D.field "deadlineMonotonicNs" A.counterDecoder) (D.field "preparedId" A.counterDecoder))
reasons = ["original-deadline-expired","ambiguous-or-ineligible-restore-focus","dependency-mismatch","exclusive-input","family-state-mismatch","implicit-transfer-required","ineligible-family","ineligible-workspace-owner","invalid-family","invalid-family-root","mixed-family-workspace-owner","native-operation-bound","native-operation-unresolved","native-pointer-owned","navigation-family-state-changed","navigation-recipient-changed","navigation-refused","seat-grab","stale-incarnation","state-bound","superseded-switcher-selection","switcher-cancelled-or-retired","unsupported-operation","workspace-navigation-unresolved"]
statusDecoder = D.map2 Tuple.pair (D.field "status" D.string) (D.field "reason" D.string) |> D.andThen (\(status,reason) ->
    case (status,reason) of
        ("Committed","applied") -> D.succeed Committed
        ("Cancelled","cancelled-before-commit") -> D.succeed Cancelled
        ("Unknown","effect-unproven") -> D.succeed Unknown
        ("Refused",_) -> if List.member reason reasons then D.succeed (Refused reason) else D.fail "unsupported refusal"
        _ -> D.fail "invalid terminal status/reason")
outcomeDecoder = A.strict ["binding","intent","selectionId","deadlineMonotonicNs","preparedId","status","reason","revision","outputGeneration"]
    (D.map4 Outcome (D.map5 Identity (D.field "binding" A.bindingDecoder) (D.field "intent" A.intentDecoder) (D.field "selectionId" (identifier 32)) (D.field "deadlineMonotonicNs" A.counterDecoder) (D.field "preparedId" A.counterDecoder)) statusDecoder (D.field "revision" A.counterDecoder) (D.field "outputGeneration" A.counterDecoder))

historyDecoder = A.strict ["deliveryBinding","key","originalBinding","intent","selection","preparedId","certificate","ackState","acknowledgement","executionAuthorized"]
    (D.map2 (\first second -> {deliveryBinding=first.delivery,key=first.key,originalBinding=first.original,intent=first.intent,selection=first.selection,preparedId=second.prepared,certificate=second.certificate,ackState=second.ack,acknowledgement=second.acknowledgement,authorized=second.authorized})
        (D.map5 (\delivery key original intent selection -> {delivery=delivery,key=key,original=original,intent=intent,selection=selection}) (D.field "deliveryBinding" A.bindingDecoder) (D.field "key" (identifier 64)) (D.field "originalBinding" A.bindingDecoder) (D.field "intent" A.intentDecoder) (D.field "selection" A.selectionDecoder))
        (D.map5 (\prepared certificate ack acknowledgement authorized -> {prepared=prepared,certificate=certificate,ack=ack,acknowledgement=acknowledgement,authorized=authorized}) (D.field "preparedId" A.counterDecoder) (D.field "certificate" outcomeDecoder) (D.field "ackState" D.string) (D.field "acknowledgement" (D.nullable identityDecoder)) (D.field "executionAuthorized" D.bool)))
    |> D.andThen (\h ->
        let
            id = h.certificate.identity
            validAck = case (h.ackState,h.acknowledgement) of
                ("not-sent",Nothing) -> True
                ("pending",Nothing) -> True
                ("acknowledged",Just ack) -> ack == id
                _ -> False
        in if not h.authorized && h.deliveryBinding.lifetime == h.originalBinding.lifetime && h.intent.context.lifetime==h.originalBinding.lifetime && h.intent.context.epoch==h.originalBinding.frontend && id.binding==h.originalBinding && id.intent==h.intent && id.selectionId==h.selection.selectionId && id.deadlineMonotonicNs==h.selection.deadlineMonotonicNs && id.preparedId==h.preparedId && h.certificate.status/=Unknown && validAck then D.succeed (Historical h.deliveryBinding h.key h.originalBinding h.intent h.selection h.preparedId h.certificate h.ackState h.acknowledgement) else D.fail "historical identity mismatch")

memberDecoder = D.field "kind" D.string |> D.andThen (\kind -> case kind of
    "negotiate" -> A.strict ["kind","requestId"] (D.field "requestId" A.counterDecoder |> D.map Negotiation)
    "prepare" -> A.strict ["kind","intent","selectionId"] (D.map2 Preparation (D.field "intent" A.intentDecoder) (D.field "selectionId" (identifier 32)))
    "decision" -> A.strict ["kind","intent","selectionId","deadlineMonotonicNs","preparedId","decision"] (D.map5 Decision (D.field "intent" A.intentDecoder) (D.field "selectionId" (identifier 32)) (D.field "deadlineMonotonicNs" A.counterDecoder) (D.field "preparedId" A.counterDecoder) (D.field "decision" (D.string |> D.andThen (\value -> if List.member value ["commit","cancel"] then D.succeed value else D.fail "invalid decision"))))
    _ -> D.fail "unsupported batch member")
batchFields = ["binding","batchId","packetSHA256","members"]
batchBody = D.map4 Batch (D.field "binding" A.bindingDecoder) (D.field "batchId" (identifier 32)) (D.field "packetSHA256" (identifier 64)) (D.field "members" (D.list memberDecoder)) |> D.andThen (\batch ->
    let unique=List.foldl (\member seen -> if List.member member seen then seen else member::seen) [] batch.members
    in if List.isEmpty batch.members || List.length batch.members>16 || List.length unique/=List.length batch.members then D.fail "batch member bound" else D.succeed batch)

lookupFields = ["deliveryBinding","requestId","key","originalBinding","intent","selection","preparedId"]
lookupQueryDecoder = D.map7 LookupQuery (D.field "deliveryBinding" A.bindingDecoder) (D.field "requestId" A.counterDecoder) (D.field "key" (identifier 64)) (D.field "originalBinding" A.bindingDecoder) (D.field "intent" A.intentDecoder) (D.field "selection" A.selectionDecoder) (D.field "preparedId" (D.nullable A.counterDecoder)) |> D.andThen (\q -> if q.intent.context.lifetime == q.originalBinding.lifetime && q.intent.context.epoch == q.originalBinding.frontend then D.succeed q else D.fail "lookup original binding mismatch")
lookupResultDecoder = A.strict (lookupFields ++ ["result","observedPreparedId"]) (D.map3 (\query result observed -> (query,result,observed)) lookupQueryDecoder (D.field "result" D.string) (D.field "observedPreparedId" (D.nullable A.counterDecoder))) |> D.andThen (\(query,result,observed) ->
    case (result,observed) of
        ("absent",Nothing) -> D.succeed (LookupResponse query Absent)
        ("unknown",Nothing) -> D.succeed (LookupResponse query LookupUnknown)
        ("settlement-available",Nothing) -> D.succeed (LookupResponse query SettlementAvailable)
        ("prepared",Just prepared) -> if query.preparedId == Nothing || query.preparedId == Just prepared then D.succeed (LookupResponse query (LookupPrepared prepared)) else D.fail "prepared identity mismatch"
        _ -> D.fail "invalid lookup result")

decoder : D.Decoder Event
decoder = A.strict ["version","kind","body"] (D.map3 (\version kind body -> (version,kind,body)) (D.field "version" D.int) (D.field "kind" D.string) (D.field "body" D.value)) |> D.andThen (\(version,kind,body) ->
    let decode child = case D.decodeValue child body of
            Ok value -> D.succeed value
            Err _ -> D.fail "invalid body"
    in if version /= 2 then D.fail "unsupported version" else case kind of
        "lookup-result" -> decode lookupResultDecoder
        "hello" -> decode (A.strict ["binding"] (D.field "binding" A.bindingDecoder |> D.map Hello))
        "capabilities" -> decode (A.strict ["binding","requestId","operations","maxPreparedPerSession","maxPreparedGlobal","deadlineClock"] (D.map8 (\bound request _ _ _ _ _ _ -> Capabilities bound request) (D.field "binding" A.bindingDecoder) (D.field "requestId" A.counterDecoder) (exact "operations" (D.list D.string) ["restore"]) (exact "maxPreparedPerSession" D.int 1) (exact "maxPreparedGlobal" D.int 64) (exact "deadlineClock" D.string "CLOCK_MONOTONIC") (D.succeed ()) (D.succeed ())))
        "selection" -> decode (A.strict ["binding","selection"] (D.map2 Selected (D.field "binding" A.bindingDecoder) (D.field "selection" A.selectionDecoder)))
        "prepared" -> decode (D.map Prepared identityDecoder)
        "outcome" -> decode (D.map Observed outcomeDecoder)
        "history" -> decode (D.map History historyDecoder)
        "batch-registered" -> decode (A.strict batchFields (D.map BatchRegistered batchBody))
        "batch-disposition" -> decode (A.strict (batchFields ++ ["disposition"]) (D.map2 BatchDisposition batchBody (D.field "disposition" (D.string |> D.andThen (\value -> if List.member value ["preflight-unsent","admitted","uncertain"] then D.succeed value else D.fail "batch disposition")))))
        _ -> D.fail "unsupported kind")
encodeEnvelope kind body = E.object [("version",E.int 2),("kind",E.string kind),("body",body)]
