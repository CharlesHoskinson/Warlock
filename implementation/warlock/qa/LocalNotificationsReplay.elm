port module LocalNotificationsReplay exposing (main)

import Desktop
import Notifications
import Shell
import Surface
import Json.Encode as E
import Json.Decode as D
import UInt64
import Platform

port outgoing : E.Value -> Cmd msg
bound = E.object [("lifetime",E.string "1"),("session",E.string "1"),("frontend",E.string "1")]
attachment local = E.object ([("protocolVersion",E.int 3),("kind",E.string "application-attached"),("binding",bound),("nativeOperations",E.list identity []),("applicationOperations",E.list E.string ["application-launch"])] ++ local)
receive wire model = Desktop.update (Desktop.Incoming wire) model |> Tuple.first
dispatch build model = Desktop.capture model |> Maybe.map (\stamp -> Desktop.update (build stamp) model) |> Maybe.withDefault (model,[])
enabled identity model =
    Surface.packet UInt64.zero UInt64.zero model |> D.decodeValue (D.field "bar" (D.list (D.map2 Tuple.pair (D.field "id" D.string) (D.field "enabled" D.bool)))) |> Result.map (List.any (\(id,ready) -> id==identity && ready)) |> Result.withDefault False
noProvider effects = List.all (\effect -> case effect of
    Desktop.Send _ -> False
    Desktop.WindowEffect (Shell.Send _) -> False
    _ -> True) effects
hasFocus suffix effects = List.any (\effect -> case effect of
    Desktop.Focus target -> String.endsWith suffix target
    _ -> False) effects
result =
    let legacy=receive (attachment []) Desktop.initial
        local=receive (attachment [("localOperations",E.list E.string ["notification-policy"])]) Desktop.initial
        malformed=receive (attachment [("localOperations",E.list E.string ["notification-policy","notification-policy"])]) Desktop.initial
        unknown=receive (attachment [("localOperations",E.list E.string ["window-effect"])]) Desktop.initial
        (legacyOpen,legacyEffects)=dispatch Desktop.OpenNotifications legacy
        (opened,openEffects)=dispatch Desktop.OpenNotifications local
        (refreshed,refreshEffects)=dispatch Desktop.RefreshNotifications opened
        policy={doNotDisturb=True,interruptCritical=False}
        (operated,operationEffects)=dispatch (\stamp -> Desktop.ConfigureNotificationPolicy stamp policy) opened
        (closed,closeEffects)=dispatch Desktop.CloseNotifications operated
        (_,closedEffects)=dispatch (\stamp -> Desktop.ConfigureNotificationPolicy stamp {policy|doNotDisturb=False}) closed
        staleEffects=Desktop.capture opened |> Maybe.map (\stamp -> Desktop.update (Desktop.ConfigureNotificationPolicy stamp {policy|doNotDisturb=False}) operated |> Tuple.second) |> Maybe.withDefault []
        detached=receive (E.object [("protocolVersion",E.int 3),("kind",E.string "host-disconnected")]) operated
        check name value=(name,E.bool value)
    in E.object [("checks",E.object
        [check "legacyNotificationsUnavailable" (not (enabled "bar:notifications" legacy) && not legacyOpen.notificationsOpen && List.isEmpty legacyEffects)
        ,check "explicitLocalCapabilityReachable" (enabled "bar:notifications" local && opened.notificationsOpen)
        ,check "applicationOnlyAndWindowsRemainHonest" (local.windows.shell.applicationOnly && not (Shell.available local.windows.shell) && not (enabled "bar:overview" local) && not (enabled "bar:switcher" local))
        ,check "otherUtilitiesUnavailable" (List.all (\id -> not (enabled id local)) ["bar:files","bar:system","bar:settings"])
        ,check "applicationsRemainEnabled" (enabled "bar:applications" legacy && enabled "bar:applications" local)
        ,check "malformedCapabilityRefused" (malformed.windows.shell.binding==Nothing && unknown.windows.shell.binding==Nothing)
        ,check "openHasNoDaemonReadAndFocusesClose" (noProvider openEffects && hasFocus "notifications:close" openEffects && opened.notificationsExpected==Nothing && not opened.notificationsOpening)
        ,check "serviceUnavailableWithoutFabricatedSnapshot" (opened.notifications.snapshot==Nothing && opened.notifications.notice=="Notification service unavailable. Session notification policy is available.")
        ,check "refreshHasNoDaemonRead" (noProvider refreshEffects && refreshed.notificationsExpected==Nothing)
        ,check "daemonRefreshControlDisabled" (Surface.controls opened |> List.any (\control -> control.id=="notifications:refresh" && not control.enabled && control.message==Nothing))
        ,check "sessionDndOperatesLocally" (operated.notifications.policy.doNotDisturb && noProvider operationEffects && List.isEmpty operationEffects)
        ,check "dismissRestoresOpener" (not closed.notificationsOpen && hasFocus "notifications:opener" closeEffects)
        ,check "closedAndStalePolicyCannotOperate" (List.isEmpty closedEffects && List.isEmpty staleEffects)
        ,check "disconnectClearsCapability" (not (enabled "bar:notifications" detached) && detached.windows.shell.phase==Shell.Detached && not (Shell.localNotificationPolicyAvailable detached.windows.shell) && not detached.windows.shell.localNotificationPolicy)
        ])]
main = Platform.worker {init=\() -> ((),outgoing result),update=\_ model -> (model,Cmd.none),subscriptions=\_ -> Sub.none}
