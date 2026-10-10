module OutcomeAnnouncements exposing (Model, initial, observe, encode)

import Announcement
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
type Model = Model Counter (Maybe Announcement.Message)

initial : Model
initial = Model UInt64.zero Nothing

launch model = Launch.refusal model.launch
transfer model = model.windows.shell.effects.transaction |> Maybe.andThen (\transaction ->
    case transaction.intent.operation of
        Effects.TransferWorkspace _ -> if transaction.status==Effects.Refused then Just (E.object [("effectProtocol",E.int transaction.effectProtocol),("intent",Effects.encodeIntent transaction.intent)]) else Nothing
        _ -> Nothing)
settings model = model.settings.outcome |> Maybe.andThen (\outcome -> if outcome.result==Settings.Refused then Just outcome.request else Nothing)

observe : Desktop.Model -> Desktop.Model -> Model -> Model
observe before after ((Model sequence _) as prior) =
    let correlated kind value text = {correlation=E.encode 0 (E.object [("outcome",E.string kind),("binding",after.windows.shell.binding |> Maybe.map Binding.encode |> Maybe.withDefault E.null),("identity",value)]),text=text,interrupt=False}
        candidate =
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
    in case (candidate,UInt64.next sequence) of
        (Just event,Just next) -> Model next (Just {sequence=next,correlation=event.correlation,text=event.text,interrupt=event.interrupt})
        _ -> prior

encode : Model -> E.Value
encode (Model _ current) = current |> Maybe.map Announcement.encodeMessage |> Maybe.withDefault E.null
