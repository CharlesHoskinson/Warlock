# Qt Widgets window-modal compatibility contract

This is a new toolkit contract check, separate from the accepted GTK modal/caption and Qt Quick motion/Files evidence. The existing GTK modal fixture's independent peer is a separate process. The Qt fixture must prove a same-application independent top-level window remains interactive while a WindowModal child blocks its own hierarchy.

Qt6.11.2 defines WindowModal as blocking the associated parent hierarchy and ApplicationModal as blocking all application windows. The standard QDialog.open() API creates an asynchronous window-modal dialog; the fixture uses that public path without an extra event loop. [Qt6.11.2 WindowModality](https://doc.qt.io/qt-6.11/qt.html#WindowModality-enum), [QDialog.open](https://doc.qt.io/qt-6.11/qdialog.html#open).

## Bounded native gates

1. One disposable public QtWidgets QApplication creates independent owner and peer top-level windows. Capture exact native address/stableId/PID plus Qt object names; require native Wayland. The compiled public Qt version is6.11.2.
2. Open a genuine child QDialog through QDialog.open(). Qt reports WindowModal and transientParent owner; native compositor family metadata must independently report matching parent stable identity and modal flag.
3. Native virtual-pointer clicks on the independent SAME-PID peer invoke its real QPushButton callback and focus that peer. Owner client/caption input must not invoke the owner callback; it must route focus to its modal child. The dialog's own real button remains usable.
4. Open a child of that dialog. Both Qt and native parent chains must agree. Owner and intermediate-dialog clicks cannot invoke their callbacks and redirect to the deepest modal; the deepest button receives its own native click.
5. Close deepest dialog through the fixture control channel, retaining normal Qt destruction. The surviving modal receives its own real native click and remains the parent focus target. Close the surviving dialog; owner button becomes actionable again.
6. Reopen child and exercise only one bounded installed-helper family minimize/restore pair with exact captured identities. Both owner/child hide and return together; same-application peer remains separate and deepest modal remains actionable. This checks the toolkit family integration; existing drag/snap/animation paths are not repeated.
7. Destroy the owner while its modal exists. Owned dialog destruction and compositor family metadata removal must complete; the independent peer remains usable. Stop the exact fixture process normally and verify all owned identities are gone.

The program writes actual Qt input/click/visibility/activation/dialog-lifetime observations and command acknowledgments to a private output directory. The Python native runner must correlate actual Qt events with compositor native identities, without claiming success from an IPC acknowledgement alone. Virtual pointer/keyboard inputs are not physical hardware evidence.

## Preservation and authorization

No native launch until root reviews a frozen runner/dependency manifest and grants the exclusive GUI slot. No product patch or settings change is proposed by this fixture. Never send original applications input, mutate original Files667402, alter operations/scripts/spec, overwrite user catalogs, or change accessibility flags/reader state. Reuse the accepted full main preservation projection, raw private snapshots, all four catalog natural4second settling, full hidden Files/UI/PID/start, typed clipboard/primary hashes, layers/outputs/plugins/keyboards/socket/ReaderEnabled.

Cleanup releases held virtual input, terminates only captured owned process groups/PIDs with start guards, retains all evidence, restores original focus/cursor through exact captured identities and verifies complete main preservation. A failed native parent-modal observation is retained as a toolkit compatibility gap; the fixture must not publish synthetic native modal metadata or modify the product to satisfy its own expectations.
