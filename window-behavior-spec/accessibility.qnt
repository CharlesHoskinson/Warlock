/** Assistive action ownership and lifecycle. UI tickets stand for native AX nodes. */
module accessibility {
  type Command = RestoreWindow | MinimizeWindow | TogglePin | CloseWindow
  type Window = {live:bool, identity:int, pid:int, minimized:bool, pinned:bool}
  type Ticket = {surface:int, epoch:int, address:int, identity:int, pid:int, command:Command}
  type Event = Show(int) | Hide | Rebuild | Select(int) | Enable(bool)
    | Capture((int,Command)) | CaptureWrongPid(int) | Invoke | Focus(int)
    | Close(int) | Open(int)
  type State = {
    windows:int -> Window, visible:bool, enabled:bool, surface:int, epoch:int,
    selected:int, focus:int, ticket:Ticket,
    invoked:bool, accepted:bool, before:int -> Window, focusBefore:int
  }
  var s: State
  pure val ADDRESSES = Set(1,2)
  pure val initialWindows = Map(
    1 -> {live:true,identity:1,pid:101,minimized:false,pinned:false},
    2 -> {live:true,identity:1,pid:102,minimized:false,pinned:false})
  pure def allowed(state:State):bool = state.visible and state.enabled
    and state.ticket.surface == state.surface and state.ticket.epoch == state.epoch
    and ADDRESSES.contains(state.ticket.address)
    and state.windows.get(state.ticket.address).live
    and state.ticket.identity == state.windows.get(state.ticket.address).identity
    and state.ticket.pid == state.windows.get(state.ticket.address).pid
  pure def capture(state:State,address:int,command:Command):Ticket = {
    surface:state.surface,epoch:state.epoch,address:address,
    identity:state.windows.get(address).identity,pid:state.windows.get(address).pid,
    command:command}
  action init = s' = {
    windows:initialWindows,visible:false,enabled:true,surface:1,epoch:0,
    selected:1,focus:1,
    ticket:{surface:1,epoch:0,address:1,identity:1,pid:101,command:RestoreWindow},
    invoked:false,accepted:false,before:initialWindows,focusBefore:1}
  action fire(event:Event):bool = {
    val base = {...s,invoked:false,accepted:false,before:s.windows,focusBefore:s.focus}
    s' = match event {
      | Show(surface) => {...base,visible:true,enabled:true,surface:surface,epoch:if(surface==s.surface)s.epoch else s.epoch+1,selected:1}
      | Hide => {...base,visible:false}
      | Rebuild => {...base,epoch:s.epoch+1}
      | Select(address) => {...base,selected:address}
      | Enable(isEnabled) => {...base,enabled:isEnabled}
      | Capture(payload) => {...base,ticket:capture(s,payload._1,payload._2)}
      | CaptureWrongPid(address) => {...base,ticket:{...capture(s,address,RestoreWindow),pid:s.windows.get(address).pid+1}}
      | Focus(address) => if(s.windows.get(address).live and not(s.windows.get(address).minimized)) {...base,focus:address} else base
      | Close(address) => {...base,windows:s.windows.setBy(address,w=>{...w,live:false}),focus:if(s.focus==address)0 else s.focus}
      | Open(address) => if(s.windows.get(address).live) base else {...base,windows:s.windows.setBy(address,w=>{...w,live:true,identity:w.identity+1,minimized:false,pinned:false})}
      | Invoke => if (allowed(s)) {
          val target = s.ticket.address
          val window = s.windows.get(target)
          val command = s.ticket.command
          val updated = match command {
            | RestoreWindow => {...window,minimized:false}
            | MinimizeWindow => {...window,minimized:true}
            | TogglePin => {...window,pinned:not(window.pinned)}
            | CloseWindow => {...window,live:false}
          }
          val focus = match command {
            | RestoreWindow => target
            | MinimizeWindow => if(s.focus==target)0 else s.focus
            | CloseWindow => if(s.focus==target)0 else s.focus
            | TogglePin => s.focus
          }
          {...base,invoked:true,accepted:true,windows:s.windows.set(target,updated),focus:focus}
        } else {...base,invoked:true}
    }
  }
  action step = {
    nondet event = Set(Show(1),Show(2),Show(3),Hide,Rebuild,Select(1),Select(2),Enable(true),Enable(false),
      Capture((1,RestoreWindow)),Capture((2,RestoreWindow)),Capture((1,MinimizeWindow)),Capture((2,MinimizeWindow)),
      Capture((1,TogglePin)),Capture((2,TogglePin)),Capture((1,CloseWindow)),Capture((2,CloseWindow)),
      CaptureWrongPid(1),CaptureWrongPid(2),Invoke,Focus(1),Focus(2),Close(1),Close(2),Open(1),Open(2)).oneOf()
    fire(event)
  }
  val rejectedActionsSafe = (s.invoked and not(s.accepted)) implies (s.windows==s.before and s.focus==s.focusBefore)
  val capturedOwnerOnly = (s.invoked and s.accepted) implies ADDRESSES.exclude(Set(s.ticket.address)).forall(a=>s.windows.get(a)==s.before.get(a))
  val liveFocus = s.focus==0 or (ADDRESSES.contains(s.focus) and s.windows.get(s.focus).live and not(s.windows.get(s.focus).minimized))
  val boundedSelection = ADDRESSES.contains(s.selected)
  val allProps = rejectedActionsSafe and capturedOwnerOnly and liveFocus and boundedSelection
}
