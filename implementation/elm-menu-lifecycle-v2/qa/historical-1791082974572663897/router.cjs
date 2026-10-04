'use strict';
const fs = require('fs');
const assert = require('assert/strict');
const app = require(process.argv[2]).Elm.RouterReplay.init({flags:null});
const fixtures = JSON.parse(fs.readFileSync(process.argv[3], 'utf8'));
const deadline = setTimeout(() => { throw new Error('Compiled Elm replay deadline'); }, 15000);
function replay(value) { return new Promise(resolve => {
  const receive = result => { app.ports.outgoing.unsubscribe(receive); resolve(result); };
  app.ports.outgoing.subscribe(receive); app.ports.incoming.send(value);
}); }
function subset(actual, expected, label) {
  if (expected !== null && typeof expected === 'object' && !Array.isArray(expected)) {
    assert(actual !== null && typeof actual === 'object', label);
    for (const [key, value] of Object.entries(expected)) subset(actual[key], value, label + '.' + key);
  } else assert.deepEqual(actual, expected, label);
}
(async () => {
  const checks = [];
  function check(id, body) {
    try { body(); checks.push({id, passed:true}); }
    catch (error) { checks.push({id, passed:false, error:String(error)}); console.error(id + ': ' + error.stack); }
  }
  for (const fixture of fixtures.traces) {
    const result = await replay({kind:'trace', steps:fixture.steps});
    if (!result.passed) { check(fixture.id, () => assert.equal(result.passed, true, result.error)); continue; }
    for (const expectation of fixture.expect) {
      check(fixture.id + ':' + expectation.at, () =>
        subset(result.steps[expectation.at], expectation.value, fixture.id + '[' + expectation.at + ']'));
    }
  }
  for (const fixture of (fixtures.decoders || [])) {
    const result = await replay({kind:fixture.kind, value:fixture.value});
    check(fixture.id, () => {
      assert.equal(result.passed, fixture.accepted, fixture.id);
      if (fixture.encoded !== undefined) assert.deepEqual(result.value, fixture.encoded, fixture.id);
    });
  }
  const first = fixtures.traces[0];
  const provider = first.steps[0].provider;
  const originalCommand = first.steps[1].command;
  const cyclic = {}; cyclic.self = cyclic;
  const command = JSON.parse(JSON.stringify(originalCommand));
  command.intent.context = cyclic;
  const rejected = await replay({steps:[{op:'open', provider}, {op:'activate', index:1, command}]});
  check('native-cyclic-command-refused-without-serialization-or-state-leak', () => {
    subset(rejected.steps[1], {registry:0,outstanding:0,commands:0,menu:{status:'refused'}}, 'cyclic-command');
    assert.equal(typeof rejected.steps[1].error, 'string');
  });
  const frame = {...originalCommand, kind:'effect-outcome', status:'Committed', reason:'',
    revision:'999', outputGeneration:'777', intent:'DEEP_PLACEHOLDER'};
  const raw = JSON.stringify(frame).replace('"DEEP_PLACEHOLDER"', '['.repeat(5000)+'0'+']'.repeat(5000));
  assert(Buffer.byteLength(raw, 'utf8') < 16384);
  const deep = await replay({steps:[{op:'open', provider}, {op:'activate', index:1, command:originalCommand},
    {op:'receipt', frame:raw}]});
  check('native-deep-receipt-under-byte-limit-refused-without-serializing-failure', () => {
    subset(deep.steps[2], {registry:1,outstanding:1,commands:1,menu:{status:'pending'},observed:null}, 'deep-receipt');
    assert.equal(typeof deep.steps[2].error, 'string');
  });
  const passed = checks.every(check => check.passed);
  fs.writeFileSync(process.argv[4], JSON.stringify({passed, checks:checks.length,
    namedChecks:checks, traces:fixtures.traces.length, decoderCases:(fixtures.decoders || []).length}, null, 2) + '\n');
  clearTimeout(deadline);
  if (!passed) process.exitCode = 1;
})().catch(error => { clearTimeout(deadline); console.error(error.stack); process.exitCode = 1; });
