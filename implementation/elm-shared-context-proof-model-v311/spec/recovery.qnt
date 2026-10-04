module recovery {
 type State={live:Set[int],epoch:int,proofScope:int,proofEpoch:int,available:bool,held:bool,pending:bool,pendingScope:int,pendingEpoch:int,age:int,deliveries:int}
 var s:State
 action init=s'={live:Set(1,2),epoch:1,proofScope:0,proofEpoch:0,available:false,held:false,pending:false,pendingScope:0,pendingEpoch:0,age:0,deliveries:0}
 action press(scope:int):bool=s'=if(s.live.contains(scope)){...s,epoch:s.epoch+1,proofScope:scope,proofEpoch:s.epoch+1,available:not(s.held),held:true,age:0} else s
 action release=s'={...s,held:false}
 action replay=s'=s
 action cancel=s'={...s,epoch:s.epoch+1,available:false}
 action retire(scope:int):bool=s'={...s,live:s.live.exclude(Set(scope)),epoch:s.epoch+1,available:false}
 action consume(scope:int):bool=s'=if(s.available and s.proofScope==scope and s.proofEpoch==s.epoch and s.live.contains(scope) and s.age<=2){...s,available:false,pending:true,pendingScope:scope,pendingEpoch:s.epoch} else s
 action finish(scope:int,dom:bool):bool=s'=if(s.pending){...s,pending:false,deliveries:s.deliveries+(if(dom and scope==s.pendingScope and s.pendingEpoch==s.epoch and s.live.contains(scope) and s.age<=2) 1 else 0)} else s
 action wait=s'={...s,age:s.age+1}
 action step=any{press(1),press(2),release,replay,cancel,retire(1),retire(2),consume(1),consume(2),finish(1,true),finish(2,true),finish(1,false),wait}
 val safety=s.deliveries>=0 and s.age>=0 and (not(s.available) or (s.live.contains(s.proofScope) and s.proofEpoch==s.epoch))
 run exactEngineSingleUseTest=init.then(press(1)).then(consume(1)).then(consume(1)).then(finish(1,true)).then(finish(1,true)).then(all{assert(s.deliveries==1),s'=s})
 run foreignEngineCannotConsumeTest=init.then(press(1)).then(consume(2)).then(all{assert(s.available and not(s.pending) and s.deliveries==0),s'=s})
 run foreignAsyncEngineRefusesTest=init.then(press(1)).then(consume(1)).then(finish(2,true)).then(all{assert(s.deliveries==0),s'=s})
 run domVerificationRequiredTest=init.then(press(1)).then(consume(1)).then(finish(1,false)).then(all{assert(s.deliveries==0),s'=s})
 run retirementInvalidatesAsyncTest=init.then(press(1)).then(consume(1)).then(retire(1)).then(finish(1,true)).then(all{assert(s.deliveries==0 and s.held),s'=s})
 run epochChangeInvalidatesAsyncTest=init.then(press(1)).then(consume(1)).then(cancel).then(finish(1,true)).then(all{assert(s.deliveries==0 and s.held),s'=s})
 run closeKeepsHeldSuppressionTest=init.then(press(1)).then(cancel).then(press(2)).then(consume(2)).then(finish(2,true)).then(all{assert(s.held and s.deliveries==0),s'=s})
 run physicalReleasePermitsNewInputTest=init.then(press(1)).then(cancel).then(release).then(press(2)).then(consume(2)).then(finish(2,true)).then(all{assert(s.deliveries==1),s'=s})
 run replayDoesNotReplaceNewProofTest=init.then(press(1)).then(replay).then(consume(1)).then(finish(1,true)).then(all{assert(s.deliveries==1 and s.held),s'=s})
 run expiredNativeProofRefusesTest=init.then(press(1)).then(wait).then(wait).then(wait).then(consume(1)).then(all{assert(not(s.pending) and s.deliveries==0),s'=s})
 run asynchronousDeadlinePreservedTest=init.then(press(1)).then(consume(1)).then(wait).then(wait).then(wait).then(finish(1,true)).then(all{assert(s.deliveries==0),s'=s})
 run laterPhysicalInputRetiresOldCallbackTest=init.then(press(1)).then(consume(1)).then(release).then(press(2)).then(finish(1,true)).then(all{assert(s.deliveries==0 and s.proofScope==2),s'=s})
}
