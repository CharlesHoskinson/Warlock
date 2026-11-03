'use strict';
// QA ONLY, ROOT EXECUTION ONLY. Read-only compiled-root replay, not native/browser acceptance.
// Capture exact actual init/update/subscription values and typed data before private interpretation.
const fs = require('node:fs');
const path = require('node:path');
const vm = require('node:vm');
const crypto = require('node:crypto');
const { isDeepStrictEqual } = require('node:util');
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

const INIT_HOOK = '__solHttpInitialV1';
const TYPED_HOOK = '__solHttpTypedV1';
const RETURN_HOOK = '__solHttpReturnV1';
const API = '__solHttpApiV1';
const PREFIX = '$author$project$';
function instrument(original, root) {
  insist(['HttpMain', 'HttpBar', 'HttpPopup'].includes(root), 'unsupported owning root');
  insist(![INIT_HOOK, TYPED_HOOK, RETURN_HOOK, API].some(name => original.includes(name)), 'observer already present');
  const insertions = [];
  const init = [...original.matchAll(/var\s+model\s*=\s*initPair\.a\s*;/g)];
  insist(init.length === 1, 'unrecognized actual _Platform_initialize init layout');
  insertions.push({ offset: init[0].index + init[0][0].length,
    text: `\nglobalThis.${INIT_HOOK}(model,update,subscriptions,initPair.b);\n` });
  const startup = `var ${PREFIX}UiHttp$${root === 'HttpMain' ? 'controller' : 'renderer'} =`;
  const start = original.indexOf(startup);
  insist(start >= 0 && original.indexOf(startup, start + 1) < 0, 'actual startup value missing/duplicated');
  insist(original.includes(`var ${PREFIX}UiHttp$interpret =`), 'typed UiHttp source patch absent');
  // Startup is an Elm top-level VALUE: wrap interpretation BEFORE that value
  // is evaluated, rather than lose the initial ReadEvents description.
  insertions.push({ offset: start, text: `
var __solOriginalHttpStart = ${PREFIX}UiHttp$startEffects;
${PREFIX}UiHttp$startEffects = function(role) {
  var pair = __solOriginalHttpStart(role);
  globalThis.${RETURN_HOOK}('startup',pair);
  return pair;
};
var __solOriginalHttpInterpret = ${PREFIX}UiHttp$interpret;
${PREFIX}UiHttp$interpret = function(descriptions) {
  globalThis.${TYPED_HOOK}('UiHttp',descriptions);
  return __solOriginalHttpInterpret(descriptions);
};
` });
  const exports = [...original.matchAll(/\n[ \t]*_Platform_export\(/g)];
  insist(exports.length === 1, 'actual program export layout changed');
  let observe = '';
  for (const fn of ['updateEffects', 'enqueueEffects', 'stopEffects']) {
    const symbol = `${PREFIX}UiHttp$${fn}`;
    if (!original.includes(`var ${symbol} =`)) {
      insist(fn !== 'updateEffects', 'actual pure transport reducer missing');
      continue; // unused helpers may be absent from this owning-root bundle
    }
    const saved = `__solOriginalHttp${fn}`;
    observe += `
var ${saved} = ${symbol};
${symbol} = F2(function(first,model) {
  var result = A2(${saved},first,model);
  globalThis.${RETURN_HOOK}('transition',result);
  return result;
});
`;
  }
  const wrappers = root === 'HttpMain'
    ? [['DesktopPolicy', 'update'], ['HttpMain.effects', 'effects']]
    : [[root === 'HttpPopup' ? 'Popup' : 'Bar', root === 'HttpPopup' ? 'transition' : 'step']];
  for (const [label, fn] of wrappers) {
    const module = label === 'HttpMain.effects' ? 'HttpMain' : label;
    const symbol = `${PREFIX}${module}$${fn}`;
    const saved = `__solOriginal${module}${fn}`;
    insist(original.includes(`var ${symbol} =`), `actual ${module}.${fn} missing`);
    observe += `
var ${saved} = ${symbol};
${symbol} = F2(function(first,model) {
  ${label === 'HttpMain.effects' ? `globalThis.${TYPED_HOOK}('${label}',first);` : ''}
  var pair = A2(${saved},first,model);
  ${label !== 'HttpMain.effects' ? `globalThis.${TYPED_HOOK}('${label}',pair.b);` : ''}
  return pair;
});
`;
  }
  observe += `
globalThis.${API} = {
  nonoptimized: function(){ return _Utils_Tuple2(0,0).$ === '#2'; },
  transport: ${PREFIX}${root}$Transport,
  view: ${root === 'HttpMain' ? 'null' : `${PREFIX}${root}$View`},
  a2: A2,
  message: function(input) {
    if (typeof ${PREFIX}UiHttp$Polled !== 'function' || typeof ${PREFIX}UiHttp$Posted !== 'function'
      || !$elm$http$Http$NetworkError || $elm$http$Http$NetworkError.$ !== 'NetworkError') {
      throw new Error('actual public HTTP message constructors missing/changed');
    }
    var message;
    switch(input.kind) {
      case 'viewAction':
        ${root === 'HttpMain' ? "throw new Error('no renderer View in HttpMain');" : `return ${PREFIX}${root}$View(${PREFIX}${root === 'HttpBar' ? 'Bar' : 'Popup'}$Action(_Json_wrap(input.value)));`}
        break;
      case 'poll': message=${PREFIX}UiHttp$Poll; break;
      case 'polledOk': message=${PREFIX}UiHttp$Polled($elm$core$Result$Ok(input.body)); break;
      case 'postedOk': message=${PREFIX}UiHttp$Posted($elm$core$Result$Ok(input.body)); break;
      case 'polledNetworkError': message=${PREFIX}UiHttp$Polled($elm$core$Result$Err($elm$http$Http$NetworkError)); break;
      case 'postedNetworkError': message=${PREFIX}UiHttp$Posted($elm$core$Result$Err($elm$http$Http$NetworkError)); break;
      default: throw new Error('unsupported sanitized HTTP fixture input');
    }
    return ${PREFIX}${root}$Transport(message);
  }
};
`;
  insertions.push({ offset: exports[0].index, text: observe });
  insertions.sort((a, b) => a.offset - b.offset);
  let cursor = 0, changed = '', shift = 0;
  for (const item of insertions) {
    changed += original.slice(cursor, item.offset) + item.text;
    item.actualOffset = item.offset + shift;
    shift += item.text.length;
    cursor = item.offset;
  }
  changed += original.slice(cursor);
  let recovered = changed;
  for (const item of [...insertions].reverse()) {
    recovered = recovered.slice(0, item.actualOffset) + recovered.slice(item.actualOffset + item.text.length);
  }
  insist(recovered === original, 'observation changes are not exactly reversible');
  return { changed, insertions: insertions.map(item => ({ originalOffset: item.offset,
    actualOffset: item.actualOffset, offsetUnit: 'UTF16-code-units',
    originalByteOffset: Buffer.byteLength(original.slice(0, item.offset)),
    actualByteOffset: Buffer.byteLength(changed.slice(0, item.actualOffset)),
    insertedBytes: Buffer.byteLength(item.text), sha256: hash(item.text) })) };
}

function listValues(value, label) {
  const values = [];
  while (value && value.$ === '::') {
    insist(Object.keys(value).sort().join(',') === '$,a,b', `${label}: malformed list cell`);
    values.push(value.a); value = value.b;
    insist(values.length <= 10000, `${label}: QA list bound`);
  }
  insist(value && value.$ === '[]' && Object.keys(value).join(',') === '$', `${label}: malformed list terminator`);
  return values;
}
// An ADDITIONAL closed manager/leaf guard; not a claimed Cmd AST serializer.
// Actual Cmd payload functions belong to the private interpreter and require
// separate source-bound runtime XHR/timer/focus qualification (Gemini0510).
// COMPLETE typed descriptions above contain no functions and are never reduced
// to these counts. Unknown managers/taggers/extra command leaves fail closed.
function commandLeaves(bag, api, counts = { Http: 0, Task: 0 }) {
  insist(bag && typeof bag === 'object', 'malformed Cmd bag');
  const keys = Object.keys(bag).sort().join(',');
  if (bag.$ === 2) {
    insist(keys === '$,m', 'unknown Cmd batch fields');
    for (const child of listValues(bag.m, 'Cmd batch')) commandLeaves(child, api, counts);
  } else if (bag.$ === 3) {
    insist(keys === '$,n,o' && typeof bag.n === 'function' &&
      (bag.n === api.transport || bag.n === api.view), 'unknown Cmd map/tagger');
    commandLeaves(bag.o, api, counts);
  } else if (bag.$ === 1) {
    insist(keys === '$,k,l' && ['Http', 'Task'].includes(bag.k), 'unknown Cmd manager/fields');
    counts[bag.k]++;
  } else throw new Error('unknown Cmd bag constructor');
  return counts;
}
function describedLeaves(descriptions) {
  const counts = { Http: 0, Task: 0 };
  for (const description of descriptions) {
    for (const effect of listValues(description.effects, description.module)) {
      if (description.module === 'UiHttp') {
        if (['ReadEvents', 'SendController', 'SendRenderer', 'CancelEvents', 'CancelPost'].includes(effect.$)) counts.Http++;
        else if (effect.$ === 'WakeAfter') counts.Task++;
        else throw new Error('unsupported typed UiHttp effect');
      } else if (description.module === 'HttpMain.effects') {
        if (effect.$ === 'Delay') counts.Task++;
        else insist(effect.$ === 'Publish', 'unsupported applied policy effect');
      } else if (description.module === 'Bar') {
        if (effect.$ === 'ResetStatusViewport') counts.Task++;
        else insist(effect.$ === 'Dispatch', 'unsupported Bar effect');
      } else if (description.module === 'Popup') {
        insist(['Dispatch', 'PreviewCommand', 'PaintRequest'].includes(effect.$), 'unsupported Popup effect');
      } else insist(description.module === 'DesktopPolicy', 'unknown typed description module');
    }
  }
  return counts;
}

function load(original, root) {
  const typed = [];
  const returns = [];
  let initial = null;
  const sentinel = {};
  const noIO = () => { throw new Error('unexpected task/DOM execution in PURE replay; use runtime boundary profile'); };
  const context = { console: { log() {}, warn() {}, error() {} }, setTimeout: noIO,
    clearTimeout: noIO, requestAnimationFrame: noIO, cancelAnimationFrame: noIO };
  context[TYPED_HOOK] = (module, effects) => { typed.push(full({ module, effects })); };
  context[RETURN_HOOK] = (kind, value) => { returns.push(full({ kind, value })); };
  context[INIT_HOOK] = (model, update, subscriptions, command) => {
    initial = { model, update, subscriptions, command };
    throw sentinel;
  };
  vm.createContext(context);
  registerRealm(context);
  const observed = instrument(original, root);
  new vm.Script(observed.changed, { filename: `${root}.readonly-fixture.js` }).runInContext(context, { timeout: WAIT_MS });
  insist(context[API] && context[API].nonoptimized(), 'actual owning root must be NONOPTIMIZED');
  insist(context.Elm && context.Elm[root], 'actual owning root export missing');
  try { context.Elm[root].init({ node: {}, flags: null }); }
  catch (error) { if (error !== sentinel) throw error; }
  insist(initial, 'actual root init was not observed');
  // Stop only this QA init BEFORE stepper/effect-manager setup; retain the
  // actual immutable GIVEN. No reducer/model/authority token was rewritten.
  return { context, typed, returns, initial, observed, api: context[API] };
}
function snapshot(env, state, command) {
  const descriptions = env.typed.splice(0);
  const transportReturns = env.returns.splice(0);
  const actualLeaves = commandLeaves(command, env.api);
  insist(isDeepStrictEqual(actualLeaves, describedLeaves(descriptions)), 'Cmd contains unobserved/missing effects (focus needs its own declared fixture)');
  env.context.__solSubscriptions = env.initial.subscriptions;
  env.context.__solSubscriptionModel = state;
  const subscriptions = vm.runInContext('__solSubscriptions(__solSubscriptionModel)', env.context, { timeout: WAIT_MS });
  return full({ state, subscriptions, descriptions, transportReturns });
}
function run(original, spec) {
  const env = load(original, spec.root);
  let model = env.initial.model;
  const trace = [];
  for (let i = 0; i < spec.steps.length; i++) {
    const step = spec.steps[i];
    let command;
    if (i === 0) {
      insist(step.input.kind === 'init', 'history must start from actual owning init');
      command = env.initial.command;
    } else {
      insist(step.input && typeof step.input.kind === 'string' &&
        Object.keys(step.input).every(key => ['kind', 'body', 'value'].includes(key)) &&
        (!Object.hasOwn(step.input, 'body') || typeof step.input.body === 'string'), 'unsupported fixture input field');
      if (['polledOk', 'postedOk'].includes(step.input.kind)) insist(typeof step.input.body === 'string', 'exact HTTP callback body required');
      else insist(!Object.hasOwn(step.input, 'body'), 'unexpected callback body');
      if (step.input.kind === 'viewAction') {
        insist(Object.hasOwn(step.input, 'value'), 'exact captured action value required');
        full(step.input.value); // reject unsupported fixture data, do not strip fields
      } else insist(!Object.hasOwn(step.input, 'value'), 'unexpected action value');
      env.context.__solInput = step.input;
      env.context.__solModel = model;
      env.context.__solUpdate = env.initial.update;
      const pair = vm.runInContext(`globalThis.${API}.a2(__solUpdate,globalThis.${API}.message(__solInput),__solModel)`, env.context, { timeout: WAIT_MS });
      model = pair.a; command = pair.b;
    }
    const actual = snapshot(env, model, command);
    const expected = full(step.expected);
    if (!isDeepStrictEqual(actual, expected)) {
      const error = new Error(`${spec.name} step ${i}: COMPLETE owning model/subscription/typed descriptions differ`);
      // Retain a counterexample, NEVER use it to populate an expected oracle.
      error.counterexample = { name: spec.name, step: i, input: step.input, actual, expected };
      throw error;
    }
    trace.push(actual);
  }
  return { trace, instrumentation: env.observed.insertions, instrumentedHash: hash(env.observed.changed) };
}
function main() {
  insist(process.argv.length === 7, 'usage: observer.cjs repository HttpMain.plain.js HttpBar.plain.js HttpPopup.plain.js httpbar-literals.cjs');
  const repository = path.resolve(process.argv[2]);
  const paths = Object.fromEntries(['HttpMain', 'HttpBar', 'HttpPopup'].map((name, i) => [name, path.resolve(process.argv[3 + i])]));
  for (const [name, filename] of Object.entries(paths)) {
    const original = fs.readFileSync(filename, 'utf8');
    insist(original.includes(`var ${PREFIX}UiHttp$interpret =`), `${name}: typed UiHttp source patch absent`);
  }
  const manifestPath = path.join(__dirname, 'http-root-cases-manifest.json');
  const manifest = JSON.parse(fs.readFileSync(manifestPath, 'utf8'));
  const { validateFiles, validateCases } = require('./http-root-cases-guard.cjs');
  const oraclePath = path.join(__dirname, 'sol-http-popup-literals-0525.cjs');
  const peerPath = path.resolve(process.argv[6]);
  insist(peerPath === path.join(__dirname, 'httpbar-literals.cjs'), 'required staged peer path differs');
  const fixtureFiles = { base: fs.readFileSync(oraclePath), peer: fs.readFileSync(peerPath),
    policy: fs.readFileSync(path.join(repository, 'implementation/warlock/qa/tea-contract-cases.cjs')) };
  validateFiles(manifest, fixtureFiles);
  const oracle = require(oraclePath);
  insist(oracle.coverage && oracle.coverage.complete === false, 'coverage must remain incomplete');
  const packet = oracle.build(repository);
  const peer = require(peerPath);
  insist(typeof peer.build === 'function', 'peer must export independent build(repository)');
  const supplied = peer.build(repository);
  insist(supplied && Array.isArray(supplied.cases) && supplied.cases.length > 0, 'peer literal cases missing');
  packet.cases.push(...supplied.cases);
  validateCases(manifest, packet.cases);
  const peerSources = [{ path: peerPath, sha256: hash(fixtureFiles.peer) }];
  const results = [];
  for (const spec of packet.cases) {
    const original = fs.readFileSync(paths[spec.root], 'utf8');
    const first = run(original, spec);
    const second = run(original, spec);
    insist(isDeepStrictEqual(first.trace, second.trace), `${spec.name}: deterministic replay differs AFTER literal assertions`);
    results.push({ name: spec.name, root: spec.root, assertedStepsPerRun: spec.steps.length,
      freshRuns: 2, compiledOriginal: hash(original), instrumentedInMemory: first.instrumentedHash,
      reversibleInsertions: first.instrumentation });
  }
  console.log(JSON.stringify({ ok: true, coverage: oracle.coverage, cases: results,
    policyLiteralSource: packet.policyOracle, oracleHash: hash(fs.readFileSync(oraclePath)),
    observerHash: hash(fs.readFileSync(__filename)), manifestHash: hash(fs.readFileSync(manifestPath)), peerSources,
    limits: ['pure replay only: actual root init is observed then stopped before DOM/effect execution',
      'complete immutable models, Sub.none trees and typed effect DATA; opaque Cmd AST is NOT serialized or claimed',
      'Cmd manager/leaf checks are additional guards; source-bound optimized runtime interpreter fixtures still required',
      'actual native host/provider/IME/AT/hardware/resource/release ordering is separate',
      'Root must bind exact production source/input/artifact hashes; runtime file hashes alone do not prove compiler provenance'],
    originalAcceptanceClaim: false }));
}
try { main(); } catch (error) { console.error(JSON.stringify({ ok: false, error: error.message,
  counterexample: error.counterexample || null, originalAcceptanceClaim: false })); process.exitCode = 1; }
