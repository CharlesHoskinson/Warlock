module NativePreviewVisual exposing (Projection, decoder, encode, view, action)

import Dict
import Html exposing (Html, text)
import Json.Decode as D
import Json.Encode as E
import NativePreviewRealm as Realm
import PreviewVisual as Visual
import SurfaceRenderer
import UInt64

-- A validated visual projection, never a preview/window lifecycle model.
type Projection = Projection Realm.Domain (Maybe SurfaceRenderer.Snapshot) (List (String,Visual.Visual))

strict : List String -> D.Decoder a -> D.Decoder a
strict fields parser = D.keyValuePairs D.value |> D.andThen (\pairs -> if List.sort (List.map Tuple.first pairs)==List.sort fields then parser else D.fail "Closed native visual fields")

decoder : Realm.Domain -> D.Decoder Projection
decoder authority =
    let surface = D.nullable D.value |> D.andThen (\raw -> case raw of
            Nothing -> D.succeed Nothing
            Just value -> case SurfaceRenderer.decode value of
                Ok snapshot -> D.succeed (Just snapshot)
                Err message -> D.fail message)
        rows = D.list D.value |> D.andThen (\values -> if List.length values>2051 then D.fail "Original popup capacity" else D.list (strict ["identity","visual"] (D.map2 Tuple.pair (D.field "identity" D.string) (D.field "visual" Visual.decoder))))
    in strict ["visualProtocol","kind","binding","receiverEpoch","surface","previews"]
        (D.map5 (\protocol kind domain snapshot previews -> (protocol,kind,(domain,snapshot,previews)))
            (D.field "visualProtocol" D.int) (D.field "kind" D.string) Realm.domainDecoder
            (D.field "surface" surface) (D.field "previews" rows))
        |> D.andThen (\(protocol,kind,(domain,snapshot,previews)) ->
            let identities = snapshot |> Maybe.map (SurfaceRenderer.identities True) |> Maybe.withDefault []
            in if protocol/=1 || kind/="native-preview-visual" || not (Realm.same domain authority) || List.map Tuple.first previews/=identities then D.fail "Exact original domain and ordered popup projection required"
               else D.succeed (Projection domain snapshot previews))

encode : Projection -> E.Value
encode (Projection domain snapshot previews) = E.object [("visualProtocol",E.int 1),("kind",E.string "native-preview-visual"),("binding",Realm.bindingValue domain),("receiverEpoch",E.string (UInt64.string domain.receiverEpoch)),("surface",snapshot |> Maybe.map SurfaceRenderer.encode |> Maybe.withDefault E.null),("previews",E.list (\(name,visual) -> E.object [("identity",E.string name),("visual",Visual.encode visual)]) previews)]

view : (E.Value -> msg) -> Projection -> Html msg
view send (Projection _ snapshot previews) =
    let visuals = Dict.fromList previews
    in snapshot |> Maybe.map (SurfaceRenderer.viewWithPreview (\name -> Dict.get name visuals |> Maybe.map Visual.inlineView |> Maybe.withDefault (text "")) True send) |> Maybe.withDefault (text "")

action : String -> Projection -> Maybe E.Value
action identity (Projection _ snapshot _) = snapshot |> Maybe.andThen (SurfaceRenderer.action True identity)
