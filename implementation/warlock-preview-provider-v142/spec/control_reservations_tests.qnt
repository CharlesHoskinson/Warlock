module control_reservations_tests {
 import control_reservations.* from "./control_reservations"
 action check(ok:bool):bool=all{assert(ok and safety),s'=s}
 run cleanupReservationPrecedesIssuance=init.then(fire(ReserveA)).then(check(s.ar==2 and s.issued==0)).then(fire(IssueA1)).then(check(s.ar==1 and s.issued==1))
 run fullReservedCapacityRefusesSpeculation=init.then(fire(ReserveA)).then(fire(ReserveB)).then(fire(ReleaseB)).then(fire(ReserveB)).then(check(s.ar+s.br==4)).then(fire(CapacityProbe)).then(check(s.last==0 and s.groups==3)).then(fire(IssueA1)).then(check(s.ar+s.br==3 and tickets(s)==1))
 run reservedOrdinalTailProtectsCleanup=init.then(fire(Boundary)).then(fire(ReserveA)).then(fire(ReserveB)).then(check(s.last==0 and s.a>0 and s.b==0)).then(fire(IssueA1)).then(fire(IssueA2)).then(check(s.issued==maximum-1 and s.ar==0))
 run sameSlotRetryKeepsOriginalOrdinal=init.then(fire(ReserveA)).then(fire(IssueA1)).then(fire(IssueA1)).then(check(s.lastOrdinal==1 and s.issued==1 and s.ar==1))
 run changedSlotCannotReissue=init.then(fire(ReserveA)).then(fire(IssueA1)).then(fire(ChangedA1)).then(check(s.last== -1 and s.issued==1 and s.ar==1))
 run unconfirmedTicketKeepsReservation=init.then(fire(ReserveA)).then(fire(IssueA1)).then(fire(ReleaseA)).then(check(s.last==0 and s.a>0 and s.ar==1))
 run confirmedReleaseNeverResetsIssuer=init.then(fire(ReserveA)).then(fire(IssueA1)).then(fire(Deliver)).then(fire(ReleaseA)).then(check(s.a==0 and s.issued==1 and s.groups==1)).then(fire(ReserveA)).then(fire(IssueA1)).then(check(s.issued==2 and s.groups==2))
 run oldReservationCannotResurrect=init.then(fire(ReserveA)).then(fire(IssueA1)).then(fire(Deliver)).then(fire(ReleaseA)).then(fire(OldA1)).then(check(s.last== -1 and s.issued==1 and s.a==0))
 run foreignGrantCannotReserve=init.then(fire(ForeignReserve)).then(check(s.last== -1 and s.groups==0 and s.issued==0))
 run unusedQuotaRollsBackBeforePhysicalAdmission=init.then(fire(ReserveA)).then(fire(ReleaseA)).then(check(s.a==0 and s.ar==0 and s.issued==0 and s.groups==1))
 run singleIssuerOwnsOriginalNamespace=init.then(fire(SecondIssuer)).then(check(s.last== -1 and s.groups==0 and s.issued==0))
}
