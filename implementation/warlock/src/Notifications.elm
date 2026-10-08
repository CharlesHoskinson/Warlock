module Notifications exposing (Model, Snapshot, Entry, Target, initial, decoder, observe, reconcile, target, identity, encodeIntent, live, propose, receive)

import Json.Decode as D
import Json.Encode as E
import Set
import UInt64 exposing (Counter)

type alias Entry = { id : Counter, incarnation : Counter, producer : String, app : String, summary : String, body : String, state : String, actions : List { key : String, label : String } }
type alias Snapshot = { service : Counter, revision : Counter, available : Bool, reason : String, entries : List Entry }
type alias Target = { service : Counter, id : Counter, incarnation : Counter, producer : String, action : String, verb : String }
type alias Model = { snapshot : Maybe Snapshot, pending : Maybe { request : Counter, target : Target }, spent : List Target, notice : String }

initial : Model
initial = {snapshot=Nothing,pending=Nothing,spent=[],notice="Loading notifications…"}
strict fields child = D.keyValuePairs D.value |> D.andThen (\pairs -> if List.sort (List.map Tuple.first pairs)==List.sort fields then child else D.fail "Notification fields")
positive = UInt64.decoder |> D.andThen (\value -> if value/=UInt64.zero then D.succeed value else D.fail "Notification identity")
bounded limit = D.string |> D.andThen (\value -> if String.length value<=limit && not (String.any (\c -> Char.toCode c<32 && c/='\n' && c/='\t') value) then D.succeed value else D.fail "Notification text")
unique values = List.length values==Set.size (Set.fromList values)
entryDecoder : D.Decoder Entry
entryDecoder = strict ["id","incarnation","producer","app","summary","body","state","actions"] (D.map8 Entry
    (D.field "id" positive) (D.field "incarnation" positive)
    (D.field "producer" (bounded 128 |> D.andThen (\value -> if String.startsWith ":" value then D.succeed value else D.fail "Notification producer")))
    (D.field "app" (bounded 128)) (D.field "summary" (bounded 256)) (D.field "body" (bounded 1024))
    (D.field "state" (D.string |> D.andThen (\value -> if List.member value ["live","expired","invoked","dismissed","closed","disconnected","unknown","unavailable"] then D.succeed value else D.fail "Notification state")))
    (D.field "actions" (D.list (strict ["key","label"] (D.map2 (\key label -> {key=key,label=label}) (D.field "key" (bounded 64)) (D.field "label" (bounded 128)))))))
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
    in if not admitted then model else {model | snapshot=Just current,notice=if model.pending/=Nothing then model.notice else notice}
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
        ({model | pending=Just {request=request,target=choice},spent=List.take 64 (choice::model.spent),notice="Sending notification action…"},Just (encodeIntent choice))
receive : Counter -> String -> Snapshot -> Model -> Model
receive request status current model = case model.pending of
    Nothing -> model
    Just pending ->
        if request/=pending.request || not (List.member status ["Dispatched","Refused","Unknown"]) || current.service/=pending.target.service then model else
        let observed=observe current model
        in if observed.snapshot/=Just current then model else
            if status=="Unknown" then {observed | notice="Notification action not confirmed. It will not be repeated."}
            else {observed | pending=Nothing,notice=if status=="Dispatched" then "Notification action sent." else "Notification action refused. The target expired or changed; choose a current notification."}

reconcile : Snapshot -> Model -> Model
reconcile snapshot model =
    let current=observe snapshot model
    in case current.pending of
        Nothing -> current
        Just pending ->
            if current.snapshot==Just snapshot && not (List.any (\row -> row.id==pending.target.id && row.incarnation==pending.target.incarnation && row.producer==pending.target.producer && row.state=="live") snapshot.entries) then
                {current | pending=Nothing,notice="Notification target is no longer live. Its action will not be repeated."}
            else current
