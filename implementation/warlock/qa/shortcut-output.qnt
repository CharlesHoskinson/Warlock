// ELM-UX-023 / ux-023 and ELM-UI-005 / search-no-match support.
// One native/host/Elm event thread, two outputs, explicit independent topology updates.
// Integer logical boxes abstract native/GDK advertised bounds. No pixels/AT/hardware proof.
module shortcut_output {
 type State = {native: int->int,host: int->int,inc: int->int,live:Set[int],capture:int,capturedInc:int,box:int,event:int,seen:int,owner:int,blocked:bool,opened:int,proofFresh:bool,proofLive:bool,proofUnique:bool,effects:int,refused:int}
 var s:State
 action init=s'={native:Map(0->0,1->10,2->20),host:Map(1->10,2->20),inc:Map(0->0,1->1,2->1),live:Set(1,2),capture:0,capturedInc:0,box:0,event:0,seen:0,owner:1,blocked:false,opened:0,proofFresh:false,proofLive:false,proofUnique:false,effects:0,refused:0}
 val safety=s.effects==0 and (s.opened==0 or (s.proofFresh and s.proofLive and s.proofUnique))
 pure def matches(st:State,b:int):Set[int]=st.live.filter(i=>st.host.get(i)==b)
 val liveCapture=s.live.contains(s.capture) and s.inc.get(s.capture)==s.capturedInc and s.native.get(s.capture)==s.box
 action press(i:int):bool=all{s.live.contains(i),not(s.blocked),s'={...s,capture:i,capturedInc:s.inc.get(i),box:s.native.get(i),event:s.event+1}}
 action receive=all{s.event>s.seen,
  val ms=matches(s,s.box)
  val accepted=not(s.blocked) and liveCapture and ms.size()==1
  s'={...s,seen:s.event,owner:if(accepted) (if(ms.contains(1)) 1 else 2) else s.owner,opened:if(accepted) s.opened+1 else s.opened,refused:if(accepted) s.refused else s.refused+1,proofFresh:if(accepted) s.event>s.seen else s.proofFresh,proofLive:if(accepted) liveCapture else s.proofLive,proofUnique:if(accepted) ms.size()==1 else s.proofUnique}}
 action retire(i:int):bool=all{s.live.contains(i),s'={...s,live:s.live.exclude(Set(i)),owner:if(s.owner==i) 0 else s.owner}}
 action replace(i:int):bool=all{s.live.contains(i),s'={...s,inc:s.inc.set(i,s.inc.get(i)+1)}}
 action moveNative(i:int):bool=all{s.live.contains(i),s'={...s,native:s.native.set(i,s.native.get(i)+10)}}
 action mirror=s'={...s,host:s.host.set(1,20)}
 action block=s'={...s,blocked:true}
 val rightOpened=s.owner==2 and s.opened>0
 val retiredRejected=not(s.live.contains(2)) and s.capture==2 and s.refused>0 and s.opened==0
 val ambiguousRejected=matches(s,20).size()==2 and s.capture==2 and s.refused>0 and s.opened==0
 val blockedRejected=s.blocked and s.refused>0 and s.opened==0
 action step={nondet i=oneOf(Set(1,2));any{press(i),receive,retire(i),replace(i),moveNative(i),mirror,block,s'=s}}

}
