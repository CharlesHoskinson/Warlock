module query_delivery_test {
  import query_delivery.* from "./query-delivery"
  run queryBeforeAckTest = init.then(edit(3,1,1))
    .then(check(s.root==0 and s.pending==3))
    .then(acknowledge(1,1)).then(check(s.root==3 and s.pending== -1))
  run latestQueryWinsTest = init.then(edit(2,1,1)).then(edit(4,1,1))
    .then(acknowledge(1,1)).then(check(s.root==4 and safety))
  run stalePublicationDoesNotReplayTest = init.then(edit(2,1,1)).then(present)
    .then(acknowledge(1,1)).then(acknowledge(2,1))
    .then(check(s.root==0 and s.pending== -1 and safety))
  run currentQueryAfterRefreshTest = init.then(edit(2,1,1)).then(present)
    .then(edit(4,2,1)).then(acknowledge(2,1))
    .then(check(s.root==4 and s.lastDeliveredPub==2 and safety))
  run retiredLeaseDoesNotReplayTest = init.then(edit(3,1,1)).then(reopen)
    .then(edit(4,2,1)).then(acknowledge(1,1)).then(acknowledge(2,2))
    .then(check(s.root==0 and s.pending== -1 and safety))
  run queryAfterAckTest = init.then(acknowledge(1,1)).then(edit(3,1,1))
    .then(check(s.root==3 and s.pending== -1 and safety))
}
