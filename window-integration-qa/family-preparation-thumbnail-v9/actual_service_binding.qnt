module actual_service_binding {
 type Modules={moduleToken:int,ownerToken:int,outer:int,baseline:int,recovery:int,actual:int,complete:bool,paths:bool,hashes:bool,modes:bool,linked:bool,durable:bool}
 type Ledger={ledgerToken:int,ownerToken:int,currentOwner:bool,currentSource:bool,currentRoot:bool,nonempty:bool,complete:bool,closed:bool,published:bool,fault:bool,diskEqual:bool}
 type Event=Bind(Modules)|Queries(Ledger)|Original({baseline:bool,fault:bool})|Finish({moduleToken:int,ledgerToken:int,ownerToken:int,modulesSame:bool,ledgerSame:bool})|AcceptBaseline|AcceptFault|Refuse
 type State={moduleToken:int,ownerToken:int,ledgerToken:int,binding:bool,ledger:bool,originalBaseline:bool,originalFault:bool,final:bool,refused:bool,baselineAccepted:bool,faultAccepted:bool}
 var s:State
 action init=s'={moduleToken:0,ownerToken:0,ledgerToken:0,binding:false,ledger:false,originalBaseline:false,originalFault:false,final:false,refused:false,baselineAccepted:false,faultAccepted:false}
 pure def valid(p:Modules):bool=p.moduleToken>0 and p.ownerToken>0 and p.outer==23 and p.baseline==23 and p.recovery==23 and p.actual==23 and p.complete and p.paths and p.hashes and p.modes and p.linked and p.durable
 pure def validLedger(p:Ledger):bool=p.ledgerToken>0 and p.ownerToken>0 and p.currentOwner and p.currentSource and p.currentRoot and p.nonempty and p.complete and p.closed and p.published and not(p.fault) and p.diskEqual
 action fire(e:Event):bool=s'=if(s.refused)s else match e {
 | Bind(p)=>if(valid(p) and (not(s.binding) or (p.moduleToken==s.moduleToken and p.ownerToken==s.ownerToken))){...s,binding:true,moduleToken:p.moduleToken,ownerToken:p.ownerToken} else {...s,refused:true,binding:false,baselineAccepted:false,faultAccepted:false}
 | Queries(p)=>if(s.binding and validLedger(p) and p.ownerToken==s.ownerToken){...s,ledger:true,ledgerToken:p.ledgerToken,final:false,baselineAccepted:false,faultAccepted:false} else {...s,refused:true,ledger:false,baselineAccepted:false,faultAccepted:false}
 | Original(p)=>{...s,originalBaseline:p.baseline,originalFault:p.fault,baselineAccepted:false,faultAccepted:false}
 | Finish(p)=>if(s.binding and s.ledger and p.moduleToken==s.moduleToken and p.ledgerToken==s.ledgerToken and p.ownerToken==s.ownerToken and p.modulesSame and p.ledgerSame){...s,final:true} else {...s,refused:true,final:false,baselineAccepted:false,faultAccepted:false}
 | AcceptBaseline=>{...s,baselineAccepted:s.binding and s.ledger and s.final and s.originalBaseline}
 | AcceptFault=>{...s,faultAccepted:s.baselineAccepted and s.binding and s.ledger and s.final and s.originalFault}
 | Refuse=>{...s,refused:true,baselineAccepted:false,faultAccepted:false}
 }
 val allProps=(s.baselineAccepted implies (s.binding and s.ledger and s.final and s.originalBaseline and not(s.refused))) and (s.faultAccepted implies (s.baselineAccepted and s.originalFault and not(s.refused)))
 action step={nondet n=Set(17,19,23).oneOf();nondet yes=Set(true,false).oneOf();nondet e=Set(Bind({moduleToken:n,ownerToken:1,outer:23,baseline:n,recovery:23,actual:n,complete:yes,paths:true,hashes:true,modes:true,linked:true,durable:true}),Queries({ledgerToken:n,ownerToken:1,currentOwner:yes,currentSource:true,currentRoot:true,nonempty:true,complete:true,closed:true,published:true,fault:false,diskEqual:true}),Original({baseline:yes,fault:yes}),Finish({moduleToken:n,ledgerToken:n,ownerToken:1,modulesSame:yes,ledgerSame:yes}),AcceptBaseline,AcceptFault,Refuse).oneOf();fire(e)}
}
