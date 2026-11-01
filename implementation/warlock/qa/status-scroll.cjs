'use strict';
// Actual Bar.step and opaque StatusScroll; no physical DOM/input claim.
const fs=require('node:fs'),path=require('node:path'),crypto=require('node:crypto');
const [file,output]=process.argv.slice(2);if(process.argv.length!==4)throw Error('usage: node status-scroll.cjs REPLAY.js REPORT.json');
const hash=p=>crypto.createHash('sha256').update(fs.readFileSync(p)).digest('hex');
const report={schema:1,seed:20261101,checks:[],failures:[],hashes:{replay:hash(file),harness:hash(__filename)},nativeAcceptance:false,guiAcceptance:false};
let app,waiting;
function check(name,ok,detail){const row={name,passed:!!ok};if(!ok)row.detail=detail;report.checks.push(row);if(!ok)report.failures.push(row);}
function send(kind,value,extra={}){const response=new Promise((resolve,reject)=>{const timeout=setTimeout(()=>{waiting=null;reject(Error('missing output '+kind));},2000);waiting=x=>{clearTimeout(timeout);waiting=null;resolve(x);};});app.ports.incoming.send({kind,...(value===undefined?{}:{value}),...extra});return response;}
const prefix='warlock-bar-status-scroll-';
function frame(publication,status,domId='app-control'){return {surfaceProtocol:2,publication,lease:'0',mode:'closed',status,bar:[{id:'bar:applications',domId,label:'Applications',ariaLabel:'Applications',detail:'',enabled:true}],popup:[]};}
(async()=>{try{app=require(path.resolve(file)).Elm.StatusScrollReplay.init();app.ports.outgoing.subscribe(x=>{if(waiting)waiting(x)});
for(let seed=0;seed<32;seed++){
 const base=9007199254741001n+BigInt(seed)*5n,p=String(base),next=String(base+1n),earlier=String(base-1n);
 await send('reset');let r=await send('present',frame(p,'Restore unconfirmed'));
 check('initial seed without reset '+seed,r.publication===p&&r.epoch==='1'&&r.domId===prefix+'1'&&r.effects.length===0,r);
 r=await send('present',frame(next,'Restore unconfirmed'));check('same text retains id and no reset '+seed,r.epoch==='1'&&r.domId===prefix+'1'&&r.effects.length===0,r);
 r=await send('present',frame(earlier,'Restore pending'));check('stale frame cannot alter epoch '+seed,r.publication===next&&r.epoch==='1'&&r.effects.length===0,r);
 const a={surfaceProtocol:2,kind:'surface-action',surface:'bar',publication:next,lease:'0',id:'bar:applications'};
 r=await send('action',a);check('current action dispatch '+seed,r.effects.length===1&&r.effects[0].kind==='dispatch',r);
 r=await send('action',{...a,publication:p});check('stale action rejected '+seed,r.effects.length===0,r);
 r=await send('present',frame(String(base+2n),'Restore pending'));const oldTask=r.effects[0];check('changed text resets fresh identity '+seed,r.epoch==='2'&&r.domId===prefix+'2'&&oldTask?.kind==='reset'&&oldTask.target===r.domId,r);
 r=await send('present',frame(String(base+3n),'Restore done'));check('queued old target distinct from new '+seed,r.epoch==='3'&&r.domId===prefix+'3'&&r.effects[0]?.target!==oldTask?.target,r);
 r=await send('settled');check('late viewport completion has no dispatch '+seed,r.epoch==='3'&&r.effects.length===0,r);
 r=await send('present',{...frame(String(base+4n),'Invalid'),surfaceProtocol:9});check('invalid clears presentation keeps epoch '+seed,r.status===null&&r.domId===null&&r.epoch==='3'&&r.effects.length===0,r);
 }
 const max='18446744073709551615',near='18446744073709551614';
 await send('reset',undefined,{floor:near});let r=await send('present',frame('1','one'));check('max uint64 initial id exact',r.epoch===max&&r.domId===prefix+max&&r.effects.length===0,r);
 r=await send('present',frame('2','two'));check('exhaustion withdraws id without reuse',r.exhausted&&r.epoch===null&&r.domId===null&&r.effects.length===0,r);
 r=await send('present',frame('3','three'));check('exhaustion sticky',r.exhausted&&r.epoch===null&&r.domId===null&&r.effects.length===0,r);
 await send('reset');await send('present',frame('1','one'));r=await send('present',frame('2','two'));const deferred=r.effects[0].target;
 r=await send('present',frame('3','three',deferred));check('old queued target cannot address later control',!r.controlIds.includes(deferred),{deferred,result:r});
 await send('reset');await send('present',frame('1','one'));r=await send('present',frame('2','two'));const sameDeferred=r.effects[0].target;
 r=await send('present',frame('3','two',sameDeferred));check('same status queued target cannot address colliding control',!r.controlIds.includes(sameDeferred),{deferred:sameDeferred,result:r});
 await send('reset');
 const rawA=prefix+'2', row=(id,domId)=>({id,domId,label:id,ariaLabel:id,detail:'',enabled:true});
 r=await send('present',{...frame('1','one'),bar:[row('a',rawA),row('normal','normal-id')]});
 const mappedA=r.controlIds[0];check('normal control id unchanged',r.controlIds[1]==='normal-id',r);
 r=await send('present',{...frame('2','one'),bar:[row('a',rawA),row('b',mappedA),row('normal','normal-id')]});
 check('reserved mapping stable when new raw control equals old mapping',r.controlIds[0]===mappedA&&new Set(r.controlIds).size===3&&r.controlIds[2]==='normal-id',r);
 const mappedB=r.controlIds[1];r=await send('present',{...frame('3','one'),bar:[row('a',rawA),row('b',mappedA),row('c',mappedB),row('normal','normal-id')]});
 check('repeated escape mappings remain stable and distinct',r.controlIds[0]===mappedA&&r.controlIds[1]===mappedB&&new Set(r.controlIds).size===4&&r.controlIds[3]==='normal-id',r);
 await send('reset');r=await send('present',frame('1','one',prefix+'1'));check('reserved first control id mapped away',r.epoch==='1'&&r.domId===prefix+'1'&&!r.controlIds.includes(r.domId)&&r.effects.length===0,r);
 r=await send('present',frame('2','two',prefix+'2'));check('reserved changed control id mapped away',r.epoch==='2'&&r.effects[0]?.target===prefix+'2'&&!r.controlIds.includes(r.effects[0].target),r);
}catch(e){report.failures.push({name:'harness exception',message:String(e.stack||e)});}report.passed=report.failures.length===0;fs.writeFileSync(output,JSON.stringify(report,null,2)+'\n');if(!report.passed)process.exitCode=1;})();
