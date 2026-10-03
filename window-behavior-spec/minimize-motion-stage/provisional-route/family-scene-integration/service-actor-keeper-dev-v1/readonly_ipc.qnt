module readonly_ipc {
 type Owner={service:int,lease:int,root:int,source:int,compositor:int,socket:int,executable:int}
 type Event=Begin({id:int,request:int,owner:Owner,durable:bool})|Connect({owner:Owner,peer:bool})|Reply({eof:bool,bounded:bool,decoded:bool,deadline:bool})|Close(bool)|Confirm({owner:Owner,durable:bool})|PublishRefusal(bool)|Replace(int)|Refuse|Fail|Consume
 type State={owner:Owner,observed:Owner,history:Set[int],id:int,request:int,registered:bool,connected:bool,reply:bool,closed:bool,published:bool,refused:bool,usable:bool,fault:bool,consumed:bool}
 var s:State
 val owner={service:1,lease:1,root:1,source:1,compositor:1,socket:1,executable:1}
 val maxHistory=4
 pure def allowed(r:int):bool=r>=1 and r<=5
 pure def changed(o:Owner,n:int):Owner=if(n==0){...o,service:o.service+1} else if(n==1){...o,lease:o.lease+1} else if(n==2){...o,root:o.root+1} else if(n==3){...o,source:o.source+1} else if(n==4){...o,compositor:o.compositor+1} else if(n==5){...o,socket:o.socket+1} else {...o,executable:o.executable+1}
 action init=s'={owner:owner,observed:owner,history:Set(),id:0,request:0,registered:false,connected:false,reply:false,closed:false,published:false,refused:false,usable:false,fault:false,consumed:false}
 action fire(e:Event):bool={val b={...s,consumed:false};s'=match e {
 | Begin(p)=>if(not(s.fault) and p.id>0 and s.history.size()<maxHistory and not(s.history.contains(p.id)) and allowed(p.request) and p.owner==s.owner and (not(s.registered) or s.closed and s.published)){if(p.durable){...b,history:s.history.union(Set(p.id)),id:p.id,request:p.request,observed:p.owner,registered:true,connected:false,reply:false,closed:false,published:false,refused:false,usable:false} else {...b,fault:true,usable:false}} else {...b,usable:false}
 | Connect(p)=>if(not(s.fault) and not(s.refused) and s.registered and not(s.closed) and p.owner==s.owner and s.observed==s.owner and p.peer){...b,connected:true} else {...b,refused:s.registered,published:false,usable:false}
 | Reply(p)=>if(not(s.fault) and not(s.refused) and s.connected and not(s.closed) and s.observed==s.owner and p.eof and p.bounded and p.decoded and p.deadline){...b,reply:true,usable:false} else {...b,refused:s.registered,reply:false,published:false,usable:false}
 | Close(normal)=>{...b,closed:normal,refused:s.refused or not(normal),usable:false}
 | Confirm(p)=>if(not(s.fault) and not(s.refused) and s.registered and s.closed and s.reply and p.owner==s.owner and s.observed==s.owner){if(p.durable){...b,published:true,usable:true} else {...b,fault:true,refused:true,published:false,usable:false}} else {...b,refused:s.registered,published:false,usable:false}
 | PublishRefusal(durable)=>if(not(s.fault) and s.registered and s.refused and s.closed){if(durable){...b,published:true,usable:false} else {...b,fault:true,published:false,usable:false}} else {...b,usable:false}
 | Replace(n)=>{...b,owner:changed(s.owner,n),refused:s.registered,published:false,usable:false}
 | Refuse=>{...b,refused:s.registered,published:false,usable:false}
 | Fail=>{...b,fault:true,usable:false}
 | Consume=>{...b,consumed:s.usable}
 }}
 val authority=s.registered and s.connected and s.reply and s.closed and s.published and allowed(s.request) and s.observed==s.owner and not(s.fault) and not(s.refused)
 val allProps=(s.usable implies authority) and (s.consumed implies authority) and (s.registered implies s.history.contains(s.id)) and s.history.size()<=maxHistory and (s.refused implies not(s.usable))
 action step={nondet id=1.to(5).oneOf();nondet e=Set(Begin({id:id,request:1,owner:owner,durable:true}),Begin({id:id,request:2,owner:owner,durable:true}),Begin({id:id,request:6,owner:owner,durable:true}),Begin({id:id,request:1,owner:owner,durable:false}),Connect({owner:owner,peer:true}),Connect({owner:owner,peer:false}),Reply({eof:true,bounded:true,decoded:true,deadline:true}),Reply({eof:false,bounded:true,decoded:true,deadline:true}),Reply({eof:true,bounded:false,decoded:true,deadline:true}),Reply({eof:true,bounded:true,decoded:false,deadline:true}),Reply({eof:true,bounded:true,decoded:true,deadline:false}),Close(true),Close(false),Confirm({owner:owner,durable:true}),Confirm({owner:owner,durable:false}),PublishRefusal(true),PublishRefusal(false),Replace(0),Replace(1),Replace(2),Replace(3),Replace(4),Replace(5),Replace(6),Refuse,Fail,Consume).oneOf();fire(e)}
}
