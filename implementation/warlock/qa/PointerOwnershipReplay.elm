port module PointerOwnershipReplay exposing (main)
import Binding
import Desktop
import Json.Decode as D
import Json.Encode as E
import Platform
import PointerOwnership as Pointer
import Shell
import UInt64
port outgoing : E.Value -> Cmd msg
counter value = D.decodeValue UInt64.decoder (E.string value) |> Result.withDefault UInt64.zero
bound = D.decodeValue Binding.decoder (E.object [("lifetime",E.string "1"),("session",E.string "1"),("frontend",E.string "1")]) |> Result.toMaybe
wire binding serial state owner = E.object [("protocolVersion",E.int 3),("kind",E.string "pointer-ownership"),("ownershipProtocol",E.int 1),("binding",Binding.encode binding),("requestId",E.string "1"),("serial",E.string serial),("state",E.string state),("owner",owner |> Maybe.map E.string |> Maybe.withDefault E.null)]
receive binding serial state owner model = D.decodeValue Pointer.decoder (wire binding serial state owner) |> Result.map (\value -> Pointer.receive (Just binding) value model) |> Result.withDefault model
result binding =
    let idle=receive binding "1" "idle" Nothing Pointer.initial
        moving=receive binding "2" "move" (Just "9") idle
        resizing=receive binding "3" "resize" (Just "9") moving
        old=receive binding "1" "idle" Nothing resizing
        duplicate=receive binding "3" "idle" Nothing resizing
        released=receive binding "4" "idle" Nothing resizing
        noRoot=receive binding "5" "move" Nothing released
        initial=Desktop.initial
        windows=initial.windows
        shell=windows.shell
        base={initial | windows={windows | shell={shell | binding=Just binding,phase=Shell.Ready}},open=True,overview=True,settingsOpen=True,notificationsOpen=True,systemMenuOpen=True,filesOpen=True}
        (retired,retireEffects)=Desktop.update (Desktop.Incoming (wire binding "2" "move" (Just "9"))) base
        tryOpen constructor=Desktop.capture retired |> Maybe.map (\stamp -> Desktop.update (constructor stamp) retired) |> Maybe.withDefault (retired,[])
        inert pair=Tuple.first pair==retired && List.isEmpty (Tuple.second pair)
        (ended,endEffects)=Desktop.update (Desktop.Incoming (wire binding "3" "idle" Nothing)) retired
        reopened=Desktop.capture ended |> Maybe.map (\stamp -> Desktop.update (Desktop.OpenApplications stamp) ended) |> Maybe.withDefault (ended,[])
        checks=[("IdlePermitsShell",not (Pointer.blocked (Just binding) idle))
            ,("MoveBlocks",Pointer.blocked (Just binding) moving)
            ,("ResizeBlocks",Pointer.blocked (Just binding) resizing)
            ,("OldIdleCannotEndOwnership",old==resizing)
            ,("SameSerialCannotChangeOwner",duplicate==resizing)
            ,("ReleasePermitsShell",not (Pointer.blocked (Just binding) released))
            ,("ActiveUnknownRootStillBlocks",Pointer.blocked (Just binding) noRoot)
            ,("NoBindingCannotApplyForeignOwner",Pointer.receive Nothing {binding=binding,serial=counter "8",state=Pointer.Moving,owner=Nothing} idle==idle)
            ,("IdleWithOwnerRefused",D.decodeValue Pointer.decoder (wire binding "6" "idle" (Just "9")) |> Result.toMaybe |> (==) Nothing)
            ,("ZeroSerialRefused",D.decodeValue Pointer.decoder (wire binding "0" "idle" Nothing) |> Result.toMaybe |> (==) Nothing)
            ,("UnknownModeRefused",D.decodeValue Pointer.decoder (wire binding "6" "drag" Nothing) |> Result.toMaybe |> (==) Nothing)
            ,("NativeOwnerRetiresAllShellSurfaces",not retired.open && not retired.overview && not retired.settingsOpen && not retired.notificationsOpen && not retired.systemMenuOpen && not retired.filesOpen && retired.snap==Nothing && retired.windows.picker==Nothing)
            ,("RetirementNeverStealsFocusOrMutates",List.isEmpty retireEffects)
            ,("GestureObservationPreservesNativeTransactionAndLaunch",retired.windows.shell==base.windows.shell && retired.launch==base.launch)
            ,("ApplicationsBlockedDuringMove",inert (tryOpen Desktop.OpenApplications))
            ,("SystemBlockedDuringMove",inert (tryOpen Desktop.OpenSystemMenu))
            ,("NotificationsBlockedDuringMove",inert (tryOpen Desktop.OpenNotifications))
            ,("SettingsBlockedDuringMove",inert (tryOpen Desktop.OpenSettings))
            ,("FilesBlockedDuringMove",inert (tryOpen Desktop.OpenFiles))
            ,("OverviewBlockedDuringMove",inert (tryOpen Desktop.OpenOverview))
            ,("ReleaseDoesNotReplayPopup",not ended.open && List.isEmpty endEffects)
            ,("FreshInputAfterReleaseWorks",(Tuple.first reopened).open)]
    in E.object [("checks",E.object (List.map (\(name,value) -> (name,E.bool value)) checks)),("nativeAcceptance",E.bool False)]
main : Program () () Never
main = Platform.worker {init=\_ -> ((),outgoing (bound |> Maybe.map result |> Maybe.withDefault E.null)),update=\_ model -> (model,Cmd.none),subscriptions=\_ -> Sub.none}
