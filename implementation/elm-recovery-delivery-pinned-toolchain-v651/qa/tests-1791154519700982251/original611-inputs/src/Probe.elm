port module Probe exposing (main)
import Platform
import Desktop
import SurfaceController as C
import SurfaceRenderer
import TaskbarShell
import Shell
import Effects
import Menu
import MenuBridge
import Binding
import Json.Decode as D
import Json.Encode as E
import UInt64
port incoming : (D.Value -> msg) -> Sub msg
port outgoing : E.Value -> Cmd msg
type Msg = Run D.Value
number text = D.decodeValue UInt64.decoder (E.string text) |> Result.withDefault UInt64.zero
main : Program () () Msg
main = Platform.worker {init=\_ -> ((),Cmd.none),subscriptions=\_ -> incoming Run,update=\(Run raw) _ ->
 let events=D.decodeValue (D.list D.value) raw |> Result.withDefault []
     (_,rows)=List.foldl apply (C.initial,[]) events
 in ((),outgoing (E.list identity (List.reverse rows)))}
apply raw (model,rows) =
 let kind=D.decodeValue (D.field "kind" D.string) raw |> Result.withDefault ""
     value key=D.decodeValue (D.field key D.value) raw |> Result.withDefault E.null
     desktop=C.desktop model
     event=case kind of
       "owner" -> Just (C.Interaction (Desktop.OwnerScope (value "frame")))
       "native" -> Just (C.Interaction (Desktop.Incoming (value "frame")))
       "refresh" -> Just (C.Interaction (Desktop.Window (TaskbarShell.Native Shell.Refresh)))
       "reconnect" -> Just (C.Interaction (Desktop.Window (TaskbarShell.Native Shell.Reconnect)))
       "menu-open" -> Shell.capture desktop.windows.shell |> Maybe.map (\stamp -> C.Interaction (Desktop.OpenWindowMenu stamp (number "2")))
       "menu-minimize" -> (MenuBridge.menuSnapshot desktop.windows.menus).menu |> Maybe.andThen (\view -> List.indexedMap Tuple.pair view.items |> List.filter (\(_,item) -> item.action==Menu.Minimize) |> List.head |> Maybe.map (\(index,_) -> C.Interaction (Desktop.Window (TaskbarShell.MenuEvent (Menu.Activate view.id view.binding index)))))
       "act2" -> Shell.capture desktop.windows.shell |> Maybe.map (\stamp -> C.Interaction (Desktop.Window (TaskbarShell.Native (Shell.Act stamp Effects.Minimize (number "2")))))
       "renderer-act2" -> SurfaceRenderer.decode (C.frame model) |> Result.toMaybe |> Maybe.andThen (SurfaceRenderer.action False "bar:group:application:GTK Application") |> Maybe.map C.Renderer
       _ -> Nothing
     (next,effects)=event |> Maybe.map (\e -> C.update e model) |> Maybe.withDefault (model,[])
     shell=(C.desktop next).windows.shell
     state=shell.effects
     menu=MenuBridge.menuSnapshot (C.desktop next).windows.menus
     wires=List.filterMap (\effect -> case effect of
       C.DesktopEffect (Desktop.Send wire) -> Just wire
       C.DesktopEffect (Desktop.WindowEffect (Shell.Send wire)) -> Just wire
       _ -> Nothing) effects
     counter=UInt64.string >> E.string
     row=E.object [("history",E.list (\slot -> E.object [("binding",Binding.encode slot.record.binding),("status",E.string (Effects.statusName slot.record.status)),("released",E.bool slot.released)]) (C.reconciliation next).slots),("inputKind",E.string kind),("frame",C.frame next),("shell",Shell.encode shell),("binding",Maybe.map Binding.encode shell.binding |> Maybe.withDefault E.null),("shellRequest",counter shell.request),("expected",Maybe.map counter shell.expected |> Maybe.withDefault E.null),("geometryExpected",Maybe.map counter shell.geometryExpected |> Maybe.withDefault E.null),("blocked",E.bool (Effects.blocked (number (D.decodeValue (D.at ["binding","lifetime"] D.string) (E.object [("binding",Maybe.map Binding.encode shell.binding |> Maybe.withDefault E.null)]) |> Result.withDefault "0")) (number "2") state)),("blocked1",E.bool (state.observed |> Maybe.map (\snapshot -> Effects.blocked snapshot.context.lifetime (number "1") state) |> Maybe.withDefault False)),("unresolved",E.int (List.length state.unresolved)),("transaction",Effects.encode state),("effectRequest",counter state.request),("effectGeneration",counter state.generation),("outstanding",E.int menu.outstanding),("historicalUnknownMenus",E.int menu.releasedUnknown),("registry",E.int (MenuBridge.receiptCount (C.desktop next).windows.menus)),("prepared",E.bool (MenuBridge.preparedSnapshot (C.desktop next).windows.menus/=Nothing)),("choice",E.bool ((C.desktop next).choice/=Nothing)),("wires",E.list identity wires)]
 in (next,row::rows)
