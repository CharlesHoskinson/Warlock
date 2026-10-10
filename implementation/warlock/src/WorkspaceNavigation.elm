module WorkspaceNavigation exposing (Model, Intent, Record, Status(..), initial, bind, disconnect, blocked, propose, begin, receive, recover, expire, notice, clear, intentDecoder, encodeIntent)

import Binding
import GeometryProjection
import Json.Decode as D
import Json.Encode as E
import UInt64 exposing (Counter)
import WorkspaceInventory

type Status = Pending | Unknown | Committed | Refused
type alias Context = {lifetime:Counter,epoch:Counter,output:Counter,revision:Counter}
type alias Intent = {request:Counter,generation:Counter,source:WorkspaceInventory.Row,destination:WorkspaceInventory.Row,context:Context}
type alias Record = {binding:Binding.Binding,intent:Intent,status:Status,reason:String}
type alias Model = {binding:Maybe Binding.Binding,ready:Bool,request:Counter,generation:Counter,record:Maybe Record,recovering:Bool,origin:Maybe String,returning:Bool}
initial = {binding=Nothing,ready=False,request=UInt64.zero,generation=UInt64.zero,record=Nothing,recovering=False,origin=Nothing,returning=False}
strict fields decoder = D.keyValuePairs D.value |> D.andThen (\pairs -> if List.sort (List.map Tuple.first pairs)==List.sort fields then decoder else D.fail "Workspace navigation fields")
positive = UInt64.decoder |> D.andThen (\v -> if v==UInt64.zero then D.fail "Zero navigation identity" else D.succeed v)
contextDecoder = strict ["lifetime","epoch","output","revision"] (D.map4 Context (D.field "lifetime" positive) (D.field "epoch" positive) (D.field "output" positive) (D.field "revision" positive))
intentDecoder = strict ["request","generation","source","destination","context"] (D.map5 Intent (D.field "request" positive) (D.field "generation" positive) (D.field "source" WorkspaceInventory.rowDecoder) (D.field "destination" WorkspaceInventory.rowDecoder) (D.field "context" contextDecoder))
statusDecoder = D.string |> D.andThen (\s -> case s of
    "Pending" -> D.succeed Pending
    "Unknown" -> D.succeed Unknown
    "Committed" -> D.succeed Committed
    "Refused" -> D.succeed Refused
    _ -> D.fail "Workspace navigation status")
reasonDecoder = D.string |> D.andThen (\s -> if String.length s<=64 && (String.uncons s |> Maybe.map (\(first,_) -> first>='a' && first<='z') |> Maybe.withDefault False) && String.all (\c -> (c>='a' && c<='z') || (c>='0' && c<='9') || c=='-') s then D.succeed s else D.fail "Workspace navigation reason")
recordBody = D.map4 Record (D.field "binding" Binding.decoder) (D.field "intent" intentDecoder) (D.field "status" statusDecoder) (D.field "reason" reasonDecoder) |> D.andThen (\r -> if Binding.matchesContext r.intent.context.lifetime r.intent.context.epoch r.binding then D.succeed r else D.fail "Workspace navigation authority")
recordDecoder = strict ["schema","binding","intent","status","reason"] (D.field "schema" D.int |> D.andThen (\n -> if n==1 then recordBody else D.fail "Workspace record schema"))
protocol = D.map2 Tuple.pair (D.field "protocolVersion" D.int) (D.field "workspaceProtocol" D.int) |> D.andThen (\pair -> if pair==(3,1) then D.succeed () else D.fail "Workspace navigation protocol")
encodeRow r = E.object [("identity",E.string r.identity),("generation",E.string (UInt64.string r.generation)),("monitor",E.string (UInt64.string r.monitor)),("outputOwnershipGeneration",E.string (UInt64.string r.outputOwnershipGeneration))]
encodeIntent i = E.object [("request",E.string (UInt64.string i.request)),("generation",E.string (UInt64.string i.generation)),("source",encodeRow i.source),("destination",encodeRow i.destination),("context",E.object [("lifetime",E.string (UInt64.string i.context.lifetime)),("epoch",E.string (UInt64.string i.context.epoch)),("output",E.string (UInt64.string i.context.output)),("revision",E.string (UInt64.string i.context.revision))])]
wire kind binding extras = E.object ([("protocolVersion",E.int 3),("kind",E.string kind),("workspaceProtocol",E.int 1),("binding",Binding.encode binding)]++extras)
blocked model = model.record |> Maybe.map (\r -> r.status==Pending || r.status==Unknown) |> Maybe.withDefault False
bind binding model = if model.binding==Just binding then model else {model|binding=Just binding,ready=False,recovering=False,origin=Nothing,returning=False,record=model.record |> Maybe.map (\r -> if r.status==Pending then {r|status=Unknown,reason="delivery-unproven"} else r)}
disconnect model = {model|binding=Nothing,ready=False,recovering=False,origin=Nothing,returning=False,record=model.record |> Maybe.map (\r -> if r.status==Pending then {r|status=Unknown,reason="delivery-unproven"} else r)}
propose : WorkspaceInventory.Snapshot -> GeometryProjection.Snapshot -> String -> Model -> Maybe Intent
propose inventory geometry destination model =
    if not model.ready || blocked model || model.binding/=Just geometry.binding || geometry.blocked || not (WorkspaceInventory.coherent inventory geometry) || List.any (\w -> w.workspace==Just destination) geometry.windows then Nothing else
    case (inventory.active |> Maybe.andThen (\id -> List.filter (\r -> r.identity==id) inventory.rows |> List.head),List.filter (\r -> r.identity==destination) inventory.rows |> List.head) of
        (Just source,Just target) -> if source.identity==target.identity then Nothing else
            Maybe.map2 (\request generation -> {request=request,generation=generation,source=source,destination=target,context=geometry.context}) (UInt64.next model.request) (UInt64.next model.generation)
        _ -> Nothing
begin intent model = case model.binding of
    Just binding -> if blocked model || not model.ready then (model,Nothing) else
        ({model|request=intent.request,generation=intent.generation,record=Just {binding=binding,intent=intent,status=Pending,reason="admitted"},origin=Just intent.destination.identity,returning=False},Just (wire "workspace-navigation" binding [("intent",encodeIntent intent)]))
    Nothing -> (model,Nothing)
expire intent model = case model.record of
    Just r -> if r.intent==intent && r.status==Pending then {model|record=Just {r|status=Unknown,reason="delivery-unproven"}} else model
    _ -> model
recover model = case (model.binding,model.record) of
    (Just binding,Just r) -> if r.status==Unknown && not model.recovering && model.ready then ({model|recovering=True},Just (wire "workspace-navigation-recover" binding [])) else (model,Nothing)
    _ -> (model,Nothing)
maxCounter a b = if UInt64.compare a b==GT then a else b
accept r model = {model|record=Just r,request=maxCounter model.request r.intent.request,generation=maxCounter model.generation r.intent.generation,returning=r.status==Refused && model.origin/=Nothing}
receive raw model = case D.decodeValue (D.field "kind" D.string) raw of
    Ok "workspace-navigation-outcome" ->
        case D.decodeValue (strict ["protocolVersion","kind","workspaceProtocol","binding","intent","status","reason"] (protocol |> D.andThen (\_ -> recordBody))) raw of
            Ok r -> case model.record of
                Just current -> if model.binding==Just r.binding && r.binding==current.binding && r.intent==current.intent && (current.status==Pending || current.status==Unknown) && r.status/=Pending then accept r model else model
                _ -> model
            Err _ -> model
    Ok "workspace-navigation-recovery" ->
        case D.decodeValue (strict ["protocolVersion","kind","workspaceProtocol","binding","record"] (protocol |> D.andThen (\_ -> D.map2 Tuple.pair (D.field "binding" Binding.decoder) (D.field "record" (D.nullable recordDecoder))))) raw of
            Ok (binding,maybeRecord) ->
                if model.binding/=Just binding || (model.ready && not model.recovering) then model else
                let matches r = Binding.sameLifetime r.intent.context.lifetime binding && r.status/=Pending && (not model.ready || (model.record |> Maybe.map (\current -> current.binding==r.binding && current.intent==r.intent) |> Maybe.withDefault False))
                in case maybeRecord of
                    Just r -> if matches r then accept r {model|ready=True,recovering=False} else model
                    Nothing -> if model.ready then model else {model|ready=True,recovering=False,record=Nothing,origin=Nothing,returning=False}
            Err _ -> model
    _ -> model
clear model = if blocked model then model else {model|record=Nothing,origin=Nothing,returning=False}
notice model = model.record |> Maybe.map (\r -> "Workspace "++r.intent.destination.identity++": "++(case r.status of
    Pending -> "switching…"
    Unknown -> "switch could not be confirmed. Refresh workspace status; do not try again."
    Committed -> "now active."
    Refused -> "switch refused ("++r.reason++"). Choose again after refreshing.")) |> Maybe.withDefault ""
