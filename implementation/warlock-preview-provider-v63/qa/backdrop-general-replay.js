'use strict';
const assert = require('node:assert/strict');
const fs = require('node:fs');
const path = require('node:path');
const crypto = require('node:crypto');
const {Elm} = require(path.resolve(process.argv[2]));
const fixture = JSON.parse(fs.readFileSync(process.argv[3], 'utf8'));
assert.equal(crypto.createHash('sha256').update(fs.readFileSync(fixture.nativeReport)).digest('hex'), fixture.sha256);
const app = Elm.NativePreviewSourceReplay.init();
let pending = null;
app.ports.outgoing.subscribe(value => {assert(pending); const done = pending; pending = null; done(value);});
function send(value) {
  return new Promise((resolve, reject) => {
    assert.equal(pending, null);
    const timer = setTimeout(() => reject(new Error('Original three-second Elm decoder deadline')), 3000);
    pending = result => {clearTimeout(timer); resolve(result);};
    app.ports.incoming.send(value);
  });
}
(async () => {
  let checks = 0;
  for (const source of fixture.scopes) {
    const result = await send(source);
    assert(result.accepted);
    assert.equal(result.observation.source, 'generated-backdrop-family-unqualified');
    assert.deepEqual(result.observation.generatedBackdrop, source.generatedBackdrop);
    assert.deepEqual(result.observation.scope, source.scope);
    checks += 4;
  }
  for (const mutate of [
    v => {v.generatedBackdrop.colorARGB = '4294967296';},
    v => {v.generatedBackdrop.colorARGB = '4278190079';},
    v => {v.kind = 'preview-client-scope';},
    v => {v.kind = 'preview-family-style-crop-scope';},
    v => {delete v.generatedBackdrop;},
    v => {v.previewEligible = true;}
  ]) {
    const source = structuredClone(fixture.scopes[0]); mutate(source);
    assert.equal((await send(source)).accepted, false); checks++;
  }
  process.stdout.write(JSON.stringify({passed:true, checks, nativeAcceptance:false,
    scope:'Actual optimized shared native source dispatcher admits explicit generated color and refuses malformed/cross-plane sources.'})+'\n');
})().catch(error => {process.stderr.write(error.stack+'\n'); process.exitCode = 1;});
