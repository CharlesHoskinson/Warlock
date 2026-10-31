// Development-only ELM-UI-007 production Surface.packet regression.
// Usage: node feedback-context.cjs COMPILED_ELM.js REPORT.json
// Raw rows and every named failed assertion are retained before nonzero exit.
const fs = require('node:fs');
const vm = require('node:vm');
const {isDeepStrictEqual} = require('node:util');
const [file, output] = process.argv.slice(2);
if (!file || !output) throw new Error('Expected compiled Elm path and report path');
const report = {
  schema: 1, seed: 20261031, generatedCases: 96, passed: false,
  scope: 'Actual Desktop SearchQuery/stale input and Surface.packet projection; typed receipts are fixtures',
  nativeAcceptance: false, releaseAccepted: false, checks: [], failures: [], rows: []
};
let completed = false;
function save() {fs.writeFileSync(output, JSON.stringify(report, null, 2) + '\n');}
function check(name, condition, detail) {
  const result = {name, passed: Boolean(condition)};
  if (!condition) result.detail = detail;
  report.checks.push(result);
  if (!condition) report.failures.push(result);
}
const timer = setTimeout(() => {
  if (!completed) {
    report.error = 'No outgoing fixture rows within three seconds';
    save();
    process.exitCode = 2;
  }
}, 3000);
try {
  const sandbox = {console, setTimeout, clearTimeout};
  vm.createContext(sandbox);
  vm.runInContext(fs.readFileSync(file, 'utf8'), sandbox, {timeout: 1500});
  const app = sandbox.Elm.FeedbackContextReplay.init();
  app.ports.outgoing.subscribe(rows => {
    completed = true;
    clearTimeout(timer);
    report.rows = JSON.parse(JSON.stringify(rows));
    check('Fixture emits the nonempty exact fixed/generated/lifecycle case budget', Array.isArray(rows) && rows.length === 160, {count: rows?.length});
    check('Bounded seeded variants executed', rows.filter(row => row.generated).length === 96);
    const kinds = new Set();
    for (const row of report.rows) {
      const prefix = row.name + ': ';
      kinds.add(row.status);
      check(prefix + 'decoded current fixture preconditions are reachable', row.setupReady && row.frameDecodes);
      check(prefix + 'actual query update is admitted with current idle pointer ownership', row.queryEdited);
      check(prefix + 'publication projects the selected Applications or closed surface', row.frame.mode === (row.open ? 'applications' : 'closed'), row.frame.mode);
      check(prefix + 'SearchQuery emits no effect', row.queryEffects === 0, row.queryEffects);
      check(prefix + 'stale prior query cannot alter context or emit an effect', row.staleQuery === row.expectedQuery && row.staleEffectsCount === 0, {query: row.staleQuery, effects: row.staleEffectsCount});
      check(prefix + 'query and stale input preserve exact window effect custody', isDeepStrictEqual(row.effectsBeforeQuery, row.effectsAfterQuery) && isDeepStrictEqual(row.effectsAfterQuery, row.effectsAfterStale));
      check(prefix + 'query and stale input preserve every unresolved intent/status/protocol', isDeepStrictEqual(row.unresolvedBeforeQuery, row.unresolvedAfterQuery) && isDeepStrictEqual(row.unresolvedAfterQuery, row.unresolvedAfterStale));
      check(prefix + 'repeated projection is stable without new dispatch', isDeepStrictEqual(row.frame, row.repeatFrame));
      check(prefix + 'full-width native identities survive projection context', row.intent.generation === '9007199254740993' && row.intent.incarnation === '18446744073709551614', row.intent);
      const expectedUnresolved = row.older || ['Pending', 'Unknown'].includes(row.status) ? 1 : 0;
      check(prefix + 'pending and unknown remain unresolved', row.unresolved === expectedUnresolved, row.unresolved);
      if (row.open) {
        const search = row.frame.popup.find(control => control.id === 'control:search');
        check(prefix + 'search context stays visible in the real packet', search?.label === row.expectedQuery, search);
        check(prefix + 'launcher guidance survives alongside window feedback', row.frame.status.includes(row.expectedGuidance), row.frame.status);
      }
      if (row.feedback !== null) {
        check(prefix + 'correlated window state is exposed', row.frame.status.includes(row.feedback), row.frame.status);
        check(prefix + 'closed-launcher positive control exposes identical action feedback', row.closedFrame.status.includes(row.feedback), row.closedFrame.status);
        if (row.open) check(prefix + 'action feedback precedes launcher guidance for clipped bars', row.frame.status.startsWith(row.feedback), row.frame.status);
      } else {
        check(prefix + 'no false outstanding action state for terminal or absent receipt', row.forbidden.every(text => !row.frame.status.includes(text)), row.frame.status);
        if (row.open) check(prefix + 'terminal/absent receipt leaves launcher guidance exact', row.frame.status === row.expectedGuidance, row.frame.status);
      }
      if (!row.detached && (row.older || ['Pending', 'Unknown', 'Refused'].includes(row.status))) {
        const recovery = row.frame.bar.find(control => control.id === 'bar:recovery-refresh');
        check(prefix + 'read-only recovery remains represented', recovery?.label === 'Refresh window status' && recovery?.detail === 'Observation only', recovery);
        check(prefix + 'pending suppresses duplicate recovery; settled unknown/refusal permits observation', recovery?.enabled === (row.status !== 'Pending'), recovery);
      }
      if (row.detached) {
        check(prefix + 'disconnected recovery offers reconnect instead of observation under a lost binding', row.frame.bar.some(control => control.id === 'bar:reconnect') && !row.frame.bar.some(control => control.id === 'bar:recovery-refresh'));
        check(prefix + 'disconnect retains Unknown and its original identity without replay', row.effectsAfterQuery.transaction?.status === 'Unknown' && row.unresolvedAfterQuery.length === 1);
      }
    }
    check('All current receipt states and no-transaction negative control exercised', ['Pending', 'Refused', 'Unknown', 'Cancelled', 'Committed', 'None'].every(state => kinds.has(state)), [...kinds]);
    report.passed = report.failures.length === 0;
    save();
    console.log(JSON.stringify({passed: report.passed, rows: report.rows.length, checks: report.checks.length, failures: report.failures.length, report: output}));
    process.exitCode = report.passed ? 0 : 1;
  });
} catch (error) {
  clearTimeout(timer);
  report.error = String(error.stack || error);
  save();
  console.error(report.error);
  process.exitCode = 2;
}
