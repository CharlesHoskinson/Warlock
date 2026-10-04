module recovery {
 type State={host:int,hp:int,broker:int,bp:int,status:str,next:int}
 var s:State
 action init=s'={host:0,hp:1,broker:0,bp:1,status:"Empty",next:1}
 action admit(p:int):bool=s'={...s,host:s.next,hp:p,next:s.next+1}
 action submit=s'=if(s.host>0){...s,broker:s.host,bp:s.hp,status:"Pending"} else s
 action receipt(request:int,protocol:int,status:str):bool=s'=if(s.broker==request and s.bp==protocol and s.status=="Pending" and Set("Committed","Refused","Unknown").contains(status)){...s,status:status} else s
 action reconnect=s'=s
 val uncertain=s.host>0 and not(s.host==s.broker and s.hp==s.bp and Set("Committed","Refused").contains(s.status))
 action step=any{admit(1),admit(2),submit,receipt(s.broker,s.bp,"Committed"),receipt(s.broker,s.bp,"Unknown"),receipt(s.broker,3-s.bp,"Committed"),receipt(s.broker+1,s.bp,"Committed"),reconnect}
 val safety=Set(1,2).contains(s.hp) and Set(1,2).contains(s.bp) and s.host<s.next and s.broker<s.next and (not(uncertain) and s.host>0 implies s.host==s.broker and s.hp==s.bp and Set("Committed","Refused").contains(s.status))
 run geometryUnreadTest=init.then(admit(2)).then(reconnect).then(all{assert(uncertain and s.broker==0),s'=s})
 run legacyCommitTest=init.then(admit(1)).then(submit).then(receipt(1,1,"Committed")).then(all{assert(not(uncertain)),s'=s})
 run geometryCommitTest=init.then(admit(2)).then(submit).then(receipt(1,2,"Committed")).then(all{assert(not(uncertain)),s'=s})
 run wrongProtocolTest=init.then(admit(2)).then(submit).then(receipt(1,1,"Committed")).then(all{assert(uncertain and s.status=="Pending"),s'=s})
 run wrongRequestTest=init.then(admit(2)).then(submit).then(receipt(2,2,"Committed")).then(all{assert(uncertain and s.status=="Pending"),s'=s})
 run newerGeometryAdmissionTest=init.then(admit(1)).then(submit).then(receipt(1,1,"Committed")).then(admit(2)).then(all{assert(uncertain and s.host==2 and s.broker==1),s'=s})
 run unknownPersistsTest=init.then(admit(2)).then(submit).then(receipt(1,2,"Unknown")).then(reconnect).then(all{assert(uncertain and s.status=="Unknown" and s.next==2),s'=s})
 run reconnectNoReplayTest=init.then(admit(2)).then(reconnect).then(reconnect).then(all{assert(s.host==1 and s.broker==0 and s.next==2),s'=s})
 run duplicateTerminalTest=init.then(admit(2)).then(submit).then(receipt(1,2,"Committed")).then(receipt(1,2,"Unknown")).then(all{assert(not(uncertain) and s.status=="Committed"),s'=s})
}
