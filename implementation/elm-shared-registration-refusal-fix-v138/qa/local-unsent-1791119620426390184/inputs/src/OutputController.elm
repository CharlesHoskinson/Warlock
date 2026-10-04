module OutputController exposing (Model, Event(..), Scope, initial, update, frame, controller, owner, views, scopeDecoder, encodeScope, register, pendingBatches)

import Binding
import MenuBridge
import Shell
import TaskbarShell
import Desktop
import Json.Decode as D
import Json.Encode as E
import Surface
import SurfaceController as Controller
import SurfaceRenderer
import UnsentOperation
import UInt64 exposing (Counter)

-- The native host, never an engine instance, issues these view capabilities.
type Scope = Scope Counter Counter

type Model = Model
    { controller : Controller.Model
    , revision : Counter
    , highest : Counter
    , views : List Scope
    , selected : Maybe Scope
    , batches : List Batch
    , batchExhausted : Bool
    , capacityRefused : Bool
    }

type alias Batch = { scope : Scope, revision : Counter, publication : Counter, lease : Counter, binding : Binding.Binding, wire : String, observations : List (String,Counter), operations : List UnsentOperation.Key }

type Event = Disposition D.Value | Topology D.Value | Renderer D.Value | Interaction Desktop.Msg | Dismiss D.Value | Reflow D.Value

initial : Model
initial = Model {controller=Controller.initial,revision=UInt64.zero,highest=UInt64.zero,views=[],selected=Nothing,batches=[],batchExhausted=False,capacityRefused=False}

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
        Disposition raw -> receiveDisposition raw current
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
                            prepared = MenuBridge.preparedSnapshot (Controller.desktop assigned).windows.menus
                            (cancelled,cancelEffects)=case prepared of
                                Just slot -> Controller.update (Controller.Interaction (Desktop.Window (TaskbarShell.CancelPrepared slot.token))) assigned
                                Nothing -> (assigned,[])
                            (unblocked,_) = Controller.update (Controller.Interaction (Desktop.Window (TaskbarShell.Native (Shell.RegistrationAvailable False)))) cancelled
                            (refreshed,readEffects)=Controller.update (Controller.Interaction (Desktop.Window (TaskbarShell.Native (Shell.SupersedeObservations (selected/=Nothing))))) unblocked
                            result = Model {model | revision=table.revision,highest=highest,views=table.scopes,selected=selected,controller=refreshed,batches=[],batchExhausted=False,capacityRefused=False}
                            -- These reads were allocated in this same unsent update,
                            -- before the supersession above. Never forward obsolete
                            -- observations; retain every operation/local effect.
                            prior = List.filter (not << observationEffect) (effects++ownerEffects++cancelEffects)
                        in (result,Controller.Publish (Controller.frame refreshed)::(prior++readEffects))
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
                        in if (popup && owner current/=Just callback.scope) || not canMove then (current,[]) else
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

-- Registration precedes the actual outgoing port. Capacity refuses transport
-- conservatively; it never evicts an unacknowledged batch or replays an effect.
pendingBatches : Model -> Int
pendingBatches (Model model) = List.length model.batches

register : List Controller.Effect -> Model -> (Model,Maybe E.Value)
register effects ((Model model) as current) =
    let requests = List.filterMap (\effect -> case effect of
            Controller.DesktopEffect (Desktop.Send wire) -> Just wire
            Controller.DesktopEffect (Desktop.WindowEffect (Shell.Send wire)) -> Just wire
            Controller.DesktopEffect (Desktop.WindowEffect Shell.RestartBackend) -> Just (E.object [("protocolVersion",E.int 3),("kind",E.string "host-reconnect")])
            _ -> Nothing) effects
        focus = List.filterMap (\effect -> case effect of
            Controller.DesktopEffect (Desktop.Focus target) -> Just (E.string target)
            _ -> Nothing) effects
        packet = E.object [("viewProtocol",E.int 1),("kind",E.string "view-commit"),("projection",frame current),("requests",E.list (\item -> item) requests),("focus",E.list (\item -> item) focus)]
        text = E.encode 0 packet
        binding = (Controller.desktop model.controller).windows.shell.binding
        scoped = owner current |> Maybe.withDefault (model.selected |> Maybe.withDefault (Scope UInt64.zero UInt64.zero))
        observations = List.filterMap observation requests
        operations = List.filterMap (\request -> D.decodeValue UnsentOperation.commandDecoder request |> Result.toMaybe) requests
        bound = List.all (\request -> D.decodeValue (D.field "binding" Binding.decoder) request |> Result.toMaybe |> (==) binding) requests
    in if List.isEmpty effects then (current,Nothing) else
        if List.isEmpty requests || not bound || binding==Nothing then (current,Just packet) else
            if not (List.member scoped model.views) || model.batchExhausted || List.length model.batches>=16 || List.length requests>16 || String.length text>131072 || utf8Length text>131072 then
                let capacity = List.length model.batches>=16 && List.member scoped model.views && List.length requests<=16 && String.length text<=131072 && utf8Length text<=131072
                    (refused,_) = apply (Controller.Interaction (Desktop.Window (TaskbarShell.Native (Shell.RegistrationRefused operations observations)))) (Model {model|batchExhausted=True,capacityRefused=if model.batchExhausted then model.capacityRefused else capacity})
                    prepared = MenuBridge.preparedSnapshot (Controller.desktop (controller refused)).windows.menus
                    belongs slot = List.member ("projection-request",slot.legacyRequest) observations || (slot.geometryRequest |> Maybe.map (\id -> List.member ("geometry-facts-request",id) observations) |> Maybe.withDefault False)
                    (settled,_) = case prepared of
                        Just slot -> if belongs slot then apply (Controller.Interaction (Desktop.Window (TaskbarShell.CancelPrepared slot.token))) refused else (refused,[])
                        Nothing -> (refused,[])
                    presentation = E.object [("viewProtocol",E.int 1),("kind",E.string "view-commit"),("projection",frame settled),("requests",E.list identity []),("focus",E.list identity [])]
                in (settled,Just presentation)
            else case (binding,SurfaceRenderer.decode (Controller.frame model.controller)) of
                (Just authority,Ok snapshot) ->
                    let batch = {scope=scoped,revision=model.revision,publication=SurfaceRenderer.publication snapshot,lease=SurfaceRenderer.lease snapshot,binding=authority,wire=text,observations=observations,operations=operations}
                    in (Model {model|batches=batch::model.batches},Just packet)
                _ -> (current,Nothing)

observation : D.Value -> Maybe (String,Counter)
observation raw =
    case D.decodeValue (D.map2 Tuple.pair (D.field "kind" D.string) (D.field "requestId" UInt64.decoder)) raw of
        Ok ((kind,_) as value) -> if List.member kind ["projection-request","geometry-attach","geometry-facts-request"] then Just value else Nothing
        Err _ -> Nothing

receiveDisposition : D.Value -> Model -> (Model,List Controller.Effect)
receiveDisposition raw ((Model model) as current) =
    let decoder = strict ["viewProtocol","kind","disposition","scope","revision","publication","lease","binding","batch"]
            (D.map8 (\scope revision publication token binding batch disposition header -> {scope=scope,revision=revision,publication=publication,lease=token,binding=binding,wire=batch,disposition=disposition,header=header})
                (D.field "scope" scopeDecoder) (D.field "revision" UInt64.decoder) (D.field "publication" UInt64.decoder) (D.field "lease" UInt64.decoder) (D.field "binding" Binding.decoder)
                (D.field "batch" (D.string |> D.andThen (\text -> if String.length text<=131072 && utf8Length text<=131072 then D.succeed text else D.fail "Batch bound")))
                (D.field "disposition" D.string) (D.map2 Tuple.pair (D.field "viewProtocol" D.int) (D.field "kind" D.string)))
    in case D.decodeValue decoder raw of
        Ok certificate ->
            let matches batch = batch.scope==certificate.scope && batch.revision==certificate.revision && batch.publication==certificate.publication && batch.lease==certificate.lease && batch.binding==certificate.binding && batch.wire==certificate.wire
            in if certificate.header/=(1,"batch-disposition") || not (List.member certificate.disposition ["preflight-unsent","admitted","uncertain"]) || certificate.revision/=model.revision || not (List.member certificate.scope model.views) then (current,[]) else
                case List.filter matches model.batches |> List.head of
                    Nothing -> (current,[])
                    Just batch ->
                        let remaining = List.filter (matches >> not) model.batches
                            canRecover = model.capacityRefused && List.length remaining<16
                            consumed = Model {model|batches=remaining,batchExhausted=if canRecover then False else model.batchExhausted,capacityRefused=if canRecover then False else model.capacityRefused}
                            currentShell = (Controller.desktop model.controller).windows.shell
                            (settled,operationEffects) = if certificate.disposition=="preflight-unsent" && currentShell.binding==Just batch.binding then
                                apply (Controller.Interaction (Desktop.Window (TaskbarShell.Native (Shell.UnsentOperations batch.operations)))) consumed
                                else (consumed,[])
                                                    (recovered,recoveryEffects) = if canRecover then apply (Controller.Interaction (Desktop.Window (TaskbarShell.Native (Shell.RegistrationAvailable True)))) settled else (settled,[])
                        in if certificate.disposition/="preflight-unsent" || not (Shell.matchesUnsent batch.observations currentShell) || currentShell.binding/=Just batch.binding || lease model.controller/=Just batch.lease then (recovered,operationEffects++recoveryEffects) else
                            let (closed,closeEffects)=apply (Controller.NativeDismiss batch.lease) recovered
                                prepared = MenuBridge.preparedSnapshot (Controller.desktop (controller closed)).windows.menus
                                (cancelled,cancelEffects)=case prepared of
                                    Just selection -> apply (Controller.Interaction (Desktop.Window (TaskbarShell.CancelPrepared selection.token))) closed
                                    Nothing -> (closed,[])
                                (fresh,effects)=apply (Controller.Interaction (Desktop.Window (TaskbarShell.Native (Shell.UnsentObservations batch.observations)))) cancelled
                            in (fresh,operationEffects++recoveryEffects++closeEffects++cancelEffects++effects)
        Err _ -> (current,[])

utf8Length : String -> Int
utf8Length text = String.foldl (\char count -> let code=Char.toCode char in count+(if code<=127 then 1 else if code<=2047 then 2 else if code<=65535 then 3 else 4)) 0 text

observationEffect : Controller.Effect -> Bool
observationEffect effect = case effect of
    Controller.DesktopEffect (Desktop.WindowEffect (Shell.Send wire)) -> observation wire/=Nothing
    _ -> False
