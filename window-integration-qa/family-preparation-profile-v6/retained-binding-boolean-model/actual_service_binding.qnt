module actual_service_binding {
 type Modules={outer:int,baseline:int,recovery:int,actual:int,complete:bool,paths:bool,hashes:bool,modes:bool,linked:bool,durable:bool}
 type Ledger={currentOwner:bool,currentSource:bool,currentRoot:bool,nonempty:bool,complete:bool,closed:bool,published:bool,fault:bool,diskEqual:bool}
 type Event=Bind(Modules)|Queries(Ledger)|Original({baseline:bool,fault:bool})|Finish({modulesSame:bool,ledgerSame:bool})|AcceptBaseline|AcceptFault|Refuse
 type State={binding:bool,ledger:bool,originalBaseline:bool,originalFault:bool,final:bool,refused:bool,baselineAccepted:bool,faultAccepted:bool}
 var s:State
 action init=s'={binding:false,ledger:false,originalBaseline:false,originalFault:false,final:false,refused:false,baselineAccepted:false,faultAccepted:false}
 pure def valid(p:Modules):bool=p.outer==20 and p.baseline==20 and p.recovery==20 and p.actual==20 and p.complete and p.paths and p.hashes and p.modes and p.linked and p.durable
 pure def validLedger(p:Ledger):bool=p.currentOwner and p.currentSource and p.currentRoot and p.nonempty and p.complete and p.closed and p.published and not(p.fault) and p.diskEqual
 action fire(e:Event):bool=s'=if(s.refused)s else match e {
 | Bind(p)=>if(valid(p)){...s,binding:true} else {...s,refused:true,binding:false,baselineAccepted:false,faultAccepted:false}
 | Queries(p)=>if(s.binding and validLedger(p)){...s,ledger:true} else {...s,refused:true,ledger:false,baselineAccepted:false,faultAccepted:false}
 | Original(p)=>{...s,originalBaseline:p.baseline,originalFault:p.fault,baselineAccepted:false,faultAccepted:false}
 | Finish(p)=>if(s.binding and s.ledger and p.modulesSame and p.ledgerSame){...s,final:true} else {...s,refused:true,final:false,baselineAccepted:false,faultAccepted:false}
 | AcceptBaseline=>{...s,baselineAccepted:s.binding and s.ledger and s.final and s.originalBaseline}
 | AcceptFault=>{...s,faultAccepted:s.baselineAccepted and s.binding and s.ledger and s.final and s.originalFault}
 | Refuse=>{...s,refused:true,baselineAccepted:false,faultAccepted:false}
 }
 val allProps=(s.baselineAccepted implies (s.binding and s.ledger and s.final and s.originalBaseline and not(s.refused))) and (s.faultAccepted implies (s.baselineAccepted and s.originalFault and not(s.refused)))
 action step={nondet n=Set(17,19,20).oneOf();nondet yes=Set(true,false).oneOf();nondet e=Set(Bind({outer:20,baseline:n,recovery:20,actual:n,complete:yes,paths:true,hashes:true,modes:true,linked:true,durable:true}),Queries({currentOwner:yes,currentSource:true,currentRoot:true,nonempty:true,complete:true,closed:true,published:true,fault:false,diskEqual:true}),Original({baseline:yes,fault:yes}),Finish({modulesSame:yes,ledgerSame:yes}),AcceptBaseline,AcceptFault,Refuse).oneOf();fire(e)}
}
