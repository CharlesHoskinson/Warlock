module Notifications exposing (Policy, Urgency(..), Model, Snapshot, Entry, Target, initial, configure, arrivals, expirations, focus, clearFocus, focusedIdentity, critical, decoder, observe, reconcile, target, identity, encodeIntent, live, propose, receive, receiveReason)

import Json.Decode as D
import Json.Encode as E
import Set
import UInt64 exposing (Counter)

type Urgency = Low | Normal | Critical
type alias Policy = { doNotDisturb : Bool, interruptCritical : Bool }
type alias Entry = { urgency : Urgency, id : Counter, incarnation : Counter, producer : String, app : String, summary : String, body : String, state : String, actions : List { key : String, label : String } }
type alias Snapshot = { service : Counter, revision : Counter, available : Bool, reason : String, entries : List Entry }
type alias Target = { service : Counter, id : Counter, incarnation : Counter, producer : String, action : String, verb : String }
type alias Model = { focused : Maybe {target:Target,label:String}, outcome : Maybe {request:Counter,target:Target,status:String,expired:Bool}, policy : Policy, snapshot : Maybe Snapshot, pending : Maybe { request : Counter, target : Target, expired : Bool }, spent : List Target, notice : String }

initial : Model
initial = {focused=Nothing,outcome=Nothing,policy={doNotDisturb=False,interruptCritical=False},snapshot=Nothing,pending=Nothing,spent=[],notice="Loading notifications…"}
strict fields child = D.keyValuePairs D.value |> D.andThen (\pairs -> if List.sort (List.map Tuple.first pairs)==List.sort fields then child else D.fail "Notification fields")
positive = UInt64.decoder |> D.andThen (\value -> if value/=UInt64.zero then D.succeed value else D.fail "Notification identity")
bounded limit = D.string |> D.andThen (\value -> if String.length value<=limit && not (String.any (\c -> Char.toCode c<32 && c/='\n' && c/='\t') value) then D.succeed value else D.fail "Notification text")
unique values = List.length values==Set.size (Set.fromList values)
entryDecoder : D.Decoder Entry
entryDecoder =
    let base = D.map8 (\id incarnation producer app summary body state actions -> {urgency=Normal,id=id,incarnation=incarnation,producer=producer,app=app,summary=summary,body=body,state=state,actions=actions})
            (D.field "id" positive) (D.field "incarnation" positive)
            (D.field "producer" (bounded 128 |> D.andThen (\value -> if String.startsWith ":" value then D.succeed value else D.fail "Notification producer")))
            (D.field "app" (bounded 128)) (D.field "summary" (bounded 256)) (D.field "body" (bounded 1024))
            (D.field "state" (D.string |> D.andThen (\value -> if List.member value ["live","expired","invoked","dismissed","closed","disconnected","unknown","unavailable"] then D.succeed value else D.fail "Notification state")))
            (D.field "actions" (D.list (strict ["key","label"] (D.map2 (\key label -> {key=key,label=label}) (D.field "key" (bounded 64)) (D.field "label" (bounded 128))))))
        urgency = D.int |> D.andThen (\value -> case value of
            0 -> D.succeed Low
            1 -> D.succeed Normal
            2 -> D.succeed Critical
            _ -> D.fail "Notification urgency")
    in D.oneOf [strict ["id","incarnation","producer","app","summary","body","state","actions","urgency"] (D.map2 (\entry level -> {entry|urgency=level}) base (D.field "urgency" urgency)),strict ["id","incarnation","producer","app","summary","body","state","actions"] base]
    |> D.andThen (\entry -> if List.length entry.actions<=8 && unique (List.map .key entry.actions) && List.all (\a -> not (String.isEmpty a.key) && not (String.isEmpty a.label)) entry.actions && (entry.state=="live" || List.isEmpty entry.actions) then D.succeed entry else D.fail "Notification action lifecycle")
decoder : D.Decoder Snapshot
decoder = strict ["service","revision","available","reason","entries"] (D.map5 Snapshot
    (D.field "service" positive) (D.field "revision" positive) (D.field "available" D.bool)
    (D.field "reason" (bounded 256)) (D.field "entries" (D.list entryDecoder)))
    |> D.andThen (\value -> if List.length value.entries<=32 && unique (List.map (.id >> UInt64.string) value.entries) && unique (List.map (.incarnation >> UInt64.string) value.entries) then D.succeed value else D.fail "Notification capacity/identity")
observe : Snapshot -> Model -> Model
observe current model =
    let admitted=case model.snapshot of
            Nothing -> True
            Just old -> current.service==old.service && (UInt64.compare current.revision old.revision==GT || current==old)
        entries=List.filter (\row -> row.state=="live") current.entries
        count=List.length entries
        notice=if not current.available then current.reason else if count==0 then "No live notifications. Previous notifications remain in history." else String.fromInt count++" live notifications. Actions apply only to the current notification."
        pending=model.pending |> Maybe.map (\waiting -> {waiting|expired=waiting.expired || List.any (\entry -> same waiting.target current.service entry && entry.state=="expired") current.entries})
    in if not admitted then model else {model | snapshot=Just current,pending=pending,notice=if model.pending/=Nothing then model.notice else notice}
target : Snapshot -> Entry -> String -> String -> Target
target snapshot entry verb action = {service=snapshot.service,id=entry.id,incarnation=entry.incarnation,producer=entry.producer,action=action,verb=verb}
identity : Target -> String
identity value = "notification:"++UInt64.string value.service++":"++UInt64.string value.incarnation++":"++value.verb++":"++value.action
encodeIntent value = E.object [("service",E.string (UInt64.string value.service)),("id",E.string (UInt64.string value.id)),("incarnation",E.string (UInt64.string value.incarnation)),("producer",E.string value.producer),("action",E.string value.action),("verb",E.string value.verb)]
live : Target -> Model -> Bool
live choice model = case model.snapshot of
    Nothing -> False
    Just current -> current.available && current.service==choice.service && not (List.member choice model.spent) && List.any (\row -> row.id==choice.id && row.incarnation==choice.incarnation && row.producer==choice.producer && row.state=="live" && ((choice.verb=="dismiss" && choice.action=="") || (choice.verb=="invoke" && List.any (\action -> action.key==choice.action) row.actions))) current.entries
propose : Counter -> Target -> Model -> (Model,Maybe E.Value)
propose request choice model =
    if model.pending/=Nothing || not (live choice model) then (model,Nothing) else
        ({model | pending=Just {request=request,target=choice,expired=False},spent=List.take 64 (choice::model.spent),notice="Sending notification action…"},Just (encodeIntent choice))
receive : Counter -> String -> Snapshot -> Model -> Model
receive request status current model = receiveReason request status "" current model

receiveReason request status reason current model = case model.pending of
    Nothing -> model
    Just pending ->
        if request/=pending.request || not (List.member status ["Dispatched","Refused","Unknown"]) || current.service/=pending.target.service then model else
        let observed=observe current model
            expired=reason=="expired" || (observed.pending |> Maybe.map .expired |> Maybe.withDefault pending.expired)
            outcome=Just {request=request,target=pending.target,status=status,expired=expired}
        in if observed.snapshot/=Just current then model else
            if status=="Unknown" then {observed | outcome=outcome,notice="Notification action not confirmed. It will not be repeated."}
            else {observed | outcome=outcome,pending=Nothing,notice=if status=="Dispatched" then "Notification action sent." else "Notification action refused. The target expired or changed; choose a current notification."}

reconcile : Snapshot -> Model -> Model
reconcile snapshot model =
    let current=observe snapshot model
    in case current.pending of
        Nothing -> current
        Just pending ->
            if current.snapshot==Just snapshot && not (List.any (\row -> row.id==pending.target.id && row.incarnation==pending.target.incarnation && row.producer==pending.target.producer && row.state=="live") snapshot.entries) then
                {current | pending=Nothing,notice="Notification target is no longer live. Its action will not be repeated."}
            else current


-- Session controls are explicit user policy, not producer-supplied hints.
-- Already-observed/suppressed history is never replayed when policy changes.
configure : Policy -> Model -> Model
configure policy model = {model|policy=policy}
critical : Entry -> Bool
critical entry = entry.urgency==Critical
arrivals : Model -> Model -> List Entry
arrivals before after =
    case (before.snapshot,after.snapshot) of
        (Just old,Just current) ->
            if not current.available || current.service/=old.service || UInt64.compare current.revision old.revision/=GT || after.policy.doNotDisturb then [] else
            current.entries |> List.filter (\entry -> entry.state=="live" && not (List.any (\prior -> prior.incarnation==entry.incarnation) old.entries)) |> List.sortWith (\a b -> UInt64.compare a.incarnation b.incarnation)
        _ -> []


-- Observed control identity is admitted by the current popup publication/lease.
-- It creates no action, native intent, deadline or availability authority.
same choice service entry = choice.service==service && choice.id==entry.id && choice.incarnation==entry.incarnation && choice.producer==entry.producer
focusedIdentity model = model.focused |> Maybe.map (.target >> identity)
clearFocus model = {model|focused=Nothing}
focus selected model =
    if focusedIdentity model==Just selected then model else
    let chosen=model.snapshot |> Maybe.andThen (\snapshot ->
            snapshot.entries |> List.filter (\entry -> entry.state=="live") |> List.concatMap (\entry ->
                List.map (\action -> {target=target snapshot entry "invoke" action.key,label=action.label}) entry.actions ++ [{target=target snapshot entry "dismiss" "",label="Dismiss notification"}])
            |> List.filter (\row -> identity row.target==selected) |> List.head)
    in {model|focused=chosen}
expirations : Model -> Model -> List Entry
expirations before after = case (before.snapshot,after.snapshot) of
    (Just old,Just current) ->
        if current.service/=old.service || UInt64.compare current.revision old.revision/=GT || after.policy.doNotDisturb then [] else
        current.entries |> List.filter (\entry -> entry.state=="expired" && List.any (\prior -> prior.state=="live" && prior.id==entry.id && prior.incarnation==entry.incarnation && prior.producer==entry.producer) old.entries &&
            ((before.focused |> Maybe.map (\selected -> same selected.target current.service entry) |> Maybe.withDefault False) || (before.pending |> Maybe.map (\waiting -> same waiting.target current.service entry) |> Maybe.withDefault False))) |> List.sortWith (\a b -> UInt64.compare a.incarnation b.incarnation)
    _ -> []
