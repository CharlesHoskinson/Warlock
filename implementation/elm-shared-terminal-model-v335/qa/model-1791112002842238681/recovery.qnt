module recovery {
 type State={held:bool,pending:bool,popup:bool,valid:bool,expired:bool,closed:int,qualified:int}
 var s:State
 action init=s'={held:false,pending:false,popup:true,valid:true,expired:false,closed:0,qualified:0}
 action press=s'=if(s.popup and not(s.held)){...s,held:true,pending:true,valid:true,expired:false} else s
 action replay=s'=s
 action repeat=s'=if(s.held){...s,valid:false} else s
 action wrongRelease=s'=s
 action retire=s'={...s,popup:false,pending:false,valid:false}
 action changeScope=s'={...s,valid:false}
 action expire=s'={...s,expired:true}
 action release=s'=if(s.held){...s,held:false,pending:false,popup:if(s.pending and s.valid and not(s.expired))false else s.popup,closed:s.closed+(if(s.pending and s.valid and not(s.expired))1 else 0),qualified:s.qualified+(if(s.pending and s.valid and not(s.expired))1 else 0)} else s
 action reopen=s'=if(not(s.popup) and not(s.held)){...s,popup:true,valid:true,expired:false} else s
 action step=any{press,replay,repeat,wrongRelease,retire,changeScope,expire,release,reopen}
 val safety=(not(s.pending) or s.held) and s.closed==s.qualified and s.closed>=0
 run pressNeverClosesTest=init.then(press).then(all{assert(s.popup and s.pending and s.held and s.closed==0),s'=s})
 run releaseOnceTest=init.then(press).then(release).then(release).then(all{assert(not(s.popup) and not(s.held) and not(s.pending) and s.closed==1),s'=s})
 run secondEscapeTest=init.then(press).then(release).then(reopen).then(press).then(release).then(all{assert(s.closed==2 and not(s.held)),s'=s})
 run forgedReleaseTest=init.then(press).then(wrongRelease).then(all{assert(s.popup and s.held and s.pending and s.closed==0),s'=s})
 run retirementKeepsHeldTest=init.then(press).then(retire).then(reopen).then(all{assert(s.held and not(s.pending) and not(s.popup) and s.closed==0),s'=s})
 run scopeChangeRefusesTest=init.then(press).then(changeScope).then(release).then(all{assert(s.popup and not(s.held) and s.closed==0),s'=s})
 run deadlineNeverRenewedTest=init.then(press).then(expire).then(release).then(all{assert(s.popup and s.closed==0 and not(s.pending)),s'=s})
 run repeatNeverClosesTest=init.then(press).then(repeat).then(release).then(all{assert(s.popup and s.closed==0),s'=s})
 run replayPreservesOriginalTest=init.then(press).then(replay).then(release).then(all{assert(s.closed==1 and not(s.held)),s'=s})
}
