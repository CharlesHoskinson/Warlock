module Protocol.Session exposing (Model, Msg(..), Status(..), RefusalReason(..), PolicySnapshot, initial, update, snapshot, refusalReason, refusalCode, policySnapshot, samePolicy)

{-| Proposed pure GUI session reducer. This is not an IPC implementation:
Haskell must authenticate, frame, validate and own every input and native effect. -}
import Protocol.Authority as A
import Json.Decode as D
import Json.Encode as E
import Protocol.Wire as Wire

type Status = Waiting | Preparing | Prepared | Uncertain | Done Wire.Status

{-| One bounded local observation. It cannot hold source text or native authority. -}
type RefusalReason = UnsupportedVersion | MalformedEnvelope
type alias Transaction = { binding : A.Binding, intent : A.Intent, selection : A.Selection, prepared : Maybe A.Counter, controlIssued : Bool, status : Status, commitAttempted : Bool, cancelAttempted : Bool }
type Model = Model { refusal : Maybe RefusalReason, current : Maybe A.Binding, seenBindings : List A.Binding, pendingCapability : Maybe A.Counter, capabilityHigh : Maybe A.Counter, capable : Bool, selection : Maybe A.Selection, view : Maybe {scope : A.Scope, publication : A.Counter, lease : A.Counter}, transaction : Maybe Transaction, batch : Maybe Wire.Batch, lookup : Maybe Wire.LookupQuery, lookupHigh : Maybe A.Counter, history : List Wire.Historical }
type Msg = Backend D.Value | StartNegotiation A.Counter | SetView A.Scope A.Counter A.Counter | Choose A.Intent String | Decide String | RequestLookup Wire.LookupQuery | Disconnect

initial : Model
initial = Model {refusal=Nothing,current=Nothing,seenBindings=[],pendingCapability=Nothing,capabilityHigh=Nothing,capable=False,selection=Nothing,view=Nothing,transaction=Nothing,batch=Nothing,lookup=Nothing,lookupHigh=Nothing,history=[]}

out kind body = Wire.encodeEnvelope kind body
sameContext bound intent = intent.context.lifetime==bound.lifetime && intent.context.epoch==bound.frontend
uncertain transaction = case transaction.status of
    Done _ -> transaction
    _ -> {transaction | status=Uncertain}

update : Msg -> Model -> (Model,List E.Value)
update message ((Model model) as original) =
    case message of
        Disconnect -> (Model {model|current=Nothing,pendingCapability=Nothing,capable=False,selection=Nothing,view=Nothing,batch=Nothing,lookup=Nothing,transaction=Maybe.map uncertain model.transaction},[])
        StartNegotiation request -> case model.current of
            Just bound -> if model.pendingCapability/=Nothing || model.capable || (model.capabilityHigh |> Maybe.map (\prior -> A.compareCounter request prior/=GT) |> Maybe.withDefault False) then (original,[]) else
                (Model {model|pendingCapability=Just request,capabilityHigh=Just request},[out "negotiate" (E.object [("binding",A.encodeBinding bound),("requestId",E.string (A.counterString request))])])
            Nothing -> (original,[])
        SetView scope publication lease ->
            let next={scope=scope,publication=publication,lease=lease}
            in (Model {model|view=Just next,selection=if model.view==Just next then model.selection else Nothing},[])
        Choose intent controlId -> case (model.current,model.selection,model.transaction) of
            (Just bound,Just selected,Nothing) ->
                if not model.capable || selected.controlId/=controlId || not (sameContext bound intent) || intent.operation/="restore" then (original,[]) else
                let transaction={binding=bound,intent=intent,selection=selected,prepared=Nothing,controlIssued=False,status=Preparing,commitAttempted=False,cancelAttempted=False}
                in (Model {model|selection=Nothing,transaction=Just transaction},[out "prepare" (E.object [("binding",A.encodeBinding bound),("intent",A.encodeIntent intent),("selectionId",E.string selected.selectionId)])])
            _ -> (original,[])
        Decide decision -> case (model.current,model.transaction) of
            (Just bound,Just tx) -> case tx.prepared of
                Just prepared ->
                    let cancelState = case tx.status of
                            Prepared -> True
                            Uncertain -> True
                            Done Wire.Committed -> True
                            _ -> False
                        allowed = tx.binding==bound && tx.controlIssued &&
                            ((decision=="commit" && tx.status==Prepared && not tx.commitAttempted && not tx.cancelAttempted) ||
                             (decision=="cancel" && cancelState && not tx.cancelAttempted))
                        nextStatus = case tx.status of
                            Done Wire.Committed -> Done Wire.Committed
                            _ -> Uncertain
                    in if not allowed then (original,[]) else
                    let next={tx|status=nextStatus,commitAttempted=tx.commitAttempted || decision=="commit",cancelAttempted=tx.cancelAttempted || decision=="cancel"}
                        body=E.object [("binding",A.encodeBinding bound),("intent",A.encodeIntent tx.intent),("selectionId",E.string tx.selection.selectionId),("deadlineMonotonicNs",E.string (A.counterString tx.selection.deadlineMonotonicNs)),("preparedId",E.string (A.counterString prepared)),("decision",E.string decision)]
                    in (Model {model|transaction=Just next},[out "decision" body])
                Nothing -> (original,[])
            _ -> (original,[])
        RequestLookup query ->
            let validKey = String.length query.key == 64 && String.all (\c -> (c >= '0' && c <= '9') || (c >= 'a' && c <= 'f')) query.key
                advancing = model.lookupHigh |> Maybe.map (\prior -> A.compareCounter query.requestId prior == GT) |> Maybe.withDefault True
                validOriginal = sameContext query.originalBinding query.intent
                maybeCounter value = value |> Maybe.map (A.counterString >> E.string) |> Maybe.withDefault E.null
                body = E.object [("deliveryBinding",A.encodeBinding query.deliveryBinding),("requestId",E.string (A.counterString query.requestId)),("key",E.string query.key),("originalBinding",A.encodeBinding query.originalBinding),("intent",A.encodeIntent query.intent),("selection",A.encodeSelection query.selection),("preparedId",maybeCounter query.preparedId)]
            in if model.current /= Just query.deliveryBinding || model.lookup /= Nothing || not validKey || not advancing || not validOriginal then (original,[]) else
                (Model {model|lookup=Just query,lookupHigh=Just query.requestId},[out "lookup" body])
        Backend raw -> case D.decodeValue Wire.decoder raw of
            Err _ -> (Model {model | refusal = Just (classifyRefusal raw)},[])
            Ok event -> case event of
                Wire.Hello bound ->
                    if model.current/=Nothing || List.member bound model.seenBindings || List.length model.seenBindings>=128 then (original,[]) else
                        (Model {model|current=Just bound,seenBindings=bound::model.seenBindings,pendingCapability=Nothing,capabilityHigh=Nothing,lookupHigh=Nothing,lookup=Nothing,capable=False,selection=Nothing},[])
                Wire.Capabilities bound request ->
                    if model.current/=Just bound || model.pendingCapability/=Just request then (original,[]) else
                        (Model {model|pendingCapability=Nothing,capable=True},[])
                Wire.Selected bound selected ->
                    if model.current/=Just bound || not model.capable || model.transaction/=Nothing || (model.view |> Maybe.map (\view -> view.scope==selected.scope && view.publication==selected.publication && view.lease==selected.lease) |> Maybe.withDefault False)==False then (original,[]) else
                        (Model {model|selection=Just selected},[])
                Wire.Prepared identity -> case model.transaction of
                    Nothing -> (original,[])
                    Just tx -> if model.current/=Just identity.binding || tx.binding/=identity.binding || tx.intent/=identity.intent || tx.selection.selectionId/=identity.selectionId || tx.selection.deadlineMonotonicNs/=identity.deadlineMonotonicNs || (tx.prepared/=Nothing && tx.prepared/=Just identity.preparedId) || (tx.status/=Preparing && not (tx.status==Uncertain && tx.prepared==Just identity.preparedId)) then (original,[]) else
                        (Model {model|transaction=Just {tx|prepared=Just identity.preparedId,controlIssued=True,status=Prepared}},[])
                Wire.Observed outcome -> case model.transaction of
                    Nothing -> (original,[])
                    Just tx ->
                        let identity=outcome.identity
                            exact=tx.binding==identity.binding && tx.intent==identity.intent && tx.selection.selectionId==identity.selectionId && tx.selection.deadlineMonotonicNs==identity.deadlineMonotonicNs && tx.prepared==Just identity.preparedId
                            priorTerminal=case tx.status of
                                Done _ -> True
                                _ -> False
                        in if model.current/=Just identity.binding || not exact || priorTerminal || (outcome.status==Wire.Committed && not tx.commitAttempted) then (original,[]) else
                            (Model {model|transaction=Just {tx|status=if outcome.status==Wire.Unknown then Uncertain else Done outcome.status}},[])
                Wire.BatchRegistered batch ->
                    let matches member = case member of
                            Wire.Negotiation request -> model.pendingCapability==Just request
                            Wire.Preparation intent token -> model.transaction |> Maybe.map (\tx -> tx.binding==batch.binding && tx.intent==intent && tx.selection.selectionId==token && tx.status==Preparing) |> Maybe.withDefault False
                            Wire.Decision intent token deadline prepared decision -> model.transaction |> Maybe.map (\tx -> tx.binding==batch.binding && tx.intent==intent && tx.selection.selectionId==token && tx.selection.deadlineMonotonicNs==deadline && tx.prepared==Just prepared && ((decision=="commit" && tx.commitAttempted) || (decision=="cancel" && tx.cancelAttempted))) |> Maybe.withDefault False
                    in if model.current/=Just batch.binding || model.batch/=Nothing || not (List.all matches batch.members) then (original,[]) else (Model {model|batch=Just batch},[])
                Wire.BatchDisposition batch disposition ->
                    if model.current/=Just batch.binding || model.batch/=Just batch then (original,[]) else
                    let negotiation = List.any (\member -> case member of
                            Wire.Negotiation request -> model.pendingCapability==Just request
                            _ -> False) batch.members
                        mutation = List.any (\member -> case member of
                            Wire.Negotiation _ -> False
                            _ -> True) batch.members
                        pending = if disposition=="preflight-unsent" && negotiation then Nothing else model.pendingCapability
                        transaction = if mutation && disposition/="admitted" then Maybe.map uncertain model.transaction else model.transaction
                    in (Model {model|batch=Nothing,pendingCapability=pending,transaction=transaction},[])
                Wire.LookupResponse query result ->
                    if model.current /= Just query.deliveryBinding || model.lookup /= Just query then (original,[]) else
                        let recover tx =
                                case result of
                                    Wire.LookupPrepared prepared ->
                                        if tx.binding == query.deliveryBinding && tx.binding == query.originalBinding && tx.intent == query.intent && tx.selection == query.selection && tx.prepared == query.preparedId && (tx.status == Preparing || tx.status == Uncertain) then
                                            {tx|prepared=Just prepared,status=Uncertain}
                                        else tx
                                    _ -> tx
                        in (Model {model|lookup=Nothing,transaction=Maybe.map recover model.transaction},[])
                Wire.History item ->
                    let sameIdentity old = old.key==item.key && old.originalBinding==item.originalBinding && old.intent==item.intent && old.selection==item.selection && old.preparedId==item.preparedId && old.certificate==item.certificate
                        rank state = if state=="acknowledged" then 2 else if state=="pending" then 1 else 0
                        settle tx =
                            if tx.binding==item.originalBinding && tx.intent==item.intent && tx.selection==item.selection && tx.prepared==Just item.preparedId then
                                case tx.status of
                                    Done _ -> tx
                                    _ -> {tx|status=Done item.certificate.status}
                            else tx
                        conflict tx = tx.binding==item.originalBinding && tx.intent==item.intent && tx.selection==item.selection && tx.prepared==Just item.preparedId && (case tx.status of
                            Done prior -> prior/=item.certificate.status
                            _ -> False)
                        replace existing = List.map (\entry -> if entry.key==existing.key then item else entry) model.history
                    in if model.current/=Just item.deliveryBinding || (model.transaction |> Maybe.map conflict |> Maybe.withDefault False) then (original,[]) else
                        case List.filter (\old -> old.key==item.key || old.selection.selectionId==item.selection.selectionId) model.history of
                            [] -> if List.length model.history>=64 then (original,[]) else (Model {model|history=item::model.history,transaction=Maybe.map settle model.transaction},[])
                            [old] -> if not (sameIdentity old) || rank item.ackState < rank old.ackState || (old.acknowledgement/=Nothing && old.acknowledgement/=item.acknowledgement) then (original,[]) else
                                (Model {model|history=replace old,transaction=Maybe.map settle model.transaction},[])
                            _ -> (original,[])

snapshot : Model -> { current : Maybe A.Binding, capable : Bool, selection : Maybe A.Selection, status : Maybe Status, historyCount : Int }
snapshot (Model model) = {current=model.current,capable=model.capable,selection=model.selection,status=Maybe.map .status model.transaction,historyCount=List.length model.history}


{-| The observation is retained until the next refusal, including across valid
messages. It does not confer capabilities or change any policy transition. -}
refusalReason : Model -> Maybe RefusalReason
refusalReason (Model model) =
    model.refusal

refusalCode : RefusalReason -> String
refusalCode reason =
    case reason of
        UnsupportedVersion ->
            "unsupported-version"

        MalformedEnvelope ->
            "malformed-envelope"

{-| Compare the complete original policy record, including hidden authority,
transaction, batch, lookup, history and attempt fields; only the separate
bounded diagnostic observation is excluded. -}
type PolicySnapshot = PolicySnapshot Model

policySnapshot : Model -> PolicySnapshot
policySnapshot (Model model) =
    PolicySnapshot (Model { model | refusal = Nothing })

samePolicy : Model -> Model -> Bool
samePolicy left right =
    policySnapshot left == policySnapshot right

{-| Classify only after a structurally exact envelope header. A malformed body
or unsupported kind on version 2 remains MalformedEnvelope. No decoder error
text, unknown fields or client-supplied strings are retained. -}
classifyRefusal : D.Value -> RefusalReason
classifyRefusal raw =
    case D.decodeValue (A.strict [ "version", "kind", "body" ] (D.map3 (\version _ _ -> version) (D.field "version" D.int) (D.field "kind" D.string) (D.field "body" D.value))) raw of
        Ok version ->
            if version /= 2 then
                UnsupportedVersion
            else
                MalformedEnvelope

        Err _ ->
            MalformedEnvelope
