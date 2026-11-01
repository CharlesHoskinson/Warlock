port module RetirementProofReplay exposing (main)

-- QA-only decoder and correlation fixture for ReconciliationFrame.Proof ADTs,
-- ReconciliationTracking correlation, and SurfaceController reconciliation
-- transitions. Synthetic JSON inputs exercise Elm decoding and pure state/effect
-- correlation only; they are NOT authenticated native proofs or native/release
-- acceptance evidence.

import Binding
import Desktop
import Json.Decode as D
import Json.Encode as E
import Platform
import ReconciliationFrame as R
import ReconciliationTracking as Tracking
import Shell
import SurfaceController as Controller
import UInt64


port outgoing : E.Value -> Cmd msg


counter : String -> UInt64.Counter
counter value =
    D.decodeValue UInt64.decoder (E.string value) |> Result.withDefault UInt64.zero


lifetime : String
lifetime =
    "9007199254741001"


session : String
session =
    "9007199254741201"


oldEpoch : String
oldEpoch =
    "9007199254741101"


currentEpoch : String
currentEpoch =
    "9007199254741102"


foreignLifetime : String
foreignLifetime =
    "9007199254749999"


outputId : String
outputId =
    "9007199254741301"


otherOutputId : String
otherOutputId =
    "9007199254741302"


incarnation : String
incarnation =
    "9007199254741701"


proofRequestId : String
proofRequestId =
    "9007199254741801"


bindingRaw : String -> String -> String -> E.Value
bindingRaw life sess front =
    E.object
        [ ( "lifetime", E.string life )
        , ( "session", E.string sess )
        , ( "frontend", E.string front )
        ]


oldBindingRaw : E.Value
oldBindingRaw =
    bindingRaw lifetime session oldEpoch


currentBindingRaw : E.Value
currentBindingRaw =
    bindingRaw lifetime session currentEpoch


foreignBindingRaw : E.Value
foreignBindingRaw =
    bindingRaw foreignLifetime session currentEpoch


contextRaw : String -> String -> String -> String -> E.Value
contextRaw life epoch out rev =
    E.object
        [ ( "lifetime", E.string life )
        , ( "epoch", E.string epoch )
        , ( "output", E.string out )
        , ( "revision", E.string rev )
        ]


intentRaw : String -> String -> E.Value
intentRaw life epoch =
    E.object
        [ ( "request", E.string "9007199254741501" )
        , ( "generation", E.string "9007199254741601" )
        , ( "incarnation", E.string incarnation )
        , ( "operation", E.string "activate" )
        , ( "context", contextRaw life epoch outputId "9007199254741401" )
        ]


recordRaw : E.Value -> String -> String -> E.Value
recordRaw bind life epoch =
    E.object
        [ ( "schema", E.int 2 )
        , ( "effectProtocol", E.int 1 )
        , ( "binding", bind )
        , ( "intent", intentRaw life epoch )
        , ( "status", E.string "Unknown" )
        ]


validRecordRaw : E.Value
validRecordRaw =
    recordRaw oldBindingRaw lifetime oldEpoch


proofFields : Int -> String -> Int -> String -> E.Value -> String -> E.Value -> String -> String -> List ( String, E.Value )
proofFields version kind retirementProto op bind req queried seq grant =
    [ ( "protocolVersion", E.int version )
    , ( "kind", E.string kind )
    , ( "retirementProtocol", E.int retirementProto )
    , ( "operation", E.string op )
    , ( "binding", bind )
    , ( "requestId", E.string req )
    , ( "queriedBinding", queried )
    , ( "sequence", E.string seq )
    , ( "grantState", E.string grant )
    ]


observeProofRaw : E.Value
observeProofRaw =
    E.object (proofFields 3 "binding-retirement" 1 "observe" currentBindingRaw proofRequestId oldBindingRaw "1" "Retired")


retireProofRaw : E.Value
retireProofRaw =
    E.object (proofFields 3 "binding-retirement" 1 "retire" currentBindingRaw proofRequestId oldBindingRaw "1" "Retired")


retireProofSeq2Raw : E.Value
retireProofSeq2Raw =
    E.object (proofFields 3 "binding-retirement" 1 "retire" currentBindingRaw "9007199254741802" oldBindingRaw "2" "Retired")


unknownFrameRaw : E.Value -> E.Value
unknownFrameRaw bind =
    E.object
        [ ( "protocolVersion", E.int 3 )
        , ( "kind", E.string "host-reservation-unknown" )
        , ( "binding", bind )
        , ( "record", validRecordRaw )
        ]


releaseId64 : String
releaseId64 =
    String.repeat 64 "a"


releaseFrameRaw : E.Value -> String -> String -> E.Value -> E.Value -> E.Value
releaseFrameRaw proof actReq geomReq actCtx geomCtx =
    E.object
        [ ( "protocolVersion", E.int 3 )
        , ( "kind", E.string "host-reservation-released" )
        , ( "binding", currentBindingRaw )
        , ( "record", validRecordRaw )
        , ( "release"
          , E.object
                [ ( "id", E.string releaseId64 )
                , ( "proof", proof )
                , ( "observation"
                  , E.object
                        [ ( "actionRequestId", E.string actReq )
                        , ( "geometryRequestId", E.string geomReq )
                        , ( "actionContext", actCtx )
                        , ( "geometryContext", geomCtx )
                        ]
                  )
                ]
          )
        ]


nativeFrame : String -> List ( String, E.Value ) -> E.Value
nativeFrame kind fields =
    E.object ([ ( "protocolVersion", E.int 3 ), ( "kind", E.string kind ) ] ++ fields)


actionProjection : String -> String -> E.Value
actionProjection req rev =
    nativeFrame "action-projection"
        [ ( "binding", currentBindingRaw )
        , ( "requestId", E.string req )
        , ( "context", contextRaw lifetime currentEpoch outputId rev )
        , ( "scene"
          , E.object
                [ ( "revision", E.string rev )
                , ( "focused", E.null )
                , ( "windows", E.list identity [] )
                ]
          )
        ]


geometryFacts : String -> String -> String -> String -> E.Value
geometryFacts req seq rev out =
    nativeFrame "geometry-facts"
        [ ( "geometryProtocol", E.int 3 )
        , ( "binding", currentBindingRaw )
        , ( "requestId", E.string req )
        , ( "sequence", E.string seq )
        , ( "revision", E.string rev )
        , ( "outputGeneration", E.string out )
        , ( "facts"
          , E.object
                [ ( "focused", E.null )
                , ( "inputBlocked", E.bool False )
                , ( "windows", E.list identity [] )
                ]
          )
        ]


step : D.Value -> Controller.Model -> ( Controller.Model, List Controller.Effect )
step raw model =
    Controller.update (Controller.Interaction (Desktop.Incoming raw)) model


feed : D.Value -> Controller.Model -> Controller.Model
feed raw model =
    step raw model |> Tuple.first


shell : Controller.Model -> Shell.Model
shell model =
    (Controller.desktop model).windows.shell


expectedId : (Shell.Model -> Maybe UInt64.Counter) -> Controller.Model -> String
expectedId accessor model =
    accessor (shell model) |> Maybe.map UInt64.string |> Maybe.withDefault "0"


decodeRejected : D.Decoder a -> D.Value -> Bool
decodeRejected decoder raw =
    case D.decodeValue decoder raw of
        Ok _ ->
            False

        Err _ ->
            True


isReconciliationReadyFor : String -> E.Value -> Controller.Effect -> Bool
isReconciliationReadyFor expectedProofReq expectedQueried effect =
    case effect of
        Controller.DesktopEffect (Desktop.Send wire) ->
            D.decodeValue (D.field "kind" D.string) wire == Ok "reconciliation-ready"
                && D.decodeValue (D.field "protocolVersion" D.int) wire == Ok 3
                && D.decodeValue (D.field "proofRequestId" D.string) wire == Ok expectedProofReq
                && D.decodeValue (D.field "queriedBinding" Binding.decoder) wire == D.decodeValue Binding.decoder expectedQueried

        _ ->
            False


result : E.Value
result =
    let
        decodedObserve =
            D.decodeValue R.proofDecoder observeProofRaw

        decodedRetire =
            D.decodeValue R.proofDecoder retireProofRaw

        attached =
            nativeFrame "attached" [ ( "binding", currentBindingRaw ) ]

        negotiate =
            nativeFrame "host-geometry-negotiate" []

        afterAttached =
            feed attached Controller.initial

        afterInitialProj =
            feed (actionProjection (expectedId .expected afterAttached) "10") afterAttached

        afterNegotiate =
            feed negotiate afterInitialProj

        caps =
            nativeFrame "geometry-attached"
                [ ( "geometryProtocol", E.int 3 )
                , ( "binding", currentBindingRaw )
                , ( "requestId", E.string (expectedId .geometryAttachExpected afterNegotiate) )
                , ( "capabilities"
                  , E.object
                        [ ( "observe", E.bool True )
                        , ( "effects", E.bool True )
                        , ( "effectProtocol", E.int 2 )
                        , ( "operations", E.list E.string [ "maximize", "restore-geometry", "pin", "unpin" ] )
                        , ( "placementCapacity", E.int 256 )
                        , ( "canonicalScene", E.bool False )
                        ]
                  )
                ]

        afterCaps =
            feed caps afterNegotiate

        readyController =
            feed (geometryFacts (expectedId .geometryExpected afterCaps) "1" "10" outputId) afterCaps

        afterUnknown =
            feed (unknownFrameRaw currentBindingRaw) readyController

        ( afterAnnounce, announceEffects ) =
            step retireProofRaw afterUnknown

        actReqStr =
            expectedId .expected afterAnnounce

        geomReqStr =
            expectedId .geometryExpected afterAnnounce

        afterActObs =
            feed (actionProjection actReqStr "11") afterAnnounce

        afterBothObs =
            feed (geometryFacts geomReqStr "2" "11" outputId) afterActObs

        obsCtxRaw =
            contextRaw lifetime currentEpoch outputId "11"

        validReleaseRaw =
            releaseFrameRaw retireProofRaw actReqStr geomReqStr obsCtxRaw obsCtxRaw

        mutatedOpReleaseRaw =
            releaseFrameRaw observeProofRaw actReqStr geomReqStr obsCtxRaw obsCtxRaw

        wrongActReqReleaseRaw =
            releaseFrameRaw retireProofRaw "999" geomReqStr obsCtxRaw obsCtxRaw

        mismatchedOutputReleaseRaw =
            releaseFrameRaw retireProofRaw actReqStr geomReqStr obsCtxRaw (contextRaw lifetime currentEpoch otherOutputId "11")

        legacyUncertainRaw =
            nativeFrame "host-uncertain"
                [ ( "binding", currentBindingRaw )
                , ( "effectProtocol", E.int 1 )
                , ( "intent", intentRaw lifetime oldEpoch )
                ]

        afterMutatedController =
            feed mutatedOpReleaseRaw afterBothObs

        afterValidController =
            feed validReleaseRaw afterBothObs

        bindingChecks =
            case ( D.decodeValue Binding.decoder oldBindingRaw, D.decodeValue Binding.decoder currentBindingRaw, D.decodeValue Binding.decoder foreignBindingRaw ) of
                ( Ok oldBind, Ok currentBind, Ok foreignBind ) ->
                    let
                        trackingReady =
                            Controller.reconciliation afterBothObs

                        reannouncedHigher =
                            Tracking.announce currentBind retireProofSeq2Raw (Controller.reconciliation afterAnnounce)

                        nonIncreasingSeqRejected =
                            case reannouncedHigher of
                                Ok advanced ->
                                    Tracking.announce currentBind retireProofRaw advanced == Err "Uncorrelated proof announcement"

                                Err _ ->
                                    False

                        reconcilingShell =
                            let
                                currentShell =
                                    shell afterBothObs
                            in
                            { currentShell | phase = Shell.Reconciling }

                        legacyMarked =
                            Tracking.legacy legacyUncertainRaw reconcilingShell trackingReady

                        trackingReleasedResult =
                            Tracking.release currentBind validReleaseRaw trackingReady
                    in
                    { foreignUnknownRejected = R.decodeUnknown currentBind (unknownFrameRaw oldBindingRaw) == Err "Foreign current binding"
                    , uncorrelatedAnnounceRejected =
                        Tracking.announce currentBind retireProofRaw Tracking.empty == Err "Uncorrelated proof announcement"
                            && Tracking.announce currentBind (E.object (proofFields 3 "binding-retirement" 1 "retire" foreignBindingRaw proofRequestId oldBindingRaw "1" "Retired")) (Controller.reconciliation afterUnknown) == Err "Uncorrelated proof announcement"
                            && Tracking.announce currentBind (E.object (proofFields 3 "binding-retirement" 1 "retire" currentBindingRaw proofRequestId currentBindingRaw "1" "Retired")) (Controller.reconciliation afterUnknown) == Err "Uncorrelated proof announcement"
                            && Tracking.announce foreignBind retireProofRaw (Controller.reconciliation afterUnknown) == Err "Uncorrelated proof announcement"
                            && nonIncreasingSeqRejected
                    , prematureReleaseRejected =
                        Tracking.release currentBind validReleaseRaw (Controller.reconciliation afterActObs) == Err "Proof and both accepted observations required"
                    , changedOperationRejected =
                        Tracking.release currentBind mutatedOpReleaseRaw trackingReady == Err "Announced proof changed"
                    , mismatchedObservationRejected =
                        Tracking.release currentBind wrongActReqReleaseRaw trackingReady == Err "Uncorrelated retirement or current observation"
                            && Tracking.release currentBind mismatchedOutputReleaseRaw trackingReady == Err "Uncorrelated retirement or current observation"
                    , legacyBlocksRelease =
                        Tracking.release currentBind validReleaseRaw legacyMarked == Err "Legacy origin remains unsupported"
                    , correlatedReleaseSucceeds =
                        case trackingReleasedResult of
                            Ok ( releasedTracking, releasedRecord ) ->
                                releasedRecord.binding == oldBind
                                    && List.length releasedTracking.slots == 1
                                    && List.all .released releasedTracking.slots
                                    && Tracking.unknown currentBind (unknownFrameRaw currentBindingRaw) releasedTracking == Err "Historical reservation already released"

                            Err _ ->
                                False
                    }

                _ ->
                    { foreignUnknownRejected = False
                    , uncorrelatedAnnounceRejected = False
                    , prematureReleaseRejected = False
                    , changedOperationRejected = False
                    , mismatchedObservationRejected = False
                    , legacyBlocksRelease = False
                    , correlatedReleaseSucceeds = False
                    }

        checked name value =
            ( name, E.bool value )

        checks =
            [ checked "observeProofDecodesTypedConstructorsAndNames"
                (case decodedObserve of
                    Ok proof ->
                        proof.protocolVersion == 3
                            && proof.kind == R.BindingRetirement
                            && proof.retirementProtocol == 1
                            && proof.operation == R.Observe
                            && proof.requestId == counter proofRequestId
                            && proof.sequence == counter "1"
                            && proof.grantState == R.Retired
                            && R.proofKindName proof.kind == "binding-retirement"
                            && R.retirementOperationName proof.operation == "observe"
                            && R.grantStateName proof.grantState == "Retired"

                    Err _ ->
                        False
                )
            , checked "retireProofDecodesTypedConstructorsAndNames"
                (case ( decodedRetire, decodedObserve ) of
                    ( Ok retireProof, Ok observeProof ) ->
                        retireProof.kind == R.BindingRetirement
                            && retireProof.operation == R.Retire
                            && retireProof.grantState == R.Retired
                            && R.retirementOperationName retireProof.operation == "retire"
                            && retireProof /= observeProof

                    _ ->
                        False
                )
            , checked "wrongKindRefused"
                (decodeRejected R.proofDecoder (E.object (proofFields 3 "host-reservation-released" 1 "retire" currentBindingRaw proofRequestId oldBindingRaw "1" "Retired")))
            , checked "wrongGrantStateRefused"
                (decodeRejected R.proofDecoder (E.object (proofFields 3 "binding-retirement" 1 "retire" currentBindingRaw proofRequestId oldBindingRaw "1" "Active"))
                    && decodeRejected R.proofDecoder (E.object (proofFields 3 "binding-retirement" 1 "retire" currentBindingRaw proofRequestId oldBindingRaw "1" "retired"))
                )
            , checked "wrongProtocolVersionRefused"
                (decodeRejected R.proofDecoder (E.object (proofFields 2 "binding-retirement" 1 "retire" currentBindingRaw proofRequestId oldBindingRaw "1" "Retired")))
            , checked "wrongRetirementProtocolRefused"
                (decodeRejected R.proofDecoder (E.object (proofFields 3 "binding-retirement" 2 "retire" currentBindingRaw proofRequestId oldBindingRaw "1" "Retired")))
            , checked "extraFieldRefused"
                (decodeRejected R.proofDecoder (E.object ((proofFields 3 "binding-retirement" 1 "retire" currentBindingRaw proofRequestId oldBindingRaw "1" "Retired") ++ [ ( "extra", E.string "1" ) ])))
            , checked "missingFieldRefused"
                (decodeRejected R.proofDecoder (E.object (List.take 8 (proofFields 3 "binding-retirement" 1 "retire" currentBindingRaw proofRequestId oldBindingRaw "1" "Retired"))))
            , checked "invalidOperationRefused"
                (decodeRejected R.proofDecoder (E.object (proofFields 3 "binding-retirement" 1 "cancel" currentBindingRaw proofRequestId oldBindingRaw "1" "Retired"))
                    && decodeRejected R.proofDecoder (E.object (proofFields 3 "binding-retirement" 1 "Retire" currentBindingRaw proofRequestId oldBindingRaw "1" "Retired"))
                )
            , checked "zeroCounterRefused"
                (decodeRejected R.proofDecoder (E.object (proofFields 3 "binding-retirement" 1 "retire" currentBindingRaw "0" oldBindingRaw "1" "Retired"))
                    && decodeRejected R.proofDecoder (E.object (proofFields 3 "binding-retirement" 1 "retire" currentBindingRaw proofRequestId oldBindingRaw "0" "Retired"))
                )
            , checked "foreignBindingUnknownRefused"
                bindingChecks.foreignUnknownRejected
            , checked "recordBindingContextMismatchRefused"
                (decodeRejected R.recordDecoder (recordRaw oldBindingRaw lifetime currentEpoch))
            , checked "uncorrelatedAnnouncementRefused"
                bindingChecks.uncorrelatedAnnounceRejected
            , checked "prematureReleaseWithoutBothObservationsRefused"
                bindingChecks.prematureReleaseRejected
            , checked "changedOperationInReleaseProofRefused"
                bindingChecks.changedOperationRejected
            , checked "mismatchedObservationRequestOrOutputRefused"
                bindingChecks.mismatchedObservationRejected
            , checked "legacyUncertainOriginBlocksRelease"
                bindingChecks.legacyBlocksRelease
            , checked "correlatedTrackingReleaseSucceedsAndPreventsReplay"
                bindingChecks.correlatedReleaseSucceeds
            , checked "owningRouteAnnounceEmitsReconciliationReadyAndRetainsTypedProof"
                (List.any (isReconciliationReadyFor proofRequestId oldBindingRaw) announceEffects
                    && (case (Controller.reconciliation afterAnnounce).slots of
                            [ slot ] ->
                                (slot.proof
                                    |> Maybe.map (\proof -> proof.kind == R.BindingRetirement && proof.operation == R.Retire && proof.grantState == R.Retired)
                                    |> Maybe.withDefault False
                                )
                                    && slot.actionRequest == Just (counter actReqStr)
                                    && slot.geometryRequest == Just (counter geomReqStr)

                            _ ->
                                False
                       )
                )
            , checked "owningRouteCorrelatedReleaseClearsUnresolvedUnknown"
                (List.length (shell afterMutatedController).effects.unresolved == 1
                    && List.isEmpty (shell afterValidController).effects.unresolved
                    && List.all .released (Controller.reconciliation afterValidController).slots
                )
            ]
    in
    E.object
        [ ( "checks", E.object checks )
        , ( "observeProofRaw", observeProofRaw )
        , ( "retireProofRaw", retireProofRaw )
        , ( "validReleaseRaw", validReleaseRaw )
        , ( "mutatedOpReleaseRaw", mutatedOpReleaseRaw )
        ]


main : Program () () Never
main =
    Platform.worker
        { init = \() -> ( (), outgoing result )
        , update = \_ model -> ( model, Cmd.none )
        , subscriptions = \_ -> Sub.none
        }
