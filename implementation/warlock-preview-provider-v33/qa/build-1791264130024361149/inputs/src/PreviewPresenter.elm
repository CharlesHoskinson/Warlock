module PreviewPresenter exposing (Model, initial, present, receive, image, observe)

import Dict exposing (Dict)
import Html exposing (Html, text)
import Json.Decode as D
import Json.Encode as E
import PreviewLifecycle as Preview
import NativePreviewSource
import SurfaceRenderer
import UInt64 exposing (Counter)

type alias Stamp = { publication : Counter, lease : Counter }
type alias Entry = { model : Preview.Model, binding : String, source : Maybe NativePreviewSource.Source, stamp : Maybe Stamp, title : String, application : String }
type Model = Model (Dict String Entry)
type Input = Seed Stamp String Preview.Scope D.Value String String String (Maybe NativePreviewSource.Source) | Event String Preview.Event D.Value
type alias Output = { identity : String, commands : List Preview.Command }

initial : Model
initial = Model Dict.empty

strict : List String -> D.Decoder a -> D.Decoder a
strict fields decoder = D.keyValuePairs D.value |> D.andThen (\pairs -> if List.sort (List.map Tuple.first pairs) == List.sort fields then decoder else D.fail "Preview presenter fields")

positive : D.Decoder Counter
positive = UInt64.decoder |> D.andThen (\value -> if value /= UInt64.zero then D.succeed value else D.fail "Positive preview presentation identity")

bounded : D.Decoder String
bounded = D.string |> D.andThen (\value -> if String.length value <= 1024 && not (String.any (\c -> Char.toCode c < 32) value) then D.succeed value else D.fail "Preview label")

binding : D.Decoder String
binding = D.map3 (\a b c -> String.join ":" (List.map UInt64.string [a,b,c])) (D.field "lifetime" positive) (D.field "session" positive) (D.field "frontend" positive)

input : D.Decoder Input
input = D.field "kind" D.string |> D.andThen (\kind -> case kind of
    "seed" -> strict ["kind","publication","lease","identity","scope","title","application"]
        (D.map7 (\publication lease identity raw title application owner -> {publication=publication,lease=lease,identity=identity,raw=raw,title=title,application=application,owner=owner})
            (D.field "publication" positive) (D.field "lease" positive) (D.field "identity" bounded) (D.field "scope" D.value) (D.field "title" bounded) (D.field "application" bounded) (D.at ["scope","binding"] binding)
            |> D.andThen (\seed ->
                case (D.decodeValue Preview.scopeDecoder seed.raw,D.decodeValue (D.at ["context","incarnation"] positive) seed.raw) of
                    (Ok scope,Ok incarnation) -> if seed.identity == "family:" ++ UInt64.string incarnation then D.succeed (Seed {publication=seed.publication,lease=seed.lease} seed.identity scope seed.raw seed.title seed.application seed.owner Nothing) else D.fail "Preview control incarnation mismatch"
                    _ -> D.fail "Native preview scope"))
    "source-seed" -> strict ["kind","publication","lease","identity","source","title","application"]
        (D.map6 (\publication lease identity raw title application -> {publication=publication,lease=lease,identity=identity,raw=raw,title=title,application=application})
            (D.field "publication" positive) (D.field "lease" positive) (D.field "identity" bounded) (D.field "source" D.value) (D.field "title" bounded) (D.field "application" bounded)
            |> D.andThen (\seed ->
                case (D.decodeValue NativePreviewSource.decoder seed.raw,D.decodeValue (D.map3 (\native incarnation owner -> (native,incarnation,owner)) (D.field "scope" D.value) (D.at ["scope","context","incarnation"] positive) (D.at ["scope","binding"] binding)) seed.raw) of
                    (Ok observation,Ok (native,incarnation,owner)) ->
                        if seed.identity == "family:" ++ UInt64.string incarnation then
                            D.succeed (Seed {publication=seed.publication,lease=seed.lease} seed.identity (NativePreviewSource.scope observation) native seed.title seed.application owner (Just (NativePreviewSource.source observation)))
                        else D.fail "Typed source control incarnation mismatch"
                    _ -> D.fail "Typed native preview source"))
    "event" -> strict ["kind","identity","event"] (D.map3 Event (D.field "identity" bounded) (D.field "event" Preview.eventDecoder) (D.field "event" D.value))
    _ -> D.fail "Preview presenter kind")

-- Observe/Attach may retarget a standalone lifecycle. A picker entry has a
-- fixed native incarnation and may never inherit another control's subject.
eventOwns : String -> D.Value -> Bool
eventOwns identity wire =
    case D.decodeValue (D.field "kind" D.string) wire of
        Ok "observe" -> D.decodeValue (D.at ["scope","context","incarnation"] positive) wire |> Result.map (\incarnation -> identity == "family:" ++ UInt64.string incarnation) |> Result.withDefault False
        Ok "attach" -> D.decodeValue (D.at ["scope","context","incarnation"] positive) wire |> Result.map (\incarnation -> identity == "family:" ++ UInt64.string incarnation) |> Result.withDefault False
        _ -> True

familyFrameOwns : Maybe NativePreviewSource.Source -> D.Value -> Bool
familyFrameOwns sourceKind wire =
    if sourceKind /= Just NativePreviewSource.StyleCroppedFamily then True
    else
        let shape = D.map2 (\fidelity coverage -> fidelity == "family" && List.sort coverage == [ "client", "decoration", "modal", "popup" ]) (D.field "fidelity" D.string) (D.field "coverage" (D.list D.string))
            admit path = D.decodeValue (D.at path shape) wire |> Result.withDefault False
        in case D.decodeValue (D.field "kind" D.string) wire of
            Ok "offer" -> admit [ "frame" ]
            Ok "fence" -> admit [ "frame" ]
            Ok "expired" -> admit [ "frame" ]
            Ok "receipt" -> case D.decodeValue (D.at [ "event", "kind" ] D.string) wire of
                Ok "released" -> admit [ "event", "frame" ]
                _ -> True
            _ -> True

same : Stamp -> SurfaceRenderer.Snapshot -> Bool
same stamp snapshot = stamp.publication == SurfaceRenderer.publication snapshot && stamp.lease == SurfaceRenderer.lease snapshot && SurfaceRenderer.mode snapshot == "picker"

encode : List Output -> E.Value
encode outputs = E.list (\out -> E.object [("identity",E.string out.identity),("commands",Preview.encodeCommands out.commands)]) (List.filter (\out -> not (List.isEmpty out.commands)) outputs)

-- Closing the UI cancels demand but keeps every lifecycle, request counter and
-- pending receipt. Late cleanup events continue to reach the retained owner.
present : Maybe SurfaceRenderer.Snapshot -> Model -> (Model,E.Value)
present snapshot (Model entries) =
    let advance identity entry (next,outputs) =
            let current = entry.stamp |> Maybe.map (\stamp -> snapshot |> Maybe.map (\shown -> same stamp shown && SurfaceRenderer.enabled True identity shown) |> Maybe.withDefault False) |> Maybe.withDefault False
            in if current || entry.stamp == Nothing then (Dict.insert identity entry next,outputs)
               else
                let (closed,commands) = D.decodeValue Preview.eventDecoder (E.object [("kind",E.string "close")]) |> Result.map (\event -> Preview.update event entry.model) |> Result.withDefault (entry.model,[])
                in (Dict.insert identity {entry | model=closed,stamp=Nothing} next,outputs ++ [{identity=identity,commands=commands}])
        (collected,emissions) = Dict.foldl advance (Dict.empty,[]) entries
    in (Model collected,encode emissions)

receive : Maybe SurfaceRenderer.Snapshot -> D.Value -> Model -> (Model,E.Value)
receive snapshot raw ((Model entries) as prior) =
    case D.decodeValue input raw of
        Err _ -> (prior,encode [])
        Ok (Event identity event wire) ->
            case Dict.get identity entries of
                Nothing -> (prior,encode [])
                Just entry ->
                    if not (eventOwns identity wire && familyFrameOwns entry.source wire) then (prior,encode [])
                    else
                        let (next,commands) = Preview.update event entry.model
                            owner = D.decodeValue (D.at ["scope","binding"] binding) (Preview.observe next) |> Result.withDefault entry.binding
                        in (Model (Dict.insert identity {entry | model=next,binding=owner} entries),encode [{identity=identity,commands=commands}])
        Ok (Seed stamp identity scope native title application owner sourceKind) ->
            let allowed = snapshot |> Maybe.map (\shown -> same stamp shown && SurfaceRenderer.enabled True identity shown) |> Maybe.withDefault False
                old = Dict.get identity entries
                matching = old |> Maybe.map (\entry -> entry.binding == owner && entry.source == sourceKind) |> Maybe.withDefault True
                observeEvent = D.decodeValue Preview.eventDecoder (E.object [("kind",E.string "observe"),("scope",native)])
                openEvent = D.decodeValue Preview.eventDecoder (E.object [("kind",E.string "open")])
            in if not allowed || not matching || (old == Nothing && Dict.size entries >= 2051) then (prior,encode [])
               else
                let base = old |> Maybe.map .model |> Maybe.withDefault (Preview.init scope)
                    (observed,first) = observeEvent |> Result.map (\event -> Preview.update event base) |> Result.withDefault (base,[])
                    (opened,second) = openEvent |> Result.map (\event -> Preview.update event observed) |> Result.withDefault (observed,[])
                    entry = {model=opened,binding=owner,source=sourceKind,stamp=Just stamp,title=title,application=application}
                in (Model (Dict.insert identity entry entries),encode [{identity=identity,commands=first ++ second}])

image : SurfaceRenderer.Snapshot -> String -> Model -> Html msg
image snapshot identity (Model entries) =
    Dict.get identity entries |> Maybe.andThen (\entry -> entry.stamp |> Maybe.andThen (\stamp -> if same stamp snapshot then Just (Preview.inlineView {title=entry.title,application=entry.application,icon=Nothing} entry.model) else Nothing)) |> Maybe.withDefault (text "")

observe : Model -> E.Value
observe (Model entries) = E.list (\(identity,entry) -> E.object [("identity",E.string identity),("active",E.bool (entry.stamp /= Nothing)),("model",Preview.observe entry.model)]) (Dict.toList entries)
