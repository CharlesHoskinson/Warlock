module AdapterNotice exposing (Source(..), Notice, failedRead, connectionLost, encode, message)

import Binding
import Json.Encode as E
import UInt64 exposing (Counter)

-- A typed observed failure event, never a second availability/effect policy.
-- Native snapshots and existing matched-request reducers decide admission.
type Source = Applications | Notifications | Files | ApplicationActions | System | Settings | Motion | Shortcuts | Windows
type alias Notice = {source:Source,binding:Binding.Binding,request:Counter,service:Maybe Counter,revision:Maybe Counter}
failedRead source binding request service revision unavailable prior =
    if unavailable then Just {source=source,binding=binding,request=request,service=service,revision=revision} else prior
connectionLost binding request = {source=Windows,binding=binding,request=request,service=Nothing,revision=Nothing}
name source = case source of
    Applications -> "applications"
    Notifications -> "notifications"
    Files -> "files"
    ApplicationActions -> "application-actions"
    System -> "system"
    Settings -> "settings"
    Motion -> "motion-preferences"
    Shortcuts -> "shortcut-choices"
    Windows -> "windows"
encode notice = E.object [("adapter",E.string (name notice.source)),("request",E.string (UInt64.string notice.request)),("service",notice.service |> Maybe.map (UInt64.string >> E.string) |> Maybe.withDefault E.null),("revision",notice.revision |> Maybe.map (UInt64.string >> E.string) |> Maybe.withDefault E.null)]
message notice = case notice.source of
    Applications -> "Applications unavailable. Refresh applications, then choose again."
    Notifications -> "Notifications unavailable. Refresh notifications to read current status. No action will be repeated."
    Files -> "Files unavailable. Refresh Files state to read current access. No opening will be repeated."
    ApplicationActions -> "Application actions unavailable. Refresh application actions, then choose again."
    System -> "System controls unavailable. Refresh system state to read current capabilities. No change will be repeated."
    Settings -> "Settings unavailable or unsupported. Refresh settings; the stored copy is preserved."
    Motion -> "Motion preferences unavailable or unsupported. Refresh motion preferences; the stored copy is preserved."
    Shortcuts -> "Shortcut choices unavailable or unsupported. Refresh shortcut choices; existing bindings are preserved."
    Windows -> "Window adapter unavailable. Reconnect to read current state. Unconfirmed actions will not be repeated."
