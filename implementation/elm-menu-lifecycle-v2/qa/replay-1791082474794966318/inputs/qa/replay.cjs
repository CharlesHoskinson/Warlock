'use strict';
const fs = require('fs');
const assert = require('assert/strict');
const app = require(process.argv[2]).Elm.Replay.init({flags:null});
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
  for (const fixture of fixtures.decoders) {
    const result = await replay({kind:fixture.kind, value:fixture.value});
    check(fixture.id, () => {
      assert.equal(result.passed, fixture.accepted, fixture.id);
      if (fixture.encoded !== undefined) assert.deepEqual(result.value, fixture.encoded, fixture.id);
    });
  }
  // Raw JS graphs cannot be serialized into JSON fixture files. Exercise the
  // actual decoded-value boundary without ever stringifying rejected graphs.
  const validProvider = fixtures.decoders.find(f => f.id === 'provider-valid').value;
  for (const variant of ['unknown-cycle', 'cyclic-title', 'deep-unknown-field']) {
    const value = JSON.parse(JSON.stringify(validProvider));
    if (variant === 'deep-unknown-field') {
      let graph = {};
      for (let depth = 0; depth < 10000; depth++) graph = {child:graph};
      value.unknown = graph;
    } else {
      const graph = {}; graph.self = graph;
      if (variant === 'cyclic-title') value.title = graph;
      else value.unknown = graph;
    }
    const result = await replay({kind:'provider', value});
    check('provider-adversarial-' + variant, () => assert.equal(result.passed, false));
  }
  const passed = checks.every(check => check.passed);
  fs.writeFileSync(process.argv[4], JSON.stringify({passed, checks:checks.length,
    namedChecks:checks, traces:fixtures.traces.length, decoderCases:fixtures.decoders.length}, null, 2) + '\n');
  clearTimeout(deadline);
  if (!passed) process.exitCode = 1;
})().catch(error => { clearTimeout(deadline); console.error(error.stack); process.exitCode = 1; });
