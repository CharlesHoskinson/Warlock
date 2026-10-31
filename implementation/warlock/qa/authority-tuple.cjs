'use strict';

// ELM-ARC-005 / architecture-005 independent bridge oracle.
// Expected authority comes from raw fixture inputs and pre-dispatch counters,
// never from an expected intent encoded by the implementation under test.
// Root compiles/runs this through reviewed protected QA; no native issuer here.
const fs = require('node:fs');
const vm = require('node:vm');
const path = require('node:path');
const crypto = require('node:crypto');
const {isDeepStrictEqual} = require('node:util');

const [compiledFile, reportFile] = process.argv.slice(2);
if (!compiledFile || !reportFile) throw new Error('Expected COMPILED_ELM.js REPORT.json');
const MAX = 18446744073709551615n;
const SAFE = 9007199254740991n;
const operations = new Map([
  ['minimize', 1], ['restore', 1], ['activate', 1],
  ['maximize', 2], ['restore-geometry', 2], ['exit-fullscreen', 2],
  ['pin', 2], ['unpin', 2], ['snap', 2], ['transfer-workspace', 2]
]);
const negativeCategories = [
  'stale-stamp', 'invalid-projection', 'invalid-numeric', 'counter-exhaustion',
  'invalid-target', 'unknown-no-replay', 'foreign-receipt', 'stale-proposal', 'duplicate'
];
const report = {
  schema: 1,
  requirement: 'ELM-ARC-005',
  scenario: 'architecture-005',
  oracle: 'the serialized request contains the full authority tuple',
  verification: 'Preserved scenario report with native or bridge trace showing: the serialized request contains the full authority tuple; artifact hashes and matching scenario receipts included.',
  scope: 'Root-compiled actual Elm production route with explicit simulated bridge outcomes; no genuine native issuer or physical mutation',
  passed: false,
  nativeAcceptance: false,
  haskellPortAcceptance: false,
  releaseAccepted: false,
  checks: [],
  failures: [],
  scenarioReceipts: [],
  artifactHashes: {},
  trace: null,
  traces: [],
  seededTesting: {
    initialSeed: 20261031,
    algorithm: 'initial seed then xorshift32 unsigned-right-shift1, replacing zero with1; select eight distinct fixture offsets modulo17',
    seeds: [],
    candidateSeeds: [],
    constraint: 'The fixture varies identities by seed modulo17; equivalent offsets are deduplicated before any execution or oracle outcome is observed',
    scope: 'Eight fixed production-route matrices with independently varied full-width fixture authority identities; no random scheduler or exhaustive proof claim'
  }
};

const sha = bytes => crypto.createHash('sha256').update(bytes).digest('hex');
function save() { fs.writeFileSync(reportFile, JSON.stringify(report, null, 2) + '\n'); }
function check(name, condition, detail) {
  const row = {name, passed: Boolean(condition)};
  if (!condition) row.detail = detail === undefined ? null : detail;
  report.checks.push(row);
  if (!condition) report.failures.push(row);
  return Boolean(condition);
}
function uint64(value, name, positive = true) {
  if (typeof value !== 'string' || !/^(0|[1-9][0-9]{0,19})$/.test(value)) {
    throw new Error(name + ' must be a canonical decimal string, received ' + JSON.stringify(value));
  }
  const parsed = BigInt(value);
  if (parsed > MAX || (positive && parsed === 0n)) throw new Error(name + ' outside required UInt64 range');
  return parsed;
}
function increment(value, name) {
  const before = uint64(value, name, false);
  if (before === MAX) throw new Error(name + ' exhausted in a positive case');
  return String(before + 1n);
}
function exactFields(value, names) {
  return value !== null && typeof value === 'object' && !Array.isArray(value)
    && isDeepStrictEqual(Object.keys(value).sort(), [...names].sort());
}
function effects(values) {
  if (!Array.isArray(values)) throw new Error('Expected an array of actual emitted native wire values');
  return values.filter(value => value?.kind === 'window-effect');
}
function tupleOf(intent) {
  return {
    request: intent?.request,
    lifetime: intent?.context?.lifetime,
    epoch: intent?.context?.epoch,
    generation: intent?.generation,
    incarnation: intent?.incarnation,
    output: intent?.context?.output,
    revision: intent?.context?.revision
  };
}
function matchingRecord(record, wire, issued) {
  return record && isDeepStrictEqual(record.intent, wire.intent)
    && record[issued ? 'protocol' : 'effectProtocol'] === wire.effectProtocol
    && (!issued || isDeepStrictEqual(record.binding, wire.binding));
}
function expectedFromRaw(row) {
  const {binding, attached, watermarks, actionProjection, geometryFacts} = row.admitted;
  if (!exactFields(binding, ['lifetime', 'session', 'frontend'])) throw new Error('Raw binding shape missing');
  for (const [key, value] of Object.entries(binding)) uint64(value, 'raw binding.' + key);
  if (attached?.protocolVersion !== 3 || attached.kind !== 'attached' || !isDeepStrictEqual(attached.binding, binding)) {
    throw new Error('Raw attached input does not establish the reported binding');
  }
  if (watermarks?.protocolVersion !== 3 || watermarks.kind !== 'host-recovery-watermarks' || !isDeepStrictEqual(watermarks.binding, binding)
    || watermarks.request !== row.before.request || watermarks.generation !== row.before.generation) {
    throw new Error('Actual preallocation counters do not match raw installed recovery watermarks');
  }
  const geometry = row.effectProtocol === 2;
  const source = geometry ? geometryFacts : actionProjection;
  if (!source || source.protocolVersion !== 3 || source.kind !== (geometry ? 'geometry-facts' : 'action-projection')) {
    throw new Error('Missing raw admitted source frame for protocol ' + row.effectProtocol);
  }
  if (!isDeepStrictEqual(source.binding, binding)) throw new Error('Raw source frame and binding differ');
  const rawContext = geometry ? {
    lifetime: binding.lifetime,
    epoch: binding.frontend,
    output: geometryFacts.outputGeneration,
    revision: geometryFacts.revision
  } : actionProjection.context;
  if (!exactFields(rawContext, ['lifetime', 'epoch', 'output', 'revision'])) throw new Error('Raw authority context shape missing');
  if (rawContext.lifetime !== binding.lifetime || rawContext.epoch !== binding.frontend) {
    throw new Error('Raw source authority does not join current binding');
  }
  const rows = geometry ? geometryFacts.facts?.windows : actionProjection.scene?.windows;
  if (!Array.isArray(rows) || !rows.some(window => window.incarnation === row.targetIncarnation)) {
    throw new Error('Selected target is absent from the raw admitted source');
  }
  const expected = {
    request: increment(row.before.request, 'pre-dispatch request'),
    lifetime: rawContext.lifetime,
    epoch: rawContext.epoch,
    generation: increment(row.before.generation, 'pre-dispatch generation'),
    incarnation: row.targetIncarnation,
    output: rawContext.output,
    revision: rawContext.revision
  };
  for (const [key, value] of Object.entries(expected)) uint64(value, 'expected ' + key);
  return {expected, binding, rawContext, target: rows.find(window => window.incarnation === row.targetIncarnation)};
}

function positive(row, seed) {
  const label = 'positive ' + row.name + ': ';
  const start = report.failures.length;
  const {expected, binding, rawContext, target} = expectedFromRaw(row);
  check(label + 'operation selects its recorded production protocol', operations.get(row.operation) === row.effectProtocol, row.operation);
  const emitted = effects(row.emitted);
  check(label + 'actual owning route emits one window-effect', emitted.length === 1, row.emitted);
  if (emitted.length !== 1) return;
  const wire = emitted[0];
  check(label + 'real protocol3 window-effect envelope has exact fields', exactFields(wire, ['protocolVersion', 'kind', 'effectProtocol', 'binding', 'intent']) && wire.protocolVersion === 3 && wire.kind === 'window-effect', wire);
  check(label + 'wire binding and protocol match admitted facts', isDeepStrictEqual(wire.binding, binding) && wire.effectProtocol === row.effectProtocol, wire);
  const intentFields = ['request', 'generation', 'incarnation', 'operation', 'context'];
  if (row.operation === 'snap') intentFields.push('placement');
  if (row.operation === 'transfer-workspace') intentFields.push('transfer');
  check(label + 'intent and context use their closed production schema', exactFields(wire.intent, intentFields) && exactFields(wire.intent.context, ['lifetime', 'epoch', 'output', 'revision']), wire.intent);
  check(label + 'operation is the independently selected action', wire.intent.operation === row.operation, wire.intent.operation);
  const actual = tupleOf(wire.intent);
  for (const [field, value] of Object.entries(actual)) {
    uint64(value, label + field);
    check(label + 'serialized ' + field + ' equals independent raw-input expectation', value === expected[field], {expected: expected[field], actual: value});
  }
  check(label + 'all seven authority values are distinct full-width positive strings', new Set(Object.values(expected)).size === 7 && Object.values(expected).every(value => uint64(value, label + 'known authority') > SAFE), expected);
  if (row.effectProtocol === 2) {
    uint64(target.monitor, label + 'raw native output identity');
    check(label + 'output authority uses native generation rather than monitor identity', expected.output !== target.monitor && actual.output !== target.monitor, {monitor: target.monitor, outputGeneration: expected.output, emitted: actual.output});
  }
  check(label + 'request/generation advance exactly once in custody', row.custodyAfter.request === expected.request && row.custodyAfter.generation === expected.generation, row.custodyAfter);
  check(label + 'the exact issued request is Pending', row.custodyAfter.transaction?.status === 'Pending' && isDeepStrictEqual(row.custodyAfter.transaction?.intent, wire.intent), row.custodyAfter.transaction);
  const pending = row.custodyAfter.unresolved?.filter(record => matchingRecord(record, wire, false)) ?? [];
  const issued = row.custodyAfter.issued?.filter(record => matchingRecord(record, wire, true)) ?? [];
  check(label + 'one exact unresolved and issued record retain the admitted tuple', pending.length === 1 && pending[0].status === 'Pending' && issued.length === 1, row.custodyAfter);
  const otherUnresolved = row.custodyAfter.unresolved?.filter(record => !matchingRecord(record, wire, false));
  const otherIssued = row.custodyAfter.issued?.filter(record => !matchingRecord(record, wire, true));
  check(label + 'unrelated unresolved/issued custody survives actual dispatch', isDeepStrictEqual(otherUnresolved, row.custodyBefore.unresolved) && isDeepStrictEqual(otherIssued, row.custodyBefore.issued));
  const receipt = row.receipt;
  check(label + 'outcome is explicitly a simulated bridge fixture', receipt?.simulated === true);
  check(label + 'matching bridge receipt retains the entire emitted identity', receipt?.wire?.protocolVersion === 3 && receipt.wire.kind === 'effect-outcome' && receipt.wire.status === 'Committed' && receipt.wire.effectProtocol === wire.effectProtocol && isDeepStrictEqual(receipt.wire.binding, wire.binding) && isDeepStrictEqual(receipt.wire.intent, wire.intent), receipt?.wire);
  check(label + 'actual receipt route settles exactly the emitted request', receipt?.after?.transaction?.status === 'Committed' && isDeepStrictEqual(receipt.after.transaction.intent, wire.intent), receipt?.after?.transaction);
  check(label + 'terminal receipt releases only its exact unresolved/issued records', isDeepStrictEqual(receipt?.after?.unresolved, row.custodyBefore.unresolved) && isDeepStrictEqual(receipt?.after?.issued, row.custodyBefore.issued));
  check(label + 'receipt processing emits no repeated window effect', effects(receipt?.emittedAfter).length === 0, receipt?.emittedAfter);
  report.scenarioReceipts.push({
    requirement: report.requirement, scenario: report.scenario, case: row.name, seed,
    operation: row.operation, effectProtocol: row.effectProtocol,
    knownAuthority: expected, rawObservationContext: rawContext,
    emittedEnvelopeSHA256: sha(JSON.stringify(wire)),
    simulatedBridgeReceiptSHA256: sha(JSON.stringify(receipt.wire)),
    passed: report.failures.length === start,
    nativeAcceptance: false
  });
}

function hasNumericAuthority(value) {
  if (!value || typeof value !== 'object') return false;
  const identityFields = new Set(['lifetime', 'session', 'frontend', 'epoch', 'request', 'generation', 'incarnation', 'output', 'outputGeneration', 'revision']);
  return Object.entries(value).some(([key, child]) => (identityFields.has(key) && typeof child === 'number') || hasNumericAuthority(child));
}
function hasMalformedAuthority(value) {
  if (!value || typeof value !== 'object') return false;
  const identityFields = new Set(['lifetime', 'session', 'frontend', 'epoch', 'request', 'generation', 'incarnation', 'output', 'outputGeneration', 'revision']);
  return Object.entries(value).some(([key, child]) => {
    if (identityFields.has(key)) {
      try { uint64(child, key); }
      catch (_) { return true; }
    }
    return hasMalformedAuthority(child);
  });
}
function custodyWithoutDiagnostics(value) {
  if (value === null || typeof value !== 'object' || Array.isArray(value)) throw new Error('Missing exact authority custody state');
  const copy = {...value};
  // These two bounded diagnostic fields are explicitly allowed by the reviewed
  // decoder contract. Every other exported domain/custody field stays exact.
  delete copy.notice;
  delete copy.decoderRefusal;
  return copy;
}
function negative(row) {
  const label = 'negative ' + row.name + ': ';
  check(label + 'declared negative category is independently required', negativeCategories.includes(row.category), row.category);
  check(label + 'no window-effect mutation is emitted', row.effectCount === 0 && effects(row.emitted).length === 0, {windowEffectCount: row.effectCount, emitted: row.emitted, totalControllerEffectCount: row.totalControllerEffectCount});
  check(label + 'only the reviewed bounded diagnostic fields may change', Array.isArray(row.diagnosticChangesAllowed) && isDeepStrictEqual([...row.diagnosticChangesAllowed].sort(), ['decoderRefusal', 'notice']));
  check(label + 'all exact authority and resource custody is unchanged', isDeepStrictEqual(custodyWithoutDiagnostics(row.custodyBefore), custodyWithoutDiagnostics(row.custodyAfter)), {before: row.custodyBefore, after: row.custodyAfter});
  if (row.category === 'invalid-numeric') check(label + 'actual malformed input contains an invalid canonical authority value', hasMalformedAuthority(row.input), row.input);
  if (row.name.startsWith('numeric-')) check(label + 'actual numeric-field counterexample is retained', hasNumericAuthority(row.input), row.input);
  if (row.category === 'counter-exhaustion') check(label + 'a real pre-dispatch identity counter is exhausted', row.before?.request === String(MAX) || row.before?.generation === String(MAX), row.before);
  if (row.category === 'duplicate') {
    const terminalReceipt = row.input?.kind === 'effect-outcome' && row.input?.status === 'Committed';
    check(label + (terminalReceipt ? 'terminal receipt duplicate starts from Committed' : 'duplicate dispatch starts from an already Pending transaction'), row.custodyBefore?.transaction?.status === (terminalReceipt ? 'Committed' : 'Pending'), row.custodyBefore);
  }
  if (row.category === 'unknown-no-replay') check(label + 'uncertain retry starts from an actual Unknown outcome', row.custodyBefore?.transaction?.status === 'Unknown', row.custodyBefore);
  if (row.category === 'invalid-target') check(label + 'unknown target is absent from the admitted action inventory', typeof row.input === 'string' && Array.isArray(row.custodyBefore?.observed?.windows) && !row.custodyBefore.observed.windows.some(window => window.incarnation === row.input), row.input);
}

let timer;
try {
  const bytes = fs.readFileSync(compiledFile);
  report.artifactHashes[path.resolve(compiledFile)] = sha(bytes);
  report.artifactHashes[path.resolve(__filename)] = sha(fs.readFileSync(__filename));
  const sandbox = {console, setTimeout, clearTimeout};
  vm.createContext(sandbox);
  vm.runInContext(bytes.toString('utf8'), sandbox, {timeout: 2000});
  let state = 20261031 >>> 0;
  const seeds = [state];
  const offsets = new Set([state % 17]);
  report.seededTesting.candidateSeeds.push(state);
  while (seeds.length < 8) {
    state ^= state << 13;
    state ^= state >>> 17;
    state ^= state << 5;
    state >>>= 0;
    const candidate = (state >>> 1) || 1;
    report.seededTesting.candidateSeeds.push(candidate);
    if (!offsets.has(candidate % 17)) {
      offsets.add(candidate % 17);
      seeds.push(candidate);
    }
  }
  report.seededTesting.seeds = seeds;
  function inspect(trace, seed) {
    check('Fixture names the exact original requirement and scenario', trace.schema === 1 && trace.requirement === report.requirement && trace.scenario === report.scenario, trace);
    check('Retained fixture trace names its actual seed', trace.seed === seed, {expected: seed, actual: trace.seed});
    const positives = trace.positives;
    const negatives = trace.negatives;
    check('Positive and negative routes are both nonempty', Array.isArray(positives) && positives.length > 0 && Array.isArray(negatives) && negatives.length > 0);
    if (!Array.isArray(positives) || !Array.isArray(negatives)) throw new Error('Missing fixture case arrays');
    check('All ten current Operation constructors reach real emitted requests', [...operations.keys()].every(operation => positives.some(row => row.operation === operation)), positives.map(row => row.operation));
    check('Both owning construction protocols are covered', [1, 2].every(protocol => positives.some(row => row.effectProtocol === protocol)));
    check('Stale/malformed/unavailable/exhaustion/duplicate/Unknown/foreign-receipt negative routes are all present', negativeCategories.every(category => negatives.some(row => row.category === category)), negatives.map(row => row.category));
    check('Case names remain unique and nonempty', [...positives, ...negatives].every(row => typeof row.name === 'string' && row.name.length > 0) && new Set([...positives, ...negatives].map(row => row.name)).size === positives.length + negatives.length);
    for (const row of positives) {
      try { positive(row, seed); }
      catch (error) { check('positive ' + row.name + ': independent oracle prerequisites', false, String(error.stack || error)); }
    }
    for (const row of negatives) {
      try { negative(row); }
      catch (error) { check('negative ' + row.name + ': independent oracle prerequisites', false, String(error.stack || error)); }
    }
    if (positives.some(row => row.seeded) || negatives.some(row => row.seeded)) {
      check('Seeded variants retain reproducible generator metadata', Number.isInteger(trace.seed) && typeof trace.generator === 'string' && trace.generator.length > 0 && Number.isInteger(trace.variantCount) && trace.variantCount === [...positives, ...negatives].filter(row => row.seeded).length, {seed: trace.seed, generator: trace.generator, variantCount: trace.variantCount});
    }
  }
  function run(index) {
    if (index === seeds.length) {
      check('All eight independent seeded route matrices emitted retained traces', report.traces.length === seeds.length);
      const observedTuples = report.scenarioReceipts.filter(row => row.operation === 'minimize').map(row => JSON.stringify(row.knownAuthority));
      check('Seed variants actually vary full authority inputs', observedTuples.length === seeds.length && new Set(observedTuples).size === seeds.length, observedTuples);
      report.passed = report.failures.length === 0;
      save();
      console.log(JSON.stringify({passed: report.passed, seedCases: report.traces.length, scenarioReceipts: report.scenarioReceipts.length, checks: report.checks.length, failures: report.failures.length, report: reportFile}));
      process.exitCode = report.passed ? 0 : 1;
      return;
    }
    const seed = seeds[index];
    let received = false;
    timer = setTimeout(() => {
      if (!received) {
        report.error = 'Compiled fixture did not emit seed ' + seed + ' within three seconds';
        save();
        process.exitCode = 2;
      }
    }, 3000);
    let app;
    try {
      app = sandbox.Elm.AuthorityTupleReplay.init({flags: seed});
    } catch (error) {
      clearTimeout(timer);
      check('Seed ' + seed + ': compiled fixture initialization', false, String(error.stack || error));
      save();
      setTimeout(() => run(index + 1), 0);
      return;
    }
    app.ports.outgoing.subscribe(value => {
      if (received) {
        check('Fixture emits exactly one trace for seed ' + seed, false);
        save();
        process.exitCode = 1;
        return;
      }
      received = true;
      clearTimeout(timer);
      try {
        const trace = JSON.parse(JSON.stringify(value));
        report.trace = trace;
        report.traces.push({seed, trace});
        // Preserve every raw trace before an independent assertion can throw.
        save();
        inspect(trace, seed);
      } catch (error) {
        check('Seed ' + seed + ': complete independent oracle prerequisites', false, String(error.stack || error));
      }
      save();
      setTimeout(() => run(index + 1), 0);
    });
  }
  run(0);
} catch (error) {
  clearTimeout(timer);
  report.error = String(error.stack || error);
  save();
  console.error(report.error);
  process.exitCode = 2;
}
