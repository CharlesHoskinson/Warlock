module bootstrap_lifecycle {
 type State={created:bool,queued:bool,sent:bool,configured:bool,acked:bool,announced:bool,failed:bool,parent:bool,owned:bool}
 type Event=Create|FlushSuccess|FlushNegative|ParentConfigure|SurfaceAck|Announce|Incidental|ParentLost|WrongOwner
 var s:State
 pure val initial={created:false,queued:false,sent:false,configured:false,acked:false,announced:false,failed:false,parent:true,owned:true}
 action init=s'=initial
 action fire(e:Event):bool=s'=(match e {
 |Create=>if(s.parent and s.owned and not(s.failed) and not(s.created)){...s,created:true,queued:true}else s
 |FlushSuccess=>if(s.parent and s.owned and not(s.failed) and s.created){...s,queued:false,sent:true}else s
 |FlushNegative=>{...s,failed:true,announced:false}
 |ParentConfigure=>if(s.sent and s.parent and s.owned and not(s.failed)){...s,configured:true}else s
 |SurfaceAck=>if(s.configured and s.parent and s.owned and not(s.failed)){...s,acked:true}else s
 |Announce=>if(s.acked and s.parent and s.owned and not(s.failed)){...s,announced:true}else s
 |Incidental=>if(s.created and s.queued and s.parent and s.owned and not(s.failed)){...s,queued:false,sent:true}else s
 |ParentLost=>{...s,parent:false,failed:true,announced:false}
 |WrongOwner=>{...s,owned:false,failed:true,announced:false}
 })
 val allProps=(s.announced implies s.sent and s.configured and s.acked and s.parent and s.owned and not(s.failed)) and (s.configured implies s.sent) and (s.acked implies s.configured)
 action step={nondet e=Set(Create,FlushSuccess,FlushNegative,ParentConfigure,SurfaceAck,Announce,Incidental,ParentLost,WrongOwner).oneOf();fire(e)}
}
