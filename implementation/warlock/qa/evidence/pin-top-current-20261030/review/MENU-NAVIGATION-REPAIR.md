# Known menu-navigation fixture repair

SOURCE_READY for the bounded v2 repair. This is a demonstrated mismatch between fixture input and existing menu navigation, not a product defect or a new diagnostic investigation. Preserve the failed v1 run, source, counter/timer history and stopped keyboard-only Menu/New instance routes. No reviewer QA or public edits occurred.

Actual v1 report native-pin-independence-1793326042992469752/report.json SHA2562588f14a815d72fc6f6316887ac529fa1f0050df4dc022e0f83fbf9f00715f1e is failed overall. Its165 named checks pass, followed by an unlabelled focus assertion in actual saved executed-framework.py:1148. The traceback's old framework source excerpts are misleading because the composed code used the historical filename; the saved executed source identifies the real statement. The failure is in focus_control before Enter at the keyboard Always-on-top action and before AT actions.

Read actual retained warlock-window-feedback-1793326042992601188/warlock.log: publication71/lease7 focus moves Minimize→Open new instance of Peer→Actions for Peer→Close window actions→Minimize, repeats and ends on New instance. Helper74–82 input files each contain physical key15 press/release. No target Enter or AT invocation occurred at this failing step. Current assets/context.js:74–96 explicitly defines Tab as a ring of close, selected operation and utilities, while ArrowDown selects window-operation rows. /usr/include/linux/input-event-codes.h defines KEY_TAB15 and KEY_DOWN108.

Actual v2 branch diff is exactly key(15)→key(108 if mode=='menu' else15). Application navigation retains Tab. Native menu opening remains a physical secondary click; the change concerns selection within the already open menu. All current control, publication/lease, exact native object, geometry, paint, receipt, native identity, independent storage/effect, no-launch, AT and cleanup assertions remain unchanged. No deadline, iteration budget or policy oracle changes. Parser and runtime/frontend tuple are unchanged. Runner changes only its branch pin and compile filename to its actual saved executed-framework.py, improving future traceback attribution.

Reviewed v2 hashes:

* runner.py: dcf78fc3a035778147b977b44db69a9d8c3ab48cd86b558e64deea16a7311447
* branch.txt: 05d72e6b6561c6a04c6c18b83d6815fda3a5f6f4f8020b7f8650e36703f552cf
* popup_join.py: 5a73d1639c0c2350bad922c5017e902e5aa20e9075c6c91cb3af9d1bd6019aa3 (unchanged)

Public wrapper was still v1 at review; its executed bytes must remain preserved and its declared pins switched to these reviewed v2 files before execution. Root confirms executed public v1 bytes are saved. This review authorizes no counter reset and does not itself execute a retry.

The failed run supports only observed partial results: five correlated application Saved intervals and one native pointer pin Committed with independent storage preserved. Seven owned processes exited normally; plugin unload and cleanup passed; /run/user/1000/wqa/f538 is absent. Full bidirectional independence, keyboard target activation and applicable AT observations remain unaccepted. Root separately reports visual inspection of Pin Peer/Always-on-top captures; this reviewer did not infer image acceptance from the CPU report. A repaired run must still meet all original live assertions.
