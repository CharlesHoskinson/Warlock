port module ApplicationAvailabilityReplay exposing (main)

import Binding
import Catalog
import Desktop
import Json.Decode as D
import Json.Encode as E
import Launch
import Platform
import Shell
import Surface
import TaskbarShell
import UInt64

port incoming : (D.Value -> msg) -> Sub msg
port outgoing : E.Value -> Cmd msg

type Msg = Input D.Value
one : UInt64.Counter
one = UInt64.next UInt64.zero |> Maybe.withDefault UInt64.zero

request : Desktop.Effect -> Maybe E.Value
request item =
    case item of
        Desktop.Send raw -> Just raw
        Desktop.WindowEffect (Shell.Send raw) -> Just raw
        _ -> Nothing

report : Desktop.Model -> Bool -> List Desktop.Effect -> E.Value
report model resolved effects =
    let shell = model.windows.shell
    in E.object
        [ ("shell", Shell.encode shell)
        , ("applicationOnly", E.bool shell.applicationOnly)
        , ("available", E.bool (Shell.available shell))
        , ("transportRefused", E.bool shell.transportRefused)
        , ("binding", shell.binding |> Maybe.map Binding.encode |> Maybe.withDefault E.null)
        , ("query", E.string model.query)
        , ("open", E.bool model.open)
        , ("catalogIds", model.applications |> Maybe.map (Catalog.entries >> List.map (.identity >> Catalog.id)) |> Maybe.withDefault [] |> E.list E.string)
        , ("pendingCatalog", model.expected |> Maybe.map (UInt64.string >> E.string) |> Maybe.withDefault E.null)
        , ("pointerObservationAbsent", E.bool (model.pointer.observation == Nothing))
        , ("launchPending", E.bool (Launch.pending model.launch /= Nothing))
        , ("launchUnknown", E.bool (Launch.uncertain model.launch /= Nothing))
        , ("launchStatus", E.string (Launch.status model.launch))
        , ("selectionExists", E.bool (Launch.select "sample.desktop" model.launch /= Nothing))
        , ("resolved", E.bool resolved)
        , ("requests", E.list identity (List.filterMap request effects))
        , ("frame", Surface.packet one one model)
        ]

update : Msg -> Desktop.Model -> ( Desktop.Model, Cmd Msg )
update (Input raw) model =
    let kind = D.decodeValue (D.field "kind" D.string) raw |> Result.withDefault ""
        value = D.decodeValue (D.field "value" D.value) raw |> Result.withDefault E.null
        resolved = if kind == "surface" then Surface.resolve one one value model else Nothing
        message = case kind of
            "native" -> Just (Desktop.Incoming value)
            "open" -> Desktop.capture model |> Maybe.map Desktop.OpenApplications
            "search" -> Desktop.capture model |> Maybe.map (\stamp -> Desktop.SearchQuery stamp (D.decodeValue D.string value |> Result.withDefault ""))
            "surface" -> resolved
            "direct-start" -> Launch.select "sample.desktop" model.launch |> Maybe.map Desktop.Start
            "deadline" -> Launch.pending model.launch |> Maybe.map Desktop.Deadline
            "transport-refused" -> Just (Desktop.Window (TaskbarShell.Native (Shell.RegistrationRefused [] [])))
            "refresh" -> Just (Desktop.Window (TaskbarShell.Native Shell.Refresh))
            "reconnect" -> Just (Desktop.Window (TaskbarShell.Native Shell.Reconnect))
            _ -> Nothing
        (next,effects) = if kind == "reset" then (Desktop.initial,[]) else message |> Maybe.map (\msg -> Desktop.update msg model) |> Maybe.withDefault (model,[])
    in (next,outgoing (report next (resolved /= Nothing) effects))

main : Program () Desktop.Model Msg
main = Platform.worker {init=\_ -> (Desktop.initial,Cmd.none),update=update,subscriptions=\_ -> incoming Input}
