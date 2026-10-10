module overviewRetirement {
  // ELM-UI-006 overview-retire; Desktop.syncOverviewWorkspace.
  // Coherent means the existing exact action/geometry/inventory join passed.
  // No clocks, native dispatch, visual focus or AT verdict are modeled here.
  type State={open:bool,coherent:bool,transfer:int,selected:int,live:Set[int],workspaces:Set[int],focus:int,focusCommands:int,mutations:int}
  var s:State
  action init=s'={open:true,coherent:true,transfer:7,selected:2,live:Set(7,8),workspaces:Set(1,2),focus:0,focusCommands:0,mutations:0}
  action idle=s'=s
  pure def reconcile(state:State):State={
    val workspaceRetired=state.selected>0 and not(state.workspaces.contains(state.selected))
    val memberRetired=state.transfer>0 and not(state.live.contains(state.transfer))
    val target=if(workspaceRetired) 0 else state.selected
    if(state.open and state.coherent and (workspaceRetired or memberRetired))
      {...state,transfer:0,selected:target,focus:target,focusCommands:state.focusCommands+1}
    else state
  }
  action retireMember=all{s.live.contains(7),s'={...s,live:Set(8),coherent:true}}
  action incoherentRetirement=all{s.live.contains(7),s'={...s,live:Set(8),coherent:false}}
  action becomeCoherent=all{not(s.coherent),s'={...s,coherent:true}}
  action retireWorkspace=all{s.workspaces.contains(2),s'={...s,workspaces:Set(1),live:Set(8),coherent:true}}
  action sync=s'=reconcile(s)
  action close=all{s.open,s'={...s,open:false,transfer:0,selected:0}}
  action replace=all{s.open,s'={...s,open:false,coherent:false,transfer:0,selected:0,live:Set(8)}}
  action step=any{idle,retireMember,incoherentRetirement,becomeCoherent,retireWorkspace,sync,close,replace}
  // Two distinct retirements may each move UI focus: member, then workspace.
  // Duplicate sync remains inert (named test); neither retirement acts natively.
  val safety=s.mutations==0 and Set(0,1,2).contains(s.focus) and s.focusCommands<=2 and Set(0,7).contains(s.transfer)
  val filterReturnWitness=s.open and s.transfer==0 and s.focus==2 and s.focusCommands==1
  val allReturnWitness=s.open and s.transfer==0 and s.selected==0 and s.focusCommands==1
  val incoherentHeldWitness=not(s.coherent) and s.transfer==7 and s.focusCommands==0
}
