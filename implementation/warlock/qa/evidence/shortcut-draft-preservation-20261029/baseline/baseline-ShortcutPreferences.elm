module ShortcutPreferences exposing (Choice(..), Choices, Row, Inventory, Snapshot, Model, initial, defaults, decoder, inventoryDecoder, name, label, choices, row, edit, observe, writable, ready, changed, propose, receive, encode)

import Json.Decode as D
import Json.Encode as E
import UInt64 exposing (Counter)

type Choice = Undecided | Keep | Default | Alternate
type alias Choices = { applications : Choice, system : Choice, notifications : Choice }
type alias Row = { defaultChord : String, alternateChord : String, defaultAvailable : Bool, alternateAvailable : Bool, active : Choice }
type alias Inventory = { fingerprint : String, applications : Row, system : Row, notifications : Row }
type alias Snapshot = { schema : Int, revision : Counter, choices : Choices }
type alias Model = { snapshot : Maybe Snapshot, inventory : Maybe Inventory, draft : Choices, pending : Maybe {request : Counter, choices : Choices}, notice : String }
defaults = {applications=Undecided,system=Undecided,notifications=Undecided}
initial = {snapshot=Nothing,inventory=Nothing,draft=defaults,pending=Nothing,notice="Loading shortcut choices…"}
strict fields child = D.keyValuePairs D.value |> D.andThen (\pairs -> if List.sort (List.map Tuple.first pairs)==List.sort fields then child else D.fail "Shortcut fields")
choiceDecoder = D.string |> D.andThen (\value -> case value of
    "undecided" -> D.succeed Undecided
    "keep" -> D.succeed Keep
    "default" -> D.succeed Default
    "alternate" -> D.succeed Alternate
    _ -> D.fail "Shortcut decision")
choicesDecoder = strict ["applications","system","notifications"] (D.map3 Choices (D.field "applications" choiceDecoder) (D.field "system" choiceDecoder) (D.field "notifications" choiceDecoder))
decoder = strict ["schema","revision","choices"] (D.map3 Snapshot
    (D.field "schema" (D.int |> D.andThen (\v -> if v==1 then D.succeed v else D.fail "Shortcut schema")))
    (D.field "revision" (UInt64.decoder |> D.andThen (\v -> if v/=UInt64.zero then D.succeed v else D.fail "Shortcut revision")))
    (D.field "choices" choicesDecoder))
rowDecoder defaultChord alternateChord = strict ["defaultChord","alternateChord","defaultAvailable","alternateAvailable","active"] (D.map5 Row
    (D.field "defaultChord" (D.string |> D.andThen (\v -> if v==defaultChord then D.succeed v else D.fail "Default chord")))
    (D.field "alternateChord" (D.string |> D.andThen (\v -> if v==alternateChord then D.succeed v else D.fail "Alternate chord")))
    (D.field "defaultAvailable" D.bool) (D.field "alternateAvailable" D.bool)
    (D.field "active" (choiceDecoder |> D.andThen (\v -> if List.member v [Keep,Default,Alternate] then D.succeed v else D.fail "Observed shortcut"))))
    |> D.andThen (\value -> if (value.active==Default && not value.defaultAvailable) || (value.active==Alternate && not value.alternateAvailable) then D.fail "Active shortcut conflicts" else D.succeed value)
inventoryDecoder = strict ["fingerprint","applications","system","notifications"] (D.map4 Inventory
    (D.field "fingerprint" (D.string |> D.andThen (\v -> if String.length v==64 && String.all (\c -> String.contains (String.fromChar c) "0123456789abcdef") v then D.succeed v else D.fail "Binding fingerprint")))
    (D.field "applications" (rowDecoder "SUPER + ALT + SPACE" "SUPER + CTRL + ALT + SPACE"))
    (D.field "system" (rowDecoder "SUPER + ESCAPE" "SUPER + CTRL + ESCAPE"))
    (D.field "notifications" (rowDecoder "SUPER + SHIFT + ALT + comma" "SUPER + CTRL + ALT + comma")))
name value = case value of
    Undecided -> "undecided"
    Keep -> "keep"
    Default -> "default"
    Alternate -> "alternate"
label route = case route of
    "applications" -> "Apps menu"
    "system" -> "System menu"
    _ -> "Notification history"
choices route values = case route of
    "applications" -> values.applications
    "system" -> values.system
    _ -> values.notifications
row route inventory = case route of
    "applications" -> inventory.applications
    "system" -> inventory.system
    _ -> inventory.notifications
encode snapshot = E.object [("schema",E.int 1),("revision",E.string (UInt64.string snapshot.revision)),("choices",E.object [("applications",E.string (name snapshot.choices.applications)),("system",E.string (name snapshot.choices.system)),("notifications",E.string (name snapshot.choices.notifications))])]
writable model = model.snapshot/=Nothing && model.inventory/=Nothing && model.pending==Nothing
allowed selected observed = case selected of
    Keep -> True
    Default -> observed.defaultAvailable
    Alternate -> observed.alternateAvailable
    Undecided -> False
ready model = writable model && (model.inventory |> Maybe.map (\inventory -> List.all (\route -> allowed (choices route model.draft) (row route inventory)) ["applications","system","notifications"]) |> Maybe.withDefault False)
changed model =
    (model.snapshot |> Maybe.map (\current -> current.choices/=model.draft) |> Maybe.withDefault False) ||
    (model.inventory |> Maybe.map (\current -> List.any (\route -> choices route model.draft/=(row route current).active) ["applications","system","notifications"]) |> Maybe.withDefault False)
edit route selected model =
    if not (writable model) || not (List.member route ["applications","system","notifications"]) || not (model.inventory |> Maybe.map (row route >> allowed selected) |> Maybe.withDefault False) then model else
    let draft=model.draft
        next=case route of
            "applications" -> {draft | applications=selected}
            "system" -> {draft | system=selected}
            _ -> {draft | notifications=selected}
    in {model | draft=next,notice="Unsaved shortcut choices. Existing bindings remain unchanged until you save."}
observe snapshot inventory model =
    case (snapshot,inventory) of
        (Just current,Just native) ->
            if model.snapshot |> Maybe.map (\old -> UInt64.compare current.revision old.revision==LT) |> Maybe.withDefault False then model else
                {model | snapshot=Just current,inventory=Just native,draft=current.choices,pending=Nothing,notice="Shortcut choices loaded. Conflicting bindings are preserved; choose a free chord or keep the existing shortcut."}
        _ -> {model | snapshot=Nothing,inventory=Nothing,pending=Nothing,notice="Shortcut choices unavailable. Stored choices are preserved. Refresh to read again."}
propose request model = case (model.snapshot,model.inventory) of
    (Just current,Just native) ->
        if not (ready model && changed model) then (model,Nothing) else
            ({model | pending=Just {request=request,choices=model.draft},notice="Saving and applying shortcut choices…"},Just (E.object [("preferences",encode {current | choices=model.draft}),("fingerprint",E.string native.fingerprint)]))
    _ -> (model,Nothing)
receive request status snapshot inventory model = case model.pending of
    Nothing -> model
    Just pending ->
        if pending.request/=request then model else
        if status=="Saved" && (snapshot |> Maybe.map (\current -> current.choices==pending.choices && (model.snapshot |> Maybe.map (\old -> UInt64.compare current.revision old.revision/=LT) |> Maybe.withDefault False)) |> Maybe.withDefault False) && (inventory |> Maybe.map (\native -> List.all (\route -> choices route pending.choices==(row route native).active) ["applications","system","notifications"]) |> Maybe.withDefault False) then
            {model | snapshot=snapshot,inventory=inventory,pending=Nothing,notice="Shortcut choices saved and active. Existing bindings were preserved."}
        else if status=="Stored" && (snapshot |> Maybe.map (\current -> current.choices==pending.choices) |> Maybe.withDefault False) then
            {model | snapshot=snapshot,inventory=inventory,pending=Nothing,notice="Choices saved, but live bindings changed. Refresh and choose a free shortcut before applying."}
        else if status=="Refused" then {model | pending=Nothing,notice="Shortcut choices refused. Bindings or stored choices changed; refresh and choose again."}
        else {model | notice="Shortcut application not confirmed. Refresh reads stored choices and live bindings; this action will not be repeated."}
