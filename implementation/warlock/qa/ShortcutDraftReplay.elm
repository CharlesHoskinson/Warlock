port module ShortcutDraftReplay exposing (main)

import Desktop
import NativePointerFixture
import ShortcutPreferences as P
import Json.Decode as D
import Json.Encode as E
import Platform
import UInt64

port outgoing : E.Value -> Cmd msg
counter value = D.decodeValue UInt64.decoder (E.string value) |> Result.withDefault UInt64.zero
bound = E.object [("lifetime",E.string "1"),("session",E.string "1"),("frontend",E.string "1")]
foreign = E.object [("lifetime",E.string "1"),("session",E.string "1"),("frontend",E.string "2")]
attached = E.object [("protocolVersion",E.int 3),("kind",E.string "attached"),("binding",bound)]
native wire model = NativePointerFixture.incoming wire model |> Tuple.first
dispatch message model = Desktop.capture model |> Maybe.map (\stamp -> Desktop.update (message stamp) model) |> Maybe.withDefault (model,[])
preferences revision values = {schema=1,revision=counter revision,choices=values}
row normal alternate alternateAvailable active = E.object [("defaultChord",E.string normal),("alternateChord",E.string alternate),("defaultAvailable",E.bool True),("alternateAvailable",E.bool alternateAvailable),("active",E.string active)]
inventory available apps = E.object [("fingerprint",E.string (String.repeat 64 "a")),("applications",row "SUPER + ALT + SPACE" "SUPER + CTRL + ALT + SPACE" available apps),("system",row "SUPER + ESCAPE" "SUPER + CTRL + ESCAPE" True "default"),("notifications",row "SUPER + SHIFT + ALT + comma" "SUPER + CTRL + ALT + comma" True "keep")]
receipt binding request snapshot inv = E.object [("protocolVersion",E.int 3),("kind",E.string "shortcut-preferences"),("binding",binding),("requestId",E.string (UInt64.string request)),("snapshot",P.encode snapshot),("inventory",inv)]
outcome request status = E.object [("protocolVersion",E.int 3),("kind",E.string "shortcut-preferences-outcome"),("binding",bound),("requestId",E.string (UInt64.string request)),("status",E.string status),("snapshot",E.null),("inventory",inventory True "keep")]
write effect = case effect of
    Desktop.Send raw -> D.decodeValue (D.field "kind" D.string) raw == Ok "shortcut-preferences-write"
    _ -> False

result =
    let initial = native attached Desktop.initial
        opened = dispatch Desktop.OpenSettings initial |> Tuple.first
        request = opened.shortcutExpected |> Maybe.withDefault UInt64.zero
        base = preferences "1" P.defaults
        loaded = native (receipt bound request base (inventory True "keep")) opened
        edited = dispatch (\s -> Desktop.EditShortcutChoice s "applications" P.Alternate) loaded |> Tuple.first
        complete = edited |> (dispatch (\s -> Desktop.EditShortcutChoice s "system" P.Default) >> Tuple.first) |> (dispatch (\s -> Desktop.EditShortcutChoice s "notifications" P.Keep) >> Tuple.first)
        (refreshing,reads) = dispatch Desktop.RefreshShortcutChoices complete
        readId = refreshing.shortcutExpected |> Maybe.withDefault UInt64.zero
        (after,afterEffects) = NativePointerFixture.incoming (receipt bound readId base (inventory True "keep")) refreshing
        wrongBinding = native (receipt foreign readId base (inventory True "keep")) refreshing
        wrongRequest = native (receipt bound (counter "999") base (inventory True "keep")) refreshing
        closed = dispatch Desktop.CloseSettings complete |> Tuple.first
        (reopened,reopenReads) = dispatch Desktop.OpenSettings closed
        reopenId = reopened.shortcutExpected |> Maybe.withDefault UInt64.zero
        afterReopen = native (receipt bound reopenId base (inventory True "keep")) reopened
        unavailable = native (receipt bound readId base (inventory False "keep")) refreshing
        changedSnapshot = preferences "2" {applications=P.Keep,system=P.Default,notifications=P.Keep}
        changed = native (receipt bound readId changedSnapshot (inventory True "keep")) refreshing
        (saving,writes) = dispatch Desktop.SaveShortcutChoices complete
        pendingId = saving.shortcutPreferences.pending |> Maybe.map .request |> Maybe.withDefault UInt64.zero
        unknown = native (outcome pendingId "Unknown") saving
        (unknownRefresh,unknownReads) = dispatch Desktop.RefreshShortcutChoices unknown
        unknownReadId = unknownRefresh.shortcutExpected |> Maybe.withDefault UInt64.zero
        unknownMismatch = native (receipt bound unknownReadId base (inventory True "keep")) unknownRefresh
        wanted = preferences "2" complete.shortcutPreferences.draft
        (unknownExact,exactEffects) = NativePointerFixture.incoming (receipt bound unknownReadId wanted (inventory True "alternate")) unknownRefresh
        checks =
            [ ("preconditionDirtyAlternate",complete.shortcutPreferences.draft.applications==P.Alternate && P.ready complete.shortcutPreferences && complete.shortcutPreferences.snapshot==Just base && not (List.any write reads))
            , ("refreshRequestIsLive",refreshing.shortcutExpected/=Nothing && List.length reads==1)
            , ("foreignBindingIgnored",wrongBinding==refreshing)
            , ("foreignRequestIgnored",wrongRequest==refreshing)
            , ("matchedReadDoesNotWrite",not (List.any write afterEffects))
            , ("sameRevisionRetainsDirty",after.shortcutPreferences.draft.applications==P.Alternate)
            , ("reopenOnlyReads",reopened.shortcutExpected/=Nothing && not (List.any write reopenReads))
            , ("reopenRetainsDirty",afterReopen.shortcutPreferences.draft.applications==P.Alternate)
            , ("invalidInventoryKeepsIntentAndBlocksReady",unavailable.shortcutPreferences.draft.applications==P.Alternate && not (P.ready unavailable.shortcutPreferences))
            , ("changedRevisionKeepsLocalIntent",changed.shortcutPreferences.draft.applications==P.Alternate && not (P.ready changed.shortcutPreferences))
            , ("unknownSaveWasSubmittedOnce",List.length (List.filter write writes)==1 && unknown.shortcutPreferences.pending/=Nothing)
            , ("unknownRefreshDoesNotWrite",List.length unknownReads==1 && not (List.any write unknownReads))
            , ("unknownMismatchStaysPending",unknownMismatch.shortcutPreferences.pending/=Nothing)
            , ("unknownExactReadDoesNotWrite",not (List.any write exactEffects))
            , ("unknownExactSettles",unknownExact.shortcutPreferences.pending==Nothing && unknownExact.shortcutPreferences.snapshot==Just wanted)
            ]
    in E.object [("checks",E.object (List.map (\(name,ok) -> (name,E.bool ok)) checks))]
main = Platform.worker {init=\() -> ((),outgoing result),update=\_ state -> (state,Cmd.none),subscriptions=\_ -> Sub.none}
