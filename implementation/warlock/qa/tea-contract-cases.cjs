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
  if (pinCases.includes(record)) return cloneLiteral(record);
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
    'pin-unknown-reservation-no-replay', 'pin-unknown-read-reconciliation']),
  missing: Object.freeze(['window-pending-mutation', 'window-committed-receipt', 'window-refused-mutation-receipt',
    'disconnect-unknown-no-replay', 'rebind', 'exact-reachable-delay']),
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
const cases = Object.freeze(baseCases.concat(pinCases));
module.exports = { schema: 1, coverage, cases, materialize };
