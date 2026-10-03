# Latest-context fixture completion evidence

This is a test observation correction, separate from the read-only IPC product
change. The inherited reversed-context test's first two-second wait checks only
`not manager.pending`. Source activation submits `SceneController.prepare` to a
separate metadata worker, then removes pending. This can publish context acceptance
while the latest restore is still unvalidated. The actual retained failure records
receipt2/current restore, metadataStart set, no cleanup completion. Neither empty
pending nor empty frontend context jobs proves metadata/native cleanup completion.

Before changing the fixture, model the distinct phases: reserve, context accepted,
metadata preparation, all three native returns, cleanup acknowledgment, latest
history and current cleared. The fixture must observe under the manager lock that
pending is empty, every current scene is absent and the latest receipt appears in
history with cleanupAck. Preserve its one original two-second first wait, its
original second wait and every original latest operation, endpoint, three commits,
no transport and superseded-first-receipt assertion. This creates no product
authority, durability exemption, timing change or successful native claim.

A CPU counterexample uses the unchanged manager/frontend/controller with fresh
family metadata held at a real worker event: pending empties while current remains.
The corrected predicate stays false. Releasing metadata must satisfy the complete
predicate and all original assertions. Older completion, partial native returns or
cleanup without the current receipt cannot count as latest completion.
