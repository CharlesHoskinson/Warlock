// New live parent device/output anchor vs unchanged-coordinate suppression.
// Normal hit-test policy is represented by allowFocus; no native rendering.
module anchor {
 type State={live:bool,ready:bool,device:int,next:int,output:int,lastDevice:int,lastOutput:int,point:int,lastPoint:int,focus:int,allowFocus:bool,refreshes:int,violations:int}
 var s:State
 action init=s'={live:true,ready:true,device:1,next:1,output:1,lastDevice:0,lastOutput:0,point:0,lastPoint:0,focus:0,allowFocus:true,refreshes:0,violations:0}
 val newSource=s.lastDevice!=s.device or s.lastOutput!=s.output
 val eligible=s.live and s.ready and s.device>0 and s.output>0
 val ordinaryFocus=if(s.allowFocus and s.point!=s.lastPoint) 1 else s.focus
 val refresh=true
 val resultFocus=if(refresh and s.allowFocus) 1 else ordinaryFocus
 action warp=s'=if(eligible) {...s,lastDevice:s.device,lastOutput:s.output,lastPoint:s.point,focus:resultFocus,refreshes:s.refreshes+(if(refresh) 1 else 0),violations:s.violations+(if(newSource and s.allowFocus and resultFocus!=1) 1 else 0)} else s
 action retire=s'={...s,device:0,lastDevice:0,lastOutput:0,focus:0}
 action recreate=s'={...s,device:s.next+1,next:s.next+1}
 action outputChange=s'={...s,output:s.output+1,focus:0}
 action move=s'={...s,point:s.point+1}
 action programFocus=s'={...s,focus:2}
 action inactive=s'={...s,ready:false}
 action shutdown=s'={...s,live:false}
 action grab=s'={...s,allowFocus:false}
 action commit=s'=s
 action step=any{warp,retire,recreate,outputChange,move,programFocus,inactive,shutdown,grab,commit}
 val safety=s.violations==0 and s.lastDevice>=0 and s.refreshes>=0
 run firstStationaryAnchorTest=init.then(warp).then(all{assert(s.focus==1 and s.refreshes==1),s'=s})
 run replacementStationaryAnchorTest=init.then(warp).then(retire).then(recreate).then(warp).then(all{assert(s.focus==1 and s.refreshes==2),s'=s})
 run outputStationaryAnchorTest=init.then(warp).then(outputChange).then(warp).then(all{assert(s.focus==1 and s.refreshes==2),s'=s})
 run ordinaryWarpPreservesProgramFocusTest=init.then(warp).then(programFocus).then(warp).then(all{assert(s.focus==2 and s.refreshes==1),s'=s})
 run ordinaryCommitPreservesProgramFocusTest=init.then(warp).then(programFocus).then(commit).then(all{assert(s.focus==2 and s.refreshes==1),s'=s})
 run deadDeviceRefusedTest=init.then(retire).then(warp).then(all{assert(s.focus==0 and s.refreshes==0),s'=s})
 run inactiveParentRefusedTest=init.then(inactive).then(warp).then(all{assert(s.focus==0 and s.refreshes==0),s'=s})
 run shutdownRefusedTest=init.then(shutdown).then(warp).then(all{assert(s.focus==0 and s.refreshes==0),s'=s})
 run normalGrabPolicyTest=init.then(programFocus).then(grab).then(warp).then(all{assert(s.focus==2 and s.refreshes==1),s'=s})
 run subsequentMovedWarpTest=init.then(warp).then(programFocus).then(move).then(warp).then(all{assert(s.focus==1 and s.refreshes==1),s'=s})
}
