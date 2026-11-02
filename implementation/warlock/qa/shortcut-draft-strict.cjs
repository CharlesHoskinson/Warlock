'use strict';
// Fixed CLI: node qa/shortcut-draft-strict.cjs /absolute/ShortcutDraftProperties.js.
// Root records stdout and complete compiler/package provenance.
const fs = require('fs');
const crypto = require('crypto');
const path = require('path');
const artifact = path.resolve(process.argv[2]);
// Bind the authored source closure, entrypoint, manifest, harness and compiled
// artifact. Integrator must additionally bind Elm compiler and package closure.
const closure = {
  harness: __filename,
  artifact,
  fixture: path.join(__dirname, 'ShortcutDraftProperties.elm'),
  preferences: path.join(__dirname, '../src/ShortcutPreferences.elm'),
  counter: path.join(__dirname, '../src/UInt64.elm'),
  elmManifest: path.join(__dirname, '../elm.json'),
};
const hashes = Object.fromEntries(Object.entries(closure).map(([name,file]) =>
  [name, crypto.createHash('sha256').update(fs.readFileSync(file)).digest('hex')]));
const { Elm } = require(require('path').resolve(process.argv[2]));
const seed = 0x5eeda405;
let rng = seed >>> 0;
function random() { rng ^= rng << 13; rng ^= rng >>> 17; rng ^= rng << 5; return rng >>> 0; }
function sequence(index) {
  const revision = (index & 1) ? '18446744073709551614' : '2';
  const finalRevision = (index & 1) ? '18446744073709551615' : '3';
  const request = (index & 2) ? '18446744073709551615' : '1';
  const events = ['load','edit-app','edit-system','edit-notifications','same',
    'changed','blocked-save','same','stale','reaffirm-app','blocked-save',
    'reaffirm-system','failure','blocked-save','recover','invalid','blocked-save',
    'valid','save','unknown','foreign','failure','blocked-save','recover','mismatch'];
  // Repeat observation in a conflict or pending phase, retaining length 26–30.
  const extras = random() % 5;
  for (let i = 0; i < extras; i++) events.splice(8, 0, 'same');
  if (index & 4) events.splice(events.indexOf('unknown'), 0, 'newer-pending','stale-stored','stale-saved','stored-only','blocked-save','same','reaffirm-app','blocked-save','reaffirm-system','save');
  events.push((random() & 1) ? 'match' : 'receipt');
  return {index, revision, finalRevision, request, events};
}
const app = Elm.ShortcutDraftProperties.init({flags:null});
let cursor = 0;
const failures = [];
let failureCount = 0;
const inputs = Array.from({length:200}, (_, index) => sequence(index));
// These literal names are the independent result-consumer contract. Unknown,
// omitted, renamed or extra checks do not pass vacuously. Port objects cannot
// reveal duplicate JSON keys lost before this consumer receives the object.
const expectedName = Object.freeze({
  'load':'initial observation reaches writable model',
  'edit-app':'valid edit reaches chosen value',
  'edit-system':'valid edit reaches chosen value',
  'edit-notifications':'valid edit reaches chosen value',
  'same':'same revision retains draft and conflicts',
  'stale':'stale read preserves state',
  'changed':'new store preserves draft and identifies only changed routes',
  'reaffirm-app':'reaffirm clears only applications',
  'reaffirm-system':'reaffirm clears remaining route and restores readiness',
  'failure':'failed read preserves snapshot draft pending and conflicts; blocks writes',
  'recover':'recovery preserves draft and pending',
  'invalid':'invalidated selected chord blocks readiness',
  'valid':'valid inventory restores readiness when no pending or conflicts',
  'save':'explicit valid save emits proposal and pending',
  'blocked-save':'blocked save emits no proposal and preserves state',
  'newer-pending':'newer pending read retains intent and creates route conflicts',
  'stale-stored':'late Stored cannot roll back newer basis or release pending',
  'stale-saved':'late Saved cannot roll back newer basis or release pending',
  'stored-only':'definite stored completion preserves unresolved native conflicts',
  'unknown':'unknown preserves pending and draft',
  'foreign':'foreign receipt preserves entire state',
  'mismatch':'stored match with native mismatch remains pending',
  'match':'exact stored and native match settles pending',
  'receipt':'matching saved receipt settles pending',
});
const record = x => x !== null && typeof x === 'object' && !Array.isArray(x) &&
  (Object.getPrototypeOf(x) === Object.prototype || Object.getPrototypeOf(x) === null) &&
  Reflect.ownKeys(x).every(k => typeof k === 'string' &&
    Object.getOwnPropertyDescriptor(x,k)?.enumerable === true &&
    Object.hasOwn(Object.getOwnPropertyDescriptor(x,k),'value'));
const keys = (x, expected) => record(x) &&
  JSON.stringify(Object.keys(x).sort()) === JSON.stringify([...expected].sort());
const equal = (a,b) => JSON.stringify(a) === JSON.stringify(b);
const routes = ['applications','system','notifications'];
const choices = x => keys(x,routes) && routes.every(k =>
  ['undecided','keep','default','alternate'].includes(x[k]));
const counter = x => typeof x === 'string' && /^(0|[1-9][0-9]*)$/.test(x) &&
  x.length <= 20 && BigInt(x) <= 18446744073709551615n;
const snapshot = x => keys(x,['revision','choices']) && counter(x.revision) && choices(x.choices);
const inventory = x => keys(x,['fingerprint','active','applicationsDefaultAvailable']) &&
  typeof x.fingerprint === 'string' && /^[0-9a-f]{64}$/.test(x.fingerprint) &&
  choices(x.active) && typeof x.applicationsDefaultAvailable === 'boolean';
const pending = x => keys(x,['request','choices','confirmation']) && counter(x.request) &&
  choices(x.choices) && ['awaiting','unconfirmed'].includes(x.confirmation);
const dense = x => Array.isArray(x) && Object.getPrototypeOf(x) === Array.prototype &&
  Reflect.ownKeys(x).length === x.length+1 &&
  Object.keys(x).length === x.length && Array.from({length:x.length},(_,i) =>
    Object.getOwnPropertyDescriptor(x,String(i))).every(d => d && d.enumerable &&
      Object.hasOwn(d,'value'));
const denseRoutes = x => Array.isArray(x) && x.length<=routes.length && dense(x) &&
  x.every(v => routes.includes(v)) && new Set(x).size === x.length;
// This is the fixture's explicitly encoded state projection, not the whole
// opaque policy model; omitted policy fields require their own full oracle.
const state = x => keys(x,['snapshot','inventory','draft','conflicts','pending','notice','ready','changed']) &&
  (x.snapshot===null || snapshot(x.snapshot)) && (x.inventory===null || inventory(x.inventory)) &&
  choices(x.draft) && denseRoutes(x.conflicts) && (x.pending===null || pending(x.pending)) &&
  typeof x.notice==='string' && typeof x.ready==='boolean' && typeof x.changed==='boolean';
const proposal = x => x===null || (keys(x,['preferences','fingerprint']) &&
  keys(x.preferences,['schema','revision','choices']) && x.preferences.schema===1 &&
  counter(x.preferences.revision) && choices(x.preferences.choices) &&
  typeof x.fingerprint==='string' && /^[0-9a-f]{64}$/.test(x.fingerprint));
function validate(result, input) {
  if (!keys(result,['input','trace']) ||
      !keys(result.input,['index','revision','finalRevision','request','events']) ||
      !Array.isArray(result.input.events) || result.input.events.length !== input.events.length ||
      !dense(result.input.events) || !equal(result.input,input) ||
      !Array.isArray(result.trace) || result.trace.length !== input.events.length || !dense(result.trace))
    return 'invalid result, input error, identity or trace length';
  for (let i=0; i<input.events.length; i++) {
    const event=input.events[i], step=result.trace[i], name=expectedName[event];
    if (!name || !keys(step,['event','input','before','after','proposal','checks']) ||
        step.event !== event || !keys(step.input,['revision','request','finalRevision']) ||
        step.input.revision !== input.revision || step.input.request !== input.request ||
        step.input.finalRevision !== input.finalRevision || !state(step.before) || !state(step.after) || !proposal(step.proposal) ||
        !keys(step.checks,[name]) || !keys(step.checks[name],['expected','actual']) ||
        step.checks[name].expected !== true || step.checks[name].actual !== true)
      return `invalid trace/check at event ${i}: ${event}`;
    if (i>0 && !equal(result.trace[i-1].after,step.before))
      return `discontinuous state at event ${i}: ${event}`;
  }
  return null;
}
app.ports.outgoing.subscribe(result => {
  const input = inputs[cursor];
  const bad = validate(result,input);
  if (bad) {
    failureCount++;
    if (failures.length < 8) failures.push({seed, sequence:cursor, reason:bad});
  }
  cursor++;
  if (cursor === inputs.length) {
    process.stdout.write(JSON.stringify({seed, algorithm:'xorshift32', sequences:inputs.length,
      minSteps:26, maxSteps:40, hashes, failureCount, failures}, null, 2) + '\n');
    process.exitCode = failureCount ? 1 : 0;
  } else app.ports.incoming.send(inputs[cursor]);
});
app.ports.incoming.send(inputs[0]);
