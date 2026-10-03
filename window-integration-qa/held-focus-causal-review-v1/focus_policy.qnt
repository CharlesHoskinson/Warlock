module focus_policy {
 type S = {active:bool,exact:bool,mapped:bool,independentMapped:bool,focus:int,rawDown:bool,groups:int,moved:int,retired:bool,beforeFocus:int}
 var s:S
 action init = s'={active:false,exact:true,mapped:true,independentMapped:true,focus:1,rawDown:false,groups:0,moved:0,retired:false,beforeFocus:1}
 action press = all {not(s.rawDown),s'={...s,active:true,rawDown:true,focus:1,retired:false,beforeFocus:s.focus}}
 action wmFocusPeer = s'={...s,focus:2,beforeFocus:s.focus,retired:false}
 action motion = all {s.active,s.rawDown,s'={...s,moved:s.moved+1,focus:if(s.exact and s.mapped and s.independentMapped and s.focus==2)2 else 1,retired:false,beforeFocus:s.focus}}
 action nonrelease = s'={...s,active:false,retired:true,beforeFocus:s.focus}
 action keyboardPeer = s'={...s,active:false,focus:2,retired:false,beforeFocus:s.focus}
 action release = s'={...s,active:false,rawDown:false,retired:false,beforeFocus:s.focus}
 action stale = s'={...s,exact:false,retired:false,beforeFocus:s.focus}
 action unmap = s'={...s,mapped:false,active:false,retired:false,beforeFocus:s.focus}
 action idle = s'={...s,retired:false,beforeFocus:s.focus}
 action step = any {press,wmFocusPeer,motion,nonrelease,keyboardPeer,release,stale,unmap,idle}
 val invariant = all {s.active implies s.rawDown,s.retired implies all {s.focus==s.beforeFocus,s.groups==0}}
 run wmFocusRetainsExactCaptureTest = init.then(press).then(wmFocusPeer).then(all {assert(s.active and s.rawDown and s.focus==2),idle})
 run motionPreservesIndependentFocusTest = init.then(press).then(wmFocusPeer).then(motion).then(all {assert(s.active and s.focus==2 and s.moved==1),idle})
 run escapePreservesAlreadyIndependentFocusTest = init.then(press).then(wmFocusPeer).then(motion).then(nonrelease).then(all {assert(not(s.active) and s.rawDown and s.focus==2),idle})
 run actualKeyboardFocusRetiresFirstTest = init.then(press).then(keyboardPeer).then(all {assert(not(s.active) and s.rawDown and s.focus==2),idle})
 run staleTargetHasNoShieldAuthorityTest = init.then(press).then(wmFocusPeer).then(stale).then(motion).then(all {assert(s.focus==1 and not(s.exact)),idle})
 run genuineReleaseQuiescesTest = init.then(press).then(wmFocusPeer).then(motion).then(nonrelease).then(release).then(all {assert(not(s.rawDown) and not(s.active) and s.groups==0),idle})
}
