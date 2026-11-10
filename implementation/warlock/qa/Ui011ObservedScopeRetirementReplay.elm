port module Ui011ObservedScopeRetirementReplay exposing (main)

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

-- Refresh enters through the currently rendered popup control, never a direct
-- model update. Its keyboard/pointer origin is the actual public wire field.
refreshMenu trigger model = step (Outputs.Renderer (viewAction "surface-action" trigger "popup" "control:observation-refresh" model)) model
fallback model = bar model |> List.filter (\entry -> entry.id=="bar:applications" && entry.enabled) |> List.map .dom
emptyFocus effects = List.isEmpty (focuses effects)
sameReadAuthority before after =
    let previous=(Fixture.desktop before).windows.shell
        current=(Fixture.desktop after).windows.shell
    in current.binding==previous.binding && current.windowExpected==previous.windowExpected && current.windowObservation==previous.windowObservation && current.windowObservationOperations==previous.windowObservationOperations
refusalWitness before after effects = E.object [("authorityUnchanged",E.bool (sameReadAuthority before after)),("decoderRefused",E.bool ((Fixture.desktop after).windows.shell.decoderRefusal/=Nothing)),("focus",E.list E.string (focuses effects))]
finishRead status rows pending issued = receive (reply (bound "1") (readId issued) status (if status=="Observed" then snapshot "1" "2" rows else E.null)) pending
prepared trigger rows =
    let (ready,_)=load rows
        (opened,_)=openMenu trigger ready
    in refreshMenu trigger opened

sample seed =
    let ident=String.fromInt (1000+seed)
        variant=modBy 8 seed
        trigger=if variant==7 then "pointer" else "keyboard"
        (pending,issued)=prepared trigger [row ident]
        rows=if variant==1 then [] else if variant==2 then [row (String.fromInt (2000+seed))] else [row ident]
        wire=case variant of
            3 -> reply (bound "1") "999" "Observed" (snapshot "1" "2" rows)
            4 -> reply (bound "1") (readId issued) "Unknown" E.null
            5 -> reply (bound "2") (readId issued) "Observed" (snapshot "1" "2" rows)
            6 -> reply (bound "1") (readId issued) "Observed" (snapshot "2" "2" rows)
            _ -> reply (bound "1") (readId issued) "Observed" (snapshot "1" "2" rows)
        (after,effects)=receive wire pending
        (_,duplicate)=receive wire after
        expected=if variant==0 then group after |> List.map .dom else if variant==1 || variant==2 then fallback after else []
    in E.object [("seed",E.int seed),("variant",E.int variant),("prepared",E.bool (List.length (readRequests issued)==1 && closed pending && emptyFocus issued)),("actualFocus",E.list E.string (focuses effects)),("expectedFocus",E.list E.string expected),("expectedEligible",E.bool (variant>2 || List.length expected==1)),("once",E.bool (emptyFocus duplicate)),("noMutation",E.bool (noMutations (issued++effects++duplicate)))]

result =
    let (ready,_)=load [row "11"]
        (opened,_)=openMenu "keyboard" ready
        (pending,issued)=refreshMenu "keyboard" opened
        fresh rows=finishRead "Observed" rows pending issued
        (same,sameEffects)=fresh [row "11"]
        (removed,removedEffects)=fresh []
        (replacement,replacementEffects)=fresh [row "12"]
        (_,duplicateEffects)=receive (reply (bound "1") (readId issued) "Observed" (snapshot "1" "2" [])) removed
        (wrongRequest,wrongRequestEffects)=receive (reply (bound "1") "999" "Observed" (snapshot "1" "2" [])) pending
        (oldRevision,oldRevisionEffects)=receive (reply (bound "1") (readId issued) "Observed" (snapshot "1" "1" [])) pending
        (foreignBinding,foreignBindingEffects)=receive (reply (bound "2") (readId issued) "Observed" (snapshot "1" "2" [])) pending
        (foreignOwner,foreignOwnerEffects)=receive (reply (bound "1") (readId issued) "Observed" (snapshot "2" "2" [])) pending
        (_,unknownEffects)=finishRead "Unknown" [] pending issued
        (_,unavailableEffects)=finishRead "Unavailable" [] pending issued
        (disconnected,_)=receive (E.object [("protocolVersion",E.int 3),("kind",E.string "host-disconnected")]) pending
        (detached,detachedEffects)=finishRead "Observed" [] disconnected issued
        (refused,_)=step (Outputs.Interaction (Desktop.Window (TaskbarShell.Native (Shell.RegistrationRefused [] [])))) pending
        (_,refusedEffects)=finishRead "Observed" [] refused issued
        (full,_)=step (Outputs.Interaction (Desktop.Window (TaskbarShell.Native Shell.ReconciliationFull))) pending
        (_,fullEffects)=finishRead "Observed" [] full issued
        (gone,_)=step (Outputs.Topology (Fixture.topology "2" [])) pending
        (_,goneEffects)=finishRead "Observed" [] gone issued
        (changed,_)=step (Outputs.Topology (Fixture.topology "2" [("2",Fixture.left)])) pending
        (_,changedEffects)=finishRead "Observed" [] changed issued
        (pointerPending,pointerIssued)=prepared "pointer" [row "11"]
        (_,pointerEffects)=finishRead "Observed" [] pointerPending pointerIssued
        (escaped,escapeIssued)=escape opened
        (_,escapeRemovedEffects)=finishRead "Observed" [] escaped escapeIssued
        (_,escapeReplacementEffects)=finishRead "Observed" [row "12"] escaped escapeIssued
        (ordinaryPending,ordinaryIssued)=refresh ready
        (_,ordinaryEffects)=finishRead "Observed" [] ordinaryPending ordinaryIssued
        staleWire=viewAction "surface-action" "keyboard" "popup" "control:observation-refresh" opened
        (_,staleEffects)=step (Outputs.Renderer staleWire) pending
        check name yes=(name,E.bool yes)
        allEffects=[issued,sameEffects,removedEffects,replacementEffects,duplicateEffects,wrongRequestEffects,oldRevisionEffects,foreignBindingEffects,foreignOwnerEffects,unknownEffects,unavailableEffects,detachedEffects,refusedEffects,fullEffects,goneEffects,changedEffects,pointerIssued,pointerEffects,escapeIssued,escapeRemovedEffects,escapeReplacementEffects,ordinaryIssued,ordinaryEffects,staleEffects]
    in E.object
        [("checks",E.object
            [check "public-refresh-retires-menu-and-reads-once" (closed pending && List.length (readRequests issued)==1)
            ,check "pending-read-never-focuses" (emptyFocus issued)
            ,check "same-incarnation-restores-current-group" (List.length (group same)==1 && focuses sameEffects==(group same |> List.map .dom))
            ,check "closed-origin-restores-declared-fallback" (List.length (fallback removed)==1 && focuses removedEffects==fallback removed)
            ,check "replacement-restores-only-declared-fallback" (List.length (group replacement)==1 && focuses replacementEffects==fallback replacement && focuses replacementEffects/=(group replacement |> List.map .dom))
            ,check "fallback-keeps-captured-control-identity" (fallback removed==fallback opened && not (List.isEmpty (fallback opened)))
            ,check "duplicate-reply-does-not-refocus" (emptyFocus duplicateEffects)
            ,check "wrong-request-cannot-settle" (Outputs.frame wrongRequest==Outputs.frame pending && emptyFocus wrongRequestEffects)
            ,check "old-revision-cannot-settle" (Outputs.frame oldRevision==Outputs.frame pending && emptyFocus oldRevisionEffects)
            ,check "foreign-binding-cannot-settle" (sameReadAuthority pending foreignBinding && (Fixture.desktop foreignBinding).windows.shell.decoderRefusal/=Nothing && emptyFocus foreignBindingEffects)
            ,check "foreign-owner-cannot-settle" (sameReadAuthority pending foreignOwner && (Fixture.desktop foreignOwner).windows.shell.decoderRefusal/=Nothing && emptyFocus foreignOwnerEffects)
            ,check "unknown-does-not-grant-fallback" (emptyFocus unknownEffects)
            ,check "unavailable-does-not-grant-fallback" (emptyFocus unavailableEffects)
            ,check "detached-ineligible-fallback-cannot-focus" (List.isEmpty (fallback detached) && emptyFocus detachedEffects)
            ,check "transport-refusal-cannot-focus" (emptyFocus refusedEffects)
            ,check "reconciliation-full-cannot-focus" (emptyFocus fullEffects)
            ,check "retired-presentation-cannot-focus" (emptyFocus goneEffects)
            ,check "changed-presentation-cannot-focus" (emptyFocus changedEffects)
            ,check "pointer-refresh-does-not-focus" (List.length (readRequests pointerIssued)==1 && emptyFocus pointerIssued && emptyFocus pointerEffects)
            ,check "post-escape-removed-origin-still-no-focus" (List.length (readRequests escapeIssued)==1 && emptyFocus escapeRemovedEffects)
            ,check "post-escape-replacement-still-no-focus" (emptyFocus escapeReplacementEffects)
            ,check "refresh-without-open-scope-does-not-focus" (List.length (readRequests ordinaryIssued)==1 && emptyFocus ordinaryEffects)
            ,check "stale-refresh-callback-does-not-issue" (List.isEmpty (requests staleEffects) && emptyFocus staleEffects)
            ,check "all-routes-preserve-no-native-mutation" (List.all noMutations allEffects)
            ])
        ,("preconditions",E.object
            [check "current-view-one" (Fixture.owner ready==Just "1")
            ,check "current-observed-keyboard-menu" (Surface.mode (Fixture.desktop opened)=="menu")
            ,check "actual-enabled-refresh-control" (controls opened |> List.any (\item -> item.id=="control:observation-refresh" && item.enabled && item.message/=Nothing))
            ,check "actual-enabled-applications-fallback" (List.length (fallback opened)==1)
            ,check "application-only-no-native-authority" ((Fixture.desktop ready).windows.shell.applicationOnly && not (Shell.available (Fixture.desktop ready).windows.shell))
            ])
        ,("seeded",E.object [("seeds",E.list E.int (List.range 0 31)),("samples",E.list sample (List.range 0 31))])
        ,("foreignBindingWitness",refusalWitness pending foreignBinding foreignBindingEffects),("foreignOwnerWitness",refusalWitness pending foreignOwner foreignOwnerEffects)
        ,("pendingFrame",Outputs.frame pending),("removedFrame",Outputs.frame removed),("replacementFrame",Outputs.frame replacement)
        ,("sameFocus",E.list E.string (focuses sameEffects)),("removedFocus",E.list E.string (focuses removedEffects)),("replacementFocus",E.list E.string (focuses replacementEffects))]

main : Program () () Never
main = Platform.worker {init=\_ -> ((),outgoing result),update=\_ state -> (state,Cmd.none),subscriptions=\_ -> Sub.none}
