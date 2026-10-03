module readonly_predecessor_test {
 import readonly_predecessor.* from "./readonly_predecessor"
 val witness={owner:2,root:1,source:1,dataset:1,previous:1,file:1,complete:true,chain:true,rowsEqual:true,durable:true}
 action check(p:bool):bool=all{assert(p),s'=s}
 action lease=fire(Acquire({owner:2,root:1,oldTerminal:true}))
 action sealed=lease.then(fire(Seal(witness)))
 action confirmed=sealed.then(fire(Confirm(witness)))
 action publish=fire(PublishNew({owner:2,pointer:1,durable:true}))
 run pendingAndUnpublishedRowsRetainedBeforeNewIssuerTest=init.then(confirmed).then(publish).then(check(s.newPublished and s.diskRetained==Set(1,2,3) and s.oldPending.subseteq(s.diskRetained) and allProps))
 run liveOldServiceCannotAuthorizeNewIssuerTest=init.then(fire(Acquire({owner:2,root:1,oldTerminal:false}))).then(check(s.fault and not(s.lease)))
 run missingActualNewLeaseCannotSealTest=init.then(fire(Seal(witness))).then(check(s.fault and not(s.sealed)))
 run wrongLeaseOwnerCannotSealTest=init.then(lease).then(fire(Seal({...witness,owner:3}))).then(check(s.fault))
 run partialDatasetCannotBeNormalizedTest=init.then(lease).then(fire(Seal({...witness,complete:false}))).then(check(s.fault and s.diskRetained==Set(1,2,3)))
 run pendingRowCannotBeDiscardedBySealTest=init.then(lease).then(fire(Seal({...witness,rowsEqual:false}))).then(check(s.fault and s.oldUnpublished==Set(2)))
 run invalidArchiveChainCannotBeSealedTest=init.then(lease).then(fire(Seal({...witness,chain:false}))).then(check(s.fault))
 run predecessorFileMustBeDurableTest=init.then(lease).then(fire(Seal({...witness,durable:false}))).then(check(s.fault and not(s.sealed)))
 run stillValidDatasetReplacementCannotConfirmTest=init.then(sealed).then(fire(Replace({root:1,source:1,dataset:2,previous:1,file:1}))).then(fire(Confirm({...witness,dataset:2}))).then(check(s.fault and not(s.confirmed)))
 run everyOtherValidIdentityReplacementCannotConfirmTest=init.then(sealed).then(all{nondet selector=Set(1,2,3,4).oneOf();val changed={...witness,root:if(selector==1)2 else 1,source:if(selector==2)2 else 1,previous:if(selector==3)2 else 1,file:if(selector==4)2 else 1};fire(Replace({root:changed.root,source:changed.source,dataset:changed.dataset,previous:changed.previous,file:changed.file})).then(fire(Confirm(changed)))}).then(check(s.fault))
 run unconfirmedSealCannotReplaceOldJournalTest=init.then(sealed).then(publish).then(check(s.fault and not(s.diskNew) and s.diskRetained==Set(1,2,3)))
 run wrongPredecessorPointerCannotPublishTest=init.then(confirmed).then(fire(PublishNew({owner:2,pointer:2,durable:true}))).then(check(s.fault and not(s.diskNew)))
 run failedNewJournalPublicationPreservesOldRowsTest=init.then(confirmed).then(fire(PublishNew({owner:2,pointer:1,durable:false}))).then(check(s.fault and not(s.diskNew) and s.diskRetained==Set(1,2,3)))
 run crashBeforeNewPublicationKeepsFullOldDatasetTest=init.then(sealed).then(fire(Crash)).then(fire(Recover({chain:true,pointer:true,namespace:true}))).then(check(not(s.diskNew) and s.diskRetained==Set(1,2,3) and s.recovered))
 run crashAfterNewPublicationKeepsExactPredecessorTest=init.then(confirmed).then(publish).then(fire(Crash)).then(fire(Recover({chain:true,pointer:true,namespace:true}))).then(check(s.diskNew and s.diskPointer==1 and s.diskRetained==Set(1,2,3) and s.recovered and allProps))
 run everyBadRecoveryWitnessRefusesTest=init.then(confirmed).then(publish).then(fire(Crash)).then(all{nondet selector=Set(1,2,3).oneOf();fire(Recover({chain:selector!=1,pointer:selector!=2,namespace:selector!=3}))}).then(check(s.fault and not(s.recovered)))
 run oldDataNeverSuppliesNewQueryResultTest=init.then(confirmed).then(publish).then(fire(Crash)).then(fire(Recover({chain:true,pointer:true,namespace:true}))).then(fire(UseOld)).then(check(not(s.oldUsable)))
 run refusalCannotBeClearedByGoodLaterSealTest=init.then(lease).then(fire(Seal({...witness,chain:false}))).then(fire(Seal(witness))).then(fire(Confirm(witness))).then(publish).then(check(s.fault and not(s.diskNew)))
}
