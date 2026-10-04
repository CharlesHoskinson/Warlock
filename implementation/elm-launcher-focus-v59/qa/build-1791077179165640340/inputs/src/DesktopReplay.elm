port module DesktopReplay exposing (main)
import Array exposing (Array)
import Catalog
import Desktop
import Json.Decode as D
import Json.Encode as E
import Launch
import Platform
import Shell
import UInt64
port incoming : (D.Value -> msg) -> Sub msg
port outgoing : E.Value -> Cmd msg
type Msg = Run D.Value
type alias State = { model : Desktop.Model, selections : Array Launch.Selection }
main : Program () () Msg
main = Platform.worker {init=\_ -> ((),Cmd.none),subscriptions=\_ -> incoming Run,update=\(Run raw) _ ->
    let events = D.decodeValue (D.list D.value) raw |> Result.withDefault []
        (_,rows) = List.foldl apply ({model=Desktop.initial,selections=Array.empty},[]) events
    in ((),outgoing (E.list identity (List.reverse rows)))}
apply : D.Value -> (State,List E.Value) -> (State,List E.Value)
apply raw (state,rows) =
    let kind = D.decodeValue (D.field "kind" D.string) raw |> Result.withDefault ""
        message = case kind of
            "open" -> Desktop.capture state.model |> Maybe.map Desktop.OpenApplications
            "close" -> Desktop.capture state.model |> Maybe.map Desktop.CloseApplications
            "incoming" -> D.decodeValue (D.field "frame" D.value) raw |> Result.toMaybe |> Maybe.map Desktop.Incoming
            "start" -> D.decodeValue (D.field "index" D.int) raw |> Result.toMaybe |> Maybe.andThen (\index -> Array.get index state.selections) |> Maybe.map Desktop.Start
            _ -> Nothing
        (model,effects) = message |> Maybe.map (\value -> Desktop.update value state.model) |> Maybe.withDefault (state.model,[])
        selections = if kind=="select" then
            D.decodeValue (D.field "entry" D.string) raw |> Result.toMaybe |> Maybe.andThen (\entry -> Launch.select entry model.launch) |> Maybe.map (\selection -> Array.push selection state.selections) |> Maybe.withDefault state.selections
            else state.selections
        wires = List.filterMap (\effect -> case effect of
            Desktop.Send wire -> Just wire
            Desktop.WindowEffect (Shell.Send wire) -> Just wire
            _ -> Nothing) effects
        row = E.object [("status",E.string (Launch.status model.launch)),("count",E.int (model.applications |> Maybe.map (Catalog.entries >> List.length) |> Maybe.withDefault 0)),("expected",model.expected |> Maybe.map (UInt64.string >> E.string) |> Maybe.withDefault E.null),("open",E.bool model.open),("selections",E.int (Array.length selections)),("wires",E.list identity wires)]
    in ({model=model,selections=selections},row::rows)
