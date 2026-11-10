port module Ui011AutomaticWindowWatchReplay exposing (main)

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

sample seed =
    let ident=String.fromInt (1000+seed)
        variant=modBy 8 seed
        (ready,_)=pLoad True [row ident,otherRow "Before"]
        (opened,armed)=pOpen ready
        (pending,issued)=pFire armed opened
        (selected,_)=if variant==7 then pEscape pending else (pending,[])
        status=if variant==0 then "Unchanged" else if variant==6 then "Unknown" else "Changed"
        rows=case variant of
            1 -> [otherRow "Before"]
            2 -> [row (String.fromInt (2000+seed)),otherRow "Before"]
            3 -> [retitle ident,otherRow "Before"]
            4 -> [row ident,otherRow "After"]
            _ -> [row ident,otherRow "Before"]
        wire=if variant==5 then watchReply (bound "2") (pRequestId "window-watch" issued) "1" "Unchanged" E.null else watchWire issued status rows
        (after,effects)=pReceive wire selected
        (_,duplicate)=pReceive wire after
        expected=if variant==1 || variant==2 then pFallback after else []
        preserve=if List.member variant [0,3,4,5] then pMenuIdentity after==pMenuIdentity opened && not (pClosed after) else True
    in E.object [("seed",E.int seed),("variant",E.int variant),("contractReady",E.bool (pReady ready && List.length (pTimers armed)==1 && List.length (pKind "window-watch" issued)==1)),("actualFocus",E.list E.string (pFocus effects)),("expectedFocus",E.list E.string expected),("expectedEligible",E.bool (not (List.member variant [1,2]) || List.length expected==1)),("preservedScope",E.bool preserve),("once",E.bool (List.isEmpty (pFocus duplicate))),("noMutation",E.bool (List.all pNoMutation [issued,effects,duplicate]))]

result =
    let (legacy,_)=pLoad False [row "11"]
        (legacyMenu,legacyArmed)=pOpen legacy
        (ready,_)=pLoad True [row "11",otherRow "Before"]
        (opened,armed)=pOpen ready
        (pending,issued)=pFire armed opened
        (_,duplicateTick)=pFire armed pending
        current = pReady ready && not (pClosed opened) && List.length (pTimers armed)==1 && List.length (pKind "window-watch" issued)==1
        settle status rows=pReceive (watchWire issued status rows) pending
        (unchanged,unchangedEffects)=settle "Unchanged" []
        (_,rearmed)=pFire unchangedEffects unchanged
        (removed,removedEffects)=settle "Changed" [otherRow "Before"]
        (replaced,replacedEffects)=settle "Changed" [row "12",otherRow "Before"]
        (metadata,metadataEffects)=settle "Changed" [retitle "11",otherRow "Before"]
        (unrelated,unrelatedEffects)=settle "Changed" [row "11",otherRow "After"]
        (counterOnly,counterEffects)=settle "Changed" [row "11",otherRow "Before"]
        (_,duplicateChanged)=pReceive (watchWire issued "Changed" [otherRow "Before"]) removed
        (_,unknownEffects)=settle "Unknown" []
        (_,unavailableEffects)=settle "Unavailable" []
        (_,wrongRequest)=pReceive (watchReply (bound "1") "999" "1" "Changed" (snapshot "1" "2" [])) pending
        (_,wrongBase)=pReceive (watchReply (bound "1") (pRequestId "window-watch" issued) "2" "Changed" (snapshot "1" "3" [])) pending
        (_,foreignBinding)=pReceive (watchReply (bound "2") (pRequestId "window-watch" issued) "1" "Unchanged" E.null) pending
        (_,foreignOwner)=pReceive (watchReply (bound "1") (pRequestId "window-watch" issued) "1" "Changed" (snapshot "2" "2" [])) pending
        (closedScope,_)=pEscape pending
        (_,lateClosed)=pReceive (watchWire issued "Changed" []) closedScope
        (_,lateTimer)=pFire armed closedScope
        (superseded,_)=pStep "view-topology" (Fixture.topology "2" [("2",Fixture.left)]) pending
        (_,lateOwner)=pReceive (watchWire issued "Changed" []) superseded
        (detached,_)=pReceive (E.object [("protocolVersion",E.int 3),("kind",E.string "host-disconnected")]) pending
        (_,lateDetached)=pReceive (watchWire issued "Changed" []) detached
        (pointer, pointerArmed)=pStep "view-action" (viewAction "surface-context" "pointer" "bar" groupId ready.controller) ready
        noFocus = List.isEmpty << pFocus
        check name yes=(name,E.bool yes)
        negative effects=noFocus effects && pNoMutation effects
    in E.object [("checks",E.object
        [check "explicit-watch-capability-is-admitted" (pReady ready)
        ,check "legacy-read-only-menu-does-not-watch" (not (pClosed legacyMenu) && List.isEmpty (pTimers legacyArmed) && List.isEmpty (pKind "window-watch" legacyArmed))
        ,check "keyboard-scope-arms-one-backpressure-timer" (pReady ready && List.map Tuple.first (pTimers armed)==[100])
        ,check "timer-sends-one-bound-watch-with-base" (current && (pKind "window-watch" issued |> List.head |> Maybe.map (\wire -> D.decodeValue (D.field "binding" D.value) wire==Ok (bound "1") && D.decodeValue (D.field "observedRevision" D.string) wire==Ok "1") |> Maybe.withDefault False))
        ,check "duplicate-timer-cannot-issue-second-watch" (current && List.isEmpty (pKind "window-watch" duplicateTick))
        ,check "pending-watch-preserves-open-menu-frame" (current && pFrame pending==pFrame opened && noFocus issued)
        ,check "unchanged-preserves-frame-stamp-and-focus" (current && pFrame unchanged==pFrame opened && noFocus unchangedEffects)
        ,check "unchanged-only-rearms-no-publication" (current && List.isEmpty (pPublished unchangedEffects) && List.map Tuple.first (pTimers unchangedEffects)==[100])
        ,check "successor-watch-request-is-distinct" (current && List.length (pKind "window-watch" rearmed)==1 && pRequestId "window-watch" issued/=pRequestId "window-watch" rearmed)
        ,check "closed-origin-automatically-restores-fallback" (current && pClosed removed && List.length (pFallback removed)==1 && pFocus removedEffects==pFallback removed)
        ,check "replacement-never-receives-old-focus" (current && pClosed replaced && pFocus replacedEffects==pFallback replaced && pFocus replacedEffects/=(group replaced.controller |> List.map .dom))
        ,check "same-origin-title-change-preserves-menu" (current && pMenuIdentity metadata==pMenuIdentity opened && not (pClosed metadata) && noFocus metadataEffects)
        ,check "other-window-change-preserves-menu" (current && pMenuIdentity unrelated==pMenuIdentity opened && not (pClosed unrelated) && noFocus unrelatedEffects)
        ,check "counter-only-changed-cannot-retire" (current && pMenuIdentity counterOnly==pMenuIdentity opened && not (pClosed counterOnly) && noFocus counterEffects)
        ,check "changed-reply-settles-once" (current && negative duplicateChanged)
        ,check "unknown-stops-watch-no-fallback" (current && negative unknownEffects && List.isEmpty (pTimers unknownEffects))
        ,check "unavailable-stops-watch-no-fallback" (current && negative unavailableEffects && List.isEmpty (pTimers unavailableEffects))
        ,check "wrong-request-cannot-restore" (current && negative wrongRequest)
        ,check "wrong-base-cannot-restore" (current && negative wrongBase)
        ,check "foreign-binding-cannot-restore" (current && negative foreignBinding)
        ,check "foreign-owner-cannot-restore" (current && negative foreignOwner)
        ,check "closed-scope-ignores-late-watch" (current && negative lateClosed)
        ,check "closed-scope-ignores-old-timer" (current && List.isEmpty (pRequests lateTimer) && noFocus lateTimer)
        ,check "superseded-presentation-ignores-watch" (current && negative lateOwner)
        ,check "detached-scope-ignores-watch" (current && negative lateDetached)
        ,check "pointer-scope-does-not-arm" (pReady ready && not (pClosed pointer) && List.isEmpty (pTimers pointerArmed))
        ,check "watch-never-issues-native-mutation" (current && List.all pNoMutation [armed,issued,unchangedEffects,removedEffects,replacedEffects,metadataEffects,unrelatedEffects])
        ])
        ,("preconditions",E.object [check "existing-read-route-admitted" (pReady legacy),check "existing-menu-route-opens" (not (pClosed legacyMenu)),check "actual-view-one" (Fixture.owner legacy.controller==Just "1")])
        ,("contractReady",E.bool current)
        ,("seeded",E.object [("seeds",E.list E.int (List.range 0 31)),("samples",E.list sample (List.range 0 31))])
        ,("openedFrame",pFrame opened),("unchangedFrame",pFrame unchanged),("removedFrame",pFrame removed),("metadataFrame",pFrame metadata),("unrelatedFrame",pFrame unrelated)]

main : Program () () Never
main = Platform.worker {init=\_ -> ((),outgoing result),update=\_ state -> (state,Cmd.none),subscriptions=\_ -> Sub.none}
