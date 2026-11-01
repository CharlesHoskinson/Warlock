module OverviewRecovery exposing (Model, Origin, initial, begin, issue, cancelChoice, observe, retainedOrigin)

import Binding
import Effects
import UInt64 exposing (Counter)

-- UI presentation context only. This model emits no native operation or retry.
type alias Origin = { binding : Binding.Binding, root : Counter, workspace : Maybe String }
type Model = Idle | Choosing Origin Counter | Issued Origin Effects.Intent | Returning Origin Effects.Intent

initial : Model
initial = Idle

begin : Origin -> Counter -> Model
begin = Choosing

issue : Counter -> Maybe (Binding.Binding, Effects.Intent) -> Model -> Model
issue read sent model =
    case model of
        Choosing origin expected ->
            if read /= expected then model else
            case sent of
                Just (binding,intent) ->
                    if binding==origin.binding && intent.incarnation==origin.root && List.member intent.operation [Effects.Activate,Effects.Restore] then Issued origin intent else Idle
                Nothing -> Idle
        _ -> model

cancelChoice : Counter -> Model -> Model
cancelChoice read model = case model of
    Choosing _ expected -> if read==expected then Idle else model
    _ -> model

observe : Maybe Binding.Binding -> Maybe Effects.Transaction -> Bool -> Bool -> Model -> (Model, Maybe Origin)
observe authority transaction occupied ready model =
    let origin = case model of
            Idle -> Nothing
            Choosing owner _ -> Just owner
            Issued owner _ -> Just owner
            Returning owner _ -> Just owner
        matched = case (model,transaction) of
            (Issued owner intent,Just outcome) ->
                if outcome.intent/=intent then model else
                case outcome.status of
                    Effects.Refused -> Returning owner intent
                    Effects.Committed -> Idle
                    Effects.Cancelled -> Idle
                    _ -> model
            _ -> model
    in if occupied || (origin |> Maybe.map (\owner -> authority/=Just owner.binding) |> Maybe.withDefault False) then (Idle,Nothing) else
        case matched of
            Returning owner intent ->
                case transaction of
                    Just current ->
                        if current.intent/=intent || current.status/=Effects.Refused then (Idle,Nothing)
                        else if ready then (Idle,Just owner) else (matched,Nothing)
                    Nothing -> (Idle,Nothing)
            _ -> (matched,Nothing)

retainedOrigin : Maybe Binding.Binding -> Maybe Effects.Transaction -> Model -> Maybe Origin
retainedOrigin authority transaction model =
    case (model,transaction) of
        (Issued origin intent,Just current) ->
            if authority==Just origin.binding && current.intent==intent && List.member current.status [Effects.Pending,Effects.Unknown] then Just origin else Nothing
        (Returning origin intent,Just current) ->
            if authority==Just origin.binding && current.intent==intent && current.status==Effects.Refused then Just origin else Nothing
        _ -> Nothing
