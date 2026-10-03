module bounded_read_authority {
 // Tokens are concrete equality abstractions, not Boolean identity assertions.
 type Owner={pid:int,start:int,lease:int,root:int,lock:int,directory:int,session:int,socket:int,source:int,executable:int,generation:int}
 type FD={number:int,device:int,inode:int,name:int,uid:int,mode:int,size:int,flags:int,access:int,fdFlags:int,seals:int,digest:int,noOPath:bool,noExec:bool,dataRole:bool}
 type Binding={owner:Owner,fd:FD,lineage:int}
 type Tip={epoch:int,fd:FD,digest:int,previous:int,publication:int}
 type Row={failed:bool,phase:int,closed:bool,published:bool,held:bool,borrow:Tip}
 type Event=Startup(Binding,Tip,bool)|Observe(Binding,Tip)|Begin(int)|Connect(int,bool)|Reply(int,bool)|Close(int,bool)|Confirm(int,Binding,Tip,Tip,bool)|Consume(int)|Release(int)|Plan(int,Tip)|FileDurable(bool)|Publish(Binding,Tip,bool)|Adopt|AncestorChanged|FullAudit(bool)|Crash|Refuse
 type State={bound:bool,fault:bool,binding:Binding,latest:Tip,rows:int->Row,planning:bool,selected:int,planned:Tip,fileDurable:bool,tipPublished:bool,archived:int,fullCurrent:bool,startupValidated:bool,bytesNow:bool,consumeID:int,queryWork:int,nativeEffects:int,oldRetained:bool}
 val owner={pid:1,start:1,lease:1,root:1,lock:1,directory:1,session:1,socket:1,source:1,executable:1,generation:1}
 val fd={number:7,device:1,inode:1,name:1,uid:1000,mode:384,size:128,flags:2,access:2,fdFlags:1,seals:31,digest:1,noOPath:true,noExec:true,dataRole:true}
 val binding={owner:owner,fd:fd,lineage:1}
 val emptyTip={epoch:0,fd:fd,digest:1,previous:0,publication:1}
 val nextTip={epoch:1,fd:{...fd,number:8,inode:2,name:2,digest:2},digest:2,previous:1,publication:2}
 // Two slots abstract the production512 active-operation bound; no total-history bound.
 val capacity=2
 def validOwner(o:Owner):bool=o.pid>0 and o.start>0 and o.lease>0 and o.root>0 and o.lock>0 and o.directory>0 and o.session>0 and o.socket>0 and o.source>0 and o.executable>0 and o.generation>0
 def validFD(f:FD):bool=f.number>=0 and f.device>0 and f.inode>0 and f.name>0 and f.uid==1000 and f.mode==384 and f.size>0 and f.flags>=0 and f.access==2 and f.fdFlags==1 and f.seals==31 and f.digest>0 and f.noOPath and f.noExec and f.dataRole
 def validBinding(b:Binding):bool=validOwner(b.owner) and validFD(b.fd) and b.lineage>0
 def validTip(t:Tip):bool=t.epoch>=0 and validFD(t.fd) and t.digest>0 and t.previous>=0 and t.publication>0
 def authority(b:Binding,t:Tip):bool=s.bound and not(s.fault) and b==s.binding and t==s.latest and validBinding(b) and validTip(t)
 def eligible(i:int):bool=s.rows.keys().contains(i) and s.rows.get(i).closed and s.rows.get(i).published and not(s.rows.get(i).held)
 action init=s'={bound:false,fault:false,binding:binding,latest:emptyTip,rows:Map(),planning:false,selected:0,planned:nextTip,fileDurable:false,tipPublished:false,archived:0,fullCurrent:true,startupValidated:false,bytesNow:false,consumeID:0,queryWork:0,nativeEffects:0,oldRetained:true}
 action fire(e:Event):bool={
 val b={...s,bytesNow:false,queryWork:0}
 s'=match e {
 | Release(i)=>if(s.rows.keys().contains(i)){...b,rows:s.rows.set(i,{...s.rows.get(i),held:false})} else {...b,fault:true}
 | Crash=>{...b,bound:false,rows:Map(),planning:false,fileDurable:false,tipPublished:false,startupValidated:false}
 | _=>if(s.fault)b else match e {
 | Startup(p,t,complete)=>if(not(s.bound) and complete and s.fullCurrent and validBinding(p) and validTip(t)){...b,bound:true,binding:p,latest:t,startupValidated:true} else {...b,fault:true}
 | Observe(p,t)=>if(authority(p,t))b else {...b,fault:true}
 | Begin(i)=>if(s.bound and not(s.rows.keys().contains(i)) and s.rows.size()<capacity){...b,rows:s.rows.set(i,{failed:false,phase:0,closed:false,published:false,held:true,borrow:s.latest}),queryWork:capacity+1} else {...b,fault:true}
 | Connect(i,ok)=>if(s.rows.keys().contains(i)){val r=s.rows.get(i);{...b,rows:s.rows.set(i,{...r,failed:r.failed or not(ok) or r.phase!=0,phase:if(ok and not(r.failed) and r.phase==0)1 else r.phase})}} else {...b,fault:true}
 | Reply(i,ok)=>if(s.rows.keys().contains(i)){val r=s.rows.get(i);{...b,rows:s.rows.set(i,{...r,failed:r.failed or not(ok) or r.phase!=1,phase:if(ok and not(r.failed) and r.phase==1)2 else r.phase})}} else {...b,fault:true}
 | Close(i,durable)=>if(s.rows.keys().contains(i)){val r=s.rows.get(i);{...b,rows:s.rows.set(i,{...r,closed:true,published:durable,failed:r.failed or not(durable) or r.phase!=2})}} else {...b,fault:true}
 | Confirm(i,p,t,borrow,durable)=>if(s.rows.keys().contains(i)){val r=s.rows.get(i);if(authority(p,t) and validTip(borrow) and borrow==r.borrow and r.closed and r.published and r.held and not(r.failed) and durable){...b,rows:s.rows.set(i,{...r,phase:3}),queryWork:capacity+2} else {...b,rows:s.rows.set(i,{...r,failed:true}),fault:not(authority(p,t)) or not(validTip(borrow)) or borrow!=r.borrow}} else {...b,fault:true}
 | Consume(i)=>if(s.bound and s.rows.keys().contains(i)){val r=s.rows.get(i);if(r.phase==3 and r.closed and r.published and r.held and not(r.failed)){...b,bytesNow:true,consumeID:i,rows:s.rows.set(i,{...r,phase:4}),queryWork:capacity+2} else {...b,rows:s.rows.set(i,{...r,failed:true})}} else {...b,fault:true}
 | Plan(i,t)=>if(s.bound and not(s.planning) and eligible(i) and validTip(t) and t.epoch==s.latest.epoch+1 and t.previous==s.latest.digest and t.publication!=s.latest.publication and t.fd!=s.latest.fd){...b,planning:true,selected:i,planned:t,fileDurable:false,tipPublished:false} else {...b,fault:true}
 | FileDurable(ok)=>if(s.planning and ok){...b,fileDurable:true} else {...b,fault:true}
 | Publish(p,t,ok)=>if(s.planning and s.fileDurable and authority(p,t) and eligible(s.selected) and ok){...b,tipPublished:true} else {...b,fault:true}
 | Adopt=>if(s.planning and s.fileDurable and s.tipPublished and eligible(s.selected)){...b,latest:s.planned,rows:s.rows.filter((i,r)=>i!=s.selected),planning:false,fileDurable:false,tipPublished:false,archived:s.archived+1} else {...b,fault:true}
 | AncestorChanged=>{...b,fullCurrent:false}
 | FullAudit(ok)=>if(ok and s.fullCurrent)b else {...b,fault:true}
 | Refuse=>{...b,fault:true}
 | _=>{...b,fault:true}
 }}
 val allProps=s.oldRetained and s.nativeEffects==0 and s.rows.size()<=capacity and s.queryWork<=capacity+2 and (s.tipPublished implies(s.planning and s.fileDurable)) and (s.bound implies s.startupValidated) and (s.bytesNow implies(s.bound and not(s.fault) and s.rows.keys().contains(s.consumeID) and not(s.rows.get(s.consumeID).failed) and s.rows.get(s.consumeID).closed and s.rows.get(s.consumeID).published and s.rows.get(s.consumeID).held))
 action step={nondet i=Set(0,1,2).oneOf();nondet ok=Set(true,false).oneOf();nondet replace=Set(true,false).oneOf();val p=if(replace){...binding,owner:{...owner,source:2}} else binding;val t=if(replace)nextTip else emptyTip;nondet e=Set(Startup(p,t,ok),Observe(p,t),Begin(i),Connect(i,ok),Reply(i,ok),Close(i,ok),Confirm(i,p,t,emptyTip,ok),Consume(i),Release(i),Plan(i,nextTip),FileDurable(ok),Publish(p,t,ok),Adopt,AncestorChanged,FullAudit(ok),Crash,Refuse).oneOf();fire(e)}
}
