module UiHttp exposing (Model, Msg(..), Event(..), controller, renderer, enqueue, update, problem, stop, gateway)

import Http
import Json.Decode as D
import Json.Encode as E
import Process
import Task

-- Only compiled roots select these roles. Flags and wire data cannot select a
-- destination or privileged source. Each root runs on its own trusted origin.
type Role = Controller | Renderer

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
    , pending : List E.Value
    , active : Maybe E.Value
    , polling : Bool
    , failed : Maybe Failure
    }
type Msg = Poll | Polled (Result Http.Error String) | Posted (Result Http.Error String)
type Event = Incoming D.Value | Lost String

controller : (Model,Cmd Msg)
controller = start Controller

renderer : (Model,Cmd Msg)
renderer = start Renderer

start : Role -> (Model,Cmd Msg)
start role = (Model {role=role,pending=[],active=Nothing,polling=True,failed=Nothing},poll)

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

post : Role -> E.Value -> Cmd Msg
post role value = Http.request
    {method="POST",headers=headers,url=if role==Controller then "/commit" else "/actions"
    ,body=Http.jsonBody value,expect=Http.expectStringResponse Posted (response False),timeout=Just 5000,tracker=Just "warlock-ui-post"}

failed : Failure -> Model -> (Model,Cmd Msg,Maybe Event)
failed reason model =
    if problem model/=Nothing then (model,Cmd.none,Nothing) else
        (reject reason model,Cmd.batch [Http.cancel "warlock-ui-events",Http.cancel "warlock-ui-post"],Just (Lost (failureText reason)))

stop : String -> Model -> (Model,Cmd Msg,Maybe Event)
stop reason = failed (ExplicitStop reason)

enqueue : E.Value -> Model -> (Model,Cmd Msg,Maybe Event)
enqueue value ((Model model) as current) =
    if model.failed/=Nothing then (current,Cmd.none,Nothing) else
    let limit=if model.role==Controller then 131072 else 8192
        retained=List.length model.pending+(if model.active==Nothing then 0 else 1)
    in if not (fits limit (E.encode 0 value)) || retained>=16 then failed CapacityExceeded current else
        case model.active of
            Nothing -> (Model {model | active=Just value},post model.role value,Nothing)
            Just _ -> (Model {model | pending=model.pending++[value]},Cmd.none,Nothing)

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
        Renderer -> List.member kind ["presentation","announcements","focus"]

update : Msg -> Model -> (Model,Cmd Msg,Maybe Event)
update message ((Model model) as current) =
    if model.failed/=Nothing then (current,Cmd.none,Nothing) else
    case message of
        Poll -> if model.polling then (current,Cmd.none,Nothing) else (Model {model | polling=True},poll,Nothing)
        Polled (Err _) -> failed EventTransportUnavailable current
        Polled (Ok text) ->
            if String.isEmpty text then (Model {model | polling=False},Process.sleep 100 |> Task.perform (\_ -> Poll),Nothing)
            else if not (fits 1048704 text) then failed EventTooLarge current
            else case D.decodeString D.value text |> Result.toMaybe of
                Nothing -> failed EventInvalidJson current
                Just value ->
                    case gateway value of
                        Just (kind,_) ->
                            if allowed model.role kind then (current,poll,Just (Incoming value)) else failed EventSourceRejected current
                        Nothing -> failed EventGatewayMismatch current
        Posted (Err _) -> failed DeliveryUnconfirmed current
        Posted (Ok text) ->
            -- Delivery completion only permits the next queued HTTP request.
            -- It never enters Desktop as a presentation/native acknowledgement.
            if not (String.isEmpty text) then failed DeliveryUnexpected current else
            case model.pending of
                [] -> (Model {model | active=Nothing},Cmd.none,Nothing)
                next::rest -> (Model {model | active=Just next,pending=rest},post model.role next,Nothing)
