module PointerOwnership exposing (Model, State(..), Snapshot, initial, decoder, receive, blocked)
import Binding
import Json.Decode as D
import UInt64 exposing (Counter)
type State = Idle | Moving | Resizing
type alias Snapshot = { binding : Binding.Binding, serial : Counter, state : State, owner : Maybe Counter }
type alias Model = { observation : Maybe Snapshot }
initial = {observation=Nothing}
strict fields child = D.keyValuePairs D.value |> D.andThen (\pairs -> if List.sort (List.map Tuple.first pairs)==List.sort fields then child else D.fail "Pointer fields")
positive = UInt64.decoder |> D.andThen (\v -> if v==UInt64.zero then D.fail "Pointer counter" else D.succeed v)
stateDecoder = D.string |> D.andThen (\v -> case v of
    "idle" -> D.succeed Idle
    "move" -> D.succeed Moving
    "resize" -> D.succeed Resizing
    _ -> D.fail "Pointer state")
decoder = strict ["protocolVersion","kind","ownershipProtocol","binding","requestId","serial","state","owner"]
    (D.map8 (\version kind protocol binding request serial state owner -> {version=version,kind=kind,protocol=protocol,snapshot={binding=binding,serial=serial,state=state,owner=owner}})
        (D.field "protocolVersion" D.int) (D.field "kind" D.string) (D.field "ownershipProtocol" D.int) (D.field "binding" Binding.decoder) (D.field "requestId" positive) (D.field "serial" positive) (D.field "state" stateDecoder) (D.field "owner" (D.nullable positive)))
    |> D.andThen (\r -> if r.version/=3 || r.kind/="pointer-ownership" || r.protocol/=1 || (r.snapshot.state==Idle && r.snapshot.owner/=Nothing) then D.fail "Pointer protocol/owner" else D.succeed r.snapshot)
receive expected snapshot model =
    if expected/=Just snapshot.binding then model else
    case model.observation of
        Just prior -> if prior.binding==snapshot.binding && UInt64.compare snapshot.serial prior.serial/=GT then model else {observation=Just snapshot}
        Nothing -> {observation=Just snapshot}
blocked expected model =
    -- A live binding must establish current native ownership before shell input.
    -- No observation, or an old frontend's idle observation, cannot release it.
    case expected of
        Nothing -> False
        Just binding ->
            case model.observation of
                Just snapshot -> snapshot.binding/=binding || snapshot.state/=Idle
                Nothing -> True
