// ELM-UI-006 overview-empty: existing ordinary empty native destination.
// Frontend, host and broker may crash; messages/ACKs may be lost. One
// authenticated native authority serializes mutations. Counters/owners stand
// for exact wire identities; disks, rendering, AT and deadlines are excluded.
module workspaceNavigation {
 type Status = Idle | Pending | Unknown | Committed | Refused
 type State = {status:Status,host:bool,broker:bool,nativeStarted:bool,native:Status,effects:int,active:int,owner:int,context:int,busy:bool,open:bool,frontend:int,reads:int}
 var s:State
 action init=s'={status:Idle,host:false,broker:false,nativeStarted:false,native:Idle,effects:0,active:1,owner:1,context:1,busy:false,open:true,frontend:1,reads:0}
 pure def definitive(status:Status):bool=status==Committed or status==Refused
 pure def eligible(owner:int,context:int,busy:bool):bool=owner==1 and context==1 and not(busy)
 action admit=all{s.status==Idle,s.open,s'={...s,status:Pending,host:true}}
 action reserve=all{s.host,s.status==Pending,not(s.broker),not(s.busy),s'={...s,broker:true}}
 action commit=all{s.host,s.broker,s.status==Pending,not(s.nativeStarted),eligible(s.owner,s.context,s.busy),s'={...s,nativeStarted:true,native:Committed,effects:1,active:2}}
 action refuse=all{s.host,s.broker,s.status==Pending,not(s.nativeStarted),not(eligible(s.owner,s.context,s.busy)),s'={...s,nativeStarted:true,native:Refused}}
 action indeterminate=all{s.host,s.broker,s.status==Pending,not(s.nativeStarted),eligible(s.owner,s.context,s.busy),s'={...s,nativeStarted:true,native:Unknown,effects:1,active:2}}
 action acknowledge=all{s.status==Pending,definitive(s.native),s'={...s,status:s.native}}
 action lostAck=all{s.host,s.status==Pending,s'={...s,status:Unknown}}
 action restart=all{s.host,s.frontend==1,s'={...s,frontend:2,status:if(definitive(s.status)) s.status else Unknown}}
 action read=all{s.status==Unknown,s.reads<2,s'={...s,status:if(definitive(s.native)) s.native else Unknown,reads:s.reads+1}}
 action duplicate=all{s.host,s'=s}
 action foreign=all{s.host,s'=s}
 action retire=all{s.owner==1,not(s.nativeStarted),s'={...s,owner:2}}
 action invalidate=all{s.context==1,not(s.nativeStarted),s'={...s,context:2}}
 action windowBusy=all{not(s.busy),not(s.nativeStarted),s'={...s,busy:true}}
 action dismiss=all{s.open,s'={...s,open:false}}
 action step=any{admit,reserve,commit,refuse,indeterminate,acknowledge,lostAck,restart,read,duplicate,foreign,retire,invalidate,windowBusy,dismiss}
 val safety=s.effects<=1 and (s.nativeStarted implies s.host and s.broker) and (s.status==Committed implies s.native==Committed and s.effects==1 and s.active==2) and (s.status==Refused implies s.native==Refused and s.effects==0 and s.active==1) and (s.effects>0 implies s.nativeStarted)
 val commitWitness=s.status==Committed
 val refusalWitness=s.status==Refused
 val recoveredWitness=s.frontend==2 and s.status==Committed and s.reads>0
 val unknownWitness=s.status==Unknown and s.native==Unknown and s.reads>0 and not(s.open)
}
