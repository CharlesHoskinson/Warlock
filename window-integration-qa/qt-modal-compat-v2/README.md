# Qt Widgets WindowModal native review

Prepared and compiled offline only. No fixture has launched. The installed app/tooling sources remain unchanged; there is no proposed product patch.

The new case is one genuine QtWidgets QApplication with an owner, independent SAME-PID peer, asynchronous QDialog.open() child, and nested child. Previous GTK peer trials used a separate process. Qt WindowModal permits an independent same-app peer, so this checks toolkit behavior that those trials did not establish.

The native runner correlates public Qt modality/transient parent/callback events with actual native compositor address/stableId/PID/modal/parent metadata. Before each blocked ancestor click it moves focus to its own independent peer, then requires the actual pointer event to route to the deepest modal while leaving the ancestor callback count unchanged. Valid dialog/peer clicks must increment real QPushButton callbacks. It includes one family minimize/restore pair and owner destruction; it repeats no drag/snap/motion matrix. Command acknowledgments are recorded separately from feature gates.

Sources/compiled fixture use only public QtWidgets6.11.2 APIs and compile with -Wall -Wextra -Werror. The runner uses the installed Wayland virtual-pointer fixture, not physical hardware; it needs the captured single untransformed output at origin0,0 whose physical-size/scale yields exact integer logical extents at least1500×900 (current2560×1600/1.6 =1600×1000). This is a scoped native compatibility result; other display geometries and application-modal dialogs are separate questions.

Root must review the frozen packet and grant one exact command before execution:

`python3 /home/hoskinson/window-integration-qa/qt-modal-compat-v2/run_native.py --attempt /home/hoskinson/window-integration-qa/qt-modal-compat-v2/attempt-1`

Reports/output are exclusive0700/0600. Main preservation reuses the accepted complete stable-client projection plus original Files full/public/hidden/PID/instance/start, four catalogs naturally settled for4seconds, dashboard, typed clipboard/primary, original focus/cursor/layers, outputs/plugins/keyboards/a11yflags/socket/ReaderEnabled. App-owned current-title hashes are observations. No original input, reader/flags changes, original Files launch/kill, operations changes, catalog overwrites or global installs.

Review1 remains immutable and was not executed: its scale1 precondition did not fit the current scale1.6 main output. Review2 changes only fixture coordinate derivation and pre-button actual IPC cursor observation. The compiled QtWidgets fixture is byte-identical. See coordinate-provenance.json for the actual helper/protocol/native handler evidence.
