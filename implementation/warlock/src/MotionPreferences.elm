module MotionPreferences exposing (Override(..), Snapshot, Model, initial, decoder, encode, observe, edit, writable, propose, receive, selected, label)

import Json.Decode as D
import Json.Encode as E
import UInt64 exposing (Counter)

type Override = System | Reduce | Full
type alias Snapshot = { revision : Counter, override : Override }
type alias Model = { snapshot : Maybe Snapshot, draft : Override, pending : Maybe { request : Counter, revision : Counter, override : Override }, notice : String }

initial : Model
initial = {snapshot=Nothing,draft=System,pending=Nothing,notice="Reading motion preference…"}

strict fields child = D.keyValuePairs D.value |> D.andThen (\pairs -> if List.sort (List.map Tuple.first pairs)==List.sort fields then child else D.fail "Motion preference fields")
overrideDecoder = D.nullable D.string |> D.andThen (\value -> case value of
    Nothing -> D.succeed System
    Just "reduced" -> D.succeed Reduce
    Just "full" -> D.succeed Full
    _ -> D.fail "Motion override")

decoder : D.Decoder Snapshot
decoder = strict ["schema","revision","override"] (D.map3 (\_ revision override -> {revision=revision,override=override})
    (D.field "schema" D.int |> D.andThen (\v -> if v==1 then D.succeed () else D.fail "Motion preference version"))
    (D.field "revision" UInt64.decoder |> D.andThen (\v -> if v/=UInt64.zero then D.succeed v else D.fail "Motion preference revision"))
    (D.field "override" overrideDecoder))

encode : Snapshot -> E.Value
encode snapshot = E.object [("schema",E.int 1),("revision",E.string (UInt64.string snapshot.revision)),("override",case snapshot.override of
    System -> E.null
    Reduce -> E.string "reduced"
    Full -> E.string "full")]

selected : Model -> Override
selected model = model.snapshot |> Maybe.map .override |> Maybe.withDefault System

label : Override -> String
label override = case override of
    System -> "Follow system"
    Reduce -> "Reduced motion"
    Full -> "Full motion"

observe : Maybe Snapshot -> Model -> Model
observe snapshot model = case snapshot of
    Nothing -> {model | snapshot=Nothing,notice="Stored motion preference unavailable. Refresh to read it again; the stored copy is preserved."}
    Just current ->
        if model.snapshot |> Maybe.map (\old -> UInt64.compare current.revision old.revision==LT || (current.revision==old.revision && current.override/=old.override)) |> Maybe.withDefault False then model
        else {model | snapshot=Just current,draft=current.override,pending=Nothing,notice="Motion preference loaded."}

writable : Model -> Bool
writable model = model.snapshot/=Nothing && model.pending==Nothing

edit : Override -> Model -> Model
edit override model = if writable model then {model | draft=override,notice="Unsaved motion preference. Save to apply."} else model

propose : Counter -> Model -> (Model,Maybe E.Value)
propose request model = case model.snapshot of
    Nothing -> (model,Nothing)
    Just current ->
        if request==UInt64.zero || not (writable model) || current.override==model.draft then (model,Nothing)
        else ({model | pending=Just {request=request,revision=current.revision,override=model.draft},notice="Saving motion preference…"},Just (encode {current | override=model.draft}))

receive : Counter -> String -> Maybe Snapshot -> Model -> Model
receive request status snapshot model = case model.pending of
    Nothing -> model
    Just pending ->
        if request/=pending.request then model
        else if status=="Saved" && (snapshot |> Maybe.map (\s -> s.override==pending.override && UInt64.compare s.revision pending.revision==GT) |> Maybe.withDefault False) then
            {model | snapshot=snapshot,pending=Nothing,notice="Motion preference saved."}
        else if status=="Refused" then {model | pending=Nothing,notice="Motion preference refused. Refresh, then choose again."}
        else {model | notice="Motion preference save not confirmed. Refresh to read stored values; this write will not be repeated."}
