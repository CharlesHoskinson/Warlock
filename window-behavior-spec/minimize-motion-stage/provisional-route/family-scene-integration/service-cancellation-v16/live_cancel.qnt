module live_cancel {
 type Binding={root:int,lock:int,session:int,owner:int,actor:int,receipt:int,token:int,scope:int,keeper:int,resource:int}
 type Event=Reserve({request:Binding,explicit:bool,peer:bool,durable:bool})|LeaseProof({binding:Binding,held:bool,authenticated:bool})|Replace(int)|Promote|NativeWrite|NativeUncertain|Retire({normal:bool,callbacks:bool,durable:bool})|Attest({binding:Binding,allJobs:bool,authenticated:bool})|Observe({binding:Binding,complete:bool,stable:bool})|Acknowledge(bool)|Dispose|Expose|OtherActor|Crash|Reload|Reduce(bool)|ReturnedEndpoint
 type State={current:Binding,original:Binding,witness:Binding,leaseWitness:Binding,leaseFresh:bool,reserved:bool,retired:bool,attested:bool,observed:bool,uncertain:bool,ack:bool,directory:bool,crashed:bool,promoted:bool,write:bool,exposed:bool,otherRunning:bool,otherSteps:int,reduced:bool,validated:bool,endpointReturned:bool}
 var s:State
 val binding={root:1,lock:1,session:1,owner:1,actor:1,receipt:1,token:1,scope:1,keeper:1,resource:1}
 action init=s'={current:binding,original:binding,witness:binding,leaseWitness:binding,leaseFresh:true,reserved:false,retired:false,attested:false,observed:false,uncertain:false,ack:false,directory:true,crashed:false,promoted:false,write:false,exposed:false,otherRunning:true,otherSteps:0,reduced:false,validated:false,endpointReturned:false}
 pure def changed(b:Binding,i:int):Binding=if(i==0){...b,root:b.root+1} else if(i==1){...b,lock:b.lock+1} else if(i==2){...b,session:b.session+1} else if(i==3){...b,owner:b.owner+1} else if(i==4){...b,actor:b.actor+1} else if(i==5){...b,receipt:b.receipt+1} else if(i==6){...b,token:b.token+1} else if(i==7){...b,scope:b.scope+1} else if(i==8){...b,keeper:b.keeper+1} else {...b,resource:b.resource+1}
 val sameIntent=s.current.root==s.original.root and s.current.lock==s.original.lock and s.current.session==s.original.session and s.current.actor==s.original.actor and s.current.receipt==s.original.receipt and s.current.token==s.original.token and s.current.scope==s.original.scope and s.current.resource==s.original.resource
 val leaseCurrent=s.leaseFresh and s.leaseWitness==s.current
 val authorized=leaseCurrent and s.reserved and sameIntent and s.retired and s.attested and s.observed and s.witness==s.current and not(s.uncertain) and not(s.crashed)
 action fire(e:Event):bool={val b={...s,promoted:false,write:false,exposed:false};s'=match e {
 | Reserve(p)=>if(leaseCurrent and p.explicit and p.peer and p.durable and p.request==s.current and not(s.uncertain) and not(s.crashed) and not(s.reserved)){...b,reserved:true,original:s.current,observed:false,attested:false} else b
 | LeaseProof(p)=>if(p.held and p.authenticated and p.binding==s.current and sameIntent and not(s.crashed)){...b,leaseWitness:s.current,leaseFresh:true} else {...b,leaseFresh:false}
 | Replace(i)=>{...b,current:changed(s.current,i),observed:false,attested:false,leaseFresh:false}
 | Promote=>if(leaseCurrent and not(s.reserved) and not(s.crashed) and not(s.uncertain)){...b,promoted:true,validated:true} else b
 | NativeWrite=>if(leaseCurrent and not(s.reserved) and s.validated and not(s.crashed) and not(s.uncertain)){...b,write:true} else b
 | NativeUncertain=>{...b,uncertain:true,observed:false,attested:false}
 | Retire(p)=>if(s.reserved and p.normal and p.callbacks and p.durable and not(s.uncertain) and not(s.crashed)){...b,retired:true} else b
 | Attest(p)=>if(s.reserved and s.retired and p.allJobs and p.authenticated and p.binding==s.current and not(s.uncertain) and not(s.crashed)){...b,attested:true,witness:s.current} else b
 | Observe(p)=>if(s.reserved and s.retired and s.attested and p.complete and p.stable and p.binding==s.current and not(s.uncertain) and not(s.crashed)){...b,observed:true,witness:s.current} else b
 | Acknowledge(durable)=>if(authorized and durable){...b,ack:true} else b
 | Dispose=>if(authorized and s.ack){...b,directory:false} else b
 | Expose=>if(authorized and s.ack and not(s.directory)){...b,exposed:true} else b
 | OtherActor=>if(s.otherRunning and not(s.crashed)){...b,otherSteps:s.otherSteps+1} else b
 | Crash=>{...b,crashed:true,leaseFresh:false,observed:false,attested:false,retired:false}
 | Reload=>{...b,crashed:false,leaseFresh:false,current:{...s.current,owner:s.current.owner+1,keeper:s.current.keeper+1},observed:false,attested:false}
 | Reduce(validated)=>{...b,reduced:true,validated:validated and s.validated}
 | ReturnedEndpoint=>if(s.reduced and s.validated and not(s.reserved) and not(s.uncertain) and not(s.crashed)){...b,endpointReturned:true} else b
 }}
 val allProps=(s.write or s.promoted implies not(s.reserved)) and (not(s.directory) implies(s.reserved and s.ack)) and (s.exposed implies(authorized and s.ack and not(s.directory))) and (s.ack implies s.reserved) and s.otherRunning
 action step={nondet e=Set(Reserve({request:binding,explicit:true,peer:true,durable:true}),Reserve({request:binding,explicit:false,peer:true,durable:true}),Reserve({request:binding,explicit:true,peer:false,durable:true}),Reserve({request:binding,explicit:true,peer:true,durable:false}),LeaseProof({binding:binding,held:true,authenticated:true}),LeaseProof({binding:binding,held:false,authenticated:true}),LeaseProof({binding:binding,held:true,authenticated:false}),Replace(0),Replace(1),Replace(2),Replace(3),Replace(4),Replace(5),Replace(6),Replace(7),Replace(8),Replace(9),Promote,NativeWrite,NativeUncertain,Retire({normal:true,callbacks:true,durable:true}),Retire({normal:false,callbacks:true,durable:true}),Retire({normal:true,callbacks:false,durable:true}),Retire({normal:true,callbacks:true,durable:false}),Attest({binding:binding,allJobs:true,authenticated:true}),Attest({binding:binding,allJobs:false,authenticated:true}),Attest({binding:binding,allJobs:true,authenticated:false}),Observe({binding:binding,complete:true,stable:true}),Observe({binding:binding,complete:false,stable:true}),Observe({binding:binding,complete:true,stable:false}),Acknowledge(true),Acknowledge(false),Dispose,Expose,OtherActor,Crash,Reload,Reduce(true),Reduce(false),ReturnedEndpoint).oneOf();fire(e)}
}
