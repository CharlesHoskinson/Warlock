port module BatchReplay exposing (main)

import OutputController as Outputs
import Binding
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
        (_,rows) = List.foldl apply (Outputs.initial,[]) events
    in ((),outgoing (E.list identity (List.reverse rows)))}

apply : D.Value -> (Outputs.Model,List E.Value) -> (Outputs.Model,List E.Value)
apply raw (model,rows) =
    let
        value name = D.decodeValue (D.field name D.value) raw |> Result.withDefault E.null
        kind = D.decodeValue (D.field "kind" D.string) raw |> Result.withDefault ""
        event = case kind of
            "prepared-deadline" -> D.decodeValue (D.field "token" UInt64.decoder) raw |> Result.toMaybe |> Maybe.map (TaskbarShell.ExpirePrepared >> Desktop.Window >> Outputs.Interaction)
            "prepared-cancel" -> D.decodeValue (D.field "token" UInt64.decoder) raw |> Result.toMaybe |> Maybe.map (TaskbarShell.CancelPrepared >> Desktop.Window >> Outputs.Interaction)
            "geometry-attach" -> Just (Outputs.Interaction (Desktop.Window (TaskbarShell.Native Shell.GeometryAttach)))
            "geometry-refresh" -> Just (Outputs.Interaction (Desktop.Window (TaskbarShell.Native Shell.GeometryRefresh)))
            "topology" -> Just (Outputs.Topology (value "frame"))
            "disposition" -> Just (Outputs.Disposition (value "frame"))
            "choice-deadline" -> Desktop.choiceToken (Controller.desktop (Outputs.controller model)) |> Maybe.map (Desktop.ChoiceDeadline >> Outputs.Interaction)
            "direct-native-begin" ->
                let desktop=Controller.desktop (Outputs.controller model)
                in D.decodeValue (D.field "operation" Effects.operationDecoder) raw |> Result.toMaybe
                    |> Maybe.andThen (\operation -> Maybe.map2 (\stamp incarnation -> Outputs.Interaction (Desktop.Window (TaskbarShell.Native (Shell.Act stamp operation incarnation))))
                        (if Effects.protocol operation==2 then Shell.captureGeometry desktop.windows.shell else Shell.capture desktop.windows.shell)
                        (D.decodeValue (D.field "incarnation" UInt64.decoder) raw |> Result.toMaybe))
            "native" -> Just (Outputs.Interaction (Desktop.Incoming (value "frame")))
            "action" -> Just (Outputs.Renderer (value "action"))
            "reflow" -> Just (Outputs.Reflow (value "frame"))
            "dismiss" -> Just (Outputs.Dismiss (value "frame"))
            "open" -> Desktop.capture (Controller.desktop (Outputs.controller model)) |> Maybe.map (Desktop.OpenApplications >> Outputs.Interaction)
            _ -> Nothing
        (updated,effects) = event |> Maybe.map (\message -> Outputs.update message model) |> Maybe.withDefault (model,[])
        (batched,extraEffects) = if D.decodeValue (D.field "mixed" D.bool) raw==Ok True then Outputs.update (Outputs.Interaction (Desktop.Window (TaskbarShell.Native Shell.GeometryRefresh))) updated else (updated,[])
        count = D.decodeValue (D.field "registerCopies" D.int) raw |> Result.withDefault 1
        padding = D.decodeValue (D.field "registerFocus" D.string) raw |> Result.toMaybe |> Maybe.map (Desktop.Focus >> Controller.DesktopEffect >> List.singleton) |> Maybe.withDefault []
        (next,submitted) = Outputs.register (List.concat (List.repeat count (effects++extraEffects))++padding) batched
        wires = List.filterMap (\effect -> case effect of
            Controller.DesktopEffect (Desktop.Send wire) -> Just wire
            Controller.DesktopEffect (Desktop.WindowEffect (Shell.Send wire)) -> Just wire
            Controller.DesktopEffect (Desktop.WindowEffect Shell.RestartBackend) -> Just (E.object [("protocolVersion",E.int 3),("kind",E.string "host-reconnect")])
            _ -> Nothing) effects
        packet = Controller.frame (Outputs.controller next)
        valid = SurfaceRenderer.decode (if kind=="validate" then value "frame" else packet) |> Result.map (\_ -> True) |> Result.withDefault False
        order = List.map (\effect -> case effect of
            Controller.Publish _ -> "publish"
            Controller.DesktopEffect (Desktop.Send _) -> "send"
            _ -> "local") effects
        windows = (Controller.desktop (Outputs.controller next)).windows
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
        counter maybeCounter = maybeCounter |> Maybe.map (UInt64.string >> E.string) |> Maybe.withDefault E.null
        correlation = E.object [("legacy",counter windows.shell.expected),("geometry",counter windows.shell.geometryExpected),("attach",counter windows.shell.geometryAttachExpected),("deferNotifications",E.bool windows.shell.deferNotifications)]
        row = E.object [("submitted",Maybe.withDefault E.null submitted),("batchCount",E.int (Outputs.pendingBatches next)),("outputs",Outputs.frame next),("correlation",correlation),("preparedToken",prepared |> Maybe.map (.token >> UInt64.string >> E.string) |> Maybe.withDefault E.null),("prepared",prepared |> Maybe.map preparedValue |> Maybe.withDefault E.null),("geometry",geometry),("unresolved",unresolved),("providerScope",scope |> Maybe.map scopeValue |> Maybe.withDefault E.null),("ownerScope",(Controller.desktop (Outputs.controller next)).ownerScope |> Maybe.map scopeValue |> Maybe.withDefault E.null),("ownerExhausted",E.bool (Controller.desktop (Outputs.controller next)).ownerExhausted),("focus",E.list E.string focus),("order",E.list E.string order),("frame",packet),("rendererAdmitted",E.bool valid),("attemptedRequests",E.list identity wires),("issued",E.list (\entry -> E.object [("binding",Binding.encode entry.binding),("protocol",E.int entry.protocol),("intent",Effects.encodeIntent entry.intent)]) windows.shell.issued),("unresolvedFull",E.list (\entry -> E.object [("intent",Effects.encodeIntent entry.intent),("protocol",E.int entry.effectProtocol),("status",E.string (Effects.statusName entry.status))]) windows.shell.effects.unresolved),("requests",E.list identity (case submitted |> Maybe.andThen (\batch -> D.decodeValue (D.field "requests" (D.list D.value)) batch |> Result.toMaybe) of
                    Just issued -> issued
                    Nothing -> [])),
              ("shell",Shell.encode windows.shell),("outstanding",E.int snapshot.outstanding),("registry",E.int (MenuBridge.receiptCount windows.menus)),("menu",menu)]
    in (next,row::rows)
