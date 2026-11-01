'use strict';

// ELM-TEA-003 independent pin dependency/decoder oracle. The root runner also
// qualifies the other TEA clauses; this matrix alone never claims whole EARS.
const fs = require('node:fs');
const vm = require('node:vm');
const path = require('node:path');
const crypto = require('node:crypto');
const {isDeepStrictEqual: equal} = require('node:util');
const [compiledFile, reportFile] = process.argv.slice(2);
if (!compiledFile || !reportFile) throw new Error('Expected COMPILED_ELM.js REPORT.json');
const seeds = Array.from({length: 8}, (_, index) => 20261031 + index);
const sha = bytes => crypto.createHash('sha256').update(bytes).digest('hex');
const report = {
  schema: 1, requirement: 'ELM-TEA-003', scenario: 'tea-effects', passed: false,
  scope: 'Actual published SurfaceSnapshot action -> OutputController -> SurfaceController -> Desktop -> Pins route, with explicit simulated bridge inputs',
  verification: 'Independent exact pin models and effect descriptions; preserve pending save through read observations, settle matching Saved, preserve Unknown explicit read recovery and legal backend FIFO controls',
  wholeRequirementAccepted: false, nativeAccepted: false, releaseAccepted: false,
  otherOriginalClauses: 'Root separately qualifies dependent Committed receipts, all owning Cmd.batch independence and typed decoder boundaries; this pin matrix alone is insufficient',
  seeds, generator: 'Eight fixed consecutive seeds chosen before outcomes; fixture varies2-8pin identities and full-width revisions by seed modulo17',
  artifactHashes: {}, traces: [], checks: [], failures: [], scenarioReceipts: []
};
const save = () => fs.writeFileSync(reportFile, JSON.stringify(report, null, 2) + '\n');
function check(name, passed, witness) {
  const row = {name, passed: Boolean(passed)};
  if (!passed) row.witness = witness === undefined ? null : witness;
  report.checks.push(row);
  if (!passed) report.failures.push(row);
}
function uint(value) {
  if (typeof value !== 'string' || !/^[1-9][0-9]{0,19}$/.test(value) || BigInt(value) > 18446744073709551615n) throw new Error('Noncanonical positive UInt64 ' + JSON.stringify(value));
  return BigInt(value);
}
function next(value) { const result = uint(value) + 1n; if (result > 18446744073709551615n) throw new Error('Exhausted positive fixture counter'); return String(result); }
function exact(value, keys) { return value && typeof value === 'object' && !Array.isArray(value) && equal(Object.keys(value).sort(), [...keys].sort()); }
const wires = row => row.effects.filter(effect => effect.kind === 'send' || effect.kind === 'window-send').map(effect => effect.wire);
const writes = row => wires(row).filter(wire => wire.kind === 'taskbar-pins-write');
const focus = row => row.effects.filter(effect => effect.kind === 'focus').map(effect => effect.target);
const custody = pins => ({snapshot: pins.snapshot, pending: pins.pending, writable: pins.writable});
const pinControl = (frame, identity) => frame.popup.find(control => control.id === identity);
function wireOf(label, row, kind) {
  const values = wires(row);
  check(label + ' exact one serialized ' + kind + ' effect', values.length === 1 && values[0].kind === kind, row.effects);
  if (values.length !== 1 || values[0].kind !== kind) throw new Error(label + ' did not reach its actual emitted ' + kind);
  return values[0];
}
function knownEffects(label, row) {
  check(label + ' all actual effect descriptions are retained and known', row.effects.every(effect => ['send', 'window-send', 'publish', 'focus'].includes(effect.kind)), row.effects);
  for (const effect of row.effects.filter(effect => effect.kind === 'publish')) check(label + ' published effect matches current owning frame', equal(effect.frame, row.frameAfter), effect);
  if (row.commit !== null) {
    check(label + ' actual registered commit preserves exact wire order and projection', row.commit.viewProtocol === 1 && row.commit.kind === 'view-commit' && equal(row.commit.requests, wires(row)) && equal(row.commit.projection.frame, row.frameAfter) && equal(row.commit.focus, focus(row)), row.commit);
  }
}
function published(label, row, identity, popup, kind, binding) {
  const envelope = row.input;
  const action = envelope?.action;
  check(label + ' action originates in current actual published enabled control', exact(envelope, ['viewProtocol', 'kind', 'scope', 'action']) && envelope.viewProtocol === 1 && envelope.kind === 'view-action' && equal(envelope.scope, {id: '1', generation: '1'}) && action?.surfaceProtocol === 2 && action.kind === 'surface-action' && action.id === identity && action.surface === (popup ? 'popup' : 'bar') && action.publication === row.frameBefore.publication && action.lease === row.frameBefore.lease && row.frameBefore[popup ? 'popup' : 'bar'].some(control => control.id === identity && control.enabled), {action, frameBefore: row.frameBefore});
  const emitted = wireOf(label, row, kind);
  check(label + ' emitted request uses actual admitted binding and independent next Desktop counter', emitted.protocolVersion === 3 && equal(emitted.binding, binding) && emitted.requestId === next(row.before.request) && row.after.request === emitted.requestId, {emitted, before: row.before, after: row.after});
  knownEffects(label, row);
  return emitted;
}
function noMutation(label, row) {
  check(label + ' emits no pin/native mutation', wires(row).every(wire => !['taskbar-pins-write', 'window-effect', 'application-launch'].includes(wire.kind)), row.effects);
  knownEffects(label, row);
}
function exactUnchanged(label, row) {
  check(label + ' exact complete owning model is unchanged', row.sameDesktop === true && row.sameOutput === true && equal(row.after, row.before) && equal(row.frameAfter, row.frameBefore), row);
  check(label + ' rejected input emits no effect or registered commit', row.effects.length === 0 && row.commit === null, row);
}
function pendingCustody(label, row) {
  check(label + ' preserves exact pending request, proposal, base snapshot and writable gate', equal(custody(row.after.pins), custody(row.before.pins)) && row.after.pins.pending !== null && row.after.pins.writable === false && row.after.request === row.before.request, {before: row.before, after: row.after});
  noMutation(label, row);
}
function matchingSaved(label, row, write, expectedSnapshot) {
  check(label + ' receives exact independent correlated Saved fixture', row.input.protocolVersion === 3 && row.input.kind === 'taskbar-pins-outcome' && row.input.status === 'Saved' && row.input.requestId === write.requestId && equal(row.input.binding, write.binding) && equal(row.input.preferences, expectedSnapshot), row.input);
  const expectedPins = {snapshot: expectedSnapshot, pending: null, notice: 'Pin order saved.', writable: true};
  check(label + ' exact matching Saved adopts confirmed order and retires only pending request', equal(row.after.pins, expectedPins) && row.after.request === row.before.request && row.after.expected === row.before.expected, {expectedPins, before: row.before, after: row.after});
  check(label + ' accepted receipt restores only launcher search focus', equal(focus(row), ['launcher-search']), row.effects);
  noMutation(label, row);
}
function inspect(trace, seed) {
  const label = 'seed ' + seed + ': ';
  check(label + ' original named scenario and schema retained', trace.schema === 1 && trace.requirement === report.requirement && trace.scenario === report.scenario, trace);
  const p = trace.pipeline;
  check(label + ' seed retained before oracle execution', p.seed === seed);
  const raw = p.setup;
  const initialSnapshot = raw.catalog.preferences;
  const initialOrder = initialSnapshot.identities;
  const expectedOrder = [initialOrder[1], initialOrder[0], ...initialOrder.slice(2)];
  const expectedSnapshot = {revision: next(initialSnapshot.revision), identities: expectedOrder};
  const binding = raw.attached.binding;
  check(label + ' full-width positive revision is canonical and unrounded', uint(initialSnapshot.revision) > 9007199254740991n && uint(raw.catalog.snapshot.lifetime) > 9007199254740991n, initialSnapshot);
  check(label + ' independent raw fixture has2-8unique pins and matching catalog identities', initialOrder.length >= 2 && initialOrder.length <= 8 && initialOrder.length === p.pinCount && new Set(initialOrder).size === initialOrder.length && equal(raw.catalog.snapshot.entries.map(entry => entry.id).sort(), [...initialOrder].sort()), raw);
  check(label + ' actual base is reached by native decoders and published Applications opener', raw.topology.viewProtocol === 2 && equal(raw.catalog.binding, binding) && equal(raw.pointer.binding, binding) && raw.pointer.state === 'idle' && raw.openAction.action?.id === 'bar:applications' && raw.openAction.action?.surface === 'bar' && raw.openCommit?.requests.some(wire => wire.kind === 'catalog-request' && wire.requestId === raw.catalog.requestId) && p.initial.open === true && equal(p.initial.binding, binding) && p.initialFrame.mode === 'applications' && p.initial.popupOwner !== null && equal(p.initial.pins, {snapshot: initialSnapshot, pending: null, notice: '', writable: true}) && equal(p.initial.applications, [...initialOrder].sort()), {raw, initial: p.initial, frame: p.initialFrame});
  check(label + ' MovePin target comes from independent second identity', p.moveId === 'pin-left:' + initialOrder[1]);
  const rw = p.readThenWrite;
  const r = published(label + 'Refresh R', rw.refresh, 'control:refresh', true, 'catalog-request', binding);
  check(label + ' Refresh changes only catalog authority, retaining writable pins during loading', rw.refresh.after.applications === null && rw.refresh.after.expected === r.requestId && equal(rw.refresh.after.pins, p.initial.pins), rw.refresh);
  const w = published(label + 'MovePin W', rw.move, p.moveId, true, 'taskbar-pins-write', binding);
  const expectedProposal = {revision: initialSnapshot.revision, identities: expectedOrder};
  check(label + ' independent order permutation and old CAS revision match actual write', equal(w.proposal, expectedProposal), {actual: w.proposal, expectedProposal});
  const expectedPending = {request: w.requestId, identities: expectedOrder};
  check(label + ' W is actually Pending, preserves confirmed old order and earlier R authority', equal(rw.move.after.pins, {snapshot: initialSnapshot, pending: expectedPending, notice: 'Saving pin order…', writable: false}) && rw.move.after.expected === r.requestId && uint(r.requestId) < uint(w.requestId), rw.move.after);
  check(label + ' primary receipt is legal FIFO read-before-write, not a reordered response', rw.read.input.requestId === r.requestId && equal(rw.read.input.preferences, initialSnapshot) && equal(rw.read.input.binding, binding) && equal(rw.read.before, rw.move.after), rw.read);
  check(label + ' matching earlier catalog read consumes only its own read authority', rw.read.after.expected === null && rw.read.after.request === w.requestId && equal(rw.read.after.applications, [...initialOrder].sort()), rw.read.after);
  check(label + ' Saving ignores earlier read without claiming save completion', equal(rw.read.after.pins, rw.move.after.pins), {before: rw.move.after.pins, after: rw.read.after.pins});
  noMutation(label + 'Read R', rw.read);
  const blockedControl = pinControl(rw.repeatMove.frameBefore, p.moveId);
  check(label + ' second conflicting pin command remains disabled in actual published frame', blockedControl?.enabled === false && rw.repeatMove.input.action === null, rw.repeatMove);
  exactUnchanged(label + 'conflicting command while Saving', rw.repeatMove);
  matchingSaved(label + 'Saved W after R', rw.saved, w, expectedSnapshot);

  const wr = p.writeThenRead;
  const firstW = published(label + 'W-before-R write', wr.move, p.moveId, true, 'taskbar-pins-write', binding);
  const laterR = published(label + 'W-before-R refresh', wr.refresh, 'control:refresh', true, 'catalog-request', binding);
  check(label + ' backend-barrier control preserves actual W-before-R request order', uint(firstW.requestId) < uint(laterR.requestId) && equal(firstW.proposal, expectedProposal) && equal(wr.saved.before, wr.refresh.after) && equal(wr.read.before, wr.saved.after), {firstW, laterR});
  matchingSaved(label + 'W-before-R Saved', wr.saved, firstW, expectedSnapshot);
  check(label + ' later read confirms order after actual Saved without another write', wr.read.input.requestId === laterR.requestId && equal(wr.read.input.preferences, expectedSnapshot) && equal(custody(wr.read.after.pins), {snapshot: expectedSnapshot, pending: null, writable: true}) && wr.read.after.expected === null, wr.read);
  noMutation(label + 'W-before-R read', wr.read);

  const recovery = p.unknownRecovery;
  check(label + ' Unknown fixture correlates to first actual W', recovery.unknown.input.status === 'Unknown' && recovery.unknown.input.requestId === firstW.requestId && equal(recovery.unknown.input.binding, binding) && recovery.unknown.input.preferences === null, recovery.unknown.input);
  pendingCustody(label + 'Unknown W', recovery.unknown);
  const recoveryR = published(label + 'explicit Unknown recovery read', recovery.refresh, 'control:refresh', true, 'catalog-request', binding);
  check(label + ' Unknown recovery read has fresh authority after W and does not repeat W', uint(recoveryR.requestId) > uint(firstW.requestId) && writes(recovery.refresh).length === 0 && equal(custody(recovery.refresh.after.pins), custody(recovery.unknown.after.pins)), recovery.refresh);
  check(label + ' explicit matched new read reconciles Unknown to independently expected persisted order', recovery.read.input.requestId === recoveryR.requestId && equal(recovery.read.input.preferences, expectedSnapshot) && equal(custody(recovery.read.after.pins), {snapshot: expectedSnapshot, pending: null, writable: true}) && recovery.read.after.expected === null, recovery.read);
  noMutation(label + 'Unknown recovered read', recovery.read);
  const older = p.unknownOlderRead;
  check(label + ' old read was already issued when matching Unknown arrived', older.unknown.before.expected === laterR.requestId && older.unknown.input.requestId === firstW.requestId && equal(older.unknown.before, wr.refresh.after), older.unknown);
  pendingCustody(label + 'Unknown with old read in flight', older.unknown);
  check(label + ' response to pre-Unknown read cannot masquerade as explicit recovery', older.olderRead.input.requestId === laterR.requestId && equal(older.olderRead.input.preferences, expectedSnapshot) && equal(older.olderRead.before, older.unknown.after) && older.olderRead.after.expected === null, older.olderRead);
  pendingCustody(label + 'pre-Unknown read preserves original save custody', older.olderRead);
  matchingSaved(label + 'matching Saved after protected old read', older.saved, firstW, expectedSnapshot);
  const explicitLaterR = published(label + 'later explicit Unknown recovery', older.refresh, 'control:refresh', true, 'catalog-request', binding);
  check(label + ' later recovery uses fresh read authority after ignored old response', uint(explicitLaterR.requestId) > uint(laterR.requestId) && writes(older.refresh).length === 0 && equal(custody(older.refresh.after.pins), custody(older.olderRead.after.pins)), older.refresh);
  check(label + ' only new explicit read reconciles Unknown after older response', older.read.input.requestId === explicitLaterR.requestId && equal(older.read.input.preferences, expectedSnapshot) && equal(custody(older.read.after.pins), {snapshot: expectedSnapshot, pending: null, writable: true}) && older.read.after.expected === null, older.read);
  noMutation(label + 'later explicit Unknown read', older.read);
  check(label + ' Refused receipt retires matching write without claiming proposed order', p.refused.input.status === 'Refused' && p.refused.input.requestId === firstW.requestId && equal(custody(p.refused.after.pins), {snapshot: initialSnapshot, pending: null, writable: true}) && p.refused.after.request === p.refused.before.request, p.refused);
  noMutation(label + 'Refused W', p.refused);

  check(label + ' null/lower/same/higher read variants all retained', equal(p.readVariants.map(row => row.name).sort(), ['null-preferences', 'lower-revision', 'same-revision', 'higher-revision'].sort()), p.readVariants.map(row => row.name));
  for (const row of p.readVariants) {
    check(label + row.name + ' is matching read issued before actual pending W', row.input.requestId === r.requestId && equal(row.before, rw.move.after), row);
    check(label + row.name + ' preserves entire Saving base/request/order state', equal(row.after.pins, row.before.pins) && row.after.expected === null && row.after.request === row.before.request, row);
    noMutation(label + row.name, row);
  }
  check(label + ' read typed-boundary negatives retain every required mutation', equal(p.readNegatives.map(row => row.name).sort(), ['foreign-lifetime', 'foreign-session', 'foreign-frontend', 'foreign-request', 'numeric-request', 'numeric-revision', 'extra-envelope', 'duplicate-identities', 'unknown-preference-field'].sort()));
  check(label + ' Saved typed-boundary negatives retain every required mutation', equal(p.savedNegatives.map(row => row.name).sort(), ['foreign-binding', 'foreign-request', 'numeric-request', 'numeric-revision', 'unknown-status', 'extra-envelope'].sort()));
  for (const row of [...p.readNegatives, ...p.savedNegatives]) exactUnchanged(label + row.name, row);
  check(label + ' invalid Saved advance/order controls retained', equal(p.invalidSaved.map(row => row.name).sort(), ['nonadvancing-saved', 'different-identities'].sort()));
  for (const row of p.invalidSaved) pendingCustody(label + row.name, row);
  pendingCustody(label + 'stale revision read', p.staleRead);
  check(label + ' stale input revision actually precedes known snapshot', uint(p.staleRead.input.preferences.revision) < uint(initialSnapshot.revision));
  exactUnchanged(label + 'duplicate Saved', p.duplicateSaved);
  exactUnchanged(label + 'duplicate old read', p.duplicateRead);
  report.scenarioReceipts.push({requirement: report.requirement, scenario: report.scenario, seed, pins: initialOrder.length, readRequest: r.requestId, pendingWriteRequest: w.requestId, originalRevision: initialSnapshot.revision, expectedSavedRevision: expectedSnapshot.revision, matrixHash: sha(JSON.stringify(p)), simulatedBridge: true, nativeAcceptance: false, wholeRequirementAccepted: false});
}
async function main() {
  const bytes = fs.readFileSync(compiledFile);
  report.artifactHashes[path.resolve(compiledFile)] = sha(bytes);
  report.artifactHashes[path.resolve(__filename)] = sha(fs.readFileSync(__filename));
  const fixture = path.join(__dirname, 'PinsPendingReplay.elm');
  report.artifactHashes[fixture] = sha(fs.readFileSync(fixture));
  const sandbox = {console, setTimeout, clearTimeout};
  vm.createContext(sandbox);
  vm.runInContext(bytes.toString('utf8'), sandbox, {timeout: 2000});
  save();
  for (const seed of seeds) {
    try {
      const trace = await new Promise((resolve, reject) => {
        const timer = setTimeout(() => reject(new Error('Compiled worker did not emit seed ' + seed)), 3000);
        const app = sandbox.Elm.PinsPendingReplay.init({flags: seed});
        let emitted = false;
        app.ports.outgoing.subscribe(value => {
          if (emitted) { check('seed ' + seed + ' emits one matrix only', false); save(); return; }
          emitted = true; clearTimeout(timer); resolve(JSON.parse(JSON.stringify(value)));
        });
      });
      report.traces.push({seed, trace});
      // Preserve every raw published action, state, wire and failure witness
      // before any independent oracle assertion can throw.
      save();
      inspect(trace, seed);
    } catch (error) { check('seed ' + seed + ' independent fixture prerequisites', false, String(error.stack || error)); }
    save();
  }
  check('all eight raw matrices and scenario receipts retained', report.traces.length === 8 && report.scenarioReceipts.length === 8);
  check('seeded actual pin counts cover the complete2-8range', equal([...new Set(report.traces.map(row => row.trace.pipeline.pinCount))].sort((a, b) => a - b), [2, 3, 4, 5, 6, 7, 8]));
  check('seeded actual full-width revisions genuinely vary', new Set(report.traces.map(row => row.trace.pipeline.setup.catalog.preferences.revision)).size === 8);
  report.passed = report.failures.length === 0;
  save();
  console.log(JSON.stringify({passed: report.passed, seedCases: report.traces.length, checks: report.checks.length, failures: report.failures.length, report: reportFile}));
  process.exitCode = report.passed ? 0 : 1;
}
main().catch(error => { report.error = String(error.stack || error); save(); console.error(report.error); process.exitCode = 2; });
