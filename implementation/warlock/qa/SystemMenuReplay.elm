port module SystemMenuReplay exposing (main)
import Desktop
import SystemMenu
import Surface
import SurfaceRenderer
import Json.Decode as D
import Json.Encode as E
import Platform
import UInt64
port outgoing : E.Value -> Cmd msg
counter value = D.decodeValue UInt64.decoder (E.string value) |> Result.withDefault UInt64.zero
bound = E.object [("lifetime",E.string "1"),("session",E.string "1"),("frontend",E.string "1")]
native raw model = Desktop.update (Desktop.Incoming raw) model |> Tuple.first
attached = E.object [("protocolVersion",E.int 3),("kind",E.string "attached"),("binding",bound)]
snapshot revision percent = E.object [("service",E.string "9"),("revision",E.string revision),("volume",E.object [("percent",E.int percent),("muted",E.bool False),("label",E.string "Warlock private audio")]),("network",E.null),("power",E.object [("suspend",E.string "yes"),("reboot",E.string "yes"),("poweroff",E.string "no")]),("session",E.object [("name",E.string "Warlock private session"),("state",E.string "active"),("locked",E.bool False)])]
loaded request value = E.object [("protocolVersion",E.int 3),("kind",E.string "system-menu-snapshot"),("binding",bound),("requestId",E.string (UInt64.string request)),("snapshot",value)]
outcome request status value = E.object [("protocolVersion",E.int 3),("kind",E.string "system-menu-outcome"),("binding",bound),("requestId",E.string (UInt64.string request)),("status",E.string status),("snapshot",value)]
dispatch build model = Desktop.capture model |> Maybe.map (\stamp -> Desktop.update (build stamp) model) |> Maybe.withDefault (model,[])
effect e = case e of
    Desktop.Send wire -> D.decodeValue (D.field "kind" D.string) wire==Ok "system-menu-effect"
    _ -> False
result =
    let ready=native attached Desktop.initial
        (opened,_)=dispatch Desktop.OpenSystemMenu ready
        request=opened.systemMenuExpected |> Maybe.withDefault UInt64.zero
        (read,readEffects)=Desktop.update (Desktop.Incoming (loaded request (snapshot "1" 100))) opened
        current=D.decodeValue SystemMenu.decoder (snapshot "1" 100) |> Result.withDefault {service=counter "9",revision=counter "1",volume=Nothing,network=Nothing,power=Nothing,session=Nothing}
        volume=SystemMenu.intent current SystemMenu.Volume 25
        (pending,effects)=dispatch (\stamp -> Desktop.SystemChange stamp volume) read
        effectRequest=pending.systemMenu.pending |> Maybe.map .request |> Maybe.withDefault UInt64.zero
        (_,duplicate)=dispatch (\stamp -> Desktop.SystemChange stamp volume) pending
        committed=native (outcome effectRequest "Committed" (snapshot "2" 25)) pending
        (_,afterCommit)=dispatch (\stamp -> Desktop.SystemChange stamp volume) committed
        unknown=native (outcome effectRequest "Unknown" (snapshot "1" 100)) pending
        (_,unknownRepeat)=dispatch (\stamp -> Desktop.SystemChange stamp volume) unknown
        (refreshing,refreshEffects)=dispatch Desktop.RefreshSystemMenu unknown
        reconciled=native (loaded (refreshing.systemMenuExpected |> Maybe.withDefault UInt64.zero) (snapshot "2" 25)) refreshing
        unavailable=SystemMenu.intent current SystemMenu.Network 0
        (_,unavailableEffects)=dispatch (\stamp -> Desktop.SystemChange stamp unavailable) read
        restart=SystemMenu.intent current SystemMenu.Reboot 0
        (confirm,confirmEffects)=dispatch (\stamp -> Desktop.SystemChange stamp restart) read
        (cancelled,cancelEffects)=dispatch Desktop.CancelSystemChange confirm
        (submitted,submitEffects)=dispatch (\stamp -> Desktop.ConfirmSystemChange stamp restart) confirm
        (_,directConfirm)=dispatch (\stamp -> Desktop.ConfirmSystemChange stamp restart) read
        wrong=native (outcome (counter "999") "Committed" (snapshot "2" 25)) pending
        stale=Desktop.capture read |> Maybe.map (\stamp -> Desktop.update (Desktop.SystemChange stamp volume) committed |> Tuple.second) |> Maybe.withDefault []
        (closed,closeEffects)=dispatch Desktop.CloseSystemMenu read
        (otherPopup,_)=dispatch Desktop.OpenNotifications read
        frame=Surface.packet (counter "1") (counter "1") read
        checked name value=(name,E.bool value)
        checks=[checked "systemMenuOpenerIntegrated" (D.decodeValue (D.field "bar" (D.list (D.field "id" D.string))) frame |> Result.map (List.member "bar:system") |> Result.withDefault False)
            ,checked "menuModeAcceptedByProductionRenderer" (SurfaceRenderer.decode frame |> Result.map (SurfaceRenderer.mode >> (==) "system") |> Result.withDefault False)
            ,checked "openingReadFocusMatchesCloseControl" (List.any (\e -> case e of
                Desktop.Focus target -> Surface.controls read |> List.any (\c -> c.id=="control:close" && c.domId==target)
                _ -> False) readEffects)
            ,checked "originalUnavailableNetworkShown" (List.any (\c -> c.label=="Network unavailable" && not c.enabled && c.message==Nothing) (Surface.controls read))
            ,checked "remainingStateObserved" (List.any (\c -> String.startsWith "Volume 100%" c.label) (Surface.controls read) && List.any (\c -> String.startsWith "Session Warlock private session" c.label) (Surface.controls read))
            ,checked "oneExplicitVolumeChange" (List.length (List.filter effect effects)==1)
            ,checked "pendingCannotRepeat" (List.isEmpty duplicate)
            ,checked "committedCannotRepeatOldRevision" (List.isEmpty afterCommit && committed.systemMenu.pending==Nothing)
            ,checked "unknownCannotReplay" (List.isEmpty unknownRepeat && unknown.systemMenu.pending/=Nothing && String.contains "not confirmed" unknown.systemMenu.notice)
            ,checked "readReconcilesChangedStateWithoutEffect" (reconciled.systemMenu.pending==Nothing && not (List.any effect refreshEffects))
            ,checked "unavailableNeverSubmits" (List.isEmpty unavailableEffects)
            ,checked "restartRequiresUIConfirmation" (confirm.systemMenuConfirmation==Just restart && not (List.any effect confirmEffects))
            ,checked "cancelHasNoNativeEffect" (cancelled.systemMenuConfirmation==Nothing && not (List.any effect cancelEffects))
            ,checked "confirmedRestartSubmitsOnce" (List.length (List.filter effect submitEffects)==1 && submitted.systemMenu.pending/=Nothing)
            ,checked "directConfirmationCannotBypassPrompt" (List.isEmpty directConfirm)
            ,checked "wrongReceiptCannotSettle" (wrong==pending)
            ,checked "staleViewCannotSubmit" (List.isEmpty stale)
            ,checked "closingFocusesOpenerWithoutNativeEffect" (not closed.systemMenuOpen && not (List.any effect closeEffects))
            ,checked "anotherPopupRetiresSystemWithoutLosingNativeState" (not otherPopup.systemMenuOpen && otherPopup.notificationsOpen && otherPopup.systemMenu==read.systemMenu)
            ,checked "allControlsHaveNames" (List.all (\c -> not (String.isEmpty c.ariaLabel)) (Surface.controls read))]
    in E.object [("checks",E.object checks),("frame",frame),("confirmFrame",Surface.packet (counter "2") (counter "1") confirm),("pendingFrame",Surface.packet (counter "3") (counter "1") pending)]
main = Platform.worker {init=\() -> ((),outgoing result),update=\_ model -> (model,Cmd.none),subscriptions=\_ -> Sub.none}
