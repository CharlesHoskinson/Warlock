module closure_alias_identity_test {
 import closure_alias_identity.* from "./closure_alias_identity"
 action check(v:bool):bool=all{assert(v),s'=s}
 run originalRegularAcceptedTest=init.then(observe(regular)).then(check(s.accepted))
 run exactSelectedAliasAcceptedTest=init.then(observe(alias)).then(check(s.accepted))
 run inheritedExactAliasAcceptedTest=init.then(observe({...alias,declared:Absent,priorLink:A})).then(check(s.accepted))
 run byteLinkOverlapSameExactIdentityAcceptedTest=init.then(observe({...alias,priorHash:A,priorLink:A})).then(check(s.accepted))
 run unknownAliasMatchingBytesRefusedTest=init.then(observe({...alias,declared:Absent})).then(check(s.refused))
 run sameBytesWrongNamedTargetRefusedTest=init.then(observe({...alias,named:B})).then(check(s.refused))
 run conflictingPriorTargetRefusedTest=init.then(observe({...alias,priorLink:B})).then(check(s.refused))
 run conflictingPriorDigestRefusedTest=init.then(observe({...alias,priorHash:B})).then(check(s.refused))
 run conflictingPriorModeRefusedTest=init.then(observe({...alias,priorHash:A,priorMode:M644})).then(check(s.refused))
 run wrongTargetModeRefusedTest=init.then(observe({...alias,mode:M644})).then(check(s.refused))
 run targetNotRegularRefusedTest=init.then(observe({...alias,resolvedRegular:false})).then(check(s.refused))
 run missingTargetRefusedTest=init.then(observe({...alias,named:Absent})).then(check(s.refused))
 run unknownKindRefusedTest=init.then(observe({...alias,kind:Unknown})).then(check(s.refused))
 run regularOverwritesPinnedLinkRefusedTest=init.then(observe({...regular,priorLink:A})).then(check(s.refused))
 run laterGoodCannotEraseRefusalTest=init.then(observe({...alias,named:B})).then(observe(alias)).then(check(s.refused and not(s.accepted)))
 run resolvedBackingUncapturedRefusedTest=init.then(observe({...alias,resolvedCaptured:false})).then(check(s.refused))
 run selectedLinkMismatchBeforeBytesRefusedTest=init.then(observe({...alias,linksBefore:false})).then(check(s.refused))
 run selectedLinkMismatchAfterBytesRefusedTest=init.then(observe({...alias,linksAfter:false})).then(check(s.refused))
}
