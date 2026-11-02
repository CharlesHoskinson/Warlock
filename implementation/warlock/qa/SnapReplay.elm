port module SnapReplay exposing (main, readyFor, geometryFor, bound, counter)

import Binding
import Desktop
import NativePointerFixture
import Effects
import NativeOutcome
import GeometryProjection as Geometry
import Json.Decode as D
import Json.Encode as E
import Platform
import Shell
import Snap
import Surface
import TaskbarShell
import UInt64

port outgoing : E.Value -> Cmd msg

counter value = D.decodeValue UInt64.decoder (E.string value) |> Result.withDefault UInt64.zero
bound = E.object [("lifetime",E.string "1"),("session",E.string "1"),("frontend",E.string "1")]
window = {incarnation=counter "1",owner=Nothing,workspace=Just "1",workspaceGeneration=Just (counter "4"),monitor=Just UInt64.zero,outputOwnershipGeneration=Just (counter "2"),workAreaRevision=Just (counter "3"),workArea=Just [-80,30,801,601],logicalGeometry=[0,80,320,240],visualGeometry=[0,80,320,240],nativeMode=Geometry.Ordinary,clientMode=Geometry.Ordinary,minimized=False,floating=True,grouped=False,fixedSize=False,constrainedSize=False,eligible=True,pin=Nothing,placementKnown=False,maximize=True,restoreGeometry=False,sizePolicy=Nothing}
geometryFor binding = {binding=binding,request=counter "1",sequence=counter "1",context={lifetime=counter "1",epoch=counter "1",output=counter "1",revision=counter "1"},focused=Just (counter "1"),blocked=False,windows=[window]}
native raw model = NativePointerFixture.incoming raw model |> Tuple.first
attached = E.object [("protocolVersion",E.int 3),("kind",E.string "attached"),("binding",bound)]
projection = E.object [("protocolVersion",E.int 3),("kind",E.string "action-projection"),("binding",bound),("requestId",E.string "1"),("context",E.object [("lifetime",E.string "1"),("epoch",E.string "1"),("output",E.string "1"),("revision",E.string "1")]),("scene",E.object [("revision",E.string "1"),("focused",E.string "1"),("windows",E.list identity [E.object [("incarnation",E.string "1"),("label",E.string "Document"),("owner",E.null),("application",E.string "documents"),("minimized",E.bool False),("available",E.bool True)]])])]
readyFor binding =
    let model=Desktop.initial |> native attached |> native projection
        windows=model.windows
        shell=windows.shell
    in {model|windows={windows|shell={shell|geometry=Just (geometryFor binding),geometryCaps=Just {effects=True,operations=[Geometry.CanMaximize,Geometry.CanRestoreGeometry]}}}}
proposal model = model.snap |> Maybe.andThen Snap.proposal
mutation effect = case effect of
    Desktop.WindowEffect (Shell.Send wire) -> D.decodeValue (D.field "kind" D.string) wire==Ok "window-effect"
    Desktop.Send wire -> D.decodeValue (D.field "kind" D.string) wire==Ok "window-effect"
    _ -> False

resultFor binding =
    let ready=readyFor binding
        geometry=geometryFor binding
        opened=Desktop.capture ready |> Maybe.map (\stamp -> Desktop.update (Desktop.OpenSnap stamp (counter "1")) ready |> Tuple.first) |> Maybe.withDefault ready
        right=Desktop.capture opened |> Maybe.map (\stamp -> Desktop.update (Desktop.SelectSnap stamp Snap.RightHalf) opened) |> Maybe.withDefault (opened,[])
        (invalidated,reads)=Desktop.update Desktop.InvalidateSnap opened
        stale=Desktop.capture ready |> Maybe.map (\stamp -> Desktop.update (Desktop.SelectSnap stamp Snap.BottomRight) opened) |> Maybe.withDefault (opened,[])
        context=geometry.context
        changed={geometry|context={context|output=counter "2"}}
        changedArea={geometry|windows=[{window|workAreaRevision=Just (counter "5")}]}
        invalidGeometry={geometry|windows=[{window|minimized=True}]}
        refreshed={geometry|context={context|revision=counter "2"}}
        grabbed={refreshed|blocked=True,windows=[{window|eligible=False,maximize=False}]}
        ineligible={geometry|windows=[{window|eligible=False}]}
        pending=Desktop.update (Desktop.Window (TaskbarShell.Native Shell.Refresh)) opened |> Tuple.first
        closed=Desktop.capture opened |> Maybe.map (\stamp -> Desktop.update (Desktop.CloseSnap stamp) opened |> Tuple.first) |> Maybe.withDefault opened
        controls=Surface.controls opened
        disabledAction=E.object [("surfaceProtocol",E.int 2),("kind",E.string "surface-action"),("surface",E.string "popup"),("publication",E.string "1"),("lease",E.string "1"),("id",E.string "snap:apply")]
        caps={effects=True,operations=[Geometry.CanMaximize,Geometry.CanRestoreGeometry,Geometry.CanSnap]}
        placement=Snap.open geometry (counter "1") |> Maybe.andThen Snap.proposal
        begun=placement |> Maybe.map (\value -> Effects.beginGeometry caps geometry (Effects.SnapPlacement value) (counter "1") ready.windows.shell.effects) |> Maybe.withDefault (ready.windows.shell.effects,Nothing,Just "No fixture proposal")
        (allocated,wire,error)=begun
        currentIntent=allocated.transaction |> Maybe.map .intent
        roundtrip=currentIntent |> Maybe.map (Effects.encodeIntent >> D.decodeValue Effects.intentDecoder >> Result.mapError D.errorToString) |> Maybe.withDefault (Err "Missing intent")
        duplicate=placement |> Maybe.map (\value -> Effects.beginGeometry caps geometry (Effects.SnapPlacement value) (counter "1") allocated) |> Maybe.withDefault begun
        stalePlacement=placement |> Maybe.map (\value -> Effects.beginGeometry caps changed (Effects.SnapPlacement value) (counter "1") ready.windows.shell.effects) |> Maybe.withDefault begun
        blockedPlacement=placement |> Maybe.map (\value -> Effects.beginGeometry caps grabbed (Effects.SnapPlacement value) (counter "1") ready.windows.shell.effects) |> Maybe.withDefault begun
        negotiatedWindows=ready.windows
        negotiatedShell=negotiatedWindows.shell
        negotiated={ready|windows={negotiatedWindows|shell={negotiatedShell|geometryCaps=Just caps}}}
        chooser=Desktop.capture negotiated |> Maybe.map (\stamp -> Desktop.update (Desktop.OpenSnap stamp (counter "1")) negotiated |> Tuple.first) |> Maybe.withDefault negotiated
        submitted=Desktop.capture chooser |> Maybe.map (\stamp -> Desktop.update (Desktop.ApplySnap stamp) chooser) |> Maybe.withDefault (chooser,[])
        recovered=currentIntent |> Maybe.map (\intent -> Effects.recoverUnknown 2 intent ready.windows.shell.effects |> Result.withDefault ready.windows.shell.effects) |> Maybe.withDefault ready.windows.shell.effects
        issued=placement |> Maybe.andThen (\proposed -> Shell.captureGeometry negotiatedShell |> Maybe.map (\stamp -> Shell.update (Shell.Act stamp (Effects.SnapPlacement proposed) (counter "1")) {negotiatedShell|geometryCaps=Just caps} |> Tuple.first)) |> Maybe.withDefault negotiatedShell
        issuedIntent=issued.effects.transaction |> Maybe.map .intent
        nativeReceipt intent = E.object [("protocolVersion",E.int 3),("kind",E.string "effect-outcome"),("effectProtocol",E.int 2),("binding",bound),("intent",Effects.encodeIntent intent),("status",E.string "Committed"),("reason",E.string "applied"),("revision",E.string "2"),("outputGeneration",E.string "1")]
        settled=issuedIntent |> Maybe.map (nativeReceipt >> Shell.Incoming >> (\message -> Shell.update message issued |> Tuple.first)) |> Maybe.withDefault issued
        altered=issuedIntent |> Maybe.map (\intent -> {intent|operation=Effects.SnapPlacement {region=Snap.RightHalf,geometry=[320.5,30,400.5,601],monitor=UInt64.zero,outputOwnershipGeneration=counter "2",workAreaRevision=counter "3",workspaceGeneration=counter "4",context=geometry.context}})
        rejected=altered |> Maybe.map (nativeReceipt >> Shell.Incoming >> (\message -> Shell.update message issued |> Tuple.first)) |> Maybe.withDefault issued
        -- Literal expectations are independent of Snap.identity and the reducer.
        expectedRegions =
            [ (Snap.LeftHalf,"left-half",[-80,30,400.5,601])
            , (Snap.RightHalf,"right-half",[320.5,30,400.5,601])
            , (Snap.TopLeft,"top-left",[-80,30,400.5,300.5])
            , (Snap.TopRight,"top-right",[320.5,30,400.5,300.5])
            , (Snap.BottomLeft,"bottom-left",[-80,330.5,400.5,300.5])
            , (Snap.BottomRight,"bottom-right",[320.5,330.5,400.5,300.5])
            ]
        literalPlacement regionText rectangle outputGeneration = E.object
            [("region",E.string regionText),("geometry",E.list E.float rectangle)
            ,("monitor",E.string "0"),("outputOwnershipGeneration",E.string outputGeneration)
            ,("workAreaRevision",E.string "3"),("workspaceGeneration",E.string "4")]
        candidateFor selectedRegion = Snap.open geometry (counter "1")
            |> Maybe.andThen (Snap.select geometry selectedRegion)
            |> Maybe.andThen Snap.proposal
        exactRegion (selectedRegion,regionText,rectangle) =
            candidateFor selectedRegion |> Maybe.map (\candidate ->
                let expected=literalPlacement regionText rectangle "2"
                    (next,requestWire,problem)=Effects.beginGeometry caps geometry (Effects.SnapPlacement candidate) (counter "1") ready.windows.shell.effects
                    sent=requestWire |> Maybe.map (\payload ->
                        D.decodeValue (D.at ["intent","placement","region"] D.string) payload==Ok regionText
                        && (D.decodeValue (D.field "intent" Effects.intentDecoder) payload |> Result.map (\intent -> intent.operation==Effects.SnapPlacement candidate) |> Result.withDefault False)) |> Maybe.withDefault False
                in candidate.region==selectedRegion && candidate.geometry==rectangle
                    && Snap.matches geometry (counter "1") candidate
                    && E.encode 0 (Snap.encodeProposal candidate)==E.encode 0 expected
                    && D.decodeValue (Snap.proposalDecoder geometry.context) expected==Ok candidate
                    && problem==Nothing && sent && next.transaction/=Nothing) |> Maybe.withDefault False
        unknownRegion=literalPlacement "middle" [-80,30,400.5,601] "2"
        badRectangle=literalPlacement "left-half" [-80,30,0,601] "2"
        zeroGeneration=literalPlacement "left-half" [-80,30,400.5,601] "0"
        extraPlacement=E.object [("region",E.string "left-half"),("geometry",E.list E.float [-80,30,400.5,601]),("monitor",E.string "0"),("outputOwnershipGeneration",E.string "2"),("workAreaRevision",E.string "3"),("workspaceGeneration",E.string "4"),("extra",E.bool True)]
        refusedPlacement raw = D.decodeValue (Snap.proposalDecoder geometry.context) raw |> Result.toMaybe |> (==) Nothing
        -- Literal geometry and wire identities are authored independently of
        -- Snap.identity/proposal. Selection passes through Desktop.update.
        regionCases =
            [ (Snap.LeftHalf, "left-half", [-80,30,400.5,601])
            , (Snap.RightHalf, "right-half", [320.5,30,400.5,601])
            , (Snap.TopLeft, "top-left", [-80,30,400.5,300.5])
            , (Snap.TopRight, "top-right", [320.5,30,400.5,300.5])
            , (Snap.BottomLeft, "bottom-left", [-80,330.5,400.5,300.5])
            , (Snap.BottomRight, "bottom-right", [320.5,330.5,400.5,300.5])
            ]
        choose region =
            Desktop.capture opened
                |> Maybe.map (\stamp -> Desktop.update (Desktop.SelectSnap stamp region) opened)
        expectedRegion (region, expectedName, expectedGeometry) =
            choose region |> Maybe.map (\(model,effects) ->
                let selected = proposal model
                    encoded = selected |> Maybe.map Snap.encodeProposal
                in List.isEmpty effects
                    && (selected |> Maybe.map .geometry) == Just expectedGeometry
                    && (encoded |> Maybe.andThen (D.decodeValue (D.field "region" D.string) >> Result.toMaybe)) == Just expectedName
                    && (encoded |> Maybe.andThen (D.decodeValue (Snap.proposalDecoder geometry.context) >> Result.toMaybe)) == selected
                    && (selected |> Maybe.map (Snap.matches geometry (counter "1"))) == Just True
                ) |> Maybe.withDefault False
        -- Fixed reproducible seeds exercise positive and negative translations.
        -- Translation preserves shape; its oracle is independent of Snap.
        offsets = List.map (\seed ->
            (toFloat (modBy 419 (seed*37+11)-209),toFloat (modBy 431 (seed*73+19)-215)))
            [0,1,17,91,2026,65535]
        translation (dx,dy) (region,_,expectedGeometry) =
            let shiftedWindow = {window|workArea=Just [-80+dx,30+dy,801,601]}
                shifted = {geometry|windows=[shiftedWindow]}
                translated = Snap.open shifted (counter "1")
                    |> Maybe.andThen (Snap.select shifted region)
                    |> Maybe.andThen Snap.proposal
                expected = case expectedGeometry of
                    [x,y,w,h] -> [x+dx,y+dy,w,h]
                    _ -> []
            in (translated |> Maybe.map .geometry) == Just expected
        maxCounter = counter "18446744073709551615"
        maxWindow = {window|monitor=Just maxCounter,outputOwnershipGeneration=Just maxCounter,workAreaRevision=Just maxCounter,workspaceGeneration=Just maxCounter}
        maxGeometry = {geometry|windows=[maxWindow]}
        maxProposal = Snap.open maxGeometry (counter "1") |> Maybe.andThen Snap.proposal
        maxWire = maxProposal |> Maybe.map Snap.encodeProposal
        maxFields = ["monitor","outputOwnershipGeneration","workAreaRevision","workspaceGeneration"]
        maxFieldsExact = List.all (\field -> (maxWire |> Maybe.andThen (D.decodeValue (D.field field D.string) >> Result.toMaybe)) == Just "18446744073709551615") maxFields
        placementObject fields = E.object fields
        wireFields =
            [("region",E.string "left-half"),("geometry",E.list E.float [-80,30,400.5,601])
            ,("monitor",E.string "0"),("outputOwnershipGeneration",E.string "2")
            ,("workAreaRevision",E.string "3"),("workspaceGeneration",E.string "4")]
        accepted fields = D.decodeValue (Snap.proposalDecoder geometry.context) (placementObject fields) |> Result.toMaybe
        replace key value = List.map (\(field,old) -> if field==key then (field,value) else (field,old)) wireFields
        badFields =
            [ replace "region" (E.string "LEFT-HALF")
            , replace "region" (E.string "left-half ")
            , replace "geometry" (E.list E.float [-80,30,0,601])
            , replace "geometry" (E.list E.float [-80,30,400.5])
            , replace "workAreaRevision" (E.string "0")
            , replace "outputOwnershipGeneration" (E.string "18446744073709551616")
            , replace "workspaceGeneration" (E.string "04")
            , wireFields ++ [("unexpected",E.bool True)]
            , List.filter (Tuple.first >> (/=) "monitor") wireFields
            ]
        foreignBinding = D.decodeValue Binding.decoder
            (E.object [("lifetime",E.string "1"),("session",E.string "2"),("frontend",E.string "1")])
            |> Result.toMaybe
        foreignGeometry = foreignBinding |> Maybe.map (\other -> {geometry|binding=other})
        wrongContext = {geometry|context={context|epoch=counter "2"}}
        wrongMonitor = {geometry|windows=[{window|monitor=Just (counter "1")}]}
        wrongWorkspace = {geometry|windows=[{window|workspaceGeneration=Just (counter "5")}]}
        wrongTarget = counter "2"
        exhausted = {allocated|request=maxCounter}
        exhaustedGeneration = {allocated|generation=maxCounter}
        beginUsing model = placement |> Maybe.map (\p -> Effects.beginGeometry caps geometry (Effects.SnapPlacement p) (counter "1") model)
        recoveredIssued = currentIntent |> Maybe.andThen (\intent -> Effects.recoverUnknown 2 intent allocated |> Result.toMaybe)
        refusedReceipt intent = E.object [("protocolVersion",E.int 3),("kind",E.string "effect-outcome"),("effectProtocol",E.int 2),("binding",bound),("intent",Effects.encodeIntent intent),("status",E.string "Refused"),("reason",E.string "refused"),("revision",E.string "2"),("outputGeneration",E.string "1")]
        refusal = issuedIntent |> Maybe.map (refusedReceipt >> Shell.Incoming >> (\message -> Shell.update message issued |> Tuple.first))
        regionChecks =
            [ ("allSixDesktopSelectionsHaveLiteralGeometryWireAndRoundTrip",List.all expectedRegion regionCases)
            , ("seededTranslationKeepsSixGeometryRelations",List.all (\offset -> List.all (translation offset) regionCases) offsets)
            , ("fullWidthCountersRoundTripExactly",maxFieldsExact && (maxWire |> Maybe.andThen (D.decodeValue (Snap.proposalDecoder maxGeometry.context) >> Result.toMaybe)) == maxProposal)
            , ("malformedPlacementFieldsRefused",accepted wireFields /= Nothing && List.all (accepted >> (==) Nothing) badFields)
            , ("changedBindingInvalidatesRetainedChooser",case (foreignGeometry,opened.snap) of
                (Just changedBinding,Just originalChoice) -> not (Snap.valid changedBinding originalChoice)
                _ -> False)
            , ("epochMonitorWorkspaceAndTargetChangesInvalidateExactProposal",placement |> Maybe.map (\p -> not (Snap.matches wrongContext (counter "1") p) && not (Snap.matches wrongMonitor (counter "1") p) && not (Snap.matches wrongWorkspace (counter "1") p) && not (Snap.matches geometry wrongTarget p)) |> Maybe.withDefault False)
            , ("allocatorRejectsMaxRequestWithoutMutation",case beginUsing exhausted of
                Just (next,sent,err) -> next==exhausted && sent==Nothing && err==Just "Missing geometry target or exhausted identity"
                Nothing -> False)
            , ("allocatorRejectsMaxGenerationWithoutMutation",case beginUsing exhaustedGeneration of
                Just (next,sent,err) -> next==exhaustedGeneration && sent==Nothing && err==Just "Missing geometry target or exhausted identity"
                Nothing -> False)
            , ("recoveredUnknownBlocksExactSnapReplay",case recoveredIssued of
                Just model ->
                    case beginUsing model of
                        Just (next,sent,err) -> next==model && sent==Nothing && err==Just "Unresolved or disconnected native operation"
                        Nothing -> False
                Nothing -> False)
            , ("exactRefusalIsTerminalWithoutClaimingPlacement",refusal |> Maybe.map (\model -> model.effects.transaction |> Maybe.map (\tx -> tx.status==Effects.Refused && Just tx.intent==issuedIntent) |> Maybe.withDefault False) |> Maybe.withDefault False)
            ]
        baseChecks=[("sixRegionsExactGeometryWireAndProductionIntent",List.all exactRegion expectedRegions),
            ("unsupportedRegionRefused",refusedPlacement unknownRegion),
            ("invalidRectangleRefused",refusedPlacement badRectangle),
            ("zeroAuthorityGenerationRefused",refusedPlacement zeroGeneration),
            ("extraPlacementFieldRefused",refusedPlacement extraPlacement),
            ("actualDesktopOpensSnap",Surface.mode opened=="snap" && opened.snap/=Nothing),
            ("leftHalfUsesNativeWorkArea",(proposal opened |> Maybe.map .geometry)==Just [-80,30,400.5,601]),
            ("rightHalfCompletesOddWidth",(proposal (Tuple.first right) |> Maybe.map .geometry)==Just [320.5,30,400.5,601]),
            ("selectionHasNoNativeEffects",List.isEmpty (Tuple.second right)),
            ("staleViewCannotChangeRegion",Tuple.first stale==opened && List.isEmpty (Tuple.second stale)),
            ("changedOutputInvalidatesPreview",opened.snap |> Maybe.map (Snap.valid changed >> not) |> Maybe.withDefault False),
            ("changedWorkAreaInvalidatesPreview",opened.snap |> Maybe.map (Snap.valid changedArea >> not) |> Maybe.withDefault False),
            ("sameScopeRevisionCanRefreshPreview",opened.snap |> Maybe.map (Snap.valid refreshed) |> Maybe.withDefault False),
            ("grabRetainsOnlyExistingUnchangedPreview",opened.snap |> Maybe.map (Snap.valid grabbed) |> Maybe.withDefault False),
            ("grabCannotAdmitNewChooser",Snap.open grabbed (counter "1")==Nothing),
            ("unblockedIneligibleTargetRetiresPreview",opened.snap |> Maybe.map (Snap.valid ineligible >> not) |> Maybe.withDefault False),
            ("readonlyRefreshRetainsPreview",Surface.mode pending=="snap" && pending.snap/=Nothing),
            ("refreshPendingDisablesRegionInput",List.length (List.filter .enabled (Surface.controls pending))==1),
            ("minimizedTargetHasNoChooser",Snap.open invalidGeometry (counter "1")==Nothing),
            ("allSixRegionsAndCloseReachable",List.length (List.filter .enabled controls)==7),
            ("nativePlacementExplicitlyUnavailable",List.any (\control -> control.id=="snap:apply" && not control.enabled && control.message==Nothing) controls),
            ("disabledApplyCannotResolve",Surface.resolve (counter "1") (counter "1") disabledAction opened==Nothing),
            ("outputReflowRetiresChoiceAndOnlyReads",invalidated.snap==Nothing && not (List.any mutation reads)),
            ("snapUsesSharedAllocator",error==Nothing && wire/=Nothing && allocated.request==counter "1" && allocated.generation==counter "1"),
            ("placementIntentRoundTripsStrictly",roundtrip==(currentIntent |> Maybe.map Ok |> Maybe.withDefault (Err "Missing intent"))),
            ("pendingSnapCannotAllocateAgain",duplicate==(allocated,Nothing,Just "Unresolved or disconnected native operation")),
            ("staleOutputCannotSubmitPlacement",case stalePlacement of (_,sent,_) -> sent==Nothing),
            ("grabCannotSubmitPlacement",case blockedPlacement of (_,sent,_) -> sent==Nothing),
            ("negotiatedSnapExposesApply",List.any (\control -> control.id=="snap:apply" && control.enabled && control.message/=Nothing) (Surface.controls chooser)),
            ("applyClosesChooserAndReadsBeforeMutation",Surface.mode (Tuple.first submitted)=="closed" && (Tuple.first submitted).choice/=Nothing && not (List.any mutation (Tuple.second submitted))),
            ("unknownRecoveryRetainsPlacementAndBlocksReplay",recovered.transaction |> Maybe.map (\transaction -> transaction.status==Effects.Unknown && Just transaction.intent==currentIntent && Effects.blocked geometry.context.lifetime (counter "1") recovered) |> Maybe.withDefault False),
            ("sharedOutcomeGateAcceptsExactSnapShape",issuedIntent |> Maybe.map (nativeReceipt >> NativeOutcome.valid) |> Maybe.withDefault False),
            ("shellCorrelatesSnapCommittedReceipt",settled.effects.transaction |> Maybe.map (\transaction -> transaction.status==Effects.Committed) |> Maybe.withDefault False),
            ("sameIdsDifferentPlacementCannotSettle",rejected==issued),
            ("closeRetiresPreview",Surface.mode closed=="closed")]
        checks=baseChecks ++ regionChecks
    in E.object [("checks",E.object (List.map (\(name,passed) -> (name,E.bool passed)) checks)),("frame",Surface.packet (counter "1") (counter "1") opened),
        ("scope",E.string "Actual Desktop/Surface policy with typed geometry fixture; native geometry decoding, placement authority and original isolated recordings remain required.")]

result = case D.decodeValue Binding.decoder bound of
    Ok binding -> resultFor binding
    Err _ -> E.object [("checks",E.object [("fixtureBinding",E.bool False)])]

main : Program () () Never
main = Platform.worker {init=\_ -> ((),outgoing result),update=\_ state -> (state,Cmd.none),subscriptions=\_ -> Sub.none}
