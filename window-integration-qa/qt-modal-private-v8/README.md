# Private Qt WindowModal V8 native cursor observation

No native launch. Preserve Qt203 and failed V4–V7 packets unchanged. Host V4, AQ4ed46, production v18, read-only diagnostic module and Qt fixture/source/binary are byte-identical to V7.

V7 passed configured geometry/layout readiness, then timed out before pressing: requested116,400, native115.99999999999999,400, public integer IPC115,400. Official Hyprland cursorpos floors its native cursor. The producer/normalization math reproduces this exact floating value. No modal was opened and normal shutdown/all18 main preservation passed.

V8 changes only the pre-button observation: use the unchanged private probe's finite native floats and existing0.5 logical-pixel per-axis limit. Keep public integer IPC as a separate diagnostic, retain the full native hit/pointer/focus/guard snapshot, and apply no rounding, offset or tolerance increase. All19 toolkit gates and10 host gates remain strict.

Frozen command after review:

```bash
python3 /home/hoskinson/window-integration-qa/qa_run.py -- python3 /home/hoskinson/window-integration-qa/qt-modal-private-v8/run_native.py --attempt /home/hoskinson/window-integration-qa/qt-modal-private-v8/attempt-1
```
