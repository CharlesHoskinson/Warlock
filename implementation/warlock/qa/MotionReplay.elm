port module MotionReplay exposing (main)

import Binding
import Desktop
import Json.Decode as D
import Json.Encode as E
import Motion
import Platform
import Shell
import SnapReplay as Fixture
import Surface
import SurfaceRenderer
import UInt64

port outgoing : E.Value -> Cmd msg

observation serial profile = E.object [("protocolVersion",E.int 3),("kind",E.string "host-motion-preference"),("serial",E.string serial),("profile",E.string profile),("source",E.string "gtk")]
native raw = Desktop.update (Desktop.Incoming raw)
wire effects = List.filterMap (\effect -> case effect of
    Desktop.Send value -> Just value
    _ -> Nothing) effects

result binding =
    let base=Fixture.readyFor binding
        (first,commands)=native (observation "1" "reduced") base
        pending=first.motion.pending
        receipt p=E.object [("protocolVersion",E.int 3),("kind",E.string "motion-profile"),("binding",Binding.encode p.binding),("requestId",E.string (UInt64.string p.request)),("profile",E.string (Motion.name p.profile))]
        wrong=pending |> Maybe.map (\p -> native (receipt {p | request=Fixture.counter "999"}) first |> Tuple.first) |> Maybe.withDefault first
        settled=pending |> Maybe.map (\p -> native (receipt p) first) |> Maybe.withDefault (first,[])
        reduced=Tuple.first settled
        (changed,changeCommands)=native (observation "2" "full") reduced
        waiting=native (observation "3" "reduced") changed
        outdated=changed.motion.pending |> Maybe.map (\p -> native (receipt p) (Tuple.first waiting)) |> Maybe.withDefault waiting
        repeat=native (observation "1" "full") reduced
        duplicate=pending |> Maybe.map (\p -> native (receipt p) reduced) |> Maybe.withDefault (reduced,[])
        blocked=Desktop.capture first |> Maybe.map (\stamp -> Desktop.update (Desktop.OpenOverview stamp) first) |> Maybe.withDefault (first,[])
        disconnected=native (E.object [("protocolVersion",E.int 3),("kind",E.string "host-disconnected")]) changed |> Tuple.first
        frame=Surface.packet (Fixture.counter "1") (Fixture.counter "1") reduced
        decoded=SurfaceRenderer.decode frame
        malformed=E.object [("protocolVersion",E.int 3),("kind",E.string "host-motion-preference"),("serial",E.string "4"),("profile",E.string "fast"),("source",E.string "gtk")]
        checks=
            [("preferenceProducesOneProfileConfiguration",List.length (wire commands)==1 && first.motion.pending/=Nothing)
            ,("configurationHasNoWindowEffect",List.all (\v -> D.decodeValue (D.field "kind" D.string) v==Ok "motion-profile-set") (wire commands))
            ,("awaitAcknowledgementBeforeGesture",not (Motion.ready first.windows.shell.binding first.motion) && Tuple.first blocked==first && List.isEmpty (Tuple.second blocked))
            ,("wrongRequestCannotApplyProfile",wrong.motion==first.motion)
            ,("matchingAcknowledgementAppliesProfile",Motion.ready reduced.windows.shell.binding reduced.motion && List.isEmpty (Tuple.second settled))
            ,("duplicateAcknowledgementHasNoCommands",Tuple.first duplicate==reduced && List.isEmpty (Tuple.second duplicate))
            ,("staleObservationCannotChangeProfile",Tuple.first repeat==reduced && List.isEmpty (Tuple.second repeat))
            ,("changedPreferenceUsesOneConfiguration",List.length (wire changeCommands)==1 && Motion.desired changed.motion==Motion.Full)
            ,("newPreferenceWaitsForExistingConfiguration",List.isEmpty (Tuple.second waiting) && Motion.desired (Tuple.first waiting).motion==Motion.Reduced)
            ,("oldAcknowledgementConfiguresLatestPreferenceOnce",List.length (wire (Tuple.second outdated))==1 && ((Tuple.first outdated).motion.pending |> Maybe.map .profile)==Just Motion.Reduced)
            ,("disconnectRetiresProfileReceipt",disconnected.motion.pending==Nothing && disconnected.motion.applied==Nothing && disconnected.windows.shell.phase==Shell.Detached)
            ,("nativePreferenceSurvivesBindingRetirement",Motion.desired disconnected.motion==Motion.Full)
            ,("malformedProfileRejected",Tuple.first (native malformed reduced)==reduced)
            ,("surfaceCarriesTypedProfile",D.decodeValue (D.field "motion" D.string) frame==Ok "reduced" && Result.toMaybe decoded/=Nothing)
            ]
    in E.object [("checks",E.object (List.map (\(name,ok) -> (name,E.bool ok)) checks)),("frame",frame)]

main : Program () () Never
main = Platform.worker {init=\_ -> ((),outgoing (D.decodeValue Binding.decoder Fixture.bound |> Result.map result |> Result.withDefault E.null)),update=\_ state -> (state,Cmd.none),subscriptions=\_ -> Sub.none}
