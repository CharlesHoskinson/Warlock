module reflow {
 type State={lease:int,pub:int,closed:int,waiting:bool,configured:int,renderedLease:int,renderedPub:int,accepted:bool,keyboard:int}
 var s:State
 action init=s'={lease:1,pub:1,closed:0,waiting:false,configured:1,renderedLease:1,renderedPub:1,accepted:false,keyboard:1}
 action resize=s'={...s,closed:s.lease,waiting:true,configured:0,renderedLease:0,renderedPub:0,accepted:false,keyboard:0}
 action renew(token:int):bool=s'=if(s.waiting and token==s.lease) {...s,lease:s.lease+1,pub:s.pub+1,waiting:false} else s
 action configure(token:int):bool=s'=if(not(s.waiting) and token==s.lease and token>s.closed) {...s,configured:token} else s
 action render(token:int,pub:int):bool=s'=if(not(s.waiting) and token==s.lease and token>s.closed and pub==s.pub) {...s,renderedLease:token,renderedPub:pub} else s
 action focus(token:int):bool=s'=if(not(s.waiting) and token==s.lease and token>s.closed) {...s,keyboard:token} else s
 val ready=not(s.waiting) and s.lease>s.closed and s.keyboard==s.lease and s.configured==s.lease and s.renderedLease==s.lease and s.renderedPub==s.pub
 action choose=s'={...s,accepted:ready}
 action step=any{focus(s.lease),focus(s.lease-1),resize,renew(s.lease),renew(s.lease-1),configure(s.lease),configure(s.lease-1),render(s.lease,s.pub),render(s.lease-1,s.pub-1),choose}
 val safety=(s.accepted implies ready) and s.closed<=s.lease
 run resizeBlocksTest=init.then(resize).then(choose).then(all{assert(not(s.accepted)),s'=s})
 run freshLeaseTest=init.then(resize).then(renew(1)).then(configure(2)).then(render(2,2)).then(focus(2)).then(choose).then(all{assert(s.accepted and s.lease==2),s'=s})
 run sameRetiredLeaseTest=init.then(resize).then(configure(1)).then(render(1,1)).then(choose).then(all{assert(not(s.accepted)),s'=s})
 run lateReflowTest=init.then(resize).then(renew(1)).then(renew(1)).then(all{assert(s.lease==2),s'=s})
 run staleRenderTest=init.then(resize).then(renew(1)).then(configure(2)).then(render(1,1)).then(choose).then(all{assert(not(s.accepted)),s'=s})
 run staleConfigureTest=init.then(resize).then(renew(1)).then(configure(1)).then(render(2,2)).then(choose).then(all{assert(not(s.accepted)),s'=s})
 run missingKeyboardTest=init.then(resize).then(renew(1)).then(configure(2)).then(render(2,2)).then(choose).then(all{assert(not(s.accepted)),s'=s})
 run staleKeyboardTest=init.then(resize).then(renew(1)).then(configure(2)).then(render(2,2)).then(focus(1)).then(choose).then(all{assert(not(s.accepted)),s'=s})
}
