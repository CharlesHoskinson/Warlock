# Isolated client capture — failed owning compile preserved

The owning205 compile correctly rejects a call to the protected renderWindow
method. Actual 2,000 geometry controls and sealed-FD/PNG controls passed in
the corrected CPU harness; its subsequent Quint typecheck failed on a missing
action return annotation. Both failures and the first missing-GIO fixture
compile remain intact. No native loading or capture acceptance occurred.
Fresh v3 uses the public surface-pass API and fixes only the model annotation.
