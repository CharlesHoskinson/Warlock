# Credential and cleanup classification review

Initial mutable review found a final-ordering blocker: classification reread descriptors under the private runtime after inherited teardown removes that runtime. The preserved mutable capture occurred after descriptorCapture began landing; it is not an exact unsafe predecessor. A historical-record witness failed its old DTO precondition and is retained as a review harness failure. A successor must retain exact pinned descriptor bytes outside runtime and verify them against original journal path/hash; the final proof must be tested after actual runtime removal.

The intended policy preserves real/effective/saved/filesystem UID distinctions and same-real-UID/kernel-waitid ownership. Privileged credentials qualify wait accounting only. Both original and fresh credential tuples must be unprivileged to signal, through an opened pidfd and fresh PID/start correlation.

Expected-unavailable is restricted to the captured installed systemd1 descriptor/binfalse, single primary exit1 with no signals or cancellation. GVfs normal exit15 requires exact captured producer and actual same-PID/start SIGTERM recorded before exit, original cancelled=true and no fallback/error. Neither classification asserts normal service operation. All other nonzero or unauthenticated outcomes refuse.

Final readiness requires held source, actual credential/identity controls and post-runtime classification controls. No GUI is performed; full GTK gates remain open.

Final held276 fixes descriptor lifetime using private output captures whose bytes/hash/full DTO remain tied to original journal descriptor path. The actual late private-bus test removes runtime before final classification. Actual kernel credential and pidfd controls refuse privilege/wrong-start and signal only exact owned unprivileged processes. Expected-unavailable is exercised with real installed binfalse; GVfs15 edge controls remain synthetic and are not fresh daemon acceptance. No final source blocker was found for the diagnostic launch; full GTK native gates remain open.
