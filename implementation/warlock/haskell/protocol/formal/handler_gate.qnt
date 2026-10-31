module handler_gate {
  type Mode = Live | Draining | Retired
  type Lock = Free | Admission
  type Outcome = Normal | ThreadKilled | SyncError
  type Reason = BadSchema | UnsupportedVersion | BadUtf8 | Malformed | GateBusy | GateRetired | HandlerFailed
  // Tokens are bounded ghost identities of caller-owned callbacks, not public capabilities.
  type State = {mode:Mode, count:int, lock:Lock, owner:int, pending:int, active:Set[int],
    entered:Set[int], completed:Set[int], invalidTokens:Set[int], reasons:List[Reason], admitted:int,
    normal:int, interrupted:int, syncErrors:int, ownLockEntries:int}
  var s: State
  val tokenDomain = 1.to(64)
  action init = s'={mode:Live,count:0,lock:Free,owner:0,pending:0,active:Set(),entered:Set(),completed:Set(),invalidTokens:Set(),
    reasons:[],admitted:0,normal:0,interrupted:0,syncErrors:0,ownLockEntries:0}
  // Public rejectionReasons reverses source's newest-first list, yielding oldest to newest.
  pure def retain(xs:List[Reason], reason:Reason): List[Reason] = if(xs.length()<128) xs.append(reason) else xs.tail().append(reason)
  action rejectInvalid(reason:Reason): bool = all {s.lock==Free,Set(BadSchema,UnsupportedVersion,BadUtf8,Malformed).contains(reason),
    s'={...s,reasons:retain(s.reasons,reason)}}
  // The input is assumed to have passed bounded decoding and current-binding checks.
  action beginAdmission(token:int): bool = all {s.lock==Free,s.mode==Live,s.count<64,tokenDomain.contains(token),
    not(s.active.contains(token)),s'={...s,lock:Admission,owner:token,pending:token,entered:s.entered.exclude(Set(token)),completed:s.completed.exclude(Set(token)),invalidTokens:s.invalidTokens.exclude(Set(token))}}
  action publishAdmission: bool = all {s.lock==Admission,s.pending!=0,
    s'={...s,lock:Free,owner:0,active:s.active.union(Set(s.pending)),count:s.count+1,admitted:s.admitted+1,pending:0}}
  action rejectBusy: bool = all {s.lock==Free,s.mode==Live,s.count==64,
    s'={...s,reasons:retain(s.reasons,GateBusy)}}
  action rejectClosed: bool = all {s.lock==Free,s.mode!=Live,
    s'={...s,reasons:retain(s.reasons,GateRetired)}}
  // Callback IO is outside the state MVar, including while a retire occurs.
  action enterCallback(token:int): bool = all {(s.lock==Free or s.owner!=token),s.active.contains(token),not(s.entered.contains(token)),
    s'={...s,entered:s.entered.union(Set(token))}}
  action retire: bool = all {s.lock==Free,
    s'=if(s.mode==Live) {...s,mode:if(s.count==0) Retired else Draining} else s}
  // One completion per callback token abstracts try/finally and the finite masked decrement.
  pure def completeState(old:State, token:int, outcome:Outcome): State =
    {...old,active:old.active.exclude(Set(token)),completed:old.completed.union(Set(token)),count:old.count-1,
      mode:if(old.mode==Draining and old.count==1) Retired else old.mode,
      normal:old.normal+(if(outcome==Normal) 1 else 0),
      interrupted:old.interrupted+(if(outcome==ThreadKilled) 1 else 0),
      syncErrors:old.syncErrors+(if(outcome==SyncError) 1 else 0),
      reasons:if(outcome==Normal) old.reasons else retain(old.reasons,HandlerFailed)}
  action complete(token:int, outcome:Outcome): bool = all {s.lock==Free,s.active.contains(token),
    (outcome!=Normal or s.entered.contains(token)),s'=completeState(s,token,outcome)}
  // Broken variants are excluded from step.
  action brokenDoubleComplete(token:int): bool = all {s.lock==Free,s.completed.contains(token),
    s'={...s,count:s.count-1,normal:s.normal+1}}
  action brokenAdmitInvalid(token:int): bool = all {s.lock==Free,s.mode==Live,s.count<64,tokenDomain.contains(token),not(s.active.contains(token)),
    s'={...s,count:s.count+1,active:s.active.union(Set(token)),admitted:s.admitted+1,invalidTokens:s.invalidTokens.union(Set(token))}}
  // Deliberately broken publication leaves the admitting caller holding its lock.
  action brokenPublishHoldingLock: bool = all {s.lock==Admission,s.pending!=0,
    s'={...s,active:s.active.union(Set(s.pending)),count:s.count+1,admitted:s.admitted+1,pending:0}}
  action brokenEnterOwnLock(token:int): bool = all {s.lock==Admission,s.owner==token,s.active.contains(token),not(s.entered.contains(token)),
    s'={...s,entered:s.entered.union(Set(token)),ownLockEntries:s.ownLockEntries+1}}
  val countOwned: bool = s.count==s.active.size() and s.count>=0 and s.count<=64
  val accounting: bool = s.admitted==s.count+s.normal+s.interrupted+s.syncErrors
  val boundedReasons: bool = s.reasons.length()<=128
  val retiredEmpty: bool = s.mode!=Retired or (s.count==0 and s.active==Set())
  val noCallbackUnderLock: bool = s.ownLockEntries==0
  val enteredOwned: bool = s.entered.subseteq(s.active.union(s.completed))
  val noInvalidAdmission: bool = s.invalidTokens.intersect(s.active.union(s.completed))==Set()
  val safety: bool = noInvalidAdmission and countOwned and accounting and boundedReasons and retiredEmpty and noCallbackUnderLock and enteredOwned
  val witnessAdmitted: bool = s.admitted>0
  val witnessEntered: bool = s.entered.size()>0
  val witnessDraining: bool = s.mode==Draining and s.count>0
  val witnessRetiredAfterWork: bool = s.mode==Retired and s.completed.size()>0
  val witnessBusy: bool = s.count==64 and s.reasons.indices().exists(i => s.reasons.nth(i)==GateBusy)
  val witnessReasonBound: bool = s.reasons.length()==128
  action step: bool = { nondet token=tokenDomain.oneOf() any {rejectInvalid(BadSchema),rejectInvalid(UnsupportedVersion),rejectInvalid(BadUtf8),rejectInvalid(Malformed),beginAdmission(token),publishAdmission,rejectBusy,rejectClosed,enterCallback(token),retire,complete(token,Normal),complete(token,ThreadKilled),complete(token,SyncError)} }
}
