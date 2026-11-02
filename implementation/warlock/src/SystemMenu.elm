module SystemMenu exposing (Model, Snapshot, Intent, Operation(..), ReceiptPhase(..), NetworkPermission(..), PowerCapability(..), SessionState(..), sessionStateName, powerCapabilityLabel, initial, decoder, observe, reconcile, name, code, confirmed, supported, propose, receive, intent, encode)

import Json.Decode as D
import Json.Encode as E
import UInt64 exposing (Counter)

type Operation = Volume | Mute | Network | Suspend | Reboot | PowerOff | Lock | Logout

-- Receipt lifecycle is independent of the user confirmation prompt. Unknown
-- retains the same request/intent reservation and never grants replay.
type ReceiptPhase = AwaitingReceipt | UnconfirmedReceipt
type NetworkPermission = NetworkYes | NetworkNo | NetworkAuth
type PowerCapability = PowerYes | PowerNo | PowerUnavailable | PowerChallenge

-- Native session text remains open and bounded by the decoder. Only the
-- closing classification participates in frontend logout policy.
type SessionState = SessionClosing | OtherSessionState String

sessionStateName : SessionState -> String
sessionStateName state = case state of
    SessionClosing -> "closing"
    OtherSessionState observed -> observed

networkPermissionDecoder : D.Decoder NetworkPermission
networkPermissionDecoder = D.string |> D.andThen (\value -> case value of
    "yes" -> D.succeed NetworkYes
    "no" -> D.succeed NetworkNo
    "auth" -> D.succeed NetworkAuth
    _ -> D.fail "Native network permission")

powerCapabilityDecoder : D.Decoder PowerCapability
powerCapabilityDecoder = D.string |> D.andThen (\value -> case value of
    "yes" -> D.succeed PowerYes
    "no" -> D.succeed PowerNo
    "na" -> D.succeed PowerUnavailable
    "challenge" -> D.succeed PowerChallenge
    _ -> D.fail "Native power capability")

powerCapabilityLabel : PowerCapability -> String
powerCapabilityLabel capability = case capability of
    PowerYes -> "available"
    PowerChallenge -> "authorization required"
    _ -> "unavailable"

type alias Intent = { service : Counter, revision : Counter, operation : Operation, value : Int }
type alias Snapshot =
    { service : Counter, revision : Counter
    , volume : Maybe { percent : Int, muted : Bool, label : String }
    , network : Maybe { enabled : Bool, state : String, permission : NetworkPermission }
    , power : Maybe { suspend : PowerCapability, reboot : PowerCapability, poweroff : PowerCapability }
    , session : Maybe { name : String, state : SessionState, locked : Bool }
    }
type alias Model = { snapshot : Maybe Snapshot, pending : Maybe { request : Counter, intent : Intent, receipt : ReceiptPhase }, spent : List Intent, notice : String }
initial : Model
initial = {snapshot=Nothing,pending=Nothing,spent=[],notice="Loading system state…"}
strict fields child = D.keyValuePairs D.value |> D.andThen (\pairs -> if List.sort (List.map Tuple.first pairs)==List.sort fields then child else D.fail "System fields")
positive = UInt64.decoder |> D.andThen (\value -> if value==UInt64.zero then D.fail "System identity" else D.succeed value)
bounded limit = D.string |> D.andThen (\value -> if String.length value<=limit && not (String.any (\c -> Char.toCode c<32) value) then D.succeed value else D.fail "System text")
decoder : D.Decoder Snapshot
decoder = strict ["service","revision","volume","network","power","session"] (D.map6 Snapshot
    (D.field "service" positive) (D.field "revision" positive)
    (D.field "volume" (D.nullable (strict ["percent","muted","label"] (D.map3 (\percent muted label -> {percent=percent,muted=muted,label=label})
        (D.field "percent" (D.int |> D.andThen (\value -> if value>=0 && value<=1600 then D.succeed value else D.fail "Native volume"))) (D.field "muted" D.bool) (D.field "label" (bounded 128))))))
    (D.field "network" (D.nullable (strict ["enabled","state","permission"] (D.map3 (\enabled state permission -> {enabled=enabled,state=state,permission=permission}) (D.field "enabled" D.bool) (D.field "state" (bounded 32)) (D.field "permission" networkPermissionDecoder)))))
    (D.field "power" (D.nullable (strict ["suspend","reboot","poweroff"] (D.map3 (\suspend reboot poweroff -> {suspend=suspend,reboot=reboot,poweroff=poweroff}) (D.field "suspend" powerCapabilityDecoder) (D.field "reboot" powerCapabilityDecoder) (D.field "poweroff" powerCapabilityDecoder)))))
    (D.field "session" (D.nullable (strict ["name","state","locked"] (D.map3 (\ownerName state locked -> {name=ownerName,state=state,locked=locked}) (D.field "name" (bounded 128)) (D.field "state" (bounded 32 |> D.map (\observed -> if observed=="closing" then SessionClosing else OtherSessionState observed))) (D.field "locked" D.bool))))))
observe current model =
    let admitted=case model.snapshot of
            Nothing -> True
            Just old -> current.service==old.service && (UInt64.compare current.revision old.revision==GT || current==old)
    in if not admitted then model else {model | snapshot=Just current,notice=if model.pending/=Nothing then model.notice else "Current system state. Unavailable controls cannot be changed."}
intent snapshot operation value = {service=snapshot.service,revision=snapshot.revision,operation=operation,value=value}
code operation = case operation of
    Volume -> "volume-set"
    Mute -> "volume-mute"
    Network -> "network-enable"
    Suspend -> "suspend"
    Reboot -> "reboot"
    PowerOff -> "poweroff"
    Lock -> "session-lock"
    Logout -> "session-logout"
name operation = case operation of
    Volume -> "Volume"
    Mute -> "Mute"
    Network -> "Network"
    Suspend -> "Suspend"
    Reboot -> "Restart"
    PowerOff -> "Shut down"
    Lock -> "Lock session"
    Logout -> "Log out"
confirmed value = List.member value.operation [Reboot,PowerOff,Logout] || (value.operation==Network && value.value==0)
supported value model = case model.snapshot of
    Nothing -> False
    Just current ->
        value.service==current.service && value.revision==current.revision && not (List.member value model.spent) &&
        (case value.operation of
            Volume -> current.volume |> Maybe.map (\v -> value.value>=0 && value.value<=100 && value.value/=v.percent) |> Maybe.withDefault False
            Mute -> current.volume |> Maybe.map (\v -> List.member value.value [0,1] && (value.value==1)/=v.muted) |> Maybe.withDefault False
            Network -> current.network |> Maybe.map (\v -> List.member v.permission [NetworkYes,NetworkAuth] && List.member value.value [0,1] && (value.value==1)/=v.enabled) |> Maybe.withDefault False
            Suspend -> current.power |> Maybe.map (\v -> List.member v.suspend [PowerYes,PowerChallenge] && value.value==0) |> Maybe.withDefault False
            Reboot -> current.power |> Maybe.map (\v -> List.member v.reboot [PowerYes,PowerChallenge] && value.value==0) |> Maybe.withDefault False
            PowerOff -> current.power |> Maybe.map (\v -> List.member v.poweroff [PowerYes,PowerChallenge] && value.value==0) |> Maybe.withDefault False
            Lock -> current.session |> Maybe.map (\v -> not v.locked && value.value==0) |> Maybe.withDefault False
            Logout -> current.session |> Maybe.map (\v -> case v.state of
                SessionClosing -> False
                OtherSessionState _ -> value.value==0) |> Maybe.withDefault False)
encode value = E.object [("service",E.string (UInt64.string value.service)),("revision",E.string (UInt64.string value.revision)),("operation",E.string (code value.operation)),("value",E.int value.value)]
propose request value model =
    if model.pending/=Nothing || not (supported value model) then (model,Nothing) else
        ({model | pending=Just {request=request,intent=value,receipt=AwaitingReceipt},spent=List.take 128 (value::model.spent),notice= name value.operation++": waiting for native result…"},Just (encode value))
receive request status snapshot model = case model.pending of
    Nothing -> model
    Just pending ->
        if request/=pending.request || not (List.member status ["Committed","Submitted","Refused","Unknown"]) || snapshot.service/=pending.intent.service then model else
        let next=observe snapshot model
            notice=name pending.intent.operation++(if status=="Committed" then ": change observed." else if status=="Submitted" then ": request accepted by the native service." else if status=="Refused" then ": refused or no longer available. Refresh before choosing again." else ": not confirmed. Refresh only reads state; the request will not be repeated.")
        in if next.snapshot/=Just snapshot then model else {next | pending=if status=="Unknown" then Just {pending | receipt=UnconfirmedReceipt} else Nothing,notice=notice}
reconcile snapshot model =
    let next=observe snapshot model
    in case next.pending of
        Nothing -> next
        Just pending ->
            if next.snapshot==Just snapshot && UInt64.compare snapshot.revision pending.intent.revision==GT then {next | pending=Nothing,notice="System state refreshed. The previous request will not be repeated."} else next
