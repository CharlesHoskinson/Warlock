module actor_ledger {
 type Role=Helper|Renderer|Native
 type Issuer={lifetime:int,nonce:int,source:int,service:int,session:int,root:int}
 type Intent={actor:int,receipt:int,token:int,scope:int}
 type Job={id:int,actor:int,lifetime:int,source:int,role:Role}
 type Event=Register({job:Job,observed:bool,durable:bool})|Release({id:int,durable:bool})|Gone(int)|Complete({id:int,durable:bool})|Returned({id:int,source:int,lifetime:int,result:int,durable:bool})|Uncertain(int)|Freeze({intent:Intent,authenticated:bool,current:bool,durable:bool})|Observe|Attest({intent:Intent,authenticated:bool,inventory:bool})|ReplaceIssuer(int)|ReplaceIntent|DropHistory|Crash|FailPersistence
 type State={issuer:Issuer,observedIssuer:Issuer,intent:Intent,observedIntent:Intent,jobs:Set[Job],active:Set[int],released:Set[int],complete:Set[int],returned:Set[int],uncertain:Set[int],frozen:bool,revision:int,witnessRevision:int,fresh:bool,attested:bool,fault:bool,crashed:bool,lateReleased:bool}
 var s:State
 val issuer={lifetime:1,nonce:1,source:1,service:1,session:1,root:1}
 val intent={actor:1,receipt:1,token:1,scope:1}
 val empty={actor:0,receipt:0,token:0,scope:0}
 action init=s'={issuer:issuer,observedIssuer:issuer,intent:empty,observedIntent:empty,jobs:Set(),active:Set(),released:Set(),complete:Set(),returned:Set(),uncertain:Set(),frozen:false,revision:0,witnessRevision:0,fresh:false,attested:false,fault:false,crashed:false,lateReleased:false}
 pure def valid(i:Intent):bool=i.actor>0 and i.receipt>0 and i.token>0 and i.scope>0
 pure def owned(j:Job):bool=j.actor==1
 pure def changed(i:Issuer,n:int):Issuer=if(n==0){...i,lifetime:i.lifetime+1} else if(n==1){...i,nonce:i.nonce+1} else if(n==2){...i,source:i.source+1} else if(n==3){...i,service:i.service+1} else if(n==4){...i,session:i.session+1} else {...i,root:i.root+1}
 val ready=not(s.fault) and not(s.crashed)
 val closed=s.jobs.filter(owned).forall(j=>not(s.active.contains(j.id)) and s.complete.contains(j.id) and not(s.uncertain.contains(j.id)) and (j.role!=Native or s.returned.contains(j.id)))
 val authority=ready and s.frozen and s.fresh and s.observedIssuer==s.issuer and s.observedIntent==s.intent and s.witnessRevision==s.revision and closed
 action fire(e:Event):bool={val b={...s,attested:false,lateReleased:false};s'=match e {
 | Register(p)=>if(ready and p.observed and p.job.id>0 and p.job.actor>0 and p.job.lifetime>0 and p.job.source>0 and not(s.jobs.exists(j=>j.id==p.job.id)) and not(s.frozen and owned(p.job))) {if(p.durable){...b,jobs:s.jobs.union(Set(p.job)),active:s.active.union(Set(p.job.id)),revision:s.revision+(if(owned(p.job))1 else 0),fresh:if(owned(p.job))false else s.fresh} else {...b,fault:true,fresh:false}} else b
 | Release(p)=>if(ready and s.jobs.exists(j=>j.id==p.id and not(s.frozen and owned(j)))){if(p.durable){...b,released:s.released.union(Set(p.id))} else {...b,fault:true,fresh:false}} else b
 | Gone(id)=>{...b,active:s.active.exclude(Set(id)),fresh:if(s.jobs.exists(j=>j.id==id and owned(j)))false else s.fresh}
 | Complete(p)=>if(ready and not(s.active.contains(p.id)) and s.jobs.exists(j=>j.id==p.id)){if(p.durable){...b,complete:s.complete.union(Set(p.id)),revision:s.revision+(if(s.jobs.exists(j=>j.id==p.id and owned(j)))1 else 0),fresh:false} else {...b,fault:true,fresh:false}} else b
 | Returned(p)=>if(ready and p.result>0 and s.jobs.exists(j=>j.id==p.id and j.role==Native and j.source==p.source and j.lifetime==p.lifetime) and not(s.uncertain.contains(p.id))){if(p.durable){...b,returned:s.returned.union(Set(p.id)),revision:s.revision+1,fresh:false} else {...b,fault:true,fresh:false}} else b
 | Uncertain(id)=>{...b,uncertain:s.uncertain.union(Set(id)),fresh:false}
 | Freeze(p)=>if(ready and valid(p.intent) and p.intent.actor==1 and p.authenticated and p.current and (not(s.frozen) or p.intent==s.intent)){if(p.durable){...b,frozen:true,intent:p.intent,revision:s.revision+1,fresh:false} else {...b,fault:true,fresh:false}} else b
 | Observe=>if(ready){...b,observedIssuer:s.issuer,observedIntent:s.intent,witnessRevision:s.revision,fresh:true} else b
 | Attest(p)=>if(authority and p.authenticated and p.inventory and p.intent==s.intent){...b,attested:true} else b
 | ReplaceIssuer(n)=>{...b,issuer:changed(s.issuer,n),fresh:false}
 | ReplaceIntent=>{...b,intent:{...s.intent,receipt:s.intent.receipt+1},fresh:false}
 | DropHistory=>{...b,fault:true,fresh:false}
 | Crash=>{...b,crashed:true,fresh:false}
 | FailPersistence=>{...b,fault:true,fresh:false}
 }}
 val allProps=(s.attested implies authority) and not(s.lateReleased) and (s.fault implies not(s.attested))
 val renderer={id:1,actor:1,lifetime:1,source:1,role:Renderer}
 val native={id:2,actor:1,lifetime:2,source:2,role:Native}
 val other={id:3,actor:2,lifetime:3,source:3,role:Helper}
 action step={nondet e=Set(Register({job:renderer,observed:true,durable:true}),Register({job:native,observed:true,durable:true}),Register({job:other,observed:true,durable:true}),Register({job:renderer,observed:false,durable:true}),Register({job:renderer,observed:true,durable:false}),Release({id:1,durable:true}),Release({id:2,durable:false}),Gone(1),Gone(2),Gone(3),Complete({id:1,durable:true}),Complete({id:2,durable:true}),Complete({id:3,durable:true}),Complete({id:1,durable:false}),Returned({id:2,source:2,lifetime:2,result:1,durable:true}),Returned({id:2,source:3,lifetime:2,result:1,durable:true}),Returned({id:2,source:2,lifetime:3,result:1,durable:true}),Returned({id:2,source:2,lifetime:2,result:1,durable:false}),Uncertain(2),Freeze({intent:intent,authenticated:true,current:true,durable:true}),Freeze({intent:intent,authenticated:false,current:true,durable:true}),Freeze({intent:intent,authenticated:true,current:false,durable:true}),Freeze({intent:intent,authenticated:true,current:true,durable:false}),Observe,Attest({intent:intent,authenticated:true,inventory:true}),Attest({intent:intent,authenticated:false,inventory:true}),Attest({intent:intent,authenticated:true,inventory:false}),ReplaceIssuer(0),ReplaceIssuer(1),ReplaceIssuer(2),ReplaceIssuer(3),ReplaceIssuer(4),ReplaceIssuer(5),ReplaceIntent,DropHistory,Crash,FailPersistence).oneOf();fire(e)}
}
