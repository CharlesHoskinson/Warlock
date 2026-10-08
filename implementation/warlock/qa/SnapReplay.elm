port module SnapReplay exposing (main)

import Binding
import Desktop
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
window = {incarnation=counter "1",owner=Nothing,workspace=Just "1",workspaceGeneration=Just (counter "4"),monitor=Just UInt64.zero,outputOwnershipGeneration=Just (counter "2"),workAreaRevision=Just (counter "3"),workArea=Just [-80,30,801,601],logicalGeometry=[0,80,320,240],visualGeometry=[0,80,320,240],nativeMode=Geometry.Ordinary,clientMode=Geometry.Ordinary,minimized=False,floating=True,grouped=False,fixedSize=False,constrainedSize=False,eligible=True,placementKnown=False,maximize=True,restoreGeometry=False,sizePolicy=Nothing}
geometryFor binding = {binding=binding,request=counter "1",sequence=counter "1",context={lifetime=counter "1",epoch=counter "1",output=counter "1",revision=counter "1"},focused=Just (counter "1"),blocked=False,windows=[window]}
native raw model = Desktop.update (Desktop.Incoming raw) model |> Tuple.first
attached = E.object [("protocolVersion",E.int 3),("kind",E.string "attached"),("binding",bound)]
projection = E.object [("protocolVersion",E.int 3),("kind",E.string "action-projection"),("binding",bound),("requestId",E.string "1"),("context",E.object [("lifetime",E.string "1"),("epoch",E.string "1"),("output",E.string "1"),("revision",E.string "1")]),("scene",E.object [("revision",E.string "1"),("focused",E.string "1"),("windows",E.list identity [E.object [("incarnation",E.string "1"),("label",E.string "Document"),("owner",E.null),("application",E.string "documents"),("minimized",E.bool False),("available",E.bool True)]])])]
readyFor binding =
    let model=Desktop.initial |> native attached |> native projection
        windows=model.windows
        shell=windows.shell
    in {model|windows={windows|shell={shell|geometry=Just (geometryFor binding),geometryCaps=Just {effects=True,operations=["maximize","restore-geometry"]}}}}
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
        checks=[("actualDesktopOpensSnap",Surface.mode opened=="snap" && opened.snap/=Nothing),
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
            ("closeRetiresPreview",Surface.mode closed=="closed")]
    in E.object [("checks",E.object (List.map (\(name,passed) -> (name,E.bool passed)) checks)),("frame",Surface.packet (counter "1") (counter "1") opened),
        ("scope",E.string "Actual Desktop/Surface policy with typed geometry fixture; native geometry decoding, placement authority and original isolated recordings remain required.")]

result = case D.decodeValue Binding.decoder bound of
    Ok binding -> resultFor binding
    Err _ -> E.object [("checks",E.object [("fixtureBinding",E.bool False)])]

main : Program () () Never
main = Platform.worker {init=\_ -> ((),outgoing result),update=\_ state -> (state,Cmd.none),subscriptions=\_ -> Sub.none}
