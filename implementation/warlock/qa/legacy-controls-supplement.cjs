'use strict';
// Fixed reviewed-harness reuse; controlled component evidence, no native authority.
const fs=require('node:fs'),path=require('node:path'),vm=require('node:vm'),crypto=require('node:crypto');
const {isDeepStrictEqual:equal}=require('node:util');
const [mainFile,barFile,popupFile,replayFile,reportFile,sourceRoot]=process.argv.slice(2);
if(process.argv.length!==8)throw Error('Expected fixed4images REPORT.json SOURCE_ROOT');
const hash=x=>crypto.createHash('sha256').update(x).digest('hex');
const budgetPath=path.join(__dirname,'legacy-controls-budget.json');
const harnessPath=path.join(__dirname,'ui-http.cjs');
const budgetBytes=fs.readFileSync(budgetPath),budget=JSON.parse(budgetBytes);
const expectedNames=["retry-positive-original-proposal", "retry-active-exact-dedup", "retry-stale-domain-no-new-post", "retry-foreign-domain-no-new-post", "legacy-foreign-no-current-realm-post", "retry-after-204-reoffers-original", "retry-duplicate-active-still-one", "retry-missing-fails-closed", "retry-extra-fails-closed", "retry-zero-fails-closed", "retry-leading-zero-fails-closed", "retry-overflow-fails-closed", "legacy-missing-fails-closed", "legacy-extra-fails-closed", "legacy-wrapped-fails-closed", "legacy-zero-fails-closed", "legacy-leading-zero-fails-closed", "legacy-overflow-fails-closed", "controller-role-native-preview-retry-rejected", "controller-role-native-preview-retirement-rejected", "bar-role-native-preview-retry-rejected", "bar-role-native-preview-retirement-rejected"];
const anchor="\n(async()=>{try{\n  const campaigns=[roots,exactQueueContract,previewReconciliationTransport,previewDeferredFullQueue,focusRoutes,rendererSeedRoutes,fifo,capacities,failures,eventDuringDelivery,receiptNotAck,pendingQueryHonestControls,seededPendingQueryDom,httpPopupRetainedQueryOnFailure,cancellationPendingControls,betaUsabilityControlsAndLoading];";
const expectedHarness='11ba46628c54b83486af54173849a5868d770c3e462b39907cdd87a5a2b78cc1';
const expectedPrefix='c42f09abe1c5db21fff32df1a1f87391ca119d1ec7209e690b2e20d4bd5adb50';
const expectedSourceKeys=['implementation/warlock/src/UiHttp.elm','implementation/warlock/src/HttpPopup.elm','implementation/warlock/src/HttpMain.elm','implementation/warlock/src/HttpBar.elm','implementation/warlock/qa/UiHttpReplay.elm','implementation/warlock/qa/ui-http.cjs'];
if(budget.schema!==1||budget.cases!==22||budget.assertions!==50||budget.seed!==20261101||budget.seedCount!==1||budget.responseMs!==5000||budget.campaignMs!==60000||budget.overallMs!==180000||!equal(budget.namedCases,expectedNames)||!equal(Object.keys(budget.sourceHashes).sort(),expectedSourceKeys.sort())||path.resolve(sourceRoot)!==budget.sourceRoot)throw Error('fixed supplemental budget/source roster mismatch');
if(hash(fs.readFileSync(__filename))!==budget.driverSha256)throw Error('supplement driver digest mismatch');
const harnessBytes=fs.readFileSync(harnessPath),harnessSource=harnessBytes.toString('utf8');
const offset=harnessSource.indexOf(anchor);
if(hash(harnessBytes)!==expectedHarness||budget.harnessSha256!==expectedHarness||offset<0||offset!==harnessSource.lastIndexOf(anchor))throw Error('reviewed harness digest/unique launch anchor mismatch');
const prefix=harnessSource.slice(0,offset);
if(hash(Buffer.from(prefix))!==expectedPrefix||budget.prefixSha256!==expectedPrefix||Buffer.byteLength(prefix)!==budget.prefixBytes)throw Error('reviewed harness prefix digest/length mismatch');
for(const [name,sha]of Object.entries(budget.sourceHashes))if(hash(fs.readFileSync(path.join(sourceRoot,name)))!==sha)throw Error('supplement source mismatch: '+name);
const selectedImages={main:mainFile,bar:barFile,popup:popupFile,replay:replayFile};
for(const file of Object.values(selectedImages))if(!fs.lstatSync(file).isFile())throw Error('expected regular supplemental image');
const initialImages=Object.fromEntries(Object.entries(selectedImages).map(([k,file])=>[k,hash(fs.readFileSync(file))]));
const trackedTimers=new Set();let api;
const trackedSetTimeout=(fn,ms,...args)=>{const timer=setTimeout(fn,ms,...args);trackedTimers.add(timer);return timer;};
const trackedClearTimeout=timer=>{trackedTimers.delete(timer);clearTimeout(timer);};
function cleanup(){for(const timer of trackedTimers)clearTimeout(timer);trackedTimers.clear();if(api)for(const env of api.environments)env.close();}
const processView={argv:[process.argv[0],harnessPath,mainFile,barFile,popupFile,replayFile,reportFile],exit:code=>{cleanup();process.exit(code);}};
let report,bounded,harness,worker,gateway,walk,check,need;
async function legacyControlSupplement(){
  const binding={lifetime:'1',session:'2',frontend:'3'},receiverEpoch='4';
  const domain={binding,receiverEpoch};
  const env=harness(popupFile,'HttpPopup');await bounded('init',env.flush());
  await env.event(gateway('presentation',{surfaceProtocol:2,publication:'1',lease:'0',mode:'closed',status:'Closed',bar:[],popup:[]}));
  await env.event(gateway('native-preview-grant',{...domain,capacity:1}));
  await env.event(gateway('native-preview-quarantine',domain));
  need('retry-positive-original-proposal',env.posts().length===1&&env.posts()[0].url==='/preview-proposals');
  const original=env.posts()[0].body;
  await env.event(gateway('native-preview-retry',domain));
  check('retry-active-exact-dedup',env.posts().length===1&&Boolean(env.get()));
  await env.event(gateway('native-preview-retry',{binding,receiverEpoch:'5'}));
  check('retry-stale-domain-no-new-post',env.posts().length===1&&Boolean(env.get()));
  await env.event(gateway('native-preview-retry',{binding:{...binding,frontend:'9'},receiverEpoch}));
  check('retry-foreign-domain-no-new-post',env.posts().length===1&&Boolean(env.get()));
  await env.event(gateway('native-preview-retirement',{lifetime:'9',session:'2',frontend:'3'}));
  check('legacy-foreign-no-current-realm-post',env.posts().length===1&&Boolean(env.get()));
  env.posts()[0].respond(204);await env.flush();
  await env.event(gateway('native-preview-retry',domain));
  check('retry-after-204-reoffers-original',env.posts().length===2&&env.posts()[1].url==='/preview-proposals'&&env.posts()[1].body===original);
  await env.event(gateway('native-preview-retry',domain));
  check('retry-duplicate-active-still-one',env.posts().length===2&&Boolean(env.get()));
  env.close();
  const bad=[
    ['retry-missing','native-preview-retry',{binding}],
    ['retry-extra','native-preview-retry',{...domain,extra:true}],
    ['retry-zero','native-preview-retry',{binding,receiverEpoch:'0'}],
    ['retry-leading-zero','native-preview-retry',{binding,receiverEpoch:'01'}],
    ['retry-overflow','native-preview-retry',{binding,receiverEpoch:'18446744073709551616'}],
    ['legacy-missing','native-preview-retirement',{lifetime:'1',session:'2'}],
    ['legacy-extra','native-preview-retirement',{...binding,extra:true}],
    ['legacy-wrapped','native-preview-retirement',domain],
    ['legacy-zero','native-preview-retirement',{...binding,lifetime:'0'}],
    ['legacy-leading-zero','native-preview-retirement',{...binding,session:'02'}],
    ['legacy-overflow','native-preview-retirement',{...binding,frontend:'18446744073709551616'}]
  ];
  for(const [name,kind,payload] of bad){
    const failed=harness(popupFile,'HttpPopup');await failed.flush();
    await failed.event(gateway(kind,payload));
    check(name+'-fails-closed',Boolean(walk(failed.container,n=>n.attributes?.role==='alert'))&&failed.posts().length===0&&!failed.get());
    failed.close();
  }
  for(const renderer of [false,true])for(const kind of ['native-preview-retry','native-preview-retirement']){
    const workerEnv=await worker(renderer);
    await workerEnv.event(gateway(kind,kind.endsWith('retry')?domain:binding));
    check((renderer?'bar-role-':'controller-role-')+kind+'-rejected',Boolean(workerEnv.latest()?.problem)&&workerEnv.latest()?.event?.kind==='lost'&&workerEnv.posts().length===0);
    workerEnv.close();
  }
}

(async()=>{try{
  const factory=new vm.Script('(function(require,process,__filename,setTimeout,clearTimeout){\n'+prefix+'\n;return {report,bounded,harness,worker,gateway,walk,check,need,environments,watchdog,save};})',{filename:harnessPath+'#reviewed-prefix'}).runInThisContext({timeout:2000});
  api=factory(require,processView,harnessPath,trackedSetTimeout,trackedClearTimeout);
  ({report,bounded,harness,worker,gateway,walk,check,need}=api);
  const boundedEvents=env=>{const event=env.event;env.event=value=>bounded('event reply',event.call(env,value),5000);return env;};
  harness=(...args)=>boundedEvents(api.harness(...args));
  worker=async(...args)=>boundedEvents(await api.worker(...args));
  report.seedCount=1;report.acceptanceAuthority=false;report.originalAcceptance=false;
  report.artifactHashes={...initialImages,harness:expectedHarness,driver:budget.driverSha256,budget:hash(budgetBytes),prefix:expectedPrefix};
  report.sourceHashes=budget.sourceHashes;
  report.budgets={responseMs:5000,campaignMs:60000,overallMs:180000};
  await bounded('legacy-controls-supplement',legacyControlSupplement(),60000);
  const missing=expectedNames.filter(name=>report.checks.filter(row=>row.name===name).length!==1);
  for(const [name,file]of Object.entries(selectedImages))if(!fs.lstatSync(file).isFile()||hash(fs.readFileSync(file))!==initialImages[name])throw Error('supplement image changed: '+name);
  for(const [name,sha]of Object.entries(budget.sourceHashes))if(hash(fs.readFileSync(path.join(sourceRoot,name)))!==sha)throw Error('supplement source changed: '+name);
  if(hash(fs.readFileSync(__filename))!==budget.driverSha256||hash(fs.readFileSync(budgetPath))!==hash(budgetBytes)||hash(fs.readFileSync(harnessPath))!==expectedHarness)throw Error('supplement script/budget/harness changed');
  report.terminal={schema:1,complete:true,cases:expectedNames.length,assertions:report.checks.length,expectedAssertions:50,seed:20261101,seedCount:1,namedCases:expectedNames,missing,artifactHashes:report.artifactHashes,sourceHashes:report.sourceHashes,budgets:report.budgets,scope:'controlled HTTP; nonempty legacy retirement state not covered; renderer role uses UiHttpReplay proxy'};
  report.passed=missing.length===0&&expectedNames.length===22&&report.checks.length===50&&report.failures.length===0;
}catch(error){if(!report)report={schema:1,passed:false,acceptanceAuthority:false,originalAcceptance:false,nativeAcceptance:false,guiAcceptance:false,cspExecutionAcceptance:false,releaseAccepted:false,checks:[],failures:[]};report.error=String(error.stack??error);report.terminal={schema:1,complete:false,assertions:report.checks.length};report.passed=false;}
finally{cleanup();fs.writeFileSync(reportFile,JSON.stringify(report,null,2)+'\n');process.exitCode=report.passed?0:1;}})();
