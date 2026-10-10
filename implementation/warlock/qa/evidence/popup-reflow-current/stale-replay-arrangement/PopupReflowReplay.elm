port module PopupReflowReplay exposing (main)

import Desktop
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
ready = Controller.initial |> native attached |> native projection
opened = Shell.capture (Controller.desktop ready).windows.shell |> Maybe.map (\stamp -> Controller.update (Controller.Interaction (Desktop.Window (TaskbarShell.Primary stamp "application:documents"))) ready |> Tuple.first) |> Maybe.withDefault ready
onlyPresentation effects = case effects of
    [Controller.Publish _] -> True
    _ -> False

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
            ("successiveReflowRetainsPolicyWithoutReplay",Controller.desktop again==Controller.desktop opened && onlyPresentation againEffects && UInt64.compare (field "lease" again) newLease==GT)]
    in E.object [("checks",E.object (List.map (\(name,passed) -> (name,E.bool passed)) checks)),("scope",E.string "Compiled actual reflow reducer and legacy two-root picker; physical native input/AT and geometry authority remain separate.")]

main : Program () () Never
main = Platform.worker {init=\_ -> ((),outgoing result),update=\_ state -> (state,Cmd.none),subscriptions=\_ -> Sub.none}
