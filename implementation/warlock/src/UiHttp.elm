module UiHttp exposing (Model, Msg(..), Event(..), Effect(..), controller, renderer, controllerEffects, rendererEffects, enqueue, enqueueEffects, update, updateEffects, problem, stop, stopEffects, gateway, popup, popupEffects, enqueueProposal, enqueueProposalEffects, tryEnqueueConsumed, tryEnqueueConsumedEffects, EnqueueConsumedResult(..), RequestKind(..), RequestId)

import Http
import Json.Decode as D
import Json.Encode as E
import NativePreviewProposalIngress as Ingress
import NativePreviewRealm as Realm
import UInt64
import Process
import Task

-- Only compiled roots select these roles. Flags and wire data cannot select a
-- destination or privileged source. Each root runs on its own trusted origin.
type Role = Controller | Renderer | PopupRole
type RequestKind = ControllerCommit | RendererAction | PopupProposal | PopupConsumed
type RequestId = RequestId UInt64.Counter
type EnqueueConsumedResult = Queued | AlreadyQueued | Deferred | Stopped
type alias Request = { id : RequestId, kind : RequestKind, body : E.Value, ticket : Maybe Ingress.AcceptedTicket }

-- Transport lifecycle classification is retained independently of the exact
-- user-facing notice. Explicit stops keep their supplied text byte-for-byte.
type Failure
    = EventTransportUnavailable
    | EventTooLarge
    | EventInvalidJson
    | EventSourceRejected
    | EventGatewayMismatch
    | DeliveryUnconfirmed
    | DeliveryUnexpected
    | CapacityExceeded
    | ExplicitStop String

failureText : Failure -> String
failureText failure =
    case failure of
        EventTransportUnavailable -> "UI event transport unavailable. Actions were not retried."
        EventTooLarge -> "UI event exceeds the bounded profile."
        EventInvalidJson -> "UI event is not valid JSON."
        EventSourceRejected -> "UI event source is not allowed for this role."
        EventGatewayMismatch -> "UI event does not match the recorded gateway."
        DeliveryUnconfirmed -> "UI delivery is unconfirmed. The action will not be repeated."
        DeliveryUnexpected -> "Unexpected UI delivery response."
        CapacityExceeded -> "UI transport capacity exceeded. No action was retried."
        ExplicitStop reason -> reason
type Model = Model
    { role : Role
    , pending : List Request
    , active : Maybe Request
    , counter : UInt64.Counter
    , polling : Bool
    , failed : Maybe Failure
    }
type Msg = Poll | Polled (Result Http.Error String) | Posted (Result Http.Error String) | PostedFor RequestId RequestKind (Result Http.Error String)
type Event = Incoming D.Value | Lost String | TransportConsumedCompleted Ingress.AcceptedTicket

-- Data descriptions used by the SAME production transition and interpreter.
-- No public interpreter or Role constructor is added. These values neither
-- select native authority nor turn local HTTP completion into a receipt.
type Effect
    = ReadEvents
    | SendController E.Value
    | SendRenderer E.Value
    | SendRequest RequestId RequestKind E.Value
    | CancelEvents
    | CancelPost
    | WakeAfter Float Msg

interpret : List Effect -> Cmd Msg
interpret descriptions =
    let command description = case description of
            ReadEvents -> poll
            SendController _ -> Cmd.none
            SendRenderer _ -> Cmd.none
            SendRequest requestId kind value -> post requestId kind value
            CancelEvents -> Http.cancel "warlock-ui-events"
            CancelPost -> Http.cancel "warlock-ui-post"
            WakeAfter duration message -> Process.sleep duration |> Task.perform (\_ -> message)
    in Cmd.batch (List.map command descriptions)

interpreted : (Model,List Effect,Maybe Event) -> (Model,Cmd Msg,Maybe Event)
interpreted (model,descriptions,event) = (model,interpret descriptions,event)

sendEffect : Request -> Effect
sendEffect request = SendRequest request.id request.kind request.body

controller : (Model,Cmd Msg)
controller = start Controller

renderer : (Model,Cmd Msg)
renderer = start Renderer

popup : (Model,Cmd Msg)
popup = start PopupRole

popupEffects : (Model,List Effect)
popupEffects = startEffects PopupRole

controllerEffects : (Model,List Effect)
controllerEffects = startEffects Controller

rendererEffects : (Model,List Effect)
rendererEffects = startEffects Renderer

startEffects : Role -> (Model,List Effect)
startEffects role = (Model {role=role,pending=[],active=Nothing,counter=UInt64.zero,polling=True,failed=Nothing},[ReadEvents])

start : Role -> (Model,Cmd Msg)
start role =
    let (model,descriptions) = startEffects role
    in (model,interpret descriptions)

problem : Model -> Maybe String
problem (Model model) = Maybe.map failureText model.failed

reject : Failure -> Model -> Model
reject reason ((Model model) as current) =
    if model.failed/=Nothing then current else Model {model | failed=Just reason}

utf8Length : String -> Int
utf8Length = String.foldl (\char count -> let code=Char.toCode char in count+(if code<128 then 1 else if code<2048 then 2 else if code<65536 then 3 else 4)) 0

fits : Int -> String -> Bool
fits limit text = String.length text<=limit && utf8Length text<=limit

-- The nonsimple header is required even on consuming GETs. Cross-origin web
-- content must preflight; the owner denies OPTIONS and never grants CORS.
headers : List Http.Header
headers = [Http.header "X-Warlock-Api" "1"]

response : Bool -> Http.Response String -> Result Http.Error String
response events result =
    case result of
        Http.BadUrl_ url -> Err (Http.BadUrl url)
        Http.Timeout_ -> Err Http.Timeout
        Http.NetworkError_ -> Err Http.NetworkError
        Http.BadStatus_ metadata _ -> Err (Http.BadStatus metadata.statusCode)
        Http.GoodStatus_ metadata body ->
            if metadata.statusCode==204 && String.isEmpty body then Ok body
            else if events && metadata.statusCode==200 && not (String.isEmpty body) then Ok body
            else Err (Http.BadBody "Unexpected UI response status or body")

poll : Cmd Msg
poll = Http.request
    {method="GET",headers=headers,url="/events",body=Http.emptyBody
    ,expect=Http.expectStringResponse Polled (response True),timeout=Just 5000,tracker=Just "warlock-ui-events"}

post : RequestId -> RequestKind -> E.Value -> Cmd Msg
post requestId kind value = Http.request
    {method="POST",headers=headers,url=case kind of
        ControllerCommit -> "/commit"
        RendererAction -> "/actions"
        PopupProposal -> "/preview-proposals"
        PopupConsumed -> "/preview-consumed"
    ,body=Http.jsonBody value,expect=Http.expectStringResponse (PostedFor requestId kind) (response False),timeout=Just 5000,tracker=Just "warlock-ui-post"}

-- Existing callers keep their public API. All policy/state decisions above
-- the interpreter are made once in the pure *Effects functions below.
stop : String -> Model -> (Model,Cmd Msg,Maybe Event)
stop reason model = interpreted (stopEffects reason model)

enqueue : E.Value -> Model -> (Model,Cmd Msg,Maybe Event)
enqueue value model = interpreted (enqueueEffects value model)

update : Msg -> Model -> (Model,Cmd Msg,Maybe Event)
update message model = interpreted (updateEffects message model)

failedEffects : Failure -> Model -> (Model,List Effect,Maybe Event)
failedEffects reason model =
    if problem model/=Nothing then (model,[],Nothing) else
        (reject reason model,[CancelEvents,CancelPost],Just (Lost (failureText reason)))

stopEffects : String -> Model -> (Model,List Effect,Maybe Event)
stopEffects reason = failedEffects (ExplicitStop reason)

enqueueEffects : E.Value -> Model -> (Model,List Effect,Maybe Event)
enqueueEffects value ((Model model) as current) =
    enqueueRequest (if model.role==Controller then ControllerCommit else RendererAction) value Nothing current

enqueueProposal : E.Value -> Model -> (Model,Cmd Msg,Maybe Event)
enqueueProposal value model = interpreted (enqueueProposalEffects value model)

-- Compare exactly the encoded bytes that the HTTP interpreter will send.
-- A validated proposal is data; this check never allocates native purpose.
validProposal : E.Value -> Bool
validProposal value =
    let exact fields decoder = D.keyValuePairs D.value |> D.andThen (\pairs ->
            if List.sort (List.map Tuple.first pairs)==List.sort fields then decoder else D.fail "Exact proposal fields")
        command = exact ["kind","binding"] (D.map2 Tuple.pair (D.field "kind" D.string) (D.field "binding" D.value))
        row = exact ["identity","commands"] (D.map2 Tuple.pair (D.field "identity" D.string) (D.field "commands" (D.list command)))
        envelope = exact ["previewProtocol","kind","binding","receiverEpoch","entries"]
            (D.map4 (\version kind domain rows -> {version=version,kind=kind,domain=domain,rows=rows})
                (D.field "previewProtocol" D.int) (D.field "kind" D.string) Realm.domainDecoder (D.field "entries" (D.list row)))
    in fits 4096 (E.encode 0 value) && (case D.decodeValue envelope value of
        Ok {version,kind,domain,rows} ->
            case rows of
                [(identity,[(commandKind,binding)])] ->
                    version==3 && kind=="preview-proposals" && commandKind=="reconcile" && fits 512 identity && identity=="binding:" ++ Realm.owner domain && E.encode 0 binding==E.encode 0 (Realm.bindingValue domain)
                _ -> False
        _ -> False)

enqueueProposalEffects : E.Value -> Model -> (Model,List Effect,Maybe Event)
enqueueProposalEffects value ((Model model) as current) =
    if model.failed/=Nothing then (current,[],Nothing)
    else if model.role/=PopupRole then failedEffects (ExplicitStop "Preview transport unavailable for this role.") current
    else if not (validProposal value) then failedEffects (ExplicitStop "Invalid preview proposal.") current
    else
        let requests = Maybe.map (\item -> [item]) model.active |> Maybe.withDefault [] |> (\active -> active ++ model.pending)
            wire = E.encode 0 value
            same request = request.kind==PopupProposal && E.encode 0 request.body==wire
        in if List.any same requests then (current,[],Nothing)
           else enqueueRequest PopupProposal value Nothing current

enqueueRequest : RequestKind -> E.Value -> Maybe Ingress.AcceptedTicket -> Model -> (Model,List Effect,Maybe Event)
enqueueRequest kind value ticket ((Model model) as current) =
    if model.failed/=Nothing then (current,[],Nothing) else
    let limit=if model.role==Controller then 131072 else if kind==PopupConsumed then 32768 else if kind==PopupProposal then 4096 else 8192
        retained=List.length model.pending+(case model.active of
            Nothing -> 0
            Just _ -> 1)
    in if not (fits limit (E.encode 0 value)) || retained>=16 then failedEffects CapacityExceeded current else
        case UInt64.next model.counter of
            Nothing -> failedEffects CapacityExceeded current
            Just nextId ->
                let request = {id=RequestId nextId,kind=kind,body=value,ticket=ticket}
                in case model.active of
                    Nothing -> (Model {model | counter=nextId,active=Just request},[sendEffect request],Nothing)
                    Just _ -> (Model {model | counter=nextId,pending=model.pending++[request]},[],Nothing)

tryEnqueueConsumed : Ingress.AcceptedTicket -> Model -> (Model,Cmd Msg,EnqueueConsumedResult)
tryEnqueueConsumed ticket model =
    let (next,effects,result) = tryEnqueueConsumedEffects ticket model
    in (next,interpret effects,result)

-- The encoder exposes only validated data, not an issuer capability.
confirmationKey : Ingress.AcceptedTicket -> Maybe (Realm.Domain, UInt64.Counter)
confirmationKey ticket =
    D.decodeValue (D.map2 Tuple.pair Realm.domainDecoder (D.field "controlOrdinal" UInt64.decoder)) (Ingress.encodeConsumed ticket)
        |> Result.toMaybe

tryEnqueueConsumedEffects : Ingress.AcceptedTicket -> Model -> (Model,List Effect,EnqueueConsumedResult)
tryEnqueueConsumedEffects ticket ((Model model) as current) =
    if model.failed/=Nothing || model.role/=PopupRole then (current,[],Stopped) else
    let requests = Maybe.map (\item -> [item]) model.active |> Maybe.withDefault [] |> (\active -> active ++ model.pending)
        same request = request.ticket |> Maybe.map (Ingress.sameAcceptedTicket ticket) |> Maybe.withDefault False
        sameKey request = request.ticket |> Maybe.andThen confirmationKey |> (\key -> key /= Nothing && key == confirmationKey ticket)
        conflict request = sameKey request && not (same request)
    in if confirmationKey ticket == Nothing || List.any conflict requests then
            let (next,effects,_) = failedEffects (ExplicitStop "Conflicting preview confirmation identity.") current
            in (next,effects,Stopped)
       else if List.any same requests then (current,[],AlreadyQueued)
       else if List.length requests >= 16 then (current,[],Deferred)
       else let (next,effects,event) = enqueueRequest PopupConsumed (Ingress.encodeConsumed ticket) (Just ticket) current
            in case event of
                Just (Lost _) -> (next,effects,Stopped)
                _ -> (next,effects,Queued)

gateway : D.Value -> Maybe (String,D.Value)
gateway value =
    let decoder=D.keyValuePairs D.value |> D.andThen (\pairs ->
            if List.sort (List.map Tuple.first pairs)/=["bridgeProtocol","kind","payload"] then D.fail "UI gateway fields" else
                D.map3 (\_ kind payload -> (kind,payload))
                    (D.field "bridgeProtocol" (D.int |> D.andThen (\version -> if version==1 then D.succeed () else D.fail "UI gateway version")))
                    (D.field "kind" D.string) (D.field "payload" D.value))
    in D.decodeValue decoder value |> Result.toMaybe

allowed : Role -> String -> Bool
allowed role kind =
    case role of
        Controller -> List.member kind ["native-event","view-topology","view-action","view-disposition","view-dismiss","view-escape","view-reflow"]
        Renderer -> List.member kind ["presentation","announcements","focus","native-preview-grant","native-preview-quarantine","native-preview-closed"]
        PopupRole -> List.member kind ["presentation","announcements","focus","native-preview-grant","native-preview-quarantine","native-preview-closed","native-preview-issued","native-preview-retry","native-preview-retirement"]

updateEffects : Msg -> Model -> (Model,List Effect,Maybe Event)
updateEffects message ((Model model) as current) =
    if model.failed/=Nothing then (current,[],Nothing) else
    case message of
        Poll -> if model.polling then (current,[],Nothing) else (Model {model | polling=True},[ReadEvents],Nothing)
        Polled (Err _) -> failedEffects EventTransportUnavailable current
        Polled (Ok text) ->
            if String.isEmpty text then (Model {model | polling=False},[WakeAfter 100 Poll],Nothing)
            else if not (fits 1048704 text) then failedEffects EventTooLarge current
            else case D.decodeString D.value text |> Result.toMaybe of
                Nothing -> failedEffects EventInvalidJson current
                Just value ->
                    case gateway value of
                        Just (kind,_) ->
                            if allowed model.role kind then (current,[ReadEvents],Just (Incoming value)) else failedEffects EventSourceRejected current
                        Nothing -> failedEffects EventGatewayMismatch current
        -- Untagged callbacks cannot confirm or advance a request. Errors and
        -- malformed responses still preserve the original fail-closed boundary.
        Posted (Err _) -> failedEffects DeliveryUnconfirmed current
        Posted (Ok text) ->
            if String.isEmpty text then (current,[],Nothing)
            else failedEffects DeliveryUnexpected current
        PostedFor requestId kind outcome ->
            case model.active of
                Nothing -> (current,[],Nothing)
                Just active ->
                    if active.id /= requestId || active.kind /= kind then (current,[],Nothing) else
                    case outcome of
                        Err _ -> failedEffects DeliveryUnconfirmed current
                        Ok text ->
                            if not (String.isEmpty text) then failedEffects DeliveryUnexpected current else
                            let event = if kind==PopupConsumed then Maybe.map TransportConsumedCompleted active.ticket else Nothing
                            in case model.pending of
                                [] -> (Model {model | active=Nothing},[],event)
                                next::rest -> (Model {model | active=Just next,pending=rest},[sendEffect next],event)
