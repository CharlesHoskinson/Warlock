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
  const startup = `var ${PREFIX}UiHttp$${root === 'HttpMain' ? 'controller' : root === 'HttpPopup' ? 'popup' : 'renderer'} =`;
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
  for (const fn of ['updateEffects', 'enqueueEffects', 'enqueueProposalEffects', 'tryEnqueueConsumedEffects', 'stopEffects']) {
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
    if (typeof ${PREFIX}UiHttp$Polled !== 'function' || typeof ${PREFIX}UiHttp$PostedFor !== 'function' || typeof ${PREFIX}UiHttp$RequestId !== 'function'
      || !$elm$http$Http$NetworkError || $elm$http$Http$NetworkError.$ !== 'NetworkError') {
      throw new Error('actual public HTTP message constructors missing/changed');
    }
    var message;
    switch(input.kind) {
      case 'viewAction':
        ${root === 'HttpMain' ? "throw new Error('no renderer View in HttpMain');" : `return ${PREFIX}${root}$View(${PREFIX}${root === 'HttpBar' ? 'Bar' : 'Popup'}$Action(_Json_wrap(input.value)));`}
        break;
      case 'viewNativeQuarantine':
        ${root !== 'HttpPopup' ? "throw new Error('direct native control is HttpPopup QA-only');" : `return ${PREFIX}HttpPopup$View({$:'NativeQuarantine', a:_Json_wrap(input.value)});`}
        break;
      case 'poll': message=${PREFIX}UiHttp$Poll; break;
      case 'polledOk': message=${PREFIX}UiHttp$Polled($elm$core$Result$Ok(input.body)); break;
      case 'postedOk': message={$:'Posted',a:$elm$core$Result$Ok(input.body)}; break;
      case 'postedForNetworkError':
      case 'postedForOk':
        if (!['1','2'].includes(input.requestId) || !['ControllerCommit','RendererAction','PopupProposal'].includes(input.requestKind)) throw new Error('undeclared independent callback identity');
        var kind = input.requestKind === 'ControllerCommit' ? ${PREFIX}UiHttp$ControllerCommit : input.requestKind === 'PopupProposal' ? ${PREFIX}UiHttp$PopupProposal : ${PREFIX}UiHttp$RendererAction;
        message=A3(${PREFIX}UiHttp$PostedFor,${PREFIX}UiHttp$RequestId(${PREFIX}UInt64$Counter(input.requestId)),kind,input.kind === 'postedForOk' ? $elm$core$Result$Ok(input.body) : $elm$core$Result$Err($elm$http$Http$NetworkError));
        break;
      case 'polledNetworkError': message=${PREFIX}UiHttp$Polled($elm$core$Result$Err($elm$http$Http$NetworkError)); break;
      case 'postedNetworkError': message={$:'Posted',a:$elm$core$Result$Err($elm$http$Http$NetworkError)}; break;
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
        if (effect.$ === 'SendRequest') {
          insist(effect.a && effect.a.$ === 'RequestId' && effect.a.a && effect.a.a.$ === 'Counter' && Object.keys(effect.a).sort().join(',') === '$,a' && Object.keys(effect.a.a).sort().join(',') === '$,a' && typeof effect.a.a.a === 'string' && /^[1-9][0-9]{0,19}$/.test(effect.a.a.a) && BigInt(effect.a.a.a) <= 18446744073709551615n && effect.b && ['ControllerCommit','RendererAction','PopupProposal'].includes(effect.b.$), 'undeclared joined HTTP request metadata');
          counts.Http++;
        } else if (['ReadEvents', 'SendController', 'SendRenderer', 'CancelEvents', 'CancelPost'].includes(effect.$)) counts.Http++;
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
function snapshot(env, state, command, where = null) {
  const descriptions = env.typed.splice(0);
  const transportReturns = env.returns.splice(0);
  const actualLeaves = commandLeaves(command, env.api);
  describedLeaves(descriptions); // Validate all constructed typed effects; wrappers can discard a constructed Cmd.
  env.context.__solSubscriptions = env.initial.subscriptions;
  env.context.__solSubscriptionModel = state;
  const subscriptions = vm.runInContext('__solSubscriptions(__solSubscriptionModel)', env.context, { timeout: WAIT_MS });
  return full({ state, subscriptions, descriptions, transportReturns, commandLeaves:actualLeaves });
}
function run(original, spec) {
  const env = load(original, spec.root);
  let model = env.initial.model;
  const trace = [];
  for (let i = 0; i < spec.steps.length; i++) {
    const step = spec.steps[i];
    insist(step.expected && step.expected.commandLeaves && Object.keys(step.expected.commandLeaves).sort().join(',')==='Http,Task' &&
      ['Http','Task'].every(key=>Number.isSafeInteger(step.expected.commandLeaves[key])&&step.expected.commandLeaves[key]>=0), 'independent returned command literal missing/invalid');
    let command;
    if (i === 0) {
      insist(step.input.kind === 'init' || (spec.root === 'HttpPopup' && step.input.kind === 'given'), 'history must start from actual owning init or Popup QA given');
      if (step.input.kind === 'given') {
        insist(Object.keys(step.input).length === 1, 'malformed Popup QA given');
        env.context.__solGivenJson = JSON.stringify(full(step.expected.state));
        model = vm.runInContext('JSON.parse(__solGivenJson)', env.context, {timeout:WAIT_MS});
        env.typed.splice(0); env.returns.splice(0);
        command = {$:2,m:{$:'[]'}};
      } else command = env.initial.command;
    } else {
      insist(step.input && typeof step.input.kind === 'string' &&
        Object.keys(step.input).every(key => ['kind', 'body', 'value', 'requestId', 'requestKind'].includes(key)) &&
        (!Object.hasOwn(step.input, 'body') || typeof step.input.body === 'string'), 'unsupported fixture input field');
      if (['polledOk', 'postedOk', 'postedForOk'].includes(step.input.kind)) insist(typeof step.input.body === 'string', 'exact HTTP callback body required');
      else insist(!Object.hasOwn(step.input, 'body'), 'unexpected callback body');
      if (['viewAction', 'viewNativeQuarantine'].includes(step.input.kind)) {
        insist(Object.hasOwn(step.input, 'value'), 'exact captured action value required');
        full(step.input.value); // reject unsupported fixture data, do not strip fields
        if (step.input.kind !== 'viewAction') insist(spec.root === 'HttpPopup' &&
          JSON.stringify(step.input.value).length <= 65536, 'invalid bounded Popup QA control');
      } else insist(!Object.hasOwn(step.input, 'value'), 'unexpected action value');
      env.context.__solInput = step.input;
      env.context.__solModel = model;
      env.context.__solUpdate = env.initial.update;
      const pair = vm.runInContext(`globalThis.${API}.a2(__solUpdate,globalThis.${API}.message(__solInput),__solModel)`, env.context, { timeout: WAIT_MS });
      model = pair.a; command = pair.b;
    }
    const actual = snapshot(env, model, command, {name:spec.name,root:spec.root,step:i,input:full(step.input)});
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
// QA-only joined replay. The peer provides every expected state and packet;
// the values below only enforce the source-reviewed Owner projection relation.
// This does not execute Haskell Owner or claim owner admission/native delivery.
function runJoined(originals, spec, onStep = () => {}) {
  insist(spec.root === 'HttpJoined' && Array.isArray(spec.steps), 'invalid joined history');
  const envs = Object.fromEntries(['HttpMain', 'HttpPopup'].map(root => [root, load(originals[root], root)]));
  const models = {}, trace = [], commits = new Map();
  const pending = [];
  for (let i = 0; i < spec.steps.length; i++) {
    onStep(i);
    const step = spec.steps[i], root = step.root, env = envs[root];
    insist(env && step.input && typeof step.input.kind === 'string', 'invalid joined root/input');
    // Check linked delivery order before a reducer or literal mismatch can
    // conceal the ordering rejection being exercised by its counterfactual.
    if (step.join && ['presentation', 'announcements'].includes(step.join.kind)) {
      const head = pending[0];
      insist(root === 'HttpPopup' && step.input.kind === 'polledOk' && head &&
        pending.length === 1 && commits.has(step.join.commitStep) &&
        head.index === step.join.commitStep && head.next === step.join.kind,
        'renderer delivery out of order');
    }
    let command;
    if (step.input.kind === 'given') {
      insist(!Object.hasOwn(models, root) && Object.keys(step.input).length === 1, 'duplicate or malformed joined given');
      // Independent source literal in the pinned fixture, never an observed value.
      // Hydrate only plain JSON data inside the root's own realm.
      const literal = full(step.expected.state);
      env.context.__solGivenJson = JSON.stringify(literal);
      models[root] = vm.runInContext('JSON.parse(__solGivenJson)', env.context, { timeout: WAIT_MS });
      env.typed.splice(0); env.returns.splice(0);
      command = { $: 2, m: { $: '[]' } };
    } else if (step.input.kind === 'init') {
      insist(!Object.hasOwn(models, root) && Object.keys(step.input).length === 1, 'duplicate or malformed joined init');
      models[root] = env.initial.model; command = env.initial.command;
    } else {
      insist(Object.hasOwn(models, root), 'joined root not initialized');
      const allowedInput = step.input.kind === 'postedForOk' ? ['kind','body','requestId','requestKind'] : ['kind','body','value'];
      insist(Object.keys(step.input).every(key => allowedInput.includes(key)), 'unsupported joined input');
      if (['polledOk', 'postedOk', 'postedForOk'].includes(step.input.kind)) insist(typeof step.input.body === 'string', 'exact callback body required');
      else insist(!Object.hasOwn(step.input, 'body'), 'unexpected callback body');
      if (step.input.kind === 'viewAction') { insist(Object.hasOwn(step.input, 'value'), 'missing action'); full(step.input.value); }
      else insist(!Object.hasOwn(step.input, 'value'), 'unexpected action');
      env.context.__solInput = step.input; env.context.__solModel = models[root]; env.context.__solUpdate = env.initial.update;
      const pair = vm.runInContext(`globalThis.${API}.a2(__solUpdate,globalThis.${API}.message(__solInput),__solModel)`, env.context, { timeout: WAIT_MS });
      models[root] = pair.a; command = pair.b;
    }
    const actual = snapshot(env, models[root], command), expected = full(step.expected);
    if (!isDeepStrictEqual(actual, expected)) {
      const error = new Error(`${spec.name} step ${i}: joined full literal mismatch`);
      error.counterexample = { name: spec.name, step: i, root, input: step.input, actual, expected };
      throw error;
    }
    const sends = actual.descriptions.flatMap(d => d.module === 'UiHttp'
      ? listValues(d.effects, 'UiHttp').filter(x => x.$ === 'SendRequest' && x.b.$ === 'ControllerCommit').map(x => x.c.a) : []);
    if (step.join && step.join.kind === 'commit') {
      insist(root === 'HttpMain' && sends.length === 1 && pending.length === 0, 'joined commit ordering');
      const commit = full(step.join.commit), selected = full(step.join.selected);
      insist(isDeepStrictEqual(sends[0], commit), 'actual controller commit differs from independent complete literal');
      const p = commit.projection;
      insist(commit.viewProtocol === 1 && commit.kind === 'view-commit' && p && p.viewProtocol === 1 && p.kind === 'view-frame', 'invalid commit header');
      insist(isDeepStrictEqual(p.views, selected === null ? [] : [selected]) &&
        (p.focusOwner === null || isDeepStrictEqual(p.focusOwner, selected)) &&
        (p.popupOwner === null || isDeepStrictEqual(p.popupOwner, selected)), 'projection custody differs');
      insist(p.frame && p.frame.surfaceProtocol === 2, 'invalid projection frame');
      commits.set(i, { commit, selected }); pending.push({ index: i, next: 'presentation' });
    } else insist(sends.length === 0, 'unbound controller commit');
    if (step.join && ['presentation', 'announcements'].includes(step.join.kind)) {
      insist(root === 'HttpPopup' && step.input.kind === 'polledOk' && pending.length === 1, 'invalid joined renderer delivery');
      const head = pending[0], entry = commits.get(step.join.commitStep);
      insist(entry && head.index === step.join.commitStep && head.next === step.join.kind, 'renderer delivery out of order');
      const p = entry.commit.projection, f = p.frame;
      const recipient = { scope: entry.selected, surface: 'popup' };
      const payload = step.join.kind === 'presentation' ? f : {
        announcementProtocol: 1, kind: 'announcement-projection', recipient,
        announcer: p.announcer, publication: f.publication, lease: f.lease,
        message: p.announcement, deliver: isDeepStrictEqual(p.announcer, full(recipient))
      };
      insist(isDeepStrictEqual(full(JSON.parse(step.input.body)), full({bridgeProtocol:1, kind:step.join.kind, payload})), 'renderer packet does not match committed projection');
      if (head.next === 'presentation') head.next = 'announcements'; else pending.shift();
    } else {
      if (step.join) insist(step.join.kind === 'commit', 'unknown joined assertion');
      if (root === 'HttpPopup' && step.input.kind === 'polledOk' && step.input.body !== '') {
        const packet = JSON.parse(step.input.body);
        insist(!['presentation', 'announcements'].includes(packet.kind), 'unbound renderer event');
      }
    }
    trace.push(actual);
  }
  insist(Object.hasOwn(models, 'HttpMain') && Object.hasOwn(models, 'HttpPopup') && commits.size > 0 && pending.length === 0, 'incomplete joined history');
  return {trace, instrumentation:Object.fromEntries(Object.entries(envs).map(([root, env]) => [root, env.observed.insertions])),
    instrumentedHash:Object.fromEntries(Object.entries(envs).map(([root, env]) => [root, hash(env.observed.changed)]))};
}

function main() {
  insist(process.argv.length === 6, 'usage: observer.cjs repository HttpMain.plain.js HttpBar.plain.js HttpPopup.plain.js');
  const fixtureDirectory = path.join(__dirname, 'parents');
  const binding=JSON.parse(fs.readFileSync(path.join(__dirname,'full-manifest.json')));
  const checkedRepository=path.resolve(process.argv[2]);
  for(const [file,sha]of Object.entries(binding.bundle))insist(hash(fs.readFileSync(path.join(__dirname,file)))===sha,'active bundle digest: '+file);
  for(const [file,sha]of Object.entries(binding.target))insist(hash(fs.readFileSync(path.join(checkedRepository,file)))===sha,'target source digest: '+file);

  const repository = path.resolve(process.argv[2]);
  const paths = Object.fromEntries(['HttpMain', 'HttpBar', 'HttpPopup'].map((name, i) => [name, path.resolve(process.argv[3 + i])]));
  for (const [name, filename] of Object.entries(paths)) {
    const original = fs.readFileSync(filename, 'utf8');
    insist(original.includes(`var ${PREFIX}UiHttp$interpret =`), `${name}: typed UiHttp source patch absent`);
  }
  const manifestPath = path.join(fixtureDirectory, 'http-root-cases-manifest.json');
  const manifest = JSON.parse(fs.readFileSync(manifestPath, 'utf8'));
  const { validateFiles, validateCases, validateJoined, validatePopupControl } = require('./parents/http-root-cases-guard.cjs');
  const oraclePath = path.join(fixtureDirectory, 'sol-http-popup-literals-0525.cjs');
  const peerPath = path.join(fixtureDirectory,'httpbar-literals.cjs');
  insist(peerPath === path.join(fixtureDirectory, 'httpbar-literals.cjs'), 'required staged peer path differs');
  const joinedPath = path.join(fixtureDirectory, 'joined-control-literals.cjs');
  const closedPath = path.join(fixtureDirectory, 'closed-topology-after-dismiss-literals.cjs');
  const popupControlPath = path.join(fixtureDirectory, 'http-popup-control-literals.cjs');
  const historical=(name)=>fs.readFileSync(path.join(repository,'implementation/warlock/qa',name));
  const fixtureFiles={base:historical('sol-http-popup-literals-0525.cjs'),peer:historical('httpbar-literals.cjs'),joined:historical('joined-control-literals.cjs'),closedTopology:historical('closed-topology-after-dismiss-literals.cjs'),popupControl:historical('http-popup-control-literals.cjs'),policy:historical('tea-contract-cases.cjs')};
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
  const migrated = require('./full-literals.cjs').build(repository);
  insist(isDeepStrictEqual(packet.cases,migrated.originals),'base peer originals changed');
  packet.cases=migrated.cases;
  validateCases(manifest,packet.cases);
  const control = require(popupControlPath);
  insist(control.schema === 1 && typeof control.build === 'function', 'popup control literal schema mismatch');
  const controlPacket = control.build(repository);
  insist(controlPacket && controlPacket.coverage && controlPacket.coverage.complete === false &&
    controlPacket.coverage.originalAccepted === false && controlPacket.coverage.nativeAccepted === false &&
    Array.isArray(controlPacket.cases), 'popup control literal missing cases or incomplete coverage');
  validatePopupControl(manifest, controlPacket.cases);
  insist(isDeepStrictEqual(controlPacket.cases,migrated.controlOriginals),'control originals changed');
  controlPacket.cases=migrated.controlCases;
  validatePopupControl(manifest,controlPacket.cases);
  const popupControlResults = [];
  for (const spec of controlPacket.cases) {
    insist(spec.root === 'HttpPopup', 'popup control belongs to HttpPopup only');
    const original = fs.readFileSync(paths.HttpPopup, 'utf8');
    const first = run(original, spec), second = run(original, spec);
    insist(isDeepStrictEqual(first.trace, second.trace), `${spec.name}: nondeterministic popup control replay`);
    popupControlResults.push({name:spec.name, root:spec.root, assertedStepsPerRun:spec.steps.length,
      freshRuns:2, compiledOriginal:hash(original), instrumentedInMemory:first.instrumentedHash,
      reversibleInsertions:first.instrumentation});
  }
  const controlNegatives = [];
  for (const [name, mutation] of [
    ['HttpPopup-action-sends-renderer-then-settles', state => { state.http.a.active = {$:'Nothing'}; }],
    ['HttpPopup-native-event-gateway-rejected', state => { state.http.a.failed = {$:'Nothing'}; }],
    ['HttpPopup-synthetic-quarantine-preview-command-refused', state => { state.http.a.failed = {$:'Nothing'}; }],
  ]) {
    const original = fs.readFileSync(paths.HttpPopup, 'utf8');
    const source = controlPacket.cases.find(c => c.name === name);
    insist(source && source.steps.length > 1, 'popup control negative source missing');
    const spec = JSON.parse(JSON.stringify(source));
    mutation(spec.steps[1].expected.state);
    let rejected = false;
    try { run(original, spec); } catch (error) {
      const reason = `${name} step 1: COMPLETE owning model/subscription/typed descriptions differ`;
      insist(error.message === reason && error.counterexample && error.counterexample.step === 1,
        `popup control negative failed for unrelated reason: ${name}: ${error.message}`);
      controlNegatives.push({name,reason,step:1}); rejected = true;
    }
    insist(rejected, `popup control negative did not reject: ${name}`);
  }
  const joined = require(joinedPath);
  insist(joined.schema === 1 && typeof joined.build === 'function', 'joined literal schema mismatch');
  const migratedJoined=require('./literals.cjs').build(repository);
  const joinedPacket={...joined.build(repository),cases:[migratedJoined.cases[0]]};
  insist(joinedPacket && joinedPacket.coverage && joinedPacket.coverage.complete === false &&
    joinedPacket.coverage.originalAccepted === false && joinedPacket.coverage.nativeAccepted === false &&
    Array.isArray(joinedPacket.cases), 'joined literal missing cases or incomplete coverage');
  const closed = require(closedPath);
  insist(closed.schema === 1 && typeof closed.build === 'function', 'closed topology literal schema mismatch');
  const closedPacket={...closed.build(repository),cases:[migratedJoined.cases[1]]};
  insist(closedPacket && closedPacket.coverage && closedPacket.coverage.complete === false &&
    closedPacket.coverage.originalAccepted === false && closedPacket.coverage.nativeAccepted === false &&
    Array.isArray(closedPacket.cases), 'closed topology literal missing cases or incomplete coverage');
  validateJoined(manifest, joinedPacket.cases.concat(closedPacket.cases));
  insist(isDeepStrictEqual(full(closedPacket.cases[0].steps.slice(0, 5)), full(joinedPacket.cases[0].steps)), 'dismiss prefix differs from tested case');
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
  const originals = Object.fromEntries(['HttpMain', 'HttpPopup'].map(root => [root, fs.readFileSync(paths[root], 'utf8')]));
  const joinedSpec = joinedPacket.cases[0];
  const firstJoined = runJoined(originals, joinedSpec), secondJoined = runJoined(originals, joinedSpec);
  insist(isDeepStrictEqual(firstJoined.trace, secondJoined.trace), 'joined replay nondeterministic after literal assertions');
  // Mutate independent inputs after the positive literal replay; never turn
  // observed output into an expectation. Each counterfactual must be refused.
  const clone = value => JSON.parse(JSON.stringify(value));
  const negativeRejections = [];
  function rejectJoined(name, mutate, reason, mismatchStep) {
    const spec = clone(joinedSpec);
    mutate(spec);
    let rejected = false;
    try { runJoined(originals, spec); } catch (error) {
      const expected = mismatchStep === undefined ? reason
        : `${spec.name} step ${mismatchStep}: joined full literal mismatch`;
      insist(error.message === expected && (mismatchStep === undefined ||
        error.counterexample && error.counterexample.step === mismatchStep),
        `joined negative failed for an unrelated reason: ${name}: ${error.message}`);
      negativeRejections.push({name, reason: error.message,
        step: mismatchStep === undefined ? null : mismatchStep});
      rejected = true;
    }
    insist(rejected, `joined negative did not reject: ${name}`);
  }
  rejectJoined('given-mutated', spec => { spec.steps[0].expected.state.policy.controller.a.controller.a.desktop.open = false; }, null, 2);
  rejectJoined('given-omitted', spec => { spec.steps.splice(0, 1); }, 'joined root not initialized');
  rejectJoined('commit-altered', spec => { spec.steps[2].join.commit.projection.frame.mode = 'applications'; }, 'actual controller commit differs from independent complete literal');
  rejectJoined('projection-reordered', spec => { [spec.steps[3], spec.steps[4]] = [spec.steps[4], spec.steps[3]]; }, 'renderer delivery out of order');
  rejectJoined('projection-duplicated', spec => { spec.steps.splice(4, 0, clone(spec.steps[3])); }, 'renderer delivery out of order');
  rejectJoined('projection-missing', spec => { spec.steps.pop(); }, 'incomplete joined history');
  const joinedResult = {name: joinedSpec.name, root: joinedSpec.root, assertedStepsPerRun: joinedSpec.steps.length,
    freshRuns: 2, compiledOriginal: Object.fromEntries(Object.entries(originals).map(([root, original]) => [root, hash(original)])),
    instrumentedInMemory: firstJoined.instrumentedHash, reversibleInsertions: firstJoined.instrumentation,
    negatives: ['given-mutated', 'given-omitted', 'commit-altered', 'projection-reordered', 'projection-duplicated', 'projection-missing'],
    negativeRejections,
    literalHash: hash(fixtureFiles.joined)};
  const closedSpec = closedPacket.cases[0];
  const firstClosed = runJoined(originals, closedSpec), secondClosed = runJoined(originals, closedSpec);
  insist(isDeepStrictEqual(firstClosed.trace, secondClosed.trace), 'closed topology replay nondeterministic after literal assertions');
  const closedRejections = [];
  function rejectClosed(name, mutate, reason, expectedStep, mismatch) {
    const spec = clone(closedSpec);
    mutate(spec);
    let step = null, rejected = false;
    try { runJoined(originals, spec, i => { step = i; }); } catch (error) {
      const expected = mismatch ? `${spec.name} step ${expectedStep}: joined full literal mismatch` : reason;
      insist(step === expectedStep && error.message === expected && (!mismatch ||
        error.counterexample && error.counterexample.step === expectedStep),
        `closed topology negative failed for an unrelated reason: ${name}: step ${step}: ${error.message}`);
      closedRejections.push({name, reason:error.message, step}); rejected = true;
    }
    insist(rejected, `closed topology negative did not reject: ${name}`);
  }
  rejectClosed('second-commit-altered', spec => { spec.steps[6].join.commit.projection.frame.publication = '10'; },
    'actual controller commit differs from independent complete literal', 6, false);
  rejectClosed('topology-before-post-settle', spec => { [spec.steps[5], spec.steps[6]] = [spec.steps[6], spec.steps[5]]; }, null, 5, true);
  rejectClosed('duplicate-revision-changed', spec => { const input = JSON.parse(spec.steps[10].input.body); input.payload.revision = '3'; spec.steps[10].input.body = JSON.stringify(input); }, null, 10, true);
  rejectClosed('whole-model-altered', spec => { spec.steps[9].expected.state.policy.controller.a.revision.a = '99'; }, null, 9, true);
  const joinedTopology = {name:closedSpec.name, root:closedSpec.root, assertedStepsPerRun:closedSpec.steps.length, freshRuns:2,
    compiledOriginal:Object.fromEntries(Object.entries(originals).map(([root, original]) => [root, hash(original)])),
    instrumentedInMemory:firstClosed.instrumentedHash, reversibleInsertions:firstClosed.instrumentation,
    negativeRejections:closedRejections, literalHash:hash(fixtureFiles.closedTopology)};
  console.log(JSON.stringify({ ok: true, coverage: oracle.coverage, cases: results,
    joined: joinedResult, joinedTopology, popupControl:{cases:popupControlResults, negativeRejections:controlNegatives, literalHash:hash(fixtureFiles.popupControl)},
    policyLiteralSource: packet.policyOracle, oracleHash: hash(fs.readFileSync(oraclePath)),
    observerHash: hash(fs.readFileSync(__filename)), manifestHash: hash(fs.readFileSync(manifestPath)), peerSources,
    limits: ['pure replay only: actual root init is observed then stopped before DOM/effect execution',
      'complete immutable models, Sub.none trees and typed effect DATA; opaque Cmd AST is NOT serialized or claimed',
      'Cmd manager/leaf checks are additional guards; source-bound optimized runtime interpreter fixtures still required',
      'actual native host/provider/IME/AT/hardware/resource/release ordering is separate',
      'Root must bind exact production source/input/artifact hashes; runtime file hashes alone do not prove compiler provenance'],
    originalAcceptanceClaim: false }));
}
if (require.main === module) {
  try { main(); } catch (error) { console.error(JSON.stringify({ ok: false, error: error.message,
    counterexample: error.counterexample || null, originalAcceptanceClaim: false })); process.exitCode = 1; }
} else module.exports = {run,runJoined};
