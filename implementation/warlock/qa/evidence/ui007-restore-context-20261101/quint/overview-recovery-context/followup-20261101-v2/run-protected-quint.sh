#!/usr/bin/env bash
set -euo pipefail
out=implementation/warlock/qa/evidence/ui007-restore-context-20261101/quint/overview-recovery-context/followup-20261101-v2
model=implementation/warlock/qa/overview-recovery-context.qnt
tests=implementation/warlock/qa/overview-recovery-context_test.qnt
witnesses='issueRestoreReached exactUnknownReached exactRefusalReached differentUnknownReached removeWorkspaceReached reopenReached repeatedOpenReached freshReadAfterRefusalReached unknownWorkspaceWitness vanishedWorkspaceFallbackWitness oldOriginReturnedAfterMismatch'
invariants='noReplayOnUnknownReopen selectedWorkspaceExists focusMatchesSelection returnRequiresExactRefusal'
quint --version 2>&1 | tee "$out/quint-version.txt"
quint typecheck "$model" 2>&1 | tee "$out/model-typecheck.txt"
quint typecheck "$tests" 2>&1 | tee "$out/test-typecheck.txt"
quint test "$tests" --seed=52012 2>&1 | tee "$out/tests.txt"
quint run "$model" --invariants $invariants --max-samples=5000 --max-steps=8 --seed=52012 --witnesses $witnesses --verbosity=1 2>&1 | tee "$out/sample-seed-52012-a.txt"
quint run "$model" --invariants $invariants --max-samples=5000 --max-steps=8 --seed=0x5acec --witnesses $witnesses --verbosity=1 2>&1 | tee "$out/sample-suggested-seed-0x5acec.txt"
quint run "$model" --invariants $invariants --max-samples=5000 --max-steps=8 --seed=52012 --witnesses $witnesses --verbosity=1 2>&1 | tee "$out/sample-seed-52012-b.txt"
