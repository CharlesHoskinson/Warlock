port module Probe exposing (main)
import Platform
import Desktop
import SurfaceController as C
import SurfaceRenderer
import TaskbarShell
import Shell
import Effects
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
     packet=C.frame model
     event=case kind of
       "native" -> Just (C.Interaction (Desktop.Incoming (value "frame")))
       "refresh" -> Just (C.Interaction (Desktop.Window (TaskbarShell.Native Shell.Refresh)))
       "retry-observation" -> Just (C.Interaction Desktop.RetryWindows)
       "recovery-control" -> SurfaceRenderer.decode packet |> Result.toMaybe |> Maybe.andThen (SurfaceRenderer.action False "bar:recovery-refresh") |> Maybe.map C.Renderer
       "family-one" -> SurfaceRenderer.decode packet |> Result.toMaybe |> Maybe.andThen (SurfaceRenderer.action True "family:1") |> Maybe.map C.Renderer
       "applications" -> Desktop.capture (C.desktop model) |> Maybe.map (Desktop.OpenApplications >> C.Interaction)
       "activate-current" -> SurfaceRenderer.decode packet |> Result.toMaybe |> Maybe.andThen (SurfaceRenderer.action False "bar:group:application:GTK Application") |> Maybe.map C.Renderer
       _ -> Nothing
     (next,effects)=event |> Maybe.map (\e -> C.update e model) |> Maybe.withDefault (model,[])
     state=(C.desktop next).windows.shell.effects
     blocked=state.observed |> Maybe.map (\s -> Effects.blocked s.context.lifetime (number "2") state) |> Maybe.withDefault False
     wires=List.filterMap (\effect -> case effect of
       C.DesktopEffect (Desktop.Send wire) -> Just wire
       C.DesktopEffect (Desktop.WindowEffect (Shell.Send wire)) -> Just wire
       _ -> Nothing) effects
     row=E.object [("rendererValid",E.bool (SurfaceRenderer.decode (if kind=="validate" then value "frame" else C.frame next) |> Result.toMaybe |> (/=) Nothing)),("inputKind",E.string kind),("frame",C.frame next),("blocked",E.bool blocked),("unresolved",E.int (List.length state.unresolved)),("effectRequest",E.string (UInt64.string state.request)),("effectGeneration",E.string (UInt64.string state.generation)),("phase",E.string (case (C.desktop next).windows.shell.phase of
       Shell.Ready -> "Ready"
       Shell.Detached -> "Detached"
       _ -> "Other")),("wires",E.list identity wires)]
 in (next,row::rows)
