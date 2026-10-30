module fd_lease {
  // slot, logical allocation epoch and inode remain distinct even on slot reuse.
  type Handle = { slot: int, epoch: int, inode: int, open: bool, owner: str, cloexec: bool }
  type Event = DidBorrowA | DidBorrowB | DidBorrowFail | DidRetireRoot | DidCloseRetiredOriginal | DidUseA | DidCloseA | DidCloseB | DidProbeRegular | DidMaskedObserverHandoff | DidObserve | DidCancelObserver | DidInterruptBeforeRetire | DidInterruptAfterRetire | DidReuseRootSlot | DidRejectStaleClose | DidCloseOldRoot | DidBrokenEnterLongGate | DidBrokenOuterClose | DidBrokenUnmaskedHandoff | DidBrokenStaleIntegerClose
  type State = {events: Set[Event], root: Handle, proc: Handle, aRoot: Handle, aProc: Handle,
    bRoot: Handle, bProc: Handle, probe: Handle, observer: Handle,
    visible: bool, gate: str, bracketed: bool, masked: bool, used: bool,
    staleRejected: bool, interrupted: str, leak: bool, wrongClose: bool }
  val closed: Handle = {slot:0, epoch:0, inode:0, open:false, owner:"none", cloexec:true}
  var s: State
  action init = s' = {events:Set(),root:{slot:1,epoch:1,inode:10,open:true,owner:"root",cloexec:true},
    proc:{slot:2,epoch:1,inode:20,open:true,owner:"root",cloexec:true},
    aRoot:closed,aProc:closed,bRoot:closed,bProc:closed,probe:closed,observer:closed,
    visible:true,gate:"free",bracketed:false,masked:false,used:false,
    staleRejected:false,interrupted:"none",leak:false,wrongClose:false}
  pure def opened(n: int, e: int, ino: int, who: str): Handle =
    {slot:n,epoch:e,inode:ino,open:true,owner:who,cloexec:true}
  pure def shut(h: Handle): Handle = {...h,open:false,owner:"closed"}
  // Both F_DUPFD_CLOEXEC operations and ownership installation are finite gate transitions.
  action borrowA: bool = all {s.visible,s.gate=="free",s.aRoot.epoch==0,s.root.open,s.proc.open,
    s'={...s,events:s.events.union(Set(DidBorrowA)),aRoot:opened(3,1,10,"leaseA"),aProc:opened(4,1,20,"leaseA")}}
  action borrowB: bool = all {s.visible,s.gate=="free",s.bRoot.epoch==0,s.root.open,s.proc.open,
    s'={...s,events:s.events.union(Set(DidBorrowB)),bRoot:opened(6,1,10,"leaseB"),bProc:opened(7,1,20,"leaseB")}}
  // Failed duplication closes any partial duplicate before returning: no owner escapes.
  action borrowFail: bool = all {s.visible,s.gate=="free",not(s.aRoot.open),s'={...s,events:s.events.union(Set(DidBorrowFail))}}
  action retireRoot: bool = all {s.visible,s.gate=="free",s.root.open,s.proc.open,
    s'={...s,events:s.events.union(Set(DidRetireRoot)),visible:false,root:{...s.root,owner:"closing"},proc:{...s.proc,owner:"closing"}}}
  action closeRetiredOriginal: bool = all {not(s.visible),s.root.open,s.proc.open,s.root.owner=="closing",s.proc.owner=="closing",
    s'={...s,events:s.events.union(Set(DidCloseRetiredOriginal)),root:shut(s.root),proc:shut(s.proc)}}
  action useA: bool = all {s.aRoot.open,s.aProc.open,s.aRoot.inode==10,s.aProc.inode==20,
    s'={...s,events:s.events.union(Set(DidUseA)),used:true}}
  action closeA: bool = all {s.aRoot.open,s.aProc.open,
    s'={...s,events:s.events.union(Set(DidCloseA)),aRoot:shut(s.aRoot),aProc:shut(s.aProc)}}
  action closeB: bool = all {s.bRoot.open,s.bProc.open,
    s'={...s,events:s.events.union(Set(DidCloseB)),bRoot:shut(s.bRoot),bProc:shut(s.bProc)}}
  // Abstract a verified regular O_PATH probe; procfs opening follows this inode, never a pathname.
  action probeRegular: bool = all {s.aRoot.open,not(s.probe.open),
    s'={...s,events:s.events.union(Set(DidProbeRegular)),probe:opened(8,1,30,"probe")}}
  action maskedObserverHandoff: bool = all {s.probe.open,s.aProc.open,not(s.observer.open),
    s'={...s,events:s.events.union(Set(DidMaskedObserverHandoff)),observer:opened(9,1,s.probe.inode,"observer"),bracketed:true,masked:true}}
  action observe: bool = all {s.observer.open,s.bracketed,s.observer.inode==s.probe.inode,
    s'={...s,events:s.events.union(Set(DidObserve)),used:true}}
  // Deferred exception reaches the installed bracket and closes only its own descriptor.
  action cancelObserver: bool = all {s.observer.open,s.bracketed,
    s'={...s,events:s.events.union(Set(DidCancelObserver)),observer:shut(s.observer),bracketed:false,masked:false,interrupted:"afterInstall"}}
  action interruptBeforeRetire: bool = all {s.visible,s.gate=="free",s.interrupted=="none",
    s'={...s,events:s.events.union(Set(DidInterruptBeforeRetire)),interrupted:"beforeInvalidate"}}
  action interruptAfterRetire: bool = all {not(s.visible),s.gate=="free",s.interrupted=="none",
    s'={...s,events:s.events.union(Set(DidInterruptAfterRetire)),interrupted:"afterInvalidate"}}
  // Kernel reuses numeric root slot for a distinct allocation; stale old epoch cannot close it.
  action reuseRootSlot: bool = all {not(s.visible),not(s.root.open),s.root.epoch==1,
    s'={...s,events:s.events.union(Set(DidReuseRootSlot)),root:opened(1,2,99,"foreign")}}
  action rejectStaleClose: bool = all {s.root.open,s.root.epoch==2,s.root.owner=="foreign",
    s'={...s,events:s.events.union(Set(DidRejectStaleClose)),staleRejected:true}}
  // Model a close from the retired original allocation, never an integer alone.
  action closeOldRoot: bool = all {s.root.open,s.root.epoch==1,s.root.owner=="closing",not(s.visible),
    s'={...s,events:s.events.union(Set(DidCloseOldRoot)),root:shut(s.root)}}
  // Deliberately broken schedules, excluded from step.
  action brokenEnterLongGate: bool = all {s.visible,s.gate=="free",s'={...s,events:s.events.union(Set(DidBrokenEnterLongGate)),gate:"traversal"}}
  action brokenOuterClose: bool = all {s.visible,s.gate=="traversal",s.root.open,
    s'={...s,events:s.events.union(Set(DidBrokenOuterClose)),root:shut(s.root),proc:shut(s.proc)}}
  action brokenUnmaskedHandoff: bool = all {s.probe.open,s.aProc.open,not(s.observer.open),
    s'={...s,events:s.events.union(Set(DidBrokenUnmaskedHandoff)),observer:opened(9,1,s.probe.inode,"unowned"),leak:true,interrupted:"beforeInstall"}}
  // Deliberately broken integer-only close: excluded from the correct step.
  action brokenStaleIntegerClose: bool = all {not(s.visible),s.root.open,s.root.epoch==2,s.root.owner=="foreign",
    s'={...s,events:s.events.union(Set(DidBrokenStaleIntegerClose)),root:shut(s.root),wrongClose:true}}
  val rootValidity: bool = not(s.visible) or (s.root.open and s.proc.open and s.root.owner=="root" and s.proc.owner=="root")
  val leasePairs: bool = (s.aRoot.open == s.aProc.open) and (s.bRoot.open == s.bProc.open)
  val leaseIdentity: bool = (not(s.aRoot.open) or (s.aRoot.owner=="leaseA" and s.aProc.owner=="leaseA" and s.aRoot.inode==10 and s.aProc.inode==20 and s.aRoot.cloexec and s.aProc.cloexec)) and
    (not(s.bRoot.open) or (s.bRoot.owner=="leaseB" and s.bProc.owner=="leaseB" and s.bRoot.inode==10 and s.bProc.inode==20 and s.bRoot.cloexec and s.bProc.cloexec))
  val observerOwned: bool = not(s.observer.open) or (s.bracketed and s.observer.owner=="observer" and s.probe.open and s.observer.inode==s.probe.inode)
  val finiteGate: bool = s.gate=="free"
  val noLeakOrWrongClose: bool = not(s.leak) and not(s.wrongClose)
  val safety: bool = rootValidity and leasePairs and leaseIdentity and observerOwned and finiteGate and noLeakOrWrongClose
  action step: bool = any {borrowA,borrowB,borrowFail,retireRoot,closeRetiredOriginal,useA,closeA,closeB,probeRegular,maskedObserverHandoff,observe,cancelObserver,interruptBeforeRetire,interruptAfterRetire,reuseRootSlot,rejectStaleClose}
  val reachedBorrowA = s.events.contains(DidBorrowA)
  val reachedBorrowB = s.events.contains(DidBorrowB)
  val reachedBorrowFail = s.events.contains(DidBorrowFail)
  val reachedRetireRoot = s.events.contains(DidRetireRoot)
  val reachedCloseRetiredOriginal = s.events.contains(DidCloseRetiredOriginal)
  val reachedUseA = s.events.contains(DidUseA)
  val reachedCloseA = s.events.contains(DidCloseA)
  val reachedCloseB = s.events.contains(DidCloseB)
  val reachedProbeRegular = s.events.contains(DidProbeRegular)
  val reachedMaskedObserverHandoff = s.events.contains(DidMaskedObserverHandoff)
  val reachedObserve = s.events.contains(DidObserve)
  val reachedCancelObserver = s.events.contains(DidCancelObserver)
  val reachedInterruptBeforeRetire = s.events.contains(DidInterruptBeforeRetire)
  val reachedInterruptAfterRetire = s.events.contains(DidInterruptAfterRetire)
  val reachedReuseRootSlot = s.events.contains(DidReuseRootSlot)
  val reachedRejectStaleClose = s.events.contains(DidRejectStaleClose)
  val reachedCloseOldRoot = s.events.contains(DidCloseOldRoot)
  val reachedBrokenEnterLongGate = s.events.contains(DidBrokenEnterLongGate)
  val reachedBrokenOuterClose = s.events.contains(DidBrokenOuterClose)
  val reachedBrokenUnmaskedHandoff = s.events.contains(DidBrokenUnmaskedHandoff)
  val reachedBrokenStaleIntegerClose = s.events.contains(DidBrokenStaleIntegerClose)
}
