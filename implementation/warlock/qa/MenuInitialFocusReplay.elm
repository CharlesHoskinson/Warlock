port module MenuInitialFocusReplay exposing (main)

import Desktop
import Json.Decode as D
import Json.Encode as E
import MenuBridge
import OutputController as Outputs
import OutputRetirementReplay as Fixture
import Platform
import Shell
import Surface
import SurfaceController as Controller
import TaskbarShell
import UInt64

port outgoing : E.Value -> Cmd msg

scope output = E.object [("id",E.string output),("generation",E.string "1")]
field name model = D.decodeValue (D.at ["frame",name] D.string) (Outputs.frame model) |> Result.withDefault "missing"
step event model = Outputs.update event model |> Tuple.first
native raw = Outputs.Interaction (Desktop.Incoming raw)
row available = E.object [("incarnation",E.string "1"),("label",E.string "Document 1"),("owner",E.null),("application",E.string "documents"),("minimized",E.bool False),("available",E.bool available)]
observation revision rows model =
    let request = (Fixture.desktop model).windows.shell.expected |> Maybe.map UInt64.string |> Maybe.withDefault "0"
    in E.object
        [("protocolVersion",E.int 3),("kind",E.string "action-projection"),("binding",Fixture.bound),("requestId",E.string request)
        ,("context",E.object [("lifetime",E.string "1"),("epoch",E.string "1"),("output",E.string "1"),("revision",E.string revision)])
        ,("scene",E.object [("revision",E.string revision),("focused",if List.isEmpty rows then E.null else E.string "1"),("windows",E.list identity rows)])]
ready =
    let base = Fixture.base [("1",Fixture.left),("2",Fixture.right)]
        refreshing = step (Outputs.Interaction (Desktop.Window (TaskbarShell.Native Shell.Refresh))) base
    in step (native (observation "2" [row True] refreshing)) refreshing
context trigger model = E.object
    [("viewProtocol",E.int 1),("kind",E.string "view-action"),("scope",scope "1")
    ,("action",E.object [("surfaceProtocol",E.int 2),("kind",E.string "surface-context"),("surface",E.string "bar")
        ,("publication",E.string (field "publication" model)),("lease",E.string (field "lease" model))
        ,("id",E.string "bar:group:application:documents"),("trigger",E.string trigger),("x",E.int 0),("y",E.int 0)])]
opened trigger = step (Outputs.Renderer (context trigger ready)) ready
escape output publication lease = E.object [("scope",scope output),("publication",E.string publication),("lease",E.string lease)]
currentEscape model = escape "1" (field "publication" model) (field "lease" model)
closed model = Surface.mode (Fixture.desktop model)=="closed"
focuses effects = List.filterMap (\effect -> case effect of
    Controller.DesktopEffect (Desktop.Focus target) -> Just target
    _ -> Nothing) effects
requests effects = List.filterMap (\effect -> case effect of
    Controller.DesktopEffect (Desktop.WindowEffect (Shell.Send wire)) -> Just wire
    Controller.DesktopEffect (Desktop.Send wire) -> Just wire
    _ -> Nothing) effects
kinds effects = List.map (D.decodeValue (D.field "kind" D.string) >> Result.withDefault "invalid") (requests effects)
unchanged event model =
    let (after,effects)=Outputs.update event model
    in Outputs.frame after==Outputs.frame model && Fixture.desktop after==Fixture.desktop model && List.isEmpty effects
observed label model effects = E.object [("label",E.string label),("frame",Outputs.frame model),("focus",E.list E.string (focuses effects)),("requests",E.list identity (requests effects)),("returnFocusPending",E.bool ((Fixture.desktop model).returnFocus/=Nothing))]

contextAt trigger output publication lease model =
    E.object [("viewProtocol",E.int 1),("kind",E.string "view-action"),("scope",scope output)
        ,("action",E.object [("surfaceProtocol",E.int 2),("kind",E.string "surface-context"),("surface",E.string "bar")
            ,("publication",E.string publication),("lease",E.string lease),("id",E.string "bar:group:application:documents"),("trigger",E.string trigger),("x",E.int 0),("y",E.int 0)])]

menuClose model =
    Surface.controls (Fixture.desktop model) |> List.filter (\item -> item.id=="control:menu-close" && item.enabled) |> List.map .domId

registered model effects = Outputs.register effects model |> Tuple.second
commitFocus model effects =
    registered model effects |> Maybe.andThen (D.decodeValue (D.field "focus" (D.list D.string)) >> Result.toMaybe) |> Maybe.withDefault []
commitMatches model effects expected =
    case registered model effects of
        Nothing -> False
        Just packet ->
            D.decodeValue (D.field "viewProtocol" D.int) packet==Ok 1
            && D.decodeValue (D.field "kind" D.string) packet==Ok "view-commit"
            && D.decodeValue (D.field "projection" D.value) packet==Ok (Outputs.frame model)
            && D.decodeValue (D.field "focus" (D.list D.string)) packet==Ok expected

sample seed =
    let choice=modBy 8 seed
        refreshing=step (Outputs.Interaction (Desktop.Window (TaskbarShell.Native Shell.Refresh))) ready
        unavailable=step (native (observation "3" [row False] refreshing)) refreshing
        removed=step (native (observation "3" [] refreshing)) refreshing
        retired=step (Outputs.Topology (Fixture.topology "2" [("2",Fixture.right)])) ready
        before=if choice==5 then unavailable else if choice==6 then removed else if choice==7 then retired else ready
        trigger=if choice==1 then "pointer" else "keyboard"
        wire=contextAt trigger (if choice==4 then "99" else "1") (if choice==2 then "0" else field "publication" before) (if choice==3 then "9" else field "lease" before) before
        (after,effects)=Outputs.update (Outputs.Renderer wire) before
        (repeated,repeatEffects)=Outputs.update (Outputs.Renderer wire) after
        expected=if choice==0 then ["menu:1:close"] else []
        valid=focuses effects==expected && commitFocus after effects==expected && List.isEmpty (focuses repeatEffects) && List.isEmpty (commitFocus repeated repeatEffects)
            && (if choice<=1 then Surface.mode (Fixture.desktop after)=="menu" else Surface.mode (Fixture.desktop after)=="closed")
            && (if choice==0 then menuClose after==expected && commitMatches after effects expected else True)
    in E.object [("seed",E.int seed),("case",E.int choice),("passed",E.bool valid),("mode",E.string (Surface.mode (Fixture.desktop after)))
        ,("focus",E.list E.string (focuses effects)),("commitFocus",E.list E.string (commitFocus after effects)),("repeatFocus",E.list E.string (focuses repeatEffects))
        ,("projection",Outputs.frame after),("commit",registered after effects |> Maybe.withDefault E.null)]

result =
    let (menu,openEffects)=Outputs.update (Outputs.Renderer (context "keyboard" ready)) ready
        (pointerMenu,pointerEffects)=Outputs.update (Outputs.Renderer (context "pointer" ready)) ready
        (repeated,repeatEffects)=Outputs.update (Outputs.Renderer (context "keyboard" ready)) menu
        (refreshing,refreshEffects)=Outputs.update (Outputs.Interaction (Desktop.Window (TaskbarShell.Native Shell.Refresh))) menu
        (refreshed,refreshedEffects)=Outputs.update (native (observation "3" [row True] refreshing)) refreshing
        (dismissed,dismissEffects)=Outputs.update (Outputs.Escape (currentEscape menu)) menu
        (returned,returnEffects)=Outputs.update (native (observation "3" [row True] dismissed)) dismissed
        (removed,removedEffects)=Outputs.update (native (observation "3" [] dismissed)) dismissed
        (unavailable,unavailableEffects)=Outputs.update (native (observation "3" [row False] dismissed)) dismissed
        disconnected=step (native (E.object [("protocolVersion",E.int 3),("kind",E.string "host-disconnected")])) ready
        retired=step (Outputs.Topology (Fixture.topology "2" [("2",Fixture.right)])) ready
        expected=["menu:1:close"]
        expectedReturn=["group:{\"lifetime\":\"1\",\"session\":\"1\",\"frontend\":\"1\"}:1:3:application:documents"]
        preconditions=
            [("current-taskbar-group-eligible",Shell.available (Fixture.desktop ready).windows.shell && List.length (TaskbarShell.groups (Fixture.desktop ready).windows)==1)
            ,("keyboard-menu-opened",Surface.mode (Fixture.desktop menu)=="menu" && (Fixture.desktop menu).popupOrigin==Desktop.KeyboardEntry)
            ,("pointer-menu-opened",Surface.mode (Fixture.desktop pointerMenu)=="menu" && (Fixture.desktop pointerMenu).popupOrigin==Desktop.PointerEntry)
            ,("exact-enabled-current-menu-close",menuClose menu==expected)
            ,("menu-publication-and-lease-current",field "publication" menu/="0" && field "lease" menu=="1")]
        checks=
            [("keyboard-open-one-exact-dom-focus",focuses openEffects==expected)
            ,("focus-in-same-current-projection-commit",commitMatches menu openEffects expected)
            ,("focus-target-is-current-unique-close",focuses openEffects==menuClose menu && List.length (focuses openEffects)==1)
            ,("keyboard-origin-established-before-open",(Fixture.desktop menu).popupOrigin==Desktop.KeyboardEntry && (Fixture.desktop menu).menuOrigin/=Nothing && focuses openEffects==expected)
            ,("pointer-open-no-dom-focus",List.isEmpty (focuses pointerEffects) && List.isEmpty (commitFocus pointerMenu pointerEffects))
            ,("old-open-callback-no-repeat",Outputs.frame repeated==Outputs.frame menu && List.isEmpty (focuses repeatEffects) && List.isEmpty (commitFocus repeated repeatEffects))
            ,("refresh-request-no-initial-focus",List.isEmpty (focuses refreshEffects) && List.isEmpty (commitFocus refreshing refreshEffects))
            ,("refreshed-menu-no-initial-focus",List.isEmpty (focuses refreshedEffects) && List.isEmpty (commitFocus refreshed refreshedEffects))
            ,("stale-publication-no-focus",unchanged (Outputs.Renderer (contextAt "keyboard" "1" "0" (field "lease" ready) ready)) ready)
            ,("stale-lease-no-focus",unchanged (Outputs.Renderer (contextAt "keyboard" "1" (field "publication" ready) "9" ready)) ready)
            ,("foreign-owner-no-focus",unchanged (Outputs.Renderer (contextAt "keyboard" "99" (field "publication" ready) (field "lease" ready) ready)) ready)
            ,("retired-owner-no-focus",unchanged (Outputs.Renderer (context "keyboard" ready)) retired)
            ,("disconnected-origin-no-focus",unchanged (Outputs.Renderer (context "keyboard" ready)) disconnected)
            ,("dismiss-does-not-immediately-restore",closed dismissed && List.isEmpty (focuses dismissEffects) && (Fixture.desktop dismissed).returnFocus/=Nothing)
            ,("eligible-return-stays-exact-group",focuses returnEffects==expectedReturn && commitMatches returned returnEffects expectedReturn)
            ,("removed-return-target-refused",List.isEmpty (focuses removedEffects) && List.isEmpty (commitFocus removed removedEffects))
            ,("unavailable-return-target-refused",List.isEmpty (focuses unavailableEffects) && List.isEmpty (commitFocus unavailable unavailableEffects))]
        seeds=[0,1,2,3,4,5,6,7,8,9,10,11,12,13,14,15,16,17,18,19,20,21,22,23,24,25,26,27,28,29,30,31]
    in E.object [("preconditions",E.object (List.map (Tuple.mapSecond E.bool) preconditions)),("checks",E.object (List.map (Tuple.mapSecond E.bool) checks))
        ,("seeded",E.object [("algorithm",E.string "literal-seed-modulo8-public-event-sequence"),("seeds",E.list E.int seeds),("samples",E.list sample seeds)])
        ,("observations",E.list identity [observed "keyboard-menu" menu openEffects,observed "pointer-menu" pointerMenu pointerEffects,observed "returned" returned returnEffects])]

main : Program () () Never
main = Platform.worker {init=\_ -> ((),outgoing result),update=\_ state -> (state,Cmd.none),subscriptions=\_ -> Sub.none}
