port module MenuSurfaceReplay exposing (main)

import Desktop
import GeometryProjection
import Effects
import Menu
import MenuBridge
import Provider
import Shell
import TaskbarShell
import Json.Decode as D
import Json.Encode as E
import SurfaceController as Controller
import SurfaceRenderer
import UInt64
import Platform

port incoming : (D.Value -> msg) -> Sub msg
port outgoing : E.Value -> Cmd msg
type Msg = Run D.Value

main : Program () () Msg
main = Platform.worker {init=\_ -> ((),Cmd.none),subscriptions=\_ -> incoming Run,update=\(Run raw) _ ->
    let events = D.decodeValue (D.list D.value) raw |> Result.withDefault []
        (_,rows) = List.foldl apply (Controller.initial,[]) events
    in ((),outgoing (E.list identity (List.reverse rows)))}

apply : D.Value -> (Controller.Model,List E.Value) -> (Controller.Model,List E.Value)
apply raw (model,rows) =
    let
        value name = D.decodeValue (D.field name D.value) raw |> Result.withDefault E.null
        kind = D.decodeValue (D.field "kind" D.string) raw |> Result.withDefault ""
        event = case kind of
            "direct-native-begin" ->
                let desktop = Controller.desktop model
                in D.decodeValue (D.field "operation" Effects.operationDecoder) raw |> Result.toMaybe
                    |> Maybe.andThen (\operation ->
                        Maybe.map2 (\stamp incarnation -> Controller.Interaction (Desktop.Window (TaskbarShell.Native (Shell.Act stamp operation incarnation))))
                            (if Effects.protocol operation==2 then Shell.captureGeometry desktop.windows.shell else Shell.capture desktop.windows.shell)
                            (D.decodeValue (D.field "incarnation" UInt64.decoder) raw |> Result.toMaybe))
            "prepared-deadline" -> D.decodeValue (D.field "token" UInt64.decoder) raw |> Result.toMaybe |> Maybe.map (TaskbarShell.ExpirePrepared >> Desktop.Window >> Controller.Interaction)
            "prepared-cancel" -> D.decodeValue (D.field "token" UInt64.decoder) raw |> Result.toMaybe |> Maybe.map (TaskbarShell.CancelPrepared >> Desktop.Window >> Controller.Interaction)
            "geometry-attach" -> Just (Controller.Interaction (Desktop.Window (TaskbarShell.Native Shell.GeometryAttach)))
            "geometry-refresh" -> Just (Controller.Interaction (Desktop.Window (TaskbarShell.Native Shell.GeometryRefresh)))
            "owner" -> Just (Controller.Interaction (Desktop.OwnerScope (value "frame")))
            "choice-deadline" -> Desktop.choiceToken (Controller.desktop model) |> Maybe.map (Desktop.ChoiceDeadline >> Controller.Interaction)
            "native" -> Just (Controller.Interaction (Desktop.Incoming (value "frame")))
            "action" -> Just (Controller.Renderer (value "action"))
            "reflow" -> D.decodeValue (D.field "lease" UInt64.decoder) raw |> Result.toMaybe |> Maybe.map Controller.NativeReflow
            "dismiss" -> D.decodeValue (D.field "lease" UInt64.decoder) raw |> Result.toMaybe |> Maybe.map Controller.NativeDismiss
            "open" -> Desktop.capture (Controller.desktop model) |> Maybe.map (Desktop.OpenApplications >> Controller.Interaction)
            _ -> Nothing
        (next,effects) = event |> Maybe.map (\message -> Controller.update message model) |> Maybe.withDefault (model,[])
        wires = List.filterMap (\effect -> case effect of
            Controller.DesktopEffect (Desktop.Send wire) -> Just wire
            Controller.DesktopEffect (Desktop.WindowEffect (Shell.Send wire)) -> Just wire
            Controller.DesktopEffect (Desktop.WindowEffect Shell.RestartBackend) -> Just (E.object [("protocolVersion",E.int 3),("kind",E.string "host-reconnect")])
            _ -> Nothing) effects
        packet = Controller.frame next
        valid = SurfaceRenderer.decode (if kind=="validate" then value "frame" else packet) |> Result.map (\_ -> True) |> Result.withDefault False
        order = List.map (\effect -> case effect of
            Controller.Publish _ -> "publish"
            Controller.DesktopEffect (Desktop.Send _) -> "send"
            _ -> "local") effects
        windows = (Controller.desktop next).windows
        snapshot = MenuBridge.menuSnapshot windows.menus
        menu = case snapshot.menu of
            Nothing -> E.null
            Just current -> E.object
                [("id",E.int (Menu.menuNumber current.id)),("selected",current.selected |> Maybe.map E.int |> Maybe.withDefault E.null),
                 ("status",E.string (case current.status of
                    Menu.Ready -> "ready"
                    Menu.Pending _ -> "pending"
                    Menu.Unknown _ -> "unknown"
                    Menu.Refused _ -> "refused"
                    Menu.Cancelled -> "cancelled"))]
        scope = MenuBridge.currentProvider windows.menus |> Maybe.map Provider.presentationScope
        scopeValue owner = E.object [("outputId",E.string (UInt64.string owner.outputId)),("providerId",E.string (UInt64.string owner.providerId))]
        focus = List.filterMap (\effect -> case effect of
            Controller.DesktopEffect (Desktop.Focus target) -> Just target
            _ -> Nothing) effects
        geometry = windows.shell.geometry |> Maybe.map (\observed -> E.object
            [("revision",E.string (UInt64.string observed.context.revision)),("output",E.string (UInt64.string observed.context.output))
            ,("windows",E.list (\w -> E.object [("incarnation",E.string (UInt64.string w.incarnation)),("mode",E.string (GeometryProjection.modeName w.nativeMode)),("minimized",E.bool w.minimized)]) observed.windows)]) |> Maybe.withDefault E.null
        unresolved = E.list (\t -> E.object [("effectProtocol",E.int t.effectProtocol),("intent",Effects.encodeIntent t.intent),("status",E.string (Effects.statusName t.status))]) windows.shell.effects.unresolved
        prepared = MenuBridge.preparedSnapshot windows.menus
        preparedValue slot = E.object [("token",E.string (UInt64.string slot.token)),("legacyRequest",E.string (UInt64.string slot.legacyRequest)),("geometryRequest",slot.geometryRequest |> Maybe.map (UInt64.string >> E.string) |> Maybe.withDefault E.null),("legacyReady",E.bool slot.legacyReady),("geometryReady",E.bool slot.geometryReady)]
        row = E.object [("preparedToken",prepared |> Maybe.map (.token >> UInt64.string >> E.string) |> Maybe.withDefault E.null),("prepared",prepared |> Maybe.map preparedValue |> Maybe.withDefault E.null),("geometry",geometry),("unresolved",unresolved),("providerScope",scope |> Maybe.map scopeValue |> Maybe.withDefault E.null),("ownerScope",(Controller.desktop next).ownerScope |> Maybe.map scopeValue |> Maybe.withDefault E.null),("ownerExhausted",E.bool (Controller.desktop next).ownerExhausted),("focus",E.list E.string focus),("order",E.list E.string order),("frame",packet),("rendererAdmitted",E.bool valid),("requests",E.list identity wires),
              ("shell",Shell.encode windows.shell),("outstanding",E.int snapshot.outstanding),("registry",E.int (MenuBridge.receiptCount windows.menus)),("menu",menu)]
    in (next,row::rows)
