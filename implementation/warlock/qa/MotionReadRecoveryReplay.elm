port module MotionReadRecoveryReplay exposing (main)

{-| Unexecuted QA draft. Requires the MotionPreferences Awaiting/Unconfirmed
bundle. It drives the actual Desktop update route. Its literal assertions cover
complete MotionPreferences.Model plus complete returned Desktop effects, not
complete DesktopPolicy state or native issuer/GUI behavior. -}

import Binding
import Desktop
import Json.Decode as D
import Json.Encode as E
import Motion
import MotionPreferences as Preference
import Platform
import SnapReplay as Fixture
import UInt64

port outgoing : E.Value -> Cmd msg

counter = Fixture.counter
native raw = Desktop.update (Desktop.Incoming raw)
dispatch build model = Desktop.capture model |> Maybe.map (\stamp -> Desktop.update (build stamp) model) |> Maybe.withDefault (model,[])
snapshot revision override = Preference.encode {revision=counter revision,override=override}
read model value = E.object [("protocolVersion",E.int 3),("kind",E.string "motion-preferences"),("binding",Fixture.bound),("requestId",E.string (UInt64.string (Maybe.withDefault UInt64.zero model.motionExpected))),("snapshot",value)]
outcome request status value = E.object [("protocolVersion",E.int 3),("kind",E.string "motion-preferences-outcome"),("binding",Fixture.bound),("requestId",E.string request),("status",E.string status),("snapshot",value)]
source = E.object [("protocolVersion",E.int 3),("kind",E.string "host-motion-preference"),("serial",E.string "1"),("profile",E.string "full"),("source",E.string "gtk")]
ack model = model.motion.pending |> Maybe.map (\pending -> native (E.object [("protocolVersion",E.int 3),("kind",E.string "motion-profile"),("binding",Binding.encode pending.binding),("requestId",E.string (UInt64.string pending.request)),("profile",E.string (Motion.name pending.profile))]) model |> Tuple.first) |> Maybe.withDefault model

exactSend expected effects = case effects of
    [Desktop.Send raw] -> E.encode 0 raw == E.encode 0 expected
    _ -> False

exactProfile = exactSend (E.object [("protocolVersion",E.int 3),("kind",E.string "motion-profile-set"),("binding",Fixture.bound),("requestId",E.string "7"),("profile",E.string "reduced")])
exactRead = exactSend (E.object [("protocolVersion",E.int 3),("kind",E.string "motion-preferences-request"),("binding",Fixture.bound),("requestId",E.string "7")])
exactWrite revision = exactSend (E.object [("protocolVersion",E.int 3),("kind",E.string "motion-preferences-write"),("binding",Fixture.bound),("requestId",E.string "6"),("proposal",snapshot revision Preference.Reduce)])

result binding seed =
    let revision = String.fromInt (seed+1)
        nextRevision = String.fromInt (seed+2)
        initial = Fixture.readyFor binding
        loaded = native (read initial (snapshot revision Preference.System)) initial |> Tuple.first
        full = native source loaded |> Tuple.first |> ack
        settings = {full | settingsOpen=True}
        edited = dispatch (\stamp -> Desktop.EditMotionPreference stamp Preference.Reduce) settings |> Tuple.first
        (saving,writeEffects) = dispatch Desktop.SaveMotionPreference edited
        (unknown,unknownEffects) = native (outcome "6" "Unknown" E.null) saving
        pending = {request=counter "6",revision=counter revision,override=Preference.Reduce,state=Preference.Unconfirmed}
        literalUnknown = {snapshot=Just {revision=counter revision,override=Preference.System},draft=Preference.Reduce,pending=Just pending,notice="Motion preference save not confirmed. Refresh to read stored values; this write will not be repeated."}
        (conflictRead,conflictRequest) = dispatch Desktop.RefreshMotionPreference unknown
        (conflict,conflictEffects) = native (read conflictRead (snapshot revision Preference.Full)) conflictRead
        (unavailableRead,unavailableRequest) = dispatch Desktop.RefreshMotionPreference unknown
        (unavailable,unavailableEffects) = native (read unavailableRead E.null) unavailableRead
        literalUnavailable = {literalUnknown | snapshot=Nothing,notice="Stored motion preference unavailable. Refresh to read it again; the stored copy is preserved."}
        (recoveryRead,recoveryRequest) = dispatch Desktop.RefreshMotionPreference unknown
        (recovered,recoveryEffects) = native (read recoveryRead (snapshot revision Preference.System)) recoveryRead
        literalRecovered = {snapshot=Just {revision=counter revision,override=Preference.System},draft=Preference.System,pending=Nothing,notice="Motion preference loaded."}
        (_,repeatEffects) = dispatch Desktop.SaveMotionPreference unknown
        (saved,savedEffects) = native (outcome "6" "Saved" (snapshot nextRevision Preference.Reduce)) unknown
        literalSaved = {snapshot=Just {revision=counter nextRevision,override=Preference.Reduce},draft=Preference.Reduce,pending=Nothing,notice="Motion preference saved."}
        check name value = (name,E.bool value)
        checks =
            [check "preludeExactPendingRequest" ((saving.motion.preferences.pending |> Maybe.map .request)==Just (counter "6") && exactWrite revision writeEffects)
            ,check "unknownLiteral" (unknown.motion.preferences==literalUnknown && List.isEmpty unknownEffects)
            ,check "explicitRefreshSendsOneRequest" (exactRead conflictRequest && exactRead unavailableRequest && exactRead recoveryRequest)
            ,check "conflictingSameRevisionReadRetainsLiteralPending" (conflict.motion.preferences==literalUnknown && List.isEmpty conflictEffects)
            ,check "unavailableReadRetainsLiteralPending" (unavailable.motion.preferences==literalUnavailable && List.isEmpty unavailableEffects)
            ,check "sameStoredReadReconcilesWithoutWriteReceipt" (recovered.motion.preferences==literalRecovered && List.isEmpty recoveryEffects)
            ,check "unknownNeverAutomaticallyRepeats" (List.isEmpty repeatEffects)
            ,check "lateSavedRequiresNewRevisionAndExactProfileEffect" (saved.motion.preferences==literalSaved && exactProfile savedEffects)
            ]
    in E.object [("seed",E.int seed),("revision",E.string revision),("checks",E.object checks)]

main : Program () () Never
main = Platform.worker
    { init = \_ -> ((),outgoing (case D.decodeValue Binding.decoder Fixture.bound of
        Err _ -> E.object [("bindingDecodeFailed",E.bool True)]
        Ok binding -> E.object [("cases",E.list (result binding) (List.range 0 15))]))
    , update = \_ model -> (model,Cmd.none)
    , subscriptions = \_ -> Sub.none
    }
