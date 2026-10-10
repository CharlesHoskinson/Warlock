port module FullscreenExitReplay exposing (main)

import Desktop
import Binding
import Effects
import GeometryProjection as Geometry
import Json.Decode as D
import Json.Encode as E
import NativeProvider
import Menu
import MenuBridge
import Platform
import Provider
import Shell
import SnapReplay as Fixture
import TaskbarShell
import UInt64

port outgoing : E.Value -> Cmd msg

caps = { effects=True, operations=["maximize","restore-geometry","snap","transfer-workspace","pin","unpin","exit-fullscreen"] }
geometryFor bound =
    let old=Fixture.geometryFor bound
    in {old|windows=List.map (\row -> {row|nativeMode=Geometry.Fullscreen,clientMode=Geometry.Fullscreen,eligible=False,maximize=False,restoreGeometry=False,placementKnown=False,pin=Just {pinned=False,eligible=False}}) old.windows}
effectsFor bound = (Fixture.readyFor bound).windows.shell.effects
start capabilities snapshot effects = Effects.beginGeometry capabilities snapshot Effects.ExitFullscreen (Fixture.counter "1") effects
refused (_,wire,error) = wire==Nothing && error/=Nothing
menuItems bound capabilities snapshot =
    let desktop=Fixture.readyFor bound
        windows=desktop.windows
        shell=windows.shell
        supplied={shell|geometry=Just snapshot,geometryCaps=Just capabilities,geometryExpected=Nothing}
    in NativeProvider.fromShell {outputId=Fixture.counter "1",providerId=Fixture.counter "1",capabilityGeneration=Fixture.counter "1"} (Fixture.counter "1") supplied
        |> Result.map Provider.getItems |> Result.withDefault []

preparedExit bound =
    let desktop=Fixture.readyFor bound
        windows=desktop.windows
        shell=windows.shell
        snapshot=geometryFor bound
        supplied={shell|geometry=Just snapshot,geometryCaps=Just caps,geometryExpected=Nothing}
        ready={desktop|windows={windows|shell=supplied}}
        opened=NativeProvider.fromShell {outputId=Fixture.counter "1",providerId=Fixture.counter "1",capabilityGeneration=Fixture.counter "1"} (Fixture.counter "1") supplied
            |> Result.map (\provider -> Desktop.update (Desktop.Window (TaskbarShell.OpenMenu provider)) ready |> Tuple.first) |> Result.withDefault ready
        selected=(MenuBridge.menuSnapshot opened.windows.menus).menu |> Maybe.map (\menu ->
            let index=List.indexedMap Tuple.pair menu.items |> List.filter (\(_,item) -> item.action==Menu.ExitFullscreen) |> List.head |> Maybe.map Tuple.first |> Maybe.withDefault -1
            in Desktop.update (Desktop.Window (TaskbarShell.MenuEvent (Menu.Activate menu.id menu.binding index))) opened |> Tuple.first) |> Maybe.withDefault opened
        before=selected.windows.shell
        reply kind request=Shell.Incoming (E.object [("kind",E.string kind),("binding",Binding.encode bound),("requestId",E.string (UInt64.string request))])
    in case MenuBridge.preparedSnapshot selected.windows.menus of
        Nothing -> False
        Just slot ->
            let fresh={before|expected=Nothing}
                first=MenuBridge.advancePrepared (reply "action-projection" slot.legacyRequest) before fresh selected.windows.menus
                firstShell=first.shell
                next={firstShell|phase=Shell.Ready,geometryExpected=Nothing,geometry=Just {snapshot|sequence=Fixture.counter "2"}}
                completed=MenuBridge.advancePrepared (reply "geometry-facts" (Maybe.withDefault UInt64.zero slot.geometryRequest)) firstShell next first.bridge
            in List.length completed.effects==1 && MenuBridge.receiptCount completed.bridge==1 &&
                (completed.shell.effects.transaction |> Maybe.map (\t -> t.intent.operation==Effects.ExitFullscreen && t.status==Effects.Pending) |> Maybe.withDefault False)

checksFor bound =
    let observed=geometryFor bound
        ready=effectsFor bound
        (allocated,wire,error)=start caps observed ready
        pending=allocated.transaction |> Maybe.map (\t -> t.intent.operation==Effects.ExitFullscreen && t.effectProtocol==2 && t.status==Effects.Pending) |> Maybe.withDefault False
        receipt status=allocated.transaction |> Maybe.map (\t -> E.object [("kind",E.string "receipt"),("effectProtocol",E.int 2),("intent",Effects.encodeIntent t.intent),("status",E.string status)]) |> Maybe.withDefault E.null
        (unknown,_,_)=Effects.apply (receipt "Unknown") allocated
        (committed,_,_)=Effects.apply (receipt "Committed") allocated
        noExit={caps|operations=List.filter ((/=) "exit-fullscreen") caps.operations}
        mode selected={observed|windows=List.map (\w -> {w|nativeMode=selected,clientMode=selected}) observed.windows}
        blocked={observed|blocked=True}
        parented={observed|windows=List.map (\w -> {w|owner=Just (Fixture.counter "2")}) observed.windows}
        fullItems=menuItems bound caps observed
        allows items=List.any (\item -> item.label=="Exit fullscreen" && item.enabled) items
        capWire=E.object [("observe",E.bool True),("effects",E.bool True),("effectProtocol",E.int 2),("operations",E.list E.string caps.operations),("placementCapacity",E.int 256),("canonicalScene",E.bool False)]
    in E.object (List.map (\(name,passed) -> (name,E.bool passed))
        [ ("sevenOperationsDecode",D.decodeValue Geometry.capabilitiesDecoder capWire==Ok caps)
        , ("fullscreenMenuEnabled",allows fullItems)
        , ("ordinaryHasNoExit",not (allows (menuItems bound caps (mode Geometry.Ordinary))))
        , ("maxHasNoExit",not (allows (menuItems bound caps (mode Geometry.Maximized))))
        , ("unsupportedHasNoExit",not (allows (menuItems bound noExit observed)))
        , ("exactTypedPending",wire/=Nothing && error==Nothing && pending)
        , ("blockedRefuses",refused (start caps blocked ready))
        , ("parentedRefuses",refused (start caps parented ready))
        , ("unsupportedRefuses",refused (start noExit observed ready))
        , ("maxRefuses",refused (start caps (mode Geometry.Maximized) ready))
        , ("unknownNeverReplays",refused (start caps observed unknown) && unknown.request==allocated.request)
        , ("receiptCorrelates",committed.transaction |> Maybe.map (\t -> t.status==Effects.Committed) |> Maybe.withDefault False)
        , ("preparedExitRegistersOnce",preparedExit bound)
        ])
checks = case D.decodeValue Binding.decoder Fixture.bound of
    Ok bound -> checksFor bound
    Err _ -> E.object [("bindingDecode",E.bool False)]
main : Program () () ()
main = Platform.worker {init=\_ -> ((),outgoing (E.object [("checks",checks)])),update=\_ model -> (model,Cmd.none),subscriptions=\_ -> Sub.none}
