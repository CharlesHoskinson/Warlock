module Shortcuts exposing (Model, Route(..), Snapshot, Box, boxDecoder, destination, currentGeneration, decoder, initial, receive)
import Binding
import Json.Decode as D
import UInt64 exposing (Counter)
type Route = Applications | System | Notifications
type alias Event = { serial : Counter, route : Route, outputGeneration : Maybe Counter }
type alias Snapshot = { binding : Binding.Binding, serial : Counter, blocked : Bool, events : List Event }
type alias Model = { binding : Maybe Binding.Binding, seen : Counter }
initial = {binding=Nothing,seen=UInt64.zero}
strict fields child=D.keyValuePairs D.value |> D.andThen (\pairs -> if List.sort (List.map Tuple.first pairs)==List.sort fields then child else D.fail "Shortcut fields")
positive=UInt64.decoder |> D.andThen (\v -> if v==UInt64.zero then D.fail "Shortcut serial" else D.succeed v)
routeDecoder=D.string |> D.andThen (\v -> case v of
    "applications" -> D.succeed Applications
    "system" -> D.succeed System
    "notifications" -> D.succeed Notifications
    _ -> D.fail "Unsupported shell shortcut")
type alias Box = List Int
boxDecoder = D.list D.int |> D.andThen (\box -> case box of
    [x,y,width,height] -> if width>0 && height>0 && List.all (\v -> v >= -2147483648 && v<=2147483647) box then D.succeed box else D.fail "Shortcut output bounds"
    _ -> D.fail "Shortcut output shape")
destination raw = D.decodeValue (D.field "events" (D.list (D.field "output" (D.nullable boxDecoder)))) raw |> Result.toMaybe |> Maybe.andThen (List.reverse >> List.head) |> Maybe.andThen identity
currentGeneration expected snapshot =
    expected/=Nothing && (snapshot.events |> List.reverse |> List.head |> Maybe.andThen .outputGeneration)==expected
eventDecoder protocol = if protocol==1 then strict ["serial","route"] (D.map2 (\serial route -> Event serial route Nothing) (D.field "serial" positive) (D.field "route" routeDecoder)) else if protocol==2 then
    strict ["serial","route","output"] (D.map3 (\serial route _ -> Event serial route Nothing) (D.field "serial" positive) (D.field "route" routeDecoder) (D.field "output" (D.nullable boxDecoder))) else
    strict ["serial","route","output","outputGeneration"] (D.map4 (\serial route _ generation -> Event serial route (Just generation)) (D.field "serial" positive) (D.field "route" routeDecoder) (D.field "output" (D.nullable boxDecoder)) (D.field "outputGeneration" positive))
decoder = D.field "shortcutProtocol" D.int |> D.andThen (\eventProtocol -> strict ["protocolVersion","kind","shortcutProtocol","binding","requestId","serial","blocked","events"]
    (D.map8 (\version kind protocol binding request serial blocked events -> {version=version,kind=kind,protocol=protocol,snapshot={binding=binding,serial=serial,blocked=blocked,events=events}})
        (D.field "protocolVersion" D.int) (D.field "kind" D.string) (D.field "shortcutProtocol" D.int) (D.field "binding" Binding.decoder) (D.field "requestId" positive) (D.field "serial" UInt64.decoder) (D.field "blocked" D.bool) (D.field "events" (D.list (eventDecoder eventProtocol))))
    |> D.andThen (\receipt ->
        let snapshot=receipt.snapshot
        in
        let ordered rows=case rows of
                [] -> True
                [_] -> True
                a::b::rest -> UInt64.next a.serial==Just b.serial && ordered (b::rest)
            last=snapshot.events |> List.reverse |> List.head |> Maybe.map .serial
        in if receipt.version/=3 || receipt.kind/="shell-shortcuts" || not (List.member receipt.protocol [1,2,3]) || List.length snapshot.events>64 || not (ordered snapshot.events) || (last/=Nothing && last/=Just snapshot.serial) then D.fail "Shortcut protocol/order" else D.succeed snapshot))
receive expected snapshot model =
    if expected/=Just snapshot.binding then (model,Nothing,Nothing) else
    if model.binding/=expected then ({binding=expected,seen=snapshot.serial},Nothing,Nothing) else
    if UInt64.compare snapshot.serial model.seen/=GT then (model,Nothing,Nothing) else
    let next={model | seen=snapshot.serial}
        fresh=List.filter (\event -> UInt64.compare event.serial model.seen==GT) snapshot.events
        contiguous=fresh |> List.head |> Maybe.map (\event -> UInt64.next model.seen==Just event.serial) |> Maybe.withDefault False
    in if snapshot.blocked then (next,Nothing,Just "Shell shortcut unavailable while input is blocked.")
       else if not contiguous then (next,Nothing,Just "Shortcut history expired. Press the shortcut again.")
       else (next,fresh |> List.reverse |> List.head |> Maybe.map .route,Nothing)
