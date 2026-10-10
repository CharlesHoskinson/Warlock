module overviewTransferCancel {
  // ELM-UI-006 overview-cancel: Desktop.CancelOverviewTransfer and
  // Surface's same exact eligible Move control. One immutable UI reducer.
  // Revision abstracts the captured current presentation/binding stamp.
  // Coherence abstracts the existing action/geometry/inventory exact join.
  // Native opener restoration, real pixels/keyboard, AT and timing are separate.
  type State={open:bool,transfer:int,selected:int,workspaces:Set[int],live:Set[int],available:bool,coherent:bool,capable:bool,ready:bool,blocked:bool,revision:int,focus:int,focusCommands:int,lastOriginEligible:bool,mutations:int}
  var s:State
  action init=s'={open:true,transfer:7,selected:2,workspaces:Set(1,2),live:Set(7,8),available:true,coherent:true,capable:true,ready:true,blocked:false,revision:1,focus:0,focusCommands:0,lastOriginEligible:false,mutations:0}
  action idle=s'=s
  pure def originEligible(state:State):bool=
    state.coherent and state.ready and state.capable and not(state.blocked) and state.available and
    state.live.contains(7) and (state.selected==0 or state.selected==2)
  pure def cancelled(state:State,stamp:int):State=
    if(not(state.open) or state.transfer==0 or stamp!=state.revision) state
    else {
      val eligible=originEligible(state)
      val filterPresent=state.coherent and state.selected>0 and state.workspaces.contains(state.selected)
      {...state,transfer:0,revision:state.revision+1,focus:if(eligible) 7 else if(filterPresent) state.selected else 0,focusCommands:state.focusCommands+1,lastOriginEligible:eligible}
    }
  action cancel=s'=cancelled(s,s.revision)
  action staleCancel=s'=cancelled(s,s.revision-1)
  pure def dismissed(state:State,stamp:int):State=
    if(not(state.open) or stamp!=state.revision) state
    else if(state.transfer>0) cancelled(state,stamp)
    else {...state,open:false,revision:state.revision+1}
  action escape=s'=dismissed(s,s.revision)
  action unavailable=s'={...s,available:false}
  action retire=s'={...s,live:Set(8)}
  action incoherent=s'={...s,coherent:false}
  action reserve=s'={...s,blocked:true}
  action removeCapability=s'={...s,capable:false}
  action unready=s'={...s,ready:false}
  action filterOther=s'={...s,selected:1}
  action filterAll=s'={...s,selected:0}
  action retireWorkspace=s'={...s,workspaces:Set(1),live:Set(8)}
  action close=s'={...s,open:false,transfer:0,revision:s.revision+1}
  action replaceScope=s'={...s,coherent:false,transfer:0,revision:s.revision+1}
  action step=any{idle,cancel,staleCancel,escape,unavailable,retire,incoherent,reserve,removeCapability,unready,filterOther,filterAll,retireWorkspace,close,replaceScope}
  // Focus eligibility is evidence at emission, not a timeless assertion about
  // the environment after it changes. A retired incarnation never substitutes.
  val safety=s.mutations==0 and Set(0,1,2,7).contains(s.focus) and s.focusCommands<=1 and (s.focus==7 implies s.lastOriginEligible)
  val originReturnWitness=s.transfer==0 and s.focus==7 and s.focusCommands==1
  val filterReturnWitness=s.transfer==0 and s.focus==2 and s.focusCommands==1
  val allReturnWitness=s.transfer==0 and s.focus==0 and s.focusCommands==1
  val staleHeldWitness=s.transfer==7 and s.focusCommands==0
  val fullDismissalWitness=not(s.open) and s.transfer==0 and s.focusCommands==1
}
