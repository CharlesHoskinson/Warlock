module chord {
 type Event=Plan(bool)|Connect(bool)|MapReady(bool)|Press(int)|Release(int)|Modifiers(Set[int])|Change|Error|Finish|Retry
 type State={planned:bool,connected:bool,mapped:bool,live:bool,failed:bool,held:Set[int],mods:Set[int],presses:int,releases:int,complete:bool,retry:int}
 var s:State
 pure val keySet=Set(1,2,3)
 action init=s'={planned:false,connected:false,mapped:false,live:true,failed:false,held:Set(),mods:Set(),presses:0,releases:0,complete:false,retry:0}
 val ready=s.planned and s.connected and s.mapped and s.live and not(s.failed)
 action fire(e:Event):bool={s'=match e{
 |Plan(ok)=>{...s,planned:s.planned or(ok and not(s.connected)and s.presses==0),failed:s.failed or not(ok)or s.connected or s.presses>0}
 |Connect(ok)=>{...s,connected:s.connected or(s.planned and s.live and not(s.failed)and ok),failed:s.failed or not(s.planned and ok)}
 |MapReady(ok)=>{...s,mapped:s.mapped or(s.planned and s.connected and s.live and not(s.failed)and ok),failed:s.failed or not(s.planned and s.connected and ok)}
 |Press(k)=>if(ready and keySet.contains(k)and not(s.held.contains(k))){...s,held:s.held.union(Set(k)),presses:s.presses+1,complete:false}else{...s,failed:true,complete:false}
 |Release(k)=>if(ready and s.held.contains(k)){...s,held:s.held.exclude(Set(k)),releases:s.releases+1,complete:false}else{...s,failed:true,complete:false}
 |Modifiers(v)=>if(ready and v.subseteq(Set(1,2))and v==s.held.intersect(Set(1,2))){...s,mods:v,complete:false}else{...s,failed:true,complete:false}
 |Change=>{...s,live:false,failed:true,complete:false}
 |Error=>{...s,failed:true,complete:false}
 |Finish=>{...s,complete:ready and s.held==Set()and s.mods==Set()and s.presses>0 and s.presses==s.releases}
 |Retry=>s
 }}
 val allProps=all{s.releases<=s.presses,s.presses-s.releases==s.held.size(),s.presses>0 implies s.planned and s.connected and s.mapped,s.complete implies s.live and not(s.failed)and s.held==Set()and s.mods==Set()and s.presses==s.releases,s.retry==0}
 action step={nondet k=keySet.oneOf();nondet b=Set(true,false).oneOf();nondet e=Set(Plan(b),Connect(b),MapReady(b),Press(k),Release(k),Modifiers(Set()),Modifiers(Set(1)),Modifiers(Set(1,2)),Change,Error,Finish,Retry).oneOf();fire(e)}
 action check(v:bool):bool=all{assert(v),s'=s}
 action setup=fire(Plan(true)).then(fire(Connect(true))).then(fire(MapReady(true)))
 run heldMetaThroughTargetTest=init.then(setup).then(fire(Press(1))).then(fire(Modifiers(Set(1)))).then(fire(Press(3))).then(check(s.held==Set(1,3)and s.mods==Set(1)))
 run heldMetaControlThroughTargetTest=init.then(setup).then(fire(Press(1))).then(fire(Modifiers(Set(1)))).then(fire(Press(2))).then(fire(Modifiers(Set(1,2)))).then(fire(Press(3))).then(fire(Release(3))).then(fire(Release(2))).then(fire(Modifiers(Set(1)))).then(fire(Release(1))).then(fire(Modifiers(Set()))).then(fire(Finish)).then(check(s.complete))
 run noPlanNoKeyTest=init.then(fire(Press(1))).then(check(s.presses==0))
 run wrongPeerNoKeyTest=init.then(fire(Plan(true))).then(fire(Connect(false))).then(fire(Press(1))).then(check(s.presses==0))
 run errorWhileHeldNoReleaseRequestTest=init.then(setup).then(fire(Press(1))).then(fire(Error)).then(fire(Release(1))).then(check(s.held==Set(1)and s.releases==0 and not(s.complete)))
 run changedLifetimeNoModifierRequestTest=init.then(setup).then(fire(Press(1))).then(fire(Change)).then(fire(Modifiers(Set(1)))).then(check(s.mods==Set()and not(s.complete)))
 run nonzeroModsNoNormalCompletionTest=init.then(setup).then(fire(Press(1))).then(fire(Modifiers(Set(1)))).then(fire(Release(1))).then(fire(Finish)).then(check(not(s.complete)))
}
