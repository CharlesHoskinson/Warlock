module producer_closure {
 type S={owner:int,captured:int,bound:bool,registered:int,closed:int,known:bool,
 source:bool,raw:bool,sealed:bool,pre:bool,post:bool,order:bool,base:bool,
 signals:bool,fault:bool,accepted:bool}
 pure val empty:S={owner:1,captured:0,bound:false,registered:0,closed:0,known:true,
 source:true,raw:false,sealed:false,pre:false,post:false,order:true,base:true,
 signals:false,fault:false,accepted:false}
 var s:S
 pure def valid(s:S):bool=all{s.bound,s.owner==s.captured,s.registered>0,s.registered<=2,
 s.closed==s.registered,s.known,s.source,s.raw,s.sealed,s.pre,s.post,s.order,s.base,
 not(s.signals),not(s.fault)}
 action init={s'=empty}
 action bind=all{not(s.bound),not(s.fault),s'=s.with("bound",true).with("captured",s.owner)}
 action register(known:bool,source:bool)=all{s.bound,not(s.sealed),not(s.fault),s.owner==s.captured,s.registered<2,
 s'=s.with("registered",s.registered+1).with("known",s.known and known).with("source",s.source and source)}
 action terminal(normal:bool)=all{s.closed<s.registered,not(s.sealed),
 s'=if(normal) s.with("closed",s.closed+1) else s.with("fault",true).with("accepted",false)}
 action seal=all{s.closed==s.registered,not(s.fault),s.known,s.source,s.owner==s.captured,
 s'=s.with("sealed",true)}
 action capture(exact:bool)=all{s.sealed,not(s.fault),s'=s.with("raw",true).with("pre",exact).with("fault",not(exact))}
 action host(base:bool,order:bool,signals:bool,exact:bool)=all{s.raw,not(s.post),
 s'=s.with("post",exact).with("base",base).with("order",order).with("signals",signals)
 .with("fault",s.fault or not(base and order and not(signals) and exact)).with("accepted",false)}
 action decide={s'=s.with("accepted",valid(s))}
 action replace={s'=s.with("owner",s.owner+1).with("accepted",false)}
 action check(ok:bool)=all{assert(ok),s'=s}
 action good=bind.then(register(true,true)).then(terminal(true)).then(seal).then(capture(true))
 action step=any{bind,register(true,true),register(false,true),register(true,false),terminal(true),terminal(false),seal,capture(true),capture(false),host(true,true,false,true),host(false,true,false,true),host(true,false,false,true),host(true,true,true,true),host(true,true,false,false),decide,replace}
 val allProps=all{s.accepted implies valid(s),s.fault implies not(s.accepted),s.accepted implies not(s.signals)}
 run exactNormal=init.then(good).then(host(true,true,false,true)).then(decide).then(check(s.accepted))
 run noInputNoCredit=init.then(bind).then(seal).then(capture(true)).then(host(true,true,false,true)).then(decide).then(check(not(s.accepted)))
 run unknownRoleRefused=init.then(bind).then(register(false,true)).then(terminal(true)).then(decide).then(check(not(s.accepted)))
 run changedSourceRefused=init.then(bind).then(register(true,false)).then(terminal(true)).then(decide).then(check(not(s.accepted)))
 run runningClientRefused=init.then(bind).then(register(true,true)).then(decide).then(check(not(s.accepted)))
 run missingRawRefused=init.then(bind).then(register(true,true)).then(terminal(true)).then(seal).then(decide).then(check(not(s.accepted)))
 run badBeforeRefused=init.then(good).then(host(true,true,false,false)).then(decide).then(check(not(s.accepted)))
 run signalRefused=init.then(good).then(host(true,true,true,true)).then(decide).then(check(not(s.accepted)))
 run badHostRefused=init.then(good).then(host(false,true,false,true)).then(decide).then(check(not(s.accepted)))
 run reorderedStopsRefused=init.then(good).then(host(true,false,false,true)).then(decide).then(check(not(s.accepted)))
 run forceClientRefused=init.then(bind).then(register(true,true)).then(terminal(false)).then(decide).then(check(not(s.accepted)))
 run validReplacementRefused=init.then(good).then(replace).then(host(true,true,false,true)).then(decide).then(check(not(s.accepted)))
 run faultCannotRevive=init.then(good).then(host(true,true,true,true)).then(decide).then(decide).then(check(not(s.accepted)))
 run twoKnownClients=init.then(bind).then(register(true,true)).then(register(true,true)).then(terminal(true)).then(terminal(true)).then(seal).then(capture(true)).then(host(true,true,false,true)).then(decide).then(check(s.accepted))
}
