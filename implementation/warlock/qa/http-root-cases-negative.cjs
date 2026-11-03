'use strict';
// Root-only controls; fixtures remain independent source literals.
const fs = require('node:fs');
const path = require('node:path');
const { validateFiles, validateCases, validateJoined } = require('./http-root-cases-guard.cjs');
const dir = __dirname;
const repo = path.resolve(process.argv[2] || '.');
const manifest = JSON.parse(fs.readFileSync(path.join(dir, 'http-root-cases-manifest.json'), 'utf8'));
const files = { base: fs.readFileSync(path.join(dir, manifest.fixtures.base.file)),
  peer: fs.readFileSync(path.join(dir, manifest.fixtures.peer.file)),
  policy: fs.readFileSync(path.join(repo, manifest.fixtures.policy.file)),
  joined: fs.readFileSync(path.join(dir, manifest.fixtures.joined.file)),
  closedTopology: fs.readFileSync(path.join(dir, manifest.fixtures.closedTopology.file)) };
function mustFail(name, fn, expected) {
  let error;
  try { fn(); } catch (e) { error = e; }
  if (!error || !String(error.message).includes(expected)) throw new Error(`${name}: expected rejection ${expected}`);
}
validateFiles(manifest, files);
const base = require('./sol-http-popup-literals-0525.cjs').build(repo);
const peer = require('./httpbar-literals.cjs').build(repo);
const cases = base.cases.concat(peer.cases);
validateCases(manifest, cases);
const joined = require('./joined-control-literals.cjs').build(repo).cases.concat(
  require('./closed-topology-after-dismiss-literals.cjs').build(repo).cases);
validateJoined(manifest, joined);
mustFail('absent peer', () => validateFiles(manifest, {...files, peer: undefined}), 'peer: missing or empty');
mustFail('empty peer', () => validateFiles(manifest, {...files, peer: Buffer.alloc(0)}), 'peer: missing or empty');
mustFail('altered peer', () => validateFiles(manifest, {...files, peer: Buffer.concat([files.peer, Buffer.from('x')])}), 'peer: fixture digest mismatch');
mustFail('removed peer cases', () => validateCases(manifest, base.cases), 'ordered case inventory differs');
mustFail('removed named case', () => validateCases(manifest, cases.slice(0, -1)), 'ordered case inventory differs');
mustFail('duplicate case', () => validateCases(manifest, cases.concat(cases[0])), 'duplicate case name');
mustFail('absent joined', () => validateFiles(manifest, {...files, joined: undefined}), 'joined: missing or empty');
mustFail('empty joined', () => validateFiles(manifest, {...files, joined: Buffer.alloc(0)}), 'joined: missing or empty');
mustFail('altered joined', () => validateFiles(manifest, {...files, joined: Buffer.concat([files.joined,Buffer.from('x')])}), 'joined: fixture digest mismatch');
mustFail('removed joined case', () => validateJoined(manifest, []), 'joined case inventory differs');
mustFail('duplicate joined case', () => validateJoined(manifest, joined.concat(joined[0])), 'joined case inventory differs');
mustFail('absent closed topology', () => validateFiles(manifest, {...files, closedTopology: undefined}), 'closedTopology: missing or empty');
mustFail('empty closed topology', () => validateFiles(manifest, {...files, closedTopology: Buffer.alloc(0)}), 'closedTopology: missing or empty');
mustFail('altered closed topology', () => validateFiles(manifest, {...files, closedTopology: Buffer.concat([files.closedTopology,Buffer.from('x')])}), 'closedTopology: fixture digest mismatch');
mustFail('removed closed topology case', () => validateJoined(manifest, joined.slice(0, 1)), 'joined case inventory differs');
mustFail('reordered joined cases', () => validateJoined(manifest, [...joined].reverse()), 'joined case inventory differs');
console.log(JSON.stringify({ok: true, controls: ['absent-peer','empty-peer','altered-peer','removed-peer-cases','removed-case','duplicate-case','absent-joined','empty-joined','altered-joined','removed-joined-case','duplicate-joined-case','absent-closed-topology','empty-closed-topology','altered-closed-topology','removed-closed-topology-case','reordered-joined-cases'], originalAcceptanceClaim: false}));
