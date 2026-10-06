module NativeActorRetirement exposing (Fact, Ledger, Observation, actorDecoder, admittedAfter, bindingValue, empty, fresh, observationDecoder, owner, readyCommand, settles)

import Json.Decode as D
import Json.Encode as E
import UInt64 exposing (Counter)

type alias Observation =
    { lifetime : Counter, session : Counter, frontend : Counter, subject : Counter
    , request : Counter, sequence : Counter, clock : Counter, now : Counter, issuedThrough : Counter }

type alias Fact =
    { native : Observation, entry : Counter, entryIssuedThrough : Counter, requestFloor : Counter }

type alias Ledger =
    { observed : Maybe Observation, settled : Maybe Fact }

empty : Ledger
empty = { observed = Nothing, settled = Nothing }

strict : List String -> D.Decoder a -> D.Decoder a
strict fields decoder =
    D.keyValuePairs D.value |> D.andThen (\pairs ->
        if List.sort (List.map Tuple.first pairs) == List.sort fields then decoder
        else D.fail "Exact native actor retirement fields")

positive : D.Decoder Counter
positive =
    UInt64.decoder |> D.andThen (\value ->
        if value /= UInt64.zero then D.succeed value else D.fail "Positive native retirement identity")

owner : Observation -> String
owner value = String.join ":" (List.map UInt64.string [value.lifetime,value.session,value.frontend])

bindingValue : Observation -> E.Value
bindingValue value =
    E.object [("lifetime",E.string (UInt64.string value.lifetime)),("session",E.string (UInt64.string value.session)),("frontend",E.string (UInt64.string value.frontend))]

nativeDecoder : D.Decoder Observation
nativeDecoder =
    D.map2 (\(lifetime,session,frontend) construct -> construct lifetime session frontend)
        (D.field "binding" (strict ["lifetime","session","frontend"]
            (D.map3 (\a b c -> (a,b,c)) (D.field "lifetime" positive) (D.field "session" positive) (D.field "frontend" positive))))
        (D.map6 (\subject request sequence clock now issuedThrough ->
            \lifetime session frontend ->
                {lifetime=lifetime,session=session,frontend=frontend,subject=subject,request=request,sequence=sequence,clock=clock,now=now,issuedThrough=issuedThrough})
            (D.field "subject" positive) (D.field "request" positive) (D.field "sequence" positive)
            (D.field "clock" positive) (D.field "now" positive) (D.field "issuedThrough" UInt64.decoder))

validate : Observation -> Bool
validate value =
    value.clock == value.lifetime && UInt64.compare value.subject value.issuedThrough /= GT

observationDecoder : D.Decoder Observation
observationDecoder =
    strict ["kind","binding","subject","request","sequence","clock","now","issuedThrough","state"]
        (D.map2 Tuple.pair nativeDecoder (D.field "state" D.string))
        |> D.andThen (\(value,state) ->
            if state == "Retired" && validate value then D.succeed value
            else D.fail "Exact permanent native retirement observation")

actorDecoder : D.Decoder Fact
actorDecoder =
    strict ["kind","identity","binding","subject","entry","entryIssuedThrough","requestFloor","request","sequence","clock","now","issuedThrough"]
        (D.map5 (\native entry frontier floor identity -> (Fact native entry frontier floor,identity))
            nativeDecoder (D.field "entry" positive) (D.field "entryIssuedThrough" positive)
            (D.field "requestFloor" UInt64.decoder) (D.field "identity" D.string))
        |> D.andThen (\(fact,identity) ->
            if validate fact.native && identity == "family:" ++ UInt64.string fact.native.subject &&
                UInt64.compare fact.entry fact.entryIssuedThrough /= GT then D.succeed fact
            else D.fail "Exact native aggregate retirement fact")

fresh : Maybe Observation -> Observation -> Bool
fresh previous incoming =
    previous |> Maybe.map (\old ->
        owner incoming == owner old && incoming.clock == old.clock &&
        UInt64.compare incoming.request old.request == GT &&
        UInt64.compare incoming.sequence old.sequence == GT &&
        UInt64.compare incoming.now old.now /= LT &&
        UInt64.compare incoming.issuedThrough old.issuedThrough /= LT)
        |> Maybe.withDefault True

settles : Observation -> Fact -> Bool
settles pending fact =
    fact.native.subject == pending.subject && fresh (Just pending) fact.native

-- Source observations and retirement observations have separate sequence
-- domains. Compare the original native clock only; never compare their IDs.
-- This compact cutoff rejects historical seeds for absent, retired entries.
admittedAfter : Ledger -> String -> D.Value -> Bool
admittedAfter ledger binding raw =
    case ledger.settled of
        Nothing -> True
        Just final ->
            case D.decodeValue (D.map2 Tuple.pair (D.field "clock" positive) (D.field "now" positive)) raw of
                Ok (clock,now) ->
                    binding == owner final.native && clock == final.native.clock &&
                    UInt64.compare now final.native.now == GT
                Err _ -> False

readyCommand : Observation -> E.Value
readyCommand value =
    E.object [("kind",E.string "retire-ready"),("binding",bindingValue value),
        ("subject",E.string (UInt64.string value.subject)),
        ("observationRequest",E.string (UInt64.string value.request)),
        ("observationSequence",E.string (UInt64.string value.sequence))]
