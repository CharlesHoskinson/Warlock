# Size-correct buffer selection

This fresh core derivative changes only `CMonitorState::ensureBufferPresent`.
A reusable pending buffer must match both the selected mode's pixel dimensions
and the required dmabuf format. Otherwise the existing swapchain selection and
rollback path supplies a replacement. Output mode and custom mode remain
mutually exclusive through Aquamarine's setters; selection uses the same
precedence as the owning core's `updateSwapchain`.

The build replaces exactly `Monitor.cpp.o` in the frozen v23 archive. It preserves
the original archive, binary, source and owning headers. Every ordered archive
member payload except that one object is compared byte-for-byte by SHA-256,
including repeated basenames. All 701 compile dependencies are recorded.
Source, candidate headers, test fixture and build runner are captured as read-only
files under the successful run's `inputs` directory.

Latest protected CPU evidence: `build-1791090562611157328/report.json`. Twelve
checks compile the actual extracted production method with controlled buffer and
swapchain doubles. They cover exact reuse, restored-mode stale dimensions,
one-axis mismatches, format failure, missing buffer, disabled outputs, custom
mode selection and rollback conservation. Removing the dimension guard produces
the preserved expected exit-1 regression; it does not crash the test process.
The full production translation unit compiles and the derived core links.

`build-1791090427112559436` is preserved earlier evidence. Its duplicate-name
archive comparison was less complete; use the latest ordered-payload proof.

This does not prove real GBM allocation, buffer presentation, parent fullscreen
geometry compatibility, native resize recovery, or plugin/core tuple acceptance.
Aquamarine's parent configure and viewport contract is a separate integration.
No installed replacement, GUI campaign or plugin load was performed.
