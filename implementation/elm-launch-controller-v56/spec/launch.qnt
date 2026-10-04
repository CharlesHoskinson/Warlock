module launch {
 type State={revision:int,shown:int,request:int,phase:str,connected:bool,catalog:bool,timer:int,ack:int,callback:int,emitted:bool}
 var s:State
 action init=s'={revision:1,shown:1,request:0,phase:"Idle",connected:true,catalog:true,timer:0,ack:0,callback:0,emitted:false}
 action chooseCurrent=s'={...s,shown:s.revision,emitted:false}
 action invalidate=s'={...s,revision:s.revision+1,emitted:false}
 action start=all{s.connected,s.catalog,s.shown==s.revision,Set("Idle","Submitted","Refused").contains(s.phase),s'={...s,request:s.request+1,revision:s.revision+1,phase:"Pending",callback:s.revision,emitted:true}}
 action ignore=s'={...s,emitted:false}
 action arm=all{s.phase=="Pending",s'={...s,timer:s.request,emitted:false}}
 action settle(result:str):bool=all{s.phase=="Pending",s'={...s,phase:result,revision:s.revision+1,emitted:false}}
 action expire=all{s.phase=="Pending",s'={...s,phase:if(s.timer==s.request) "Unknown" else "Pending",revision:s.revision+(if(s.timer==s.request) 1 else 0),emitted:false}}
 action capture=all{s.phase=="Unknown",s'={...s,ack:s.request,emitted:false}}
 action acknowledge=all{s.phase=="Unknown",s'={...s,phase:if(s.ack==s.request) "Idle" else "Unknown",revision:s.revision+(if(s.ack==s.request) 1 else 0),emitted:false}}
 action disconnect=s'={...s,phase:if(s.phase=="Pending") "Unknown" else s.phase,connected:false,catalog:false,revision:s.revision+1,emitted:false}
 action reconnect=s'={...s,connected:true,catalog:true,revision:s.revision+1,emitted:false}
 action step=any{chooseCurrent,invalidate,start,ignore,arm,settle("Submitted"),settle("Refused"),settle("Unknown"),expire,capture,acknowledge,disconnect,reconnect}
 val safety=all{s.request>=0,s.emitted implies s.phase=="Pending" and s.connected and s.catalog and s.callback==s.revision-1,not(s.connected) implies s.phase!="Pending",s.timer<=s.request,s.ack<=s.request}
 run pendingTest=init.then(start).then(all{assert(s.phase=="Pending" and s.request==1),s'=s})
 run staleSelectionTest=init.then(invalidate).then(ignore).then(all{assert(s.request==0 and not(s.emitted)),s'=s})
 run uncertaintyTest=init.then(start).then(arm).then(expire).then(all{assert(s.phase=="Unknown"),s'=s})
 run disconnectTest=init.then(start).then(disconnect).then(reconnect).then(all{assert(s.phase=="Unknown" and s.request==1),s'=s})
 run retiredTimerTest=init.then(start).then(arm).then(settle("Submitted")).then(chooseCurrent).then(start).then(expire).then(all{assert(s.phase=="Pending" and s.request==2),s'=s})
 run retiredAckTest=init.then(start).then(settle("Unknown")).then(capture).then(acknowledge).then(chooseCurrent).then(start).then(settle("Unknown")).then(acknowledge).then(all{assert(s.phase=="Unknown" and s.request==2),s'=s})
 run freshActionTest=init.then(start).then(settle("Submitted")).then(chooseCurrent).then(start).then(all{assert(s.request==2 and s.phase=="Pending"),s'=s})
 run acknowledgementTest=init.then(start).then(settle("Unknown")).then(capture).then(acknowledge).then(all{assert(s.phase=="Idle" and s.request==1),s'=s})
}
