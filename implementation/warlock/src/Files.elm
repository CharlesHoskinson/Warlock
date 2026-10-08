module Files exposing (Model, Snapshot, Peer, Intent, initial, collections, decoder, observe, reconcile, edit, intent, supported, propose, receive, disconnect)

import Json.Decode as D
import Json.Encode as E
import UInt64 exposing (Counter)

type alias Peer = { pid : Counter, start : Counter, instance : String, target : String, visible : Bool }
type alias Snapshot = { service : Counter, revision : Counter, available : Bool, reason : String, peer : Maybe Peer }
type alias Intent = { service : Counter, revision : Counter, target : String }
type alias Model = { snapshot : Maybe Snapshot, draft : String, pending : Maybe { request : Counter, intent : Intent }, spent : List Intent, notice : String }

initial : Model
initial = {snapshot=Nothing,draft="",pending=Nothing,spent=[],notice="Loading Files…"}

collections : List (String,String)
collections = [("recent","Recent"),("images","Images"),("videos","Videos"),("documents","Documents"),("downloads","Downloads"),("large","Large files"),("screenshots","Screenshots")]

strict fields child = D.keyValuePairs D.value |> D.andThen (\pairs -> if List.sort (List.map Tuple.first pairs)==List.sort fields then child else D.fail "Files fields")
positive = UInt64.decoder |> D.andThen (\value -> if value==UInt64.zero then D.fail "Files identity" else D.succeed value)
textValid value = String.length value<=512 && not (String.any (\c -> Char.toCode c<32 || Char.toCode c==127) value)
bounded limit = D.string |> D.andThen (\value -> if String.length value<=limit && textValid value then D.succeed value else D.fail "Files text")
validTarget value = textValid value && (value=="home" || List.any (\(collection,_) -> value=="coll:"++collection) collections || String.startsWith "/" (String.trim value) || value=="~" || String.startsWith "~/" value)

decoder : D.Decoder Snapshot
decoder = strict ["service","revision","available","reason","peer"] (D.map5 Snapshot
    (D.field "service" positive) (D.field "revision" positive) (D.field "available" D.bool) (D.field "reason" (bounded 128))
    (D.field "peer" (D.nullable (strict ["pid","start","instance","target","visible"] (D.map5 Peer
        (D.field "pid" positive) (D.field "start" positive)
        (D.field "instance" (bounded 128 |> D.andThen (\value -> if not (String.isEmpty value) && String.all (\c -> Char.isAlphaNum c || c=='_' || c=='-') value then D.succeed value else D.fail "Files instance")))
        (D.field "target" (bounded 512 |> D.andThen (\value -> if validTarget value && not (String.startsWith "~" value) then D.succeed value else D.fail "Files observed target"))) (D.field "visible" D.bool))))))
    |> D.andThen (\snapshot -> if not snapshot.available && snapshot.peer/=Nothing then D.fail "Unavailable Files peer" else D.succeed snapshot)

observe : Snapshot -> Model -> Model
observe snapshot model =
    let admitted=model.snapshot |> Maybe.map (\old -> snapshot.service==old.service && (UInt64.compare snapshot.revision old.revision==GT || snapshot==old)) |> Maybe.withDefault True
    in if not admitted then model else {model | snapshot=Just snapshot,notice=if model.pending/=Nothing then model.notice else if snapshot.available then "Choose a collection or folder." else snapshot.reason}

edit : String -> Model -> Model
edit value model = if textValid value then {model | draft=value} else model

intent snapshot target = {service=snapshot.service,revision=snapshot.revision,target=target}

supported : Intent -> Model -> Bool
supported value model = model.pending==Nothing && validTarget value.target && not (List.member value model.spent) &&
    (model.snapshot |> Maybe.map (\snapshot -> snapshot.available && value.service==snapshot.service && value.revision==snapshot.revision) |> Maybe.withDefault False)

propose : Counter -> Intent -> Model -> (Model,Maybe E.Value)
propose request value model =
    if request==UInt64.zero || not (supported value model) then (model,Nothing) else
        ({model | pending=Just {request=request,intent=value},spent=List.take 128 (value::model.spent),notice="Files: waiting for the requested location…"},Just (E.object [("service",E.string (UInt64.string value.service)),("revision",E.string (UInt64.string value.revision)),("target",E.string value.target)]))

receive : Counter -> String -> Snapshot -> Model -> Model
receive request status snapshot model = case model.pending of
    Nothing -> model
    Just pending ->
        if request/=pending.request || snapshot.service/=pending.intent.service || not (List.member status ["Opened","Refused","Unknown"]) then model else
        let next=observe snapshot model
            samePeer=case (model.snapshot |> Maybe.andThen .peer,snapshot.peer) of
                (Just old,Just current) -> old.pid==current.pid && old.start==current.start && old.instance==current.instance
                (Nothing,Just _) -> True
                _ -> False
            locationMatches=snapshot.peer |> Maybe.map (\peer -> if String.startsWith "~" (String.trim pending.intent.target) then String.startsWith "/" peer.target else peer.target==normalize pending.intent.target) |> Maybe.withDefault False
            opened=snapshot.available && samePeer && locationMatches && UInt64.compare snapshot.revision pending.intent.revision==GT && (snapshot.peer |> Maybe.map .visible |> Maybe.withDefault False)
            notice=if status=="Opened" && opened then "Files: requested location opened." else if status=="Refused" then "Files: request refused. Refresh before choosing again." else "Files: opening not confirmed. Refresh only reads state; this request will not be repeated."
        in if next.snapshot/=Just snapshot then model else {next | pending=if status=="Refused" || (status=="Opened" && opened) then Nothing else model.pending,notice=notice}

reconcile : Snapshot -> Model -> Model
reconcile snapshot model =
    let next=observe snapshot model
    in case next.pending of
        Nothing -> next
        Just pending -> if next.snapshot==Just snapshot && UInt64.compare snapshot.revision pending.intent.revision==GT then {next | pending=Nothing,notice="Files state refreshed. The previous request will not be repeated."} else next

normalize : String -> String
normalize value =
    if not (String.startsWith "/" (String.trim value)) then value else
        "/"++(String.split "/" (String.trim value) |> List.foldl (\part parts -> if part=="" || part=="." then parts else if part==".." then List.drop 1 parts else part::parts) [] |> List.reverse |> String.join "/")

disconnect : Model -> Model
disconnect model = {model | snapshot=Nothing,pending=Nothing,spent=[],notice=if model.pending/=Nothing then "Files: opening not confirmed after connection loss. Open the menu to read current state; this request will not be repeated." else model.notice}
