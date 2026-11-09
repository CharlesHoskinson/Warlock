port module MenuEscapeReplay exposing (main)

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
result =
    let menu = opened "keyboard"
        wire = currentEscape menu
        (dismissed,dismissEffects) = Outputs.update (Outputs.Escape wire) menu
        fresh = observation "3" [row True] dismissed
        (returned,returnEffects) = Outputs.update (native fresh) dismissed
        (duplicateRead,duplicateEffects) = Outputs.update (native fresh) returned
        (duplicateEscape,escapeAgainEffects) = Outputs.update (Outputs.Escape wire) returned
        (removed,removedEffects) = Outputs.update (native (observation "3" [] dismissed)) dismissed
        (unavailable,unavailableEffects) = Outputs.update (native (observation "3" [row False] dismissed)) dismissed
        disconnected = step (native (E.object [("protocolVersion",E.int 3),("kind",E.string "host-disconnected")])) dismissed
        (afterDisconnect,disconnectEffects) = Outputs.update (native fresh) disconnected
        retired = step (Outputs.Topology (Fixture.topology "2" [("2",Fixture.right)])) menu
        pointerMenu = opened "pointer"
        (pointerClosed,pointerEffects) = Outputs.update (Outputs.Escape (currentEscape pointerMenu)) pointerMenu
        (pointerReturned,pointerReturnEffects) = Outputs.update (native (observation "3" [row True] pointerClosed)) pointerClosed
        applicationsAction = E.object [("viewProtocol",E.int 1),("kind",E.string "view-action"),("scope",scope "1"),("action",E.object
            [("surfaceProtocol",E.int 2),("kind",E.string "surface-action"),("surface",E.string "bar"),("publication",E.string (field "publication" ready)),("lease",E.string (field "lease" ready)),("id",E.string "bar:applications"),("trigger",E.string "keyboard")])]
        applications = step (Outputs.Renderer applicationsAction) ready
        appsClosed = step (Outputs.Escape (currentEscape applications)) applications
        wrongEnvelope = E.object [("scope",scope "1"),("publication",E.string (field "publication" menu)),("lease",E.string (field "lease" menu)),("surface",E.string "bar")]
        expectedFocus = "group:{\"lifetime\":\"1\",\"session\":\"1\",\"frontend\":\"1\"}:1:3:application:documents"
        preconditions =
            [("one-current-eligible-taskbar-group",List.length (TaskbarShell.groups (Fixture.desktop ready).windows)==1 && Shell.available (Fixture.desktop ready).windows.shell)
            ,("keyboard-menu-opened-through-renderer",Surface.mode (Fixture.desktop menu)=="menu" && (Fixture.desktop menu).popupOrigin==Desktop.KeyboardEntry && (Fixture.desktop menu).menuOrigin/=Nothing)
            ,("actual-enabled-menu-close-control",Surface.controls (Fixture.desktop menu) |> List.any (\item -> item.id=="control:menu-close" && item.enabled && item.message/=Nothing))
            ,("pointer-menu-opened-through-renderer",Surface.mode (Fixture.desktop pointerMenu)=="menu" && (Fixture.desktop pointerMenu).popupOrigin==Desktop.PointerEntry)
            ,("applications-other-mode-opened",Surface.mode (Fixture.desktop applications)=="applications")]
        checks =
            [("current-menu-escape-closes",closed dismissed && (MenuBridge.menuSnapshot (Fixture.desktop dismissed).windows.menus).menu==Nothing)
            ,("dismissal-queues-current-refresh",kinds dismissEffects==["projection-request"] && (Fixture.desktop dismissed).windows.shell.expected/=Nothing)
            ,("no-return-before-fresh-observation",closed dismissed && (Fixture.desktop dismissed).returnFocus/=Nothing && List.isEmpty (focuses dismissEffects))
            ,("eligible-origin-return-once",closed returned && focuses returnEffects==[expectedFocus] && (Fixture.desktop returned).returnFocus==Nothing)
            ,("duplicate-escape-no-repeat-focus",List.isEmpty (focuses duplicateEffects++focuses escapeAgainEffects) && Outputs.frame duplicateRead==Outputs.frame returned && Outputs.frame duplicateEscape==Outputs.frame returned)
            ,("stale-lease-refused",unchanged (Outputs.Escape (escape "1" (field "publication" menu) "0")) menu)
            ,("stale-publication-refused",unchanged (Outputs.Escape (escape "1" "0" (field "lease" menu))) menu)
            ,("foreign-owner-scope-refused",unchanged (Outputs.Escape (escape "2" (field "publication" menu) (field "lease" menu))) menu)
            ,("retired-view-refused",unchanged (Outputs.Escape wire) retired)
            ,("removed-origin-no-focus",closed removed && (Fixture.desktop removed).returnFocus==Nothing && List.isEmpty (focuses removedEffects))
            ,("changed-binding-or-output-no-focus",closed afterDisconnect && (Fixture.desktop afterDisconnect).returnFocus==Nothing && List.isEmpty (focuses disconnectEffects))
            ,("pointer-origin-no-keyboard-steal",closed pointerClosed && closed pointerReturned && (Fixture.desktop pointerClosed).returnFocus==Nothing && List.isEmpty (focuses pointerEffects++focuses pointerReturnEffects))
            ,("nonmenu-close-path-preserved",closed appsClosed)
            ,("unavailable-origin-no-focus",closed unavailable && List.isEmpty (focuses unavailableEffects))
            ,("missing-close-does-nothing",unchanged (Outputs.Escape (currentEscape ready)) ready)
            ,("wrong-surface-envelope-refused",unchanged (Outputs.Escape wrongEnvelope) menu)]
    in E.object
        [("preconditions",E.object (List.map (Tuple.mapSecond E.bool) preconditions))
        ,("checks",E.object (List.map (Tuple.mapSecond E.bool) checks))
        ,("observations",E.list identity [observed "menu" menu [],observed "dismissed" dismissed dismissEffects,observed "returned" returned returnEffects,observed "removed" removed removedEffects])]

main : Program () () Never
main = Platform.worker {init=\_ -> ((),outgoing result),update=\_ state -> (state,Cmd.none),subscriptions=\_ -> Sub.none}
