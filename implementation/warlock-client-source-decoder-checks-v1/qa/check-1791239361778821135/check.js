'use strict';
const assert = require('node:assert/strict');
const fs = require('node:fs');
const path = require('node:path');
const {Elm} = require(path.resolve(process.argv[2]));
const original = JSON.parse(fs.readFileSync(process.argv[3], 'utf8'));
const app = Elm.NativePreviewSourceReplay.init();
let pending = null;
const checks = [];
app.ports.outgoing.subscribe(value => { assert(pending, 'Unexpected Elm emission'); const accept = pending; pending = null; accept(value); });
function decode(value) {
  return new Promise((resolve, reject) => {
    const timer = setTimeout(() => { pending = null; reject(new Error('Compiled Elm source port timeout')); }, 3000);
    assert.equal(pending, null);
    pending = result => { clearTimeout(timer); resolve(result); };
    app.ports.incoming.send(value);
  });
}
async function check(name, value, expected, source = 'client') {
  const result = await decode(value);
  assert.equal(result.accepted, expected, name);
  if (expected) assert.deepEqual(result.observation, {
    source, request: value.requestId, maximumTransferBytes: value.maximumTransferBytes,
    previewEligible: false, scope: value.scope
  }, name + ': lossless original scope and identities');
  else assert.deepEqual(result, {accepted: false}, name + ': no invented facts');
  checks.push({name, passed: true});
}
const changed = edit => { const value = structuredClone(original); edit(value); return value; };
(async () => {
  assert.equal(original.kind, 'preview-client-scope');
  assert(BigInt(original.binding.lifetime) > 9007199254740991n, 'Actual native lifetime exercises lossless uint64');
  await check('actual-own-provider-client-observation', original, true);
  const monitor = changed(v => { v.kind = 'preview-capture-probe-scope'; v.scopeKind = 'root-surface-commit-monitor-plane-unqualified'; });
  await check('explicit-legacy-monitor-kind', monitor, true, 'monitor');
  await check('client-kind-with-monitor-label', changed(v => { v.scopeKind = monitor.scopeKind; }), false);
  await check('monitor-kind-with-client-label', changed(v => { v.kind = monitor.kind; }), false);
  for (const value of [true, 1, 'false', null]) await check('no-eligibility-promotion-' + JSON.stringify(value), changed(v => { v.previewEligible = value; }), false);
  for (const version of [2, 4, '3', null, true]) await check('protocol-' + JSON.stringify(version), changed(v => { v.protocolVersion = version; }), false);
  for (const field of ['lifetime', 'session', 'frontend']) {
    await check('outer-binding-mismatch-' + field, changed(v => { v.binding[field] = String(BigInt(v.binding[field]) + 1n); }), false);
    await check('inner-binding-mismatch-' + field, changed(v => { v.scope.binding[field] = String(BigInt(v.scope.binding[field]) + 1n); }), false);
  }
  await check('context-lifetime-mismatch', changed(v => { v.scope.context.lifetime = '1'; }), false);
  await check('clock-domain-mismatch', changed(v => { v.scope.clock = '1'; }), false);
  const paths = [
    ['requestId'], ['maximumTransferBytes'],
    ...['lifetime', 'session', 'frontend'].flatMap(k => [['binding', k], ['scope', 'binding', k]]),
    ...Object.keys(original.scope.context).map(k => ['scope', 'context', k]),
    ...['observation', 'clock', 'now'].map(k => ['scope', k])
  ];
  for (const keys of paths) {
    for (const invalid of ['0', '01', '-1', '1.0', '1e3', '18446744073709551616', 1, null, true]) {
      await check(keys.join('.') + '-invalid-' + JSON.stringify(invalid), changed(v => {
        let target = v; for (const k of keys.slice(0, -1)) target = target[k]; target[keys.at(-1)] = invalid;
      }), false);
    }
  }
  for (const budget of ['1', '4095', '4097', '9007199254740991', '18446744073709551615'])
    await check('unaligned-budget-' + budget, changed(v => { v.maximumTransferBytes = budget; }), false);
  for (const budget of ['4096', '9007199254740992', '18446744073709547520'])
    await check('lossless-aligned-budget-' + budget, changed(v => { v.maximumTransferBytes = budget; }), true);
  for (const keys of [[], ['binding'], ['scope'], ['scope', 'binding'], ['scope', 'context']]) {
    const target = keys.reduce((value, k) => value[k], original);
    for (const field of Object.keys(target)) await check('missing-' + [...keys, field].join('.'), changed(v => {
      let out = v; for (const k of keys) out = out[k]; delete out[field];
    }), false);
    await check('extra-' + (keys.join('.') || 'envelope'), changed(v => {
      let out = v; for (const k of keys) out = out[k]; out.extra = 'injected';
    }), false);
  }
  for (const flag of ['present', 'sourceLive', 'locked', 'gpuReady']) {
    await check('typed-native-flag-' + flag, changed(v => { v.scope[flag] = !v.scope[flag]; }), true);
    await check('malformed-native-flag-' + flag, changed(v => { v.scope[flag] = 1; }), false);
  }
  for (const bad of [null, [], true, 3, 'client']) await check('non-envelope-' + JSON.stringify(bad), bad, false);
  process.stdout.write(JSON.stringify({passed: true, checks, nativeAcceptance: false, fullReleaseAccepted: false,
    scope: 'Actual optimized Elm typed source decoder with retained real native observation; no full Popup/WebKit presentation claim'}) + '\n');
})().catch(error => { process.stderr.write(error.stack + '\n'); process.exitCode = 1; });
