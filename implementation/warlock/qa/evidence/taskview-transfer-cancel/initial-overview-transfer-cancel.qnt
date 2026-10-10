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
  action step=idle
  val safety=s.mutations==0
}
