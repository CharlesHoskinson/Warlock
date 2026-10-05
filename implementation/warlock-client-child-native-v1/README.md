# Retained synchronized-state failure

The exact compiled core-surface-revision-v2/source-revisions-v1/AQ155 tuple
passed independent desynchronized child-only pixels and stale-context rejection,
then failed `syncQueuedRetainsAppliedContextAndPixels`. A synchronized child
advanced context and displayed blue before the parent committed. Root commit
counters prove no artificial root commit occurred. All eight processes exited
normally and cleanup passed.

Preserve the failed source, oracles and report. Child-native-v2 corrects actual
owning core state application without changing the fixture or pixel expectation.
Production/native release acceptance remains open.
