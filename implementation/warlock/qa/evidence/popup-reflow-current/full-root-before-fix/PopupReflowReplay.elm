port module PopupReflowReplay exposing (main)

import Desktop
import Binding
import Motion
import OutputController as Outputs
import Json.Decode as D
import Json.Encode as E
import Platform
import Shell
import Surface
import SurfaceController as Controller
import TaskbarShell
import UInt64

port outgoing : E.Value -> Cmd msg

counter value = D.decodeValue UInt64.decoder (E.string value) |> Result.withDefault UInt64.zero
binding = E.object [("lifetime",E.string "1"),("session",E.string "1"),("frontend",E.string "1")]
window root = E.object [("incarnation",E.string root),("label",E.string ("Document "++root)),("owner",E.null),("application",E.string "documents"),("minimized",E.bool False),("available",E.bool True)]
attached = E.object [("protocolVersion",E.int 3),("kind",E.string "attached"),("binding",binding)]
projection = E.object [("protocolVersion",E.int 3),("kind",E.string "action-projection"),("binding",binding),("requestId",E.string "1"),("context",E.object [("lifetime",E.string "1"),("epoch",E.string "1"),("output",E.string "1"),("revision",E.string "1")]),("scene",E.object [("revision",E.string "1"),("focused",E.string "1"),("windows",E.list identity [window "1",window "2"])])]
field name model = D.decodeValue (D.field name UInt64.decoder) (Controller.frame model) |> Result.withDefault UInt64.zero
native raw model = Controller.update (Controller.Interaction (Desktop.Incoming raw)) model |> Tuple.first
-- Current readiness requires explicit native idle and the matched motion receipt.
pointerIdle = E.object [("protocolVersion",E.int 3),("kind",E.string "pointer-ownership"),("ownershipProtocol",E.int 1),("binding",binding),("requestId",E.string "1"),("serial",E.string "1"),("state",E.string "idle"),("owner",E.null)]
settleMotion controller =
    (Controller.desktop controller).motion.pending
        |> Maybe.map (\pending -> native (E.object [("protocolVersion",E.int 3),("kind",E.string "motion-profile"),("binding",Binding.encode pending.binding),("requestId",E.string (UInt64.string pending.request)),("profile",E.string (Motion.name pending.profile))]) controller)
        |> Maybe.withDefault controller
ready = Controller.initial |> native attached |> native pointerIdle |> native projection |> settleMotion
opened = Shell.capture (Controller.desktop ready).windows.shell |> Maybe.map (\stamp -> Controller.update (Controller.Interaction (Desktop.Window (TaskbarShell.Primary stamp "application:documents"))) ready |> Tuple.first) |> Maybe.withDefault ready
onlyPresentation effects = case effects of
    [Controller.Publish _] -> True
    _ -> False

scope generation = E.object [("id",E.string "1"),("generation",E.string generation)]
topology revision generation width = E.object [("viewProtocol",E.int 2),("kind",E.string "view-topology"),("revision",E.string revision),("views",E.list identity [scope generation]),("locations",E.list identity [E.object [("scope",scope generation),("box",E.list E.int [0,0,width,480])]])]
outputStep event model = Outputs.update event model |> Tuple.first
outputNative raw model = outputStep (Outputs.Interaction (Desktop.Incoming raw)) model
outputDesktop model = Controller.desktop (Outputs.controller model)
outputMotion model = (outputDesktop model).motion.pending
    |> Maybe.map (\pending -> outputNative (E.object [("protocolVersion",E.int 3),("kind",E.string "motion-profile"),("binding",Binding.encode pending.binding),("requestId",E.string (UInt64.string pending.request)),("profile",E.string (Motion.name pending.profile))]) model)
    |> Maybe.withDefault model
outputReady = Outputs.initial |> outputStep (Outputs.Topology (topology "1" "1" 480)) |> outputNative attached |> outputNative pointerIdle |> outputNative projection |> outputMotion
outputOpened = Shell.capture (outputDesktop outputReady).windows.shell |> Maybe.map (\stamp -> outputStep (Outputs.Interaction (Desktop.Window (TaskbarShell.Primary stamp "application:documents"))) outputReady) |> Maybe.withDefault outputReady
popupCallback generation shown = E.object [("scope",scope generation),("lease",E.string (UInt64.string (field "lease" (Outputs.controller shown))))]

outputChecks =
    let (located,locationEffects)=Outputs.update (Outputs.Topology (topology "2" "1" 640)) outputOpened
        (grown,reflowEffects)=Outputs.update (Outputs.Reflow (popupCallback "1" outputOpened)) located
        shrunkLocation=outputStep (Outputs.Topology (topology "3" "1" 480)) grown
        (shrunk,shrinkEffects)=Outputs.update (Outputs.Reflow (popupCallback "1" grown)) shrunkLocation
        (stale,staleEffects)=Outputs.update (Outputs.Reflow (popupCallback "1" outputOpened)) shrunk
        (foreign,foreignEffects)=Outputs.update (Outputs.Reflow (popupCallback "2" shrunk)) shrunk
        (duplicate,duplicateEffects)=Outputs.update (Outputs.Topology (topology "3" "1" 640)) shrunk
        replaced=outputStep (Outputs.Topology (topology "4" "2" 480)) shrunk
        (retired,retiredEffects)=Outputs.update (Outputs.Reflow (popupCallback "1" shrunk)) replaced
        unready=outputStep (Outputs.Interaction (Desktop.Window (TaskbarShell.Native (Shell.RegistrationRefused [] [])))) outputOpened
        reconciled=outputStep (Outputs.Topology (topology "2" "1" 640)) unready
        ids model=List.map .id (Surface.controls (outputDesktop model))
    in [("outputFixtureHasReadyPicker",Surface.mode (outputDesktop outputOpened)=="picker" && Shell.available (outputDesktop outputOpened).windows.shell),
        ("locationTopologyPreservesEntireController",Outputs.controller located==Outputs.controller outputOpened && onlyPresentation locationEffects && Outputs.pendingBatches located==Outputs.pendingBatches outputOpened),
        ("locationTopologyUpdatesRoutingBox",D.decodeValue (D.field "revision" D.string) (Outputs.frame located)==Ok "2" && Outputs.owner located==Outputs.owner outputOpened),
        ("integratedGrowShrinkPreservesPolicyAndOrder",outputDesktop shrunk==outputDesktop outputOpened && ids shrunk==ids outputOpened && Surface.mode (outputDesktop shrunk)=="picker"),
        ("integratedReflowFreshLeaseWithoutEffects",UInt64.compare (field "lease" (Outputs.controller shrunk)) (field "lease" (Outputs.controller grown))==GT && onlyPresentation reflowEffects && onlyPresentation shrinkEffects),
        ("integratedStaleLeaseInert",stale==shrunk && List.isEmpty staleEffects),
        ("integratedForeignScopeInert",foreign==shrunk && List.isEmpty foreignEffects),
        ("integratedStaleTopologyInert",duplicate==shrunk && List.isEmpty duplicateEffects),
        ("changedViewGenerationRetiresPicker",Surface.mode (outputDesktop replaced)=="closed" && not (Shell.available (outputDesktop replaced).windows.shell)),
        ("retiredScopeCannotReopenPicker",retired==replaced && List.isEmpty retiredEffects),
        ("unreadyTopologyStillReconciles",not (Shell.available (outputDesktop reconciled).windows.shell) && (outputDesktop reconciled).windows.shell.expected/=(outputDesktop unready).windows.shell.expected)]

result =
    let oldLease=field "lease" opened
        (reflow,effects)=Controller.update (Controller.NativeReflow oldLease) opened
        newLease=field "lease" reflow
        (duplicate,duplicateEffects)=Controller.update (Controller.NativeReflow oldLease) reflow
        (staleDismiss,staleDismissEffects)=Controller.update (Controller.NativeDismiss oldLease) reflow
        (freshDismiss,_)=Controller.update (Controller.NativeDismiss newLease) reflow
        oldAction=E.object [("surfaceProtocol",E.int 2),("kind",E.string "surface-action"),("surface",E.string "popup"),("publication",E.string (UInt64.string (field "publication" opened))),("lease",E.string (UInt64.string oldLease)),("id",E.string "family:2")]
        (staleAction,staleActionEffects)=Controller.update (Controller.Renderer oldAction) reflow
        (closed,closedEffects)=Controller.update (Controller.NativeReflow UInt64.zero) Controller.initial
        (again,againEffects)=Controller.update (Controller.NativeReflow newLease) reflow
        checks=[("fixtureHasActualReadyPicker",Surface.mode (Controller.desktop opened)=="picker" && Shell.available (Controller.desktop opened).windows.shell),
            ("reflowPreservesEntireDesktopPolicy",Controller.desktop reflow==Controller.desktop opened),
            ("reflowPublishesWithoutReadsFocusOrEffects",onlyPresentation effects),
            ("reflowMintsFreshLeaseAndPublication",UInt64.compare newLease oldLease==GT && UInt64.compare (field "publication" reflow) (field "publication" opened)==GT),
            ("duplicateRetiredLeaseIsInert",duplicate==reflow && List.isEmpty duplicateEffects),
            ("retiredLeaseDismissalIsInert",staleDismiss==reflow && List.isEmpty staleDismissEffects),
            ("retiredLeaseCannotSelectWindow",staleAction==reflow && List.isEmpty staleActionEffects),
            ("currentLeaseCanStillDismiss",Surface.mode (Controller.desktop freshDismiss)=="closed"),
            ("closedSurfaceCannotReflow",closed==Controller.initial && List.isEmpty closedEffects),
            ("successiveReflowRetainsPolicyWithoutReplay",Controller.desktop again==Controller.desktop opened && onlyPresentation againEffects && UInt64.compare (field "lease" again) newLease==GT)]++outputChecks
    in E.object [("checks",E.object (List.map (\(name,passed) -> (name,E.bool passed)) checks)),("scope",E.string "Compiled actual reflow reducer and full output/topology integration with typed native idle/current motion readiness; physical native input/AT and geometry authority remain separate.")]

main : Program () () Never
main = Platform.worker {init=\_ -> ((),outgoing result),update=\_ state -> (state,Cmd.none),subscriptions=\_ -> Sub.none}
