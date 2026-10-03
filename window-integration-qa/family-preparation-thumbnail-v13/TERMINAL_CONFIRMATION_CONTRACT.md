# Terminal archive confirmation after refusal

The V7 native baseline retained the primary ledger rejection but confirmation raised UnboundLocalError because `packet` was assigned only after ledger validation. Frozen V7 and its actual failure are retained.

Fresh V8 will change only terminal post-disk source acquisition and explicit raw-error refusal. Each confirmation acquires its own reviewed source packet; no local variable from successful pre-disk execution supplies that packet. Confirmation retains independent source, owner, ledger, module and actor callback observations. A prior terminal validation error is permanent: fresh observations cannot grant acceptance. The original query predicate, callback identity, retained ownership and all normal-close requirements remain exact. Missing or changed source and failed confirmation remain failures.

CPU tests must use actual Unix query peers, RuntimeLease, JournalStore and persisted evidence. They cover a genuine refused query, a complete-query positive control, packet acquisition failure before disk, and packet replacement after disk. Synthetic kernel test replies establish harness behavior only, never native window acceptance. Original actual binding tests run alongside these additions. No GUI/native grant is conferred by this stage.

Implementation mapping: `archive_final` confirmation obtains `packet=source_packet()` in its own try; after terminal batch observation, explicit `if raw['errors']` rejects before comparison to the possibly missing pre-disk witness. Existing raw errors and persistence order are retained.
