module SurfaceController exposing (Model, Event(..), Effect(..), initial, update, frame, desktop, reconciliation)

import Menu
import Binding
import ReconciliationFrame
import ReconciliationTracking as Recovery
import Effects
import MenuBridge
import Desktop
import Switcher
import Json.Decode as D
import Json.Encode as E
import Surface
import Shell
import TaskbarShell
import UInt64 exposing (Counter)

type Model = Model { recovery : Recovery.Model, desktop : Desktop.Model, publication : Counter, lease : Counter, exhausted : Bool }
type Event = Interaction Desktop.Msg | Renderer D.Value | NativeDismiss Counter | NativeReflow Counter | NativeRelocate
type Effect = DesktopEffect Desktop.Effect | Publish E.Value

initial : Model
initial = Model {recovery=Recovery.empty,desktop=Desktop.initial,publication=UInt64.zero,lease=UInt64.zero,exhausted=False}

desktop : Model -> Desktop.Model
desktop (Model model) = model.desktop

reconciliation : Model -> Recovery.Model
reconciliation (Model model) = model.recovery

frame : Model -> E.Value
frame (Model model) = Surface.packet model.publication model.lease model.desktop

applyOrdinary : Desktop.Msg -> Model -> (Model,List Effect)
applyOrdinary message ((Model model) as current) =
    if model.exhausted then (current,[]) else
    let
        (next,effects) = Desktop.update message model.desktop
        changed = next/=model.desktop
        oldMode = Surface.mode model.desktop
        nextMode = Surface.mode next
        newLease = nextMode/="closed" && (nextMode/=oldMode || ((MenuBridge.menuSnapshot model.desktop.windows.menus).menu |> Maybe.map .id)/=((MenuBridge.menuSnapshot next.windows.menus).menu |> Maybe.map .id) || (nextMode=="picker" && (model.desktop.windows.picker |> Maybe.map .generation)/=(next.windows.picker |> Maybe.map .generation)) || (nextMode=="switcher" && Switcher.generation model.desktop.switcher/=Switcher.generation next.switcher))
        lease = if newLease then UInt64.next model.lease else Just model.lease
    in
    if not changed && List.isEmpty effects then (current,[]) else
        let stableSurface = model.publication/=UInt64.zero && not newLease && List.isEmpty effects
                    && E.encode 0 (Surface.packet model.publication model.lease next)==E.encode 0 (frame current)
            stableApplications = case message of
                Desktop.Window (TaskbarShell.Native (Shell.SupersedeObservations _)) ->
                    oldMode=="applications" && nextMode=="applications" && not newLease
                        && E.encode 0 (Surface.packet model.publication model.lease next)==E.encode 0 (frame current)
                _ -> False
        in if stableSurface || stableApplications then
            (Model {model|desktop=next},List.map DesktopEffect effects)
        else case (UInt64.next model.publication,lease) of
            (Just publication,Just token) ->
                let result = Model {model | desktop=next,publication=publication,lease=token}
                in (result,Publish (frame result) :: List.map DesktopEffect effects)
            _ -> (Model {model | exhausted=True},[])


apply : Desktop.Msg -> Model -> (Model,List Effect)
apply message ((Model model) as current) =
    let incoming=case message of
            Desktop.Incoming raw -> Just raw
            Desktop.Window (TaskbarShell.Native (Shell.Incoming raw)) -> Just raw
            _ -> Nothing
        register effects recovery = List.foldl (\effect state -> case effect of
            DesktopEffect (Desktop.WindowEffect (Shell.Send wire)) ->
                case D.decodeValue (D.map2 Tuple.pair (D.field "kind" D.string) (D.field "requestId" UInt64.decoder)) wire of
                    Ok (kind,request) -> Recovery.requested kind request state
                    Err _ -> state
            _ -> state) recovery effects
        ordinary prepared action =
            let (next,effects)=applyOrdinary action prepared
                (Model result)=next
                recovery=case incoming of
                    Just raw -> Recovery.observed raw model.desktop.windows.shell result.desktop.windows.shell result.recovery |> Recovery.legacy raw result.desktop.windows.shell
                    Nothing -> result.recovery
                reset=if model.desktop.windows.shell.binding/=result.desktop.windows.shell.binding || result.desktop.windows.shell.phase==Shell.Detached then Recovery.reset recovery else recovery
                hasReads=List.any (\effect -> case effect of
                    DesktopEffect (Desktop.WindowEffect (Shell.Send wire)) -> D.decodeValue (D.field "kind" D.string) wire |> Result.map (\kind -> List.member kind ["projection-request","geometry-facts-request"]) |> Result.withDefault False
                    _ -> False) effects
                proofs=(List.filter (\slot -> not slot.released) reset.slots |> List.filterMap .proof) ++ (reset.informational |> Maybe.map List.singleton |> Maybe.withDefault []) |> List.foldl (\proof values -> if List.member proof values then values else proof::values) []
                readyEffects=if hasReads then List.map (\proof -> DesktopEffect (Desktop.Send (E.object [("protocolVersion",E.int 3),("kind",E.string "reconciliation-ready"),("binding",Binding.encode proof.binding),("proofRequestId",E.string (UInt64.string proof.requestId)),("queriedBinding",Binding.encode proof.queriedBinding)]))) proofs else []
                emitted=readyEffects++effects
            in if result.desktop/=model.desktop && not (List.any (\effect -> case effect of
                Publish _ -> True
                _ -> False) effects) then
                    case UInt64.next result.publication of
                        Just publication ->
                            let updated=Model {result|recovery=register emitted reset,publication=publication}
                            in (updated,Publish (frame updated)::emitted)
                        Nothing -> (Model {result|exhausted=True},[])
               else (Model {result|recovery=register emitted reset},emitted)
        clearChoices application =
            let windows=application.windows
                shell=windows.shell
            in {application|filesOpen=False,filesOpening=False,systemMenuOpen=False,systemMenuOpening=False,systemMenuConfirmation=Nothing,notificationsOpen=False,notificationsOpening=False,settingsOpen=False,settingsOpening=False,choice=Nothing,overview=False,overviewWorkspace=Nothing,switcher=Switcher.cancel (Switcher.generation application.switcher) application.switcher,switcherExpected=Nothing,switcherHistory=Nothing,returnFocus=Nothing,menuOrigin=Nothing,windows={windows|picker=Nothing,menus=MenuBridge.retireChoices windows.menus,shell={shell|deferNotifications=False}}}
        publishDesktop recovery next =
            if next==model.desktop then (Model {model|recovery=recovery},[]) else
            case UInt64.next model.publication of
                Nothing -> (Model {model|exhausted=True},[])
                Just publication ->
                    let updated=Model {model|desktop=next,recovery=recovery,publication=publication}
                    in (updated,[Publish (frame updated)])
    in case incoming of
        Nothing -> ordinary current message
        Just raw ->
            case (D.decodeValue (D.field "kind" D.string) raw,model.desktop.windows.shell.binding) of
                (Ok "host-reservation-unknown",Just currentBinding) ->
                    if model.desktop.windows.shell.phase==Shell.Detached || model.desktop.windows.shell.phase==Shell.Exhausted then (current,[]) else
                    case Recovery.unknown currentBinding raw model.recovery of
                        Err "Historical reservation capacity" -> ordinary current (Desktop.Window (TaskbarShell.Native Shell.ReconciliationFull))
                        Err _ -> (current,[])
                        Ok (recovery,record) ->
                            let (admitted,_)=Desktop.update (Desktop.Window (TaskbarShell.Native (Shell.RecoveredUnknown record.effectProtocol record.intent))) model.desktop
                                windows=admitted.windows
                                menus=MenuBridge.observeReservationUnknown record.binding record.effectProtocol record.intent windows.menus
                                tracked=List.any (\entry -> entry.intent==record.intent && entry.effectProtocol==record.effectProtocol && entry.status==Effects.Unknown) windows.shell.effects.unresolved
                            in if not tracked then (current,[]) else publishDesktop recovery {admitted|windows={windows|menus=menus}}
                (Ok "binding-retirement",Just currentBinding) ->
                    if model.desktop.windows.shell.phase==Shell.Detached || model.desktop.windows.shell.phase==Shell.Exhausted then (current,[]) else
                    case Recovery.announce currentBinding raw model.recovery of
                        Err _ -> (current,[])
                        Ok recovery ->
                            case D.decodeValue ReconciliationFrame.proofDecoder raw of
                                Err _ -> (current,[])
                                Ok proof ->
                                    let (next,effects)=ordinary (Model {model|recovery=recovery,desktop=clearChoices model.desktop}) (Desktop.Window (TaskbarShell.Native Shell.Refresh))
                                        ready=E.object [("protocolVersion",E.int 3),("kind",E.string "reconciliation-ready"),("binding",Binding.encode currentBinding),("proofRequestId",E.string (UInt64.string proof.requestId)),("queriedBinding",Binding.encode proof.queriedBinding)]
                                    in if List.any (\effect -> case effect of
                                        DesktopEffect (Desktop.Send wire) -> D.decodeValue (D.field "kind" D.string) wire==Ok "reconciliation-ready"
                                        _ -> False) effects then (next,effects) else (next,DesktopEffect (Desktop.Send ready)::effects)
                (Ok "host-reservation-released",Just currentBinding) ->
                    if model.desktop.windows.shell.phase==Shell.Detached || model.desktop.windows.shell.phase==Shell.Exhausted then (current,[]) else
                    case Recovery.release currentBinding raw model.recovery of
                        Err _ -> (current,[])
                        Ok (recovery,record) ->
                            if not (List.any (\entry -> entry.status==Effects.Unknown && entry.effectProtocol==record.effectProtocol && entry.intent==record.intent) model.desktop.windows.shell.effects.unresolved) then (Model {model|recovery=recovery},[]) else
                            let cleared=clearChoices model.desktop
                                windows=cleared.windows
                                menus=MenuBridge.releaseReservationUnknown record.binding record.effectProtocol record.intent windows.menus
                                preserveShared=List.any (\slot -> not slot.released && slot.record.intent==record.intent && slot.record.effectProtocol==record.effectProtocol) recovery.slots
                                (released,_)=Desktop.update (Desktop.Window (TaskbarShell.Native (Shell.ReservationReleased preserveShared record.binding record.effectProtocol record.intent))) {cleared|windows={windows|menus=menus}}
                            in publishDesktop recovery released
                _ -> ordinary current message

update : Event -> Model -> (Model,List Effect)
update event ((Model model) as current) =
    if model.exhausted then (current,[]) else
    case event of
        Interaction message -> apply message current
        Renderer raw -> Surface.resolve model.publication model.lease raw model.desktop |> Maybe.map (\message -> apply message current) |> Maybe.withDefault (current,[])
        NativeRelocate ->
            if Surface.mode model.desktop=="closed" then (current,[]) else
                case (UInt64.next model.lease,UInt64.next model.publication) of
                    (Just token,Just shown) ->
                        let result = Model {model | lease=token,publication=shown}
                        in (result,[Publish (frame result)])
                    _ -> (Model {model | exhausted=True},[])
        NativeReflow lease ->
            if lease/=model.lease || Surface.mode model.desktop=="closed" then (current,[]) else
            if model.desktop.snap/=Nothing then apply Desktop.InvalidateSnap current else
                case (UInt64.next model.lease,UInt64.next model.publication) of
                    (Just token,Just shown) ->
                        -- The host has retired the old popup/input lease. Output
                        -- geometry changes its presentation, not the authority
                        -- or membership of the displayed choices. Ordinary native
                        -- observations still reconcile changed window state.
                        let result = Model {model | lease=token,publication=shown}
                        in (result,[Publish (frame result)])
                    _ -> (Model {model | exhausted=True},[])
        NativeDismiss lease ->
            if lease/=model.lease || Surface.mode model.desktop=="closed" then (current,[]) else
                if model.desktop.filesOpen then
                    Desktop.capture model.desktop |> Maybe.map (\stamp -> apply (Desktop.CloseFiles stamp) current) |> Maybe.withDefault (current,[])
                else if model.desktop.systemMenuOpen then
                    Desktop.capture model.desktop |> Maybe.map (\stamp -> apply (Desktop.CloseSystemMenu stamp) current) |> Maybe.withDefault (current,[])
                else if model.desktop.notificationsOpen then
                    Desktop.capture model.desktop |> Maybe.map (\stamp -> apply (Desktop.CloseNotifications stamp) current) |> Maybe.withDefault (current,[])
                else if model.desktop.settingsOpen then
                    Desktop.capture model.desktop |> Maybe.map (\stamp -> apply (Desktop.CloseSettings stamp) current) |> Maybe.withDefault (current,[])
                else if model.desktop.snap/=Nothing then
                    Desktop.capture model.desktop |> Maybe.map (\stamp -> apply (Desktop.CloseSnap stamp) current) |> Maybe.withDefault (current,[])
                else if Surface.mode model.desktop=="menu" then
                    (MenuBridge.menuSnapshot model.desktop.windows.menus).menu |> Maybe.map (\menu -> apply (Desktop.Window (TaskbarShell.MenuEvent (Menu.Dismiss menu.id))) current) |> Maybe.withDefault (current,[])
                else if Desktop.switcherOpen model.desktop then
                    Desktop.capture model.desktop |> Maybe.map (\stamp -> apply (Desktop.CloseSwitcher stamp) current) |> Maybe.withDefault (current,[])
                else if model.desktop.overview then
                    Desktop.capture model.desktop |> Maybe.map (\stamp -> apply (Desktop.CloseOverview stamp) current) |> Maybe.withDefault (current,[])
                else if model.desktop.open then
                    Desktop.capture model.desktop |> Maybe.map (\stamp -> apply (Desktop.CloseApplications stamp) current) |> Maybe.withDefault (current,[])
                else
                    model.desktop.windows.picker |> Maybe.map (\picker -> apply (Desktop.Window (TaskbarShell.Close picker.scope picker.generation)) current) |> Maybe.withDefault (current,[])
