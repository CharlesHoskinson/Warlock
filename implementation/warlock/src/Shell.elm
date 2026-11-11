module Shell exposing (receiveWindowWatch, watchWindows, watchAvailable, inspectionAvailable, observationAvailable, canProveUnsent, Model, Msg(..), Phase(..), Effect(..), Stamp, stampKey, capture, stampDecoder, initial, update, encode, status, available, applicationLaunchAvailable, localNotificationPolicyAvailable, notificationServiceAvailable, captureGeometry, resumeNotifications, matchesUnsent)

import WindowObservation
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
type ApplicationAvailability = ApplicationUnavailable | ApplicationLaunchAvailable
type NotificationAvailability = NotificationsUnavailable | NotificationsAvailable
type Stamp = Stamp Binding Counter Counter | ObservedContext Binding Counter Counter
type Msg = ReconciliationFull | RecoveredUnknown Int Effects.Intent | ReservationReleased Bool Binding Int Effects.Intent | Incoming D.Value | Refresh | Reconnect | Ignore | GeometryAttach | GeometryRefresh | Act Stamp Effects.Operation Counter | UnsentObservations (List (String,Counter)) | SupersedeObservations Bool | UnsentOperations (List UnsentOperation.Key) | RegistrationRefused (List UnsentOperation.Key) (List (String,Counter)) | RegistrationAvailable Bool
type Effect = Send E.Value | RestartBackend | ArmPrepared Counter
type alias Model = { windowWatchOperations : Bool, windowWatchExpected : Maybe {request : Counter, revision : Counter}, windowObservationOperations : Bool, windowObservation : Maybe WindowObservation.Snapshot, windowExpected : Maybe Counter, applicationOnly : Bool, localNotificationPolicy : Bool, notificationAvailability : NotificationAvailability, applicationAvailability : ApplicationAvailability, decoderRefusal : Maybe String, reconciliationFull : Bool, effects : Effects.Model, binding : Maybe Binding, request : Counter, expected : Maybe Counter, phase : Phase, reconnecting : Bool, notice : String, geometry : Maybe GeometryProjection.Snapshot, geometryCaps : Maybe GeometryProjection.Capabilities, geometryExpected : Maybe Counter, geometryAttachExpected : Maybe Counter, attachNeeded : Bool, recoveryFailure : Maybe RecoveryFailure, issued : List { binding : Binding, protocol : Int, intent : Effects.Intent }, notificationQueued : Bool, projectionRetryQueued : Bool, transportRefused : Bool, deferNotifications : Bool }
stampKey : Stamp -> String
stampKey stamp = case stamp of
    Stamp binding output revision -> E.encode 0 (Binding.encode binding) ++ ":" ++ UInt64.string output ++ ":" ++ UInt64.string revision
    ObservedContext binding owner revision -> "observed:" ++ E.encode 0 (Binding.encode binding) ++ ":" ++ UInt64.string owner ++ ":" ++ UInt64.string revision
capture : Model -> Maybe Stamp
capture model =
    if model.windowObservationOperations then
        Maybe.map2 (\binding observed -> ObservedContext binding observed.owner observed.revision) model.binding model.windowObservation
    else case (model.binding,model.effects.observed) of
        (Just binding,Just observed) ->
            if Binding.matchesContext observed.context.lifetime observed.context.epoch binding then Just (Stamp binding observed.context.output observed.context.revision) else Nothing
        _ -> Nothing
positive : D.Decoder Counter
positive = UInt64.decoder |> D.andThen (\value -> if value /= UInt64.zero then D.succeed value else D.fail "Zero displayed scope")
stampDecoder : D.Decoder Stamp
stampDecoder = strict ["binding","output","revision"] (D.map3 Stamp (D.field "binding" Binding.decoder) (D.field "output" positive) (D.field "revision" positive))

initial : Model
initial = { windowWatchOperations=False,windowWatchExpected=Nothing,windowObservationOperations=False,windowObservation=Nothing,windowExpected=Nothing, applicationOnly=False, localNotificationPolicy=False, notificationAvailability=NotificationsUnavailable, applicationAvailability=ApplicationUnavailable, decoderRefusal=Nothing, reconciliationFull=False, effects = Effects.empty, binding = Nothing, request = UInt64.zero, expected = Nothing, phase = Detached, reconnecting = True, notice = "Connecting…", geometry=Nothing,geometryCaps=Nothing,geometryExpected=Nothing,geometryAttachExpected=Nothing,attachNeeded=False,issued=[],notificationQueued=False,projectionRetryQueued=False,transportRefused=False,deferNotifications=False,recoveryFailure=Nothing }
strict : List String -> D.Decoder a -> D.Decoder a
strict fields decoder = D.keyValuePairs D.value |> D.andThen (\pairs -> if List.sort (List.map Tuple.first pairs) == List.sort fields then decoder else D.fail "Unexpected fields")
version : D.Decoder ()
version = D.field "protocolVersion" D.int |> D.andThen (\v -> if v == 3 then D.succeed () else D.fail "Protocol version")
-- Diagnostics are separate from the authority, request and presentation state.
rejectEnvelope : D.Value -> Model -> (Model,List Effect)
rejectEnvelope raw model =
    let reason = case D.decodeValue version raw of
            Err _ -> "Native envelope rejected: missing or unsupported protocol version."
            Ok _ -> "Native envelope rejected: malformed fields."
    in rejectReason reason model

rejectReason : String -> Model -> (Model,List Effect)
rejectReason reason model = ({model | decoderRefusal=Just reason},[])

refresh : Model -> (Model,List Effect)
refresh model =
    if model.windowObservationOperations then refreshWindows model else
    if model.applicationOnly then (model,[]) else
    case ( model.binding, UInt64.next model.request ) of
        (Just binding,Just request) ->
            if model.phase == Detached || model.transportRefused then (model,[]) else
                ({model | request = request, expected = Just request, projectionRetryQueued=False, phase = Reconciling},[Send (E.object [("protocolVersion",E.int 3),("kind",E.string "projection-request"),("binding",Binding.encode binding),("requestId",E.string (UInt64.string request))])])
        _ -> ({model | phase = Exhausted, expected = Nothing, projectionRetryQueued=False, notice = "Restart the shell to continue."},[])
disconnect : Model -> Model
disconnect model =
    let (effects,_,_) = Effects.apply (E.object [("kind",E.string "disconnect")]) model.effects
    in {model | windowWatchOperations=False,windowWatchExpected=Nothing,windowObservationOperations=False,windowObservation=Nothing,windowExpected=Nothing,applicationOnly=False, localNotificationPolicy=False, notificationAvailability=NotificationsUnavailable, applicationAvailability=ApplicationUnavailable, effects = effects, expected = Nothing, geometry=Nothing,geometryCaps=Nothing,geometryExpected=Nothing,geometryAttachExpected=Nothing, attachNeeded=False, notificationQueued=False,projectionRetryQueued=False,transportRefused=False,deferNotifications=False, phase = Detached, reconnecting = False, notice = Maybe.map recoveryNotice model.recoveryFailure |> Maybe.withDefault "Connection lost. Reconnect to continue."}
available : Model -> Bool
available model = not model.applicationOnly && not model.reconciliationFull && not model.transportRefused && model.phase == Ready && not model.attachNeeded && not (Effects.pending model.effects) && model.geometryAttachExpected==Nothing && (not (model.geometryCaps |> Maybe.map .effects |> Maybe.withDefault False) || (model.geometryExpected==Nothing && model.geometry/=Nothing))
applicationLaunchAvailable : Model -> Bool
applicationLaunchAvailable model =
    model.applicationOnly && model.applicationAvailability==ApplicationLaunchAvailable && model.binding/=Nothing && model.phase/=Detached && model.phase/=Exhausted && not model.transportRefused && not model.reconciliationFull

localNotificationPolicyAvailable : Model -> Bool
localNotificationPolicyAvailable model =
    model.localNotificationPolicy && model.applicationOnly && model.binding/=Nothing && model.phase/=Detached && model.phase/=Exhausted && not model.transportRefused && not model.reconciliationFull

-- The full native attachment keeps its existing notification route. An
-- application-only attachment needs its separate, strictly decoded capability.
notificationServiceAvailable : Model -> Bool
notificationServiceAvailable model =
    model.binding/=Nothing && model.phase/=Detached && model.phase/=Exhausted && not model.transportRefused && not model.reconciliationFull
        && (not model.applicationOnly || model.notificationAvailability==NotificationsAvailable)

type alias ApplicationAttachment = { binding : Binding, application : ApplicationAvailability, local : Bool, notifications : NotificationAvailability, observations : (Bool,Bool) }

applicationAttachment : D.Decoder ApplicationAttachment
applicationAttachment =
    D.keyValuePairs D.value |> D.andThen (\pairs ->
        let hasAvailability = List.member "applicationOperations" (List.map Tuple.first pairs)
            hasLocal = List.member "localOperations" (List.map Tuple.first pairs)
            hasObservations = List.member "windowObservationOperations" (List.map Tuple.first pairs)
            hasNotifications = List.member "notificationOperations" (List.map Tuple.first pairs)
            fields = ["protocolVersion","kind","binding","nativeOperations"] ++ (if hasAvailability then ["applicationOperations"] else []) ++ (if hasLocal then ["localOperations"] else []) ++ (if hasNotifications then ["notificationOperations"] else []) ++ (if hasObservations then ["windowObservationOperations"] else [])
            availability =
                if hasAvailability then
                    D.field "applicationOperations" (D.list D.string |> D.andThen (\operations ->
                        case operations of
                            [] -> D.succeed ApplicationUnavailable
                            ["application-launch"] -> D.succeed ApplicationLaunchAvailable
                            _ -> D.fail "Application operations unavailable"))
                else D.succeed ApplicationUnavailable
            local =
                if hasLocal && hasAvailability then
                    D.field "localOperations" (D.list D.string |> D.andThen (\operations -> if operations==["notification-policy"] then D.succeed True else D.fail "Local operations unavailable"))
                else if hasLocal then D.fail "Explicit application capabilities required"
                else D.succeed False
            notifications =
                if hasNotifications && hasAvailability then
                    D.field "notificationOperations" (D.list D.string |> D.andThen (\operations ->
                        case operations of
                            [] -> D.succeed NotificationsUnavailable
                            ["notification-read","notification-action"] -> D.succeed NotificationsAvailable
                            _ -> D.fail "Notification operations unavailable"))
                else if hasNotifications then D.fail "Explicit application capabilities required"
                else D.succeed NotificationsUnavailable
            observations =
                if hasObservations && hasAvailability then
                    D.field "windowObservationOperations" (D.list D.string |> D.andThen (\operations -> if operations==["window-read"] then D.succeed (True,False) else if operations==["window-read","window-watch"] then D.succeed (True,True) else if List.isEmpty operations then D.succeed (False,False) else D.fail "Window observation operations"))
                else if hasObservations then D.fail "Explicit application capabilities required" else D.succeed (False,False)
        in strict fields
            (D.map7 (\_ binding _ capability localPolicy notificationCapability observationCapability -> {binding=binding,application=capability,local=localPolicy,notifications=notificationCapability,observations=observationCapability}) version (D.field "binding" Binding.decoder)
                (D.field "nativeOperations" (D.list D.string |> D.andThen (\operations -> if List.isEmpty operations then D.succeed () else D.fail "Native operations unavailable")))
                availability local notifications observations))
status : Model -> String
status model =
    if model.reconciliationFull then "Window recovery history is full. Restart the shell to continue." else
    if model.transportRefused then "Window transport is full or unavailable. Waiting for a verified output or capacity update." else
    case model.effects.transaction |> Maybe.map .status of
        Just Effects.Pending -> "Applying window change…"
        Just Effects.Unknown -> model.notice ++ " The last request could not be confirmed."
        Just Effects.Refused -> model.notice ++ " The window change was refused."
        _ -> model.notice
update : Msg -> Model -> (Model,List Effect)
update msg model =
    case msg of
        ReconciliationFull -> ({model|reconciliationFull=True,transportRefused=True},[])
        RecoveredUnknown protocolId intent ->
            case Effects.recoverUnknown protocolId intent model.effects of
                Err _ -> (model,[])
                Ok effects -> ({model|effects=effects,notice="The previous window change could not be confirmed."},[])
        ReservationReleased preserveShared oldBinding protocolId intent ->
            ({model | effects=if preserveShared then model.effects else Effects.releaseUnknown protocolId intent model.effects,issued=List.filter (\entry -> not (entry.binding==oldBinding && entry.protocol==protocolId && entry.intent==intent)) model.issued,notice="Previous request remains unconfirmed. Choose a new window action."},[])
        Refresh -> if model.phase == Detached || Effects.pending model.effects then (model,[]) else if geometrySupported model then notificationRefresh model else refresh model
        Reconnect ->
            if model.phase == Detached && not model.reconnecting then ({model | reconnecting = True, notice = "Reconnecting…"},[RestartBackend]) else (model,[])
        SupersedeObservations reissue ->
            if model.windowObservationOperations then
                let retired={model|windowWatchExpected=Nothing,windowExpected=Nothing,windowObservation=Nothing}
                in if reissue then refreshWindows retired else (retired,[])
            else if model.applicationOnly || model.phase==Detached || model.phase==Exhausted || model.binding==Nothing then (model,[]) else
                let attach = model.attachNeeded || model.geometryAttachExpected/=Nothing
                    retired = {model|expected=Nothing,geometryExpected=Nothing,geometryAttachExpected=Nothing,projectionRetryQueued=False,phase=Reconciling,notificationQueued=True,deferNotifications=False}
                in if not reissue then (retired,[]) else
                    let (fresh,commands)=refreshObservations retired
                        (attached,attachCommands)=if attach then geometryRequest True fresh else (fresh,[])
                    in (attached,commands++attachCommands)
        RegistrationRefused operations observations ->
            let keys = List.foldl (\key unique -> if List.member key unique then unique else key::unique) [] operations
                proven = List.filter (\key -> canProveUnsent [key] model) keys
                matches key entry = entry.binding==key.binding && entry.protocol==key.protocol && entry.intent==key.intent
                effects = List.foldl (\key state -> Effects.locallyRefuseUnsent key.protocol key.intent state) model.effects proven
                has kind slot = List.any (\(name,id) -> name==kind && slot==Just id) observations
                retired = {model|effects=effects,issued=List.filter (\entry -> not (List.any (\key -> matches key entry) proven)) model.issued,
                    windowWatchExpected=if has "window-watch" (Maybe.map .request model.windowWatchExpected) then Nothing else model.windowWatchExpected,
                    windowExpected=if has "window-read" model.windowExpected then Nothing else model.windowExpected,
                    expected=if has "projection-request" model.expected then Nothing else model.expected,
                    geometryExpected=if has "geometry-facts-request" model.geometryExpected then Nothing else model.geometryExpected,
                    geometryAttachExpected=if has "geometry-attach" model.geometryAttachExpected then Nothing else model.geometryAttachExpected,
                    attachNeeded=model.attachNeeded || has "geometry-attach" model.geometryAttachExpected,
                    transportRefused=True,notificationQueued=True,deferNotifications=False,phase=if model.phase==Detached || model.phase==Exhausted then model.phase else Reconciling,
                    notice="The request was not sent. Waiting for window transport recovery."}
            in (retired,[])
        RegistrationAvailable reissue ->
            if not model.transportRefused then (model,[]) else
                let recovered = {model|transportRefused=False}
                in if not reissue || recovered.phase==Detached || recovered.phase==Exhausted || Effects.pending recovered.effects || recovered.expected/=Nothing || recovered.geometryExpected/=Nothing || recovered.geometryAttachExpected/=Nothing then (recovered,[]) else if recovered.windowObservationOperations then refreshWindows recovered else refreshObservations recovered
        UnsentOperations operations ->
            if not (canProveUnsent operations model) then (model,[]) else
                let matches key entry = entry.binding==key.binding && entry.protocol==key.protocol && entry.intent==key.intent
                    effects = List.foldl (\key state -> Effects.locallyRefuseUnsent key.protocol key.intent state) model.effects operations
                    updated = {model|effects=effects,issued=List.filter (\entry -> not (List.any (\key -> matches key entry) operations)) model.issued,notice="The request was not sent. Choose again."}
                in resumeNotifications updated
        UnsentObservations observations ->
            let valid = matchesUnsent observations model
                contains kind = List.any (\(name,_) -> name==kind) observations
                cleared = {model|windowWatchExpected=if contains "window-watch" then Nothing else model.windowWatchExpected,windowExpected=if contains "window-read" then Nothing else model.windowExpected,expected=if contains "projection-request" then Nothing else model.expected,geometryExpected=if contains "geometry-facts-request" then Nothing else model.geometryExpected,geometryAttachExpected=if contains "geometry-attach" then Nothing else model.geometryAttachExpected,notificationQueued=True}
            in if not valid || model.phase==Detached || model.phase==Exhausted then (model,[]) else
                if model.windowObservationOperations then (cleared,[]) else
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
                        Err _ -> rejectEnvelope raw model
                Ok "host-disconnected" ->
                    case D.decodeValue (strict ["protocolVersion","kind"] version) raw of
                        Ok _ -> (disconnect model,[])
                        Err _ -> rejectEnvelope raw model
                Ok "host-refresh" ->
                    case D.decodeValue (strict ["protocolVersion","kind"] version) raw of
                        Ok _ -> notificationRefresh model
                        Err _ -> rejectEnvelope raw model
                Ok "application-attached" ->
                    case D.decodeValue applicationAttachment raw of
                        Ok attached ->
                            if model.phase /= Detached || not model.reconnecting || (model.binding |> Maybe.map (Binding.replaces attached.binding >> not) |> Maybe.withDefault False) then (model,[]) else
                                let detached = disconnect model
                                in refreshWindows {detached | windowObservationOperations=Tuple.first attached.observations,windowWatchOperations=Tuple.second attached.observations,applicationOnly=True,localNotificationPolicy=attached.local,notificationAvailability=attached.notifications,applicationAvailability=attached.application,binding=Just attached.binding,phase=Reconciling,reconnecting=False,recoveryFailure=Nothing,notice="Applications connected. Window controls unavailable."}
                        Err _ -> rejectEnvelope raw model
                Ok "attached" ->
                    case D.decodeValue (D.map2 (\_ binding -> binding) version (D.field "binding" Binding.decoder)) raw of
                        Ok binding ->
                            if model.phase /= Detached || not model.reconnecting || (model.binding |> Maybe.map (Binding.replaces binding >> not) |> Maybe.withDefault False) then (model,[]) else
                                let detached = disconnect model
                                in refresh { detached | binding = Just binding, phase = Reconciling, reconnecting = False, recoveryFailure=Nothing, notice = "Updating window information…" }
                        Err _ -> rejectEnvelope raw model
                Ok "window-watch-result" ->
                    case receiveWindowWatch raw model of
                        Nothing -> (model,[])
                        Just (next,_) -> (next,[])
                Ok "window-observation" ->
                    case D.decodeValue WindowObservation.replyDecoder raw of
                        Err _ -> rejectEnvelope raw model
                        Ok observed ->
                            if not (observationAvailable model) || model.binding/=Just observed.binding || model.windowExpected/=Just observed.request then (model,[]) else
                            case observed.snapshot of
                                Nothing -> ({model|windowExpected=Nothing,windowObservation=Nothing,notice="Window observation unavailable."},[])
                                Just snapshot ->
                                    if model.windowObservation |> Maybe.map (\previous -> previous.owner/=snapshot.owner || UInt64.compare snapshot.revision previous.revision/=GT) |> Maybe.withDefault False then (model,[]) else
                                    ({model|windowExpected=Nothing,windowObservation=Just snapshot,notice="Window observations connected. Native actions unavailable."},[])
                Ok "projection-unavailable" ->
                    let decoder = strict ["protocolVersion","kind","binding","requestId","reason"]
                            (D.map4 (\_ binding request _ -> (binding,request)) version (D.field "binding" Binding.decoder)
                                (D.field "requestId" positive)
                                (D.field "reason" D.string |> D.andThen (\reason -> if reason=="scene-changed" then D.succeed () else D.fail "Projection terminal reason")))
                    in case D.decodeValue decoder raw of
                        Err _ -> rejectEnvelope raw model
                        Ok (binding,request) ->
                            if model.phase==Detached || model.phase==Exhausted || model.binding/=Just binding || model.expected/=Just request then (model,[]) else
                                drainNotifications {model|expected=Nothing,projectionRetryQueued=True,notificationQueued=True,phase=Reconciling}
                Ok "action-projection" ->
                    let decoder = strict ["protocolVersion","kind","binding","requestId","context","scene"] (D.map5 (\_ binding request life epoch -> (binding,request,(life,epoch))) version (D.field "binding" Binding.decoder) (D.field "requestId" UInt64.decoder) (D.at ["context","lifetime"] UInt64.decoder) (D.at ["context","epoch"] UInt64.decoder))
                    in case D.decodeValue decoder raw of
                        Ok (binding,request,(life,epoch)) ->
                            if model.phase == Detached || model.binding /= Just binding || model.expected /= Just request || not (Binding.matchesContext life epoch binding) then (model,[]) else
                                case D.decodeValue (D.map2 (\context scene -> E.object [("kind",E.string "snapshot"),("context",context),("scene",scene)]) (D.field "context" D.value) (D.field "scene" D.value)) raw of
                                    Ok snapshot ->
                                        let (effects,_,error) = Effects.apply snapshot model.effects
                                        in if error/=Nothing then rejectEnvelope raw model else
                                            drainNotifications {model | effects = effects, phase = Ready, expected = Nothing, notice = "Connected"}
                                    Err _ -> rejectEnvelope raw model
                        Err _ -> rejectEnvelope raw model
                Ok "host-geometry-negotiate" ->
                    case D.decodeValue (strict ["protocolVersion","kind"] version) raw of
                        Err _ -> rejectEnvelope raw model
                        Ok _ -> if model.geometryCaps/=Nothing || model.geometryAttachExpected/=Nothing then (model,[]) else geometryRequest True model
                Ok "geometry-unavailable" ->
                    let decoder = strict ["protocolVersion","kind","binding","requestId","reason"]
                            (D.map4 (\_ binding request reason -> {binding=binding,request=request,reason=reason}) version (D.field "binding" Binding.decoder) (D.field "requestId" positive)
                                (D.field "reason" D.string |> D.andThen (\reason -> if String.length reason<=256 then D.succeed reason else D.fail "Geometry refusal reason")))
                    in case D.decodeValue decoder raw of
                        Err _ -> rejectEnvelope raw model
                        Ok refusal -> if model.binding/=Just refusal.binding || model.geometryAttachExpected/=Just refusal.request then (model,[]) else
                            drainNotifications {model|geometryCaps=Just {effects=False,operations=[]},geometry=Nothing,geometryAttachExpected=Nothing,attachNeeded=False,geometryExpected=Nothing}
                Ok "geometry-attached" ->
                    let decoder = strict ["protocolVersion","kind","geometryProtocol","binding","requestId","capabilities"]
                            (D.map5 (\_ _ binding request caps -> {binding=binding,request=request,caps=caps}) version
                                (D.field "geometryProtocol" D.int |> D.andThen (\v -> if v==3 then D.succeed () else D.fail "Geometry protocol"))
                                (D.field "binding" Binding.decoder) (D.field "requestId" positive) (D.field "capabilities" GeometryProjection.capabilitiesDecoder))
                    in case D.decodeValue decoder raw of
                        Ok value -> if model.binding/=Just value.binding || model.geometryAttachExpected/=Just value.request || model.phase==Detached then (model,[]) else geometryRequest False {model|geometryCaps=Just value.caps,geometry=Nothing,geometryAttachExpected=Nothing,attachNeeded=False}
                        Err _ -> rejectEnvelope raw model
                Ok "geometry-facts" ->
                    case model.geometryCaps of
                        Nothing -> rejectReason "Native geometry facts rejected: no negotiated capabilities." model
                        Just caps -> case GeometryProjection.decode caps raw of
                            Err _ -> rejectEnvelope raw model
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
                        Err _ -> rejectEnvelope raw model
                Ok "host-uncertain" ->
                    let decoder=D.oneOf
                            [ strict ["protocolVersion","kind","binding","intent"] (D.map3 (\_ binding intent -> (binding,intent,1)) version (D.field "binding" Binding.decoder) (D.field "intent" D.value))
                            , strict ["protocolVersion","kind","binding","intent","effectProtocol"] (D.map4 (\_ binding intent protocolId -> (binding,intent,protocolId)) version (D.field "binding" Binding.decoder) (D.field "intent" D.value) (D.field "effectProtocol" D.int)) ]
                    in case D.decodeValue decoder raw of
                        Ok (binding,intent,protocolId) ->
                            case D.decodeValue Effects.intentDecoder intent of
                                Err _ -> rejectEnvelope raw model
                                Ok _ ->
                                    if model.binding/=Just binding || model.phase/=Reconciling || (D.decodeValue (D.at ["context","lifetime"] positive) intent |> Result.map (\life -> Binding.sameLifetime life binding))/=Ok True then (model,[]) else
                                        let (effects,_,error)=Effects.apply (E.object [("kind",E.string "recover"),("intent",intent),("effectProtocol",E.int protocolId)]) model.effects
                                        in if error/=Nothing then rejectEnvelope raw model else ({model|effects=effects,notice="The previous window change could not be confirmed."},[])
                        Err _ -> rejectEnvelope raw model
                Ok "effect-outcome" ->
                    if not (NativeOutcome.valid raw) then rejectEnvelope raw model else
                    case D.decodeValue (D.map4 (\_ binding protocolId receipt -> (binding,protocolId,receipt)) version (D.field "binding" Binding.decoder) (D.field "effectProtocol" D.int)
                        (D.map3 (\intent outcome protocolId -> E.object [("kind",E.string "receipt"),("intent",intent),("status",outcome),("effectProtocol",protocolId)]) (D.field "intent" D.value) (D.field "status" D.value) (D.field "effectProtocol" D.value))) raw of
                        Ok (binding,protocolId,receipt) ->
                            let receivedIntent = D.decodeValue (D.field "intent" Effects.intentDecoder) raw |> Result.toMaybe
                                exact entry = entry.binding==binding && entry.protocol==protocolId && Just entry.intent==receivedIntent
                                known = List.any exact model.issued
                            in if not known then (model,[]) else
                                let (effects,_,error) = Effects.apply receipt model.effects
                                    retained = if D.decodeValue (D.field "status" D.string) raw==Ok "Unknown" then model.issued else List.filter (exact >> not) model.issued
                                in if error /= Nothing then rejectEnvelope raw model else
                                    let current = case model.effects.transaction of
                                            Nothing -> False
                                            Just transaction -> transaction.effectProtocol==protocolId && Just transaction.intent==receivedIntent
                                    in if not current || model.phase==Detached || model.binding/=Just binding then ({model|effects=effects,issued=retained},[]) else
                                    refreshObservations {model|effects=effects,issued=retained}
                        Err _ -> rejectEnvelope raw model
                Ok _ -> (model,[])
                Err _ -> rejectEnvelope raw model
encode : Model -> E.Value
encode model = E.object [("decoderRefusal",Maybe.map E.string model.decoderRefusal |> Maybe.withDefault E.null),("phase",E.string (case model.phase of
    Detached -> "Detached"
    Reconciling -> "Reconciling"
    Ready -> "Ready"
    Exhausted -> "Exhausted")),("transportRefused",E.bool model.transportRefused),("notificationQueued",E.bool model.notificationQueued),("request",E.string (UInt64.string model.request)),("available",E.bool (available model)),("reconnecting",E.bool model.reconnecting),("effects",Effects.encode model.effects),("status",E.string (status model)),("recoveryFailure",Maybe.map (recoveryNotice >> E.string) model.recoveryFailure |> Maybe.withDefault E.null)]

captureGeometry : Model -> Maybe Stamp
captureGeometry model = model.geometry |> Maybe.map (\observed -> Stamp observed.binding observed.context.output observed.context.revision)

geometryRequest : Bool -> Model -> (Model,List Effect)
geometryRequest attach model =
    if model.applicationOnly || model.transportRefused then (model,[]) else
    case (model.binding,UInt64.next model.request) of
        (Just binding,Just request) ->
            if model.phase==Detached || (attach && model.geometryAttachExpected/=Nothing) || (not attach && (model.geometryCaps==Nothing || model.geometryExpected/=Nothing)) then (model,[]) else
            let common=[("protocolVersion",E.int 3),("kind",E.string (if attach then "geometry-attach" else "geometry-facts-request")),("geometryProtocol",E.int 3),("binding",Binding.encode binding),("requestId",E.string (UInt64.string request))]
                payload=if attach then common else common++[("minimumWatermark",E.string (model.geometry |> Maybe.map (.sequence >> UInt64.string) |> Maybe.withDefault "0"))]
            in ({model|request=request,geometryAttachExpected=if attach then Just request else model.geometryAttachExpected,attachNeeded=attach || model.attachNeeded,geometryExpected=if attach then Nothing else Just request},[Send (E.object payload)])
        _ -> (model,[])

geometrySupported : Model -> Bool
geometrySupported model = model.geometryCaps |> Maybe.map .effects |> Maybe.withDefault False

refreshObservations : Model -> (Model,List Effect)
refreshObservations model =
    if model.applicationOnly || model.transportRefused then (model,[]) else
    let (legacy,commands)=refresh {model|notificationQueued=False}
    in if legacy.attachNeeded then
        let (attached,attachCommands)=geometryRequest True legacy
        in (attached,commands++attachCommands)
       else if geometrySupported legacy then
        let (geometry,geometryCommands)=geometryRequest False legacy
        in (geometry,commands++geometryCommands)
       else (legacy,commands)

notificationRefresh : Model -> (Model,List Effect)
notificationRefresh model =
    if model.applicationOnly || model.phase==Detached || model.phase==Exhausted || model.transportRefused then (model,[]) else
    if model.deferNotifications || Effects.pending model.effects || model.expected/=Nothing || model.geometryExpected/=Nothing || model.geometryAttachExpected/=Nothing then ({model|notificationQueued=True},[])
    else refreshObservations model

-- One dirty bit bounds any number of notifications during an in-flight batch.
-- Only admitted responses drain it; rejected/obsolete data never clears it.
drainNotifications : Model -> (Model,List Effect)
drainNotifications model =
    if model.projectionRetryQueued then
        if model.phase==Detached || model.phase==Exhausted || model.binding==Nothing then ({model|projectionRetryQueued=False},[])
        else if model.transportRefused || model.deferNotifications || Effects.pending model.effects || model.expected/=Nothing || model.geometryAttachExpected/=Nothing then (model,[])
        else refresh model
    else if not model.transportRefused && not model.deferNotifications && model.notificationQueued && model.phase==Ready && not (Effects.pending model.effects) && model.expected==Nothing && model.geometryExpected==Nothing && model.geometryAttachExpected==Nothing then refreshObservations model else (model,[])

resumeNotifications : Model -> (Model,List Effect)
resumeNotifications model = drainNotifications {model|deferNotifications=False}

-- Both the shared controller and this handler check identical current read IDs.
-- This guard precedes every dismissal/cancellation side effect.
matchesUnsent : List (String,Counter) -> Model -> Bool
matchesUnsent observations model =
    let slot kind = case kind of
            "window-watch" -> Maybe.map .request model.windowWatchExpected
            "window-read" -> model.windowExpected
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

-- This does not participate in available/native effect admission.
observationAvailable : Model -> Bool
observationAvailable model = model.windowObservationOperations && model.applicationOnly && model.binding/=Nothing
    && model.phase/=Detached && model.phase/=Exhausted && not model.transportRefused && not model.reconciliationFull
inspectionAvailable : Model -> Bool
inspectionAvailable model = observationAvailable model && model.windowExpected==Nothing && model.windowObservation/=Nothing
refreshWindows : Model -> (Model,List Effect)
refreshWindows model =
    if not (observationAvailable model) || model.windowExpected/=Nothing then (model,[]) else
    case (model.binding,UInt64.next model.request) of
        (Just binding,Just request) ->
            ({model|request=request,windowWatchExpected=Nothing,windowExpected=Just request},[Send (E.object [("protocolVersion",E.int 3),("kind",E.string "window-read"),("binding",Binding.encode binding),("requestId",E.string (UInt64.string request))])])
        _ -> ({model|phase=Exhausted,windowWatchExpected=Nothing,windowExpected=Nothing,windowObservation=Nothing},[])

watchAvailable : Model -> Bool
watchAvailable model = model.windowWatchOperations && inspectionAvailable model
watchWindows : Counter -> Model -> (Model,List Effect)
watchWindows revision model =
    if not (watchAvailable model) || model.windowWatchExpected/=Nothing || Maybe.map .revision model.windowObservation/=Just revision then (model,[]) else
    case (model.binding,UInt64.next model.request) of
        (Just binding,Just request) ->
            ({model|request=request,windowWatchExpected=Just {request=request,revision=revision}},[Send (E.object [("protocolVersion",E.int 3),("kind",E.string "window-watch"),("binding",Binding.encode binding),("requestId",E.string (UInt64.string request)),("observedRevision",E.string (UInt64.string revision))])])
        _ -> ({model|phase=Exhausted,windowWatchExpected=Nothing},[])

-- The same accepted transition serves ordinary Shell ingress and the current
-- Desktop watch scope. A receipt proves only this read's completion.
receiveWindowWatch : D.Value -> Model -> Maybe (Model,WindowObservation.WatchReply)
receiveWindowWatch raw model =
    case D.decodeValue WindowObservation.watchReplyDecoder raw of
        Err _ -> Nothing
        Ok receipt ->
            case (model.windowWatchExpected,model.windowObservation) of
                (Just pending,Just previous) ->
                    if not (watchAvailable model) || model.binding/=Just receipt.binding || pending.request/=receipt.request
                        || pending.revision/=receipt.observedRevision || previous.revision/=pending.revision then Nothing else
                    case receipt.snapshot of
                        Nothing -> Just ({model|windowWatchExpected=Nothing},receipt)
                        Just current ->
                            if previous.owner/=current.owner || WindowObservation.sameContent previous current then Nothing else
                                Just ({model|windowWatchExpected=Nothing,windowObservation=Just current},receipt)
                _ -> Nothing
