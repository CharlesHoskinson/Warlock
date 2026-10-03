/** Family actions use a successful fresh native relationship graph, never a
 * failed enrichment's singleton/PID guess. Rejected preparation settles the
 * previous accepted member intent; it cannot accept primary-only new intent.
 */
module family_scope {
 type Observation = {identity:int,epoch:int}
 type Event = Reserve | RelationFailure | FreshFamily(Observation) | GenuineDetached(Observation) | Commit(int) | FailValidation | CloseReuse | Reload
 type State = {live:bool,id:int,captured:int,epoch:int,acceptedEpoch:int,scope:Set[int],reserved:bool,queryOk:bool,
  intent:bool,previousIntent:bool,primaryMin:bool,peerMin:bool,rejected:bool,stale:bool,beforePrimary:bool,beforePeer:bool,queryFailed:bool,beforeScope:Set[int],beforeAccepted:int,acceptedEvidence:str,evidenceEpoch:int,evidenceIdentity:int}
 var s:State
 action init=s'={live:true,id:1,captured:1,epoch:1,acceptedEpoch:1,scope:Set(0,1),reserved:false,queryOk:true,
  intent:false,previousIntent:false,primaryMin:true,peerMin:true,rejected:false,stale:false,beforePrimary:true,beforePeer:true,queryFailed:false,beforeScope:Set(0,1),beforeAccepted:1,acceptedEvidence:"family",evidenceEpoch:1,evidenceIdentity:1}
 action fire(e:Event):bool={
  val b={...s,stale:false,beforePrimary:s.primaryMin,beforePeer:s.peerMin,queryFailed:false,beforeScope:s.scope,beforeAccepted:s.acceptedEpoch}
  s'=match e {
   | Reserve => if(not(s.live))b else {...b,captured:s.id,epoch:s.epoch+1,reserved:true,queryOk:false,previousIntent:s.intent,intent:not(s.intent),rejected:false}
   | RelationFailure => if(not(s.reserved))b else {...b,queryOk:false,queryFailed:true}
   | FreshFamily(obs) => if(not(s.reserved) or not(s.live) or s.id!=s.captured or obs.identity!=s.id or obs.epoch!=s.epoch) {...b,stale:true} else {...b,queryOk:true,reserved:false,scope:Set(0,1),acceptedEpoch:s.epoch,acceptedEvidence:"family",evidenceEpoch:s.epoch,evidenceIdentity:s.id}
   | GenuineDetached(obs) => if(not(s.reserved) or not(s.live) or s.id!=s.captured or obs.identity!=s.id or obs.epoch!=s.epoch) {...b,stale:true} else {...b,queryOk:true,reserved:false,scope:Set(0),acceptedEpoch:s.epoch,acceptedEvidence:"detached",evidenceEpoch:s.epoch,evidenceIdentity:s.id}
   | Commit(t) => if(t!=s.acceptedEpoch or s.reserved or not(s.queryOk) or not(s.live) or s.id!=s.captured) {...b,stale:true} else
       {...b,primaryMin:s.intent,peerMin:if(s.scope.contains(1))s.intent else s.peerMin}
   | FailValidation => if(not(s.reserved))b else {...b,reserved:false,rejected:true,intent:s.previousIntent,queryOk:s.evidenceEpoch>0 and s.evidenceIdentity==s.id,
       primaryMin:if(s.live and s.id==s.captured and s.evidenceEpoch>0 and s.evidenceIdentity==s.id)s.previousIntent else s.primaryMin}
   | CloseReuse => {...b,live:true,id:s.id+1,primaryMin:false,epoch:s.epoch+1,reserved:false,queryOk:false,intent:false,previousIntent:false,scope:Set(),acceptedEpoch:0,acceptedEvidence:"",evidenceEpoch:0,evidenceIdentity:s.id+1}
   | Reload => {...b,reserved:false,primaryMin:if(s.live and s.id==s.captured)s.previousIntent else s.primaryMin}
  }
 }
 val staleCannotCommit=s.stale implies (s.primaryMin==s.beforePrimary and s.peerMin==s.beforePeer)
 val queryFailurePreservesAcceptedScope=s.queryFailed implies (s.scope==s.beforeScope and s.acceptedEpoch==s.beforeAccepted)
 val reservedHasNoNewNativeAuthority=s.reserved implies s.acceptedEpoch<s.epoch
 val acceptedScopeHasCurrentNativeEvidence=(s.queryOk and not(s.reserved) and s.id==s.captured) implies (s.evidenceEpoch==s.acceptedEpoch and s.evidenceIdentity==s.id and (s.scope==Set(0) implies s.acceptedEvidence=="detached"))
 val allProps=acceptedScopeHasCurrentNativeEvidence and queryFailurePreservesAcceptedScope and staleCannotCommit and reservedHasNoNewNativeAuthority
 action step={nondet e=Set(Reserve,RelationFailure,FreshFamily({identity:s.id,epoch:s.epoch}),FreshFamily({identity:s.id,epoch:s.epoch-1}),GenuineDetached({identity:s.id,epoch:s.epoch}),GenuineDetached({identity:s.id-1,epoch:s.epoch}),Commit(s.epoch),Commit(s.epoch-1),FailValidation,CloseReuse,Reload).oneOf();fire(e)}
}
