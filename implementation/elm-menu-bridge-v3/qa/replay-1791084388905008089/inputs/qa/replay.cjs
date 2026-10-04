'use strict';
const fs = require('fs');
const assert = require('assert/strict');
const app = require(process.argv[2]).Elm.BridgeReplay.init({flags:null});
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
  const first = fixtures.traces[0];
  const setup = first.steps.slice(0,4);
  const validReceipt = first.steps[4].frame;
  const cycle = {}; cycle.self = cycle;
  const cyclic = JSON.parse(JSON.stringify(validReceipt)); cyclic.intent = cycle;
  let deep = {};
  for (let depth=0; depth<5000; depth++) deep={child:deep};
  const deeplyNested = JSON.parse(JSON.stringify(validReceipt)); deeplyNested.intent=deep;
  for (const [name,frame] of [['cyclic',cyclic],['deep',deeplyNested]]) {
    const result = await replay({steps:[...setup,{op:'frame',frame}]});
    check('production-' + name + '-malformed-receipt-rejected-before-serialization', () =>
      subset(result.steps[4], {outstanding:1,registry:1,commands:first.expect.find(e => e.at===3).value.commands,
        shell:{phase:'Ready',effects:{transaction:{status:'Pending'}}}}, name));
  }
  const passed = checks.every(check => check.passed);
  fs.writeFileSync(process.argv[4], JSON.stringify({passed, checks:checks.length,
    namedChecks:checks, traces:fixtures.traces.length, decoderCases:0}, null, 2) + '\n');
  clearTimeout(deadline);
  if (!passed) process.exitCode = 1;
})().catch(error => { clearTimeout(deadline); console.error(error.stack); process.exitCode = 1; });
