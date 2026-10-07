module native_realm_ingress_tests {
 import native_realm_ingress.* from "./native_realm_ingress"
 action check(ok:bool):bool=all{assert(ok and safety),s'=s}
 run currentEnvelopeIssuesNativePurpose=init.then(fire(Valid)).then(check(s.accepted and s.issued==1))
 run exactDuplicateRetainsOriginalOrdinal=init.then(fire(Valid)).then(fire(Valid)).then(check(s.accepted and s.issued==1))
 run foreignEpochConsumesNoOrdinal=init.then(fire(ForeignEpoch)).then(check(not(s.accepted) and s.issued==0))
 run foreignBindingConsumesNoOrdinal=init.then(fire(ForeignBinding)).then(check(not(s.accepted) and s.issued==0))
 run extraHeaderConsumesNoOrdinal=init.then(fire(ExtraHeader)).then(check(not(s.accepted) and s.issued==0))
 run aggregateCannotPartiallyIssue=init.then(fire(MultipleRows)).then(check(not(s.accepted) and s.issued==0))
 run emptyEnvelopeConsumesNoOrdinal=init.then(fire(EmptyRows)).then(check(not(s.accepted) and s.issued==0))
 run malformedCommandConsumesNoOrdinal=init.then(fire(MalformedCommand)).then(check(not(s.accepted) and s.issued==0))
 run numericEpochConsumesNoOrdinal=init.then(fire(NumericEpoch)).then(check(not(s.accepted) and s.issued==0))
 run rendererOrdinalConsumesNoOrdinal=init.then(fire(OrdinalHeader)).then(check(not(s.accepted) and s.issued==0))
 run oversizedIngressConsumesNoOrdinal=init.then(fire(Oversized)).then(check(not(s.accepted) and s.issued==0))
 run refusalPreservesAlreadyIssuedPurpose=init.then(fire(Valid)).then(fire(ForeignEpoch)).then(fire(ForeignBinding)).then(fire(ExtraHeader)).then(check(not(s.accepted) and s.issued==1))
}
