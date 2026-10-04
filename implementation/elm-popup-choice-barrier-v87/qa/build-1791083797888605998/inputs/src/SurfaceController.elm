module SurfaceController exposing (Model, Event(..), Effect(..), initial, update, frame, desktop)

import Desktop
import Json.Decode as D
import Json.Encode as E
import Surface
import TaskbarShell
import UInt64 exposing (Counter)

type Model = Model { desktop : Desktop.Model, publication : Counter, lease : Counter, exhausted : Bool }
type Event = Interaction Desktop.Msg | Renderer D.Value | NativeDismiss Counter
type Effect = DesktopEffect Desktop.Effect | Publish E.Value

initial : Model
initial = Model {desktop=Desktop.initial,publication=UInt64.zero,lease=UInt64.zero,exhausted=False}

desktop : Model -> Desktop.Model
desktop (Model model) = model.desktop

frame : Model -> E.Value
frame (Model model) = Surface.packet model.publication model.lease model.desktop

apply : Desktop.Msg -> Model -> (Model,List Effect)
apply message ((Model model) as current) =
    if model.exhausted then (current,[]) else
    let
        (next,effects) = Desktop.update message model.desktop
        changed = next/=model.desktop
        oldMode = Surface.mode model.desktop
        nextMode = Surface.mode next
        newLease = nextMode/="closed" && (nextMode/=oldMode || (nextMode=="picker" && (model.desktop.windows.picker |> Maybe.map .generation)/=(next.windows.picker |> Maybe.map .generation)))
        lease = if newLease then UInt64.next model.lease else Just model.lease
    in
    if not changed && List.isEmpty effects then (current,[]) else
        case (UInt64.next model.publication,lease) of
            (Just publication,Just token) ->
                let result = Model {model | desktop=next,publication=publication,lease=token}
                in (result,Publish (frame result) :: List.map DesktopEffect effects)
            _ -> (Model {model | exhausted=True},[])

update : Event -> Model -> (Model,List Effect)
update event ((Model model) as current) =
    if model.exhausted then (current,[]) else
    case event of
        Interaction message -> apply message current
        Renderer raw -> Surface.resolve model.publication model.lease raw model.desktop |> Maybe.map (\message -> apply message current) |> Maybe.withDefault (current,[])
        NativeDismiss lease ->
            if lease/=model.lease || Surface.mode model.desktop=="closed" then (current,[]) else
                if model.desktop.open then
                    Desktop.capture model.desktop |> Maybe.map (\stamp -> apply (Desktop.CloseApplications stamp) current) |> Maybe.withDefault (current,[])
                else
                    model.desktop.windows.picker |> Maybe.map (\picker -> apply (Desktop.Window (TaskbarShell.Close picker.scope picker.generation)) current) |> Maybe.withDefault (current,[])
