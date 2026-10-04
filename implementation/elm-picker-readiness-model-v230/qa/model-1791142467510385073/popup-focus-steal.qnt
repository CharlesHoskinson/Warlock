module readiness {
 var s: { binding: int, output: int, root: int, app: int, live: bool, connected: bool, popup: bool,
   savedBinding: int, savedOutput: int, savedRoot: int, savedApp: int, mode: int, token: int,
   pr: int, gr: int, pReady: bool, gReady: bool, pending: bool, serial: int, lastEmission: int,
   effects: int, focus: int, violations: int }
 action init = s' = {binding:1,output:1,root:2,app:1,live:true,connected:true,popup:false,
   savedBinding:1,savedOutput:1,savedRoot:2,savedApp:1,mode:0,token:0,
   pr:0,gr:0,pReady:false,gReady:false,pending:false,serial:0,lastEmission:0,effects:0,focus:0,violations:0}
 action begin(mode: int): bool = s' = {...s, mode:mode, pending:true, popup:false, serial:s.serial+1,
   token:s.serial+1, savedBinding:s.binding,savedOutput:s.output,savedRoot:s.root,savedApp:s.app,
   pr:s.pr+2,gr:s.pr+3,pReady:false,gReady:false}
 action supersede = s' = {...s,pr:s.pr+2,gr:s.pr+3,pReady:false,gReady:false}
 action reply(kind: int, request: int, binding: int, valid: bool): bool = {
   val admitted = valid and s.connected and binding == s.binding and request == (if (kind == 1) s.pr else s.gr) and not(if (kind == 1) s.pReady else s.gReady)
   val p = s.pReady or (admitted and kind == 1)
   val g = s.gReady or (admitted and kind == 2)
   val ready = p and g and s.connected
   val safe = s.binding == s.savedBinding and s.output == s.savedOutput and s.root == s.savedRoot and s.app == s.savedApp and s.live and true
   val completion = admitted and ready
   val emit = completion and s.pending and safe
   val bad = emit and (not(valid) or binding != s.binding or request != (if (kind == 1) s.pr else s.gr) or not(p) or not(g) or not(s.connected) or s.binding != s.savedBinding or s.output != s.savedOutput or s.root != s.savedRoot or s.app != s.savedApp or not(s.live) or (s.mode == 2 and s.popup) or s.lastEmission == s.serial)
   s' = {...s,pReady:p,gReady:g,pending:if (completion) false else s.pending,
     effects:s.effects+(if (emit and s.mode == 1) 1 else 0),focus:s.focus+(if (emit and s.mode == 2) 1 else 0),
     lastEmission:if (emit) s.serial else s.lastEmission,violations:s.violations+(if (bad) 1 else 0)}
 }
 action expire(token: int): bool = s' = {...s,pending:if (token == s.token) false else s.pending}
 action disconnect = s' = {...s,connected:false,pending:false,pReady:false,gReady:false}
 action retire = s' = {...s,live:false}
 action replaceRoot = s' = {...s,root:s.root+1}
 action replaceApp = s' = {...s,app:s.app+1}
 action moveOutput = s' = {...s,output:s.output+1}
 action changeBinding = s' = {...s,binding:s.binding+1}
 action openPopup = s' = {...s,popup:true}
 action step = any { begin(1),begin(2),supersede,reply(1,s.pr,s.binding,true),reply(2,s.gr,s.binding,true),reply(1,s.pr,s.binding,false),reply(2,s.gr,s.binding,false),reply(1,0,s.binding,true),reply(2,s.gr,0,true),expire(s.token),expire(0),disconnect,retire,replaceRoot,replaceApp,moveOutput,changeBinding,openPopup }
 val safety = s.violations == 0 and s.effects >= 0 and s.focus >= 0 and s.effects+s.focus <= s.serial
 run projectionFirstTest = init.then(begin(1)).then(reply(1,s.pr,s.binding,true)).then(reply(2,s.gr,s.binding,true)).then(all {assert(s.effects == 1 and not(s.pending)),s'=s})
 run geometryFirstTest = init.then(begin(1)).then(reply(2,s.gr,s.binding,true)).then(reply(1,s.pr,s.binding,true)).then(all {assert(s.effects == 1 and not(s.pending)),s'=s})
 run projectionOnlyTest = init.then(begin(1)).then(reply(1,s.pr,s.binding,true)).then(all {assert(s.effects == 0 and s.pending),s'=s})
 run geometryOnlyTest = init.then(begin(1)).then(reply(2,s.gr,s.binding,true)).then(all {assert(s.effects == 0 and s.pending),s'=s})
 run invalidGeometryTest = init.then(begin(1)).then(reply(1,s.pr,s.binding,true)).then(reply(2,s.gr,s.binding,false)).then(all {assert(s.effects == 0 and s.pending),s'=s})
 run invalidProjectionTest = init.then(begin(1)).then(reply(2,s.gr,s.binding,true)).then(reply(1,s.pr,s.binding,false)).then(all {assert(s.effects == 0 and s.pending),s'=s})
 run wrongRequestTest = init.then(begin(1)).then(reply(1,s.pr,s.binding,true)).then(reply(2,0,s.binding,true)).then(all {assert(s.effects == 0 and s.pending),s'=s})
 run wrongBindingTest = init.then(begin(1)).then(reply(1,s.pr,s.binding,true)).then(reply(2,s.gr,0,true)).then(all {assert(s.effects == 0 and s.pending),s'=s})
 run wrongOutputTest = init.then(begin(1)).then(moveOutput).then(reply(1,s.pr,s.binding,true)).then(reply(2,s.gr,s.binding,true)).then(all {assert(s.effects == 0 and not(s.pending)),s'=s})
 run changedBindingTest = init.then(begin(1)).then(changeBinding).then(reply(1,s.pr,s.binding,true)).then(reply(2,s.gr,s.binding,true)).then(all {assert(s.effects == 0 and not(s.pending)),s'=s})
 run retiredRootTest = init.then(begin(1)).then(retire).then(reply(1,s.pr,s.binding,true)).then(reply(2,s.gr,s.binding,true)).then(all {assert(s.effects == 0 and not(s.pending)),s'=s})
 run replacementRootTest = init.then(begin(1)).then(replaceRoot).then(reply(1,s.pr,s.binding,true)).then(reply(2,s.gr,s.binding,true)).then(all {assert(s.effects == 0),s'=s})
 run changedApplicationTest = init.then(begin(1)).then(replaceApp).then(reply(1,s.pr,s.binding,true)).then(reply(2,s.gr,s.binding,true)).then(all {assert(s.effects == 0),s'=s})
 run expiredChoiceTest = init.then(begin(1)).then(expire(s.token)).then(reply(1,s.pr,s.binding,true)).then(reply(2,s.gr,s.binding,true)).then(all {assert(s.effects == 0 and not(s.pending)),s'=s})
 run oldTimerTest = init.then(begin(1)).then(begin(1)).then(expire(s.token-1)).then(reply(1,s.pr,s.binding,true)).then(reply(2,s.gr,s.binding,true)).then(all {assert(s.effects == 1 and not(s.pending)),s'=s})
 run disconnectedChoiceTest = init.then(begin(1)).then(disconnect).then(reply(1,s.pr,s.binding,true)).then(reply(2,s.gr,s.binding,true)).then(all {assert(s.effects == 0 and not(s.pending)),s'=s})
 run supersededPairTest = init.then(begin(1)).then(supersede).then(reply(1,s.pr-2,s.binding,true)).then(reply(2,s.gr-2,s.binding,true)).then(all {assert(s.effects == 0 and s.pending),s'=s})
 run freshSupersedingPairTest = init.then(begin(1)).then(reply(1,s.pr,s.binding,true)).then(supersede).then(reply(2,s.gr,s.binding,true)).then(reply(1,s.pr,s.binding,true)).then(all {assert(s.effects == 1 and not(s.pending)),s'=s})
 run duplicateCompletionTest = init.then(begin(1)).then(reply(1,s.pr,s.binding,true)).then(reply(2,s.gr,s.binding,true)).then(reply(2,s.gr,s.binding,true)).then(reply(1,s.pr,s.binding,true)).then(all {assert(s.effects == 1 and not(s.pending)),s'=s})
 run focusGeometryLastTest = init.then(begin(2)).then(reply(1,s.pr,s.binding,true)).then(reply(2,s.gr,s.binding,true)).then(all {assert(s.focus == 1 and s.effects == 0 and not(s.pending)),s'=s})
 run focusProjectionLastTest = init.then(begin(2)).then(reply(2,s.gr,s.binding,true)).then(reply(1,s.pr,s.binding,true)).then(all {assert(s.focus == 1 and s.effects == 0 and not(s.pending)),s'=s})
 run focusPopupNoStealTest = init.then(begin(2)).then(openPopup).then(reply(1,s.pr,s.binding,true)).then(reply(2,s.gr,s.binding,true)).then(all {assert(s.focus == 0 and s.effects == 0 and not(s.pending)),s'=s})
}
