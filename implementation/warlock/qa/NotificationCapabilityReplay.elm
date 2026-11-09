port module NotificationCapabilityReplay exposing (main)

import Desktop
import Json.Decode as D
import Json.Encode as E
import NativePointerFixture
import Notifications
import Platform
import Shell
import Surface
import TaskbarShell
import UInt64

port outgoing : E.Value -> Cmd msg
one = UInt64.next UInt64.zero |> Maybe.withDefault UInt64.zero
bound version = E.object [("lifetime",E.string version),("session",E.string version),("frontend",E.string version)]
attachment extra = E.object ([("protocolVersion",E.int 3),("kind",E.string "application-attached"),("binding",bound "1"),("nativeOperations",E.list identity []),("applicationOperations",E.list identity [])] ++ extra)
service = ("notificationOperations",E.list E.string ["notification-read","notification-action"])
local = ("localOperations",E.list E.string ["notification-policy"])
receive wire model = Desktop.update (Desktop.Incoming wire) model |> Tuple.first
shellMessage msg model = Desktop.update (Desktop.Window (TaskbarShell.Native msg)) model |> Tuple.first
dispatch build model = Desktop.capture model |> Maybe.map (\stamp -> Desktop.update (build stamp) model) |> Maybe.withDefault (model,[])
surface role id model =
    Surface.resolve one one (E.object [("surfaceProtocol",E.int 2),("kind",E.string "surface-action"),("surface",E.string role),("publication",E.string "1"),("lease",E.string "1"),("id",E.string id)]) model |> Maybe.map (\message -> Desktop.update message model) |> Maybe.withDefault (model,[])
requests effects = List.filterMap (\effect -> case effect of
    Desktop.Send wire -> Just wire
    Desktop.WindowEffect (Shell.Send wire) -> Just wire
    _ -> Nothing) effects
kinds effects = List.filterMap (\wire -> D.decodeValue (D.field "kind" D.string) wire |> Result.toMaybe) (requests effects)
notificationOnly expected effects = kinds effects==[expected]
noNotifications effects = not (List.any (\kind -> List.member kind ["notification-request","notification-effect"]) (kinds effects))
enabled id model = Surface.packet one one model |> D.decodeValue (D.oneOf [D.field "bar" (D.list (D.map2 Tuple.pair (D.field "id" D.string) (D.field "enabled" D.bool)))]) |> Result.map (List.any (\(name,ready) -> name==id && ready)) |> Result.withDefault False
popupEnabled id model = Surface.controls model |> List.any (\control -> control.id==id && control.enabled && control.message/=Nothing)
row state = E.object [("id",E.string "7"),("incarnation",E.string "11"),("producer",E.string ":1.21"),("app",E.string "Producer A"),("summary",E.string "Current notification"),("body",E.string "Body"),("state",E.string state),("actions",E.list identity (if state=="live" then [E.object [("key",E.string "open"),("label",E.string "Open")]] else []))]
snapshot revision state = E.object [("service",E.string "9"),("revision",E.string revision),("available",E.bool True),("reason",E.string ""),("entries",E.list identity [row state])]
loaded binding request = E.object [("protocolVersion",E.int 3),("kind",E.string "notification-snapshot"),("binding",binding),("requestId",E.string (UInt64.string request)),("snapshot",snapshot "1" "live")]
updated binding = E.object [("protocolVersion",E.int 3),("kind",E.string "notification-update"),("binding",binding),("snapshot",snapshot "2" "expired")]
outcome binding request status = E.object [("protocolVersion",E.int 3),("kind",E.string "notification-outcome"),("binding",binding),("requestId",E.string (UInt64.string request)),("status",E.string status),("snapshot",snapshot "2" (if status=="Unknown" then "unknown" else "invoked"))]
retiredReplies model request effectRequest =
    receive (loaded (bound "1") request) model==model
    && receive (updated (bound "1")) model==model
    && receive (outcome (bound "1") effectRequest "Dispatched") model==model
result =
    let attached=receive (attachment [service,local]) Desktop.initial
        serviceOnly=receive (attachment [service]) Desktop.initial
        legacy=receive (attachment [local]) Desktop.initial
        empty=receive (attachment [local,("notificationOperations",E.list identity [])]) Desktop.initial
        malformed fields=receive (attachment fields) Desktop.initial
        (opened,openEffects)=surface "bar" "bar:notifications" attached
        request=opened.notificationsExpected |> Maybe.withDefault UInt64.zero
        ready=receive (loaded (bound "1") request) opened
        (pending,actionEffects)=surface "popup" "notification:9:11:invoke:open" ready
        effectRequest=pending.notifications.pending |> Maybe.map .request |> Maybe.withDefault UInt64.zero
        settled=receive (outcome (bound "1") effectRequest "Dispatched") pending
        unknown=receive (outcome (bound "1") effectRequest "Unknown") pending
        (serviceOpened,serviceEffects)=surface "bar" "bar:notifications" serviceOnly
        (localOpened,localEffects)=surface "bar" "bar:notifications" legacy
        (_,localRefresh)=dispatch Desktop.RefreshNotifications localOpened
        (dnd,dndEffects)=dispatch (\stamp -> Desktop.ConfigureNotificationPolicy stamp {doNotDisturb=True,interruptCritical=False}) localOpened
        (_,emptyEffects)=surface "bar" "bar:notifications" empty
        transport=shellMessage (Shell.RegistrationRefused [] []) ready
        full=shellMessage Shell.ReconciliationFull ready
        detached=receive (E.object [("protocolVersion",E.int 3),("kind",E.string "host-disconnected")]) pending
        -- Explicit typed phase boundary fixture; requests still traverse the public reducer.
        windows=ready.windows
        oldShell=windows.shell
        exhausted={ready|windows={windows|shell={oldShell|phase=Shell.Exhausted}}}
        denied model = noNotifications (dispatch Desktop.RefreshNotifications model |> Tuple.second) && noNotifications (surface "popup" "notification:9:11:invoke:open" model |> Tuple.second) && not (popupEnabled "notification:9:11:invoke:open" model)
        oldStamp=Desktop.capture ready
        stale=oldStamp |> Maybe.map (\stamp -> Desktop.update (Desktop.RefreshNotifications stamp) settled |> Tuple.second) |> Maybe.withDefault []
        reconnected=shellMessage Shell.Reconnect detached
        oldAttach=receive (attachment [service,local]) reconnected
        native=NativePointerFixture.incoming (E.object [("protocolVersion",E.int 3),("kind",E.string "attached"),("binding",bound "1")]) Desktop.initial |> Tuple.first
        (_,nativeEffects)=dispatch Desktop.OpenNotifications native
        badMissingApplication=E.object [("protocolVersion",E.int 3),("kind",E.string "application-attached"),("binding",bound "1"),("nativeOperations",E.list identity []),service]
        badNative=E.object [("protocolVersion",E.int 3),("kind",E.string "application-attached"),("binding",bound "1"),("nativeOperations",E.list E.string ["window-effect"]),("applicationOperations",E.list identity []),service]
        check name value=(name,E.bool value)
    in E.object [("checks",E.object
        [check "validApplicationOnlyReconcilingService" (attached.windows.shell.applicationOnly && attached.windows.shell.phase==Shell.Reconciling && attached.windows.shell.binding/=Nothing && enabled "bar:notifications" attached)
        ,check "serviceDoesNotGrantApplicationLaunch" (not (Shell.applicationLaunchAvailable attached.windows.shell))
        ,check "serviceDoesNotGrantWindowsOrOtherUtilities" (not (Shell.available attached.windows.shell) && List.all (\id -> not (enabled id attached)) ["bar:overview","bar:switcher","bar:files","bar:system","bar:settings"])
        ,check "actualSurfaceOpenerEmitsOneRead" (opened.notificationsOpen && opened.notificationsExpected/=Nothing && notificationOnly "notification-request" openEffects)
        ,check "readCarriesCurrentBinding" (requests openEffects |> List.head |> Maybe.map (\wire -> D.decodeValue (D.field "binding" D.value) wire |> Result.map (E.encode 0 >> (==) (E.encode 0 (bound "1"))) |> Result.withDefault False) |> Maybe.withDefault False)
        ,check "currentSnapshotEnablesActualActionControl" (ready.notifications.snapshot/=Nothing && ready.notificationsExpected==Nothing && popupEnabled "notification:9:11:invoke:open" ready)
        ,check "actualSurfaceActionEmitsOnce" (notificationOnly "notification-effect" actionEffects && pending.notifications.pending/=Nothing)
        ,check "literalActionIdentityPreserved" (requests actionEffects |> List.head |> Maybe.map (\wire -> D.decodeValue (D.field "intent" D.value) wire |> Result.map (E.encode 0 >> (==) (E.encode 0 (E.object [("service",E.string "9"),("id",E.string "7"),("incarnation",E.string "11"),("producer",E.string ":1.21"),("action",E.string "open"),("verb",E.string "invoke")]))) |> Result.withDefault False) |> Maybe.withDefault False)
        ,check "pendingCannotSendAgain" (noNotifications (surface "popup" "notification:9:11:invoke:open" pending |> Tuple.second))
        ,check "currentOutcomeSettlesTypedPending" (settled.notifications.pending==Nothing && (settled.notifications.outcome |> Maybe.map (.status >> (==) Notifications.OutcomeDispatched) |> Maybe.withDefault False))
        ,check "unknownOutcomeCannotReplay" (unknown.notifications.pending/=Nothing && noNotifications (surface "popup" "notification:9:11:invoke:open" unknown |> Tuple.second))
        ,check "serviceWithoutLocalPolicyStillReads" (serviceOpened.notificationsOpen && notificationOnly "notification-request" serviceEffects && not (Shell.localNotificationPolicyAvailable serviceOnly.windows.shell))
        ,check "serviceDoesNotGrantLocalPolicy" (not (popupEnabled "notifications:dnd" serviceOpened) && not (popupEnabled "notifications:critical-interrupt" serviceOpened))
        ,check "absentServicePreservesLocalOnlyOpen" (localOpened.notificationsOpen && localOpened.notifications.snapshot==Nothing && noNotifications localEffects && noNotifications localRefresh)
        ,check "localDndRemainsLocal" (dnd.notifications.policy.doNotDisturb && List.isEmpty (requests dndEffects))
        ,check "explicitEmptyServiceUnavailable" (empty.windows.shell.binding/=Nothing && noNotifications emptyEffects)
        ,check "duplicateOperationsRefused" ((malformed [("notificationOperations",E.list E.string ["notification-read","notification-action","notification-read"])]).windows.shell.binding==Nothing)
        ,check "unknownOperationRefused" ((malformed [("notificationOperations",E.list E.string ["notification-read","invented"])]).windows.shell.binding==Nothing)
        ,check "partialPairRefused" ((malformed [("notificationOperations",E.list E.string ["notification-read"])]).windows.shell.binding==Nothing)
        ,check "reversedPairRefused" ((malformed [("notificationOperations",E.list E.string ["notification-action","notification-read"])]).windows.shell.binding==Nothing)
        ,check "unknownEnvelopeFieldRefused" ((malformed [service,("unknownCapability",E.bool True)]).windows.shell.binding==Nothing)
        ,check "wrongTypeRefused" ((malformed [("notificationOperations",E.bool True)]).windows.shell.binding==Nothing)
        ,check "explicitApplicationFieldRequired" ((receive badMissingApplication Desktop.initial).windows.shell.binding==Nothing)
        ,check "nativeAuthorityStillRefused" ((receive badNative Desktop.initial).windows.shell.binding==Nothing)
        ,check "transportRefusalBlocksActionsAndReads" (transport.windows.shell.transportRefused && denied transport)
        ,check "reconciliationFullBlocksActionsAndReads" (full.windows.shell.reconciliationFull && denied full)
        ,check "exhaustedBlocksActionsAndReads" (denied exhausted)
        ,check "detachedBlocksActionsAndReads" (detached.windows.shell.phase==Shell.Detached && denied detached)
        ,check "retiredRepliesCannotGrantOrSettle" (retiredReplies transport request effectRequest && retiredReplies full request effectRequest && retiredReplies exhausted request effectRequest && retiredReplies detached request effectRequest)
        ,check "wrongBindingSnapshotRefused" (receive (loaded (bound "2") request) opened==opened)
        ,check "wrongBindingUpdateRefused" (receive (updated (bound "2")) ready==ready)
        ,check "wrongBindingOutcomeRefused" (receive (outcome (bound "2") effectRequest "Dispatched") pending==pending)
        ,check "wrongRequestSnapshotRefused" (receive (loaded (bound "1") UInt64.zero) opened==opened)
        ,check "wrongRequestOutcomeRefused" (receive (outcome (bound "1") UInt64.zero "Dispatched") pending==pending)
        ,check "stalePresentationCannotRead" (noNotifications stale)
        ,check "retiredBindingCannotReattach" (oldAttach.windows.shell.phase==Shell.Detached && noNotifications (dispatch Desktop.OpenNotifications oldAttach |> Tuple.second))
        ,check "genuineNativeNotificationRoutePreserved" (not native.windows.shell.applicationOnly && notificationOnly "notification-request" nativeEffects)
        ])]
main = Platform.worker {init=\() -> ((),outgoing result),update=\_ model -> (model,Cmd.none),subscriptions=\_ -> Sub.none}
