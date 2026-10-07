module native_policy_driver_tests {
 import native_policy_driver.* from "./native_policy_driver"
 action check(ok:bool):bool=all{assert(ok and safety),s'=s}
 run inputCustodyRunsNoPolicy=init.then(fire(Queue)).then(check(s.inputs==1 and not(s.proposal) and s.issued==0))
 run fullInputQueueRefuses=init.then(fire(Fill)).then(fire(Queue)).then(check(s.inputs==1065 and s.code==27))
 run quarantineBypassesInputPressure=init.then(fire(Proposal)).then(fire(Fill)).then(fire(Quarantine)).then(check(s.quarantined and s.inputs==1065 and s.obligation and s.proposal))
 run ticketRetainedBeforeNotification=init.then(fire(Proposal)).then(fire(Issue)).then(check(s.posted and s.proposal and s.issued==1 and s.notified==0 and s.delivered==0))
 run dispatchCannotPrecedeIssuedFact=init.then(fire(Proposal)).then(fire(Issue)).then(fire(Dispatch)).then(check(s.code==1 and s.posted and s.delivered==0))
 run notificationPerformsNoEffect=init.then(fire(Proposal)).then(fire(Issue)).then(fire(Notify)).then(check(not(s.proposal) and s.posted and s.obligation and s.delivered==0))
 run receiptDoesNotConfirmOrSettle=init.then(fire(Proposal)).then(fire(Issue)).then(fire(Notify)).then(fire(Dispatch)).then(check(s.delivered==1 and s.confirmed==0 and s.obligation))
 run confirmationCannotSettleJob=init.then(fire(Proposal)).then(fire(Issue)).then(fire(Notify)).then(fire(Dispatch)).then(fire(Confirm)).then(check(s.confirmed==1 and s.obligation))
 run duplicateDispatchCannotInvoke=init.then(fire(Proposal)).then(fire(Issue)).then(fire(Notify)).then(fire(Dispatch)).then(fire(Dispatch)).then(check(s.code==1 and s.delivered==1 and s.obligation))
 run foreignSourceCannotEnterCustody=init.then(fire(Queue)).then(fire(Foreign)).then(fire(WrongEpoch)).then(fire(Malformed)).then(check(s.inputs==1 and s.issued==0))
 run unknownCannotReset=init.then(fire(Proposal)).then(fire(Issue)).then(fire(Unknown)).then(fire(Notify)).then(fire(Close)).then(check(s.uncertain and not(s.closed) and s.posted and s.proposal))
 run custodyPreventsClose=init.then(fire(Queue)).then(fire(Close)).then(check(not(s.closed) and s.inputs==1 and s.code==1))
 run originalTerminalRequiredForClose=init.then(fire(Proposal)).then(fire(Issue)).then(fire(Notify)).then(fire(Dispatch)).then(fire(Confirm)).then(fire(Close)).then(check(not(s.closed) and s.obligation))
 run settledRealmCloses=init.then(fire(Proposal)).then(fire(Issue)).then(fire(Notify)).then(fire(Dispatch)).then(fire(Confirm)).then(fire(Terminal)).then(fire(Close)).then(check(s.closed and not(s.obligation)))
}
