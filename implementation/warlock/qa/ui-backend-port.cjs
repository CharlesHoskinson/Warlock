'use strict';

// Actual compiled Main ports plus the actual production Haskell executable.
// DOM is only an empty text mount: this is deliberately not GUI acceptance.
const fs = require('node:fs');
const path = require('node:path');
const vm = require('node:vm');
const crypto = require('node:crypto');
const {spawnSync} = require('node:child_process');
const {isDeepStrictEqual: equal} = require('node:util');
const [mainFile, manifestFile, qaRoot, reportFile] = process.argv.slice(2);
if (!mainFile || !manifestFile || !qaRoot || !reportFile || process.argv.length !== 6) throw Error('Expected MAIN.js TRUSTED_MANIFEST.json FRESH_QA_ROOT REPORT.json');
const sha = value => crypto.createHash('sha256').update(value).digest('hex');
const report = {schema:1, requirements:['ELM-ARC-003','ELM-DEL-011'], passed:false, nativeAcceptance:false, guiAcceptance:false, releaseAccepted:false, checks:[], failures:[], trace:[], sessions:[], scenarios:[]};
const timers = new Set();
function save() { fs.writeFileSync(reportFile, JSON.stringify(report, null, 2)+'\n'); }
function check(name, passed, witness) {
  const row={name,passed:Boolean(passed)};
  if (!passed) row.witness=witness===undefined?null:witness;
  report.checks.push(row); if (!passed) report.failures.push(row);
}
function requireCheck(name, passed, witness) { check(name,passed,witness); if (!passed) throw Error(name); }
function imagePin(file) { const s=fs.lstatSync(file,{bigint:true}); if (!s.isFile() || s.isSymbolicLink()) throw Error('Nonregular image'); return [String(s.dev),String(s.ino),String(s.size),sha(fs.readFileSync(file))]; }
function directoryPin(file) { const s=fs.lstatSync(file,{bigint:true}); if (!s.isDirectory() || s.isSymbolicLink()) throw Error('Non-directory pin'); return {path:file,device:String(s.dev),inode:String(s.ino)}; }
function privateJSON(file, value) { fs.writeFileSync(file, JSON.stringify(value),{mode:0o600,flag:'wx'}); }
const pause = () => new Promise(resolve => setTimeout(resolve,20));
function later(fn, delay) { const id=setTimeout(()=>{timers.delete(id);fn();},delay); timers.add(id); return id; }
function cancel(id) { clearTimeout(id);timers.delete(id); }

async function main() {
  const manifest=JSON.parse(fs.readFileSync(manifestFile,'utf8'));
  let activeConfig=manifest.config;
  let queuedPresentations=[],queuedConfig=null,queuedConfigKey=null,presentationBatch=0;
  const applicationFrames=[];
  requireCheck('independent actual production executable pin',equal(imagePin(manifest.backend.path),manifest.backend.pin));
  requireCheck('independent selected UI child pin',equal(imagePin(manifest.ui.path),manifest.ui.pin));
  fs.mkdirSync(qaRoot,{mode:0o700});
  report.artifactHashes={main:sha(fs.readFileSync(mainFile)),manifest:sha(fs.readFileSync(manifestFile)),harness:sha(fs.readFileSync(__filename))};
  const mount={nodeType:3,textContent:'',replaceData(_a,_b,value){this.textContent=value;}};
  const document={createTextNode:value=>({nodeType:3,textContent:value}),addEventListener(){},removeEventListener(){}};
  const window={addEventListener(){},removeEventListener(){},requestAnimationFrame:fn=>later(fn,0),cancelAnimationFrame:cancel};
  const sandbox={console,document,window,setTimeout:later,clearTimeout:cancel,requestAnimationFrame:window.requestAnimationFrame,cancelAnimationFrame:cancel};
  vm.createContext(sandbox);
  vm.runInContext(fs.readFileSync(mainFile,'utf8'),sandbox,{timeout:2000});
  const app=sandbox.Elm.Main.init({node:mount,flags:null});
  requireCheck('actual compiled Main exposes exactly the canonical two ports',equal(Object.keys(app.ports).sort(),['incoming','surfaceCommits']),Object.keys(app.ports));
  let phase='controlled-connected-host-precondition';
  const commits=[];
  app.ports.surfaceCommits.subscribe(value=>{
    const copy=JSON.parse(JSON.stringify(value));commits.push(copy);
    report.trace.push({phase,direction:'Main.surfaceCommits',wholeCommit:copy,sha256:sha(JSON.stringify(copy))});
  });
  async function incoming(kind,payload, origin='explicit controlled bridge fixture; no native issuer claim') {
    const wire={bridgeProtocol:1,kind,payload};
    report.trace.push({phase,direction:'Main.incoming',wire,origin,sha256:sha(JSON.stringify(wire))});
    const before=commits.length;app.ports.incoming.send(wire);await pause();return commits.slice(before);
  }
  function frame() { for (let n=commits.length-1;n>=0;n--) if(commits[n].projection?.frame) return commits[n].projection.frame; throw Error('Main did not publish a frame'); }
  function actionEnvelope(id,popup,current=frame()) {
    return {viewProtocol:1,kind:'view-action',scope:{id:'1',generation:'1'},action:{surfaceProtocol:2,kind:'surface-action',surface:popup?'popup':'bar',publication:current.publication,lease:current.lease,id}};
  }
  async function action(id,popup) {
    if(id!=='control:page-next' && id!=='control:page-previous') await flushPresentations();
    const current=frame(), controls=popup?current.popup:current.bar;
    const control=controls.find(x=>x.id===id);
    requireCheck('actual published control enabled: '+id,control?.enabled===true,control);
    const raw=actionEnvelope(id,popup,current);
    const values=await incoming('view-action',raw,'controlled renderer input captured from actual published frame');
    requireCheck('renderer action emits a complete actual Main commit',values.length===1,values);
    return values[0];
  }
  async function search(query,label) {
    await flushPresentations();
    const current=frame();
    requireCheck(label+' actual published search field',current.popup.some(x=>x.id==='control:search' && x.enabled));
    const event={viewProtocol:1,kind:'view-action',scope:{id:'1',generation:'1'},action:{surfaceProtocol:2,kind:'surface-query',surface:'popup',publication:current.publication,lease:current.lease,id:'control:search',query}};
    const output=await incoming('view-action',event,'controlled query captured from actual published search field');
    requireCheck(label+' emits exactly one complete presentation commit',output.length===1 && output[0].requests.length===0,output);
    await exchange(output[0],label,0);
  }
  const binding=manifest.config.binding;
  // These preconditions are explicit bridge fixtures, NOT replies from the
  // application-only service. Retain every full command produced during them.
  await incoming('view-topology',{viewProtocol:2,kind:'view-topology',revision:'1',views:[{id:'1',generation:'1'}],locations:[{scope:{id:'1',generation:'1'},box:[0,0,800,600]}]});
  await incoming('native-event',{protocolVersion:3,kind:'attached',binding});
  await incoming('native-event',{protocolVersion:3,kind:'action-projection',binding,requestId:'1',context:{lifetime:binding.lifetime,epoch:binding.frontend,output:'9007199254741307',revision:'9007199254741407'},scene:{revision:'9007199254741407',focused:null,windows:[]}});
  await incoming('native-event',{protocolVersion:3,kind:'pointer-ownership',ownershipProtocol:1,binding,requestId:'1',serial:'1',state:'idle',owner:null});
  const beforeInvalid=commits.length;
  for (const value of [null,{bridgeProtocol:2,kind:'native-event',payload:{}},{bridgeProtocol:1,kind:'native-event',payload:{},extra:true},{bridgeProtocol:1,kind:'forged-owner',payload:{}}]) { app.ports.incoming.send(value);await pause(); }
  requireCheck('malformed gateway discriminators cannot emit a Main commit',commits.length===beforeInvalid);

  async function executeFrames(rows,label,selectedConfig) {
    requireCheck(label+' fixed complete-frame batch bound',rows.length>0 && rows.length<=16,rows.length);
    const directory=path.join(qaRoot,label);fs.mkdirSync(directory,{mode:0o700});
    const script=path.join(directory,'script.json'), replies=path.join(directory,'replies.json'), configPath=path.join(directory,'startup.json');
    privateJSON(script,{schema:1,frames:rows.map(row=>({wire:row.wire,replies:row.expectedReplies,refused:false}))});
    const ancestors=[];let parent=path.dirname(manifest.ui.path);while(parent!=='/'){ancestors.unshift(directoryPin(parent));parent=path.dirname(parent);}
    // Exactly one original5s deadline for the entire multi-frame conversation.
    const config={...selectedConfig,deadlineMonotonicNs:String(process.hrtime.bigint()+5000000000n),ui:{path:manifest.ui.path,device:manifest.ui.pin[0],inode:manifest.ui.pin[1],size:manifest.ui.pin[2],sha256:manifest.ui.pin[3],arguments:[script,replies],ancestors}};
    privateJSON(configPath,config);
    const result=spawnSync(manifest.backend.path,[configPath],{encoding:'utf8',timeout:12000,maxBuffer:16*1024*1024});
    fs.writeFileSync(path.join(directory,'stdout'),result.stdout||'');fs.writeFileSync(path.join(directory,'stderr'),result.stderr||'');
    const session={label,frames:rows.map(row=>({label:row.label,sequence:row.sequence,sha256:sha(row.wire),bytes:Buffer.byteLength(row.wire)})),exit:result.status,signal:result.signal,error:result.error?String(result.error):null,configHash:sha(fs.readFileSync(configPath)),scriptHash:sha(fs.readFileSync(script))};
    report.sessions.push(session);requireCheck(label+' actual production CLI normal success',result.status===0 && !result.signal && !result.error,session);
    const receipt=JSON.parse(result.stdout.trim());
    session.receipt=receipt;
    requireCheck(label+' actual callback and operation receipt',receipt.passed===true && receipt.cleanup===true && receipt.callbacks===rows.length && receipt.operations===rows.reduce((n,row)=>n+row.wholeCommit.requests.length,0),receipt);
    const strings=JSON.parse(fs.readFileSync(replies,'utf8'));
    requireCheck(label+' exact real reply count',strings.length===rows.reduce((n,row)=>n+row.expectedReplies,0),strings);
    const output=[];
    for(const bytes of strings) {
      const value=JSON.parse(bytes);
      requireCheck(label+' actual server gateway is canonical native-event',equal(Object.keys(value).sort(),['bridgeProtocol','kind','payload']) && value.bridgeProtocol===1 && value.kind==='native-event',value);
      session.replyHashes??=[];session.replyHashes.push(sha(bytes));
      report.trace.push({phase,direction:'production-backend.gateway',bytes,sha256:sha(bytes)});
      const before=commits.length;
      report.trace.push({phase,direction:'Main.incoming',wire:value,origin:'exact actual production gateway bytes; no test wrap/extraction',sha256:sha(bytes)});
      app.ports.incoming.send(value);await pause();output.push(...commits.slice(before));
    }
    return {strings,output};
  }
  async function flushPresentations() {
    if(queuedPresentations.length===0) return;
    const rows=queuedPresentations;
    requireCheck('presentation flush contains only whole presentation frames',rows.every(row=>row.expectedReplies===0 && row.wholeCommit.requests.length===0));
    const result=await executeFrames(rows,'presentation-batch-'+String(presentationBatch++).padStart(3,'0'),queuedConfig);
    requireCheck('presentation flush invents no gateway or GUI ACK',result.strings.length===0 && result.output.length===0);
    queuedPresentations=[];queuedConfig=null;queuedConfigKey=null;
  }
  async function exchange(wholeCommit,label,expectedReplies) {
    // Preserve the complete actual Main value and its serialized bytes. Batching
    // changes only process amortization, never request extraction or replay.
    requireCheck(label+' exact whole outgoing schema',equal(Object.keys(wholeCommit).sort(),['focus','kind','projection','requests','viewProtocol']) && wholeCommit.viewProtocol===1 && wholeCommit.kind==='view-commit',wholeCommit);
    const row={wholeCommit,wire:JSON.stringify(wholeCommit),label,expectedReplies,sequence:applicationFrames.length};
    applicationFrames.push(row);
    if(expectedReplies===0 && wholeCommit.requests.length===0) {
      const configKey=JSON.stringify(activeConfig);
      if(queuedPresentations.length>0 && queuedConfigKey!==configKey) await flushPresentations();
      if(queuedPresentations.length===0) {queuedConfig=JSON.parse(configKey);queuedConfigKey=configKey;}
      queuedPresentations.push(row);
      if(queuedPresentations.length===16) await flushPresentations();
      return {strings:[],output:[]};
    }
    await flushPresentations();
    return executeFrames([row],label,activeConfig);
  }
  phase='actual-application-backend';
  const opening=await action('bar:applications',false);
  requireCheck('actual Applications opener produces one catalog intent',opening.requests.length===1 && opening.requests[0].kind==='catalog-request',opening);
  const response=await exchange(opening,'catalog-read',1);
  const catalog=JSON.parse(response.strings[0]).payload;
  requireCheck('actual backend request and outcome preserve exact binding/request',catalog.protocolVersion===3 && catalog.kind==='application-catalog' && equal(catalog.binding,binding) && catalog.requestId===opening.requests[0].requestId,catalog);
  requireCheck('actual catalog is complete and available',catalog.snapshot?.catalogProtocol===2 && catalog.snapshot.entries.length>=2 && catalog.preferences!==null,catalog);
  requireCheck('same actual Main consumes backend reply and publishes Applications',frame().mode==='applications' && response.output.length>0,frame());
  for(let n=0;n<response.output.length;n++) await exchange(response.output[n],'catalog-presentation-'+n,0);
  const identities=catalog.snapshot.entries.map(x=>x.id);
  const existing=catalog.preferences.identities;
  // Choose the real published pin action; actual store begins empty or the
  // declared initial pins are retained, so no outcome is fabricated here.
  const target=identities.find(id=>!existing.includes(id));
  requireCheck('catalog supplies a fresh pinnable identity',typeof target==='string',identities);
  const pin=await action('pin:'+target,true);
  requireCheck('actual Main proposes one correlated fixed-store write',pin.requests.length===1 && pin.requests[0].kind==='taskbar-pins-write' && equal(pin.requests[0].proposal.identities,[...existing,target]) && pin.requests[0].proposal.revision===catalog.preferences.revision,pin);
  const saved=await exchange(pin,'pin-write',1);
  const outcome=JSON.parse(saved.strings[0]).payload;
  requireCheck('actual Saved retains proposal/request and advances real revision',outcome.kind==='taskbar-pins-outcome' && outcome.status==='Saved' && outcome.requestId===pin.requests[0].requestId && equal(outcome.preferences.identities,[...existing,target]) && BigInt(outcome.preferences.revision)===BigInt(catalog.preferences.revision)+1n,outcome);
  requireCheck('same actual Main emits search focus after matching Saved',saved.output.some(x=>x.focus.includes('launcher-search')),saved.output);
  for(let n=0;n<saved.output.length;n++) await exchange(saved.output[n],'saved-presentation-'+n,0);
  const refresh=await action('control:refresh',true);
  const reloaded=await exchange(refresh,'durable-read-after-restart',1);
  const observed=JSON.parse(reloaded.strings[0]).payload;
  requireCheck('production CLI restart observes exact persisted order',equal(observed.preferences,outcome.preferences),observed);
  for(let n=0;n<reloaded.output.length;n++) await exchange(reloaded.output[n],'reloaded-presentation-'+n,0);
  // Actual production metadata traversal, not a fabricated catalog snapshot.
  // Feed the entire result to the same Main and retain/forward its full output;
  // this catches the empty-request capacity branch as well as response framing.
  const capacityDirectory=path.join(qaRoot,'catalog-2048');fs.mkdirSync(capacityDirectory,{mode:0o700});
  for(let n=1;n<=2048;n++) fs.writeFileSync(path.join(capacityDirectory,'capacity-'+String(n).padStart(4,'0')+'.desktop'),'[Desktop Entry]\nType=Application\nName='+('Catalog capacity '+String(n)).padEnd(80,'x')+'\nExec=/bin/true\n',{mode:0o600,flag:'wx'});
  await flushPresentations();
  activeConfig={...manifest.config,catalogRoots:[directoryPin(capacityDirectory)]};
  const capacityRefresh=await action('control:refresh',true);
  const capacityResponse=await exchange(capacityRefresh,'actual-catalog-2048',1);
  const capacityCatalog=JSON.parse(capacityResponse.strings[0]).payload;
  requireCheck('actual production gateway delivers all2048 catalog entries above64KiB',capacityCatalog.snapshot?.entries.length===2048 && Buffer.byteLength(capacityResponse.strings[0])>65536, {entries:capacityCatalog.snapshot?.entries.length,bytes:Buffer.byteLength(capacityResponse.strings[0])});
  requireCheck('same actual Main consumes full2048 catalog and publishes a complete frame',capacityResponse.output.length>0 && frame().mode==='applications');
  for(let n=0;n<capacityResponse.output.length;n++) {
    const whole=capacityResponse.output[n];
    check('full2048 Main presentation wire capacity observation '+n,Buffer.byteLength(JSON.stringify(whole))<=131072,{bytes:Buffer.byteLength(JSON.stringify(whole)),limit:131072,requests:whole.requests.length});
    await exchange(whole,'capacity-presentation-'+n,0);
  }
  report.capacity={entries:2048,rawGatewayBytes:Buffer.byteLength(capacityResponse.strings[0]),completeMainCommitBytes:capacityResponse.output.map(x=>Buffer.byteLength(JSON.stringify(x)))};
  // Walk every real page; eight is the combined body-control budget, not an
  // assumption that every page contains eight application entries. Pinned
  // management and application actions share the same reachable body.
  const fixed=new Set(['control:search','control:close','control:refresh','control:acknowledge','control:page-previous','control:page-next','control:page-range']);
  const catalogIds=capacityCatalog.snapshot.entries.map(x=>x.id).sort();
  const seenEntries=new Set(),seenBody=new Set(),pages=[];
  const firstPage=frame(),pagingLease=firstPage.lease;
  const staleNext=actionEnvelope('control:page-next',true,firstPage);
  let previousEnd=0,lastPublication=BigInt(firstPage.publication)-1n;
  for(let page=0;page<512;page++) {
    const current=frame();
    const range=current.popup.find(x=>x.id==='control:page-range');
    const previous=current.popup.find(x=>x.id==='control:page-previous');
    const next=current.popup.find(x=>x.id==='control:page-next');
    const bounds=/^Items (\d+)–(\d+) of (\d+)$/.exec(range?.label||'');
    requireCheck('page '+page+' explicit range and navigation controls',bounds!==null && previous!==undefined && next!==undefined,{range,previous,next});
    const [start,end,total]=bounds.slice(1).map(Number);
    const body=current.popup.filter(x=>!fixed.has(x.id));
    requireCheck('page '+page+' bounded reachable body with consecutive truthful range',body.length<=8 && body.length===end-start+1 && start===previousEnd+1 && end<=total && total===2048+3*capacityCatalog.preferences.identities.length+2,{body:body.map(x=>x.id),start,end,total,previousEnd});
    requireCheck('page '+page+' keeps lease and advances publication',current.lease===pagingLease && BigInt(current.publication)>lastPublication,{lease:current.lease,publication:current.publication});
    requireCheck('page '+page+' exact matching-application and pin counts',equal((range.detail.match(/\d+/g)||[]).map(Number),[2048,capacityCatalog.preferences.identities.length]),range.detail);
    requireCheck('page '+page+' truthful previous/next availability',previous.enabled===(start>1) && next.enabled===(end<total),{previous,next,start,end,total});
    for(const control of body) {
      requireCheck('page '+page+' no duplicate or repeated body control '+control.id,!seenBody.has(control.id));
      seenBody.add(control.id);
      if(control.id.startsWith('entry:')) {
        const identity=control.id.slice(6);
        requireCheck('page '+page+' actual catalog identity without duplicate '+identity,catalogIds.includes(identity) && !seenEntries.has(identity));
        seenEntries.add(identity);
      }
    }
    pages.push({page,start,end,total,publication:current.publication,lease:current.lease,body:body.map(x=>x.id)});
    previousEnd=end;lastPublication=BigInt(current.publication);
    if(!next.enabled) break;
    const nextCommit=await action('control:page-next',true);
    requireCheck('page '+page+' navigation emits no domain operation',nextCommit.requests.length===0,nextCommit.requests);
    requireCheck('page '+page+' complete navigation commit obeys wire limit',Buffer.byteLength(JSON.stringify(nextCommit))<=131072,{bytes:Buffer.byteLength(JSON.stringify(nextCommit))});
    await exchange(nextCommit,'page-next-'+page,0);
    if(page===0) {
      const beforeStale=JSON.stringify(frame());
      const staleOutput=await incoming('view-action',staleNext,'deliberately stale previously published page control');
      requireCheck('stale page publication is inert',staleOutput.length===0 && JSON.stringify(frame())===beforeStale,staleOutput);
    }
  }
  requireCheck('pagination reaches every full-catalog identity exactly once',seenEntries.size===2048 && equal([...seenEntries].sort(),catalogIds),{observed:seenEntries.size,expected:2048});
  requireCheck('pagination reaches real last page without truncating body',pages.length>1 && previousEnd===pages[0].total && pages.length===Math.ceil(pages[0].total/8),{pages:pages.length,previousEnd,total:pages[0]?.total});
  const lastRange=pages[pages.length-1];
  const back=await action('control:page-previous',true);
  requireCheck('previous-page navigation has zero domain operations',back.requests.length===0);
  await exchange(back,'page-previous-from-last',0);
  const previousRange=frame().popup.find(x=>x.id==='control:page-range');
  requireCheck('previous-page navigation reverses exact body window',previousRange?.label.startsWith('Items '+(lastRange.start-8)+'–'),previousRange);
  for(const index of [0,capacityCatalog.snapshot.entries.length-1]) {
    const selected=capacityCatalog.snapshot.entries[index];
    await search(selected.name,'search-full-catalog-'+index);
    const result=frame(),entries=result.popup.filter(x=>x.id.startsWith('entry:')).map(x=>x.id.slice(6));
    requireCheck('search '+index+' retains full catalog beyond previous page',equal(entries,[selected.id]),{selected:selected.id,entries});
    // A one-page result has no navigation controls; it is still page zero.
    requireCheck('search '+index+' resets page and retains exact query',result.popup.find(x=>x.id==='control:page-previous')?.enabled!==true && result.popup.find(x=>x.id==='control:search')?.label===selected.name && result.popup.filter(x=>!fixed.has(x.id)).length<=8,result);
    await search('','clear-query-'+index);
    requireCheck('clearing search restores first full-catalog page',frame().popup.find(x=>x.id==='control:page-range')?.label.startsWith('Items 1–') && frame().popup.find(x=>x.id==='control:page-next')?.enabled===true,frame());
  }
  report.capacity.pages=pages;
  report.capacity.reachableEntries=[...seenEntries].sort();
  report.capacity.reachableBody=seenBody.size;

  // Separate trusted physical fixture at the allowed metadata/pin boundary.
  // These are real files consumed by the same production scanner/store; no
  // catalog or pin outcome is fabricated in the JS host bridge.
  const maximumDirectory=path.join(qaRoot,'catalog-maximum-metadata');
  const maximumPins=path.join(qaRoot,'pins-maximum-metadata');
  fs.mkdirSync(maximumDirectory,{mode:0o700});fs.mkdirSync(maximumPins,{mode:0o700});
  const maximumIds=[];
  for(let n=1;n<=32;n++) {
    const suffix=String(n).padStart(4,'0'),identity='maximum-'+suffix;
    maximumIds.push(identity);
    fs.writeFileSync(path.join(maximumDirectory,identity+'.desktop'),'[Desktop Entry]\nType=Application\nName='+(String.fromCodePoint(0x4e00+n)+'界'.repeat(511))+'\nExec=/bin/true\n',{mode:0o600,flag:'wx'});
  }
  privateJSON(path.join(maximumPins,'taskbar.json'),{schema:1,revision:'1000',identities:maximumIds});
  await flushPresentations();
  activeConfig={...manifest.config,catalogRoots:[directoryPin(maximumDirectory)],pinsRoot:directoryPin(maximumPins)};
  report.trace.push({phase,direction:'explicit-trusted-startup-fixture',purpose:'32 actual desktop files with512 UTF16-unit BMP names and fixed private32-pin file',catalogRoot:activeConfig.catalogRoots[0],pinsRoot:activeConfig.pinsRoot,pinFileSHA256:sha(fs.readFileSync(path.join(maximumPins,'taskbar.json')))});
  const maximumRefresh=await action('control:refresh',true);
  const maximumResponse=await exchange(maximumRefresh,'actual-maximum-metadata',1);
  const maximumCatalog=JSON.parse(maximumResponse.strings[0]).payload;
  requireCheck('actual maximum metadata catalog retains full512-unit Unicode names',maximumCatalog.snapshot?.entries.length===32 && maximumCatalog.snapshot.entries.every(x=>x.name.length===512 && Buffer.byteLength(x.name)===1536 && x.name.slice(1)==='界'.repeat(511)) && equal(maximumCatalog.snapshot.entries.map(x=>x.id).sort(),maximumIds),{entries:maximumCatalog.snapshot?.entries.length});
  requireCheck('actual maximum metadata read retains real32-pin revision1000',equal(maximumCatalog.preferences,{revision:'1000',identities:maximumIds}),maximumCatalog.preferences);
  requireCheck('maximum metadata triggers explicit compact presentation outcome',frame().status.includes('Compact presentation') && frame().bar.some(x=>x.id==='bar:pins-summary' && x.label==='32 pinned applications'),frame());
  requireCheck('maximum metadata emits complete compact projection',maximumResponse.output.length>0);
  for(let n=0;n<maximumResponse.output.length;n++) {
    requireCheck('maximum metadata complete initial commit stays within profile '+n,Buffer.byteLength(JSON.stringify(maximumResponse.output[n]))<=131072,{bytes:Buffer.byteLength(JSON.stringify(maximumResponse.output[n]))});
    await exchange(maximumResponse.output[n],'maximum-presentation-'+n,0);
  }
  const maximumSeen=new Set(),maximumEntries=new Set(),maximumManagement=new Set(),maximumPages=[];
  const maximumLease=frame().lease;
  let maximumEnd=0;
  for(let page=0;page<512;page++) {
    const current=frame(),body=current.popup.filter(x=>!fixed.has(x.id));
    const range=current.popup.find(x=>x.id==='control:page-range');
    const previous=current.popup.find(x=>x.id==='control:page-previous');
    const next=current.popup.find(x=>x.id==='control:page-next');
    const bounds=/^Items (\d+)–(\d+) of (\d+)$/.exec(range?.label||'');
    requireCheck('compact page '+page+' truthful one-row range and original full action count',bounds!==null && body.length===1 && Number(bounds[1])===maximumEnd+1 && bounds[1]===bounds[2] && Number(bounds[3])===129,{range,body:body.map(x=>x.id)});
    const end=Number(bounds[2]);
    requireCheck('compact page '+page+' explicit notice,full counts,stable lease and navigation',current.status.includes('Compact presentation') && current.lease===maximumLease && equal((range.detail.match(/\d+/g)||[]).map(Number),[32,32]) && previous?.enabled===(end>1) && next?.enabled===(end<129),{status:current.status,range,previous,next});
    const control=body[0];
    requireCheck('compact page '+page+' retains each exact action identity once',!maximumSeen.has(control.id),control.id);maximumSeen.add(control.id);
    if(control.id.startsWith('entry:')) {
      const identity=control.id.slice(6),entry=maximumCatalog.snapshot.entries.find(x=>x.id===identity);
      requireCheck('compact page '+page+' retains full application name in accessible label',entry!==undefined && control.ariaLabel===entry.name && control.label.length<=512,{identity,ariaLength:control.ariaLabel.length,labelLength:control.label.length});
      maximumEntries.add(identity);
    }
    if(/^(unpin:|pin-left:|pin-right:)/.test(control.id)) {
      const identity=control.id.slice(control.id.indexOf(':')+1),entry=maximumCatalog.snapshot.entries.find(x=>x.id===identity);
      requireCheck('compact page '+page+' retains full pin name in accessible label',entry!==undefined && control.ariaLabel===entry.name && control.label.length<=512,{identity,ariaLength:control.ariaLabel.length,labelLength:control.label.length});
      maximumManagement.add(control.id);
    }
    maximumPages.push({page,range:range.label,body:control.id,publication:current.publication,lease:current.lease});maximumEnd=end;
    if(!next.enabled) break;
    const nextCommit=await action('control:page-next',true);
    requireCheck('compact page '+page+' complete commit bounded and no domain operation',nextCommit.requests.length===0 && Buffer.byteLength(JSON.stringify(nextCommit))<=131072,{bytes:Buffer.byteLength(JSON.stringify(nextCommit))});
    await exchange(nextCommit,'compact-page-next-'+page,0);
  }
  const expectedManagement=maximumIds.flatMap(id=>['unpin:'+id,'pin-left:'+id,'pin-right:'+id]).sort();
  requireCheck('compact presentation retains all32 full catalog application actions',equal([...maximumEntries].sort(),maximumIds),[...maximumEntries]);
  requireCheck('compact presentation retains all96 pin management actions',equal([...maximumManagement].sort(),expectedManagement),[...maximumManagement]);
  requireCheck('compact presentation reaches every one-row page without dropped tail',maximumPages.length===129 && maximumEnd===129 && maximumSeen.size===129,{pages:maximumPages.length,end:maximumEnd,actions:maximumSeen.size});
  const maximumSearchName=maximumCatalog.snapshot.entries[31].name;
  await flushPresentations();
  const beforeLongQuery=JSON.stringify(frame()),longQueryFrame=frame();
  const longQuery=await incoming('view-action',{viewProtocol:1,kind:'view-action',scope:{id:'1',generation:'1'},action:{surfaceProtocol:2,kind:'surface-query',surface:'popup',publication:longQueryFrame.publication,lease:longQueryFrame.lease,id:'control:search',query:maximumSearchName}},'deliberately over256-unit query; full catalog metadata is valid but input limit is unchanged');
  requireCheck('compact over256-unit search is inert and preserves current page',longQuery.length===0 && JSON.stringify(frame())===beforeLongQuery,longQuery);
  const maximumSearchPrefix=maximumSearchName.slice(0,1);
  await search(maximumSearchPrefix,'compact-full-metadata-search');
  const searched=frame(),searchedRange=searched.popup.find(x=>x.id==='control:page-range');
  requireCheck('compact valid prefix searches retained512-unit metadata and resets page',searched.popup.find(x=>x.id==='control:search')?.label===maximumSearchPrefix && searchedRange?.label==='Items 1–1 of 98' && equal((searchedRange.detail.match(/\d+/g)||[]).map(Number),[1,32]) && searched.popup.filter(x=>!fixed.has(x.id)).length===1 && searched.status.includes('Compact presentation'),{range:searchedRange,queryLength:searched.popup.find(x=>x.id==='control:search')?.label.length});
  await search('','compact-clear-query');
  requireCheck('compact clear query keeps explicit compact mode and restores all actions',frame().status.includes('Compact presentation') && frame().popup.find(x=>x.id==='control:page-range')?.label==='Items 1–1 of 129',frame());
  report.maximumMetadata={sourceFallback:'OutputController.boundedPresentation → Desktop.PresentationCapacity → Surface compact bar and one-row Applications pages',catalogEntries:32,nameUTF16Units:512,pinCount:32,pinRevision:'1000',rawGatewayBytes:Buffer.byteLength(maximumResponse.strings[0]),initialCommitBytes:maximumResponse.output.map(x=>Buffer.byteLength(JSON.stringify(x))),pages:maximumPages,reachableEntries:[...maximumEntries].sort(),reachablePinManagement:[...maximumManagement].sort()};
  await flushPresentations();
  const actualHashes=report.trace.filter(row=>row.phase==='actual-application-backend' && row.direction==='Main.surfaceCommits').map(row=>row.sha256);
  const offeredHashes=applicationFrames.map(row=>sha(row.wire));
  const executedHashes=report.sessions.flatMap(session=>session.frames.map(row=>row.sha256));
  requireCheck('every complete application commit offered once in original order',equal(actualHashes,offeredHashes),{actual:actualHashes.length,offered:offeredHashes.length});
  requireCheck('every complete application commit actually executed once in original order',queuedPresentations.length===0 && equal(offeredHashes,executedHashes),{offered:offeredHashes.length,executed:executedHashes.length});
  report.completeFrameCustody={frameCount:offeredHashes.length,executedFrameCount:executedHashes.length,presentationBatchLimit:16,presentationBatches:presentationBatch,originalSessionDeadlineNs:'5000000000',wholeFrameSHA256:offeredHashes,allActualMainFramesExecutedInOrder:true};
  report.scenarios.push({requirement:'ELM-ARC-003',scenario:'architecture-003',intentSHA256:sha(JSON.stringify(opening)),outcomeSHA256:sha(response.strings[0]),nativeAcceptance:false});
  requireCheck('backend and selected client pins unchanged',equal(imagePin(manifest.backend.path),manifest.backend.pin) && equal(imagePin(manifest.ui.path),manifest.ui.pin));
  report.passed=report.failures.length===0;
}
main().catch(error=>{report.error=String(error.stack||error);report.passed=false;}).finally(()=>{for(const id of timers)clearTimeout(id);save();console.log(JSON.stringify({passed:report.passed,checks:report.checks.length,failures:report.failures.length,report:reportFile}));process.exitCode=report.passed?0:1;});
