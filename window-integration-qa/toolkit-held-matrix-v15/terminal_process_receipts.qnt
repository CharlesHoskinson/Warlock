module terminal_process_receipts {
 type State={quiesced:bool,queued:int,requested:int,started:int,ended:int,active:int,pid:int,normal:bool,owner:bool,failed:bool,drained:bool}
 type Event=Request|Queue|RequestQueued|Start(int)|Exit(int)|AbnormalExit|MissingStart|Quiesce|Drain|ChangedOwner|ResetEpoch
 var s:State
 pure val initial={quiesced:false,queued:0,requested:0,started:0,ended:0,active:0,pid:0,normal:true,owner:true,failed:false,drained:false}
 action init=s'=initial
 pure def advance(x:State,e:Event):State=(if(x.failed)x else match e {
 |Request=>if(x.quiesced or x.requested>x.ended){...x,failed:true,drained:false}else {...x,requested:x.requested+1}
 |Queue=>if(x.quiesced){...x,failed:true,drained:false}else {...x,queued:x.queued+1}
 |RequestQueued=>if(not(x.quiesced) or x.queued==0 or x.requested>x.ended){...x,failed:true,drained:false}else {...x,queued:x.queued-1,requested:x.requested+1,drained:false}
 |Start(g)=>if(x.requested!=x.started+1 or x.active!=0 or g!=x.requested){...x,failed:true,drained:false}else {...x,started:x.started+1,active:g,pid:42}
 |Exit(g)=>if(x.active!=g or x.pid!=42 or g!=x.ended+1){...x,failed:true,drained:false}else {...x,ended:x.ended+1,active:0,pid:0}
 |AbnormalExit=>{...x,normal:false,failed:true,drained:false}
 |MissingStart=>{...x,failed:true,drained:false}
 |Quiesce=>{...x,quiesced:true}
 |Drain=>if(x.quiesced and x.queued==0 and x.requested==x.started and x.started==x.ended and x.active==0 and x.pid==0 and x.normal and x.owner){...x,drained:true}else x
 |ChangedOwner=>{...x,owner:false,failed:true,drained:false}
 |ResetEpoch=>{...x,failed:true,drained:false}
 })
 action fire(e:Event):bool=s'=advance(s,e)
 val allProps=s.ended<=s.started and s.started<=s.requested and (s.drained implies s.quiesced and s.queued==0 and s.requested==s.started and s.started==s.ended and s.active==0 and s.pid==0 and s.normal and s.owner and not(s.failed))
 action step={nondet e=Set(Request,Queue,RequestQueued,Start(s.requested),Start(0),Exit(s.active),Exit(0),AbnormalExit,MissingStart,Quiesce,Drain,ChangedOwner,ResetEpoch).oneOf();fire(e)}
}
