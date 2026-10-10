port module ShortcutGenerationReplay exposing (main)
import Desktop
import Json.Encode as E
import OutputController as Outputs
import OutputRetirementReplay as Fixture
import Platform
import Shell
port outgoing : E.Value -> Cmd msg
result =
 let ready=Fixture.base [("1",Fixture.left),("2",Fixture.right)]
     delayed=Fixture.shortcutAt "1" Fixture.bound "1" (E.list E.int Fixture.right)
     removed=Fixture.step (Outputs.Topology (Fixture.topology "2" [("1",Fixture.left)])) ready
     replaced=Fixture.step (Outputs.Topology (Fixture.topology "3" [("1",Fixture.left),("3",Fixture.right)])) removed
     staleFacts=Fixture.native Fixture.projection replaced
     early=Fixture.native delayed staleFacts
     reconciled=Fixture.reconcile "2" replaced
     late=Fixture.native delayed reconciled
     duplicate=Fixture.native delayed late
     recovered=Fixture.native (Fixture.shortcutAt "2" Fixture.bound "2" (E.list E.int Fixture.right)) late
     consumedEarly=Fixture.native delayed (Fixture.reconcile "2" early)
     emptied=Fixture.step (Outputs.Topology (Fixture.topology "2" [])) ready
     returned=Fixture.step (Outputs.Topology (Fixture.topology "3" [("3",Fixture.right)])) emptied |> Fixture.reconcile "2"
     oldAtReturn=Fixture.native delayed returned
     legacy=E.object [("protocolVersion",E.int 3),("kind",E.string "shell-shortcuts"),("shortcutProtocol",E.int 2),("binding",Fixture.bound),("requestId",E.string "1"),("serial",E.string "1"),("blocked",E.bool False),("events",E.list identity [E.object [("serial",E.string "1"),("route",E.string "applications"),("output",E.list E.int Fixture.right)]])]
     unstamped=Fixture.native legacy reconciled
     checks=[("OriginalRootStartsReady",(Fixture.desktop ready).windows.shell.phase==Shell.Ready)
       ,("OriginalOldObservationCannotReconcileReplacement",(Fixture.desktop staleFacts).windows.shell.phase/=Shell.Ready)
       ,("UnreconciledFreshReplyConsumed",not(Fixture.open early) && Fixture.seen early=="1")
       ,("ReconciledGenerationRejectsFreshOldReply",not(Fixture.open late) && Fixture.seen late=="1" && Fixture.owner late==Just "1")
       ,("ConsumedReplyCannotReplay",not(Fixture.open duplicate) && Outputs.frame duplicate==Outputs.frame late && not(Fixture.open consumedEarly))
       ,("FreshReplacementShortcutStillOpens",Fixture.open recovered && Fixture.owner recovered==Just "3")
       ,("AllGoneReturnRejectsOldReceipt",not(Fixture.open oldAtReturn) && Fixture.seen oldAtReturn=="1")
       ,("UnstampedLegacyConsumedWithoutRouting",not(Fixture.open unstamped) && Fixture.seen unstamped=="1")
       ,("NoWindowEffectFromOldReceipts",List.all (\m -> List.isEmpty (Fixture.desktop m).windows.shell.issued) [early,late,duplicate,consumedEarly,oldAtReturn,unstamped])]
 in E.object [("checks",E.object (List.map (Tuple.mapSecond E.bool) checks)),("recovered",Outputs.frame recovered),("rejected",Outputs.frame late)]
main : Program () () Never
main=Platform.worker {init=\_->((),outgoing result),update=\_ state->(state,Cmd.none),subscriptions=\_->Sub.none}
