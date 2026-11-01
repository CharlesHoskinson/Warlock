'use strict';
// QA ONLY. The protected root compiles TeaContractReplay WITHOUT --optimize.
// Usage: node qa/tea-contract.cjs /absolute/TeaContractReplay.js [cases.cjs]
// The compiled fixture invokes Debug.log on exactly the unchanged tuple returned
// by DesktopPolicy.update. The sole temporary in-memory insertion intercepts
// that marker before Elm formats it. It does not change reducer functions,
// compiled source on disk, ports, values, or product build inputs. Both exact
// bundle hashes and the reversible byte patch are reported. No native claim.
const fs = require('node:fs');
const path = require('node:path');
const vm = require('node:vm');
const crypto = require('node:crypto');
const { isDeepStrictEqual } = require('node:util');
const MARKER = 'TEA_CONTRACT_OBSERVE_V1';
const HOOK = '__warlockTeaCaptureV1';
const WAIT_MS = 10000;
const hash = data => crypto.createHash('sha256').update(data).digest('hex');
function insist(condition, message) { if (!condition) throw new Error(message); }
const trustedPrototypes = new WeakMap();
function registerPrototype(proto, kind) {
  const descriptors = Object.getOwnPropertyDescriptors(proto);
  trustedPrototypes.set(proto, { kind, descriptors });
}
function registerRealm(context) {
  const intrinsics = vm.runInContext('({object: Object.prototype, array: Array.prototype})', context);
  registerPrototype(intrinsics.object, 'object');
  registerPrototype(intrinsics.array, 'array');
}
function checkPrototype(proto, kind, where) {
  if (proto === null && kind === 'object') return;
  const saved = trustedPrototypes.get(proto);
  insist(saved && saved.kind === kind, `${where}: untrusted prototype`);
  const now = Object.getOwnPropertyDescriptors(proto);
  const keys = Reflect.ownKeys(saved.descriptors);
  insist(keys.length === Reflect.ownKeys(now).length, `${where}: changed intrinsic prototype`);
  for (const key of keys) {
    const before = saved.descriptors[key];
    const after = now[key];
    insist(after && ['value', 'get', 'set', 'writable', 'enumerable', 'configurable']
      .every(field => Object.is(before[field], after[field])), `${where}: changed intrinsic prototype member`);
  }
}
registerPrototype(Object.prototype, 'object');
registerPrototype(Array.prototype, 'array');

// Preserve every own data field, including constructor tags, list cells,
// tuples, opaque wrappers and JSON values. Functions, cycles, accessors, sparse
// arrays, exotic prototypes, non-finite or non-JSON numbers and symbols fail:
// the harness must never silently shrink a model or a typed effect.
function full(value, where = '$', active = new Set()) {
  if (value === null || typeof value === 'string' || typeof value === 'boolean') return value;
  if (typeof value === 'number') {
    insist(Number.isFinite(value) && !Object.is(value, -0), `${where}: unsupported number`);
    return value;
  }
  insist(typeof value === 'object', `${where}: unsupported ${typeof value}`);
  insist(!active.has(value), `${where}: cyclic value`);
  insist(Object.getOwnPropertySymbols(value).length === 0, `${where}: symbol property`);
  active.add(value);
  try {
    const descriptors = Object.getOwnPropertyDescriptors(value);
    if (Array.isArray(value)) {
      checkPrototype(Object.getPrototypeOf(value), 'array', where);
      const keys = Object.keys(descriptors).filter(key => key !== 'length');
      insist(keys.length === value.length && keys.every((key, i) => key === String(i)), `${where}: sparse or extended array`);
      return keys.map(key => {
        const d = descriptors[key];
        insist(d && 'value' in d && d.enumerable, `${where}[${key}]: non-data property`);
        return full(d.value, `${where}[${key}]`, active);
      });
    }
    checkPrototype(Object.getPrototypeOf(value), 'object', where);
    const out = Object.create(null);
    for (const key of Object.keys(descriptors).sort()) {
      const d = descriptors[key];
      insist(d && 'value' in d && d.enumerable, `${where}.${key}: accessor or hidden property`);
      Object.defineProperty(out, key, { value: full(d.value, `${where}.${key}`, active), enumerable: true });
    }
    return out;
  } finally { active.delete(value); }
}

function instrument(original) {
  // Anchor to the actual non-optimized Elm debug implementation, not the
  // _UNUSED placeholder. Reject compiler layout changes rather than guessing.
  const definition = /var _Debug_log\s*=\s*F2\(function\s*\(tag,\s*value\)\s*\{/g;
  const matches = [...original.matchAll(definition)];
  insist(matches.length === 1, 'expected exactly one Elm _Debug_log definition');
  const begin = matches[0].index + matches[0][0].length;
  const end = original.indexOf('});', begin);
  insist(end > begin && end - begin < 1000, 'unrecognized _Debug_log body');
  const body = original.slice(begin, end);
  insist(body.includes('_Debug_toString(value)') && /return\s+value\s*;/.test(body), 'fixture must be unoptimized debug Elm');
  insist(original.split(MARKER).length === 2, 'expected exactly one fixture observation marker');
  insist(!original.includes(HOOK), 'capture hook already present');
  const insertion = `\nif (tag === ${JSON.stringify(MARKER)}) { globalThis.${HOOK}(value); }\n`;
  const changed = original.slice(0, begin) + insertion + original.slice(begin);
  insist(changed.slice(0, begin) + changed.slice(begin + insertion.length) === original, 'instrumentation not exactly reversible');
  return { changed, insertionOffset: begin, insertedBytes: Buffer.byteLength(insertion) };
}

function loadElm(source, captures) {
  const context = { console: { log() {}, warn() {}, error() {} }, setTimeout, clearTimeout };
  context[HOOK] = value => {
    const tuple = full(value);
    insist(tuple && typeof tuple === 'object' && !Array.isArray(tuple), 'observer value is not a tuple');
    const keys = Object.keys(tuple).sort().join(',');
    insist(keys === '$,a,b' && tuple.$ === '#2', `unexpected debug tuple shape: ${keys}`);
    captures.push(full({ state: tuple.a, effects: tuple.b }));
  };
  vm.createContext(context);
  registerRealm(context);
  new vm.Script(source, { filename: 'TeaContractReplay.instrumented.js' }).runInContext(context, { timeout: 10000 });
  insist(context.Elm && context.Elm.TeaContractReplay && typeof context.Elm.TeaContractReplay.init === 'function', 'compiled TeaContractReplay worker missing');
  const app = context.Elm.TeaContractReplay.init({ flags: null });
  insist(app.ports && app.ports.incoming && typeof app.ports.incoming.send === 'function' && app.ports.outgoing && typeof app.ports.outgoing.subscribe === 'function', 'required fixture ports missing');
  return app;
}

// Inspect the complete debug List Policy.Effect instead of trusting port
// counts or constructor names alone. All payloads remain in the full tree.
function countDelays(list, where) {
  let count = 0;
  let cursor = list;
  let cells = 0;
  while (cursor && typeof cursor === 'object' && cursor.$ === '::') {
    insist(Object.keys(cursor).sort().join(',') === '$,a,b', `${where}: malformed effect-list cell`);
    const effect = cursor.a;
    insist(effect && typeof effect === 'object', `${where}: malformed effect`);
    const keys = Object.keys(effect).sort().join(',');
    if (effect.$ === 'Publish') insist(keys === '$,a', `${where}: malformed Publish`);
    else if (effect.$ === 'Delay') {
      insist(keys === '$,a,b' && typeof effect.a === 'number' && Number.isFinite(effect.a), `${where}: malformed Delay`);
      count++;
    } else throw new Error(`${where}: unsupported typed effect ${String(effect.$)}`);
    cursor = cursor.b;
    insist(++cells <= 10000, `${where}: effect list exceeds QA bound`);
  }
  insist(cursor && cursor.$ === '[]' && Object.keys(cursor).join(',') === '$', `${where}: malformed effect-list terminator`);
  return count;
}

// Inputs were already fully validated. Elm keyValuePairs calls hasOwnProperty,
// so port-bound nested records need ordinary prototypes. Keep observed and
// expected trees unchanged; defineProperty safely preserves __proto__ keys.
function portValue(value) {
  if (value === null || typeof value !== 'object') return value;
  if (Array.isArray(value)) return value.map(portValue);
  const result = {};
  for (const key of Object.keys(value)) {
    Object.defineProperty(result, key, { value: portValue(value[key]),
      enumerable: true, writable: true, configurable: true });
  }
  return result;
}

function validateCases(moduleValue) {
  insist(moduleValue && Array.isArray(moduleValue.cases) && typeof moduleValue.materialize === 'function', 'oracle must export cases and materialize(case)');
  insist(moduleValue.cases.length > 0, 'independent oracle has no cases');
  const seen = new Set();
  return moduleValue.cases.map(spec => {
    const expanded = moduleValue.materialize(spec); // authored literal GIVEN/overrides, never observed reducer output
    insist(expanded && typeof expanded.name === 'string' && expanded.name.length > 0 && !seen.has(expanded.name), 'case name missing or duplicate');
    seen.add(expanded.name);
    insist(Array.isArray(expanded.steps) && expanded.steps.length > 1 &&
      expanded.steps.some((step, index) => index > 0 && step && step.input && step.input.kind !== 'prelude' && step.input.kind !== 'reset'),
      `${expanded.name}: at least one tested transition after setup required`);
    return { name: expanded.name, steps: expanded.steps.map((step, index) => {
      insist(step && step.input && step.expected && Object.hasOwn(step.expected, 'state') && Object.hasOwn(step.expected, 'effects'), `${expanded.name}/${index}: complete literal expected state and effects required`);
      const input = full(step.input, `${expanded.name}/${index}/input`);
      insist(input && typeof input.kind === 'string' && (index !== 0 || input.kind === 'reset') && (index === 0 || input.kind !== 'reset'), `${expanded.name}/${index}: exactly one leading reset required`);
      insist(!Object.hasOwn(input, 'caseId') && !Object.hasOwn(input, 'step'), `${expanded.name}/${index}: reserved input metadata`);
      const isPrelude = input.kind === 'prelude';
      insist(!isPrelude || (index === 1 && Number.isSafeInteger(step.setupTimers) && step.setupTimers >= 0),
        `${expanded.name}/${index}: prelude requires a literal setupTimers and must immediately follow reset`);
      insist(isPrelude || !Object.hasOwn(step, 'setupTimers'), `${expanded.name}/${index}: setupTimers outside prelude`);
      return { input, expected: full(step.expected, `${expanded.name}/${index}/expected`), setupTimers: isPrelude ? step.setupTimers : null };
    }) };
  });
}

// Load exactly the oracle bytes that are hashed. No Node require, process,
// filesystem, clocks or random source are supplied to the oracle realm. This
// narrows the reproducibility boundary; independent literal authorship still
// requires source review and is not proved by sandboxing.
function loadOracle(bytes, filename) {
  const source = bytes.toString('utf8');
  insist(Buffer.from(source, 'utf8').equals(bytes), 'oracle is not canonical UTF-8');
  const context = vm.createContext({ Date: undefined,
    process: undefined, require: undefined, fetch: undefined, console: undefined },
    { codeGeneration: { strings: false, wasm: false } });
  registerRealm(context);
  new vm.Script('globalThis.module = { exports: {} }; globalThis.exports = module.exports; Math.random = undefined;\n' + source,
    { filename }).runInContext(context, { timeout: 10000 });
  return context.module.exports;
}

async function executeCase(source, testCase) {
  const captures = [];
  const app = loadElm(source, captures);
  let pending = null;
  let protocolError = null;
  app.ports.outgoing.subscribe(message => {
    if (!pending) { protocolError = new Error(`${testCase.name}: unexpected or duplicate acknowledgement`); return; }
    const resolve = pending;
    pending = null;
    resolve(full(message, `${testCase.name}/ack`));
  });
  const trace = [];
  let deadlineCount = 0;
  for (let i = 0; i < testCase.steps.length; i++) {
    insist(!protocolError && captures.length === i, `${testCase.name}/${i}: unexpected capture or acknowledgement`);
    const current = testCase.steps[i];
    const ack = await new Promise((resolve, reject) => {
      let timer;
      pending = value => { clearTimeout(timer); resolve(value); };
      timer = setTimeout(() => { pending = null; reject(new Error(`${testCase.name}/${i}: worker acknowledgement timeout`)); }, WAIT_MS);
      try { app.ports.incoming.send({ ...portValue(current.input), caseId: testCase.name, step: i }); }
      catch (error) { clearTimeout(timer); pending = null; reject(error); }
    });
    insist(!protocolError && ack && ack.ok === true && ack.error === '' && ack.caseId === testCase.name && ack.step === i, `${testCase.name}/${i}: invalid fixture acknowledgement`);
    insist(captures.length === i + 1, `${testCase.name}/${i}: expected one complete capture`);
    const observed = captures[i];
    if (i === 0) deadlineCount = 0;
    const currentDelays = countDelays(observed.effects, `${testCase.name}/${i}`);
    if (current.input.kind === 'prelude') {
      // GIVEN setup, not a tested transition. Earlier effects are hidden;
      // retained timer total is an independent literal oracle.
      insist(current.setupTimers >= currentDelays, `${testCase.name}/${i}: impossible setup timer count`);
      deadlineCount = current.setupTimers;
    } else deadlineCount += currentDelays;
    insist(Number.isSafeInteger(ack.timers) && ack.timers === deadlineCount, `${testCase.name}/${i}: timer retention mismatch`);
    insist(isDeepStrictEqual(observed, current.expected), `${testCase.name}/${i}: full state/effects differ from independent literal oracle\nexpected=${JSON.stringify(current.expected)}\nactual=${JSON.stringify(observed)}`);
    trace.push(observed);
  }
  insist(!protocolError, `${testCase.name}: acknowledgement protocol failure`);
  return trace;
}

async function main() {
  insist(process.argv.length === 3 || process.argv.length === 4, 'usage: node tea-contract.cjs compiled-fixture.js [cases.cjs]');
  const compiledPath = path.resolve(process.argv[2]);
  const casesPath = path.resolve(process.argv[3] || path.join(__dirname, 'tea-contract-cases.cjs'));
  const fixtureElmPath = path.join(__dirname, 'TeaContractReplay.elm');
  const raw = fs.readFileSync(compiledPath);
  const original = raw.toString('utf8');
  insist(Buffer.from(original, 'utf8').equals(raw), 'fixture is not canonical UTF-8');
  const patch = instrument(original);
  const oracleBytes = fs.readFileSync(casesPath);
  const oracle = loadOracle(oracleBytes, casesPath);
  const coverage = full(oracle.coverage, 'oracle/coverage');
  insist(coverage && typeof coverage.complete === 'boolean' &&
    Array.isArray(coverage.supported) && coverage.supported.every(x => typeof x === 'string') &&
    Array.isArray(coverage.missing) && coverage.missing.every(x => typeof x === 'string') &&
    (!coverage.complete || coverage.missing.length === 0) &&
    (coverage.complete || coverage.missing.length > 0), 'explicit honest oracle coverage declaration required');
  const cases = validateCases(oracle);
  let transitions = 0;
  let preludes = 0;
  for (const testCase of cases) {
    const first = await executeCase(patch.changed, testCase);
    const second = await executeCase(patch.changed, testCase);
    insist(isDeepStrictEqual(first, second), `${testCase.name}: nondeterministic full trace`);
    transitions += testCase.steps.filter(step => step.input.kind !== 'reset' && step.input.kind !== 'prelude').length;
    preludes += testCase.steps.filter(step => step.input.kind === 'prelude').length;
  }
  process.stdout.write(JSON.stringify({ schema: 1, scope: 'QA compiled owning-route replay; not native or whole-EARS acceptance',
    originalFixtureSha256: hash(raw), instrumentedFixtureSha256: hash(Buffer.from(patch.changed, 'utf8')),
    oracleSha256: hash(oracleBytes), runnerSha256: hash(fs.readFileSync(__filename)),
    fixtureElmSha256: hash(fs.readFileSync(fixtureElmPath)), marker: MARKER,
    patchOffset: patch.insertionOffset, patchInsertedBytes: patch.insertedBytes,
    reversiblePatch: true, coverageDeclaration: coverage, wholeTeaStatus: 'NOT_ASSESSED',
    cases: cases.map(c => c.name), transitions, preludes, runsPerCase: 2, passed: true }, null, 2) + '\n');
}
main().catch(error => { process.stderr.write(`tea-contract: ${error && error.stack || String(error)}\n`); process.exitCode = 1; });
