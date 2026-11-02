"use strict";
// QA-only unexecuted fixed FilesReplay result consumer adapted from Sol reconnect runner. Root's current protected profile
// binds full sources/compiler/artifact/executed runner bytes and process timeout.
// The 3s watchdog waits for output; it is not a whole-process/lifetime proof.
// No env, network, compiler, service, native operation or process launch.
const fs = require('node:fs');
const path = require('node:path');
const crypto = require('node:crypto');
const vm = require('node:vm');
const assert = (ok,why) => {if(!ok) throw Error(why);};
const sha = bytes => crypto.createHash('sha256').update(bytes).digest('hex');
const FIXTURE = Object.freeze({name: 'FilesReplay', names: Object.freeze(["FilesOpenerIntegrated", "InstalledCollectionNamesPreserved", "NativeModeAccepted", "CurrentLocationDisplayed", "ExactlyOneExplicitCollectionOpening", "PopupClosesBeforeNativeOpening", "ObservedOutcomeSettles", "UnknownRemainsVisibleAndCannotReplay", "RefreshNeverOpens", "ChangedReadReconcilesWithoutReplay", "ReplacementCannotBeReportedAsReused", "WrongLocationCannotBeReportedAsOpened", "ConnectionLossKeepsUnknownWithoutReplay", "WrongReceiptDoesNotSettle", "TypingHasNoEffect", "FolderRequiresExplicitAction", "CommandTextDoesNotOpen", "CloseHasNoNavigationEffect", "AnotherPopupRetiresFiles", "FolderFieldHasScopedAcknowledgment", "DetachedSessionRetiresFiles", "MalformedDisconnectBindingRetainsFiles", "AllControlsNamed", "AwaitingCompleteLiteralState", "UnknownCompleteLiteralState", "DuplicateUnknownPreservesFullState", "MismatchedRefusalPreservesFullState", "LateCorrelatedRefusalPreservesReservationHistory", "LateVerifiedOpenHasCompleteLiteralState", "WrongPeerBecomesUnconfirmed", "WrongLocationBecomesUnconfirmed"]), count: 31, top: ['checks','frame','pathFrame','pendingFrame']});

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
    new vm.Script(artifact.text,{filename:path.basename(filename)}).runInContext(context,{timeout:3000});
    assert(context.Elm && context.Elm[spec.name] && typeof context.Elm[spec.name].init === 'function', 'wrong compiled worker module');
    const app = context.Elm[spec.name].init({flags:null});
    assert(app.ports && app.ports.outgoing && typeof app.ports.outgoing.subscribe === 'function', 'missing outgoing port');
    await new Promise((resolve,reject) => {
      rejectActive = reject;
      const watchdog = schedule(() => reject(new Error('worker output timeout')),3000);
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
  assert(process.argv.length === 4 && process.argv.slice(2).every(path.isAbsolute),'expected absolute compiled FilesReplay.js and NEW report path');
  let result;
  try { result = await observe(FIXTURE,process.argv[2]); }
  catch(error) { result = {name:FIXTURE.name,file:process.argv[2],checks:[],error:String(error && error.stack || error),passed:false}; }
  const passed = result.passed === true && result.checks.length === 31;
  const report = {schema:1,scope:'Files confirmation component; no whole-original/native/GUI/provider/AT/IME/performance/release acceptance',settleWindowMs:25,runnerPathSha256AtReport:readPinned(__filename).sha256,executedRunnerProvenance:'External protected launcher must bind executed bytes; self-read is path-at-report-time only',result,passed,originalAccepted:false,nativeAccepted:false};
  const fd = fs.openSync(process.argv[3],fs.constants.O_WRONLY|fs.constants.O_CREAT|fs.constants.O_EXCL|fs.constants.O_NOFOLLOW,0o600);
  try {fs.writeFileSync(fd,JSON.stringify(report,null,2)+'\n');}
  finally {fs.closeSync(fd);}
  if(!passed) process.exitCode=1;
}
main().catch(error=>{process.stderr.write(String(error && error.stack || error)+'\n');process.exitCode=1;});
