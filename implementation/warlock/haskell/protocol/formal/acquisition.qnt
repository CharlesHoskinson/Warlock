module acquisition {
  type Phase = NoShell | Empty | Pending | SettingUp | Live | Failed | Stopped
  type Endpoint = NoEndpoint | Open | Closing | Confirmed | Uncertain
  type Fault = NoFault | SyncFault | AsyncFault
  type TransferResult = TransferPending | TransferReturned | TransferInterrupted
  type ActivationResult = ActivationPending | ActivationReturned | ThrownOriginalSync | ThrownOriginalAsync | ThrownCleanupSync | ThrownCleanupAsync
  type SelectedBranch = NotSelected | SuccessfulBranch | CleanupBranch
  // Resource IDs are logical identities, not numerical FDs or capabilities.
  type State = {phase:Phase, endpoint:Endpoint, retained:bool, accepted:bool,
    caller:Set[int], held:Set[int], objectId:int, lease:bool, retireRequested:bool,
    gateRetired:bool, attempts:int, setupFault:Fault, closeFault:Fault,
    transferResult:TransferResult, activationResult:ActivationResult, activationStarted:bool,selectedBranch:SelectedBranch, rejectedOffers:int, prepareFailures:int, abandoned:bool}
  var s: State
  val resources = Set(1,2)
  action init = s'={phase:NoShell,endpoint:NoEndpoint,retained:false,accepted:false,
    caller:resources,held:Set(),objectId:0,lease:false,retireRequested:false,
    gateRetired:false,attempts:0,setupFault:NoFault,closeFault:NoFault,
    transferResult:TransferPending,activationResult:ActivationPending,activationStarted:false,selectedBranch:NotSelected,rejectedOffers:0,prepareFailures:0,abandoned:false}
  pure def published(old:State, objectId:int):State =
    {...old,phase:Pending,endpoint:Open,accepted:true,caller:old.caller.exclude(Set(objectId)),
      held:old.held.union(Set(objectId)),objectId:objectId}
  pure def setupFinished(old:State, fault:Fault):State =
    {...old,lease:false,setupFault:fault,
      selectedBranch:if(fault==NoFault and not(old.retireRequested)) SuccessfulBranch else CleanupBranch,
      phase:if(fault!=NoFault) Failed else if(old.retireRequested) Stopped else Live}
  pure def preferred(original:Fault, cleanup:Fault):ActivationResult =
    if(original==AsyncFault) ThrownOriginalAsync
    else if(cleanup==AsyncFault) ThrownCleanupAsync
    else if(original==SyncFault) ThrownOriginalSync
    else if(cleanup==SyncFault) ThrownCleanupSync else ActivationReturned
  // Historical v1 single-result guard, included only to expose its disabled trace.
  pure def v1DeliverWouldBeEnabled(transfer:TransferResult):bool = transfer==TransferPending
  action prepareFailure:bool = all {s.phase==NoShell,s'={...s,prepareFailures:s.prepareFailures+1}}
  action prepare:bool = all {s.phase==NoShell,s'={...s,phase:Empty,retained:true}}
  // Under exclusive one-offer caller discipline this is the masked publication point.
  action offer(objectId:int):bool = all {s.retained,s.phase==Empty,not(s.accepted),s.caller.contains(objectId),
    s'=published(s,objectId)}
  action rejectOffer(objectId:int):bool = all {s.retained,s.phase!=Empty,s.caller.contains(objectId),
    s'={...s,rejectedOffers:s.rejectedOffers+1}}
  action interruptBeforeOffer:bool = all {s.retained,s.phase==Empty,not(s.accepted),s.transferResult==TransferPending,
    s'={...s,transferResult:TransferInterrupted}}
  action interruptAfterOffer:bool = all {s.phase==Pending,s.accepted,s.transferResult==TransferPending,
    s'={...s,transferResult:TransferInterrupted}}
  action transferReturned:bool = all {s.phase==Pending,s.accepted,s.transferResult==TransferPending,
    s'={...s,transferResult:TransferReturned}}
  action beginSetup:bool = all {s.phase==Pending,s.endpoint==Open,
    s'={...s,phase:SettingUp,lease:true,activationStarted:true}}
  action finishSetup(fault:Fault):bool = all {s.phase==SettingUp,s.lease,not(s.abandoned),
    s'=setupFinished(s,fault)}
  // Retirement stops admission first. While setup is borrowed it only marks a request.
  action requestRetire:bool = all {s.retained,not(s.retireRequested),
    s'={...s,retireRequested:true,
      phase:if(s.phase==SettingUp) SettingUp else Stopped}}
  action retireGate:bool = all {s.retained,s.retireRequested,not(s.gateRetired),s'={...s,gateRetired:true}}
  action repeatRetire:bool = all {s.retained,s.retireRequested,(s.lease or not(s.accepted) or s.endpoint!=Open),s'=s}
  action claimClose:bool = all {s.accepted,not(s.lease),s.endpoint==Open,
    (s.phase==Failed or s.retireRequested),s'={...s,endpoint:Closing,attempts:s.attempts+1}}
  action closeResult(fault:Fault):bool = all {s.endpoint==Closing,
    s'={...s,endpoint:if(fault==NoFault) Confirmed else Uncertain,closeFault:fault}}
  // Completion can throw, but the previously retained owner remains inspectable.
  action deliver:bool = all {s.retained,s.activationStarted,s.activationResult==ActivationPending,
    ((s.phase==Live and not(s.retireRequested)) or
     ((s.phase==Failed or s.retireRequested) and
       (not(s.accepted) or s.endpoint==Confirmed or s.endpoint==Uncertain))),
    s'={...s,activationResult:if(s.selectedBranch==SuccessfulBranch) ActivationReturned else preferred(s.setupFault,s.closeFault)}}
  // Excluded fault-injection variants, used only by separate counterexample tests.
  action brokenSetupHandoff:bool = all {s.phase==SettingUp,s.lease,s'={...s,abandoned:true}}
  action brokenConsumeBeforeShell:bool = all {s.phase==NoShell,s.caller.contains(1),
    s'={...s,caller:s.caller.exclude(Set(1)),objectId:1}}
  action brokenCloseDuringSetup:bool = all {s.lease,s.endpoint==Open,
    s'={...s,endpoint:Closing,attempts:s.attempts+1}}
  action brokenRetryUncertain:bool = all {s.endpoint==Uncertain,
    s'={...s,endpoint:Closing,attempts:s.attempts+1}}
  action brokenConsumeSecond:bool = all {s.accepted,s.caller.contains(2),
    s'={...s,caller:s.caller.exclude(Set(2)),held:s.held.union(Set(2))}}
  action brokenGateMeansClosed:bool = all {s.gateRetired,s.endpoint==Uncertain,
    s'={...s,endpoint:Confirmed}}
  // A later retirement caller cannot change an already-selected success return.
  action brokenForeignCloseStealsSuccess:bool = all {s.selectedBranch==SuccessfulBranch,s.closeFault==AsyncFault,
    s'={...s,activationResult:ThrownCleanupAsync}}
  val successfulBranchReturns:bool = s.selectedBranch!=SuccessfulBranch or
    s.activationResult==ActivationPending or s.activationResult==ActivationReturned
  val ownerCustody:bool = s.caller.union(s.held)==resources and s.caller.intersect(s.held)==Set() and
    (s.held==Set() or (s.retained and s.accepted and s.held==Set(s.objectId)))
  val noCloseDuringLease:bool = not(s.lease and s.endpoint==Closing)
  val oneClose:bool = s.attempts<=1
  val uncertaintySticky:bool = s.closeFault==NoFault or s.endpoint==Uncertain
  val acceptedOwnsOne:bool = not(s.accepted) or (s.retained and s.held==Set(s.objectId))
  val activeSetupConsistent:bool = s.lease==(s.phase==SettingUp)
  val noAbandonedSetup:bool = not(s.abandoned)
  val safety:bool = successfulBranchReturns and noAbandonedSetup and ownerCustody and noCloseDuringLease and oneClose and uncertaintySticky and acceptedOwnsOne and activeSetupConsistent
  val witnessPending:bool = s.accepted and s.phase==Pending
  val witnessLive:bool = s.phase==Live
  val witnessSetupFailure:bool = s.setupFault!=NoFault
  val witnessUncertain:bool = s.endpoint==Uncertain
  val witnessConfirmed:bool = s.endpoint==Confirmed
  val witnessDeferred:bool = s.lease and s.retireRequested
  action step:bool = { nondet objectId=resources.oneOf() nondet fault=Set(NoFault,SyncFault,AsyncFault).oneOf()
    any {prepareFailure,prepare,offer(objectId),rejectOffer(objectId),interruptBeforeOffer,interruptAfterOffer,transferReturned,beginSetup,finishSetup(fault),
      requestRetire,retireGate,repeatRetire,claimClose,closeResult(fault),deliver} }
}
