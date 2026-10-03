module mapping_evidence_test {
 import mapping_evidence.* from "./mapping_evidence"
 run acceptedRetainedTest=init.then(capture(true,true,true)).then(save).then(validate).then(all{assert(accepted and allProps),validate})
 run missingClosureRetainedTest=init.then(capture(true,true,false)).then(save).then(validate).then(all{assert(not(accepted) and persisted and allProps),validate})
 run unreadableRetainedTest=init.then(capture(false,true,true)).then(save).then(validate).then(all{assert(not(accepted) and persisted and allProps),validate})
 run staleLifetimeRetainedTest=init.then(capture(true,false,true)).then(save).then(validate).then(all{assert(not(accepted) and persisted and allProps),validate})
 run allErrorsRetainedTest=init.then(capture(false,false,false)).then(save).then(validate).then(all{assert(not(accepted) and persisted and allProps),validate})
 run noValidationBeforeSaveTest=init.then(capture(true,true,true)).then(all{assert(not(checked) and not(accepted) and not(persisted) and allProps),save})
}
