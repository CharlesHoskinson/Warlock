module ReconciliationTracking exposing (Model, Slot, empty, unknown, announce, requested, observed, release, legacy, reset)

import Binding exposing (Binding)
import Effects
import Json.Decode as D
import ReconciliationFrame as R
import Shell
import UInt64 exposing (Counter)

type alias Accepted = {request : Counter, context : R.Context}
type alias Slot = {record : R.Record, proof : Maybe R.Proof, actionRequest : Maybe Counter, geometryRequest : Maybe Counter, action : Maybe Accepted, geometry : Maybe Accepted, released : Bool}
type alias Model = {slots : List Slot, legacy : List {intent : Effects.Intent, protocol : Int}}
empty : Model
empty = {slots=[],legacy=[]}
same a b = a.binding==b.binding && a.intent==b.intent && a.effectProtocol==b.effectProtocol
reset model = {model|slots=List.map (\slot -> {slot|proof=Nothing,actionRequest=Nothing,geometryRequest=Nothing,action=Nothing,geometry=Nothing}) model.slots}

unknown : Binding -> D.Value -> Model -> Result String (Model,R.Record)
unknown current raw model =
    R.decodeUnknown current raw |> Result.andThen (\frame -> case frame of
        R.ReservationUnknown _ record ->
            case List.filter (\slot -> same slot.record record) model.slots |> List.head of
                Just slot -> if slot.released then Err "Historical reservation already released" else Ok (model,record)
                Nothing -> if List.length model.slots>=64 then Err "Historical reservation capacity" else
                    Ok ({model|slots={record=record,proof=Nothing,actionRequest=Nothing,geometryRequest=Nothing,action=Nothing,geometry=Nothing,released=False}::model.slots},record)
        _ -> Err "Expected Unknown")

announce : Binding -> D.Value -> Model -> Result String Model
announce current raw model =
    D.decodeValue R.proofDecoder raw |> Result.mapError D.errorToString |> Result.andThen (\proof ->
        let eligible slot = not slot.released && slot.record.binding==proof.queriedBinding && Binding.sameLifetime slot.record.intent.context.lifetime current
            anotherActiveScope=List.any (\slot -> not slot.released && (slot.proof |> Maybe.map (\active -> active.queriedBinding/=proof.queriedBinding) |> Maybe.withDefault False)) model.slots
            newer slot = slot.proof |> Maybe.map (\old -> UInt64.compare proof.sequence old.sequence==GT) |> Maybe.withDefault True
        in if anotherActiveScope || proof.binding/=current || proof.queriedBinding==current || not (List.any eligible model.slots) || not (List.all (\slot -> not (eligible slot) || newer slot) model.slots) then Err "Uncorrelated proof announcement" else
            Ok {model|slots=List.map (\slot -> if eligible slot then {slot|proof=Just proof,actionRequest=Nothing,geometryRequest=Nothing,action=Nothing,geometry=Nothing} else slot) model.slots})

requested : String -> Counter -> Model -> Model
requested kind request model =
    {model|slots=List.map (\slot -> if slot.released || slot.proof==Nothing then slot else
        if kind=="projection-request" then {slot|actionRequest=Just request}
        else if kind=="geometry-facts-request" then {slot|geometryRequest=Just request} else slot) model.slots}

observed : D.Value -> Shell.Model -> Shell.Model -> Model -> Model
observed raw before after model =
    case D.decodeValue (D.map2 Tuple.pair (D.field "kind" D.string) (D.field "requestId" UInt64.decoder)) raw of
        Err _ -> model
        Ok (kind,request) ->
            let actionContext=D.decodeValue (D.field "context" R.contextDecoder) raw |> Result.toMaybe
                actionAccepted = kind=="action-projection" && before.expected==Just request && after.expected/=Just request && actionContext/=Nothing && (after.effects.observed |> Maybe.map .context)==actionContext
                geometryAccepted = kind=="geometry-facts" && before.geometryExpected==Just request && after.geometryExpected/=Just request && (after.geometry |> Maybe.map .request)==Just request
                geometryContext=after.geometry |> Maybe.map .context
            in {model|slots=List.map (\slot -> if slot.released || slot.proof==Nothing then slot else
                if actionAccepted && slot.actionRequest==Just request then {slot|action=Maybe.map (\context -> {request=request,context=context}) actionContext}
                else if geometryAccepted && slot.geometryRequest==Just request then {slot|geometry=Maybe.map (\context -> {request=request,context=context}) geometryContext} else slot) model.slots}

legacy : D.Value -> Shell.Model -> Model -> Model
legacy raw shell model =
    if D.decodeValue (D.field "kind" D.string) raw/=Ok "host-uncertain" || shell.phase/=Shell.Reconciling || (D.decodeValue (D.field "binding" Binding.decoder) raw |> Result.toMaybe)/=shell.binding || D.decodeValue (D.field "protocolVersion" D.int) raw/=Ok 3 then model else
        case D.decodeValue (D.field "intent" Effects.intentDecoder) raw of
            Err _ -> model
            Ok intent ->
                let protocol=D.decodeValue (D.field "effectProtocol" D.int) raw |> Result.withDefault 1
                    entry={intent=intent,protocol=protocol}
                in if List.member entry model.legacy || List.length model.legacy>=64 || not (List.any (\t -> t.intent==intent && t.effectProtocol==protocol && t.status==Effects.Unknown) shell.effects.unresolved) then model else {model|legacy=entry::model.legacy}

release : Binding -> D.Value -> Model -> Result String (Model,R.Record)
release current raw model =
    D.decodeValue (D.field "record" R.recordDecoder) raw |> Result.mapError D.errorToString |> Result.andThen (\record ->
        if List.any (\entry -> entry.intent==record.intent && entry.protocol==record.effectProtocol) model.legacy then Err "Legacy origin remains unsupported" else
        case List.filter (\slot -> not slot.released && same slot.record record) model.slots |> List.head of
            Nothing -> Err "No stored Unknown reservation"
            Just slot -> case (slot.proof,slot.action,slot.geometry) of
                (Just proof,Just action,Just geometry) ->
                    R.decodeReleased {currentBinding=current,record=slot.record,proofRequestId=proof.requestId,actionRequestId=action.request,geometryRequestId=geometry.request,actionContext=action.context,geometryContext=geometry.context} raw |> Result.andThen (\frame -> case frame of
                        R.ReservationReleased _ _ accepted -> if accepted.proof/=proof then Err "Announced proof changed" else
                            Ok ({model|slots=List.map (\entry -> if same entry.record record then {entry|released=True} else entry) model.slots},record)
                        _ -> Err "Expected released frame")
                _ -> Err "Proof and both accepted observations required")
