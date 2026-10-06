'use strict';
const assert = require('node:assert/strict');
const fs = require('node:fs');
const path = require('node:path');
const crypto = require('node:crypto');
const child = require('node:child_process');
const {Elm} = require(path.resolve(process.argv[2]));
const fixture = JSON.parse(fs.readFileSync(process.argv[4], 'utf8'));
assert.equal(crypto.createHash('sha256').update(fs.readFileSync(fixture.nativeReport)).digest('hex'), fixture.sha256);
const native = JSON.parse(fs.readFileSync(fixture.nativeReport, 'utf8'));
assert(native.passed && native.cleanupPassed && native.ownedExitCodes.every(row => row.exitCode === 0));
assert.deepEqual(fixture.scopes, native.styleCropCaptureSamples.map(row => row.source));
const app = Elm.NativeFamilyPreviewSourceReplay.init();
let pending = null;
app.ports.outgoing.subscribe(value => { assert(pending); const deliver = pending; pending = null; deliver(value); });
function elm(value) {
  return new Promise((resolve, reject) => {
    assert.equal(pending, null);
    const timer = setTimeout(() => { pending = null; reject(new Error('Original three-second compiled Elm port deadline')); }, 3000);
    pending = result => { clearTimeout(timer); resolve(result); };
    app.ports.incoming.send(value);
  });
}
let checks = 0;
async function coupled(value, baseline, accepted) {
  const args = ['lifetime', 'session', 'frontend'].map(key => baseline.binding[key]);
  args.push(baseline.scope.context.incarnation, baseline.requestId);
  const run = child.spawnSync(process.argv[3], args, {input:JSON.stringify(value)+'\n', encoding:'utf8', timeout:3000});
  assert.equal(run.status, 0, run.stderr);
  const cpp = JSON.parse(run.stdout);
  const result = await elm(value);
  assert.equal(cpp.accepted, accepted);
  assert.equal(result.accepted, accepted);
  checks += 2;
  if (accepted) {
    assert.deepEqual(result.observation.scope, baseline.scope);
    assert.deepEqual(result.observation.crop, cpp.crop);
    assert.equal(result.observation.memberCount, cpp.memberCount);
    assert.equal(result.observation.styleCount, cpp.styleCount);
    assert.equal(result.observation.previewEligible, false);
    checks += 5;
  }
}
(async () => {
  for (const value of fixture.scopes) await coupled(value, value, true);
  const base = fixture.scopes[2];
  const mutations = [
    v => {v.protocolVersion = 2;},
    v => {v.kind = 'preview-client-scope';},
    v => {v.scopeKind = 'isolated-root-client-unqualified';},
    v => {v.previewEligible = true;},
    v => {v.extra = true;},
    v => {v.requestId = '0';},
    v => {v.binding.session = '999';},
    v => {v.scope.binding.frontend = '999';},
    v => {v.scope.clock = '999';},
    v => {v.scope.context.lifetime = '999';},
    v => {v.scope.context.incarnation = '999';},
    v => {v.scope.context.content = 8;},
    v => {v.maximumTransferBytes = '4097';},
    v => {v.maximumTransferBytes = '134221824';},
    v => {v.maximumTransferBytes = '18446744073709551615';},
    v => {v.members = [];},
    v => {v.members.push(structuredClone(v.members[0]));},
    v => {v.members[1].parent = null;},
    v => {v.members[1].parent = v.members[1].incarnation;},
    v => {v.members[1].parent = '999';},
    v => {v.members[0].parent = v.members[1].incarnation;},
    v => {v.members[0].geometry.pop();},
    v => {v.members[0].geometry[0] = null;},
    v => {v.members[0].flags = 512;},
    v => {v.styles.pop();},
    v => {v.styles[1].incarnation = v.styles[0].incarnation;},
    v => {v.styles[0].flags = 4096;},
    v => {v.styles[0].channels.pop();},
    v => {v.styles[0].channels[7] = '0.3';},
    v => {v.styles[0].gradients.pop();},
    v => {v.styles[0].gradients[0].colors = -1;},
    v => {v.styles[0].gradients[0].angle = null;},
    v => {v.crop.width = 0;},
    v => {v.crop.height = 4097;},
    v => {v.crop.scale = 0;},
    v => {v.crop.scale = -1;},
    v => {v.crop.pixelX = '-0';},
    v => {v.crop.pixelX = '-2147483649';},
    v => {v.crop.pixelY = '2147483648';},
    v => {v.crop.pixelX = -187;},
    v => {v.crop.pixelX = '-0187';},
    v => {delete v.crop;},
    v => {v.crop.extra = true;}
  ];
  for (const mutation of mutations) {const value = structuredClone(base); mutation(value); await coupled(value, base, false);}
  process.stdout.write(JSON.stringify({passed:true, checks, nativeScopes:fixture.scopes.length, malformedScopes:mutations.length,
    nativeAcceptance:false, fullReleaseAccepted:false,
    scope:'Actual compiled C++ and optimized Elm structural/correlation admission over retained native43 scopes. No new live family provider image transport.'})+'\n');
})().catch(error => {process.stderr.write(error.stack+'\n'); process.exitCode = 1;});
