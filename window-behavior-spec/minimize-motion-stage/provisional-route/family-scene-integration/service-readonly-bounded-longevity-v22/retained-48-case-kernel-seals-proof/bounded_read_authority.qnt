module bounded_read_authority {
 // Tokens are concrete equality abstractions, not Boolean identity assertions.
 type Owner={pid:int,start:int,lease:int,root:int,lock:int,directory:int,session:int,socket:int,source:int,executable:int,generation:int}
 type FD={number:int,device:int,inode:int,name:int,uid:int,mode:int,size:int,flags:int,access:int,fdFlags:int,seals:int,digest:int,noOPath:bool,noExec:bool,dataRole:bool,role:int}
 type Binding={owner:Owner,fd:FD,lineage:int}
 type Tip={epoch:int,fd:FD,token:FD,digest:int,previous:int,publication:int}
 type Row={failed:bool,phase:int,closed:bool,published:bool,held:bool,borrow:Tip}
 type Event=Startup((Binding,Tip,bool))|Observe((Binding,Tip))|Begin(int)|Connect((int,bool))|Reply((int,bool))|Close((int,bool))|Confirm((int,Binding,Tip,Tip,bool))|Consume(int)|Release(int)|Plan((int,Tip))|FileDurable(bool)|Publish((Binding,Tip,bool))|Adopt|AncestorChanged|FullAudit(bool)|Crash|Refuse
 type State={bound:bool,fault:bool,binding:Binding,latest:Tip,diskTip:Tip,diskInitialized:bool,rows:int->Row,planning:bool,selected:int,planned:Tip,fileDurable:bool,tipPublished:bool,archived:int,fullCurrent:bool,startupValidated:bool,bytesNow:bool,consumeID:int,queryWork:int,nativeEffects:int,oldRetained:bool}
 var s:State
 val owner={pid:1,start:1,lease:1,root:1,lock:1,directory:1,session:1,socket:1,source:1,executable:1,generation:1}
 val fd={number:7,device:1,inode:1,name:1,uid:1000,mode:384,size:128,flags:2,access:2,fdFlags:1,seals:47,digest:1,noOPath:true,noExec:true,dataRole:true,role:1}
 val binding={owner:owner,fd:fd,lineage:1}
 val emptyTip={epoch:0,fd:fd,token:fd,digest:1,previous:0,publication:1}
 val nextTip={epoch:1,fd:{...fd,number:8,inode:2,name:2,digest:2,access:0,flags:0,role:2,seals:0},token:{...fd,number:9,inode:3,name:3,digest:2},digest:2,previous:1,publication:2}
 // Two slots abstract the production512 active-operation bound; no total-history bound.
 val capacity=2
 def validOwner(o:Owner):bool=o.pid>0 and o.start>0 and o.lease>0 and o.root>0 and o.lock>0 and o.directory>0 and o.session>0 and o.socket>0 and o.source>0 and o.executable>0 and o.generation>0
 def validFD(f:FD):bool=f.number>=0 and f.device>0 and f.inode>0 and f.name>0 and f.uid==1000 and f.mode==384 and f.size>0 and f.flags>=0 and (f.access==0 or f.access==2) and f.flags % 4 == f.access and f.fdFlags==1 and f.seals>=0 and f.digest>0 and f.noOPath and f.noExec and f.dataRole
 def validBinding(b:Binding):bool=validOwner(b.owner) and validFD(b.fd) and b.fd.role==1 and b.fd.access==2 and b.fd.seals==47 and b.lineage>0
 def validTip(t:Tip):bool=t.epoch>=0 and validFD(t.fd) and (if(t.epoch==0)t.fd.role==1 and t.fd.access==2 and t.fd.seals==47 else t.fd.role==2 and t.fd.access==0 and t.fd.seals==0) and validFD(t.token) and t.token.role==1 and t.token.access==2 and t.token.seals==47 and t.digest>0 and t.previous>=0 and t.publication>0
 def authority(b:Binding,t:Tip):bool=s.bound and not(s.fault) and b==s.binding and t==s.latest and validBinding(b) and validTip(t)
 def eligible(i:int):bool=s.rows.keys().contains(i) and s.rows.get(i).closed and s.rows.get(i).published and not(s.rows.get(i).held)
 action init=s'={bound:false,fault:false,binding:binding,latest:emptyTip,diskTip:emptyTip,diskInitialized:false,rows:Map(),planning:false,selected:0,planned:nextTip,fileDurable:false,tipPublished:false,archived:0,fullCurrent:true,startupValidated:false,bytesNow:false,consumeID:0,queryWork:0,nativeEffects:0,oldRetained:true}
 action fire(e:Event):bool={
 val b={...s,bytesNow:false,queryWork:0}
 s'=match e {
 | Release(i)=>if(s.rows.keys().contains(i)){...b,rows:s.rows.set(i,{...s.rows.get(i),held:false})} else {...b,fault:true}
 | Crash=>{...b,bound:false,rows:Map(),planning:false,fileDurable:false,tipPublished:false,startupValidated:false}
 | _=>if(s.fault)b else match e {
 | Startup(x)=>{val p=x._1;val t=x._2;val complete=x._3;if(not(s.bound) and complete and s.fullCurrent and validBinding(p) and validTip(t) and (not(s.diskInitialized) or t==s.diskTip)){...b,bound:true,binding:p,latest:t,diskTip:t,diskInitialized:true,startupValidated:true} else {...b,fault:true}}
 | Observe(x)=>{val p=x._1;val t=x._2;if(authority(p,t))b else {...b,fault:true}}
 | Begin(i)=>if(s.bound and not(s.planning) and not(s.rows.keys().contains(i)) and s.rows.keys().size()<capacity){...b,rows:s.rows.put(i,{failed:false,phase:0,closed:false,published:false,held:true,borrow:s.latest}),queryWork:capacity+1} else {...b,fault:true}
 | Connect(x)=>{val i=x._1;val ok=x._2;if(s.rows.keys().contains(i)){val r=s.rows.get(i);{...b,rows:s.rows.set(i,{...r,failed:r.failed or not(ok) or r.phase!=0,phase:if(ok and not(r.failed) and r.phase==0)1 else r.phase})}} else {...b,fault:true}}
 | Reply(x)=>{val i=x._1;val ok=x._2;if(s.rows.keys().contains(i)){val r=s.rows.get(i);{...b,rows:s.rows.set(i,{...r,failed:r.failed or not(ok) or r.phase!=1,phase:if(ok and not(r.failed) and r.phase==1)2 else r.phase})}} else {...b,fault:true}}
 | Close(x)=>{val i=x._1;val durable=x._2;if(s.rows.keys().contains(i)){val r=s.rows.get(i);{...b,rows:s.rows.set(i,{...r,closed:true,published:durable,failed:r.failed or not(durable) or r.phase!=2})}} else {...b,fault:true}}
 | Confirm(x)=>{val i=x._1;val p=x._2;val t=x._3;val borrow=x._4;val durable=x._5;if(s.rows.keys().contains(i)){val r=s.rows.get(i);if(not(s.planning) and authority(p,t) and validTip(borrow) and borrow==r.borrow and r.closed and r.published and r.held and not(r.failed) and durable){...b,rows:s.rows.set(i,{...r,phase:3}),queryWork:capacity+3} else {...b,rows:s.rows.set(i,{...r,failed:true}),fault:not(authority(p,t)) or not(validTip(borrow)) or borrow!=r.borrow}} else {...b,fault:true}}
 | Consume(i)=>if(s.bound and not(s.planning) and s.rows.keys().contains(i)){val r=s.rows.get(i);if(r.phase==3 and r.closed and r.published and r.held and not(r.failed)){...b,bytesNow:true,consumeID:i,rows:s.rows.set(i,{...r,phase:4}),queryWork:capacity+3} else {...b,rows:s.rows.set(i,{...r,failed:true})}} else {...b,fault:true}
 | Plan(x)=>{val i=x._1;val t=x._2;if(s.bound and not(s.planning) and eligible(i) and validTip(t) and t.epoch==s.latest.epoch+1 and t.previous==s.latest.digest and t.publication!=s.latest.publication and t.fd!=s.latest.fd){...b,planning:true,selected:i,planned:t,fileDurable:false,tipPublished:false} else {...b,fault:true}}
 | FileDurable(ok)=>if(s.planning and ok){...b,fileDurable:true} else {...b,fault:true}
 | Publish(x)=>{val p=x._1;val t=x._2;val ok=x._3;if(s.planning and s.fileDurable and authority(p,t) and eligible(s.selected) and ok){...b,tipPublished:true,diskTip:s.planned} else {...b,fault:true}}
 | Adopt=>if(s.planning and s.fileDurable and s.tipPublished and eligible(s.selected)){...b,latest:s.planned,rows:s.rows.keys().filter(i=>i!=s.selected).mapBy(i=>s.rows.get(i)),planning:false,fileDurable:false,tipPublished:false,archived:s.archived+1} else {...b,fault:true}
 | AncestorChanged=>{...b,fullCurrent:false}
 | FullAudit(ok)=>if(ok and s.fullCurrent)b else {...b,fault:true}
 | Refuse=>{...b,fault:true}
 | _=>{...b,fault:true}
 }}}
 val heldTipCount=s.rows.keys().filter(i=>s.rows.get(i).held).map(i=>s.rows.get(i).borrow).union(Set(s.latest)).union(if(s.planning)Set(s.planned) else Set()).size()
 val descriptorBound=2*heldTipCount+1 <= 2*(capacity+2)+1
 val allProps=descriptorBound and s.oldRetained and s.nativeEffects==0 and s.rows.keys().size()<=capacity and s.queryWork<=capacity+3 and (s.tipPublished implies(s.planning and s.fileDurable)) and (s.bound implies s.startupValidated) and (s.bytesNow implies(s.bound and not(s.fault) and s.rows.keys().contains(s.consumeID) and not(s.rows.get(s.consumeID).failed) and s.rows.get(s.consumeID).closed and s.rows.get(s.consumeID).published and s.rows.get(s.consumeID).held))
 action adversarialStep={nondet i=Set(0,1,2).oneOf();nondet ok=Set(true,false).oneOf();nondet replace=Set(true,false).oneOf();val p=if(replace){...binding,owner:{...owner,source:2}} else binding;val t=if(replace)nextTip else emptyTip;nondet e=Set(Startup((p,t,ok)),Observe((p,t)),Begin(i),Connect((i,ok)),Reply((i,ok)),Close((i,ok)),Confirm((i,p,t,emptyTip,ok)),Consume(i),Release(i),Plan((i,nextTip)),FileDurable(ok),Publish((p,t,ok)),Adopt,AncestorChanged,FullAudit(ok),Crash,Refuse).oneOf();fire(e)}
 action validStep:bool={
 val t={...nextTip,epoch:s.latest.epoch+1,fd:{...nextTip.fd,number:s.latest.fd.number+1,inode:s.latest.fd.inode+1,name:s.latest.fd.name+1,digest:s.latest.digest+1},token:{...fd,number:s.latest.token.number+2,inode:s.latest.token.inode+2,name:s.latest.token.name+2,digest:s.latest.digest+1},digest:s.latest.digest+1,previous:s.latest.digest,publication:s.latest.publication+1}
 if(s.fault)fire(Refuse)
 else if(not(s.bound))fire(Startup((binding,emptyTip,true)))
 else if(s.planning){if(not(s.fileDurable))fire(FileDurable(true)) else if(not(s.tipPublished))fire(Publish((s.binding,s.latest,true))) else fire(Adopt)}
 else if(not(s.rows.keys().contains(0)))fire(Begin(0))
 else {val r=s.rows.get(0);if(r.phase==0)fire(Connect((0,true))) else if(r.phase==1)fire(Reply((0,true))) else if(r.phase==2 and not(r.closed))fire(Close((0,true))) else if(r.phase==2)fire(Confirm((0,s.binding,s.latest,r.borrow,true))) else if(r.phase==3)fire(Consume(0)) else if(r.held)fire(Release(0)) else fire(Plan((0,t)))}
 }
 action step=any{validStep,adversarialStep}
}
