// ELM-UI-010 arrival/DND/urgency; one Elm policy actor over admitted facts.
// Native hint validation and single-owner transport have separate concrete checks.
// Opaque bounded identity, atomic observation; no speech/timing/restart proof.
module notificationAnnouncements {
  type State = {next: int, history: Set[int], dnd: bool, optIn: bool,
    counts: int -> int, permitted: int -> bool, interrupt: int -> bool,
    critical: int -> bool, consent: int -> bool, sequence: int, focus: int, repeats: int, baselined: bool}
  var s: State
  action init = s'={next:0,history:Set(),dnd:false,optIn:false,
    counts:Set(1,2,3,4,5,6).mapBy(_=>0),permitted:Set(1,2,3,4,5,6).mapBy(_=>false),
    interrupt:Set(1,2,3,4,5,6).mapBy(_=>false),critical:Set(1,2,3,4,5,6).mapBy(_=>false),
    consent:Set(1,2,3,4,5,6).mapBy(_=>false),sequence:0,focus:7,repeats:0,baselined:false}
  pure def canArrive(state: State): bool = state.next<6
  pure def arrived(state: State, urgent: bool): State = {
    val id=state.next+1
    val allowed=not(state.dnd)
    {...state,next:id,history:state.history.union(Set(id)),
      counts:state.counts.set(id,if (allowed) 1 else 0),
      permitted:state.permitted.set(id,allowed),
      critical:state.critical.set(id,urgent),consent:state.consent.set(id,state.optIn),
      interrupt:state.interrupt.set(id,allowed and urgent and state.optIn),
      sequence:state.sequence+(if (allowed) 1 else 0)}
  }
  action arrival(urgent: bool): bool = all {canArrive(s),s'=arrived(s,urgent)}
  val arrivalWitness = s.history.size()>0
  val safety = s.focus==7 and s.counts.keys().forall(id=>s.counts.get(id)<=1 and (s.counts.get(id)==1 implies s.permitted.get(id)) and (s.interrupt.get(id) implies s.critical.get(id) and s.permitted.get(id) and s.consent.get(id)))
  action dnd(selected: bool): bool = all {selected!=s.dnd,s'={...s,dnd:selected}}
  action optIn(selected: bool): bool = all {selected!=s.optIn,s'={...s,optIn:selected}}
  // An observed receipt repeat changes only its ghost observation counter.
  action duplicateObservation = all {s.next>0,s'={...s,repeats:s.repeats+1}}
  action baseline = all {s.next==0,not(s.baselined),s'={...s,next:1,history:Set(1),baselined:true}}
  val suppressedWitness = s.history.exists(id=>not(s.permitted.get(id)))
  val politeCriticalWitness = s.history.exists(id=>s.critical.get(id) and s.counts.get(id)==1 and not(s.interrupt.get(id)))
  val interruptWitness = s.history.exists(id=>s.interrupt.get(id))
  val dndWitness = s.dnd
  val optInWitness = s.optIn
  val repeatWitness = s.repeats>0
  val baselineWitness = s.baselined
  action step = any {arrival(false),arrival(true),dnd(true),dnd(false),optIn(true),optIn(false),duplicateObservation,baseline}
}
