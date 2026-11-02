port module ShortcutDraftProperties exposing (main)

import Json.Decode as D
import Json.Encode as E
import Platform
import ShortcutPreferences as P
import UInt64

port incoming : (D.Value -> msg) -> Sub msg
port outgoing : E.Value -> Cmd msg

type Msg = Run D.Value

counter s = D.decodeValue UInt64.decoder (E.string s) |> Result.withDefault UInt64.zero
routes = [ "applications", "system", "notifications" ]
base = P.Choices P.Keep P.Keep P.Keep
changed = P.Choices P.Alternate P.Default P.Default
snapshot revision values = P.Snapshot 1 (counter revision) values
row normal alternate active available = P.Row normal alternate available True active
inventory values available =
    P.Inventory (String.repeat 64 "a")
        (row "SUPER + ALT + SPACE" "SUPER + CTRL + ALT + SPACE" values.applications available)
        (row "SUPER + ESCAPE" "SUPER + CTRL + ESCAPE" values.system True)
        (row "SUPER + SHIFT + ALT + comma" "SUPER + CTRL + ALT + comma" values.notifications True)

choices values = E.object (List.map (\r -> (r, E.string (P.name (P.choices r values)))) routes)
maybe f value = Maybe.map f value |> Maybe.withDefault E.null
state model = E.object
    [ ("snapshot", maybe (\s -> E.object [("revision", E.string (UInt64.string s.revision)), ("choices", choices s.choices)]) model.snapshot)
    , ("inventory", maybe (\i -> E.object [("fingerprint",E.string i.fingerprint), ("active",choices (P.Choices i.applications.active i.system.active i.notifications.active)), ("applicationsDefaultAvailable",E.bool i.applications.defaultAvailable)]) model.inventory)
    , ("draft", choices model.draft)
    , ("conflicts", E.list E.string model.conflicts)
    , ("pending", maybe (\p -> E.object [("request",E.string (UInt64.string p.request)),("choices",choices p.choices),("confirmation",E.string (case p.confirmation of
        P.Awaiting -> "awaiting"
        P.Unconfirmed -> "unconfirmed"))]) model.pending)
    , ("notice", E.string model.notice), ("ready",E.bool (P.ready model)), ("changed",E.bool (P.changed model)) ]

sameConflict a b = List.sort a == List.sort b
unconfirmedPending pending = Maybe.map (\p -> {p | confirmation=P.Unconfirmed}) pending
check name condition = (name, E.object [("expected", E.bool True), ("actual", E.bool condition)])
step revision finalRevision request op model =
    let
        stored = snapshot revision changed
        good = inventory base True
        (next, proposal) =
            case op of
                "load" -> (P.observe (Just (snapshot "1" base)) (Just good) model, Nothing)
                "edit-app" -> (P.edit "applications" P.Default model, Nothing)
                "edit-system" -> (P.edit "system" P.Alternate model, Nothing)
                "edit-notifications" -> (P.edit "notifications" P.Default model, Nothing)
                "same" -> (P.observe model.snapshot model.inventory model, Nothing)
                "stale" -> (P.observe (Just (snapshot "1" base)) (Just good) model, Nothing)
                "changed" -> (P.observe (Just stored) (Just good) model, Nothing)
                "reaffirm-app" -> (P.edit "applications" model.draft.applications model, Nothing)
                "reaffirm-system" -> (P.edit "system" model.draft.system model, Nothing)
                "failure" -> (P.observe Nothing Nothing model, Nothing)
                "recover" -> (P.observe model.snapshot (Just good) model, Nothing)
                "invalid" -> (P.observe model.snapshot (Just (inventory base False)) model, Nothing)
                "valid" -> (P.observe model.snapshot (Just good) model, Nothing)
                "save" -> P.propose (counter request) model
                "blocked-save" -> P.propose (counter request) model
                "newer-pending" -> (P.observe (Just (snapshot finalRevision (P.Choices P.Keep P.Keep P.Default))) (Just good) model, Nothing)
                "stale-stored" -> (P.receive (counter request) "Stored" (Just (snapshot revision model.draft)) (Just good) model, Nothing)
                "stale-saved" -> (P.receive (counter request) "Saved" (Just (snapshot revision model.draft)) (Just (inventory model.draft True)) model, Nothing)
                "stored-only" -> (P.receive (counter request) "Stored" (Just (snapshot finalRevision model.draft)) (Just good) model, Nothing)
                "unknown" -> (P.receive (counter request) "Unknown" Nothing (Just good) model, Nothing)
                "foreign" -> (P.receive UInt64.zero "Saved" (Just stored) (Just good) model, Nothing)
                "mismatch" -> (P.observe (Just (snapshot finalRevision model.draft)) (Just good) model, Nothing)
                "match" -> (P.observe (Just (snapshot finalRevision model.draft)) (Just (inventory model.draft True)) model, Nothing)
                "receipt" -> (P.receive (counter request) "Saved" (Just (snapshot finalRevision model.draft)) (Just (inventory model.draft True)) model, Nothing)
                _ -> (model, Nothing)
        checks = case op of
            "load" -> [check "initial observation reaches writable model" (next.snapshot /= Nothing && next.inventory /= Nothing && P.ready next)]
            "edit-app" -> [check "valid edit reaches chosen value" (next.draft.applications == P.Default && next.draft /= model.draft)]
            "edit-system" -> [check "valid edit reaches chosen value" (next.draft.system == P.Alternate && next.draft /= model.draft)]
            "edit-notifications" -> [check "valid edit reaches chosen value" (next.draft.notifications == P.Default && next.draft /= model.draft)]
            "same" -> [check "same revision retains draft and conflicts" (next.draft == model.draft && sameConflict next.conflicts model.conflicts && next.pending == model.pending)]
            "stale" -> [check "stale read preserves state" (next == model)]
            "changed" -> [check "new store preserves draft and identifies only changed routes" (next.draft == model.draft && sameConflict next.conflicts ["applications","system"] && not (P.ready next))]
            "reaffirm-app" -> [check "reaffirm clears only applications" (next.draft == model.draft && sameConflict next.conflicts ["system"] && not (P.ready next))]
            "reaffirm-system" -> [check "reaffirm clears remaining route and restores readiness" (next.draft == model.draft && List.isEmpty next.conflicts && P.ready next)]
            "failure" -> [check "failed read preserves snapshot draft pending and conflicts; blocks writes" (next.snapshot == model.snapshot && next.draft == model.draft && next.pending == model.pending && sameConflict next.conflicts model.conflicts && next.inventory == Nothing && not (P.ready next))]
            "recover" -> [check "recovery preserves draft and pending" (next.draft == model.draft && next.pending == model.pending)]
            "invalid" -> [check "invalidated selected chord blocks readiness" (not (P.ready next) && next.draft == model.draft)]
            "valid" -> [check "valid inventory restores readiness when no pending or conflicts" (P.ready next && next.draft == model.draft)]
            "save" -> [check "explicit valid save emits proposal and pending" (proposal /= Nothing && next.pending /= Nothing && next.draft == model.draft)]
            "blocked-save" -> [check "blocked save emits no proposal and preserves state" (proposal == Nothing && next == model)]
            "newer-pending" -> [check "newer pending read retains intent and creates route conflicts" (next.pending == unconfirmedPending model.pending && next.pending /= Nothing && next.draft == model.draft && sameConflict next.conflicts ["applications","system"])]
            "stale-stored" -> [check "late Stored cannot roll back newer basis or release pending" (next.snapshot == model.snapshot && next.inventory == model.inventory && next.pending == model.pending && sameConflict next.conflicts model.conflicts)]
            "stale-saved" -> [check "late Saved cannot roll back newer basis or release pending" (next.snapshot == model.snapshot && next.inventory == model.inventory && next.pending == model.pending && sameConflict next.conflicts model.conflicts)]
            "stored-only" -> [check "definite stored completion preserves unresolved native conflicts" (next.pending == Nothing && next.draft == model.draft && sameConflict next.conflicts ["applications","system"] && not (P.ready next))]
            "unknown" -> [check "unknown preserves pending and draft" (next.pending == unconfirmedPending model.pending && next.draft == model.draft)]
            "foreign" -> [check "foreign receipt preserves entire state" (next == model)]
            "mismatch" -> [check "stored match with native mismatch remains pending" (next.pending == unconfirmedPending model.pending && next.pending /= Nothing && next.draft == model.draft)]
            "match" -> [check "exact stored and native match settles pending" (model.pending /= Nothing && next.pending == Nothing && next.draft == model.draft)]
            "receipt" -> [check "matching saved receipt settles pending" (model.pending /= Nothing && next.pending == Nothing && next.draft == model.draft)]
            _ -> [check "recognized event" False]
    in (next, E.object [("event",E.string op),("input",E.object [("revision",E.string revision),("request",E.string request),("finalRevision",E.string finalRevision)]),("before",state model),("after",state next),("proposal",maybe identity proposal),("checks",E.object checks)])

run raw =
    let decoder = D.map4 (\revision finalRevision request events -> { revision = revision, finalRevision = finalRevision, request = request, events = events }) (D.field "revision" D.string) (D.field "finalRevision" D.string) (D.field "request" D.string) (D.field "events" (D.list D.string))
    in case D.decodeValue decoder raw of
        Err err -> E.object [("inputError",E.string (D.errorToString err))]
        Ok input ->
            let folder event (model,entries) = let (next,entry) = step input.revision input.finalRevision input.request event model in (next,entry::entries)
                (_,trace) = List.foldl folder (P.initial,[]) input.events
            in E.object [("input",raw),("trace",E.list identity (List.reverse trace))]

main = Platform.worker {init = \() -> ((),Cmd.none), update = \(Run raw) model -> (model,outgoing (run raw)), subscriptions = \_ -> incoming Run}
