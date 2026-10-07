module visual_channel_tests {
 import visual_channel.* from "./visual_channel"
 action check(ok:bool):bool=all{assert(ok and safety),s'=s}
 run detachedHasNoVisualAuthority=init.then(fire(Offer)).then(check(s.code==3 and s.sequence==0))
 run attachCannotReplaceContext=init.then(fire(Attach)).then(fire(Attach)).then(check(s.code==1 and s.lease==1))
 run deliveryDoesNotAccept=init.then(fire(Attach)).then(fire(Offer)).then(fire(Current)).then(check(s.code==4 and not(s.accepted)))
 run exactReceiptAcceptsCurrent=init.then(fire(Attach)).then(fire(Offer)).then(fire(Ack)).then(fire(Current)).then(check(s.code==0 and s.accepted))
 run retryRetainsVisualSequence=init.then(fire(Attach)).then(fire(Offer)).then(fire(Retry)).then(fire(Retry)).then(check(s.code==0 and s.sequence==1 and not(s.accepted)))
 run changedPolicyRefusesReceipt=init.then(fire(Attach)).then(fire(Offer)).then(fire(Change)).then(fire(Ack)).then(check(s.code==4 and s.pending==-1 and not(s.accepted)))
 run changedPolicyRefusesRetry=init.then(fire(Attach)).then(fire(Offer)).then(fire(Change)).then(fire(Retry)).then(check(s.code==4 and s.pending==-1))
 run changedAcceptedPolicyLosesCurrency=init.then(fire(Attach)).then(fire(Offer)).then(fire(Ack)).then(fire(Change)).then(fire(Current)).then(check(s.code==4 and not(s.accepted)))
 run invalidationCannotRetainAcceptance=init.then(fire(Attach)).then(fire(Offer)).then(fire(Ack)).then(fire(Invalidate)).then(fire(Current)).then(check(s.code==4 and s.pending==-1))
 run replacementKeepsSequenceFloor=init.then(fire(Attach)).then(fire(Offer)).then(fire(Detach)).then(fire(Attach)).then(fire(Offer)).then(check(s.lease==2 and s.sequence==2 and not(s.accepted)))
 run foreignContextCannotInvalidate=init.then(fire(Attach)).then(fire(Offer)).then(fire(Ack)).then(fire(ForeignContext)).then(fire(Current)).then(check(s.code==0 and s.accepted))
 run foreignThreadCannotDestroy=init.then(fire(Attach)).then(fire(ForeignThread)).then(check(s.code==2 and s.held and s.attached))
 run attachedContextPreventsDestroy=init.then(fire(Attach)).then(fire(Destroy)).then(check(s.code==1 and s.held))
 run detachedChannelClosesNormally=init.then(fire(Attach)).then(fire(Offer)).then(fire(Detach)).then(fire(Destroy)).then(fire(Offer)).then(check(s.code==1 and not(s.held)))
}
