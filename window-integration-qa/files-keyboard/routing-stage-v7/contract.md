# Focused file keyboard routing and action payload contract

Written after actual V6 reader/offscreen counterexample and before fresh product edits. Preserve frozen V6 and failed native-review3 attempt.

Plain Up/Down/Home/End/Page and grid Left/Right events on a focused file peer use the existing Explorer command handler, preserving existing selection/range semantics. Focus, cur and selected file path must agree after plain navigation. Shift navigation extends the existing range. Merely focusing another retained visible peer through accessibility does not rewrite existing selection authority; its own accessible Press remains bound to its path.

F2/context actions use the existing selection and captured prompt payload. After plain keyboard navigation selects a file, F2 must capture that same file, not an earlier selection. No file-operation changes. Filter/path/prompt text editing precedence and modal focus traps remain intact. Tab keeps native roving navigation.

List/grid native ListView handling must not intercept file commands ahead of the existing handler. Forward focused list rows/grid cells/containers into existing keyTarget rather than replacing command semantics. Existing keyboard/focus model gains explicit selected path tracking and action payload assertions before product patch; previous model/evidence remains immutable.

Corrected private reader observation calls exact public Atspi.Text.get_text(obj,start,end), separate from action dispatch. The original terminal title-difference gate remains a recorded failure; no title reset/reclassification.

Raw Qt attached gallery toggleAction requires the same valid/enabled/effective-visible/mapped/modal authority as Press. Actual retained-current-peer baseline changes selected path while hidden, disabled and modal background; first probe lost its peer after callback and therefore did not test refusal. Keep both reports and their lifetime classification. Valid visible Toggle preserves existing Ctrl-click selection semantics.

Preservation compares every captured stable compositor field strictly, including mapped/hidden/visible/input/fullscreen/xdg/content metadata. Current application-owned title hashes are observed separately (Codex terminal animated spinner), with raw private snapshots retained. The prior strict-title failure remains immutable; titles are never reset.
