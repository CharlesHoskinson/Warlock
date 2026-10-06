port module PreviewCatalogReplay exposing (main)
import Json.Decode as D
import Json.Encode as E
import Platform
import Presentation
import PreviewPresenter as Preview
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
        Ok ("native",value) ->
            let (previews,result)=Preview.receive (Presentation.current model.shown) value model.previews
            in ({model | previews=previews},result)
        _ -> (model,E.list identity [])
 in (next,outgoing (E.object [("models",Preview.observe next.previews),("metadata",Preview.metadata next.previews),("enrollment",Preview.enrollment next.previews),("commands",commands)]))
