// ELM-UI-008 / overflow-resize: identity/order and reachable active selection.
// One Elm reducer observes native topology and exact popup callbacks. Native
// geometry retires input before callbacks; location alone changes no view grant.
// Scope: output routing and presentation leases, not native geometry/action
// validation, preview custody, actual pixels, AT, transport or UInt64 exhaustion.
module popup_location_reflow {
  type State = {revision:int, generation:int, authority:int, width:int,
    ready:bool, refused:bool, exhausted:bool, open:bool, lease:int,
    inputLease:int, choice:int, order:List[int], observations:int, effects:int,
    reflows:int}
  var s:State
  action init = s'={revision:1,generation:1,authority:1,width:480,
    ready:true,refused:false,exhausted:false,open:true,lease:1,inputLease:1,
    choice:10,order:List(1,2,3,4,5,6,7,8,9,10),observations:0,effects:0,reflows:0}
  val safety = s.effects==0 and s.choice==10 and
    s.order==List(1,2,3,4,5,6,7,8,9,10) and
    (not(s.open) or (s.ready and s.generation==s.authority)) and
    (s.inputLease==0 or s.inputLease==s.lease)
  pure def canLocate(st:State):bool = st.ready and not(st.refused) and not(st.exhausted)
  pure def locate(st:State,w:int):State = {...st,revision:st.revision+1,width:w,inputLease:0}
  pure def canReflow(st:State,g:int,l:int):bool = st.open and st.generation==g and st.lease==l and not(st.exhausted)
  pure def reflow(st:State):State = {...st,lease:st.lease+1,inputLease:st.lease+1,reflows:st.reflows+1}
  action location(w:int):bool = all { canLocate(s), s'=locate(s,w) }
  action currentReflow(g:int,l:int):bool = all { canReflow(s,g,l), s'=reflow(s) }
  action rejectedCallback(g:int,l:int):bool = all { not(canReflow(s,g,l)), s'=s }
  action replace = s'={...s,revision:s.revision+1,generation:s.generation+1,
    authority:s.authority+1,ready:false,open:false,inputLease:0,observations:s.observations+1}
  action refuse = s'={...s,refused:true,ready:false,open:false,inputLease:0}
  action exhaust = s'={...s,exhausted:true,ready:false,open:false,inputLease:0}
  action unready = s'={...s,ready:false,open:false,inputLease:0}
  action fullTopology = all {not(canLocate(s)),
    s'={...s,revision:s.revision+1,observations:s.observations+1,open:false,inputLease:0}}
  val resizedAndReflowed = s.open and s.width==640 and s.reflows>0 and s.observations==0
  val grownAndShrunk = s.open and s.width==480 and s.reflows>=2 and s.observations==0
  val replacementRetired = s.generation>1 and not(s.open) and not(s.ready) and s.observations>0
  val refusalRetained = s.refused and not(s.ready) and not(s.open)
  action step = any {location(640),location(480),currentReflow(s.generation,s.lease),
    rejectedCallback(s.generation-1,s.lease),rejectedCallback(s.generation,s.lease-1),
    replace,refuse,exhaust,unready,fullTopology,s'=s}
}
