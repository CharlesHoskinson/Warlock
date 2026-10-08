module JumpList exposing (Model, Snapshot, Action, Intent, initial, decoder, intent, supported, propose, observe, reconcile, receive, disconnect)
import Json.Decode as D
import Json.Encode as E
import UInt64 exposing (Counter)

type alias Action = { id : String, label : String, kind : String }
type alias Snapshot = { service : Counter, revision : Counter, entry : String, name : String, available : Bool, reason : String, actions : List Action }
type alias Intent = { service : Counter, revision : Counter, entry : String, action : String }
type alias Model = { snapshot : Maybe Snapshot, pending : Maybe { request : Counter, intent : Intent }, spent : List Intent, notice : String }
initial : Model
initial = {snapshot=Nothing,pending=Nothing,spent=[],notice="Reading application actions…"}
strict fields child = D.keyValuePairs D.value |> D.andThen (\pairs -> if List.sort (List.map Tuple.first pairs)==List.sort fields then child else D.fail "Jump list fields")
positive = UInt64.decoder |> D.andThen (\value -> if value==UInt64.zero then D.fail "Jump list identity" else D.succeed value)
bounded limit nonempty = D.string |> D.andThen (\value -> if String.length value<=limit && (not nonempty || not (String.isEmpty value)) && not (String.any (\c -> Char.toCode c<32 || Char.toCode c==127) value) then D.succeed value else D.fail "Jump list text")
actionDecoder = strict ["id","label","kind"] (D.map3 Action (D.field "id" (bounded 256 True)) (D.field "label" (bounded 512 True)) (D.field "kind" (D.string |> D.andThen (\value -> if List.member value ["desktop","recent"] then D.succeed value else D.fail "Unsupported action kind"))))
decoder : D.Decoder Snapshot
decoder = strict ["service","revision","entry","name","available","reason","actions"] (D.map7 Snapshot (D.field "service" positive) (D.field "revision" positive) (D.field "entry" (bounded 256 True)) (D.field "name" (bounded 512 False)) (D.field "available" D.bool) (D.field "reason" (bounded 128 False)) (D.field "actions" (D.list actionDecoder)))
    |> D.andThen (\snapshot ->
        let keys=List.map .id snapshot.actions
            unique=List.foldl (\key seen -> if List.member key seen then seen else key::seen) [] keys
        in if List.length keys>44 || List.length keys/=List.length unique || (not snapshot.available && not (List.isEmpty keys)) || List.any (\row -> not (String.startsWith (row.kind++":") row.id)) snapshot.actions then D.fail "Jump list actions" else D.succeed snapshot)
intent snapshot action = {service=snapshot.service,revision=snapshot.revision,entry=snapshot.entry,action=action}
supported value model = model.pending==Nothing && not (List.member value model.spent) && (model.snapshot |> Maybe.map (\snapshot -> snapshot.available && snapshot.service==value.service && snapshot.revision==value.revision && snapshot.entry==value.entry && List.any (\row -> row.id==value.action) snapshot.actions) |> Maybe.withDefault False)
propose request value model =
    if request==UInt64.zero || not (supported value model) then (model,Nothing) else
        ({model | pending=Just {request=request,intent=value},spent=List.take 128 (value::model.spent),notice="Application action: waiting for native submission…"},Just (E.object [("service",E.string (UInt64.string value.service)),("revision",E.string (UInt64.string value.revision)),("entry",E.string value.entry),("action",E.string value.action)]))
observe snapshot model =
    let admitted=model.snapshot |> Maybe.map (\old -> snapshot.service==old.service && (UInt64.compare snapshot.revision old.revision==GT || snapshot==old)) |> Maybe.withDefault True
    in if not admitted then model else {model | snapshot=Just snapshot,notice=if model.pending/=Nothing then model.notice else if snapshot.available then (if String.isEmpty snapshot.reason then "Choose an application action or recent file." else snapshot.reason) else snapshot.reason}
receive request status snapshot model = case model.pending of
    Nothing -> model
    Just pending ->
        if request/=pending.request || snapshot.service/=pending.intent.service || snapshot.entry/=pending.intent.entry || not (List.member status ["Submitted","Refused","Unknown"]) then model else
        let next=observe snapshot model
        in if next.snapshot/=Just snapshot then model else {next | pending=if status=="Unknown" then model.pending else Nothing,notice=if status=="Submitted" then "Application action: submitted to the native launcher." else if status=="Refused" then "Application action: refused or no longer available. Refresh before choosing again." else "Application action: not confirmed. Refresh only reads actions; this request will not be repeated."}
reconcile snapshot model =
    let next=observe snapshot model
    in case next.pending of
        Nothing -> next
        Just pending -> if next.snapshot==Just snapshot && UInt64.compare snapshot.revision pending.intent.revision==GT then {next | pending=Nothing,notice="Application actions refreshed. The previous request will not be repeated."} else next
disconnect model = {model | snapshot=Nothing,pending=Nothing,spent=[],notice=if model.pending/=Nothing then "Application action: not confirmed after connection loss. This request will not be repeated." else model.notice}
