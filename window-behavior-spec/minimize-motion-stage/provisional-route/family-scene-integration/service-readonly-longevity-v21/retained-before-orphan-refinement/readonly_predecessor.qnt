module readonly_predecessor {
 type Witness={owner:int,root:int,source:int,dataset:int,previous:int,file:int,complete:bool,chain:bool,rowsEqual:bool,durable:bool}
 type Event=Acquire({owner:int,root:int,oldTerminal:bool})|Seal(Witness)|Replace({root:int,source:int,dataset:int,previous:int,file:int})|Confirm(Witness)|PublishNew({owner:int,pointer:int,durable:bool})|Crash|Recover({chain:bool,pointer:bool,namespace:bool})|UseOld|Refuse
 type State={oldRows:Set[int],oldPending:Set[int],oldUnpublished:Set[int],oldArchived:Set[int],owner:int,root:int,source:int,dataset:int,previous:int,file:int,capturedOwner:int,capturedRoot:int,capturedSource:int,capturedDataset:int,capturedPrevious:int,capturedFile:int,lease:bool,sealed:bool,confirmed:bool,newPublished:bool,diskNew:bool,diskPointer:int,oldRetained:Set[int],diskRetained:Set[int],fault:bool,recovered:bool,oldUsable:bool}
 var s:State
 action init=s'={oldRows:Set(1,2),oldPending:Set(2),oldUnpublished:Set(2),oldArchived:Set(3),owner:0,root:1,source:1,dataset:1,previous:1,file:1,capturedOwner:0,capturedRoot:0,capturedSource:0,capturedDataset:0,capturedPrevious:0,capturedFile:0,lease:false,sealed:false,confirmed:false,newPublished:false,diskNew:false,diskPointer:0,oldRetained:Set(1,2,3),diskRetained:Set(1,2,3),fault:false,recovered:false,oldUsable:false}
 def valid(p:Witness):bool=p.owner==s.owner and p.owner>1 and p.root==s.root and p.source==s.source and p.dataset==s.dataset and p.previous==s.previous and p.file==s.file and p.root>0 and p.source>0 and p.dataset>0 and p.previous>0 and p.file>0 and p.complete and p.chain and p.rowsEqual and p.durable
 def same(p:Witness):bool=p.owner==s.capturedOwner and p.root==s.capturedRoot and p.source==s.capturedSource and p.dataset==s.capturedDataset and p.previous==s.capturedPrevious and p.file==s.capturedFile
 action fire(e:Event):bool=s'=if(s.fault)s else match e {
 | Acquire(p)=>if(not(s.lease) and p.owner>1 and p.root==s.root and p.oldTerminal){...s,owner:p.owner,lease:true} else {...s,newPublished:false,fault:true}
 | Seal(p)=>if(s.lease and not(s.sealed) and valid(p)){...s,sealed:true,confirmed:false,capturedOwner:p.owner,capturedRoot:p.root,capturedSource:p.source,capturedDataset:p.dataset,capturedPrevious:p.previous,capturedFile:p.file} else {...s,newPublished:false,fault:true}
 | Replace(p)=>{...s,root:p.root,source:p.source,dataset:p.dataset,previous:p.previous,file:p.file,confirmed:false,newPublished:false}
 | Confirm(p)=>if(s.lease and s.sealed and valid(p) and same(p)){...s,confirmed:true} else {...s,newPublished:false,fault:true}
 | PublishNew(p)=>if(s.lease and s.confirmed and p.owner==s.capturedOwner and p.owner==s.owner and p.pointer==s.capturedFile and p.durable){...s,newPublished:true,diskNew:true,diskPointer:p.pointer,diskRetained:s.oldRows.union(s.oldArchived)} else {...s,newPublished:false,fault:true}
 | Crash=>{...s,lease:false,confirmed:false,newPublished:false,recovered:false}
 | Recover(p)=>if(not(s.lease) and p.chain and p.pointer and p.namespace){...s,recovered:true,oldRetained:s.diskRetained} else {...s,newPublished:false,fault:true,recovered:false}
 | UseOld=>{...s,oldUsable:false}
 | Refuse=>{...s,newPublished:false,fault:true}
 }
 val allProps=s.oldRetained==Set(1,2,3) and s.diskRetained==Set(1,2,3) and s.oldPending.subseteq(s.diskRetained) and s.oldUnpublished.subseteq(s.diskRetained) and not(s.oldUsable) and (s.newPublished implies(s.lease and s.confirmed and s.diskNew and s.diskPointer>0 and not(s.fault)))
 action step={nondet yes=Set(true,false).oneOf();nondet n=Set(1,2,3).oneOf();val w={owner:2,root:n,source:1,dataset:1,previous:1,file:1,complete:yes,chain:yes,rowsEqual:yes,durable:yes};nondet e=Set(Acquire({owner:2,root:1,oldTerminal:yes}),Seal(w),Confirm(w),Replace({root:1,source:1,dataset:n,previous:1,file:1}),PublishNew({owner:2,pointer:n,durable:yes}),Crash,Recover({chain:yes,pointer:yes,namespace:yes}),UseOld,Refuse).oneOf();fire(e)}
}
