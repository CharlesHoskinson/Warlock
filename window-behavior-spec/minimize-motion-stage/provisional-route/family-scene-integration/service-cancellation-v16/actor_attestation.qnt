module actor_attestation {
 type Kind=Helper|Renderer|Native
 type Job={id:int,actor:int,lifetime:int,source:int,kind:Kind}
 type Issuer={lifetime:int,nonce:int,root:int,service:int,revision:int}
 type Event=Register(Job)|PhysicalGone(int)|Returned({id:int,exact:bool,durable:bool})|Complete(int)|Observe|Attest({actor:int,authenticated:bool,ledgerExact:bool})|DropLedger|ReplaceIssuer|OtherActor
 type State={issuer:Issuer,witness:Issuer,ledger:Set[Job],groups:Set[int],returned:Set[int],completed:Set[int],fresh:bool,ledgerExact:bool,attested:bool,actor:int,otherProgress:int}
 var s:State
 val issuer={lifetime:1,nonce:1,root:1,service:1,revision:1}
 action init=s'={issuer:issuer,witness:issuer,ledger:Set(),groups:Set(),returned:Set(),completed:Set(),fresh:false,ledgerExact:true,attested:false,actor:0,otherProgress:0}
 pure def jobsFor(rows:Set[Job],actor:int):Set[Job]=rows.filter(j=>j.actor==actor)
 action fire(e:Event):bool={val b={...s,attested:false};s'=match e {
 | Register(j)=>if(j.id>0 and j.actor>0 and j.lifetime>0 and j.source>0 and not(s.ledger.exists(k=>k.id==j.id))){...b,ledger:s.ledger.union(Set(j)),groups:s.groups.union(Set(j.id)),issuer:{...s.issuer,revision:s.issuer.revision+1},fresh:false} else b
 | PhysicalGone(id)=>{...b,groups:s.groups.exclude(Set(id)),fresh:false}
 | Returned(p)=>if(p.exact and p.durable and s.ledger.exists(j=>j.id==p.id)){...b,returned:s.returned.union(Set(p.id)),fresh:false} else b
 | Complete(id)=>if(not(s.groups.contains(id)) and s.ledger.exists(j=>j.id==id and (j.kind!=Native or s.returned.contains(id)))){...b,completed:s.completed.union(Set(id)),issuer:{...s.issuer,revision:s.issuer.revision+1},fresh:false} else b
 | Observe=>{...b,witness:s.issuer,fresh:true}
 | Attest(p)=>if(p.actor>0 and p.authenticated and p.ledgerExact and s.ledgerExact and s.fresh and s.witness==s.issuer and jobsFor(s.ledger,p.actor).forall(j=>s.completed.contains(j.id) and not(s.groups.contains(j.id)) and (j.kind!=Native or s.returned.contains(j.id)))){...b,attested:true,actor:p.actor} else b
 | DropLedger=>{...b,ledgerExact:false,fresh:false}
 | ReplaceIssuer=>{...b,issuer:{...s.issuer,nonce:s.issuer.nonce+1},fresh:false}
 | OtherActor=>{...b,otherProgress:s.otherProgress+1}
 }}
 val allProps=s.attested implies(s.fresh and s.witness==s.issuer and s.ledgerExact and jobsFor(s.ledger,s.actor).forall(j=>s.completed.contains(j.id) and not(s.groups.contains(j.id)) and (j.kind!=Native or s.returned.contains(j.id))))
 action step={nondet e=Set(Register({id:1,actor:1,lifetime:1,source:1,kind:Renderer}),Register({id:2,actor:1,lifetime:2,source:2,kind:Native}),Register({id:3,actor:2,lifetime:3,source:3,kind:Helper}),PhysicalGone(1),PhysicalGone(2),PhysicalGone(3),Returned({id:2,exact:true,durable:true}),Returned({id:2,exact:false,durable:true}),Returned({id:2,exact:true,durable:false}),Complete(1),Complete(2),Complete(3),Observe,Attest({actor:1,authenticated:true,ledgerExact:true}),Attest({actor:1,authenticated:false,ledgerExact:true}),Attest({actor:1,authenticated:true,ledgerExact:false}),DropLedger,ReplaceIssuer,OtherActor).oneOf();fire(e)}
}
