# Applications window-action feedback

Scope: ELM-UI-007 `restore-pending`, `restore-refused`, `restore-unknown`.
The source correction and component results are verified. The original EARS remains partial for native, keyboard and assistive-technology observations.

## Behavior and authority

[Surface.elm](../../../implementation/warlock/src/Surface.elm) puts existing window feedback before Applications guidance when there is a current Pending, Unknown, Refused or Cancelled transaction, or retained recovery work. The query and launcher guidance remain intact. Older unresolved Unknown with a current Committed or absent transaction uses the existing generic recovery notice; it does not invent a current receipt outcome.

[SurfaceRenderer.elm](../../../implementation/warlock/src/SurfaceRenderer.elm) top-aligns the bounded taskbar status so the leading action state remains visible. The full message stays in its accessible label/title and popup; a narrow bar can clip the tail. The existing keyed controls and announcement authority are unchanged. The pure view change dispatches no action or retry and changes no query, receipt, focus or native authority. Elm owns GUI policy; Haskell owns backend and reviewed native integration.

## Evidence and reproduction

The [compact source-bound report](../../../implementation/warlock/qa/evidence/applications-window-feedback-20261031/report.json) and [independent review](../../warlock-build-loop/v2/applications-feedback-review-20261031.json) preserve:

- Fresh pinned Main, Bar, Popup and production-fixture compilation.
- 160 production-route cases with 2,435 assertions, including 96 seed `20261031` variants: actual query/stale-input admission, exact unresolved custody, retained older Unknown, detached recovery and maximum query length.
- 201 isolated compiled-view browser checks at 320/1440 widths, including 24 actual text-prefix range observations, retained query/focus, no actions and accessibility names. Chrome exited normally. Four Unknown screenshots are retained.
- The initial invalid pointer fixture RED, corrected valid baseline's 176 feedback failures, first candidate's four older-Unknown failures, and a passing 177-check DOM/AX report whose screenshot exposed vertically clipped text. That earlier report did not establish prefix visibility.

Root may execute the durable exact [review packet](../../../implementation/warlock/qa/evidence/applications-window-feedback-20261031/cpu-review.json) while all bound inputs still match:

```sh
python3 -B tools/qa_cpu.py \
  --review implementation/warlock/qa/evidence/applications-window-feedback-20261031/cpu-review.json \
  --sha256 7b332d5a5501bef290451b8157e1611b4f235c434ba988e2f2602f6636cc67e8
```

The CPU equivalent enforces the original scope/core/private-runtime protections and an exact reviewed source/tool closure. Browser checks use a private network/PID namespace with host desktop sockets hidden. Regenerate and independently review the packet after source/tool changes. Native campaigns retain the unchanged native launcher and gates. Follow the [selected-change guide](../how-to/verify-selected-change.md) and [loop contract](../../warlock-build-loop/v2/INSTRUCTIONS.md).

## Original acceptance and documentation scope

These results establish no native GUI, keyboard/AT, audible/braille or release verdict. All original 242 requirements/417 scenarios, literal oracles, deadlines, failed evidence and stopped histories remain preserved. GHC and the replacement Haskell/native runtime are not qualified on this host. See [evidence scope](status-and-evidence.md).

This is the Diátaxis reference destination. The [tutorial](../tutorials/first-contribution.md), verification how-to and [boundary explanation](../explanation/elm-haskell-boundary.md) retain their roles; root owns shared documentation, wiki and ledger integration.
