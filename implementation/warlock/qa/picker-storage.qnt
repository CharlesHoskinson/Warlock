module pickerStorage {
  // UI-016 native storage refinement. A job abstracts the full authenticated
  // peer/binding/incarnation/request/context. One slot owns one sealed backing.
  // Original renderer peak/byte bound is conservative; pixels, clocks and AT
  // are outside this model, not inferred from a descriptor or reservation.
  type State = {held:Set[int], sealed:Set[int], exported:Set[int], mapped:Set[int], issued:Set[int], retired:Set[int], revoked:bool, reply:int, refused:bool, deliveries:int}
  val empty:State={held:Set(),sealed:Set(),exported:Set(),mapped:Set(),issued:Set(),retired:Set(),revoked:false,reply:0,refused:false,deliveries:0}
  var s:State
  action init=s'=empty
  action idle=s'=s
  pure def reserve(st:State, job:int):State =
    if (not(job.in(Set(1,2,3))) or st.revoked or job.in(st.held.union(st.retired)) or st.held.size()>=2) {...st, reply:0,refused:true}
    else {...st, held:st.held.union(Set(job)),reply:0,refused:false}
  pure def seal(st:State, job:int):State =
    if (job.in(st.held) and not(st.revoked)) {...st, sealed:st.sealed.union(Set(job)),reply:0,refused:false} else {...st, reply:0,refused:true}
  pure def offer(st:State, owner:int, requested:int):State =
    if (owner==requested and owner.in(st.sealed) and not(owner.in(st.issued)) and not(st.revoked))
      {...st, exported:st.exported.union(Set(owner)),mapped:st.mapped.union(Set(owner)),issued:st.issued.union(Set(owner)),deliveries:st.deliveries+1,reply:owner,refused:false}
    else {...st, reply:0,refused:true}
  pure def closeMap(st:State, job:int):State = {...st, mapped:st.mapped.exclude(Set(job)),reply:0,refused:false}
  pure def release(st:State, owner:int, requested:int):State =
    if (owner==requested and owner.in(st.exported) and not(owner.in(st.mapped))) {...st, exported:st.exported.exclude(Set(owner)),reply:0,refused:false} else {...st, reply:0,refused:true}
  pure def retire(st:State, owner:int, requested:int):State =
    if (owner==requested and owner.in(st.held) and not(owner.in(st.exported.union(st.mapped))))
      {...st, held:st.held.exclude(Set(owner)),sealed:st.sealed.exclude(Set(owner)),retired:st.retired.union(Set(owner)),reply:0,refused:false}
    else {...st, reply:0,refused:true}
  action allocate(job:int):bool=s'=reserve(s,job)
  action finish(job:int):bool=s'=seal(s,job)
  action offerDescriptor(job:int,requested:int):bool=s'=offer(s,job,requested)
  action close(job:int):bool=s'=closeMap(s,job)
  action releaseExport(job:int,requested:int):bool=s'=release(s,job,requested)
  action retireProducer(job:int,requested:int):bool=s'=retire(s,job,requested)
  // Native capture and consumer close/release are synchronous sequences on
  // their owning thread. Macros add legal reachability paths; individual steps
  // remain available for failure/interleaving exploration and named tests.
  action captureFinished(job:int):bool=all{not(job.in(s.held.union(s.retired))),s'=seal(reserve(s,job),job)}
  action closeAndRelease(job:int):bool=s'=release(closeMap(s,job),job,job)
  action revoke=s'={...s, revoked:true,reply:0,refused:false}
  action step={nondet job=Set(1,2,3).oneOf();nondet requested=Set(1,2,3,4).oneOf();any{allocate(job),finish(job),captureFinished(job),offerDescriptor(job,job),offerDescriptor(job,requested),close(job),closeAndRelease(job),releaseExport(job,requested),retireProducer(job,requested),revoke,idle}}
  val twoFamiliesWitness=s.exported==Set(1,2) and s.held==Set(1,2)
  val retainedAfterReleaseWitness=s.held.size()>0 and s.exported==Set() and s.issued.size()>0
  val capacityRefusalWitness=s.held.size()==2 and s.refused
  val safety=s.held.size()<=2 and s.held.size()*64<=128 and s.sealed.subseteq(s.held) and s.exported.subseteq(s.sealed) and s.mapped.subseteq(s.exported) and s.exported.subseteq(s.issued) and s.retired.intersect(s.held)==Set() and s.deliveries==s.issued.size() and (s.reply==0 or (s.reply.in(s.exported) and not(s.revoked)))
}
