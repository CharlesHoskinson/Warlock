// UI-019/outputs-return; moveWorkspaceToMonitor pinned branch. One native
// compositor-thread owner; retirement then migration are separate transitions.
// Monitor IDs abstract old=0, survivor=1, returned=2. No coordinate, transport,
// focus/custody, physical hotplug or AT proof; those require native evidence.
module pinned_output_retirement {
 var s:{phase:int,workspace:int,monitor:int,target:int,focusMonitor:int,activeWorkspace:int,oldExists:bool,oldEnabled:bool,pinned:bool,minimized:bool,pinFixture:bool,width:int,height:int,effects:int}
 pure def stayPinned(pin:bool,oldExists:bool,oldEnabled:bool):bool=pin and oldExists and oldEnabled
 // Native effect admission/focus mechanics: explicit navigation on the same
 // focus output is allowed before focusing a pin. Cross-output focus would
 // implicitly transfer its workspace in the existing native focus path.
 pure def mayRecoverPin(pin:bool,focusMonitor:int,ownerMonitor:int,navigating:bool,activeWorkspace:int,ownerWorkspace:int):bool=
  not(pin) or (focusMonitor==ownerMonitor and (navigating or activeWorkspace==ownerWorkspace))
 action init=s'={phase:0,workspace:2,monitor:0,target:0,focusMonitor:0,activeWorkspace:2,oldExists:true,oldEnabled:true,pinned:true,minimized:false,pinFixture:true,width:108,height:440,effects:0}
 action minimizedFixture=all{s.phase==0,s.pinFixture,s'={...s,pinned:false,minimized:true,pinFixture:false}}
 action retire=all{s.phase==0,s'={...s,phase:1,target:1,oldEnabled:false}}
 // Gap repair calls changeWorkspace before the window loop. On a retired
 // active monitor that callback can first move the pin to workspace 1, making
 // it absent from the original workspace's later migration loop.
 action skipRetiredGapNavigation=all{s.phase==1,not(s.oldExists and s.oldEnabled),s'={...s,phase:10}}
 action migrate=all{s.phase==10,not(stayPinned(s.pinned,s.oldExists,s.oldEnabled)),s'={...s,phase:2,monitor:s.target}}
 action legacyStay=all{s.phase==1,s.pinned,s'={...s,phase:8,workspace:1}}
 action legacyReturn=all{s.phase==8,s'={...s,phase:9,monitor:-1,target:2,oldExists:false}}
 action empty={
  nondet ownerStillExists=Set(true,false).oneOf()
  all{s.phase==2,s'={...s,phase:3,target:-1,oldExists:ownerStillExists,oldEnabled:false,monitor:if(ownerStillExists) s.monitor else -1}}
 }
 action returnOutput=all{s.phase==3,not(stayPinned(s.pinned,s.oldExists,s.oldEnabled)),s'={...s,phase:4,target:2,monitor:2,focusMonitor:2,activeWorkspace:1}}
 action taskbarRecovery=all{s.phase==4,mayRecoverPin(s.pinned,s.focusMonitor,s.monitor,s.activeWorkspace!=s.workspace,s.activeWorkspace,s.workspace),s'={...s,phase:6,minimized:false,activeWorkspace:s.workspace,effects:1}}
 action focusElsewhere=all{s.phase==4,s.pinned,s.focusMonitor==s.monitor,s'={...s,focusMonitor:3}}
 action refuseCrossOutputPin=all{s.phase==4,not(mayRecoverPin(s.pinned,s.focusMonitor,s.monitor,s.activeWorkspace!=s.workspace,s.activeWorkspace,s.workspace)),s'={...s,phase:7}}
 action legacyAdmissionRefusal=all{s.phase==4,s.pinned,s.activeWorkspace!=s.workspace,s'={...s,phase:12}}
 // Moving a workspace while its old monitor is live retains the pre-existing
 // pinned behavior: attach the pin to the old monitor's remaining workspace.
 action moveWhileLive=all{s.phase==0,s.pinned,stayPinned(s.pinned,s.oldExists,s.oldEnabled),s'={...s,phase:5,target:1,workspace:1}}
 action idle=s'=s
 action step=any{minimizedFixture,retire,skipRetiredGapNavigation,migrate,empty,returnOutput,taskbarRecovery,focusElsewhere,refuseCrossOutputPin,moveWhileLive,idle}
 val retired=s.phase==1
 val migrated=s.phase==2
 val skippedRetiredNavigation=s.phase==10
 val reconciled=s.phase==4
 val recovered=s.phase==6
 val livePinnedMove=s.phase==5
 val minimizedRecovery=s.phase==6 and not(s.pinFixture)
 val crossOutputRefused=s.phase==7
 val safety=all{s.workspace==(if(s.phase==5) 1 else 2),s.pinned==s.pinFixture,
  s.minimized==(not(s.pinFixture) and s.phase!=6),s.width==108,s.height==440,
  s.effects==(if(s.phase==6) 1 else 0),
  (s.phase!=2 and s.phase!=4 and s.phase!=6) or s.monitor==s.target,
  s.phase!=5 or (s.monitor==0 and s.oldExists and s.oldEnabled and s.pinned),
  s.phase!=6 or (s.activeWorkspace==s.workspace and (not(s.pinned) or s.focusMonitor==s.monitor))}
}
