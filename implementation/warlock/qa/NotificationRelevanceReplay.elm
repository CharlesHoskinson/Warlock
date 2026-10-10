port module NotificationRelevanceReplay exposing (main)

import Desktop
import Json.Decode as D
import Json.Encode as E
import Notifications
import OutputController as Outputs
import Platform
import SurfaceController as Controller
import UInt64

port outgoing : E.Value -> Cmd msg
counter value = D.decodeValue UInt64.decoder (E.string value) |> Result.withDefault UInt64.zero
bound = E.object [("lifetime",E.string "1"),("session",E.string "1"),("frontend",E.string "1")]
current root = Controller.desktop (Outputs.controller root)
field name raw = D.decodeValue (D.field name D.value) raw |> Result.withDefault E.null
step message root = Outputs.update (Outputs.Interaction message) root |> Tuple.first
scoped make root = Desktop.capture (current root) |> Maybe.map (\stamp -> step (make stamp) root) |> Maybe.withDefault root
serial root = D.decodeValue (D.at ["announcement","sequence"] UInt64.decoder) (Outputs.frame root) |> Result.withDefault UInt64.zero
scope id = E.object [("id",E.string id),("generation",E.string "1")]
topology = E.object [("viewProtocol",E.int 1),("kind",E.string "view-topology"),("revision",E.string "1"),("views",E.list scope ["1","2"])]
attached = E.object [("protocolVersion",E.int 3),("kind",E.string "attached"),("binding",bound)]
entry id state = E.object [("id",E.string id),("incarnation",E.string id),("producer",E.string ":1.7"),("app",E.string "Calendar"),("summary",E.string ("Meeting "++id)),("body",E.string "Details"),("state",E.string state),("actions",E.list identity (if state=="live" then [E.object [("key",E.string "open"),("label",E.string "Open meeting")]] else [])),("urgency",E.int 1)]
snapshot revision rows = E.object [("service",E.string "9"),("revision",E.string revision),("available",E.bool True),("reason",E.string ""),("entries",E.list identity rows)]
update revision rows = E.object [("protocolVersion",E.int 3),("kind",E.string "notification-update"),("binding",bound),("snapshot",snapshot revision rows)]
start = Outputs.update (Outputs.Topology topology) Outputs.initial |> Tuple.first |> step (Desktop.Incoming attached) |> step (Desktop.Incoming (update "1" [entry "1" "live",entry "2" "live"])) |> scoped Desktop.OpenNotifications
ready = step (Desktop.Incoming (E.object [("protocolVersion",E.int 3),("kind",E.string "notification-snapshot"),("binding",bound),("requestId",E.string ((current start).notificationsExpected |> Maybe.map UInt64.string |> Maybe.withDefault "0")),("snapshot",snapshot "1" [entry "1" "live",entry "2" "live"])])) start
focusAction id root =
    let frame=field "frame" (Outputs.frame root)
    in E.object [("surfaceProtocol",E.int 2),("kind",E.string "surface-notification-focus"),("surface",E.string "popup"),("publication",field "publication" frame),("lease",field "lease" frame),("id",E.string id)]
renderer owner action root = Outputs.update (Outputs.Renderer (E.object [("viewProtocol",E.int 1),("kind",E.string "view-action"),("scope",scope owner),("action",action)])) root |> Tuple.first
focused = renderer "1" (focusAction "notification:9:1:invoke:open" ready) ready
expiredRaw = update "2" [entry "1" "expired",entry "2" "live"]
expired = step (Desktop.Incoming expiredRaw) focused
repeated = step (Desktop.Incoming expiredRaw) expired
unrelated = step (Desktop.Incoming (update "2" [entry "1" "live",entry "2" "expired"])) focused
lateFocused = renderer "1" (focusAction "notification:9:1:invoke:open" (step (Desktop.Incoming expiredRaw) ready)) (step (Desktop.Incoming expiredRaw) ready)
target = {service=counter "9",id=counter "1",incarnation=counter "1",producer=":1.7",verb="invoke",action="open"}
pending = scoped (\stamp -> Desktop.NotificationAction stamp target) focused
pendingExpired = step (Desktop.Incoming expiredRaw) pending
request root = (current root).notifications.pending |> Maybe.map .request |> Maybe.withDefault UInt64.zero
receipt owner req value status = E.object [("protocolVersion",E.int 3),("kind",E.string "notification-outcome"),("binding",owner),("requestId",E.string (UInt64.string req)),("status",E.string status),("snapshot",value)]
refusal = receipt bound (request pending) (snapshot "2" [entry "1" "expired",entry "2" "live"]) "Refused"
refused = step (Desktop.Incoming refusal) pendingExpired
replacement = step (Desktop.Incoming (update "3" [entry "2" "live",entry "3" "live"])) pendingExpired
replacementRefused = step (Desktop.Incoming (receipt bound (request pending) (snapshot "3" [entry "2" "live",entry "3" "live"]) "Refused")) replacement
policy root = scoped (\stamp -> Desktop.ConfigureNotificationPolicy stamp {doNotDisturb=True,interruptCritical=True}) root
silent = step (Desktop.Incoming expiredRaw) (policy focused)
silentRefused = step (Desktop.Incoming refusal) (step (Desktop.Incoming expiredRaw) (policy pending))
cleared = renderer "1" (focusAction "control:close" refused) refused
noFocus effects = List.all (\effect -> case effect of
    Controller.DesktopEffect (Desktop.Focus _) -> False
    _ -> True) effects
controlValue id root = D.decodeValue (D.at ["frame","popup"] (D.list D.value)) (Outputs.frame root) |> Result.withDefault [] |> List.filter (\raw -> D.decodeValue (D.field "id" D.string) raw==Ok id) |> List.head |> Maybe.withDefault E.null
result =
    let id="notification:9:1:invoke:open"
        retained=controlValue id expired
        (_,expiryEffects)=Outputs.update (Outputs.Interaction (Desktop.Incoming expiredRaw)) focused
        (_,refusalEffects)=Outputs.update (Outputs.Interaction (Desktop.Incoming refusal)) pendingExpired
        foreign=E.object [("lifetime",E.string "1"),("session",E.string "1"),("frontend",E.string "2")]
        checks=[("MatchedFocusedExpiryPolite",serial expired==counter "1" && D.decodeValue (D.at ["announcement","interrupt"] D.bool) (Outputs.frame expired)==Ok False)
            ,("PassiveFocusCreatesNoAnnouncement",serial focused==UInt64.zero && Notifications.focusedIdentity (current focused).notifications==Just id)
            ,("IrrelevantExpirySilent",serial unrelated==UInt64.zero)
            ,("RepeatedExpirySilent",serial repeated==serial expired)
            ,("LateFocusCannotReplayExpiry",serial lateFocused==UInt64.zero)
            ,("FocusedUnavailableNodeIsNotActionable",D.decodeValue (D.field "focusOnly" D.bool) retained==Ok True && D.decodeValue (D.field "enabled" D.bool) retained==Ok False)
            ,("PendingActionRetainsFocusWithoutAuthority",D.decodeValue (D.field "focusOnly" D.bool) (controlValue id pending)==Ok True && D.decodeValue (D.field "enabled" D.bool) (controlValue id pending)==Ok False)
            ,("UserInvokedExpiryRelevant",serial pendingExpired==counter "1")
            ,("MatchedExpiredActionRefusalPolite",serial refused==counter "2" && (current refused).notifications.pending==Nothing)
            ,("RefusalRetainsExactRequestAndTarget",(current refused).notifications.outcome |> Maybe.map (\outcome -> outcome.request==request pending && outcome.target==target && outcome.expired) |> Maybe.withDefault False)
            ,("ReplacementCannotLosePendingExpiryIdentity",serial replacementRefused==counter "3" && ((current replacementRefused).notifications.outcome |> Maybe.map .expired)==Just True)
            ,("ExactNativeExpiryReasonWithoutIntermediateObservation",serial (step (Desktop.Incoming (E.object [("protocolVersion",E.int 3),("kind",E.string "notification-outcome"),("binding",bound),("requestId",E.string (UInt64.string (request pending))),("status",E.string "Refused"),("reason",E.string "expired"),("snapshot",snapshot "2" [entry "2" "live",entry "3" "live"])])) pending)==counter "1")
            ,("RepeatedMatchedRefusalSilent",serial (step (Desktop.Incoming refusal) refused)==serial refused)
            ,("ForeignRefusalCannotSettle",step (Desktop.Incoming (receipt foreign (request pending) (snapshot "2" [entry "1" "expired",entry "2" "live"]) "Refused")) pendingExpired==pendingExpired)
            ,("ExpiryAndRefusalDoNotRequestFocus",noFocus expiryEffects && noFocus refusalEffects)
            ,("DndSuppressesExpiryAndRefusal",serial silent==UInt64.zero && serial silentRefused==UInt64.zero)
            ,("LeavingRetiredControlReleasesPlaceholder",controlValue id cleared==E.null && Notifications.focusedIdentity (current cleared).notifications==Nothing)
            ,("ForeignOutputCannotSupplyFocus",renderer "2" (focusAction id ready) ready==ready)
            ,("StalePublicationCannotSupplyFocus",renderer "1" (focusAction id ready) focused==focused)]
    in E.object [("checks",E.object (List.map (\(name,passed)->(name,E.bool passed)) checks)),("readyFrame",Outputs.frame ready),("focusedFrame",Outputs.frame focused),("pendingFrame",Outputs.frame pending),("expiredFrame",Outputs.frame expired),("pendingExpiredFrame",Outputs.frame pendingExpired),("refusedFrame",Outputs.frame refused),("clearedFrame",Outputs.frame cleared)]
main = Platform.worker {init=\()->((),outgoing result),update=\_ model->(model,Cmd.none),subscriptions=\_->Sub.none}
