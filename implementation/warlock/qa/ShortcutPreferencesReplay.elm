port module ShortcutPreferencesReplay exposing (main)
import Desktop
import NativePointerFixture
import ShortcutPreferences as P
import Surface
import SurfaceRenderer
import Json.Decode as D
import Json.Encode as E
import Platform
import UInt64
port outgoing : E.Value -> Cmd msg
counter value = D.decodeValue UInt64.decoder (E.string value) |> Result.withDefault UInt64.zero
bound = E.object [("lifetime",E.string "1"),("session",E.string "1"),("frontend",E.string "1")]
attached = E.object [("protocolVersion",E.int 3),("kind",E.string "attached"),("binding",bound)]
native wire model=NativePointerFixture.incoming wire model |> Tuple.first
dispatch message model=Desktop.capture model |> Maybe.map (\stamp -> Desktop.update (message stamp) model) |> Maybe.withDefault (model,[])
preferences revision values={schema=1,revision=counter revision,choices=values}
row normal alternate available active=E.object [("defaultChord",E.string normal),("alternateChord",E.string alternate),("defaultAvailable",E.bool available),("alternateAvailable",E.bool True),("active",E.string active)]
inventory active=E.object [("fingerprint",E.string (String.repeat 64 "a")),("applications",row "SUPER + ALT + SPACE" "SUPER + CTRL + ALT + SPACE" False active),("system",row "SUPER + ESCAPE" "SUPER + CTRL + ESCAPE" True "default"),("notifications",row "SUPER + SHIFT + ALT + comma" "SUPER + CTRL + ALT + comma" True "keep")]
receipt kind request status snapshot observation=E.object ([("protocolVersion",E.int 3),("kind",E.string kind),("binding",bound),("requestId",E.string (UInt64.string request)),("snapshot",snapshot),("inventory",observation)]++(if kind=="shortcut-preferences-outcome" then [("status",E.string status)] else []))
result=
    let initial=native attached Desktop.initial
        opened=dispatch Desktop.OpenSettings initial |> Tuple.first
        current=opened.shortcutExpected |> Maybe.withDefault UInt64.zero
        read=native (receipt "shortcut-preferences" current "" (P.encode (preferences "1" P.defaults)) (inventory "keep")) opened
        blocked=dispatch (\stamp -> Desktop.EditShortcutChoice stamp "applications" P.Default) read
        alternate=dispatch (\stamp -> Desktop.EditShortcutChoice stamp "applications" P.Alternate) read |> Tuple.first
        chosen=alternate |> (dispatch (\stamp -> Desktop.EditShortcutChoice stamp "system" P.Default) >> Tuple.first) |> (dispatch (\stamp -> Desktop.EditShortcutChoice stamp "notifications" P.Keep) >> Tuple.first)
        (saving,effects)=dispatch Desktop.SaveShortcutChoices chosen
        expected=saving.shortcutPreferences.pending |> Maybe.map .request |> Maybe.withDefault UInt64.zero
        (duplicate,duplicateEffects)=dispatch Desktop.SaveShortcutChoices saving
        wanted=preferences "2" chosen.shortcutPreferences.draft
        saved=native (receipt "shortcut-preferences-outcome" expected "Saved" (P.encode wanted) (inventory "alternate")) saving
        unknown=native (receipt "shortcut-preferences-outcome" expected "Unknown" E.null (inventory "keep")) saving
        (unknownDuplicate,unknownEffects)=dispatch Desktop.SaveShortcutChoices unknown
        (refreshing,refreshEffects)=dispatch Desktop.RefreshShortcutChoices unknown
        reconciled=native (receipt "shortcut-preferences" (refreshing.shortcutExpected |> Maybe.withDefault UInt64.zero) "" (P.encode wanted) (inventory "alternate")) refreshing
        wrong=native (receipt "shortcut-preferences-outcome" (counter "999") "Saved" (P.encode wanted) (inventory "alternate")) saving
        optimistic=native (receipt "shortcut-preferences-outcome" expected "Saved" (P.encode wanted) (inventory "keep")) saving
        restartOpened=dispatch Desktop.OpenSettings (native attached Desktop.initial) |> Tuple.first
        restarted=native (receipt "shortcut-preferences" (restartOpened.shortcutExpected |> Maybe.withDefault UInt64.zero) "" (P.encode wanted) (inventory "alternate")) restartOpened
        stale=Desktop.capture read |> Maybe.map (\stamp -> Desktop.update (Desktop.EditShortcutChoice stamp "applications" P.Keep) chosen |> Tuple.first) |> Maybe.withDefault chosen
        frame=Surface.packet (counter "30") (counter "1") read
        write effect=case effect of
            Desktop.Send raw -> D.decodeValue (D.field "kind" D.string) raw==Ok "shortcut-preferences-write"
            _ -> False
        checked name value=(name,E.bool value)
        checks=[checked "actualRendererAcceptsShortcutControls" (SurfaceRenderer.decode frame |> Result.map (SurfaceRenderer.mode >> (==) "settings") |> Result.withDefault False)
            ,checked "defaultConflictCannotBeChosen" (Tuple.first blocked==read && List.isEmpty (Tuple.second blocked))
            ,checked "freeAlternateIsExplicit" (chosen.shortcutPreferences.draft.applications==P.Alternate)
            ,checked "undecidedCannotSubmit" (not (P.ready read.shortcutPreferences))
            ,checked "oneGuardedPreferenceWrite" (List.length (List.filter write effects)==1)
            ,checked "pendingCannotRepeat" (duplicate==saving && List.isEmpty duplicateEffects)
            ,checked "unknownCannotRepeat" (unknownDuplicate==unknown && List.isEmpty unknownEffects && unknown.shortcutPreferences.pending/=Nothing)
            ,checked "unknownRefreshOnlyReads" (List.length refreshEffects==1 && not (List.any write refreshEffects))
            ,checked "readReconcilesActualStoredAndNativeState" (reconciled.shortcutPreferences.pending==Nothing && reconciled.shortcutPreferences.snapshot==Just wanted)
            ,checked "savedRequiresActualChosenNativeState" (saved.shortcutPreferences.pending==Nothing && optimistic.shortcutPreferences.pending/=Nothing)
            ,checked "foreignReceiptCannotCommit" (wrong==saving)
            ,checked "staleControlCannotEdit" (stale==chosen)
            ,checked "hostRestartRestoresStoredChoiceWithoutEffects" (restarted.shortcutPreferences.draft==wanted.choices)
            ,checked "renderedDefaultConflictDisabled" (List.any (\c -> c.id=="settings:shortcuts:applications:default" && not c.enabled) (Surface.controls read))
            ,checked "helpRemainsAvailable" (List.any (\c -> c.id=="settings:help" && c.enabled) (Surface.controls saving))]
    in E.object [("checks",E.object checks),("frame",frame),("savedFrame",Surface.packet (counter "31") (counter "1") saved),("pendingFrame",Surface.packet (counter "32") (counter "1") saving),("unknownFrame",Surface.packet (counter "33") (counter "1") unknown)]
main=Platform.worker {init=\() -> ((),outgoing result),update=\_ model -> (model,Cmd.none),subscriptions=\_ -> Sub.none}
