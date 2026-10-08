port module PinMaxReplay exposing (main)

import Binding
import Desktop
import Effects
import GeometryProjection as Geometry
import Json.Decode as D
import Json.Encode as E
import Menu
import NativeProvider
import Platform
import Provider
import Shell
import SnapReplay
import Surface
import TaskbarShell

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
            ,("NoPinWithoutNegotiatedCapability",refused (Effects.beginGeometry {effects=True,operations=["maximize","restore-geometry"]} observed Effects.Pin (counter "1") ready.windows.shell.effects))]
    in E.object [("checks",E.object (List.map (\(name,pass) -> (name,E.bool pass)) checks))]
main : Program () () Never
main = Platform.worker {init=\_ -> ((),outgoing (D.decodeValue Binding.decoder SnapReplay.bound |> Result.map result |> Result.withDefault (E.object [("checks",E.object [("Binding",E.bool False)])]))),update=\_ model -> (model,Cmd.none),subscriptions=\_ -> Sub.none}
