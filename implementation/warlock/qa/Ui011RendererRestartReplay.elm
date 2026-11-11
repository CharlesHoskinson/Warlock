port module Ui011RendererRestartReplay exposing (main)

-- Public production reducers and rendered packets only. No endpoint or native
-- capability is constructed by this component fixture.
import Desktop
import Effects
import Json.Decode as D
import Json.Encode as E
import OutputController as Outputs
import OutputRetirementReplay as Fixture
import Platform
import Shell
import Surface
import SurfaceController as Controller
import TaskbarShell
import UInt64

port outgoing : E.Value -> Cmd msg

bound front = E.object [("lifetime",E.string "1"),("session",E.string "1"),("frontend",E.string front)]
scope ident = E.object [("id",E.string ident),("generation",E.string "1")]
attachment operations = E.object [("protocolVersion",E.int 3),("kind",E.string "application-attached"),("binding",bound "1"),("nativeOperations",E.list identity []),("applicationOperations",E.list identity []),("localOperations",E.list E.string ["notification-policy"]),("windowObservationOperations",operations)]
legacyAttachment = E.object [("protocolVersion",E.int 3),("kind",E.string "application-attached"),("binding",bound "1"),("nativeOperations",E.list identity []),("applicationOperations",E.list identity []),("localOperations",E.list E.string ["notification-policy"])]
row ident = E.object [("id",E.string ident),("title",E.string "Document α😀"),("appId",E.string "org.example.Editor"),("states",E.list E.string ["activated"]),("outputs",E.list E.string ["41"]),("parent",E.null)]
snapshot owner revision rows = E.object [("owner",E.string owner),("revision",E.string revision),("view",E.string "global"),("outputs",E.list E.string ["41"]),("windows",E.list identity rows)]
reply binding request status value = E.object [("protocolVersion",E.int 3),("kind",E.string "window-observation"),("binding",binding),("requestId",E.string request),("status",E.string status),("snapshot",value)]
step message = Outputs.update message
receive wire = step (Outputs.Interaction (Desktop.Incoming wire))
base = Outputs.initial |> step (Outputs.Topology (Fixture.topology "1" [("1",Fixture.left)])) |> Tuple.first
requests effects = List.filterMap (\effect -> case effect of
    Controller.DesktopEffect (Desktop.WindowEffect (Shell.Send wire)) -> Just wire
    Controller.DesktopEffect (Desktop.Send wire) -> Just wire
    _ -> Nothing) effects
readRequests effects = requests effects |> List.filter (\wire -> D.decodeValue (D.field "kind" D.string) wire==Ok "window-read")
readId effects = readRequests effects |> List.head |> Maybe.andThen (D.decodeValue (D.field "requestId" D.string) >> Result.toMaybe) |> Maybe.withDefault "1"
focuses effects = List.filterMap (\effect -> case effect of
    Controller.DesktopEffect (Desktop.Focus target) -> Just target
    _ -> Nothing) effects
noMutations effects = requests effects |> List.all (\wire -> D.decodeValue (D.field "kind" D.string) wire |> Result.map (\kind -> not (List.member kind ["window-effect","application-launch","notification-effect"])) |> Result.withDefault False)
field name model = D.decodeValue (D.at ["frame",name] D.string) (Outputs.frame model) |> Result.withDefault "0"
packet model = Surface.packet UInt64.zero UInt64.zero (Fixture.desktop model)
bar model = D.decodeValue (D.field "bar" (D.list (D.map3 (\ident enabled dom -> {id=ident,enabled=enabled,dom=dom}) (D.field "id" D.string) (D.field "enabled" D.bool) (D.field "domId" D.string)))) (packet model) |> Result.withDefault []
groupId = "bar:group:observed:application:org.example.Editor"
group model = bar model |> List.filter (\entry -> entry.id==groupId && entry.enabled)
noGroups model = List.isEmpty (group model)
viewAction kind trigger role ident model = E.object [("viewProtocol",E.int 1),("kind",E.string "view-action"),("scope",scope "1"),("action",E.object ([("surfaceProtocol",E.int 2),("kind",E.string kind),("surface",E.string role),("publication",E.string (field "publication" model)),("lease",E.string (field "lease" model)),("id",E.string ident),("trigger",E.string trigger)] ++ (if kind=="surface-context" then [("x",E.int 0),("y",E.int 0)] else [])))]
openMenu trigger model = step (Outputs.Renderer (viewAction "surface-context" trigger "bar" groupId model)) model
refresh model = step (Outputs.Interaction (Desktop.Window (TaskbarShell.Native Shell.Refresh))) model
escape model = step (Outputs.Escape (E.object [("scope",scope "1"),("publication",E.string (field "publication" model)),("lease",E.string (field "lease" model))])) model
closed model = Surface.mode (Fixture.desktop model)=="closed"
controls model = Surface.controls (Fixture.desktop model)
closeTargets model = controls model |> List.filter (\item -> item.id=="control:menu-close" && item.enabled) |> List.map .domId
load rows =
    let (attached,commands)=receive (attachment (E.list E.string ["window-read"])) base
        (observed,replyEffects)=receive (reply (bound "1") (readId commands) "Observed" (snapshot "1" "1" rows)) attached
    in (observed,commands++replyEffects)


restartTopology revision generationValue = E.object [("viewProtocol",E.int 2),("kind",E.string "view-topology"),("revision",E.string revision),("views",E.list identity [E.object [("id",E.string "1"),("generation",E.string generationValue)]]),("locations",E.list identity [E.object [("scope",E.object [("id",E.string "1"),("generation",E.string generationValue)]),("box",E.list E.int Fixture.left)]])]
replace model = step (Outputs.Topology (restartTopology "2" "2")) model
currentGeneration model = D.decodeValue (D.at ["focusOwner","generation"] D.string) (Outputs.frame model) |> Result.toMaybe
currentGroup model = group model |> List.map .dom
fallback model = bar model |> List.filter (\entry -> entry.id=="bar:applications" && entry.enabled) |> List.map .dom
settle status binding rows effects model = receive (reply binding (readId effects) status (if status=="Observed" then snapshot (D.decodeValue (D.field "frontend" D.string) binding |> Result.withDefault "0") "2" rows else E.null)) model
noIssued model = List.isEmpty (Fixture.desktop model).windows.shell.issued

counter value = D.decodeValue UInt64.decoder (E.string value) |> Result.withDefault UInt64.zero
nativeAction model =
    Shell.capture (Fixture.desktop model).windows.shell
        |> Maybe.map (\stamp -> step (Outputs.Interaction (Desktop.Window (TaskbarShell.Native (Shell.Act stamp Effects.Minimize (counter "1"))))) model)
        |> Maybe.withDefault (model,[])
unknownReceipt intent = E.object [("protocolVersion",E.int 3),("kind",E.string "effect-outcome"),("effectProtocol",E.int 1),("binding",Fixture.bound),("intent",Effects.encodeIntent intent),("status",E.string "Unknown"),("reason",E.string "applied"),("revision",E.string "2"),("outputGeneration",E.string "1")]
transaction model = (Fixture.desktop model).windows.shell.effects.transaction

result =
    let (ready,_)=load [row "11"]
        (opened,_)=openMenu "keyboard" ready
        (replaced,replacementEffects)=replace opened
        (restored,restoredEffects)=settle "Observed" (bound "1") [row "11"] replacementEffects replaced
        (missing,missingEffects)=settle "Observed" (bound "1") [] replacementEffects replaced
        (incarnation,incarnationEffects)=settle "Observed" (bound "1") [row "12"] replacementEffects replaced
        (unknown,unknownEffects)=settle "Unknown" (bound "1") [] replacementEffects replaced
        (foreign,foreignEffects)=settle "Observed" (bound "2") [row "11"] replacementEffects replaced
        (duplicate,duplicateEffects)=settle "Observed" (bound "1") [row "11"] replacementEffects restored
        (stale,staleEffects)=step (Outputs.Topology (Fixture.topology "1" [("1",Fixture.left)])) restored
        (staleAction,staleActionEffects)=step (Outputs.Renderer (viewAction "surface-context" "keyboard" "bar" groupId restored)) restored
        (staleEscape,staleEscapeEffects)=escape restored
        (again,againEffects)=replace restored
        draftOpened=Fixture.base [("1",Fixture.left)] |> Fixture.native (Fixture.shortcut Fixture.bound "1" (E.list E.int Fixture.left))
        draftBefore=Desktop.capture (Fixture.desktop draftOpened) |> Maybe.map (\stamp -> step (Outputs.Interaction (Desktop.SearchQuery stamp "retain renderer draft")) draftOpened |> Tuple.first) |> Maybe.withDefault draftOpened
        (draftAfter,_)=replace draftBefore
        (actionPending,_)=nativeAction (Fixture.base [("1",Fixture.left)])
        actionUnknown=transaction actionPending |> Maybe.map (\value -> receive (unknownReceipt value.intent) actionPending |> Tuple.first) |> Maybe.withDefault actionPending
        (actionAfter,actionAfterEffects)=replace actionUnknown
        setup=[("current-opener-eligible",List.length (currentGroup ready)==1),("keyboard-scope-open",not (closed opened) && List.length (closeTargets opened)==1),("replacement-generation-current",currentGeneration replaced==Just "2"),("one-fresh-correlated-read",List.length (readRequests replacementEffects)==1),("fresh-opener-eligible",List.length (currentGroup restored)==1),("user-draft-prepared",(Fixture.desktop draftBefore).query=="retain renderer draft"),("unknown-reservation-prepared",transaction actionUnknown |> Maybe.map (.status >> Effects.statusName >> (==) "Unknown") |> Maybe.withDefault False)]
        checks=[("restart-retires-open-scope",closed replaced),("no-focus-before-current-observation",List.isEmpty (focuses replacementEffects)),("current-logical-opener-restored",focuses restoredEffects==currentGroup restored),("no-old-dom-target-reused",List.all (\target -> not (List.member target (currentGroup ready))) (focuses restoredEffects)),("missing-opener-current-fallback",focuses missingEffects==fallback missing && List.length (fallback missing)==1),("replacement-incarnation-current-fallback",focuses incarnationEffects==fallback incarnation && not (List.any (String.contains groupId) (focuses incarnationEffects))),("unknown-observation-no-focus",List.isEmpty (focuses unknownEffects)),("foreign-binding-no-focus",List.isEmpty (focuses foreignEffects) && noMutations foreignEffects && (Fixture.desktop foreign).windows.shell.binding==(Fixture.desktop replaced).windows.shell.binding && (Fixture.desktop foreign).windows.shell.windowExpected==(Fixture.desktop replaced).windows.shell.windowExpected && (Fixture.desktop foreign).windows.shell.windowObservation==(Fixture.desktop replaced).windows.shell.windowObservation && (Fixture.desktop foreign).windows.shell.issued==(Fixture.desktop replaced).windows.shell.issued),("duplicate-observation-no-refocus",List.isEmpty (focuses duplicateEffects) && duplicate==restored),("stale-topology-no-change",stale==restored && List.isEmpty staleEffects),("retired-renderer-action-refused",staleAction==restored && List.isEmpty staleActionEffects),("retired-renderer-escape-refused",staleEscape==restored && List.isEmpty staleEscapeEffects),("duplicate-topology-no-refocus",again==restored && List.isEmpty againEffects),("no-window-mutation-issued",List.all noMutations [replacementEffects,restoredEffects,missingEffects,incarnationEffects,unknownEffects,foreignEffects,duplicateEffects,staleEffects,staleActionEffects,staleEscapeEffects,againEffects] && List.all noIssued [ready,opened,replaced,restored,missing,incarnation,unknown,foreign])]
        preservedChecks=checks++[("user-draft-survives-renderer-generation",(Fixture.desktop draftAfter).query==(Fixture.desktop draftBefore).query),("unknown-reservation-retained",(Fixture.desktop actionAfter).windows.shell.effects.unresolved==(Fixture.desktop actionUnknown).windows.shell.effects.unresolved && (Fixture.desktop actionAfter).windows.shell.issued==(Fixture.desktop actionUnknown).windows.shell.issued),("unknown-action-never-replayed",noMutations actionAfterEffects)]
        sample seed =
            let ident=String.fromInt (1000+seed)
                (sampleReady,_)=load [row ident]
                (sampleOpen,_)=openMenu "keyboard" sampleReady
                (samplePending,sampleRequests)=replace sampleOpen
                variant=modBy 4 seed
                (sampleAfter,sampleEffects)=if variant==1 then settle "Unknown" (bound "1") [] sampleRequests samplePending else if variant==2 then settle "Observed" (bound "2") [row ident] sampleRequests samplePending else if variant==3 then settle "Observed" (bound "1") [] sampleRequests samplePending else settle "Observed" (bound "1") [row ident] sampleRequests samplePending
                expected=if variant==0 then currentGroup sampleAfter else if variant==3 then fallback sampleAfter else []
            in E.object [("seed",E.int seed),("prepared",E.bool (not (closed sampleOpen) && List.length (readRequests sampleRequests)==1)),("actualFocus",E.list E.string (focuses sampleEffects)),("expectedFocus",E.list E.string expected),("scopeClosed",E.bool (closed sampleAfter)),("noMutation",E.bool (noMutations sampleEffects && noIssued sampleAfter))]
    in E.object [("preconditions",E.object (List.map (Tuple.mapSecond E.bool) setup)),("checks",E.object (List.map (Tuple.mapSecond E.bool) preservedChecks)),("witness",E.object [("retiredFrame",Outputs.frame replaced),("currentFrame",Outputs.frame restored),("oldTargets",E.list E.string (currentGroup ready)),("currentTargets",E.list E.string (currentGroup restored)),("actualFocus",E.list E.string (focuses restoredEffects)),("foreignFocus",E.list E.string (focuses foreignEffects)),("foreignPendingRetained",E.bool ((Fixture.desktop foreign).windows.shell.windowExpected==(Fixture.desktop replaced).windows.shell.windowExpected)),("foreignSnapshotRetained",E.bool ((Fixture.desktop foreign).windows.shell.windowObservation==(Fixture.desktop replaced).windows.shell.windowObservation)),("foreignDecoderDiagnostic",(Fixture.desktop foreign).windows.shell.decoderRefusal |> Maybe.map E.string |> Maybe.withDefault E.null)]),("seeded",E.list sample (List.range 0 31))]
main = Platform.worker {init=\() -> ((),outgoing result),update=\_ model -> (model,Cmd.none),subscriptions=\_ -> Sub.none}
