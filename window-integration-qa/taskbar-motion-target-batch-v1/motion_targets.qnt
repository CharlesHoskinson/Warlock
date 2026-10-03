module motion_targets {
 type Event=Request({valid:bool,unique:bool,bounded:bool})|Lookup({actual:bool,complete:bool,stable:bool})|Confirm({epoch:bool,members:bool,outputs:bool})|Commit|Change|Override|SingleQuery
 type State={request:bool,looked:bool,complete:bool,confirmed:bool,committed:bool,current:bool,bulk:int,nativeWrites:int}
 var s:State
 action init=s'={request:false,looked:false,complete:false,confirmed:false,committed:false,current:true,bulk:0,nativeWrites:0}
 action fire(e:Event):bool={s'=match e {
 |Request(v)=>{...s,request:v.valid and v.unique and v.bounded,looked:false,complete:false,confirmed:false,committed:false,current:true,bulk:s.bulk+1}
 |Lookup(v)=>{...s,looked:s.request and s.current and v.actual and v.stable,complete:s.request and s.current and v.actual and v.stable and v.complete,confirmed:false,committed:false}
 |Confirm(v)=>{...s,confirmed:s.current and s.looked and s.complete and v.epoch and v.members and v.outputs,committed:false}
 |Commit=>{...s,committed:s.current and s.request and s.looked and s.complete and s.confirmed}
 |Change=>{...s,current:false,confirmed:false,committed:false}
 |Override=>s
 |SingleQuery=>s
 }}
 val allProps=all{s.nativeWrites==0,s.committed implies s.current and s.request and s.looked and s.complete and s.confirmed}
 action step={nondet a=Set(true,false).oneOf();nondet b=Set(true,false).oneOf();nondet c=Set(true,false).oneOf();nondet e=Set(Request({valid:a,unique:b,bounded:c}),Lookup({actual:a,complete:b,stable:c}),Confirm({epoch:a,members:b,outputs:c}),Commit,Change,Override,SingleQuery).oneOf();fire(e)}
 action check(v:bool):bool=all{assert(v),s'=s}
 action request=fire(Request({valid:true,unique:true,bounded:true}))
 action lookup=fire(Lookup({actual:true,complete:true,stable:true}))
 action confirm=fire(Confirm({epoch:true,members:true,outputs:true}))
 run completeFamilyTest=init.then(request).then(lookup).then(confirm).then(fire(Commit)).then(check(s.committed and s.bulk==1))
 run duplicateRefusedTest=init.then(fire(Request({valid:true,unique:false,bounded:true}))).then(lookup).then(confirm).then(fire(Commit)).then(check(not(s.committed)))
 run oversizedRefusedTest=init.then(fire(Request({valid:true,unique:true,bounded:false}))).then(lookup).then(confirm).then(fire(Commit)).then(check(not(s.committed)))
 run malformedRefusedTest=init.then(fire(Request({valid:false,unique:true,bounded:true}))).then(lookup).then(confirm).then(fire(Commit)).then(check(not(s.committed)))
 run missingMemberRefusedTest=init.then(request).then(fire(Lookup({actual:true,complete:false,stable:true}))).then(confirm).then(fire(Commit)).then(check(not(s.committed)))
 run fabricatedTargetRefusedTest=init.then(request).then(fire(Lookup({actual:false,complete:true,stable:true}))).then(confirm).then(fire(Commit)).then(check(not(s.committed)))
 run changedAllocationRefusedTest=init.then(request).then(fire(Lookup({actual:true,complete:true,stable:false}))).then(confirm).then(fire(Commit)).then(check(not(s.committed)))
 run engineReloadRefusedTest=init.then(request).then(lookup).then(confirm).then(fire(Change)).then(fire(Commit)).then(check(not(s.committed)))
 run staleMemberRefusedTest=init.then(request).then(lookup).then(fire(Confirm({epoch:true,members:false,outputs:true}))).then(fire(Commit)).then(check(not(s.committed)))
 run staleOutputRefusedTest=init.then(request).then(lookup).then(fire(Confirm({epoch:true,members:true,outputs:false}))).then(fire(Commit)).then(check(not(s.committed)))
 run noFakeBulkAccountingTest=init.then(fire(SingleQuery)).then(fire(SingleQuery)).then(fire(SingleQuery)).then(check(s.bulk==0))
 run noOverrideAuthorityTest=init.then(request).then(fire(Override)).then(confirm).then(fire(Commit)).then(check(not(s.committed)))
}
