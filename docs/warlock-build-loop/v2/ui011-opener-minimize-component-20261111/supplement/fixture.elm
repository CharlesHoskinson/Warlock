port module Ui011MinimizeCapturedRootReplay exposing (main)

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
    let prepare rows =
            let (preparedReady,_)=pLoad True rows
                (preparedOpened,preparedArmed)=pOpen preparedReady
                (preparedPending,preparedIssued)=pFire preparedArmed preparedOpened
            in (preparedOpened,preparedPending,preparedIssued)
        (opened,pending,issued)=prepare [row "11",row "12"]
        (sibling,siblingEffects)=pReceive (watchWire issued "Changed" [row "11",minimized "12"]) pending
        (target,targetEffects)=pReceive (watchWire issued "Changed" [minimized "11",row "12"]) pending
        (_,duplicateEffects)=pReceive (watchWire issued "Changed" [minimized "11",row "12"]) target
        (alreadyOpened,alreadyPending,alreadyIssued)=prepare [minimized "11",row "12"]
        (already,alreadyEffects)=pReceive (watchWire alreadyIssued "Changed" [minimized "11",minimized "12"]) alreadyPending
        (removed,removedEffects)=pReceive (watchWire issued "Changed" [row "12"]) pending
        preconditions=[("same-group-two-windows",List.length (pGroup opened)==1 && not (pClosed opened)),("current-watch-issued",List.length (pKind "window-watch" issued)==1)]
        checks=[("different-root-minimize-preserves-scope",not (pClosed sibling) && pMenuIdentity sibling==pMenuIdentity opened && List.isEmpty (pFocus siblingEffects)),("captured-root-minimize-retires-with-sibling",pClosed target && pFocus targetEffects==pGroup target),("captured-root-is-not-whole-group-minimized",pGroup target/= [] && pClosed target),("already-minimized-root-ignores-sibling-transition",not (pClosed already) && pMenuIdentity already==pMenuIdentity alreadyOpened && List.isEmpty (pFocus alreadyEffects)),("retired-captured-root-does-not-refocus",List.isEmpty (pFocus duplicateEffects)),("removed-root-cannot-receive-old-focus",pClosed removed && pFocus removedEffects==pFallback removed),("all-effects-remain-read-only",List.all pNoMutation [siblingEffects,targetEffects,duplicateEffects,alreadyEffects,removedEffects])]
        sample seed =
            let first=String.fromInt (1000+seed*2)
                second=String.fromInt (1001+seed*2)
                (sampleOpened,samplePending,sampleIssued)=prepare [row second,row first]
                targetMinimized=modBy 2 seed==0
                rows=if targetMinimized then [row second,minimized first] else [minimized second,row first]
                (after,effects)=pReceive (watchWire sampleIssued "Changed" rows) samplePending
            in E.object [("seed",E.int seed),("prepared",E.bool (not (pClosed sampleOpened) && List.length (pKind "window-watch" sampleIssued)==1)),("scopeMatches",E.bool (pClosed after==targetMinimized)),("actualFocus",E.list E.string (pFocus effects)),("expectedFocus",E.list E.string (if targetMinimized then pGroup after else [])),("noMutation",E.bool (pNoMutation effects))]
    in E.object [("preconditions",E.object (List.map (Tuple.mapSecond E.bool) preconditions)),("checks",E.object (List.map (Tuple.mapSecond E.bool) checks)),("seeded",E.list sample (List.range 0 31))]
main = Platform.worker {init=\() -> ((),outgoing result),update=\_ model -> (model,Cmd.none),subscriptions=\_ -> Sub.none}
