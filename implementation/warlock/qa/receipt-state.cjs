'use strict';

// Independent original ELM-ARC-007 oracle over the compiled owning Elm route.
// The fixture supplies simulated bridge frames, never native issuer evidence.
const fs = require('node:fs');
const vm = require('node:vm');
const path = require('node:path');
const crypto = require('node:crypto');
const {isDeepStrictEqual: equal} = require('node:util');
const [compiledFile, reportFile] = process.argv.slice(2);
if (!compiledFile || !reportFile) throw new Error('Expected COMPILED_ELM.js REPORT.json');
const originalScenarios = ['architecture-007', 'receipt-pending', 'receipt-committed', 'receipt-refused', 'receipt-cancelled'];
const statuses = ['Pending', 'Unknown', 'Committed', 'Refused', 'Cancelled'];
const negativeNames = ['remote-Pending', 'unknown-status', 'binding-lifetime', 'binding-session', 'binding-frontend', 'request', 'generation', 'incarnation', 'operation', 'lifetime', 'epoch', 'output', 'revision', 'protocol', 'unexpected-field', 'numeric-request', 'numeric-output', 'overlong-reason'];
const report = {
  schema: 1, requirement: 'ELM-ARC-007', scenarios: originalScenarios,
  scope: 'Actual OutputController/SurfaceController/Desktop/TaskbarShell/MenuBridge/ReceiptRouter/Shell/Effects route, explicit simulated bridge frames; no native execution or authenticated native issuer claim',
  verification: 'Matching request state is distinct for Pending, Committed, Refused, Cancelled and Unknown; another retained request is unchanged; loss of unproven final effect produces Unknown, never Committed; no replay on reads',
  passed: false, nativeAcceptance: false, haskellPortAcceptance: false, releaseAccepted: false,
  checks: [], failures: [], traces: [], scenarioReceipts: [], artifactHashes: {},
  seededTesting: {initialSeed: 20261031, algorithm: 'xorshift32, unsigned shift1, nonzero; eight distinct fixture offsets modulo17 selected before outcomes', seeds: [], candidates: [], scope: 'Actual production-route sequences with varied full-width authority inputs, not exhaustive state exploration'}
};
const hash = bytes => crypto.createHash('sha256').update(bytes).digest('hex');
const save = () => fs.writeFileSync(reportFile, JSON.stringify(report, null, 2) + '\n');
function check(name, passed, witness) {
  const row = {name, passed: Boolean(passed)};
  if (!passed) row.witness = witness === undefined ? null : witness;
  report.checks.push(row);
  if (!passed) report.failures.push(row);
}
function exact(value, keys) { return value && typeof value === 'object' && !Array.isArray(value) && equal(Object.keys(value).sort(), [...keys].sort()); }
function counter(value) {
  if (typeof value !== 'string' || !/^[1-9][0-9]{0,19}$/.test(value) || BigInt(value) > 18446744073709551615n) throw new Error('Noncanonical positive UInt64 ' + JSON.stringify(value));
  return BigInt(value);
}
function successor(value) { const result = counter(value) + 1n; if (result > 18446744073709551615n) throw new Error('Positive fixture exhausted'); return String(result); }
const tx = (wire, status) => ({intent: wire.intent, status, effectProtocol: wire.effectProtocol});
const issued = wire => ({binding: wire.binding, protocol: wire.effectProtocol, intent: wire.intent});
const windows = row => Array.isArray(row) ? row.filter(wire => wire.kind === 'window-effect') : [];
function identity(wire) {
  const intent = wire.intent;
  return [intent.request, intent.context.lifetime, intent.context.epoch, intent.generation, intent.incarnation, intent.context.output, intent.context.revision];
}
function recordFor(state, wire) { return state.unresolved.filter(row => equal(row.intent, wire.intent) && row.effectProtocol === wire.effectProtocol); }
function authorityState(state) {
  // These are actual custody facts. Rendered refusal diagnostics are separate.
  const {request, generation, transaction, unresolved, issued: sent, observed, connected, binding, phase, menu} = state;
  return {request, generation, transaction, unresolved, issued: sent, observed, connected, binding, phase, menu};
}
function wireOracle(label, wire, before, admitted, target, operation, protocol) {
  check(label + ' emits exact protocol3 window-effect shape', exact(wire, ['protocolVersion', 'kind', 'effectProtocol', 'binding', 'intent']) && wire.protocolVersion === 3 && wire.kind === 'window-effect' && wire.effectProtocol === protocol, wire);
  const observation = protocol === 2 ? admitted.freshGeometry : admitted.freshProjection;
  const expectedContext = protocol === 2
    ? {lifetime: observation.binding.lifetime, epoch: observation.binding.frontend, output: observation.outputGeneration, revision: observation.revision}
    : admitted.freshProjection.context;
  const expected = {request: successor(before.request), generation: successor(before.generation), incarnation: target, operation, context: expectedContext};
  check(label + ' independent raw-input authority and preallocation counters match wire', equal(wire.intent, expected) && equal(wire.binding, admitted.attached.binding), {wire, expected, admitted});
  check(label + ' full seven authority fields are distinct canonical strings above 2^53', identity(wire).every(value => counter(value) > 9007199254740991n) && new Set(identity(wire)).size === 7, identity(wire));
  check(label + ' selected target is present in raw action projection', admitted.initialProjection.scene.windows.some(window => window.incarnation === target), {target, scene: admitted.initialProjection.scene});
}
function unchanged(label, before, after, emitted) {
  check(label + ' preserves exact authority custody', equal(authorityState(after), authorityState(before)), {before, after});
  check(label + ' emits no window-effect mutation', windows(emitted).length === 0, emitted);
}
function outcome(label, row, expectedStatus, a, b) {
  check(label + ' starts from the actual two-request Pending/Unknown custody', equal(row.before.transaction, tx(a, 'Pending')) && equal(recordFor(row.before, a), [tx(a, 'Pending')]) && equal(recordFor(row.before, b), [tx(b, 'Unknown')]), row.before);
  check(label + ' exact full native receipt is correlated to A', row.input.protocolVersion === 3 && row.input.kind === 'effect-outcome' && row.input.status === expectedStatus && equal(row.input.intent, a.intent) && equal(row.input.binding, a.binding) && row.input.effectProtocol === a.effectProtocol && row.simulatedBridge === true, row.input);
  check(label + ' only A receives requested state', equal(row.after.transaction, tx(a, expectedStatus)), {expected: tx(a, expectedStatus), actual: row.after.transaction});
  const remains = expectedStatus === 'Unknown' ? [tx(a, 'Unknown'), tx(b, 'Unknown')] : [tx(b, 'Unknown')];
  check(label + ' full unresolved ownership is exact', equal(row.after.unresolved, remains), row.after.unresolved);
  const retainedIssued = expectedStatus === 'Unknown' ? row.before.issued : row.before.issued.filter(entry => !equal(entry, issued(a)));
  check(label + ' issued authority retires only terminal A', equal(row.after.issued, retainedIssued), row.after.issued);
  check(label + ' other request B remains exactly Unknown', equal(recordFor(row.after, b), recordFor(row.before, b)), {before: recordFor(row.before, b), after: recordFor(row.after, b)});
  check(label + ' receipt preserves counters and observed scene', row.after.request === row.before.request && row.after.generation === row.before.generation && equal(row.after.observed, row.before.observed), {before: row.before, after: row.after});
  check(label + ' receipt emits no new mutation', windows(row.emitted).length === 0, row.emitted);
  const expectedMenu = {Committed: 'Committed', Refused: 'Refusal', Cancelled: 'Cancellation', Unknown: 'Uncertain'}[expectedStatus];
  const last = row.after.menu.lastOutcome;
  check(label + ' actual menu/router has exact distinct outcome ' + expectedMenu, last && Number.isInteger(last.identity) && last.identity > 0 && last.outcome === expectedMenu && row.after.menu.outstanding === (expectedStatus === 'Unknown' ? 1 : 0) && row.after.menu.receiptCount === (expectedStatus === 'Unknown' ? 1 : 0), row.after.menu);
}
function inspectPipeline(pipeline, seed) {
  const label = 'seed ' + seed + ' protocol ' + pipeline.protocol + ': ';
  const raw = pipeline.rawInputs;
  check(label + ' real menu provider and post-close selection preparation are reachable', pipeline.providerReady === true && pipeline.selectionPrepared === true, pipeline);
  check(label + ' both requests emit exactly one actual mutation', pipeline.aEmitted.length === 1 && pipeline.bEmitted.length === 1, {a: pipeline.aEmitted, b: pipeline.bEmitted});
  const a = pipeline.aEmitted[0];
  const b = pipeline.bEmitted[0];
  if (!a || !b) throw new Error(label + ' Fixture did not reach both genuine production emissions');
  check(label + ' raw binding/watermarks establish initial authority', equal(raw.binding, raw.attached.binding) && equal(raw.binding, raw.watermarks.binding) && pipeline.initial.request === raw.watermarks.request && pipeline.initial.generation === raw.watermarks.generation, {raw, initial: pipeline.initial});
  wireOracle(label + 'A', a, pipeline.beforeA, raw, pipeline.targetA, pipeline.operation, pipeline.protocol);
  wireOracle(label + 'B', b, pipeline.initial, {...raw, freshProjection: raw.initialProjection}, pipeline.targetB, 'minimize', 1);
  check(label + ' two requests have unique exact request and incarnation identities', a.intent.request !== b.intent.request && a.intent.incarnation !== b.intent.incarnation && a.intent.generation !== b.intent.generation, {a, b});
  check(label + ' fixture does not substitute an expected serializer for actual emitted wire', equal(a.intent, pipeline.aIntent) && equal(b.intent, pipeline.bIntent), {a, b});
  check(label + ' B actually begins Pending', equal(pipeline.bPending.transaction, tx(b, 'Pending')) && equal(pipeline.bPending.unresolved, [tx(b, 'Pending')]), pipeline.bPending);
  check(label + ' exact simulated Unknown B receipt precedes independent A request', equal(raw.bUnknown.intent, b.intent) && raw.bUnknown.status === 'Unknown' && equal(raw.bUnknown.binding, b.binding) && equal(pipeline.bReconciled.transaction, tx(b, 'Unknown')) && equal(pipeline.bReconciled.unresolved, [tx(b, 'Unknown')]) && pipeline.bReconciled.connected && pipeline.bReconciled.phase === 'Ready' && pipeline.bReceiptEmitted.length === 0, pipeline.bReconciled);
  check(label + ' A local action retains B while creating A Pending', equal(pipeline.pendingA.transaction, tx(a, 'Pending')) && equal(pipeline.pendingA.unresolved, [tx(a, 'Pending'), tx(b, 'Unknown')]) && equal(pipeline.pendingA.issued, [issued(a), issued(b)]) && pipeline.pendingA.menu.outstanding === 1 && pipeline.pendingA.menu.receiptCount === 1, pipeline.pendingA);
  check(label + ' all five original scenario identifiers appear once', pipeline.scenarios.length === 5 && equal(pipeline.scenarios.map(row => row.scenario).sort(), [...originalScenarios].sort()), pipeline.scenarios);
  const byScenario = new Map(pipeline.scenarios.map(row => [row.scenario, row]));
  const pending = byScenario.get('receipt-pending');
  check(label + ' original Pending is actual local emission before any final outcome', pending.status === 'Pending' && equal(pending.after, pipeline.pendingA) && equal(pending.emitted, pipeline.aEmitted), pending);
  for (const status of ['Committed', 'Refused', 'Cancelled']) outcome(label + status, byScenario.get('receipt-' + status.toLowerCase()), status, a, b);
  outcome(label + 'matching Unknown', pipeline.unknownReceipt, 'Unknown', a, b);
  const drop = byScenario.get('architecture-007');
  check(label + ' original loss scenario uses actual connection loss event with unproven A', drop.input.kind === 'host-disconnected' && equal(drop.before, pipeline.pendingA), drop);
  check(label + ' loss makes A Unknown and preserves exact B Unknown', equal(drop.after.transaction, tx(a, 'Unknown')) && equal(drop.after.unresolved, [tx(a, 'Unknown'), tx(b, 'Unknown')]) && equal(drop.after.issued, drop.before.issued) && !drop.after.connected && drop.after.phase === 'Detached', drop.after);
  check(label + ' loss cannot fabricate success, scene change, counter advance or replay', drop.after.transaction.status !== 'Committed' && equal(drop.after.observed, drop.before.observed) && drop.after.request === drop.before.request && drop.after.generation === drop.before.generation && windows(drop.emitted).length === 0, drop);
  check(label + ' all five receipt states remain distinct', new Set(pipeline.scenarios.map(row => row.after.transaction.status)).size === statuses.length && statuses.every(status => pipeline.scenarios.some(row => row.after.transaction.status === status)), pipeline.scenarios.map(row => row.after.transaction));
  check(label + ' all terminal duplicate controls present', equal(pipeline.duplicates.map(row => row.input.status).sort(), ['Cancelled', 'Committed', 'Refused']), pipeline.duplicates);
  for (const row of pipeline.duplicates) {
    check(label + row.name + ' starts terminal with no outstanding local request', row.before.transaction.status === row.input.status && row.before.menu.outstanding === 0 && row.before.menu.receiptCount === 0 && recordFor(row.before, a).length === 0, row.before);
    unchanged(label + row.name, row.before, row.after, row.emitted);
  }
  check(label + ' old unrelated request terminal controls include Committed and Cancelled', equal(pipeline.late.map(row => row.input.status).sort(), ['Cancelled', 'Committed']), pipeline.late);
  for (const row of pipeline.late) {
    check(label + row.name + ' consumes exact B ownership while preserving entire current A', equal(row.input.intent, b.intent) && equal(row.after.transaction, row.before.transaction) && equal(row.after.unresolved, [tx(a, 'Pending')]) && equal(row.after.issued, [issued(a)]) && equal(row.after.menu, row.before.menu) && equal(row.after.observed, row.before.observed) && row.after.request === row.before.request && row.after.generation === row.before.generation && windows(row.emitted).length === 0, row);
  }
  check(label + ' full tuple/binding/protocol/schema/numeric/reason negative controls present', equal(pipeline.negatives.map(row => row.name).sort(), [...negativeNames].sort()), pipeline.negatives.map(row => row.name));
  for (const row of pipeline.negatives) {
    check(label + row.name + ' starts from same reachable Pending A', equal(row.before, pipeline.pendingA), row.before);
    const valid = byScenario.get('receipt-cancelled').input;
    check(label + row.name + ' is an actual altered receipt', !equal(row.input, valid), {mutated: row.input, valid});
    unchanged(label + row.name, row.before, row.after, row.emitted);
  }
  const recovery = pipeline.recovery;
  check(label + ' recovery starts with actual matching Unknown receipt', equal(recovery.before, pipeline.unknownReceipt.after), recovery.before);
  check(label + ' raw recovery read retains same admitted scene authority', recovery.readInput.kind === 'action-projection' && equal(recovery.readInput.context, raw.initialProjection.context) && equal(recovery.readInput.scene, raw.initialProjection.scene), recovery.readInput);
  check(label + ' bounded recovery answers all actual outstanding read slots', recovery.drainBound === 8 && Array.isArray(recovery.drain) && recovery.drain.length <= 8 && equal(recovery.remainingSlots, {projection: null, geometry: null, attach: null}), recovery);
  for (const [index, step] of recovery.drain.entries()) {
    const slot = step.input.kind === 'action-projection' ? 'projection' : 'geometry';
    check(label + ' recovery read ' + index + ' matches actual pending observation ID', ['action-projection', 'geometry-facts'].includes(step.input.kind) && step.input.requestId === step.slotsBefore[slot] && equal(step.input.binding, raw.binding), step);
    check(label + ' recovery read ' + index + ' preserves exact request custody without replay', equal(step.after.transaction, step.before.transaction) && equal(step.after.unresolved, step.before.unresolved) && equal(step.after.issued, step.before.issued) && equal(step.after.menu, step.before.menu) && step.after.request === step.before.request && step.after.generation === step.before.generation && windows(step.emitted).length === 0, step);
  }
  check(label + ' read reconciliation keeps exact Unknown reservations and issued authority', equal(recovery.after.transaction, tx(a, 'Unknown')) && equal(recovery.after.unresolved, recovery.before.unresolved) && equal(recovery.after.issued, recovery.before.issued) && recovery.after.request === recovery.before.request && recovery.after.generation === recovery.before.generation && recovery.after.phase === 'Ready' && recovery.after.connected && windows(recovery.readEmitted).length === 0, recovery);
  unchanged(label + 'same-target action after read cannot replay Unknown', recovery.after, recovery.retryAfter, recovery.retryEmitted);
  for (const scenario of originalScenarios) {
    const row = byScenario.get(scenario);
    report.scenarioReceipts.push({requirement: report.requirement, scenario, seed, protocol: pipeline.protocol, operation: pipeline.operation, request: a.intent.request, otherRequest: b.intent.request, outcome: row.after.transaction.status, traceHash: hash(JSON.stringify(row)), simulatedBridge: true, nativeExecution: false});
  }
}
async function main() {
  const bytes = fs.readFileSync(compiledFile);
  report.artifactHashes[path.resolve(compiledFile)] = hash(bytes);
  report.artifactHashes[path.resolve(__filename)] = hash(fs.readFileSync(__filename));
  const elmFixture = path.join(__dirname, 'ReceiptStateReplay.elm');
  report.artifactHashes[elmFixture] = hash(fs.readFileSync(elmFixture));
  const sandbox = {console, setTimeout, clearTimeout};
  vm.createContext(sandbox);
  vm.runInContext(bytes.toString('utf8'), sandbox, {timeout: 2000});
  let generator = 20261031 >>> 0;
  const offsets = new Set();
  while (report.seededTesting.seeds.length < 8) {
    const candidate = report.seededTesting.candidates.length === 0 ? generator : (generator >>> 1) || 1;
    report.seededTesting.candidates.push(candidate);
    if (!offsets.has(candidate % 17)) { offsets.add(candidate % 17); report.seededTesting.seeds.push(candidate); }
    generator ^= generator << 13; generator ^= generator >>> 17; generator ^= generator << 5; generator >>>= 0;
  }
  save();
  for (const seed of report.seededTesting.seeds) {
    try {
      const trace = await new Promise((resolve, reject) => {
        const timer = setTimeout(() => reject(new Error('Compiled worker did not emit seed ' + seed)), 3000);
        const app = sandbox.Elm.ReceiptStateReplay.init({flags: seed});
        let emitted = false;
        app.ports.outgoing.subscribe(value => {
          if (emitted) { check('seed ' + seed + ' emits once', false); save(); return; }
          emitted = true; clearTimeout(timer); resolve(JSON.parse(JSON.stringify(value)));
        });
      });
      report.traces.push({seed, trace});
      // Retain all raw production-route traces before any assertion can throw.
      save();
      check('seed ' + seed + ' exact requirement/schema/seed', trace.schema === 1 && trace.requirement === report.requirement && trace.seed === seed, trace);
      check('seed ' + seed + ' both protocol pipelines present', equal(trace.pipelines.map(row => row.protocol), [1, 2]), trace.pipelines);
      for (const pipeline of trace.pipelines) {
        try { inspectPipeline(pipeline, seed); }
        catch (error) { check('seed ' + seed + ' protocol ' + pipeline.protocol + ' independent prerequisite', false, String(error.stack || error)); }
      }
    } catch (error) { check('seed ' + seed + ' compiled fixture invocation', false, String(error.stack || error)); }
    save();
  }
  check('all eight actual route traces retained', report.traces.length === 8, report.traces.length);
  const identities = report.traces.flatMap(row => row.trace.pipelines.map(pipeline => pipeline.aEmitted[0]?.intent?.request));
  check('seed variants genuinely vary full-width request inputs', identities.length === 16 && new Set(identities).size === 8, identities);
  check('all original scenarios have both-protocol receipts for every seed', report.scenarioReceipts.length === 80 && originalScenarios.every(scenario => report.scenarioReceipts.filter(row => row.scenario === scenario).length === 16), report.scenarioReceipts);
  report.passed = report.failures.length === 0;
  save();
  console.log(JSON.stringify({passed: report.passed, checks: report.checks.length, failures: report.failures.length, traces: report.traces.length, scenarioReceipts: report.scenarioReceipts.length, report: reportFile}));
  process.exitCode = report.passed ? 0 : 1;
}
main().catch(error => { report.error = String(error.stack || error); save(); console.error(report.error); process.exitCode = 2; });
