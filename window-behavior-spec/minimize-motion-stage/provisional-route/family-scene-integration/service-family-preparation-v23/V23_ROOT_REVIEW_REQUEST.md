# V23 reserved staging source review

Fresh source only, derived from immutable V22. Root alone freezes and owns native integration. The sole inherited source change is `batch_preview.py`; all 133 other copied V22 source/doc files retain exact bytes and modes, including NativeDesktop, SceneController, helpers, current-receipt/family guards, hidden cache, pixel validation, and original 2 s / 1 s deadlines.

The new staging reservation retains the exact epoch while PNG material opens, reads, validation, hashing and descriptor closure run outside the lifecycle lock. A short exact-object commit publishes it; an ordinary failed material scan unwinds only its own reservation after closing the descriptor. A replaced reservation quarantines the owned epoch and preserves the replacement. Exact live staging epochs refuse release/disposal, any live staging refuses batch launch, and pending plus staging capacity is bounded by 64. Unrelated completed epochs remain releasable during the scan. This proves the represented lock boundary, without claiming all filesystem calls or OS scheduling are latency bounded.

Formal-before-runtime: the retained 14 named proof and the subsequent 16 named + 2,000 × 100 refinement both ran with runtime unchanged. The two added cases explicitly model a replaced registry binding and refuse disposal; the root-reviewed runtime patch stayed identical. See `STAGING_SOURCE_PLAN-v2.json` and the exact intended diff.

Actual focused CPU/kernel: nine new tests use real PNG FDs, gated pread, real NativeDesktop cleanup and failed-capture wrapper, actual shared receipt lock, a real owned Keeper, combined 64 capacity, changed material identity, replaced reservation quarantine, unknown lifecycle, and close-before-release outside lifecycle. The external old V22 counterexample remains retained; the fresh corrected replay proves unrelated cleanup and new receipt complete before PNG read release while own staging deletion refuses. All fixture processes and threads close normally.

Final full proof is external at QA/family-preparation-v23-full-proof-v1/report.json: required 359 Python tests, 296 named Quint cases, 32 models × 2,000 × 100, 97 commands, all original gates/deadlines retained. Collector checks complete sources/modes and the frozen V22 closure with exact links, inherited source conservation, reviewed patch/model, full logs and retained failure epochs. It preserves the original Toolkit V5/V21 and ordinary producer V10 pairing.

Commands (from this stage):

```
/usr/bin/python3 freeze_staging_preparation.py --collect
/usr/bin/python3 freeze_staging_preparation.py --freeze
/usr/bin/python3 freeze_staging_preparation.py --verify
```

The source-ready packet is immutable after collection; root must review before freeze. Original native collector 38 baseline gates, 34 fault gates, native performance, full parity, live actor cancellation and deployment remain unaccepted. No V18/V21/actor cancellation/performance source merge is implied.
