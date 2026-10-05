# Preserved initial layout campaign failure

Native-v4 passed the cache replay then failed layoutPositionPendingHeld.
The queued position changed context39to40 without a parent commit. However,
its final cache trace had detached the child, so the appended layout test
incorrectly assumed visible blue baseline pixels. All63 owned processes exited
normally and private teardown passed. Preserve this failure; native-v5 explicitly
resets and decodes the visible baseline before the same pending-layout oracle.
No layout/native/full-release acceptance is claimed.
