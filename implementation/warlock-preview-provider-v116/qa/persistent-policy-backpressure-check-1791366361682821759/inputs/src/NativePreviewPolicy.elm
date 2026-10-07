port module NativePreviewPolicy exposing (main)
import Json.Decode as D
import Json.Encode as E
import Platform
import Presentation
import RetainedPreviewPresenter as Preview
import NativePreviewRealm as Realm
port incoming : (D.Value -> msg) -> Sub msg
port outgoing : E.Value -> Cmd msg
type Msg = Run D.Value
type alias Model = { shown : Presentation.Model, previews : Preview.Model }
main : Program () Model Msg
main = Platform.worker {init=\_ -> ({shown=Presentation.initial,previews=Preview.initial},Cmd.none),subscriptions=\_ -> incoming Run,update=update}
update : Msg -> Model -> (Model,Cmd Msg)
update (Run raw) model =
 let decoded=D.decodeValue (D.map2 Tuple.pair (D.field "kind" D.string) (D.field "value" D.value)) raw
     (next,commands)=case decoded of
        Ok ("presentation",value) ->
            let shown=Presentation.accept value model.shown
                (previews,result)=Preview.present (Presentation.current shown) model.previews
            in ({shown=shown,previews=previews},result)
        Ok ("grant",value) ->
            let previews=D.decodeValue Realm.grantDecoder value |> Result.toMaybe |> Maybe.andThen (\grant -> Preview.enrollRealm grant model.previews) |> Maybe.withDefault model.previews
            in ({model | previews=previews},E.list identity [])
        Ok ("native",value) ->
            let (previews,result)=Preview.receiveRealm (Presentation.current model.shown) value model.previews
            in ({model | previews=previews},result)
        Ok ("legacy",value) ->
            let (previews,result)=Preview.receive (Presentation.current model.shown) value model.previews
            in ({model | previews=previews},result)
        Ok ("quarantine",value) ->
            let (previews,result)=D.decodeValue Realm.domainDecoder value |> Result.map (\domain -> Preview.quarantineRealm domain model.previews) |> Result.withDefault (model.previews,E.list identity [])
            in ({model | previews=previews},result)
        Ok ("issued",value) -> ({model | previews=Preview.issued value model.previews},E.list identity [])
        Ok ("retry",value) ->
            let (previews,result)=D.decodeValue Realm.domainDecoder value |> Result.map (\domain -> Preview.retry domain model.previews) |> Result.withDefault (model.previews,E.list identity [])
            in ({model | previews=previews},result)
        Ok ("closed",value) ->
            let previews=D.decodeValue Realm.domainDecoder value |> Result.toMaybe |> Maybe.andThen (\domain -> Preview.closeRealm domain model.previews) |> Maybe.withDefault model.previews
            in ({model | previews=previews},E.list identity [])
        _ -> (model,E.list identity [])
 in (next,outgoing (E.object [("models",Preview.observe next.previews),("commands",commands),("realm",Preview.realmStatus next.previews),("metadata",Preview.metadata next.previews),("enrollment",Preview.enrollment next.previews),("feedback",Preview.feedback next.previews)]))
