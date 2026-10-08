port module LiveMotionReplay exposing (main)

import Binding
import Desktop
import Effects
import Json.Decode as D
import Json.Encode as E
import Motion
import MotionPreferences as Preference
import Platform
import Shell
import SnapReplay as Fixture
import Surface
import SurfaceRenderer
import TaskbarShell
import UInt64

port outgoing : E.Value -> Cmd msg

counter = Fixture.counter
dispatch build model = Desktop.capture model |> Maybe.map (\stamp -> Desktop.update (build stamp) model) |> Maybe.withDefault (model,[])
native raw = Desktop.update (Desktop.Incoming raw)
snapshot revision override = Preference.encode {revision=counter revision,override=override}
loaded model value = E.object [("protocolVersion",E.int 3),("kind",E.string "motion-preferences"),("binding",Fixture.bound),("requestId",E.string (UInt64.string (Maybe.withDefault UInt64.zero model.motionExpected))),("snapshot",value)]
outcome model status value = E.object [("protocolVersion",E.int 3),("kind",E.string "motion-preferences-outcome"),("binding",Fixture.bound),("requestId",E.string (UInt64.string (model.motion.preferences.pending |> Maybe.map .request |> Maybe.withDefault UInt64.zero))),("status",E.string status),("snapshot",value)]
source serial profile = E.object [("protocolVersion",E.int 3),("kind",E.string "host-motion-preference"),("serial",E.string serial),("profile",E.string profile),("source",E.string "gtk")]
ack model = model.motion.pending |> Maybe.map (\pending -> native (E.object [("protocolVersion",E.int 3),("kind",E.string "motion-profile"),("binding",Binding.encode pending.binding),("requestId",E.string (UInt64.string pending.request)),("profile",E.string (Motion.name pending.profile))]) model) |> Maybe.withDefault (model,[])
kinds effects = List.filterMap (\effect -> case effect of
    Desktop.Send value -> D.decodeValue (D.field "kind" D.string) value |> Result.toMaybe
    Desktop.WindowEffect (Shell.Send value) -> D.decodeValue (D.field "kind" D.string) value |> Result.toMaybe
    _ -> Nothing) effects
edit override = dispatch (\stamp -> Desktop.EditMotionPreference stamp override)

result binding =
    let initial=Fixture.readyFor binding
        read=native (loaded initial (snapshot "1" Preference.System)) initial |> Tuple.first
        full=native (source "1" "full") read |> Tuple.first |> ack |> Tuple.first
        settings={full | settingsOpen=True}
        unsaved=edit Preference.Reduce settings |> Tuple.first
        (saving,writes)=dispatch Desktop.SaveMotionPreference unsaved
        (repeat,repeated)=dispatch Desktop.SaveMotionPreference saving
        malformed=native (outcome saving "Saved" (snapshot "1" Preference.Reduce)) saving |> Tuple.first
        wrong=native (outcome saving "Saved" (snapshot "2" Preference.Full)) saving |> Tuple.first
        (saved,apply)=native (outcome saving "Saved" (snapshot "2" Preference.Reduce)) saving
        reduced=ack saved |> Tuple.first
        changed=native (source "2" "full") reduced
        (refreshing,reads)=dispatch Desktop.RefreshMotionPreference (native (outcome saving "Unknown" E.null) saving |> Tuple.first)
        reconciled=native (loaded refreshing (snapshot "2" Preference.Reduce)) refreshing |> Tuple.first
        unknown=native (outcome saving "Unknown" E.null) saving |> Tuple.first
        (_,unknownWrites)=dispatch Desktop.SaveMotionPreference unknown
        refused=native (outcome saving "Refused" (snapshot "2" Preference.Full)) saving |> Tuple.first
        resetDraft=edit Preference.System reduced |> Tuple.first
        resetSaving=dispatch Desktop.SaveMotionPreference resetDraft |> Tuple.first
        (reset,resetCommands)=native (outcome resetSaving "Saved" (snapshot "3" Preference.System)) resetSaving
        disabled=ack reset |> Tuple.first
        restart=native (loaded initial (snapshot "2" Preference.Reduce)) initial |> Tuple.first
        unsupported=native (loaded initial E.null) initial |> Tuple.first
        recoverable=dispatch Desktop.OpenSettings unsupported |> Tuple.first
        (acted,windowCommands)=Shell.capture full.windows.shell |> Maybe.map (\stamp -> Desktop.update (Desktop.Window (TaskbarShell.Native (Shell.Act stamp Effects.Minimize (counter "1")))) full) |> Maybe.withDefault (full,[])
        during=native (source "2" "reduced") acted
        disconnected=native (E.object [("protocolVersion",E.int 3),("kind",E.string "host-disconnected")]) saving |> Tuple.first
        late=native (outcome saving "Saved" (snapshot "2" Preference.Reduce)) disconnected |> Tuple.first
        frame=Surface.packet (counter "8") (counter "1") reduced
        checks=
            [("initialReadUsesThirdSharedRequest",initial.motionExpected==Just (counter "3"))
            ,("followSystemLoadsFullProfile",Motion.desired full.motion==Motion.Full && Motion.ready full.windows.shell.binding full.motion)
            ,("draftDoesNotChangeEffectiveProfile",Motion.desired unsaved.motion==Motion.Full)
            ,("saveUsesOnePreferenceWrite",kinds writes==["motion-preferences-write"])
            ,("pendingWriteCannotRepeat",repeat==saving && List.isEmpty repeated)
            ,("sameRevisionCannotConfirmSave",Motion.desired malformed.motion==Motion.Full && malformed.motion.preferences.pending/=Nothing)
            ,("wrongValueCannotConfirmSave",Motion.desired wrong.motion==Motion.Full && wrong.motion.preferences.pending/=Nothing)
            ,("confirmedSaveConfiguresOneNativeProfile",kinds apply==["motion-profile-set"] && Motion.desired saved.motion==Motion.Reduced)
            ,("saveWaitsForNativeAcknowledgement",not (Motion.ready saved.windows.shell.binding saved.motion) && Motion.ready reduced.windows.shell.binding reduced.motion)
            ,("explicitOverrideWinsOverSystem",Motion.desired (Tuple.first changed).motion==Motion.Reduced && List.isEmpty (Tuple.second changed))
            ,("unknownPreservesPriorProfileAndNoReplay",Motion.desired unknown.motion==Motion.Full && unknown.motion.preferences.pending/=Nothing && List.isEmpty unknownWrites)
            ,("refreshOnlyReadsUnknownWrite",kinds reads==["motion-preferences-request"])
            ,("readReconcilesStoredOverride",Motion.desired reconciled.motion==Motion.Reduced && reconciled.motion.preferences.pending==Nothing)
            ,("refusalDoesNotApplyProposedOverride",Motion.desired refused.motion==Motion.Full && refused.motion.preferences.pending==Nothing)
            ,("resetRestoresCurrentSystemProfile",Motion.desired reset.motion==Motion.Full && kinds resetCommands==["motion-profile-set"])
            ,("disablingNeverReplaysWindowEffect",Motion.ready disabled.windows.shell.binding disabled.motion && disabled.windows==reduced.windows && not (List.member "window-effect" (kinds resetCommands)))
            ,("restartLoadsSavedOverrideBeforeSystemObservation",Motion.desired restart.motion==Motion.Reduced && restart.motion.pending/=Nothing)
            ,("unsupportedStorageRemainsRecoverableInSettings",unsupported.motion.preferences.snapshot==Nothing && recoverable.settingsOpen)
            ,("fixtureReallyHasPendingWindowEffect",Effects.pending acted.windows.shell.effects && List.member "window-effect" (kinds windowCommands))
            ,("liveSourcePreservesWholeWindowTransaction",(Tuple.first during).windows==acted.windows && kinds (Tuple.second during)==["motion-profile-set"])
            ,("retiredBindingCannotReceiveLatePreferenceSave",late==disconnected && disconnected.motion.preferences.pending==Nothing)
            ,("controlsExposeAllThreeChoices",List.all (\id -> List.any (\control -> control.id==id) (Surface.controls reduced)) ["settings:motion:system","settings:motion:reduced","settings:motion:full","settings:motion:save","settings:motion:refresh"])
            ,("settingsFrameAcceptedByActualRenderer",Result.toMaybe (SurfaceRenderer.decode frame)/=Nothing)
            ]
    in E.object [("checks",E.object (List.map (\(name,value)->(name,E.bool value)) checks)),("settingsFrame",frame)]

main : Program () () Never
main = Platform.worker {init=\_ -> ((),outgoing (D.decodeValue Binding.decoder Fixture.bound |> Result.map result |> Result.withDefault E.null)),update=\_ state -> (state,Cmd.none),subscriptions=\_ -> Sub.none}
