'use strict';
const assert = require('node:assert/strict');
const fs = require('node:fs');
const path = require('node:path');
const crypto = require('node:crypto');
const {Elm} = require(path.resolve(process.argv[2]));
const fixture = JSON.parse(fs.readFileSync(process.argv[3], 'utf8'));
assert.equal(crypto.createHash('sha256').update(fs.readFileSync(fixture.sourceReport)).digest('hex'), fixture.sourceReportSHA256);
const native = JSON.parse(fs.readFileSync(fixture.sourceReport, 'utf8'));
assert(native.passed && native.cleanupPassed);
assert.deepEqual(fixture.clientScope, native.providerReport.clientScope);
assert.deepEqual(fixture.terminalReceipts, native.providerReport.terminalReceipts);
const source = fixture.clientScope;
const identity = 'family:' + source.scope.context.incarnation;
const frame = fixture.terminalReceipts[0].event.event.frame;
let checks = 0;
function check(ok, message) { assert(ok, message); checks++; }
function worker() {
  const app = Elm.PreviewPresenterReplay.init(); let pending = null;
  app.ports.outgoing.subscribe(value => { assert(pending); const done = pending; pending = null; done(value); });
  return (kind, value) => new Promise((resolve, reject) => {
    const timer = setTimeout(() => { pending = null; reject(new Error('Compiled Presenter port timeout')); }, 3000);
    assert.equal(pending, null); pending = value => { clearTimeout(timer); resolve(value); };
    app.ports.incoming.send({kind, value});
  });
}
const presentation = (publication='1', mode='picker') => ({surfaceProtocol:2, publication, lease:'1', mode, status:'', bar:[],
  popup: mode === 'picker' ? [{id:identity, domId:'actual-client', label:'Client', ariaLabel:'Client', detail:'', enabled:true}] : []});
const seed = (source_=source) => ({kind:'source-seed', publication:'1', lease:'1', identity, source:structuredClone(source_), title:'Native source', application:'warlock-child-probe'});
async function refuse(send, value, prior, message) {
  const result = await send('native', value); assert.deepEqual(result.models, prior.models, message); checks++;
  check(result.commands.length === 0, message + ': no effects'); return result;
}
(async () => {
  const send = worker(); await send('presentation', presentation());
  let result = await send('native', seed());
  check(result.models.length === 1 && result.models[0].model.demand, 'Actual Popup presenter consumes typed native client seed');
  assert.deepEqual(result.models[0].model.scope, source.scope); checks++;
  check(result.commands.length === 0 && result.models[0].model.known.length === 0, 'Source admission alone creates no capture or receipt');
  const trigger = {...frame.job}; delete trigger.request;
  result = await send('native', {kind:'event', identity, event:{kind:'request', trigger}});
  assert.deepEqual(result.commands, [{identity, commands:[{kind:'acquire', job:frame.job}]}]); checks++;
  check(result.models[0].model.known.length === 1, 'Original native job and deadline remain retained');
  const held = result;
  const monitor = structuredClone(source); monitor.kind = 'preview-capture-probe-scope'; monitor.scopeKind = 'root-surface-commit-monitor-plane-unqualified';
  await refuse(send, seed(monitor), held, 'Typed client cannot become monitor while a native job is retained');
  await refuse(send, {kind:'seed', publication:'1', lease:'1', identity, scope:source.scope, title:'Legacy', application:'legacy'}, held, 'Legacy seed cannot downgrade typed client');
  for (const mutation of [
    v => { v.source.previewEligible = true; },
    v => { v.source.kind = monitor.kind; },
    v => { v.source.scopeKind = monitor.scopeKind; },
    v => { v.source.binding.session = '999'; },
    v => { v.identity = 'family:999'; },
    v => { v.publication = '2'; },
    v => { v.lease = '2'; },
    v => { v.source.maximumTransferBytes = '4097'; },
    v => { v.extra = true; },
    v => { v.source.scope.clock = '1'; },
    v => { v.source.binding.frontend = v.source.scope.binding.frontend = '999'; }
  ]) { const value = seed(); mutation(value); await refuse(send, value, held, 'Malformed/foreign/stale source seed preserves retained owner'); }
  const offered = {...frame, signaled:false};
  result = await send('native', {kind:'event', identity, event:{kind:'offer', frame:offered}});
  check(result.models[0].model.candidate !== null, 'Real native client packet waits for readiness');
  result = await send('native', {kind:'event', identity, event:{kind:'fence', frame}});
  check(result.models[0].model.state === 'live' && result.models[0].model.accepted.fidelity === 'client', 'Actual compiled lifecycle preserves client fidelity');
  const renewed = seed(); renewed.source.scope.now = String(BigInt(source.scope.now)+1n); renewed.source.scope.observation = String(BigInt(source.scope.observation)+1n);
  result = await send('native', renewed);
  check(result.models[0].model.scope.now === renewed.source.scope.now && result.models[0].model.known.length === 1, 'Same typed source admits newer facts while retaining ownership');
  check(result.models[0].model.known[0].deadline === frame.job.deadline, 'New observation does not renew original native deadline');
  result = await send('presentation', presentation('2', 'closed'));
  check(result.models[0].model.retiring.length === 1 && result.models[0].model.known.length === 1, 'Popup closure retains physical release obligations');
  check(result.commands[0].commands[0].kind === 'release', 'Actual Elm requests explicit physical release');
  const receipt = fixture.terminalReceipts[0];
  result = await send('native', receipt);
  assert.deepEqual(result.commands, [{identity, commands:[{kind:'acknowledge', job:frame.job, sequence:receipt.event.sequence}]}]); checks++;
  check(result.models[0].model.known.length === 0 && result.models[0].model.retiring.length === 0, 'Exact retained native terminal proof drains Elm obligations');
  const fresh = worker(); await fresh('presentation', presentation());
  result = await fresh('native', seed(monitor));
  check(result.models.length === 1 && result.models[0].model.demand, 'Separately typed monitor seed remains supported');
  await refuse(fresh, seed(), result, 'Monitor entry cannot alias a client entry');
  const legacy = worker(); await legacy('presentation', presentation());
  result = await legacy('native', {kind:'seed', publication:'1', lease:'1', identity, scope:source.scope, title:'Legacy', application:'legacy'});
  check(result.models.length === 1, 'Existing legacy seed protocol remains supported');
  await refuse(legacy, seed(), result, 'An untyped retained entry cannot silently change source domain');
  process.stdout.write(JSON.stringify({passed:true, checks, source:'real retained own-provider observation and packet',
    nativeAcceptance:false, fullReleaseAccepted:false,
    scope:'Actual optimized Popup-shared PreviewPresenter and lifecycle replay; no WebKit or live native ACK execution'})+'\n');
})().catch(error => { process.stderr.write(error.stack+'\n'); process.exitCode=1; });
