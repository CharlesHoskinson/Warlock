port module KeyboardShortcutsReplay exposing (main)

import Binding
import Desktop
import NativePointerFixture
import Json.Decode as D
import Json.Encode as E
import Platform
import Shell
import Shortcuts
import UInt64

port outgoing : E.Value -> Cmd msg

counter value = D.decodeValue UInt64.decoder (E.string value) |> Result.withDefault UInt64.zero
one = counter "1"
bound = E.object [("lifetime",E.string "1"),("session",E.string "1"),("frontend",E.string "1")]
snapshot binding serial blocked events = { binding = binding, serial = counter serial, blocked = blocked, events = List.map (\(ordinal,route) -> {serial=counter ordinal,route=route,outputGeneration=Nothing}) events }
receive binding value model = Shortcuts.receive (Just binding) value model
base binding =
    let initial=Desktop.initial
        windows=initial.windows
        shell=windows.shell
    in NativePointerFixture.ready {initial | windows={windows | shell={shell | binding=Just binding,phase=Shell.Ready}}}
wire binding serial blocked events = E.object
    [("protocolVersion",E.int 3),("kind",E.string "shell-shortcuts"),("shortcutProtocol",E.int 1)
    ,("binding",Binding.encode binding),("requestId",E.string "1"),("serial",E.string serial),("blocked",E.bool blocked)
    ,("events",E.list (\(ordinal,route) -> E.object [("serial",E.string ordinal),("route",E.string route)]) events)]
incoming value model = Desktop.update (Desktop.Incoming value) model
mutations effects = effects |> List.filter (\effect -> case effect of
    Desktop.Send value -> D.decodeValue (D.field "kind" D.string) value |> Result.map (\kind -> List.member kind ["window-effect","application-launch","shell-settings-write","notification-action","system-change"]) |> Result.withDefault False
    Desktop.WindowEffect (Shell.Send value) -> D.decodeValue (D.field "kind" D.string) value == Ok "window-effect"
    _ -> False)
resultFor binding =
    let (initial,_,_)=receive binding (snapshot binding "0" False []) Shortcuts.initial
        (opened,route,notice)=receive binding (snapshot binding "1" False [("1",Shortcuts.Applications)]) initial
        (_,duplicate,_)=receive binding (snapshot binding "1" False [("1",Shortcuts.Applications)]) opened
        (_,stale,_)=receive binding (snapshot binding "0" False []) opened
        (blocked,blockedRoute,blockedNotice)=receive binding (snapshot binding "2" True []) opened
        (_,gapRoute,gapNotice)=receive binding (snapshot binding "66" False [("3",Shortcuts.System),("4",Shortcuts.Applications)]) opened
        (burst,burstRoute,_)=receive binding (snapshot binding "3" False [("1",Shortcuts.Applications),("2",Shortcuts.System),("3",Shortcuts.Notifications)]) initial
        (_,replay,_)=receive binding (snapshot binding "3" False [("1",Shortcuts.Applications),("2",Shortcuts.System),("3",Shortcuts.Notifications)]) burst
        (rebound,reboundRoute,_)=receive binding (snapshot binding "9" False [("9",Shortcuts.System)]) Shortcuts.initial
        foreign=D.decodeValue Binding.decoder (E.object [("lifetime",E.string "1"),("session",E.string "1"),("frontend",E.string "2")]) |> Result.withDefault binding
        (_,foreignRoute,_)=Shortcuts.receive (Just foreign) (snapshot binding "1" False [("1",Shortcuts.Applications)]) initial
        baseline=incoming (wire binding "0" False []) (base binding) |> Tuple.first
        apps=incoming (wire binding "1" False [("1","applications")]) baseline
        closed=Desktop.capture (Tuple.first apps) |> Maybe.map (\stamp -> Desktop.update (Desktop.CloseApplications stamp) (Tuple.first apps)) |> Maybe.withDefault apps
        repeated=incoming (wire binding "1" False [("1","applications")]) (Tuple.first closed)
        system=incoming (wire binding "2" False [("1","applications"),("2","system")]) (Tuple.first apps)
        notifications=incoming (wire binding "3" False [("1","applications"),("2","system"),("3","notifications")]) (Tuple.first system)
        detached=incoming (wire binding "1" False [("1","applications")]) Desktop.initial
        checks=
            [("FirstCurrentShortcutRoutes",route==Just Shortcuts.Applications && notice==Nothing)
            ,("DuplicateNeverReopens",duplicate==Nothing)
            ,("OlderWatermarkIgnored",stale==Nothing)
            ,("BlockedWatermarkConsumedWithoutRoute",blocked.seen==counter "2" && blockedRoute==Nothing && blockedNotice/=Nothing)
            ,("MissingHistoryRefusedWithoutReplay",gapRoute==Nothing && gapNotice/=Nothing)
            ,("NavigationBurstChoosesLatestOverlay",burstRoute==Just Shortcuts.Notifications && burst.seen==counter "3")
            ,("BurstNeverReplays",replay==Nothing)
            ,("NewBindingAdoptsBaselineWithoutHistoryReplay",rebound.seen==counter "9" && reboundRoute==Nothing)
            ,("ForeignBindingCannotRoute",foreignRoute==Nothing)
            ,("UnknownRouteRefused",D.decodeValue Shortcuts.decoder (wire binding "1" False [("1","exec")]) |> Result.toMaybe |> (==) Nothing)
            ,("MalformedWatermarkRefused",D.decodeValue Shortcuts.decoder (wire binding "9" False [("1","system")]) |> Result.toMaybe |> (==) Nothing)
            ,("RootOpensApplicationsFromNativeEvent",(Tuple.first apps).open && (Tuple.first apps).expected/=Nothing)
            ,("AppsCloseRestoresNamedControl",not (Tuple.first closed).open && (Tuple.second closed |> List.any (\effect -> case effect of
                Desktop.Focus target -> String.endsWith ":control:opener" target
                _ -> False)))
            ,("OldNativeEventCannotReopenAfterDismissal",not (Tuple.first repeated).open && List.isEmpty (Tuple.second repeated))
            ,("SystemRetiresApplications",(Tuple.first system).systemMenuOpen && not (Tuple.first system).open)
            ,("NotificationsRetireSystem",(Tuple.first notifications).notificationsOpen && not (Tuple.first notifications).systemMenuOpen)
            ,("DetachedNativeEventInert",Tuple.first detached==Desktop.initial && List.isEmpty (Tuple.second detached))
            ,("ShortcutRoutesCannotLaunchOrMutateWindows",List.isEmpty (mutations (Tuple.second apps++Tuple.second system++Tuple.second notifications)))]
    in E.object [("checks",E.object (List.map (\(name,yes) -> (name,E.bool yes)) checks))]
result = case D.decodeValue Binding.decoder bound of
    Ok binding -> resultFor binding
    Err _ -> E.object [("checks",E.object [("BindingFixture",E.bool False)])]
main=Platform.worker {init=\() -> ((),outgoing result),update=\_ state -> (state,Cmd.none),subscriptions=\_ -> Sub.none}
