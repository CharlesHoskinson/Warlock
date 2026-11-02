'use strict';
// UNRUN fixed result consumer for compiled UiHttpFailureReplay, QA only.
// Root's existing protected profile supplies absolute compiled JS and a NEW
// report path, and binds complete sources, compiler, artifact and runner bytes.
// Its whole-process deadline must cover synchronous init/subscribe; the VM
// script timeout and asynchronous watchdog cannot preempt a blocked event loop.
// Early argument/read/report-write failures have stderr+nonzero but no report.
// The 25ms window bounds observation of output cardinality, not product latency
// or proof of future silence. Commands from the Elm replay are not interpreted.
const fs=require('node:fs');
const vm=require('node:vm');
const path=require('node:path');
const crypto=require('node:crypto');
const assert=(condition,message)=>{if(!condition)throw Error(message);};
const hash=bytes=>crypto.createHash('sha256').update(bytes).digest('hex');
// Harness-only resource caps; these are not product or performance budgets.
const MAX_ARTIFACT=16*1024*1024, MAX_NODES=10000, MAX_DEPTH=64, MAX_STRING=1048576, MAX_TEXT=4*1024*1024, MAX_TIMERS=512;
const NAMES=Object.freeze([
  'initial-no-problem',
  'empty-poll-then-valid-presentation',
  'successful-post-does-not-fail',
  'poll-timeout-first-failure',
  'post-timeout-unconfirmed',
  'malformed-json',
  'malformed-gateway',
  'wrong-renderer-kind',
  'unexpected-post-body',
  'event-bound',
  'queue-17-capacity',
  'encoded-action-byte-bound',
  'explicit-stop-first-reason',
  'empty-explicit-stop-remains-stopped'
]);
const exactKeys=(value,keys,where)=>assert(value!==null&&typeof value==='object'&&!Array.isArray(value)&&
  JSON.stringify(Object.keys(value).sort())===JSON.stringify([...keys].sort()),`${where}: missing or extra fields`);
function plainData(value,where,ancestors,realm,budget,depth){
  assert(depth<=MAX_DEPTH&&++budget.nodes<=MAX_NODES,`${where}: payload structural bound`);
  if(typeof value==='string'){budget.chars+=value.length;assert(value.length<=MAX_STRING&&budget.chars<=MAX_TEXT,`${where}: string bound`);return;}
  if(value===null||typeof value==='boolean')return;
  if(typeof value==='number'){assert(Number.isFinite(value)&&!Object.is(value,-0),`${where}: unsupported number`);return;}
  assert(typeof value==='object'&&!ancestors.has(value),`${where}: unsupported or cyclic value`);
  const array=Array.isArray(value),proto=Object.getPrototypeOf(value);
  assert(proto===(array?realm.array:realm.object)||(!array&&proto===null),`${where}: unsupported prototype`);
  assert(Object.getOwnPropertySymbols(value).length===0,`${where}: symbol keys`);
  const desc=Object.getOwnPropertyDescriptors(value);
  const keys=Object.keys(desc).filter(key=>!(array&&key==='length'));
  if(array)assert(keys.length===value.length&&keys.every((key,index)=>key===String(index)),`${where}: sparse/extended array`);
  ancestors.add(value);
  try{for(const key of keys){budget.chars+=key.length;assert(key.length<=MAX_STRING&&budget.chars<=MAX_TEXT&&Object.hasOwn(desc[key],'value')&&desc[key].enumerable,`${where}.${key}: invalid key/accessor/hidden field`);plainData(desc[key].value,`${where}.${key}`,ancestors,realm,budget,depth+1);}}
  finally{ancestors.delete(value);}
}
function readPinned(filename){
  const fd=fs.openSync(filename,fs.constants.O_RDONLY|fs.constants.O_NOFOLLOW);
  try{
    const before=fs.fstatSync(fd,{bigint:true});assert(before.isFile()&&before.size<=BigInt(MAX_ARTIFACT),'artifact must be a bounded regular file');
    const bytes=fs.readFileSync(fd),after=fs.fstatSync(fd,{bigint:true});
    for(const key of ['dev','ino','size','mtimeNs','ctimeNs'])assert(before[key]===after[key],'compiled artifact changed while reading');
    const text=bytes.toString('utf8');assert(Buffer.from(text,'utf8').equals(bytes),'artifact is not exact UTF-8');
    return {text,sha256:hash(bytes)};
  }finally{fs.closeSync(fd);}
}
async function observe(artifact){
  const timers=new Set(),messages=[];let asyncFailure=null,rejectActive=null;
  const schedule=(fn,delay=0,...args)=>{assert(timers.size<MAX_TIMERS&&Number.isFinite(delay)&&delay>=0,'timer bound');let handle;handle=setTimeout(()=>{timers.delete(handle);try{fn(...args);}catch(error){asyncFailure=error;if(rejectActive)rejectActive(error);}},delay);timers.add(handle);return handle;};
  const cancel=handle=>{timers.delete(handle);clearTimeout(handle);};
  try{
    const context=vm.createContext({console:{log(){},warn(){},error(){}},setTimeout:schedule,clearTimeout:cancel});
    const realm=vm.runInContext('({object:Object.prototype,array:Array.prototype})',context);
    new vm.Script(artifact.text,{filename:'UiHttpFailureReplay.js'}).runInContext(context,{timeout:10000});
    const entry=context.Elm?.UiHttpFailureReplay;
    assert(entry&&typeof entry.init==='function','missing exact UiHttpFailureReplay module');
    const app=entry.init({flags:null});
    assert(app.ports?.outgoing&&typeof app.ports.outgoing.subscribe==='function','missing outgoing port');
    await new Promise((resolve,reject)=>{
      rejectActive=reject;
      const deadline=schedule(()=>reject(Error('worker output timeout')),3000);
      app.ports.outgoing.subscribe(payload=>{
        try{
          assert(messages.length===0,'unexpected second worker output');
          plainData(payload,'$',new Set(),realm,{nodes:0,chars:0},0);
          messages.push(JSON.parse(JSON.stringify(payload)));
          if(messages.length===1)schedule(()=>{cancel(deadline);resolve();},25);
        }catch(error){reject(error);}
      });
      if(asyncFailure)reject(asyncFailure);
    });
    assert(!asyncFailure,'asynchronous worker failure');
    assert(messages.length===1,`expected one output within bounded window; got ${messages.length}`);
    const payload=messages[0];exactKeys(payload,['checks'],'output');
    assert(Array.isArray(payload.checks)&&payload.checks.length===14,'expected exactly 14 named results');
    const names=new Set();
    for(const [index,row] of payload.checks.entries()){
      exactKeys(row,['name','passed'],`checks[${index}]`);
      assert(typeof row.name==='string'&&NAMES.includes(row.name)&&!names.has(row.name),`unexpected or duplicate result ${row.name}`);
      assert(typeof row.passed==='boolean',`${row.name}: passed must be boolean`);names.add(row.name);
    }
    assert(names.size===NAMES.length&&NAMES.every(name=>names.has(name)),'missing required named result');
    return {checks:payload.checks,payload,passed:payload.checks.every(row=>row.passed===true)};
  }catch(error){return {checks:[],passed:false,payloads:messages,error:String(error&&error.stack||error)};}
  finally{rejectActive=null;for(const timer of timers)clearTimeout(timer);timers.clear();}
}
async function main(){
  assert(process.argv.length===4&&process.argv.slice(2).every(path.isAbsolute),'expected absolute UiHttpFailureReplay.js and NEW report path');
  const artifact=readPinned(process.argv[2]);
  const result=await observe(artifact);
  const report={schema:1,scope:'compiled UiHttp pure component only; no native, GUI, AT, IME, performance or original acceptance',
    requiredCount:14,outputWindowMs:25,passed:result.passed,
    result:{name:'UiHttpFailureReplay',sha256:artifact.sha256,passed:result.passed,checks:result.checks,...(result.payload?{payload:result.payload}:{}),...(result.payloads?{payloads:result.payloads}:{}),...(result.error?{error:result.error}:{})},
    runnerPathSha256AtReport:readPinned(__filename).sha256,
    sourceReplaySha256Expected:'d3dab516f45f00d3e2f4fad71901e2204718b4f4ec8a0c5eac9661bc47cebc70',
    sourceBinding:'External protected profile must attest complete source closure and executed runner/artifact; self-read and declared hash are not execution provenance',
    originalAccepted:false,nativeAccepted:false};
  const fd=fs.openSync(process.argv[3],fs.constants.O_WRONLY|fs.constants.O_CREAT|fs.constants.O_EXCL|fs.constants.O_NOFOLLOW,0o600);
  try{fs.writeFileSync(fd,JSON.stringify(report,null,2)+'\n');}finally{fs.closeSync(fd);}
  if(!report.passed)process.exitCode=1;
}
main().catch(error=>{process.stderr.write(String(error&&error.stack||error)+'\n');process.exitCode=1;});
