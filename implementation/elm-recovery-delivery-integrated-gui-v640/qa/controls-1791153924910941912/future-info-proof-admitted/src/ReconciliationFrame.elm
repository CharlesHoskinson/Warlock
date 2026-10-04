module ReconciliationFrame exposing (Context, Record, Proof, Observation, Release, Expected, Frame(..), proofDecoder, recordDecoder, contextDecoder, expectedDecoder, decodeUnknown, decodeReleased)

import Binding exposing (Binding)
import Effects
import Json.Decode as D
import UInt64 exposing (Counter)

type alias Context = { lifetime : Counter, epoch : Counter, output : Counter, revision : Counter }
type alias Record = { schema : Int, effectProtocol : Int, binding : Binding, intent : Effects.Intent, status : Effects.Status }
type alias Proof = { protocolVersion : Int, kind : String, retirementProtocol : Int, operation : String, binding : Binding, requestId : Counter, queriedBinding : Binding, sequence : Counter, grantState : String }
type alias Observation = { actionRequestId : Counter, geometryRequestId : Counter, actionContext : Context, geometryContext : Context }
type alias Release = { id : String, proof : Proof, observation : Observation }
type alias Expected = { currentBinding : Binding, record : Record, proofRequestId : Counter, actionRequestId : Counter, geometryRequestId : Counter, actionContext : Context, geometryContext : Context }
type Frame = ReservationUnknown Binding Record | ReservationReleased Binding Record Release

strict fields decoder = D.keyValuePairs D.value |> D.andThen (\pairs -> if List.sort (List.map Tuple.first pairs)==List.sort fields then decoder else D.fail "Unexpected or missing reconciliation fields")
positive = UInt64.decoder |> D.andThen (\value -> if value==UInt64.zero then D.fail "Zero authority counter" else D.succeed value)
exactInt n = D.int |> D.andThen (\v -> if v==n then D.succeed v else D.fail "Unsupported protocol/schema")
exactString n = D.string |> D.andThen (\v -> if v==n then D.succeed v else D.fail "Unexpected frame/status")
contextDecoder = strict ["lifetime","epoch","output","revision"] (D.map4 Context (D.field "lifetime" positive) (D.field "epoch" positive) (D.field "output" positive) (D.field "revision" positive))
protocolDecoder = D.int |> D.andThen (\v -> if v==1 || v==2 then D.succeed v else D.fail "Unsupported effect protocol")
recordDecoder : D.Decoder Record
recordDecoder = strict ["schema","effectProtocol","binding","intent","status"]
    (D.map5 Record (D.field "schema" (exactInt 2)) (D.field "effectProtocol" protocolDecoder) (D.field "binding" Binding.decoder) (D.field "intent" Effects.intentDecoder) (D.field "status" (exactString "Unknown" |> D.map (\_ -> Effects.Unknown))))
    |> D.andThen (\record ->
        let operationMatches = if record.effectProtocol==1 then List.member record.intent.operation [Effects.Minimize,Effects.Restore,Effects.Activate] else List.member record.intent.operation [Effects.Maximize,Effects.RestoreGeometry]
        in if Binding.matchesContext record.intent.context.lifetime record.intent.context.epoch record.binding && operationMatches then D.succeed record else D.fail "Record authority or operation/protocol mismatch")

proofDecoder : D.Decoder Proof
proofDecoder = strict ["protocolVersion","kind","retirementProtocol","operation","binding","requestId","queriedBinding","sequence","grantState"]
    (D.map8 (\version kind protocol operation binding request queried sequence -> Proof version kind protocol operation binding request queried sequence "Retired")
        (D.field "protocolVersion" (exactInt 3)) (D.field "kind" (exactString "binding-retirement"))
        (D.field "retirementProtocol" (exactInt 1))
        (D.field "operation" (D.string |> D.andThen (\v -> if List.member v ["observe","retire"] then D.succeed v else D.fail "Retirement operation")))
        (D.field "binding" Binding.decoder) (D.field "requestId" positive) (D.field "queriedBinding" Binding.decoder) (D.field "sequence" positive))
    |> D.andThen (\proof -> D.field "grantState" (D.string) |> D.map (\_ -> proof))
observationDecoder = strict ["actionRequestId","geometryRequestId","actionContext","geometryContext"]
    (D.map4 Observation (D.field "actionRequestId" positive) (D.field "geometryRequestId" positive) (D.field "actionContext" contextDecoder) (D.field "geometryContext" contextDecoder))
releaseIdDecoder = D.string |> D.andThen (\value -> if String.length value==64 && List.all (\c -> (c>='0' && c<='9') || (c>='a' && c<='f')) (String.toList value) then D.succeed value else D.fail "Release ID must be64lowerhex")
releaseDecoder = strict ["id","proof","observation"] (D.map3 Release (D.field "id" releaseIdDecoder) (D.field "proof" proofDecoder) (D.field "observation" observationDecoder))
expectedDecoder : D.Decoder Expected
expectedDecoder = strict ["currentBinding","record","proofRequestId","actionRequestId","geometryRequestId","actionContext","geometryContext"]
    (D.map7 Expected (D.field "currentBinding" Binding.decoder) (D.field "record" recordDecoder) (D.field "proofRequestId" positive) (D.field "actionRequestId" positive) (D.field "geometryRequestId" positive) (D.field "actionContext" contextDecoder) (D.field "geometryContext" contextDecoder))

contextMatches binding context = Binding.matchesContext context.lifetime context.epoch binding

-- Trusted expectations come from the actual admitted current reads and stored history.
-- Revisions, read IDs and retirement sequence are independent numeric domains.
decodeUnknown : Binding -> D.Value -> Result String Frame
decodeUnknown current raw =
    let decoder = strict ["protocolVersion","kind","binding","record"]
            (D.map4 (\_ _ binding record -> (binding,record)) (D.field "protocolVersion" (exactInt 3)) (D.field "kind" (exactString "host-reservation-unknown")) (D.field "binding" Binding.decoder) (D.field "record" recordDecoder))
    in D.decodeValue decoder raw |> Result.mapError D.errorToString |> Result.andThen (\(binding,record) -> if binding==current then Ok (ReservationUnknown binding record) else Err "Foreign current binding")

decodeReleased : Expected -> D.Value -> Result String Frame
decodeReleased expected raw =
    let decoder = strict ["protocolVersion","kind","binding","record","release"]
            (D.map5 (\_ _ binding record release -> (binding,record,release)) (D.field "protocolVersion" (exactInt 3)) (D.field "kind" (exactString "host-reservation-released")) (D.field "binding" Binding.decoder) (D.field "record" recordDecoder) (D.field "release" releaseDecoder))
    in D.decodeValue decoder raw |> Result.mapError D.errorToString |> Result.andThen (\(binding,record,release) ->
        let proof=release.proof
            observation=release.observation
            expectedValid = contextMatches expected.currentBinding expected.actionContext && contextMatches expected.currentBinding expected.geometryContext && expected.actionContext.output==expected.geometryContext.output
            correlated = binding==expected.currentBinding && record==expected.record && proof.binding==binding && proof.queriedBinding==record.binding && proof.requestId==expected.proofRequestId
                && record.binding/=binding && Binding.sameLifetime record.intent.context.lifetime binding
                && observation.actionRequestId==expected.actionRequestId && observation.geometryRequestId==expected.geometryRequestId
                && observation.actionContext==expected.actionContext && observation.geometryContext==expected.geometryContext
                && contextMatches binding observation.actionContext && contextMatches binding observation.geometryContext
                && observation.actionContext.output==observation.geometryContext.output
        in if expectedValid && correlated then Ok (ReservationReleased binding record release) else Err "Uncorrelated retirement or current observation")
