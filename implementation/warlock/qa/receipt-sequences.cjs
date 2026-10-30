'use strict';
// Read a root-compiled worker. Capture stdout/stderr and executable hashes externally.
const { Elm } = require(require('path').resolve(process.argv[2]));
const initialSeed = 0x65a7c013;
let state = initialSeed >>> 0;
function next() { state ^= state << 13; state ^= state >>> 17; state ^= state << 5; return state >>> 0; }
const seeds = Array.from({length:200}, () => next());
const failures = [];
let representative = null;
let index = 0;
function failedChecks(result) {
  const out = [];
  function walk(x, path) {
    if (!x || typeof x !== 'object') return;
    for (const [key, value] of Object.entries(x)) {
      const p = path ? path + '.' + key : key;
      if (key === 'checks' && value && typeof value === 'object') {
        for (const [name, ok] of Object.entries(value)) if (ok !== true) out.push(p + '.' + name);
      }
      if (key === 'unchangedCorrelationNoMutation' && value !== true) out.push(p);
      walk(value, p);
    }
  }
  walk(result, '');
  const c = result.case;
  if (!c || !c.checks) out.push('case.checks missing');
  else {
    const top=['readyPendingActuallyEmitsOne','topologyAdmitsNewOutput','newerDifferentIncarnationActuallyPending','disconnectMakesUnknownWithoutEffect','validatedUnknownRecordNormalizesMatchingReservation'];
    if (Object.keys(c.checks).sort().join() !== top.sort().join()) out.push('exact top check set differs');
    if (!c.receipts || Object.keys(c.receipts).sort().join() !== ['Committed','Refused','Unknown'].sort().join()) out.push('exact receipt status set differs');
    else for (const row of Object.values(c.receipts)) if (!row.checks || Object.keys(row.checks).sort().join() !== ['sameExactStatusAndOwnership','disconnectedExactStatusAndOwnership','lateExactStatusAndOwnership','newTransactionAndOtherRecordsPreserved','terminalDuplicateNoop'].sort().join()) out.push('exact receipt check set differs');
    if (!c.foreign || Object.keys(c.foreign).sort().join() !== ['binding','request','generation','incarnation','operation','lifetime','epoch','output','revision','protocol','malformed'].sort().join()) out.push('exact foreign check set differs');
    else for (const row of Object.values(c.foreign)) if (row.unchangedCorrelationNoMutation !== true) out.push('foreign assertion missing or failed');
  }
  return out;
}
function run() {
  if (index === seeds.length) {
    process.stdout.write(JSON.stringify({initialSeed, algorithm:'xorshift32', cases:seeds.length, checksPerCase:31, representative,
      scope:'fixed production route per case with varied valid foreign counter and receipt-case ordering', failures},null,2)+'\n');
    process.exitCode = failures.length ? 1 : 0;
    return;
  }
  const seed = seeds[index];
  const app = Elm.ReceiptOutputLifecycleReplay.init({flags:seed});
  const timeout = setTimeout(() => {
    failures.push({index, seed, checks:["worker output deadline"], fullResult:null});
    process.stdout.write(JSON.stringify({initialSeed, algorithm:"xorshift32", sequencesCompleted:index, failures},null,2)+"\n");
    process.exit(1);
  }, 3000);
  app.ports.outgoing.subscribe(result => {
    clearTimeout(timeout);
    const checks = failedChecks(result);
    if (!representative && !checks.length) representative = {index,seed,fullResult:result};
    if (checks.length) failures.push({index, seed, checks, fullResult:result});
    index++;
    setTimeout(run,0);
  });
}
run();
