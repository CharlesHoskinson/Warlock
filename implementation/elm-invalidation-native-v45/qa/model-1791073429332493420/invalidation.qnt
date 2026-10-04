module invalidation {
 type State={native:int,view:int,focus:int,mutations:int,hint:bool,connected:bool,reading:bool,readRevision:int}
 var s:State
 action init=s'={native:1,view:1,focus:2,mutations:0,hint:false,connected:true,reading:false,readRevision:0}
 action unfocusedMinimize=s'={...s,native:s.native+1,mutations:s.mutations+1,hint:s.connected or s.hint}
 action activate=s'={...s,native:s.native+1,focus:1,mutations:s.mutations+1,hint:s.connected or s.hint}
 action uncertainMutation=s'={...s,native:s.native+1,mutations:s.mutations+1,hint:s.connected or s.hint}
 action refusal=s'=s
 action exactRetry=s'=s
 action read=all{s.connected,s.hint,not(s.reading),s'={...s,reading:true,readRevision:s.native,hint:false}}
 action publish=all{s.connected,s.reading,s'={...s,view:if(s.readRevision==s.native) s.native else s.view,reading:false,hint:s.hint or s.readRevision!=s.native}}
 action disconnect=s'={...s,connected:false,reading:false}
 action reconnect=s'={...s,connected:true,hint:true}
 action step=any{unfocusedMinimize,activate,uncertainMutation,refusal,exactRetry,read,publish,disconnect,reconnect}
 val safety=all{s.view<=s.native,s.native==s.mutations+1,not(s.connected) implies not(s.reading)}
 run unfocusedChangeTest=init.then(unfocusedMinimize).then(read).then(publish).then(all{assert(s.view==2 and s.focus==2 and s.mutations==1),s'=s})
 run focusChangeTest=init.then(activate).then(read).then(publish).then(all{assert(s.view==2 and s.focus==1),s'=s})
 run coalescedHintsTest=init.then(unfocusedMinimize).then(activate).then(read).then(publish).then(all{assert(s.view==3 and s.mutations==2),s'=s})
 run racedReadTest=init.then(unfocusedMinimize).then(read).then(activate).then(publish).then(all{assert(s.view==1 and s.hint),s'=s}).then(read).then(publish).then(all{assert(s.view==3),s'=s})
 run reconnectReconcilesWithoutMutationTest=init.then(disconnect).then(unfocusedMinimize).then(reconnect).then(read).then(publish).then(all{assert(s.view==2 and s.mutations==1),s'=s})
 run refusalNoHintTest=init.then(refusal).then(all{assert(not(s.hint) and s.mutations==0),s'=s})
 run retryNoMutationTest=init.then(unfocusedMinimize).then(read).then(publish).then(exactRetry).then(all{assert(not(s.hint) and s.mutations==1),s'=s})
 run unknownInvalidatesTest=init.then(uncertainMutation).then(read).then(publish).then(all{assert(s.view==2 and s.mutations==1),s'=s})
}
