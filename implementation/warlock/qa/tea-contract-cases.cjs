'use strict';

/*
 * Independent DesktopPolicy contract cases.  All test inputs and outcomes
 * below are authored from the decoder and reducer contract, not from observed
 * reducer results.  The complete debug representation of each GIVEN must be
 * independently transcribed and reviewed against its pinned source tuple.
 * Never populate this table by recording the test worker's output.
 *
 * The initial GIVEN is a source transcription, not a capture. Its debug
 * constructor representation, including Dict.empty, requires root's compiled
 * artifact qualification. This file is not a complete TEA-002 campaign:
 * receipt histories, all timer tokens and additional positive paths remain required.
 */

const NIL = Object.freeze({ $: '[]' });
const none = () => ({ $: 'Nothing' });
const zero = () => ({ $: 'Counter', a: '0' });
const empty = () => ({ $: '[]' });
const model = value => ({ $: 'Model', a: value });

// Source: Desktop.initial and each domain's named initial/init/empty. Peer
// source transcriptions: terra-graph 6d002350... and terra-engine ffce5a50....
// The debug Dict tag is an explicit prediction, not a runtime observation.
const shell = {
  applicationOnly: false, decoderRefusal: none(), reconciliationFull: false,
  effects: { connected: false, observed: none(), request: zero(), generation: zero(), transaction: none(), unresolved: empty() },
  binding: none(), request: zero(), expected: none(), phase: { $: 'Detached' },
  reconnecting: true, notice: 'Connecting…', geometry: none(), geometryCaps: none(),
  geometryExpected: none(), geometryAttachExpected: none(), attachNeeded: false,
  issued: empty(), notificationQueued: false, projectionRetryQueued: false,
  transportRefused: false, deferNotifications: false, recoveryFailure: none(),
};
const menu = model({ menu: none(), nextMenu: 1, nextIntent: 1, outstanding: empty(),
  releasedUnknown: empty(), lastOutcome: none(), invalidated: empty(), retiredOutputs: empty(), exhausted: false });
const windows = { shell, picker: none(), generation: zero(), menus: model({
  menu, router: model(empty()), provider: none(), prepared: none(), preparedSerial: zero(),
}) };
const launch = model({ host: none(), snapshot: none(), revision: zero(), request: zero(), phase: { $: 'Idle' } });
const desktop = {
  windows, choice: none(), choiceNotice: '', popupOrigin: { $: 'KeyboardEntry' },
  returnFocus: none(), menuOrigin: none(), ownerScope: none(), ownerExhausted: false,
  launch, launchFromApplications: false, applications: none(), applicationPage: 0,
  presentationCapacity: false, query: '', pins: { snapshot: none(), pending: none(), notice: '' },
  pointer: { observation: none() }, shortcuts: { binding: none(), seen: zero() },
  jumpList: { snapshot: none(), pending: none(), spent: empty(), notice: 'Reading application actions…' },
  jumpEntry: none(), jumpOpening: false, jumpExpected: none(), jumpBack: false,
  files: { snapshot: none(), draft: '', pending: none(), spent: empty(), notice: 'Loading Files…' },
  filesOpen: false, filesOpening: false, filesExpected: none(),
  systemMenu: { snapshot: none(), pending: none(), spent: empty(), notice: 'Loading system state…' },
  systemMenuOpen: false, systemMenuOpening: false, systemMenuExpected: none(), systemMenuConfirmation: none(),
  notifications: { focused: none(), outcome: none(), policy: { doNotDisturb: false, interruptCritical: false },
    snapshot: none(), pending: none(), spent: empty(), notice: 'Loading notifications…' },
  notificationsOpen: false, notificationsOpening: false, notificationsExpected: none(), motionExpected: none(),
  motion: { preferences: { snapshot: none(), draft: { $: 'System' }, pending: none(), notice: 'Reading motion preference…' },
    observation: none(), pending: none(), applied: none() },
  settings: { outcome: none(), snapshot: none(), draft: { theme: { $: 'Night' }, textScale: 100,
    effectsOff: false, reducedTransparency: false }, pending: none(), notice: 'Loading settings…' },
  settingsOpen: false, settingsOpening: false, settingsExpected: none(), settingsHelp: true,
  shortcutPreferences: { snapshot: none(), inventory: none(), draft: { applications: { $: 'Undecided' },
    system: { $: 'Undecided' }, notifications: { $: 'Undecided' } }, pending: none(), conflicts: empty(),
    notice: 'Loading shortcut choices…' },
  shortcutExpected: none(), open: false, overview: false, overviewWorkspace: none(), overviewRecovery: { $: 'Idle' },
  workspaceInventory: none(), workspaceNavigation: { binding: none(), ready: false, request: zero(), generation: zero(),
    record: none(), recovering: false, origin: none(), returning: false },
  overviewTransfer: none(), snap: none(), switcher: model({ generation: zero(), phase: { $: 'Idle' },
    steps: { $: 'RBEmpty_elm_builtin' }, released: none(), ready: false, entries: empty(), ring: empty(),
    origin: none(), selected: 0, baseline: none() }),
  nativeSwitcher: none(), switcherOrigin: none(), switcherExpected: none(), switcherHistory: none(),
  request: zero(), presentation: { $: 'Just', a: zero() }, expected: none(), adapterNotice: none(),
  catalogFailure: none(), catalogOpening: false,
};
const controller = model({ recovery: { slots: empty(), legacy: empty(), informational: none() },
  desktop, publication: zero(), lease: zero(), exhausted: false });
const initial = { controller: model({ announcements: { $: 'Model', a: zero(), b: none() },
  controller, revision: zero(), highest: zero(), views: empty(), locations: empty(), selected: none(),
  batches: empty(), batchExhausted: false, capacityRefused: false }) };
const GIVENS = Object.freeze({ initial });

function object(value) {
  return value !== null && typeof value === 'object' && !Array.isArray(value);
}

function equalLiteral(left, right) {
  if (Object.is(left, right)) return true;
  if (typeof left !== typeof right || left === null || right === null ||
      typeof left !== 'object' || Array.isArray(left) !== Array.isArray(right)) return false;
  const leftKeys = Object.keys(left).sort();
  const rightKeys = Object.keys(right).sort();
  return leftKeys.length === rightKeys.length && leftKeys.every((key, i) =>
    key === rightKeys[i] && equalLiteral(left[key], right[key]));
}

// Copy and validate every leaf.  The runner uses this complete raw debug tree;
// no serialization shortcut is permitted to erase undefined, accessors,
// symbols, functions, nonfinite numbers, cycles, or unsupported host values.
function cloneLiteral(value, ancestors = new Set()) {
  if (value === null || typeof value === 'string' || typeof value === 'boolean') return value;
  if (typeof value === 'number' && Number.isFinite(value)) return value;
  if (!object(value) && !Array.isArray(value)) throw new Error('unsupported literal value');
  if (ancestors.has(value)) throw new Error('cyclic literal value');
  if (Object.getOwnPropertySymbols(value).length) throw new Error('symbol in literal');
  const proto = Object.getPrototypeOf(value);
  if (Array.isArray(value) ? proto !== Array.prototype : proto !== Object.prototype) {
    throw new Error('unsupported literal prototype');
  }
  const next = new Set(ancestors);
  next.add(value);
  const descriptors = Object.getOwnPropertyDescriptors(value);
  for (const [key, desc] of Object.entries(descriptors)) {
    if (key === 'length' && Array.isArray(value)) continue;
    if (!Object.prototype.hasOwnProperty.call(desc, 'value') || !desc.enumerable) {
      throw new Error('non-data or hidden literal property: ' + key);
    }
  }
  if (Array.isArray(value)) {
    const keys = Object.keys(value);
    if (keys.length !== value.length || keys.some((key, i) => key !== String(i))) {
      throw new Error('sparse or extended array');
    }
    return value.map(item => cloneLiteral(item, next));
  }
  const copy = {};
  for (const key of Object.keys(value).sort()) {
    if (key === '__proto__' || key === 'constructor' || key === 'prototype') {
      throw new Error('unsafe literal property');
    }
    copy[key] = cloneLiteral(value[key], next);
  }
  return copy;
}

// Immutable, exact path replacement for an independently supplied positive
// transition.  Old and new values are both literals; absent paths, ambiguous
// duplicate writes and unexpected original values are failures.  This cannot
// manufacture expectations from a worker capture or silently omit siblings.
function literalPatches(given, patches) {
  const result = cloneLiteral(given);
  if (!Array.isArray(patches) || patches.length === 0) throw new Error('missing literal changes');
  const seen = new Set();
  for (const patch of patches) {
    if (!object(patch) || !Array.isArray(patch.path) || patch.path.length === 0 ||
        !Object.prototype.hasOwnProperty.call(patch, 'before') ||
        !Object.prototype.hasOwnProperty.call(patch, 'after')) throw new Error('bad literal patch');
    let target = result;
    for (let i = 0; i < patch.path.length; i++) {
      const key = patch.path[i];
      if (typeof key !== 'string' || key === '__proto__' || key === 'constructor' ||
          key === 'prototype' || !object(target) ||
          !Object.prototype.hasOwnProperty.call(target, key)) throw new Error('missing literal path');
      if (i === patch.path.length - 1) {
        const path = JSON.stringify(patch.path);
        if (seen.has(path)) throw new Error('duplicate literal path');
        seen.add(path);
        if (!equalLiteral(cloneLiteral(target[key]), cloneLiteral(patch.before))) {
          throw new Error('literal patch precondition differs: ' + path);
        }
        target[key] = cloneLiteral(patch.after);
      } else target = target[key];
    }
  }
  return result;
}

// Each input is rejected by DesktopPolicy.incomingEvent before OutputController
// is invoked.  Therefore the literal expected transition is the *entire*
// pinned initial model unchanged and exactly the empty Elm effect list.
// These do not assert that a malformed inner native envelope is a no-op.
const invalidEnvelopes = [
  ['outer-not-object', null],
  ['outer-missing-version', { kind: 'native-event', payload: {} }],
  ['outer-version-string', { bridgeProtocol: '1', kind: 'native-event', payload: {} }],
  ['outer-wrong-version', { bridgeProtocol: 2, kind: 'native-event', payload: {} }],
  ['outer-unknown-kind', { bridgeProtocol: 1, kind: 'native-unknown', payload: {} }],
  ['outer-missing-payload', { bridgeProtocol: 1, kind: 'native-event' }],
  ['outer-extra-field', { bridgeProtocol: 1, kind: 'native-event', payload: {}, extra: true }],
];

// These reach the actual OutputController topology decoder.  A zero revision,
// noncanonical counter, out-of-range counter or numeric counter is refused;
// no frame, registration, request, focus, or timer is emitted.
const invalidTopologies = [
  ['topology-zero-revision', '0'],
  ['topology-leading-zero', '01'],
  ['topology-counter-overflow', '18446744073709551616'],
  ['topology-negative-counter', '-1'],
  ['topology-numeric-counter', 9007199254740992],
];

function topology(revision) {
  return { bridgeProtocol: 1, kind: 'view-topology', payload: {
    viewProtocol: 1, kind: 'view-topology', revision, views: [],
  } };
}

// Independently source-derived detached/empty-topology transition. Two
// Desktop.windowBase calls advance presentation and Launch.revision; the two
// SurfaceController publications advance independently. No source code from
// the reducer or captured output is used to construct these expectations.
const topologyChanges = Object.freeze([
  { path: ['controller', 'a', 'revision'], before: zero(), after: { $: 'Counter', a: '1' } },
  { path: ['controller', 'a', 'controller', 'a', 'publication'], before: zero(), after: { $: 'Counter', a: '2' } },
  { path: ['controller', 'a', 'controller', 'a', 'desktop', 'presentation'],
    before: { $: 'Just', a: zero() }, after: { $: 'Just', a: { $: 'Counter', a: '2' } } },
  { path: ['controller', 'a', 'controller', 'a', 'desktop', 'launch', 'a', 'revision'],
    before: zero(), after: { $: 'Counter', a: '2' } },
]);
const topologyPacket = {
  viewProtocol: 1, kind: 'view-commit', requests: [], focus: [],
  projection: {
    viewProtocol: 1, kind: 'view-frame', revision: '1', views: [], focusOwner: null,
    popupOwner: null, announcer: null, announcement: null,
    frame: {
      surfaceProtocol: 2, keyboardParent: true, motion: 'reduced',
      appearance: { theme: 'night', textScale: 100, effectsOff: false, reducedTransparency: false },
      publication: '2', lease: '0', mode: 'closed', status: 'Connecting…', popup: [],
      bar: [
        { id: 'bar:reconnect', domId: 'reconnect', label: 'Reconnect', ariaLabel: 'Reconnect to the window system', detail: '', enabled: false, focusOnly: false },
        { id: 'bar:overview', domId: 'applications:detached:2:control:overview-opener', label: 'Task View', ariaLabel: 'Open Task View', detail: '', enabled: false, focusOnly: false },
        { id: 'bar:switcher', domId: 'applications:detached:2:control:switcher-opener', label: 'Switch windows', ariaLabel: 'Open window switcher', detail: '', enabled: false, focusOnly: false },
        { id: 'bar:notifications', domId: 'applications:detached:2:notifications:opener', label: 'Notifications', ariaLabel: 'Open notifications', detail: '', enabled: false, focusOnly: false },
        { id: 'bar:files', domId: 'applications:detached:2:files:opener', label: 'Files', ariaLabel: 'Open Files menu', detail: '', enabled: false, focusOnly: false },
        { id: 'bar:system', domId: 'applications:detached:2:system:opener', label: 'System', ariaLabel: 'Open system menu', detail: '', enabled: false, focusOnly: false },
        { id: 'bar:settings', domId: 'applications:detached:2:settings:opener', label: 'Settings', ariaLabel: 'Open settings', detail: '', enabled: false, focusOnly: false },
      ],
    },
  },
};
// Debug Json.Encode.Value is predicted as {$:0,a:raw}; the exact root-built
// artifact must be inspected. A mismatch fails comparison, never unwraps data.
const topologyEffects = { $: '::', a: { $: 'Publish', a: { $: 0, a: topologyPacket } }, b: NIL };
const oneScope = { $: 'Scope', a: { $: 'Counter', a: '1' }, b: { $: 'Counter', a: '1' } };
const oneScopeJson = { id: '1', generation: '1' };
const oneViewInput = { bridgeProtocol: 1, kind: 'view-topology', payload: {
  viewProtocol: 1, kind: 'view-topology', revision: '1', views: [oneScopeJson],
} };
const oneViewChanges = Object.freeze([
  { path: ['controller', 'a', 'highest'], before: zero(), after: { $: 'Counter', a: '1' } },
  { path: ['controller', 'a', 'views'], before: empty(), after: { $: '::', a: oneScope, b: empty() } },
  { path: ['controller', 'a', 'selected'], before: none(), after: { $: 'Just', a: oneScope } },
  { path: ['controller', 'a', 'controller', 'a', 'desktop', 'ownerScope'], before: none(), after: {
    $: 'Just', a: { outputId: { $: 'Counter', a: '1' }, providerId: { $: 'Counter', a: '1' } },
  } },
]);
const bindingJson = { lifetime: '1', session: '1', frontend: '1' };
const binding = { $: 'Binding', a: { $: 'Counter', a: '1' }, b: { $: 'Counter', a: '1' }, c: { $: 'Counter', a: '1' } };
const host = '{"lifetime":"1","session":"1","frontend":"1"}';
// Key insertion order here is the source order used by Elm's E.encode 0.
// In addition to structural JSON equality the retained batch's wire string is
// compared byte-for-byte, so sorting, projection, or replay cannot forge it.
const attachedPacket = {
  viewProtocol: 1, kind: 'view-commit', projection: {
    viewProtocol: 1, kind: 'view-frame', revision: '1', views: [oneScopeJson],
    focusOwner: oneScopeJson, popupOwner: null, frame: {
      surfaceProtocol: 2, keyboardParent: true, motion: 'reduced',
      appearance: { theme: 'night', textScale: 100, effectsOff: false, reducedTransparency: false },
      publication: '4', lease: '0', mode: 'closed', status: 'Applications connected. Window controls unavailable.',
      bar: [
        { id: 'bar:applications', domId: 'applications:' + host + ':3:control:opener', label: 'Applications', ariaLabel: 'Open applications', detail: '', enabled: true, focusOnly: false },
        { id: 'bar:overview', domId: 'applications:' + host + ':3:control:overview-opener', label: 'Task View', ariaLabel: 'Open Task View', detail: '', enabled: false, focusOnly: false },
        { id: 'bar:switcher', domId: 'applications:' + host + ':3:control:switcher-opener', label: 'Switch windows', ariaLabel: 'Open window switcher', detail: '', enabled: false, focusOnly: false },
        { id: 'bar:notifications', domId: 'applications:' + host + ':3:notifications:opener', label: 'Notifications', ariaLabel: 'Open notifications', detail: '', enabled: false, focusOnly: false },
        { id: 'bar:files', domId: 'applications:' + host + ':3:files:opener', label: 'Files', ariaLabel: 'Open Files menu', detail: '', enabled: false, focusOnly: false },
        { id: 'bar:system', domId: 'applications:' + host + ':3:system:opener', label: 'System', ariaLabel: 'Open system menu', detail: '', enabled: false, focusOnly: false },
        { id: 'bar:settings', domId: 'applications:' + host + ':3:settings:opener', label: 'Settings', ariaLabel: 'Open settings', detail: '', enabled: false, focusOnly: false },
      ], popup: [],
    }, announcer: { scope: oneScopeJson, surface: 'bar' }, announcement: null,
  }, requests: [{ protocolVersion: 3, kind: 'catalog-request', binding: bindingJson, requestId: '1' }], focus: [],
};
const attachedWire = JSON.stringify(attachedPacket);
const one = { $: 'Counter', a: '1' };
const attachedBatch = {
  scope: oneScope, revision: one, publication: { $: 'Counter', a: '4' }, lease: zero(), binding,
  wire: attachedWire, observations: empty(), operations: empty(),
  catalogs: { $: '::', a: { binding, request: one }, b: empty() },
};
const attachedChanges = Object.freeze([
  { path: ['controller', 'a', 'controller', 'a', 'publication'], before: { $: 'Counter', a: '3' }, after: { $: 'Counter', a: '4' } },
  { path: ['controller', 'a', 'controller', 'a', 'desktop', 'presentation'], before: { $: 'Just', a: { $: 'Counter', a: '2' } }, after: { $: 'Just', a: { $: 'Counter', a: '3' } } },
  { path: ['controller', 'a', 'controller', 'a', 'desktop', 'request'], before: zero(), after: one },
  { path: ['controller', 'a', 'controller', 'a', 'desktop', 'expected'], before: none(), after: { $: 'Just', a: one } },
  { path: ['controller', 'a', 'controller', 'a', 'desktop', 'workspaceNavigation', 'binding'], before: none(), after: { $: 'Just', a: binding } },
  { path: ['controller', 'a', 'controller', 'a', 'desktop', 'launch', 'a', 'revision'], before: { $: 'Counter', a: '2' }, after: { $: 'Counter', a: '4' } },
  { path: ['controller', 'a', 'controller', 'a', 'desktop', 'launch', 'a', 'host'], before: none(), after: { $: 'Just', a: host } },
  { path: ['controller', 'a', 'controller', 'a', 'desktop', 'windows', 'shell', 'applicationOnly'], before: false, after: true },
  { path: ['controller', 'a', 'controller', 'a', 'desktop', 'windows', 'shell', 'binding'], before: none(), after: { $: 'Just', a: binding } },
  { path: ['controller', 'a', 'controller', 'a', 'desktop', 'windows', 'shell', 'phase'], before: { $: 'Detached' }, after: { $: 'Reconciling' } },
  { path: ['controller', 'a', 'controller', 'a', 'desktop', 'windows', 'shell', 'reconnecting'], before: true, after: false },
  { path: ['controller', 'a', 'controller', 'a', 'desktop', 'windows', 'shell', 'notice'], before: 'Connecting…', after: 'Applications connected. Window controls unavailable.' },
  { path: ['controller', 'a', 'batches'], before: empty(), after: { $: '::', a: attachedBatch, b: empty() } },
]);
const attachInput = { kind: 'incoming', value: { bridgeProtocol: 1, kind: 'native-event', payload: {
  protocolVersion: 3, kind: 'application-attached', binding: bindingJson, nativeOperations: [],
} } };
const mismatchCertificates = [
  ['scope', { scope: { id: '2', generation: '1' } }],
  ['revision', { revision: '2' }], ['publication', { publication: '5' }], ['lease', { lease: '1' }],
  ['binding', { binding: { lifetime: '1', session: '1', frontend: '2' } }],
  ['wire', { batch: attachedWire + ' ' }],
];
function mismatchInput(change) {
  return { kind: 'incoming', value: { bridgeProtocol: 1, kind: 'view-disposition', payload: {
    viewProtocol: 1, kind: 'batch-disposition', disposition: 'preflight-unsent', scope: oneScopeJson,
    revision: '1', publication: '4', lease: '0', binding: bindingJson, batch: attachedWire, ...change,
  } } };
}
const matchedDisposition = mismatchInput({});
const catalogSnapshot = { $: 'Snapshot', a: one, b: one, c: { $: 'RBEmpty_elm_builtin' } };
const matchingCatalog = { kind: 'incoming', value: { bridgeProtocol: 1, kind: 'native-event', payload: {
  protocolVersion: 3, kind: 'application-catalog', binding: bindingJson, requestId: '1',
  snapshot: { catalogProtocol: 1, lifetime: '1', generation: '1', entries: [] },
  preferences: { revision: '1', identities: [] },
} } };
const catalogSuccessChanges = Object.freeze([
  { path: ['controller', 'a', 'controller', 'a', 'publication'], before: { $: 'Counter', a: '4' }, after: { $: 'Counter', a: '5' } },
  { path: ['controller', 'a', 'controller', 'a', 'desktop', 'presentation'], before: { $: 'Just', a: { $: 'Counter', a: '3' } }, after: { $: 'Just', a: { $: 'Counter', a: '4' } } },
  { path: ['controller', 'a', 'controller', 'a', 'desktop', 'expected'], before: { $: 'Just', a: one }, after: none() },
  { path: ['controller', 'a', 'controller', 'a', 'desktop', 'applications'], before: none(), after: { $: 'Just', a: catalogSnapshot } },
  { path: ['controller', 'a', 'controller', 'a', 'desktop', 'pins', 'snapshot'], before: none(), after: { $: 'Just', a: { revision: one, identities: empty() } } },
  { path: ['controller', 'a', 'controller', 'a', 'desktop', 'launch', 'a', 'revision'], before: { $: 'Counter', a: '4' }, after: { $: 'Counter', a: '5' } },
  { path: ['controller', 'a', 'controller', 'a', 'desktop', 'launch', 'a', 'snapshot'], before: none(), after: { $: 'Just', a: catalogSnapshot } },
]);
const disconnectedText = 'Window adapter unavailable. Reconnect to read current state. Unconfirmed actions will not be repeated.';
const disconnectedCorrelation = '{"outcome":"adapter-unavailable","binding":{"lifetime":"1","session":"1","frontend":"1"},"identity":{"adapter":"windows","request":"0","service":null,"revision":null}}';
const disconnectedChanges = Object.freeze([
  { path: ['controller', 'a', 'controller', 'a', 'publication'], before: { $: 'Counter', a: '4' }, after: { $: 'Counter', a: '5' } },
  { path: ['controller', 'a', 'controller', 'a', 'desktop', 'presentation'], before: { $: 'Just', a: { $: 'Counter', a: '3' } }, after: { $: 'Just', a: { $: 'Counter', a: '4' } } },
  { path: ['controller', 'a', 'controller', 'a', 'desktop', 'expected'], before: { $: 'Just', a: one }, after: none() },
  { path: ['controller', 'a', 'controller', 'a', 'desktop', 'workspaceNavigation', 'binding'], before: { $: 'Just', a: binding }, after: none() },
  { path: ['controller', 'a', 'controller', 'a', 'desktop', 'launch', 'a', 'revision'], before: { $: 'Counter', a: '4' }, after: { $: 'Counter', a: '5' } },
  { path: ['controller', 'a', 'controller', 'a', 'desktop', 'launch', 'a', 'host'], before: { $: 'Just', a: host }, after: none() },
  { path: ['controller', 'a', 'controller', 'a', 'desktop', 'windows', 'shell', 'applicationOnly'], before: true, after: false },
  { path: ['controller', 'a', 'controller', 'a', 'desktop', 'windows', 'shell', 'phase'], before: { $: 'Reconciling' }, after: { $: 'Detached' } },
  { path: ['controller', 'a', 'controller', 'a', 'desktop', 'windows', 'shell', 'notice'], before: 'Applications connected. Window controls unavailable.', after: 'Connection lost. Reconnect to continue.' },
  { path: ['controller', 'a', 'controller', 'a', 'desktop', 'adapterNotice'], before: none(), after: { $: 'Just', a: {
    source: { $: 'Windows' }, binding, request: zero(), service: none(), revision: none(),
  } } },
  { path: ['controller', 'a', 'announcements', 'a'], before: zero(), after: one },
  { path: ['controller', 'a', 'announcements', 'b'], before: none(), after: { $: 'Just', a: {
    interrupt: false, sequence: one, correlation: disconnectedCorrelation, text: disconnectedText,
  } } },
]);
const reconnectInput = { kind: 'incoming', value: { bridgeProtocol: 1, kind: 'view-action', payload: {
  viewProtocol: 1, kind: 'view-action', scope: oneScopeJson, action: {
    surfaceProtocol: 2, kind: 'surface-action', surface: 'bar', publication: '5', lease: '0',
    id: 'bar:reconnect', trigger: 'keyboard',
  },
} } };
const reconnectChanges = Object.freeze([
  { path: ['controller', 'a', 'controller', 'a', 'publication'], before: { $: 'Counter', a: '5' }, after: { $: 'Counter', a: '6' } },
  { path: ['controller', 'a', 'controller', 'a', 'desktop', 'presentation'], before: { $: 'Just', a: { $: 'Counter', a: '4' } }, after: { $: 'Just', a: { $: 'Counter', a: '5' } } },
  { path: ['controller', 'a', 'controller', 'a', 'desktop', 'launch', 'a', 'revision'], before: { $: 'Counter', a: '5' }, after: { $: 'Counter', a: '6' } },
  { path: ['controller', 'a', 'controller', 'a', 'desktop', 'windows', 'shell', 'reconnecting'], before: false, after: true },
  { path: ['controller', 'a', 'controller', 'a', 'desktop', 'windows', 'shell', 'notice'], before: 'Connection lost. Reconnect to continue.', after: 'Reconnecting…' },
]);
const unavailableText = 'Applications unavailable. Refresh applications, then choose again.';
const unavailableCorrelation = '{"outcome":"adapter-unavailable","binding":{"lifetime":"1","session":"1","frontend":"1"},"identity":{"adapter":"applications","request":"1","service":null,"revision":null}}';
const refusedChanges = Object.freeze([
  { path: ['controller', 'a', 'batches'], before: { $: '::', a: attachedBatch, b: empty() }, after: empty() },
  { path: ['controller', 'a', 'controller', 'a', 'publication'], before: { $: 'Counter', a: '4' }, after: { $: 'Counter', a: '5' } },
  { path: ['controller', 'a', 'controller', 'a', 'desktop', 'expected'], before: { $: 'Just', a: one }, after: none() },
  { path: ['controller', 'a', 'controller', 'a', 'desktop', 'catalogFailure'], before: none(), after: { $: 'Just', a: { binding, request: one } } },
  { path: ['controller', 'a', 'controller', 'a', 'desktop', 'adapterNotice'], before: none(), after: { $: 'Just', a: {
    source: { $: 'Applications' }, binding, request: one, service: none(), revision: none(),
  } } },
  { path: ['controller', 'a', 'announcements', 'a'], before: zero(), after: one },
  { path: ['controller', 'a', 'announcements', 'b'], before: none(), after: { $: 'Just', a: {
    interrupt: false, sequence: one, correlation: unavailableCorrelation, text: unavailableText,
  } } },
]);

const baseCases = Object.freeze([
  Object.freeze({ name: 'empty-topology-publishes-complete-frame', given: 'initial',
    input: Object.freeze({ kind: 'incoming', value: topology('1') }), expected: 'empty-topology-publish',
    topologyRevision: '1', post: Object.freeze({ kind: 'incoming', value: topology('1') }) }),
  Object.freeze({ name: 'topology-full-width-9007199254740993', given: 'initial',
    input: Object.freeze({ kind: 'incoming', value: topology('9007199254740993') }),
    expected: 'empty-topology-publish', topologyRevision: '9007199254740993' }),
  Object.freeze({ name: 'topology-maximum-then-overflow', given: 'initial',
    input: Object.freeze({ kind: 'incoming', value: topology('18446744073709551615') }),
    expected: 'empty-topology-publish', topologyRevision: '18446744073709551615',
    post: Object.freeze({ kind: 'incoming', value: topology('18446744073709551616') }) }),
  Object.freeze({ name: 'one-view-topology-assigns-owner', given: 'initial',
    input: Object.freeze({ kind: 'incoming', value: oneViewInput }), expected: 'one-view-topology' }),
  ...mismatchCertificates.map(([field, change]) => Object.freeze({
    name: 'pending-catalog-disposition-mismatch-' + field, given: 'initial',
    input: Object.freeze({ kind: 'incoming', value: oneViewInput }), expected: 'one-view-then-attached-mismatch',
    mismatch: mismatchInput(change),
  })),
  Object.freeze({ name: 'pending-catalog-mismatched-domain-receipt', given: 'initial',
    input: Object.freeze({ kind: 'incoming', value: oneViewInput }), expected: 'one-view-then-attached-mismatch',
    mismatch: { kind: 'incoming', value: { bridgeProtocol: 1, kind: 'native-event', payload: {
      protocolVersion: 3, kind: 'application-catalog', binding: bindingJson, requestId: '2',
      snapshot: { catalogProtocol: 1, lifetime: '1', generation: '1', entries: [] }, preferences: null,
    } } } }),
  Object.freeze({ name: 'catalog-preflight-refusal-no-replay', given: 'initial',
    input: Object.freeze({ kind: 'incoming', value: oneViewInput }), expected: 'one-view-then-attach-refusal' }),
  Object.freeze({ name: 'catalog-matched-read-then-stale-receipt', given: 'initial',
    input: Object.freeze({ kind: 'incoming', value: oneViewInput }), expected: 'one-view-then-catalog-success' }),
  Object.freeze({ name: 'catalog-pending-disconnect-rejects-late-receipt', given: 'initial',
    input: Object.freeze({ kind: 'incoming', value: oneViewInput }), expected: 'one-view-then-catalog-disconnect' }),
  ...invalidEnvelopes.map(([name, value]) => Object.freeze({
    name, given: 'initial', input: Object.freeze({ kind: 'incoming', value }),
    expected: 'unchanged-and-no-effects',
  })),
  ...invalidTopologies.map(([name, revision]) => Object.freeze({
    name, given: 'initial', input: Object.freeze({ kind: 'incoming', value: topology(revision) }),
    expected: 'unchanged-and-no-effects',
  })),
]);

function materialize(record) {
  if (pinCases.includes(record) || additionalCases.includes(record)) return cloneLiteral(record);
  if (!record || !baseCases.includes(record)) throw new Error('unknown independent contract case');
  if (!Object.prototype.hasOwnProperty.call(GIVENS, record.given)) {
    throw new Error('TEA contract incomplete: independently pinned full GIVEN missing: ' + record.given);
  }
  const initial = cloneLiteral(GIVENS[record.given]);
  let after;
  let effects;
  if (record.expected === 'unchanged-and-no-effects') {
    after = cloneLiteral(initial);
    effects = cloneLiteral(NIL);
  } else if (record.expected === 'empty-topology-publish') {
    const allowed = ['1', '9007199254740993', '18446744073709551615'];
    if (!allowed.includes(record.topologyRevision)) throw new Error('unknown literal topology revision');
    const changes = cloneLiteral(topologyChanges);
    changes[0].after = { $: 'Counter', a: record.topologyRevision };
    after = literalPatches(initial, changes);
    effects = cloneLiteral(topologyEffects);
    effects.a.a.a.projection.revision = record.topologyRevision;
  } else if (record.expected === 'one-view-topology' || record.expected === 'one-view-then-attached-mismatch' ||
             record.expected === 'one-view-then-attach-refusal' || record.expected === 'one-view-then-catalog-success' ||
             record.expected === 'one-view-then-catalog-disconnect') {
    const changes = cloneLiteral(topologyChanges);
    changes[1].after = { $: 'Counter', a: '3' };
    after = literalPatches(initial, changes.concat(cloneLiteral(oneViewChanges)));
    effects = cloneLiteral(topologyEffects);
    const projection = effects.a.a.a.projection;
    projection.views = [cloneLiteral(oneScopeJson)];
    projection.focusOwner = cloneLiteral(oneScopeJson);
    projection.announcer = { scope: cloneLiteral(oneScopeJson), surface: 'bar' };
    projection.frame.publication = '3';
  } else throw new Error('unsupported expectation');
  const steps = [
      { input: { kind: 'reset' }, expected: { state: cloneLiteral(initial), effects: cloneLiteral(NIL) } },
      { input: cloneLiteral(record.input), expected: { state: after, effects } },
  ];
  if (record.expected === 'one-view-then-attached-mismatch' || record.expected === 'one-view-then-attach-refusal' ||
      record.expected === 'one-view-then-catalog-success' || record.expected === 'one-view-then-catalog-disconnect') {
    const attached = literalPatches(after, attachedChanges);
    const attachedEffects = { $: '::', a: { $: 'Publish', a: { $: 0, a: attachedPacket } }, b: NIL };
    steps.push({ input: cloneLiteral(attachInput), expected: { state: cloneLiteral(attached), effects: cloneLiteral(attachedEffects) } });
    if (record.expected === 'one-view-then-attached-mismatch') {
      steps.push({ input: cloneLiteral(record.mismatch), expected: { state: cloneLiteral(attached), effects: cloneLiteral(NIL) } });
    } else if (record.expected === 'one-view-then-attach-refusal') {
      const refused = literalPatches(attached, refusedChanges);
      const refusalEffect = cloneLiteral(attachedEffects);
      const commit = refusalEffect.a.a.a;
      commit.requests = [];
      commit.projection.frame.publication = '5';
      commit.projection.frame.status = 'Applications were not opened. Choose Applications again.';
      commit.projection.announcement = { interrupt: false, sequence: '1', correlation: unavailableCorrelation, text: unavailableText };
      steps.push({ input: cloneLiteral(matchedDisposition), expected: { state: cloneLiteral(refused), effects: refusalEffect } });
      steps.push({ input: cloneLiteral(matchedDisposition), expected: { state: cloneLiteral(refused), effects: cloneLiteral(NIL) } });
    } else if (record.expected === 'one-view-then-catalog-success') {
      const read = literalPatches(attached, catalogSuccessChanges);
      const readEffect = cloneLiteral(attachedEffects);
      const commit = readEffect.a.a.a;
      commit.requests = [];
      commit.projection.frame.publication = '5';
      for (const control of commit.projection.frame.bar) {
        control.domId = control.domId.replace(':3:', ':4:');
      }
      steps.push({ input: cloneLiteral(matchingCatalog), expected: { state: cloneLiteral(read), effects: readEffect } });
      steps.push({ input: cloneLiteral(matchingCatalog), expected: { state: cloneLiteral(read), effects: cloneLiteral(NIL) } });
    } else {
      const disconnected = literalPatches(attached, disconnectedChanges);
      const disconnectedEffect = cloneLiteral(attachedEffects);
      const commit = disconnectedEffect.a.a.a;
      commit.requests = [];
      commit.projection.frame.publication = '5';
      commit.projection.frame.status = 'Connection lost. Reconnect to continue.';
      commit.projection.frame.bar[0] = { id: 'bar:reconnect', domId: 'reconnect', label: 'Reconnect',
        ariaLabel: 'Reconnect to the window system', detail: '', enabled: true, focusOnly: false };
      for (const control of commit.projection.frame.bar.slice(1)) {
        control.domId = control.domId.replace(':3:', ':4:');
        if (['bar:notifications', 'bar:files', 'bar:system', 'bar:settings'].includes(control.id)) control.enabled = true;
      }
      commit.projection.announcement = { interrupt: false, sequence: '1', correlation: disconnectedCorrelation, text: disconnectedText };
      steps.push({ input: { kind: 'transportLost' }, expected: { state: cloneLiteral(disconnected), effects: disconnectedEffect } });
      steps.push({ input: cloneLiteral(matchingCatalog), expected: { state: cloneLiteral(disconnected), effects: cloneLiteral(NIL) } });
      const reconnecting = literalPatches(disconnected, reconnectChanges);
      const reconnectEffect = cloneLiteral(disconnectedEffect);
      const reconnectCommit = reconnectEffect.a.a.a;
      reconnectCommit.requests = [{ protocolVersion: 3, kind: 'host-reconnect' }];
      reconnectCommit.projection.frame.publication = '6';
      reconnectCommit.projection.frame.status = 'Reconnecting…';
      reconnectCommit.projection.frame.bar[0].enabled = false;
      for (const control of reconnectCommit.projection.frame.bar.slice(1)) {
        control.domId = control.domId.replace(':4:', ':5:');
      }
      steps.push({ input: cloneLiteral(reconnectInput), expected: { state: reconnecting, effects: reconnectEffect } });
    }
  }
  if (record.post !== undefined) {
    steps.push({ input: cloneLiteral(record.post), expected: { state: cloneLiteral(after), effects: cloneLiteral(NIL) } });
  }
  return { name: record.name, steps };
}

const coverage = Object.freeze({
  complete: false,
  supported: Object.freeze(['outer-bridge-refusal', 'topology-initial-positive', 'topology-stale', 'uint64-revision-boundaries',
    'catalog-pending', 'mismatched-batch-disposition', 'mismatched-catalog-receipt', 'catalog-matched-read',
    'catalog-preflight-refusal-no-replay', 'catalog-disconnect-late-receipt',
    'pin-pending-mutation', 'pin-refused-mutation-receipt', 'pin-saved-receipt',
    'pin-unknown-reservation-no-replay', 'pin-unknown-read-reconciliation',
    'window-pending-mutation', 'window-committed-receipt', 'window-refused-mutation-receipt',
    'disconnect-unknown-no-replay', 'rebind', 'exact-reachable-delay',
    'pending-preference-finite-status', 'pending-preference-positive-outcomes',
    'pending-settings-ux-feedback']),
  missing: Object.freeze(['whole-frontend-contract-review']),
  note: 'Component inputs only; full original TEA-002 coverage and debug-artifact qualification remain open.',
});

'use strict';
// Source-derived QA draft, NOT RUN. Integrator supplies the independent
// source-transcribed canonical initial/topology/attachment literals and the
// strict cloneLiteral/literalPatches helpers from tea-contract-cases.cjs.
// No test expectation may come from the replay worker's captured values.
// The hidden sanitized prelude must be run from Policy.initial by the worker;
// its full final GIVEN + last full effect are compared, but its intermediate
// steps are setup rather than tested transitions. Full debug encoding and
// source/artifact hashes require Root qualification.
function buildPinCases(c) {
  const { cloneLiteral: copy, literalPatches: patch, initial, topologyChanges,
    oneViewChanges, attachedChanges, oneScope, oneScopeJson, binding, bindingJson,
    attachedBatch, host, empty, none, zero, NIL } = c;
  if ([copy, patch, initial, topologyChanges, oneViewChanges, attachedChanges,
       oneScope, oneScopeJson, binding, bindingJson, attachedBatch, host, empty,
       none, zero, NIL].some(value => value === undefined)) {
    throw new Error('independent full GIVEN dependencies required');
  }
  const counter = text => ({ $: 'Counter', a: text });
  const just = value => ({ $: 'Just', a: value });
  const list = values => values.reduceRight((tail, value) => ({ $: '::', a: value, b: tail }), empty());
  const scopeJson = { id: '1', generation: '1' };
  const givenIdentities = ['alpha', 'beta'];
  const desiredIdentities = ['beta', 'alpha'];
  const row = (id, domId, label, ariaLabel, detail, enabled) =>
    ({ id, domId, label, ariaLabel, detail, enabled, focusOnly: false });
  const prefix = n => 'applications:' + host + ':' + n + ':';
  const barRows = (presentation, order) => {
    const p = prefix(presentation);
    return order.map(id => row('bar:pin:' + id, p + 'pin:' + id, id,
      'Unavailable application: ' + id, 'Unavailable application: ', false)).concat([
      row('bar:applications', p + 'control:opener', 'Applications', 'Open applications', '', true),
      row('bar:overview', p + 'control:overview-opener', 'Task View', 'Open Task View', '', false),
      row('bar:switcher', p + 'control:switcher-opener', 'Switch windows', 'Open window switcher', '', false),
      row('bar:notifications', p + 'notifications:opener', 'Notifications', 'Open notifications', '', false),
      row('bar:files', p + 'files:opener', 'Files', 'Open Files menu', '', false),
      row('bar:system', p + 'system:opener', 'System', 'Open system menu', '', false),
      row('bar:settings', p + 'settings:opener', 'Settings', 'Open settings', '', false),
    ]);
  };
  const popupRows = (presentation, order, writable) => {
    const p = prefix(presentation);
    const controls = [
      row('control:search', 'launcher-search', '', 'Search applications', '', true),
      row('control:close', p + 'control:close', 'Windows', 'Close applications and return to windows', '', true),
      row('control:refresh', p + 'control:refresh', 'Refresh', 'Refresh applications', '', true),
    ];
    for (let i = 0; i < order.length; i++) {
      const id = order[i];
      for (const [suffix, label, detail, allowed] of [
        ['unpin:', 'Unpin ' + id, 'Pinned application', true],
        ['pin-left:', 'Move ' + id + ' left', 'Pin order', i > 0],
        ['pin-right:', 'Move ' + id + ' right', 'Pin order', i + 1 < order.length],
      ]) controls.push(row(suffix + id, p + suffix + id, label, label, detail, writable && allowed));
    }
    return controls;
  };
  const commit = ({ publication, presentation, status, order, writable, requests, focus }) => ({
    viewProtocol: 1, kind: 'view-commit', projection: {
      viewProtocol: 1, kind: 'view-frame', revision: '1', views: [scopeJson],
      focusOwner: scopeJson, popupOwner: scopeJson,
      frame: { surfaceProtocol: 2, keyboardParent: true, motion: 'reduced',
        appearance: { theme: 'night', textScale: 100, effectsOff: false, reducedTransparency: false },
        publication, lease: '1', mode: 'applications', status,
        bar: barRows(presentation, order), popup: popupRows(presentation, order, writable) },
      announcer: { scope: scopeJson, surface: 'popup' }, announcement: null,
    }, requests, focus,
  });
  const publish = packet => ({ $: '::', a: { $: 'Publish', a: { $: 0, a: packet } }, b: empty() });
  const openRequest = { protocolVersion: 3, kind: 'catalog-request', binding: bindingJson, requestId: '2' };
  const writeRequest = { protocolVersion: 3, kind: 'taskbar-pins-write', binding: bindingJson,
    requestId: '3', proposal: { revision: '1', identities: desiredIdentities } };
  const openCommit = commit({ publication: '6', presentation: '5', status: 'Loading applications…',
    order: givenIdentities, writable: true, requests: [openRequest], focus: ['launcher-search'] });
  const pendingCommit = commit({ publication: '7', presentation: '6', status: 'Saving pin order…',
    order: givenIdentities, writable: false, requests: [writeRequest], focus: [] });
  const batch2 = { scope: oneScope, revision: counter('1'), publication: counter('6'), lease: counter('1'),
    binding, wire: JSON.stringify(openCommit), observations: empty(), operations: empty(),
    catalogs: list([{ binding, request: counter('2') }]) };
  const batch3 = { scope: oneScope, revision: counter('1'), publication: counter('7'), lease: counter('1'),
    binding, wire: JSON.stringify(pendingCommit), observations: empty(), operations: empty(), catalogs: empty() };
  const oneViewBaseChanges = copy(topologyChanges);
  oneViewBaseChanges[1].after = counter('3');
  const oneView = patch(initial, oneViewBaseChanges.concat(copy(oneViewChanges)));
  const attached = patch(oneView, attachedChanges);
  const modelPath = ['controller', 'a', 'controller', 'a', 'desktop'];
  const path = (...tail) => modelPath.concat(tail);
  const pendingChanges = [
    { path: ['controller','a','controller','a','publication'], before: counter('4'), after: counter('7') },
    { path: ['controller','a','controller','a','lease'], before: zero(), after: counter('1') },
    { path: path('presentation'), before: just(counter('3')), after: just(counter('6')) },
    { path: path('request'), before: counter('1'), after: counter('3') },
    { path: path('expected'), before: just(counter('1')), after: just(counter('2')) },
    { path: path('open'), before: false, after: true },
    { path: path('catalogOpening'), before: false, after: true },
    { path: path('pins','snapshot'), before: none(), after: just({ revision: counter('1'), identities: list(givenIdentities) }) },
    { path: path('pins','pending'), before: none(), after: just({ request: counter('3'), identities: list(desiredIdentities), confirmation: { $: 'Saving' } }) },
    { path: path('pins','notice'), before: '', after: 'Saving pin order…' },
    { path: path('launch','a','revision'), before: counter('4'), after: counter('6') },
    { path: ['controller','a','batches'], before: list([attachedBatch]), after: list([batch3, batch2, attachedBatch]) },
  ];
  const pending = patch(attached, pendingChanges);
  const topology = { bridgeProtocol: 1, kind: 'view-topology', payload: {
    viewProtocol: 1, kind: 'view-topology', revision: '1', views: [scopeJson] } };
  const attach = { bridgeProtocol: 1, kind: 'native-event', payload: {
    protocolVersion: 3, kind: 'application-attached', binding: bindingJson, nativeOperations: [] } };
  const catalog = { bridgeProtocol: 1, kind: 'native-event', payload: {
    protocolVersion: 3, kind: 'application-catalog', binding: bindingJson, requestId: '1',
    snapshot: { catalogProtocol: 1, lifetime: '1', generation: '1', entries: [] },
    preferences: { revision: '1', identities: givenIdentities } } };
  const action = (surface, publication, lease, id) => ({ bridgeProtocol: 1, kind: 'view-action', payload: {
    viewProtocol: 1, kind: 'view-action', scope: scopeJson, action: {
      surfaceProtocol: 2, kind: 'surface-action', surface, publication, lease, id, trigger: 'keyboard' } } });
  const values = [topology, attach, catalog, action('bar', '5', '0', 'bar:applications'),
    action('popup', '6', '1', 'pin-left:beta')];
  const receipt = (requestId, status, preferences) => ({ kind: 'incoming', value: {
    bridgeProtocol: 1, kind: 'native-event', payload: { protocolVersion: 3, kind: 'taskbar-pins-outcome',
      binding: bindingJson, requestId, status, preferences } } });
  const givenStep = { input: { kind: 'prelude', values }, setupTimers: 0,
    expected: { state: copy(pending), effects: publish(pendingCommit) } };
  const reset = { input: { kind: 'reset' }, expected: { state: copy(initial), effects: copy(NIL) } };
  const variants = [
    { name: 'pin-wrong-request-retains-pending', input: receipt('4', 'Refused', null),
      changes: [], effects: copy(NIL) },
    { name: 'pin-refused-retains-observed-order', input: receipt('3', 'Refused', null),
      changes: [
        { path: path('pins','pending'), before: just({ request: counter('3'), identities: list(desiredIdentities), confirmation: { $: 'Saving' } }), after: none() },
        { path: path('pins','notice'), before: 'Saving pin order…', after: 'Pin change refused. Refresh applications and choose again.' },
      ], status: 'Pin change refused. Refresh applications and choose again.', order: givenIdentities, writable: true },
    { name: 'pin-unknown-retains-reservation-no-replay', input: receipt('3', 'Unknown', null),
      changes: [
        { path: path('pins','pending','a','confirmation'), before: { $: 'Saving' }, after: { $: 'Unconfirmed', a: none() } },
        { path: path('pins','notice'), before: 'Saving pin order…', after: 'Pin save not confirmed. Refresh applications to read the order; the change will not be repeated.' },
      ], status: 'Pin save not confirmed. Refresh applications to read the order; the change will not be repeated.', order: givenIdentities, writable: false },
    { name: 'pin-saved-receipt-confirms-exact-new-order', input: receipt('3', 'Saved', { revision: '2', identities: desiredIdentities }),
      changes: [
        { path: path('pins','pending'), before: just({ request: counter('3'), identities: list(desiredIdentities), confirmation: { $: 'Saving' } }), after: none() },
        { path: path('pins','snapshot'), before: just({ revision: counter('1'), identities: list(givenIdentities) }), after: just({ revision: counter('2'), identities: list(desiredIdentities) }) },
        { path: path('pins','notice'), before: 'Saving pin order…', after: 'Pin order saved.' },
      ], status: 'Loading applications…', order: desiredIdentities, writable: true },
  ];
  const simpleCases = variants.map(v => {
    if (v.changes.length === 0) return { name: v.name, steps: [copy(reset), copy(givenStep),
      { input: copy(v.input), expected: { state: copy(pending), effects: copy(v.effects) } }] };
    const after = patch(pending, v.changes.concat([{ path: ['controller','a','controller','a','publication'],
      before: counter('7'), after: counter('8') }]));
    const expectedCommit = commit({ publication: '8', presentation: '6', status: v.status,
      order: v.order, writable: v.writable, requests: [], focus: ['launcher-search'] });
    const steps = [copy(reset), copy(givenStep), { input: copy(v.input), expected: { state: after, effects: publish(expectedCommit) } }];
    if (v.name === 'pin-unknown-retains-reservation-no-replay') {
      steps.push({ input: copy(v.input), expected: { state: copy(after), effects: copy(NIL) } });
      const recoveryRequest = { protocolVersion: 3, kind: 'catalog-request', binding: bindingJson, requestId: '4' };
      const recoveryCommit = commit({ publication: '9', presentation: '7', status: v.status,
        order: givenIdentities, writable: false, requests: [recoveryRequest], focus: [] });
      const batch4 = { scope: oneScope, revision: counter('1'), publication: counter('9'), lease: counter('1'),
        binding, wire: JSON.stringify(recoveryCommit), observations: empty(), operations: empty(),
        catalogs: list([{ binding, request: counter('4') }]) };
      const oldBatches = list([batch3, batch2, attachedBatch]);
      const recovery = patch(after, [
        { path: ['controller','a','controller','a','publication'], before: counter('8'), after: counter('9') },
        { path: path('presentation'), before: just(counter('6')), after: just(counter('7')) },
        { path: path('request'), before: counter('3'), after: counter('4') },
        { path: path('expected'), before: just(counter('2')), after: just(counter('4')) },
        { path: path('catalogOpening'), before: true, after: false },
        { path: path('launch','a','revision'), before: counter('6'), after: counter('7') },
        { path: path('pins','pending','a','confirmation'), before: { $: 'Unconfirmed', a: none() }, after: { $: 'Unconfirmed', a: just(counter('4')) } },
        { path: ['controller','a','batches'], before: oldBatches, after: list([batch4, batch3, batch2, attachedBatch]) },
      ]);
      steps.push({ input: { kind: 'incoming', value: action('popup', '8', '1', 'control:refresh') },
        expected: { state: copy(recovery), effects: publish(recoveryCommit) } });
      const catalogReply = (id, preferences) => ({ kind: 'incoming', value: {
        bridgeProtocol: 1, kind: 'native-event', payload: { protocolVersion: 3, kind: 'application-catalog',
          binding: bindingJson, requestId: id, snapshot: { catalogProtocol: 1, lifetime: '1', generation: '1', entries: [] }, preferences } } });
      steps.push({ input: catalogReply('2', null), expected: { state: copy(recovery), effects: copy(NIL) } });
      const observedSnapshot = { $: 'Snapshot', a: counter('1'), b: counter('1'), c: { $: 'RBEmpty_elm_builtin' } };
      const recovered = patch(recovery, [
        { path: ['controller','a','controller','a','publication'], before: counter('9'), after: counter('10') },
        { path: path('presentation'), before: just(counter('7')), after: just(counter('8')) },
        { path: path('expected'), before: just(counter('4')), after: none() },
        { path: path('applications'), before: none(), after: just(observedSnapshot) },
        { path: path('launch','a','revision'), before: counter('7'), after: counter('8') },
        { path: path('launch','a','snapshot'), before: none(), after: just(observedSnapshot) },
        { path: path('pins','snapshot'), before: just({ revision: counter('1'), identities: list(givenIdentities) }),
          after: just({ revision: counter('2'), identities: list(desiredIdentities) }) },
        { path: path('pins','pending'), before: just({ request: counter('3'), identities: list(desiredIdentities), confirmation: { $: 'Unconfirmed', a: just(counter('4')) } }), after: none() },
        { path: path('pins','notice'), before: v.status, after: '' },
      ]);
      const observedCommit = commit({ publication: '10', presentation: '8', status: 'No matching applications. Change your search or Refresh.',
        order: desiredIdentities, writable: true, requests: [], focus: [] });
      steps.push({ input: catalogReply('4', { revision: '2', identities: desiredIdentities }),
        expected: { state: recovered, effects: publish(observedCommit) } });
    }
    return { name: v.name, steps };
  });
  const unknownNotice = 'Pin save not confirmed. Refresh applications to read the order; the change will not be repeated.';
  const pendingSaving = just({ request: counter('3'), identities: list(desiredIdentities), confirmation: { $: 'Saving' } });
  const pendingUnknown = just({ request: counter('3'), identities: list(desiredIdentities), confirmation: { $: 'Unconfirmed', a: none() } });
  const unknownState = patch(pending, [
    { path: ['controller','a','controller','a','publication'], before: counter('7'), after: counter('8') },
    { path: path('pins','pending'), before: pendingSaving, after: pendingUnknown },
    { path: path('pins','notice'), before: 'Saving pin order…', after: unknownNotice },
  ]);
  const unknownCommit = commit({ publication: '8', presentation: '6', status: unknownNotice,
    order: givenIdentities, writable: false, requests: [], focus: ['launcher-search'] });
  const afterUnknown = [
    { name: 'pin-unknown-then-correlated-refused', status: 'Refused', preferences: null,
      notice: 'Pin change refused. Refresh applications and choose again.', order: givenIdentities },
    { name: 'pin-unknown-then-correlated-saved', status: 'Saved',
      preferences: { revision: '2', identities: desiredIdentities }, notice: 'Pin order saved.', order: desiredIdentities },
  ].map(v => {
    const changes = [
      { path: ['controller','a','controller','a','publication'], before: counter('8'), after: counter('9') },
      { path: path('pins','pending'), before: pendingUnknown, after: none() },
      { path: path('pins','notice'), before: unknownNotice, after: v.notice },
    ];
    if (v.status === 'Saved') changes.push({ path: path('pins','snapshot'),
      before: just({ revision: counter('1'), identities: list(givenIdentities) }),
      after: just({ revision: counter('2'), identities: list(desiredIdentities) }) });
    const settled = patch(unknownState, changes);
    const settledCommit = commit({ publication: '9', presentation: '6',
      status: v.status === 'Saved' ? 'Loading applications…' : v.notice,
      order: v.order, writable: true, requests: [], focus: ['launcher-search'] });
    return { name: v.name, steps: [copy(reset), copy(givenStep),
      { input: receipt('3', 'Unknown', null), expected: { state: copy(unknownState), effects: publish(unknownCommit) } },
      { input: receipt('3', v.status, v.preferences), expected: { state: settled, effects: publish(settledCommit) } },
    ] };
  });
  return simpleCases.concat(afterUnknown);
}

const pinCases = buildPinCases({ cloneLiteral, literalPatches, initial, topologyChanges,
  oneViewChanges, attachedChanges, oneScope, oneScopeJson, binding, bindingJson,
  attachedBatch, host, empty, none, zero, NIL });
'use strict';
// Source-derived QA factory for Root integration, not executed.  The context
// must consist of the independently authored literals/functions already in the
// green tea-contract-cases.cjs, never observed reducer or worker output.
// Exact base source hash and every added factory's hash belong in the handoff.
// Elm debug object tags and wire serialization still require Root's checks.
// Inlined reviewed q-origin factory source SHA256 113cf5419456680f52822d862cec39fba916c5652ee863b6682baf115d1a4b07.
// QA-only source-literal supplement. NOT RUN, and not a replacement for the
// separate pending settings/motion/shortcut finite-receipt cases. Integrator
// must inline the factory in the sandboxed oracle and supply ONLY the reviewed
// source-authored pinCases, cloneLiteral, NIL from tea-contract-cases.cjs.
// No reducer output or observed state may be used as an oracle dependency.
// Desktop.elm taskbar-pins-outcome rejects status outside Saved/Refused/Unknown
// before Pins.receive; Pins.elm preserves an Unknown reservation without replay.
function buildMalformedPinPreferenceCases(c) {
  if (!c || !Array.isArray(c.pinCases) || typeof c.cloneLiteral !== 'function' || !c.NIL) {
    throw new Error('independently authored pin literals required');
  }
  const copy = c.cloneLiteral;
  const candidates = c.pinCases.filter(x => x && x.name === 'pin-unknown-retains-reservation-no-replay');
  if (candidates.length !== 1) throw new Error('one canonical pin Unknown literal required');
  const baseline = candidates[0];
  if (!Array.isArray(baseline.steps) || baseline.steps.length < 4 ||
      baseline.steps[0].input.kind !== 'reset' || baseline.steps[1].input.kind !== 'prelude' ||
      baseline.steps[1].setupTimers !== 0) throw new Error('canonical pending prelude shape changed');
  const positive = baseline.steps[2];
  const late = baseline.steps[3];
  const payload = positive && positive.input && positive.input.value && positive.input.value.payload;
  if (!payload || payload.kind !== 'taskbar-pins-outcome' || payload.status !== 'Unknown' ||
      payload.requestId !== '3' || !payload.binding || payload.binding.lifetime !== '1' ||
      payload.binding.session !== '1' || payload.binding.frontend !== '1' || payload.preferences !== null ||
      !positive.expected || !late || !late.expected) throw new Error('canonical positive literal changed');
  return ['Stored', 'Bogus', 'saved', ''].map(status => {
    const invalid = copy(positive.input);
    invalid.value.payload.status = status;
    const before = copy(baseline.steps[1].expected.state);
    return {
      name: 'pin-pending-invalid-status-' + (status === '' ? 'empty' : status),
      steps: [
        copy(baseline.steps[0]),
        copy(baseline.steps[1]),
        { input: invalid, expected: { state: before, effects: copy(c.NIL) } },
        // The original independently literal matching Unknown is a positive
        // control after refusal; it must not replay the saved mutation.
        copy(positive),
        // Repeated Unknown is independently asserted as unchanged/no effect.
        copy(late),
      ],
    };
  });
}

// Inlined peer terra-q-network-window-receipts.cjs SHA256 149f2f4181b1c23ca1ccdeb2a692e6be6aa812eaee365375852013ec85c22275.
// Source-derived DRAFT. No reducer capture, model/compiler/test execution, or
// native authority. Source pins: DesktopPolicy 018934fe4762e8357665ce7c37cb289883c6cdd1bad31d6592402b369d7bad3e;
// OutputController fdf7b44483ec9312182a1b50bb2bbb5d52b804538e5c4d4ce5a4a8479e9af6ae;
// SurfaceController 2e86781c41c1b1c62d518e886ee965a875a04ea88980159a00511c549b25e998;
// Desktop 91223c94074f8ff908b2ed66f52e8025c8afcb78a977d4a5f3daf44df8ce7af4;
// Shell 6f6a63168d1d39da6e85290b564074ca21f7c719140aacee939973e3706ad094;
// Effects 80c574e8c564c28a1fb11f1f89bb5bfa7ac97a92474bbf027a737324bb2a82cd;
// ActionProjection 911faed965465fac4e32f404d75a4d130b4e560cda191c7773eb96749be1d062;
// TaskbarShell eeb91d15cab97c94bf12ef3d1e25f513ac6c037774bef5150867eb01c6f86c26;
// Surface c1a34f50b3b1da96f732d63fe9fb9f0e7022735881385ed5419aca8e76796ccb;
// canonical QA c3272b69d6e22182063014649a04acdf0a87b1aaf61ce5b9b043c6f7bb1e5a9c.
// Root must review initial/prelude, artifact encoding and all
// state/effect values before integration. Factory is inlineable into QA runner.
function buildWindowReceiptCases(c) {
  const { cloneLiteral: copy, literalPatches: patch, initial, topologyChanges,
    oneViewChanges, oneScope, oneScopeJson, binding, bindingJson, host, empty,
    none, zero, NIL } = c;
  if ([copy,patch,initial,topologyChanges,oneViewChanges,oneScope,oneScopeJson,
       binding,bindingJson,host,empty,none,zero,NIL].some(x => x === undefined)) {
    throw new Error('independently literal window fixture dependencies missing');
  }
  const C = s => ({ $:'Counter', a:s });
  const J = x => ({ $:'Just', a:x });
  const L = xs => xs.reduceRight((b,a) => ({ $:'::', a,b }), empty());
  const dp = (...xs) => ['controller','a','controller','a','desktop', ...xs];
  const sp = (...xs) => dp('windows','shell',...xs);
  const pub = n => ['controller','a','controller','a','publication'];
  const change = (path,before,after) => ({ path,before,after });
  const P = (status, publication, group, requests) => {
    const prefix = 'applications:' + host + ':3:';
    const row = (id,domId,label,ariaLabel,detail,enabled) =>
      ({id,domId,label,ariaLabel,detail,enabled,focusOnly:false});
    const utility = [
      row('bar:applications',prefix+'control:opener','Applications','Open applications','',true),
      row('bar:overview',prefix+'control:overview-opener','Task View','Open Task View','',group === 'ready'),
      row('bar:switcher',prefix+'control:switcher-opener','Switch windows','Open window switcher','',group === 'ready'),
      row('bar:notifications',prefix+'notifications:opener','Notifications','Open notifications','',true),
      row('bar:files',prefix+'files:opener','Files','Open Files menu','',true),
      row('bar:system',prefix+'system:opener','System','Open system menu','',true),
      row('bar:settings',prefix+'settings:opener','Settings','Open settings','',true),
    ];
    const recovery = group === 'pending' || group === 'refused' ? [
      row('bar:recovery-refresh',prefix+'bar:recovery-refresh','Refresh window status',
          'Refresh window status; read observations without retrying actions','Observation only',group === 'refused')
    ] : [];
    const blocked = group === 'pending';
    const groupRow = group === 'none' ? [] : [row('bar:group:application:demo',
      'group:'+host+':1:1:application:demo','Window',
      'Minimize Window; Active'+(blocked?'; awaiting native confirmation':''),
      blocked?'Awaiting native confirmation; Active':'Active',group === 'ready')];
    return {viewProtocol:1,kind:'view-commit',projection:{
      viewProtocol:1,kind:'view-frame',revision:'1',views:[oneScopeJson],focusOwner:oneScopeJson,
      popupOwner:null,frame:{surfaceProtocol:2,keyboardParent:true,motion:'reduced',
        appearance:{theme:'night',textScale:100,effectsOff:false,reducedTransparency:false},
        publication,lease:'0',mode:'closed',status,bar:recovery.concat(groupRow,utility),popup:[]},
      announcer:{scope:oneScopeJson,surface:'bar'},announcement:null},requests,focus:[]};
  };
  const wrap = packet => ({ $:'::', a:{ $:'Publish', a:{ $:0,a:packet } }, b:empty() });
  const incoming = (kind,payload) => ({bridgeProtocol:1,kind,payload});
  const request = (kind,id) => ({protocolVersion:3,kind,binding:bindingJson,requestId:id});
  const startupRequests = [request('catalog-request','1'),request('shell-settings-request','2'),
    request('motion-preferences-request','3'),request('shortcut-preferences-request','4'),
    request('projection-request','1')];
  const attachedPacket = P('Updating window information…','4','none',startupRequests);
  const pair = (a,b) => ({ $:'#2',a,b });
  const startupBatch = {scope:oneScope,revision:C('1'),publication:C('4'),lease:C('0'),
    binding,wire:JSON.stringify(attachedPacket),observations:L([pair('projection-request',C('1'))]),
    operations:empty(),catalogs:L([{binding,request:C('1')}])};
  const context = {lifetime:C('1'),epoch:C('1'),output:C('1'),revision:C('1')};
  const wireContext = {lifetime:'1',epoch:'1',output:'1',revision:'1'};
  const window = {incarnation:C('1'),label:'Window',minimized:false,owner:none(),
    application:'demo',available:true,attention:false};
  // Debug constructor form for a one-node Dict, subject to Root's actual
  // compiler artifact qualification; this representation is not guessed from
  // a captured reducer result.
  const node = {$:'RBNode_elm_builtin',a:{$:'Black'},b:'1',c:C('1'),
    d:{$:'RBEmpty_elm_builtin'},e:{$:'RBEmpty_elm_builtin'}};
  const scene = {$:'Admitted',a:C('1'),b:J(C('1')),c:L([window]),d:node};
  const observed = {context,scene};
  const intent = {request:C('1'),generation:C('1'),incarnation:C('1'),operation:{$:'Minimize'},context};
  const wireIntent = {request:'1',generation:'1',incarnation:'1',operation:'minimize',context:wireContext};
  const transaction = status => ({intent,status:{$:status},effectProtocol:1});
  const issued = {binding,protocol:1,intent};
  const windowRequest = {protocolVersion:3,kind:'window-effect',effectProtocol:1,binding:bindingJson,intent:wireIntent};
  const pendingPacket = P('Minimize: applying to Window…','7','pending',[windowRequest]);
  const mutationBatch = {scope:oneScope,revision:C('1'),publication:C('7'),lease:C('0'),binding,
    wire:JSON.stringify(pendingPacket),observations:empty(),operations:L([issued]),catalogs:empty()};
  const oneViewChanges0 = copy(topologyChanges); oneViewChanges0[1].after=C('3');
  const oneView = patch(initial,oneViewChanges0.concat(copy(oneViewChanges)));
  const stateChanges = [
    change(pub(),C('3'),C('7')),
    change(dp('presentation'),J(C('2')),J(C('3'))),
    change(dp('request'),zero(),C('4')),
    change(dp('expected'),none(),J(C('1'))),
    change(dp('settingsExpected'),none(),J(C('2'))),
    change(dp('motionExpected'),none(),J(C('3'))),
    change(dp('shortcutExpected'),none(),J(C('4'))),
    change(dp('workspaceNavigation','binding'),none(),J(binding)),
    change(dp('launch','a','host'),none(),J(host)),
    change(dp('launch','a','revision'),C('2'),C('4')),
    change(dp('pointer','observation'),none(),J({binding,serial:C('1'),state:{$:'Idle'},owner:none()})),
    change(sp('binding'),none(),J(binding)),
    change(sp('request'),zero(),C('1')),
    change(sp('phase'),{$:'Detached'},{$:'Ready'}),
    change(sp('reconnecting'),true,false),
    change(sp('notice'),'Connecting…','Connected'),
    change(sp('effects','connected'),false,true),
    change(sp('effects','observed'),none(),J(observed)),
    change(sp('effects','request'),zero(),C('1')),
    change(sp('effects','generation'),zero(),C('1')),
    change(sp('effects','transaction'),none(),J(transaction('Pending'))),
    change(sp('effects','unresolved'),empty(),L([transaction('Pending')])),
    change(sp('issued'),empty(),L([issued])),
    change(['controller','a','batches'],empty(),L([mutationBatch,startupBatch])),
  ];
  const pending = patch(oneView,stateChanges);
  const topology = incoming('view-topology',{viewProtocol:1,kind:'view-topology',revision:'1',views:[oneScopeJson]});
  const attached = incoming('native-event',{protocolVersion:3,kind:'attached',binding:bindingJson});
  const projection = incoming('native-event',{protocolVersion:3,kind:'action-projection',binding:bindingJson,
    requestId:'1',context:wireContext,scene:{revision:'1',focused:'1',windows:[{incarnation:'1',
      label:'Window',minimized:false,owner:null,application:'demo',available:true}]}});
  const pointer = incoming('native-event',{protocolVersion:3,kind:'pointer-ownership',ownershipProtocol:1,
    binding:bindingJson,requestId:'1',serial:'1',state:'idle',owner:null});
  const mutate = incoming('view-action',{viewProtocol:1,kind:'view-action',scope:oneScopeJson,
    action:{surfaceProtocol:2,kind:'surface-action',surface:'bar',publication:'6',lease:'0',
      id:'bar:group:application:demo',trigger:'keyboard'}});
  // Shared source-literal native-ready GIVEN: exactly four real Policy.Incoming
  // inputs. The helper returns no captured output and introduces no authority.
  // Consumers may compose their own independently literal tested transitions.
  if (c.windowReadyOnly === true) {
    const ready = patch(pending,[
      change(pub(),C('7'),C('6')),
      change(sp('effects','request'),C('1'),zero()),
      change(sp('effects','generation'),C('1'),zero()),
      change(sp('effects','transaction'),J(transaction('Pending')),none()),
      change(sp('effects','unresolved'),L([transaction('Pending')]),empty()),
      change(sp('issued'),L([issued]),empty()),
      change(['controller','a','batches'],L([mutationBatch,startupBatch]),L([startupBatch])),
    ]);
    const readyPacket = P('Connected','6','ready',[]);
    return {input:{kind:'prelude',values:[copy(topology),copy(attached),copy(projection),copy(pointer)]},
      setupTimers:0,expected:{state:ready,effects:wrap(readyPacket)},
      literals:{binding:copy(binding),bindingJson:copy(bindingJson),scope:copy(oneScope),
        scopeJson:copy(oneScopeJson),context:copy(context),wireContext:copy(wireContext),
        startupBatch:copy(startupBatch),host}};
  }
  const reset = {input:{kind:'reset'},expected:{state:copy(initial),effects:copy(NIL)}};
  const given = {input:{kind:'prelude',values:[topology,attached,projection,pointer,mutate]},setupTimers:0,
    expected:{state:copy(pending),effects:wrap(pendingPacket)}};
  const receipt = status => ({kind:'incoming',value:incoming('native-event',{
    protocolVersion:3,kind:'effect-outcome',effectProtocol:1,binding:bindingJson,intent:wireIntent,
    status,reason:'applied',revision:'2',outputGeneration:'1'})});
  const cases = ['Committed','Refused'].map(status => {
    const statusText = status === 'Refused' ? 'Minimize: refused for Window. Refresh window status, then choose again.' : 'Connected';
    const packet = P(statusText,'8',status === 'Refused' ? 'refused':'settled',[request('projection-request','2')]);
    const readBatch = {scope:oneScope,revision:C('1'),publication:C('8'),lease:C('0'),binding,
      wire:JSON.stringify(packet),observations:L([pair('projection-request',C('2'))]),operations:empty(),catalogs:empty()};
    const settled = patch(pending,[
      change(pub(),C('7'),C('8')),
      change(sp('request'),C('1'),C('2')),
      change(sp('expected'),none(),J(C('2'))),
      change(sp('phase'),{$:'Ready'},{$:'Reconciling'}),
      change(sp('effects','transaction'),J(transaction('Pending')),J(transaction(status))),
      change(sp('effects','unresolved'),L([transaction('Pending')]),empty()),
      change(sp('issued'),L([issued]),empty()),
      change(['controller','a','batches'],L([mutationBatch,startupBatch]),L([readBatch,mutationBatch,startupBatch])),
    ]);
    const duplicate = receipt(status);
    const stale = receipt(status); stale.value.payload.intent = {...wireIntent,request:'2'};
    return {name:'window-minimize-'+status.toLowerCase()+'-duplicate-and-stale',steps:[
      copy(reset),copy(given),{input:receipt(status),expected:{state:copy(settled),effects:wrap(packet)}},
      {input:duplicate,expected:{state:copy(settled),effects:copy(NIL)}},
      {input:stale,expected:{state:copy(settled),effects:copy(NIL)}}]};
  });
  return cases;
}

// Inlined peer tea-delay-front.cjs SHA256 98f633ae25bd5eb4ac657d97988c7aa6075fc0bf5165f3c040e67fdf5efed4f2.

/* Source-derived QA draft; not executed. Insert this factory into the same
 * sandboxed oracle module as tea-contract-cases.cjs. The prelude uses actual
 * incoming policy events; no authority constructor is injected into the worker.
 * Runtime/model timers and native acceptance are outside this fixture. */
function buildLaunchDeadlineCases(c) {
  const { cloneLiteral: copy, literalPatches: patch, initial, topologyChanges,
    oneViewChanges, oneScope, oneScopeJson, binding, bindingJson, host,
    empty, none, zero, NIL } = c;
  if ([copy, patch, initial, topologyChanges, oneViewChanges, oneScope,
    oneScopeJson, binding, bindingJson, host, empty, none, zero, NIL]
    .some(value => value === undefined)) throw new Error('missing independently pinned source literal');
  const counter = value => ({ $: 'Counter', a: String(value) });
  const just = value => ({ $: 'Just', a: value });
  const list = values => values.reduceRight((tail, value) => ({ $: '::', a: value, b: tail }), empty());
  const tuple = (a, b) => ({ $: '#2', a, b });
  const prefix = n => 'applications:' + host + ':' + n + ':';
  const row = (id, domId, label, ariaLabel, detail, enabled) =>
    ({ id, domId, label, ariaLabel, detail, enabled, focusOnly: false });
  const bar = p => [
    row('bar:applications', prefix(p) + 'control:opener', 'Applications', 'Open applications', '', true),
    row('bar:overview', prefix(p) + 'control:overview-opener', 'Task View', 'Open Task View', '', false),
    row('bar:switcher', prefix(p) + 'control:switcher-opener', 'Switch windows', 'Open window switcher', '', false),
    row('bar:notifications', prefix(p) + 'notifications:opener', 'Notifications', 'Open notifications', '', true),
    row('bar:files', prefix(p) + 'files:opener', 'Files', 'Open Files menu', '', true),
    row('bar:system', prefix(p) + 'system:opener', 'System', 'Open system menu', '', true),
    row('bar:settings', prefix(p) + 'settings:opener', 'Settings', 'Open settings', '', true),
  ];
  const popup = (p, state, catalog) => {
    if (state === 'closed') return [];
    const rows = [
      row('control:search', 'launcher-search', '', 'Search applications', '', true),
      row('control:close', prefix(p) + 'control:close', 'Windows', 'Close applications and return to windows', '', true),
      row('control:refresh', prefix(p) + 'control:refresh', 'Refresh', 'Refresh applications', '', true),
    ];
    if (state === 'unknown') rows.push(row('control:acknowledge', prefix(p) + 'control:acknowledge',
      'I checked; allow another launch', 'I checked; allow another launch', '', true));
    if (catalog) rows.push(
      row('jump:open:sample.desktop', prefix(p) + 'jump:open:sample.desktop', 'Actions for Sample', 'Actions for Sample', 'Application actions and recent files', true),
      row('pin:sample.desktop', prefix(p) + 'pin:sample.desktop', 'Pin Sample', 'Pin Sample', 'Add to taskbar', true),
      row('entry:sample.desktop', prefix(p) + 'entry:sample.desktop', 'Open Sample', 'Open Sample', '', state === 'ready'));
    return rows;
  };
  const packet = (pub, lease, p, state, status, catalog, requests, focus) => ({
    viewProtocol: 1, kind: 'view-commit', projection: {
      viewProtocol: 1, kind: 'view-frame', revision: '1', views: [oneScopeJson],
      focusOwner: oneScopeJson, popupOwner: state === 'closed' ? null : oneScopeJson,
      frame: { surfaceProtocol: 2, keyboardParent: true, motion: 'reduced',
        appearance: { theme: 'night', textScale: 100, effectsOff: false, reducedTransparency: false },
        publication: pub, lease, mode: state === 'closed' ? 'closed' : 'applications', status,
        bar: bar(p), popup: popup(p, state, catalog) },
      announcer: { scope: oneScopeJson, surface: state === 'closed' ? 'bar' : 'popup' }, announcement: null,
    }, requests, focus,
  });
  const request = (kind, id) => ({ protocolVersion: 3, kind, binding: bindingJson, requestId: id });
  const entry = { identity: { $: 'EntryId', a: 'sample.desktop' }, name: 'Sample', iconHint: '',
    wmclass: '', genericName: '', keywords: empty() };
  const dictEmpty = { $: 'RBEmpty_elm_builtin' };
  const dict = { $: 'RBNode_elm_builtin', a: { $: 'Black' }, b: 'sample.desktop', c: entry,
    d: dictEmpty, e: dictEmpty };
  const snapshot = { $: 'Snapshot', a: counter(1), b: counter(1), c: dict };
  const attachRequests = [request('catalog-request', '1'), request('shell-settings-request', '2'),
    request('motion-preferences-request', '3'), request('shortcut-preferences-request', '4'),
    request('projection-request', '1')];
  const attachPacket = packet('4', '0', '3', 'closed', 'Updating window information…', false, attachRequests, []);
  const openRequest = request('catalog-request', '5');
  const openPacket = packet('6', '1', '4', 'open', 'Loading applications…', false, [openRequest], ['launcher-search']);
  const catalogPacket = packet('7', '1', '5', 'ready', 'Type to search applications.', true, [], ['launcher-search']);
  const batch1 = { scope: oneScope, revision: counter(1), publication: counter(4), lease: zero(), binding,
    wire: JSON.stringify(attachPacket), observations: list([tuple('projection-request', counter(1))]),
    operations: empty(), catalogs: list([{ binding, request: counter(1) }]) };
  const batch2 = { scope: oneScope, revision: counter(1), publication: counter(6), lease: counter(1), binding,
    wire: JSON.stringify(openPacket), observations: empty(), operations: empty(),
    catalogs: list([{ binding, request: counter(5) }]) };
  const baseChanges = copy(topologyChanges);
  baseChanges[1].after = counter(3);
  const base = patch(initial, baseChanges.concat(copy(oneViewChanges)));
  const dp = ['controller', 'a', 'controller', 'a', 'desktop'];
  const path = (...tail) => dp.concat(tail);
  const given = patch(base, [
    { path: ['controller','a','controller','a','publication'], before: counter(3), after: counter(7) },
    { path: ['controller','a','controller','a','lease'], before: zero(), after: counter(1) },
    { path: path('presentation'), before: just(counter(2)), after: just(counter(5)) },
    { path: path('request'), before: zero(), after: counter(5) },
    { path: path('settingsExpected'), before: none(), after: just(counter(2)) },
    { path: path('motionExpected'), before: none(), after: just(counter(3)) },
    { path: path('shortcutExpected'), before: none(), after: just(counter(4)) },
    { path: path('open'), before: false, after: true },
    { path: path('workspaceNavigation','binding'), before: none(), after: just(binding) },
    { path: path('pointer','observation'), before: none(), after: just({ binding, serial: counter(1), state: { $: 'Idle' }, owner: none() }) },
    { path: path('applications'), before: none(), after: just(snapshot) },
    { path: path('pins','snapshot'), before: none(), after: just({ revision: counter(1), identities: empty() }) },
    { path: path('launch','a','host'), before: none(), after: just(host) },
    { path: path('launch','a','snapshot'), before: none(), after: just(snapshot) },
    { path: path('launch','a','revision'), before: counter(2), after: counter(6) },
    { path: path('windows','shell','binding'), before: none(), after: just(binding) },
    { path: path('windows','shell','phase'), before: { $: 'Detached' }, after: { $: 'Reconciling' } },
    { path: path('windows','shell','reconnecting'), before: true, after: false },
    { path: path('windows','shell','notice'), before: 'Connecting…', after: 'Updating window information…' },
    { path: path('windows','shell','request'), before: zero(), after: counter(1) },
    { path: path('windows','shell','expected'), before: none(), after: just(counter(1)) },
    { path: ['controller','a','batches'], before: empty(), after: list([batch2,batch1]) },
  ]);
  const gateway = (kind, payload) => ({ bridgeProtocol: 1, kind, payload });
  const native = (kind, fields) => gateway('native-event', { protocolVersion: 3, kind, ...fields });
  const action = (surface, publication, lease, id) => gateway('view-action', {
    viewProtocol: 1, kind: 'view-action', scope: oneScopeJson,
    action: { surfaceProtocol: 2, kind: 'surface-action', surface, publication, lease, id, trigger: 'keyboard' },
  });
  const values = [
    gateway('view-topology', { viewProtocol: 1, kind: 'view-topology', revision: '1', views: [oneScopeJson] }),
    native('attached', { binding: bindingJson }),
    native('pointer-ownership', { ownershipProtocol: 1, binding: bindingJson, requestId: '1', serial: '1', state: 'idle', owner: null }),
    action('bar', '5', '0', 'bar:applications'),
    native('application-catalog', { binding: bindingJson, requestId: '5',
      snapshot: { catalogProtocol: 1, lifetime: '1', generation: '1', entries: [
        { id: 'sample.desktop', name: 'Sample', iconHint: '', wmclass: '' } ] },
      preferences: { revision: '1', identities: [] } }),
  ];
  const publish = value => ({ $: 'Publish', a: { $: 0, a: value } });
  const intent = { request: counter(1), lifetime: counter(1), generation: counter(1), entry: 'sample.desktop' };
  const wireIntent = { request: '1', lifetime: '1', generation: '1', entry: 'sample.desktop' };
  const launchRequest = { protocolVersion: 3, kind: 'application-launch', binding: bindingJson, intent: wireIntent };
  const pendingPacket = packet('8', '1', '5', 'pending', 'Opening application…', true, [launchRequest], []);
  const batch3 = { scope: oneScope, revision: counter(1), publication: counter(8), lease: counter(1), binding,
    wire: JSON.stringify(pendingPacket), observations: empty(), operations: empty(), catalogs: empty() };
  const pending = patch(given, [
    { path: ['controller','a','controller','a','publication'], before: counter(7), after: counter(8) },
    { path: path('launchFromApplications'), before: false, after: true },
    { path: path('launch','a','request'), before: zero(), after: counter(1) },
    { path: path('launch','a','revision'), before: counter(6), after: counter(7) },
    { path: path('launch','a','phase'), before: { $: 'Idle' }, after: { $: 'Pending', a: host, b: intent } },
    { path: ['controller','a','batches'], before: list([batch2,batch1]), after: list([batch3,batch2,batch1]) },
  ]);
  const token = { $: 'PendingToken', a: host, b: intent };
  const pendingEffects = list([publish(pendingPacket), { $: 'Delay', a: 10000, b: { $: 'Deadline', a: token } }]);
  const unknown = patch(pending, [
    { path: ['controller','a','controller','a','publication'], before: counter(8), after: counter(9) },
    { path: path('launch','a','revision'), before: counter(7), after: counter(8) },
    { path: path('launch','a','phase'), before: { $: 'Pending', a: host, b: intent },
      after: { $: 'Settled', a: intent, b: { $: 'Unknown' } } },
  ]);
  const unknownPacket = packet('9', '1', '5', 'unknown',
    'The launch could not be confirmed. Check your windows before opening it again.', true, [], []);
  const reset = { input: { kind: 'reset' }, expected: { state: copy(initial), effects: copy(NIL) } };
  const givenStep = { input: { kind: 'prelude', values }, setupTimers: 0,
    expected: { state: copy(given), effects: list([publish(catalogPacket)]) } };
  const start = { input: { kind: 'incoming', value: action('popup', '7', '1', 'entry:sample.desktop') },
    expected: { state: copy(pending), effects: pendingEffects } };
  const submitted = patch(pending, [
    { path: ['controller','a','controller','a','publication'], before: counter(8), after: counter(9) },
    { path: path('open'), before: true, after: false },
    { path: path('launch','a','revision'), before: counter(7), after: counter(8) },
    { path: path('launch','a','phase'), before: { $: 'Pending', a: host, b: intent },
      after: { $: 'Settled', a: intent, b: { $: 'Submitted' } } },
  ]);
  const submittedPacket = packet('9', '1', '5', 'closed', 'Launch submitted.', true, [], []);
  const submittedReceipt = native('application-launch-outcome', { binding: bindingJson,
    outcome: { catalogProtocol: 1, kind: 'launch-outcome', intent: wireIntent,
      status: 'Submitted', reason: 'native-submission-accepted' } });
  return [
    { name: 'launch-delay-exact-timeout-and-stale-token', steps: [copy(reset), copy(givenStep), copy(start),
      { input: { kind: 'deadline', index: 0 }, expected: { state: copy(unknown), effects: list([publish(unknownPacket)]) } },
      { input: { kind: 'deadline', index: 0 }, expected: { state: copy(unknown), effects: copy(NIL) } },
    ] },
    { name: 'launch-delay-stale-after-matching-submitted', steps: [copy(reset), copy(givenStep), copy(start),
      { input: { kind: 'incoming', value: submittedReceipt }, expected: { state: copy(submitted), effects: list([publish(submittedPacket)]) } },
      { input: { kind: 'deadline', index: 0 }, expected: { state: copy(submitted), effects: copy(NIL) } },
    ] },
  ];
}

// Inlined q-http source SHA256 47972d000c4c678d3e7ee222bfa4bee4effe76217f941bb7266a95a30b823398.
// Source-derived, unexecuted QA draft. This is a pure-policy bridge fixture,
// NOT current application-only Haskell native authority or native acceptance.
// The independent window factory dependency is SHA-256
// 149f2f4181b1c23ca1ccdeb2a692e6be6aa812eaee365375852013ec85c22275.
// It must supply its source-literal Pending GIVEN, not captured reducer data.
// Root must review exact compiler tags, all fields and prelude reachability.
function buildWindowRebindCases(c) {
  const {cloneLiteral: copy, literalPatches: patch, buildWindowCases,
    oneScope, oneScopeJson, binding, bindingJson, host, empty, none, zero, NIL} = c;
  if ([copy,patch,buildWindowCases,oneScope,oneScopeJson,binding,bindingJson,host,
       empty,none,zero,NIL].some(x => x === undefined) ||
      typeof copy !== 'function' || typeof patch !== 'function' || typeof buildWindowCases !== 'function') {
    throw new Error('independent window GIVEN and complete literal context required');
  }
  const original = buildWindowCases(c);
  if (!Array.isArray(original) || !original[0] || !Array.isArray(original[0].steps) ||
      original[0].steps[0].input.kind !== 'reset' || original[0].steps[1].input.kind !== 'prelude') {
    throw new Error('unexpected source-literal window GIVEN');
  }
  const given = copy(original[0].steps[1]);
  const pending = given.expected.state;
  const C = s => ({$: 'Counter', a:s});
  const J = x => ({$: 'Just', a:x});
  const L = xs => xs.reduceRight((b,a) => ({$:'::',a,b}),empty());
  const dp = (...xs) => ['controller','a','controller','a','desktop',...xs];
  const sp = (...xs) => dp('windows','shell',...xs);
  const cp = (...xs) => ['controller','a',...xs];
  const change = (path,before,after) => ({path,before,after});
  const pair = (a,b) => ({$:'#2',a,b});
  const context = {lifetime:C('1'),epoch:C('1'),output:C('1'),revision:C('1')};
  const intent = {request:C('1'),generation:C('1'),incarnation:C('1'),operation:{$:'Minimize'},context};
  const wireContext = {lifetime:'1',epoch:'1',output:'1',revision:'1'};
  const wireIntent = {request:'1',generation:'1',incarnation:'1',operation:'minimize',context:wireContext};
  const tx = status => ({intent,status:{$:status},effectProtocol:1});
  const issued = {binding,protocol:1,intent};
  const B2 = {$:'Binding',a:C('1'),b:C('1'),c:C('2')};
  const b2 = {lifetime:'1',session:'1',frontend:'2'};
  const host2 = '{"lifetime":"1","session":"1","frontend":"2"}';
  const lostText = 'Window adapter unavailable. Reconnect to read current state. Unconfirmed actions will not be repeated.';
  const correlation = '{"outcome":"adapter-unavailable","binding":{"lifetime":"1","session":"1","frontend":"1"},"identity":{"adapter":"windows","request":"1","service":null,"revision":null}}';
  const announce = {interrupt:false,sequence:'1',correlation,text:lostText};
  const rawAnnounce = {interrupt:false,sequence:C('1'),correlation,text:lostText};
  const row = (id,domId,label,ariaLabel,detail,enabled) =>
    ({id,domId,label,ariaLabel,detail,enabled,focusOnly:false});
  const wrap = packet => L([{$:'Publish',a:{$:0,a:packet}}]);
  const gateway = payload => ({bridgeProtocol:1,kind:'native-event',payload});
  const viewAction = (publication,id) => ({kind:'incoming',value:{bridgeProtocol:1,kind:'view-action',payload:{
    viewProtocol:1,kind:'view-action',scope:oneScopeJson,action:{surfaceProtocol:2,kind:'surface-action',
      surface:'bar',publication,lease:'0',id,trigger:'keyboard'}}}});
  const ordinary = (wireHost,presentation) => {
    const p='applications:'+wireHost+':'+presentation+':';
    return [
      row('bar:overview',p+'control:overview-opener','Task View','Open Task View','',false),
      row('bar:switcher',p+'control:switcher-opener','Switch windows','Open window switcher','',false),
      row('bar:notifications',p+'notifications:opener','Notifications','Open notifications','',true),
      row('bar:files',p+'files:opener','Files','Open Files menu','',true),
      row('bar:system',p+'system:opener','System','Open system menu','',true),
      row('bar:settings',p+'settings:opener','Settings','Open settings','',true),
    ];
  };
  const group = (dom,blocked) => row('bar:group:application:demo',dom,'Window',
    'Minimize Window; Active'+(blocked?'; awaiting native confirmation':''),
    blocked?'Awaiting native confirmation; Active':'Active',false);
  const request = (kind,id) => ({protocolVersion:3,kind,binding:b2,requestId:id});
  const commit = (publication,status,bar,requests) => ({viewProtocol:1,kind:'view-commit',projection:{
    viewProtocol:1,kind:'view-frame',revision:'1',views:[oneScopeJson],focusOwner:oneScopeJson,popupOwner:null,
    frame:{surfaceProtocol:2,keyboardParent:true,motion:'reduced',
      appearance:{theme:'night',textScale:100,effectsOff:false,reducedTransparency:false},
      publication,lease:'0',mode:'closed',status,bar,popup:[]},
    announcer:{scope:oneScopeJson,surface:'bar'},announcement:announce},requests,focus:[]});
  const blockedGroup = group('group:'+host+':1:1:application:demo',true);
  const closedStatus = 'Minimize: not confirmed for Window. Reconnect to read window status; the action will not be repeated.';
  const lostBar = [row('bar:reconnect','reconnect','Reconnect','Reconnect to the window system','',true),
    ...ordinary(host,'4'),blockedGroup];
  const lostPacket = commit('8',closedStatus,lostBar,[]);
  const disconnected = patch(pending,[
    change(cp('controller','a','publication'),C('7'),C('8')),
    change(dp('presentation'),J(C('3')),J(C('4'))),
    change(dp('expected'),J(C('1')),none()),
    change(dp('settingsExpected'),J(C('2')),none()),
    change(dp('motionExpected'),J(C('3')),none()),
    change(dp('shortcutExpected'),J(C('4')),none()),
    change(dp('workspaceNavigation','binding'),J(binding),none()),
    change(dp('launch','a','revision'),C('4'),C('5')),
    change(dp('launch','a','host'),J(host),none()),
    change(sp('phase'),{$:'Ready'},{$:'Detached'}),
    change(sp('notice'),'Connected','Connection lost. Reconnect to continue.'),
    change(sp('effects','connected'),true,false),
    change(sp('effects','transaction'),J(tx('Pending')),J(tx('Unknown'))),
    change(sp('effects','unresolved'),L([tx('Pending')]),L([tx('Unknown')])),
    change(dp('adapterNotice'),none(),J({source:{$:'Windows'},binding,request:C('1'),service:none(),revision:none()})),
    change(cp('announcements','a'),zero(),C('1')),
    change(cp('announcements','b'),none(),J(rawAnnounce)),
  ]);
  const reconnectBar = [row('bar:reconnect','reconnect','Reconnect','Reconnect to the window system','',false),
    ...ordinary(host,'5'),blockedGroup];
  const reconnectPacket = commit('9',closedStatus,reconnectBar,[{protocolVersion:3,kind:'host-reconnect'}]);
  const reconnecting = patch(disconnected,[
    change(cp('controller','a','publication'),C('8'),C('9')),
    change(dp('presentation'),J(C('4')),J(C('5'))),
    change(dp('launch','a','revision'),C('5'),C('6')),
    change(sp('reconnecting'),false,true),
    change(sp('notice'),'Connection lost. Reconnect to continue.','Reconnecting…'),
  ]);
  const refresh = row('bar:recovery-refresh','applications:'+host2+':6:bar:recovery-refresh',
    'Refresh window status','Refresh window status; read observations without retrying actions','Observation only',true);
  const app = row('bar:applications','applications:'+host2+':6:control:opener',
    'Applications','Open applications','',true);
  const pendingRebindStatus = 'Minimize: not confirmed for Window. Check your windows; Refresh only reads status.';
  const requests = [request('catalog-request','5'),request('shell-settings-request','6'),
    request('motion-preferences-request','7'),request('shortcut-preferences-request','8'),
    request('projection-request','2')];
  const reboundBar = [refresh,group('detached-group',true),app,...ordinary(host2,'6')];
  const reboundPacket = commit('10',pendingRebindStatus,reboundBar,requests);
  const batch = {scope:oneScope,revision:C('1'),publication:C('10'),lease:zero(),binding:B2,
    wire:JSON.stringify(reboundPacket),observations:L([pair('projection-request',C('2'))]),
    operations:empty(),catalogs:L([{binding:B2,request:C('5')}])};
  // The two original batches are literal values from the separately authored
  // source-derived GIVEN; neither this code nor the dependency reads runtime output.
  const priorBatches = pending.controller.a.batches;
  const rebound = patch(reconnecting,[
    change(cp('controller','a','publication'),C('9'),C('10')),
    change(dp('presentation'),J(C('5')),J(C('6'))),
    change(dp('request'),C('4'),C('8')),
    change(dp('expected'),none(),J(C('5'))),
    change(dp('settingsExpected'),none(),J(C('6'))),
    change(dp('motionExpected'),none(),J(C('7'))),
    change(dp('shortcutExpected'),none(),J(C('8'))),
    change(dp('workspaceNavigation','binding'),none(),J(B2)),
    change(dp('launch','a','revision'),C('6'),C('8')),
    change(dp('launch','a','host'),none(),J(host2)),
    change(sp('binding'),J(binding),J(B2)),
    change(sp('request'),C('1'),C('2')),
    change(sp('expected'),none(),J(C('2'))),
    change(sp('phase'),{$:'Detached'},{$:'Reconciling'}),
    change(sp('reconnecting'),true,false),
    change(sp('notice'),'Reconnecting…','Updating window information…'),
    change(dp('adapterNotice'),J({source:{$:'Windows'},binding,request:C('1'),service:none(),revision:none()}),none()),
    change(cp('batches'),priorBatches,L([batch])),
  ]);
  const oldReceipt = requestId => ({kind:'incoming',value:gateway({protocolVersion:3,kind:'effect-outcome',
    effectProtocol:1,binding:bindingJson,intent:{...wireIntent,request:requestId},status:'Refused',
    reason:'dependency-mismatch',revision:'2',outputGeneration:'1'})});
  const refusedBar = [refresh,group('detached-group',false),app,...ordinary(host2,'6')];
  const refusedPacket = commit('11','Minimize: refused for Window. Refresh window status, then choose again.',refusedBar,[]);
  const historicalSettled = patch(rebound,[
    change(cp('controller','a','publication'),C('10'),C('11')),
    change(sp('effects','transaction'),J(tx('Unknown')),J(tx('Refused'))),
    change(sp('effects','unresolved'),L([tx('Unknown')]),empty()),
    change(sp('issued'),L([issued]),empty()),
  ]);
  // IMPORTANT: Shell.elm applies an exact retained old-binding receipt BEFORE
  // testing current binding. Thus the final step below describes code-as-built,
  // and contradicts a blanket 'all old receipts rejected' contract. It must not
  // be presented as proof of that contract or as authority to weaken it.
  return [{name:'window-pending-disconnect-rebind-historical-receipt',steps:[
    copy(original[0].steps[0]),given,
    {input:{kind:'transportLost'},expected:{state:copy(disconnected),effects:wrap(lostPacket)}},
    {input:viewAction('8','bar:group:application:demo'),expected:{state:copy(disconnected),effects:copy(NIL)}},
    {input:viewAction('8','bar:reconnect'),expected:{state:copy(reconnecting),effects:wrap(reconnectPacket)}},
    {input:{kind:'incoming',value:gateway({protocolVersion:3,kind:'attached',binding:b2})},
      expected:{state:copy(rebound),effects:wrap(reboundPacket)}},
    {input:oldReceipt('2'),expected:{state:copy(rebound),effects:copy(NIL)}},
    {input:oldReceipt('1'),expected:{state:copy(historicalSettled),effects:wrap(refusedPacket)}},
  ]}];
}

function buildAdditionalCases(c) {
  const { baseCases, materialize, cloneLiteral: copy, literalPatches: patch,
    attachedPacket, attachedBatch, oneScope, oneScopeJson, binding, host,
    disconnectedText, disconnectedCorrelation, matchingCatalog, empty, none, zero, NIL } = c;
  if (!Array.isArray(baseCases) || typeof materialize !== 'function' || typeof copy !== 'function' ||
      typeof patch !== 'function' || [attachedPacket,attachedBatch,oneScope,oneScopeJson,binding,host,
        disconnectedText,disconnectedCorrelation,matchingCatalog,empty,none,zero,NIL].some(x => x === undefined)) {
    throw new Error('complete independent rebind literal dependencies required');
  }
  const base = baseCases.find(item => item.name === 'catalog-pending-disconnect-rejects-late-receipt');
  if (!base) throw new Error('source-literal disconnected/reconnect baseline absent');
  const previous = materialize(base);
  if (!previous || !Array.isArray(previous.steps) || previous.steps.length !== 6 ||
      previous.steps[5].input.kind !== 'incoming') throw new Error('unexpected independent baseline shape');
  // previous is produced solely from source-transcribed literal cases, not a
  // fixture capture.  The explicit preconditions below bind every changed leaf;
  // all other fields remain in the complete copied model.
  const reconnecting = previous.steps[5].expected.state;
  const one = { $: 'Counter', a: '1' }, two = { $: 'Counter', a: '2' };
  const nextBindingJson = { lifetime: '1', session: '1', frontend: '2' };
  const nextBinding = { $: 'Binding', a: one, b: one, c: two };
  const nextHost = '{"lifetime":"1","session":"1","frontend":"2"}';
  const rows = attachedPacket.projection.frame.bar.map(row => ({
    id: row.id, domId: row.domId.replace(host, nextHost).replace(':3:', ':6:'),
    label: row.label, ariaLabel: row.ariaLabel, detail: row.detail, enabled: row.enabled, focusOnly: row.focusOnly,
  }));
  // All keys follow OutputController.commit/frame and Surface.packet's source
  // insertion order. The batch wire is the exact compact encoding of this
  // independent literal, not a copy of the runtime-emitted commit.
  const packet = { viewProtocol: 1, kind: 'view-commit', projection: {
    viewProtocol: 1, kind: 'view-frame', revision: '1', views: [oneScopeJson], focusOwner: oneScopeJson,
    popupOwner: null, frame: { surfaceProtocol: 2, keyboardParent: true, motion: 'reduced',
      appearance: { theme: 'night', textScale: 100, effectsOff: false, reducedTransparency: false },
      publication: '7', lease: '0', mode: 'closed', status: 'Applications connected. Window controls unavailable.',
      bar: rows, popup: [] }, announcer: { scope: oneScopeJson, surface: 'bar' },
    announcement: { interrupt: false, sequence: '1', correlation: disconnectedCorrelation, text: disconnectedText },
  }, requests: [{ protocolVersion: 3, kind: 'catalog-request', binding: nextBindingJson, requestId: '2' }], focus: [] };
  const batch = { scope: oneScope, revision: one, publication: { $:'Counter', a:'7' }, lease: zero(),
    binding: nextBinding, wire: JSON.stringify(packet), observations: empty(), operations: empty(),
    catalogs: { $:'::', a: { binding: nextBinding, request: two }, b: empty() } };
  const changes = [
    { path:['controller','a','controller','a','publication'], before:{$:'Counter',a:'6'}, after:{$:'Counter',a:'7'} },
    { path:['controller','a','controller','a','desktop','presentation'], before:{$:'Just',a:{$:'Counter',a:'5'}}, after:{$:'Just',a:{$:'Counter',a:'6'}} },
    { path:['controller','a','controller','a','desktop','request'], before:one, after:two },
    { path:['controller','a','controller','a','desktop','expected'], before:none(), after:{$:'Just',a:two} },
    { path:['controller','a','controller','a','desktop','workspaceNavigation','binding'], before:none(), after:{$:'Just',a:nextBinding} },
    { path:['controller','a','controller','a','desktop','launch','a','revision'], before:{$:'Counter',a:'6'}, after:{$:'Counter',a:'8'} },
    { path:['controller','a','controller','a','desktop','launch','a','host'], before:none(), after:{$:'Just',a:nextHost} },
    { path:['controller','a','controller','a','desktop','windows','shell','binding'], before:{$:'Just',a:binding}, after:{$:'Just',a:nextBinding} },
    { path:['controller','a','controller','a','desktop','windows','shell','applicationOnly'], before:false, after:true },
    { path:['controller','a','controller','a','desktop','windows','shell','phase'], before:{$:'Detached'}, after:{$:'Reconciling'} },
    { path:['controller','a','controller','a','desktop','windows','shell','reconnecting'], before:true, after:false },
    { path:['controller','a','controller','a','desktop','windows','shell','notice'], before:'Reconnecting…', after:'Applications connected. Window controls unavailable.' },
    { path:['controller','a','controller','a','desktop','adapterNotice'], before:{$:'Just',a:{source:{$:'Windows'},binding,request:zero(),service:none(),revision:none()}}, after:none() },
    { path:['controller','a','batches'], before:{$:'::',a:attachedBatch,b:empty()}, after:{$:'::',a:batch,b:empty()} },
  ];
  const rebound = patch(reconnecting, changes);
  const input = { kind:'incoming', value:{ bridgeProtocol:1, kind:'native-event', payload:{
    protocolVersion:3, kind:'application-attached', binding:nextBindingJson, nativeOperations:[] } } };
  const effect = { $:'::', a:{$:'Publish',a:{$:0,a:packet}}, b:empty() };
  const reboundCase = { name:'catalog-rebind-new-frontend-no-old-replay', steps:copy(previous.steps).concat([
    { input, expected:{ state:copy(rebound), effects:effect } },
    { input:copy(matchingCatalog), expected:{ state:copy(rebound), effects:copy(NIL) } },
  ]) };
  const cases = [reboundCase];
  const missing = [];
  // Optional factories are independently authored/hashed complete literals,
  // passed explicitly by Root when integrated. A missing factory is reported,
  // never treated as coverage or replaced with a captured worker state.
  for (const [name, factory] of [['pin-malformed',buildMalformedPinPreferenceCases], ['window',buildWindowReceiptCases], ['window-rebind',buildWindowRebindCases], ['delay',buildLaunchDeadlineCases],
    ['preference',c.buildPreferenceReceiptCases]]) {
    if (factory === undefined) { missing.push(name); continue; }
    if (typeof factory !== 'function') throw new Error('invalid source-literal factory: ' + name);
    const more = factory({ ...c, buildWindowCases: buildWindowReceiptCases, windowReadyOnly: false });
    if (!Array.isArray(more) || more.length === 0) throw new Error('empty source-literal factory: ' + name);
    for (const item of more) {
      if (!item || typeof item.name !== 'string' || !Array.isArray(item.steps) || item.steps.length < 2) {
        throw new Error('invalid complete literal case: ' + name);
      }
      cases.push(item);
    }
  }
  if (new Set(cases.map(item => item.name)).size !== cases.length) throw new Error('duplicate case names');
  return { cases, missing };
}

'use strict';

/*
 * Independent source-literal full-model and every-effect regression factory for
 * Desktop.elm finite receipt decoding (d6fa51ec) across reachable pending
 * Settings, MotionPreferences, and ShortcutPreferences save flows.
 *
 * DRAFT ONLY — NOT EXECUTED, NOT A CANONICAL EDIT, NOT EARS ACCEPTANCE.
 * Every GIVEN, intermediate state delta, Publish frame, retained batch wire,
 * and OutcomeAnnouncements record below is transcribed directly from the actual
 * Elm source contracts at:
 *   - Desktop.elm (sha256:91223c94074f8ff908b2ed66f52e8025c8afcb78a977d4a5f3daf44df8ce7af4)
 *   - DesktopPolicy.elm (sha256:018934fe4762e8357665ce7c37cb289883c6cdd1bad31d6592402b369d7bad3e)
 *   - OutputController.elm (sha256:fdf7b44483ec9312182a1b50bb2bbb5d52b804538e5c4d4ce5a4a8479e9af6ae)
 *   - SurfaceController.elm (sha256:2e86781c41c1b1c62d518e886ee965a875a04ea88980159a00511c549b25e998)
 *   - Surface.elm (sha256:91d38d818e40523cd395d3622633676149c42b8b9b0be3a40223a13bdf45d9ca)
 *   - Settings.elm, MotionPreferences.elm, Motion.elm, ShortcutPreferences.elm,
 *     PointerOwnership.elm, OutcomeAnnouncements.elm, AnnouncementMessage.elm.
 *
 * Zero reducer capture, zero oracle harvesting, zero host globals (sandbox-safe
 * for qa/tea-contract.cjs loadOracle).
 *
 * Exports:
 *   - buildPreferenceReceiptCases(c): returns 7 complete { name, steps } cases
 *     (26 non-prelude tested transitions) exercising malformed save-status
 *     complete no-ops (contrasted against pre-d6fa51ec else-branch
 *     notice/outcome/publication mutations) followed by valid Unknown (retaining
 *     pending reservation without replay), Refused (including
 *     OutcomeAnnouncements settings-refused), Stored (shortcut-only), and Saved
 *     (including Motion.propose syncMotion profile-set emission).
 *     If c.preferenceSeedsOnly === true, returns { pendingSettings,
 *     pendingMotion, pendingShortcut } seed descriptors compatible with
 *     terra-browser-tea-preference-feedback.cjs.
 *   - buildPreferenceSeeds(c): convenience wrapper returning those 3 seeds
 *     (each exposing { prelude, setupTimers, given, givenEffects, requestId,
 *     unknown, refused, saved[, stored] }).
 */

function buildPreferenceSeeds(c) {
  if (!c || typeof c !== 'object') {
    throw new Error('independent full GIVEN context required');
  }
  const {
    cloneLiteral: copy,
    literalPatches: patch,
    initial,
    topologyChanges,
    oneViewChanges,
    oneScope,
    oneScopeJson,
    binding,
    bindingJson,
    host,
    empty,
    none,
    zero,
    NIL,
  } = c;
  if ([copy, patch, initial, topologyChanges, oneViewChanges, oneScope,
       oneScopeJson, binding, bindingJson, host, empty, none, zero, NIL]
        .some(value => value === undefined)) {
    throw new Error('independent full GIVEN dependencies required');
  }

  const counter = text => ({ $: 'Counter', a: text });
  const just = value => ({ $: 'Just', a: value });
  const list = values => values.reduceRight((tail, value) => ({ $: '::', a: value, b: tail }), empty());
  const tuple2 = (a, b) => ({ $: '#2', a, b });
  const publish = packet => ({ $: '::', a: { $: 'Publish', a: { $: 0, a: packet } }, b: empty() });

  // Exact Elm E.object key insertion orders for byte-exact batch.wire strings.
  const wireScope = { id: String(oneScopeJson.id), generation: String(oneScopeJson.generation) };
  const wireBinding = {
    lifetime: String(bindingJson.lifetime),
    session: String(bindingJson.session),
    frontend: String(bindingJson.frontend),
  };

  const controlRow = (id, domId, label, ariaLabel, detail, enabled) => ({
    id,
    domId,
    label,
    ariaLabel,
    detail,
    enabled,
    focusOnly: false,
  });

  const keyPrefix = presentation => 'applications:' + host + ':' + presentation + ':';

  // Surface.barControls when phase == Reconciling, applicationOnly == False,
  // pinIds == [], ordinaryGroups == [], recoveryNeeded == False.
  const shellBarRows = presentation => {
    const p = keyPrefix(presentation);
    return [
      controlRow('bar:applications', p + 'control:opener', 'Applications', 'Open applications', '', true),
      controlRow('bar:overview', p + 'control:overview-opener', 'Task View', 'Open Task View', '', false),
      controlRow('bar:switcher', p + 'control:switcher-opener', 'Switch windows', 'Open window switcher', '', false),
      controlRow('bar:notifications', p + 'notifications:opener', 'Notifications', 'Open notifications', '', true),
      controlRow('bar:files', p + 'files:opener', 'Files', 'Open Files menu', '', true),
      controlRow('bar:system', p + 'system:opener', 'System', 'Open system menu', '', true),
      controlRow('bar:settings', p + 'settings:opener', 'Settings', 'Open settings', '', true),
    ];
  };

  const motionLabel = override => (
    override === 'System' ? 'Follow system'
      : override === 'Reduce' ? 'Reduced motion'
        : 'Full motion'
  );

  const shortcutRoutes = [
    ['applications', 'Apps menu'],
    ['system', 'System menu'],
    ['notifications', 'Notification history'],
  ];

  // Surface.controls for model.settingsOpen == True, model.settingsHelp == True
  // (Surface.elm:192-238). Every popup control in settings mode sets ariaLabel === label.
  const settingsPopupRows = spec => {
    const p = keyPrefix(spec.presentation);
    const ctl = (id, label, detail, enabled) => controlRow(
      id,
      p + (id === 'control:close' ? 'settings:close' : id),
      label,
      label,
      detail,
      enabled
    );
    const settingsReady = spec.settingsSnapshot !== null && !spec.settingsPending && spec.settingsExpectedEmpty;
    const settingsChanged = spec.settingsSnapshot !== null && (
      spec.settingsSnapshot.theme !== spec.settingsDraft.theme ||
      spec.settingsSnapshot.textScale !== spec.settingsDraft.textScale ||
      spec.settingsSnapshot.effectsOff !== spec.settingsDraft.effectsOff ||
      spec.settingsSnapshot.reducedTransparency !== spec.settingsDraft.reducedTransparency
    );
    const motionReady = spec.motionSnapshot !== null && !spec.motionPending && spec.motionExpectedEmpty;
    const motionSelected = spec.motionSnapshot !== null ? spec.motionSnapshot : 'System';
    const desiredProfile = spec.motionSnapshot === 'Full' ? 'full' : 'reduced';
    const motionHeadline = spec.motionSnapshot === null
      ? spec.motionNotice
      : spec.motionProfilePending
        ? 'Applying motion preference…'
        : (desiredProfile === 'reduced' ? 'Reduced motion: instant transitions' : 'Full motion') +
          ' · ' + motionLabel(motionSelected);

    const shortcutWritable = spec.shortcutSnapshot !== null && spec.shortcutInventory !== null && !spec.shortcutPending;
    const shortcutReady = shortcutWritable && spec.shortcutExpectedEmpty;
    const shortcutAllowed = (choice, row) => (
      choice === 'keep' ? true
        : choice === 'default' ? row.defaultAvailable
          : choice === 'alternate' ? row.alternateAvailable
            : false
    );
    const shortcutReadyToSave = spec.shortcutExpectedEmpty && shortcutWritable &&
      spec.shortcutInventory !== null &&
      shortcutRoutes.every(([route]) => shortcutAllowed(spec.shortcutDraft[route], spec.shortcutInventory[route]));
    const shortcutChanged = (
      spec.shortcutSnapshot !== null &&
      shortcutRoutes.some(([route]) => spec.shortcutSnapshot[route] !== spec.shortcutDraft[route])
    ) || (
      spec.shortcutInventory !== null &&
      shortcutRoutes.some(([route]) => spec.shortcutDraft[route] !== spec.shortcutInventory[route].active)
    );

    const rows = [
      ctl('control:close', 'Close settings', '', true),
      ctl('settings:help', 'Dismiss help', 'Expanded', true),
      ctl('settings:help:text:keyboard', 'Keyboard navigation', 'Tab and Shift+Tab move focus. Arrows move through lists; Home/End reach endpoints. Enter chooses; Escape closes.', false),
      ctl('settings:help:text:preferences', 'Keeping your preferences', 'Save applies appearance preferences. Motion has its own Save. Dismissing help keeps unsaved edits.', false),
      ctl('settings:help:text:recovery', 'When an action is not confirmed', 'Pending is waiting; Refused did not proceed; Unknown is unconfirmed. Refresh reads state without repeating an action.', false),
      ctl('settings:effects-off', 'Disable soft effects', spec.settingsDraft.effectsOff ? 'On' : 'Off', settingsReady),
      ctl('settings:reduced-transparency', 'Reduce transparency', spec.settingsDraft.reducedTransparency ? 'On' : 'Off', settingsReady),
      ctl('settings:motion', motionHeadline, spec.motionNotice, false),
      ctl('settings:motion:system', 'Follow system', spec.motionDraft === 'System' ? 'Selected' : '', motionReady),
      ctl('settings:motion:reduced', 'Reduced motion', spec.motionDraft === 'Reduce' ? 'Selected' : '', motionReady),
      ctl('settings:motion:full', 'Full motion', spec.motionDraft === 'Full' ? 'Selected' : '', motionReady),
      ctl('settings:motion:save', 'Save motion preference', 'Apply and keep across restart', motionReady && spec.motionDraft !== motionSelected),
      ctl('settings:motion:refresh', 'Refresh motion preference', 'Read stored preference; no write is repeated', spec.motionExpectedEmpty),
      ctl('settings:theme:night', 'Night theme', spec.settingsDraft.theme === 'night' ? 'Selected' : '', settingsReady),
      ctl('settings:theme:dawn', 'Dawn theme', spec.settingsDraft.theme === 'dawn' ? 'Selected' : '', settingsReady),
      ctl('settings:theme:high-contrast', 'High contrast theme', spec.settingsDraft.theme === 'high-contrast' ? 'Selected' : '', settingsReady),
      ctl('settings:scale:100', 'Text size 100%', spec.settingsDraft.textScale === 100 ? 'Selected' : '', settingsReady),
      ctl('settings:scale:125', 'Text size 125%', spec.settingsDraft.textScale === 125 ? 'Selected' : '', settingsReady),
      ctl('settings:scale:150', 'Text size 150%', spec.settingsDraft.textScale === 150 ? 'Selected' : '', settingsReady),
      ctl('settings:scale:200', 'Text size 200%', spec.settingsDraft.textScale === 200 ? 'Selected' : '', settingsReady),
      ctl('settings:save', 'Save settings', 'Apply and keep across restart', settingsReady && settingsChanged),
      ctl('settings:refresh', 'Refresh settings', 'Read stored values; discard unsaved changes', spec.settingsExpectedEmpty),
      ctl('settings:shortcuts:notice:state', spec.shortcutNotice, '', false),
    ];

    for (const [route, routeLabel] of shortcutRoutes) {
      const inv = spec.shortcutInventory ? spec.shortcutInventory[route] : null;
      const stateText = inv
        ? routeLabel + ': ' + (inv.active === 'keep' ? 'existing shortcut preserved' : inv.active === 'default' ? inv.defaultChord : inv.alternateChord)
        : routeLabel + ': live bindings unavailable';
      rows.push(
        ctl('settings:shortcuts:' + route + ':state', stateText, '', false),
        ctl('settings:shortcuts:' + route + ':keep', 'Keep existing shortcut for ' + routeLabel, spec.shortcutDraft[route] === 'keep' ? 'Selected' : '', shortcutReady),
        ctl('settings:shortcuts:' + route + ':default', 'Use ' + routeLabel + ' default', spec.shortcutDraft[route] === 'default' ? 'Selected' : '', shortcutReady && inv !== null && inv.defaultAvailable),
        ctl('settings:shortcuts:' + route + ':default:state', inv ? inv.defaultChord + (inv.defaultAvailable ? ' · Available' : ' · Unavailable: existing binding') : 'Default unavailable', '', false),
        ctl('settings:shortcuts:' + route + ':alternate', 'Use ' + routeLabel + ' alternative', spec.shortcutDraft[route] === 'alternate' ? 'Selected' : '', shortcutReady && inv !== null && inv.alternateAvailable),
        ctl('settings:shortcuts:' + route + ':alternate:state', inv ? inv.alternateChord + (inv.alternateAvailable ? ' · Available' : ' · Unavailable: existing binding') : 'Alternative unavailable', '', false)
      );
    }

    rows.push(
      ctl('settings:shortcuts:save', 'Save shortcut choices', 'Apply only the free chosen chords; preserve existing bindings', shortcutReadyToSave && shortcutChanged),
      ctl('settings:shortcuts:refresh', 'Refresh shortcut choices', 'Read stored choices and live bindings without repeating an action', spec.shortcutExpectedEmpty)
    );
    return rows;
  };

  const settingsCommit = spec => {
    const appearanceSource = spec.settingsSnapshot !== null
      ? spec.settingsSnapshot
      : { theme: 'night', textScale: 100, effectsOff: false, reducedTransparency: false };
    const motionProfile = spec.motionSnapshot === 'Full' ? 'full' : 'reduced';
    const statusText = (spec.settingsExpectedEmpty ? spec.settingsNotice : 'Loading settings…') + ' · ' + spec.shortcutNotice;
    return {
      viewProtocol: 1,
      kind: 'view-commit',
      projection: {
        viewProtocol: 1,
        kind: 'view-frame',
        revision: '1',
        views: [wireScope],
        focusOwner: wireScope,
        popupOwner: wireScope,
        frame: {
          surfaceProtocol: 2,
          keyboardParent: true,
          motion: motionProfile,
          appearance: {
            theme: appearanceSource.theme,
            textScale: appearanceSource.textScale,
            effectsOff: appearanceSource.effectsOff,
            reducedTransparency: appearanceSource.reducedTransparency,
          },
          publication: spec.publication,
          lease: spec.lease,
          mode: 'settings',
          status: statusText,
          bar: shellBarRows(spec.presentation),
          popup: settingsPopupRows(spec),
        },
        announcer: { scope: wireScope, surface: 'popup' },
        announcement: spec.announcement || null,
      },
      requests: spec.requests,
      focus: spec.focus,
    };
  };

  // Event 1: oneView topology (publication 3, lease 0, presentation 2).
  const oneViewBaseChanges = copy(topologyChanges);
  oneViewBaseChanges[1].after = counter('3');
  const oneViewState = patch(initial, oneViewBaseChanges.concat(copy(oneViewChanges)));

  // Event 2: full shell "attached" (applicationOnly == false so bar:settings is enabled).
  // Emits 5 read requests (catalog 1, settings 2, motion 3, shortcuts 4, projection 1).
  const attachRequests = [
    { protocolVersion: 3, kind: 'catalog-request', binding: wireBinding, requestId: '1' },
    { protocolVersion: 3, kind: 'shell-settings-request', binding: wireBinding, requestId: '2' },
    { protocolVersion: 3, kind: 'motion-preferences-request', binding: wireBinding, requestId: '3' },
    { protocolVersion: 3, kind: 'shortcut-preferences-request', binding: wireBinding, requestId: '4' },
    { protocolVersion: 3, kind: 'projection-request', binding: wireBinding, requestId: '1' },
  ];
  const attachCommit = {
    viewProtocol: 1,
    kind: 'view-commit',
    projection: {
      viewProtocol: 1,
      kind: 'view-frame',
      revision: '1',
      views: [wireScope],
      focusOwner: wireScope,
      popupOwner: null,
      frame: {
        surfaceProtocol: 2,
        keyboardParent: true,
        motion: 'reduced',
        appearance: { theme: 'night', textScale: 100, effectsOff: false, reducedTransparency: false },
        publication: '4',
        lease: '0',
        mode: 'closed',
        status: 'Updating window information…',
        bar: shellBarRows('3'),
        popup: [],
      },
      announcer: { scope: wireScope, surface: 'bar' },
      announcement: null,
    },
    requests: attachRequests,
    focus: [],
  };
  const batchAttach = {
    scope: oneScope,
    revision: counter('1'),
    publication: counter('4'),
    lease: zero(),
    binding,
    wire: JSON.stringify(attachCommit),
    observations: list([tuple2('projection-request', counter('1'))]),
    operations: empty(),
    catalogs: list([{ binding, request: counter('1') }]),
  };

  // Event 3: pointer-ownership idle (Desktop.elm:621 requires idle observation
  // for non-applicationOnly gestureAction; SurfaceController.elm:87-94 advances
  // publication 4->5 without advancing Desktop.presentation '3' or adding a batch).

  // Event 4: bar:settings at pub '5' -> OpenSettings (requests settings 5 & shortcuts 6,
  // lease 0->1, pub 5->6, pres 3->6).
  const openSettingsRequests = [
    { protocolVersion: 3, kind: 'shell-settings-request', binding: wireBinding, requestId: '5' },
    { protocolVersion: 3, kind: 'shortcut-preferences-request', binding: wireBinding, requestId: '6' },
  ];
  const openSettingsCommit = settingsCommit({
    publication: '6',
    lease: '1',
    presentation: '6',
    settingsSnapshot: null,
    settingsDraft: { theme: 'night', textScale: 100, effectsOff: false, reducedTransparency: false },
    settingsPending: false,
    settingsExpectedEmpty: false,
    settingsNotice: 'Loading settings…',
    motionSnapshot: null,
    motionDraft: 'System',
    motionPending: false,
    motionProfilePending: false,
    motionExpectedEmpty: false,
    motionNotice: 'Reading motion preference…',
    shortcutSnapshot: null,
    shortcutInventory: null,
    shortcutDraft: { applications: 'undecided', system: 'undecided', notifications: 'undecided' },
    shortcutPending: false,
    shortcutExpectedEmpty: false,
    shortcutNotice: 'Loading shortcut choices…',
    requests: openSettingsRequests,
    focus: [keyPrefix('6') + 'settings:close'],
  });
  const batchOpenSettings = {
    scope: oneScope,
    revision: counter('1'),
    publication: counter('6'),
    lease: counter('1'),
    binding,
    wire: JSON.stringify(openSettingsCommit),
    observations: empty(),
    operations: empty(),
    catalogs: empty(),
  };

  const fingerprint = 'a'.repeat(64);
  const baseShortcutInventoryWire = {
    fingerprint,
    applications: { defaultChord: 'SUPER + ALT + SPACE', alternateChord: 'SUPER + CTRL + ALT + SPACE', defaultAvailable: true, alternateAvailable: true, active: 'keep' },
    system: { defaultChord: 'SUPER + ESCAPE', alternateChord: 'SUPER + CTRL + ESCAPE', defaultAvailable: true, alternateAvailable: true, active: 'default' },
    notifications: { defaultChord: 'SUPER + SHIFT + ALT + comma', alternateChord: 'SUPER + CTRL + ALT + comma', defaultAvailable: true, alternateAvailable: true, active: 'keep' },
  };
  const appliedShortcutInventoryWire = {
    fingerprint,
    applications: { defaultChord: 'SUPER + ALT + SPACE', alternateChord: 'SUPER + CTRL + ALT + SPACE', defaultAvailable: true, alternateAvailable: true, active: 'alternate' },
    system: { defaultChord: 'SUPER + ESCAPE', alternateChord: 'SUPER + CTRL + ESCAPE', defaultAvailable: true, alternateAvailable: true, active: 'default' },
    notifications: { defaultChord: 'SUPER + SHIFT + ALT + comma', alternateChord: 'SUPER + CTRL + ALT + comma', defaultAvailable: true, alternateAvailable: true, active: 'keep' },
  };
  const choiceTag = raw => (
    raw === 'keep' ? { $: 'Keep' }
      : raw === 'default' ? { $: 'Default' }
        : raw === 'alternate' ? { $: 'Alternate' }
          : { $: 'Undecided' }
  );
  const inventoryModel = wire => ({
    fingerprint: wire.fingerprint,
    applications: {
      defaultChord: wire.applications.defaultChord,
      alternateChord: wire.applications.alternateChord,
      defaultAvailable: wire.applications.defaultAvailable,
      alternateAvailable: wire.applications.alternateAvailable,
      active: choiceTag(wire.applications.active),
    },
    system: {
      defaultChord: wire.system.defaultChord,
      alternateChord: wire.system.alternateChord,
      defaultAvailable: wire.system.defaultAvailable,
      alternateAvailable: wire.system.alternateAvailable,
      active: choiceTag(wire.system.active),
    },
    notifications: {
      defaultChord: wire.notifications.defaultChord,
      alternateChord: wire.notifications.alternateChord,
      defaultAvailable: wire.notifications.defaultAvailable,
      alternateAvailable: wire.notifications.alternateAvailable,
      active: choiceTag(wire.notifications.active),
    },
  });

  const nightValuesModel = { theme: { $: 'Night' }, textScale: 100, effectsOff: false, reducedTransparency: false };
  const dawnValuesModel = { theme: { $: 'Dawn' }, textScale: 100, effectsOff: false, reducedTransparency: false };
  const nightValuesWire = { theme: 'night', textScale: 100, effectsOff: false, reducedTransparency: false };
  const dawnValuesWire = { theme: 'dawn', textScale: 100, effectsOff: false, reducedTransparency: false };

  const baseShortcutChoicesWire = { applications: 'keep', system: 'default', notifications: 'keep' };
  const desiredShortcutChoicesWire = { applications: 'alternate', system: 'default', notifications: 'keep' };
  const baseShortcutChoicesModel = { applications: { $: 'Keep' }, system: { $: 'Default' }, notifications: { $: 'Keep' } };
  const desiredShortcutChoicesModel = { applications: { $: 'Alternate' }, system: { $: 'Default' }, notifications: { $: 'Keep' } };
  const loadedShortcutNotice = 'Shortcut choices loaded. Conflicting bindings are preserved; choose a free chord or keep the existing shortcut.';

  const modelPath = ['controller', 'a', 'controller', 'a', 'desktop'];
  const dpath = (...tail) => modelPath.concat(tail);

  // State after Events 1..7 (loadedSettingsMotionShortcuts: pub 9, lease 1, pres 9, req 6).
  const loadedState = patch(oneViewState, [
    { path: ['controller', 'a', 'controller', 'a', 'publication'], before: counter('3'), after: counter('9') },
    { path: ['controller', 'a', 'controller', 'a', 'lease'], before: zero(), after: counter('1') },
    { path: ['controller', 'a', 'batches'], before: empty(), after: list([batchOpenSettings, batchAttach]) },
    { path: dpath('presentation'), before: just(counter('2')), after: just(counter('9')) },
    { path: dpath('request'), before: zero(), after: counter('6') },
    { path: dpath('expected'), before: none(), after: just(counter('1')) },
    { path: dpath('workspaceNavigation', 'binding'), before: none(), after: just(binding) },
    { path: dpath('pointer', 'observation'), before: none(), after: just({ binding, serial: counter('1'), state: { $: 'Idle' }, owner: none() }) },
    { path: dpath('launch', 'a', 'revision'), before: counter('2'), after: counter('4') },
    { path: dpath('launch', 'a', 'host'), before: none(), after: just(host) },
    { path: dpath('windows', 'shell', 'binding'), before: none(), after: just(binding) },
    { path: dpath('windows', 'shell', 'request'), before: zero(), after: counter('1') },
    { path: dpath('windows', 'shell', 'expected'), before: none(), after: just(counter('1')) },
    { path: dpath('windows', 'shell', 'phase'), before: { $: 'Detached' }, after: { $: 'Reconciling' } },
    { path: dpath('windows', 'shell', 'reconnecting'), before: true, after: false },
    { path: dpath('windows', 'shell', 'notice'), before: 'Connecting…', after: 'Updating window information…' },
    { path: dpath('settingsOpen'), before: false, after: true },
    { path: dpath('settings', 'snapshot'), before: none(), after: just({ schema: 2, revision: counter('1'), values: nightValuesModel }) },
    { path: dpath('settings', 'notice'), before: 'Loading settings…', after: 'Settings loaded.' },
    { path: dpath('motion', 'preferences', 'snapshot'), before: none(), after: just({ revision: counter('1'), override: { $: 'System' } }) },
    { path: dpath('motion', 'preferences', 'notice'), before: 'Reading motion preference…', after: 'Motion preference loaded.' },
    { path: dpath('shortcutPreferences', 'snapshot'), before: none(), after: just({ schema: 1, revision: counter('1'), choices: baseShortcutChoicesModel }) },
    { path: dpath('shortcutPreferences', 'inventory'), before: none(), after: just(inventoryModel(baseShortcutInventoryWire)) },
    { path: dpath('shortcutPreferences', 'draft'), before: { applications: { $: 'Undecided' }, system: { $: 'Undecided' }, notifications: { $: 'Undecided' } }, after: baseShortcutChoicesModel },
    { path: dpath('shortcutPreferences', 'notice'), before: 'Loading shortcut choices…', after: loadedShortcutNotice },
  ]);

  const loadedSpec = {
    lease: '1',
    settingsSnapshot: nightValuesWire,
    settingsDraft: nightValuesWire,
    settingsPending: false,
    settingsExpectedEmpty: true,
    settingsNotice: 'Settings loaded.',
    motionSnapshot: 'System',
    motionDraft: 'System',
    motionPending: false,
    motionProfilePending: false,
    motionExpectedEmpty: true,
    motionNotice: 'Motion preference loaded.',
    shortcutSnapshot: baseShortcutChoicesWire,
    shortcutInventory: baseShortcutInventoryWire,
    shortcutDraft: baseShortcutChoicesWire,
    shortcutPending: false,
    shortcutExpectedEmpty: true,
    shortcutNotice: loadedShortcutNotice,
    requests: [],
    focus: [],
  };

  const viewAction = (surface, publication, lease, id) => ({
    bridgeProtocol: 1,
    kind: 'view-action',
    payload: {
      viewProtocol: 1,
      kind: 'view-action',
      scope: wireScope,
      action: {
        surfaceProtocol: 2,
        kind: 'surface-action',
        surface,
        publication,
        lease,
        id,
        trigger: 'keyboard',
      },
    },
  });

  const nativeEvent = payload => ({ bridgeProtocol: 1, kind: 'native-event', payload });

  const basePrelude = [
    { bridgeProtocol: 1, kind: 'view-topology', payload: { viewProtocol: 1, kind: 'view-topology', revision: '1', views: [wireScope] } },
    nativeEvent({ protocolVersion: 3, kind: 'attached', binding: wireBinding }),
    nativeEvent({ protocolVersion: 3, kind: 'pointer-ownership', ownershipProtocol: 1, binding: wireBinding, requestId: '1', serial: '1', state: 'idle', owner: null }),
    viewAction('bar', '5', '0', 'bar:settings'),
    nativeEvent({ protocolVersion: 3, kind: 'shell-settings', binding: wireBinding, requestId: '5', snapshot: { schema: 2, revision: '1', values: nightValuesWire } }),
    nativeEvent({ protocolVersion: 3, kind: 'motion-preferences', binding: wireBinding, requestId: '3', snapshot: { schema: 1, revision: '1', override: null } }),
    nativeEvent({ protocolVersion: 3, kind: 'shortcut-preferences', binding: wireBinding, requestId: '6', snapshot: { schema: 1, revision: '1', choices: baseShortcutChoicesWire }, inventory: baseShortcutInventoryWire }),
  ];

  // =========================================================================
  // Branch 1: Pending Settings Save (requestId '7', Dawn theme)
  // =========================================================================
  const settingsWriteRequest = {
    protocolVersion: 3,
    kind: 'shell-settings-write',
    binding: wireBinding,
    requestId: '7',
    proposal: { schema: 2, revision: '1', values: dawnValuesWire },
  };
  const settingsPendingSpec = {
    ...loadedSpec,
    publication: '11',
    presentation: '11',
    settingsDraft: dawnValuesWire,
    settingsPending: true,
    settingsNotice: 'Saving settings…',
    requests: [settingsWriteRequest],
  };
  const settingsPendingCommit = settingsCommit(settingsPendingSpec);
  const batchSettingsWrite = {
    scope: oneScope,
    revision: counter('1'),
    publication: counter('11'),
    lease: counter('1'),
    binding,
    wire: JSON.stringify(settingsPendingCommit),
    observations: empty(),
    operations: empty(),
    catalogs: empty(),
  };
  const settingsPendingState = patch(loadedState, [
    { path: ['controller', 'a', 'controller', 'a', 'publication'], before: counter('9'), after: counter('11') },
    { path: ['controller', 'a', 'batches'], before: list([batchOpenSettings, batchAttach]), after: list([batchSettingsWrite, batchOpenSettings, batchAttach]) },
    { path: dpath('presentation'), before: just(counter('9')), after: just(counter('11')) },
    { path: dpath('request'), before: counter('6'), after: counter('7') },
    { path: dpath('settings', 'draft'), before: nightValuesModel, after: dawnValuesModel },
    { path: dpath('settings', 'pending'), before: none(), after: just({ request: counter('7'), values: dawnValuesModel }) },
    { path: dpath('settings', 'notice'), before: 'Settings loaded.', after: 'Saving settings…' },
  ]);
  const settingsPrelude = basePrelude.concat([
    viewAction('popup', '9', '1', 'settings:theme:dawn'),
    viewAction('popup', '10', '1', 'settings:save'),
  ]);

  const settingsUnknownNotice = 'Settings save not confirmed. Refresh to read the stored values; this write will not be repeated.';
  const settingsUnknownState = patch(settingsPendingState, [
    { path: ['controller', 'a', 'controller', 'a', 'publication'], before: counter('11'), after: counter('12') },
    { path: dpath('presentation'), before: just(counter('11')), after: just(counter('12')) },
    { path: dpath('settings', 'outcome'), before: none(), after: just({ request: counter('7'), result: { $: 'Unconfirmed' } }) },
    { path: dpath('settings', 'notice'), before: 'Saving settings…', after: settingsUnknownNotice },
  ]);
  const settingsUnknownCommit = settingsCommit({
    ...settingsPendingSpec,
    publication: '12',
    presentation: '12',
    settingsNotice: settingsUnknownNotice,
    requests: [],
  });

  const settingsRefusedNotice = 'Settings change refused. Refresh, then choose again.';
  const settingsRefusedCorrelation = '{"outcome":"settings-refused","binding":{"lifetime":"1","session":"1","frontend":"1"},"identity":"7"}';
  const settingsRefusedAnnouncement = {
    interrupt: false,
    sequence: '1',
    correlation: settingsRefusedCorrelation,
    text: settingsRefusedNotice,
  };
  const settingsRefusedState = patch(settingsUnknownState, [
    { path: ['controller', 'a', 'controller', 'a', 'publication'], before: counter('12'), after: counter('13') },
    { path: dpath('presentation'), before: just(counter('12')), after: just(counter('13')) },
    { path: dpath('settings', 'pending'), before: just({ request: counter('7'), values: dawnValuesModel }), after: none() },
    { path: dpath('settings', 'outcome'), before: just({ request: counter('7'), result: { $: 'Unconfirmed' } }), after: just({ request: counter('7'), result: { $: 'Refused' } }) },
    { path: dpath('settings', 'notice'), before: settingsUnknownNotice, after: settingsRefusedNotice },
    { path: ['controller', 'a', 'announcements', 'a'], before: zero(), after: counter('1') },
    { path: ['controller', 'a', 'announcements', 'b'], before: none(), after: just({
      interrupt: false,
      sequence: counter('1'),
      correlation: settingsRefusedCorrelation,
      text: settingsRefusedNotice,
    }) },
  ]);
  const settingsRefusedCommit = settingsCommit({
    ...settingsPendingSpec,
    publication: '13',
    presentation: '13',
    settingsPending: false,
    settingsNotice: settingsRefusedNotice,
    requests: [],
    announcement: settingsRefusedAnnouncement,
  });

  const settingsSavedState = patch(settingsPendingState, [
    { path: ['controller', 'a', 'controller', 'a', 'publication'], before: counter('11'), after: counter('12') },
    { path: dpath('presentation'), before: just(counter('11')), after: just(counter('12')) },
    { path: dpath('settings', 'snapshot'), before: just({ schema: 2, revision: counter('1'), values: nightValuesModel }), after: just({ schema: 2, revision: counter('2'), values: dawnValuesModel }) },
    { path: dpath('settings', 'pending'), before: just({ request: counter('7'), values: dawnValuesModel }), after: none() },
    { path: dpath('settings', 'outcome'), before: none(), after: just({ request: counter('7'), result: { $: 'Saved' } }) },
    { path: dpath('settings', 'notice'), before: 'Saving settings…', after: 'Settings saved.' },
  ]);
  const settingsSavedCommit = settingsCommit({
    ...settingsPendingSpec,
    publication: '12',
    presentation: '12',
    settingsSnapshot: dawnValuesWire,
    settingsPending: false,
    settingsNotice: 'Settings saved.',
    requests: [],
  });

  // =========================================================================
  // Branch 2: Pending MotionPreferences Save (requestId '7', Full override)
  // =========================================================================
  const motionWriteRequest = {
    protocolVersion: 3,
    kind: 'motion-preferences-write',
    binding: wireBinding,
    requestId: '7',
    proposal: { schema: 1, revision: '1', override: 'full' },
  };
  const motionPendingSpec = {
    ...loadedSpec,
    publication: '11',
    presentation: '11',
    motionDraft: 'Full',
    motionPending: true,
    motionNotice: 'Saving motion preference…',
    requests: [motionWriteRequest],
  };
  const motionPendingCommit = settingsCommit(motionPendingSpec);
  const batchMotionWrite = {
    scope: oneScope,
    revision: counter('1'),
    publication: counter('11'),
    lease: counter('1'),
    binding,
    wire: JSON.stringify(motionPendingCommit),
    observations: empty(),
    operations: empty(),
    catalogs: empty(),
  };
  const motionPendingState = patch(loadedState, [
    { path: ['controller', 'a', 'controller', 'a', 'publication'], before: counter('9'), after: counter('11') },
    { path: ['controller', 'a', 'batches'], before: list([batchOpenSettings, batchAttach]), after: list([batchMotionWrite, batchOpenSettings, batchAttach]) },
    { path: dpath('presentation'), before: just(counter('9')), after: just(counter('11')) },
    { path: dpath('request'), before: counter('6'), after: counter('7') },
    { path: dpath('motion', 'preferences', 'draft'), before: { $: 'System' }, after: { $: 'Full' } },
    { path: dpath('motion', 'preferences', 'pending'), before: none(), after: just({ request: counter('7'), revision: counter('1'), override: { $: 'Full' } }) },
    { path: dpath('motion', 'preferences', 'notice'), before: 'Motion preference loaded.', after: 'Saving motion preference…' },
  ]);
  const motionPrelude = basePrelude.concat([
    viewAction('popup', '9', '1', 'settings:motion:full'),
    viewAction('popup', '10', '1', 'settings:motion:save'),
  ]);

  const motionUnknownNotice = 'Motion preference save not confirmed. Refresh to read stored values; this write will not be repeated.';
  const motionUnknownState = patch(motionPendingState, [
    { path: ['controller', 'a', 'controller', 'a', 'publication'], before: counter('11'), after: counter('12') },
    { path: dpath('presentation'), before: just(counter('11')), after: just(counter('12')) },
    { path: dpath('motion', 'preferences', 'notice'), before: 'Saving motion preference…', after: motionUnknownNotice },
  ]);
  const motionUnknownCommit = settingsCommit({
    ...motionPendingSpec,
    publication: '12',
    presentation: '12',
    motionNotice: motionUnknownNotice,
    requests: [],
  });

  const motionRefusedNotice = 'Motion preference refused. Refresh, then choose again.';
  const motionRefusedState = patch(motionUnknownState, [
    { path: ['controller', 'a', 'controller', 'a', 'publication'], before: counter('12'), after: counter('13') },
    { path: dpath('presentation'), before: just(counter('12')), after: just(counter('13')) },
    { path: dpath('motion', 'preferences', 'pending'), before: just({ request: counter('7'), revision: counter('1'), override: { $: 'Full' } }), after: none() },
    { path: dpath('motion', 'preferences', 'notice'), before: motionUnknownNotice, after: motionRefusedNotice },
  ]);
  const motionRefusedCommit = settingsCommit({
    ...motionPendingSpec,
    publication: '13',
    presentation: '13',
    motionPending: false,
    motionNotice: motionRefusedNotice,
    requests: [],
  });

  // Saved MotionPreferences ('full', rev '2') also triggers Desktop.syncMotion ->
  // Motion.propose (requestId '8', profile 'full'), advancing presentation twice (11->13).
  const motionProfileSetRequest = {
    protocolVersion: 3,
    kind: 'motion-profile-set',
    binding: wireBinding,
    requestId: '8',
    profile: 'full',
  };
  const motionSavedCommit = settingsCommit({
    ...motionPendingSpec,
    publication: '12',
    presentation: '13',
    motionSnapshot: 'Full',
    motionPending: false,
    motionProfilePending: true,
    motionNotice: 'Motion preference saved.',
    requests: [motionProfileSetRequest],
  });
  const batchMotionProfileSet = {
    scope: oneScope,
    revision: counter('1'),
    publication: counter('12'),
    lease: counter('1'),
    binding,
    wire: JSON.stringify(motionSavedCommit),
    observations: empty(),
    operations: empty(),
    catalogs: empty(),
  };
  const motionSavedState = patch(motionPendingState, [
    { path: ['controller', 'a', 'controller', 'a', 'publication'], before: counter('11'), after: counter('12') },
    { path: ['controller', 'a', 'batches'], before: list([batchMotionWrite, batchOpenSettings, batchAttach]), after: list([batchMotionProfileSet, batchMotionWrite, batchOpenSettings, batchAttach]) },
    { path: dpath('presentation'), before: just(counter('11')), after: just(counter('13')) },
    { path: dpath('request'), before: counter('7'), after: counter('8') },
    { path: dpath('motion', 'preferences', 'snapshot'), before: just({ revision: counter('1'), override: { $: 'System' } }), after: just({ revision: counter('2'), override: { $: 'Full' } }) },
    { path: dpath('motion', 'preferences', 'pending'), before: just({ request: counter('7'), revision: counter('1'), override: { $: 'Full' } }), after: none() },
    { path: dpath('motion', 'preferences', 'notice'), before: 'Saving motion preference…', after: 'Motion preference saved.' },
    { path: dpath('motion', 'pending'), before: none(), after: just({ binding, request: counter('8'), profile: { $: 'Full' } }) },
  ]);

  // =========================================================================
  // Branch 3: Pending ShortcutPreferences Save (requestId '7', apps Alternate)
  // =========================================================================
  const shortcutWriteRequest = {
    protocolVersion: 3,
    kind: 'shortcut-preferences-write',
    binding: wireBinding,
    requestId: '7',
    proposal: {
      preferences: { schema: 1, revision: '1', choices: desiredShortcutChoicesWire },
      fingerprint,
    },
  };
  const shortcutPendingSpec = {
    ...loadedSpec,
    publication: '11',
    presentation: '11',
    shortcutDraft: desiredShortcutChoicesWire,
    shortcutPending: true,
    shortcutNotice: 'Saving and applying shortcut choices…',
    requests: [shortcutWriteRequest],
  };
  const shortcutPendingCommit = settingsCommit(shortcutPendingSpec);
  const batchShortcutWrite = {
    scope: oneScope,
    revision: counter('1'),
    publication: counter('11'),
    lease: counter('1'),
    binding,
    wire: JSON.stringify(shortcutPendingCommit),
    observations: empty(),
    operations: empty(),
    catalogs: empty(),
  };
  const shortcutPendingState = patch(loadedState, [
    { path: ['controller', 'a', 'controller', 'a', 'publication'], before: counter('9'), after: counter('11') },
    { path: ['controller', 'a', 'batches'], before: list([batchOpenSettings, batchAttach]), after: list([batchShortcutWrite, batchOpenSettings, batchAttach]) },
    { path: dpath('presentation'), before: just(counter('9')), after: just(counter('11')) },
    { path: dpath('request'), before: counter('6'), after: counter('7') },
    { path: dpath('shortcutPreferences', 'draft'), before: baseShortcutChoicesModel, after: desiredShortcutChoicesModel },
    { path: dpath('shortcutPreferences', 'pending'), before: none(), after: just({ request: counter('7'), choices: desiredShortcutChoicesModel }) },
    { path: dpath('shortcutPreferences', 'notice'), before: loadedShortcutNotice, after: 'Saving and applying shortcut choices…' },
  ]);
  const shortcutPrelude = basePrelude.concat([
    viewAction('popup', '9', '1', 'settings:shortcuts:applications:alternate'),
    viewAction('popup', '10', '1', 'settings:shortcuts:save'),
  ]);

  const shortcutUnknownNotice = 'Shortcut application not confirmed. Refresh reads stored choices and live bindings; this action will not be repeated.';
  const shortcutUnknownState = patch(shortcutPendingState, [
    { path: ['controller', 'a', 'controller', 'a', 'publication'], before: counter('11'), after: counter('12') },
    { path: dpath('presentation'), before: just(counter('11')), after: just(counter('12')) },
    { path: dpath('shortcutPreferences', 'notice'), before: 'Saving and applying shortcut choices…', after: shortcutUnknownNotice },
  ]);
  const shortcutUnknownCommit = settingsCommit({
    ...shortcutPendingSpec,
    publication: '12',
    presentation: '12',
    shortcutNotice: shortcutUnknownNotice,
    requests: [],
  });

  const shortcutRefusedNotice = 'Shortcut choices refused. Bindings or stored choices changed; refresh and choose again.';
  const shortcutRefusedState = patch(shortcutUnknownState, [
    { path: ['controller', 'a', 'controller', 'a', 'publication'], before: counter('12'), after: counter('13') },
    { path: dpath('presentation'), before: just(counter('12')), after: just(counter('13')) },
    { path: dpath('shortcutPreferences', 'pending'), before: just({ request: counter('7'), choices: desiredShortcutChoicesModel }), after: none() },
    { path: dpath('shortcutPreferences', 'notice'), before: shortcutUnknownNotice, after: shortcutRefusedNotice },
  ]);
  const shortcutRefusedCommit = settingsCommit({
    ...shortcutPendingSpec,
    publication: '13',
    presentation: '13',
    shortcutPending: false,
    shortcutNotice: shortcutRefusedNotice,
    requests: [],
  });

  const shortcutStoredNotice = 'Choices saved, but live bindings changed. Refresh and choose a free shortcut before applying.';
  const shortcutStoredState = patch(shortcutPendingState, [
    { path: ['controller', 'a', 'controller', 'a', 'publication'], before: counter('11'), after: counter('12') },
    { path: dpath('presentation'), before: just(counter('11')), after: just(counter('12')) },
    { path: dpath('shortcutPreferences', 'snapshot'), before: just({ schema: 1, revision: counter('1'), choices: baseShortcutChoicesModel }), after: just({ schema: 1, revision: counter('2'), choices: desiredShortcutChoicesModel }) },
    { path: dpath('shortcutPreferences', 'pending'), before: just({ request: counter('7'), choices: desiredShortcutChoicesModel }), after: none() },
    { path: dpath('shortcutPreferences', 'notice'), before: 'Saving and applying shortcut choices…', after: shortcutStoredNotice },
  ]);
  const shortcutStoredCommit = settingsCommit({
    ...shortcutPendingSpec,
    publication: '12',
    presentation: '12',
    shortcutSnapshot: desiredShortcutChoicesWire,
    shortcutPending: false,
    shortcutNotice: shortcutStoredNotice,
    requests: [],
  });

  const shortcutSavedNotice = 'Shortcut choices saved and active. Existing bindings were preserved.';
  const shortcutSavedState = patch(shortcutPendingState, [
    { path: ['controller', 'a', 'controller', 'a', 'publication'], before: counter('11'), after: counter('12') },
    { path: dpath('presentation'), before: just(counter('11')), after: just(counter('12')) },
    { path: dpath('shortcutPreferences', 'snapshot'), before: just({ schema: 1, revision: counter('1'), choices: baseShortcutChoicesModel }), after: just({ schema: 1, revision: counter('2'), choices: desiredShortcutChoicesModel }) },
    { path: dpath('shortcutPreferences', 'inventory'), before: just(inventoryModel(baseShortcutInventoryWire)), after: just(inventoryModel(appliedShortcutInventoryWire)) },
    { path: dpath('shortcutPreferences', 'pending'), before: just({ request: counter('7'), choices: desiredShortcutChoicesModel }), after: none() },
    { path: dpath('shortcutPreferences', 'notice'), before: 'Saving and applying shortcut choices…', after: shortcutSavedNotice },
  ]);
  const shortcutSavedCommit = settingsCommit({
    ...shortcutPendingSpec,
    publication: '12',
    presentation: '12',
    shortcutSnapshot: desiredShortcutChoicesWire,
    shortcutInventory: appliedShortcutInventoryWire,
    shortcutPending: false,
    shortcutNotice: shortcutSavedNotice,
    requests: [],
  });

  return {
    pendingSettings: {
      prelude: copy(settingsPrelude),
      setupTimers: 0,
      given: copy(settingsPendingState),
      givenEffects: copy(publish(settingsPendingCommit)),
      requestId: '7',
      unknown: { state: copy(settingsUnknownState), effects: copy(publish(settingsUnknownCommit)) },
      refused: { state: copy(settingsRefusedState), effects: copy(publish(settingsRefusedCommit)) },
      saved: { state: copy(settingsSavedState), effects: copy(publish(settingsSavedCommit)) },
    },
    pendingMotion: {
      prelude: copy(motionPrelude),
      setupTimers: 0,
      given: copy(motionPendingState),
      givenEffects: copy(publish(motionPendingCommit)),
      requestId: '7',
      unknown: { state: copy(motionUnknownState), effects: copy(publish(motionUnknownCommit)) },
      refused: { state: copy(motionRefusedState), effects: copy(publish(motionRefusedCommit)) },
      saved: { state: copy(motionSavedState), effects: copy(publish(motionSavedCommit)) },
    },
    pendingShortcut: {
      prelude: copy(shortcutPrelude),
      setupTimers: 0,
      given: copy(shortcutPendingState),
      givenEffects: copy(publish(shortcutPendingCommit)),
      requestId: '7',
      baseInventoryWire: copy(baseShortcutInventoryWire),
      appliedInventoryWire: copy(appliedShortcutInventoryWire),
      desiredChoicesWire: copy(desiredShortcutChoicesWire),
      unknown: { state: copy(shortcutUnknownState), effects: copy(publish(shortcutUnknownCommit)) },
      refused: { state: copy(shortcutRefusedState), effects: copy(publish(shortcutRefusedCommit)) },
      stored: { state: copy(shortcutStoredState), effects: copy(publish(shortcutStoredCommit)) },
      saved: { state: copy(shortcutSavedState), effects: copy(publish(shortcutSavedCommit)) },
    },
    dawnValuesWire: copy(dawnValuesWire),
    viewAction,
  };
}

function buildPreferenceReceiptCases(c) {
  const seeds = buildPreferenceSeeds(c);
  if (c && c.preferenceSeedsOnly === true) {
    return {
      pendingSettings: seeds.pendingSettings,
      pendingMotion: seeds.pendingMotion,
      pendingShortcut: seeds.pendingShortcut,
    };
  }
  const { cloneLiteral: copy, initial, bindingJson, NIL } = c;
  const reset = { input: { kind: 'reset' }, expected: { state: copy(initial), effects: copy(NIL) } };
  const wireBinding = {
    lifetime: String(bindingJson.lifetime),
    session: String(bindingJson.session),
    frontend: String(bindingJson.frontend),
  };

  const settingsOutcome = (requestId, status, snapshot) => ({
    kind: 'incoming',
    value: {
      bridgeProtocol: 1,
      kind: 'native-event',
      payload: {
        protocolVersion: 3,
        kind: 'shell-settings-outcome',
        binding: wireBinding,
        requestId,
        status,
        snapshot,
      },
    },
  });

  const motionOutcome = (requestId, status, snapshot) => ({
    kind: 'incoming',
    value: {
      bridgeProtocol: 1,
      kind: 'native-event',
      payload: {
        protocolVersion: 3,
        kind: 'motion-preferences-outcome',
        binding: wireBinding,
        requestId,
        status,
        snapshot,
      },
    },
  });

  const shortcutOutcome = (requestId, status, snapshot, inventory) => ({
    kind: 'incoming',
    value: {
      bridgeProtocol: 1,
      kind: 'native-event',
      payload: {
        protocolVersion: 3,
        kind: 'shortcut-preferences-outcome',
        binding: wireBinding,
        requestId,
        status,
        snapshot,
        inventory,
      },
    },
  });

  const { pendingSettings: s, pendingMotion: m, pendingShortcut: k, dawnValuesWire, viewAction } = seeds;
  const preludeStep = domain => ({
    input: { kind: 'prelude', values: copy(domain.prelude) },
    setupTimers: domain.setupTimers,
    expected: { state: copy(domain.given), effects: copy(domain.givenEffects) },
  });

  return [
    {
      name: 'settings-pending-malformed-status-noop-then-unknown-and-refused',
      steps: [
        copy(reset),
        preludeStep(s),
        // 'Stored' is valid only for shortcuts; pre-d6fa51ec this mutated settings.outcome/notice.
        { input: settingsOutcome('7', 'Stored', null), expected: { state: copy(s.given), effects: copy(NIL) } },
        { input: settingsOutcome('7', 'bogus', null), expected: { state: copy(s.given), effects: copy(NIL) } },
        { input: settingsOutcome('99', 'Refused', null), expected: { state: copy(s.given), effects: copy(NIL) } },
        { input: settingsOutcome('7', 'Unknown', null), expected: copy(s.unknown) },
        // Duplicate Unknown and attempted re-save while Unknown pending is retained are complete no-ops.
        { input: settingsOutcome('7', 'Unknown', null), expected: { state: copy(s.unknown.state), effects: copy(NIL) } },
        { input: { kind: 'incoming', value: viewAction('popup', '12', '1', 'settings:save') }, expected: { state: copy(s.unknown.state), effects: copy(NIL) } },
        // Correlated Refused clears pending and emits OutcomeAnnouncements settings-refused.
        { input: settingsOutcome('7', 'Refused', null), expected: copy(s.refused) },
      ],
    },
    {
      name: 'settings-pending-malformed-status-noop-then-saved',
      steps: [
        copy(reset),
        preludeStep(s),
        { input: settingsOutcome('7', '', { schema: 2, revision: '2', values: copy(dawnValuesWire) }), expected: { state: copy(s.given), effects: copy(NIL) } },
        { input: settingsOutcome('7', 'Saved', { schema: 2, revision: '2', values: copy(dawnValuesWire) }), expected: copy(s.saved) },
      ],
    },
    {
      name: 'motion-pending-malformed-status-noop-then-unknown-and-refused',
      steps: [
        copy(reset),
        preludeStep(m),
        // 'Stored' is invalid for MotionPreferences; pre-d6fa51ec this mutated motion.preferences.notice.
        { input: motionOutcome('7', 'Stored', null), expected: { state: copy(m.given), effects: copy(NIL) } },
        { input: motionOutcome('7', 'bogus', null), expected: { state: copy(m.given), effects: copy(NIL) } },
        { input: motionOutcome('7', 'Unknown', null), expected: copy(m.unknown) },
        { input: { kind: 'incoming', value: viewAction('popup', '12', '1', 'settings:motion:save') }, expected: { state: copy(m.unknown.state), effects: copy(NIL) } },
        { input: motionOutcome('7', 'Refused', null), expected: copy(m.refused) },
      ],
    },
    {
      name: 'motion-pending-malformed-status-noop-then-saved-syncs-profile',
      steps: [
        copy(reset),
        preludeStep(m),
        { input: motionOutcome('7', 'Pending', { schema: 1, revision: '2', override: 'full' }), expected: { state: copy(m.given), effects: copy(NIL) } },
        { input: motionOutcome('7', 'Saved', { schema: 1, revision: '2', override: 'full' }), expected: copy(m.saved) },
      ],
    },
    {
      name: 'shortcut-pending-malformed-status-noop-then-unknown-and-refused',
      steps: [
        copy(reset),
        preludeStep(k),
        // 'Applied' is an internal adapter status, invalid on shortcut-preferences-outcome wire.
        { input: shortcutOutcome('7', 'Applied', null, copy(k.baseInventoryWire)), expected: { state: copy(k.given), effects: copy(NIL) } },
        { input: shortcutOutcome('7', 'Unknown', null, copy(k.baseInventoryWire)), expected: copy(k.unknown) },
        { input: { kind: 'incoming', value: viewAction('popup', '12', '1', 'settings:shortcuts:save') }, expected: { state: copy(k.unknown.state), effects: copy(NIL) } },
        { input: shortcutOutcome('7', 'Refused', null, copy(k.baseInventoryWire)), expected: copy(k.refused) },
      ],
    },
    {
      name: 'shortcut-pending-malformed-status-noop-then-stored',
      steps: [
        copy(reset),
        preludeStep(k),
        { input: shortcutOutcome('7', 'saved', { schema: 1, revision: '2', choices: copy(k.desiredChoicesWire) }, copy(k.baseInventoryWire)), expected: { state: copy(k.given), effects: copy(NIL) } },
        { input: shortcutOutcome('7', 'Stored', { schema: 1, revision: '2', choices: copy(k.desiredChoicesWire) }, copy(k.baseInventoryWire)), expected: copy(k.stored) },
      ],
    },
    {
      name: 'shortcut-pending-malformed-status-noop-then-saved',
      steps: [
        copy(reset),
        preludeStep(k),
        { input: shortcutOutcome('7', 'UNKNOWN', { schema: 1, revision: '2', choices: copy(k.desiredChoicesWire) }, copy(k.appliedInventoryWire)), expected: { state: copy(k.given), effects: copy(NIL) } },
        { input: shortcutOutcome('7', 'Saved', { schema: 1, revision: '2', choices: copy(k.desiredChoicesWire) }, copy(k.appliedInventoryWire)), expected: copy(k.saved) },
      ],
    },
  ];
}

buildPreferenceReceiptCases.buildPreferenceReceiptCases = buildPreferenceReceiptCases;
buildPreferenceReceiptCases.buildPreferenceSeeds = buildPreferenceSeeds;
buildPreferenceReceiptCases.seeds = buildPreferenceSeeds;


'use strict';

// Independent source-derived UX companion, NOT RUN. Root must inline this
// function into the existing literal-oracle sandbox after another author has
// supplied the named, independently transcribed reachable pending-settings
// GIVEN and prelude. None of these inputs may be captured reducer output.
// The existing runner must compare every field of each expected Model and
// each ordered Effect; the extra assertions here are not that comparison.
function buildPreferenceFeedbackCases(c) {
  const { cloneLiteral: copy, initial, NIL, bindingJson, pendingSettings } = c;
  const must = (condition, why) => { if (!condition) throw new Error('preference UX fixture: ' + why); };
  must(typeof copy === 'function' && initial && NIL && bindingJson && pendingSettings,
    'independent full pendingSettings GIVEN and prelude required');
  const f = pendingSettings;
  must(Array.isArray(f.prelude) && f.prelude.length > 0 && f.given && f.givenEffects,
    'independent nonempty prelude and full given/effects required');
  must(typeof f.requestId === 'string' && /^[1-9][0-9]*$/.test(f.requestId),
    'fixed canonical positive request identity required');
  must(f.unknown && f.unknown.state && f.unknown.effects,
    'independently authored full Unknown state and effects required');
  const desktop = f.given.controller.a.controller.a.desktop;
  const setting = desktop.settings;
  must(desktop.settingsOpen === true && desktop.settingsExpected.$ === 'Nothing', 'open loaded settings required');
  must(setting.pending.$ === 'Just' && setting.pending.a.request.a === f.requestId,
    'exact pending write request required');
  must(setting.outcome.$ === 'Nothing' && setting.notice === 'Saving settings…',
    'literal pending feedback required');
  const packetOf = effects => {
    must(effects.$ === '::' && effects.a.$ === 'Publish' && effects.b.$ === '[]',
      'exact sole full Publish effect required');
    return effects.a.a.a;
  };
  const pendingPacket = packetOf(f.givenEffects);
  const pendingFrame = pendingPacket.projection.frame;
  must(pendingFrame.mode === 'settings' && pendingFrame.status ===
    'Saving settings… · ' + desktop.shortcutPreferences.notice, 'literal current pending status required');
  const one = (rows, id) => {
    const matches = rows.filter(row => row.id === id);
    must(matches.length === 1, 'unique control ' + id + ' required');
    return matches[0];
  };
  const save = one(pendingFrame.popup, 'settings:save');
  const refresh = one(pendingFrame.popup, 'settings:refresh');
  must(save.label === 'Save settings' && save.ariaLabel === 'Save settings' && !save.enabled,
    'pending save disabled and named');
  must(refresh.label === 'Refresh settings' && refresh.ariaLabel === 'Refresh settings' && refresh.enabled,
    'read-only recovery remains reachable');
  must(Array.isArray(pendingPacket.focus), 'complete focus list required');
  const unknownDesktop = f.unknown.state.controller.a.controller.a.desktop;
  const unknownSettings = unknownDesktop.settings;
  must(unknownSettings.pending.$ === 'Just' && unknownSettings.pending.a.request.a === f.requestId,
    'Unknown retains exact pending write');
  must(unknownSettings.outcome.$ === 'Just' && unknownSettings.outcome.a.result.$ === 'Unconfirmed',
    'Unknown outcome remains explicitly unconfirmed');
  must(unknownSettings.notice === 'Settings save not confirmed. Refresh to read the stored values; this write will not be repeated.',
    'literal Unknown guidance');
  const unknownPacket = packetOf(f.unknown.effects);
  must(unknownPacket.projection.frame.status === unknownSettings.notice + ' · ' + unknownDesktop.shortcutPreferences.notice,
    'Unknown visible status matches retained guidance');
  must(one(unknownPacket.projection.frame.popup, 'settings:save').enabled === false,
    'Unknown does not re-enable repeat write');
  must(Array.isArray(unknownPacket.requests) && unknownPacket.requests.length === 0 &&
    Array.isArray(unknownPacket.focus) && unknownPacket.focus.length === 0,
    'Unknown emits no write and does not move focus');
  const input = status => ({ kind: 'incoming', value: { bridgeProtocol: 1, kind: 'native-event', payload: {
    protocolVersion: 3, kind: 'shell-settings-outcome', binding: copy(bindingJson),
    requestId: f.requestId, status, snapshot: null,
  } } });
  const reset = { input: { kind: 'reset' }, expected: { state: copy(initial), effects: copy(NIL) } };
  const setup = { input: { kind: 'prelude', values: copy(f.prelude) }, setupTimers: f.setupTimers,
    expected: { state: copy(f.given), effects: copy(f.givenEffects) } };
  must(Number.isInteger(f.setupTimers) && f.setupTimers >= 0, 'setup timer count required');
  const cases = [
    ['unsupported-name', 'Bogus'], ['wrong-case', 'saved'], ['empty-status', ''],
    ['wrong-domain-stored', 'Stored'], ['null-status', null], ['numeric-status', 1],
  ].map(([suffix, status]) => ({ name: 'ux-pending-settings-malformed-' + suffix,
    steps: [copy(reset), copy(setup), { input: input(status),
      expected: { state: copy(f.given), effects: copy(NIL) } }] }));
  const missing = input('Unknown');
  delete missing.value.payload.status;
  const extra = input('Unknown');
  extra.value.payload.unexpected = true;
  for (const [suffix, malformed] of [['missing-status', missing], ['extra-field', extra]]) {
    cases.push({ name: 'ux-pending-settings-malformed-' + suffix, steps: [copy(reset), copy(setup),
      { input: malformed, expected: { state: copy(f.given), effects: copy(NIL) } }] });
  }
  cases.push({ name: 'ux-pending-settings-valid-unknown-is-distinct', steps: [copy(reset), copy(setup),
    { input: input('Unknown'), expected: { state: copy(f.unknown.state), effects: copy(f.unknown.effects) } }] });
  return cases;
}


// Independent source-literal factories below never inspect reducer output.
let additionalCases = [];
const additionalResult = buildAdditionalCases({ baseCases, materialize, cloneLiteral,
  literalPatches, attachedPacket, attachedBatch, oneScope, oneScopeJson, binding,
  bindingJson, host, disconnectedText, disconnectedCorrelation, matchingCatalog,
  empty, none, zero, NIL, pinCases, topologyChanges, oneViewChanges, initial,
  buildPreferenceReceiptCases });
const preferenceContext = { cloneLiteral, literalPatches, initial, topologyChanges,
  oneViewChanges, oneScope, oneScopeJson, binding, bindingJson, host, empty, none, zero, NIL };
const preferenceFeedback = buildPreferenceFeedbackCases({ ...preferenceContext,
  pendingSettings: buildPreferenceSeeds(preferenceContext).pendingSettings });
additionalCases = additionalResult.cases.concat(preferenceFeedback);
const cases = Object.freeze(baseCases.concat(pinCases, additionalCases));
module.exports = { schema: 1, coverage, cases, materialize };
