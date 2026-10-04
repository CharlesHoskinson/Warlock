module recovery {
 type State={host:Set[int],visible:Set[int],entries:Set[int],settled:Set[int],seen:Set[int],watermark:int,submissions:int,owner:bool,mutex:bool,oldProducer:bool,poisoned:bool,initialized:bool,ledgerPresent:bool}
 var s:State
 action init=s'={host:Set(),visible:Set(),entries:Set(),settled:Set(),seen:Set(),watermark:0,submissions:0,owner:true,mutex:false,oldProducer:false,poisoned:false,initialized:false,ledgerPresent:true}
 action hostAdmit(k:int):bool=s'=if(not(s.poisoned) and not(s.mutex) and s.host.size()<2 and not(s.seen.contains(k))){...s,host:s.host.union(Set(k)),visible:s.visible.union(Set(k)),seen:s.seen.union(Set(k))} else s
 action importUnread=s'=if(not(s.poisoned) and not(s.mutex) and not(s.oldProducer) and (s.ledgerPresent or not(s.initialized))){...s,entries:s.entries.union(s.visible.exclude(s.settled)),watermark:s.watermark.max(s.visible.size()),initialized:true,ledgerPresent:true} else s
 action begin(k:int):bool=s'=if(not(s.poisoned) and not(s.mutex) and not(s.oldProducer) and s.ledgerPresent and s.visible.contains(k) and not(s.entries.contains(k)) and not(s.settled.contains(k)) and s.entries.size()<2){...s,entries:s.entries.union(Set(k)),watermark:s.watermark+1,submissions:s.submissions+1,initialized:true} else s
 action settle(k:int):bool=s'=if(not(s.poisoned) and s.ledgerPresent and s.entries.contains(k)){...s,entries:s.entries.exclude(Set(k)),settled:s.settled.union(Set(k))} else s
 action unlinkVisible(k:int):bool=s'=if(not(s.poisoned) and s.settled.contains(k)){...s,visible:s.visible.exclude(Set(k))} else s
 action syncDirectory=s'=if(not(s.poisoned)){...s,host:s.visible,settled:s.settled.intersect(s.visible)} else s
 action cold=s'={...s,visible:s.host}
 action fault=s'={...s,poisoned:true}
 action missingLedger=s'={...s,ledgerPresent:false}
 action oldOwner=s'={...s,oldProducer:true}
 action lock=s'={...s,mutex:true}
 action unlock=s'={...s,mutex:false}
 action step=any{hostAdmit(1),hostAdmit(2),hostAdmit(3),begin(1),begin(2),importUnread,settle(1),settle(2),unlinkVisible(1),unlinkVisible(2),syncDirectory,cold,fault,missingLedger,oldOwner,lock,unlock}
 val safety=s.host.size()<=2 and s.visible.size()<=2 and s.entries.size()<=2 and s.settled.size()<=2 and s.entries.intersect(s.settled)==Set() and s.submissions<=s.watermark
 run liveOwnerAllowsImportTest=init.then(hostAdmit(1)).then(importUnread).then(all{assert(s.owner and s.entries==Set(1) and s.submissions==0),s'=s})
 run unreadNeverReplaysTest=init.then(hostAdmit(1)).then(importUnread).then(begin(1)).then(cold).then(importUnread).then(all{assert(s.entries==Set(1) and s.submissions==0),s'=s})
 run lostReceiptDoesNotResurrectTest=init.then(hostAdmit(1)).then(begin(1)).then(settle(1)).then(cold).then(importUnread).then(all{assert(s.entries==Set() and s.settled==Set(1)),s'=s})
 run earlierUnknownSurvivesLaterCommitTest=init.then(hostAdmit(1)).then(importUnread).then(hostAdmit(2)).then(begin(2)).then(settle(2)).then(cold).then(importUnread).then(all{assert(s.entries==Set(1) and s.settled==Set(2)),s'=s})
 run exactRetirementTest=init.then(hostAdmit(1)).then(importUnread).then(hostAdmit(2)).then(begin(2)).then(settle(2)).then(unlinkVisible(2)).then(syncDirectory).then(cold).then(importUnread).then(all{assert(s.host==Set(1) and s.entries==Set(1) and s.settled==Set()),s'=s})
 run unknownCannotRetireTest=init.then(hostAdmit(1)).then(importUnread).then(unlinkVisible(1)).then(all{assert(s.visible==Set(1)),s'=s})
 run failedUnlinkSyncKeepsTombstoneTest=init.then(hostAdmit(1)).then(begin(1)).then(settle(1)).then(unlinkVisible(1)).then(fault).then(syncDirectory).then(cold).then(all{assert(s.host==Set(1) and s.visible==Set(1) and s.settled==Set(1)),s'=s})
 run capacityNeverEvictsTest=init.then(hostAdmit(1)).then(hostAdmit(2)).then(hostAdmit(3)).then(importUnread).then(all{assert(s.host==Set(1,2) and s.entries==Set(1,2)),s'=s})
 run oldProducerBlocksImportTest=init.then(hostAdmit(1)).then(oldOwner).then(importUnread).then(all{assert(s.entries==Set() and not(s.initialized)),s'=s})
 run mutexBlocksUntilReleaseTest=init.then(hostAdmit(1)).then(lock).then(importUnread).then(unlock).then(importUnread).then(all{assert(s.entries==Set(1) and s.owner),s'=s})
 run missingInitializedLedgerRefusesTest=init.then(hostAdmit(1)).then(importUnread).then(missingLedger).then(importUnread).then(all{assert(not(s.ledgerPresent) and s.entries==Set(1)),s'=s})
 run unprovenIntentNeverSubmitsTest=init.then(begin(1)).then(all{assert(s.submissions==0 and s.entries==Set()),s'=s})
}
