// ELM-UI-010 selected refusal scenarios; WARLOCK-DL-011.
// One integrated Elm policy plus scoped native/renderer delivery state.
// Bounded request/serial identities are opaque. No pixel/AT delivery proof,
// timing, process recovery or permitted notification source is represented.
module announcementOwner {
  type State = { next: int, pending: int -> bool, sequence: int,
    publication: int, owner: int, popup: bool, frontier: int,
    delivered: int -> int, routed: int -> int, focus: int,
    repeats: int, visualNotifications: int }
  var s: State
  action init = s' = {next:0,pending:Set(1,2,3).mapBy(_=>false),sequence:0,
    publication:1,owner:1,popup:false,frontier:0,
    delivered:Set(1,2,3,4,5,6).mapBy(_=>0),routed:Set(1,2,3,4,5,6).mapBy(_=>0),
    focus:7,repeats:0,visualNotifications:0}
  pure def canRequest(state: State, kind: int): bool = state.next<6 and not(state.pending.get(kind))
  pure def requested(state: State, kind: int): State = {...state,next:state.next+1,pending:state.pending.set(kind,true),publication:state.publication+1}
  action request(kind: int): bool = all {canRequest(s,kind),s'=requested(s,kind)}
  pure def canRefuse(state: State, kind: int): bool = state.pending.get(kind) and state.sequence<6
  pure def refused(state: State, kind: int): State = {...state,pending:state.pending.set(kind,false),sequence:state.sequence+1,publication:state.publication+1}
  action refuse(kind: int): bool = all {canRefuse(s,kind),s'=refused(s,kind)}
  pure def route(state: State): int = state.owner+(if (state.popup) 10 else 0)
  pure def canPublish(state: State, recipient: int, publication: int): bool = state.owner>0 and state.sequence>state.frontier and recipient==route(state) and publication==state.publication
  pure def published(state: State, recipient: int): State = {...state,frontier:state.sequence,delivered:state.delivered.setBy(state.sequence,n=>n+1),routed:state.routed.set(state.sequence,recipient)}
  action publish(recipient: int, publication: int): bool = all {canPublish(s,recipient,publication),s'=published(s,recipient)}
  action choose(owner: int): bool = all {owner.in(Set(0,1,2)),owner!=s.owner,s'={...s,owner:owner,publication:s.publication+1}}
  action popup(open: bool): bool = all {open!=s.popup,s'={...s,popup:open,publication:s.publication+1}}
  // Observation counter is a ghost: repeated input is an actual received event,
  // not a business-state escape hatch for disabled transitions.
  action duplicateReceipt = all {s.sequence>0,not(s.pending.get(1)),s'={...s,repeats:s.repeats+1}}
  action unpermittedNotification = s'={...s,visualNotifications:s.visualNotifications+1,publication:s.publication+1}
  val deliveryWitness = s.frontier>0
  val popupWitness = s.routed.keys().exists(k=>s.routed.get(k)>10)
  val repeatWitness = s.repeats>0
  val ownerChangeWitness = s.owner==2
  val visualNotificationWitness = s.visualNotifications>0
  val refusalWitness = s.sequence>0
  val requestedWitness = s.next>0
  val safety = s.frontier<=s.sequence and s.focus==7 and s.delivered.keys().forall(k=>s.delivered.get(k)<=1)
  action step = any {request(1),request(2),request(3),refuse(1),refuse(2),refuse(3),publish(route(s),s.publication),choose(0),choose(1),choose(2),popup(true),popup(false),duplicateReceipt,unpermittedNotification}
}
