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
  for (const fixture of fixtures.traces) {
    const result = await replay({kind:'trace', steps:fixture.steps});
    assert.equal(result.passed, true, fixture.id + ': ' + result.error);
    for (const expectation of fixture.expect) {
      subset(result.steps[expectation.at], expectation.value, fixture.id + '[' + expectation.at + ']');
      checks.push({id:fixture.id + ':' + expectation.at, passed:true});
    }
  }
  for (const fixture of fixtures.decoders) {
    const result = await replay({kind:fixture.kind, value:fixture.value});
    assert.equal(result.passed, fixture.accepted, fixture.id);
    if (fixture.encoded !== undefined) assert.deepEqual(result.value, fixture.encoded, fixture.id);
    checks.push({id:fixture.id, passed:true});
  }
  fs.writeFileSync(process.argv[4], JSON.stringify({passed:true, checks:checks.length,
    namedChecks:checks, traces:fixtures.traces.length, decoderCases:fixtures.decoders.length}, null, 2) + '\n');
  clearTimeout(deadline);
})().catch(error => { clearTimeout(deadline); console.error(error.stack); process.exitCode = 1; });
