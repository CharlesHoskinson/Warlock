# Check support metadata before source CAS

Use this check before a source replacement that requires `reconcile-support`.

1. Retain the exact participant snapshot, planned source bytes, claim proof and independent review.
2. Put the four evidence files under `.warlock-contributor/evidence/support-custody/`.
3. Set `AGENTBUS_RUN` to the assigned run.
4. Set `AGENTBUS_AGENT` to the actual claim agent.
5. Run `scripts/support_cas_precheck.py` with the exact planned destination paths.
6. Stop if the check refuses the plan.
7. Keep the existing participant lock through the source precheck and CAS.
8. Keep the existing live-claim, hash, snapshot and review checks.
9. Run the installed canonical `reconcile-support` command after CAS.
10. Retain a failed receipt if reconciliation fails.

The utility checks metadata placement and the assigned environment. It does not grant ownership or execution authority.
It does not replace the canonical checker or prove that a later write will succeed.

For sparse evidence staging, use `git add --sparse --` with the reviewed explicit file list when Git requires it.
Verify every staged blob against the reviewed bytes. Keep the sparse-checkout configuration unchanged.
Run the installed staging review before committing. Never include unrelated paths to resolve a staging refusal.
