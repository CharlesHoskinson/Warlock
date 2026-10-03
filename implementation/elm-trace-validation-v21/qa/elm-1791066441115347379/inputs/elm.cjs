const fs = require('fs');
const assert = require('assert');
const app = require(process.argv[2]).Elm.Replay.init({flags: null});
const deadline = setTimeout(() => { throw new Error('Trace decoder deadline'); }, 15000);
function replay(message) {
  return new Promise(resolve => {
    const receive = value => { app.ports.outgoing.unsubscribe(receive); resolve(value); };
    app.ports.outgoing.subscribe(receive);
    app.ports.incoming.send(message);
  });
}
(async () => {
  const native = JSON.parse(fs.readFileSync(process.argv[3]));
  const packets = [...Object.entries(native.captures).map(([name, capture]) => [name, capture.renderTrace]),
    ...native.identityTracePackets.map((packet, index) => ['identity-' + index, packet])];
  assert.equal(packets.length, 18, 'Original native packet inventory');
  const cases = [];
  function diagnostic(summary) {
    assert.equal(summary.canonicalScene, false);
    assert.equal(summary.currentSceneAdmitted, false);
    assert.equal(summary.currentSceneEvidence, false);
    assert.equal(summary.presentationEvidence, false);
    assert.equal(summary.bindingCorrelationVerified, false);
  }
  async function check(name, packet, accepted, unusable = false) {
    const result = await replay(packet);
    assert.equal(result.passed, accepted, name + ': ' + (result.error || 'unexpected acceptance'));
    if (accepted) {
      diagnostic(result.summary);
      if (unusable) assert.equal(result.summary.frames[0].usableDispatchTrace, false, name);
    }
    cases.push({name, passed: true, expectedDecode: accepted, unusableDispatchExpected: unusable});
  }
  for (const [name, packet] of packets) await check('native-' + name, packet, true);
  const seed = packets[0][1];
  assert(seed.frames[0].draws.length > 0);
  const clone = () => JSON.parse(JSON.stringify(seed));
  async function mutate(name, change, accepted = false, unusable = false) {
    const packet = clone(); change(packet, packet.frames[0], packet.frames[0].draws[0]);
    await check(name, packet, accepted, unusable);
  }
  for (const key of ['protocolVersion', 'traceProtocol']) {
    await mutate(key + '-wrong', packet => { packet[key] = 2; });
    await mutate(key + '-string', packet => { packet[key] = '3'; });
  }
  await mutate('wrong-kind', packet => { packet.kind = 'scene'; });
  await mutate('extra-envelope-field', packet => { packet.order = []; });
  await mutate('missing-envelope-field', packet => { delete packet.retained; });
  await mutate('extra-frame-field', (_, frame) => { frame.presentation = true; });
  await mutate('missing-frame-field', (_, frame) => { delete frame.complete; });
  await mutate('extra-draw-field', (_, __, draw) => { draw.current = true; });
  await mutate('missing-draw-field', (_, __, draw) => { delete draw.surface; });
  for (const key of ['complete', 'overflow', 'committed']) await mutate(key + '-nonboolean', (_, frame) => { frame[key] = 1; });
  for (const key of ['retired', 'unbound', 'main', 'popup']) await mutate(key + '-nonboolean', (_, __, draw) => { draw[key] = 1; });
  await mutate('retained-nonboolean', packet => { packet.retained = 1; });
  for (const key of ['requestId', 'outputGeneration']) {
    for (const value of ['0', '01', '18446744073709551616', 1]) await mutate(key + '-invalid-' + value, packet => { packet[key] = value; });
  }
  for (const key of ['lifetime', 'session', 'frontend']) await mutate('binding-' + key + '-zero', packet => { packet.binding[key] = '0'; });
  await mutate('binding-extra-field', packet => { packet.binding.extra = '1'; });
  await mutate('duplicate-monitor', packet => { packet.frames.push(packet.frames[0]); });
  await mutate('too-many-monitors', packet => { packet.frames = Array.from({length: 33}, (_, index) => ({...packet.frames[0], monitor: String(index)})); });
  await mutate('too-many-draws', (_, frame, draw) => { frame.draws = Array(1025).fill(draw); });
  await mutate('too-many-input-rectangles', (_, __, draw) => { draw.input = Array(65).fill([0, 0, 1, 1]); });
  await mutate('input-boundary-64', (_, __, draw) => { draw.input = Array(64).fill([0, 0, 1, 1]); }, true);
  await mutate('draw-boundary-1024', (_, frame, draw) => { frame.draws = Array(1024).fill(draw); }, true);
  await mutate('empty-input-is-valid', (_, __, draw) => { draw.input = []; }, true);
  for (const [name, value] of [['negative', -0.1], ['above-one', 1.1], ['nan', NaN], ['positive-infinity', Infinity], ['negative-infinity', -Infinity], ['string', '1'], ['null', null]]) {
    await mutate('alpha-' + name, (_, __, draw) => { draw.alpha = value; });
  }
  for (const value of [0, 1]) await mutate('alpha-boundary-' + value, (_, __, draw) => { draw.alpha = value; }, true);
  for (const key of ['box', 'input']) {
    const set = (draw, rectangle) => { draw[key] = key === 'input' ? [rectangle] : rectangle; };
    for (const [name, rectangle] of [['short', [0, 0, 1]], ['long', [0, 0, 1, 1, 1]], ['zero-width', [0, 0, 0, 1]], ['negative-height', [0, 0, 1, -1]], ['nan-x', [NaN, 0, 1, 1]], ['infinite-width', [0, 0, Infinity, 1]], ['string-y', [0, '0', 1, 1]]]) {
      await mutate(key + '-' + name, (_, __, draw) => set(draw, rectangle));
    }
  }
  for (const [name, configuration] of [['short', [0, 0, 800, 600]], ['long', [0, 0, 800, 600, 1, 1]], ['zero-width', [0, 0, 0, 600, 1]], ['negative-height', [0, 0, 800, -600, 1]], ['zero-scale', [0, 0, 800, 600, 0]], ['negative-scale', [0, 0, 800, 600, -1]], ['nan-position', [NaN, 0, 800, 600, 1]], ['infinite-scale', [0, 0, 800, 600, Infinity]]]) {
    await mutate('output-' + name, (_, frame) => { frame.outputConfiguration = configuration; });
  }
  for (const value of [-1, 8, 0.5, '0']) await mutate('transform-invalid-' + value, (_, frame) => { frame.outputTransform = value; });
  for (const value of [0, 7]) await mutate('transform-boundary-' + value, (_, frame) => { frame.outputTransform = value; }, true);
  for (const field of ['frame', 'configurationGeneration']) {
    for (const value of ['0', '01', '-1', '18446744073709551616', 9007199254740992]) {
      await mutate(field + '-invalid-' + value, (_, frame) => { frame[field] = value; });
    }
    await mutate(field + '-uint64-max', (_, frame) => { frame[field] = '18446744073709551615'; }, true);
  }
  await mutate('surface-zero', (_, __, draw) => { draw.surface = '0'; });
  await mutate('surface-uint64-overflow', (_, __, draw) => { draw.surface = '18446744073709551616'; });
  await mutate('null-authority-with-incarnation', (_, __, draw) => { draw.authority = null; });
  await mutate('null-incarnation-with-authority', (_, __, draw) => { draw.incarnation = null; });
  await mutate('retired-windowless', (_, __, draw) => { draw.incarnation = draw.authority = null; draw.retired = true; });
  await mutate('bound-and-unbound', (_, __, draw) => { draw.unbound = true; });
  await mutate('windowless-valid', (_, __, draw) => { draw.incarnation = draw.authority = null; draw.retired = draw.unbound = false; }, true);
  await mutate('unbound-window-valid-unusable', (_, __, draw) => { draw.incarnation = draw.authority = null; draw.retired = false; draw.unbound = true; }, true, true);
  await mutate('retained-valid-unusable', packet => { packet.retained = true; }, true, true);
  await mutate('incomplete-valid-unusable', (_, frame) => { frame.complete = false; }, true, true);
  await mutate('overflow-valid-unusable', (_, frame) => { frame.complete = false; frame.overflow = true; }, true, true);
  await mutate('overflow-and-complete-refused', (_, frame) => { frame.complete = frame.overflow = true; });
  await mutate('uncommitted-valid-unusable', (_, frame) => { frame.committed = false; }, true, true);
  await mutate('retired-valid-unusable', (_, __, draw) => { draw.retired = true; }, true, true);
  await mutate('foreign-lifetime-valid-unusable', (packet, _, draw) => { draw.authority = packet.binding.lifetime === '1' ? '2' : '1'; }, true, true);
  // A query response and internally consistent dispatch never establish correlation,
  // current policy admission or presentation. Even counter/configuration disagreement
  // remains only diagnostic data; the separate counter namespaces must not be equated.
  await mutate('configuration-generation-is-independent', (packet, frame) => { packet.outputGeneration = '1'; frame.configurationGeneration = '99'; }, true);
  fs.writeFileSync(process.argv[4], JSON.stringify({passed: true, scope: 'Typed diagnostic decoding only; no current scene admission, correlation or presentation acceptance', checks: cases.length, nativeCaptures: packets.length, cases}, null, 2) + '\n');
  clearTimeout(deadline);
})().catch(error => { clearTimeout(deadline); console.error(error); process.exitCode = 1; });
