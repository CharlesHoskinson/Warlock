'use strict';
// Integration fragment: pass the compiled Elm output as argv[2]. No I/O beyond
// loading it and printing the result; caller retains stdout and tool provenance.
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
const inputs = Array.from({length:200}, (_, index) => sequence(index));
app.ports.outgoing.subscribe(result => {
  const input = inputs[cursor];
  const bad = result.inputError || !Array.isArray(result.trace) || result.trace.length !== input.events.length ||
    result.trace.some(step => Object.values(step.checks || {}).some(c => c.actual !== c.expected));
  if (bad) failures.push({seed, sequence:cursor, input, result});
  cursor++;
  if (cursor === inputs.length) {
    process.stdout.write(JSON.stringify({seed, algorithm:'xorshift32', sequences:inputs.length,
      minSteps:26, maxSteps:40, failures}, null, 2) + '\n');
    process.exitCode = failures.length ? 1 : 0;
  } else app.ports.incoming.send(inputs[cursor]);
});
app.ports.incoming.send(inputs[0]);
