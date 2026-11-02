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
import Launch
import NativePointerFixture
import OutputController as Outputs
import Platform
import Shell
import Surface
import SurfaceController
import TaskbarShell
import UInt64

port incoming : (D.Value -> msg) -> Sub msg
port outgoing : E.Value -> Cmd msg

one : UInt64.Counter
one = UInt64.next UInt64.zero |> Maybe.withDefault UInt64.zero

type alias Model = { desktop : Desktop.Model, policy : Policy.Model, publication : UInt64.Counter }
type Msg = Input D.Value
initial : Model
initial = {desktop=Desktop.initial,policy=Policy.initial,publication=one}

effect : Desktop.Effect -> Maybe E.Value
effect value = case value of
    Desktop.Send raw -> Just raw
    Desktop.WindowEffect (Shell.Send raw) -> Just raw
    _ -> Nothing

report : Model -> Bool -> List Desktop.Effect -> List Policy.Effect -> Cmd Msg
report model resolved effects policyEffects =
    let shell=model.desktop.windows.shell
        controllerDesktop=SurfaceController.desktop (Outputs.controller model.policy.controller)
        packets=List.filterMap (\item -> case item of
            Policy.Publish raw -> Just raw
            _ -> Nothing) policyEffects
    in outgoing (E.object
        [ ("shell",Shell.encode shell)
        , ("applicationOnly",E.bool shell.applicationOnly)
        , ("binding",shell.binding |> Maybe.map Binding.encode |> Maybe.withDefault E.null)
        , ("catalogIds",E.list E.string (model.desktop.applications |> Maybe.map (Catalog.entries >> List.map (.identity >> Catalog.id)) |> Maybe.withDefault []))
        , ("pendingCatalog",model.desktop.expected |> Maybe.map (UInt64.string >> E.string) |> Maybe.withDefault E.null)
        , ("open",E.bool model.desktop.open)
        , ("query",E.string model.desktop.query)
        , ("publication",E.string (UInt64.string model.publication))
        , ("resolved",E.bool resolved)
        , ("launchPending",E.bool (Launch.pending model.desktop.launch/=Nothing))
        , ("launchUncertain",E.bool (Launch.uncertain model.desktop.launch/=Nothing))
        , ("launchStatus",E.string (Launch.status model.desktop.launch))
        , ("jumpEntry",model.desktop.jumpEntry |> Maybe.map E.string |> Maybe.withDefault E.null)
        , ("jumpOpening",E.bool model.desktop.jumpOpening)
        , ("jumpExpected",model.desktop.jumpExpected |> Maybe.map (UInt64.string >> E.string) |> Maybe.withDefault E.null)
        , ("windowChoiceReserved",E.bool (model.desktop.choice/=Nothing))
        , ("frame",Surface.packet model.publication one model.desktop)
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
        resolvedMsg=if kind=="surface-action" then Surface.resolve model.publication one value model.desktop else Nothing
        (desktop,effects)=case kind of
            "native" -> apply (Desktop.Incoming value)
            "refresh" -> apply (Desktop.Window (TaskbarShell.Native Shell.Refresh))
            "supersede" -> apply (Desktop.Window (TaskbarShell.Native (Shell.SupersedeObservations True)))
            "reconnect" -> apply (Desktop.Window (TaskbarShell.Native Shell.Reconnect))
            "geometry" -> apply (Desktop.Window (TaskbarShell.Native Shell.GeometryAttach))
            "pointer-ready" -> (NativePointerFixture.ready model.desktop,[])
            "open" -> Desktop.capture model.desktop |> Maybe.map (\stamp -> apply (Desktop.OpenApplications stamp)) |> Maybe.withDefault (model.desktop,[])
            "search" -> Desktop.capture model.desktop |> Maybe.map (\stamp -> apply (Desktop.SearchQuery stamp (D.decodeValue D.string value |> Result.withDefault ""))) |> Maybe.withDefault (model.desktop,[])
            "pin" -> Desktop.capture model.desktop |> Maybe.map (\stamp -> apply (Desktop.TogglePin stamp (D.decodeValue D.string value |> Result.withDefault ""))) |> Maybe.withDefault (model.desktop,[])
            "surface-action" ->
                resolvedMsg |> Maybe.map apply |> Maybe.withDefault (model.desktop,[])
            "reset" -> (Desktop.initial,[])
            _ -> (model.desktop,[])
        publication=if kind=="reset" then one else if kind=="advance-publication" then UInt64.next model.publication |> Maybe.withDefault model.publication else model.publication
        (policy,policyEffects)=if kind=="policy" then Policy.update (Policy.Incoming value) model.policy else if kind=="reset" then (Policy.initial,[]) else (model.policy,[])
        next={desktop=desktop,policy=policy,publication=publication}
    in (next,report next (resolvedMsg/=Nothing) effects policyEffects)

main : Program () Model Msg
main = Platform.worker {init=\_ -> (initial,Cmd.none),update=update,subscriptions=\_ -> incoming Input}
