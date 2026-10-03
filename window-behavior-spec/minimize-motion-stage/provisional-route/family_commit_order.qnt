/** A native relation snapshot certifies membership, not future workspace
 * state. Re-read exact member identities under the callback lock and reserve
 * the entire accepted family before slow preparation. An older restore may
 * finish before acceptance, but cannot commit after its member is reserved.
 */
module family_commit_order {
 type Observation={identity:int,epoch:int}
 type Event=Snapshot(Observation) | OldOwnerRestore | Accept(Observation) | Commit((int,int)) | Reuse
 type State={identity:int,epoch:int,snapshotIdentity:int,snapshotEpoch:int,snapshotOwnerMin:bool,ownerMin:bool,childMin:bool,nestedMin:bool,accepted:bool,plans:Set[int],oldAuthority:bool,stale:bool,beforeOwner:bool,beforeChild:bool,beforeNested:bool}
 var s:State
 action init=s'={identity:1,epoch:1,snapshotIdentity:0,snapshotEpoch:0,snapshotOwnerMin:false,ownerMin:true,childMin:true,nestedMin:true,accepted:false,plans:Set(),oldAuthority:true,stale:false,beforeOwner:true,beforeChild:true,beforeNested:true}
 action fire(e:Event):bool={
  val b={...s,stale:false,beforeOwner:s.ownerMin,beforeChild:s.childMin,beforeNested:s.nestedMin}
  s'=match e {
   | Snapshot(o)=>if(o.identity!=s.identity or o.epoch!=s.epoch){...b,stale:true} else {...b,snapshotIdentity:o.identity,snapshotEpoch:o.epoch,snapshotOwnerMin:s.ownerMin}
   | OldOwnerRestore=>if(not(s.oldAuthority)){...b,stale:true} else {...b,ownerMin:false}
   | Accept(o)=>if(o.identity!=s.identity or o.epoch!=s.epoch or s.snapshotIdentity!=s.identity or s.snapshotEpoch!=s.epoch){...b,stale:true}
      else {...b,accepted:true,oldAuthority:false,plans:if(s.ownerMin)Set(1,2) else Set(0,1,2)}
   | Commit(pair)=>if(not(s.accepted) or pair._2!=s.epoch or not(s.plans.contains(pair._1))){...b,stale:true}
      else {...b,plans:s.plans.exclude(Set(pair._1)),ownerMin:if(pair._1==0)true else s.ownerMin,childMin:if(pair._1==1)true else s.childMin,nestedMin:if(pair._1==2)true else s.nestedMin}
   | Reuse=>{...b,identity:s.identity+1,epoch:s.epoch+1,accepted:false,plans:Set(),oldAuthority:false,ownerMin:false,childMin:false,nestedMin:false,snapshotIdentity:0,snapshotEpoch:0}
  }
 }
 val acceptedFamilyHasWorkOrFreshEndpoint=s.accepted implies ((s.ownerMin or s.plans.contains(0)) and (s.childMin or s.plans.contains(1)) and (s.nestedMin or s.plans.contains(2)))
 val oldCallbacksHaveNoAuthority=s.accepted implies not(s.oldAuthority)
 val staleCannotCommit=s.stale implies (s.ownerMin==s.beforeOwner and s.childMin==s.beforeChild and s.nestedMin==s.beforeNested)
 val allProps=acceptedFamilyHasWorkOrFreshEndpoint and oldCallbacksHaveNoAuthority and staleCannotCommit
 action step={nondet e=Set(Snapshot({identity:s.identity,epoch:s.epoch}),Snapshot({identity:s.identity-1,epoch:s.epoch}),OldOwnerRestore,Accept({identity:s.identity,epoch:s.epoch}),Accept({identity:s.identity-1,epoch:s.epoch}),Commit((0,s.epoch)),Commit((1,s.epoch)),Commit((2,s.epoch)),Commit((0,s.epoch-1)),Reuse).oneOf();fire(e)}
}
