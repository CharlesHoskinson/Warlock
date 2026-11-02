port module GeometryCapabilitySequences exposing (main)

{-| Unexecuted QA draft. Exercises Shell.Incoming geometry negotiation and
Effects.beginGeometry, not native authority or compositor behavior. The
trusted typed geometry/legacy scene prelude is SnapReplay.readyFor; each
capability is admitted through the real geometry-attached decoder. Literals
below are independent wire/guard oracles; no reducer output creates an expected
operation list. Deterministic exhaustive 2^7 subsets and six seeded rotations.
Requires terra-security GeometryProjection.capabilityName migration; Root
owns integration, compilation and execution. -}

import Binding
import Effects
import GeometryProjection as Geometry
import Json.Decode as D
import Json.Encode as E
import Platform
import Shell
import Snap
import SnapReplay
import Transfer
import UInt64

port outgoing : E.Value -> Cmd msg

wireNames : List String
wireNames =
    [ "maximize", "restore-geometry", "snap", "transfer-workspace"
    , "pin", "unpin", "exit-fullscreen" ]

subsets : List a -> List (List a)
subsets xs =
    case xs of
        [] -> [ [] ]
        first :: rest ->
            let smaller = subsets rest
            in smaller ++ List.map (\entry -> first :: entry) smaller

rotate : Int -> List a -> List a
rotate seed xs =
    let n = modBy (List.length xs) seed
    in List.drop n xs ++ List.take n xs

capability : List String -> Bool -> E.Value
capability operations effects = E.object
    [ ("observe", E.bool True), ("effects", E.bool effects), ("effectProtocol", E.int 2)
    , ("operations", E.list E.string operations), ("placementCapacity", E.int 256)
    , ("canonicalScene", E.bool False) ]

attached : E.Value -> E.Value -> E.Value -> E.Value
attached owner request caps = E.object
    [ ("protocolVersion", E.int 3), ("kind", E.string "geometry-attached")
    , ("geometryProtocol", E.int 3), ("binding", owner), ("requestId", request)
    , ("capabilities", caps) ]

negotiate : E.Value
negotiate = E.object [("protocolVersion",E.int 3),("kind",E.string "host-geometry-negotiate")]

kind : Shell.Effect -> Maybe String
kind effect =
    case effect of
        Shell.Send wire -> D.decodeValue (D.field "kind" D.string) wire |> Result.toMaybe
        _ -> Nothing

resultFor : Binding.Binding -> E.Value
resultFor binding =
    let
        ready = (SnapReplay.readyFor binding).windows.shell
        base = {ready | geometry=Nothing, geometryCaps=Nothing, geometryExpected=Nothing, geometryAttachExpected=Nothing, attachNeeded=False}
        (pending, startup) = Shell.update (Shell.Incoming negotiate) base
        request = pending.geometryAttachExpected |> Maybe.map (UInt64.string >> E.string) |> Maybe.withDefault E.null
        wire owner req operations = attached owner req (capability operations (not (List.isEmpty operations)))
        allSets = subsets wireNames
        seededSets = List.concatMap (\seed -> subsets (rotate seed wireNames)) [0,1,3,11,29,65535]
        accept operations =
            let (next, commands) = Shell.update (Shell.Incoming (wire SnapReplay.bound request operations)) pending
            in next.geometryAttachExpected == Nothing
                && (next.geometryCaps |> Maybe.map (\caps -> caps.effects == not (List.isEmpty operations) && List.map Geometry.capabilityName caps.operations == operations) |> Maybe.withDefault False)
                && next.geometryExpected == UInt64.next pending.request
                && List.filterMap kind commands == ["geometry-facts-request"]
        original = SnapReplay.geometryFor binding
        candidate = Snap.open original (SnapReplay.counter "1") |> Maybe.andThen Snap.proposal
        snapAllowed operations =
            case (D.decodeValue Geometry.capabilitiesDecoder (capability operations (not (List.isEmpty operations))),candidate) of
                (Ok caps,Just placement) ->
                    let (next, sent, err) = Effects.beginGeometry caps original (Effects.SnapPlacement placement) (SnapReplay.counter "1") ready.effects
                        allowed = List.member "snap" operations
                    in if allowed then sent /= Nothing && err == Nothing && next.transaction /= Nothing
                       else next == ready.effects && sent == Nothing && err == Just "Geometry operation not negotiated"
                _ -> False
        maxAllowed operations =
            case D.decodeValue Geometry.capabilitiesDecoder (capability operations (not (List.isEmpty operations))) of
                Err _ -> False
                Ok caps ->
                    let (next, sent, err) = Effects.beginGeometry caps original Effects.Maximize (SnapReplay.counter "1") ready.effects
                    in if List.member "maximize" operations then sent /= Nothing && err == Nothing && next.transaction /= Nothing
                       else next == ready.effects && sent == Nothing && err == Just "Geometry operation not negotiated"
        -- The seven actual operation constructors have deliberately different
        -- admissible observed rows. The wire name is an independent literal.
        -- Each begin is a fresh given; no mutation or receipt is replayed.
        withRow change = {original | windows=List.map change original.windows}
        restoreGeometry = withRow (\row -> {row | nativeMode=Geometry.Maximized,clientMode=Geometry.Maximized,maximize=False,restoreGeometry=True,placementKnown=True})
        fullscreenGeometry = withRow (\row -> {row | nativeMode=Geometry.Fullscreen,clientMode=Geometry.Fullscreen,eligible=False,maximize=False,restoreGeometry=False,pin=Just {pinned=False,eligible=False}})
        pinGeometry = withRow (\row -> {row | pin=Just {pinned=False,eligible=True}})
        unpinGeometry = withRow (\row -> {row | pin=Just {pinned=True,eligible=True}})
        transfer = Transfer.propose original (SnapReplay.counter "1") "2"
        sevenOperations = case (candidate,transfer) of
            (Just placement,Just destination) ->
                [ {name="maximize",operation=Effects.Maximize,observed=original}
                , {name="restore-geometry",operation=Effects.RestoreGeometry,observed=restoreGeometry}
                , {name="snap",operation=Effects.SnapPlacement placement,observed=original}
                , {name="transfer-workspace",operation=Effects.TransferWorkspace destination,observed=original}
                , {name="pin",operation=Effects.Pin,observed=pinGeometry}
                , {name="unpin",operation=Effects.Unpin,observed=unpinGeometry}
                , {name="exit-fullscreen",operation=Effects.ExitFullscreen,observed=fullscreenGeometry}
                ]
            _ -> []
        allocation operations item =
            case D.decodeValue Geometry.capabilitiesDecoder (capability operations (not (List.isEmpty operations))) of
                Err _ -> False
                Ok capabilities ->
                    let (next, sent, problem) = Effects.beginGeometry capabilities item.observed item.operation (SnapReplay.counter "1") ready.effects
                    in if List.member item.name operations then
                        problem == Nothing && (next.transaction |> Maybe.map (\transaction -> transaction.status==Effects.Pending && transaction.intent.operation==item.operation) |> Maybe.withDefault False)
                            && (sent |> Maybe.andThen (D.decodeValue (D.at ["intent","operation"] D.string) >> Result.toMaybe)) == Just item.name
                       else next == ready.effects && sent == Nothing && problem == Just "Geometry operation not negotiated"
        receipt status intent = E.object [("kind",E.string "receipt"),("effectProtocol",E.int 2),("intent",Effects.encodeIntent intent),("status",E.string status)]
        receiptSequence item =
            case D.decodeValue Geometry.capabilitiesDecoder (capability wireNames True) of
                Err _ -> False
                Ok capabilities ->
                    let (pendingEffects,wireValue,issueError)=Effects.beginGeometry capabilities item.observed item.operation (SnapReplay.counter "1") ready.effects
                    in case pendingEffects.transaction of
                        Nothing -> False
                        Just transaction ->
                            let
                                originalIntent = transaction.intent
                                changedIntent = {originalIntent | request=SnapReplay.counter "999"}
                                (mismatch,mismatchWire,mismatchError)=Effects.apply (receipt "Refused" changedIntent) pendingEffects
                                (unknown,unknownWire,unknownError)=Effects.apply (receipt "Unknown" transaction.intent) pendingEffects
                                (repeatUnknown,repeatWire,repeatError)=Effects.beginGeometry capabilities item.observed item.operation (SnapReplay.counter "1") unknown
                                (refused,refusedWire,refusedError)=Effects.apply (receipt "Refused" transaction.intent) pendingEffects
                            in wireValue /= Nothing && issueError == Nothing
                                && mismatch==pendingEffects && mismatchWire==Nothing && mismatchError==Just "Stale, mismatched or terminal receipt"
                                && unknownWire==Nothing && unknownError==Nothing
                                && (unknown.transaction |> Maybe.map (\tx -> tx.status==Effects.Unknown && tx.intent==transaction.intent) |> Maybe.withDefault False)
                                && repeatUnknown==unknown && repeatWire==Nothing && repeatError==Just "Unresolved or disconnected native operation"
                                && refusedWire==Nothing && refusedError==Nothing && List.isEmpty refused.unresolved
                                && refused.request==pendingEffects.request && refused.generation==pendingEffects.generation
                                && (refused.transaction |> Maybe.map (\tx -> tx.status==Effects.Refused && tx.intent==transaction.intent) |> Maybe.withDefault False)
        -- Separate owning-route positive: attach FULL negotiated capabilities,
        -- then deliver real geometry-facts through Shell.Incoming. The geometry
        -- row, size-policy and wire values are literal independent givens.
        -- The exhaustive matrix above is a typed-input allocator boundary, not
        -- a claim that every incompatible row can pass Geometry.decode.
        policyProjection logical visual configure = E.object
            [("logical",E.list E.float logical),("visual",visual),("real",E.list E.float logical),("configure",E.list E.float configure)]
        literalSizePolicy = E.object
            [("inputs",E.object [("profile",E.string "wayland-zero-origin-v1"),("rawMinimum",E.list E.float [1,1]),("rawMaximum",E.list E.float [0,0]),("layoutMinimum",E.list E.float [1,1]),("layoutMaximum",E.list E.float [10000,10000]),("geometryOrigin",E.list E.float [0,0]),("reservedTopLeft",E.list E.float [0,0]),("reservedBottomRight",E.list E.float [0,0]),("monitorScale",E.float 1)])
            ,("maximize",policyProjection [0,0,800,600] E.null [800,600])
            ,("restoreGeometry",policyProjection [10,20,320,240] (E.list E.float [10,20,320,240]) [320,240])]
        geometryRow operation =
            let mode = if operation=="restore-geometry" then "maximized" else if operation=="exit-fullscreen" then "fullscreen" else "ordinary"
                eligible = mode /= "fullscreen"
            in E.object
                [("incarnation",E.string "1"),("owner",E.null),("workspace",E.string "1"),("workspaceGeneration",E.string "4")
                ,("monitor",E.string "0"),("outputOwnershipGeneration",E.string "2"),("workAreaRevision",E.string "3"),("workArea",E.list E.float [0,0,800,600])
                ,("logicalGeometry",E.list E.float [10,20,320,240]),("visualGeometry",E.list E.float [10,20,320,240])
                ,("nativeMode",E.string mode),("clientMode",E.string mode),("minimized",E.bool False),("floating",E.bool True),("grouped",E.bool False)
                ,("fixedSize",E.bool False),("constrainedSize",E.bool True),("geometryEligible",E.bool eligible),("ordinaryPlacementKnown",E.bool (mode=="maximized"))
                ,("capabilities",E.object [("maximize",E.bool (mode=="ordinary")),("restoreGeometry",E.bool (mode=="maximized"))])
                ,("sizePolicy",literalSizePolicy),("pin",E.object [("pinned",E.bool (operation=="unpin")),("eligible",E.bool (eligible && operation /= "maximize-no-pin"))])]
        observedWire operation seed req = E.object
            [("protocolVersion",E.int 3),("kind",E.string "geometry-facts"),("geometryProtocol",E.int 3),("binding",SnapReplay.bound)
            ,("requestId",req),("sequence",E.string seed),("revision",E.string seed),("outputGeneration",E.string "1")
            ,("facts",E.object [("focused",E.string "1"),("inputBlocked",E.bool False),("windows",E.list identity [geometryRow operation])])]
        -- Input proposals are constructed from the actual decoded observation;
        -- expected operation kind and accepted/refused branch remain literals.
        decodedOperation name observed =
            case name of
                "maximize" -> Just Effects.Maximize
                "restore-geometry" -> Just Effects.RestoreGeometry
                "snap" -> Snap.open observed (SnapReplay.counter "1") |> Maybe.andThen Snap.proposal |> Maybe.map Effects.SnapPlacement
                "transfer-workspace" -> Transfer.propose observed (SnapReplay.counter "1") "2" |> Maybe.map Effects.TransferWorkspace
                "pin" -> Just Effects.Pin
                "unpin" -> Just Effects.Unpin
                "exit-fullscreen" -> Just Effects.ExitFullscreen
                _ -> Nothing
        routeOperation seed name =
            let (negotiated,_) = Shell.update (Shell.Incoming (wire SnapReplay.bound request wireNames)) pending
                expectedFacts = negotiated.geometryExpected |> Maybe.map (UInt64.string >> E.string) |> Maybe.withDefault E.null
                (withFacts, factCommands) = Shell.update (Shell.Incoming (observedWire name seed expectedFacts)) negotiated
            in case (withFacts.geometry,withFacts.geometryCaps) of
                (Just observed,Just caps) ->
                    decodedOperation name observed |> Maybe.map (\operation ->
                        let action = Shell.captureGeometry withFacts |> Maybe.map (\stamp -> Shell.update (Shell.Act stamp operation (SnapReplay.counter "1")) withFacts)
                            sentOperation effect = case effect of
                                Shell.Send value -> D.decodeValue (D.at ["intent","operation"] D.string) value |> Result.toMaybe
                                _ -> Nothing
                            literalAuthority effect = case effect of
                                Shell.Send value ->
                                    D.decodeValue (D.field "protocolVersion" D.int) value == Ok 3
                                    && D.decodeValue (D.field "effectProtocol" D.int) value == Ok 2
                                    && D.decodeValue (D.field "binding" Binding.decoder) value == Ok binding
                                    && D.decodeValue (D.at ["intent","request"] D.string) value == Ok "1"
                                    && D.decodeValue (D.at ["intent","generation"] D.string) value == Ok "1"
                                    && D.decodeValue (D.at ["intent","incarnation"] D.string) value == Ok "1"
                                    && D.decodeValue (D.at ["intent","context","lifetime"] D.string) value == Ok "1"
                                    && D.decodeValue (D.at ["intent","context","epoch"] D.string) value == Ok "1"
                                    && D.decodeValue (D.at ["intent","context","output"] D.string) value == Ok "1"
                                    && D.decodeValue (D.at ["intent","context","revision"] D.string) value == Ok seed
                                _ -> False
                        in negotiated.geometryExpected /= Nothing && withFacts.geometryExpected==Nothing && List.isEmpty factCommands
                            && UInt64.string observed.context.revision==seed && List.length caps.operations==7
                            && (action |> Maybe.map (\(next, emitted) ->
                                (next.effects.transaction |> Maybe.map (\tx -> tx.status==Effects.Pending && tx.intent.operation==operation) |> Maybe.withDefault False)
                                    && List.length emitted == 1 && List.filterMap kind emitted == ["window-effect"]
                                    && List.filterMap sentOperation emitted == [name] && List.all literalAuthority emitted) |> Maybe.withDefault False)
                        ) |> Maybe.withDefault False
                _ -> False
        (fullNegotiated,_) = Shell.update (Shell.Incoming (wire SnapReplay.bound request wireNames)) pending
        (factsWrongId,factsWrongCommands) = Shell.update (Shell.Incoming (observedWire "maximize" "1" (E.string "999"))) fullNegotiated
        (snapOnlyNegotiated,_) = Shell.update (Shell.Incoming (wire SnapReplay.bound request ["snap"])) pending
        snapOnlyRequest = snapOnlyNegotiated.geometryExpected |> Maybe.map (UInt64.string >> E.string) |> Maybe.withDefault E.null
        -- Pin is ineligible here; the only capability mismatch is maximize
        -- advertised by this row when only snap was negotiated.
        (incoherentFacts,incoherentCommands) = Shell.update (Shell.Incoming (observedWire "maximize-no-pin" "1" snapOnlyRequest)) snapOnlyNegotiated
        firstFactsRequest = fullNegotiated.geometryExpected |> Maybe.map (UInt64.string >> E.string) |> Maybe.withDefault E.null
        (firstGeometry,_) = Shell.update (Shell.Incoming (observedWire "maximize" "1" firstFactsRequest)) fullNegotiated
        firstStamp = Shell.captureGeometry firstGeometry
        (refreshGeometry,_) = Shell.update Shell.GeometryRefresh firstGeometry
        refreshRequest = refreshGeometry.geometryExpected |> Maybe.map (UInt64.string >> E.string) |> Maybe.withDefault E.null
        (refreshedGeometry,_) = Shell.update (Shell.Incoming (observedWire "maximize" "2" refreshRequest)) refreshGeometry
        staleStampRefused = firstStamp |> Maybe.map (\oldStamp ->
            let (next,emitted) = Shell.update (Shell.Act oldStamp Effects.Maximize (SnapReplay.counter "1")) refreshedGeometry
            in next.effects==refreshedGeometry.effects && next.issued==refreshedGeometry.issued
                && next.notice=="Window list changed. Choose again." && List.isEmpty emitted
            ) |> Maybe.withDefault False
        malformed =
            [ capability ["snap","snap"] True
            , capability ["SNAP"] True
            , capability ["snap"] False
            , capability [] True
            , capability (wireNames ++ ["unknown-operation"]) True
            , E.object [("observe",E.bool True),("effects",E.bool False),("effectProtocol",E.int 2),("operations",E.list E.string []),("placementCapacity",E.int 256),("canonicalScene",E.bool False),("extra",E.bool True)]
            ]
        reject raw =
            let (next, commands) = Shell.update (Shell.Incoming (attached SnapReplay.bound request raw)) pending
            in next == {pending | decoderRefusal=Just "Native envelope rejected: malformed fields."} && List.isEmpty commands
        wrongRequest = Shell.update (Shell.Incoming (wire SnapReplay.bound (E.string "999") ["snap"])) pending
        wrongBinding = E.object [("lifetime",E.string "1"),("session",E.string "2"),("frontend",E.string "1")]
        foreign = Shell.update (Shell.Incoming (wire wrongBinding request ["snap"])) pending
        (accepted,_) = Shell.update (Shell.Incoming (wire SnapReplay.bound request ["snap"])) pending
        duplicate = Shell.update (Shell.Incoming (wire SnapReplay.bound request ["snap"])) accepted
        detached = Shell.update (Shell.Incoming (E.object [("protocolVersion",E.int 3),("kind",E.string "host-disconnected")])) pending |> Tuple.first
        afterDisconnect = Shell.update (Shell.Incoming (wire SnapReplay.bound request ["snap"])) detached
        checks =
            [ ("negotiationActuallyIssued", pending.geometryAttachExpected /= Nothing && List.filterMap kind startup == ["geometry-attach"])
            , ("all128CapabilitySubsetsFollowActualShellRoute", List.length allSets == 128 && List.all accept allSets)
            , ("seededOrderingPreservesActualRoute", List.length seededSets == 768 && List.all accept seededSets)
            , ("allSubsetsGateSnapAtRealAllocator", List.all snapAllowed allSets)
            , ("allSubsetsGateMaximizeAtRealAllocator", List.all maxAllowed allSets)
            , ("allSevenOperationsRespectAllCapabilitySubsets", List.length sevenOperations==7 && List.all (\item -> List.all (\ops -> allocation ops item) allSets) sevenOperations)
            , ("allSevenOperationsRetainUnknownAndRefuseMismatchedReceipt", List.length sevenOperations==7 && List.all receiptSequence sevenOperations)
            , ("allSevenNegotiatedDecodedFactsReachAllocator", List.all (\seed -> List.all (routeOperation seed) wireNames) ["1","2","19"])
            , ("wrongFactsRequestCannotAdmitGeometry", factsWrongId==fullNegotiated && List.isEmpty factsWrongCommands)
            , ("unnegotiatedGeometryFactRefused", incoherentFacts == {snapOnlyNegotiated | decoderRefusal=Just "Native envelope rejected: malformed fields."} && List.isEmpty incoherentCommands)
            , ("staleDecodedGeometryStampCannotEmitOperation", staleStampRefused)
            , ("malformedCapabilitiesRefusedWithoutGrant", List.all reject malformed)
            , ("mismatchedRequestCannotGrant", Tuple.first wrongRequest == pending && List.isEmpty (Tuple.second wrongRequest))
            , ("foreignBindingCannotGrant", Tuple.first foreign == pending && List.isEmpty (Tuple.second foreign))
            , ("duplicateAttachCannotReissue", Tuple.first duplicate == accepted && List.isEmpty (Tuple.second duplicate))
            , ("lateAttachAfterDisconnectCannotGrant", Tuple.first afterDisconnect == detached && List.isEmpty (Tuple.second afterDisconnect))
            ]
    in E.object [("checks",E.object (List.map (\(name,passed) -> (name,E.bool passed)) checks)),
        ("scope",E.string "Elm Shell capability admission and allocator; trusted typed prelude only; no native or compositor proof.")]

main : Program () () Never
main = Platform.worker
    { init = \() ->
        ((), outgoing (D.decodeValue Binding.decoder SnapReplay.bound |> Result.map resultFor
            |> Result.withDefault (E.object [("checks",E.object [("bindingFixture",E.bool False)])])))
    , update = \_ model -> (model, Cmd.none)
    , subscriptions = \_ -> Sub.none
    }
