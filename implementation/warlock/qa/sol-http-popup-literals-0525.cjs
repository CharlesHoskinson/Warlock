'use strict';
// INDEPENDENT SOURCE LITERALS. Root-only fixture consumer; no execution by
// author. All wrapper fields and every reached typed description are asserted.
// No production reducer or observed output is used to manufacture this oracle.
const fs = require('node:fs');
const path = require('node:path');
const crypto = require('node:crypto');
const PINNED_POLICY_ORACLE = '41e3ccabc5843153b604205dd937c56890f659e294929788a959951d39b7bcb7';
const C = (name, ...values) => Object.fromEntries([['$', name], ...values.map((v, i) => [String.fromCharCode(97 + i), v])]);
const nil = () => C('[]');
const L = values => values.reduceRight((tail, head) => C('::', head, tail), nil());
const N = () => C('Nothing');
const J = value => C('Just', value);
const Z = () => C('Counter', '0');
const D = () => C('RBEmpty_elm_builtin');
const json = value => ({ $: 0, a: value });
const S = () => ({ $: 2, m: nil() }); // actual nonoptimized Sub.none bag prediction
const description = (module, values) => ({ module, effects: L(values) });
const HTTP = values => description('UiHttp', values);
const read = () => C('ReadEvents');
const cancel = () => HTTP([C('CancelEvents'), C('CancelPost')]);
const idle = () => HTTP([]);
function popup() {
  const preview = C('Model', D(), N(), { observed: N(), settled: N(), channel: N(), processed: Z() },
    { grant: N(), closing: false, closed: false, processed: Z(), completed: D() });
  return { announcements: C('Model', { last: Z(), active: false, message: N() }),
    presentation: C('Model', { last: Z(), lease: Z(), snapshot: N() }),
    previews: C('Model', preview, N(), N(), nil()), paintGate: C('Model', Z(), D()),
    pendingQuery: N(), composition: C('Idle'), lastQuery: N() };
}
function bar() {
  return { presentation: C('Model', { last: Z(), lease: Z(), snapshot: N() }),
    announcements: C('Model', { last: Z(), active: false, message: N() }),
    statusScroll: C('Model', C('Unseeded', Z())) };
}
function http(role, polling = true, failure = null, active = null, pending = []) {
  return C('Model', { role: C(role), pending: L(pending.map(json)),
    active: active === null ? N() : J(json(active)), polling,
    failed: failure === null ? N() : J(C(failure)) });
}
function wrapper(root, domain, transport) {
  const field = { HttpPopup: 'popup', HttpBar: 'bar', HttpMain: 'policy' }[root];
  if (!field) throw new Error('unknown root');
  return { [field]: domain, http: transport };
}
function step(kind, state, descriptions, body) {
  const transport = descriptions.find(item => item.module === 'UiHttp');
  if (!transport) throw new Error('literal transport descriptions missing');
  const failure = state.http.a.failed;
  let event = N();
  if (['polledNetworkError', 'postedNetworkError'].includes(kind)) {
    const text = kind === 'polledNetworkError'
      ? 'UI event transport unavailable. Actions were not retried.'
      : 'UI delivery is unconfirmed. The action will not be repeated.';
    event = J(C('Lost', text));
  } else if (kind === 'polledOk' && body !== '' && failure.$ === 'Nothing') {
    event = J(C('Incoming', json(JSON.parse(body))));
  }
  const transportReturns = kind === 'init'
    ? [{ kind: 'startup', value: C('#2', state.http, transport.effects) }]
    : [{ kind: 'transition', value: C('#3', state.http, transport.effects, event) }];
  return { input: body === undefined ? { kind } : { kind, body },
    expected: { state, subscriptions: S(), descriptions, transportReturns } };
}
function rendererCases(root) {
  const domain = root === 'HttpPopup' ? popup() : bar();
  const domModule = root === 'HttpPopup' ? 'Popup' : 'Bar';
  const state = (polling = true, failure = null) => wrapper(root, domain, http('Renderer', polling, failure));
  const announcement = JSON.stringify({ bridgeProtocol: 1, kind: 'announcements', payload: null });
  return [
    { name: `${root}-poll-delay-allowed-event-failed-sticky`, root, steps: [
      step('init', state(), [HTTP([read()])]),
      step('poll', state(), [idle()]),
      step('polledOk', state(false), [HTTP([C('WakeAfter', 100, C('Poll'))])], ''),
      step('poll', state(), [HTTP([read()])]),
      step('polledOk', state(), [HTTP([read()]), description(domModule, [])], announcement),
      // failed/reject changes ONLY failed. Retain polling/pending/active.
      step('polledNetworkError', state(true, 'EventTransportUnavailable'), [cancel()]),
      step('poll', state(true, 'EventTransportUnavailable'), [idle()]),
      step('polledOk', state(true, 'EventTransportUnavailable'), [idle()], announcement),
      step('postedOk', state(true, 'EventTransportUnavailable'), [idle()], ''),
    ] },
    { name: `${root}-late-delivery-error-before-sleep-target`, root, steps: [
      step('init', state(), [HTTP([read()])]),
      step('polledOk', state(false), [HTTP([C('WakeAfter', 100, C('Poll'))])], ''),
      // An independent boundary-negative callback, not a claim that this
      // fixture issued a POST or that a real HTTP stack delivered it.
      step('postedNetworkError', state(false, 'DeliveryUnconfirmed'), [cancel()]),
      step('poll', state(false, 'DeliveryUnconfirmed'), [idle()]),
      step('polledOk', state(false, 'DeliveryUnconfirmed'), [idle()], announcement),
    ] },
  ];
}
function build(repository) {
  const oraclePath = path.join(repository, 'implementation/warlock/qa/tea-contract-cases.cjs');
  const actual = crypto.createHash('sha256').update(fs.readFileSync(oraclePath)).digest('hex');
  if (actual !== PINNED_POLICY_ORACLE) throw new Error('literal policy oracle source changed; explicit rebase required');
  const oracle = require(oraclePath);
  const source = oracle.cases.find(spec => spec.name === 'catalog-pending-disconnect-rejects-late-receipt');
  if (!source) throw new Error('pinned independent policy history missing');
  const literal = oracle.materialize(source);
  const [initial, topology, attached, lost, late] = literal.steps;
  if (initial.input.kind !== 'reset' || topology.input.kind !== 'incoming' ||
      attached.input.kind !== 'incoming' || lost.input.kind !== 'transportLost' || late.input.kind !== 'incoming') {
    throw new Error('pinned independent history shape changed');
  }
  function packet(effects) {
    if (effects.$ !== '::' || effects.b.$ !== '[]' || effects.a.$ !== 'Publish' || effects.a.a.$ !== 0) {
      throw new Error('expected one complete independent Publish payload');
    }
    return effects.a.a.a;
  }
  const p1 = packet(topology.expected.effects);
  const p2 = packet(attached.expected.effects);
  const incoming1 = JSON.stringify(topology.input.value);
  const incoming2 = JSON.stringify(attached.input.value);
  const lateBody = JSON.stringify(late.input.value);
  const policy = effects => ({ module: 'DesktopPolicy', effects });
  const main = (model, active = null, pending = [], failure = null, polling = true) =>
    wrapper('HttpMain', model, http('Controller', polling, failure, active, pending));
  const start = () => [
    step('init', main(initial.expected.state), [HTTP([read()])]),
    step('polledOk', main(topology.expected.state, p1), [HTTP([read()]),
      policy(topology.expected.effects), { module: 'HttpMain.effects', effects: topology.expected.effects },
      HTTP([C('SendController', json(p1))])], incoming1),
    step('polledOk', main(attached.expected.state, p1, [p2]), [HTTP([read()]),
      policy(attached.expected.effects), { module: 'HttpMain.effects', effects: attached.expected.effects }, idle()], incoming2),
  ];
  // Exact intermediate pure returns for normal incoming-policy publication:
  // GET callback precedes domain reduction and the subsequent enqueue.
  // Both are literal states; neither is captured from the worker.
  const plainStart = start;
  const completeStart = () => {
    const steps = plainStart();
    steps[1].expected.transportReturns = [
      { kind: 'transition', value: C('#3', http('Controller'), L([read()]), J(C('Incoming', json(topology.input.value)))) },
      { kind: 'transition', value: C('#3', http('Controller', true, null, p1), L([C('SendController', json(p1))]), N()) },
    ];
    steps[2].expected.transportReturns = [
      { kind: 'transition', value: C('#3', http('Controller', true, null, p1), L([read()]), J(C('Incoming', json(attached.input.value)))) },
      { kind: 'transition', value: C('#3', http('Controller', true, null, p1, [p2]), nil(), N()) },
    ];
    return steps;
  };
  const cases = rendererCases('HttpPopup').concat(rendererCases('HttpBar'), [
    { name: 'HttpMain-complete-publish-queue-http-completion-is-not-native-ack', root: 'HttpMain', steps: completeStart().concat([
      step('postedOk', main(attached.expected.state, p2), [HTTP([C('SendController', json(p2))])], ''),
      step('postedOk', main(attached.expected.state), [idle()], ''),
      step('postedOk', main(attached.expected.state), [idle()], ''),
    ]) },
    { name: 'HttpMain-unknown-delivery-retains-active-and-pending-no-replay', root: 'HttpMain', steps: completeStart().concat([
      step('postedNetworkError', main(lost.expected.state, p1, [p2], 'DeliveryUnconfirmed'),
        [cancel(), policy(lost.expected.effects)]),
      step('postedOk', main(lost.expected.state, p1, [p2], 'DeliveryUnconfirmed'), [idle()], ''),
      step('poll', main(lost.expected.state, p1, [p2], 'DeliveryUnconfirmed'), [idle()]),
      step('polledOk', main(lost.expected.state, p1, [p2], 'DeliveryUnconfirmed'), [idle()], lateBody),
    ]) },
    { name: 'HttpMain-polling-failure-retains-queued-data-and-policy-loss', root: 'HttpMain', steps: completeStart().concat([
      step('polledNetworkError', main(lost.expected.state, p1, [p2], 'EventTransportUnavailable'),
        [cancel(), policy(lost.expected.effects)]),
      step('postedOk', main(lost.expected.state, p1, [p2], 'EventTransportUnavailable'), [idle()], ''),
      step('polledOk', main(lost.expected.state, p1, [p2], 'EventTransportUnavailable'), [idle()], lateBody),
    ]) },
  ]);
  return { cases, policyOracle: { path: oraclePath, sha256: actual, case: source.name } };
}
module.exports = {
  schema: 1, build,
  coverage: { complete: false, roots: ['HttpMain', 'HttpBar', 'HttpPopup'],
    scope: 'COMPLETE wrapper models, exact Sub.none bag, every reached typed description; independent source literals',
    limits: ['pure compiled-root replay, not browser/network/native observation',
      'no new authority constructor or production model mutation',
      'focus, IME, physical display, native provider and release remain separately qualified',
      'runtime command interpretation must additionally match the source-bound optimized-root boundary fixtures',
      'initial/no-snapshot renderer histories do not cover retained-field focus replacement'] },
};
