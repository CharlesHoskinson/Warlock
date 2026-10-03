module pin_focus {
 type Event=Begin|Invoke|ChangeCore|ChangeSeat|Observe|Finish|Refocus|Retry
 type State={active:bool,invoked:bool,coreSame:bool,seatSame:bool,observed:bool,complete:bool,partial:bool,repair:int,retry:int}
 var s:State
 action init=s'={active:false,invoked:false,coreSame:true,seatSame:true,observed:false,complete:false,partial:false,repair:0,retry:0}
 action fire(e:Event):bool={s'=match e{
 |Begin=>if(not(s.active)){...s,active:true,invoked:false,coreSame:true,seatSame:true,observed:false,complete:false,partial:false}else s
 |Invoke=>if(s.active and s.coreSame and s.seatSame){...s,invoked:true,observed:false,complete:false}else s
 |ChangeCore=>{...s,coreSame:false,observed:false,complete:false,partial:s.invoked}
 |ChangeSeat=>{...s,seatSame:false,observed:false,complete:false,partial:s.invoked}
 |Observe=>{...s,observed:s.active and s.coreSame and s.seatSame,complete:false}
 |Finish=>{...s,active:false,complete:s.active and s.observed and s.coreSame and s.seatSame,partial:s.invoked and not(s.active and s.observed and s.coreSame and s.seatSame)}
 |Refocus=>s
 |Retry=>s
 }}
 val allProps=all{s.repair==0,s.retry==0,s.complete implies s.coreSame and s.seatSame and s.observed,s.invoked and(not(s.coreSame)or not(s.seatSame))implies s.partial}
 action step={nondet e=Set(Begin,Invoke,ChangeCore,ChangeSeat,Observe,Finish,Refocus,Retry).oneOf();fire(e)}
 action check(v:bool):bool=all{assert(v),s'=s}
 run exactBothRoutesCompleteTest=init.then(fire(Begin)).then(fire(Invoke)).then(fire(Observe)).then(fire(Finish)).then(check(s.complete and not(s.partial)))
 run changedCoreRefusesPartialTest=init.then(fire(Begin)).then(fire(Invoke)).then(fire(ChangeCore)).then(fire(Observe)).then(fire(Finish)).then(check(not(s.complete)and s.partial))
 run sameCoreWrongSeatRefusesTest=init.then(fire(Begin)).then(fire(Invoke)).then(fire(ChangeSeat)).then(fire(Observe)).then(fire(Finish)).then(check(s.coreSame and not(s.complete)and s.partial))
 run noObservationNoCompleteTest=init.then(fire(Begin)).then(fire(Invoke)).then(fire(Finish)).then(check(not(s.complete)and s.partial))
 run noRefocusOrRetryTest=init.then(fire(Begin)).then(fire(Invoke)).then(fire(ChangeSeat)).then(fire(Refocus)).then(fire(Retry)).then(check(s.repair==0 and s.retry==0 and not(s.seatSame)))
 run changedBeforeCallNoNativeAuthorityTest=init.then(fire(Begin)).then(fire(ChangeSeat)).then(fire(Invoke)).then(check(not(s.invoked)))
 run duplicateBeginCannotRebaselineTest=init.then(fire(Begin)).then(fire(ChangeSeat)).then(fire(Begin)).then(fire(Invoke)).then(check(not(s.invoked)and not(s.seatSame)))
}
