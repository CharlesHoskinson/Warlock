module activation {
 type Receipt={status:str,before:int,after:int,minBefore:bool,minAfter:bool,focus:int,keyboard:int,recipient:int}
 type State={revision:int,minimized:bool,eligible:bool,modal:int,grab:bool,focus:int,keyboard:int,mutations:int,request:int,intentRevision:int,pending:bool,connected:bool,receipt:Receipt}
 var s:State
 pure val emptyReceipt={status:"Idle",before:0,after:0,minBefore:false,minAfter:false,focus:2,keyboard:2,recipient:2}
 action init=s'={revision:1,minimized:false,eligible:true,modal:0,grab:false,focus:2,keyboard:2,mutations:0,request:0,intentRevision:0,pending:false,connected:true,receipt:emptyReceipt}
 action begin=all{s.connected,not(s.pending),s'={...s,request:s.request+1,intentRevision:s.revision,pending:true,receipt:{...emptyReceipt,status:"Pending"}}}
 action minimize=s'={...s,minimized:true,revision:s.revision+1}
 action modal=s'={...s,modal:1,revision:s.revision+1}
 action ambiguous=s'={...s,modal:2,revision:s.revision+1}
 action grab=s'={...s,grab:true,revision:s.revision+1}
 action ineligible=s'={...s,eligible:false,revision:s.revision+1}
 val allowed=s.connected and s.pending and s.intentRevision==s.revision and not(s.minimized) and s.eligible and not(s.grab) and s.modal!=2
 val recipient=if(s.modal==1) 1 else 0
 action perform=all{s.pending,
   if(allowed) s'={...s,pending:false,focus:recipient,keyboard:recipient,mutations:s.mutations+1,revision:s.revision+1,receipt:{status:"Committed",before:s.mutations,after:s.mutations+1,minBefore:s.minimized,minAfter:s.minimized,focus:recipient,keyboard:recipient,recipient:recipient}}
   else s'={...s,pending:false,receipt:{status:"Refused",before:s.mutations,after:s.mutations,minBefore:s.minimized,minAfter:s.minimized,focus:s.focus,keyboard:s.keyboard,recipient:recipient}}
 }
 action badSeat=all{allowed,s'={...s,pending:false,focus:recipient,mutations:s.mutations+1,revision:s.revision+1,receipt:{status:"Committed",before:s.mutations,after:s.mutations+1,minBefore:s.minimized,minAfter:s.minimized,focus:recipient,keyboard:s.keyboard,recipient:recipient}}}
 action disconnect=s'={...s,connected:false,pending:false,receipt:{...s.receipt,status:if(s.pending) "Unknown" else s.receipt.status}}
 action reconnect=s'={...s,connected:true}
 action step=any{begin,minimize,modal,ambiguous,grab,ineligible,perform,badSeat,disconnect,reconnect}
 val safety=all{
  s.receipt.minBefore==s.receipt.minAfter,
  s.receipt.status=="Committed" implies s.receipt.focus==s.receipt.recipient and s.receipt.keyboard==s.receipt.recipient,
  s.receipt.status=="Refused" implies s.receipt.before==s.receipt.after,
  not(s.connected) implies not(s.pending)
 }
 run visibleActivateTest=init.then(begin).then(perform).then(all{assert(s.receipt.status=="Committed" and s.focus==0),s'=s})
 run minimizedRefusalTest=init.then(minimize).then(begin).then(perform).then(all{assert(s.receipt.status=="Refused" and s.minimized and s.focus==2),s'=s})
 run modalRedirectTest=init.then(modal).then(begin).then(perform).then(all{assert(s.receipt.status=="Committed" and s.focus==1 and s.keyboard==1),s'=s})
 run ambiguousRefusalTest=init.then(ambiguous).then(begin).then(perform).then(all{assert(s.receipt.status=="Refused" and s.focus==2),s'=s})
 run grabRefusalTest=init.then(grab).then(begin).then(perform).then(all{assert(s.receipt.status=="Refused" and s.focus==2),s'=s})
 run ineligibleRefusalTest=init.then(ineligible).then(begin).then(perform).then(all{assert(s.receipt.status=="Refused" and s.focus==2),s'=s})
 run staleContextTest=init.then(begin).then(modal).then(perform).then(all{assert(s.receipt.status=="Refused" and s.mutations==0),s'=s})
 run unknownSeatPostconditionTest=init.then(begin).then(badSeat).then(all{assert(s.receipt.status=="Unknown" and s.keyboard!=s.focus),s'=s})
 run disconnectUnknownTest=init.then(begin).then(disconnect).then(all{assert(s.receipt.status=="Unknown" and not(s.pending)),s'=s})
 run noAutomaticReplayTest=init.then(begin).then(disconnect).then(reconnect).then(all{assert(s.receipt.status=="Unknown" and not(s.pending) and s.mutations==0),s'=s})
}
