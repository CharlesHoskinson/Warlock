module recovery {
 type State={phase:str,epoch:int,hostId:int,hostEpoch:int,publishedId:int,brokerId:int,brokerEpoch:int,receipt:str,forwards:int,unknownShown:bool}
 var s:State
 action init=s'={phase:"Live",epoch:1,hostId:0,hostEpoch:0,publishedId:0,brokerId:0,brokerEpoch:0,receipt:"Empty",forwards:0,unknownShown:false}
 val uncertain=s.hostId>0 and (s.brokerId!=s.hostId or s.brokerEpoch!=s.hostEpoch or s.receipt=="Pending")
 action admit(epoch:int):bool=s'=if(s.phase=="Live" and epoch==s.epoch and (s.hostId==0 or not(uncertain) or s.unknownShown)){...s,hostId:s.hostId+1,hostEpoch:epoch,unknownShown:false} else s
 action publish=s'=if(s.phase=="Live" and s.hostEpoch==s.epoch){...s,publishedId:s.hostId} else s
 action read=s'=if(s.phase=="Live" and s.publishedId==s.hostId and s.hostId>s.brokerId and s.hostEpoch==s.epoch){...s,brokerId:s.hostId,brokerEpoch:s.epoch,receipt:"Pending",forwards:s.forwards+1} else s
 action settle(id:int,epoch:int):bool=s'=if(s.phase=="Live" and id==s.hostId and id==s.brokerId and epoch==s.hostEpoch and epoch==s.epoch and s.receipt=="Pending"){...s,receipt:"Committed"} else s
 action failure=s'={...s,phase:"Stopped",unknownShown:false}
 action restart=s'=if(s.phase=="Stopped"){...s,phase:"Reconciling",epoch:s.epoch+1,unknownShown:uncertain} else s
 action snapshot=s'=if(s.phase=="Reconciling"){...s,phase:"Live"} else s
 action step=any{admit(s.epoch),admit(s.epoch-1),publish,read,settle(s.hostId,s.epoch),settle(s.hostId-1,s.epoch),settle(s.hostId,s.epoch-1),failure,restart,snapshot}
 val safety=s.publishedId<=s.hostId and s.brokerId<=s.hostId and s.forwards<=s.hostId and (s.unknownShown implies uncertain) and (s.brokerId>0 implies s.brokerEpoch<=s.epoch)
 run unreadAdmissionRecoversUnknownTest=init.then(admit(1)).then(publish).then(failure).then(restart).then(snapshot).then(all{assert(s.unknownShown and s.forwards==0 and safety),s'=s})
 run durableAdmissionBeforePublicationTest=init.then(publish).then(read).then(all{assert(s.hostId==0 and s.publishedId==0 and s.forwards==0),s'=s}).then(admit(1)).then(publish).then(all{assert(s.hostId==s.publishedId and uncertain),s'=s})
 run matchingSettlementResolvesAdmissionTest=init.then(admit(1)).then(publish).then(read).then(settle(1,1)).then(failure).then(restart).then(all{assert(not(s.unknownShown) and not(uncertain)),s'=s})
 run olderCommitCannotResolveNewAdmissionTest=init.then(admit(1)).then(publish).then(read).then(settle(1,1)).then(admit(1)).then(failure).then(restart).then(all{assert(s.unknownShown and s.brokerId==1 and s.hostId==2),s'=s})
 run staleBindingCannotAdmitTest=init.then(admit(0)).then(all{assert(s.hostId==0 and safety),s'=s})
 run noReplayAfterReplacementTest=init.then(admit(1)).then(publish).then(failure).then(restart).then(snapshot).then(read).then(all{assert(s.forwards==0 and s.unknownShown),s'=s})
 run freshExplicitIntentCanProceedTest=init.then(admit(1)).then(publish).then(failure).then(restart).then(snapshot).then(admit(2)).then(publish).then(read).then(settle(2,2)).then(all{assert(s.forwards==1 and s.hostId==2 and not(uncertain) and safety),s'=s})
 run wrongReceiptCannotResolveTest=init.then(admit(1)).then(publish).then(read).then(settle(1,0)).then(settle(2,1)).then(all{assert(uncertain and s.receipt=="Pending"),s'=s})
}
