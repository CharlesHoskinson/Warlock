port module Ui011WindowWatchBatchReplay exposing (main)

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

legacyResult =
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


-- No view-disposition is supplied. Each reply uses the request and base emitted
-- by the actual public policy path. Batch counts are diagnostic evidence only.
-- This probe does not invent a disposition or authorize domain-reply settlement.
watchField name effects =
    pKind "window-watch" effects
        |> List.head
        |> Maybe.andThen (D.decodeValue (D.field name D.string) >> Result.toMaybe)
        |> Maybe.withDefault "0"

actualReply effects status rows =
    let baseRevision = watchField "observedRevision" effects
        nextRevision = String.toInt baseRevision |> Maybe.map ((+) 1 >> String.fromInt) |> Maybe.withDefault "0"
    in watchReply (bound "1") (pRequestId "window-watch" effects) baseRevision status
        (if status == "Changed" then snapshot "1" nextRevision rows else E.null)

batchCount model = Outputs.pendingBatches model.controller

cycles count =
    let (ready, _) = pLoad True [row "11", otherRow "Before"]
        (opened, armed) = pOpen ready
        initial = { model = opened, effects = armed, completed = 0, issued = 0
                  , retained = batchCount opened, maximum = batchCount opened
                  , preserved = True, quiet = True, noMutation = True, requests = [] }
        advance _ state =
            let (pending, issued) = pFire state.effects state.model
                request = pRequestId "window-watch" issued
                actualIssued = List.length (pKind "window-watch" issued) == 1
                (settled, effects) =
                    if actualIssued then pReceive (actualReply issued "Unchanged" []) pending
                    else (pending, [])
                completion = actualIssued && List.length (pTimers effects) == 1 && pReady settled && not (pClosed settled)
            in { model = settled, effects = effects
               , completed = state.completed + (if completion then 1 else 0)
               , issued = state.issued + (if actualIssued then 1 else 0)
               , retained = state.retained
               , maximum = max state.maximum (max (batchCount pending) (batchCount settled))
               , preserved = state.preserved && pReady settled && not (pClosed settled)
                    && pMenuIdentity settled == pMenuIdentity opened && pFrame settled == pFrame opened
               , quiet = state.quiet && List.isEmpty (pFocus issued) && List.isEmpty (pPublished effects)
               , noMutation = state.noMutation && pNoMutation issued && pNoMutation effects
               , requests = if actualIssued then request :: state.requests else state.requests }
    in List.foldl advance initial (List.range 1 count)

closeAfter state rows =
    let (pending, issued) = pFire state.effects state.model
        wire = actualReply issued "Changed" rows
        (after, effects) = pReceive wire pending
        (_, duplicate) = pReceive wire after
    in { model = after, effects = effects, duplicate = duplicate
       , issued = List.length (pKind "window-watch" issued) == 1
       , correlated = List.isEmpty (pTimers effects) && pNoMutation effects }

refusal variant =
    let (ready, _) = pLoad True [row "11", otherRow "Before"]
        (opened, armed) = pOpen ready
        (pendingA, issuedA) = pFire armed opened
        wireA = actualReply issuedA "Unchanged" []
        (afterA, armedB) = pReceive wireA pendingA
        (pendingB, issuedB) = pFire armedB afterA
        request = pRequestId "window-watch" issuedB
        baseRevision = watchField "observedRevision" issuedB
        valid = actualReply issuedB "Unchanged" []
        invalid = case variant of
            0 -> watchReply (bound "2") request baseRevision "Unchanged" E.null
            1 -> watchReply (bound "1") "99999" baseRevision "Unchanged" E.null
            2 -> watchReply (bound "1") request "99999" "Unchanged" E.null
            3 -> watchReply (bound "1") request baseRevision "Changed" (snapshot "2" "2" [])
            4 -> wireA
            5 -> E.object [("protocolVersion", E.int 3), ("kind", E.string "window-watch-result")]
            _ -> watchReply (bound "1") request baseRevision "Unchanged" (snapshot "1" "1" [row "11"])
        (afterInvalid, invalidEffects) = pReceive invalid pendingB
        (afterValid, validEffects) = pReceive valid afterInvalid
    in { prepared = List.length (pKind "window-watch" issuedA) == 1 && List.length (pKind "window-watch" issuedB) == 1 && request /= pRequestId "window-watch" issuedA
       , preserved = batchCount afterInvalid == batchCount pendingB && List.isEmpty (pFocus invalidEffects) && List.isEmpty (pTimers invalidEffects) && pNoMutation invalidEffects
       , currentSettles = List.length (pTimers validEffects) == 1 && pReady afterValid && not (pClosed afterValid)
       , before = batchCount pendingB, afterInvalid = batchCount afterInvalid, afterValid = batchCount afterValid }

quotaSeed seed =
    let count = 17 + seed
        state = cycles count
        removed = closeAfter state [otherRow "Before"]
    in E.object
        [("seed", E.int seed), ("cycles", E.int count)
        ,("issued", E.int state.issued), ("completed", E.int state.completed)
        ,("preserved", E.bool state.preserved), ("maximumPending", E.int state.maximum)
        ,("remaining", E.int (batchCount state.model)), ("unrelatedBaseline", E.int state.retained)
        ,("noMutation", E.bool state.noMutation)
        ,("closed", E.bool (removed.issued && removed.correlated && pClosed removed.model))
        ,("actualFocus", E.list E.string (pFocus removed.effects))
        ,("expectedFocus", E.list E.string (pFallback removed.model))
        ,("once", E.bool (List.isEmpty (pFocus removed.duplicate)))]

quotaResult =
    let state = cycles 40
        removed = closeAfter state [otherRow "Before"]
        replaced = closeAfter state [row "12", otherRow "Before"]
        ready = pLoad True [row "11"] |> Tuple.first
        check name value = (name, E.bool value)
        denied name variant = let value = refusal variant in check name (value.prepared && value.preserved && value.currentSettles)
    in E.object
        [("preconditions", E.object
            [check "public-watch-route-ready" (pReady ready)
            ,check "initial-read-batch-is-retained" (batchCount ready > 0)
            ,check "public-menu-opens" (pOpen ready |> Tuple.first |> pClosed |> not)])
        ,("checks", E.object
            [check "forty-correlated-watch-requests-issued" (state.issued == 40)
            ,check "forty-correlated-watch-replies-rearm" (state.completed == 40)
            ,check "unchanged-quota-sixteen-never-exceeded" (state.maximum <= 16)
            ,check "menu-and-group-remain-current-after-forty" state.preserved
            ,check "unchanged-replies-do-not-publish-or-focus" state.quiet
            ,check "read-only-watch-never-mutates" state.noMutation
            ,check "request-ids-never-replayed" (List.length state.requests == 40 && List.length (List.foldl (\request seen -> if List.member request seen then seen else request :: seen) [] state.requests) == 40)
            ,check "closed-opener-after-forty-restores-current-fallback" (removed.issued && removed.correlated && pClosed removed.model && List.length (pFallback removed.model) == 1 && pFocus removed.effects == pFallback removed.model)
            ,check "replacement-after-forty-never-inherits-old-focus" (replaced.issued && replaced.correlated && pClosed replaced.model && List.length (pFallback replaced.model) == 1 && pFocus replaced.effects == pFallback replaced.model && pFocus replaced.effects /= (group replaced.model.controller |> List.map .dom))
            ,check "closure-reply-cannot-replay-focus" (removed.issued && List.isEmpty (pFocus removed.duplicate))
            ,denied "foreign-binding-does-not-retire-current-batch" 0
            ,denied "foreign-request-does-not-retire-current-batch" 1
            ,denied "stale-base-does-not-retire-current-batch" 2
            ,denied "foreign-owner-does-not-retire-current-batch" 3
            ,denied "duplicate-prior-result-does-not-retire-next-batch" 4
            ,denied "malformed-result-does-not-retire-current-batch" 5
            ,denied "invalid-unchanged-payload-does-not-retire-current-batch" 6])
        ,("witness", E.object [("issued", E.int state.issued), ("completed", E.int state.completed), ("maximumPending", E.int state.maximum), ("remaining", E.int (batchCount state.model)), ("unrelatedBaseline", E.int state.retained), ("frame", pFrame state.model)
            ,("refusals", E.list (\variant -> let value = refusal variant in E.object [("variant", E.int variant), ("prepared", E.bool value.prepared), ("preserved", E.bool value.preserved), ("currentSettles", E.bool value.currentSettles), ("before", E.int value.before), ("afterInvalid", E.int value.afterInvalid), ("afterValid", E.int value.afterValid)]) (List.range 0 6))])
        ,("seeded", E.list quotaSeed (List.range 0 31))]

result = E.object [("legacy", legacyResult), ("quota", quotaResult)]

main : Program () () Never
main = Platform.worker {init=\_ -> ((),outgoing result),update=\_ state -> (state,Cmd.none),subscriptions=\_ -> Sub.none}
