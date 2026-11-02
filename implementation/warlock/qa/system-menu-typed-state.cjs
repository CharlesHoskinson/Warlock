"use strict";
// Unexecuted QA-only source. Root compiles the two named Elm workers and runs
// this through its existing declared protected profile. No compiler, network,
// native operation, env read, process launch, or production authority here.
// Exactly one output is observed in a finite25ms window, not allfuture delivery.
const fs = require('node:fs');
const path = require('node:path');
const crypto = require('node:crypto');
const vm = require('node:vm');
const assert = (ok, why) => { if (!ok) throw new Error(why); };
const sha = bytes => crypto.createHash('sha256').update(bytes).digest('hex');
const LEGACY = Object.freeze(["sessionClosingClassifiedAndLogoutDenied", "otherSessionTextLabelAndLogoutPreserved", "sessionStateBoundsAndTypeRefused", "networkPermissionsPreserveAdmission", "powerCapabilitiesPreserveAdmission", "foreignNetworkCapabilityRefused", "foreignPowerPermissionRefused", "powerCapabilityLabelsPreserved", "systemMenuOpenerIntegrated", "menuModeAcceptedByProductionRenderer", "openingReadFocusMatchesCloseControl", "originalUnavailableNetworkShown", "remainingStateObserved", "oneExplicitVolumeChange", "pendingCannotRepeat", "committedCannotRepeatOldRevision", "unknownCannotReplay", "readReconcilesChangedStateWithoutEffect", "unavailableNeverSubmits", "restartRequiresUIConfirmation", "cancelHasNoNativeEffect", "confirmedRestartSubmitsOnce", "directConfirmationCannotBypassPrompt", "wrongReceiptCannotSettle", "staleViewCannotSubmit", "closingFocusesOpenerWithoutNativeEffect", "anotherPopupRetiresSystemWithoutLosingNativeState", "allControlsHaveNames"]);
const DOMAIN_SUFFIXES = Object.freeze(["given-complete-domain", "positive-proposal-complete-domain-and-wire", "pending-duplicate-no-effect", "unknown-retains-complete-reservation", "unknown-duplicate-stable", "unknown-cannot-repeat", "foreign-request-preserves-complete-state", "foreign-service-preserves-complete-state", "invalid-status-preserves-complete-state", "late-committed-settles", "late-submitted-settles-without-invented-observation", "late-refused-retains-spent-intent", "same-revision-read-keeps-unconfirmed", "observation-preserves-typed-reservation", "older-outcome-after-new-observation-is-stale", "newer-read-settles-without-replay", "old-intent-cannot-be-replayed-after-read", "fresh-explicit-intent-can-follow-new-observation", "full-width-request-preserved"]);
const DESKTOP = Object.freeze(["desktop/given-counter-and-complete-child-pinned", "desktop/given-proposal-full-ordered-effect", "desktop/unknown-full-model-and-every-effect", "desktop/duplicate-unknown-full-model-no-effect", "desktop/unknown-no-replay-full-model", "desktop/late-refused-full-model-and-every-effect", "desktop/late-submitted-full-model-and-every-effect", "desktop/wrong-request-preserves-full-model", "desktop/foreign-binding-preserves-full-model", "desktop/foreign-service-preserves-full-model", "desktop/malformed-status-preserves-full-model", "desktop/null-status-preserves-full-model", "desktop/refresh-full-model-and-exact-read-effect", "desktop/matching-newer-read-full-model-no-replay"]);
const CAPABILITIES = Object.freeze(["capability/network-yes-complete-model-wire", "capability/network-no-complete-model-wire", "capability/network-auth-complete-model-wire", "capability/power-suspend-yes-complete-model-wire", "capability/power-reboot-yes-complete-model-wire", "capability/power-poweroff-yes-complete-model-wire", "capability/power-suspend-no-complete-model-wire", "capability/power-reboot-no-complete-model-wire", "capability/power-poweroff-no-complete-model-wire", "capability/power-suspend-na-complete-model-wire", "capability/power-reboot-na-complete-model-wire", "capability/power-poweroff-na-complete-model-wire", "capability/power-suspend-challenge-complete-model-wire", "capability/power-reboot-challenge-complete-model-wire", "capability/power-poweroff-challenge-complete-model-wire", "capability/network-cross-domain-rejected", "capability/power-cross-domain-rejected"]);

const SESSIONS = Object.freeze(["session/closing-complete-model-no-wire", "session/active-complete-model-and-wire", "session/online-complete-model-and-wire", "session/open-text-complete-model-and-wire", "session/empty-complete-model-and-wire", "session/case-sensitive-complete-model-and-wire", "session/near-closing-complete-model-and-wire", "session/maximum-text-complete-model-and-wire", "session/overlong-text-rejected", "session/control-text-rejected", "session/non-string-rejected"]);

const MODERN = Object.freeze(Array.from({length:32}, (_, seed) => DOMAIN_SUFFIXES.map(s => `seed-${seed}/${s}`)).flat().concat(DESKTOP, CAPABILITIES, SESSIONS));
const FIXTURES = Object.freeze([
  { name:'SystemMenuReplay', names:LEGACY, top:['checks','frame','confirmFrame','pendingFrame'], count:28 },
  { name:'SolSystemMenuIntegratedReplay2114', names:MODERN, top:['schema','scope','seeds','checks','checkCount','requiredCheckCount','originalAccepted','nativeAccepted'], count:650 },
]);

function dataJson(value, where, ancestors, realm) {
  if (value === null || typeof value === 'string' || typeof value === 'boolean') return;
  if (typeof value === 'number') {
    assert(Number.isFinite(value) && !Object.is(value, -0), `${where}: unsupported number`);
    return;
  }
  assert(typeof value === 'object' && !ancestors.has(value), `${where}: unsupported or cyclic value`);
  const array = Array.isArray(value);
  const proto = Object.getPrototypeOf(value);
  assert(proto === (array ? realm.array : realm.object) || (!array && proto === null), `${where}: unsupported prototype`);
  assert(Object.getOwnPropertySymbols(value).length === 0, `${where}: symbol keys`);
  const desc = Object.getOwnPropertyDescriptors(value);
  const keys = Object.keys(desc).filter(k => !(array && k === 'length'));
  if (array) assert(keys.length === value.length && keys.every((k,i) => k === String(i)), `${where}: sparse or extended array`);
  ancestors.add(value);
  try {
    for (const key of keys) {
      assert(Object.hasOwn(desc[key], 'value') && desc[key].enumerable, `${where}.${key}: accessor or hidden field`);
      dataJson(desc[key].value, `${where}.${key}`, ancestors, realm);
    }
  } finally { ancestors.delete(value); }
}

function exactKeys(value, expected, where) {
  assert(value !== null && typeof value === 'object' && !Array.isArray(value), `${where}: expected object`);
  const actual = Object.keys(value).sort();
  assert(JSON.stringify(actual) === JSON.stringify([...expected].sort()), `${where}: missing or extra keys`);
}

function readPinned(filename) {
  const fd = fs.openSync(filename, fs.constants.O_RDONLY | fs.constants.O_NOFOLLOW);
  try {
    const a = fs.fstatSync(fd, {bigint:true});
    assert(a.isFile(), 'compiled artifact is not a regular file');
    const bytes = fs.readFileSync(fd);
    const b = fs.fstatSync(fd, {bigint:true});
    for (const key of ['dev','ino','size','mtimeNs','ctimeNs']) assert(a[key] === b[key], 'compiled artifact changed during read');
    const text = bytes.toString('utf8');
    assert(Buffer.from(text, 'utf8').equals(bytes), 'compiled artifact is not exact UTF-8');
    return {bytes,text,sha256:sha(bytes)};
  } finally { fs.closeSync(fd); }
}

async function observe(spec, filename) {
  assert(spec.names.length === spec.count && new Set(spec.names).size === spec.count, 'invalid fixed source check manifest');
  const artifact = readPinned(filename);
  const handles = new Set();
  const messages = [];
  let asyncFailure = null;
  let rejectActive = null;
  const schedule = (fn, delay, ...args) => {
    let timer;
    timer = setTimeout(() => {
      handles.delete(timer);
      try { fn(...args); }
      catch (error) { asyncFailure = error; if (rejectActive) rejectActive(error); }
    }, delay);
    handles.add(timer);
    return timer;
  };
  const unschedule = timer => { handles.delete(timer); clearTimeout(timer); };
  try {
    const context = vm.createContext({console:{log(){},warn(){},error(){}},setTimeout:schedule,clearTimeout:unschedule});
    const realm = vm.runInContext('({object:Object.prototype,array:Array.prototype})', context);
    new vm.Script(artifact.text,{filename:path.basename(filename)}).runInContext(context,{timeout:10000});
    assert(context.Elm && context.Elm[spec.name] && typeof context.Elm[spec.name].init === 'function', 'wrong compiled worker module');
    const app = context.Elm[spec.name].init({flags:null});
    assert(app.ports && app.ports.outgoing && typeof app.ports.outgoing.subscribe === 'function', 'missing outgoing port');
    await new Promise((resolve,reject) => {
      rejectActive = reject;
      const watchdog = schedule(() => reject(new Error('worker output timeout')),10000);
      app.ports.outgoing.subscribe(payload => {
        try {
          dataJson(payload,'$',new Set(),realm);
          messages.push(JSON.parse(JSON.stringify(payload)));
          if (messages.length === 1) schedule(() => { unschedule(watchdog); resolve(); },25);
        } catch (error) { reject(error); }
      });
      if (asyncFailure) reject(asyncFailure);
    });
    assert(!asyncFailure,'asynchronous worker failure');
    assert(messages.length === 1, `expected one output within25ms window, received ${messages.length}`);
    const payload = messages[0];
    exactKeys(payload,spec.top,'payload');
    exactKeys(payload.checks,spec.names,'checks');
    if (spec.name === 'SolSystemMenuIntegratedReplay2114') {
      assert(payload.schema === 1 && typeof payload.scope === 'string','bad worker schema');
      assert(payload.checkCount === 650 && payload.requiredCheckCount === 650,'wrong declared check count');
      assert(JSON.stringify(payload.seeds) === JSON.stringify(Array.from({length:32},(_,i)=>i)),'wrong exact seed manifest');
      assert(payload.originalAccepted === false && payload.nativeAccepted === false,'worker cannot mint original/native acceptance');
    }
    const checks = spec.names.map(name => ({name,passed:payload.checks[name] === true}));
    return {name:spec.name,file:filename,sha256:artifact.sha256,checks,payload,passed:checks.every(row=>row.passed)};
  } catch (error) {
    return {name:spec.name,file:filename,sha256:artifact.sha256,checks:[],payloads:messages,error:String(error && error.stack || error),passed:false};
  } finally {
    rejectActive = null;
    for (const timer of handles) clearTimeout(timer);
    handles.clear();
  }
}

async function main() {
  assert(process.argv.length === 5 && process.argv.slice(2).every(path.isAbsolute),'expected absolute SystemMenuReplay.js, SolSystemMenuIntegratedReplay2114.js and NEW report path');
  const fixtures = [];
  for (let i=0;i<FIXTURES.length;i++) {
    try { fixtures.push(await observe(FIXTURES[i],process.argv[i+2])); }
    catch (error) { fixtures.push({name:FIXTURES[i].name,file:process.argv[i+2],checks:[],error:String(error && error.stack || error),passed:false}); }
  }
  const passed = fixtures.length === 2 && fixtures.every(f=>f.passed === true) && fixtures.reduce((n,f)=>n+f.checks.length,0) === 678;
  // A self-read identifies the path at report time, not necessarily executed
  // bytes if another process replaced it. Root binds executed source/artifacts
  // through the existing protected launcher; this field cannot prove custody.
  const report = {schema:1,scope:'compiled SystemMenu component checks only; not EARS/native/GUI/AT/IME/provider/performance acceptance',settleWindowMs:25,runnerPathSha256AtReport:readPinned(__filename).sha256,executedRunnerProvenance:'External protected launcher must bind executed runner bytes; self-read is not execution provenance',fixtures,passed,originalAccepted:false,nativeAccepted:false};
  const fd = fs.openSync(process.argv[4],fs.constants.O_WRONLY|fs.constants.O_CREAT|fs.constants.O_EXCL|fs.constants.O_NOFOLLOW,0o600);
  try { fs.writeFileSync(fd,JSON.stringify(report,null,2)+'\n'); }
  finally { fs.closeSync(fd); }
  if (!passed) process.exitCode = 1;
}
main().catch(error => { process.stderr.write(String(error && error.stack || error)+'\n');process.exitCode=1; });
