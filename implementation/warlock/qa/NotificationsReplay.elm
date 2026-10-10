port module NotificationsReplay exposing (main)

import Desktop
import NativePointerFixture
import Notifications
import Surface
import SurfaceRenderer
import Json.Decode as D
import Json.Encode as E
import Platform
import UInt64

port outgoing : E.Value -> Cmd msg
counter value = D.decodeValue UInt64.decoder (E.string value) |> Result.withDefault UInt64.zero
bound = E.object [("lifetime",E.string "1"),("session",E.string "1"),("frontend",E.string "1")]
native raw model = NativePointerFixture.incoming raw model |> Tuple.first
attached = E.object [("protocolVersion",E.int 3),("kind",E.string "attached"),("binding",bound)]
entry incarnation state = E.object [("id",E.string "1"),("incarnation",E.string incarnation),("producer",E.string ":1.7"),("app",E.string "Calendar"),("summary",E.string "Meeting soon"),("body",E.string "Bring your notes"),("state",E.string state),("actions",if state=="live" then E.list identity [E.object [("key",E.string "open"),("label",E.string "Open meeting")]] else E.list identity [])]
snapshot revision incarnation state = E.object [("service",E.string "9"),("revision",E.string revision),("available",E.bool True),("reason",E.string ""),("entries",E.list identity [entry incarnation state])]
update value = E.object [("protocolVersion",E.int 3),("kind",E.string "notification-update"),("binding",bound),("snapshot",value)]
loaded request value = E.object [("protocolVersion",E.int 3),("kind",E.string "notification-snapshot"),("binding",bound),("requestId",E.string (UInt64.string request)),("snapshot",value)]
outcome request status value = E.object [("protocolVersion",E.int 3),("kind",E.string "notification-outcome"),("binding",bound),("requestId",E.string (UInt64.string request)),("status",E.string status),("snapshot",value)]
dispatch build model = Desktop.capture model |> Maybe.map (\stamp -> Desktop.update (build stamp) model) |> Maybe.withDefault (model,[])
result =
    let ready=native (update (snapshot "1" "1" "live")) (native attached Desktop.initial)
        (opened,_)=dispatch Desktop.OpenNotifications ready
        request=opened.notificationsExpected |> Maybe.withDefault UInt64.zero
        (read,readEffects)=Desktop.update (Desktop.Incoming (loaded request (snapshot "1" "1" "live"))) opened
        choice=read.notifications.snapshot |> Maybe.andThen (\current -> List.head current.entries |> Maybe.map (\row -> Notifications.target current row "invoke" "open"))
        action model=choice |> Maybe.map (\target -> dispatch (\stamp -> Desktop.NotificationAction stamp target) model) |> Maybe.withDefault (model,[])
        (pending,effects)=action read
        effectRequest=pending.notifications.pending |> Maybe.map .request |> Maybe.withDefault UInt64.zero
        (_,duplicate)=action pending
        committed=native (outcome effectRequest "Dispatched" (snapshot "2" "1" "invoked")) pending
        (_,afterCommit)=action committed
        expired=native (update (snapshot "2" "1" "expired")) read
        (_,afterExpiry)=action expired
        reused=native (update (snapshot "3" "2" "live")) expired
        (_,oldQueued)=action reused
        unknown=native (outcome effectRequest "Unknown" (snapshot "2" "1" "unknown")) pending
        (_,unknownRepeat)=action unknown
        (refreshing,refreshEffects)=dispatch Desktop.RefreshNotifications unknown
        reconciled=native (loaded (refreshing.notificationsExpected |> Maybe.withDefault UInt64.zero) (snapshot "2" "1" "unknown")) refreshing
        stale=case Desktop.capture read of
            Just stamp -> choice |> Maybe.map (\target -> Desktop.update (Desktop.NotificationAction stamp target) reused |> Tuple.second) |> Maybe.withDefault []
            Nothing -> []
        wrong=native (outcome (counter "999") "Dispatched" (snapshot "2" "1" "invoked")) pending
        backwards=native (update (snapshot "1" "1" "live")) expired
        (incoming,incomingEffects)=Desktop.update (Desktop.Incoming (update (snapshot "2" "1" "expired"))) read
        frame=Surface.packet (counter "1") (counter "1") read
        expiredFrame=Surface.packet (counter "2") (counter "1") expired
        effect e=case e of
            Desktop.Send wire -> D.decodeValue (D.field "kind" D.string) wire==Ok "notification-effect"
            _ -> False
        checked name value=(name,E.bool value)
        checks=[checked "notificationOpenerIntegrated" (D.decodeValue (D.field "bar" (D.list (D.field "id" D.string))) frame |> Result.map (List.member "bar:notifications") |> Result.withDefault False)
            ,checked "centerModeAcceptedByProductionRenderer" (SurfaceRenderer.decode frame |> Result.map (SurfaceRenderer.mode >> (==) "notifications") |> Result.withDefault False)
            ,checked "openingReadFocusMatchesActualControl" (List.any (\e -> case e of
                Desktop.Focus target -> Surface.controls read |> List.any (\c -> c.id=="control:close" && c.domId==target)
                _ -> False) readEffects)
            ,checked "oneExplicitAction" (List.length (List.filter effect effects)==1)
            ,checked "pendingCannotRepeat" (List.isEmpty duplicate)
            ,checked "dispatchedCannotRepeat" (List.isEmpty afterCommit)
            ,checked "expiryRemovesActionsAndKeepsHistory" (List.all (\c -> not (String.endsWith ":invoke:open" c.id)) (Surface.controls expired) && List.any (\c -> c.detail=="History · expired") (Surface.controls expired))
            ,checked "expiredChoiceIsInert" (List.isEmpty afterExpiry)
            ,checked "reusedIdRejectsOldIncarnation" (List.isEmpty oldQueued)
            ,checked "unknownCannotReplay" (List.isEmpty unknownRepeat && unknown.notifications.pending/=Nothing)
            ,checked "explicitReadReconcilesRetiredUnknownWithoutEffect" (reconciled.notifications.pending==Nothing && not (List.any effect refreshEffects))
            ,checked "staleViewCannotSubmit" (List.isEmpty stale)
            ,checked "wrongReceiptCannotSettle" (wrong==pending)
            ,checked "olderObservationCannotReviveTarget" (backwards==expired)
            ,checked "incomingExpiryNeverMovesFocus" (List.isEmpty incomingEffects && incoming.notificationsOpen)
            ,checked "allControlsHaveNames" (List.all (\c -> not (String.isEmpty c.ariaLabel)) (Surface.controls read))]
    in E.object [("checks",E.object checks),("frame",frame),("expiredFrame",expiredFrame)]
main = Platform.worker {init=\() -> ((),outgoing result),update=\_ model -> (model,Cmd.none),subscriptions=\_ -> Sub.none}
