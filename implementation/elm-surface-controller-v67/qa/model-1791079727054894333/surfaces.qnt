module surfaces {
 type State={publication:int,lease:int,open:bool,framePublication:int,frameLease:int,frameOpen:bool,barrier:int,hostOpen:bool,hostLease:int,shown:int,shownLease:int,attempts:int,emitted:bool}
 var s:State
 action init=s'={publication:1,lease:0,open:false,framePublication:0,frameLease:0,frameOpen:false,barrier:0,hostOpen:false,hostLease:0,shown:0,shownLease:0,attempts:0,emitted:false}
 action openView=all{not(s.open),s'={...s,publication:s.publication+1,lease:s.lease+1,open:true,emitted:false}}
 action refresh=s'={...s,publication:s.publication+1,emitted:false}
 action publish=s'={...s,framePublication:s.publication,frameLease:s.lease,frameOpen:s.open,emitted:false}
 action deliver=s'={...s,hostOpen:s.frameOpen and s.frameLease>s.barrier,hostLease:if(s.frameOpen and s.frameLease>s.barrier) s.frameLease else s.hostLease,shown:if(s.framePublication>s.shown and s.frameLease>=s.shownLease) s.framePublication else s.shown,shownLease:if(s.framePublication>s.shown and s.frameLease>=s.shownLease) s.frameLease else s.shownLease,emitted:false}
 action nativeClose=all{s.hostOpen,s'={...s,barrier:s.hostLease,hostOpen:false,emitted:false}}
 action dismiss=all{s.lease==s.barrier,s'={...s,open:false,publication:s.publication+1,emitted:false}}
 action launch=all{s.open,s.hostOpen,s.shown==s.publication,s.shownLease==s.lease,s'={...s,open:false,hostOpen:false,barrier:s.lease,publication:s.publication+1,attempts:s.attempts+1,emitted:true}}
 action reject=s'={...s,emitted:false}
 action step=any{openView,refresh,publish,deliver,nativeClose,dismiss,launch,reject}
 val safety=all{s.hostOpen implies s.hostLease>s.barrier,s.emitted implies not(s.open) and not(s.hostOpen),s.shown<=s.publication,s.shownLease<=s.lease,s.barrier<=s.lease}
 run openTest=init.then(openView).then(publish).then(deliver).then(all{assert(s.hostOpen),s'=s})
 run delayedFrameTest=init.then(openView).then(publish).then(deliver).then(nativeClose).then(deliver).then(all{assert(not(s.hostOpen)),s'=s})
 run refreshAfterNativeCloseTest=init.then(openView).then(publish).then(deliver).then(nativeClose).then(refresh).then(publish).then(deliver).then(all{assert(not(s.hostOpen)),s'=s})
 run newLeaseTest=init.then(openView).then(publish).then(deliver).then(nativeClose).then(dismiss).then(openView).then(publish).then(deliver).then(all{assert(s.hostOpen and s.lease==2),s'=s})
 run refreshLeaseTest=init.then(openView).then(refresh).then(all{assert(s.lease==1),s'=s})
 run staleCallbackTest=init.then(openView).then(publish).then(deliver).then(refresh).then(reject).then(all{assert(s.attempts==0),s'=s})
 run launchCloseTest=init.then(openView).then(publish).then(deliver).then(launch).then(all{assert(s.attempts==1 and not(s.open) and not(s.hostOpen)),s'=s})
 run duplicateLaunchTest=init.then(openView).then(publish).then(deliver).then(launch).then(reject).then(all{assert(s.attempts==1),s'=s})
}
