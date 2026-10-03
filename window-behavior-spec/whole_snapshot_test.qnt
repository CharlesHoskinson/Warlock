module whole_snapshot_test {
  import whole_snapshot.* from "./whole_snapshot"

  run decoratedMinimizeRestoreTest = init.then(fire(Capture)).then(fire(Hide))
    .then(all { assert(s.visual and s.header and allProps), fire(Restore) })
    .then(all { assert(s.visual and not(s.hidden) and allProps), fire(Prune) })

  run clippedDecorationPreservesClientTest = init.then(fire(ClipDecoration))
    .then(fire(Hide))
    .then(all { assert(s.visual and s.snapshotRect == 55 and s.nativeRect == 42 and allProps), fire(Restore) })

  run failedCaptureHasNoPartialVisualTest = init.then(fire(Capture))
    .then(fire(FailedCapture)).then(fire(Hide))
    .then(all { assert(not(s.visual) and not(s.header) and allProps), fire(Restore) })

  run reusedIdentityRejectsOldPixelsTest = init.then(fire(Capture)).then(fire(Close))
    .then(fire(Reuse)).then(fire(OldCapture)).then(fire(Hide))
    .then(all { assert(s.id == 2 and s.pid == 101 and not(s.visual) and allProps), fire(Prune) })

  run pruneRetainsMinimizedPreviewTest = init.then(fire(Capture)).then(fire(Hide))
    .then(fire(Prune))
    .then(all { assert(s.hidden and s.whole and s.header and allProps), fire(Restore) })

  run pruneRemovesClosedPreviewTest = init.then(fire(Capture)).then(fire(Close))
    .then(fire(Prune))
    .then(all { assert(s.cacheId == 0 and s.cachePid == 0 and not(s.visual) and allProps), fire(Reuse) })
}
