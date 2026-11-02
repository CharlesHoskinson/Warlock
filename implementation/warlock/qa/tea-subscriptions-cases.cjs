'use strict';

/*
 * Independent ELM-TEA-004 (tea-subscriptions) literal oracle.
 * Every GIVEN, intermediate state delta, typed effect list, and typed
 * subscription plan is authored directly from the Elm source definitions
 * (including combined PreviewPaintGate protocol-3 realm custody), never
 * captured from runtime output. Each case binds to its single-root worker
 * ('bar' | 'popup' | 'admission' | 'renderer') so Elm 0.19 port names stay
 * strictly disjoint across compiled QA workers.
 */

const empty = () => ({ $: '[]' });
const list = items => {
  let out = empty();
  for (let i = items.length - 1; i >= 0; i--) {
    out = { $: '::', a: items[i], b: out };
  }
  return out;
};
const none = () => ({ $: 'Nothing' });
const just = value => ({ $: 'Just', a: value });
const counter = value => ({ $: 'Counter', a: String(value) });
const previewId = value => ({ $: 'Identity', a: counter(value) });
const dictEmpty = () => ({ $: 'RBEmpty_elm_builtin' });
const dictSingle = (key, value) => ({
  $: 'RBNode_elm_builtin',
  a: { $: 'Black' },
  b: key,
  c: value,
  d: dictEmpty(),
  e: dictEmpty(),
});
const wrapModel = value => ({ $: 'Model', a: value });
const jsonVal = value => ({ $: 0, a: value });
const tag = name => ({ $: name });

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

function literalPatches(given, patches) {
  const result = cloneLiteral(given);
  if (!Array.isArray(patches) || patches.length === 0) throw new Error('missing literal changes');
  const seen = new Set();
  for (const change of patches) {
    if (!object(change) || !Array.isArray(change.path) || change.path.length === 0 ||
        !Object.prototype.hasOwnProperty.call(change, 'before') ||
        !Object.prototype.hasOwnProperty.call(change, 'after')) {
      throw new Error('invalid literal change');
    }
    const id = change.path.join('\0');
    if (seen.has(id)) throw new Error('duplicate literal change: ' + change.path.join('.'));
    seen.add(id);
    let cursor = result;
    for (let i = 0; i < change.path.length - 1; i++) {
      const part = change.path[i];
      if (!object(cursor) || !Object.prototype.hasOwnProperty.call(cursor, part)) {
        throw new Error('missing literal path: ' + change.path.join('.'));
      }
      cursor = cursor[part];
    }
    const leaf = change.path[change.path.length - 1];
    if (!object(cursor) || !Object.prototype.hasOwnProperty.call(cursor, leaf)) {
      throw new Error('missing literal leaf: ' + change.path.join('.'));
    }
    const expectedBefore = cloneLiteral(change.before);
    const nextValue = cloneLiteral(change.after);
    if (!equalLiteral(cursor[leaf], expectedBefore)) {
      throw new Error('unexpected literal before at ' + change.path.join('.'));
    }
    if (equalLiteral(expectedBefore, nextValue)) {
      throw new Error('noop literal change at ' + change.path.join('.'));
    }
    cursor[leaf] = nextValue;
  }
  return result;
}

// Complete source-authored initial models and initial subscription plans per single root.
const initialPresentation = () => wrapModel({
  last: counter('0'),
  lease: counter('0'),
  snapshot: none(),
});

const initialAnnouncement = () => wrapModel({
  active: false,
  last: counter('0'),
  message: none(),
});

const initialLedger = () => ({
  channel: none(),
  observed: none(),
  processed: counter('0'),
  settled: none(),
});

const initialScoped = () => ({
  closed: false,
  closing: false,
  completed: dictEmpty(),
  grant: none(),
  processed: counter('0'),
});

const initialPreviewPresenter = () => ({
  $: 'Model',
  a: dictEmpty(),
  b: none(),
  c: initialLedger(),
  d: initialScoped(),
});

const initialRetainedPreview = () => ({
  $: 'Model',
  a: initialPreviewPresenter(),
  b: none(),
  c: none(),
  d: empty(),
});

const initialPaintGate = () => ({
  $: 'Model',
  a: counter('0'),
  b: dictEmpty(),
});

const defaultAppearance = () => ({
  effectsOff: false,
  reducedTransparency: false,
  textScale: 100,
  theme: tag('Night'),
});

const makeControl = (id, domId, label, ariaLabel = label, detail = '', enabled = true) => ({
  ariaLabel,
  checked: none(),
  detail,
  domId,
  enabled,
  focusOnly: false,
  identity: id,
  label,
});

const makeSnapshot = (publication, lease, mode, status, barRows, popupRows) => ({
  $: 'Snapshot',
  a: {
    appearance: defaultAppearance(),
    bar: list(barRows),
    keyboardParent: none(),
    lease: counter(lease),
    mode,
    motion: 'reduced',
    popup: list(popupRows),
    publication: counter(publication),
    status,
  },
});

const basePopupSubscriptions = () => list([
  tag('PresentationChannel'),
  tag('NativePreviewGrantsChannel'),
  tag('NativePreviewQuarantineChannel'),
  tag('NativePreviewClosedChannel'),
  tag('NativePreviewRetirementChannel'),
]);

const initialBarState = () => ({
  model: {
    announcements: initialAnnouncement(),
    presentation: initialPresentation(),
    statusScroll: wrapModel({ $: 'Unseeded', a: counter('0') }),
  },
  subscriptions: list([tag('PresentationChannel')]),
});

const initialPopupState = () => ({
  model: {
    announcements: initialAnnouncement(),
    composition: tag('Idle'),
    lastQuery: none(),
    paintGate: initialPaintGate(),
    pendingQuery: none(),
    presentation: initialPresentation(),
    previews: initialRetainedPreview(),
  },
  subscriptions: basePopupSubscriptions(),
});

const initialAdmissionState = () => ({
  model: initialPresentation(),
  subscriptions: list([tag('PresentationChannel')]),
});

const initialRendererState = () => ({
  model: tag('Inert'),
  subscriptions: empty(),
});

const wireControl = (id, domId, label, ariaLabel = label, detail = '', enabled = true) => ({
  id,
  domId,
  label,
  ariaLabel,
  detail,
  enabled,
});

const wireFrame = (publication, lease, mode, status, bar, popup) => ({
  surfaceProtocol: 2,
  publication: String(publication),
  lease: String(lease),
  mode,
  status,
  bar,
  popup,
});

const bindingWire = { lifetime: '1', session: '1', frontend: '1' };
const contextWire = {
  lifetime: '1',
  incarnation: '1',
  output: '1',
  privacy: '1',
  rendering: '1',
  scene: '1',
  content: '1',
};
const scopeWire = {
  binding: bindingWire,
  context: contextWire,
  observation: '1',
  clock: '1',
  now: '10',
  present: true,
  sourceLive: true,
  locked: false,
  gpuReady: true,
};
const triggerWire = {
  binding: bindingWire,
  context: contextWire,
  origin: '1',
  clock: '1',
  deadline: '5000',
};
const jobWire = {
  binding: bindingWire,
  context: contextWire,
  request: '1',
  origin: '1',
  clock: '1',
  deadline: '5000',
};
const jobJsonKey = JSON.stringify(jobWire);
const acquireCmdWire = { kind: 'acquire', job: jobWire };
const cancelCmdWire = { kind: 'cancel', job: jobWire };
const acknowledgeCmdWire = { kind: 'acknowledge', job: jobWire, sequence: '1' };

const scopedEnvelope = (entries, receiverEpoch = '1') => ({
  previewProtocol: 3,
  kind: 'preview-proposals',
  binding: bindingWire,
  receiverEpoch: String(receiverEpoch),
  entries,
});

const bindingLiteral = () => ({
  frontend: previewId('1'),
  lifetime: previewId('1'),
  session: previewId('1'),
});
const contextLiteral = () => ({
  content: previewId('1'),
  incarnation: previewId('1'),
  lifetime: previewId('1'),
  output: previewId('1'),
  privacy: previewId('1'),
  rendering: previewId('1'),
  scene: previewId('1'),
});
const scopeLiteral = () => ({
  binding: bindingLiteral(),
  clock: previewId('1'),
  context: contextLiteral(),
  gpuReady: true,
  locked: false,
  now: previewId('10'),
  observation: previewId('1'),
  present: true,
  sourceLive: true,
});
const jobLiteral = () => ({
  binding: bindingLiteral(),
  clock: previewId('1'),
  context: contextLiteral(),
  deadline: previewId('5000'),
  origin: previewId('1'),
  request: previewId('1'),
});

const popupEffects = items => ({ $: 'PopupEffects', a: list(items) });
const popupPreviewEffects = (commands, requests) => popupEffects([
  { $: 'PreviewCommand', a: jsonVal(commands) },
  { $: 'PaintRequest', a: jsonVal(requests) },
]);

function buildBarCase() {
  const s0 = initialBarState();
  const barRowWire = [wireControl('bar:applications', 'open-apps', 'Applications')];
  const barRowLit = [makeControl('bar:applications', 'open-apps', 'Applications')];
  const frame1Wire = wireFrame('1', '0', 'closed', 'Ready', barRowWire, []);
  const snap1 = makeSnapshot('1', '0', 'closed', 'Ready', barRowLit, []);
  const s2 = literalPatches(s0, [
    {
      path: ['model', 'presentation'],
      before: initialPresentation(),
      after: wrapModel({ last: counter('1'), lease: counter('0'), snapshot: just(snap1) }),
    },
    {
      path: ['model', 'statusScroll'],
      before: wrapModel({ $: 'Unseeded', a: counter('0') }),
      after: wrapModel({ $: 'Active', a: { $: 'Epoch', a: counter('1') }, b: 'Ready' }),
    },
    {
      path: ['subscriptions'],
      before: list([tag('PresentationChannel')]),
      after: list([tag('PresentationChannel'), tag('RequestActionChannel'), tag('AnnouncementsChannel')]),
    },
  ]);
  const barRoute = { scope: { id: '1', generation: '1' }, surface: 'bar' };
  const annWire = {
    announcementProtocol: 1,
    kind: 'announcement-projection',
    recipient: barRoute,
    announcer: barRoute,
    publication: '1',
    lease: '0',
    message: { sequence: '1', correlation: 'corr-1', text: 'Taskbar ready', interrupt: false },
    deliver: true,
  };
  const s3 = literalPatches(s2, [
    {
      path: ['model', 'announcements'],
      before: initialAnnouncement(),
      after: wrapModel({
        active: true,
        last: counter('1'),
        message: just({ correlation: 'corr-1', interrupt: false, sequence: counter('1'), text: 'Taskbar ready' }),
      }),
    },
  ]);
  const actionWire = {
    surfaceProtocol: 2,
    kind: 'surface-action',
    surface: 'bar',
    publication: '1',
    lease: '0',
    id: 'bar:applications',
  };
  const frame2Wire = wireFrame('2', '0', 'closed', 'Updated status', barRowWire, []);
  const snap2 = makeSnapshot('2', '0', 'closed', 'Updated status', barRowLit, []);
  const s5 = literalPatches(s3, [
    {
      path: ['model', 'presentation'],
      before: s3.model.presentation,
      after: wrapModel({ last: counter('2'), lease: counter('0'), snapshot: just(snap2) }),
    },
    {
      path: ['model', 'statusScroll'],
      before: s3.model.statusScroll,
      after: wrapModel({ $: 'Active', a: { $: 'Epoch', a: counter('2') }, b: 'Updated status' }),
    },
  ]);
  return {
    name: 'bar-consumer-subscriptions',
    worker: 'bar',
    steps: [
      { input: { kind: 'reset' }, expected: { state: s0, effects: tag('ResetEffects') } },
      { input: { kind: 'bar-present', value: { bogus: true } }, expected: { state: s0, effects: { $: 'BarEffects', a: empty() } } },
      { input: { kind: 'bar-present', value: frame1Wire }, expected: { state: s2, effects: { $: 'BarEffects', a: empty() } } },
      { input: { kind: 'bar-announce', value: annWire }, expected: { state: s3, effects: { $: 'BarEffects', a: empty() } } },
      {
        input: { kind: 'bar-action', value: actionWire },
        expected: { state: s3, effects: { $: 'BarEffects', a: list([{ $: 'Dispatch', a: jsonVal(actionWire) }]) } },
      },
      {
        input: { kind: 'bar-present', value: frame2Wire },
        expected: {
          state: s5,
          effects: { $: 'BarEffects', a: list([{ $: 'ResetStatusViewport', a: { $: 'Epoch', a: counter('2') }, b: 'warlock-bar-status-scroll-2' }]) },
        },
      },
    ],
  };
}

function buildPopupPaintAndClosedReceiptCase() {
  const s0 = initialPopupState();
  const barRowWire = [wireControl('bar:applications', 'open-apps', 'Applications')];
  const barRowLit = [makeControl('bar:applications', 'open-apps', 'Applications')];

  // Step 1: closed presentation -> AnnouncementsChannel joins; RequestActionChannel & NativePreviewsChannel stay off
  const f1Wire = wireFrame('1', '0', 'closed', 'Ready', barRowWire, []);
  const s1 = literalPatches(s0, [
    {
      path: ['model', 'presentation'],
      before: initialPresentation(),
      after: wrapModel({ last: counter('1'), lease: counter('0'), snapshot: just(makeSnapshot('1', '0', 'closed', 'Ready', barRowLit, [])) }),
    },
    {
      path: ['subscriptions'],
      before: basePopupSubscriptions(),
      after: list([
        tag('PresentationChannel'),
        tag('AnnouncementsChannel'),
        tag('NativePreviewGrantsChannel'),
        tag('NativePreviewQuarantineChannel'),
        tag('NativePreviewClosedChannel'),
        tag('NativePreviewRetirementChannel'),
      ]),
    },
  ]);

  // Step 2: applications presentation -> RequestActionChannel joins; NativePreviewsChannel stays off (not picker, no retained previews)
  const appPopupWire = [
    wireControl('control:search', 'launcher-search', '', 'Search applications'),
    wireControl('control:close', 'close-apps', 'Close applications', 'Close applications and return to windows'),
  ];
  const appPopupLit = [
    makeControl('control:search', 'launcher-search', '', 'Search applications'),
    makeControl('control:close', 'close-apps', 'Close applications', 'Close applications and return to windows'),
  ];
  const f2Wire = wireFrame('2', '1', 'applications', 'Type to search applications.', barRowWire, appPopupWire);
  const s2 = literalPatches(s1, [
    {
      path: ['model', 'presentation'],
      before: s1.model.presentation,
      after: wrapModel({ last: counter('2'), lease: counter('1'), snapshot: just(makeSnapshot('2', '1', 'applications', 'Type to search applications.', barRowLit, appPopupLit)) }),
    },
    {
      path: ['subscriptions'],
      before: s1.subscriptions,
      after: list([
        tag('PresentationChannel'),
        tag('AnnouncementsChannel'),
        tag('RequestActionChannel'),
        tag('NativePreviewGrantsChannel'),
        tag('NativePreviewQuarantineChannel'),
        tag('NativePreviewClosedChannel'),
        tag('NativePreviewRetirementChannel'),
      ]),
    },
  ]);

  // Step 3: picker presentation -> NativePreviewsChannel joins (visible preview consumer)
  const pickerPopupWire = [
    wireControl('control:close', 'picker-close', 'Close'),
    wireControl('family:1', 'picker-family-1', 'Foot'),
  ];
  const pickerPopupLit = [
    makeControl('control:close', 'picker-close', 'Close'),
    makeControl('family:1', 'picker-family-1', 'Foot'),
  ];
  const f3Wire = wireFrame('3', '2', 'picker', 'Choose a window.', barRowWire, pickerPopupWire);
  const s3 = literalPatches(s2, [
    {
      path: ['model', 'presentation'],
      before: s2.model.presentation,
      after: wrapModel({ last: counter('3'), lease: counter('2'), snapshot: just(makeSnapshot('3', '2', 'picker', 'Choose a window.', barRowLit, pickerPopupLit)) }),
    },
    {
      path: ['subscriptions'],
      before: s2.subscriptions,
      after: list([
        tag('PresentationChannel'),
        tag('AnnouncementsChannel'),
        tag('RequestActionChannel'),
        tag('NativePreviewsChannel'),
        tag('NativePreviewGrantsChannel'),
        tag('NativePreviewQuarantineChannel'),
        tag('NativePreviewClosedChannel'),
        tag('NativePreviewRetirementChannel'),
      ]),
    },
  ]);

  // Step 4: legacy seed on family:1 -> demand=True, capture=Idle, PreviewPaintedChannel still off
  const seedWire = {
    kind: 'seed',
    publication: '3',
    lease: '2',
    identity: 'family:1',
    scope: scopeWire,
    title: 'Foot',
    application: 'foot',
  };
  const seededLifecycle = wrapModel({
    accepted: none(),
    cancelling: empty(),
    capture: tag('Idle'),
    connection: tag('Connected'),
    demand: true,
    known: empty(),
    lastTerminal: none(),
    metadataHidden: false,
    nextRequest: just(previewId('1')),
    retiring: empty(),
    scope: scopeLiteral(),
  });
  const seededEntry = {
    application: 'foot',
    binding: '1:1:1',
    detachReadySent: false,
    detachment: none(),
    feedbackFloor: none(),
    icon: none(),
    iconKind: 'unavailable',
    local: none(),
    metadataRevision: none(),
    minimized: none(),
    model: just(seededLifecycle),
    readySent: false,
    retirement: none(),
    source: none(),
    stamp: just({ lease: counter('2'), publication: counter('3') }),
    title: 'Foot',
  };
  const s4 = literalPatches(s3, [
    {
      path: ['model', 'previews', 'a', 'a'],
      before: dictEmpty(),
      after: dictSingle('family:1', seededEntry),
    },
  ]);

  // Step 5: request trigger -> Capturing job, PaintGate holds ticket "1" (realm = Nothing) -> PreviewPaintedChannel joins!
  const requestEventWire = {
    kind: 'event',
    identity: 'family:1',
    event: { kind: 'request', trigger: triggerWire },
  };
  const capturingLifecycle = wrapModel({
    accepted: none(),
    cancelling: empty(),
    capture: { $: 'Capturing', a: jobLiteral() },
    connection: tag('Connected'),
    demand: true,
    known: list([jobLiteral()]),
    lastTerminal: none(),
    metadataHidden: false,
    nextRequest: just(previewId('2')),
    retiring: empty(),
    scope: scopeLiteral(),
  });
  const pendingPaintGate = {
    $: 'Model',
    a: counter('1'),
    b: dictSingle('1', {
      command: jsonVal(acquireCmdWire),
      identity: 'family:1',
      job: jobJsonKey,
      realm: none(),
    }),
  };
  const s5 = literalPatches(s4, [
    {
      path: ['model', 'previews', 'a', 'a', 'c', 'model'],
      before: just(seededLifecycle),
      after: just(capturingLifecycle),
    },
    {
      path: ['model', 'paintGate'],
      before: initialPaintGate(),
      after: pendingPaintGate,
    },
    {
      path: ['subscriptions'],
      before: s4.subscriptions,
      after: list([
        tag('PresentationChannel'),
        tag('AnnouncementsChannel'),
        tag('RequestActionChannel'),
        tag('NativePreviewsChannel'),
        tag('PreviewPaintedChannel'),
        tag('NativePreviewGrantsChannel'),
        tag('NativePreviewQuarantineChannel'),
        tag('NativePreviewClosedChannel'),
        tag('NativePreviewRetirementChannel'),
      ]),
    },
  ]);

  // Step 6: PreviewPainted {"ticket":"1"} -> forwards acquire, drains pending -> PreviewPaintedChannel leaves!
  const drainedPaintGate = {
    $: 'Model',
    a: counter('1'),
    b: dictEmpty(),
  };
  const s6 = literalPatches(s5, [
    {
      path: ['model', 'paintGate'],
      before: pendingPaintGate,
      after: drainedPaintGate,
    },
    {
      path: ['subscriptions'],
      before: s5.subscriptions,
      after: s4.subscriptions,
    },
  ]);

  // Step 7: overlay closes (mode "closed", pub 4, retained lease 2) while Capturing job ->
  // RequestActionChannel leaves, AnnouncementsChannel stays, NativePreviewsChannel STAYS!
  const f4ClosedWire = wireFrame('4', '2', 'closed', 'Ready', barRowWire, []);
  const cancellingLifecycle = wrapModel({
    accepted: none(),
    cancelling: list([jobLiteral()]),
    capture: tag('Idle'),
    connection: tag('Connected'),
    demand: false,
    known: list([jobLiteral()]),
    lastTerminal: none(),
    metadataHidden: false,
    nextRequest: just(previewId('2')),
    retiring: empty(),
    scope: scopeLiteral(),
  });
  const s7 = literalPatches(s6, [
    {
      path: ['model', 'presentation'],
      before: s6.model.presentation,
      after: wrapModel({ last: counter('4'), lease: counter('2'), snapshot: just(makeSnapshot('4', '2', 'closed', 'Ready', barRowLit, [])) }),
    },
    {
      path: ['model', 'previews', 'a', 'a', 'c', 'model'],
      before: just(capturingLifecycle),
      after: just(cancellingLifecycle),
    },
    {
      path: ['model', 'previews', 'a', 'a', 'c', 'stamp'],
      before: just({ lease: counter('2'), publication: counter('3') }),
      after: none(),
    },
    {
      path: ['subscriptions'],
      before: s6.subscriptions,
      after: list([
        tag('PresentationChannel'),
        tag('AnnouncementsChannel'),
        tag('NativePreviewsChannel'),
        tag('NativePreviewGrantsChannel'),
        tag('NativePreviewQuarantineChannel'),
        tag('NativePreviewClosedChannel'),
        tag('NativePreviewRetirementChannel'),
      ]),
    },
  ]);

  // Step 8: ordered terminal cancelled receipt arrives while mode == "closed" -> emits acknowledge!
  const cancelledReceiptWire = {
    kind: 'event',
    identity: 'family:1',
    event: {
      kind: 'receipt',
      sequence: '1',
      event: { kind: 'cancelled', job: jobWire },
    },
  };
  const settledLifecycle = wrapModel({
    accepted: none(),
    cancelling: empty(),
    capture: tag('Idle'),
    connection: tag('Connected'),
    demand: false,
    known: empty(),
    lastTerminal: just({ $: '#2', a: jobLiteral(), b: previewId('1') }),
    metadataHidden: false,
    nextRequest: just(previewId('2')),
    retiring: empty(),
    scope: scopeLiteral(),
  });
  const s8 = literalPatches(s7, [
    {
      path: ['model', 'previews', 'a', 'a', 'c', 'model'],
      before: just(cancellingLifecycle),
      after: just(settledLifecycle),
    },
  ]);

  return {
    name: 'popup-overlay-and-paint-gate-subscriptions',
    worker: 'popup',
    steps: [
      { input: { kind: 'reset' }, expected: { state: s0, effects: tag('ResetEffects') } },
      { input: { kind: 'popup-present', value: f1Wire }, expected: { state: s1, effects: popupPreviewEffects([], []) } },
      { input: { kind: 'popup-present', value: f2Wire }, expected: { state: s2, effects: popupPreviewEffects([], []) } },
      { input: { kind: 'popup-present', value: f3Wire }, expected: { state: s3, effects: popupPreviewEffects([], []) } },
      { input: { kind: 'popup-native-preview', value: seedWire }, expected: { state: s4, effects: popupPreviewEffects([], []) } },
      {
        input: { kind: 'popup-native-preview', value: requestEventWire },
        expected: { state: s5, effects: popupPreviewEffects([], [{ ticket: '1' }]) },
      },
      {
        input: { kind: 'popup-preview-painted', value: { ticket: '1' } },
        expected: {
          state: s6,
          effects: popupEffects([{ $: 'PreviewCommand', a: jsonVal([{ identity: 'family:1', commands: [acquireCmdWire] }]) }]),
        },
      },
      {
        input: { kind: 'popup-present', value: f4ClosedWire },
        expected: {
          state: s7,
          effects: popupPreviewEffects([{ identity: 'family:1', commands: [cancelCmdWire] }], []),
        },
      },
      {
        input: { kind: 'popup-native-preview', value: cancelledReceiptWire },
        expected: {
          state: s8,
          effects: popupPreviewEffects([{ identity: 'family:1', commands: [acknowledgeCmdWire] }], []),
        },
      },
    ],
  };
}

function buildPopupRealmIngressAndClosedRevocationCase() {
  const s0 = initialPopupState();
  const domainWire = { binding: bindingWire, receiverEpoch: '1' };
  const grantWire = { binding: bindingWire, receiverEpoch: '1', capacity: 1 };
  const domainLit = () => ({
    frontend: counter('1'),
    lifetime: counter('1'),
    receiverEpoch: counter('1'),
    session: counter('1'),
  });
  const grantLit = () => ({ capacity: 1, domain: domainLit() });

  // Step 1: NativeGrant while Presentation.current == Nothing (pre-frame!)
  // Enrolls open realm -> NativePreviewsChannel joins; Issued & Retry stay off (empty ingress)
  const s1 = literalPatches(s0, [
    {
      path: ['model', 'previews'],
      before: initialRetainedPreview(),
      after: {
        $: 'Model',
        a: {
          $: 'Model',
          a: dictEmpty(),
          b: none(),
          c: { channel: just('1:1:1'), observed: none(), processed: counter('0'), settled: none() },
          d: { closed: false, closing: false, completed: dictEmpty(), grant: just(grantLit()), processed: counter('0') },
        },
        b: just(grantLit()),
        c: just({ $: 'Model', a: grantLit(), b: empty() }),
        d: empty(),
      },
    },
    {
      path: ['subscriptions'],
      before: basePopupSubscriptions(),
      after: list([
        tag('PresentationChannel'),
        tag('NativePreviewsChannel'),
        tag('NativePreviewGrantsChannel'),
        tag('NativePreviewQuarantineChannel'),
        tag('NativePreviewClosedChannel'),
        tag('NativePreviewRetirementChannel'),
      ]),
    },
  ]);

  // Step 2: picker presentation -> scoped empty preview-proposals envelope preserved!
  const barRowWire = [wireControl('bar:applications', 'open-apps', 'Applications')];
  const barRowLit = [makeControl('bar:applications', 'open-apps', 'Applications')];
  const pickerPopupWire = [wireControl('control:close', 'picker-close', 'Close'), wireControl('family:1', 'picker-f1', 'Foot')];
  const pickerPopupLit = [makeControl('control:close', 'picker-close', 'Close'), makeControl('family:1', 'picker-f1', 'Foot')];
  const f1PickerWire = wireFrame('1', '1', 'picker', 'Choose a window.', barRowWire, pickerPopupWire);
  const s2 = literalPatches(s1, [
    {
      path: ['model', 'presentation'],
      before: initialPresentation(),
      after: wrapModel({ last: counter('1'), lease: counter('1'), snapshot: just(makeSnapshot('1', '1', 'picker', 'Choose a window.', barRowLit, pickerPopupLit)) }),
    },
    {
      path: ['subscriptions'],
      before: s1.subscriptions,
      after: list([
        tag('PresentationChannel'),
        tag('AnnouncementsChannel'),
        tag('RequestActionChannel'),
        tag('NativePreviewsChannel'),
        tag('NativePreviewGrantsChannel'),
        tag('NativePreviewQuarantineChannel'),
        tag('NativePreviewClosedChannel'),
        tag('NativePreviewRetirementChannel'),
      ]),
    },
  ]);

  // Step 3: realm-wrapped seed for family:1
  const realmSeedWire = {
    previewProtocol: 3,
    kind: 'native-preview-realm-event',
    binding: bindingWire,
    receiverEpoch: '1',
    event: {
      kind: 'seed',
      publication: '1',
      lease: '1',
      identity: 'family:1',
      scope: scopeWire,
      title: 'Foot',
      application: 'foot',
    },
  };
  const seededLifecycle = wrapModel({
    accepted: none(),
    cancelling: empty(),
    capture: tag('Idle'),
    connection: tag('Connected'),
    demand: true,
    known: empty(),
    lastTerminal: none(),
    metadataHidden: false,
    nextRequest: just(previewId('1')),
    retiring: empty(),
    scope: scopeLiteral(),
  });
  const seededEntry = {
    application: 'foot',
    binding: '1:1:1',
    detachReadySent: false,
    detachment: none(),
    feedbackFloor: none(),
    icon: none(),
    iconKind: 'unavailable',
    local: none(),
    metadataRevision: none(),
    minimized: none(),
    model: just(seededLifecycle),
    readySent: false,
    retirement: none(),
    source: none(),
    stamp: just({ lease: counter('1'), publication: counter('1') }),
    title: 'Foot',
  };
  const s3 = literalPatches(s2, [
    {
      path: ['model', 'previews', 'a', 'a'],
      before: dictEmpty(),
      after: dictSingle('family:1', seededEntry),
    },
  ]);

  // Step 4: realm-wrapped request event -> Ingress.pending gets 1 acquire intent (capacity 1) AND
  // PreviewPaintGate holds ticket "1" with realm = Just domainLit ->
  // PreviewPaintedChannel, NativePreviewIssuedChannel & NativePreviewRetryChannel ALL ACTIVATE!
  const realmRequestWire = {
    previewProtocol: 3,
    kind: 'native-preview-realm-event',
    binding: bindingWire,
    receiverEpoch: '1',
    event: { kind: 'event', identity: 'family:1', event: { kind: 'request', trigger: triggerWire } },
  };
  const capturingLifecycle = wrapModel({
    accepted: none(),
    cancelling: empty(),
    capture: { $: 'Capturing', a: jobLiteral() },
    connection: tag('Connected'),
    demand: true,
    known: list([jobLiteral()]),
    lastTerminal: none(),
    metadataHidden: false,
    nextRequest: just(previewId('2')),
    retiring: empty(),
    scope: scopeLiteral(),
  });
  const acquireIntentLit = { command: jsonVal(acquireCmdWire), identity: 'family:1' };
  const cancelIntentLit = { command: jsonVal(cancelCmdWire), identity: 'family:1' };
  const scopedPendingPaintGate = {
    $: 'Model',
    a: counter('1'),
    b: dictSingle('1', {
      command: jsonVal(acquireCmdWire),
      identity: 'family:1',
      job: jobJsonKey,
      realm: just(domainLit()),
    }),
  };
  const s4 = literalPatches(s3, [
    {
      path: ['model', 'previews', 'a', 'a', 'c', 'model'],
      before: just(seededLifecycle),
      after: just(capturingLifecycle),
    },
    {
      path: ['model', 'previews', 'c', 'a', 'b'],
      before: empty(),
      after: list([acquireIntentLit]),
    },
    {
      path: ['model', 'paintGate'],
      before: initialPaintGate(),
      after: scopedPendingPaintGate,
    },
    {
      path: ['subscriptions'],
      before: s3.subscriptions,
      after: list([
        tag('PresentationChannel'),
        tag('AnnouncementsChannel'),
        tag('RequestActionChannel'),
        tag('NativePreviewsChannel'),
        tag('PreviewPaintedChannel'),
        tag('NativePreviewGrantsChannel'),
        tag('NativePreviewQuarantineChannel'),
        tag('NativePreviewClosedChannel'),
        tag('NativePreviewIssuedChannel'),
        tag('NativePreviewRetryChannel'),
        tag('NativePreviewRetirementChannel'),
      ]),
    },
  ]);

  // Step 5: overlay closes (pub 2, retained lease 1, mode "closed") BEFORE paint and while Ingress.pending is at capacity 1 ->
  // cancelIntent spills into deferred, PaintGate deduplicates held acquire ticket "1",
  // RequestActionChannel leaves, while PreviewPainted, NativePreviews, Issued & Retry ALL STAY ACTIVE!
  const f2ClosedWire = wireFrame('2', '1', 'closed', 'Ready', barRowWire, []);
  const cancellingLifecycle = wrapModel({
    accepted: none(),
    cancelling: list([jobLiteral()]),
    capture: tag('Idle'),
    connection: tag('Connected'),
    demand: false,
    known: list([jobLiteral()]),
    lastTerminal: none(),
    metadataHidden: false,
    nextRequest: just(previewId('2')),
    retiring: empty(),
    scope: scopeLiteral(),
  });
  const s5 = literalPatches(s4, [
    {
      path: ['model', 'presentation'],
      before: s4.model.presentation,
      after: wrapModel({ last: counter('2'), lease: counter('1'), snapshot: just(makeSnapshot('2', '1', 'closed', 'Ready', barRowLit, [])) }),
    },
    {
      path: ['model', 'previews', 'a', 'a', 'c', 'model'],
      before: just(capturingLifecycle),
      after: just(cancellingLifecycle),
    },
    {
      path: ['model', 'previews', 'a', 'a', 'c', 'stamp'],
      before: just({ lease: counter('1'), publication: counter('1') }),
      after: none(),
    },
    {
      path: ['model', 'previews', 'd'],
      before: empty(),
      after: list([cancelIntentLit]),
    },
    {
      path: ['subscriptions'],
      before: s4.subscriptions,
      after: list([
        tag('PresentationChannel'),
        tag('AnnouncementsChannel'),
        tag('NativePreviewsChannel'),
        tag('PreviewPaintedChannel'),
        tag('NativePreviewGrantsChannel'),
        tag('NativePreviewQuarantineChannel'),
        tag('NativePreviewClosedChannel'),
        tag('NativePreviewIssuedChannel'),
        tag('NativePreviewRetryChannel'),
        tag('NativePreviewRetirementChannel'),
      ]),
    },
  ]);

  // Step 6: PreviewPainted {"ticket":"1"} arrives while mode == "closed" ->
  // releases exact protocol-3 preview-proposals acquire envelope, drains PaintGate, PreviewPaintedChannel leaves!
  const drainedScopedPaintGate = {
    $: 'Model',
    a: counter('1'),
    b: dictEmpty(),
  };
  const s6 = literalPatches(s5, [
    {
      path: ['model', 'paintGate'],
      before: scopedPendingPaintGate,
      after: drainedScopedPaintGate,
    },
    {
      path: ['subscriptions'],
      before: s5.subscriptions,
      after: list([
        tag('PresentationChannel'),
        tag('AnnouncementsChannel'),
        tag('NativePreviewsChannel'),
        tag('NativePreviewGrantsChannel'),
        tag('NativePreviewQuarantineChannel'),
        tag('NativePreviewClosedChannel'),
        tag('NativePreviewIssuedChannel'),
        tag('NativePreviewRetryChannel'),
        tag('NativePreviewRetirementChannel'),
      ]),
    },
  ]);

  // Step 7: Foreign-domain control ticket negative while closed -> state & subscriptions unchanged!
  const ticket1Packet = JSON.stringify({
    previewProtocol: 3,
    kind: 'preview-commands',
    binding: bindingWire,
    receiverEpoch: '1',
    controlOrdinal: '1',
    entries: [{ identity: 'family:1', commands: [acquireCmdWire] }],
  });
  const foreignTicketWire = {
    previewProtocol: 3,
    kind: 'preview-control-ticket',
    binding: { lifetime: '9', session: '1', frontend: '1' },
    receiverEpoch: '1',
    controlOrdinal: '1',
    alreadyDelivered: false,
    wire: ticket1Packet,
  };

  // Step 8: NativeIssued for ordinal 1 (acquire) while closed -> pending=[], deferred=[cancelIntent] -> Issued & Retry stay active!
  const ticket1Wire = {
    previewProtocol: 3,
    kind: 'preview-control-ticket',
    binding: bindingWire,
    receiverEpoch: '1',
    controlOrdinal: '1',
    alreadyDelivered: false,
    wire: ticket1Packet,
  };
  const s8 = literalPatches(s6, [
    {
      path: ['model', 'previews', 'c', 'a', 'b'],
      before: list([acquireIntentLit]),
      after: empty(),
    },
  ]);

  // Step 9: NativeRetry while closed -> moves cancelIntent from deferred into pending and emits protocol-3 cancel proposal!
  const s9 = literalPatches(s8, [
    {
      path: ['model', 'previews', 'c', 'a', 'b'],
      before: empty(),
      after: list([cancelIntentLit]),
    },
    {
      path: ['model', 'previews', 'd'],
      before: list([cancelIntentLit]),
      after: empty(),
    },
  ]);

  // Step 10: NativeIssued for ordinal 2 (cancel) while closed -> pending=[], deferred=[] ->
  // NativePreviewIssuedChannel & NativePreviewRetryChannel BOTH DEACTIVATE!
  const ticket2Packet = JSON.stringify({
    previewProtocol: 3,
    kind: 'preview-commands',
    binding: bindingWire,
    receiverEpoch: '1',
    controlOrdinal: '2',
    entries: [{ identity: 'family:1', commands: [cancelCmdWire] }],
  });
  const ticket2Wire = {
    previewProtocol: 3,
    kind: 'preview-control-ticket',
    binding: bindingWire,
    receiverEpoch: '1',
    controlOrdinal: '2',
    alreadyDelivered: false,
    wire: ticket2Packet,
  };
  const s10 = literalPatches(s9, [
    {
      path: ['model', 'previews', 'c', 'a', 'b'],
      before: list([cancelIntentLit]),
      after: empty(),
    },
    {
      path: ['subscriptions'],
      before: s9.subscriptions,
      after: list([
        tag('PresentationChannel'),
        tag('AnnouncementsChannel'),
        tag('NativePreviewsChannel'),
        tag('NativePreviewGrantsChannel'),
        tag('NativePreviewQuarantineChannel'),
        tag('NativePreviewClosedChannel'),
        tag('NativePreviewRetirementChannel'),
      ]),
    },
  ]);

  // Step 11: NativeQuarantine while closed -> revokes realm (closing=True), queues reconcile intent,
  // emits protocol-3 reconcile proposal, and re-activates Issued & Retry!
  const reconcileCmdWire = { kind: 'reconcile', binding: bindingWire };
  const reconcileIntentLit = {
    command: jsonVal(reconcileCmdWire),
    identity: 'binding:1:1:1',
  };
  const s11 = literalPatches(s10, [
    {
      path: ['model', 'previews', 'a', 'd', 'closing'],
      before: false,
      after: true,
    },
    {
      path: ['model', 'previews', 'c', 'a', 'b'],
      before: empty(),
      after: list([reconcileIntentLit]),
    },
    {
      path: ['subscriptions'],
      before: s10.subscriptions,
      after: s9.subscriptions,
    },
  ]);

  return {
    name: 'popup-realm-ingress-and-closed-revocation',
    worker: 'popup',
    steps: [
      { input: { kind: 'reset' }, expected: { state: s0, effects: tag('ResetEffects') } },
      { input: { kind: 'popup-native-grant', value: grantWire }, expected: { state: s1, effects: popupEffects([]) } },
      { input: { kind: 'popup-present', value: f1PickerWire }, expected: { state: s2, effects: popupPreviewEffects(scopedEnvelope([]), []) } },
      { input: { kind: 'popup-native-preview', value: realmSeedWire }, expected: { state: s3, effects: popupPreviewEffects(scopedEnvelope([]), []) } },
      {
        input: { kind: 'popup-native-preview', value: realmRequestWire },
        expected: { state: s4, effects: popupPreviewEffects(scopedEnvelope([]), [{ ticket: '1' }]) },
      },
      { input: { kind: 'popup-present', value: f2ClosedWire }, expected: { state: s5, effects: popupPreviewEffects(scopedEnvelope([]), []) } },
      {
        input: { kind: 'popup-preview-painted', value: { ticket: '1' } },
        expected: {
          state: s6,
          effects: popupEffects([{ $: 'PreviewCommand', a: jsonVal(scopedEnvelope([{ identity: 'family:1', commands: [acquireCmdWire] }])) }]),
        },
      },
      { input: { kind: 'popup-native-issued', value: foreignTicketWire }, expected: { state: s6, effects: popupEffects([]) } },
      { input: { kind: 'popup-native-issued', value: ticket1Wire }, expected: { state: s8, effects: popupEffects([]) } },
      {
        input: { kind: 'popup-native-retry', value: domainWire },
        expected: { state: s9, effects: popupPreviewEffects(scopedEnvelope([{ identity: 'family:1', commands: [cancelCmdWire] }]), []) },
      },
      { input: { kind: 'popup-native-issued', value: ticket2Wire }, expected: { state: s10, effects: popupEffects([]) } },
      {
        input: { kind: 'popup-native-quarantine', value: domainWire },
        expected: { state: s11, effects: popupPreviewEffects(scopedEnvelope([{ identity: 'binding:1:1:1', commands: [reconcileCmdWire] }]), []) },
      },
    ],
  };
}

function buildPopupRealmCloseDrainsCase() {
  const s0 = initialPopupState();
  const grantWire = { binding: bindingWire, receiverEpoch: '1', capacity: 2 };
  const domainWire = { binding: bindingWire, receiverEpoch: '1' };
  const domainLit = () => ({
    frontend: counter('1'),
    lifetime: counter('1'),
    receiverEpoch: counter('1'),
    session: counter('1'),
  });
  const grantLit = () => ({ capacity: 2, domain: domainLit() });
  const s1 = literalPatches(s0, [
    {
      path: ['model', 'previews'],
      before: initialRetainedPreview(),
      after: {
        $: 'Model',
        a: {
          $: 'Model',
          a: dictEmpty(),
          b: none(),
          c: { channel: just('1:1:1'), observed: none(), processed: counter('0'), settled: none() },
          d: { closed: false, closing: false, completed: dictEmpty(), grant: just(grantLit()), processed: counter('0') },
        },
        b: just(grantLit()),
        c: just({ $: 'Model', a: grantLit(), b: empty() }),
        d: empty(),
      },
    },
    {
      path: ['subscriptions'],
      before: basePopupSubscriptions(),
      after: list([
        tag('PresentationChannel'),
        tag('NativePreviewsChannel'),
        tag('NativePreviewGrantsChannel'),
        tag('NativePreviewQuarantineChannel'),
        tag('NativePreviewClosedChannel'),
        tag('NativePreviewRetirementChannel'),
      ]),
    },
  ]);

  const s2 = literalPatches(s1, [
    {
      path: ['model', 'previews', 'a', 'd', 'closed'],
      before: false,
      after: true,
    },
    {
      path: ['model', 'previews', 'a', 'd', 'closing'],
      before: false,
      after: true,
    },
  ]);

  return {
    name: 'popup-realm-close-while-closed-preserves-retirement-ledger',
    worker: 'popup',
    steps: [
      { input: { kind: 'reset' }, expected: { state: s0, effects: tag('ResetEffects') } },
      { input: { kind: 'popup-native-grant', value: grantWire }, expected: { state: s1, effects: popupEffects([]) } },
      { input: { kind: 'popup-native-closed', value: domainWire }, expected: { state: s2, effects: popupEffects([]) } },
    ],
  };
}

function buildAdmissionCase() {
  const s0 = initialAdmissionState();
  const barRowWire = [wireControl('bar:applications', 'open-apps', 'Applications')];
  const barRowLit = [makeControl('bar:applications', 'open-apps', 'Applications')];
  const f1ClosedWire = wireFrame('1', '0', 'closed', 'Ready', barRowWire, []);
  const s1 = literalPatches(s0, [
    {
      path: ['model'],
      before: initialPresentation(),
      after: wrapModel({ last: counter('1'), lease: counter('0'), snapshot: just(makeSnapshot('1', '0', 'closed', 'Ready', barRowLit, [])) }),
    },
  ]);
  const appPopupWire = [wireControl('control:close', 'close-apps', 'Close applications')];
  const appPopupLit = [makeControl('control:close', 'close-apps', 'Close applications')];
  const f2OpenWire = wireFrame('2', '1', 'applications', 'Applications', barRowWire, appPopupWire);
  const s2 = literalPatches(s1, [
    {
      path: ['model'],
      before: s1.model,
      after: wrapModel({ last: counter('2'), lease: counter('1'), snapshot: just(makeSnapshot('2', '1', 'applications', 'Applications', barRowLit, appPopupLit)) }),
    },
    {
      path: ['subscriptions'],
      before: list([tag('PresentationChannel')]),
      after: list([tag('PresentationChannel'), tag('RequestActionChannel')]),
    },
  ]);
  const closeActionWire = {
    surfaceProtocol: 2,
    kind: 'surface-action',
    surface: 'popup',
    publication: '2',
    lease: '1',
    id: 'control:close',
  };
  const f3ClosedWire = wireFrame('3', '1', 'closed', 'Ready', barRowWire, []);
  const s3 = literalPatches(s2, [
    {
      path: ['model'],
      before: s2.model,
      after: wrapModel({ last: counter('3'), lease: counter('1'), snapshot: just(makeSnapshot('3', '1', 'closed', 'Ready', barRowLit, [])) }),
    },
    {
      path: ['subscriptions'],
      before: list([tag('PresentationChannel'), tag('RequestActionChannel')]),
      after: list([tag('PresentationChannel')]),
    },
  ]);

  return {
    name: 'admission-consumer-subscriptions',
    worker: 'admission',
    steps: [
      { input: { kind: 'reset' }, expected: { state: s0, effects: tag('ResetEffects') } },
      { input: { kind: 'admission-present', value: f1ClosedWire }, expected: { state: s1, effects: { $: 'AdmissionEffects', a: none() } } },
      { input: { kind: 'admission-action', value: closeActionWire }, expected: { state: s1, effects: { $: 'AdmissionEffects', a: none() } } },
      { input: { kind: 'admission-present', value: f2OpenWire }, expected: { state: s2, effects: { $: 'AdmissionEffects', a: none() } } },
      {
        input: { kind: 'admission-action', value: closeActionWire },
        expected: { state: s2, effects: { $: 'AdmissionEffects', a: just(jsonVal(closeActionWire)) } },
      },
      { input: { kind: 'admission-present', value: f3ClosedWire }, expected: { state: s3, effects: { $: 'AdmissionEffects', a: none() } } },
    ],
  };
}

function buildRendererCase() {
  const s0 = initialRendererState();
  const barRowWire = [wireControl('bar:applications', 'open-apps', 'Applications')];
  const barRowLit = [makeControl('bar:applications', 'open-apps', 'Applications')];
  const f1ClosedWire = wireFrame('1', '0', 'closed', 'Ready', barRowWire, []);
  const rendererGrantWire = {
    channelProtocol: 1,
    kind: 'native-preview-renderer-grant',
    binding: bindingWire,
    receiverEpoch: '1',
    rendererLease: '1',
    sequenceFloor: '0',
  };
  const rDomain = () => ({
    frontend: counter('1'),
    lifetime: counter('1'),
    receiverEpoch: counter('1'),
    session: counter('1'),
  });
  const rGrant = () => ({ domain: rDomain(), floor: counter('0'), lease: counter('1') });
  const s1 = literalPatches(s0, [
    {
      path: ['model'],
      before: tag('Inert'),
      after: { $: 'Receiver', a: rGrant(), b: counter('0'), c: none(), d: false },
    },
    {
      path: ['subscriptions'],
      before: empty(),
      after: list([tag('VisualSnapshotsChannel')]),
    },
  ]);

  const projectionPacketWire = {
    channelProtocol: 1,
    kind: 'native-preview-projection',
    binding: bindingWire,
    receiverEpoch: '1',
    rendererLease: '1',
    visualSequence: '1',
    visual: {
      visualProtocol: 1,
      kind: 'native-preview-visual',
      binding: bindingWire,
      receiverEpoch: '1',
      surface: f1ClosedWire,
      previews: [],
    },
  };
  const acceptedReceiptWire = {
    channelProtocol: 1,
    kind: 'native-preview-projection-accepted',
    binding: bindingWire,
    receiverEpoch: '1',
    rendererLease: '1',
    visualSequence: '1',
  };
  const projectionLit = {
    $: 'Projection',
    a: rDomain(),
    b: just(makeSnapshot('1', '0', 'closed', 'Ready', barRowLit, [])),
    c: empty(),
  };
  const s2 = literalPatches(s1, [
    {
      path: ['model'],
      before: s1.model,
      after: { $: 'Receiver', a: rGrant(), b: counter('1'), c: just(projectionLit), d: false },
    },
  ]);
  const s3 = literalPatches(s2, [
    {
      path: ['model'],
      before: s2.model,
      after: { $: 'Receiver', a: rGrant(), b: counter('1'), c: none(), d: true },
    },
    {
      path: ['subscriptions'],
      before: list([tag('VisualSnapshotsChannel')]),
      after: empty(),
    },
  ]);
  const projectionPacketSeq2Wire = {
    ...projectionPacketWire,
    visualSequence: '2',
  };

  return {
    name: 'renderer-grant-and-poison-subscriptions',
    worker: 'renderer',
    steps: [
      { input: { kind: 'reset' }, expected: { state: s0, effects: tag('ResetEffects') } },
      { input: { kind: 'renderer-snapshot', value: projectionPacketWire }, expected: { state: s0, effects: { $: 'ReceiverEffects', a: none() } } },
      { input: { kind: 'renderer-init', value: rendererGrantWire }, expected: { state: s1, effects: { $: 'ReceiverEffects', a: none() } } },
      {
        input: { kind: 'renderer-snapshot', value: projectionPacketWire },
        expected: { state: s2, effects: { $: 'ReceiverEffects', a: just(jsonVal(acceptedReceiptWire)) } },
      },
      {
        input: { kind: 'renderer-snapshot', value: { malformed: true } },
        expected: { state: s3, effects: { $: 'ReceiverEffects', a: none() } },
      },
      {
        input: { kind: 'renderer-snapshot', value: projectionPacketSeq2Wire },
        expected: { state: s3, effects: { $: 'ReceiverEffects', a: none() } },
      },
    ],
  };
}

const BUILT_CASES = [
  buildBarCase(),
  buildPopupPaintAndClosedReceiptCase(),
  buildPopupRealmIngressAndClosedRevocationCase(),
  buildPopupRealmCloseDrainsCase(),
  buildAdmissionCase(),
  buildRendererCase(),
];

module.exports = {
  coverage: {
    complete: false,
    requirement: 'ELM-TEA-004',
    scenario: 'tea-subscriptions',
    rootsInventoried: [
      'implementation/warlock/src/Main.elm',
      'implementation/warlock/src/HttpMain.elm',
      'implementation/warlock/src/Bar.elm',
      'implementation/warlock/src/HttpBar.elm',
      'implementation/warlock/src/Popup.elm',
      'implementation/warlock/src/HttpPopup.elm',
      'implementation/warlock/src/NativePreviewAdmission.elm',
      'implementation/warlock/src/NativePreviewRenderer.elm',
      'site/src/SiteMain.elm',
    ],
    fullModelDebugWorkerRoots: [
      'implementation/warlock/src/Bar.elm',
      'implementation/warlock/src/Popup.elm',
      'implementation/warlock/src/NativePreviewAdmission.elm',
      'implementation/warlock/src/NativePreviewRenderer.elm',
    ],
    compiledOptimizedElementRoots: [
      'implementation/warlock/src/Main.elm',
      'implementation/warlock/src/HttpMain.elm',
      'implementation/warlock/src/Bar.elm',
      'implementation/warlock/src/HttpBar.elm',
      'implementation/warlock/src/Popup.elm',
      'implementation/warlock/src/HttpPopup.elm',
      'implementation/warlock/src/NativePreviewAdmission.elm',
      'implementation/warlock/src/NativePreviewRenderer.elm',
    ],
    preservedStaticRoots: [
      'site/src/SiteMain.elm',
    ],
    companionSuites: [
      'implementation/warlock/qa/tea-contract.cjs',
      'implementation/warlock/qa/ui-http.cjs',
      'implementation/warlock/qa/sol-scoped-popup-0440.cjs',
    ],
    supported: [
      'Bar single-root full-model/effect/subscription-plan replay + compiled Browser.element port gating',
      'Popup single-root full-model/effect/subscription-plan replay (with protocol-3 PreviewPaintGate realm custody) + compiled Browser.element synchronous in-flight, delayed, and closed-overlay callback delivery across paint, issued, retry, quarantine, and terminal receipts',
      'NativePreviewAdmission single-root full-model/effect/subscription-plan replay + compiled Browser.element visible-consumer requestAction gating',
      'NativePreviewRenderer single-root full-model/effect/subscription-plan replay + compiled Browser.element grant admission and poison unsubscription',
      'Main compiled Browser.element static incoming topology (v1/v2) + native revocation delivery while closed (paired with TeaContractReplay full policy model/effects)',
      'HttpMain, HttpBar, HttpPopup compiled Browser.element recurring /events GET + 99ms/100ms Process.sleep poll timer + exact method/url/X-Warlock-Api/Content-Type/5000ms-timeout/body + focus command + mutual Http.cancel tracker abort ("warlock-ui-events" / "warlock-ui-post") + sticky no-retry stop',
      'SiteMain byte-exact Sub.none preservation',
    ],
    missing: [
      'HttpMain/HttpBar/HttpPopup keep Model/Msg/update unexposed (exposing (main)); composite wrapper state is verified via compiled Browser.element XHR/timer/abort/DOM/focus boundaries + companion UiHttpReplay/TeaContractReplay rather than direct composite AST serialization',
      'Live WebKit/GTK/Wayland native host callback ordering and native GUI acceptance remain separate',
    ],
  },
  cases: BUILT_CASES,
  materialize: spec => cloneLiteral(spec),
};
