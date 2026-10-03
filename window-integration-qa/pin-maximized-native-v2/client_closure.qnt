module client_closure {
 type Client={role:int,registered:bool,life:int,reportLife:int,argv:int,reportArgv:int,
   source:int,frozenSource:int,beforeRc:int,afterRc:int,beforeGone:bool,
   reportGone:bool,reportRc:int,forced:bool,error:bool,signals:int,reaped:bool}
 pure val good:Client={role:4,registered:true,life:1,reportLife:1,argv:1,reportArgv:1,
   source:1,frozenSource:1,beforeRc:0,afterRc:0,beforeGone:true,reportGone:true,
   reportRc:0,forced:false,error:false,signals:0,reaped:true}
 pure def known(c:Client):bool=c.role.in(4.to(9))
 pure def normal(c:Client):bool=all{known(c),c.registered,c.life>0,c.life==c.reportLife,
   c.argv>0,c.argv==c.reportArgv,c.source>0,c.source==c.frozenSource,
   c.beforeRc==0,c.afterRc==0,c.beforeGone,c.reportGone,c.reportRc==0,
   not(c.forced),not(c.error),c.signals==0,c.reaped}
 type Closure={caseSource:bool,reportBound:bool,caseNormal:bool,unique:bool,
   exactRoles:bool,reverseRegistry:bool,baseNormal:bool,beforeCaptured:bool,
   delegatedUnchanged:bool,rawPersisted:bool,client:Client}
 pure val healthy:Closure={caseSource:true,reportBound:true,caseNormal:true,unique:true,
   exactRoles:true,reverseRegistry:true,baseNormal:true,beforeCaptured:true,
   delegatedUnchanged:true,rawPersisted:true,client:good}
 pure def accepted(c:Closure):bool=all{c.caseSource,c.reportBound,c.caseNormal,c.unique,
   c.exactRoles,c.reverseRegistry,c.baseNormal,c.beforeCaptured,c.delegatedUnchanged,
   c.rawPersisted,normal(c.client)}
 var client:Client
 action init={client'=good}
 action check(ok:bool):bool=all{assert(ok),client'=client}
 action step={
   nondet role=0.to(10).oneOf()
   nondet source=1.to(2).oneOf()
   nondet life=1.to(2).oneOf()
   nondet argv=1.to(2).oneOf()
   nondet rc=Set(-15,-9,0,1).oneOf()
   nondet gone=Set(true,false).oneOf()
   nondet signals=0.to(2).oneOf()
   nondet forced=Set(true,false).oneOf()
   client'=good.with("role",role).with("source",source).with("life",life)
     .with("argv",argv).with("beforeRc",rc).with("beforeGone",gone)
     .with("signals",signals).with("forced",forced)
 }
 val allProps=all{normal(client) implies known(client),
   normal(client) implies (client.signals==0 and not(client.forced)),
   normal(client) implies (client.beforeRc==0 and client.afterRc==0),
   normal(client) implies (client.life==client.reportLife and client.source==client.frozenSource),
   normal(client) implies (client.beforeGone and client.reportGone)}
 run actualRegisteredClosedClient=init.then(check(normal(good)))
 run allSixKnownRoles=init.then(check(4.to(9).forall(r=>normal(good.with("role",r)))))
 run originalBaseRowsRemainRequired=init.then(check(not(accepted(healthy.with("baseNormal",false)))))
 run arbitraryExtraRoleRefused=init.then(check(not(normal(good.with("role",10)))))
 run currentLifetimeReplacementRefused=init.then(check(not(normal(good.with("life",2)))))
 run commandReplacementRefused=init.then(check(not(normal(good.with("argv",2)))))
 run executableReplacementRefused=init.then(check(not(normal(good.with("source",2)))))
 run runningBeforeDelegatedCloseRefused=init.then(check(not(normal(good.with("beforeRc",1)))))
 run kernelLifetimeNotGoneRefused=init.then(check(not(normal(good.with("beforeGone",false)))))
 run missingCleanupReceiptRefused=init.then(check(not(normal(good.with("reportGone",false)))))
 run cleanupNonzeroRefused=init.then(check(not(normal(good.with("reportRc",1)))))
 run clientTermIsNotNormal=init.then(check(not(normal(good.with("afterRc",-15)))))
 run clientKillIsNotNormal=init.then(check(not(normal(good.with("afterRc",-9)))))
 run clientSignalEvenZeroRefused=init.then(check(not(normal(good.with("signals",1)))))
 run forcedCaseCleanupRefused=init.then(check(not(normal(good.with("forced",true)))))
 run clientErrorRefused=init.then(check(not(normal(good.with("error",true)))))
 run missingReapRefused=init.then(check(not(normal(good.with("reaped",false)))))
 run missingCaseSourceRefused=init.then(check(not(accepted(healthy.with("caseSource",false)))))
 run missingBoundRawReportRefused=init.then(check(not(accepted(healthy.with("reportBound",false)))))
 run failedCaseCleanupRefused=init.then(check(not(accepted(healthy.with("caseNormal",false)))))
 run duplicateRegistryRefused=init.then(check(not(accepted(healthy.with("unique",false)))))
 run missingRoleRefused=init.then(check(not(accepted(healthy.with("exactRoles",false)))))
 run fullReverseRegistryRequired=init.then(check(not(accepted(healthy.with("reverseRegistry",false)))))
 run beforeCloseObservationRequired=init.then(check(not(accepted(healthy.with("beforeCaptured",false)))))
 run noNewStopSemantics=init.then(check(not(accepted(healthy.with("delegatedUnchanged",false)))))
 run rawBeforePredicateRequired=init.then(check(not(accepted(healthy.with("rawPersisted",false)))))
}
