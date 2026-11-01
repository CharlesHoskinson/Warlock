port module StandaloneMvpReplay exposing (main)

{-| Source-route QA: direct Desktop transitions and the same DesktopPolicy
entry used by HttpMain. The harness supplies transport and receipts; it cannot
establish native, browser, accessibility or release behavior. -}
import Binding
import Catalog
import Desktop
import DesktopPolicy as Policy
import Json.Decode as D
import Json.Encode as E
import OutputController as Outputs
import Platform
import Shell
import Surface
import SurfaceController
import TaskbarShell
import UInt64

port incoming : (D.Value -> msg) -> Sub msg
port outgoing : E.Value -> Cmd msg

type alias Model = { desktop : Desktop.Model, policy : Policy.Model }
type Msg = Input D.Value
initial : Model
initial = {desktop=Desktop.initial,policy=Policy.initial}

effect : Desktop.Effect -> Maybe E.Value
effect value = case value of
    Desktop.Send raw -> Just raw
    Desktop.WindowEffect (Shell.Send raw) -> Just raw
    _ -> Nothing

report : Model -> List Desktop.Effect -> List Policy.Effect -> Cmd Msg
report model effects policyEffects =
    let shell=model.desktop.windows.shell
        controllerDesktop=SurfaceController.desktop (Outputs.controller model.policy.controller)
        packets=List.filterMap (\item -> case item of
            Policy.Publish raw -> Just raw
            _ -> Nothing) policyEffects
        one=UInt64.next UInt64.zero |> Maybe.withDefault UInt64.zero
    in outgoing (E.object
        [ ("shell",Shell.encode shell)
        , ("applicationOnly",E.bool shell.applicationOnly)
        , ("binding",shell.binding |> Maybe.map Binding.encode |> Maybe.withDefault E.null)
        , ("catalogIds",E.list E.string (model.desktop.applications |> Maybe.map (Catalog.entries >> List.map (.identity >> Catalog.id)) |> Maybe.withDefault []))
        , ("pendingCatalog",model.desktop.expected |> Maybe.map (UInt64.string >> E.string) |> Maybe.withDefault E.null)
        , ("open",E.bool model.desktop.open)
        , ("frame",Surface.packet one one model.desktop)
        , ("requests",E.list identity (List.filterMap effect effects))
        , ("policyApplicationOnly",E.bool controllerDesktop.windows.shell.applicationOnly)
        , ("policyFrame",Outputs.frame model.policy.controller)
        , ("policyPackets",E.list identity packets)
        ])

update : Msg -> Model -> (Model,Cmd Msg)
update (Input raw) model =
    let kind=D.decodeValue (D.field "kind" D.string) raw |> Result.withDefault ""
        value=D.decodeValue (D.field "value" D.value) raw |> Result.withDefault E.null
        apply message = Desktop.update message model.desktop
        (desktop,effects)=case kind of
            "native" -> apply (Desktop.Incoming value)
            "refresh" -> apply (Desktop.Window (TaskbarShell.Native Shell.Refresh))
            "supersede" -> apply (Desktop.Window (TaskbarShell.Native (Shell.SupersedeObservations True)))
            "reconnect" -> apply (Desktop.Window (TaskbarShell.Native Shell.Reconnect))
            "geometry" -> apply (Desktop.Window (TaskbarShell.Native Shell.GeometryAttach))
            "open" -> Desktop.capture model.desktop |> Maybe.map (\stamp -> apply (Desktop.OpenApplications stamp)) |> Maybe.withDefault (model.desktop,[])
            "reset" -> (Desktop.initial,[])
            _ -> (model.desktop,[])
        (policy,policyEffects)=if kind=="policy" then Policy.update (Policy.Incoming value) model.policy else if kind=="reset" then (Policy.initial,[]) else (model.policy,[])
        next={desktop=desktop,policy=policy}
    in (next,report next effects policyEffects)

main : Program () Model Msg
main = Platform.worker {init=\_ -> (initial,Cmd.none),update=update,subscriptions=\_ -> incoming Input}
