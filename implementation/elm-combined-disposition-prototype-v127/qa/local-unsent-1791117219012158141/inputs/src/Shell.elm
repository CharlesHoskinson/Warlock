module Shell exposing (canProveUnsent, Model, Msg(..), Phase(..), Effect(..), Stamp, stampKey, capture, stampDecoder, initial, update, encode, status, available, captureGeometry, resumeNotifications, matchesUnsent)

import UnsentOperation
import Binding exposing (Binding)
import Effects
import GeometryProjection
import NativeOutcome
import Json.Decode as D
import Json.Encode as E
import UInt64 exposing (Counter)

type RecoveryFailure = Unavailable | Full | Busy | Unverified | LegacyOwner

recoveryDecoder : D.Decoder RecoveryFailure
recoveryDecoder = D.string |> D.andThen (\reason -> case reason of
    "unavailable" -> D.succeed Unavailable
    "full" -> D.succeed Full
    "busy" -> D.succeed Busy
    "unverified" -> D.succeed Unverified
    "legacy-owner" -> D.succeed LegacyOwner
    _ -> D.fail "Recovery reason")

recoveryNotice : RecoveryFailure -> String
recoveryNotice failure = case failure of
    Unavailable -> "Window recovery data is unavailable. Restore access, then reconnect."
    Full -> "Window recovery storage is full. Free space, then reconnect."
    Busy -> "Another shell is using window recovery data. Close it, then reconnect."
    Unverified -> "Window recovery data could not be verified. Repair it, then reconnect."
    LegacyOwner -> "Previous window recovery data has no verified owner. Complete migration, then reconnect."

type Phase = Detached | Reconciling | Ready | Exhausted
type Stamp = Stamp Binding Counter Counter
type Msg = Incoming D.Value | Refresh | Reconnect | Ignore | GeometryAttach | GeometryRefresh | Act Stamp Effects.Operation Counter | UnsentObservations (List (String,Counter)) | SupersedeObservations Bool | UnsentOperations (List UnsentOperation.Key)
type Effect = Send E.Value | RestartBackend | ArmPrepared Counter
type alias Model = { effects : Effects.Model, binding : Maybe Binding, request : Counter, expected : Maybe Counter, phase : Phase, reconnecting : Bool, notice : String, geometry : Maybe GeometryProjection.Snapshot, geometryCaps : Maybe GeometryProjection.Capabilities, geometryExpected : Maybe Counter, geometryAttachExpected : Maybe Counter, attachNeeded : Bool, recoveryFailure : Maybe RecoveryFailure, issued : List { binding : Binding, protocol : Int, intent : Effects.Intent }, notificationQueued : Bool, deferNotifications : Bool }
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
initial = { effects = Effects.empty, binding = Nothing, request = UInt64.zero, expected = Nothing, phase = Detached, reconnecting = True, notice = "Connecting…", geometry=Nothing,geometryCaps=Nothing,geometryExpected=Nothing,geometryAttachExpected=Nothing,attachNeeded=False,issued=[],notificationQueued=False,deferNotifications=False,recoveryFailure=Nothing }
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
    in {model | effects = effects, expected = Nothing, geometry=Nothing,geometryCaps=Nothing,geometryExpected=Nothing,geometryAttachExpected=Nothing, attachNeeded=False, notificationQueued=False,deferNotifications=False, phase = Detached, reconnecting = False, notice = Maybe.map recoveryNotice model.recoveryFailure |> Maybe.withDefault "Connection lost. Reconnect to continue."}
available : Model -> Bool
available model = model.phase == Ready && not (Effects.pending model.effects) && model.geometryAttachExpected==Nothing && (not (model.geometryCaps |> Maybe.map .effects |> Maybe.withDefault False) || (model.geometryExpected==Nothing && model.geometry/=Nothing))
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
        Refresh -> if model.phase == Detached || Effects.pending model.effects then (model,[]) else if geometrySupported model then notificationRefresh model else refresh model
        Reconnect ->
            if model.phase == Detached && not model.reconnecting then ({model | reconnecting = True, notice = "Reconnecting…"},[RestartBackend]) else (model,[])
        SupersedeObservations reissue ->
            if model.phase==Detached || model.phase==Exhausted || model.binding==Nothing then (model,[]) else
                let attach = model.attachNeeded || model.geometryAttachExpected/=Nothing
                    retired = {model|expected=Nothing,geometryExpected=Nothing,geometryAttachExpected=Nothing,phase=Reconciling,notificationQueued=True,deferNotifications=False}
                in if not reissue then (retired,[]) else
                    let (fresh,commands)=refreshObservations retired
                        (attached,attachCommands)=if attach then geometryRequest True fresh else (fresh,[])
                    in (attached,commands++attachCommands)
        UnsentOperations operations ->
            if not (canProveUnsent operations model) then (model,[]) else
                let matches key entry = entry.binding==key.binding && entry.protocol==key.protocol && entry.intent==key.intent
                    effects = List.foldl (\key state -> Effects.locallyRefuseUnsent key.protocol key.intent state) model.effects operations
                    updated = {model|effects=effects,issued=List.filter (\entry -> not (List.any (\key -> matches key entry) operations)) model.issued,notice="The request was not sent. Choose again."}
                in resumeNotifications updated
        UnsentObservations observations ->
            let valid = matchesUnsent observations model
                contains kind = List.any (\(name,_) -> name==kind) observations
                cleared = {model|expected=if contains "projection-request" then Nothing else model.expected,geometryExpected=if contains "geometry-facts-request" then Nothing else model.geometryExpected,geometryAttachExpected=if contains "geometry-attach" then Nothing else model.geometryAttachExpected,notificationQueued=True}
            in if not valid || model.phase==Detached || model.phase==Exhausted then (model,[]) else
                if Effects.pending model.effects || model.deferNotifications || cleared.expected/=Nothing || cleared.geometryExpected/=Nothing || cleared.geometryAttachExpected/=Nothing then (cleared,[]) else
                    let (fresh,commands)=refreshObservations cleared
                        (attached,attachCommands)=if contains "geometry-attach" then geometryRequest True fresh else (fresh,[])
                    in (attached,commands++attachCommands)
        Ignore -> (model,[])
        GeometryAttach -> geometryRequest True model
        GeometryRefresh -> geometryRequest False model
        Act stamp operation incarnation ->
            if not (available model) then (model,[])
            else if (if Effects.protocol operation==2 then captureGeometry model else capture model) /= Just stamp then ({model | notice="Window list changed. Choose again."},[]) else
                let (effects,command,error) =
                        if Effects.protocol operation==2 then case (model.geometryCaps,model.geometry) of
                            (Just caps,Just observed) -> if model.geometryExpected/=Nothing || model.geometryAttachExpected/=Nothing then (model.effects,Nothing,Just "Geometry refresh pending") else Effects.beginGeometry caps observed operation incarnation model.effects
                            _ -> (model.effects,Nothing,Just "Geometry observation unavailable")
                        else Effects.apply (E.object [("kind",E.string "begin"),("operation",E.string (Effects.operationName operation)),("incarnation",E.string (UInt64.string incarnation))]) model.effects
                    commands = case (command,model.binding) of
                        (Just value,Just binding) -> case D.decodeValue (D.field "intent" D.value) value of
                            Ok intent -> [Send (E.object [("protocolVersion",E.int 3),("kind",E.string "window-effect"),("effectProtocol",E.int (Effects.protocol operation)),("binding",Binding.encode binding),("intent",intent)])]
                            Err _ -> []
                        _ -> []
                in ({model | effects = effects, notice = Maybe.withDefault model.notice error,
                    issued=case (command,model.binding,effects.transaction) of
                        (Just _,Just binding,Just transaction) -> {binding=binding,protocol=transaction.effectProtocol,intent=transaction.intent}::model.issued
                        _ -> model.issued},commands)
        Incoming raw ->
            case D.decodeValue (D.field "kind" D.string) raw of
                Ok "host-recovery-failed" ->
                    case D.decodeValue (strict ["protocolVersion","kind","reason"] (D.map2 (\_ reason -> reason) version (D.field "reason" recoveryDecoder))) raw of
                        Ok reason ->
                            let detached = disconnect model
                            in ({detached | recoveryFailure=Just reason,notice=recoveryNotice reason},[])
                        Err _ -> (model,[])
                Ok "host-disconnected" -> (disconnect model,[])
                Ok "host-refresh" ->
                    case D.decodeValue (strict ["protocolVersion","kind"] version) raw of
                        Ok _ -> notificationRefresh model
                        Err _ -> (model,[])
                Ok "attached" ->
                    case D.decodeValue (D.map2 (\_ binding -> binding) version (D.field "binding" Binding.decoder)) raw of
                        Ok binding ->
                            if model.phase /= Detached || not model.reconnecting || (model.binding |> Maybe.map (Binding.replaces binding >> not) |> Maybe.withDefault False) then (model,[]) else
                                let detached = disconnect model
                                in refresh { detached | binding = Just binding, phase = Reconciling, reconnecting = False, recoveryFailure=Nothing, notice = "Updating window information…" }
                        Err _ -> (disconnect model,[])
                Ok "action-projection" ->
                    let decoder = strict ["protocolVersion","kind","binding","requestId","context","scene"] (D.map5 (\_ binding request life epoch -> (binding,request,(life,epoch))) version (D.field "binding" Binding.decoder) (D.field "requestId" UInt64.decoder) (D.at ["context","lifetime"] UInt64.decoder) (D.at ["context","epoch"] UInt64.decoder))
                    in case D.decodeValue decoder raw of
                        Ok (binding,request,(life,epoch)) ->
                            if model.phase == Detached || model.binding /= Just binding || model.expected /= Just request || not (Binding.matchesContext life epoch binding) then (model,[]) else
                                case D.decodeValue (D.map2 (\context scene -> E.object [("kind",E.string "snapshot"),("context",context),("scene",scene)]) (D.field "context" D.value) (D.field "scene" D.value)) raw of
                                    Ok snapshot ->
                                        let (effects,_,error) = Effects.apply snapshot model.effects
                                        in drainNotifications {model | effects = effects, phase = if error == Nothing then Ready else Reconciling, expected = if error == Nothing then Nothing else model.expected, notice = if error == Nothing then "Connected" else "Window information could not be verified."}
                                    Err _ -> (model,[])
                        Err _ -> (model,[])
                Ok "host-geometry-negotiate" ->
                    case D.decodeValue (strict ["protocolVersion","kind"] version) raw of
                        Err _ -> (model,[])
                        Ok _ -> if model.geometryCaps/=Nothing || model.geometryAttachExpected/=Nothing then (model,[]) else geometryRequest True model
                Ok "geometry-unavailable" ->
                    let decoder = strict ["protocolVersion","kind","binding","requestId","reason"]
                            (D.map4 (\_ binding request reason -> {binding=binding,request=request,reason=reason}) version (D.field "binding" Binding.decoder) (D.field "requestId" positive)
                                (D.field "reason" D.string |> D.andThen (\reason -> if String.length reason<=256 then D.succeed reason else D.fail "Geometry refusal reason")))
                    in case D.decodeValue decoder raw of
                        Err _ -> (model,[])
                        Ok refusal -> if model.binding/=Just refusal.binding || model.geometryAttachExpected/=Just refusal.request then (model,[]) else
                            drainNotifications {model|geometryCaps=Just {effects=False,operations=[]},geometry=Nothing,geometryAttachExpected=Nothing,attachNeeded=False,geometryExpected=Nothing}
                Ok "geometry-attached" ->
                    let decoder = strict ["protocolVersion","kind","geometryProtocol","binding","requestId","capabilities"]
                            (D.map5 (\_ _ binding request caps -> {binding=binding,request=request,caps=caps}) version
                                (D.field "geometryProtocol" D.int |> D.andThen (\v -> if v==1 then D.succeed () else D.fail "Geometry protocol"))
                                (D.field "binding" Binding.decoder) (D.field "requestId" positive) (D.field "capabilities" GeometryProjection.capabilitiesDecoder))
                    in case D.decodeValue decoder raw of
                        Ok value -> if model.binding/=Just value.binding || model.geometryAttachExpected/=Just value.request || model.phase==Detached then (model,[]) else geometryRequest False {model|geometryCaps=Just value.caps,geometry=Nothing,geometryAttachExpected=Nothing,attachNeeded=False}
                        Err _ -> (model,[])
                Ok "geometry-facts" ->
                    case model.geometryCaps of
                        Nothing -> (model,[])
                        Just caps -> case GeometryProjection.decode caps raw of
                            Err _ -> (model,[])
                            Ok observed ->
                                let newer=case model.geometry of
                                        Nothing -> True
                                        Just old -> if old.context.lifetime==observed.context.lifetime && old.context.epoch==observed.context.epoch then UInt64.compare observed.context.output old.context.output/=LT && UInt64.compare observed.sequence old.sequence/=LT && UInt64.compare observed.context.revision old.context.revision/=LT && (observed.context.revision/=old.context.revision || observed=={old|request=observed.request,sequence=observed.sequence}) else True
                                in if model.binding/=Just observed.binding || model.geometryExpected/=Just observed.request || model.phase==Detached || not newer then (model,[]) else drainNotifications {model|geometry=Just observed,geometryExpected=Nothing}
                Ok "host-recovery-watermarks" ->
                    let decoder=strict ["protocolVersion","kind","binding","request","generation"] (D.map4 (\_ binding request generation -> (binding,request,generation)) version (D.field "binding" Binding.decoder) (D.field "request" UInt64.decoder) (D.field "generation" UInt64.decoder))
                    in case D.decodeValue decoder raw of
                        Ok (binding,request,generation) ->
                            if model.phase/=Reconciling || model.binding/=Just binding then (model,[]) else
                                let (effects,_,_)=Effects.apply (E.object [("kind",E.string "recover-watermarks"),("request",E.string (UInt64.string request)),("generation",E.string (UInt64.string generation))]) model.effects
                                in ({model|effects=effects},[])
                        Err _ -> (model,[])
                Ok "host-uncertain" ->
                    let decoder=D.oneOf
                            [ strict ["protocolVersion","kind","binding","intent"] (D.map3 (\_ binding intent -> (binding,intent,1)) version (D.field "binding" Binding.decoder) (D.field "intent" D.value))
                            , strict ["protocolVersion","kind","binding","intent","effectProtocol"] (D.map4 (\_ binding intent protocolId -> (binding,intent,protocolId)) version (D.field "binding" Binding.decoder) (D.field "intent" D.value) (D.field "effectProtocol" D.int)) ]
                    in case D.decodeValue decoder raw of
                        Ok (binding,intent,protocolId) ->
                            if model.binding/=Just binding || model.phase/=Reconciling || (D.decodeValue (D.at ["context","lifetime"] positive) intent |> Result.map (\life -> Binding.sameLifetime life binding))/=Ok True then (model,[]) else
                                let (effects,_,error)=Effects.apply (E.object [("kind",E.string "recover"),("intent",intent),("effectProtocol",E.int protocolId)]) model.effects
                                in if error/=Nothing then (model,[]) else ({model|effects=effects,notice="The previous window change could not be confirmed."},[])
                        Err _ -> (model,[])
                Ok "effect-outcome" ->
                    if not (NativeOutcome.valid raw) then (model,[]) else
                    case D.decodeValue (D.map4 (\_ binding protocolId receipt -> (binding,protocolId,receipt)) version (D.field "binding" Binding.decoder) (D.field "effectProtocol" D.int)
                        (D.map3 (\intent outcome protocolId -> E.object [("kind",E.string "receipt"),("intent",intent),("status",outcome),("effectProtocol",protocolId)]) (D.field "intent" D.value) (D.field "status" D.value) (D.field "effectProtocol" D.value))) raw of
                        Ok (binding,protocolId,receipt) ->
                            let receivedIntent = D.decodeValue (D.field "intent" Effects.intentDecoder) raw |> Result.toMaybe
                                exact entry = entry.binding==binding && entry.protocol==protocolId && Just entry.intent==receivedIntent
                                known = List.any exact model.issued
                            in if not known then (model,[]) else
                                let (effects,_,error) = Effects.apply receipt model.effects
                                    retained = if D.decodeValue (D.field "status" D.string) raw==Ok "Unknown" then model.issued else List.filter (exact >> not) model.issued
                                in if error /= Nothing then (model,[]) else
                                    let current = case model.effects.transaction of
                                            Nothing -> False
                                            Just transaction -> transaction.effectProtocol==protocolId && Just transaction.intent==receivedIntent
                                    in if not current || model.phase==Detached || model.binding/=Just binding then ({model|effects=effects,issued=retained},[]) else
                                    refreshObservations {model|effects=effects,issued=retained}
                        Err _ -> (model,[])
                _ -> (model,[])
encode : Model -> E.Value
encode model = E.object [("phase",E.string (case model.phase of
    Detached -> "Detached"
    Reconciling -> "Reconciling"
    Ready -> "Ready"
    Exhausted -> "Exhausted")),("notificationQueued",E.bool model.notificationQueued),("request",E.string (UInt64.string model.request)),("available",E.bool (available model)),("reconnecting",E.bool model.reconnecting),("effects",Effects.encode model.effects),("status",E.string (status model)),("recoveryFailure",Maybe.map (recoveryNotice >> E.string) model.recoveryFailure |> Maybe.withDefault E.null)]

captureGeometry : Model -> Maybe Stamp
captureGeometry model = model.geometry |> Maybe.map (\observed -> Stamp observed.binding observed.context.output observed.context.revision)

geometryRequest : Bool -> Model -> (Model,List Effect)
geometryRequest attach model =
    case (model.binding,UInt64.next model.request) of
        (Just binding,Just request) ->
            if model.phase==Detached || (attach && model.geometryAttachExpected/=Nothing) || (not attach && (model.geometryCaps==Nothing || model.geometryExpected/=Nothing)) then (model,[]) else
            let common=[("protocolVersion",E.int 3),("kind",E.string (if attach then "geometry-attach" else "geometry-facts-request")),("geometryProtocol",E.int 1),("binding",Binding.encode binding),("requestId",E.string (UInt64.string request))]
                payload=if attach then common else common++[("minimumWatermark",E.string (model.geometry |> Maybe.map (.sequence >> UInt64.string) |> Maybe.withDefault "0"))]
            in ({model|request=request,geometryAttachExpected=if attach then Just request else model.geometryAttachExpected,attachNeeded=attach || model.attachNeeded,geometryExpected=if attach then Nothing else Just request},[Send (E.object payload)])
        _ -> (model,[])

geometrySupported : Model -> Bool
geometrySupported model = model.geometryCaps |> Maybe.map .effects |> Maybe.withDefault False

refreshObservations : Model -> (Model,List Effect)
refreshObservations model =
    let (legacy,commands)=refresh {model|notificationQueued=False}
    in if geometrySupported legacy then
        let (geometry,geometryCommands)=geometryRequest False legacy
        in (geometry,commands++geometryCommands)
       else (legacy,commands)

notificationRefresh : Model -> (Model,List Effect)
notificationRefresh model =
    if model.phase==Detached || model.phase==Exhausted then (model,[]) else
    if model.deferNotifications || Effects.pending model.effects || model.expected/=Nothing || model.geometryExpected/=Nothing || model.geometryAttachExpected/=Nothing then ({model|notificationQueued=True},[])
    else refreshObservations model

-- One dirty bit bounds any number of notifications during an in-flight batch.
-- Only admitted responses drain it; rejected/obsolete data never clears it.
drainNotifications : Model -> (Model,List Effect)
drainNotifications model =
    if not model.deferNotifications && model.notificationQueued && model.phase==Ready && not (Effects.pending model.effects) && model.expected==Nothing && model.geometryExpected==Nothing && model.geometryAttachExpected==Nothing then refreshObservations model else (model,[])

resumeNotifications : Model -> (Model,List Effect)
resumeNotifications model = drainNotifications {model|deferNotifications=False}

-- Both the shared controller and this handler check identical current read IDs.
-- This guard precedes every dismissal/cancellation side effect.
matchesUnsent : List (String,Counter) -> Model -> Bool
matchesUnsent observations model =
    let slot kind = case kind of
            "projection-request" -> model.expected
            "geometry-facts-request" -> model.geometryExpected
            "geometry-attach" -> model.geometryAttachExpected
            _ -> Nothing
    in not (List.isEmpty observations) && List.all (\(kind,request) -> slot kind==Just request) observations

canProveUnsent : List UnsentOperation.Key -> Model -> Bool
canProveUnsent operations model =
    let known key = model.binding==Just key.binding
            && List.any (\entry -> entry.binding==key.binding && entry.protocol==key.protocol && entry.intent==key.intent) model.issued
            && Effects.canProveUnsent key.protocol key.intent model.effects
        unique = List.foldl (\key entries -> if List.member key entries then entries else key::entries) [] operations
    in not (List.isEmpty operations) && List.length operations<=16
        && List.length unique==List.length operations && model.phase/=Detached && model.phase/=Exhausted
        && List.all known operations
