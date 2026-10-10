module overviewRecovery {
  // UI-006 overview-refusal: one explicit choice, current authority and a
  // correlated terminal refusal. Capture/transport/paint are outside this model.
  type Phase = Idle | Choosing | Issued | Ready
  type State = { phase: Phase, authority: int, owner: int, root: int, read: int,
    intent: int, workspace: int, occupied: bool, available: bool, sends: int,
    returns: int, refused: bool, unconfirmed: bool, returnOwner: int, returnWorkspace: int, ignored: int }
  var s: State
  action init = s'={phase:Idle,authority:1,owner:0,root:0,read:0,intent:0,
    workspace:0,occupied:false,available:true,sends:0,returns:0,refused:false,
    unconfirmed:false,returnOwner:0,returnWorkspace:0,ignored:0}
  action choose = all { s.phase==Idle, s.sends==0, s.returns==0,
    not(s.occupied),s.authority==1,
    s'={...s,phase:Choosing,owner:s.authority,root:17,read:7,workspace:2} }
  action issue = all {s.phase==Choosing,s.owner==s.authority,
    s'={...s,phase:Issued,intent:41,sends:s.sends+1} }
  action foreignReceipt = all {s.phase==Issued,s'={...s,ignored:s.ignored+1} }
  action unknown = all {s.phase==Issued,s'={...s,unconfirmed:true} }
  action refusal = all {s.phase==Issued,s'={...s,phase:Ready,refused:true} }
  action commit = all {s.phase==Issued,s'={...s,phase:Idle} }
  action cancel = all {s.phase!=Idle,s'={...s,phase:Idle} }
  action busy = s'={...s,available:false}
  action currentReady = s'={...s,available:true}
  action occupied = s'={...s,occupied:true,phase:Idle}
  action vacated = s'={...s,occupied:false}
  action replacement = s'={...s,authority:2,phase:Idle}
  action recover = all {s.phase==Ready,s.available,not(s.occupied),s.owner==s.authority,
    s'={...s,phase:Idle,returns:s.returns+1,returnOwner:s.authority,returnWorkspace:s.workspace} }
  action duplicate = all {s.returns==1,s.phase==Idle,s'={...s,ignored:s.ignored+1} }
  action step = any {choose,issue,foreignReceipt,unknown,refusal,commit,cancel,busy,currentReady,occupied,vacated,replacement,recover,duplicate}
  val safety = s.sends<=1 and s.returns<=1 and
    (s.returns==0 or (s.refused and s.sends==1 and s.returnOwner==s.owner and s.returnWorkspace==2))
  val choiceWitness = s.phase==Choosing
  val issuedWitness = s.phase==Issued
  val refusalWitness = s.phase==Ready
  val recoveryWitness = s.returns==1
  val unknownWitness = s.unconfirmed
  val foreignWitness = s.ignored>0
  val replacedWitness = s.authority==2
  val occupiedWitness = s.occupied
}
