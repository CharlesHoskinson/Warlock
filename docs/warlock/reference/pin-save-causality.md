# Pin saves and effect-boundary causality

ELM-TEA-003 requires matching committed receipts for dependent native effects,
independent effects in `Cmd.batch`, and typed validation before model mutation.
Its original verification permits compiler checks, deterministic replay and
independent boundary fixtures; native behavior is qualified separately.

The actual Elm Applications route now retains a pending pin reorder when an
earlier catalog read arrives. Pin controls stay disabled until the matching
write outcome or deliberate recovery is admitted. A matching Saved receipt
adopts the proposed order. The change describes verified Elm policy and surface
packets, with no native GUI or storage-durability verdict.

## Follow the causal case

Start with confirmed pins `[A,B]`. Refresh emits read R. Before its response,
the current published control permits moving B left and emits write W. The
backend can legitimately respond to R before W because R was issued first.
That old observation must not retire W, re-enable another write, or hide its
later matching Saved receipt. The owning-route fixture performs these actions
through `SurfaceSnapshot`, `OutputController`, `SurfaceController` and `Desktop`.

The initially suspected W-before-R response ordering was rejected after tracing
the existing FIFO backend. A separate ordered W-before-R control remains in the
fixture. No historical Python backend was changed or accepted as a Haskell port.

## Reproduce the bounded component campaign

Use the repository's pinned compiler/cache and reviewed fixed CPU launcher.
The retained packet is bound to its exact source and host paths:

```sh
python3 -B tools/qa_cpu.py \
  --review implementation/warlock/qa/evidence/tea-effects-20261101/cpu-review.json \
  --sha256 34002d25d2bba0d13d55cb63dd7aa6a578c70f9cab4d3f9fe5eca401ee9ec920
```

Changed inputs require a new reviewed packet under the existing protected QA
workflow. This command is a CPU component campaign. It compiles actual Main,
Bar and Popup and runs pin, preview-paint, authority-tuple and receipt fixtures.
It does not launch a compositor, issue native window effects or deploy the GUI.

## State and receipt contract

`Pins.Model.pending` retains the request and proposed identities, plus an opaque
`Confirmation` value. `Saving` protects the original confirmed base against all
catalog observations, including unavailable, equal and higher revisions.
`Unconfirmed` retains uncertainty and may register a recovery read.

`Desktop.requestApplications` calls `Pins.readStarted` only when it actually
allocates and emits a read. A read already in flight when Unknown arrives gains
no recovery permission. `observeRead` accepts recovery only for the registered
identity; Desktop also checks binding and its current expected request first.
Saved must match the pending request, proposed identities and a strictly newer
revision. Refused retires only that write. A matching invalid Saved proof remains
unconfirmed; duplicates preserve any registered recovery read. Malformed or
foreign inputs remain outside this transition.

A fresh read after uncertainty observes current storage for a possible new user
intent. It does not claim that the old write committed or replay its proposal.
For a lower recovery response, Desktop consumes the expected read even though
Pins retains an inert marker. The model's active recovery identity represents
both that marker and the still-current Desktop expectation.

## Evidence and the full original contract

[Retained evidence](../../../implementation/warlock/qa/evidence/tea-effects-20261101/report.json)
contains the syntax/model preparation failures, actual 1,531-check RED with 96
causal failures, and passing candidate. The independent Node oracle is unchanged.
The candidate has 1,563 pin checks because additional real publish/commit effects
produce 32 additional checks; the same eight raw matrices remain required.

The whole campaign passes 7,023 checks, 26 explicitly selected model tests and
two separate 10,000-trace, 50-step samples with seven positive witnesses each.
Its five fixtures cover the following parts of TEA-003:

- Pin causality and current window receipt/authority fixtures exercise dependent
  outcomes. A pin-domain Saved outcome is not relabeled a native Committed frame.
- All four Main/Popup `Cmd.batch` sites are classified by source correspondence;
  fresh paint-gate controls test exact ticket admission, immediate cancellation
  and independent control delivery. No dependent native writes rely on batch order.
- Real typed decoders and independent malformed, numeric, foreign, stale and
  duplicate fixtures precede mutation. Rejected input and permitted uncertainty
  transitions have separate expected models and effect descriptions.

An independent immutable-source review determines the original verdict. Test
counts alone do not accept TEA-003. Native input, presentation, AT/IME, actual
backend persistence and release acceptance retain their separate obligations.
