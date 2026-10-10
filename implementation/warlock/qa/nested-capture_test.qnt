module nested_capture_test {
 import nested_capture.* from "./nested-capture"
 run twoOccludedRequestsTest = init.then(request(0)).then(request(1)).then(demand(0)).then(demand(1)).then(all {assert(bothCopied and safety),s'=s})
 run retireBeforeDemandTest = init.then(request(0)).then(retire(0)).then(request(1)).then(demand(1)).then(all {assert(retiredNotCopied and not(s.get(0).armed) and safety),s'=s})
 run commitDoesNotPresentTest = init.then(request(0)).then(demand(0)).then(all {assert(notSyntheticPresentation and safety),s'=s})
 run failedBufferCannotCopyTest = init.then(request(0)).then(failed(0)).then(all {assert(s.get(0).copies==0 and not(s.get(0).committed) and safety),s'=s})
 run parentAcknowledgesTest = init.then(request(0)).then(demand(0)).then(parentDone(0)).then(all {assert(s.get(0).presented and not(s.get(0).pending) and safety),s'=s})
}
