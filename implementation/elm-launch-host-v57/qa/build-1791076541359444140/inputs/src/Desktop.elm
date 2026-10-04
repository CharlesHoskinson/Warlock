module Desktop exposing (Effect(..), Model, Msg(..), initial, update)

import Binding
import Catalog
import Json.Decode as D
import Json.Encode as E
import Launch
import Shell
import TaskbarShell
import UInt64 exposing (Counter)

type alias Model =
    { windows : TaskbarShell.Model
    , launch : Launch.Model
    , applications : Maybe Catalog.Snapshot
    , open : Bool
    , request : Counter
    , expected : Maybe Counter
    }

type Msg
    = Window TaskbarShell.Msg
    | Incoming D.Value
    | OpenApplications
    | CloseApplications
    | Start Launch.Selection
    | Deadline Launch.PendingToken
    | Acknowledge Launch.Acknowledgement

type Effect
    = WindowEffect Shell.Effect
    | Send E.Value
    | Arm Launch.PendingToken

initial : Model
initial =
    { windows = TaskbarShell.initial, launch = Launch.init, applications = Nothing, open = False, request = UInt64.zero, expected = Nothing }

host : Binding.Binding -> String
host binding =
    E.encode 0 (Binding.encode binding)

strict : List String -> D.Decoder a -> D.Decoder a
strict fields decoder =
    D.keyValuePairs D.value |> D.andThen (\pairs -> if List.sort (List.map Tuple.first pairs) == List.sort fields then decoder else D.fail "Desktop frame fields")

version : D.Decoder ()
version =
    D.field "protocolVersion" D.int |> D.andThen (\value -> if value == 3 then D.succeed () else D.fail "Desktop version")

window : TaskbarShell.Msg -> Model -> ( Model, List Effect )
window message model =
    let
        (windows, effects) = TaskbarShell.update message model.windows
        disconnected = windows.shell.phase == Shell.Detached
        changed = windows.shell.binding /= model.windows.shell.binding
        launch =
            if disconnected then Launch.disconnect model.launch
            else if changed then windows.shell.binding |> Maybe.map (\binding -> Launch.bind (host binding) model.launch) |> Maybe.withDefault (Launch.disconnect model.launch)
            else model.launch
    in
    ( { model | windows = windows, launch = launch
        , applications = if disconnected || changed then Nothing else model.applications
        , expected = if disconnected || changed then Nothing else model.expected
      }, List.map WindowEffect effects )

update : Msg -> Model -> ( Model, List Effect )
update message model =
    case message of
        Window value -> window value model
        Incoming raw ->
            case D.decodeValue (D.field "kind" D.string) raw of
                Ok "application-catalog" ->
                    let decoder = strict ["protocolVersion","kind","binding","requestId","snapshot"] (D.map4 (\_ binding request snapshot -> (binding,request,snapshot)) version (D.field "binding" Binding.decoder) (D.field "requestId" UInt64.decoder) (D.field "snapshot" D.value))
                    in case D.decodeValue decoder raw of
                        Ok (binding,request,snapshot) ->
                            if model.windows.shell.phase /= Shell.Detached && model.windows.shell.binding == Just binding && model.expected == Just request then
                                ({model | launch = Launch.catalog snapshot model.launch, applications = Catalog.decode snapshot |> Result.toMaybe, expected = Nothing},[])
                            else (model,[])
                        Err _ -> (model,[])
                Ok "application-launch-outcome" ->
                    let decoder = strict ["protocolVersion","kind","binding","outcome"] (D.map3 (\_ binding outcome -> (binding,outcome)) version (D.field "binding" Binding.decoder) (D.field "outcome" D.value))
                    in case D.decodeValue decoder raw of
                        Ok (binding,outcome) ->
                            if model.windows.shell.phase /= Shell.Detached && model.windows.shell.binding == Just binding then
                                ({model | launch = Launch.receive (host binding) outcome model.launch},[])
                            else (model,[])
                        Err _ -> (model,[])
                _ -> window (TaskbarShell.Native (Shell.Incoming raw)) model
        OpenApplications ->
            let retired = {model | open = True, applications = Nothing, launch = Launch.catalog E.null model.launch, expected = Nothing}
            in case (model.windows.shell.binding, UInt64.next model.request) of
                (Just binding,Just request) ->
                    if model.windows.shell.phase == Shell.Detached then (retired,[]) else
                        ({retired | request = request, expected = Just request},[Send (E.object [("protocolVersion",E.int 3),("kind",E.string "catalog-request"),("binding",Binding.encode binding),("requestId",E.string (UInt64.string request))])])
                _ -> (retired,[])
        CloseApplications -> ({model | open = False},[])
        Start selection ->
            let (launch,intent) = Launch.start selection model.launch
            in case (intent,model.windows.shell.binding) of
                (Just wire,Just binding) ->
                    ({model | launch = launch},Send (E.object [("protocolVersion",E.int 3),("kind",E.string "application-launch"),("binding",Binding.encode binding),("intent",wire)]) :: (Launch.pending launch |> Maybe.map (Arm >> List.singleton) |> Maybe.withDefault []))
                _ -> ({model | launch = launch},[])
        Deadline token -> ({model | launch = Launch.timeout token model.launch},[])
        Acknowledge token -> ({model | launch = Launch.acknowledgeUnknown token model.launch},[])
