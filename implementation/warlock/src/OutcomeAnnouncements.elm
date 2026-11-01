module OutcomeAnnouncements exposing (Model, initial, observe, encode)

import AnnouncementMessage
import AdapterNotice
import Binding
import Catalog
import Desktop
import Effects
import Json.Encode as E
import Launch
import Notifications
import Settings
import Surface
import UInt64 exposing (Counter)

-- One policy in the integration root. Views never infer attention from copy,
-- count changes, rendering, publications or focus. Notifications are admitted
-- only from fresh identities and explicit DND/critical-interruption policy.
type Model = Model Counter (Maybe AnnouncementMessage.Message)

initial : Model
initial = Model UInt64.zero Nothing

launch model = Launch.refusal model.launch
transfer model = model.windows.shell.effects.transaction |> Maybe.andThen (\transaction ->
    case transaction.intent.operation of
        Effects.TransferWorkspace _ -> if transaction.status==Effects.Refused then Just (E.object [("effectProtocol",E.int transaction.effectProtocol),("intent",Effects.encodeIntent transaction.intent)]) else Nothing
        _ -> Nothing)
settings model = model.settings.outcome |> Maybe.andThen (\outcome -> if outcome.result==Settings.Refused then Just outcome.request else Nothing)

-- Current-session Restore announcements are derived from typed effects, not
-- from the rendered status text. Recovered older-frontend records and a
-- disconnected binding need their own durable correlation policy.
currentRestore : Desktop.Model -> Maybe ( Binding.Binding, Effects.Transaction )
currentRestore model =
    let shell = model.windows.shell
    in case (shell.binding,shell.effects.transaction) of
        (Just binding,Just transaction) ->
            if shell.effects.connected
                && transaction.effectProtocol==1
                && transaction.intent.operation==Effects.Restore
                && Binding.matchesContext transaction.intent.context.lifetime transaction.intent.context.epoch binding
                && List.member transaction.status [Effects.Pending,Effects.Refused,Effects.Unknown] then
                Just (binding,transaction)
            else Nothing
        _ -> Nothing

issuedRestore : Binding.Binding -> Effects.Transaction -> Desktop.Model -> Bool
issuedRestore binding transaction model =
    List.any (\entry -> entry.binding==binding && entry.protocol==transaction.effectProtocol && entry.intent==transaction.intent) model.windows.shell.issued

restoreChange : Desktop.Model -> Desktop.Model -> Maybe ( Binding.Binding, Effects.Transaction )
restoreChange before after =
    case currentRestore after of
        Nothing -> Nothing
        Just (binding,transaction) ->
            if before.windows.shell.binding/=Just binding then Nothing else
                case transaction.status of
                    Effects.Pending ->
                        if before.windows.shell.effects.connected
                            && currentRestore before/=Just (binding,transaction)
                            && not (issuedRestore binding transaction before)
                            && issuedRestore binding transaction after then Just (binding,transaction) else Nothing
                    Effects.Refused -> restoreSettlement binding transaction before
                    Effects.Unknown -> restoreSettlement binding transaction before
                    _ -> Nothing

restoreSettlement : Binding.Binding -> Effects.Transaction -> Desktop.Model -> Maybe ( Binding.Binding, Effects.Transaction )
restoreSettlement binding transaction before =
    case currentRestore before of
        Just (oldBinding,old) ->
            if oldBinding==binding && old.effectProtocol==transaction.effectProtocol && old.intent==transaction.intent
                && List.member old.status [Effects.Pending,Effects.Unknown]
                && old.status/=transaction.status && issuedRestore binding old before then Just (binding,transaction) else Nothing
        Nothing -> Nothing

observe : Desktop.Model -> Desktop.Model -> Model -> Model
observe before after ((Model sequence _) as prior) =
    let correlated kind value text = {correlation=E.encode 0 (E.object [("outcome",E.string kind),("binding",after.windows.shell.binding |> Maybe.map Binding.encode |> Maybe.withDefault E.null),("identity",value)]),text=text,interrupt=False}
        existingCandidate =
            if before.adapterNotice/=after.adapterNotice && after.adapterNotice/=Nothing then
                after.adapterNotice |> Maybe.map (\notice -> {correlation=E.encode 0 (E.object [("outcome",E.string "adapter-unavailable"),("binding",Binding.encode notice.binding),("identity",AdapterNotice.encode notice)]),text=AdapterNotice.message notice,interrupt=False})
            else
                if launch before/=launch after then launch after |> Maybe.map (\refusal ->
                    let label=after.applications |> Maybe.andThen (Catalog.lookup refusal.entry) |> Maybe.map .name |> Maybe.withDefault refusal.entry
                    in correlated "launch-refused" refusal.intent ("Launch refused for "++String.left 512 label++". Refresh applications, then choose again."))
                else if transfer before/=transfer after then transfer after |> Maybe.map (\intent -> correlated "transfer-refused" intent (Surface.windowNotice after))
                else if settings before/=settings after then settings after |> Maybe.map (\request -> correlated "settings-refused" (E.string (UInt64.string request)) after.settings.notice)
                else if before.notifications.outcome/=after.notifications.outcome && not after.notifications.policy.doNotDisturb then
                    after.notifications.outcome |> Maybe.andThen (\outcome -> if outcome.status=="Refused" && outcome.expired then Just (correlated "notification-expired-action-refused" (E.object [("request",E.string (UInt64.string outcome.request)),("target",Notifications.encodeIntent outcome.target)]) "Notification action refused because the target expired. Refresh notifications, then choose a current notification.") else Nothing)
                else
                    let expired=if before.windows.shell.binding==after.windows.shell.binding && after.windows.shell.binding/=Nothing then Notifications.expirations (if before.notificationsOpen then before.notifications else Notifications.clearFocus before.notifications) after.notifications else []
                        expiryIdentity=after.notifications.snapshot |> Maybe.map (\snapshot -> E.object [("service",E.string (UInt64.string snapshot.service)),("revision",E.string (UInt64.string snapshot.revision)),("incarnations",E.list (\entry -> E.string (UInt64.string entry.incarnation)) expired)]) |> Maybe.withDefault E.null
                        expiryText=String.join "; " (List.map (\entry -> String.left 200 (String.join " " (String.words (entry.app++": "++entry.summary)))) (List.take 3 expired))++" expired. Its actions are unavailable. Refresh notifications for current history."
                        arrivals=if before.windows.shell.binding==after.windows.shell.binding && after.windows.shell.binding/=Nothing then Notifications.arrivals before.notifications after.notifications else []
                        clean value=String.join " " (String.words value)
                        summary entry=String.left 200 (clean (entry.app++": "++entry.summary))
                        details=String.join "; " (List.map summary (List.take 3 arrivals))++(if List.length arrivals>3 then "; and "++String.fromInt (List.length arrivals-3)++" more" else "")
                        identity=after.notifications.snapshot |> Maybe.map (\snapshot -> E.object [("service",E.string (UInt64.string snapshot.service)),("revision",E.string (UInt64.string snapshot.revision)),("incarnations",E.list (\entry -> E.string (UInt64.string entry.incarnation)) arrivals)]) |> Maybe.withDefault E.null
                        event=correlated "notification-arrival" identity (details++". Open Notifications for details and current actions.")
                    in if not (List.isEmpty expired) then Just (correlated "notification-expiration" expiryIdentity expiryText) else if List.isEmpty arrivals then Nothing else Just {event|interrupt=after.notifications.policy.interruptCritical && List.all Notifications.critical arrivals}
        candidate =
            case existingCandidate of
                Just event -> Just event
                Nothing -> restoreChange before after |> Maybe.map (\(_,transaction) ->
                    let identity = E.object [("effectProtocol",E.int transaction.effectProtocol),("intent",Effects.encodeIntent transaction.intent),("status",E.string (Effects.statusName transaction.status))]
                        -- Screen-reader payloads reject control characters and are
                        -- bounded independently of labels from window metadata.
                        text = Surface.windowNotice after |> String.filter (\char -> Char.toCode char>=32 && Char.toCode char/=127) |> String.left 1024
                    in correlated "restore-status" identity text)
    in case (candidate,UInt64.next sequence) of
        (Just event,Just next) -> Model next (Just {sequence=next,correlation=event.correlation,text=event.text,interrupt=event.interrupt})
        _ -> prior

encode : Model -> E.Value
encode (Model _ current) = current |> Maybe.map AnnouncementMessage.encodeMessage |> Maybe.withDefault E.null
