module Shell exposing (Model, Msg(..), Phase(..), Effect(..), Stamp, stampKey, capture, stampDecoder, initial, update, encode, status, available, captureGeometry)

import Binding exposing (Binding)
import Effects
import GeometryProjection
import NativeOutcome
import Json.Decode as D
import Json.Encode as E
import UInt64 exposing (Counter)

type Phase = Detached | Reconciling | Ready | Exhausted
type Stamp = Stamp Binding Counter Counter
type Msg = Incoming D.Value | Refresh | Reconnect | Ignore | GeometryAttach | GeometryRefresh | Act Stamp Effects.Operation Counter
type Effect = Send E.Value | RestartBackend
type alias Model = { effects : Effects.Model, binding : Maybe Binding, request : Counter, expected : Maybe Counter, phase : Phase, reconnecting : Bool, notice : String, geometry : Maybe GeometryProjection.Snapshot, geometryCaps : Maybe GeometryProjection.Capabilities, geometryExpected : Maybe Counter, geometryAttachExpected : Maybe Counter }
stampKey : Stamp -> String
stampKey (Stamp binding output revision) = E.encode 0 (Binding.encode binding) ++ ":" ++ UInt64.string output ++ ":" ++ UInt64.string revision
capture : Model -> Maybe Stamp
capture model =
    case (model.binding,model.effects.observed) of
        (Just binding,Just observed) ->
            if Binding.matchesContext observed.context.lifetime observed.context.epoch binding then Just (Stamp binding observed.context.output observed.context.revision) else Nothing
        _ -> Nothing
positive : D.Decoder Counter
positive = UInt64.decoder |> D.andThen (\value -> if value /= UInt64.zero then D.succeed value else D.fail "Zero displayed scope")
stampDecoder : D.Decoder Stamp
stampDecoder = strict ["binding","output","revision"] (D.map3 Stamp (D.field "binding" Binding.decoder) (D.field "output" positive) (D.field "revision" positive))

initial : Model
initial = { effects = Effects.empty, binding = Nothing, request = UInt64.zero, expected = Nothing, phase = Detached, reconnecting = True, notice = "Connecting…", geometry=Nothing,geometryCaps=Nothing,geometryExpected=Nothing,geometryAttachExpected=Nothing }
strict : List String -> D.Decoder a -> D.Decoder a
strict fields decoder = D.keyValuePairs D.value |> D.andThen (\pairs -> if List.sort (List.map Tuple.first pairs) == List.sort fields then decoder else D.fail "Unexpected fields")
version : D.Decoder ()
version = D.field "protocolVersion" D.int |> D.andThen (\v -> if v == 3 then D.succeed () else D.fail "Protocol version")
refresh : Model -> (Model,List Effect)
refresh model =
    case ( model.binding, UInt64.next model.request ) of
        (Just binding,Just request) ->
            if model.phase == Detached then (model,[]) else
                ({model | request = request, expected = Just request, phase = Reconciling},[Send (E.object [("protocolVersion",E.int 3),("kind",E.string "projection-request"),("binding",Binding.encode binding),("requestId",E.string (UInt64.string request))])])
        _ -> ({model | phase = Exhausted, expected = Nothing, notice = "Restart the shell to continue."},[])
disconnect : Model -> Model
disconnect model =
    let (effects,_,_) = Effects.apply (E.object [("kind",E.string "disconnect")]) model.effects
    in {model | effects = effects, expected = Nothing, geometry=Nothing,geometryCaps=Nothing,geometryExpected=Nothing,geometryAttachExpected=Nothing, phase = Detached, reconnecting = False, notice = "Connection lost. Reconnect to continue."}
available : Model -> Bool
available model = model.phase == Ready && not (Effects.pending model.effects)
status : Model -> String
status model =
    case model.effects.transaction |> Maybe.map .status of
        Just Effects.Pending -> "Applying window change…"
        Just Effects.Unknown -> model.notice ++ " The last request could not be confirmed."
        Just Effects.Refused -> model.notice ++ " The window change was refused."
        _ -> model.notice
update : Msg -> Model -> (Model,List Effect)
update msg model =
    case msg of
        Refresh -> if model.phase == Detached || Effects.pending model.effects then (model,[]) else refresh model
        Reconnect ->
            if model.phase == Detached && not model.reconnecting then ({model | reconnecting = True, notice = "Reconnecting…"},[RestartBackend]) else (model,[])
        Ignore -> (model,[])
        GeometryAttach -> geometryRequest True model
        GeometryRefresh -> geometryRequest False model
        Act stamp operation incarnation ->
            if (if Effects.protocol operation==2 then captureGeometry model else capture model) /= Just stamp then ({model | notice="Window list changed. Choose again."},[])
            else if not (available model) then (model,[]) else
                let (effects,command,error) =
                        if Effects.protocol operation==2 then case (model.geometryCaps,model.geometry) of
                            (Just caps,Just observed) -> if model.geometryExpected/=Nothing then (model.effects,Nothing,Just "Geometry refresh pending") else Effects.beginGeometry caps observed operation incarnation model.effects
                            _ -> (model.effects,Nothing,Just "Geometry observation unavailable")
                        else Effects.apply (E.object [("kind",E.string "begin"),("operation",E.string (Effects.operationName operation)),("incarnation",E.string (UInt64.string incarnation))]) model.effects
                    commands = case (command,model.binding) of
                        (Just value,Just binding) -> case D.decodeValue (D.field "intent" D.value) value of
                            Ok intent -> [Send (E.object [("protocolVersion",E.int 3),("kind",E.string "window-effect"),("effectProtocol",E.int (Effects.protocol operation)),("binding",Binding.encode binding),("intent",intent)])]
                            Err _ -> []
                        _ -> []
                in ({model | effects = effects, notice = Maybe.withDefault model.notice error},commands)
        Incoming raw ->
            case D.decodeValue (D.field "kind" D.string) raw of
                Ok "host-disconnected" -> (disconnect model,[])
                Ok "host-refresh" -> if model.phase == Detached then (model,[]) else refresh model
                Ok "attached" ->
                    case D.decodeValue (D.map2 (\_ binding -> binding) version (D.field "binding" Binding.decoder)) raw of
                        Ok binding ->
                            if model.phase /= Detached || not model.reconnecting || (model.binding |> Maybe.map (Binding.replaces binding >> not) |> Maybe.withDefault False) then (model,[]) else
                                let detached = disconnect model
                                in refresh { detached | binding = Just binding, phase = Reconciling, reconnecting = False, notice = "Updating window information…" }
                        Err _ -> (disconnect model,[])
                Ok "action-projection" ->
                    let decoder = strict ["protocolVersion","kind","binding","requestId","context","scene"] (D.map5 (\_ binding request life epoch -> (binding,request,(life,epoch))) version (D.field "binding" Binding.decoder) (D.field "requestId" UInt64.decoder) (D.at ["context","lifetime"] UInt64.decoder) (D.at ["context","epoch"] UInt64.decoder))
                    in case D.decodeValue decoder raw of
                        Ok (binding,request,(life,epoch)) ->
                            if model.phase == Detached || model.binding /= Just binding || model.expected /= Just request || not (Binding.matchesContext life epoch binding) then (model,[]) else
                                case D.decodeValue (D.map2 (\context scene -> E.object [("kind",E.string "snapshot"),("context",context),("scene",scene)]) (D.field "context" D.value) (D.field "scene" D.value)) raw of
                                    Ok snapshot ->
                                        let (effects,_,error) = Effects.apply snapshot model.effects
                                        in ({model | effects = effects, phase = if error == Nothing then Ready else Reconciling, expected = if error == Nothing then Nothing else model.expected, notice = if error == Nothing then "Connected" else "Window information could not be verified."},[])
                                    Err _ -> (model,[])
                        Err _ -> (model,[])
                Ok "geometry-attached" ->
                    let decoder = strict ["protocolVersion","kind","geometryProtocol","binding","requestId","capabilities"]
                            (D.map5 (\_ _ binding request caps -> {binding=binding,request=request,caps=caps}) version
                                (D.field "geometryProtocol" D.int |> D.andThen (\v -> if v==1 then D.succeed () else D.fail "Geometry protocol"))
                                (D.field "binding" Binding.decoder) (D.field "requestId" positive) (D.field "capabilities" GeometryProjection.capabilitiesDecoder))
                    in case D.decodeValue decoder raw of
                        Ok value -> if model.binding/=Just value.binding || model.geometryAttachExpected/=Just value.request || model.phase==Detached then (model,[]) else geometryRequest False {model|geometryCaps=Just value.caps,geometry=Nothing,geometryAttachExpected=Nothing}
                        Err _ -> (model,[])
                Ok "geometry-facts" ->
                    case model.geometryCaps of
                        Nothing -> (model,[])
                        Just caps -> case GeometryProjection.decode caps raw of
                            Err _ -> (model,[])
                            Ok observed ->
                                let newer=case model.geometry of
                                        Nothing -> True
                                        Just old -> if old.context.lifetime==observed.context.lifetime && old.context.epoch==observed.context.epoch && old.context.output==observed.context.output then UInt64.compare observed.context.revision old.context.revision/=LT && (observed.context.revision/=old.context.revision || observed=={old|request=observed.request,sequence=observed.sequence}) else True
                                in if model.binding/=Just observed.binding || model.geometryExpected/=Just observed.request || model.phase==Detached || not newer then (model,[]) else ({model|geometry=Just observed,geometryExpected=Nothing},[])
                Ok "effect-outcome" ->
                    if not (NativeOutcome.valid raw) then (model,[]) else
                    case D.decodeValue (D.map4 (\_ binding protocolId receipt -> (binding,protocolId,receipt)) version (D.field "binding" Binding.decoder) (D.field "effectProtocol" D.int)
                        (D.map3 (\intent outcome protocolId -> E.object [("kind",E.string "receipt"),("intent",intent),("status",outcome),("effectProtocol",protocolId)]) (D.field "intent" D.value) (D.field "status" D.value) (D.field "effectProtocol" D.value))) raw of
                        Ok (binding,protocolId,receipt) ->
                            if model.phase == Detached || model.binding /= Just binding then (model,[]) else
                                let (effects,_,error) = Effects.apply receipt model.effects
                                in if error /= Nothing then (model,[]) else
                                    let current = case model.effects.transaction of
                                            Nothing -> False
                                            Just transaction -> transaction.effectProtocol==protocolId && (D.decodeValue (D.field "intent" D.value) raw |> Result.map (E.encode 0) |> Result.withDefault "") == E.encode 0 (Effects.encodeIntent transaction.intent)
                                    in if not current then ({model|effects=effects},[]) else
                                    let (next,commands)=refresh {model|effects=effects}
                                    in if protocolId==2 then
                                        let (geometryNext,geometryCommands)=geometryRequest False next
                                        in (geometryNext,commands++geometryCommands)
                                       else (next,commands)
                        Err _ -> (model,[])
                _ -> (model,[])
encode : Model -> E.Value
encode model = E.object [("phase",E.string (case model.phase of
    Detached -> "Detached"
    Reconciling -> "Reconciling"
    Ready -> "Ready"
    Exhausted -> "Exhausted")),("request",E.string (UInt64.string model.request)),("available",E.bool (available model)),("reconnecting",E.bool model.reconnecting),("effects",Effects.encode model.effects)]

captureGeometry : Model -> Maybe Stamp
captureGeometry model = model.geometry |> Maybe.map (\observed -> Stamp observed.binding observed.context.output observed.context.revision)

geometryRequest : Bool -> Model -> (Model,List Effect)
geometryRequest attach model =
    case (model.binding,UInt64.next model.request) of
        (Just binding,Just request) ->
            if model.phase==Detached || (not attach && model.geometryCaps==Nothing) then (model,[]) else
            let common=[("protocolVersion",E.int 3),("kind",E.string (if attach then "geometry-attach" else "geometry-facts-request")),("geometryProtocol",E.int 1),("binding",Binding.encode binding),("requestId",E.string (UInt64.string request))]
                payload=if attach then common else common++[("minimumWatermark",E.string (model.geometry |> Maybe.map (.sequence >> UInt64.string) |> Maybe.withDefault "0"))]
            in ({model|request=request,geometryAttachExpected=if attach then Just request else model.geometryAttachExpected,geometryExpected=if attach then Nothing else Just request},[Send (E.object payload)])
        _ -> (model,[])
