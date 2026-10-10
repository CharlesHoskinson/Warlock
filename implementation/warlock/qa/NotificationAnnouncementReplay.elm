port module NotificationAnnouncementReplay exposing (main)

import Desktop
import Json.Decode as D
import Json.Encode as E
import Notifications
import OutputController as Outputs
import Platform
import Surface
import SurfaceController as Controller
import UInt64

port outgoing : E.Value -> Cmd msg
counter value = D.decodeValue UInt64.decoder (E.string value) |> Result.withDefault UInt64.zero
bound = E.object [("lifetime",E.string "1"),("session",E.string "1"),("frontend",E.string "1")]
field name raw = D.decodeValue (D.field name D.value) raw |> Result.withDefault E.null
serial root = D.decodeValue (D.field "announcement" (D.field "sequence" UInt64.decoder)) (Outputs.frame root) |> Result.withDefault UInt64.zero
interrupt root = D.decodeValue (D.field "announcement" (D.field "interrupt" D.bool)) (Outputs.frame root) |> Result.withDefault False
current root = Controller.desktop (Outputs.controller root)
step message root = Outputs.update (Outputs.Interaction message) root |> Tuple.first
scoped make root = Desktop.capture (current root) |> Maybe.map (\stamp -> step (make stamp) root) |> Maybe.withDefault root
scope id = E.object [("id",E.string id),("generation",E.string "1")]
topology = E.object [("viewProtocol",E.int 1),("kind",E.string "view-topology"),("revision",E.string "1"),("views",E.list scope ["1","2"])]
attached = E.object [("protocolVersion",E.int 3),("kind",E.string "attached"),("binding",bound)]
entry id urgency = E.object [("id",E.string id),("incarnation",E.string id),("producer",E.string ":1.7"),("app",E.string "Calendar"),("summary",E.string ("Meeting "++id)),("body",E.string "Details"),("state",E.string "live"),("actions",E.list identity []),("urgency",E.int urgency)]
snapshot revision entries = E.object [("service",E.string "9"),("revision",E.string revision),("available",E.bool True),("reason",E.string ""),("entries",E.list identity entries)]
update value = E.object [("protocolVersion",E.int 3),("kind",E.string "notification-update"),("binding",bound),("snapshot",value)]
observe revision entries root = step (Desktop.Incoming (update (snapshot revision entries))) root
start = Outputs.update (Outputs.Topology topology) Outputs.initial |> Tuple.first |> step (Desktop.Incoming attached)
ready = observe "1" [] start
ordinary = observe "2" [entry "1" 1] ready
repeat = observe "2" [entry "1" 1] ordinary
opened = scoped Desktop.OpenNotifications ordinary
loaded = step (Desktop.Incoming (E.object [("protocolVersion",E.int 3),("kind",E.string "notification-snapshot"),("binding",bound),("requestId",E.string ((current opened).notificationsExpected |> Maybe.map UInt64.string |> Maybe.withDefault "0")),("snapshot",snapshot "2" [entry "1" 1])])) opened
policy dnd opted = {doNotDisturb=dnd,interruptCritical=opted}
configured dnd opted = scoped (\stamp -> Desktop.ConfigureNotificationPolicy stamp (policy dnd opted))
dndRoot = configured True False loaded
suppressed = observe "3" [entry "2" 1,entry "1" 1] dndRoot
unsilenced = configured False False suppressed
normalCritical = observe "4" [entry "3" 2,entry "2" 1,entry "1" 1] unsilenced
consenting = configured False True normalCritical
urgent = observe "5" [entry "4" 2,entry "3" 2,entry "2" 1,entry "1" 1] consenting
ordinaryWithConsent = observe "6" [entry "5" 1,entry "4" 2,entry "3" 2,entry "2" 1,entry "1" 1] urgent
silentCritical = observe "6" [entry "5" 2,entry "4" 2,entry "3" 2,entry "2" 1,entry "1" 1] (configured True True urgent)
batch = observe "2" [entry "1" 1,entry "2" 1,entry "3" 1,entry "4" 1] ready
noFocus effects = List.all (\effect -> case effect of
    Controller.DesktopEffect (Desktop.Focus _) -> False
    _ -> True) effects
result =
    let (_,arrivalEffects)=Outputs.update (Outputs.Interaction (Desktop.Incoming (update (snapshot "2" [entry "1" 1])))) ready
        (_,criticalEffects)=Outputs.update (Outputs.Interaction (Desktop.Incoming (update (snapshot "5" [entry "4" 2,entry "3" 2,entry "2" 1,entry "1" 1])))) consenting
        baseline=observe "1" [entry "1" 1] start
        checks = [("ordinaryIsPolite",serial ordinary==counter "1" && not (interrupt ordinary))
            ,("exactRepeatSilent",repeat==ordinary)
            ,("dndKeepsHistoryWithoutNewSerial",serial suppressed==serial ordinary && ((current suppressed).notifications.snapshot |> Maybe.map (.entries >> List.length))==Just 2)
            ,("dndOffCannotReplayHistory",serial unsilenced==serial suppressed)
            ,("criticalWithoutConsentIsPolite",not (interrupt normalCritical) && serial normalCritical==counter "2")
            ,("consentCannotReplayPastCritical",serial consenting==serial normalCritical && not (interrupt consenting))
            ,("optedCriticalIsAssertive",interrupt urgent && serial urgent==counter "3")
            ,("consentDoesNotEscalateOrdinary",not (interrupt ordinaryWithConsent) && serial ordinaryWithConsent==counter "4")
            ,("dndSilencesOptedCritical",serial silentCritical==serial urgent && ((current silentCritical).notifications.snapshot |> Maybe.map (.entries >> List.length))==Just 5)
            ,("arrivalAndCriticalNeverRequestFocus",noFocus arrivalEffects && noFocus criticalEffects)
            ,("initialHistoryIsNotArrival",serial baseline==UInt64.zero)
            ,("batchRetainsEveryArrivalIdentity",D.decodeValue (D.field "announcement" (D.field "correlation" D.string |> D.andThen (\value -> D.decodeString (D.field "identity" (D.field "incarnations" (D.list D.string))) value |> Result.map D.succeed |> Result.withDefault (D.fail "Correlation")))) (Outputs.frame batch)==Ok ["1","2","3","4"])
            ,("strictUrgencyRejectsBoolean",D.decodeValue Notifications.decoder (snapshot "2" [E.object [("id",E.string "1"),("incarnation",E.string "1"),("producer",E.string ":1.7"),("app",E.string "X"),("summary",E.string "Y"),("body",E.string ""),("state",E.string "live"),("actions",E.list identity []),("urgency",E.bool True)]]) |> Result.toMaybe |> (==) Nothing)
            ,("policyControlsAreIntegrated",List.all (\id -> List.any (\control -> control.id==id && control.enabled && control.message/=Nothing) (Surface.controls (current loaded))) ["notifications:dnd","notifications:critical-interrupt"])]
    in E.object [("checks",E.object (List.map (\(name,passed) -> (name,E.bool passed)) checks)),("notificationFrame",Outputs.frame loaded),("dndFrame",Outputs.frame suppressed),("politeFrame",Outputs.frame normalCritical),("urgentFrame",Outputs.frame urgent),("ordinaryWithConsentFrame",Outputs.frame ordinaryWithConsent)]
main = Platform.worker {init=\() -> ((),outgoing result),update=\_ model -> (model,Cmd.none),subscriptions=\_ -> Sub.none}
