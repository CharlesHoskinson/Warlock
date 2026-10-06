"""Fresh test-history correction after original C paths and models pass."""
import hashlib,json,pathlib,resource,shutil,stat,sys
sys.path.insert(0,'/home/hoskinson/window-integration-qa');from qa_launch import require_qa_scope
require_qa_scope();assert resource.getrlimit(resource.RLIMIT_CORE)==(1,1)
r=pathlib.Path('/home/hoskinson/omarchy-windows-parity');p=r/'implementation/warlock-preview-provider-v69';t=r/'implementation/warlock-preview-provider-v70';sha=lambda f:hashlib.sha256(f.read_bytes()).hexdigest()
bp=next(p.glob('qa/build-*/report.json'));assert json.loads(bp.read_text())['passed']
fp=next(p.glob('qa/resume-check-*/report.json'));failed=json.loads(fp.read_text());assert not failed['passed'] and 'request' in failed['error'] and [x['exitCode'] for x in failed['commands'] if x['name'] in ['normal','resume-expire','replace-receiver']]==[0,0,0]
reports={}
for key,pattern in [('resumeModelReport','qa/resume-model-check-*/report.json'),('modelReport','qa/check-*/report.json'),('deliveryModelReport','qa/delivery-check-*/report.json')]:
 f=next(p.glob(pattern));assert json.loads(f.read_text())['passed'];reports[key]=str(f)
files={}
for f in sorted(p.rglob('*')):
 rel=f.relative_to(p)
 if any(part in {'elm-stuff','mutable-elm-home','__pycache__'} for part in rel.parts):continue
 assert not f.is_symlink(),f
 if f.is_file():files[str(rel)]={'sha256':sha(f),'size':f.stat().st_size,'mode':oct(stat.S_IMODE(f.stat().st_mode)),'kind':'file'}
m=p/'component-manifest.json';assert not m.exists();m.write_text(json.dumps({'owner':'f6779148-8f5d-4bdf-8a0f-044184e486f2','passed':False,'sourceHeld':True,'evidenceIntegrityPassed':True,'buildReport':str(bp),**reports,'files':files,'scope':'Full94 production, resumed native C normal/expired/receiver cases, resume8/584states/3mutants, demand10 and delivery6 pass. Rejected resume frontend replay incorrectly starts fresh Elm at nativefloor2, causing actual Acquire1 mismatch with actual issued2. Preserve failure; fresh70 adds actual original seed/request/proof replay to same immutable Elm state before current resume. No production or expectation identity changes.','nativeAcceptance':False,'fullReleaseAccepted':False},indent=2)+'\n')
assert not t.exists();shutil.copytree(p,t,ignore=shutil.ignore_patterns('build-*','*check-*','component-manifest.json','elm-stuff','mutable-elm-home','__pycache__','ANCESTRY.json'))
f=t/'native/resume-enrollment-test.cpp';s=f.read_text()
old='"Original resume C source");g_free(events);';new='"Original resume C source");const std::string originalRegistration(events);g_free(events);';assert s.count(old)==1;s=s.replace(old,new)
old='auto proof=endpoint.native([&](auto& b){return b.producerRefused(entry,job);});Wire ack;';new='auto proof=endpoint.native([&](auto& b){return b.producerRefused(entry,job);});char* visible=nullptr;check(warlock_preview_bootstrap_pending(bootstrap,popup,&visible,&error) && visible && !error,"Actual original proof discovery");std::string retainedProofs(visible);g_free(visible);Wire ack;';assert s.count(old)==1;s=s.replace(old,new)
old='"Actual original final proof and exact C ACK");};';new='"Actual original final proof and exact C ACK");return retainedProofs;};';assert s.count(old)==1;s=s.replace(old,new)
old='settle(1);enroll(23);';new='const auto originalReceipts=settle(1);enroll(23);';assert s.count(old)==1;s=s.replace(old,new)
old='std::cout<<"{\\"registration\\":"<<registration';new='Wire originalWire;std::cout<<"{\\"originalRegistration\\":"<<originalRegistration<<",\\"originalReceipts\\":"<<originalReceipts<<",\\"originalJob\\":"<<originalWire.job(prior).finish()<<",\\"registration\\":"<<registration';assert s.count(old)==1;s=s.replace(old,new);f.write_text(s)
f=t/'qa/resume-enrollment-replay.js';s=f.read_text();s=s.replace("publication:'2',lease:'2'","publication:'1',lease:'1'",1)
marker='  const terminalProof=fixture.receipts.at(-1);';assert s.count(marker)==1
added='''  let original=await send('native',fixture.originalRegistration[0]);
  check(original.models[0].model.nextRequest==='1','Same Elm owner begins with actual original native request');
  original=await send('native',fixture.originalRegistration[1]);
  assert.deepEqual(original.commands.flatMap(row=>row.commands),[{kind:'acquire',job:fixture.originalJob}]);checks++;
  const originalProof=fixture.originalReceipts.at(-1);
  original=await send('native',originalProof);
  assert.deepEqual(original.commands.flatMap(row=>row.commands),[{kind:'acknowledge',job:fixture.originalJob,sequence:originalProof.event.sequence}]);checks++;
  check(original.models[0].model.known.length===0 && original.models[0].model.nextRequest==='2','Actual original terminal proof settles history while retaining next request2');
  await send('presentation',{surfaceProtocol:2,publication:'2',lease:'2',mode:'picker',status:'',bar:[],popup:[{id:fixture.identity,domId:'fixture-rejected',label:'Fixture',ariaLabel:'Fixture',detail:'',enabled:true}]});
'''
s=s.replace(marker,added+marker);f.write_text(s)
f=t/'qa/resume-enrollment-check.py';s=f.read_text();assert s.count("elmEvidence['checks']==11")==1;f.write_text(s.replace("elmEvidence['checks']==11","elmEvidence['checks']==15"))
(t/'ANCESTRY.json').write_text(json.dumps({'owner':'f6779148-8f5d-4bdf-8a0f-044184e486f2','parent':str(p),'parentManifestSHA256':sha(m),'purpose':'Fixture exposes original actual C seed/request/refusedproof; same optimized Elm state retains its request2 history. No fake request identity, no altered expected resumed job and no production change. Parent69 model584states and originaldemand/delivery qualify unchanged production.','nativeAcceptance':False,'fullReleaseAccepted':False},indent=2)+'\n')
sys.path.insert(0,str(r/'implementation/elm-build-loop-v1'));import loop
e=loop.write_checkpoint(r,'f6779148-8f5d-4bdf-8a0f-044184e486f2',str(t.relative_to(r)),['PROGRESS held69 full94/C normal-expiry-epoch and resume8/584states3mutants/demand10/delivery6 pass. Failed new Elm fixture lackedoriginalrequest/proofhistory. Fresh70 corrects onlyfixture, preservingactualnativejob2 andoriginalproof inoneElmstate. ActualGUI/nativequalification follows; alloriginalfullreleasegatesactive.'], 'progress',[str(m.relative_to(r)),*reports.values()]);print(json.dumps({'held':str(m),'source':str(t),'checkpoint':str(e)}))
