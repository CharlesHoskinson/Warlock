module OutputController exposing (Model, Event(..), Scope, initial, update, frame, controller, owner, views, scopeDecoder, encodeScope)

import Desktop
import Json.Decode as D
import Json.Encode as E
import Surface
import SurfaceController as Controller
import SurfaceRenderer
import UInt64 exposing (Counter)

-- The native host, never an engine instance, issues these view capabilities.
type Scope = Scope Counter Counter

type Model = Model
    { controller : Controller.Model
    , revision : Counter
    , highest : Counter
    , views : List Scope
    , selected : Maybe Scope
    }

type Event = Topology D.Value | Renderer D.Value | Interaction Desktop.Msg | Dismiss D.Value | Reflow D.Value

initial : Model
initial = Model {controller=Controller.initial,revision=UInt64.zero,highest=UInt64.zero,views=[],selected=Nothing}

strict : List String -> D.Decoder a -> D.Decoder a
strict fields decoder = D.keyValuePairs D.value |> D.andThen (\pairs -> if List.sort (List.map Tuple.first pairs)==List.sort fields then decoder else D.fail "Output view fields")

scopeDecoder : D.Decoder Scope
scopeDecoder = strict ["id","generation"] (D.map2 Scope (D.field "id" UInt64.decoder) (D.field "generation" UInt64.decoder))
    |> D.andThen (\((Scope viewId viewGeneration) as scope) -> if viewId==UInt64.zero || viewGeneration==UInt64.zero then D.fail "Zero view scope" else D.succeed scope)

encodeScope : Scope -> E.Value
encodeScope (Scope viewId viewGeneration) = E.object [("id",E.string (UInt64.string viewId)),("generation",E.string (UInt64.string viewGeneration))]

identity : Scope -> Counter
identity (Scope value _) = value

generation : Scope -> Counter
generation (Scope _ value) = value

controller : Model -> Controller.Model
controller (Model model) = model.controller

views : Model -> List Scope
views (Model model) = model.views

owner : Model -> Maybe Scope
owner (Model model) = if Surface.mode (Controller.desktop model.controller)=="closed" then Nothing else model.selected

frame : Model -> E.Value
frame ((Model model) as current) = E.object
    [("viewProtocol",E.int 1),("kind",E.string "view-frame"),("revision",E.string (UInt64.string model.revision)),("views",E.list encodeScope model.views),("focusOwner",model.selected |> Maybe.map encodeScope |> Maybe.withDefault E.null),("popupOwner",owner current |> Maybe.map encodeScope |> Maybe.withDefault E.null),("frame",Controller.frame model.controller)]

lease : Controller.Model -> Maybe Counter
lease model = SurfaceRenderer.decode (Controller.frame model) |> Result.toMaybe |> Maybe.map SurfaceRenderer.lease

freshRelocationPossible : Controller.Model -> Bool
freshRelocationPossible model =
    case SurfaceRenderer.decode (Controller.frame model) of
        Err _ -> False
        Ok snapshot -> UInt64.next (SurfaceRenderer.lease snapshot)/=Nothing && (UInt64.next (SurfaceRenderer.publication snapshot) |> Maybe.andThen UInt64.next)/=Nothing

apply : Controller.Event -> Model -> (Model,List Controller.Effect)
apply event (Model model) =
    let (next,effects) = Controller.update event model.controller
    in (Model {model | controller=next},effects)

assignOwner : Maybe Scope -> Controller.Model -> (Controller.Model,List Controller.Effect)
assignOwner scope controllerModel =
    let registered = scope |> Maybe.map (\(Scope outputId providerId) -> {outputId=outputId,providerId=providerId})
    in Controller.update (Controller.Interaction (Desktop.PresentationOwner registered)) controllerModel

update : Event -> Model -> (Model,List Controller.Effect)
update event ((Model model) as current) =
    case event of
        Interaction message -> apply (Controller.Interaction message) current
        Topology raw ->
            let decoder = strict ["viewProtocol","kind","revision","views"]
                    (D.map4 (\version kind revision scopes -> {version=version,kind=kind,revision=revision,scopes=scopes}) (D.field "viewProtocol" D.int) (D.field "kind" D.string) (D.field "revision" UInt64.decoder) (D.field "views" (D.list scopeDecoder)))
                admitted scopes = List.length scopes<=64 && List.length (List.map identity scopes)==List.length (List.foldl (\scope ids -> if List.member (identity scope) ids then ids else identity scope::ids) [] scopes)
                    && List.all (\scope -> case List.filter (\prior -> identity prior==identity scope) model.views |> List.head of
                        Just prior -> UInt64.compare (generation scope) (generation prior)/=LT
                        Nothing -> UInt64.compare (identity scope) model.highest==GT) scopes
            in case D.decodeValue decoder raw of
                Ok table ->
                    if table.version/=1 || table.kind/="view-topology" || UInt64.compare table.revision model.revision/=GT || not (admitted table.scopes) then (current,[]) else
                        let survives = model.selected |> Maybe.map (\priorSelected -> List.member priorSelected table.scopes) |> Maybe.withDefault False
                            selected = if survives then model.selected else List.head table.scopes
                            retired = not survives && owner current/=Nothing
                            (next,effects) = if retired then lease model.controller |> Maybe.map (\token -> Controller.update (Controller.NativeDismiss token) model.controller) |> Maybe.withDefault (model.controller,[]) else (model.controller,[])
                            (assigned,ownerEffects) = assignOwner selected next
                            highest = List.foldl (\scope maximum -> if UInt64.compare (identity scope) maximum==GT then identity scope else maximum) model.highest table.scopes
                            result = Model {model | revision=table.revision,highest=highest,views=table.scopes,selected=selected,controller=assigned}
                        in (result,Controller.Publish (Controller.frame assigned)::(effects++ownerEffects))
                Err _ -> (current,[])
        Renderer raw ->
            let decoder = strict ["viewProtocol","kind","scope","action"]
                    (D.map4 (\version kind scope action -> {version=version,kind=kind,scope=scope,action=action}) (D.field "viewProtocol" D.int) (D.field "kind" D.string) (D.field "scope" scopeDecoder) (D.field "action" D.value))
            in case (D.decodeValue decoder raw,SurfaceRenderer.decode (Controller.frame model.controller)) of
                (Ok callback,Ok snapshot) ->
                    if callback.version/=1 || callback.kind/="view-action" || not (List.member callback.scope model.views) then (current,[]) else
                        let popup = D.decodeValue (D.field "surface" D.string) callback.action==Ok "popup"
                            ownerChange = not popup && model.selected/=Just callback.scope
                            canMove = not ownerChange || freshRelocationPossible model.controller
                        in if not canMove then (current,[]) else
                            case Surface.resolve (SurfaceRenderer.publication snapshot) (SurfaceRenderer.lease snapshot) callback.action (Controller.desktop model.controller) of
                                Nothing -> (current,[])
                                Just message ->
                                    let (assigned,ownerEffects)=assignOwner (Just callback.scope) model.controller
                                        (updated,effects)=Controller.update (Controller.Interaction message) assigned
                                        (next,relocation)=if ownerChange then Controller.update Controller.NativeRelocate updated else (updated,[])
                                    in (Model {model | controller=next,selected=Just callback.scope},ownerEffects++effects++relocation)
                _ -> (current,[])
        Dismiss raw -> nativePopup Controller.NativeDismiss raw current
        Reflow raw -> nativePopup Controller.NativeReflow raw current

nativePopup : (Counter -> Controller.Event) -> D.Value -> Model -> (Model,List Controller.Effect)
nativePopup event raw ((Model model) as current) =
    let decoder = strict ["scope","lease"] (D.map2 Tuple.pair (D.field "scope" scopeDecoder) (D.field "lease" UInt64.decoder))
    in case D.decodeValue decoder raw of
        Ok (scope,token) -> if owner current==Just scope && List.member scope model.views then apply (event token) current else (current,[])
        Err _ -> (current,[])
