module proof_lifecycle {
 var s:{owned:bool,intent:bool,profile:int,started:bool,loaded:bool,nonce:int,held:bool,dirty:bool,retired:bool,oldNonce:int,mainFalse:bool}
 action init=s'={owned:true,intent:false,profile:0,started:false,loaded:false,nonce:0,held:false,dirty:false,retired:false,oldNonce:0,mainFalse:true}
 action falseStart=all{s.owned,not(s.intent),s'=s.with("started",false)}
 action enable=all{s.owned,s'=s.with("intent",true)}
 action start=all{s.owned,s.intent,s'=s.with("profile",s.profile+1).with("started",true)}
 action load=all{s.owned,not(s.loaded),s'=s.with("loaded",true).with("nonce",s.nonce+1).with("oldNonce",s.nonce).with("held",false).with("dirty",false).with("retired",false)}
 action capture=all{s.loaded,not(s.retired),s'=s.with("held",true)}
 action dirty=all{s.loaded,not(s.retired),s'=s.with("dirty",true)}
 action release=s'=s.with("held",false).with("dirty",false)
 action prepare=all{s.loaded,s'=s.with("retired",s.retired or (not(s.held) and not(s.dirty)))}
 action stalePrepare=all{s.loaded,s.oldNonce!=s.nonce,s'=s}
 action unload=all{s.loaded,s.retired,not(s.held),not(s.dirty),s'=s.with("loaded",false)}
 action idle=s'=s
 action step=any{falseStart,enable,start,load,capture,dirty,release,prepare,stalePrepare,unload,idle}
 val safe=s.owned and s.mainFalse and (s.started implies s.intent) and (s.retired implies not(s.held) and not(s.dirty))
 run disabledNoProfileMutationTest=init.then(falseStart).then(all{assert(not(s.started) and s.profile==0),idle})
 run passiveLoadPreservesFalseIntentTest=init.then(load).then(all{assert(not(s.intent) and not(s.started) and s.profile==0),idle})
 run falsePreparePreservesHeldTest=init.then(load).then(capture).then(prepare).then(all{assert(s.held and not(s.retired) and s.loaded),idle})
 run falsePreparePreservesDirtyTest=init.then(load).then(dirty).then(prepare).then(all{assert(s.dirty and not(s.retired)),idle})
 run trueNormalUnloadTest=init.then(load).then(prepare).then(unload).then(all{assert(not(s.loaded) and not(s.intent)),idle})
 run reloadNewNonceTest=init.then(load).then(prepare).then(unload).then(load).then(stalePrepare).then(all{assert(s.nonce==2 and s.oldNonce==1 and not(s.retired)),idle})
 run privateEnabledRestartPreservesIntentTest=init.then(enable).then(start).then(load).then(prepare).then(unload).then(load).then(all{assert(s.intent and s.started and s.mainFalse),idle})
}
