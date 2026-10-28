module release_inventory_test {
  import release_inventory.* from "./release-inventory"
  run acceptanceTest = init.then(review).expect(st.decision == 1)
  run unaccountedTest = init.then(addPayload(2)).then(review).expect(st.decision == 2)
  run duplicateTest = init.then(addOwner(1, 2)).then(review).expect(st.decision == 2)
  run selfCycleTest = init.then(addEdge(2, 2)).then(review).expect(st.decision == 2)
  run mutualCycleTest = init.then(addEdge(2, 3)).then(addEdge(3, 2)).then(review).expect(st.decision == 2)
  run rootedCycleTest = init.then(addEdge(2, 3)).then(addEdge(3, 2)).then(addEdge(1, 2)).then(review).expect(st.decision == 1)
  run restorationTest = init.then(addPayload(2)).then(review).expect(st.decision == 2).then(addOwner(2, 1)).then(review).expect(st.decision == 1)
  run scanErrorTest = init.then(setScanError(true)).then(review).expect(st.decision == 2).then(setScanError(false)).then(review).expect(st.decision == 1)
  run staleReviewTest = init.then(review).then(addPayload(2)).expect(st.decision == 1 and st.changed and not(exact(st.payload, st.owners)))
  run removalTest = init.then(removePayload(1)).then(review).expect(st.decision == 2).then(removeOwner(1, 1)).then(review).expect(st.decision == 2)
}
