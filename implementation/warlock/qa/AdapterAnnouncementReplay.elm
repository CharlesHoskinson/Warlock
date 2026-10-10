port module AdapterAnnouncementReplay exposing (main)

import AdapterNotice
import Binding
import Desktop
import Json.Decode as D
import Json.Encode as E
import OutcomeAnnouncements as Attention
import OutputController as Outputs
import Platform
import Shell
import SnapReplay as Fixture
import Surface
import SurfaceController as Controller
import UInt64

port outgoing : E.Value -> Cmd msg
counter = Fixture.counter
bound = Fixture.bound
foreign = E.object [("lifetime",E.string "1"),("session",E.string "1"),("frontend",E.string "2")]
current root = Controller.desktop (Outputs.controller root)
step message root = Outputs.update (Outputs.Interaction message) root |> Tuple.first
scoped make root = Desktop.capture (current root) |> Maybe.map (\stamp -> step (make stamp) root) |> Maybe.withDefault root
serial root = D.decodeValue (D.at ["announcement","sequence"] UInt64.decoder) (Outputs.frame root) |> Result.withDefault UInt64.zero
scope id = E.object [("id",E.string id),("generation",E.string "1")]
topology = E.object [("viewProtocol",E.int 1),("kind",E.string "view-topology"),("revision",E.string "1"),("views",E.list scope ["1","2"])]
attached = E.object [("protocolVersion",E.int 3),("kind",E.string "attached"),("binding",bound)]
start = Outputs.update (Outputs.Topology topology) Outputs.initial |> Tuple.first |> step (Desktop.Incoming attached)
snapshot available revision = E.object [("service",E.string "9"),("revision",E.string revision),("available",E.bool available),("reason",E.string (if available then "" else "Another notification service is running.")),("entries",E.list identity [])]
receipt kind owner requestId value = E.object [("protocolVersion",E.int 3),("kind",E.string kind),("binding",owner),("requestId",E.string (UInt64.string requestId)),("snapshot",value)]
initialUpdate = E.object [("protocolVersion",E.int 3),("kind",E.string "notification-update"),("binding",bound),("snapshot",snapshot False "1")]
observed = step (Desktop.Incoming initialUpdate) start
opened = scoped Desktop.OpenNotifications observed
request root = (current root).notificationsExpected |> Maybe.withDefault UInt64.zero
failureRaw = receipt "notification-snapshot" bound (request opened) (snapshot False "1")
failed = step (Desktop.Incoming failureRaw) opened
repeated = step (Desktop.Incoming failureRaw) failed
retrying = scoped Desktop.RefreshNotifications failed
retryRaw = receipt "notification-snapshot" bound (request retrying) (snapshot False "1")
retried = step (Desktop.Incoming retryRaw) retrying
recovering = scoped Desktop.RefreshNotifications retried
recovered = step (Desktop.Incoming (receipt "notification-snapshot" bound (request recovering) (snapshot True "2"))) recovering
noFocus effects = List.all (\effect -> case effect of
    Controller.DesktopEffect (Desktop.Focus _) -> False
    _ -> True) effects
readOnly effects = List.all (\effect -> case effect of
    Controller.DesktopEffect (Desktop.Send raw) -> D.decodeValue (D.field "kind" D.string) raw==Ok "notification-request"
    Controller.DesktopEffect (Desktop.Focus _) -> False
    _ -> True) effects
base = D.decodeValue Binding.decoder bound |> Result.toMaybe |> Maybe.map Fixture.readyFor |> Maybe.withDefault Desktop.initial
matrix =
    let expected=counter "71"
        availability=[("service",E.string "9"),("revision",E.string "1"),("available",E.bool False),("reason",E.string "Native adapter unavailable.")]
        files = E.object (availability++[("peer",E.null)])
        actions = E.object (availability++[("entry",E.string "docs.desktop"),("name",E.string "Documents"),("actions",E.list identity [])])
        system volumeValue = E.object [("service",E.string "9"),("revision",E.string "1"),("volume",volumeValue),("network",E.null),("power",E.null),("session",E.null)]
        volume = E.object [("percent",E.int 40),("muted",E.bool False),("label",E.string "Native output")]
        execute name source before raw =
            let (after,effects)=Desktop.update (Desktop.Incoming raw) before
                message=Attention.observe before after Attention.initial
                duplicate=Desktop.update (Desktop.Incoming raw) after
            in (name,after.adapterNotice |> Maybe.map .source |> (==) (Just source),List.isEmpty effects && Tuple.first duplicate==after && List.isEmpty (Tuple.second duplicate) && Attention.observe after (Tuple.first duplicate) message==message)
        fileBase={base | filesExpected=Just expected,filesOpen=True,filesOpening=True}
        actionBase={base | jumpExpected=Just expected,jumpEntry=Just "docs.desktop",jumpOpening=True}
        systemBase={base | systemMenuExpected=Just expected,systemMenuOpen=True,systemMenuOpening=True}
        settingsBase={base | settingsExpected=Just expected,settingsOpen=True,settingsOpening=True}
        motionBase={base | motionExpected=Just expected}
        cases=[execute "Files" AdapterNotice.Files fileBase (receipt "files-snapshot" bound expected files)
            ,execute "ApplicationActions" AdapterNotice.ApplicationActions actionBase (receipt "jump-list-snapshot" bound expected actions)
            ,execute "System" AdapterNotice.System systemBase (receipt "system-menu-snapshot" bound expected (system E.null))
            ,execute "Settings" AdapterNotice.Settings settingsBase (receipt "shell-settings" bound expected E.null)
            ,execute "Motion" AdapterNotice.Motion motionBase (receipt "motion-preferences" bound expected E.null)]
        (partial,_)=Desktop.update (Desktop.Incoming (receipt "system-menu-snapshot" bound expected (system volume))) systemBase
        (lost,lostEffects)=Desktop.update (Desktop.Incoming (E.object [("protocolVersion",E.int 3),("kind",E.string "host-disconnected")])) base
        (lostAgain,_)=Desktop.update (Desktop.Incoming (E.object [("protocolVersion",E.int 3),("kind",E.string "host-disconnected")])) lost
    in List.concatMap (\(name,admitted,stable) -> [(name++"MatchedTypedFailure",admitted),(name++"RepeatSilentNoFocus",stable)]) cases ++ [("PartialSystemCapabilityDoesNotAnnounceWholeAdapter",partial.adapterNotice==Nothing),("ConnectionLossTypedOnce",lost.adapterNotice |> Maybe.map .source |> (==) (Just AdapterNotice.Windows)),("RepeatedConnectionLossDoesNotReannounce",lostAgain.adapterNotice==lost.adapterNotice && List.isEmpty lostEffects)]
result =
    let (_,failureEffects)=Outputs.update (Outputs.Interaction (Desktop.Incoming failureRaw)) opened
        (_,retryEffects)=Outputs.update (Outputs.Interaction (Desktop.capture (current failed) |> Maybe.map Desktop.RefreshNotifications |> Maybe.withDefault (Desktop.Incoming E.null))) failed
        identity=D.decodeValue (D.at ["announcement","correlation"] D.string) (Outputs.frame failed) |> Result.andThen (D.decodeString D.value) |> Result.withDefault E.null
        checks=[("InitialUnavailableObservationIsSilent",serial observed==UInt64.zero)
            ,("MatchedOpeningFailureAnnounces",serial failed==counter "1" && (current failed).adapterNotice/=Nothing)
            ,("OpeningFailureDoesNotRequestFocus",noFocus failureEffects)
            ,("ExactRepeatedReceiptIsSilent",repeated==failed)
            ,("ForeignBindingCannotSettle",step (Desktop.Incoming (receipt "notification-snapshot" foreign (request opened) (snapshot False "1"))) opened==opened)
            ,("ForeignRequestCannotSettle",step (Desktop.Incoming (receipt "notification-snapshot" bound (counter "999") (snapshot False "1"))) opened==opened)
            ,("ExplicitRefreshHasFreshIdentity",request retrying/=request opened && serial retried==counter "2")
            ,("RefreshIsReadOnlyNoFocus",readOnly retryEffects)
            ,("PendingRefreshCannotSubmitAnotherRead",Desktop.capture (current retrying) |> Maybe.map (\stamp -> Desktop.update (Desktop.RefreshNotifications stamp) (current retrying)==(current retrying,[])) |> Maybe.withDefault False)
            ,("SuccessfulRecoveryDoesNotReplayFailure",serial recovered==serial retried && ((current recovered).notifications.snapshot |> Maybe.map .available)==Just True)
            ,("ExactNativeCorrelation",D.decodeValue (D.field "binding" Binding.decoder) identity==D.decodeValue Binding.decoder bound && D.decodeValue (D.at ["identity","request"] UInt64.decoder) identity==Ok (request opened) && D.decodeValue (D.at ["identity","service"] D.string) identity==Ok "9" && D.decodeValue (D.at ["identity","revision"] D.string) identity==Ok "1")
            ,("PoliteFailure",D.decodeValue (D.at ["announcement","interrupt"] D.bool) (Outputs.frame failed)==Ok False)
            ,("RecoveryControlReachable",List.any (\control -> control.id=="notifications:refresh" && control.enabled && control.message/=Nothing) (Surface.controls (current failed)))]++matrix
    in E.object [("checks",E.object (List.map (\(name,passed)->(name,E.bool passed)) checks)),("openedFrame",Outputs.frame opened),("failedFrame",Outputs.frame failed),("retryPendingFrame",Outputs.frame retrying),("retryFrame",Outputs.frame retried),("recoveredFrame",Outputs.frame recovered)]
main = Platform.worker {init=\()->((),outgoing result),update=\_ model->(model,Cmd.none),subscriptions=\_->Sub.none}
