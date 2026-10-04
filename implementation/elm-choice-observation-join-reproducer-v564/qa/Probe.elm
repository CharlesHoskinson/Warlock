port module Probe exposing (main)
import Desktop as Desktop
import Json.Decode as D
import Json.Encode as E
import Platform
import Shell
import TaskbarShell
import UInt64
port incoming : (D.Value -> msg) -> Sub msg
port outgoing : E.Value -> Cmd msg
type Msg = Run D.Value
number text = D.decodeValue UInt64.decoder (E.string text) |> Result.withDefault UInt64.zero
commands effects = effects |> List.filterMap (\effect -> case effect of
 Desktop.WindowEffect (Shell.Send wire) -> Just wire
 _ -> Nothing)
state model = E.object [("choicePending",E.bool (model.choice/=Nothing)),("available",E.bool (Shell.available model.windows.shell)),("projectionPending",E.bool (model.windows.shell.expected/=Nothing)),("geometryPending",E.bool (model.windows.shell.geometryExpected/=Nothing))]
apply raw model = Desktop.update (Desktop.Incoming raw) model
main : Program () () Msg
main = Platform.worker {init=\_ -> ((),Cmd.none),subscriptions=\_ -> incoming Run,update=\(Run raw) _ ->
 let seeds=D.decodeValue (D.field "seed" (D.list D.value)) raw |> Result.withDefault []
     projection=D.decodeValue (D.field "projection" D.value) raw |> Result.withDefault E.null
     geometry=D.decodeValue (D.field "geometry" D.value) raw |> Result.withDefault E.null
     seed=List.foldl (\frame model -> apply frame model |> Tuple.first) Desktop.initial seeds
 in case Shell.capture seed.windows.shell of
  Nothing -> ((),outgoing (E.object [("error",E.string "no captured scope")]))
  Just scope ->
   let (opened,_)=Desktop.update (Desktop.Window (TaskbarShell.Primary scope "application:GTK Application")) seed
   in case opened.windows.picker of
    Nothing -> ((),outgoing (E.object [("error",E.string "no actual picker")]))
    Just picker ->
     let (chosen,requests)=Desktop.update (Desktop.Window (TaskbarShell.Choose picker.scope picker.generation (number "2"))) opened
         (afterProjection,pEffects)=apply projection chosen
         (afterGeometry,gEffects)=apply geometry afterProjection
     in ((),outgoing (E.object [("chosen",state chosen),("afterProjection",state afterProjection),("afterGeometry",state afterGeometry),("requests",E.list identity (commands requests)),("projectionCommands",E.list identity (commands pEffects)),("geometryCommands",E.list identity (commands gEffects))]))}
