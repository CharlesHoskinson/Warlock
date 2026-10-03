module readonly_startup {
 type Proof={owner:int,root:int,source:int,pointer:int,complete:bool,durable:bool}
 type Event=Lease(int)|Seal(Proof)|PublishHelper(Proof)|Bind(Proof)|Crash|ValidatePending(Proof)|NativeRecover(bool)|Query|Refuse
 type State={owner:int,pointer:int,diskPointer:int,leased:bool,sealed:bool,validated:bool,helperPublished:bool,bound:bool,oldRetained:bool,fault:bool,bytes:bool,nativeGuard:bool}
 var s:State
 action init=s'={owner:0,pointer:0,diskPointer:0,leased:false,sealed:false,validated:false,helperPublished:false,bound:false,oldRetained:true,fault:false,bytes:false,nativeGuard:false}
 def current(p:Proof):bool=s.leased and p.owner==s.owner and p.owner>1 and p.root==1 and p.source==1 and p.pointer>0 and p.complete and p.durable
 action fire(e:Event):bool={val b={...s,bytes:false};s'=if(s.fault)b else match e {
 | Lease(n)=>if(not(s.leased) and n>1){...b,owner:n,leased:true} else {...b,fault:true}
 | Seal(p)=>if(current(p)){...b,pointer:p.pointer,sealed:true,validated:true} else {...b,fault:true}
 | PublishHelper(p)=>if(current(p) and s.sealed and p.pointer==s.pointer){...b,helperPublished:true,diskPointer:p.pointer} else {...b,fault:true}
 | Bind(p)=>if(current(p) and s.validated and p.pointer==s.pointer and (not(s.helperPublished) or s.diskPointer==p.pointer)){...b,bound:true} else {...b,fault:true}
 | Crash=>{...b,leased:false,sealed:false,validated:false,bound:false,bytes:false,nativeGuard:false,pointer:0}
 | ValidatePending(p)=>if(current(p) and s.diskPointer==p.pointer){...b,pointer:p.pointer,sealed:true,validated:true} else {...b,fault:true}
 | NativeRecover(guard)=>if(s.leased and s.validated and guard){...b,nativeGuard:true} else {...b,fault:true}
 | Query=>if(s.leased and s.bound and s.validated){...b,bytes:true} else {...b,fault:true}
 | Refuse=>{...b,fault:true}
 }}
 val allProps=s.oldRetained and (s.helperPublished implies s.diskPointer>0) and (s.bytes implies(s.leased and s.bound and s.validated and not(s.fault))) and (s.nativeGuard implies(s.leased and s.validated))
 action step={nondet yes=Set(true,false).oneOf();nondet n=Set(1,2,3).oneOf();val p={owner:2,root:1,source:1,pointer:n,complete:yes,durable:yes};nondet e=Set(Lease(2),Seal(p),PublishHelper(p),Bind(p),Crash,ValidatePending(p),NativeRecover(yes),Query,Refuse).oneOf();fire(e)}
}
