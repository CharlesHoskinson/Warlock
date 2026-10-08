module motionProfile {
  var s: {binding:int,serial:int,desired:int,applied:int,native:int,pending:int,request:int,submitted:int,windowSends:int,lastWindowProfile:int,lastWindowNative:int}
  action init = s'={binding:1,serial:0,desired:1,applied:1,native:1,pending:0,request:0,submitted:1,windowSends:0,lastWindowProfile:1,lastWindowNative:1}
  action reduced = all {s.serial<4,s'={...s,serial:s.serial+1,desired:1}}
  action full = all {s.serial<4,s'={...s,serial:s.serial+1,desired:0}}
  action configure = all {s.serial>0,s.pending==0,s.applied!=s.desired,s.request<4,s'={...s,pending:s.request+1,request:s.request+1,submitted:s.desired}}
  action nativeApply = all {s.pending>0,s'={...s,native:s.submitted}}
  action acknowledge = all {s.pending>0,s.native==s.submitted,s'={...s,applied:s.submitted,pending:0}}
  action stale = s'=s
  action rebind = all {s.binding<3,s'={...s,binding:s.binding+1,pending:0,applied:1,native:1}}
  action window = all {s.pending==0,s.applied==s.desired,s.windowSends<4,s'={...s,windowSends:s.windowSends+1,lastWindowProfile:s.desired,lastWindowNative:s.native}}
  action step = any {reduced,full,configure,nativeApply,acknowledge,stale,rebind,window}
  val safety = s.lastWindowProfile==s.lastWindowNative and s.pending<=s.request and (s.pending==0 or s.pending==s.request)
  run matchingAckAppliesProfileTest = init.then(full).then(configure).then(nativeApply).then(acknowledge).then(window).then(all {assert(s.lastWindowNative==0 and s.windowSends==1),s'=s})
  run staleAckCannotApplyTest = init.then(full).then(configure).then(stale).then(all {assert(s.pending>0 and s.applied==1),s'=s})
  run changedPreferenceWaitsTest = init.then(full).then(configure).then(reduced).then(nativeApply).then(acknowledge).then(configure).then(all {assert(s.pending==2 and s.submitted==1 and s.windowSends==0),s'=s})
  run configurationIsNotWindowEffectTest = init.then(full).then(configure).then(nativeApply).then(all {assert(s.windowSends==0),s'=s})
  run disconnectRetiresProfileTest = init.then(full).then(configure).then(rebind).then(stale).then(all {assert(s.pending==0 and s.native==1 and s.applied==1),s'=s})
  run lostAcknowledgementCannotIssueWindowTest = init.then(full).then(configure).then(nativeApply).then(stale).then(all {assert(s.pending>0 and s.windowSends==0),s'=s})
}

module liveMotion {
  var s: {source:int,override:int,draft:int,revision:int,write:int,unknown:bool,effective:int,windowSends:int,target:int,deadline:int}
  pure def effective(source:int,override:int):int = if (override == -1) source else override
  action init = s'={source:0,override:-1,draft:-1,revision:1,write:0,unknown:false,effective:0,windowSends:1,target:7,deadline:6}
  action source = all {s'={...s,source:1-s.source,effective:effective(1-s.source,s.override)}}
  action edit = all {s.write==0,s'={...s,draft:if(s.draft==1) -1 else 1}}
  action save = all {s.write==0,s.draft!=s.override,s'={...s,write:1}}
  action commit = all {s.write==1,s.revision<4,s'={...s,override:s.draft,effective:effective(s.source,s.draft),revision:s.revision+1,write:0,unknown:false}}
  action lose = all {s.write==1,s'={...s,unknown:true}}
  action refused = all {s.write==1,s'={...s,write:0,unknown:false}}
  action stale = s'=s
  action step = any {source,edit,save,commit,lose,refused,stale}
  val safety = s.effective==effective(s.source,s.override) and s.windowSends==1 and s.target==7 and s.deadline==6 and (not(s.unknown) or s.write==1)
  run overrideWinsOverLiveSourceTest = init.then(edit).then(save).then(commit).then(source).then(source).then(all {assert(s.effective==1 and s.override==1),s'=s})
  run resetUsesCurrentSystemTest = init.then(edit).then(save).then(commit).then(edit).then(save).then(commit).then(all {assert(s.override == -1 and s.effective==s.source and s.windowSends==1),s'=s})
  run unknownWriteDoesNotApplyOrReplayTest = init.then(edit).then(save).then(lose).then(stale).then(all {assert(s.override == -1 and s.write==1 and s.windowSends==1 and s.deadline==6),s'=s})
}
