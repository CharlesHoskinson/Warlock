# Native text mutation authority contract

Written after actual V5 negative replay and before V6 source edits. Preserve all V5 sources, baseline editable-probe-v5/report.json and failed native-review2 attempt.

Every native content mutation (deleteText, insertText, replaceText, setText(Value)) requires a valid current item/peer, effective enabled/visible ancestors, a mapped Qt window, current Files modal-owner authority and current editable/readOnly state. A retained EditableText interface acquired before a readOnly transition cannot bypass the new state.

Selection/cursor mutations (setSelection, addSelection, removeSelection, setCursorPosition) require the same lifetime/visibility/enabled/modal authority. Read-only text still supports authorized selection and cursor navigation. Read-only text queries, geometry, boundaries and native interface exposure remain Qt behavior.

Actual Files PathBar TextInput and own prompt input must retain correct positive native editing/selection behavior. A diagnostic actual Qt TextEdit validates the second native class; no claim that Files currently includes a TextEdit. Destroyed peers remain defunct; no raw C++ pointer may be invoked after its QObject/native interface has been destroyed. Model identities/epochs reflect this boundary.

No file-operation/script/spec changes, GUI layout changes or original Files edits. A fresh module URL/binary is required; no loaded V5 module is overwritten. Actual reader native editing evidence remains separate from offscreen native-interface replay.
