'use strict';
// QA ONLY, ROOT EXECUTION ONLY. Ninth-root compiled-bundle observer for
// canonical unmodified site/src/SiteMain.elm (f05a3768...).
// Observes both pure owning-root init/update/subscriptions + typed Dom.focus
// descriptions AND live fake-DOM Browser.element keyboard focus + TabFocusSettled
// with zero recurring demand. Not native Omarchy or GUI acceptance.

const fs = require('node:fs');
const path = require('node:path');
const vm = require('node:vm');
const crypto = require('node:crypto');
const { isDeepStrictEqual } = require('node:util');

const WAIT_MS = 10000;
const CANONICAL_SITE_MAIN_SHA256 =
  'f05a3768eb4573161544099917ce009f8df7eb57b8c9408f5266001980cafcfb';
const CANONICAL_SITE_ELM_JSON_SHA256 =
  'ffe9bc4f6811166a7bbafca49540bf7b8af214118dd9aff2f4707890eb9824dc';
const REVIEWED_LITERALS_SHA256 =
  '04151053b079b4dba16656d71680d8eec9ebed709285c695e8270f3e57478cb3';

const hash = data => crypto.createHash('sha256').update(data).digest('hex');
function insist(condition, message) {
  if (!condition) throw new Error(message);
}

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
    insist(
      after &&
        ['value', 'get', 'set', 'writable', 'enumerable', 'configurable'].every(field =>
          Object.is(before[field], after[field])
        ),
      `${where}: changed intrinsic prototype member`
    );
  }
}
registerPrototype(Object.prototype, 'object');
registerPrototype(Array.prototype, 'array');

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
      insist(
        keys.length === value.length && keys.every((key, i) => key === String(i)),
        `${where}: sparse or extended array`
      );
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
      Object.defineProperty(out, key, {
        value: full(d.value, `${where}.${key}`, active),
        enumerable: true,
      });
    }
    return out;
  } finally {
    active.delete(value);
  }
}

function validateFiles(manifest, files) {
  insist(
    manifest &&
      manifest.schema === 1 &&
      manifest.requirement === 'ELM-TEA-004' &&
      manifest.scenario === 'tea-subscriptions' &&
      manifest.coverageComplete === false &&
      manifest.originalAcceptanceClaim === false &&
      manifest.fakeDomExpectedTransitions === 10,
    'invalid SiteMain manifest identity or acceptance'
  );
  for (const name of ['siteMain', 'siteElmJson', 'literals']) {
    insist(Buffer.isBuffer(files[name]) && files[name].length > 0, `${name}: missing or empty fixture`);
    insist(
      manifest.fixtures &&
        manifest.fixtures[name] &&
        hash(files[name]) === manifest.fixtures[name].sha256,
      `${name}: fixture digest mismatch`
    );
  }
  insist(
    manifest.fixtures.siteMain.file === 'site/src/SiteMain.elm' &&
      manifest.fixtures.siteMain.sha256 === CANONICAL_SITE_MAIN_SHA256,
    'required canonical SiteMain.elm pin changed'
  );
  insist(
    manifest.fixtures.siteElmJson.file === 'site/elm.json' &&
      manifest.fixtures.siteElmJson.sha256 === CANONICAL_SITE_ELM_JSON_SHA256,
    'required canonical site/elm.json pin changed'
  );
  insist(
    manifest.fixtures.literals.file === 'sitemain-root-literals.cjs' &&
      manifest.fixtures.literals.sha256 === REVIEWED_LITERALS_SHA256,
    'required reviewed sitemain-root-literals.cjs pin changed'
  );
}

function validateCases(manifest, cases, fakeDomExpectedTrace) {
  insist(
    Array.isArray(manifest.cases) && manifest.cases.length === 4 && Array.isArray(cases),
    'SiteMain case inventory missing'
  );
  const actual = cases.map(c => ({
    name: c.name,
    root: c.root,
    steps: Array.isArray(c.steps) ? c.steps.length : -1,
  }));
  insist(new Set(actual.map(c => c.name)).size === actual.length, 'duplicate case name');
  insist(isDeepStrictEqual(actual, manifest.cases), 'ordered case inventory differs from reviewed manifest');
  insist(
    Array.isArray(fakeDomExpectedTrace) &&
      fakeDomExpectedTrace.length === manifest.fakeDomExpectedTransitions,
    'fake-DOM expected transition count differs'
  );
}

const INIT_HOOK = '__siteMainInitialV1';
const STEP_HOOK = '__siteMainStepV1';
const TYPED_HOOK = '__siteMainTypedV1';
const API = '__siteMainApiV1';
const PREFIX = '$author$project$SiteMain$';

function instrument(original) {
  insist(typeof original === 'string' && original.length > 0, 'empty SiteMain bundle');
  insist(
    ![INIT_HOOK, STEP_HOOK, TYPED_HOOK, API].some(name => original.includes(name)),
    'SiteMain observer already present'
  );
  insist(
    original.includes("var _List_Nil = { $: '[]' };"),
    'SiteMain bundle must use non-optimized Elm 0.19 List ABI'
  );
  insist(
    !original.includes('$elm$browser$Browser$Events$onAnimationFrame') &&
      !original.includes('FlushPendingFocus') &&
      !original.includes('$author$project$SiteBetaStatus$'),
    'rejected animated or mutated SiteMain bundle'
  );
  for (const requiredSymbol of [
    `var ${PREFIX}init =`,
    `var ${PREFIX}update =`,
    `var ${PREFIX}main =`,
    'var $elm$browser$Browser$Dom$focus =',
    'var $elm$core$Task$attempt =',
  ]) {
    insist(original.includes(requiredSymbol), `missing required SiteMain symbol: ${requiredSymbol}`);
  }
  const initMatches = [...original.matchAll(/var\s+model\s*=\s*initPair\.a\s*;/g)];
  insist(initMatches.length === 1, 'unrecognized actual _Platform_initialize init layout');
  const stepMatches = [...original.matchAll(/var\s+pair\s*=\s*A2\(\s*update\s*,\s*msg\s*,\s*model\s*\)\s*;/g)];
  insist(stepMatches.length === 1, 'unrecognized actual _Platform_initialize sendToApp layout');
  const exportMatches = [...original.matchAll(/\n[ \t]*_Platform_export\(/g)];
  insist(exportMatches.length === 1, 'actual program export layout changed');

  const insertions = [
    {
      offset: initMatches[0].index + initMatches[0][0].length,
      text: `\nglobalThis.${INIT_HOOK}(model,update,subscriptions,initPair.b);\n`,
    },
    {
      offset: stepMatches[0].index + stepMatches[0][0].length,
      text: `\nglobalThis.${STEP_HOOK}(msg,pair.a,subscriptions(pair.a),pair.b);\n`,
    },
    {
      offset: exportMatches[0].index,
      text: `
var __siteMainOrigDomFocus = $elm$browser$Browser$Dom$focus;
var __siteMainTaskMeta = new WeakMap();
$elm$browser$Browser$Dom$focus = function(domId) {
  var task = __siteMainOrigDomFocus(domId);
  if (task && typeof task === 'object') {
    __siteMainTaskMeta.set(task, { task: 'Browser.Dom.focus', domId: domId });
  }
  return task;
};
var __siteMainOrigTaskAttempt = $elm$core$Task$attempt;
$elm$core$Task$attempt = F2(function(toMsg, task) {
  var meta = (task && typeof task === 'object' && __siteMainTaskMeta.get(task)) || null;
  if (!meta || meta.task !== 'Browser.Dom.focus' || typeof meta.domId !== 'string') {
    throw new Error('unrecognized Task.attempt task in SiteMain');
  }
  globalThis.${TYPED_HOOK}({
    effect: 'Task.attempt',
    task: meta.task,
    domId: meta.domId,
    onOk: toMsg($elm$core$Result$Ok(_Utils_Tuple0)),
    onNotFound: toMsg($elm$core$Result$Err($elm$browser$Browser$Dom$NotFound(meta.domId)))
  });
  return A2(__siteMainOrigTaskAttempt, toMsg, task);
});
globalThis.${API} = {
  nonoptimized: function() { return _Utils_Tuple2(0, 0).$ === '#2'; },
  a2: A2,
  message: function(input) {
    var themes = {
      ThemeNight: ${PREFIX}ThemeNight,
      ThemeDawn: ${PREFIX}ThemeDawn,
      ThemeHighContrast: ${PREFIX}ThemeHighContrast
    };
    var surfaces = {
      SurfaceTaskbar: ${PREFIX}SurfaceTaskbar,
      SurfaceLauncher: ${PREFIX}SurfaceLauncher,
      SurfaceSwitcher: ${PREFIX}SurfaceSwitcher,
      SurfaceTaskView: ${PREFIX}SurfaceTaskView,
      SurfaceSnap: ${PREFIX}SurfaceSnap,
      SurfaceNotifications: ${PREFIX}SurfaceNotifications,
      SurfaceSettings: ${PREFIX}SurfaceSettings,
      SurfaceFiles: ${PREFIX}SurfaceFiles
    };
    var categories = {
      CategoryAll: ${PREFIX}CategoryAll,
      CategoryWindows: ${PREFIX}CategoryWindows,
      CategoryAppsFiles: ${PREFIX}CategoryAppsFiles,
      CategorySystem: ${PREFIX}CategorySystem
    };
    var samples = {
      SampleObserved: ${PREFIX}SampleObserved,
      SamplePending: ${PREFIX}SamplePending,
      SampleUnknown: ${PREFIX}SampleUnknown,
      SampleRefused: ${PREFIX}SampleRefused
    };
    switch (input.kind) {
      case 'KeyboardStepSpotlight':
        return ${PREFIX}KeyboardStepSpotlight(input.delta);
      case 'KeyboardJumpSpotlight':
        if (!surfaces[input.surface]) throw new Error('unknown SurfaceId: ' + input.surface);
        return ${PREFIX}KeyboardJumpSpotlight(surfaces[input.surface]);
      case 'TabFocusSettledOk':
        if (!surfaces[input.surface]) throw new Error('unknown SurfaceId: ' + input.surface);
        return A3(${PREFIX}TabFocusSettled, input.seq, surfaces[input.surface], $elm$core$Result$Ok(_Utils_Tuple0));
      case 'TabFocusSettledNotFound':
        if (!surfaces[input.surface]) throw new Error('unknown SurfaceId: ' + input.surface);
        return A3(${PREFIX}TabFocusSettled, input.seq, surfaces[input.surface], $elm$core$Result$Err($elm$browser$Browser$Dom$NotFound(input.domId)));
      case 'StepSpotlight':
        return ${PREFIX}StepSpotlight(input.delta);
      case 'SelectSpotlight':
        if (!surfaces[input.surface]) throw new Error('unknown SurfaceId: ' + input.surface);
        return ${PREFIX}SelectSpotlight(surfaces[input.surface]);
      case 'ToggleMobileNav':
        return ${PREFIX}ToggleMobileNav;
      case 'CloseMobileNav':
        return ${PREFIX}CloseMobileNav;
      case 'SelectTheme':
        if (!themes[input.theme]) throw new Error('unknown AppearanceTheme: ' + input.theme);
        return ${PREFIX}SelectTheme(themes[input.theme]);
      case 'ToggleMotion':
        return ${PREFIX}ToggleMotion;
      case 'SelectCategory':
        if (!categories[input.category]) throw new Error('unknown SurfaceCategory: ' + input.category);
        return ${PREFIX}SelectCategory(categories[input.category]);
      case 'ToggleWindowFocused':
        return ${PREFIX}ToggleWindowFocused;
      case 'ToggleActiveApplication':
        return ${PREFIX}ToggleActiveApplication;
      case 'ToggleSwitcherCandidate':
        return ${PREFIX}ToggleSwitcherCandidate;
      case 'SelectOutcomeSample':
        if (!samples[input.sample]) throw new Error('unknown OutcomeSample: ' + input.sample);
        return ${PREFIX}SelectOutcomeSample(samples[input.sample]);
      default:
        throw new Error('unsupported SiteMain fixture input: ' + input.kind);
    }
  }
};
`,
    },
  ];

  insertions.sort((a, b) => a.offset - b.offset);
  let cursor = 0;
  let changed = '';
  let shift = 0;
  for (const item of insertions) {
    changed += original.slice(cursor, item.offset) + item.text;
    item.actualOffset = item.offset + shift;
    shift += item.text.length;
    cursor = item.offset;
  }
  changed += original.slice(cursor);
  let recovered = changed;
  for (const item of [...insertions].reverse()) {
    recovered =
      recovered.slice(0, item.actualOffset) + recovered.slice(item.actualOffset + item.text.length);
  }
  insist(recovered === original, 'SiteMain observation insertions are not exactly reversible');
  return {
    changed,
    insertions: insertions.map(item => ({
      originalOffset: item.offset,
      actualOffset: item.actualOffset,
      offsetUnit: 'UTF16-code-units',
      originalByteOffset: Buffer.byteLength(original.slice(0, item.offset)),
      actualByteOffset: Buffer.byteLength(changed.slice(0, item.actualOffset)),
      insertedBytes: Buffer.byteLength(item.text),
      sha256: hash(item.text),
    })),
  };
}

function listValues(value, label) {
  const values = [];
  while (value && value.$ === '::') {
    insist(Object.keys(value).sort().join(',') === '$,a,b', `${label}: malformed list cell`);
    values.push(value.a);
    value = value.b;
    insist(values.length <= 10000, `${label}: QA list bound`);
  }
  insist(
    value && value.$ === '[]' && Object.keys(value).join(',') === '$',
    `${label}: malformed list terminator`
  );
  return values;
}

function commandLeaves(bag, counts = { Task: 0 }) {
  insist(bag && typeof bag === 'object', 'malformed SiteMain Cmd bag');
  const keys = Object.keys(bag).sort().join(',');
  if (bag.$ === 2) {
    insist(keys === '$,m', 'unknown SiteMain Cmd batch fields');
    for (const child of listValues(bag.m, 'Cmd batch')) commandLeaves(child, counts);
  } else if (bag.$ === 1) {
    insist(keys === '$,k,l' && bag.k === 'Task', 'unexpected SiteMain Cmd manager/fields');
    insist(bag.l && bag.l.$ === 'Perform', 'unexpected SiteMain Task command wrapper');
    counts.Task++;
  } else {
    throw new Error('unexpected Cmd.map or unknown Cmd bag constructor in SiteMain');
  }
  return counts;
}

function subscriptionLeaves(bag) {
  insist(bag && typeof bag === 'object', 'malformed SiteMain Sub bag');
  const keys = Object.keys(bag).sort().join(',');
  insist(bag.$ === 2 && keys === '$,m', 'SiteMain subscriptions must be Sub.none batch');
  const children = listValues(bag.m, 'Sub batch');
  insist(children.length === 0, 'SiteMain must have zero active subscriptions (Sub.none)');
}

function loadPure(original) {
  const typed = [];
  let initial = null;
  const sentinel = {};
  const noIO = () => {
    throw new Error('unexpected task/DOM execution in PURE SiteMain replay');
  };
  const context = {
    console: { log() {}, warn() {}, error() {} },
    setTimeout: noIO,
    clearTimeout: noIO,
    requestAnimationFrame: noIO,
    cancelAnimationFrame: noIO,
  };
  context[TYPED_HOOK] = desc => {
    typed.push(full(desc));
  };
  context[STEP_HOOK] = () => {
    throw new Error('unexpected sendToApp in PURE SiteMain replay');
  };
  context[INIT_HOOK] = (model, update, subscriptions, command) => {
    initial = { model, update, subscriptions, command };
    throw sentinel;
  };
  vm.createContext(context);
  registerRealm(context);
  const observed = instrument(original);
  new vm.Script(observed.changed, { filename: 'SiteMain.readonly-fixture.js' }).runInContext(
    context,
    { timeout: WAIT_MS }
  );
  insist(context[API] && context[API].nonoptimized(), 'SiteMain bundle must be NONOPTIMIZED');
  insist(context.Elm && context.Elm.SiteMain, 'Elm.SiteMain export missing');
  try {
    context.Elm.SiteMain.init({ node: {}, flags: null });
  } catch (error) {
    if (error !== sentinel) throw error;
  }
  insist(initial, 'SiteMain init was not observed');
  return { context, typed, initial, observed, api: context[API] };
}

function snapshotPure(env, state, command) {
  const effects = env.typed.splice(0);
  const cmdLeaves = commandLeaves(command);
  insist(
    cmdLeaves.Task === effects.length,
    'SiteMain Cmd Task leaf count differs from captured Dom.focus effects'
  );
  env.context.__siteMainSubscriptions = env.initial.subscriptions;
  env.context.__siteMainModel = state;
  const subscriptions = vm.runInContext(
    '__siteMainSubscriptions(__siteMainModel)',
    env.context,
    { timeout: WAIT_MS }
  );
  subscriptionLeaves(subscriptions);
  return full({ state, subscriptions, cmdLeaves, effects });
}

function runPureCase(original, spec) {
  insist(spec && spec.root === 'SiteMain', 'unsupported root for SiteMain observer');
  const env = loadPure(original);
  let model = env.initial.model;
  const trace = [];
  for (let i = 0; i < spec.steps.length; i++) {
    const step = spec.steps[i];
    let command;
    if (i === 0) {
      insist(step.input && step.input.kind === 'init', 'SiteMain history must start from init');
      command = env.initial.command;
    } else {
      insist(step.input && typeof step.input.kind === 'string', 'missing SiteMain input kind');
      env.context.__siteMainInput = step.input;
      env.context.__siteMainModel = model;
      env.context.__siteMainUpdate = env.initial.update;
      const pair = vm.runInContext(
        `globalThis.${API}.a2(__siteMainUpdate, globalThis.${API}.message(__siteMainInput), __siteMainModel)`,
        env.context,
        { timeout: WAIT_MS }
      );
      model = pair.a;
      command = pair.b;
    }
    const actual = snapshotPure(env, model, command);
    const expected = full(step.expected);
    if (!isDeepStrictEqual(actual, expected)) {
      const error = new Error(
        `${spec.name} step ${i}: COMPLETE SiteMain model/subscription/effect descriptions differ`
      );
      error.counterexample = { name: spec.name, step: i, input: step.input, actual, expected };
      throw error;
    }
    trace.push(actual);
  }
  return {
    trace,
    instrumentation: env.observed.insertions,
    instrumentedHash: hash(env.observed.changed),
  };
}

class DomNode {
  constructor(type, name, text = '') {
    this.nodeType = type;
    this.tagName = name;
    this.nodeName = name;
    this.namespaceURI = 'http://www.w3.org/1999/xhtml';
    this.data = text;
    this.nodeValue = text;
    this.parentNode = null;
    this.childNodes = [];
    this.attributes = {};
    this.style = {
      setProperty(k, v) {
        this[k] = v;
      },
      removeProperty(k) {
        delete this[k];
      },
    };
    this.listeners = {};
    this.disabled = false;
    this.hidden = false;
    this.readOnly = false;
    this.value = '';
  }
  get textContent() {
    return this.nodeType === 3 ? this.data : this.childNodes.map(x => x.textContent).join('');
  }
  set textContent(value) {
    if (this.nodeType === 3) {
      this.data = String(value);
      this.nodeValue = this.data;
    } else {
      this.childNodes = [];
      if (value) this.appendChild(new DomNode(3, '#text', String(value)));
    }
  }
  appendChild(child) {
    return this.insertBefore(child, null);
  }
  insertBefore(child, before) {
    if (child.nodeType === 11) {
      for (const item of [...child.childNodes]) this.insertBefore(item, before);
      return child;
    }
    if (child.parentNode) child.parentNode.removeChild(child);
    let i = before ? this.childNodes.indexOf(before) : -1;
    if (i < 0) i = this.childNodes.length;
    this.childNodes.splice(i, 0, child);
    child.parentNode = this;
    return child;
  }
  removeChild(child) {
    const i = this.childNodes.indexOf(child);
    if (i < 0) throw new Error('Missing DOM child');
    this.childNodes.splice(i, 1);
    child.parentNode = null;
    return child;
  }
  replaceChild(child, old) {
    this.insertBefore(child, old);
    this.removeChild(old);
    return old;
  }
  replaceData(_offset, _count, value) {
    this.data = String(value);
    this.nodeValue = this.data;
  }
  setAttribute(k, v) {
    this.attributes[String(k).toLowerCase()] = String(v);
  }
  setAttributeNS(_ns, k, v) {
    this.setAttribute(k, v);
  }
  getAttribute(k) {
    return this.attributes[String(k).toLowerCase()] ?? null;
  }
  removeAttribute(k) {
    delete this.attributes[String(k).toLowerCase()];
  }
  get tabIndex() {
    const value = this.getAttribute('tabindex');
    return value === null ? -1 : Number(value);
  }
  set tabIndex(value) {
    this.setAttribute('tabindex', value);
  }
  removeAttributeNS(_ns, k) {
    this.removeAttribute(k);
  }
  addEventListener(k, fn) {
    this.listeners[k] = fn;
  }
  removeEventListener(k, fn) {
    if (this.listeners[k] === fn) delete this.listeners[k];
  }
  focus() {
    this.focused = true;
    this.focusCount = (this.focusCount ?? 0) + 1;
  }
}

function walkDom(node, predicate) {
  if (predicate(node)) return node;
  for (const child of node.childNodes) {
    const found = walkDom(child, predicate);
    if (found) return found;
  }
  return null;
}

function makeClock() {
  let now = 0;
  let sequence = 0;
  const timers = new Map();
  const trace = [];
  function schedule(fn, delay = 0) {
    const id = ++sequence;
    const deadline = now + Math.max(0, Number(delay) || 0);
    timers.set(id, { fn, deadline });
    trace.push({ event: 'create', id, at: now, deadline });
    return id;
  }
  function cancel(id) {
    const existed = timers.delete(id);
    trace.push({ event: 'cancel', id, at: now, existed });
  }
  function tick(milliseconds) {
    insist(Number.isFinite(milliseconds) && milliseconds >= 0, 'clock: invalid advance');
    const target = now + milliseconds;
    let count = 0;
    for (;;) {
      const due = [...timers]
        .filter(([, row]) => row.deadline <= target)
        .sort((a, b) => a[1].deadline - b[1].deadline || a[0] - b[0])[0];
      if (!due) break;
      insist(++count <= 10000, 'clock: runaway timers');
      const [id, row] = due;
      timers.delete(id);
      now = row.deadline;
      trace.push({ event: 'fire', id, at: now, deadline: row.deadline });
      row.fn();
    }
    now = target;
  }
  function clear() {
    for (const id of [...timers.keys()]) cancel(id);
  }
  return {
    schedule,
    cancel,
    tick,
    clear,
    trace,
    activeCount: () => timers.size,
  };
}

function runFakeDomLifecycle(original, expectedTrace) {
  const clock = makeClock();
  const container = new DomNode(1, 'DIV');
  const mount = new DomNode(3, '#text', '');
  container.appendChild(mount);
  const document = {
    body: container,
    documentElement: container,
    createTextNode: text => new DomNode(3, '#text', String(text)),
    createElement: tag => new DomNode(1, String(tag).toUpperCase()),
    createElementNS: (_ns, tag) => new DomNode(1, String(tag).toUpperCase()),
    createDocumentFragment: () => new DomNode(11, '#document-fragment'),
    addEventListener() {},
    removeEventListener() {},
    getElementById: id => walkDom(container, n => (n.id ?? n.attributes.id) === id),
  };
  const window = {
    document,
    addEventListener() {},
    removeEventListener() {},
    requestAnimationFrame: fn => clock.schedule(fn, 0),
    cancelAnimationFrame: clock.cancel,
  };
  const typed = [];
  const observedTransitions = [];
  const observedMessages = [];
  const sandbox = {
    console: { log() {}, warn() {}, error() {} },
    document,
    window,
    setTimeout: clock.schedule,
    clearTimeout: clock.cancel,
    requestAnimationFrame: window.requestAnimationFrame,
    cancelAnimationFrame: clock.cancel,
  };
  function captureStep(model, subscriptionsBag, command) {
    const effects = typed.splice(0);
    const cmdLeaves = commandLeaves(command);
    insist(
      cmdLeaves.Task === effects.length,
      'SiteMain fake-DOM step Cmd Task leaves differ from captured Dom.focus effects'
    );
    subscriptionLeaves(subscriptionsBag);
    observedTransitions.push(
      full({ state: model, subscriptions: subscriptionsBag, cmdLeaves, effects })
    );
  }
  sandbox[TYPED_HOOK] = desc => {
    typed.push(full(desc));
  };
  sandbox[INIT_HOOK] = (model, _update, subscriptions, command) => {
    captureStep(model, subscriptions(model), command);
  };
  sandbox[STEP_HOOK] = (msg, model, subscriptionsBag, command) => {
    observedMessages.push(full(msg));
    captureStep(model, subscriptionsBag, command);
  };

  vm.createContext(sandbox);
  registerRealm(sandbox);
  const instrumented = instrument(original);
  new vm.Script(instrumented.changed, { filename: 'SiteMain.fakedom.js' }).runInContext(sandbox, {
    timeout: WAIT_MS,
  });
  insist(sandbox.Elm && sandbox.Elm.SiteMain, 'missing Elm.SiteMain in fake-DOM context');
  const app = sandbox.Elm.SiteMain.init({ node: mount, flags: null });
  insist(!app.ports || Object.keys(app.ports).length === 0, 'SiteMain must have zero ports');
  clock.tick(0);
  insist(clock.activeCount() === 0, 'SiteMain must have zero pending timers after initial mount');
  insist(observedTransitions.length === 1, 'SiteMain initial mount must record exactly 1 init state');

  const getTab = id => {
    const node = document.getElementById(id);
    insist(node && typeof node.listeners.keydown === 'function', `missing rendered tab ${id}`);
    return node;
  };
  const sendKey = (node, key) => {
    let prevented = false;
    node.listeners.keydown({
      type: 'keydown',
      key,
      target: node,
      currentTarget: node,
      stopPropagation() {},
      preventDefault() {
        prevented = true;
      },
    });
    return prevented;
  };

  // 1. ArrowRight on #wl-tab-taskbar -> KeyboardStepSpotlight 1 -> rAF focuses #wl-tab-launcher -> TabFocusSettled 1 SurfaceLauncher (Ok ())
  const taskbarTab = getTab('wl-tab-taskbar');
  insist(
    taskbarTab.getAttribute('aria-selected') === 'true' && taskbarTab.tabIndex === 0,
    'initial #wl-tab-taskbar must be selected with tabIndex 0'
  );
  insist(sendKey(taskbarTab, 'ArrowRight') === true, 'ArrowRight on workbench tab must preventDefault');
  insist(observedTransitions.length === 2, 'KeyboardStepSpotlight must update synchronously before rAF');
  clock.tick(0);
  const launcherTab = getTab('wl-tab-launcher');
  insist(
    launcherTab.focused === true && launcherTab.focusCount === 1,
    'Dom.focus must focus #wl-tab-launcher on rAF'
  );
  insist(
    launcherTab.getAttribute('aria-selected') === 'true' && launcherTab.tabIndex === 0,
    '#wl-tab-launcher must be selected after rAF redraw'
  );
  insist(observedTransitions.length === 3, 'rAF focus must settle via TabFocusSettled 1 SurfaceLauncher (Ok ())');
  insist(clock.activeCount() === 0, 'no recurring timers may remain after TabFocusSettled Ok');

  // 2. Two same-frame keydowns before rAF: ArrowRight (seq 2, SurfaceSwitcher) then End (seq 3, SurfaceFiles).
  //    First rAF completion (seq 2) is rejected as stale; second rAF completion (seq 3) focuses #wl-tab-files and settles.
  insist(sendKey(launcherTab, 'ArrowRight') === true, 'second ArrowRight must preventDefault');
  insist(sendKey(launcherTab, 'End') === true, 'End key must preventDefault');
  insist(observedTransitions.length === 5, 'two same-frame keydowns must record transitions 3 and 4');
  clock.tick(0);
  const filesTab = getTab('wl-tab-files');
  insist(
    filesTab.focused === true && filesTab.focusCount === 1,
    'Dom.focus must focus #wl-tab-files on second rAF'
  );
  insist(
    observedTransitions.length === 7,
    'stale seq 2 and current seq 3 TabFocusSettled must record transitions 5 and 6'
  );
  insist(clock.activeCount() === 0, 'no recurring timers may remain after stale+current settlement');

  // 3. Detach #wl-tab-taskbar id from getElementById, press Home (seq 4, SurfaceTaskbar) -> rAF fails with Dom.NotFound("wl-tab-taskbar")
  delete taskbarTab.id;
  delete taskbarTab.attributes.id;
  insist(document.getElementById('wl-tab-taskbar') === null, '#wl-tab-taskbar must be absent for NotFound control');
  insist(sendKey(filesTab, 'Home') === true, 'Home key must preventDefault');
  insist(observedTransitions.length === 8, 'Home key must record transition 7');
  clock.tick(0);
  insist(
    observedTransitions.length === 9,
    'missing DOM node must settle via TabFocusSettled 4 SurfaceTaskbar (Err NotFound)'
  );
  const ticksBeforeIdleAdvance = observedTransitions.length;
  clock.tick(100);
  clock.tick(1000);
  insist(
    observedTransitions.length === ticksBeforeIdleAdvance && clock.activeCount() === 0,
    'SiteMain must schedule zero retry timers or recurring subscriptions after focus miss'
  );

  // 4. Pointer click on Next button -> StepSpotlight 1 clears lastTabFocusMiss with Cmd.none and zero rAF focus tasks
  const nextBtn = walkDom(container, n => n.tagName === 'BUTTON' && n.textContent === 'Next');
  insist(nextBtn && typeof nextBtn.listeners.click === 'function', 'missing rendered Next button');
  nextBtn.listeners.click({
    type: 'click',
    target: nextBtn,
    currentTarget: nextBtn,
    stopPropagation() {},
    preventDefault() {},
  });
  clock.tick(0);
  clock.tick(100);
  insist(observedTransitions.length === 10 && clock.activeCount() === 0, 'Next click must record transition 9 with no recurring timers');

  const expected = full(expectedTrace);
  if (!isDeepStrictEqual(observedTransitions, expected)) {
    const error = new Error('SiteMain fake-DOM lifecycle trace differs from independent literal oracle');
    error.counterexample = { actual: observedTransitions, expected };
    throw error;
  }
  return {
    transitions: observedTransitions.length,
    messagesObserved: observedMessages.length,
    launcherFocusCount: launcherTab.focusCount,
    filesFocusCount: filesTab.focusCount,
    activeTimersAfterIdleAdvance: clock.activeCount(),
  };
}

function main() {
  insist(
    process.argv.length === 4,
    'usage: node sitemain-root-observer.cjs <repository> <SiteMain.plain.js>'
  );
  const repository = path.resolve(process.argv[2]);
  const bundlePath = path.resolve(process.argv[3]);
  const manifestPath = path.join(__dirname, 'sitemain-root-manifest.json');
  const literalsPath = path.join(__dirname, 'sitemain-root-literals.cjs');
  const manifestBytes = fs.readFileSync(manifestPath);
  const manifest = JSON.parse(manifestBytes.toString('utf8'));
  const fixtureFiles = {
    siteMain: fs.readFileSync(path.join(repository, 'site/src/SiteMain.elm')),
    siteElmJson: fs.readFileSync(path.join(repository, 'site/elm.json')),
    literals: fs.readFileSync(literalsPath),
  };
  validateFiles(manifest, fixtureFiles);

  const literals = require(literalsPath);
  insist(literals.coverage && literals.coverage.complete === false, 'coverage must remain incomplete');
  insist(literals.coverage.originalAcceptanceClaim === false, 'originalAcceptanceClaim must remain false');
  const packet = literals.build(repository);
  validateCases(manifest, packet.cases, packet.fakeDomExpectedTrace);

  const original = fs.readFileSync(bundlePath, 'utf8');
  const compiledOriginal = hash(original);
  const results = [];
  for (const spec of packet.cases) {
    const first = runPureCase(original, spec);
    const second = runPureCase(original, spec);
    insist(
      isDeepStrictEqual(first.trace, second.trace),
      `${spec.name}: deterministic replay differs AFTER literal assertions`
    );
    results.push({
      name: spec.name,
      root: spec.root,
      assertedStepsPerRun: spec.steps.length,
      freshRuns: 2,
      compiledOriginal,
      instrumentedInMemory: first.instrumentedHash,
      reversibleInsertions: first.instrumentation,
    });
  }

  const domFirst = runFakeDomLifecycle(original, packet.fakeDomExpectedTrace);
  const domSecond = runFakeDomLifecycle(original, packet.fakeDomExpectedTrace);
  insist(isDeepStrictEqual(domFirst, domSecond), 'SiteMain fake-DOM lifecycle differs across fresh runs');

  console.log(
    JSON.stringify({
      ok: true,
      coverage: literals.coverage,
      cases: results,
      fakeDomLifecycle: {
        ...domFirst,
        freshRuns: 2,
        compiledOriginal,
      },
      sourcePins: packet.sourcePins,
      literalsHash: hash(fixtureFiles.literals),
      observerHash: hash(fs.readFileSync(__filename)),
      manifestHash: hash(manifestBytes),
      limits: [
        'ninth-root SiteMain component replay + fake-DOM focus lifecycle only; not native Omarchy or browser acceptance',
        'SiteMain has Sub.none and zero native control/revocation channels; does not satisfy desktop ELM-TEA-004 recurring-demand obligations',
        'product EARS ELM-TEA-004 remains OPEN until all desktop and native Omarchy obligations are independently verified',
      ],
      originalAcceptanceClaim: false,
    })
  );
}

module.exports = {
  CANONICAL_SITE_MAIN_SHA256,
  CANONICAL_SITE_ELM_JSON_SHA256,
  REVIEWED_LITERALS_SHA256,
  validateFiles,
  validateCases,
  instrument,
  runPureCase,
  runFakeDomLifecycle,
};

if (require.main === module) {
  try {
    main();
  } catch (error) {
    console.error(
      JSON.stringify({
        ok: false,
        error: error.message,
        counterexample: error.counterexample || null,
        originalAcceptanceClaim: false,
      })
    );
    process.exitCode = 1;
  }
}
