# Private Qt WindowModal V7 layout readiness fixture

Offline only; no native launch. Preserve accepted Qt203 and V4–V6 failed packets unchanged. Host V4, private AQ4ed46, production v18 and the read-only native diagnostic module are unchanged.

V6 failed before opening a dialog: saved Qt client773x942 was stale while the actual native surface was460x300. Fitting the saved button bounds yielded x110, outside the real button starting x111. Actual Qt/native diagnostics showed ordinary owner press/release. All eighteen main preservation and normal cleanup gates passed. The failed baseline remains retained.

V7 refreshes Qt state after Resize, Move and LayoutRequest, records actual QVBoxLayout geometry, and waits for two matching complete-layout/client/native observations before capturing any button point. At required scale1, client offsets map directly from the actual native surface origin; size mismatch is rejected. The baseline callback and all nineteen routing/family/lifetime oracles remain strict. Ten host gates and command acknowledgments are counted separately.

No input, layout activation, focus or modal behavior is added to the Qt observer. The read-only native plugin is byte-identical to V6. No Qt modal success or parent-loss success is inferred from offline tests.

Frozen command after review:

```bash
python3 /home/hoskinson/window-integration-qa/qa_run.py -- python3 /home/hoskinson/window-integration-qa/qt-modal-private-v7/run_native.py --attempt /home/hoskinson/window-integration-qa/qt-modal-private-v7/attempt-1
```
