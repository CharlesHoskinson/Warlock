module bootstrap_flush_test {
 import bootstrap_flush.* from "./bootstrap_flush"
 action check(v:bool):bool=all{assert(v),queued'=queued,readable'=readable,serverSawCommit'=serverSawCommit,configure'=configure,clientSawConfigure'=clientSawConfigure}
 run queuedInitialCommitWithoutReadableTrafficDoesNotFlushTest=init.then(create).then(eventOnly).then(eventOnly).then(check(queued and not(serverSawCommit) and not(configure)))
 run explicitInitialFlushLetsParentRespondTest=init.then(create).then(flush).then(eventOnly).then(check(serverSawCommit and clientSawConfigure))
 run incidentalParentTrafficCanMaskMissingFlushTest=init.then(create).then(incidental).then(eventOnly).then(check(serverSawCommit and configure))
}
