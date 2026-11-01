'use strict';
// Root-only: node restore-announcement.cjs ABS_REPLAY.js ABS_REPORT.json
// Production-route component evidence, never native or AT speech proof.
const fs = require('node:fs');
const path = require('node:path');
const crypto = require('node:crypto');
if (process.argv.length !== 4 || !path.isAbsolute(process.argv[2]) || !path.isAbsolute(process.argv[3]))
  throw Error('usage: node restore-announcement.cjs ABS_REPLAY.js ABS_REPORT.json');
const [replay, destination] = process.argv.slice(2);
const hash = file => crypto.createHash('sha256').update(fs.readFileSync(file)).digest('hex');
const expected = [
  'ActualRestoreBeginAllocated','PendingAnnounced','RefusedViaActualReceipt',
  'UnknownViaActualReceipt','DuplicateUnknownSilent','UnknownThenRefusedCorrelated',
  'IdenticalTransitionSilent','RepeatedOutcomeSilent',
  'FreshIntentSameTextNewSerial','ForeignSessionReceiptInert','StaleIntentReceiptInert',
  'MismatchedBindingSilent','NoEffectSilent','NonRestoreSilent','OutcomesNoNewMutationOrFocus'
];
const max = (1n << 64n) - 1n;
let state = 20261101n;
const watermarks = [0n, 1n, max - 2n, max - 3n];
// Fixed 64-bit LCG, decimal strings only; all cases have two successors.
for (let i = 0; i < 28; i++) {
  state = (6364136223846793005n * state + 1442695040888963407n) & max;
  watermarks.push(9007199254740993n + state % (max - 9007199254740993n - 1n));
}
const report = {schema:1, passed:false, seed:'20261101', cases:watermarks.length,
  checks:[], failures:[], hashes:{replay:hash(replay),harness:hash(__filename)},
  nativeAcceptance:false, atSpeechAcceptance:false};
const worker = require(replay).Elm.RestoreAnnouncementReplay;
function run(watermark) {
  return new Promise((resolve, reject) => {
    const timeout = setTimeout(() => reject(Error('missing Elm output for watermark ' + watermark)), 5000);
    try {
      const app = worker.init({flags:{watermark}});
      app.ports.outgoing.subscribe(result => { clearTimeout(timeout); resolve(result); });
    } catch (error) { clearTimeout(timeout); reject(error); }
  });
}
(async () => {
  try {
    for (const [index, value] of watermarks.entries()) {
      const watermark = value.toString();
      const result = await run(watermark);
      const checks = result && result.checks && typeof result.checks === 'object' ? result.checks : {};
      for (const name of expected) {
        const passed = checks[name] === true;
        const row = {name, case:index, watermark, passed};
        report.checks.push(row);
        if (!passed) report.failures.push({...row, actual:checks[name]});
      }
      const extras = Object.keys(checks).filter(name => !expected.includes(name));
      if (extras.length) report.failures.push({name:'unexpected fixture checks', case:index, watermark, extras});
      report.scope = result && result.scope;
    }
  } catch (error) { report.failures.push({name:'harness exception', error:String(error.stack || error)}); }
  report.passed = report.failures.length === 0 && report.checks.length === expected.length * watermarks.length;
  fs.writeFileSync(destination, JSON.stringify(report, null, 2) + '\n');
  if (!report.passed) process.exitCode = 1;
})();
