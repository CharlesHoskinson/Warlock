'use strict';
// Read a root-compiled worker. Capture stdout/stderr and executable hashes externally.
const { Elm } = require(require('path').resolve(process.argv[2]));
const initialSeed = 0x65a7c013;
let state = initialSeed >>> 0;
function next() { state ^= state << 13; state ^= state >>> 17; state ^= state << 5; return state >>> 0; }
const seeds = Array.from({length:200}, () => next());
const failures = [];
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
  if (!result.case || !result.case.checks) out.push('case.checks missing');
  return out;
}
function run() {
  if (index === seeds.length) {
    process.stdout.write(JSON.stringify({initialSeed, algorithm:'xorshift32', sequences:seeds.length,
      scope:'fixed production route per sequence with varied valid foreign counter and receipt-case ordering', failures},null,2)+'\n');
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
    if (checks.length) failures.push({index, seed, checks, fullResult:result});
    index++;
    setTimeout(run,0);
  });
}
run();
