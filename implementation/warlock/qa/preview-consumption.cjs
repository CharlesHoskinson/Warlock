'use strict';
// Run only via root's reviewed protected runner: node preview-consumption.cjs compiled-worker.js
const assertions = require('node:assert/strict');
const crypto = require('node:crypto');
const fs = require('node:fs');
const path = require('node:path');
const seeds = [20261105,20261106,20261107];
const budgets = { cases: { min: 7, max: 7 }, steps: { min: 4280, max: 4500 }, assertions: { min: 5300, max: 10000 }, seeds: { min: 3, max: 3 }, responseMs: 20000, totalMs: 180000 };
const counts = { cases:0, steps:0, assertions:0, seeds:0 };
const assert = new Proxy(assertions, { get(target, key) {
  if (typeof target[key] !== 'function') return target[key];
  return (...args) => { counts.assertions++; return target[key](...args); };
}});
const history = [];
let lastResponse = null;
let active = null;
let finished = false;
let terminal = false;
let hashes = {};
function fail(error) {
  if (terminal && !finished) return;
  terminal = true;
  finished = false;
  if (active) { clearTimeout(active.timer); active.reject(error); active = null; }
  process.exitCode = 1;
  process.stderr.write(JSON.stringify({ status:'failed', counts, budgets, hashes, error:String(error && error.stack || error), lastResponse, history })+'\n');
  clearTimeout(totalTimer);
}
const totalTimer = setTimeout(() => { fail(new Error('overall fixture deadline exceeded')); }, budgets.totalMs);
process.on('uncaughtException', error => { fail(error); });
process.on('unhandledRejection', error => { fail(error); });
const sha = filename => crypto.createHash('sha256').update(fs.readFileSync(filename)).digest('hex');
hashes = { compiled:sha(process.argv[2]), oracle:sha(__filename), elmFixture:sha(path.join(__dirname,'PreviewConsumptionReplay.elm')) };
const { Elm } = require(path.resolve(process.argv[2]));
const app = Elm.PreviewConsumptionReplay.init();
app.ports.outgoing.subscribe(value => {
  lastResponse = value;
  if (!active || finished || !value || value.sequence !== active.sequence) {
    fail(new Error('unexpected, duplicate, or out-of-order port reply'));
    return;
  }
  const current = active;
  active = null;
  clearTimeout(current.timer);
  current.resolve(value);
});
function step(kind, value, index) {
  if (terminal || active) return Promise.reject(new Error('concurrent or failed request'));
  const sequence = ++counts.steps;
  const input = {kind,value,index,sequence};
  history.push(input);
  return new Promise((resolve, reject) => {
    const timer = setTimeout(() => { fail(new Error(`missing port reply sequence=${sequence} kind=${kind}`)); }, budgets.responseMs);
    active = { sequence, resolve, reject, timer };
    try { app.ports.incoming.send(input); } catch (error) { fail(error); }
  });
}
const binding = { lifetime:'1', session:'1', frontend:'1' };
const domain = epoch => ({ binding, receiverEpoch:String(epoch) });
const grant = epoch => ({...domain(epoch), capacity:1});
const intent = {identity:'binding:1:1:1',commands:[{kind:'reconcile',binding}]};
function wire(epoch, ordinal) {
  // Whitespace and Unicode escape are deliberate: a parsed/re-encoded wire differs.
  return `{ "previewProtocol":3, "kind":"preview-commands", "binding":${JSON.stringify(binding)}, "receiverEpoch":"${epoch}", "controlOrdinal":"${ordinal}", "entries":[{"identity":"binding:1:1:1","commands":[{"kind":"reconcile","binding":${JSON.stringify(binding)},"note":"雪"}]}] }`;
}
function originalWire(epoch, ordinal) {
  return `{ "previewProtocol":3, "kind":"preview-commands", "binding":${JSON.stringify(binding)}, "receiverEpoch":"${epoch}", "controlOrdinal":"${ordinal}", "entries":[{"identity":"binding:1:1:1","commands":[{"kind":"reconcile","binding":${JSON.stringify(binding)}}]}] }`;
}
function fact(epoch, ordinal, inner = originalWire(epoch,ordinal)) {
  return {previewProtocol:3,kind:'preview-control-ticket',...domain(epoch),controlOrdinal:String(ordinal),alreadyDelivered:false,wire:inner};
}
function consumed(epoch,ordinal,inner=originalWire(epoch,ordinal)) {
  return {previewProtocol:3,kind:'preview-control-consumed',...domain(epoch),controlOrdinal:String(ordinal),wire:inner};
}
async function main() {
  counts.cases++;
  let state = await step('presentClosed');
  assert.equal(state.mode,'closed');
  await step('grant',grant(1));
  state = await step('quarantine',domain(1));
  assert.equal(state.realm.ingress.pending,1);
  assert.equal(state.subscription,false);
  counts.cases++;
  for (const bad of [
    {...fact(1,1),binding:{...binding,frontend:'9'}},
    {...fact(1,1),receiverEpoch:'2'},
    {...fact(1,1),controlOrdinal:'2'},
    {...fact(1,1),wire:'{'},
    {...fact(1,1),wire:wire(1,1)},
    {...fact(1,1),extra:true},
    {...fact(1,1),controlOrdinal:'0'},
    {...fact(1,1),controlOrdinal:'18446744073709551616'},
    {...fact(1,1),controlOrdinal:'01'}
  ]) {
    state = await step('issued',bad);
    assert.equal(state.realm.ingress.pending,1);
    assert.equal(state.outbox.length,0);
    assert.deepEqual(state.accepted,[]);
  }
  counts.cases++;
  const unicodeWire = originalWire(1,1).replace('reconcile',String.raw`reconc\u0069le`);
  state = await step('issued',fact(1,1,unicodeWire));
  assert.equal(state.realm.ingress.pending,0);
  assert.equal(state.accepted.length,1);
  assert.equal(state.outbox[0].wire,unicodeWire);
  assert.equal(state.subscription,false);
  assert.equal(state.mode,'closed');
  state = await step('issued',fact(1,1,unicodeWire));
  assert.equal(state.accepted.length,0);
  assert.equal(state.outbox.length,1);
  counts.cases++;
  const firstReceipt = consumed(1,1,unicodeWire);
  assert.deepEqual(state.outbox,[firstReceipt]);
  state = await step('closed',domain(1)); assert.deepEqual(state.outbox,[firstReceipt]);
  state = await step('grant',grant(2)); assert.deepEqual(state.outbox,[firstReceipt]);
  state = await step('quarantine',domain(2)); assert.deepEqual(state.outbox,[firstReceipt]);
  state = await step('issued',fact(2,2));
  assert.equal(state.outbox.length,2);
  const secondReceipt = consumed(2,2);
  assert.deepEqual(state.outbox,[firstReceipt,secondReceipt]);
  state = await step('complete',null,1);
  assert.deepEqual(state.outbox,[firstReceipt]);
  state = await step('completeSaved',null,1);
  assert.equal(state.outbox.length,1); // stale completed ticket cannot remove another
  state = await step('complete',null,99);
  assert.equal(state.outbox.length,1);
  counts.cases++;
  const unicodeEntry = { identity:'雪🌨', commands:[{kind:'例',value:'☃'}] };
  const unicodePacket = {previewProtocol:3,kind:'preview-commands',...domain(9),controlOrdinal:'18446744073709551615',entries:[unicodeEntry]};
  const unicodeOriginal = '  '+JSON.stringify(unicodePacket)+'  ';
  const unicodeFact = fact(9,'18446744073709551615',unicodeOriginal);
  state = await step('ingress',{grant:grant(9),proposal:{previewProtocol:3,kind:'preview-proposals',...domain(9),entries:[unicodeEntry]},ticket:unicodeFact});
  assert.equal(state.ingress.wire,unicodeOriginal);
  assert.equal(state.ingress.controlOrdinal,'18446744073709551615');
  state = await step('completeSaved',null,2);
  assert.deepEqual(state.outbox,[firstReceipt]); // foreign opaque ticket from strict ingress
  const proposal1 = {previewProtocol:3,kind:'preview-proposals',...domain(1),entries:[intent]};
  state = await step('ingress',{grant:grant(1),proposal:proposal1,ticket:fact(1,1,originalWire(1,1))});
  assert.equal(state.ingress.controlOrdinal,firstReceipt.controlOrdinal);
  assert.notEqual(state.ingress.wire,firstReceipt.wire);
  state = await step('completeSaved',null,3);
  assert.deepEqual(state.outbox,[firstReceipt]); // same domain and ordinal, different original wire
  state = await step('completeSaved',null,1);
  assert.deepEqual(state.outbox,[firstReceipt]); // duplicate old completion
  // Fill the real bounded outbox using valid new epochs and reconciliation.
  counts.cases++;
  counts.seeds = seeds.length;
  let expected = [firstReceipt];
  let random = seeds[0];
  for (let epoch=3; epoch<=1066; epoch++) {
    state = await step('closed',domain(epoch-1)); assert.deepEqual(state.outbox,expected);
    state = await step('grant',grant(epoch)); assert.deepEqual(state.outbox,expected);
    state = await step('quarantine',domain(epoch)); assert.deepEqual(state.outbox,expected);
    random = (Math.imul(random ^ seeds[epoch % seeds.length], 1664525) + 1013904223) >>> 0;
    const ordinal = String(random || 1);
    if ((random & 15) === 0) {
      const rejected = await step('issued',{...fact(epoch,ordinal),receiverEpoch:String(epoch+1)});
      assert.equal(rejected.realm.ingress.pending,1,`seeded refusal epoch=${epoch} state=${random}`);
    }
    state = await step('issued',fact(epoch,ordinal));
    assert.deepEqual(state.accepted,[consumed(epoch,ordinal)]);
    expected = expected.concat([consumed(epoch,ordinal)]);
    assert.deepEqual(state.outbox,expected);
    assert.equal(state.outbox.length,epoch-1);
  }
  counts.cases++;
  state = await step('closed',domain(1066)); assert.deepEqual(state.outbox,expected);
  state = await step('grant',grant(1067)); assert.deepEqual(state.outbox,expected);
  state = await step('quarantine',domain(1067)); assert.deepEqual(state.outbox,expected);
  state = await step('issued',fact(1067,1067));
  assert.equal(state.outbox.length,1065);
  assert.equal(state.realm.ingress.pending,1);
  assert.deepEqual(state.accepted,[]);
  assert.equal(state.wholePopupUnchanged,true);
  assert.equal(state.effectCount,0);
  assert.deepEqual(state.effectTypes,[]);
  assert.deepEqual(state.outbox,expected);
  state = await step('complete',null,0);
  expected = expected.slice(1);
  assert.deepEqual(state.outbox,expected);
  state = await step('issued',fact(1067,1067));
  assert.equal(state.realm.ingress.pending,0);
  assert.equal(state.outbox.length,1065);
  assert.equal(state.accepted.length,1);
  assert.deepEqual(state.accepted,[consumed(1067,1067)]);
  expected = expected.concat([consumed(1067,1067)]);
  assert.deepEqual(state.outbox,expected);
  assert.equal(state.accepted[0].wire,originalWire(1067,1067));
  for (const name of ['cases','steps','assertions','seeds']) {
    if (counts[name] < budgets[name].min || counts[name] > budgets[name].max) throw new Error(`budget ${name} outside declared range: ${counts[name]}`);
  }
  // Leave a bounded quiet period to detect queued duplicate or unexpected replies.
  await new Promise(resolve => setTimeout(resolve,100));
  if (terminal) throw new Error('duplicate or unexpected reply');
  finished = true;
  terminal = true;
  totalTimer.unref();
  process.stdout.write(JSON.stringify({status:'passed',counts,budgets,seeds,hashes,lastSequence:counts.steps})+'\n');
}
main().catch(fail);
