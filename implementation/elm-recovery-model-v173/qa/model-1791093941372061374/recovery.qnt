module recovery {
 type State={phase:str,epoch:int,reserved:int,bridge:bool,backend:bool,accepted:bool,lastEpoch:int,effects:int}
 var s:State
 action init=s'={phase:"Live",epoch:1,reserved:48,bridge:true,backend:true,accepted:false,lastEpoch:0,effects:0}
 action failure=s'=if(s.phase=="Live"){...s,phase:"Drain",bridge:false,accepted:false} else {...s,accepted:false}
 action drained=s'=if(s.phase=="Drain"){...s,phase:"Recovery",backend:false,accepted:false} else {...s,accepted:false}
 action nativeRestart=s'=if(s.phase=="Recovery"){...s,phase:"RestartRequested",reserved:0,accepted:false} else {...s,accepted:false}
 action launch=s'=if(s.phase=="RestartRequested"){...s,phase:"Starting",epoch:s.epoch+1,backend:true,accepted:false} else {...s,accepted:false}
 action snapshot(epoch:int):bool=s'=if(s.phase=="Starting" and epoch==s.epoch){...s,phase:"Live",reserved:48,bridge:true,accepted:false} else {...s,accepted:false}
 action rendererIntent(epoch:int):bool=s'=if(s.phase=="Live" and s.bridge and s.backend and epoch==s.epoch){...s,accepted:true,lastEpoch:epoch,effects:s.effects+1} else {...s,accepted:false}
 action stop=s'={...s,phase:"Stopped",reserved:0,bridge:false,backend:false,accepted:false}
 action step=any{failure,drained,nativeRestart,launch,snapshot(s.epoch),snapshot(s.epoch-1),rendererIntent(s.epoch),rendererIntent(s.epoch-1),stop}
 val safety=(s.phase=="Recovery" implies (s.reserved==48 and not(s.bridge) and not(s.backend))) and
   (s.accepted implies (s.phase=="Live" and s.bridge and s.backend and s.lastEpoch==s.epoch)) and
   (s.phase=="Stopped" implies (s.reserved==0 and not(s.bridge) and not(s.backend))) and
   (s.phase=="Drain" implies not(s.bridge))
 run failureReservationTest=init.then(failure).then(drained).then(all{assert(safety and s.reserved==48),s'=s})
 run recoveryIngressTest=init.then(failure).then(drained).then(rendererIntent(1)).then(all{assert(not(s.accepted) and s.effects==0),s'=s})
 run earlyRestartTest=init.then(nativeRestart).then(all{assert(s.phase=="Live"),s'=s})
 run restartFreshSnapshotTest=init.then(failure).then(drained).then(nativeRestart).then(launch).then(rendererIntent(2)).then(all{assert(not(s.accepted) and s.phase=="Starting"),s'=s}).then(snapshot(2)).then(rendererIntent(2)).then(all{assert(s.accepted and s.effects==1 and safety),s'=s})
 run retiredEpochTest=init.then(failure).then(drained).then(nativeRestart).then(launch).then(snapshot(2)).then(rendererIntent(1)).then(all{assert(not(s.accepted) and s.effects==0),s'=s})
 run stopCancelsRecoveryTest=init.then(failure).then(drained).then(stop).then(nativeRestart).then(launch).then(all{assert(s.phase=="Stopped" and safety),s'=s})
}
