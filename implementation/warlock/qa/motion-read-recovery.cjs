'use strict';
// QA-only unexecuted runner. Root stages compiled Elm and preserves stdout and
// exact source/compiler/artifact hashes through the protected QA workflow.
const path = require('node:path');
if (process.argv.length !== 3 || !path.isAbsolute(process.argv[2])) throw Error('Expected absolute compiled MotionReadRecoveryReplay.js');
const { Elm } = require(path.resolve(process.argv[2]));
const names = [
  'preludeExactPendingRequest', 'unknownLiteral', 'explicitRefreshSendsOneRequest',
  'conflictingSameRevisionReadRetainsLiteralPending', 'unavailableReadRetainsLiteralPending',
  'sameStoredReadReconcilesWithoutWriteReceipt', 'unknownNeverAutomaticallyRepeats',
  'lateSavedRequiresNewRevisionAndExactProfileEffect'
].sort();
const failures = [];
let first = null, count = 0, done = false;
function plain(value, fields) {
  if (!value || typeof value !== 'object' || Array.isArray(value)) return false;
  const proto = Object.getPrototypeOf(value);
  if (proto !== Object.prototype && proto !== null) return false;
  if (Object.getOwnPropertySymbols(value).length) return false;
  const desc = Object.getOwnPropertyDescriptors(value);
  const keys = Object.keys(desc).sort();
  return JSON.stringify(keys) === JSON.stringify([...fields].sort()) &&
    keys.every(k => Object.hasOwn(desc[k], 'value') && desc[k].enumerable);
}
function finish() {
  if (done) return;
  done = true;
  clearTimeout(watchdog);
  const cases = plain(first, ['cases']) && Array.isArray(first.cases) ? first.cases : [];
  if (count !== 1) failures.push({reason:'Expected exactly one output within settle window', actual:count});
  if (cases.length !== 16) failures.push({reason:'Expected exactly 16 cases', actual:cases.length});
  const descriptors = Object.getOwnPropertyDescriptors(cases);
  const indices = Array.from({length:cases.length}, (_, i) => String(i));
  const arrayValid = Object.getPrototypeOf(cases) === Array.prototype && !Object.getOwnPropertySymbols(cases).length &&
    Object.keys(descriptors).filter(k => k !== 'length').join(',') === indices.join(',') &&
    indices.every(k => descriptors[k] && Object.hasOwn(descriptors[k], 'value') && descriptors[k].enumerable);
  if (!arrayValid) failures.push({reason:'Sparse, extended, accessor or nonstandard case array'});
  for (let i = 0; arrayValid && i < cases.length; i++) {
    const item = descriptors[String(i)].value;
    if (!plain(item, ['seed','revision','checks'])) { failures.push({seed:i,reason:'Unexpected case shape'}); continue; }
    if (item.seed !== i || item.revision !== String(i + 1)) failures.push({seed:i,reason:'Unexpected fixture identity'});
    if (!plain(item.checks, names)) { failures.push({seed:i,reason:'Wrong exact check manifest'}); continue; }
    for (const name of names) if (item.checks[name] !== true) failures.push({seed:i,reason:name,actual:item.checks[name] ?? null});
  }
  process.stdout.write(JSON.stringify({scope:'component-only; not native, release, full policy or EARS acceptance', settleMs:25, cases:cases.length, checksPerCase:names.length, failures}, null, 2) + '\n');
  process.exitCode = failures.length ? 1 : 0;
}
const watchdog = setTimeout(() => { failures.push({reason:'No replay result before QA watchdog'}); finish(); }, 10000);
const app = Elm.MotionReadRecoveryReplay.init({flags:null});
app.ports.outgoing.subscribe(result => {
  count++;
  if (count === 1) { first = result; setTimeout(finish, 25); }
});
