module output_transport_test {
 import output_transport.* from "./output-transport"
 run returnWithoutIncomingEventTest=init.then(create).then(configure).then(acknowledge).then(publish).then(all{assert(returned and safety),s'=s})
 run ackBeforePublicationTest=init.then(create).then(configure).then(all{assert(not(s.ready) and not(s.acked) and safety),s'=s})
 run failedParentCannotPublishTest=init.then(create).then(configure).then(parentLost).then(all{assert(failed and safety),s'=s})
 run legacyQueuedCreationStallsTest=init.then(legacyCreate).then(idle).then(all{assert(s.stage=="queued" and not(s.ready)),s'=s})
}
