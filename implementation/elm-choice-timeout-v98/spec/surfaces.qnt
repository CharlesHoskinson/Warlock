module surfaces {
 type State={pub:int,lease:int,barrier:int,open:bool,configured:int,appliedPub:int,appliedLease:int,pending:bool,issuedPub:int,issuedLease:int,focusedPub:int,focusedLease:int,accepted:bool,attempts:int,emitted:bool}
 var s:State
 pure def issue(x:State):State=if(x.pending and x.open and x.configured==x.lease and x.appliedPub==x.pub and x.appliedLease==x.lease) {...x,pending:false,issuedPub:x.pub,issuedLease:x.lease} else x
 action init=s'={pub:1,lease:0,barrier:0,open:false,configured:0,appliedPub:0,appliedLease:0,pending:false,issuedPub:0,issuedLease:0,focusedPub:0,focusedLease:0,accepted:false,attempts:0,emitted:false}
 action openView=all{not(s.open),s'={...s,pub:s.pub+1,lease:s.lease+1,open:true,configured:0,appliedPub:0,appliedLease:0,pending:true,issuedPub:0,issuedLease:0,accepted:false,emitted:false}}
 action configure=all{s.open,s'=issue({...s,configured:s.lease,accepted:false,emitted:false})}
 action applyView=all{s.open,s'=issue({...s,appliedPub:s.pub,appliedLease:s.lease,accepted:false,emitted:false})}
 action publish=all{s.open,s'={...s,pub:s.pub+1,appliedPub:0,appliedLease:0,pending:false,issuedPub:0,issuedLease:0,accepted:false,emitted:false}}
 action publishFocus=all{s.open,s'={...s,pub:s.pub+1,appliedPub:0,appliedLease:0,pending:true,issuedPub:0,issuedLease:0,accepted:false,emitted:false}}
 action focusAck=all{s.open,s.issuedPub==s.pub,s.issuedLease==s.lease,s.configured==s.lease,s.appliedPub==s.pub,s.appliedLease==s.lease,s'={...s,focusedPub:s.pub,focusedLease:s.lease,issuedPub:0,issuedLease:0,accepted:true,emitted:false}}
 action close=all{s.open,s'={...s,open:false,barrier:s.lease,configured:0,appliedPub:0,appliedLease:0,pending:false,issuedPub:0,issuedLease:0,accepted:false,emitted:false}}
 action launch=all{s.open,s.configured==s.lease,s.appliedPub==s.pub,s.appliedLease==s.lease,s'={...s,open:false,barrier:s.lease,configured:0,appliedPub:0,appliedLease:0,pending:false,issuedPub:0,issuedLease:0,accepted:false,attempts:s.attempts+1,emitted:true}}
 action reject=s'={...s,accepted:false,emitted:false}
 action step=any{openView,configure,applyView,publish,publishFocus,focusAck,close,launch,reject}
 val ready=s.open and s.lease>s.barrier and s.configured==s.lease and s.appliedPub==s.pub and s.appliedLease==s.lease
 val safety=all{s.accepted implies ready and s.focusedPub==s.pub and s.focusedLease==s.lease,s.issuedPub>0 implies ready and s.issuedPub==s.pub and s.issuedLease==s.lease,s.emitted implies not(s.open),s.barrier<=s.lease}
 run configureFirstTest=init.then(openView).then(configure).then(all{assert(s.issuedPub==0),s'=s}).then(applyView).then(focusAck).then(all{assert(s.accepted),s'=s})
 run renderFirstTest=init.then(openView).then(applyView).then(all{assert(s.issuedPub==0),s'=s}).then(configure).then(focusAck).then(all{assert(s.accepted),s'=s})
 run staleRenderTest=init.then(openView).then(configure).then(applyView).then(publish).then(reject).then(all{assert(not(s.accepted) and s.issuedPub==0),s'=s})
 run staleFocusTest=init.then(openView).then(configure).then(applyView).then(publishFocus).then(reject).then(all{assert(s.issuedPub==0 and s.focusedPub==0),s'=s})
 run currentReplacementTest=init.then(openView).then(configure).then(applyView).then(close).then(openView).then(reject).then(all{assert(s.lease==2 and s.issuedPub==0 and s.configured==0),s'=s})
 run duplicateFocusTest=init.then(openView).then(configure).then(applyView).then(focusAck).then(reject).then(all{assert(s.issuedPub==0 and not(s.accepted)),s'=s})
 run prematureActionTest=init.then(openView).then(applyView).then(reject).then(all{assert(s.attempts==0),s'=s})
 run launchCloseTest=init.then(openView).then(configure).then(applyView).then(launch).then(all{assert(s.attempts==1 and not(s.open)),s'=s})
 run refreshFocusTest=init.then(openView).then(configure).then(applyView).then(focusAck).then(publishFocus).then(applyView).then(focusAck).then(all{assert(s.accepted and s.focusedPub==3 and s.lease==1),s'=s})
}
