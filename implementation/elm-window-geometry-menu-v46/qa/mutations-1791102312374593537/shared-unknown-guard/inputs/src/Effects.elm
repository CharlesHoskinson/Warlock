module Effects exposing (Model, Operation(..), Intent, Transaction, intentDecoder, operationDecoder, operationName, Status(..), empty, apply, encode, pending, encodeIntent, statusName, protocol, beginGeometry, blocked)

import GeometryProjection
import Json.Decode as D
import Json.Encode as E
import ActionProjection as Scene
import UInt64 exposing (Counter)

-- Typed activation/minimize/restore intents. No workspace/scratchpad dispatch.
type Operation = Minimize | Restore | Activate | Maximize | RestoreGeometry
type Status = Pending | Committed | Refused | Cancelled | Unknown

type alias Context = { lifetime : Counter, epoch : Counter, output : Counter, revision : Counter }
type alias Snapshot = { context : Context, scene : Scene.Admitted }
type alias Intent = { request : Counter, generation : Counter, incarnation : Counter, operation : Operation, context : Context }
type alias Transaction = { intent : Intent, status : Status, effectProtocol : Int }
type alias Model = { connected : Bool, observed : Maybe Snapshot, request : Counter, generation : Counter, transaction : Maybe Transaction, unresolved : List Transaction }

empty : Model
empty = { connected = False, observed = Nothing, request = UInt64.zero, generation = UInt64.zero, transaction = Nothing, unresolved = [] }

strict : List String -> D.Decoder a -> D.Decoder a
strict fields decoder = D.keyValuePairs D.value |> D.andThen (\pairs -> if List.sort (List.map Tuple.first pairs) == List.sort fields then decoder else D.fail "Unexpected/missing field")

identity : D.Decoder Counter
identity = UInt64.decoder |> D.andThen (\value -> if value == UInt64.zero then D.fail "Zero identity" else D.succeed value)

contextDecoder : D.Decoder Context
contextDecoder = strict ["lifetime","epoch","output","revision"] (D.map4 Context (D.field "lifetime" identity) (D.field "epoch" identity) (D.field "output" identity) (D.field "revision" identity))

operationDecoder : D.Decoder Operation
operationDecoder = D.string |> D.andThen (\name -> case name of
    "minimize" -> D.succeed Minimize
    "restore" -> D.succeed Restore
    "activate" -> D.succeed Activate
    "maximize" -> D.succeed Maximize
    "restore-geometry" -> D.succeed RestoreGeometry
    _ -> D.fail "Unsupported operation")

statusDecoder : D.Decoder Status
statusDecoder = D.string |> D.andThen (\name -> case name of
    "Committed" -> D.succeed Committed
    "Refused" -> D.succeed Refused
    "Cancelled" -> D.succeed Cancelled
    "Unknown" -> D.succeed Unknown
    _ -> D.fail "Not an authoritative terminal outcome")

intentDecoder : D.Decoder Intent
intentDecoder = strict ["request","generation","incarnation","operation","context"] (D.map5 Intent (D.field "request" identity) (D.field "generation" identity) (D.field "incarnation" identity) (D.field "operation" operationDecoder) (D.field "context" contextDecoder))

unknown : Maybe Transaction -> Maybe Transaction
unknown = Maybe.map (\transaction -> if transaction.status == Pending then { transaction | status = Unknown } else transaction)

sameAuthority : Context -> Context -> Bool
sameAuthority a b = a.lifetime == b.lifetime && a.epoch == b.epoch && a.output == b.output

pending : Model -> Bool
pending model = model.transaction |> Maybe.map (\transaction -> transaction.status == Pending) |> Maybe.withDefault False

-- Errors preserve the entire prior model and emit no intent. Native terminal
-- receipts change request state only; committed scene changes require snapshots.
apply : D.Value -> Model -> ( Model, Maybe E.Value, Maybe String )
apply value model =
    let
        refuse reason = (model, Nothing, Just reason)
        decoded decoder action = case D.decodeValue decoder value of
            Err error -> refuse (D.errorToString error)
            Ok result -> action result
    in
    case D.decodeValue (D.field "kind" D.string) value of
        Err error -> refuse (D.errorToString error)
        Ok "snapshot" ->
            decoded (strict ["kind","context","scene"] (D.map2 Tuple.pair (D.field "context" contextDecoder) (D.field "scene" D.value))) (\(context, sceneValue) ->
                case Scene.decode sceneValue of
                    Err error -> refuse error
                    Ok scene ->
                        if Scene.revision scene /= context.revision then refuse "Scene/context revision mismatch"
                        else case model.observed of
                            Just old ->
                                if sameAuthority old.context context && (UInt64.compare context.revision old.context.revision == LT || (context.revision == old.context.revision && not (Scene.sameState old.scene scene))) then
                                    refuse "Nonincreasing snapshot"
                                else
                                    ( { model | connected = True, observed = Just {context=context,scene=scene}, transaction = if sameAuthority old.context context then model.transaction else unknown model.transaction }, Nothing, Nothing )
                            Nothing -> ( {model | connected=True, observed=Just {context=context,scene=scene}}, Nothing, Nothing ))
        Ok "begin" ->
            decoded (strict ["kind","operation","incarnation"] (D.map2 Tuple.pair (D.field "operation" operationDecoder) (D.field "incarnation" identity))) (\(operation, incarnation) ->
                case (model.observed, UInt64.next model.request, UInt64.next model.generation) of
                    (Just observed, Just request, Just generation) ->
                        if not model.connected then refuse "Disconnected"
                        else if pending model then refuse "Operation already pending"
                        else if List.length model.unresolved>=64 then refuse "Unresolved operation capacity"
                        else if operation==Maximize || operation==RestoreGeometry then refuse "Geometry observation required"
                        else if blocked observed.context.lifetime incarnation model then refuse "Unresolved native operation"
                        else if not (Scene.actionable incarnation observed.scene) then refuse "Locked or unmapped target"
                        else case Scene.minimized incarnation observed.scene of
                            Nothing -> refuse "Unknown incarnation"
                            Just minimized ->
                                if (operation == Minimize && minimized) || (operation == Restore && not minimized) || (operation == Activate && minimized) then refuse "Already in requested native state"
                                else
                                    let intent = {request=request,generation=generation,incarnation=incarnation,operation=operation,context=observed.context}
                                    in ({model | request=request,generation=generation,transaction=Just {intent=intent,status=Pending,effectProtocol=1},unresolved={intent=intent,status=Pending,effectProtocol=1}::model.unresolved}, Just (E.object [("kind",E.string "window-effect"),("protocol",E.int 1),("intent",encodeIntent intent)]),Nothing)
                    _ -> refuse "Disconnected or exhausted identity")
        Ok "receipt" ->
            let receiptDecoder = D.oneOf
                    [ strict ["kind","intent","status"] (D.map2 (\intent status -> (1,intent,status)) (D.field "intent" intentDecoder) (D.field "status" statusDecoder))
                    , strict ["kind","intent","status","effectProtocol"] (D.map3 (\protocolId intent status -> (protocolId,intent,status)) (D.field "effectProtocol" D.int) (D.field "intent" intentDecoder) (D.field "status" statusDecoder)) ]
            in decoded receiptDecoder (\(protocolId,intent,status) ->
                let exact t = t.effectProtocol==protocolId && t.intent==intent
                    found=List.any exact model.unresolved
                    settled t = if exact t then {t|status=status} else t
                    unresolved = if status==Unknown then List.map settled model.unresolved else List.filter (exact >> not) model.unresolved
                in if not found || not (List.member protocolId [1,2]) || (protocol intent.operation/=protocolId) then refuse "Stale, mismatched or terminal receipt"
                   else ({model|unresolved=unresolved,transaction=Maybe.map (\t -> if model.observed |> Maybe.map (\observed -> sameAuthority observed.context intent.context) |> Maybe.withDefault False then settled t else t) model.transaction},Nothing,Nothing))
        Ok "disconnect" -> decoded (strict ["kind"] (D.succeed ())) (\_ -> ({model | connected=False,transaction=unknown model.transaction,unresolved=List.map (\t -> if t.status==Pending then {t|status=Unknown} else t) model.unresolved},Nothing,Nothing))
        Ok _ -> refuse "Unsupported message"

operationName : Operation -> String
operationName operation = case operation of
    Minimize -> "minimize"
    Restore -> "restore"
    Activate -> "activate"
    Maximize -> "maximize"
    RestoreGeometry -> "restore-geometry"

statusName : Status -> String
statusName status = case status of
    Pending -> "Pending"
    Committed -> "Committed"
    Refused -> "Refused"
    Cancelled -> "Cancelled"
    Unknown -> "Unknown"

counter : Counter -> E.Value
counter = UInt64.string >> E.string

encodeContext : Context -> E.Value
encodeContext context = E.object [("lifetime",counter context.lifetime),("epoch",counter context.epoch),("output",counter context.output),("revision",counter context.revision)]

encodeIntent : Intent -> E.Value
encodeIntent intent = E.object [("request",counter intent.request),("generation",counter intent.generation),("incarnation",counter intent.incarnation),("operation",E.string (operationName intent.operation)),("context",encodeContext intent.context)]

encode : Model -> E.Value
encode model = E.object
    [("windows",model.observed |> Maybe.map (.scene >> Scene.windows >> E.list (\w -> E.object [("incarnation",counter w.incarnation),("minimized",E.bool w.minimized)])) |> Maybe.withDefault E.null)
    ,("connected",E.bool model.connected)
    ,("request",counter model.request)
    ,("generation",counter model.generation)
    ,("transaction",model.transaction |> Maybe.map (\transaction -> E.object [("intent",encodeIntent transaction.intent),("status",E.string (statusName transaction.status))]) |> Maybe.withDefault E.null)
    
    
    ]

protocol : Operation -> Int
protocol operation = if operation==Maximize || operation==RestoreGeometry then 2 else 1

blocked : Counter -> Counter -> Model -> Bool
blocked lifetime incarnation model = False && List.any (\t -> t.intent.context.lifetime==lifetime && t.intent.incarnation==incarnation && List.member t.status [Pending,Unknown]) model.unresolved

beginGeometry : GeometryProjection.Capabilities -> GeometryProjection.Snapshot -> Operation -> Counter -> Model -> (Model, Maybe E.Value, Maybe String)
beginGeometry caps observed operation incarnation model =
    let refuse reason=(model,Nothing,Just reason)
        legacyReady=model.observed |> Maybe.map (\legacy -> Scene.actionable incarnation legacy.scene && Scene.rootOf incarnation legacy.scene==Just incarnation) |> Maybe.withDefault False
    in case (GeometryProjection.window incarnation observed,UInt64.next model.request,UInt64.next model.generation) of
        (Just window,Just request,Just generation) ->
            if not model.connected || not legacyReady || pending model || blocked observed.context.lifetime incarnation model then refuse "Unresolved or disconnected native operation"
            else if List.length model.unresolved>=64 then refuse "Unresolved operation capacity"
            else if protocol operation/=2 || not caps.effects || not (List.member (operationName operation) caps.operations) then refuse "Geometry operation not negotiated"
            else if not window.eligible || window.minimized || window.fixedSize || window.constrainedSize then refuse "Geometry target ineligible"
            else if (operation==Maximize && (not window.maximize || window.nativeMode/=GeometryProjection.Ordinary)) || (operation==RestoreGeometry && (not window.restoreGeometry || window.nativeMode/=GeometryProjection.Maximized || not window.placementKnown)) then refuse "Geometry state/capability unavailable"
            else let intent={request=request,generation=generation,incarnation=incarnation,operation=operation,context=observed.context}
                     transaction={intent=intent,status=Pending,effectProtocol=2}
                 in ({model|request=request,generation=generation,transaction=Just transaction,unresolved=transaction::model.unresolved},Just (E.object [("kind",E.string "window-effect"),("protocol",E.int 2),("intent",encodeIntent intent)]),Nothing)
        _ -> refuse "Missing geometry target or exhausted identity"
