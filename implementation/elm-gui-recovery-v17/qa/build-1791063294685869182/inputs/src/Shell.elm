module Shell exposing (Model, Msg(..), Phase(..), Effect(..), initial, update, encode, status, available)

import Binding exposing (Binding)
import Effects
import Json.Decode as D
import Json.Encode as E
import UInt64 exposing (Counter)

type Phase = Detached | Reconciling | Ready | Exhausted
type Msg = Incoming D.Value | Refresh | Reconnect | Act String Counter
type Effect = Send E.Value | RestartBackend
type alias Model = { effects : Effects.Model, binding : Maybe Binding, request : Counter, expected : Maybe Counter, phase : Phase, reconnecting : Bool, notice : String }
initial : Model
initial = { effects = Effects.empty, binding = Nothing, request = UInt64.zero, expected = Nothing, phase = Detached, reconnecting = True, notice = "Connecting…" }
strict fields decoder = D.keyValuePairs D.value |> D.andThen (\pairs -> if List.sort (List.map Tuple.first pairs) == List.sort fields then decoder else D.fail "Unexpected fields")
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
    in {model | effects = effects, expected = Nothing, phase = Detached, reconnecting = False, notice = "Connection lost. Reconnect to continue."}
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
        Act operation incarnation ->
            if not (available model) then (model,[]) else
                let (effects,command,error) = Effects.apply (E.object [("kind",E.string "begin"),("operation",E.string operation),("incarnation",E.string (UInt64.string incarnation))]) model.effects
                    commands = case (command,model.binding) of
                        (Just value,Just binding) -> case D.decodeValue (D.field "intent" D.value) value of
                            Ok intent -> [Send (E.object [("protocolVersion",E.int 3),("kind",E.string "window-effect"),("effectProtocol",E.int 1),("binding",Binding.encode binding),("intent",intent)])]
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
                            if model.binding |> Maybe.map (Binding.replaces binding >> not) |> Maybe.withDefault False then (model,[]) else
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
                Ok "effect-outcome" ->
                    case D.decodeValue (D.map3 (\_ binding receipt -> (binding,receipt)) version (D.field "binding" Binding.decoder) (D.map2 (\intent outcome -> E.object [("kind",E.string "receipt"),("intent",intent),("status",outcome)]) (D.field "intent" D.value) (D.field "status" D.value))) raw of
                        Ok (binding,receipt) ->
                            if model.phase == Detached || model.binding /= Just binding then (model,[]) else
                                let (effects,_,error) = Effects.apply receipt model.effects
                                in if error /= Nothing then (model,[]) else refresh {model | effects = effects}
                        Err _ -> (model,[])
                _ -> (model,[])
encode : Model -> E.Value
encode model = E.object [("phase",E.string (case model.phase of
    Detached -> "Detached"
    Reconciling -> "Reconciling"
    Ready -> "Ready"
    Exhausted -> "Exhausted")),("request",E.string (UInt64.string model.request)),("available",E.bool (available model)),("reconnecting",E.bool model.reconnecting),("effects",Effects.encode model.effects)]
