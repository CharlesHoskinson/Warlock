port module Arc004RefusalReplay exposing (main)

{-| Source-only production Session.update replay. Root compiles and executes. -}
import Protocol.Authority as A
import Json.Decode as D
import Json.Encode as E
import Platform
import Protocol.Session as Session

port result : E.Value -> Cmd msg

binding : E.Value
binding =
    E.object [("lifetime",E.string "1"),("session",E.string "2"),("frontend",E.string "3")]

envelope : Int -> String -> E.Value -> E.Value
envelope version kind body =
    E.object [("version",E.int version),("kind",E.string kind),("body",body)]

hello : E.Value
hello = envelope 2 "hello" (E.object [("binding",binding)])

badBody : E.Value
badBody = envelope 2 "hello" (E.object [("binding",E.null)])

badVersion : E.Value
badVersion = envelope 3 "hello" (E.object [("binding",binding)])

extraField : E.Value
extraField = E.object [("version",E.int 2),("kind",E.string "hello"),("body",E.object [("binding",binding)]),("unexpected",E.string "do-not-record")]

capabilities : E.Value
capabilities =
    envelope 2 "capabilities" (E.object [("binding",binding),("requestId",E.string "4"),("operations",E.list E.string ["restore"]),("maxPreparedPerSession",E.int 1),("maxPreparedGlobal",E.int 64),("deadlineClock",E.string "CLOCK_MONOTONIC")])

check : String -> Bool -> ( String, E.Value )
check name passed = (name,E.bool passed)

run : E.Value
run =
    case D.decodeValue A.counterDecoder (E.string "4") of
        Err _ ->
            E.object [("fixtureCounterValid",E.bool False)]

        Ok request ->
            let
                ( attached, helloWrites ) = Session.update (Session.Backend hello) Session.initial
                ( prior, negotiationWrites ) = Session.update (Session.StartNegotiation request) attached
                ( malformed, malformedWrites ) = Session.update (Session.Backend badBody) prior
                ( unsupported, unsupportedWrites ) = Session.update (Session.Backend badVersion) prior
                ( extra, extraWrites ) = Session.update (Session.Backend extraField) prior
                ( unknownKind, unknownWrites ) = Session.update (Session.Backend (envelope 2 "not-a-known-kind" (E.object []))) prior
                ( wrongType, wrongTypeWrites ) = Session.update (Session.Backend (E.object [("version",E.string "2"),("kind",E.string "hello"),("body",E.object [("binding",binding)])])) prior
                repeated = List.foldl (\_ m -> Session.update (Session.Backend badBody) m |> Tuple.first) prior (List.range 1 1000)
                ( ready, readyWrites ) = Session.update (Session.Backend capabilities) malformed
                ( noSelection, noSelectionWrites ) = Session.update (Session.Decide "commit") malformed
            in
            E.object
                [ check "fixtureCounterValid" True
                , check "validHelloBound" ((Session.snapshot attached).current /= Nothing && List.isEmpty helloWrites)
                , check "realNegotiationEmitsOnce" (List.length negotiationWrites == 1 && not (Session.samePolicy prior attached))
                , check "malformedHasTypedReason" (Session.refusalReason malformed == Just Session.MalformedEnvelope)
                , check "reasonCodesBoundedAndDistinct" (Session.refusalCode Session.MalformedEnvelope == "malformed-envelope" && Session.refusalCode Session.UnsupportedVersion == "unsupported-version")
                , check "malformedPreservesAllPolicy" (Session.samePolicy prior malformed && List.isEmpty malformedWrites)
                , check "unsupportedHasDistinctTypedReason" (Session.refusalReason unsupported == Just Session.UnsupportedVersion)
                , check "unsupportedPreservesAllPolicy" (Session.samePolicy prior unsupported && List.isEmpty unsupportedWrites)
                , check "unknownFieldRefuses" (Session.refusalReason extra == Just Session.MalformedEnvelope && Session.samePolicy prior extra && List.isEmpty extraWrites)
                , check "unsupportedKindRefuses" (Session.refusalReason unknownKind == Just Session.MalformedEnvelope && Session.samePolicy prior unknownKind && List.isEmpty unknownWrites)
                , check "nonnumericVersionRefuses" (Session.refusalReason wrongType == Just Session.MalformedEnvelope && Session.samePolicy prior wrongType && List.isEmpty wrongTypeWrites)
                , check "repeatedRefusalBounded" (Session.refusalReason repeated == Just Session.MalformedEnvelope && Session.samePolicy repeated prior)
                , check "validAfterRefusalReachesActualCapability" ((Session.snapshot ready).capable && List.isEmpty readyWrites && not (Session.samePolicy ready malformed))
                , check "validAfterRefusalRetainsObservation" (Session.refusalReason ready == Just Session.MalformedEnvelope)
                , check "noAuthorityOrIntentFromRefusal" (Session.samePolicy noSelection malformed && List.isEmpty noSelectionWrites)
                ]

main : Program () () Never
main =
    Platform.worker
        { init = \_ -> ( (), result run )
        , update = \_ model -> ( model, Cmd.none )
        , subscriptions = \_ -> Sub.none
        }
