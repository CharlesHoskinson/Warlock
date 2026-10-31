port module AuthorityTupleReplay exposing (main)

import ActionProjection
import Binding
import Desktop
import Effects
import Json.Decode as D
import Json.Encode as E
import OutputController as Outputs
import Platform
import Shell
import Snap
import SurfaceController as Controller
import TaskbarShell
import Transfer
import UInt64


port outgoing : E.Value -> Cmd msg


-- This is a bridge fixture, not an authenticated native producer. Every input
-- below enters the owning output/controller/desktop/native-message route. The
-- independent oracle derives authority from retained raw inputs, not the intent
-- encoder or a second expected-intent implementation in this fixture.
type alias Ids =
    { lifetime : String, epoch : String, session : String, output : String
    , revision : String, request : String, generation : String, incarnation : String
    , sequence : String, monitor : String, outputOwnership : String, workArea : String
    , workspace : String
    }


counter value = D.decodeValue UInt64.decoder (E.string value) |> Result.withDefault UInt64.zero
increment value = counter value |> UInt64.next |> Maybe.map UInt64.string |> Maybe.withDefault value
advance count value = List.range 1 count |> List.foldl (\_ current -> increment current) value


identities seed =
    let varied = advance (modBy 17 seed)
    in { lifetime=varied "9007199254741001",epoch=varied "9007199254741101"
       , session=varied "9007199254741201",output=varied "9007199254741301"
       , revision=varied "9007199254741401",request=varied "9007199254741501"
       , generation=varied "9007199254741601",incarnation=varied "9007199254741701"
       , sequence=varied "9007199254741801",monitor=varied "9007199254741901"
       , outputOwnership=varied "9007199254742001",workArea=varied "9007199254742101"
       , workspace=varied "9007199254742201" }


binding ids = E.object [("lifetime",E.string ids.lifetime),("session",E.string ids.session),("frontend",E.string ids.epoch)]
context ids = E.object [("lifetime",E.string ids.lifetime),("epoch",E.string ids.epoch),("output",E.string ids.output),("revision",E.string ids.revision)]
native kind fields = E.object ([("protocolVersion",E.int 3),("kind",E.string kind)] ++ fields)
shell model = (Controller.desktop (Outputs.controller model)).windows.shell
update event model = Outputs.update event model
receive raw model = update (Outputs.Interaction (Desktop.Incoming raw)) model
read raw model = receive raw model |> Tuple.first
effectState model = (shell model).effects


topology = E.object
    [("viewProtocol",E.int 2),("kind",E.string "view-topology"),("revision",E.string "1")
    ,("views",E.list identity [E.object [("id",E.string "1"),("generation",E.string "1")]])
    ,("locations",E.list identity [E.object [("scope",E.object [("id",E.string "1"),("generation",E.string "1")]),("box",E.list E.int [0,0,800,600])]])]


projection ids operation request =
    let minimized = operation=="restore"
        row = E.object [("incarnation",E.string ids.incarnation),("label",E.string "Authority fixture window"),("owner",E.null),("application",E.string "fixture.desktop"),("minimized",E.bool minimized),("available",E.bool True)]
    in native "action-projection"
        [("binding",binding ids),("requestId",E.string request),("context",context ids)
        ,("scene",E.object [("revision",E.string ids.revision),("focused",if minimized then E.null else E.string ids.incarnation),("windows",E.list identity [row])])]


operations = ["activate","minimize","restore","maximize","restore-geometry","exit-fullscreen","pin","unpin","snap","transfer-workspace"]
geometryOperations = ["maximize","restore-geometry","exit-fullscreen","pin","unpin","snap","transfer-workspace"]
geometryOperation name = List.member name geometryOperations


sizePolicy =
    let projected logical visual configure = E.object [("logical",E.list E.float logical),("visual",visual),("real",E.list E.float logical),("configure",E.list E.float configure)]
    in E.object
        [("inputs",E.object [("profile",E.string "wayland-zero-origin-v1"),("rawMinimum",E.list E.float [1,1]),("rawMaximum",E.list E.float [0,0]),("layoutMinimum",E.list E.float [1,1]),("layoutMaximum",E.list E.float [10000,10000]),("geometryOrigin",E.list E.float [0,0]),("reservedTopLeft",E.list E.float [0,0]),("reservedBottomRight",E.list E.float [0,0]),("monitorScale",E.float 1)])
        ,("maximize",projected [0,0,800,600] E.null [800,600])
        ,("restoreGeometry",projected [10,20,320,240] (E.list E.float [10,20,320,240]) [320,240])]


geometryWindow ids operation =
    let mode = if operation=="restore-geometry" then "maximized" else if operation=="exit-fullscreen" then "fullscreen" else "ordinary"
        eligible = mode/="fullscreen"
    in E.object
        [("incarnation",E.string ids.incarnation),("owner",E.null),("workspace",E.string "1"),("workspaceGeneration",E.string ids.workspace)
        ,("monitor",E.string ids.monitor),("outputOwnershipGeneration",E.string ids.outputOwnership),("workAreaRevision",E.string ids.workArea),("workArea",E.list E.float [0,0,800,600])
        ,("logicalGeometry",E.list E.float [10,20,320,240]),("visualGeometry",E.list E.float [10,20,320,240])
        ,("nativeMode",E.string mode),("clientMode",E.string mode),("minimized",E.bool False),("floating",E.bool True),("grouped",E.bool False)
        ,("fixedSize",E.bool False),("constrainedSize",E.bool True),("geometryEligible",E.bool eligible),("ordinaryPlacementKnown",E.bool (mode=="maximized"))
        ,("capabilities",E.object [("maximize",E.bool (mode=="ordinary")),("restoreGeometry",E.bool (mode=="maximized"))])
        ,("sizePolicy",sizePolicy),("pin",E.object [("pinned",E.bool (operation=="unpin")),("eligible",E.bool eligible)])]


geometryFacts ids operation request = native "geometry-facts"
    [("geometryProtocol",E.int 3),("binding",binding ids),("requestId",E.string request),("sequence",E.string ids.sequence)
    ,("revision",E.string ids.revision),("outputGeneration",E.string ids.output)
    ,("facts",E.object [("focused",E.string ids.incarnation),("inputBlocked",E.bool False),("windows",E.list identity [geometryWindow ids operation])])]


expectedRequest accessor model = accessor (shell model) |> Maybe.map UInt64.string |> Maybe.withDefault "0"


setup ids operation requestWatermark generationWatermark =
    let attached = native "attached" [("binding",binding ids)]
        watermarks = native "host-recovery-watermarks" [("binding",binding ids),("request",E.string requestWatermark),("generation",E.string generationWatermark)]
        pointer = native "pointer-ownership" [("ownershipProtocol",E.int 1),("binding",binding ids),("requestId",E.string "1"),("serial",E.string "1"),("state",E.string "idle"),("owner",E.null)]
        beforeAttached = update (Outputs.Topology topology) Outputs.initial |> Tuple.first
        beforeProjection = beforeAttached |> read attached |> read watermarks
        projected = projection ids operation (expectedRequest .expected beforeProjection)
        legacy = beforeProjection |> read projected |> read pointer
        negotiate = native "host-geometry-negotiate" []
        negotiated = if geometryOperation operation then read negotiate legacy else legacy
        caps = native "geometry-attached"
            [("geometryProtocol",E.int 3),("binding",binding ids),("requestId",E.string (expectedRequest .geometryAttachExpected negotiated))
            ,("capabilities",E.object [("observe",E.bool True),("effects",E.bool True),("effectProtocol",E.int 2),("operations",E.list E.string geometryOperations),("placementCapacity",E.int 256),("canonicalScene",E.bool False)])]
        attachedGeometry = if geometryOperation operation then read caps negotiated else negotiated
        facts = geometryFacts ids operation (expectedRequest .geometryExpected attachedGeometry)
        ready = if geometryOperation operation then read facts attachedGeometry else attachedGeometry
        admitted = E.object
            [("binding",binding ids),("topology",topology),("attached",attached),("watermarks",watermarks),("actionProjection",projected),("pointer",pointer)
            ,("negotiate",if geometryOperation operation then negotiate else E.null),("capabilities",if geometryOperation operation then caps else E.null),("geometryFacts",if geometryOperation operation then facts else E.null)]
    in {model=ready,beforeProjection=beforeProjection,beforeAttached=beforeAttached,admitted=admitted,projected=projected,attached=attached,watermarks=watermarks}


operationFor name target model =
    case name of
        "activate" -> Just Effects.Activate
        "minimize" -> Just Effects.Minimize
        "restore" -> Just Effects.Restore
        "maximize" -> Just Effects.Maximize
        "restore-geometry" -> Just Effects.RestoreGeometry
        "exit-fullscreen" -> Just Effects.ExitFullscreen
        "pin" -> Just Effects.Pin
        "unpin" -> Just Effects.Unpin
        "snap" -> (shell model).geometry |> Maybe.andThen (\observed -> Snap.open observed target |> Maybe.andThen Snap.proposal) |> Maybe.map Effects.SnapPlacement
        "transfer-workspace" -> (shell model).geometry |> Maybe.andThen (\observed -> Transfer.propose observed target "2") |> Maybe.map Effects.TransferWorkspace
        _ -> Nothing


stampFor operation model = if Effects.protocol operation==2 then Shell.captureGeometry (shell model) else Shell.capture (shell model)
actWith stamp operation target model = update (Outputs.Interaction (Desktop.Window (TaskbarShell.Native (Shell.Act stamp operation target)))) model
act operation target model = stampFor operation model |> Maybe.map (\stamp -> actWith stamp operation target model) |> Maybe.withDefault (model,[])


wires emitted = emitted |> List.filterMap (\effect -> case effect of
    Controller.DesktopEffect (Desktop.WindowEffect (Shell.Send raw)) -> if D.decodeValue (D.field "kind" D.string) raw==Ok "window-effect" then Just raw else Nothing
    _ -> Nothing)


transaction entry = E.object [("intent",Effects.encodeIntent entry.intent),("effectProtocol",E.int entry.effectProtocol),("status",E.string (Effects.statusName entry.status))]
state model =
    let current = shell model
        effects = current.effects
        contextValue c = E.object [("lifetime",E.string (UInt64.string c.lifetime)),("epoch",E.string (UInt64.string c.epoch)),("output",E.string (UInt64.string c.output)),("revision",E.string (UInt64.string c.revision))]
        observed value = E.object [("context",contextValue value.context),("windows",E.list (\row -> E.object [("incarnation",E.string (UInt64.string row.incarnation)),("minimized",E.bool row.minimized),("available",E.bool row.available)]) (ActionProjection.windows value.scene))]
    in E.object
        [("request",E.string (UInt64.string effects.request)),("generation",E.string (UInt64.string effects.generation))
        ,("transaction",effects.transaction |> Maybe.map transaction |> Maybe.withDefault E.null),("unresolved",E.list transaction effects.unresolved)
        ,("issued",E.list (\entry -> E.object [("binding",Binding.encode entry.binding),("protocol",E.int entry.protocol),("intent",Effects.encodeIntent entry.intent)]) current.issued)
        ,("observed",effects.observed |> Maybe.map observed |> Maybe.withDefault E.null),("binding",current.binding |> Maybe.map Binding.encode |> Maybe.withDefault E.null)
        ,("phase",E.string (case current.phase of
            Shell.Detached -> "Detached"
            Shell.Reconciling -> "Reconciling"
            Shell.Ready -> "Ready"
            Shell.Exhausted -> "Exhausted"))
        ,("connected",E.bool effects.connected),("available",E.bool (Shell.available current)),("observationRequest",E.string (UInt64.string current.request))
        ,("decoderRefusal",current.decoderRefusal |> Maybe.map E.string |> Maybe.withDefault E.null),("notice",E.string current.notice)]


receipt ids outcome model = (effectState model).transaction |> Maybe.map (\entry -> native "effect-outcome"
    [("effectProtocol",E.int entry.effectProtocol),("binding",binding ids),("intent",Effects.encodeIntent entry.intent),("status",E.string outcome)
    ,("reason",E.string "Simulated bridge fixture receipt; not native execution evidence"),("revision",E.string (increment ids.revision)),("outputGeneration",E.string ids.output)]) |> Maybe.withDefault E.null


positive ids name =
    let fixture = setup ids name ids.request ids.generation
        selected = operationFor name (counter ids.incarnation) fixture.model
        (pending,emitted) = selected |> Maybe.map (\operation -> act operation (counter ids.incarnation) fixture.model) |> Maybe.withDefault (fixture.model,[])
        rawReceipt = receipt ids "Committed" pending
        (settled,receiptEffects) = receive rawReceipt pending
    in E.object
        [("name",E.string name),("operation",E.string name),("effectProtocol",E.int (if geometryOperation name then 2 else 1)),("targetIncarnation",E.string ids.incarnation)
        ,("before",E.object [("request",E.string (UInt64.string (effectState fixture.model).request)),("generation",E.string (UInt64.string (effectState fixture.model).generation))])
        ,("admitted",fixture.admitted),("selectedStamp",selected |> Maybe.andThen (\operation -> stampFor operation fixture.model) |> Maybe.map (Shell.stampKey >> E.string) |> Maybe.withDefault E.null)
        ,("selectedOperationAvailable",E.bool (selected/=Nothing)),("emitted",E.list identity (wires emitted)),("custodyBefore",state fixture.model),("custodyAfter",state pending)
        ,("receipt",E.object [("simulated",E.bool True),("wire",rawReceipt),("after",state settled),("emittedAfter",E.list identity (wires receiptEffects))])]


replace fieldName value raw =
    D.decodeValue (D.keyValuePairs D.value) raw |> Result.map (List.map (\(name,old) -> (name,if name==fieldName then value else old)) >> E.object) |> Result.withDefault raw
field name raw = D.decodeValue (D.field name D.value) raw |> Result.withDefault E.null


negative name category input before (after,emitted) = E.object
    [("name",E.string name),("category",E.string category),("input",input),("before",state before)
    ,("custodyBefore",state before),("custodyAfter",state after),("effectCount",E.int (List.length (wires emitted))),("emitted",E.list identity (wires emitted))
    ,("diagnosticChangesAllowed",E.list E.string ["notice","decoderRefusal"])]


negatives ids =
    let legacy = setup ids "activate" ids.request ids.generation
        geometry = setup ids "maximize" ids.request ids.generation
        (pending,pendingEffects) = act Effects.Activate (counter ids.incarnation) legacy.model
        unknownRaw = receipt ids "Unknown" pending
        unknown = read unknownRaw pending
        terminalRaw = receipt ids "Committed" pending
        terminal = read terminalRaw pending
        attempt name category raw fixture = negative name category raw fixture (receive raw fixture)
        stampCase name replacement =
            let raw = E.object [("binding",binding ids),("output",E.string ids.output),("revision",E.string ids.revision)] |> replacement
                applied = D.decodeValue Shell.stampDecoder raw |> Result.map (\stamp -> actWith stamp Effects.Activate (counter ids.incarnation) legacy.model) |> Result.withDefault (legacy.model,[])
            in negative name "stale-stamp" raw legacy.model applied
        projectionCase name mutate =
            let raw = mutate legacy.projected
            in attempt name "invalid-projection" raw legacy.beforeProjection
        receiptCase name mutate =
            let raw = replace "intent" (mutate (field "intent" terminalRaw)) terminalRaw
            in attempt name "foreign-receipt" raw pending
        badContext fieldName value raw = replace "context" (replace fieldName value (field "context" raw)) raw
        exhausted name request generation =
            let ready = setup ids "activate" request generation
            in negative name "counter-exhaustion" ready.watermarks ready.model (act Effects.Activate (counter ids.incarnation) ready.model)
        badIncarnation value raw = replace "scene" (replace "windows" (E.list identity [field "scene" raw |> field "windows" |> (\rows -> D.decodeValue (D.index 0 D.value) rows |> Result.withDefault E.null) |> replace "incarnation" value]) (field "scene" raw)) raw
        numericAttached = replace "binding" (replace "lifetime" (E.float 9007199254740992) (binding ids)) legacy.attached
        overflowAttached = replace "binding" (replace "lifetime" (E.string "18446744073709551616") (binding ids)) legacy.attached
        noncanonicalWatermarks = replace "request" (E.string ("0"++ids.request)) legacy.watermarks
        snapReady = setup ids "snap" ids.request ids.generation
        staleSnap = operationFor "snap" (counter ids.incarnation) snapReady.model |> Maybe.map (\operation -> case operation of
            Effects.SnapPlacement proposed -> Effects.SnapPlacement {proposed|context={lifetime=counter ids.lifetime,epoch=counter ids.epoch,output=counter (increment ids.output),revision=counter ids.revision}}
            other -> other)
        transferReady = setup ids "transfer-workspace" ids.request ids.generation
        staleTransfer = operationFor "transfer-workspace" (counter ids.incarnation) transferReady.model |> Maybe.map (\operation -> case operation of
            Effects.TransferWorkspace proposed -> Effects.TransferWorkspace {proposed|sourceGeneration=counter (increment ids.workspace)}
            other -> other)
    in
        [negative "unknown-target-protocol1" "invalid-target" (E.string (increment ids.incarnation)) legacy.model (act Effects.Activate (counter (increment ids.incarnation)) legacy.model)
        ,negative "unknown-target-protocol2" "invalid-target" (E.string (increment ids.incarnation)) geometry.model (act Effects.Maximize (counter (increment ids.incarnation)) geometry.model)
        ,negative "duplicate-pending-no-dispatch" "duplicate" (E.string "activate") pending (act Effects.Activate (counter ids.incarnation) pending)
        ,negative "unknown-no-replay" "unknown-no-replay" unknownRaw unknown (act Effects.Activate (counter ids.incarnation) unknown)
        ,attempt "duplicate-terminal-receipt" "duplicate" terminalRaw terminal
        ,stampCase "stale-output-stamp" (replace "output" (E.string (increment ids.output)))
        ,stampCase "stale-revision-stamp" (replace "revision" (E.string (increment ids.revision)))
        ,stampCase "foreign-binding-stamp" (replace "binding" (replace "frontend" (E.string (increment ids.epoch)) (binding ids)))
        ,projectionCase "mismatched-context-lifetime" (badContext "lifetime" (E.string (increment ids.lifetime)))
        ,projectionCase "mismatched-context-epoch" (badContext "epoch" (E.string (increment ids.epoch)))
        ,projectionCase "zero-context-output" (badContext "output" (E.string "0"))
        ,projectionCase "noncanonical-context-revision" (badContext "revision" (E.string ("0"++ids.revision)))
        ,projectionCase "numeric-context-output" (badContext "output" (E.float 9007199254740992))
        ,projectionCase "numeric-window-incarnation" (badIncarnation (E.float 9007199254740992))
        ,projectionCase "noncanonical-window-incarnation" (badIncarnation (E.string ("0"++ids.incarnation)))
        ,attempt "numeric-binding-lifetime" "invalid-numeric" numericAttached legacy.beforeAttached
        ,attempt "overflow-binding-lifetime" "invalid-numeric" overflowAttached legacy.beforeAttached
        ,attempt "noncanonical-recovery-request" "invalid-numeric" noncanonicalWatermarks (read legacy.attached legacy.beforeAttached)
        ,exhausted "exhausted-request-counter" "18446744073709551615" ids.generation
        ,exhausted "exhausted-operation-generation" ids.request "18446744073709551615"
        ,receiptCase "foreign-request-receipt" (replace "request" (E.string (increment (increment ids.request))))
        ,receiptCase "foreign-generation-receipt" (replace "generation" (E.string (increment (increment ids.generation))))
        ,receiptCase "foreign-incarnation-receipt" (replace "incarnation" (E.string (increment ids.incarnation)))
        ,receiptCase "foreign-lifetime-receipt" (badContext "lifetime" (E.string (increment ids.lifetime)))
        ,receiptCase "foreign-epoch-receipt" (badContext "epoch" (E.string (increment ids.epoch)))
        ,receiptCase "foreign-output-receipt" (badContext "output" (E.string (increment ids.output)))
        ,receiptCase "foreign-revision-receipt" (badContext "revision" (E.string (increment ids.revision)))
        ,negative "stale-snap-placement-context" "stale-proposal" (E.string "snap") snapReady.model (staleSnap |> Maybe.map (\operation -> act operation (counter ids.incarnation) snapReady.model) |> Maybe.withDefault (snapReady.model,[]))
        ,negative "stale-transfer-source-generation" "stale-proposal" (E.string "transfer-workspace") transferReady.model (staleTransfer |> Maybe.map (\operation -> act operation (counter ids.incarnation) transferReady.model) |> Maybe.withDefault (transferReady.model,[]))]


result seed =
    let ids = identities seed
    in E.object
        [("schema",E.int 1),("requirement",E.string "ELM-ARC-005"),("scenario",E.string "architecture-005"),("seed",E.int seed)
        ,("route",E.string "OutputController -> SurfaceController -> Desktop -> TaskbarShell.Native -> MenuBridge.guardedAct -> Shell.Act -> Effects")
        ,("scope",E.string "Actual Elm bridge serialization and matching simulated receipt routing; not native issuer, certificate, physical effect, AT/IME or release evidence")
        ,("positives",E.list (positive ids) operations),("negatives",E.list identity (negatives ids))]


main : Program Int () Never
main = Platform.worker {init=\seed -> ((),outgoing (result seed)),update=\_ model -> (model,Cmd.none),subscriptions=\_ -> Sub.none}
