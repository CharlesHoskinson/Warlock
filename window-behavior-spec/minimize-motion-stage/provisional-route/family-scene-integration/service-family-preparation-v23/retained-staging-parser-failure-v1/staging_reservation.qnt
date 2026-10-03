module staging_reservation {
 type Claim={epoch:int,serial:int,material:int}
 type Scan={claim:Claim,ownsLifecycle:bool}
 type State={staging:Set[Claim],pending:Set[Claim],scans:Set[Scan],checked:Set[Claim],active:Set[Claim],quarantined:bool,serial:int,cleanupWaiting:bool,cleanupReturned:bool,releaseRefused:bool,protectedRelease:bool,published:Set[Claim],failed:Set[Claim]}
 type Event=Reserve(int)|Read(Claim)|OldLockedRead(Claim)|Material(Claim,bool)|Commit(Claim)|Abort(Claim)|Release(int)|Dispose|BatchStart|UnknownGroup|GroupClosed
 pure val original={epoch:1,serial:1,material:7}
 pure val wrong={epoch:1,serial:99,material:7}
 pure val initial={staging:Set(),pending:Set(),scans:Set(),checked:Set(),active:Set(),quarantined:false,serial:0,cleanupWaiting:false,cleanupReturned:false,releaseRefused:false,protectedRelease:false,published:Set(),failed:Set()}
 var s:State
 action init=s'=initial
 pure def occupied(x:State,e:int):bool=x.staging.union(x.pending).exists(c=>c.epoch==e)
 pure def protected(x:State,e:int):bool=x.staging.union(x.active).exists(c=>c.epoch==e)
 pure def scanned(x:State,c:Claim):bool=x.scans.exists(r=>r.claim==c)
 pure def stepState(x:State,e:Event):State=match e {
 | Reserve(n)=>if(not(x.quarantined) and x.active.size()==0 and not(occupied(x,n)) and x.pending.size()+x.staging.size()<64){...x,serial:x.serial+1,staging:x.staging.union(Set({epoch:n,serial:x.serial+1,material:7}))}else x
 | Read(c)=>if(x.staging.contains(c) and not(scanned(x,c))){...x,scans:x.scans.union(Set({claim:c,ownsLifecycle:false}))}else x
 | OldLockedRead(c)=>if(x.staging.contains(c) and not(scanned(x,c))){...x,scans:x.scans.union(Set({claim:c,ownsLifecycle:true}))}else x
 | Material(c,ok)=>if(x.staging.contains(c) and scanned(x,c)){...x,scans:x.scans.filter(r=>r.claim!=c),checked:if(ok)x.checked.union(Set(c))else x.checked,failed:if(ok)x.failed else x.failed.union(Set(c))}else x
 | Commit(c)=>if(x.staging.contains(c) and x.checked.contains(c) and not(x.failed.contains(c)) and not(x.quarantined) and x.active.size()==0){...x,staging:x.staging.exclude(Set(c)),pending:x.pending.union(Set(c)),published:x.published.union(Set(c))}else x
 | Abort(c)=>if(x.staging.contains(c) and not(scanned(x,c))){...x,staging:x.staging.exclude(Set(c))}else x
 | Release(n)=>if(protected(x,n)){...x,protectedRelease:true,releaseRefused:true,cleanupReturned:false,cleanupWaiting:false}else if(x.scans.exists(r=>r.ownsLifecycle)){...x,protectedRelease:false,releaseRefused:false,cleanupReturned:false,cleanupWaiting:true}else {...x,protectedRelease:false,releaseRefused:false,cleanupReturned:true,cleanupWaiting:false,pending:x.pending.filter(c=>c.epoch!=n)}
 | Dispose=>{...x,releaseRefused:x.staging.size()>0 or x.pending.size()>0 or x.active.size()>0 or x.quarantined,cleanupReturned:x.staging.size()==0 and x.pending.size()==0 and x.active.size()==0 and not(x.quarantined),cleanupWaiting:false,protectedRelease:false}
 | BatchStart=>if(x.staging.size()==0 and x.pending.size()>0 and x.active.size()==0 and not(x.quarantined)){...x,active:x.pending}else x
 | UnknownGroup=>if(x.active.size()>0){...x,quarantined:true}else x
 | GroupClosed=>if(not(x.quarantined)){...x,active:Set()}else x
 }
 action fire(e:Event):bool=s'=stepState(s,e)
 val allProps=s.pending.size()+s.staging.size()<=64 and s.staging.map(c=>c.epoch).size()==s.staging.size() and s.pending.map(c=>c.epoch).intersect(s.staging.map(c=>c.epoch)).size()==0 and s.published.subseteq(s.checked) and s.published.intersect(s.failed).size()==0 and s.scans.forall(r=>not(r.ownsLifecycle)) and not(s.cleanupWaiting) and (s.protectedRelease implies s.releaseRefused and not(s.cleanupReturned))
 action step={nondet c=s.staging.union(Set(wrong)).oneOf();nondet n=0.to(65).oneOf();nondet e=Set(Reserve(n),Read(c),Read(wrong),Material(c,true),Material(c,false),Material(wrong,true),Commit(c),Commit(wrong),Abort(c),Abort(wrong),Release(c.epoch),Release(99),Dispose,BatchStart,UnknownGroup,GroupClosed).oneOf();fire(e)}
}
