'use strict';
const crypto = require('node:crypto');
const { isDeepStrictEqual } = require('node:util');
const digest = bytes => crypto.createHash('sha256').update(bytes).digest('hex');
function insist(ok, message) { if (!ok) throw new Error(message); }
function validateFiles(manifest, files) {
  insist(manifest && manifest.schema === 1 && manifest.requirement === 'ELM-TEA-004' &&
    manifest.scenario === 'tea-subscriptions' && manifest.coverageComplete === false &&
    manifest.originalAcceptanceClaim === false, 'invalid manifest identity or acceptance');
  for (const name of ['base', 'peer', 'policy', 'joined']) {
    insist(Buffer.isBuffer(files[name]) && files[name].length > 0, `${name}: missing or empty fixture`);
    insist(manifest.fixtures && manifest.fixtures[name] &&
      digest(files[name]) === manifest.fixtures[name].sha256, `${name}: fixture digest mismatch`);
  }
  insist(manifest.fixtures.peer.file === 'httpbar-literals.cjs' &&
    manifest.fixtures.peer.sha256 === '6f645e235c119e2a8069d9a6d7542c1f45cd95d667ddbe5e3f6129f83a255173',
    'required reviewed HttpBar peer pin changed');
  insist(manifest.fixtures.joined.file === 'joined-control-literals.cjs', 'joined peer path changed');
}
function validateCases(manifest, cases) {
  insist(Array.isArray(manifest.cases) && manifest.cases.length > 0 && Array.isArray(cases), 'case inventory missing');
  const actual = cases.map(c => ({name: c.name, root: c.root, steps: Array.isArray(c.steps) ? c.steps.length : -1}));
  insist(new Set(actual.map(c => c.name)).size === actual.length, 'duplicate case name');
  insist(isDeepStrictEqual(actual, manifest.cases), 'ordered case inventory differs from reviewed manifest');
}
function validateJoined(manifest, cases) {
  insist(manifest.joined && Array.isArray(cases), 'joined case inventory missing');
  const actual = cases.map(c => ({name:c.name, root:c.root, steps:Array.isArray(c.steps) ? c.steps.length : -1}));
  insist(cases.length === 1 && isDeepStrictEqual(actual, [manifest.joined]), 'joined case inventory differs');
}
module.exports = { validateFiles, validateCases, validateJoined };
