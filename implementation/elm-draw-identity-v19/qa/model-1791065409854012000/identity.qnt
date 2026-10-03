module identity {
 type State={live:bool,authority:int,next:int,current:int,drawAuthority:int,drawId:int,heldAuthority:int,heldId:int}
 var s:State
 action init=s'={live:false,authority:1,next:0,current:0,drawAuthority:0,drawId:0,heldAuthority:0,heldId:0}
 action mapWindow=s'=if(s.live) s else {...s,live:true,next:s.next+1,current:s.next+1}
 action unmap=s'={...s,live:false,current:0}
 action draw=s'=if(s.live) {...s,drawAuthority:s.authority,drawId:s.current} else {...s,drawAuthority:0,drawId:0}
 action hold=s'={...s,heldAuthority:s.drawAuthority,heldId:s.drawId}
 action reload=s'={...s,authority:s.authority+1,next:1,current:1,live:true}
 action step=any{mapWindow,unmap,draw,hold,reload}
 val currentHeld=s.live and s.heldId>0 and s.heldId==s.current and s.heldAuthority==s.authority
 val safety=(not(currentHeld) or (s.live and s.heldAuthority==s.authority and s.heldId==s.current)) and ((s.drawId==0)==(s.drawAuthority==0)) and ((s.heldId==0)==(s.heldAuthority==0))
 run captureCurrentTest=init.then(mapWindow).then(draw).then(hold).then(all{assert(currentHeld),s'=s})
 run unmapRetiresHeldTest=init.then(mapWindow).then(draw).then(hold).then(unmap).then(all{assert(not(currentHeld) and s.heldId==1),s'=s})
 run remapNeverRelabelsTest=init.then(mapWindow).then(draw).then(hold).then(unmap).then(mapWindow).then(all{assert(not(currentHeld) and s.heldId==1 and s.current==2),s'=s})
 run freshRemapCaptureTest=init.then(mapWindow).then(draw).then(hold).then(unmap).then(mapWindow).then(draw).then(hold).then(all{assert(currentHeld and s.heldId==2),s'=s})
 run authorityIdReuseRetiresHeldTest=init.then(mapWindow).then(draw).then(hold).then(reload).then(all{assert(not(currentHeld) and s.heldId==s.current and s.heldAuthority!=s.authority),s'=s})
 run unboundCaptureTest=init.then(draw).then(hold).then(all{assert(not(currentHeld) and s.heldId==0),s'=s})
}
