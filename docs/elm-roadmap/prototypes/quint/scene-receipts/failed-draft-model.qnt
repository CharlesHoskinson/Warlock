/** CPU-only two-window architecture experiment. Input point overlaps both
 * clients; transparent means that point lies outside its input region.
 * Fullscreen policy: eligible fullscreen above ordinary unless pinned.
 * This is an explicit candidate policy, not an upstream/native proof. */
module scene {
  type Scene = { minimized: Set[int], inactive: Set[int], pinned: Set[int], maximized: Set[int], fullscreen: Set[int], transparent: Set[int], proxy: bool, liveReady: bool, locked: bool, gpuReady: bool, lease: bool, focus: int }
  type Event = Minimize(int) | RestoreBegin | LiveReady | Handoff | Inactive(int) | Active(int) | Pin(int) | Maximize(int) | Fullscreen(int) | Transparent(int) | Activate | Capture | Lock | Unlock | DeviceLoss | DeviceRecover
  var s: Scene
  pure val IDS = Set(1,2)
  pure def eligible(st: Scene, id: int): bool = not(st.locked) and not(st.minimized.contains(id)) and not(st.inactive.contains(id))
  pure def band(st: Scene, id: int): int = if (st.pinned.contains(id)) 3 else if (st.fullscreen.contains(id)) 2 else 1
  pure def paintTop(st: Scene): int = if (eligible(st,2) and (not(eligible(st,1)) or band(st,2) >= band(st,1))) 2 else if (eligible(st,1)) 1 else 0
  pure def inputEligible(st: Scene, id: int): bool = eligible(st,id) and not(st.transparent.contains(id))
  pure def inputTop(st: Scene): int = if (inputEligible(st,2) and (not(inputEligible(st,1)) or band(st,2) >= band(st,1))) 2 else if (inputEligible(st,1)) 1 else 0
  pure def proxyHit(st: Scene): bool = false
  pure def normalize(st: Scene): Scene = if (st.focus != 0 and not(inputEligible(st,st.focus))) {...st,focus:0} else st
  action init = s' = {minimized:Set(),inactive:Set(),pinned:Set(),maximized:Set(),fullscreen:Set(),transparent:Set(),proxy:false,liveReady:false,locked:false,gpuReady:true,lease:false,focus:0}
  action fire(e: Event): bool = {
    val next = match e {
      | Minimize(id) => {...s,minimized:s.minimized.union(Set(id)),proxy:false,liveReady:false}
      | RestoreBegin => if (s.minimized.contains(1) and s.lease and not(s.locked)) {...s,proxy:true,liveReady:false} else s
      | LiveReady => if (s.proxy and s.gpuReady and not(s.locked)) {...s,liveReady:true} else s
      | Handoff => if (s.proxy and s.liveReady and s.lease and not(s.locked)) {...s,minimized:s.minimized.exclude(Set(1)),proxy:false,liveReady:false} else s
      | Inactive(id) => {...s,inactive:s.inactive.union(Set(id))}
      | Active(id) => {...s,inactive:s.inactive.exclude(Set(id))}
      | Pin(id) => {...s,pinned:s.pinned.union(Set(id))}
      | Maximize(id) => {...s,maximized:s.maximized.union(Set(id))}
      | Fullscreen(id) => {...s,fullscreen:s.fullscreen.union(Set(id))}
      | Transparent(id) => {...s,transparent:s.transparent.union(Set(id))}
      | Activate => {...s,focus:inputTop(s)}
      | Capture => if (s.gpuReady and not(s.locked)) {...s,lease:true} else s
      | Lock => {...s,locked:true,lease:false,proxy:false,liveReady:false}
      | Unlock => {...s,locked:false}
      | DeviceLoss => {...s,gpuReady:false,lease:false,proxy:false,liveReady:false}
      | DeviceRecover => {...s,gpuReady:true}
    }
    s' = normalize(next)
  }
  pure val EVENTS = Set(Minimize(1),Minimize(2),RestoreBegin,LiveReady,Handoff,Inactive(1),Inactive(2),Active(1),Active(2),Pin(1),Pin(2),Maximize(1),Maximize(2),Fullscreen(1),Fullscreen(2),Transparent(1),Transparent(2),Activate,Capture,Lock,Unlock,DeviceLoss,DeviceRecover)
  action step = { nondet e = EVENTS.oneOf(); fire(e) }
  val noExcludedPaint = paintTop(s) == 0 or (not(s.locked) and not(s.minimized.contains(paintTop(s))) and not(s.inactive.contains(paintTop(s))))
  val noExcludedInput = inputTop(s) == 0 or (not(s.locked) and not(s.minimized.contains(inputTop(s))) and not(s.inactive.contains(inputTop(s))) and not(s.transparent.contains(inputTop(s))))
  val focusSafe = s.focus == 0 or inputEligible(s,s.focus)
  val proxyInert = not(proxyHit(s))
  val leaseValid = not(s.lease) or (s.gpuReady and not(s.locked))
  val proxyValid = not(s.proxy) or (s.minimized.contains(1) and s.lease and s.gpuReady and not(s.locked))
  val allProps = noExcludedPaint and noExcludedInput and focusSafe and proxyInert and leaseValid and proxyValid
}
