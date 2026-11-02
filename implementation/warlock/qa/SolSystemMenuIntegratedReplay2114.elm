port module SolSystemMenuIntegratedReplay2114 exposing (main)

{-| Unexecuted QA source. Root stages this file under the matching module name.
Included with sol-system-menu-integrated-2114.patch. The source incorporates
the frozen capability and pending-phase proposals plus one required legacy QA
record-shape fix. No production constructor is unwrapped.

Expected domain records and wire payloads below are independently authored.
The Desktop prelude is a named GIVEN; tests preserve every other field of that
complete GIVEN and compare the complete Desktop.Model and ordered effects.
NativePointerFixture is synthetic arrangement, never authenticated native input.
No fixture output was captured to manufacture an oracle. No original acceptance.
-}

import Desktop
import Json.Decode as D
import Json.Encode as E
import NativePointerFixture
import Platform
import SystemMenu
import UInt64


port outgoing : E.Value -> Cmd msg


counter : String -> UInt64.Counter
counter text =
    D.decodeValue UInt64.decoder (E.string text)
        |> Result.withDefault UInt64.zero


currentNotice : String
currentNotice =
    "Current system state. Unavailable controls cannot be changed."


waitingNotice : String
waitingNotice =
    "Volume: waiting for native result…"


unknownNotice : String
unknownNotice =
    "Volume: not confirmed. Refresh only reads state; the request will not be repeated."


refusedNotice : String
refusedNotice =
    "Volume: refused or no longer available. Refresh before choosing again."


readNotice : String
readNotice =
    "System state refreshed. The previous request will not be repeated."


snapshot : String -> String -> Int -> SystemMenu.Snapshot
snapshot service revision percent =
    { service = counter service
    , revision = counter revision
    , volume = Just { percent = percent, muted = False, label = "Independent volume fixture" }
    , network = Nothing
    , power = Nothing
    , session = Nothing
    }


intent : String -> Int -> SystemMenu.Intent
intent revision percent =
    { service = counter "9"
    , revision = counter revision
    , operation = SystemMenu.Volume
    , value = percent
    }


observed : SystemMenu.Model
observed =
    { snapshot = Just (snapshot "9" "1" 100)
    , pending = Nothing
    , spent = []
    , notice = currentNotice
    }


reserved : UInt64.Counter -> Int -> SystemMenu.ReceiptPhase -> String -> SystemMenu.Model
reserved request percent receipt notice =
    { snapshot = Just (snapshot "9" "1" 100)
    , pending = Just { request = request, intent = intent "1" percent, receipt = receipt }
    , spent = [ intent "1" percent ]
    , notice = notice
    }


settled : String -> Int -> Int -> String -> SystemMenu.Model
settled revision observedPercent requestedPercent notice =
    { snapshot = Just (snapshot "9" revision observedPercent)
    , pending = Nothing
    , spent = [ intent "1" requestedPercent ]
    , notice = notice
    }


intentWire : String -> Int -> E.Value
intentWire revision percent =
    E.object
        [ ( "service", E.string "9" )
        , ( "revision", E.string revision )
        , ( "operation", E.string "volume-set" )
        , ( "value", E.int percent )
        ]


sameProposal : ( SystemMenu.Model, Maybe E.Value ) -> SystemMenu.Model -> Maybe E.Value -> Bool
sameProposal ( actualModel, actualWire ) expectedModel expectedWire =
    actualModel == expectedModel
        && Maybe.map (E.encode 0) actualWire == Maybe.map (E.encode 0) expectedWire


domainCases : Int -> List ( String, Bool )
domainCases seed =
    let
        percent =
            if modBy 2 seed == 0 then
                25

            else
                75

        requestText =
            if seed == 31 then
                "18446744073709551615"

            else
                String.fromInt (101 + seed)

        request =
            counter requestText

        expectedPending =
            reserved request percent SystemMenu.AwaitingReceipt waitingNotice

        expectedUnknown =
            reserved request percent SystemMenu.UnconfirmedReceipt unknownNotice

        actualGiven =
            SystemMenu.observe (snapshot "9" "1" 100) SystemMenu.initial

        proposal =
            SystemMenu.propose request (intent "1" percent) actualGiven

        pending =
            Tuple.first proposal

        unknown =
            SystemMenu.receive request "Unknown" (snapshot "9" "1" 100) pending

        newerWhilePending =
            { snapshot = Just (snapshot "9" "2" percent)
            , pending = Just { request = request, intent = intent "1" percent, receipt = SystemMenu.UnconfirmedReceipt }
            , spent = [ intent "1" percent ]
            , notice = unknownNotice
            }

        refreshed =
            SystemMenu.reconcile (snapshot "9" "2" percent) unknown

        nextRequest =
            counter (String.fromInt (7001 + seed))

        expectedNext =
            { snapshot = Just (snapshot "9" "2" percent)
            , pending = Just { request = nextRequest, intent = intent "2" 50, receipt = SystemMenu.AwaitingReceipt }
            , spent = [ intent "2" 50, intent "1" percent ]
            , notice = waitingNotice
            }

        named suffix pass =
            ( "seed-" ++ String.fromInt seed ++ "/" ++ suffix, pass )
    in
    [ named "given-complete-domain" (actualGiven == observed)
    , named "positive-proposal-complete-domain-and-wire" (sameProposal proposal expectedPending (Just (intentWire "1" percent)))
    , named "pending-duplicate-no-effect" (sameProposal (SystemMenu.propose request (intent "1" percent) pending) expectedPending Nothing)
    , named "unknown-retains-complete-reservation" (unknown == expectedUnknown)
    , named "unknown-duplicate-stable" (SystemMenu.receive request "Unknown" (snapshot "9" "1" 100) unknown == expectedUnknown)
    , named "unknown-cannot-repeat" (sameProposal (SystemMenu.propose nextRequest (intent "1" percent) unknown) expectedUnknown Nothing)
    , named "foreign-request-preserves-complete-state" (SystemMenu.receive (counter "7") "Committed" (snapshot "9" "2" percent) unknown == expectedUnknown)
    , named "foreign-service-preserves-complete-state" (SystemMenu.receive request "Committed" (snapshot "10" "2" percent) unknown == expectedUnknown)
    , named "invalid-status-preserves-complete-state" (List.all (\status -> SystemMenu.receive request status (snapshot "9" "2" percent) unknown == expectedUnknown) [ "Saved", "", "unknown", "Committed " ])
    , named "late-committed-settles" (SystemMenu.receive request "Committed" (snapshot "9" "2" percent) unknown == settled "2" percent percent "Volume: change observed.")
    , named "late-submitted-settles-without-invented-observation" (SystemMenu.receive request "Submitted" (snapshot "9" "1" 100) unknown == settled "1" 100 percent "Volume: request accepted by the native service.")
    , named "late-refused-retains-spent-intent" (SystemMenu.receive request "Refused" (snapshot "9" "1" 100) unknown == settled "1" 100 percent refusedNotice)
    , named "same-revision-read-keeps-unconfirmed" (SystemMenu.reconcile (snapshot "9" "1" 100) unknown == expectedUnknown)
    , named "observation-preserves-typed-reservation" (SystemMenu.observe (snapshot "9" "2" percent) unknown == newerWhilePending)
    , named "older-outcome-after-new-observation-is-stale" (SystemMenu.receive request "Unknown" (snapshot "9" "1" 100) newerWhilePending == newerWhilePending)
    , named "newer-read-settles-without-replay" (refreshed == settled "2" percent percent readNotice)
    , named "old-intent-cannot-be-replayed-after-read" (sameProposal (SystemMenu.propose nextRequest (intent "1" percent) refreshed) (settled "2" percent percent readNotice) Nothing)
    , named "fresh-explicit-intent-can-follow-new-observation" (sameProposal (SystemMenu.propose nextRequest (intent "2" 50) refreshed) expectedNext (Just (intentWire "2" 50)))
    , named "full-width-request-preserved" (UInt64.string request == requestText)
    ]


bound : E.Value
bound =
    E.object [ ( "lifetime", E.string "1" ), ( "session", E.string "1" ), ( "frontend", E.string "1" ) ]


snapshotWire : String -> String -> Int -> E.Value
snapshotWire service revision percent =
    E.object
        [ ( "service", E.string service )
        , ( "revision", E.string revision )
        , ( "volume", E.object [ ( "percent", E.int percent ), ( "muted", E.bool False ), ( "label", E.string "Independent volume fixture" ) ] )
        , ( "network", E.null )
        , ( "power", E.null )
        , ( "session", E.null )
        ]


loaded : String -> String -> Int -> E.Value
loaded request revision percent =
    E.object [ ( "protocolVersion", E.int 3 ), ( "kind", E.string "system-menu-snapshot" ), ( "binding", bound ), ( "requestId", E.string request ), ( "snapshot", snapshotWire "9" revision percent ) ]


outcome : E.Value -> String -> E.Value -> String -> Int -> E.Value
outcome binding request status service percent =
    E.object [ ( "protocolVersion", E.int 3 ), ( "kind", E.string "system-menu-outcome" ), ( "binding", binding ), ( "requestId", E.string request ), ( "status", status ), ( "snapshot", snapshotWire service "1" percent ) ]


dispatch build model =
    Desktop.capture model
        |> Maybe.map (\stamp -> Desktop.update (build stamp) model)
        |> Maybe.withDefault ( model, [] )


desktopCases : List ( String, Bool )
desktopCases =
    let
        -- Named GIVEN prelude: attached -> explicit synthetic idle -> open ->
        -- matching read -> volume request. No tested outcome comes from this.
        attached =
            E.object [ ( "protocolVersion", E.int 3 ), ( "kind", E.string "attached" ), ( "binding", bound ) ]

        ready =
            NativePointerFixture.incoming attached Desktop.initial |> Tuple.first

        opened =
            dispatch Desktop.OpenSystemMenu ready |> Tuple.first

        read =
            Desktop.update (Desktop.Incoming (loaded "5" "1" 100)) opened |> Tuple.first

        ( pending, proposalEffects ) =
            dispatch (\stamp -> Desktop.SystemChange stamp (intent "1" 25)) read

        pendingDomain =
            reserved (counter "6") 25 SystemMenu.AwaitingReceipt waitingNotice

        unknownDomain =
            reserved (counter "6") 25 SystemMenu.UnconfirmedReceipt unknownNotice

        expectedUnknown =
            { pending | systemMenu = unknownDomain, presentation = Just (counter "6") }

        ( unknown, unknownEffects ) =
            Desktop.update (Desktop.Incoming (outcome bound "6" (E.string "Unknown") "9" 100)) pending

        ( refreshing, refreshEffects ) =
            dispatch Desktop.RefreshSystemMenu unknown

        expectedRefreshing =
            { pending | systemMenu = unknownDomain, presentation = Just (counter "7"), request = counter "7", systemMenuExpected = Just (counter "7") }

        expectedRefreshed =
            { pending | systemMenu = settled "2" 25 25 readNotice, presentation = Just (counter "8"), request = counter "7", systemMenuExpected = Nothing }

        effectWire =
            E.object [ ( "protocolVersion", E.int 3 ), ( "kind", E.string "system-menu-effect" ), ( "binding", bound ), ( "requestId", E.string "6" ), ( "intent", intentWire "1" 25 ) ]

        readWire =
            E.object [ ( "protocolVersion", E.int 3 ), ( "kind", E.string "system-menu-request" ), ( "binding", bound ), ( "requestId", E.string "7" ) ]

        foreignBinding =
            E.object [ ( "lifetime", E.string "1" ), ( "session", E.string "1" ), ( "frontend", E.string "2" ) ]

        check suffix pass =
            ( "desktop/" ++ suffix, pass )

        refusedExpected =
            { pending | systemMenu = settled "1" 100 25 refusedNotice, presentation = Just (counter "7") }

        submittedExpected =
            { pending | systemMenu = settled "1" 100 25 "Volume: request accepted by the native service.", presentation = Just (counter "7") }
    in
    [ check "given-counter-and-complete-child-pinned" (opened.systemMenuExpected == Just (counter "5") && pending.request == counter "6" && pending.presentation == Just (counter "5") && pending.systemMenu == pendingDomain)
    , check "given-proposal-full-ordered-effect" (proposalEffects == [ Desktop.Send effectWire ])
    , check "unknown-full-model-and-every-effect" (( unknown, unknownEffects ) == ( expectedUnknown, [] ))
    , check "duplicate-unknown-full-model-no-effect" (Desktop.update (Desktop.Incoming (outcome bound "6" (E.string "Unknown") "9" 100)) unknown == ( expectedUnknown, [] ))
    , check "unknown-no-replay-full-model" (dispatch (\stamp -> Desktop.SystemChange stamp (intent "1" 25)) unknown == ( expectedUnknown, [] ))
    , check "late-refused-full-model-and-every-effect" (Desktop.update (Desktop.Incoming (outcome bound "6" (E.string "Refused") "9" 100)) unknown == ( refusedExpected, [] ))
    , check "late-submitted-full-model-and-every-effect" (Desktop.update (Desktop.Incoming (outcome bound "6" (E.string "Submitted") "9" 100)) unknown == ( submittedExpected, [] ))
    , check "wrong-request-preserves-full-model" (Desktop.update (Desktop.Incoming (outcome bound "999" (E.string "Committed") "9" 25)) pending == ( pending, [] ))
    , check "foreign-binding-preserves-full-model" (Desktop.update (Desktop.Incoming (outcome foreignBinding "6" (E.string "Unknown") "9" 100)) pending == ( pending, [] ))
    , check "foreign-service-preserves-full-model" (Desktop.update (Desktop.Incoming (outcome bound "6" (E.string "Unknown") "10" 100)) pending == ( pending, [] ))
    , check "malformed-status-preserves-full-model" (Desktop.update (Desktop.Incoming (outcome bound "6" (E.string "Saved") "9" 100)) pending == ( pending, [] ))
    , check "null-status-preserves-full-model" (Desktop.update (Desktop.Incoming (outcome bound "6" E.null "9" 100)) pending == ( pending, [] ))
    , check "refresh-full-model-and-exact-read-effect" (( refreshing, refreshEffects ) == ( expectedRefreshing, [ Desktop.Send readWire ] ))
    , check "matching-newer-read-full-model-no-replay" (Desktop.update (Desktop.Incoming (loaded "7" "2" 25)) refreshing == ( expectedRefreshed, [] ))
    ]


capabilityWire : Maybe String -> Maybe String -> E.Value
capabilityWire permission power =
    E.object
        [ ( "service", E.string "9" )
        , ( "revision", E.string "1" )
        , ( "volume", E.null )
        , ( "network", permission |> Maybe.map (\value -> E.object [ ( "enabled", E.bool True ), ( "state", E.string "activated" ), ( "permission", E.string value ) ]) |> Maybe.withDefault E.null )
        , ( "power", power |> Maybe.map (\value -> E.object [ ( "suspend", E.string value ), ( "reboot", E.string value ), ( "poweroff", E.string value ) ]) |> Maybe.withDefault E.null )
        , ( "session", E.null )
        ]


capabilitySnapshot : Maybe SystemMenu.NetworkPermission -> Maybe SystemMenu.PowerCapability -> SystemMenu.Snapshot
capabilitySnapshot permission power =
    { service = counter "9"
    , revision = counter "1"
    , volume = Nothing
    , network = Maybe.map (\value -> { enabled = True, state = "activated", permission = value }) permission
    , power = Maybe.map (\value -> { suspend = value, reboot = value, poweroff = value }) power
    , session = Nothing
    }


capabilityCase wire expectedSnapshot operation operationCode operationLabel allowed =
    case D.decodeValue SystemMenu.decoder wire of
        Err _ ->
            False

        Ok decoded ->
            let
                -- Literal snapshot, complete model, intent and complete wire;
                -- no expected value calls supported/propose/encode under test.
                given =
                    { snapshot = Just expectedSnapshot, pending = Nothing, spent = [], notice = currentNotice }

                target =
                    { service = counter "9", revision = counter "1", operation = operation, value = 0 }

                expectedAfter =
                    if allowed then
                        { snapshot = Just expectedSnapshot
                        , pending = Just { request = counter "777", intent = target, receipt = SystemMenu.AwaitingReceipt }
                        , spent = [ target ]
                        , notice = operationLabel ++ ": waiting for native result…"
                        }

                    else
                        given

                expectedWire =
                    if allowed then
                        Just (E.object [ ( "service", E.string "9" ), ( "revision", E.string "1" ), ( "operation", E.string operationCode ), ( "value", E.int 0 ) ])

                    else
                        Nothing

                actualGiven =
                    SystemMenu.observe decoded SystemMenu.initial
            in
            decoded == expectedSnapshot
                && actualGiven == given
                && sameProposal (SystemMenu.propose (counter "777") target actualGiven) expectedAfter expectedWire


capabilityCases : List ( String, Bool )
capabilityCases =
    let
        networks =
            [ ( "yes", SystemMenu.NetworkYes, True )
            , ( "no", SystemMenu.NetworkNo, False )
            , ( "auth", SystemMenu.NetworkAuth, True )
            ]

        powers =
            [ ( "yes", SystemMenu.PowerYes, True )
            , ( "no", SystemMenu.PowerNo, False )
            , ( "na", SystemMenu.PowerUnavailable, False )
            , ( "challenge", SystemMenu.PowerChallenge, True )
            ]

        operations =
            [ ( SystemMenu.Suspend, "suspend", "Suspend" )
            , ( SystemMenu.Reboot, "reboot", "Restart" )
            , ( SystemMenu.PowerOff, "poweroff", "Shut down" )
            ]

        rejected wire =
            case D.decodeValue SystemMenu.decoder wire of
                Err _ -> True
                Ok _ -> False
    in
    List.map (\(raw, value, allowed) ->
        ( "capability/network-" ++ raw ++ "-complete-model-wire"
        , capabilityCase (capabilityWire (Just raw) Nothing) (capabilitySnapshot (Just value) Nothing) SystemMenu.Network "network-enable" "Network" allowed
        )) networks
        ++ List.concatMap (\(raw, value, allowed) ->
            List.map (\(operation, code, label) ->
                ( "capability/power-" ++ code ++ "-" ++ raw ++ "-complete-model-wire"
                , capabilityCase (capabilityWire Nothing (Just raw)) (capabilitySnapshot Nothing (Just value)) operation code label allowed
                )) operations
            ) powers
        ++ [ ( "capability/network-cross-domain-rejected", rejected (capabilityWire (Just "challenge") Nothing) )
           , ( "capability/power-cross-domain-rejected", rejected (capabilityWire Nothing (Just "auth")) )
           ]


sessionWire : E.Value -> E.Value
sessionWire rawState =
    E.object
        [ ( "service", E.string "9" ), ( "revision", E.string "1" )
        , ( "volume", E.null ), ( "network", E.null ), ( "power", E.null )
        , ( "session", E.object [ ( "name", E.string "Independent native session" ), ( "state", rawState ), ( "locked", E.bool False ) ] )
        ]


sessionCase : String -> SystemMenu.SessionState -> Bool -> Bool
sessionCase rawState expectedState allowed =
    case D.decodeValue SystemMenu.decoder (sessionWire (E.string rawState)) of
        Err _ ->
            False

        Ok actual ->
            let
                expectedSnapshot =
                    { service = counter "9", revision = counter "1", volume = Nothing, network = Nothing, power = Nothing
                    , session = Just { name = "Independent native session", state = expectedState, locked = False }
                    }

                given =
                    { snapshot = Just expectedSnapshot, pending = Nothing, spent = [], notice = currentNotice }

                target =
                    { service = counter "9", revision = counter "1", operation = SystemMenu.Logout, value = 0 }

                expectedAfter =
                    if allowed then
                        { snapshot = Just expectedSnapshot
                        , pending = Just { request = counter "777", intent = target, receipt = SystemMenu.AwaitingReceipt }
                        , spent = [ target ]
                        , notice = "Log out: waiting for native result…"
                        }
                    else
                        given

                expectedWire =
                    if allowed then
                        Just (E.object [ ( "service", E.string "9" ), ( "revision", E.string "1" ), ( "operation", E.string "session-logout" ), ( "value", E.int 0 ) ])
                    else
                        Nothing

                actualGiven =
                    SystemMenu.observe actual SystemMenu.initial
            in
            actual == expectedSnapshot
                && actualGiven == given
                && SystemMenu.sessionStateName expectedState == rawState
                && SystemMenu.supported target actualGiven == allowed
                && sameProposal (SystemMenu.propose (counter "777") target actualGiven) expectedAfter expectedWire


sessionCases : List ( String, Bool )
sessionCases =
    let
        rejected rawState =
            case D.decodeValue SystemMenu.decoder (sessionWire rawState) of
                Err _ -> True
                Ok _ -> False
    in
    [ ( "session/closing-complete-model-no-wire", sessionCase "closing" SystemMenu.SessionClosing False )
    , ( "session/active-complete-model-and-wire", sessionCase "active" (SystemMenu.OtherSessionState "active") True )
    , ( "session/online-complete-model-and-wire", sessionCase "online" (SystemMenu.OtherSessionState "online") True )
    , ( "session/open-text-complete-model-and-wire", sessionCase "native:observed" (SystemMenu.OtherSessionState "native:observed") True )
    , ( "session/empty-complete-model-and-wire", sessionCase "" (SystemMenu.OtherSessionState "") True )
    , ( "session/case-sensitive-complete-model-and-wire", sessionCase "Closing" (SystemMenu.OtherSessionState "Closing") True )
    , ( "session/near-closing-complete-model-and-wire", sessionCase "closing " (SystemMenu.OtherSessionState "closing ") True )
    , ( "session/maximum-text-complete-model-and-wire", sessionCase "ssssssssssssssssssssssssssssssss" (SystemMenu.OtherSessionState "ssssssssssssssssssssssssssssssss") True )
    , ( "session/overlong-text-rejected", rejected (E.string "sssssssssssssssssssssssssssssssss") )
    , ( "session/control-text-rejected", rejected (E.string "active\n") )
    , ( "session/non-string-rejected", List.all rejected [ E.int 0, E.null, E.bool True ] )
    ]


result : E.Value
result =
    let
        cases =
            List.concatMap domainCases (List.range 0 31) ++ desktopCases ++ capabilityCases ++ sessionCases
    in
    E.object
        [ ( "schema", E.int 1 )
        , ( "scope", E.string "Full SystemMenu domain models/wire; complete Desktop GIVEN-relative models and every ordered effect; synthetic native arrangement only" )
        , ( "seeds", E.list E.int (List.range 0 31) )
        , ( "checks", E.object (List.map (\( name, pass ) -> ( name, E.bool pass )) cases) )
        , ( "checkCount", E.int (List.length cases) )
        , ( "requiredCheckCount", E.int 650 )
        , ( "originalAccepted", E.bool False )
        , ( "nativeAccepted", E.bool False )
        ]


main =
    Platform.worker
        { init = \() -> ( (), outgoing result )
        , update = \_ model -> ( model, Cmd.none )
        , subscriptions = \_ -> Sub.none
        }
