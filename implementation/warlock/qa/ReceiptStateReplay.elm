port module ReceiptStateReplay exposing (main)

{-| Actual controller/menu/receipt route. Native observations and receipts below
are explicit bridge fixtures, never an authenticated native issuer or execution
certificate. The independent Node oracle derives identities from raw inputs.
-}

import ActionProjection
import Binding
import Desktop
import Effects
import Json.Decode as D
import Json.Encode as E
import Menu
import MenuBridge
import NativeProvider
import OutputController as Outputs
import Platform
import Shell
import SurfaceController as Controller
import TaskbarShell
import UInt64

port outgoing : E.Value -> Cmd msg

counter value = D.decodeValue UInt64.decoder (E.string value) |> Result.withDefault UInt64.zero
increment value = counter value |> UInt64.next |> Maybe.map UInt64.string |> Maybe.withDefault value
advance count value = List.range 1 count |> List.foldl (\_ current -> increment current) value
ids seed =
    let shifted = advance (modBy 17 seed)
    in {life=shifted "9007199254741001",epoch=shifted "9007199254741101",session=shifted "9007199254741201",output=shifted "9007199254741301",revision=shifted "9007199254741401",request=shifted "9007199254741501",generation=shifted "9007199254741601",a=shifted "9007199254741701",b=shifted "9007199254741801",monitor=shifted "9007199254741901",variant=shifted "9007199254750001"}
bound i = E.object [("lifetime",E.string i.life),("session",E.string i.session),("frontend",E.string i.epoch)]
context i = E.object [("lifetime",E.string i.life),("epoch",E.string i.epoch),("output",E.string i.output),("revision",E.string i.revision)]
native kind fields = E.object ([("protocolVersion",E.int 3),("kind",E.string kind)]++fields)
shell model = (Controller.desktop (Outputs.controller model)).windows.shell
menus model = (Controller.desktop (Outputs.controller model)).windows.menus
effectState model = (shell model).effects
receive raw model = Outputs.update (Outputs.Interaction (Desktop.Incoming raw)) model
read raw model = receive raw model |> Tuple.first
interaction message model = Outputs.update (Outputs.Interaction message) model
wires emitted = emitted |> List.filterMap (\effect -> case effect of
    Controller.DesktopEffect (Desktop.WindowEffect (Shell.Send raw)) -> if D.decodeValue (D.field "kind" D.string) raw==Ok "window-effect" then Just raw else Nothing
    _ -> Nothing)
act operation target model = (if Effects.protocol operation==2 then Shell.captureGeometry (shell model) else Shell.capture (shell model))
    |> Maybe.map (\stamp -> interaction (Desktop.Window (TaskbarShell.Native (Shell.Act stamp operation (counter target)))) model)
    |> Maybe.withDefault (model,[])
expected selector model = selector (shell model) |> Maybe.map UInt64.string |> Maybe.withDefault "0"

topology = E.object [("viewProtocol",E.int 2),("kind",E.string "view-topology"),("revision",E.string "1"),("views",E.list identity [E.object [("id",E.string "1"),("generation",E.string "1")]]),("locations",E.list identity [E.object [("scope",E.object [("id",E.string "1"),("generation",E.string "1")]),("box",E.list E.int [0,0,800,600])]])]
projection i request =
    let window incarnation = E.object [("incarnation",E.string incarnation),("label",E.string ("Receipt window "++incarnation)),("owner",E.null),("application",E.string "receipt.desktop"),("minimized",E.bool False),("available",E.bool True)]
    in native "action-projection" [("binding",bound i),("requestId",E.string request),("context",context i),("scene",E.object [("revision",E.string i.revision),("focused",E.string i.a),("windows",E.list identity [window i.a,window i.b])])]
geometry i request =
    let projected logical visual configure = E.object [("logical",E.list E.float logical),("visual",visual),("real",E.list E.float logical),("configure",E.list E.float configure)]
        policy = E.object [("inputs",E.object [("profile",E.string "wayland-zero-origin-v1"),("rawMinimum",E.list E.float [1,1]),("rawMaximum",E.list E.float [0,0]),("layoutMinimum",E.list E.float [1,1]),("layoutMaximum",E.list E.float [10000,10000]),("geometryOrigin",E.list E.float [0,0]),("reservedTopLeft",E.list E.float [0,0]),("reservedBottomRight",E.list E.float [0,0]),("monitorScale",E.float 1)]),("maximize",projected [0,0,800,600] E.null [800,600]),("restoreGeometry",projected [10,20,320,240] (E.list E.float [10,20,320,240]) [320,240])]
        window = E.object [("incarnation",E.string i.a),("owner",E.null),("workspace",E.string "1"),("workspaceGeneration",E.string i.monitor),("monitor",E.string i.monitor),("outputOwnershipGeneration",E.string i.monitor),("workAreaRevision",E.string i.revision),("workArea",E.list E.float [0,0,800,600]),("logicalGeometry",E.list E.float [10,20,320,240]),("visualGeometry",E.list E.float [10,20,320,240]),("nativeMode",E.string "ordinary"),("clientMode",E.string "ordinary"),("minimized",E.bool False),("floating",E.bool True),("grouped",E.bool False),("fixedSize",E.bool False),("constrainedSize",E.bool True),("geometryEligible",E.bool True),("ordinaryPlacementKnown",E.bool False),("capabilities",E.object [("maximize",E.bool True),("restoreGeometry",E.bool False)]),("sizePolicy",policy),("pin",E.object [("pinned",E.bool False),("eligible",E.bool False)])]
    in native "geometry-facts" [("geometryProtocol",E.int 3),("binding",bound i),("requestId",E.string request),("sequence",E.string i.revision),("revision",E.string i.revision),("outputGeneration",E.string i.output),("facts",E.object [("focused",E.string i.a),("inputBlocked",E.bool False),("windows",E.list identity [window])])]
receipt i protocol intent status = native "effect-outcome" [("effectProtocol",E.int protocol),("binding",bound i),("intent",intent),("status",E.string status),("reason",E.string (if status=="Cancelled" then "cancelled-before-commit" else if status=="Unknown" then "effect-unproven" else if status=="Refused" then "stale-incarnation" else "applied")),("revision",E.string (increment i.revision)),("outputGeneration",E.string i.output)]
intentOf model = (effectState model).transaction |> Maybe.map (.intent >> Effects.encodeIntent) |> Maybe.withDefault E.null
transaction entry = E.object [("intent",Effects.encodeIntent entry.intent),("status",E.string (Effects.statusName entry.status)),("effectProtocol",E.int entry.effectProtocol)]
contextValue c = E.object [("lifetime",E.string (UInt64.string c.lifetime)),("epoch",E.string (UInt64.string c.epoch)),("output",E.string (UInt64.string c.output)),("revision",E.string (UInt64.string c.revision))]
menuOutcome outcome = case outcome of
    Menu.Committed -> "Committed"
    Menu.Refusal _ -> "Refusal"
    Menu.Cancellation -> "Cancellation"
    Menu.Uncertain -> "Uncertain"
state model =
    let current=shell model
        effects=current.effects
        menu=MenuBridge.menuSnapshot (menus model)
        observed value = E.object [("context",contextValue value.context),("windows",E.list (\window -> E.object [("incarnation",E.string (UInt64.string window.incarnation)),("owner",window.owner |> Maybe.map (UInt64.string >> E.string) |> Maybe.withDefault E.null),("label",E.string window.label),("application",E.string window.application),("minimized",E.bool window.minimized),("available",E.bool window.available),("attention",E.bool window.attention)]) (ActionProjection.windows value.scene))]
    in E.object [("request",E.string (UInt64.string effects.request)),("generation",E.string (UInt64.string effects.generation)),("transaction",effects.transaction |> Maybe.map transaction |> Maybe.withDefault E.null),("unresolved",E.list transaction effects.unresolved),("issued",E.list (\entry -> E.object [("binding",Binding.encode entry.binding),("protocol",E.int entry.protocol),("intent",Effects.encodeIntent entry.intent)]) current.issued),("observed",effects.observed |> Maybe.map observed |> Maybe.withDefault E.null),("connected",E.bool effects.connected),("binding",current.binding |> Maybe.map Binding.encode |> Maybe.withDefault E.null),("phase",E.string (case current.phase of
        Shell.Detached -> "Detached"
        Shell.Reconciling -> "Reconciling"
        Shell.Ready -> "Ready"
        Shell.Exhausted -> "Exhausted")),("menu",E.object [("outstanding",E.int menu.outstanding),("receiptCount",E.int (MenuBridge.receiptCount (menus model))),("lastOutcome",menu.lastOutcome |> Maybe.map (\(identity,outcome) -> E.object [("identity",E.int (Menu.intentNumber identity)),("outcome",E.string (menuOutcome outcome))]) |> Maybe.withDefault E.null)])]
diagnostics model = E.object [("notice",E.string (shell model).notice),("decoderRefusal",(shell model).decoderRefusal |> Maybe.map E.string |> Maybe.withDefault E.null)]

readSlots model =
    let current=shell model
        nullable value=value |> Maybe.map (UInt64.string >> E.string) |> Maybe.withDefault E.null
    in E.object [("projection",nullable current.expected),("geometry",nullable current.geometryExpected),("attach",nullable current.geometryAttachExpected)]

{-| Answer only outstanding production observation IDs. A completed geometry
batch may drain a dirty notification into another batch. The bound is an oracle
precondition, not permission to synthesize a mutation or force the phase Ready.
-}
drainReads i budget model =
    let current=shell model
        next=case current.expected of
            Just request -> Just (projection i (UInt64.string request))
            Nothing -> current.geometryExpected |> Maybe.map (UInt64.string >> geometry i)
    in case (budget>0,next) of
        (True,Just input) ->
            let (after,emitted)=receive input model
                remaining=drainReads i (budget-1) after
                step=E.object [("input",input),("slotsBefore",readSlots model),("slotsAfter",readSlots after),("before",state model),("after",state after),("emitted",E.list identity (wires emitted)),("diagnostics",diagnostics after)]
            in {model=remaining.model,steps=step::remaining.steps}
        _ -> {model=model,steps=[]}

setup i protocol =
    let attached=native "attached" [("binding",bound i)]
        watermarks=native "host-recovery-watermarks" [("binding",bound i),("request",E.string i.request),("generation",E.string i.generation)]
        beforeProjection=Outputs.update (Outputs.Topology topology) Outputs.initial |> Tuple.first |> read attached |> read watermarks
        firstProjection=projection i (expected .expected beforeProjection)
        pointer=native "pointer-ownership" [("ownershipProtocol",E.int 1),("binding",bound i),("requestId",E.string "1"),("serial",E.string "1"),("state",E.string "idle"),("owner",E.null)]
        ready=beforeProjection |> read firstProjection |> read pointer
        (bPending,bEffects)=act Effects.Minimize i.b ready
        bIntent=intentOf bPending
        bUnknown=receipt i 1 bIntent "Unknown"
        (bUncertain,bReceiptEffects)=receive bUnknown bPending
        bRead=projection i (expected .expected bUncertain)
        bReconciled=read bRead bUncertain
        negotiate=native "host-geometry-negotiate" []
        negotiated=if protocol==2 then read negotiate bReconciled else bReconciled
        caps=native "geometry-attached" [("geometryProtocol",E.int 3),("binding",bound i),("requestId",E.string (expected .geometryAttachExpected negotiated)),("capabilities",E.object [("observe",E.bool True),("effects",E.bool True),("effectProtocol",E.int 2),("operations",E.list E.string ["maximize"]),("placementCapacity",E.int 256),("canonicalScene",E.bool False)])]
        capped=if protocol==2 then read caps negotiated else negotiated
        facts=geometry i (expected .geometryExpected capped)
        prepared=if protocol==2 then read facts capped else capped
        provider=NativeProvider.fromShell {outputId=counter "1",providerId=counter "1",capabilityGeneration=counter i.revision} (counter i.a) (shell prepared) |> Result.toMaybe
        opened=provider |> Maybe.map (\value -> interaction (Desktop.Window (TaskbarShell.OpenMenu value)) prepared |> Tuple.first) |> Maybe.withDefault prepared
        selected=(MenuBridge.menuSnapshot (menus opened)).menu |> Maybe.map (\menu ->
            let wanted=if protocol==2 then Menu.Maximize else Menu.Minimize
                index=List.indexedMap Tuple.pair menu.items |> List.filter (\(_,item) -> item.action==wanted && item.enabled) |> List.head |> Maybe.map Tuple.first |> Maybe.withDefault -1
            in interaction (Desktop.Window (TaskbarShell.MenuEvent (Menu.Activate menu.id menu.binding index))) opened |> Tuple.first) |> Maybe.withDefault opened
        slot=MenuBridge.preparedSnapshot (menus selected)
        freshProjection=projection i (expected .expected selected)
        (legacyFresh,legacyEffects)=receive freshProjection selected
        freshGeometry=geometry i (expected .geometryExpected legacyFresh)
        (pending,aEffects)=if protocol==2 then receive freshGeometry legacyFresh else (legacyFresh,legacyEffects)
    in {ready=ready,bPending=bPending,bIntent=bIntent,bReconciled=bReconciled,prepared=prepared,pending=pending,aIntent=intentOf pending,provider=provider,slot=slot,
        raw=E.object [("binding",bound i),("topology",topology),("attached",attached),("watermarks",watermarks),("initialProjection",firstProjection),("pointer",pointer),("bUnknown",bUnknown),("bRead",bRead),("capabilities",if protocol==2 then caps else E.null),("geometry",if protocol==2 then facts else E.null),("freshProjection",freshProjection),("freshGeometry",if protocol==2 then freshGeometry else E.null)],
        bEffects=bEffects,bReceiptEffects=bReceiptEffects,aEffects=aEffects}

replace name value raw = D.decodeValue (D.keyValuePairs D.value) raw |> Result.map (\pairs -> E.object ((name,value)::List.filter (Tuple.first >> (/=) name) pairs)) |> Result.withDefault raw
field name raw = D.decodeValue (D.field name D.value) raw |> Result.withDefault E.null
eventRow name scenario status input before (after,emitted) = E.object [("name",E.string name),("scenario",E.string scenario),("status",E.string status),("input",input),("simulatedBridge",E.bool True),("before",state before),("after",state after),("emitted",E.list identity (wires emitted)),("diagnostics",diagnostics after)]
pipeline i protocol =
    let fixture=setup i protocol
        raw status=receipt i protocol fixture.aIntent status
        terminal status=eventRow ("receipt-"++status) ("receipt-"++String.toLower status) status (raw status) fixture.pending (receive (raw status) fixture.pending)
        drop=native "host-disconnected" []
        (disconnected,dropEffects)=receive drop fixture.pending
        outcomeRows=List.map terminal ["Committed","Refused","Cancelled"]
        pendingRow=eventRow "local-Pending" "receipt-pending" "Pending" (E.object [("kind",E.string "local-menu-action")]) fixture.prepared (fixture.pending,fixture.aEffects)
        dropRow=eventRow "connection-loss-Unknown" "architecture-007" "Unknown" drop fixture.pending (disconnected,dropEffects)
        (unknown,unknownEffects)=receive (raw "Unknown") fixture.pending
        (refreshing,refreshEffects)=interaction (Desktop.Window (TaskbarShell.Native Shell.Refresh)) unknown
        recoveryRead=projection i (expected .expected refreshing)
        (legacyRecovered,legacyReadEffects)=receive recoveryRead refreshing
        recoveryGeometry=geometry i (expected .geometryExpected legacyRecovered)
        (firstRecovered,geometryReadEffects)=if protocol==2 then receive recoveryGeometry legacyRecovered else (legacyRecovered,[])
        recoveryDrain=drainReads i 8 firstRecovered
        recovered=recoveryDrain.model
        (retry,retryEffects)=act (if protocol==2 then Effects.Maximize else Effects.Minimize) i.a recovered
        duplicate status =
            let (settled,_)=receive (raw status) fixture.pending
            in eventRow ("duplicate-"++status) "support-duplicate" status (raw status) settled (receive (raw status) settled)
        late status =
            let wire=receipt i 1 fixture.bIntent status
            in eventRow ("late-other-"++status) "support-late-other" status wire fixture.pending (receive wire fixture.pending)
        variant=E.string i.variant
        mutateContext key value originalIntent=replace "context" (replace key value (field "context" originalIntent)) originalIntent
        original=raw "Cancelled"
        inputIntent=field "intent" original
        mutated name intent= (name,replace "intent" intent original)
        badInputs=[("remote-Pending",replace "status" (E.string "Pending") original),("unknown-status",replace "status" (E.string "Bogus") original),("binding-lifetime",replace "binding" (replace "lifetime" variant (bound i)) original),("binding-session",replace "binding" (replace "session" variant (bound i)) original),("binding-frontend",replace "binding" (replace "frontend" variant (bound i)) original),mutated "request" (replace "request" variant inputIntent),mutated "generation" (replace "generation" variant inputIntent),mutated "incarnation" (replace "incarnation" variant inputIntent),mutated "operation" (replace "operation" (E.string "activate") inputIntent),mutated "lifetime" (mutateContext "lifetime" variant inputIntent),mutated "epoch" (mutateContext "epoch" variant inputIntent),mutated "output" (mutateContext "output" variant inputIntent),mutated "revision" (mutateContext "revision" variant inputIntent),("protocol",replace "effectProtocol" (E.int (if protocol==1 then 2 else 1)) original),("unexpected-field",replace "unexpected" (E.bool True) original),("numeric-request",replace "intent" (replace "request" (E.float 9007199254740992) inputIntent) original),("numeric-output",replace "outputGeneration" (E.float 9007199254740992) original),("overlong-reason",replace "reason" (E.string (String.repeat 257 "x")) original)]
        negative (name,input)=eventRow name "support-invalid" "unchanged" input fixture.pending (receive input fixture.pending)
    in E.object [("protocol",E.int protocol),("operation",E.string (if protocol==2 then "maximize" else "minimize")),("rawInputs",fixture.raw),("targetA",E.string i.a),("targetB",E.string i.b),("aIntent",fixture.aIntent),("bIntent",fixture.bIntent),("providerReady",E.bool (fixture.provider/=Nothing)),("selectionPrepared",E.bool (fixture.slot/=Nothing)),("initial",state fixture.ready),("bPending",state fixture.bPending),("bReconciled",state fixture.bReconciled),("beforeA",state fixture.prepared),("pendingA",state fixture.pending),("aEmitted",E.list identity (wires fixture.aEffects)),("bEmitted",E.list identity (wires fixture.bEffects)),("bReceiptEmitted",E.list identity (wires fixture.bReceiptEffects)),("scenarios",E.list identity (pendingRow::dropRow::outcomeRows)),("unknownReceipt",eventRow "matching-Unknown" "support-unknown" "Unknown" (raw "Unknown") fixture.pending (unknown,unknownEffects)),("duplicates",E.list duplicate ["Committed","Refused","Cancelled"]),("late",E.list late ["Committed","Cancelled"]),("negatives",E.list negative badInputs),("recovery",E.object [("before",state unknown),("readRequestState",state refreshing),("readInput",recoveryRead),("geometryInput",if protocol==2 then recoveryGeometry else E.null),("drainBound",E.int 8),("drain",E.list identity recoveryDrain.steps),("remainingSlots",readSlots recovered),("after",state recovered),("readEmitted",E.list identity (wires (refreshEffects++legacyReadEffects++geometryReadEffects))),("retryAfter",state retry),("retryEmitted",E.list identity (wires retryEffects))])]

result seed = E.object [("schema",E.int 1),("requirement",E.string "ELM-ARC-007"),("seed",E.int seed),("scope",E.string "Actual owning Elm request/menu/receipt routes with simulated bridge observations; no native execution or issuer evidence"),("pipelines",E.list (pipeline (ids seed)) [1,2])]
main : Program Int () Never
main = Platform.worker {init=\seed -> ((),outgoing (result seed)),update=\_ model -> (model,Cmd.none),subscriptions=\_ -> Sub.none}
