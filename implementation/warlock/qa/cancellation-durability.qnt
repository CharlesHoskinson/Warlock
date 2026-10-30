// V7 abstract shared-envelope design; SOURCE PROPOSAL, UNVALIDATED.
module CancellationDurability {
  type Stage = Empty | Reserved | PrepareAttempt | Prepared | CommitAttempt | CancelAttempt | Uncertain | TerminalStored | AdmissionRetired | AckPending | Acknowledged
  type Native = NativeAbsent | NativePrepared | NativeCommitted | NativeRefused | NativeCancelled | NativeUnknown
  type Writer = Idle | Temp | Synced | Renamed
  type Operation = NoOperation | PrepareOperation | CommitOperation | CancelOperation | QueryOperation
  type Entry = {key:int, binding:int, target:int, deadline:int, pid:int, file:bool, live:bool,
    absenceSynced:bool, visible:Stage, durable:Stage, native:Native, preparedEvidence:bool,
    terminalEvidence:bool, ackEvidence:bool, commitAttempted:bool, visibleCommitAttempted:bool, lastOperation:Operation,
    nativeAck:int, mutations:int, sendsPrepare:int, sendsCommit:int, sendsCancel:int}
  type State = {a:Entry,b:Entry, writer:Writer, writeKey:int, wanted:Stage, poisoned:bool,
    wantedOperation:Operation, everCommitA:bool, everCommitB:bool, currentGrant:int, oldV6:int, sidecar:int, migrationValidated:bool, predecessorValid:bool, markerValid:bool, autoReplay:int}
  var s:State
  pure def entry(x:State,k:int):Entry = if(k==1) x.a else x.b
  pure def replaceEntry(x:State,k:int,e:Entry):State = if(k==1) {...x,a:e} else {...x,b:e}
  pure def validKey(k:int):bool = k==1 or k==2
  pure def terminal(n:Native):bool = n==NativeCommitted or n==NativeRefused or n==NativeCancelled
  pure def writeAllowed(x:State,k:int):bool = validKey(k) and not(x.poisoned) and x.migrationValidated and x.predecessorValid and x.markerValid and x.writer==Idle
  // Metadata classes represent complete authenticated peer/binding/protocol/intent and certificate fields.
  action init = s'={a:{key:1,binding:1,target:1,deadline:100,pid:11,file:false,live:false,absenceSynced:true,visible:Empty,durable:Empty,native:NativeAbsent,preparedEvidence:false,terminalEvidence:false,ackEvidence:false,commitAttempted:false,visibleCommitAttempted:false,lastOperation:NoOperation,nativeAck:0,mutations:0,sendsPrepare:0,sendsCommit:0,sendsCancel:0},
    b:{key:2,binding:1,target:2,deadline:200,pid:22,file:false,live:false,absenceSynced:true,visible:Empty,durable:Empty,native:NativeAbsent,preparedEvidence:false,terminalEvidence:false,ackEvidence:false,commitAttempted:false,visibleCommitAttempted:false,lastOperation:NoOperation,nativeAck:0,mutations:0,sendsPrepare:0,sendsCommit:0,sendsCancel:0},
    writer:Idle,writeKey:0,wanted:Empty,wantedOperation:NoOperation,everCommitA:false,everCommitB:false,poisoned:false,currentGrant:1,oldV6:7,sidecar:9,migrationValidated:true,predecessorValid:true,markerValid:true,autoReplay:0}
  // External corruption flags represent detected drift/missing marker, not an in-model file repair.
  action predecessorDrift = all {s.predecessorValid,s'={...s,predecessorValid:false,poisoned:true}}
  action missingMarker = all {s.markerValid,s'={...s,markerValid:false,poisoned:true}}
  // Existing C writer creates the exact schema2 Pending file; distinct targets coexist.
  action hostPending(k:int):bool = all {writeAllowed(s,k),s.migrationValidated,not(entry(s,k).file),not(entry(s,k).live),entry(s,k).durable==Empty,
    s'=replaceEntry(s,k,{...entry(s,k),file:true,absenceSynced:false})}
  action reserve(k:int):bool = all {writeAllowed(s,k),s.currentGrant==entry(s,k).binding,entry(s,k).file,
    not(entry(s,k).live),entry(s,k).durable==Empty,
    s'={...s,writer:Temp,writeKey:k,wanted:Reserved,wantedOperation:NoOperation}}
  // An already existing Pending record for target A blocks another key targeting A.
  action foreignSameTargetAdmission = all {s.a.file or s.a.live or s.a.durable!=Empty,s'=s}
  action attemptPrepare(k:int):bool = all {writeAllowed(s,k),s.currentGrant==entry(s,k).binding,entry(s,k).durable==Reserved,
    s'={...s,writer:Temp,writeKey:k,wanted:PrepareAttempt,wantedOperation:PrepareOperation}}
  action attemptCommit(k:int):bool = all {writeAllowed(s,k),s.currentGrant==entry(s,k).binding,entry(s,k).durable==Prepared,not(entry(s,k).commitAttempted),
    s'={...s,writer:Temp,writeKey:k,wanted:CommitAttempt,wantedOperation:CommitOperation}}
  action attemptCancel(k:int):bool = all {writeAllowed(s,k),s.currentGrant==entry(s,k).binding,entry(s,k).durable==Prepared,
    s'={...s,writer:Temp,writeKey:k,wanted:CancelAttempt,wantedOperation:CancelOperation}}
  action syncFile = all {not(s.poisoned),s.writer==Temp,s'={...s,writer:Synced}}
  action renameEnvelope = all {not(s.poisoned),s.writer==Synced,
    s'=replaceEntry({...s,writer:Renamed},s.writeKey,{...entry(s,s.writeKey),visible:s.wanted,
      visibleCommitAttempted:entry(s,s.writeKey).visibleCommitAttempted or s.wantedOperation==CommitOperation})}
  action syncEnvelopeDir = all {not(s.poisoned),s.writer==Renamed,
    s'=replaceEntry({...s,writer:Idle,
      everCommitA:s.everCommitA or (s.writeKey==1 and entry(s,s.writeKey).visibleCommitAttempted),
      everCommitB:s.everCommitB or (s.writeKey==2 and entry(s,s.writeKey).visibleCommitAttempted)},s.writeKey,{...entry(s,s.writeKey),durable:s.wanted,
      commitAttempted:entry(s,s.writeKey).visibleCommitAttempted,
      lastOperation:if(s.wantedOperation==NoOperation) entry(s,s.writeKey).lastOperation else s.wantedOperation,
      live:if(s.wanted==Reserved) true else if(s.wanted==AdmissionRetired) false else entry(s,s.writeKey).live})}
  action ioFailure = all {not(s.poisoned),s.writer!=Idle,s'={...s,poisoned:true}}
  // Attempts are persisted under guard before native transport; transport itself is outside guard.
  action nativePrepare(k:int):bool = all {writeAllowed(s,k),s.currentGrant==entry(s,k).binding,
    entry(s,k).durable==PrepareAttempt,entry(s,k).native==NativeAbsent,entry(s,k).sendsPrepare==0,
    s'=replaceEntry(s,k,{...entry(s,k),native:NativePrepared,sendsPrepare:1})}
  action receivePrepared(k:int,binding:int,pid:int,deadline:int):bool = all {writeAllowed(s,k),
    binding==entry(s,k).binding,s.currentGrant==binding,pid==entry(s,k).pid,deadline==entry(s,k).deadline,
    entry(s,k).native==NativePrepared,s'=replaceEntry(s,k,{...entry(s,k),preparedEvidence:true})}
  action observePrepared(k:int):bool = all {writeAllowed(s,k),s.currentGrant==entry(s,k).binding,
    entry(s,k).durable==PrepareAttempt,entry(s,k).preparedEvidence,
    s'={...s,writer:Temp,writeKey:k,wanted:Prepared,wantedOperation:NoOperation}}
  // Current-grant read-only exact query may observe Prepared after transport uncertainty.
  action queryPrepared(k:int,binding:int,pid:int,deadline:int):bool = all {writeAllowed(s,k),
    binding==entry(s,k).binding,s.currentGrant==binding,pid==entry(s,k).pid,deadline==entry(s,k).deadline,
    entry(s,k).durable==Uncertain,entry(s,k).preparedEvidence,entry(s,k).native==NativePrepared,
    s'={...s,writer:Temp,writeKey:k,wanted:Prepared,wantedOperation:QueryOperation}}
  // A failed read-only query is diagnostic uncertainty; it is not mutation permission.
  action queryFailure(k:int,binding:int,pid:int,deadline:int):bool = all {writeAllowed(s,k),
    binding==entry(s,k).binding,s.currentGrant==binding,pid==entry(s,k).pid,deadline==entry(s,k).deadline,
    entry(s,k).durable==Uncertain,entry(s,k).preparedEvidence,
    s'={...s,writer:Temp,writeKey:k,wanted:Uncertain,wantedOperation:QueryOperation}}
  action nativeCommit(k:int):bool = all {writeAllowed(s,k),s.currentGrant==entry(s,k).binding,
    entry(s,k).durable==CommitAttempt,entry(s,k).commitAttempted,entry(s,k).native==NativePrepared,entry(s,k).sendsCommit==0,
    s'=replaceEntry(s,k,{...entry(s,k),native:NativeCommitted,sendsCommit:1,mutations:entry(s,k).mutations+1})}
  action nativeCancel(k:int):bool = all {writeAllowed(s,k),s.currentGrant==entry(s,k).binding,
    entry(s,k).durable==CancelAttempt,entry(s,k).native==NativePrepared,entry(s,k).sendsCancel==0,
    s'=replaceEntry(s,k,{...entry(s,k),native:NativeCancelled,sendsCancel:1})}
  action nativeUncertain(k:int):bool = all {writeAllowed(s,k),s.currentGrant==entry(s,k).binding,
    entry(s,k).durable==CommitAttempt,entry(s,k).commitAttempted,entry(s,k).native==NativePrepared,entry(s,k).sendsCommit==0,
    s'=replaceEntry(s,k,{...entry(s,k),native:NativeUnknown,sendsCommit:1,mutations:entry(s,k).mutations+1})}
  action nativeRefuse(k:int):bool = all {writeAllowed(s,k),s.currentGrant==entry(s,k).binding,
    entry(s,k).durable==CommitAttempt,entry(s,k).commitAttempted,entry(s,k).native==NativePrepared,entry(s,k).sendsCommit==0,
    s'=replaceEntry(s,k,{...entry(s,k),native:NativeRefused,sendsCommit:1})}
  action receiveTerminal(k:int,binding:int,pid:int,deadline:int):bool = all {writeAllowed(s,k),
    binding==entry(s,k).binding,s.currentGrant==binding,pid==entry(s,k).pid,deadline==entry(s,k).deadline,terminal(entry(s,k).native),
    s'=replaceEntry(s,k,{...entry(s,k),terminalEvidence:true})}
  action observeTerminal(k:int):bool = all {writeAllowed(s,k),entry(s,k).terminalEvidence,terminal(entry(s,k).native),
    entry(s,k).durable==CommitAttempt or entry(s,k).durable==CancelAttempt,
    s'={...s,writer:Temp,writeKey:k,wanted:TerminalStored,wantedOperation:NoOperation}}
  action observeUnknown(k:int):bool = all {writeAllowed(s,k),entry(s,k).native==NativeUnknown,entry(s,k).durable==CommitAttempt,
    s'={...s,writer:Temp,writeKey:k,wanted:Uncertain,wantedOperation:NoOperation}}
  // Transport loss supplies no invented prepared ID or terminal decision.
  action observeTransportUnknown(k:int):bool = all {writeAllowed(s,k),not(entry(s,k).terminalEvidence),
    entry(s,k).durable==PrepareAttempt or entry(s,k).durable==CommitAttempt or entry(s,k).durable==CancelAttempt,
    s'={...s,writer:Temp,writeKey:k,wanted:Uncertain,wantedOperation:NoOperation}}
  // Unlink and admissions-directory fsync are separate crash cuts.
  action unlinkPending(k:int):bool = all {writeAllowed(s,k),entry(s,k).durable==TerminalStored or entry(s,k).durable==AdmissionRetired,
    s'=replaceEntry(s,k,{...entry(s,k),file:false,absenceSynced:false})}
  action syncAdmissionsDir(k:int):bool = all {writeAllowed(s,k),entry(s,k).durable==TerminalStored or entry(s,k).durable==AdmissionRetired,not(entry(s,k).file),
    s'=replaceEntry(s,k,{...entry(s,k),absenceSynced:true})}
  action admissionFailure(k:int):bool = all {writeAllowed(s,k),entry(s,k).durable==TerminalStored or entry(s,k).durable==AdmissionRetired,
    s'={...s,poisoned:true}}
  action finish(k:int):bool = all {writeAllowed(s,k),entry(s,k).durable==TerminalStored,
    not(entry(s,k).file),entry(s,k).absenceSynced,
    s'={...s,writer:Temp,writeKey:k,wanted:AdmissionRetired,wantedOperation:NoOperation}}
  action ackPending(k:int):bool = all {writeAllowed(s,k),entry(s,k).durable==AdmissionRetired,not(entry(s,k).file),entry(s,k).absenceSynced,
    s.currentGrant==entry(s,k).binding,s'={...s,writer:Temp,writeKey:k,wanted:AckPending,wantedOperation:NoOperation}}
  action nativeAck(k:int):bool = all {writeAllowed(s,k),entry(s,k).durable==AckPending,
    s.currentGrant==entry(s,k).binding,terminal(entry(s,k).native),entry(s,k).nativeAck==0,
    s'=replaceEntry(s,k,{...entry(s,k),nativeAck:1,ackEvidence:true})}
  action acknowledged(k:int):bool = all {writeAllowed(s,k),entry(s,k).durable==AckPending,entry(s,k).nativeAck==1,entry(s,k).ackEvidence,s.currentGrant==entry(s,k).binding,
    s'={...s,writer:Temp,writeKey:k,wanted:Acknowledged,wantedOperation:NoOperation}}
  // Reappearing exact old Pending is removed under the durable terminal tombstone before reuse.
  action reappear(k:int):bool = all {writeAllowed(s,k),entry(s,k).durable==TerminalStored or entry(s,k).durable==AdmissionRetired,not(entry(s,k).file),
    s'=replaceEntry(s,k,{...entry(s,k),file:true,absenceSynced:false})}
  action crash = all {s.currentGrant==1,s'={...s,currentGrant:2,poisoned:s.poisoned or s.writer!=Idle,
    a:{...s.a,preparedEvidence:false,terminalEvidence:false,ackEvidence:false},b:{...s.b,preparedEvidence:false,terminalEvidence:false,ackEvidence:false}}}
  action recoveryRead = all {s.currentGrant==2,s'=s}
  // Broken design ACKs after visible rename but before confirmed terminal directory fsync.
  action brokenAck(k:int):bool = all {validKey(k),s.writer==Renamed,s.writeKey==k,entry(s,k).visible==TerminalStored,
    s'=replaceEntry(s,k,{...entry(s,k),nativeAck:1})}
  action step = any {predecessorDrift,missingMarker,hostPending(1),hostPending(2),reserve(1),reserve(2),foreignSameTargetAdmission,
    attemptPrepare(1),attemptPrepare(2),attemptCommit(1),attemptCommit(2),attemptCancel(1),attemptCancel(2),
    syncFile,renameEnvelope,syncEnvelopeDir,ioFailure,nativePrepare(1),nativePrepare(2),receivePrepared(1,1,11,100),receivePrepared(2,1,22,200),
    observePrepared(1),observePrepared(2),queryPrepared(1,1,11,100),queryPrepared(2,1,22,200),queryFailure(1,1,11,100),nativeCommit(1),nativeCommit(2),nativeCancel(1),nativeCancel(2),nativeUncertain(1),nativeRefuse(1),nativeRefuse(2),observeUnknown(1),observeTransportUnknown(1),observeTransportUnknown(2),
    receiveTerminal(1,1,11,100),receiveTerminal(2,1,22,200),observeTerminal(1),observeTerminal(2),unlinkPending(1),unlinkPending(2),syncAdmissionsDir(1),syncAdmissionsDir(2),admissionFailure(1),admissionFailure(2),finish(1),finish(2),ackPending(1),ackPending(2),nativeAck(1),nativeAck(2),acknowledged(1),acknowledged(2),reappear(1),crash,recoveryRead}
  val ackAfterRetirement = (s.a.nativeAck>0 implies (s.a.durable==AckPending or s.a.durable==Acknowledged) and not(s.a.live) and s.a.absenceSynced) and
    (s.b.nativeAck>0 implies (s.b.durable==AckPending or s.b.durable==Acknowledged) and not(s.b.live) and s.b.absenceSynced)
  val noAutomaticReplay = s.autoReplay==0 and s.a.sendsPrepare<=1 and s.b.sendsPrepare<=1 and s.a.sendsCommit<=1 and s.b.sendsCommit<=1
  val cancelledNoMutation = (s.a.native==NativeCancelled implies s.a.mutations==0) and (s.b.native==NativeCancelled implies s.b.mutations==0)
  val immutableOriginals = s.a.key==1 and s.a.binding==1 and s.a.target==1 and s.a.pid==11 and s.a.deadline==100 and s.b.key==2 and s.b.binding==1 and s.b.target==2 and s.b.pid==22 and s.b.deadline==200
  val v6AndSidecarPreserved = s.oldV6==7 and s.sidecar==9
  val uncertaintyNotAcked = (s.a.native==NativeUnknown implies s.a.nativeAck==0) and (s.b.native==NativeUnknown implies s.b.nativeAck==0)
  val sentCommitRequiresDurableAttempt = (s.a.sendsCommit>0 implies s.a.commitAttempted) and (s.b.sendsCommit>0 implies s.b.commitAttempted)
  val durableAttemptHasVisibleEvidence = (s.a.commitAttempted implies s.a.visibleCommitAttempted) and (s.b.commitAttempted implies s.b.visibleCommitAttempted)
  val confirmedCommitAttemptNeverClears = (s.everCommitA implies s.a.commitAttempted) and (s.everCommitB implies s.b.commitAttempted)
}
