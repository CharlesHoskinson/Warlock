module data_provenance_lifecycle_test {
 import data_provenance_lifecycle.* from "./data_provenance_lifecycle"
 run stableAcceptedTest=init.then(capture(true)).then(commit).then(all{assert(accepted and allProps),commit})
 run consumerReplacedBeforeCommitTest=init.then(capture(true)).then(replace("consumer")).then(commit).then(all{assert(not(accepted) and allProps),commit})
 run producerReplacedBeforeCommitTest=init.then(capture(true)).then(replace("producer")).then(commit).then(all{assert(not(accepted) and allProps),commit})
 run fdReplacedBeforeCommitTest=init.then(capture(true)).then(replace("fd")).then(commit).then(all{assert(not(accepted) and allProps),commit})
 run vmaChangedBeforeCommitTest=init.then(capture(true)).then(replace("vma")).then(commit).then(all{assert(not(accepted) and allProps),commit})
 run peerChangedBeforeCommitTest=init.then(capture(true)).then(replace("peer")).then(commit).then(all{assert(not(accepted) and allProps),commit})
 run acceptedConsumerInvalidationTest=init.then(capture(true)).then(commit).then(replace("consumer")).then(all{assert(not(accepted) and allProps),commit})
 run acceptedProducerInvalidationTest=init.then(capture(true)).then(commit).then(replace("producer")).then(all{assert(not(accepted) and allProps),commit})
 run acceptedFdInvalidationTest=init.then(capture(true)).then(commit).then(replace("fd")).then(all{assert(not(accepted) and allProps),commit})
 run acceptedVmaInvalidationTest=init.then(capture(true)).then(commit).then(replace("vma")).then(all{assert(not(accepted) and allProps),commit})
 run recaptureFreshIdentityTest=init.then(capture(true)).then(replace("fd")).then(capture(true)).then(commit).then(all{assert(accepted and allProps),commit})
 run invalidEvidenceRefusedTest=init.then(capture(false)).then(commit).then(all{assert(not(accepted) and allProps),commit})
}
