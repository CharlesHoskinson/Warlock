port module SwitcherReplay exposing (main)

import ActionProjection as Scene
import Binding
import Desktop
import GeometryProjection as Geometry
import Json.Decode as D
import Json.Encode as E
import Platform
import Shell
import Surface
import SurfaceRenderer
import TaskbarShell
import Switcher as S
import UInt64

port outgoing : E.Value -> Cmd msg

counter value = D.decodeValue UInt64.decoder (E.string value) |> Result.withDefault UInt64.zero
one=counter "1"
two=counter "2"
three=counter "3"
family id = {root=counter id,label=id,application=id,minimized=False,available=True,active=id=="3"}
rows=List.map family ["1","2","3"]
history=[three,two,one]
start=S.step one 1 S.Forward S.initial |> Tuple.first
browsing=S.ready one history rows (Just three) start |> Tuple.first
root model=S.selected model |> Maybe.map .root
cycle number direction model=S.step one number direction model |> Tuple.first
binding=D.decodeValue Binding.decoder (E.object [("lifetime",E.string "1"),("session",E.string "1"),("frontend",E.string "1")]) |> Result.toMaybe
context={lifetime=one,epoch=one,output=one,revision=one}
window id=E.object [("incarnation",E.string id),("label",E.string id),("owner",E.null),("application",E.string id),("minimized",E.bool False),("available",E.bool True)]
scene=Scene.decode (E.object [("revision",E.string "1"),("focused",E.string "3"),("windows",E.list window ["1","2","3"])]) |> Result.toMaybe
geometryWindow id = {incarnation=id,owner=Nothing,workspace=Just "1",workspaceGeneration=Just one,monitor=Just UInt64.zero,outputOwnershipGeneration=Just one,workAreaRevision=Just one,workArea=Just [0,0,800,552],logicalGeometry=[40,100,320,240],visualGeometry=[40,100,320,240],nativeMode=Geometry.Ordinary,clientMode=Geometry.Ordinary,minimized=False,floating=True,grouped=False,fixedSize=False,constrainedSize=False,eligible=False,placementKnown=False,maximize=False,restoreGeometry=False,sizePolicy=Nothing}
base =
    let initial=Desktop.initial
        windows=initial.windows
        shell=windows.shell
        effects=shell.effects
        geometry=binding |> Maybe.map (\b -> {binding=b,request=one,sequence=one,context=context,focused=Just three,blocked=False,windows=List.map geometryWindow [one,two,three]})
    in {initial | windows={windows | shell={shell | binding=binding,phase=Shell.Ready,effects={effects | connected=True,observed=scene |> Maybe.map (\s -> {context=context,scene=s})},geometry=geometry}}}
scoped make model=Desktop.capture model |> Maybe.map (\stamp -> Desktop.update (make stamp) model) |> Maybe.withDefault (model,[])
historyFrame model=binding |> Maybe.map (\b -> E.object [("protocolVersion",E.int 3),("kind",E.string "activation-history"),("binding",Binding.encode b),("requestId",E.string (model.switcherExpected |> Maybe.map UInt64.string |> Maybe.withDefault "99")),("context",E.object [("lifetime",E.string "1"),("epoch",E.string "1"),("output",E.string "1"),("revision",E.string "1")]),("roots",E.list (UInt64.string >> E.string) history)]) |> Maybe.withDefault E.null
journalFrame nativeGeneration roots historySteps released cancelled model = binding |> Maybe.map (\b -> E.object [("protocolVersion",E.int 3),("kind",E.string "switcher-journal"),("binding",Binding.encode b),("requestId",E.string "91"),("chord",E.object [("generation",E.string nativeGeneration),("roots",E.list E.string roots),("history",E.list E.string (List.reverse roots)),("origin",E.string "3"),("steps",E.list E.int historySteps),("released",E.bool released),("cancelled",E.bool cancelled),("consumed",E.bool False)])]) |> Maybe.withDefault E.null
journal gen roots steps released cancelled model=Desktop.update (Desktop.Incoming (journalFrame gen roots steps released cancelled model)) model
mutations effects=effects |> List.filter (\effect -> case effect of
    Desktop.Send raw -> D.decodeValue (D.field "kind" D.string) raw==Ok "window-effect"
    Desktop.WindowEffect (Shell.Send raw) -> D.decodeValue (D.field "kind" D.string) raw==Ok "window-effect"
    _ -> False)
event number model = case number of
    1 -> S.step one 2 S.Forward model
    2 -> S.release one 2 model
    _ -> S.ready one history rows (Just three) model
permutation order =
    let (final,choices)=List.foldl (\number (model,emitted) -> let (next,choice)=event number model in (next,choice |> Maybe.map (\row -> row.root::emitted) |> Maybe.withDefault emitted)) (start,[]) order
        (_,again)=S.release one 2 final
    in S.phase final==S.Resolved && choices==[one] && again==Nothing

main : Program () () Never
main=Platform.worker {init=\_ -> ((),outgoing result),update=\_ model -> (model,Cmd.none),subscriptions=\_ -> Sub.none}
result =
    let reverse=S.step one 1 S.Reverse S.initial |> Tuple.first |> S.ready one history rows (Just three) |> Tuple.first
        retired=S.reconcile [family "1",family "3",family "4"] browsing
        chosen=S.choose one one browsing
        cancelled=S.cancel one browsing
        gap=S.step one 3 S.Forward start |> Tuple.first |> S.release one 3 |> Tuple.first |> S.ready one history rows (Just three) |> Tuple.first
        zero=S.ready one [] [] Nothing start
        single=S.ready one [one] [family "1"] (Just one) start |> Tuple.first |> S.release one 1
        opened=scoped (\stamp -> Desktop.OpenSwitcher stamp S.Forward) base |> Tuple.first
        -- Shell.Refresh changes phase; restore an admitted coherent read before
        -- delivering history so this test cannot imply an actual native refresh.
        windows=opened.windows
        readyBase={opened | windows={windows | shell=base.windows.shell}}
        (integrated,received)=Desktop.update (Desktop.Incoming (historyFrame readyBase)) readyBase
        (closed,closeEffects)=scoped Desktop.CloseSwitcher integrated
        (committed,commitEffects)=scoped Desktop.CommitSwitcher integrated
        oldStamp=Desktop.capture integrated
        stale=oldStamp |> Maybe.map (\stamp -> Desktop.update (Desktop.CommitSwitcher stamp) closed) |> Maybe.withDefault (closed,[])
        presentation=Surface.packet one one integrated
        (nativeOpened,nativeOpenEffects)=journal "90" ["1","2","3"] [1] False False base
        (nativeReleased,nativeReleaseEffects)=journal "90" ["1","2","3"] [1,1] True False nativeOpened
        (nativeDuplicate,nativeDuplicateEffects)=journal "90" ["1","2","3"] [1,1] True False nativeReleased
        (nativeCancelled,nativeCancelEffects)=journal "90" ["1","2","3"] [1,1] True True nativeReleased
        (frozenMembership,_)=journal "91" ["1","2"] [1] False False base
        coldWindows=base.windows
        coldShell=coldWindows.shell
        coldEffects=coldShell.effects
        cold={base | windows={coldWindows | shell={coldShell | effects={coldEffects | observed=Nothing},geometry=Nothing,phase=Shell.Reconciling}}}
        (early,earlyEffects)=journal "92" ["1","2","3"] [1,1] True False cold
        earlyWindows=early.windows
        readyEarly={early | windows={earlyWindows | shell=base.windows.shell}}
        (earlyResolved,earlyResolvedEffects)=Desktop.update (Desktop.Window (TaskbarShell.Native (Shell.Incoming E.null))) readyEarly
        checks=
            [("mruFirstForward",root browsing==Just two)
            ,("mruForwardWrap",root (cycle 2 S.Forward browsing)==Just one && root (cycle 3 S.Forward (cycle 2 S.Forward browsing))==Just three)
            ,("reverseFirst",root reverse==Just one)
            ,("releaseReadyStepPermutationsOnce",List.all permutation [[1,2,3],[1,3,2],[2,1,3],[2,3,1],[3,1,2],[3,2,1]])
            ,("gapWaits",S.phase gap==S.Waiting && (S.step one 2 S.Forward gap |> Tuple.second |> Maybe.map .root)==Just three)
            ,("cancelTombstones",S.phase (S.release one 1 cancelled |> Tuple.first)==S.Cancelled && (S.release one 1 cancelled |> Tuple.second)==Nothing)
            ,("contradictoryDuplicateCancels",S.phase (S.step one 1 S.Reverse browsing |> Tuple.first)==S.Cancelled)
            ,("oldGenerationIgnored",S.step UInt64.zero 2 S.Forward browsing |> Tuple.first |> S.generation |> (==) one)
            ,("arrivalExcluded",List.map .root (S.entries retired)==[three,one])
            ,("retiredSelectionAdvances",root retired==Just one && root (cycle 2 S.Forward retired)==Just three)
            ,("manualChoiceSurvivesNextStep",root (cycle 2 S.Forward chosen)==Just three)
            ,("zeroResolvesWithoutEffect",S.phase (Tuple.first zero)==S.Resolved && Tuple.second zero==Nothing)
            ,("oneResolvesSameFamily",Tuple.second single |> Maybe.map .root |> (==) (Just one))
            ,("integratedNativeHistoryOrder",Surface.mode integrated=="switcher" && root integrated.switcher==Just two && List.isEmpty (mutations received))
            ,("cancelClosesWithoutMutation",Surface.mode closed=="closed" && List.isEmpty (mutations closeEffects))
            ,("commitClosesAndRefreshesGrant",Surface.mode committed=="closed" && committed.choice/=Nothing && List.isEmpty (mutations commitEffects))
            ,("staleControlCannotCommit",(Tuple.first stale).choice==Nothing && List.isEmpty (mutations (Tuple.second stale)))
            ,("nativeJournalFreezesBeforeReady",List.map .root (S.entries frozenMembership.switcher)==[two,one])
            ,("nativeStepsUseOwnGeneration",S.generation nativeOpened.switcher==one && (nativeOpened.nativeSwitcher |> Maybe.map .generation)==Just (counter "90") && root nativeOpened.switcher==Just two && List.isEmpty (mutations nativeOpenEffects))
            ,("nativeReleaseResolvesOnce",nativeReleased.choice |> Maybe.map .root |> (==) (Just one))
            ,("nativeDuplicateDoesNotResolveAgain",nativeDuplicate.choice==nativeReleased.choice && List.isEmpty (mutations nativeDuplicateEffects))
            ,("nativeCancelDropsPendingSelection",nativeCancelled.choice==Nothing && Surface.mode nativeCancelled=="closed" && List.isEmpty (mutations nativeCancelEffects))
            ,("nativeReleaseBeforeReadyWaits",S.phase early.switcher==S.Waiting && early.choice==Nothing && List.isEmpty (mutations earlyEffects))
            ,("nativeReleaseBeforeReadyThenResolves",earlyResolved.choice |> Maybe.map .root |> (==) (Just one))
            ,("localNavigationKeepsNativeOrdinal",let moved=S.navigate S.Forward browsing in S.lastStep moved==1 && root moved==Just one && root (cycle 2 S.Forward moved)==Just three)
            ,("unknownManualChoiceCannotCommit",let (unchanged,commands)=scoped (\stamp -> Desktop.SwitcherChoose stamp (counter "99")) integrated in unchanged.choice==Nothing && List.isEmpty commands)
            ,("nativeReadinessDoesNotMutate",List.isEmpty (mutations earlyResolvedEffects) && List.isEmpty (mutations nativeReleaseEffects))
            ,("rendererAcceptsSwitcher",SurfaceRenderer.decode presentation |> Result.map (SurfaceRenderer.mode >> (==) "switcher") |> Result.withDefault False)]
    in E.object [("checks",E.object (List.map (\(name,value) -> (name,E.bool value)) checks)),("scope",E.string "Typed reducer and integrated current-history presentation/choice admission only; no global chord, native focus/AT or atomic cancellation verdict.")]
