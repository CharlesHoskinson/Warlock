port module RestoreAnnouncementReplay exposing (main)

{-| Source-only component fixture: actual Effects snapshot/begin/receipt via
Desktop/Shell and OutcomeAnnouncements.observe. No native or AT claim. Synthetic
scene/binding are setup; second fresh intent uses a second isolated allocator
with advanced watermarks, not a replay of the first. -}
import Binding
import Desktop
import Effects
import Json.Decode as D
import Json.Encode as E
import OutcomeAnnouncements as Attention
import Platform
import Shell
import SnapReplay as Fixture
import Surface
import TaskbarShell
import UInt64

port outgoing : E.Value -> Cmd msg

counter = Fixture.counter
bound = Fixture.bound
foreign = E.object [("lifetime",E.string "1"),("session",E.string "2"),("frontend",E.string "1")]
context = E.object [("lifetime",E.string "1"),("epoch",E.string "1"),("output",E.string "1"),("revision",E.string "1")]
scene minimized = E.object [("revision",E.string "1"),("focused",E.null),("windows",E.list identity [E.object [("incarnation",E.string "1"),("label",E.string "Document"),("owner",E.null),("application",E.string "documents"),("minimized",E.bool minimized),("available",E.bool True)]])]
snapshot minimized = E.object [("kind",E.string "snapshot"),("context",context),("scene",scene minimized)]

-- Snapshot and action are processed by production Effects.apply, including
-- target eligibility and serial allocation; Desktop routes the action.
prepare binding minimized watermark =
    let base=Fixture.readyFor binding
        windows=base.windows
        shell=windows.shell
        (observed,_,_)=Effects.apply (snapshot minimized) Effects.empty
        effects={observed | request=watermark,generation=watermark}
    in {base | windows={windows | shell={shell | effects=effects,geometryCaps=Nothing,geometry=Nothing,geometryExpected=Nothing,geometryAttachExpected=Nothing}}}

begin operation model =
    Shell.capture model.windows.shell
        |> Maybe.map (\stamp -> Desktop.update (Desktop.Window (TaskbarShell.Native (Shell.Act stamp operation (counter "1")))) model)
        |> Maybe.withDefault (model,[])

receipt binding intent status = E.object [("protocolVersion",E.int 3),("kind",E.string "effect-outcome"),("effectProtocol",E.int 1),("binding",binding),("intent",Effects.encodeIntent intent),("status",E.string status),("reason",E.string "dependency-mismatch"),("revision",E.string "1"),("outputGeneration",E.string "1")]
applyReceipt binding intent status model = Desktop.update (Desktop.Window (TaskbarShell.Native (Shell.Incoming (receipt binding intent status)))) model

serial model = D.decodeValue (D.field "sequence" UInt64.decoder) (Attention.encode model) |> Result.withDefault UInt64.zero
text model = D.decodeValue (D.field "text" D.string) (Attention.encode model) |> Result.withDefault ""
quietEffects effects = List.all (\effect -> case effect of
    Desktop.Focus _ -> False
    Desktop.Send raw -> D.decodeValue (D.field "kind" D.string) raw /= Ok "window-effect"
    Desktop.WindowEffect (Shell.Send raw) -> D.decodeValue (D.field "kind" D.string) raw /= Ok "window-effect"
    _ -> True) effects

result binding watermark =
    let base=prepare binding True watermark
        (pending,beginEffects)=begin Effects.Restore base
        intent=pending.windows.shell.effects.transaction |> Maybe.map .intent
        pendingAttention=Attention.observe base pending Attention.initial
        (refused,refusedEffects)=intent |> Maybe.map (\i -> applyReceipt bound i "Refused" pending) |> Maybe.withDefault (pending,[])
        refusedAttention=Attention.observe pending refused pendingAttention
        (unknown,unknownEffects)=intent |> Maybe.map (\i -> applyReceipt bound i "Unknown" pending) |> Maybe.withDefault (pending,[])
        unknownAttention=Attention.observe pending unknown pendingAttention
        (unknownAgain,unknownAgainEffects)=intent |> Maybe.map (\i -> applyReceipt bound i "Unknown" unknown) |> Maybe.withDefault (unknown,[])
        (unknownRefused,unknownRefusedEffects)=intent |> Maybe.map (\i -> applyReceipt bound i "Refused" unknown) |> Maybe.withDefault (unknown,[])
        (foreignState,foreignEffects)=intent |> Maybe.map (\i -> applyReceipt foreign i "Refused" pending) |> Maybe.withDefault (pending,[])
        (staleState,staleEffects)=intent |> Maybe.map (\i -> applyReceipt bound {i|request=if i.request==counter "1" then counter "2" else counter "1"} "Refused" pending) |> Maybe.withDefault (pending,[])
        duplicate=Attention.observe pending pending pendingAttention
        repeated=Attention.observe refused refused refusedAttention
        nextWatermark=UInt64.next watermark |> Maybe.withDefault UInt64.zero
        (second,secondEffects)=begin Effects.Restore (prepare binding True nextWatermark)
        secondAttention=Attention.observe (prepare binding True nextWatermark) second pendingAttention
        (other,otherEffects)=begin Effects.Minimize (prepare binding False watermark)
        otherAttention=Attention.observe (prepare binding False watermark) other Attention.initial
        mismatchedWindows=base.windows
        mismatchedShell=mismatchedWindows.shell
        missingBinding={base|windows={mismatchedWindows|shell={mismatchedShell|binding=Nothing}}}
        badBinding=Attention.observe missingBinding pending Attention.initial
        checks=
            [ ("ActualRestoreBeginAllocated",intent/=Nothing && List.length beginEffects==1 && (pending.windows.shell.effects.transaction |> Maybe.map .status)==Just Effects.Pending)
            , ("PendingAnnounced",serial pendingAttention==counter "1" && text pendingAttention==Surface.windowNotice pending && String.startsWith "Restore:" (text pendingAttention))
            , ("RefusedViaActualReceipt",(refused.windows.shell.effects.transaction |> Maybe.map .status)==Just Effects.Refused && serial refusedAttention==counter "2" && text refusedAttention==Surface.windowNotice refused)
            , ("UnknownViaActualReceipt",(unknown.windows.shell.effects.transaction |> Maybe.map .status)==Just Effects.Unknown && serial unknownAttention==counter "2" && text unknownAttention==Surface.windowNotice unknown)
            , ("DuplicateUnknownSilent",serial (Attention.observe unknown unknownAgain unknownAttention)==serial unknownAttention && quietEffects unknownAgainEffects)
            , ("UnknownThenRefusedCorrelated",(unknownRefused.windows.shell.effects.transaction |> Maybe.map .status)==Just Effects.Refused && serial (Attention.observe unknown unknownRefused unknownAttention)==counter "3" && quietEffects unknownRefusedEffects)
            , ("IdenticalTransitionSilent",serial duplicate==serial pendingAttention && text duplicate==text pendingAttention)
            , ("RepeatedOutcomeSilent",serial repeated==serial refusedAttention && text repeated==text refusedAttention)
            , ("FreshIntentSameTextNewSerial",second.windows.shell.effects.transaction/=Nothing && (second.windows.shell.effects.transaction |> Maybe.map .intent)/=intent && List.length secondEffects==1 && text secondAttention==text pendingAttention && serial secondAttention==counter "2")
            , ("ForeignSessionReceiptInert",foreignState==pending && List.isEmpty foreignEffects && serial (Attention.observe pending foreignState pendingAttention)==serial pendingAttention)
            , ("StaleIntentReceiptInert",staleState==pending && List.isEmpty staleEffects && serial (Attention.observe pending staleState pendingAttention)==serial pendingAttention)
            , ("MismatchedBindingSilent",serial badBinding==UInt64.zero)
            , ("NoEffectSilent",serial (Attention.observe base base Attention.initial)==UInt64.zero)
            , ("NonRestoreSilent",other.windows.shell.effects.transaction/=Nothing && not (List.isEmpty otherEffects) && serial otherAttention==UInt64.zero)
            , ("OutcomesNoNewMutationOrFocus",quietEffects refusedEffects && quietEffects unknownEffects)
            ]
    in E.object [("checks",E.object (List.map (\(name,ok) -> (name,E.bool ok)) checks)),("scope",E.string "Actual Desktop/Shell Effects begin and receipt plus OutcomeAnnouncements; synthetic binding and scene; scoped OutputController routing, cross-frontend recovery, simultaneous candidate arbitration, native and AT remain unobserved.")]

-- Strict string counter and two available successors are required: one for
-- each distinct actual begin. No conversion through JS Number/Float.
fixture flags =
    case (D.decodeValue Binding.decoder bound, D.decodeValue (D.field "watermark" UInt64.decoder) flags) of
        (Ok binding,Ok watermark) ->
            case UInt64.next watermark |> Maybe.andThen UInt64.next of
                Just _ -> result binding watermark
                Nothing -> E.object [("checks",E.object [("watermarkCapacity",E.bool False)])]
        _ -> E.object [("checks",E.object [("fixtureInput",E.bool False)])]

main : Program D.Value () Never
main = Platform.worker {init=\flags -> ((),outgoing (fixture flags)),update=\_ model -> (model,Cmd.none),subscriptions=\_ -> Sub.none}
