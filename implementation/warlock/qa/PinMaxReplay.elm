port module PinMaxReplay exposing (main)

import ActionProjection
import Binding
import Desktop
import Effects
import GeometryProjection as Geometry
import Json.Decode as D
import Json.Encode as E
import Menu
import MenuBridge
import NativeProvider
import Platform
import Provider
import Shell
import SnapReplay
import Surface
import TaskbarShell
import UInt64

port outgoing : E.Value -> Cmd msg

counter = SnapReplay.counter
caps = {effects=True,operations=["maximize","restore-geometry","snap","transfer-workspace","pin","unpin"]}
geometry binding pinned revision =
    let original=SnapReplay.geometryFor binding
        row=List.head original.windows
        context=original.context
    in {original|context={context|revision=counter revision},windows=row |> Maybe.map (\window -> [{window|nativeMode=Geometry.Maximized,clientMode=Geometry.Maximized,maximize=False,restoreGeometry=not pinned,placementKnown=True,eligible=not pinned,pin=Just {pinned=pinned,eligible=True}}]) |> Maybe.withDefault []}
withGeometry observed model =
    let windows=model.windows
        shell=windows.shell
    in {model|windows={windows|shell={shell|geometry=Just observed,geometryCaps=Just caps,geometryExpected=Nothing}}}
openMenu model =
    NativeProvider.fromShell {outputId=counter "1",providerId=counter "1",capabilityGeneration=counter "1"} (counter "1") model.windows.shell
        |> Result.map (\provider -> Desktop.update (Desktop.Window (TaskbarShell.OpenMenu provider)) model |> Tuple.first)
        |> Result.withDefault model
controls model = Surface.controls (openMenu model)
details model = controls model |> List.map .detail |> String.join " "
refused (_,wire,error) = wire==Nothing && error/=Nothing
receipt status allocated =
    allocated.transaction |> Maybe.map (\transaction -> E.object [("kind",E.string "receipt"),("effectProtocol",E.int 2),("intent",Effects.encodeIntent transaction.intent),("status",E.string status)]) |> Maybe.withDefault E.null

-- Execute the shipped prepared-selection bridge and allocator. Read payloads
-- below identify replies; complete scene records are decoded separately. Native
-- transport authentication and geometry decoding are exercised by the native
-- campaign, not inferred from this focused trusted-observation fixture.
preparedResult binding variant =
    let ready=withGeometry (geometry binding False "1") (SnapReplay.readyFor binding)
        windows=ready.windows
        shell=windows.shell
        effects=shell.effects
        legacy id label=E.object [("incarnation",E.string id),("label",E.string label),("owner",E.null),("application",E.string "documents"),("minimized",E.bool False),("available",E.bool True)]
        scene revision rows=ActionProjection.decode (E.object [("revision",E.string revision),("focused",E.string "1"),("windows",E.list identity rows)]) |> Result.toMaybe
        originalScene=scene "1" [legacy "1" "Document",legacy "2" "Peer"]
        changedScene=scene "2" [legacy "2" (if variant=="peer-title" then "Changed peer" else "Peer"),legacy "1" "Document"]
        context=(geometry binding False "1").context
        observed original=original |> Maybe.map (\value -> {context=context,scene=value})
        originalGeometry=geometry binding False "1"
        peer=SnapReplay.geometryFor binding |> .windows |> List.head |> Maybe.map (\row -> {row|incarnation=counter "2",eligible=False,maximize=False,pin=Just {pinned=False,eligible=True}})
        allGeometry={originalGeometry|windows=originalGeometry.windows++Maybe.withDefault [] (Maybe.map List.singleton peer)}
        fixture={ready|windows={windows|shell={shell|effects={effects|observed=observed originalScene},geometry=Just allGeometry}}}
        opened=openMenu fixture
        selected=case (MenuBridge.menuSnapshot opened.windows.menus).menu of
            Nothing -> opened
            Just menu ->
                let index=menu.items |> List.indexedMap Tuple.pair |> List.filter (\(_,item) -> item.action==Menu.AlwaysOnTop True) |> List.head |> Maybe.map Tuple.first |> Maybe.withDefault -1
                in Desktop.update (Desktop.Window (TaskbarShell.MenuEvent (Menu.Activate menu.id menu.binding index))) opened |> Tuple.first
        before=selected.windows.shell
        reply kind request=Shell.Incoming (E.object [("kind",E.string kind),("binding",Binding.encode binding),("requestId",E.string (UInt64.string request))])
    in case MenuBridge.preparedSnapshot selected.windows.menus of
        Nothing -> Nothing
        Just slot ->
            let afterContext={context|revision=counter "2",output=if variant=="output" then counter "2" else context.output}
                afterObserved=changedScene |> Maybe.map (\value -> {context=afterContext,scene=value})
                beforeEffects=before.effects
                firstShell={before|expected=Nothing,effects={beforeEffects|observed=afterObserved}}
                first=MenuBridge.advancePrepared (reply "action-projection" (if variant=="correlation" then counter "999" else slot.legacyRequest)) before firstShell selected.windows.menus
                mutate row=if variant=="peer-geometry" && row.incarnation==counter "2" then {row|logicalGeometry=[0,81,320,240]} else if variant=="target-pin" && row.incarnation==counter "1" then {row|pin=Just {pinned=True,eligible=True}} else row
                nextGeometry={allGeometry|windows=List.reverse allGeometry.windows |> List.map mutate,context=afterContext,sequence=counter "2"}
                firstState=first.shell
                nextShell={firstState|phase=Shell.Ready,geometryExpected=Nothing,geometry=Just nextGeometry}
                completed=slot.geometryRequest |> Maybe.map (\request -> MenuBridge.advancePrepared (reply "geometry-facts" request) first.shell nextShell first.bridge) |> Maybe.withDefault first
            in Just {first=first,result=completed,slot=slot}

preparedIssued value=case value of
    Nothing -> False
    Just value_ ->
        List.length value_.result.effects==1 && (value_.result.shell.effects.transaction |> Maybe.map (\t -> t.intent.operation==Effects.Pin && t.status==Effects.Pending) |> Maybe.withDefault False)

preparedRefused value=case value of
    Nothing -> False
    Just value_ -> List.isEmpty value_.result.effects && MenuBridge.preparedSnapshot value_.result.bridge==Nothing && (value_.result.error/=Nothing || value_.first.error/=Nothing)

preparedReceipts binding status altered =
    preparedResult binding "reorder" |> Maybe.map (\v ->
        let nativeIntent=v.result.shell.effects.transaction |> Maybe.map .intent
            frame original=E.object [("protocolVersion",E.int 3),("kind",E.string "effect-outcome"),("effectProtocol",E.int 2),("binding",Binding.encode binding),("intent",Effects.encodeIntent (if altered then {original|operation=Effects.Unpin} else original)),("status",E.string status),("reason",E.string "applied"),("revision",E.string "2"),("outputGeneration",E.string "1")]
            settled=nativeIntent |> Maybe.map (frame >> E.encode 0 >> (\raw -> MenuBridge.nativeFrame raw v.result.bridge |> Tuple.first)) |> Maybe.withDefault v.result.bridge
        in {registered=MenuBridge.receiptCount v.result.bridge,remaining=MenuBridge.receiptCount settled})
result binding =
    let ready=withGeometry (geometry binding False "1") (SnapReplay.readyFor binding)
        observed=geometry binding False "1"
        (allocated,wire,error)=Effects.beginGeometry caps observed Effects.Pin (counter "1") ready.windows.shell.effects
        (committed,_,_)=Effects.apply (receipt "Committed" allocated) allocated
        (unknown,_,_)=Effects.apply (receipt "Unknown" allocated) allocated
        (rejected,_,_)=Effects.apply (receipt "Refused" allocated) allocated
        pendingWindows=ready.windows
        pendingShell=pendingWindows.shell
        pending={ready|windows={pendingWindows|shell={pendingShell|effects=allocated}}}
        committedRoot={ready|windows={pendingWindows|shell={pendingShell|effects=committed}}}
        confirmed=withGeometry (geometry binding True "2") committedRoot
        pinRow=Geometry.window (counter "1") observed
        missing={observed|windows=pinRow |> Maybe.map (\row -> [{row|pin=Nothing}]) |> Maybe.withDefault []}
        fullscreen={observed|windows=pinRow |> Maybe.map (\row -> [{row|nativeMode=Geometry.Fullscreen,clientMode=Geometry.Fullscreen,pin=Just {pinned=False,eligible=False}}]) |> Maybe.withDefault []}
        unpin=Effects.beginGeometry caps (geometry binding True "2") Effects.Unpin (counter "1") committed
        checks=
            [("PinUsesExistingGeometryAllocator",wire/=Nothing && error==Nothing && (allocated.transaction |> Maybe.map (\t -> t.effectProtocol==2 && t.intent.operation==Effects.Pin && t.status==Effects.Pending) |> Maybe.withDefault False))
            ,("IntentRoundTripsTypedPin",allocated.transaction |> Maybe.map (\t -> D.decodeValue Effects.intentDecoder (Effects.encodeIntent t.intent)==Ok t.intent) |> Maybe.withDefault False)
            ,("PendingNeverShowsOptimisticPin",not (String.contains "Always on top" (details pending)) && String.contains "Maximized" (details pending))
            ,("CommittedReceiptAloneNeverShowsPin",not (String.contains "Always on top" (details committedRoot)))
            ,("CorrelatedObservationShowsPinAndMax",String.contains "Always on top" (details confirmed) && String.contains "Maximized" (details confirmed))
            ,("ConfirmedPinnedMenuOffersUnpin",List.any (\row -> row.label=="Unpin window" && row.enabled) (controls confirmed))
            ,("RefusalPreservesObservedUnpinnedMax",rejected.observed==ready.windows.shell.effects.observed)
            ,("DuplicatePendingNeverReplays",refused (Effects.beginGeometry caps observed Effects.Pin (counter "1") allocated))
            ,("UnknownNeverReplays",refused (Effects.beginGeometry caps observed Effects.Pin (counter "1") unknown))
            ,("LegacyMissingPinNeverGrantsAction",refused (Effects.beginGeometry caps missing Effects.Pin (counter "1") ready.windows.shell.effects))
            ,("FullscreenPinIsRefused",refused (Effects.beginGeometry caps fullscreen Effects.Pin (counter "1") ready.windows.shell.effects))
            ,("UnpinPreservesTypedMaxObservation",not (refused unpin) && ((geometry binding True "2").windows |> List.all (\row -> row.nativeMode==Geometry.Maximized)))
            ,("NoPinWithoutNegotiatedCapability",refused (Effects.beginGeometry {effects=True,operations=["maximize","restore-geometry"]} observed Effects.Pin (counter "1") ready.windows.shell.effects))
            ,("ReorderedCompleteFactsIssuePreparedPin",preparedIssued (preparedResult binding "reorder"))
            ,("PreparedPinWaitsForBothCorrelatedReads",preparedResult binding "reorder" |> Maybe.map (\v -> List.isEmpty v.first.effects && MenuBridge.preparedSnapshot v.first.bridge/=Nothing) |> Maybe.withDefault False)
            ,("ChangedPeerTitleRefusesPreparedPin",preparedRefused (preparedResult binding "peer-title"))
            ,("ChangedPeerGeometryRefusesPreparedPin",preparedRefused (preparedResult binding "peer-geometry"))
            ,("ChangedTargetPinRefusesPreparedPin",preparedRefused (preparedResult binding "target-pin"))
            ,("ChangedOutputRefusesPreparedPin",preparedRefused (preparedResult binding "output"))
            ,("UncorrelatedReadRefusesPreparedPin",preparedRefused (preparedResult binding "correlation"))]
            ++ [("PreparedPinRegistersOneReceiptMapping",preparedReceipts binding "Committed" False |> Maybe.map (\v -> v.registered==1 && v.remaining==0) |> Maybe.withDefault False)
            ,("DifferentPinOperationCannotSettleReservation",preparedReceipts binding "Committed" True |> Maybe.map (\v -> v.registered==1 && v.remaining==1) |> Maybe.withDefault False)
            ,("UnknownPinRetainsReservation",preparedReceipts binding "Unknown" False |> Maybe.map (\v -> v.registered==1 && v.remaining==1) |> Maybe.withDefault False)]
        probe=preparedResult binding "reorder" |> Maybe.map (\v -> E.object [("firstError",v.first.error |> Maybe.map E.string |> Maybe.withDefault E.null),("error",v.result.error |> Maybe.map E.string |> Maybe.withDefault E.null),("effects",E.int (List.length v.result.effects)),("shell",Shell.encode v.result.shell)]) |> Maybe.withDefault E.null
    in E.object [("checks",E.object (List.map (\(name,pass) -> (name,E.bool pass)) checks)),("preparedProbe",probe)]
main : Program () () Never
main = Platform.worker {init=\_ -> ((),outgoing (D.decodeValue Binding.decoder SnapReplay.bound |> Result.map result |> Result.withDefault (E.object [("checks",E.object [("Binding",E.bool False)])]))),update=\_ model -> (model,Cmd.none),subscriptions=\_ -> Sub.none}
