module SurfaceController exposing (Model, Event(..), Effect(..), initial, update, frame, desktop)

import Menu
import Binding
import ReconciliationTracking as Recovery
import Effects
import MenuBridge
import Desktop
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

frame : Model -> E.Value
frame (Model model) = Surface.packet model.publication model.lease model.desktop

apply : Desktop.Msg -> Model -> (Model,List Effect)
applyOrdinary message ((Model model) as current) =
    if model.exhausted then (current,[]) else
    let
        (next,effects) = Desktop.update message model.desktop
        changed = next/=model.desktop
        oldMode = Surface.mode model.desktop
        nextMode = Surface.mode next
        newLease = nextMode/="closed" && (nextMode/=oldMode || ((MenuBridge.menuSnapshot model.desktop.windows.menus).menu |> Maybe.map .id)/=((MenuBridge.menuSnapshot next.windows.menus).menu |> Maybe.map .id) || (nextMode=="picker" && (model.desktop.windows.picker |> Maybe.map .generation)/=(next.windows.picker |> Maybe.map .generation)))
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
                Model result=next
                recovery=case incoming of
                    Just raw -> Recovery.observed raw model.desktop.windows.shell result.desktop.windows.shell result.recovery |> Recovery.legacy raw
                    Nothing -> result.recovery
                reset=if model.desktop.windows.shell.binding/=result.desktop.windows.shell.binding || result.desktop.windows.shell.phase==Shell.Detached then Recovery.reset recovery else recovery
            in (Model {result|recovery=register effects reset},effects)
        clearChoices desktop =
            let windows=desktop.windows
                shell=windows.shell
            in {desktop|choice=Nothing,returnFocus=Nothing,menuOrigin=Nothing,windows={windows|picker=Nothing,menus=MenuBridge.retireChoices windows.menus,shell={shell|deferNotifications=False}}}
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
                    case Recovery.unknown currentBinding raw model.recovery of
                        Err _ -> (current,[])
                        Ok (recovery,record) ->
                            let (admitted,_)=Desktop.update (Desktop.Window (TaskbarShell.Native (Shell.RecoveredUnknown record.effectProtocol record.intent))) model.desktop
                                windows=admitted.windows
                                menus=MenuBridge.observeReservationUnknown record.binding record.effectProtocol record.intent windows.menus
                                tracked=List.any (\entry -> entry.intent==record.intent && entry.effectProtocol==record.effectProtocol && entry.status==Effects.Unknown) windows.shell.effects.unresolved
                            in if not tracked then (current,[]) else publishDesktop recovery {admitted|windows={windows|menus=menus}}
                (Ok "binding-retirement",Just currentBinding) ->
                    case Recovery.announce currentBinding raw model.recovery of
                        Err _ -> (current,[])
                        Ok recovery -> ordinary (Model {model|recovery=recovery,desktop=clearChoices model.desktop}) (Desktop.Window (TaskbarShell.Native Shell.Refresh))
                (Ok "host-reservation-released",Just currentBinding) ->
                    case Recovery.release currentBinding raw model.recovery of
                        Err _ -> (current,[])
                        Ok (recovery,record) ->
                            let cleared=clearChoices model.desktop
                                windows=cleared.windows
                                menus=MenuBridge.releaseReservationUnknown record.binding record.effectProtocol record.intent windows.menus
                                (released,_)=Desktop.update (Desktop.Window (TaskbarShell.Native (Shell.ReservationReleased record.binding record.effectProtocol record.intent))) {cleared|windows={windows|menus=menus}}
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
                case (UInt64.next model.lease,UInt64.next model.publication) of
                    (Just token,Just shown) ->
                        let refreshed = Model {model | lease=token,publication=shown}
                            (result,effects)=apply (Desktop.Window (TaskbarShell.Native Shell.Refresh)) refreshed
                        in (result,Publish (frame result)::effects)
                    _ -> (Model {model | exhausted=True},[])
        NativeDismiss lease ->
            if lease/=model.lease || Surface.mode model.desktop=="closed" then (current,[]) else
                if Surface.mode model.desktop=="menu" then
                    (MenuBridge.menuSnapshot model.desktop.windows.menus).menu |> Maybe.map (\menu -> apply (Desktop.Window (TaskbarShell.MenuEvent (Menu.Dismiss menu.id))) current) |> Maybe.withDefault (current,[])
                else if model.desktop.open then
                    Desktop.capture model.desktop |> Maybe.map (\stamp -> apply (Desktop.CloseApplications stamp) current) |> Maybe.withDefault (current,[])
                else
                    model.desktop.windows.picker |> Maybe.map (\picker -> apply (Desktop.Window (TaskbarShell.Close picker.scope picker.generation)) current) |> Maybe.withDefault (current,[])
