'use strict';
// QA ONLY. Root compiles the 4 single-root replay workers WITHOUT --optimize:
//   qa/TeaPopupSubscriptionsReplay.elm
//   qa/TeaBarSubscriptionsReplay.elm
//   qa/TeaAdmissionSubscriptionsReplay.elm
//   qa/TeaRendererSubscriptionsReplay.elm
// and compiles the 8 production Browser.element roots WITH --optimize:
//   src/Main.elm src/Bar.elm src/Popup.elm src/HttpMain.elm
//   src/HttpBar.elm src/HttpPopup.elm src/NativePreviewAdmission.elm src/NativePreviewRenderer.elm
// Usage:
//   node qa/tea-subscriptions.cjs \
//     --workers PopupSubReplay.js BarSubReplay.js AdmissionSubReplay.js RendererSubReplay.js \
//     --roots Main.js Bar.js Popup.js HttpMain.js HttpBar.js HttpPopup.js NativePreviewAdmission.js NativePreviewRenderer.js \
//     [--cases qa/tea-subscriptions-cases.cjs] [--out report.json]
// Uses the reviewed single pre-format _Debug_log read hook on each single-root worker
// (avoiding Elm 0.19 cross-module port-name collisions) AND verifies real compiled
// Browser.element synchronous in-flight, delayed, and closed-overlay port callbacks
// plus recurring HTTP XHR/timer commands across all 9 roots. No native/GUI claim.

const fs = require('node:fs');
const path = require('node:path');
const vm = require('node:vm');
const crypto = require('node:crypto');
const { isDeepStrictEqual } = require('node:util');

const MARKER = 'TEA_SUBSCRIPTIONS_OBSERVE_V1';
const HOOK = '__warlockTeaSubscriptionsCaptureV1';
const WAIT_MS = 10000;
const ALLOWED_SITE_MAIN_SHA256 = new Set([
  '9c432ddf2b7e4d35fae4197c52c4b97cb41fbfa16b45082d2143ea4d6b2d3ba1', // committed HEAD a327c8f7f
  'f05a3768eb4573161544099917ce009f8df7eb57b8c9408f5266001980cafcfb', // foreign working-tree SiteMain.elm
]);

const WORKER_SPEC = {
  popup: { moduleName: 'TeaPopupSubscriptionsReplay', elmFile: 'TeaPopupSubscriptionsReplay.elm' },
  bar: { moduleName: 'TeaBarSubscriptionsReplay', elmFile: 'TeaBarSubscriptionsReplay.elm' },
  admission: { moduleName: 'TeaAdmissionSubscriptionsReplay', elmFile: 'TeaAdmissionSubscriptionsReplay.elm' },
  renderer: { moduleName: 'TeaRendererSubscriptionsReplay', elmFile: 'TeaRendererSubscriptionsReplay.elm' },
};

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
    insist(after && ['value', 'get', 'set', 'writable', 'enumerable', 'configurable']
      .every(field => Object.is(before[field], after[field])), `${where}: changed intrinsic prototype member`);
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
  } finally {
    active.delete(value);
  }
}

// Positive ABI witnesses for the source-pinned official Elm 0.19.1 compiler.
// Both builds retain debug kernel helpers. The exact named List constructor,
// unlike _List_Nil_UNUSED, selects the live optimized vs debug representation.
function elm191ListAbi(code) {
  const declarations = code.match(/^var _List_Nil(?=[ \t=;])[^\r\n]*$/gm) || [];
  if (declarations.length !== 1) return null;
  if (declarations[0] === 'var _List_Nil = { $: 0 };') return 'optimized';
  if (declarations[0] === "var _List_Nil = { $: '[]' };") return 'debug';
  return null;
}

function instrument(original, label) {
  insist(elm191ListAbi(original) === 'debug', `${label}: expected source-pinned Elm 0.19.1 debug List ABI`);
  const definition = /var _Debug_log\s*=\s*F2\(function\s*\(tag,\s*value\)\s*\{/g;
  const matches = [...original.matchAll(definition)];
  insist(matches.length === 1, `${label}: expected exactly one Elm _Debug_log definition`);
  const begin = matches[0].index + matches[0][0].length;
  const end = original.indexOf('});', begin);
  insist(end > begin && end - begin < 1000, `${label}: unrecognized _Debug_log body`);
  const body = original.slice(begin, end);
  insist(body.includes('_Debug_toString(value)') && /return\s+value\s*;/.test(body), `${label}: fixture must be unoptimized debug Elm`);
  insist(original.split(MARKER).length === 2, `${label}: expected exactly one fixture observation marker`);
  insist(!original.includes(HOOK), `${label}: capture hook already present`);
  const insertion = `\nif (tag === ${JSON.stringify(MARKER)}) { globalThis.${HOOK}(value); }\n`;
  const changed = original.slice(0, begin) + insertion + original.slice(begin);
  insist(changed.slice(0, begin) + changed.slice(begin + insertion.length) === original, `${label}: instrumentation not exactly reversible`);
  return { changed, insertionOffset: begin, insertedBytes: Buffer.byteLength(insertion) };
}

function loadWorker(source, moduleName, captures) {
  const context = { console: { log() {}, warn() {}, error() {} }, setTimeout, clearTimeout };
  context[HOOK] = value => {
    const tuple = full(value);
    insist(tuple && typeof tuple === 'object' && !Array.isArray(tuple), 'observer value is not a tuple');
    const keys = Object.keys(tuple).sort().join(',');
    insist(keys === '$,a,b' && tuple.$ === '#2', `unexpected debug tuple shape: ${keys}`);
    insist(tuple.a && typeof tuple.a === 'object' && Object.keys(tuple.a).sort().join(',') === 'model,subscriptions', 'unexpected observed state shape');
    captures.push(full({ state: tuple.a, effects: tuple.b }));
  };
  vm.createContext(context);
  registerRealm(context);
  new vm.Script(source, { filename: `${moduleName}.instrumented.js` }).runInContext(context, { timeout: 10000 });
  insist(context.Elm && context.Elm[moduleName] && typeof context.Elm[moduleName].init === 'function', `compiled ${moduleName} worker missing`);
  const app = context.Elm[moduleName].init({ flags: null });
  insist(app.ports && app.ports.incoming && typeof app.ports.incoming.send === 'function' && app.ports.outgoing && typeof app.ports.outgoing.subscribe === 'function', `${moduleName}: required fixture ports missing`);
  return app;
}

function portValue(value) {
  if (value === null || typeof value !== 'object') return value;
  if (Array.isArray(value)) return value.map(portValue);
  const result = {};
  for (const key of Object.keys(value)) {
    Object.defineProperty(result, key, {
      value: portValue(value[key]),
      enumerable: true,
      writable: true,
      configurable: true,
    });
  }
  return result;
}

function loadOracle(bytes, filename) {
  const source = bytes.toString('utf8');
  insist(Buffer.from(source, 'utf8').equals(bytes), 'oracle is not canonical UTF-8');
  const context = vm.createContext(
    { Date: undefined, process: undefined, require: undefined, fetch: undefined, console: undefined },
    { codeGeneration: { strings: false, wasm: false } }
  );
  registerRealm(context);
  new vm.Script('globalThis.module = { exports: {} }; globalThis.exports = module.exports; Math.random = undefined;\n' + source,
    { filename }).runInContext(context, { timeout: 10000 });
  return context.module.exports;
}

function validateCases(moduleValue) {
  insist(moduleValue && Array.isArray(moduleValue.cases) && typeof moduleValue.materialize === 'function', 'oracle must export cases and materialize(case)');
  insist(moduleValue.cases.length > 0, 'independent oracle has no cases');
  const seen = new Set();
  return moduleValue.cases.map(spec => {
    const expanded = moduleValue.materialize(spec);
    insist(expanded && typeof expanded.name === 'string' && expanded.name.length > 0 && !seen.has(expanded.name), 'case name missing or duplicate');
    insist(Object.hasOwn(WORKER_SPEC, expanded.worker), `${expanded.name}: invalid worker ${expanded.worker}`);
    seen.add(expanded.name);
    insist(Array.isArray(expanded.steps) && expanded.steps.length > 1 &&
      expanded.steps.some((step, index) => index > 0 && step && step.input && step.input.kind !== 'reset'),
      `${expanded.name}: at least one tested transition after reset required`);
    return {
      name: expanded.name,
      worker: expanded.worker,
      steps: expanded.steps.map((step, index) => {
        insist(step && step.input && step.expected && Object.hasOwn(step.expected, 'state') && Object.hasOwn(step.expected, 'effects'),
          `${expanded.name}/${index}: complete literal expected state and effects required`);
        const input = full(step.input, `${expanded.name}/${index}/input`);
        insist(input && typeof input.kind === 'string' && (index !== 0 || input.kind === 'reset') && (index === 0 || input.kind !== 'reset'),
          `${expanded.name}/${index}: exactly one leading reset required`);
        insist(!Object.hasOwn(input, 'caseId') && !Object.hasOwn(input, 'step'), `${expanded.name}/${index}: reserved input metadata`);
        return { input, expected: full(step.expected, `${expanded.name}/${index}/expected`) };
      }),
    };
  });
}

async function executeCase(workerInfo, testCase) {
  const captures = [];
  const app = loadWorker(workerInfo.patch.changed, workerInfo.moduleName, captures);
  let pending = null;
  let protocolError = null;
  app.ports.outgoing.subscribe(message => {
    if (!pending) {
      protocolError = new Error(`${testCase.name}: unexpected or duplicate acknowledgement`);
      return;
    }
    const resolve = pending;
    pending = null;
    resolve(full(message, `${testCase.name}/ack`));
  });
  const trace = [];
  for (let i = 0; i < testCase.steps.length; i++) {
    insist(!protocolError && captures.length === i, `${testCase.name}/${i}: unexpected capture or acknowledgement`);
    const current = testCase.steps[i];
    const ack = await new Promise((resolve, reject) => {
      let timer;
      pending = value => { clearTimeout(timer); resolve(value); };
      timer = setTimeout(() => { pending = null; reject(new Error(`${testCase.name}/${i}: worker acknowledgement timeout`)); }, WAIT_MS);
      try {
        app.ports.incoming.send({ ...portValue(current.input), caseId: testCase.name, step: i });
      } catch (error) {
        clearTimeout(timer);
        pending = null;
        reject(error);
      }
    });
    insist(!protocolError && ack && ack.ok === true && ack.error === '' && ack.caseId === testCase.name && ack.step === i,
      `${testCase.name}/${i}: invalid fixture acknowledgement (${ack && ack.error})`);
    insist(captures.length === i + 1, `${testCase.name}/${i}: expected one complete capture`);
    const observed = captures[i];
    insist(isDeepStrictEqual(observed, current.expected),
      `${testCase.name}/${i} (${current.input.kind}): full state/subscriptions/effects differ from independent literal oracle\nexpected=${JSON.stringify(current.expected)}\nactual=${JSON.stringify(observed)}`);
    trace.push(observed);
  }
  insist(!protocolError, `${testCase.name}: acknowledgement protocol failure`);
  return trace;
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
    this.style = { setProperty(k, v) { this[k] = v; }, removeProperty(k) { delete this[k]; } };
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
  appendChild(child) { return this.insertBefore(child, null); }
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
  setAttribute(k, v) { this.attributes[k] = String(v); }
  setAttributeNS(_ns, k, v) { this.setAttribute(k, v); }
  getAttribute(k) { return this.attributes[k] ?? null; }
  removeAttribute(k) { delete this.attributes[k]; }
  removeAttributeNS(_ns, k) { this.removeAttribute(k); }
  addEventListener(k, fn) { this.listeners[k] = fn; }
  removeEventListener(k, fn) { if (this.listeners[k] === fn) delete this.listeners[k]; }
  focus() { this.focused = true; this.focusCount = (this.focusCount ?? 0) + 1; }
}

function walkDom(node, predicate) {
  if (predicate(node)) return node;
  for (const child of node.childNodes) {
    const found = walkDom(child, predicate);
    if (found) return found;
  }
  return null;
}

async function mountOptimizedElement(bundlePath, moduleName, flags = null) {
  const bytes = fs.readFileSync(bundlePath);
  const code = bytes.toString('utf8');
  insist(elm191ListAbi(code) === 'optimized', `${moduleName} must use the source-pinned Elm 0.19.1 optimized List ABI`);
  const requests = [];
  const timers = new Map();
  let sequence = 0;

  class ControlledXHR {
    constructor() {
      this.handlers = {};
      this.upload = { handlers: {}, addEventListener(kind, handler) { this.handlers[kind] = handler; } };
      this.headers = {};
      this.aborted = false;
      this.done = false;
      this.abortCount = 0;
    }
    addEventListener(kind, handler) { this.handlers[kind] = handler; }
    open(method, url, async) { this.method = method; this.url = url; this.async = async; }
    setRequestHeader(key, value) { this.headers[key] = value; }
    getAllResponseHeaders() { return 'Content-Type: application/json\r\n'; }
    send(body) { this.body = body ?? ''; requests.push(this); }
    abort() { this.aborted = true; this.abortCount++; }
    respond(status, body = '') {
      insist(!this.done && !this.aborted, `${moduleName}: response to inactive XHR`);
      this.done = true;
      this.status = status;
      this.statusText = String(status);
      this.response = body;
      this.responseText = body;
      this.responseURL = 'http://127.0.0.1:41001' + this.url;
      if (this.handlers.load) this.handlers.load();
    }
    fail(kind = 'error') {
      insist(!this.done && !this.aborted, `${moduleName}: failure to inactive XHR`);
      this.done = true;
      if (this.handlers[kind]) this.handlers[kind]();
    }
  }

  const schedule = (fn, delay = 0) => {
    const id = ++sequence;
    timers.set(id, { fn, delay: Number(delay) || 0 });
    return id;
  };
  const cancel = id => timers.delete(id);
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
    requestAnimationFrame: fn => schedule(fn, 0),
    cancelAnimationFrame: cancel,
  };
  const sandbox = {
    console: { log() {}, warn() {}, error() {} },
    document,
    window,
    XMLHttpRequest: ControlledXHR,
    setTimeout: schedule,
    clearTimeout: cancel,
    requestAnimationFrame: window.requestAnimationFrame,
    cancelAnimationFrame: cancel,
  };
  vm.createContext(sandbox);
  registerRealm(sandbox);
  new vm.Script(code, { filename: path.basename(bundlePath) }).runInContext(sandbox, { timeout: 10000 });
  insist(sandbox.Elm && sandbox.Elm[moduleName] && typeof sandbox.Elm[moduleName].init === 'function', `missing Elm.${moduleName}.init`);
  const app = sandbox.Elm[moduleName].init({ node: mount, flags: portValue(flags) });
  const env = {
    app,
    container,
    requests,
    sha256: hash(bytes),
    async flush() {
      for (let round = 0; round < 12; round++) {
        for (const [id, row] of [...timers]) {
          if (row.delay <= 0) {
            timers.delete(id);
            row.fn();
          }
        }
        await new Promise(resolve => setImmediate(resolve));
      }
    },
    async tick(milliseconds) {
      for (const [id, row] of [...timers]) {
        if (row.delay <= milliseconds) {
          timers.delete(id);
          row.fn();
        }
      }
      await this.flush();
    },
    gets() { return requests.filter(r => r.method === 'GET'); },
    posts() { return requests.filter(r => r.method === 'POST'); },
    activeGet() { return requests.find(r => r.method === 'GET' && !r.done && !r.aborted); },
    async sendPort(portName, value) {
      app.ports[portName].send(portValue(value));
      await this.flush();
    },
    close() {
      timers.clear();
      for (const req of requests) {
        if (!req.done && !req.aborted) req.abort();
      }
    },
  };
  await env.flush();
  return env;
}

async function verifyOptimizedRoots(rootPaths) {
  const [mainJs, barJs, popupJs, httpMainJs, httpBarJs, httpPopupJs, admissionJs, rendererJs] = rootPaths.map(p => path.resolve(p));
  const hashes = {};
  const binding = { lifetime: '1', session: '1', frontend: '1' };
  const contextWire = { lifetime: '1', incarnation: '1', output: '1', privacy: '1', rendering: '1', scene: '1', content: '1' };
  const scopeWire = { binding, context: contextWire, observation: '1', clock: '1', now: '10', present: true, sourceLive: true, locked: false, gpuReady: true };
  const triggerWire = { binding, context: contextWire, origin: '1', clock: '1', deadline: '5000' };
  const jobWire = { binding, context: contextWire, request: '1', origin: '1', clock: '1', deadline: '5000' };
  const acquireCmdWire = { kind: 'acquire', job: jobWire };
  const cancelCmdWire = { kind: 'cancel', job: jobWire };
  const acknowledgeCmdWire = { kind: 'acknowledge', job: jobWire, sequence: '1' };
  const reconcileCmdWire = { kind: 'reconcile', binding };
  const scopedEnvelope = entries => ({ previewProtocol: 3, kind: 'preview-proposals', binding, receiverEpoch: '1', entries });
  const control = (id, domId, label, enabled = true) => ({ id, domId, label, ariaLabel: label, detail: '', enabled });
  const frame = (publication, lease, mode, status, bar, popup) => ({ surfaceProtocol: 2, publication, lease, mode, status, bar, popup });
  const gateway = (kind, payload) => ({ bridgeProtocol: 1, kind, payload });

  // 1. Main: static incoming + surfaceCommits port ABI; topology v1 + v2 and native attach/disconnect delivered while closed
  const mainEnv = await mountOptimizedElement(mainJs, 'Main');
  try {
    hashes.Main = mainEnv.sha256;
    insist(isDeepStrictEqual(Object.keys(mainEnv.app.ports || {}).sort(), ['incoming', 'surfaceCommits']), 'Main port ABI mismatch');
    const mainCommits = [];
    mainEnv.app.ports.surfaceCommits.subscribe(v => mainCommits.push(full(v)));
    await mainEnv.sendPort('incoming', gateway('view-topology', { viewProtocol: 1, kind: 'view-topology', revision: '1', views: [{ id: '1', generation: '1' }] }));
    insist(mainCommits.length === 1 && mainCommits[0].viewProtocol === 1 && mainCommits[0].kind === 'view-commit', 'Main must emit view-commit on v1 topology while closed');
    await mainEnv.sendPort('incoming', gateway('view-topology', {
      viewProtocol: 2, kind: 'view-topology', revision: '2', views: [{ id: '1', generation: '1' }],
      locations: [{ scope: { id: '1', generation: '1' }, box: [0, 0, 800, 600] }],
    }));
    insist(mainCommits.length === 2 && mainCommits[1].kind === 'view-commit', 'Main must emit view-commit on v2 topology while closed');
    await mainEnv.sendPort('incoming', gateway('native-event', { protocolVersion: 3, kind: 'attached', binding }));
    insist(mainCommits.length === 3 && mainCommits[2].requests.some(r => r.kind === 'projection-request'), 'Main must process native attach while closed');
    await mainEnv.sendPort('incoming', gateway('native-event', { protocolVersion: 3, kind: 'host-disconnected' }));
    insist(mainCommits.length === 4 && mainCommits[3].projection.frame.bar.some(c => c.id === 'bar:reconnect' && c.enabled), 'Main must process native revocation while closed');
  } finally {
    mainEnv.close();
  }

  // 2. Bar: requestAction & announcements unsubscribed before presentation, subscribed and active after presentation
  const barEnv = await mountOptimizedElement(barJs, 'Bar');
  try {
    hashes.Bar = barEnv.sha256;
    insist(isDeepStrictEqual(Object.keys(barEnv.app.ports || {}).sort(), ['actions', 'announcements', 'presentation', 'requestAction']), 'Bar port ABI mismatch');
    const barActions = [];
    barEnv.app.ports.actions.subscribe(v => barActions.push(full(v)));
    const barActionWire = { surfaceProtocol: 2, kind: 'surface-action', surface: 'bar', publication: '1', lease: '0', id: 'bar:applications' };
    await barEnv.sendPort('requestAction', barActionWire);
    insist(barActions.length === 0, 'Bar must drop requestAction when unsubscribed before presentation');
    await barEnv.sendPort('presentation', frame('1', '0', 'closed', 'Ready', [control('bar:applications', 'open-apps', 'Applications')], []));
    await barEnv.sendPort('requestAction', barActionWire);
    insist(barActions.length === 1 && isDeepStrictEqual(barActions[0], full(barActionWire)), 'Bar must deliver exact surface-action once taskbar consumer is present');
    const barRoute = { scope: { id: '1', generation: '1' }, surface: 'bar' };
    await barEnv.sendPort('announcements', {
      announcementProtocol: 1, kind: 'announcement-projection', recipient: barRoute, announcer: barRoute,
      publication: '1', lease: '0', message: { sequence: '1', correlation: 'c1', text: 'Taskbar ready', interrupt: false }, deliver: true,
    });
    insist(barEnv.container.textContent.includes('Taskbar ready'), 'Bar must render live announcement once subscribed');
  } finally {
    barEnv.close();
  }

  // 3A. Popup Instance A: idle suppression + synchronous same-turn previewPainted callback + closed-overlay terminal receipt
  const popEnvA = await mountOptimizedElement(popupJs, 'Popup');
  try {
    hashes.Popup = popEnvA.sha256;
    insist(isDeepStrictEqual(Object.keys(popEnvA.app.ports || {}).sort(), [
      'actions', 'announcements', 'nativePreviewClosed', 'nativePreviewGrants', 'nativePreviewIssued',
      'nativePreviewQuarantine', 'nativePreviewRetirement', 'nativePreviewRetry', 'nativePreviews',
      'presentation', 'previewCommands', 'previewPaintRequests', 'previewPainted', 'requestAction',
    ]), 'Popup port ABI mismatch');
    const cmdsA = [];
    const paintsA = [];
    const actionsA = [];
    let syncPaint = false;
    popEnvA.app.ports.previewCommands.subscribe(v => cmdsA.push(full(v)));
    popEnvA.app.ports.previewPaintRequests.subscribe(v => {
      const clean = full(v);
      paintsA.push(clean);
      if (syncPaint && Array.isArray(clean) && clean.length === 1) {
        popEnvA.app.ports.previewPainted.send(portValue(clean[0]));
      }
    });
    popEnvA.app.ports.actions.subscribe(v => actionsA.push(full(v)));

    // Unsubscribed when idle: zero wakeups/emissions
    await popEnvA.sendPort('nativePreviews', { kind: 'bogus' });
    await popEnvA.sendPort('previewPainted', { ticket: '1' });
    await popEnvA.sendPort('nativePreviewIssued', { bogus: true });
    await popEnvA.sendPort('nativePreviewRetry', { binding, receiverEpoch: '1' });
    await popEnvA.sendPort('requestAction', { surfaceProtocol: 2, kind: 'surface-action', surface: 'popup', publication: '3', lease: '2', id: 'control:close' });
    insist(cmdsA.length === 0 && paintsA.length === 0 && actionsA.length === 0, 'Popup idle unsubscribed ports must emit zero effects');

    await popEnvA.sendPort('presentation', frame('3', '2', 'picker', 'Choose a window.', [control('bar:applications', 'open-apps', 'Applications')], [control('control:close', 'picker-close', 'Close'), control('family:1', 'picker-f1', 'Foot')]));
    await popEnvA.sendPort('nativePreviews', { kind: 'seed', publication: '3', lease: '2', identity: 'family:1', scope: scopeWire, title: 'Foot', application: 'foot' });
    const countBeforeAcquire = cmdsA.length;
    syncPaint = true;
    await popEnvA.sendPort('nativePreviews', { kind: 'event', identity: 'family:1', event: { kind: 'request', trigger: triggerWire } });
    syncPaint = false;
    insist(isDeepStrictEqual(paintsA.at(-1), full([{ ticket: '1' }])), 'Popup must emit ticket 1 paint request');
    insist(cmdsA.length === countBeforeAcquire + 2 && isDeepStrictEqual(cmdsA.at(-1), full([{ identity: 'family:1', commands: [acquireCmdWire] }])),
      'Popup synchronous previewPainted callback inside previewPaintRequests must release acquire on the same turn');

    // PreviewPaintedChannel must now be unsubscribed again (0 wakeups on duplicate ticket)
    const countAfterDrain = cmdsA.length;
    await popEnvA.sendPort('previewPainted', { ticket: '1' });
    insist(cmdsA.length === countAfterDrain, 'Popup must unsubscribe previewPainted once PaintGate drains');

    // Close overlay while Capturing job -> emits cancel, unsubscribes requestAction, retains nativePreviews for terminal receipt
    await popEnvA.sendPort('presentation', frame('4', '2', 'closed', 'Ready', [control('bar:applications', 'open-apps', 'Applications')], []));
    insist(isDeepStrictEqual(cmdsA.at(-1), full([{ identity: 'family:1', commands: [cancelCmdWire] }])), 'Popup close must emit cancel for Capturing job');
    await popEnvA.sendPort('requestAction', { surfaceProtocol: 2, kind: 'surface-action', surface: 'popup', publication: '4', lease: '0', id: 'control:close' });
    insist(actionsA.length === 0, 'Popup must unsubscribe requestAction when mode == closed');
    await popEnvA.sendPort('nativePreviews', { kind: 'event', identity: 'family:1', event: { kind: 'receipt', sequence: '1', event: { kind: 'cancelled', job: jobWire } } });
    insist(isDeepStrictEqual(cmdsA.at(-1), full([{ identity: 'family:1', commands: [acknowledgeCmdWire] }])),
      'Popup must deliver ordered terminal cancelled receipt while mode == closed and emit acknowledge');
  } finally {
    popEnvA.close();
  }

  // 3B. Popup Instance B: scoped protocol-3 realm + closed-overlay delayed paint + delayed/sync issued/retry/quarantine
  const popEnvB = await mountOptimizedElement(popupJs, 'Popup');
  try {
    const cmdsB = [];
    const paintsB = [];
    const domainWire = { binding, receiverEpoch: '1' };
    const grantWire = { binding, receiverEpoch: '1', capacity: 1 };
    const ticket1Packet = JSON.stringify({ previewProtocol: 3, kind: 'preview-commands', binding, receiverEpoch: '1', controlOrdinal: '1', entries: [{ identity: 'family:1', commands: [acquireCmdWire] }] });
    const ticket1Wire = { previewProtocol: 3, kind: 'preview-control-ticket', binding, receiverEpoch: '1', controlOrdinal: '1', alreadyDelivered: false, wire: ticket1Packet };
    const ticket2Packet = JSON.stringify({ previewProtocol: 3, kind: 'preview-commands', binding, receiverEpoch: '1', controlOrdinal: '2', entries: [{ identity: 'family:1', commands: [cancelCmdWire] }] });
    const ticket2Wire = { previewProtocol: 3, kind: 'preview-control-ticket', binding, receiverEpoch: '1', controlOrdinal: '2', alreadyDelivered: false, wire: ticket2Packet };
    let syncIssueCancel = false;
    popEnvB.app.ports.previewCommands.subscribe(v => {
      const clean = full(v);
      cmdsB.push(clean);
      if (syncIssueCancel && clean && clean.kind === 'preview-proposals' && Array.isArray(clean.entries) &&
          clean.entries.length === 1 && clean.entries[0].commands[0].kind === 'cancel') {
        popEnvB.app.ports.nativePreviewIssued.send(portValue(ticket2Wire));
      }
    });
    popEnvB.app.ports.previewPaintRequests.subscribe(v => paintsB.push(full(v)));

    await popEnvB.sendPort('nativePreviewGrants', grantWire);
    await popEnvB.sendPort('presentation', frame('1', '1', 'picker', 'Choose a window.', [control('bar:applications', 'open-apps', 'Applications')], [control('control:close', 'picker-close', 'Close'), control('family:1', 'picker-f1', 'Foot')]));
    insist(isDeepStrictEqual(cmdsB.at(-1), full(scopedEnvelope([]))), 'Scoped Popup presentation must preserve protocol-3 empty preview-proposals envelope');
    await popEnvB.sendPort('nativePreviews', {
      previewProtocol: 3, kind: 'native-preview-realm-event', binding, receiverEpoch: '1',
      event: { kind: 'seed', publication: '1', lease: '1', identity: 'family:1', scope: scopeWire, title: 'Foot', application: 'foot' },
    });
    await popEnvB.sendPort('nativePreviews', {
      previewProtocol: 3, kind: 'native-preview-realm-event', binding, receiverEpoch: '1',
      event: { kind: 'event', identity: 'family:1', event: { kind: 'request', trigger: triggerWire } },
    });
    insist(isDeepStrictEqual(paintsB.at(-1), full([{ ticket: '1' }])) && isDeepStrictEqual(cmdsB.at(-1), full(scopedEnvelope([]))),
      'Scoped acquire must queue paint ticket 1 and hold acquire behind paint');

    // Close overlay BEFORE paint: cancel spills into deferred; Paint, Issued, and Retry stay subscribed while closed
    await popEnvB.sendPort('presentation', frame('2', '1', 'closed', 'Ready', [control('bar:applications', 'open-apps', 'Applications')], []));
    insist(isDeepStrictEqual(cmdsB.at(-1), full(scopedEnvelope([]))), 'Closing before paint must deduplicate held acquire ticket without bypassing paint');

    // Delayed paint arrival while mode == closed -> emits protocol-3 acquire proposal!
    await popEnvB.sendPort('previewPainted', { ticket: '1' });
    insist(isDeepStrictEqual(cmdsB.at(-1), full(scopedEnvelope([{ identity: 'family:1', commands: [acquireCmdWire] }]))),
      'Delayed previewPainted while closed must emit protocol-3 acquire preview-proposals envelope');

    // Delayed nativePreviewIssued for ordinal 1 while closed -> drains acquire; deferred cancel remains
    await popEnvB.sendPort('nativePreviewIssued', { ...ticket1Wire, receiverEpoch: '9' });
    await popEnvB.sendPort('nativePreviewIssued', ticket1Wire);

    // Retry while closed emits protocol-3 cancel proposal AND synchronous nativePreviewIssued inside callback drains cancel!
    syncIssueCancel = true;
    await popEnvB.sendPort('nativePreviewRetry', domainWire);
    syncIssueCancel = false;
    insist(isDeepStrictEqual(cmdsB.at(-1), full(scopedEnvelope([{ identity: 'family:1', commands: [cancelCmdWire] }]))),
      'nativePreviewRetry while closed must emit protocol-3 cancel preview-proposals envelope');

    // Once Ingress.pending & deferred are both empty, nativePreviewRetry must be unsubscribed (0 wakeups)
    const countAfterCancelDrained = cmdsB.length;
    await popEnvB.sendPort('nativePreviewRetry', domainWire);
    insist(cmdsB.length === countAfterCancelDrained, 'Popup must unsubscribe nativePreviewRetry when ingress & deferred drain');

    // Quarantine while closed emits protocol-3 reconcile proposal and re-activates retry subscription
    await popEnvB.sendPort('nativePreviewQuarantine', domainWire);
    insist(isDeepStrictEqual(cmdsB.at(-1), full(scopedEnvelope([{ identity: 'binding:1:1:1', commands: [reconcileCmdWire] }]))),
      'nativePreviewQuarantine while closed must emit protocol-3 reconcile preview-proposals envelope');
    await popEnvB.sendPort('nativePreviewRetry', domainWire);
    insist(cmdsB.length === countAfterCancelDrained + 2 && isDeepStrictEqual(cmdsB.at(-1), full(scopedEnvelope([{ identity: 'binding:1:1:1', commands: [reconcileCmdWire] }]))),
      'nativePreviewRetry must re-subscribe when quarantine reconcile intent is pending');
  } finally {
    popEnvB.close();
  }

  // 4. NativePreviewAdmission: requestAction dropped before frame and when closed, delivered when open, dropped again when re-closed
  const admEnv = await mountOptimizedElement(admissionJs, 'NativePreviewAdmission');
  try {
    hashes.NativePreviewAdmission = admEnv.sha256;
    insist(isDeepStrictEqual(Object.keys(admEnv.app.ports || {}).sort(), ['actions', 'presentation', 'requestAction']), 'NativePreviewAdmission port ABI mismatch');
    const admActions = [];
    admEnv.app.ports.actions.subscribe(v => admActions.push(full(v)));
    const closeWire = { surfaceProtocol: 2, kind: 'surface-action', surface: 'popup', publication: '2', lease: '1', id: 'control:close' };
    await admEnv.sendPort('requestAction', closeWire);
    insist(admActions.length === 0, 'NativePreviewAdmission must drop pre-frame requestAction');
    await admEnv.sendPort('presentation', frame('1', '0', 'closed', 'Ready', [control('bar:applications', 'open-apps', 'Applications')], []));
    await admEnv.sendPort('requestAction', { ...closeWire, publication: '1', lease: '0' });
    insist(admActions.length === 0, 'NativePreviewAdmission must drop requestAction when mode == closed');
    await admEnv.sendPort('presentation', frame('2', '1', 'applications', 'Applications', [control('bar:applications', 'open-apps', 'Applications')], [control('control:close', 'close-apps', 'Close applications')]));
    await admEnv.sendPort('requestAction', closeWire);
    insist(admActions.length === 1 && isDeepStrictEqual(admActions[0], full(closeWire)), 'NativePreviewAdmission must deliver requestAction when overlay open');
    await admEnv.sendPort('presentation', frame('3', '1', 'closed', 'Ready', [control('bar:applications', 'open-apps', 'Applications')], []));
    await admEnv.sendPort('requestAction', { ...closeWire, publication: '3', lease: '0' });
    insist(admActions.length === 1, 'NativePreviewAdmission must unsubscribe requestAction again on close');
  } finally {
    admEnv.close();
  }

  // 5. NativePreviewRenderer: Inert unsubscribes visualSnapshots; valid grant subscribes until poisoned
  const closedSurfaceWire = frame('1', '0', 'closed', 'Ready', [control('bar:applications', 'open-apps', 'Applications')], []);
  const projectionPacket = seq => ({
    channelProtocol: 1, kind: 'native-preview-projection', binding, receiverEpoch: '1', rendererLease: '1', visualSequence: String(seq),
    visual: { visualProtocol: 1, kind: 'native-preview-visual', binding, receiverEpoch: '1', surface: closedSurfaceWire, previews: [] },
  });
  const inertRen = await mountOptimizedElement(rendererJs, 'NativePreviewRenderer', null);
  try {
    hashes.NativePreviewRenderer = inertRen.sha256;
    insist(isDeepStrictEqual(Object.keys(inertRen.app.ports || {}).sort(), ['acceptedSnapshots', 'surfaceActions', 'visualSnapshots']), 'NativePreviewRenderer port ABI mismatch');
    const inertAccepted = [];
    inertRen.app.ports.acceptedSnapshots.subscribe(v => inertAccepted.push(full(v)));
    await inertRen.sendPort('visualSnapshots', projectionPacket(1));
    insist(inertAccepted.length === 0, 'Inert NativePreviewRenderer must drop visualSnapshots');
  } finally {
    inertRen.close();
  }
  const activeRen = await mountOptimizedElement(rendererJs, 'NativePreviewRenderer', {
    channelProtocol: 1, kind: 'native-preview-renderer-grant', binding, receiverEpoch: '1', rendererLease: '1', sequenceFloor: '0',
  });
  try {
    const accepted = [];
    activeRen.app.ports.acceptedSnapshots.subscribe(v => accepted.push(full(v)));
    await activeRen.sendPort('visualSnapshots', projectionPacket(1));
    insist(accepted.length === 1 && isDeepStrictEqual(accepted[0], full({
      channelProtocol: 1, kind: 'native-preview-projection-accepted', binding, receiverEpoch: '1', rendererLease: '1', visualSequence: '1',
    })), 'Admitted NativePreviewRenderer must accept projection and emit receipt');
    await activeRen.sendPort('visualSnapshots', { malformed: true });
    await activeRen.sendPort('visualSnapshots', projectionPacket(2));
    insist(accepted.length === 1, 'Poisoned NativePreviewRenderer must unsubscribe visualSnapshots and drop subsequent packets');
  } finally {
    activeRen.close();
  }

  const assertHttpReq = (req, method, url, label) => {
    insist(Boolean(req) && req.method === method && req.url === url && req.async === true, `${label}: expected async ${method} ${url}`);
    insist(req.headers['X-Warlock-Api'] === '1', `${label}: missing X-Warlock-Api: 1 header`);
    insist(req.timeout === 5000, `${label}: expected 5000ms XHR timeout, got ${req.timeout}`);
    if (method === 'GET') {
      insist(req.body === '', `${label}: GET /events must send empty body`);
    } else {
      const ct = String(req.headers['Content-Type'] || req.headers['content-type'] || '');
      insist(ct.startsWith('application/json'), `${label}: POST must set Content-Type application/json, got ${ct}`);
    }
  };

  // 6. HttpMain: recurring /events GET + 204 Process.sleep 100 timer + closed topology/revocation -> /commit POST + tracker abort & sticky stop on error
  const httpMain = await mountOptimizedElement(httpMainJs, 'HttpMain');
  try {
    hashes.HttpMain = httpMain.sha256;
    insist(!httpMain.app.ports || Object.keys(httpMain.app.ports).length === 0, 'HttpMain must have zero ports');
    insist(httpMain.gets().length === 1, 'HttpMain initial /events GET missing');
    assertHttpReq(httpMain.activeGet(), 'GET', '/events', 'HttpMain GET#1');
    httpMain.activeGet().respond(204, '');
    await httpMain.flush();
    await httpMain.tick(99);
    insist(httpMain.gets().length === 1, 'HttpMain must not poll before 100ms timer expires');
    await httpMain.tick(100);
    insist(httpMain.gets().length === 2, 'HttpMain must issue next /events GET after 100ms timer');
    assertHttpReq(httpMain.activeGet(), 'GET', '/events', 'HttpMain GET#2');
    httpMain.activeGet().respond(200, JSON.stringify(gateway('view-topology', {
      viewProtocol: 2, kind: 'view-topology', revision: '1', views: [{ id: '1', generation: '1' }],
      locations: [{ scope: { id: '1', generation: '1' }, box: [0, 0, 800, 600] }],
    })));
    await httpMain.flush();
    insist(httpMain.gets().length === 3 && httpMain.posts().length === 1, 'HttpMain must renew /events GET and POST /commit on topology');
    assertHttpReq(httpMain.activeGet(), 'GET', '/events', 'HttpMain GET#3');
    assertHttpReq(httpMain.posts()[0], 'POST', '/commit', 'HttpMain POST#1');
    const commitBody = full(JSON.parse(httpMain.posts()[0].body));
    insist(isDeepStrictEqual(Object.keys(commitBody).sort(), ['focus', 'kind', 'projection', 'requests', 'viewProtocol']) &&
      commitBody.viewProtocol === 1 && commitBody.kind === 'view-commit', 'HttpMain POST /commit must carry 5-field view-commit');
    httpMain.posts()[0].respond(204, '');
    await httpMain.flush();
    httpMain.activeGet().respond(200, JSON.stringify(gateway('native-event', { protocolVersion: 3, kind: 'host-disconnected' })));
    await httpMain.flush();
    insist(httpMain.gets().length === 4 && httpMain.posts().length === 2, 'HttpMain must deliver revocation while closed');
    const inFlightCommit = httpMain.posts()[1];
    assertHttpReq(inFlightCommit, 'POST', '/commit', 'HttpMain POST#2');
    insist(!inFlightCommit.done && !inFlightCommit.aborted, 'HttpMain POST#2 must still be in-flight before GET failure');
    httpMain.activeGet().fail('error');
    await httpMain.flush();
    insist(inFlightCommit.aborted && inFlightCommit.abortCount === 1,
      'HttpMain GET failure must invoke Http.cancel "warlock-ui-post" to abort in-flight POST /commit');
    await httpMain.tick(100);
    insist(httpMain.gets().length === 4 && httpMain.posts().length === 2,
      'HttpMain must permanently stop /events polling and never retry POST after transport error');
  } finally {
    httpMain.close();
  }

  // 7 & 8. HttpBar & HttpPopup: /events GET across 204 (99ms vs 100ms) + closed frame -> open frame focus + DOM click -> /actions POST -> tracker abort & sticky stop
  for (const [bundle, mod, isPopup] of [[httpBarJs, 'HttpBar', false], [httpPopupJs, 'HttpPopup', true]]) {
    const httpEnv = await mountOptimizedElement(bundle, mod);
    try {
      hashes[mod] = httpEnv.sha256;
      insist(!httpEnv.app.ports || Object.keys(httpEnv.app.ports).length === 0, `${mod} must have zero ports`);
      insist(httpEnv.gets().length === 1, `${mod} initial /events GET missing`);
      assertHttpReq(httpEnv.activeGet(), 'GET', '/events', `${mod} GET#1`);
      httpEnv.activeGet().respond(204, '');
      await httpEnv.flush();
      await httpEnv.tick(99);
      insist(httpEnv.gets().length === 1, `${mod} must not poll at 99ms after 204`);
      await httpEnv.tick(100);
      insist(httpEnv.gets().length === 2, `${mod} must resume /events GET at 100ms`);
      assertHttpReq(httpEnv.activeGet(), 'GET', '/events', `${mod} GET#2`);
      httpEnv.activeGet().respond(200, JSON.stringify(gateway('presentation', frame('1', '0', 'closed', 'Ready', [control('bar:applications', 'open-apps', 'Applications')], []))));
      await httpEnv.flush();
      insist(httpEnv.gets().length === 3, `${mod} must continue /events polling across closed presentation`);
      httpEnv.activeGet().respond(204, '');
      await httpEnv.flush();
      await httpEnv.tick(100);
      insist(httpEnv.gets().length === 4, `${mod} must renew /events poll after 204 while closed`);
      httpEnv.activeGet().respond(200, JSON.stringify(gateway('presentation', frame('2', '1', 'applications', 'Ready',
        [control('bar:applications', 'open-apps', 'Applications')],
        [control('control:refresh', 'refresh-apps', 'Refresh')]))));
      await httpEnv.flush();
      const targetId = isPopup ? 'control:refresh' : 'bar:applications';
      const targetDomId = isPopup ? 'refresh-apps' : 'open-apps';
      const btn = walkDom(httpEnv.container, n => n.attributes['data-surface-control'] === targetId);
      insist(btn && typeof btn.listeners.click === 'function', `${mod} must render clickable ${targetId}`);

      // Focus event executes Browser.Dom.focus on matching DOM node without emitting POST
      httpEnv.activeGet().respond(200, JSON.stringify(gateway('focus', {
        focusProtocol: 1, kind: 'focus', surface: isPopup ? 'popup' : 'bar', publication: '2', lease: '1', domId: targetDomId,
      })));
      await httpEnv.flush();
      insist(btn.focusCount === 1 && httpEnv.posts().length === 0, `${mod} accepted focus must focus ${targetDomId} without POST`);

      btn.listeners.click({ type: 'click', target: btn, currentTarget: btn, stopPropagation() {}, preventDefault() {} });
      await httpEnv.flush();
      insist(httpEnv.posts().length === 1, `${mod} click must POST /actions`);
      assertHttpReq(httpEnv.posts()[0], 'POST', '/actions', `${mod} POST#1`);
      insist(isDeepStrictEqual(full(JSON.parse(httpEnv.posts()[0].body)), full({
        surfaceProtocol: 2, kind: 'surface-action', surface: isPopup ? 'popup' : 'bar', publication: '2', lease: '1', id: targetId,
      })), `${mod} POST /actions payload mismatch`);
      httpEnv.posts()[0].respond(204, '');
      await httpEnv.flush();

      // Leave POST#2 in-flight alongside active GET /events to prove mutual tracker cancellation and sticky stop
      btn.listeners.click({ type: 'click', target: btn, currentTarget: btn, stopPropagation() {}, preventDefault() {} });
      await httpEnv.flush();
      const inFlightPost = httpEnv.posts()[1];
      const inFlightGet = httpEnv.activeGet();
      assertHttpReq(inFlightPost, 'POST', '/actions', `${mod} POST#2`);
      assertHttpReq(inFlightGet, 'GET', '/events', `${mod} active GET before stop`);
      const getsBeforeStop = httpEnv.gets().length;
      if (!isPopup) {
        inFlightPost.fail('error');
        await httpEnv.flush();
        insist(inFlightGet.aborted && inFlightGet.abortCount === 1,
          'HttpBar POST failure must invoke Http.cancel "warlock-ui-events" to abort active GET /events');
        insist(httpEnv.container.textContent.includes('UI delivery is unconfirmed. The action will not be repeated. Restart this view to reconnect.'),
          'HttpBar must render sticky unconfirmed-delivery alert');
      } else {
        inFlightGet.respond(200, JSON.stringify(gateway('native-event', { protocolVersion: 3, kind: 'host-disconnected' })));
        await httpEnv.flush();
        insist(inFlightPost.aborted && inFlightPost.abortCount === 1,
          'HttpPopup forbidden event source must invoke Http.cancel "warlock-ui-post" to abort active POST /actions');
        insist(httpEnv.container.textContent.includes('UI event source is not allowed for this role. Restart this view to reconnect.'),
          'HttpPopup must render sticky role-rejection alert');
      }
      await httpEnv.tick(100);
      insist(httpEnv.gets().length === getsBeforeStop && httpEnv.posts().length === 2,
        `${mod} must permanently stop /events polling and never retry POST after failure`);
    } finally {
      httpEnv.close();
    }
  }

  return hashes;
}

async function main() {
  const args = process.argv.slice(2);
  let workerPaths = null;
  let rootBundles = null;
  let skipRoots = false;
  let casesPath = path.join(__dirname, 'tea-subscriptions-cases.cjs');
  let outPath = null;

  let idx = 0;
  while (idx < args.length) {
    if (args[idx] === '--workers') {
      workerPaths = args.slice(idx + 1, idx + 5);
      insist(workerPaths.length === 4, '--workers requires PopupSubReplay.js BarSubReplay.js AdmissionSubReplay.js RendererSubReplay.js');
      idx += 5;
    } else if (args[idx] === '--roots') {
      rootBundles = args.slice(idx + 1, idx + 9);
      insist(rootBundles.length === 8, '--roots requires Main, Bar, Popup, HttpMain, HttpBar, HttpPopup, NativePreviewAdmission, NativePreviewRenderer');
      idx += 9;
    } else if (args[idx] === '--skip-roots') {
      skipRoots = true;
      idx += 1;
    } else if (args[idx] === '--cases') {
      insist(idx + 1 < args.length, '--cases requires path');
      casesPath = path.resolve(args[idx + 1]);
      idx += 2;
    } else if (args[idx] === '--out') {
      insist(idx + 1 < args.length, '--out requires path');
      outPath = path.resolve(args[idx + 1]);
      idx += 2;
    } else {
      throw new Error(`unknown argument: ${args[idx]}`);
    }
  }

  insist(workerPaths, 'usage: node tea-subscriptions.cjs --workers Popup.js Bar.js Admission.js Renderer.js --roots 8-bundles... [--cases cases.cjs] [--out report.json]');
  insist(rootBundles || skipRoots, '--roots (all 8 optimized Browser.element bundles) is required unless --skip-roots is explicitly passed');

  const repoRoot = path.resolve(__dirname, '..', '..', '..');
  const siteMainPath = path.join(repoRoot, 'site', 'src', 'SiteMain.elm');
  let siteMainSha256 = null;
  let siteMainBytePreserved = null;
  if (fs.existsSync(siteMainPath)) {
    const siteMainBytes = fs.readFileSync(siteMainPath);
    siteMainSha256 = hash(siteMainBytes);
    insist(ALLOWED_SITE_MAIN_SHA256.has(siteMainSha256), `SiteMain.elm byte preservation failed: ${siteMainSha256}`);
    insist(/subscriptions\s*=\s*\\_\s*->\s*Sub\.none/.test(siteMainBytes.toString('utf8')), 'SiteMain.elm must retain Sub.none');
    siteMainBytePreserved = true;
  }

  const workerKeys = ['popup', 'bar', 'admission', 'renderer'];
  const workers = {};
  const workerMetadata = {};
  for (let i = 0; i < workerKeys.length; i++) {
    const key = workerKeys[i];
    const spec = WORKER_SPEC[key];
    const resolvedJs = path.resolve(workerPaths[i]);
    const raw = fs.readFileSync(resolvedJs);
    const original = raw.toString('utf8');
    insist(Buffer.from(original, 'utf8').equals(raw), `${spec.moduleName}: fixture is not canonical UTF-8`);
    const patch = instrument(original, spec.moduleName);
    const elmPath = path.join(__dirname, spec.elmFile);
    workers[key] = { moduleName: spec.moduleName, patch };
    workerMetadata[key] = {
      moduleName: spec.moduleName,
      fixtureElmSha256: hash(fs.readFileSync(elmPath)),
      originalFixtureSha256: hash(raw),
      instrumentedFixtureSha256: hash(Buffer.from(patch.changed, 'utf8')),
      patchOffset: patch.insertionOffset,
      patchInsertedBytes: patch.insertedBytes,
      reversiblePatch: true,
    };
  }

  const oracleBytes = fs.readFileSync(casesPath);
  const oracle = loadOracle(oracleBytes, casesPath);
  const coverage = full(oracle.coverage, 'oracle/coverage');
  insist(coverage && typeof coverage.complete === 'boolean' &&
    Array.isArray(coverage.rootsInventoried) && coverage.rootsInventoried.length === 9,
    'explicit 9-root ELM-TEA-004 inventory required in oracle coverage');

  const cases = validateCases(oracle);
  let transitions = 0;
  for (const testCase of cases) {
    const workerInfo = workers[testCase.worker];
    const first = await executeCase(workerInfo, testCase);
    const second = await executeCase(workerInfo, testCase);
    insist(isDeepStrictEqual(first, second), `${testCase.name}: nondeterministic full trace`);
    transitions += testCase.steps.filter(step => step.input.kind !== 'reset').length;
  }

  const optimizedRootHashes = rootBundles ? await verifyOptimizedRoots(rootBundles) : null;

  const summary = {
    schema: 2,
    requirement: 'ELM-TEA-004',
    scenario: 'tea-subscriptions',
    scope: 'QA single-root full-state/effect/subscription-plan replay + compiled 9-root Browser.element runtime port/XHR/timer verification; native behavior qualified separately',
    workers: workerMetadata,
    oracleSha256: hash(oracleBytes),
    runnerSha256: hash(fs.readFileSync(__filename)),
    siteMainSha256,
    siteMainBytePreserved,
    optimizedRootHashes,
    optimizedRootsVerified: Boolean(optimizedRootHashes),
    completeRuntimeBoundary: Boolean(optimizedRootHashes && siteMainBytePreserved),
    marker: MARKER,
    coverageDeclaration: coverage,
    cases: cases.map(c => ({ name: c.name, worker: c.worker })),
    transitions,
    runsPerCase: 2,
    nativeAccepted: false,
    releaseAccepted: false,
    passed: true,
  };
  const json = JSON.stringify(summary, null, 2) + '\n';
  if (outPath) fs.writeFileSync(outPath, json);
  process.stdout.write(json);
}

main().catch(error => {
  process.stderr.write(`tea-subscriptions: ${(error && error.stack) || String(error)}\n`);
  process.exitCode = 1;
});
