port module TaskViewEscapeReplay exposing (main)
import Desktop
import Json.Decode as D
import Json.Encode as E
import OutputController as Outputs
import OutputRetirementReplay as Fixture
import Platform
import Shell
import SurfaceController as Controller
import UInt64
port outgoing : E.Value -> Cmd msg
field name model=D.decodeValue (D.at ["frame",name] D.string) (Outputs.frame model) |> Result.withDefault "0"
result=
 let ready=Fixture.base [("1",Fixture.left)]
     opened=Desktop.capture (Fixture.desktop ready) |> Maybe.map (\stamp -> Fixture.step (Outputs.Interaction (Desktop.OpenOverview stamp)) ready) |> Maybe.withDefault ready
     scope generation=E.object [("id",E.string "1"),("generation",E.string generation)]
     escape generation shown token extra=E.object ([("scope",scope generation),("publication",shown),("lease",token)]++extra)
     packet=escape "1" (E.string (field "publication" opened)) (E.string (field "lease" opened)) []
     (closed,commands)=Outputs.update (Outputs.Escape packet) opened
     rejected raw=let (next,effects)=Outputs.update (Outputs.Escape raw) opened in Outputs.frame next==Outputs.frame opened && List.isEmpty effects
     (duplicate,duplicateCommands)=Outputs.update (Outputs.Escape packet) closed
     mutations=commands |> List.filter (\effect -> case effect of
         Controller.DesktopEffect (Desktop.WindowEffect (Shell.Send wire)) -> D.decodeValue (D.field "kind" D.string) wire==Ok "window-effect"
         Controller.DesktopEffect (Desktop.Send wire) -> D.decodeValue (D.field "kind" D.string) wire |> Result.map (\kind -> List.member kind ["window-effect","application-launch","taskbar-pins-write"]) |> Result.withDefault False
         _ -> False)
     checks=[("CurrentOverviewEscapeDismissesWithoutNativeMutation",(Fixture.desktop opened).overview && not (Fixture.desktop closed).overview && List.isEmpty mutations),
         ("StaleEscapePublicationCannotDismiss",rejected (escape "1" (E.string "0") (E.string (field "lease" opened)) [])),
         ("StaleEscapeLeaseCannotDismiss",rejected (escape "1" (E.string (field "publication" opened)) (E.string "0") [])),
         ("ReplacedEscapeOwnerCannotDismiss",rejected (escape "2" (E.string (field "publication" opened)) (E.string (field "lease" opened)) [])),
         ("NumericEscapeCounterCannotDismiss",rejected (escape "1" (E.int 1) (E.string (field "lease" opened)) [])),
         ("UnexpectedEscapeFieldCannotDismiss",rejected (escape "1" (E.string (field "publication" opened)) (E.string (field "lease" opened)) [("id",E.string "control:close")])),
         ("DuplicateOldEscapeCannotRemintFocus",Outputs.frame duplicate==Outputs.frame closed && List.isEmpty duplicateCommands)]
 in E.object [("checks",E.object (List.map (Tuple.mapSecond E.bool) checks))]
main : Program () () Never
main=Platform.worker {init=\_->((),outgoing result),update=\_ state->(state,Cmd.none),subscriptions=\_->Sub.none}
