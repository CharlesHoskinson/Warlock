module actor_attestation_test {
 import actor_attestation.* from "./actor_attestation"
 action check(p:bool):bool=all{assert(p),s'=s}
 action renderer=fire(Register({id:1,actor:1,lifetime:1,source:1,kind:Renderer}))
 action native=fire(Register({id:2,actor:1,lifetime:2,source:2,kind:Native}))
 action attest=fire(Observe).then(fire(Attest({actor:1,authenticated:true,ledgerExact:true})))
 run exactReturnedAndClosedActorMayAttestTest=init.then(renderer).then(native).then(fire(PhysicalGone(1))).then(fire(Complete(1))).then(fire(PhysicalGone(2))).then(fire(Returned({id:2,exact:true,durable:true}))).then(fire(Complete(2))).then(attest).then(check(s.attested and allProps))
 run emptyGroupCannotClearUnknownNativeReturnTest=init.then(native).then(fire(PhysicalGone(2))).then(fire(Complete(2))).then(attest).then(check(not(s.attested)))
 run nonDurableNativeReturnCannotAttestTest=init.then(native).then(fire(PhysicalGone(2))).then(fire(Returned({id:2,exact:true,durable:false}))).then(fire(Complete(2))).then(attest).then(check(not(s.attested)))
 run WrongNativeResultCannotAttestTest=init.then(native).then(fire(PhysicalGone(2))).then(fire(Returned({id:2,exact:false,durable:true}))).then(fire(Complete(2))).then(attest).then(check(not(s.attested)))
 run activeRendererCannotAttestTest=init.then(renderer).then(fire(Complete(1))).then(attest).then(check(not(s.attested)))
 run droppedHistoricalLedgerCannotBecomeEmptyProofTest=init.then(renderer).then(fire(PhysicalGone(1))).then(fire(Complete(1))).then(fire(DropLedger)).then(attest).then(check(not(s.attested)))
 run selfReportedClosureCannotAttestTest=init.then(renderer).then(fire(PhysicalGone(1))).then(fire(Complete(1))).then(fire(Observe)).then(fire(Attest({actor:1,authenticated:false,ledgerExact:true}))).then(check(not(s.attested)))
 run validReplacementIssuerRevokesPartialProofTest=init.then(renderer).then(fire(PhysicalGone(1))).then(fire(Complete(1))).then(fire(Observe)).then(fire(ReplaceIssuer)).then(fire(Attest({actor:1,authenticated:true,ledgerExact:true}))).then(check(not(s.attested)))
 run lateActorJobRevokesPartialProofTest=init.then(renderer).then(fire(PhysicalGone(1))).then(fire(Complete(1))).then(fire(Observe)).then(native).then(fire(Attest({actor:1,authenticated:true,ledgerExact:true}))).then(check(not(s.attested)))
 run otherActorJobDoesNotRequireWholeKeeperStopTest=init.then(renderer).then(fire(Register({id:3,actor:2,lifetime:3,source:3,kind:Helper}))).then(fire(PhysicalGone(1))).then(fire(Complete(1))).then(attest).then(check(s.attested and s.groups.contains(3)))
 run exactActorIdsCannotBorrowOtherClosureTest=init.then(renderer).then(fire(Register({id:3,actor:2,lifetime:3,source:3,kind:Helper}))).then(fire(PhysicalGone(3))).then(fire(Complete(3))).then(attest).then(check(not(s.attested)))
}
