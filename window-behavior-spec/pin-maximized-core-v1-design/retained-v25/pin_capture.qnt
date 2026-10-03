module pin_capture {
 type Event=Begin(int)|Read({owner:int,generation:int})|BeforeChange|AfterChange|PeerFailure|Malformed|Complete|Mutation
 type State={target:int,active:bool,authority:bool,received:bool,owner:int,generation:int,complete:bool,writes:int}
 var s:State
 action init=s'={target:0,active:false,authority:true,received:false,owner:0,generation:0,complete:false,writes:0}
 action fire(e:Event):bool={s'=match e{
 |Begin(w)=>if(not(s.active)){...s,target:w,active:true,received:false,complete:false}else s
 |Read(r)=>if(s.active and s.authority and r.owner==s.target and r.generation>0){...s,received:true,owner:r.owner,generation:r.generation}else{...s,received:false,complete:false}
 |BeforeChange=>{...s,authority:false,complete:false}
 |AfterChange=>{...s,authority:false,complete:false}
 |PeerFailure=>{...s,authority:false,complete:false}
 |Malformed=>{...s,received:false,complete:false}
 |Complete=>{...s,complete:s.active and s.authority and s.received and s.owner==s.target and s.generation>0,active:false}
 |Mutation=>s
 }}
 val allProps=all{s.writes==0,s.complete implies s.authority and s.received and s.owner==s.target and s.generation>0}
 action step={nondet w=Set(1,2).oneOf();nondet g=Set(0,1,2).oneOf();nondet e=Set(Begin(w),Read({owner:w,generation:g}),BeforeChange,AfterChange,PeerFailure,Malformed,Complete,Mutation).oneOf();fire(e)}
 action check(v:bool):bool=all{assert(v),s'=s}
 run exactReadTest=init.then(fire(Begin(1))).then(fire(Read({owner:1,generation:1}))).then(fire(Complete)).then(check(s.complete and s.writes==0))
 run wrongOwnerRefusedTest=init.then(fire(Begin(1))).then(fire(Read({owner:2,generation:1}))).then(fire(Complete)).then(check(not(s.complete)))
 run zeroGenerationRefusedTest=init.then(fire(Begin(1))).then(fire(Read({owner:1,generation:0}))).then(fire(Complete)).then(check(not(s.complete)))
 run changedBeforeReadTest=init.then(fire(Begin(1))).then(fire(BeforeChange)).then(fire(Read({owner:1,generation:1}))).then(fire(Complete)).then(check(not(s.complete)))
 run changedAfterReadTest=init.then(fire(Begin(1))).then(fire(Read({owner:1,generation:1}))).then(fire(AfterChange)).then(fire(Complete)).then(check(not(s.complete)))
 run wrongPeerRefusedTest=init.then(fire(Begin(1))).then(fire(PeerFailure)).then(fire(Read({owner:1,generation:1}))).then(fire(Complete)).then(check(not(s.complete)))
 run malformedNoAuthorityTest=init.then(fire(Begin(1))).then(fire(Read({owner:1,generation:1}))).then(fire(Malformed)).then(fire(Complete)).then(check(not(s.complete)))
}
