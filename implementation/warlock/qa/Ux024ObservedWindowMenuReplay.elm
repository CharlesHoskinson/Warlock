port module Ux024ObservedWindowMenuReplay exposing (main)

-- Public production reducers and rendered packets only. No endpoint or native
-- capability is constructed by this component fixture.
import Desktop
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

sample seed =
    let (attached,issued)=receive (attachment (E.list E.string ["window-read"])) base
        variant=modBy 8 seed
        target=String.fromInt (9000+seed)
        current=snapshot "1" "1" [row target]
        wire=case variant of
            0 -> reply (bound "1") (readId issued) "Observed" current
            1 -> reply (bound "1") (readId issued) "Observed" (snapshot "1" "1" [])
            2 -> reply (bound "2") (readId issued) "Observed" current
            3 -> reply (bound "1") "99" "Observed" current
            4 -> reply (bound "1") (readId issued) "Unknown" E.null
            5 -> reply (bound "1") (readId issued) "Unavailable" E.null
            6 -> reply (bound "1") (readId issued) "Observed" (snapshot "1" "1" [row target,row target])
            _ -> reply (bound "1") (readId issued) "Observed" (snapshot "2" "1" [row target])
        (after,effects)=receive wire attached
    in E.object [("seed",E.int seed),("variant",E.int variant),("eligibleGroup",E.bool (not (noGroups after))),("noMutation",E.bool (noMutations (issued++effects))),("noFocus",E.bool (List.isEmpty (focuses effects))),("nativeAvailable",E.bool (Shell.available (Fixture.desktop after).windows.shell))]

result =
    let (attached,issued)=receive (attachment (E.list E.string ["window-read"])) base
        (ready,readEffects)=load [row "11"]
        (opened,openEffects)=openMenu "keyboard" ready
        (pointer,pointerEffects)=openMenu "pointer" ready
        (closedMenu,closeEffects)=escape opened
        fresh rows=receive (reply (bound "1") (readId closeEffects) "Observed" (snapshot "1" "2" rows)) closedMenu
        (returned,returnEffects)=fresh [row "11"]
        (_,repeatReturn)=receive (reply (bound "1") (readId closeEffects) "Observed" (snapshot "1" "2" [row "11"])) returned
        (replaced,replacedEffects)=fresh [row "12"]
        (removed,removedEffects)=fresh []
        (unknown,unknownEffects)=receive (reply (bound "1") (readId closeEffects) "Unknown" E.null) closedMenu
        (pending,pendingEffects)=refresh ready
        (stale,staleEffects)=receive (reply (bound "1") "99" "Observed" (snapshot "1" "2" [row "12"])) pending
        (retired,_)=receive (E.object [("protocolVersion",E.int 3),("kind",E.string "host-disconnected")]) ready
        (late,lateEffects)=receive (reply (bound "1") "1" "Observed" (snapshot "1" "3" [row "11"])) retired
        (refused,_)=step (Outputs.Interaction (Desktop.Window (TaskbarShell.Native (Shell.RegistrationRefused [] [])))) ready
        (refusedMenu,refusedEffects)=openMenu "keyboard" refused
        (full,_)=step (Outputs.Interaction (Desktop.Window (TaskbarShell.Native Shell.ReconciliationFull))) ready
        (fullMenu,fullEffects)=openMenu "keyboard" full
        (legacy,legacyEffects)=receive legacyAttachment base
        (empty,emptyEffects)=receive (attachment (E.list identity [])) base
        malformed value=receive (attachment value) base |> Tuple.first
        unchangedCases=[malformed (E.list E.string ["window-read","window-read"]),malformed (E.list E.string ["window-effect"]),malformed (E.bool True)]
        (foreign,foreignEffects)=receive (reply (bound "2") (readId issued) "Observed" (snapshot "2" "1" [row "11"])) attached
        (wrongOwner,wrongOwnerEffects)=receive (reply (bound "1") (readId issued) "Observed" (snapshot "2" "1" [row "11"])) attached
        (staleView,viewEffects)=step (Outputs.Topology (Fixture.topology "2" [])) closedMenu
        (_,viewReturnEffects)=receive (reply (bound "1") (readId closeEffects) "Observed" (snapshot "1" "2" [row "11"])) staleView
        check name yes=(name,E.bool yes)
        expectedReturn=group returned |> List.map .dom
    in E.object [("checks",E.object
        [check "attachment-is-application-only" ((Fixture.desktop attached).windows.shell.applicationOnly && (Fixture.desktop attached).windows.shell.binding/=Nothing)
        ,check "capability-emits-one-bound-read" (List.length (readRequests issued)==1 && (readRequests issued |> List.head |> Maybe.map (\wire -> D.decodeValue (D.field "binding" D.value) wire==Ok (bound "1")) |> Maybe.withDefault False))
        ,check "read-only-does-not-enable-native-actions" (not (Shell.available (Fixture.desktop ready).windows.shell) && not (Shell.applicationLaunchAvailable (Fixture.desktop ready).windows.shell))
        ,check "actual-observed-group-is-inspectable" (List.length (group ready)==1)
        ,check "actual-context-opens-inspection-menu" (Surface.mode (Fixture.desktop opened)=="menu")
        ,check "inspection-shows-real-title" (controls opened |> List.any (\item -> String.contains "Document α😀" (item.label++item.detail)))
        ,check "inspection-shows-real-appid" (controls opened |> List.any (\item -> String.contains "org.example.Editor" (item.label++item.detail)))
        ,check "inspection-has-refresh-and-close" (not (List.isEmpty (closeTargets opened)) && (controls opened |> List.any (\item -> item.id=="control:observation-refresh" && item.enabled)))
        ,check "inspection-no-enabled-native-effect" (controls opened |> List.filter .enabled |> List.all (\item -> List.member item.id ["control:menu-close","control:observation-refresh"]))
        ,check "keyboard-open-focuses-current-close" (not (List.isEmpty (closeTargets opened)) && focuses openEffects==closeTargets opened)
        ,check "pointer-open-does-not-focus" (Surface.mode (Fixture.desktop pointer)=="menu" && List.isEmpty (focuses pointerEffects))
        ,check "escape-closes-and-reads-once" (closed closedMenu && List.length (readRequests closeEffects)==1 && List.isEmpty (focuses closeEffects))
        ,check "fresh-exact-incarnation-restores-once" (not (List.isEmpty expectedReturn) && focuses returnEffects==expectedReturn && List.isEmpty (focuses repeatReturn))
        ,check "same-application-replacement-cannot-restore" (List.isEmpty (focuses replacedEffects) && closed replaced)
        ,check "removed-origin-cannot-restore" (List.isEmpty (focuses removedEffects) && noGroups removed)
        ,check "unknown-cannot-restore" (List.isEmpty (focuses unknownEffects) && noGroups unknown)
        ,check "pending-read-disables-inspection" (List.length (readRequests pendingEffects)==1 && noGroups pending)
        ,check "wrong-request-cannot-settle" (Outputs.frame stale==Outputs.frame pending && List.isEmpty (focuses staleEffects))
        ,check "foreign-binding-cannot-publish" (noGroups foreign && List.isEmpty (focuses foreignEffects))
        ,check "foreign-owner-generation-cannot-publish" (noGroups wrongOwner && List.isEmpty (focuses wrongOwnerEffects))
        ,check "detached-reply-cannot-revive" (noGroups late && List.isEmpty (focuses lateEffects))
        ,check "transport-refusal-cannot-open" (closed refusedMenu && List.isEmpty (focuses refusedEffects))
        ,check "reconciliation-full-cannot-open" (closed fullMenu && List.isEmpty (focuses fullEffects))
        ,check "retired-presentation-view-cannot-restore" (List.isEmpty (focuses viewReturnEffects) && noMutations viewEffects)
        ,check "absent-capability-remains-unavailable" ((Fixture.desktop legacy).windows.shell.binding/=Nothing && List.isEmpty (readRequests legacyEffects) && noGroups legacy)
        ,check "empty-capability-remains-unavailable" ((Fixture.desktop empty).windows.shell.binding/=Nothing && List.isEmpty (readRequests emptyEffects) && noGroups empty)
        ,check "malformed-capability-grants-nothing" (List.all (\model -> (Fixture.desktop model).windows.shell.binding==Nothing && noGroups model) unchangedCases)
        ,check "inspection-declared-keyboard-order" ((controls opened |> List.filter .enabled |> List.map .id)==["control:menu-close","control:observation-refresh"])
        ,check "inspection-information-cannot-activate" (controls opened |> List.filter (\item -> not (List.member item.id ["control:menu-close","control:observation-refresh"])) |> List.all (\item -> not item.enabled && item.message==Nothing))
        ,check "all-routes-preserve-no-effects" (List.all noMutations [issued,readEffects,openEffects,pointerEffects,closeEffects,returnEffects,replacedEffects,removedEffects,unknownEffects,pendingEffects,staleEffects,foreignEffects,wrongOwnerEffects,lateEffects,refusedEffects,fullEffects,viewReturnEffects])
        ])
        ,("preconditions",E.object [check "actual-presentation-view-one" (Fixture.owner base==Just "1"),check "baseline-local-attachment-valid" ((Fixture.desktop legacy).windows.shell.binding/=Nothing),check "no-fabricated-catalog" ((Fixture.desktop ready).applications==Nothing)])
        ,("seeded",E.object [("seeds",E.list E.int (List.range 0 31)),("samples",E.list sample (List.range 0 31))])
        ,("openedFrame",Outputs.frame opened),("returnedFrame",Outputs.frame returned),("openFocus",E.list E.string (focuses openEffects)),("returnFocus",E.list E.string (focuses returnEffects))]

main : Program () () Never
main = Platform.worker {init=\_ -> ((),outgoing result),update=\_ state -> (state,Cmd.none),subscriptions=\_ -> Sub.none}
