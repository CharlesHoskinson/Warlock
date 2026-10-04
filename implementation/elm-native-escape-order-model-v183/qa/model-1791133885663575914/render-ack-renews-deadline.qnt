module recovery {
 type State={held:bool,domCurrent:bool,available:bool,released:bool,pending:bool,popup:bool,valid:bool,expired:bool,closed:int,qualified:int}
 var s:State
 action init=s'={held:false,domCurrent:true,available:false,released:false,pending:false,popup:true,valid:true,expired:false,closed:0,qualified:0}
 action press=s'=if(s.popup and not(s.held)){...s,held:true,available:true,released:false,pending:false,valid:true,expired:false} else s
 action web=s'=if(s.available and s.domCurrent and s.popup and s.valid and not(s.expired) and s.held!=s.released){...s,available:false,pending:s.held,popup:not(s.released),closed:s.closed+(if(s.released)1 else 0),qualified:s.qualified+(if(s.released)1 else 0)} else s
 action nativeEscape=s'=if(s.available and s.popup and s.valid and not(s.expired) and s.held and not(s.released) and not(s.pending)){...s,available:false,pending:true} else s
 action renderLag=s'={...s,domCurrent:false}
 action renderAck=s'={...s,domCurrent:true,expired:false}
 action replay=s'=s
 action repeat=s'=if(s.held){...s,valid:false,available:false} else s
 action wrongRelease=s'=s
 action retire=s'={...s,popup:false,pending:false,valid:false,available:false}
 action changeScope=s'={...s,valid:false,available:false}
 action expire=s'={...s,expired:true}
 action release=s'=if(s.held){...s,held:false,released:true,pending:false,popup:if(s.pending and s.valid and not(s.expired))false else s.popup,closed:s.closed+(if(s.pending and s.valid and not(s.expired))1 else 0),qualified:s.qualified+(if(s.pending and s.valid and not(s.expired))1 else 0)} else s
 action reopen=s'=if(not(s.popup) and not(s.held)){...s,popup:true,valid:true,expired:false,available:false,released:false} else s
 action step=any{press,web,nativeEscape,renderLag,renderAck,replay,repeat,wrongRelease,retire,changeScope,expire,release,reopen}
 val safety=(not(s.pending) or (s.held and not(s.available))) and (not(s.released) or not(s.held)) and s.closed==s.qualified and s.closed>=0
 run pressNeverClosesTest=init.then(press).then(web).then(all{assert(s.popup and s.pending and s.held and s.closed==0),s'=s})
 run releaseOnceTest=init.then(press).then(web).then(release).then(release).then(web).then(all{assert(not(s.popup) and not(s.held) and not(s.pending) and s.closed==1),s'=s})
 run secondEscapeTest=init.then(press).then(web).then(release).then(reopen).then(press).then(web).then(release).then(all{assert(s.closed==2 and not(s.held)),s'=s})
 run forgedReleaseTest=init.then(press).then(web).then(wrongRelease).then(all{assert(s.popup and s.held and s.pending and s.closed==0),s'=s})
 run retirementKeepsHeldTest=init.then(press).then(web).then(retire).then(reopen).then(all{assert(s.held and not(s.pending) and not(s.popup) and s.closed==0),s'=s})
 run scopeChangeRefusesTest=init.then(press).then(web).then(changeScope).then(release).then(all{assert(s.popup and not(s.held) and s.closed==0),s'=s})
 run deadlineNeverRenewedTest=init.then(press).then(web).then(expire).then(release).then(all{assert(s.popup and s.closed==0 and not(s.pending)),s'=s})
 run repeatNeverClosesTest=init.then(press).then(web).then(repeat).then(release).then(all{assert(s.popup and s.closed==0),s'=s})
 run replayPreservesOriginalTest=init.then(press).then(web).then(replay).then(release).then(all{assert(s.closed==1 and not(s.held)),s'=s})
 run earlyReleaseTest=init.then(press).then(release).then(all{assert(s.popup and s.available and s.released and s.closed==0),s'=s}).then(web).then(all{assert(not(s.popup) and s.closed==1),s'=s})
 run earlyReleaseOnceTest=init.then(press).then(release).then(web).then(web).then(release).then(all{assert(s.closed==1 and not(s.available)),s'=s})
 run expiredEarlyReleaseTest=init.then(press).then(release).then(expire).then(web).then(all{assert(s.popup and s.closed==0),s'=s})
 run changedEarlyReleaseTest=init.then(press).then(release).then(changeScope).then(web).then(all{assert(s.popup and s.closed==0),s'=s})
 run webWithoutNativePressTest=init.then(web).then(release).then(web).then(all{assert(s.popup and s.closed==0 and not(s.available)),s'=s})
 run nativeEscapeBeforeDOMAckTest=init.then(press).then(renderLag).then(nativeEscape).then(all{assert(s.popup and s.held and s.pending and not(s.available) and s.closed==0),s'=s}).then(release).then(all{assert(not(s.popup) and s.closed==1),s'=s})
 run staleDOMCallbackStillRefusedTest=init.then(press).then(renderLag).then(web).then(release).then(all{assert(s.popup and s.closed==0),s'=s})
 run nativeEscapeOneReleaseOnceTest=init.then(press).then(renderLag).then(nativeEscape).then(web).then(release).then(release).then(renderAck).then(web).then(all{assert(s.closed==1 and not(s.available)),s'=s})
 run nativeEscapeScopeChangeRefusedTest=init.then(press).then(nativeEscape).then(changeScope).then(release).then(all{assert(s.popup and s.closed==0),s'=s})
 run nativeEscapeDeadlineNeverRenewedTest=init.then(press).then(renderLag).then(nativeEscape).then(expire).then(renderAck).then(release).then(all{assert(s.popup and s.closed==0 and s.expired),s'=s})
 run nativeEscapeRepeatRefusedTest=init.then(press).then(nativeEscape).then(repeat).then(release).then(all{assert(s.popup and s.closed==0),s'=s})
 run nativeEscapeRetirementRefusedTest=init.then(press).then(nativeEscape).then(retire).then(release).then(all{assert(s.closed==0 and not(s.pending)),s'=s})
 run nativeEscapeWithoutPhysicalPressTest=init.then(nativeEscape).then(release).then(all{assert(s.popup and s.closed==0 and not(s.pending)),s'=s})
 run nativeEscapeCannotApproveOldReleaseTest=init.then(press).then(release).then(nativeEscape).then(all{assert(s.popup and s.closed==0 and not(s.pending)),s'=s})
 run nativeEscapeExpiredPressRefusedTest=init.then(press).then(expire).then(nativeEscape).then(all{assert(s.popup and not(s.pending) and s.available and s.closed==0),s'=s})
}
