# Retain actual focus observations before applying the original predicate

Frozen A2's actual native campaign passed seven original cases, then the original
owner-to-deepest-modal focus wait expired. Its compositor log records the core
modal-parent refusal. The existing conditional poll returns null on mismatch and
therefore loses the actual native and Seat objects it queried. Preserve that
failure and the complete A2 closure; do not infer the missing raw state.

In a fresh A3 controller, retain the exact native snapshot through the existing
guarded `observe` before querying the Seat snapshot. Retain the exact Seat snapshot
through that same observer before deciding whether the pair satisfies the
original target predicate. Always sample both when the first read succeeds,
including when core focus does not match. A second-reader failure preserves the
first successful raw observation and the second error. Persistence or host guard
failure still refuses. Each successful returned pair must be the same two objects
whose raw data was persisted, rather than a second query after a conditional.

The predicate remains exact public address/stableId/PID matching of both core
native focus and keyboard owner against the explicitly selected target. The
original `wait` and its five-second deadline, setup command, expected deepest
modal, input routes, all six static feature-check calls and fourteen runtime
feature cases remain unchanged. No retry, active-window fallback, longer budget,
or direct target focus replaces the actual requested parent focus.

The model represents observed owner agreement symbolically. It checks observation
ordering, retained negative pairs, retained reader failure, and no acceptance
without both original positive comparisons. It does not model kernel/process,
source/socket/lifetime authority, production focus writes, or actual Qt input.
CPU injected readers exercise this mapping only; native acceptance still requires
the complete root-run campaign with an independently corrected product.

The inherited wait checks its deadline between polls. This observation correction
does not claim a new post-reader wall-clock check or stronger timeout semantics;
the model's Timeout event is only that original between-poll expiry observation.
