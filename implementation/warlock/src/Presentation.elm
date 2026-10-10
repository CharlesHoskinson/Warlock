module Presentation exposing (Model, initial, accept, current, dispatch, query, editQuery, localEdit)

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

query : String -> Model -> Maybe E.Value
query value (Model model) =
    if String.length value>(model.snapshot |> Maybe.map (\snapshot -> if SurfaceRenderer.mode snapshot=="files" then 512 else 256) |> Maybe.withDefault 256) || String.any (\c -> Char.toCode c<32 || Char.toCode c==127) value then Nothing else
    model.snapshot |> Maybe.andThen (\snapshot ->
        if not (List.member (SurfaceRenderer.mode snapshot) ["applications","files"]) || not (SurfaceRenderer.enabled True (SurfaceRenderer.fieldIdentity snapshot) snapshot) then Nothing else
        Just (E.object [("surfaceProtocol",E.int 2),("kind",E.string "surface-query"),("surface",E.string "popup"),("publication",E.string (UInt64.string (SurfaceRenderer.publication snapshot))),("lease",E.string (UInt64.string (SurfaceRenderer.lease snapshot))),("id",E.string (SurfaceRenderer.fieldIdentity snapshot)),("query",E.string value)]))

editQuery : D.Value -> Model -> Maybe (String,E.Value)
editQuery raw ((Model model) as currentModel) =
    let decoder = D.map5 (\version surface publication lease value -> {version=version,surface=surface,publication=publication,lease=lease,value=value}) (D.field "surfaceProtocol" D.int) (D.field "surface" D.string) (D.field "publication" UInt64.decoder) (D.field "lease" UInt64.decoder) (D.field "query" D.string)
    in case (D.decodeValue decoder raw,model.snapshot) of
        (Ok event,Just snapshot) ->
            if event.version/=2 || event.surface/="popup" || event.publication/=SurfaceRenderer.publication snapshot || event.lease/=SurfaceRenderer.lease snapshot || D.decodeValue (D.field "id" D.string) raw/=Ok (SurfaceRenderer.fieldIdentity snapshot) then Nothing else query event.value currentModel |> Maybe.map (\wire -> (event.value,wire))
        _ -> Nothing

-- Only Popup's own Html callback uses this path. Its DOM can still show the
-- preceding publication when Elm has accepted the next one. Retain that live
-- field edit within the same lease; external ports and button actions keep
-- their exact-publication admission. The rebased query cannot dispatch an app.
localEdit : D.Value -> Model -> Maybe E.Value
localEdit raw ((Model model) as currentModel) =
    let decoder = D.map7 (\version surface publication lease identity kind value -> {version=version,surface=surface,publication=publication,lease=lease,identity=identity,kind=kind,value=value})
            (D.field "surfaceProtocol" D.int) (D.field "surface" D.string) (D.field "publication" UInt64.decoder) (D.field "lease" UInt64.decoder) (D.field "id" D.string) (D.field "kind" D.string) (D.field "query" D.string)
    in case (D.decodeValue decoder raw,model.snapshot) of
        (Ok event,Just snapshot) ->
            if event.version/=2 || event.surface/="popup" || event.publication==UInt64.zero || UInt64.compare event.publication (SurfaceRenderer.publication snapshot)==GT || event.lease/=SurfaceRenderer.lease snapshot || event.identity/=SurfaceRenderer.fieldIdentity snapshot || not (List.member event.kind ["surface-query","surface-preedit","surface-composition-start","surface-composition-end"]) then Nothing
            else query event.value currentModel |> Maybe.andThen (\wire ->
                D.decodeValue (D.keyValuePairs D.value) wire |> Result.toMaybe |> Maybe.map (\fields -> E.object (List.map (\(name,value) -> (name,if name=="kind" then E.string event.kind else value)) fields)))
        _ -> Nothing
