'use strict';
// Independent source-derived literals for Sol's read-only actual-root observer.
// No model or expected value is obtained from the implementation at runtime.
const C = (tag, ...args) => Object.fromEntries([['$', tag], ...args.map((v, i) => [String.fromCharCode(97 + i), v])]);
const L = xs => xs.reduceRight((tail, x) => C('::', x, tail), C('[]'));
const N = () => C('Nothing');
const J = x => C('Just', x);
const counter = x => C('Counter', x);
const json = x => ({ $: 0, a: x });
const sub = () => ({ $: 2, m: C('[]') });
const desc = (module, effects) => ({ module, effects: L(effects) });
const httpDesc = effects => desc('UiHttp', effects);
const read = () => C('ReadEvents');
const empty = () => [];
const control = { id: 'bar:applications', domId: 'open-applications', label: 'Applications', ariaLabel: 'Applications', detail: '', enabled: true };
const frame = (publication, mode, status) => ({ surfaceProtocol: 2, publication, lease: '1', mode, status, bar: [control], popup: [] });
const closed = frame('1', 'closed', 'Ready');
const loading = frame('2', 'applications', 'Loading applications…');
const ready = frame('3', 'applications', 'Ready');
const wire = publication => ({ surfaceProtocol: 2, kind: 'surface-action', surface: 'bar', publication, lease: '1', id: 'bar:applications' });
const gateway = payload => ({ bridgeProtocol: 1, kind: 'presentation', payload });
const details = f => ({ publication: counter(f.publication), lease: counter(f.lease), keyboardParent: N(), mode: f.mode, status: f.status,
  appearance: { theme: C('Night'), textScale: 100, effectsOff: false, reducedTransparency: false }, motion: 'reduced',
  bar: L([{ identity: control.id, domId: control.domId, label: control.label, ariaLabel: control.ariaLabel, detail: '', enabled: true, focusOnly: false, checked: N() }]), popup: L([]) });
const bar = (f, epoch = '1') => ({ presentation: C('Model', { last: counter(f.publication), lease: counter('1'), snapshot: J(C('Snapshot', details(f))) }),
  announcements: C('Model', { last: counter('0'), active: false, message: N() }),
  statusScroll: C('Model', C('Active', C('Epoch', counter(epoch)), f.status)) });
const initialBar = () => ({ presentation: C('Model', { last: counter('0'), lease: counter('0'), snapshot: N() }),
  announcements: C('Model', { last: counter('0'), active: false, message: N() }), statusScroll: C('Model', C('Unseeded', counter('0'))) });
const http = ({ polling = true, active = null, pending = [], failed = null } = {}) => C('Model', { role: C('Renderer'), pending: L(pending.map(json)), active: active === null ? N() : J(json(active)), polling, failed: failed === null ? N() : J(C(failed)) });
const state = (b, h) => ({ bar: b, http: h });
const returned = (h, effects, event = N()) => ({ kind: 'transition', value: C('#3', h, L(effects), event) });
const expectation = (b, h, descriptions, returns) => ({ state: state(b, h), subscriptions: sub(), descriptions, transportReturns: returns });
const init = () => { const h = http(); return { input: { kind: 'init' }, expected: expectation(initialBar(), h, [httpDesc([read()])], [{ kind: 'startup', value: C('#2', h, L([read()])) }]) }; };
const present = (f, b, h, effects) => {
  const packet = gateway(f), httpEffects = [read()];
  return { input: { kind: 'polledOk', body: JSON.stringify(packet) }, expected: expectation(b, h,
    [httpDesc(httpEffects), desc('Bar', effects)], [returned(h, httpEffects, J(C('Incoming', json(packet))))]) };
};
const action = (w, b, before, after, accepted) => {
  const barEffects = accepted ? [C('Dispatch', json(w))] : [];
  const transportEffects = accepted && before.a.active.$ === 'Nothing' ? [C('SendRenderer', json(w))] : [];
  return { input: { kind: 'viewAction', value: w }, expected: expectation(b, after,
    [desc('Bar', barEffects), ...(accepted ? [httpDesc(transportEffects)] : [])],
    accepted ? [returned(after, transportEffects)] : []) };
};
const transport = (kind, body, b, h, effects, event = N()) => ({ input: body === undefined ? { kind } : { kind, body },
  expected: expectation(b, h, [httpDesc(effects)], [returned(h, effects, event)]) });
const reset = (epoch, id) => C('ResetStatusViewport', C('Epoch', counter(epoch)), id);

function build() {
  const b1 = bar(closed), b2 = bar(loading, '2'), b3 = bar(ready, '3');
  const h0 = http(), one = http({ active: wire('1') }),
    queued = http({ active: wire('1'), pending: [wire('2')] }), two = http({ active: wire('2') }),
    lost = http({ active: wire('2'), failed: 'DeliveryUnconfirmed' });
  return { cases: [{ name: 'HttpBar-visible-loading-delayed-synchronous-stale-and-queue', root: 'HttpBar', steps: [
    init(),
    present(closed, b1, h0, []),
    action(wire('1'), b1, h0, one, true),
    // Empty event response schedules the real 100ms Poll message. Input
    // callbacks below are sequential explicit reducer deliveries, not a timer.
    transport('polledOk', '', b1, http({ polling: false, active: wire('1') }), [C('WakeAfter', 100, C('Poll'))]),
    transport('poll', undefined, b1, one, [read()]),
    present(loading, b2, one, [reset('2', 'warlock-bar-status-scroll-2')]),
    action(wire('1'), b2, one, one, false),
    action(wire('2'), b2, one, queued, true),
    action(wire('1'), b2, queued, queued, false),
    transport('postedOk', '', b2, two, [C('SendRenderer', json(wire('2')))]),
    present(ready, b3, two, [reset('3', 'warlock-bar-status-scroll-3')]),
    present(closed, b3, two, []), // old presentation must not roll back the model
    transport('postedNetworkError', undefined, b3, lost, [C('CancelEvents'), C('CancelPost')], J(C('Lost', 'UI delivery is unconfirmed. The action will not be repeated.'))),
    transport('postedOk', '', b3, lost, empty()),
    action(wire('2'), b3, lost, lost, false),
    action(wire('3'), b3, lost, lost, true), // accepted view event, stopped transport emits no send
  ] }] };
}
module.exports = { build };
