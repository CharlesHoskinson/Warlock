module Presentation exposing (Model, initial, accept, current, dispatch)

import Json.Decode as D
import Json.Encode as E
import CapturedAction
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
    case (model.snapshot,CapturedAction.decode raw) of
        (Just snapshot,Ok event) ->
            if CapturedAction.publication event==SurfaceRenderer.publication snapshot && CapturedAction.lease event==SurfaceRenderer.lease snapshot && CapturedAction.surface event==(if popup then "popup" else "bar") && SurfaceRenderer.enabled popup (CapturedAction.identity event) snapshot then Just (CapturedAction.encode event) else Nothing
        _ -> Nothing
