port module Ui011OpenerMinimizeReplay exposing (main)

-- Public production reducers and rendered packets only. No endpoint or native
-- capability is constructed by this component fixture.
import Desktop
import DesktopPolicy as Policy
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

-- Drive the same public policy transport and emitted Delay messages as HttpMain.
-- The fixture never constructs a Desktop watch token or changes an opaque model.
bridge kind value = E.object [("bridgeProtocol",E.int 1),("kind",E.string kind),("payload",value)]
pStep kind value = Policy.update (Policy.Incoming (bridge kind value))
pReceive = pStep "native-event"
pBase = Policy.initial |> pStep "view-topology" (Fixture.topology "1" [("1",Fixture.left)]) |> Tuple.first
pFrame model = Outputs.frame model.controller
pBar model = bar model.controller
pFallback model = pBar model |> List.filter (\entry -> entry.id=="bar:applications" && entry.enabled) |> List.map .dom
pClosed model = closed model.controller
pPublished effects = List.filterMap (\effect -> case effect of
    Policy.Publish value -> Just value
    _ -> Nothing) effects
pRequests effects = pPublished effects |> List.concatMap (D.decodeValue (D.field "requests" (D.list D.value)) >> Result.withDefault [])
pFocus effects = pPublished effects |> List.concatMap (D.decodeValue (D.field "focus" (D.list D.string)) >> Result.withDefault [])
pKind kind effects = pRequests effects |> List.filter (\value -> D.decodeValue (D.field "kind" D.string) value==Ok kind)
pRequestId kind effects = pKind kind effects |> List.head |> Maybe.andThen (D.decodeValue (D.field "requestId" D.string) >> Result.toMaybe) |> Maybe.withDefault "0"
pNoMutation effects = pRequests effects |> List.all (\value -> D.decodeValue (D.field "kind" D.string) value |> Result.map (\kind -> List.member kind ["window-read","window-watch"]) |> Result.withDefault False)
pTimers effects = List.filterMap (\effect -> case effect of
    Policy.Delay duration message -> Just (duration,message)
    _ -> Nothing) effects
pFire effects model = case List.head (pTimers effects) of
    Just (_,message) -> Policy.update (Policy.Deadline message) model
    Nothing -> (model,[])
pOpen model = pStep "view-action" (viewAction "surface-context" "keyboard" "bar" groupId model.controller) model
pEscape model = pStep "view-escape" (E.object [("scope",scope "1"),("publication",E.string (field "publication" model.controller)),("lease",E.string (field "lease" model.controller))]) model
pLoad watch rows =
    let caps=if watch then ["window-read","window-watch"] else ["window-read"]
        (attached,issued)=pReceive (attachment (E.list E.string caps)) pBase
    in pReceive (reply (bound "1") (pRequestId "window-read" issued) "Observed" (snapshot "1" "1" rows)) attached
watchReply binding request baseRevision status value = E.object [("protocolVersion",E.int 3),("kind",E.string "window-watch-result"),("binding",binding),("requestId",E.string request),("observedRevision",E.string baseRevision),("status",E.string status),("snapshot",value)]
watchWire issued status rows = watchReply (bound "1") (pRequestId "window-watch" issued) "1" status (if status=="Changed" then snapshot "1" "2" rows else E.null)
retitle value = E.object [("id",E.string value),("title",E.string "Changed document title"),("appId",E.string "org.example.Editor"),("states",E.list E.string ["activated"]),("outputs",E.list E.string ["41"]),("parent",E.null)]
otherRow title = E.object [("id",E.string "99"),("title",E.string title),("appId",E.string "org.example.Other"),("states",E.list E.string []),("outputs",E.list E.string ["41"]),("parent",E.null)]
pMenuIdentity model = closeTargets model.controller
pReady model = not (List.isEmpty (group model.controller))

-- Minimized state is a modeled authenticated reply in this CPU component.
-- Only the separate native owner stream can prove an actual minimized client.
minimized ident = E.object [("id",E.string ident),("title",E.string "Document α😀"),("appId",E.string "org.example.Editor"),("states",E.list E.string ["minimized"]),("outputs",E.list E.string ["41"]),("parent",E.null)]
otherMinimized = E.object [("id",E.string "99"),("title",E.string "Other"),("appId",E.string "org.example.Other"),("states",E.list E.string ["minimized"]),("outputs",E.list E.string ["41"]),("parent",E.null)]
pGroup model = group model.controller |> List.map .dom
sameGroup before after = (Fixture.desktop before.controller).windows.shell.binding==(Fixture.desktop after.controller).windows.shell.binding && pGroup after/= []
minimizedObserved model = (Fixture.desktop model.controller).windows.shell.windowObservation |> Maybe.map (\value -> List.any (\item -> UInt64.string item.id=="11" && List.member "minimized" item.states) value.windows) |> Maybe.withDefault False

result =
    let (ready,_)=pLoad True [row "11",otherRow "Before"]
        (opened,armed)=pOpen ready
        (pending,issued)=pFire armed opened
        minWire=watchWire issued "Changed" [minimized "11",otherRow "Before"]
        (after,effects)=pReceive minWire pending
        (duplicate,duplicateEffects)=pReceive minWire after
        (foreign,foreignEffects)=pReceive (watchReply (bound "2") (pRequestId "window-watch" issued) "1" "Changed" (snapshot "1" "2" [minimized "11"])) pending
        (wrongBase,wrongBaseEffects)=pReceive (watchReply (bound "1") (pRequestId "window-watch" issued) "999" "Changed" (snapshot "1" "2" [minimized "11"])) pending
        (unknown,unknownEffects)=pReceive (watchWire issued "Unknown" []) pending
        (unrelated,unrelatedEffects)=pReceive (watchWire issued "Changed" [row "11",otherMinimized]) pending
        (retitled,retitledEffects)=pReceive (watchWire issued "Changed" [retitle "11",otherRow "Before"]) pending
        (replacement,replacementEffects)=pReceive (watchWire issued "Changed" [minimized "12",otherRow "Before"]) pending
        (alreadyReady,_)=pLoad True [minimized "11",otherRow "Before"]
        (alreadyOpen,alreadyArmed)=pOpen alreadyReady
        (alreadyPending,alreadyIssued)=pFire alreadyArmed alreadyOpen
        (alreadyAfter,alreadyEffects)=pReceive (watchWire alreadyIssued "Changed" [minimized "11",otherRow "After"]) alreadyPending
        preconditions=[("current-group-eligible",List.length (pGroup ready)==1),("keyboard-menu-open",not (pClosed opened) && List.length (pMenuIdentity opened)==1),("one-correlated-watch",List.length (pTimers armed)==1 && List.length (pKind "window-watch" issued)==1),("actual-reducer-minimized-state",minimizedObserved after),("same-group-current-eligible",sameGroup ready after && List.length (pGroup after)==1)]
        checks=[("minimize-retires-current-scope",pClosed after),("minimize-restores-current-eligible-group",pFocus effects==pGroup after),("minimize-does-not-select-applications-fallback",List.all (\target -> not (List.member target (pFallback after))) (pFocus effects)),("current-incarnation-remains-observed",minimizedObserved after && sameGroup ready after),("duplicate-reply-cannot-refocus",duplicate==after && List.isEmpty (pFocus duplicateEffects)),("foreign-binding-cannot-retire",not (pClosed foreign) && List.isEmpty (pFocus foreignEffects)),("wrong-base-cannot-retire",not (pClosed wrongBase) && List.isEmpty (pFocus wrongBaseEffects)),("unknown-cannot-retire-or-focus",not (pClosed unknown) && List.isEmpty (pFocus unknownEffects)),("unrelated-minimize-preserves-scope",not (pClosed unrelated) && pMenuIdentity unrelated==pMenuIdentity opened && List.isEmpty (pFocus unrelatedEffects)),("title-change-preserves-scope",not (pClosed retitled) && List.isEmpty (pFocus retitledEffects)),("already-minimized-is-not-new-minimize",not (pClosed alreadyAfter) && List.isEmpty (pFocus alreadyEffects)),("replacement-never-restores-old-group",pClosed replacement && pFocus replacementEffects==pFallback replacement && not (List.any (String.contains groupId) (pFocus replacementEffects))),("no-restore-activate-or-mutation",List.all pNoMutation [effects,duplicateEffects,foreignEffects,wrongBaseEffects,unknownEffects,unrelatedEffects,retitledEffects,replacementEffects,alreadyEffects]),("no-watch-rearm-after-retirement",List.isEmpty (pTimers effects))]
        sample seed =
            let ident=String.fromInt (1000+seed)
                (sampleReady,_)=pLoad True [row ident,otherRow "Before"]
                (sampleOpen,sampleArmed)=pOpen sampleReady
                (samplePending,sampleIssued)=pFire sampleArmed sampleOpen
                variant=modBy 4 seed
                wire=if variant==1 then watchReply (bound "2") (pRequestId "window-watch" sampleIssued) "1" "Changed" (snapshot "1" "2" [minimized ident]) else if variant==2 then watchWire sampleIssued "Changed" [row ident,otherMinimized] else if variant==3 then watchWire sampleIssued "Unknown" [] else watchWire sampleIssued "Changed" [minimized ident,otherRow "Before"]
                (sampleAfter,sampleEffects)=pReceive wire samplePending
                expected=if variant==0 then pGroup sampleAfter else []
            in E.object [("seed",E.int seed),("prepared",E.bool (List.length (pGroup sampleReady)==1 && List.length (pKind "window-watch" sampleIssued)==1)),("actualFocus",E.list E.string (pFocus sampleEffects)),("expectedFocus",E.list E.string expected),("scopeMatches",E.bool (pClosed sampleAfter==(variant==0))),("noMutation",E.bool (pNoMutation sampleEffects))]
    in E.object [("preconditions",E.object (List.map (Tuple.mapSecond E.bool) preconditions)),("checks",E.object (List.map (Tuple.mapSecond E.bool) checks)),("witness",E.object [("minimized",E.bool (minimizedObserved after)),("scopeClosed",E.bool (pClosed after)),("eligibleGroupTargets",E.list E.string (pGroup after)),("actualFocus",E.list E.string (pFocus effects))]),("seeded",E.list sample (List.range 0 31))]
main = Platform.worker {init=\() -> ((),outgoing result),update=\_ model -> (model,Cmd.none),subscriptions=\_ -> Sub.none}
