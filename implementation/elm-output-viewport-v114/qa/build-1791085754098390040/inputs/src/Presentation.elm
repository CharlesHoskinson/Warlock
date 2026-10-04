module Presentation exposing (Model, initial, accept, current, dispatch)

import Json.Decode as D
import Json.Encode as E
import SurfaceRenderer
import UInt64 exposing (Counter)

type Model = Model { last : Counter, lease : Counter, snapshot : Maybe SurfaceRenderer.Snapshot }

initial : Model
initial = Model {last=UInt64.zero,lease=UInt64.zero,snapshot=Nothing}

current : Model -> Maybe SurfaceRenderer.Snapshot
current (Model model) = model.snapshot

accept : D.Value -> Model -> Model
accept raw ((Model model) as prior) =
    case SurfaceRenderer.decode raw of
        Err _ -> Model {model | snapshot=Nothing}
        Ok snapshot ->
            if UInt64.compare (SurfaceRenderer.publication snapshot) model.last/=GT || UInt64.compare (SurfaceRenderer.lease snapshot) model.lease==LT then prior
            else Model {last=SurfaceRenderer.publication snapshot,lease=SurfaceRenderer.lease snapshot,snapshot=Just snapshot}

dispatch : Bool -> D.Value -> Model -> Maybe E.Value
dispatch popup raw (Model model) =
    let
        decoder = D.keyValuePairs D.value |> D.andThen (\fields ->
            if List.sort (List.map Tuple.first fields)/=["id","kind","lease","publication","surface","surfaceProtocol"] then D.fail "Callback fields" else
                D.map6 (\version kind publication lease role identity -> {version=version,kind=kind,publication=publication,lease=lease,role=role,identity=identity}) (D.field "surfaceProtocol" D.int) (D.field "kind" D.string) (D.field "publication" UInt64.decoder) (D.field "lease" UInt64.decoder) (D.field "surface" D.string) (D.field "id" D.string))
    in case (model.snapshot,D.decodeValue decoder raw) of
        (Just snapshot,Ok event) ->
            if event.version==2 && event.kind=="surface-action" && event.publication==SurfaceRenderer.publication snapshot && event.lease==SurfaceRenderer.lease snapshot && event.role==(if popup then "popup" else "bar") then SurfaceRenderer.action popup event.identity snapshot else Nothing
        _ -> Nothing
