module driver_output_gate_tests {
 import driver_output_gate.* from "./driver_output_gate"
 action check(ok:bool):bool=all{assert(ok and safety),s'=s}
 run ticketCustodyPrecedesNotification=init.then(fire(Step)).then(check(s.issued==1 and s.notified==0 and s.effects==0))
 run notificationPrecedesDispatch=init.then(fire(Step)).then(fire(Step)).then(check(s.notified==1 and s.delivered==0 and s.effects==0))
 run reservationRefusesBeforeEffect=init.then(fire(Step)).then(fire(Step)).then(fire(Held)).then(fire(Step)).then(check(s.refused and s.code==27 and s.effects==0 and s.known))
 run quarantineBypassesOutputPressure=init.then(fire(Step)).then(fire(Step)).then(fire(Held)).then(fire(Step)).then(fire(Quarantine)).then(fire(Step)).then(check(not(s.demand) and s.refused and s.effects==0 and s.known))
 run releasedReservationUsesOriginalTicket=init.then(fire(Step)).then(fire(Step)).then(fire(Held)).then(fire(Step)).then(fire(Open)).then(fire(Step)).then(check(s.issued==1 and s.delivered==1 and s.confirmed==0 and s.effects==1))
 run confirmationCannotSettlePhysicalDuty=init.then(fire(Step)).then(fire(Step)).then(fire(Step)).then(fire(Step)).then(check(s.confirmed==1 and s.effects==1 and s.known))
 run repeatedPressureNeverInvokes=init.then(fire(Step)).then(fire(Step)).then(fire(Held)).then(fire(Step)).then(fire(Step)).then(check(s.refused and s.effects==0 and s.issued==1))
 run foreignThreadCannotConsumeHeldTicket=init.then(fire(Step)).then(fire(Step)).then(fire(Held)).then(fire(Foreign)).then(check(s.refused and s.effects==0 and s.delivered==0))
}
