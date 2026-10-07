"""Hold real rapid pending-intent failure and fix sticky original producer scope."""
import hashlib,json,pathlib,resource,shutil,stat,sys
sys.path.insert(0,'/home/hoskinson/window-integration-qa');from qa_launch import require_qa_scope
require_qa_scope();assert resource.getrlimit(resource.RLIMIT_CORE)==(1,1)
r=pathlib.Path('/home/hoskinson/omarchy-windows-parity');parent=r/'implementation/warlock-preview-provider-v133';root=r/'implementation/warlock-preview-provider-v134';sha=lambda p:hashlib.sha256(pathlib.Path(p).read_bytes()).hexdigest();load=lambda p:json.loads(pathlib.Path(p).read_text())
build=next(parent.glob('qa/build-*/report.json'));b=load(build);assert b['passed'] and len(b['commands'])==119 and all(c['exitCode']==0 for c in b['commands'])
for n,h in b['inputs'].items():assert sha(parent/n)==h,n
reports={'build':{'path':str(build),'sha256':sha(build)}}
for version,passed,count,exits in [(147,True,29,13),(148,True,51,18),(149,False,33,13)]:
 native=r/f'implementation/warlock-client-provider-native-v{version}';p=next(native.glob('qa/native-controlled-*/report.json'));d=load(p);pre=load(native/'qa/preflight.json');assert d['passed']==passed and len(d['checks'])==count and len(d['ownedExitCodes'])==exits and d['cleanupPassed']
 for n,h in pre['inputs'].items():assert sha(n)==h,n
 for n,h in d['artifacts'].items():assert sha(p.parent/n)==h,n
 if passed:assert all(c['passed'] for c in d['checks']) and all(c['exitCode']==0 for c in d['ownedExitCodes'])
 else:
  assert 'drained(1)' in d['traceback'] and 'Original six-second fixture observation deadline' in d['error']
  assert [c['exitCode'] for c in d['ownedExitCodes'] if c['name']=='controlled-host']==[1]
  assert all(c['exitCode']==0 for c in d['ownedExitCodes'] if c['name']!='controlled-host')
  log=(p.parent/'private-evidence/controlled-host.log').read_text();states=[json.loads(l.split(': ',1)[1]) for l in log.splitlines() if l.startswith('controlled-native-private-status: ')];last=states[-1];model=last['privatePolicy']['models'][0]['model']
  assert not model['known'] and not model['retiring'] and last['privatePolicy']['realm']['closing'] and not last['privatePolicy']['realm']['closed'] and last['privatePolicy']['realm']['retained']==1 and last['privatePolicy']['visuals']['surface']['lease']=='2'
  assert 'controlled-native-reader-released: epoch=1 originalCloseCalls=1' in log and 'controlled-native-realm-retired:' not in log
 reports['native'+str(version)]={'path':str(p),'sha256':sha(p),'passed':passed}
model=next(parent.glob('qa/controlled-reader-lifetime-model-v4-*/report.json'));q=load(model);assert q['passed'] and q['namedScenarios']==6 and q['invariantSamples']==200
for n,h in q['inputs'].items():assert sha(parent/n)==h,n
for n,h in q['artifacts'].items():assert sha(model.parent/n)==h,n
reports['readerModel']={'path':str(model),'sha256':sha(model)}
coupling=next((r/'docs/warlock-preview/v93').glob('retained-reader-coupling-*/report.json'));c=load(coupling);assert c['passed'] and c['coupledQuintChecks']==8
for n,h in c['inputs'].items():assert sha(n)==h,n
for n,h in c['artifacts'].items():assert sha(coupling.parent/n)==h,n
reports['readerCoupling']={'path':str(coupling),'sha256':sha(coupling)}
scope='GUI133 adds disabled-by-default QA-only real original Native-authorized URI/GIO reader hold/probe/one release, no original runtime policy/issuer/producer changes. Full119/original Native14729/13 normal passes. Later pending popup after detachment observations have already started passes Native14851/18 plus private cleanup: owned original Retiring job/denied held-fresh reads/one reader close/same later GTK popup/fresh same-policy epoch/source pixels/output. Reader Quint6named/200samples and8 coupled stages pass separately; three earlier model syntax/type failures remain held. Actual rapid Native149 uses same source and 10/8/8/10ms input phases; original6s old-epoch drain fails despite actual reader release and original known/retiring jobs becoming empty. Old closing realm retains its subject and never gets detached because producer scheduling depends on the later popup readiness. Host exits1 with original strict retirement guard; all12 other owned processes normal/private cleanup pass. Broad pending-intent/rapid lifecycle is not accepted. Preserve this exact counterexample and every oracle/deadline. Fresh GUI134 fixes only producer scope by preserving sticky closing realm observation/poll stamps independent of new popup intent. No native grant or policy reset/physical gate weakening; installed desktop/drafts untouched.'
common={'schema':1,'owner':'f6779148-8f5d-4bdf-8a0f-044184e486f2','sourceHeld':True,'passed':False,'cpuBuildPassed':True,'fullBuildCommands':119,'actualNormalRouteRegressionPassed':True,'actualDelayedPendingIntentQualified':True,'actualPendingIntentReopenQualified':False,'actualRapidPointerCloseReopenQualified':False,'rapidOriginalDeadlineFailed':True,'privateSessionCleanupPassed':True,'nativeGrantResets':0,'singlePreviewPolicy':True,'readerQuintScenarios':6,'readerInvariantSamples':200,'readerCoupledStages':8,'nativeAcceptance':False,'fullReleaseAccepted':False,'scope':scope,'reports':reports}
for base in [parent,*[r/f'implementation/warlock-client-provider-native-v{v}' for v in [147,148,149]]]:
 files={}
 for p in sorted(base.rglob('*')):
  rel=p.relative_to(base)
  if any(x in {'elm-stuff','mutable-elm-home','elm-home','__pycache__'} for x in rel.parts) and 'toolchain' not in rel.parts:continue
  assert not p.is_symlink(),p
  if p.is_file():files[str(rel)]={'kind':'file','sha256':sha(p),'size':p.stat().st_size,'mode':oct(stat.S_IMODE(p.stat().st_mode))}
 m=base/'component-manifest.json';assert not m.exists();own=dict(common,files=files)
 if base!=parent:
  version=int(base.name.rsplit('v',1)[1]);own.update(passed=version!=149,scope=load(next(base.glob('qa/native-controlled-*/report.json')))['scope'],nativeChecks={147:29,148:51,149:33}[version],normalOwnedExits={147:13,148:18,149:12}[version],actualDelayedPendingIntentQualified=version==148)
 m.write_text(json.dumps(own,indent=2)+'\n');print(base.name,len(files))
out=pathlib.Path(__file__).with_name('component-report133.json');assert not out.exists();out.write_text(json.dumps(common,indent=2)+'\n')
assert not root.exists()
def ignore(path,names):
 if pathlib.Path(path)==parent:return [n for n in names if n in {'component-manifest.json','ANCESTRY.json','__pycache__'}]
 if pathlib.Path(path)==parent/'qa':return [n for n in names if (pathlib.Path(path)/n).is_dir() and n!='toolchain']
 return [n for n in names if n in {'__pycache__','elm-stuff'}]
shutil.copytree(parent,root,ignore=ignore)
p=root/'native/controlled-preview-host.h';s=p.read_text();old='        if(!surface_popup_ready() || !popup_owner || !popup_owner->active || !client_frame_target(surface_snapshot,qa_import_subjects[0],&publication,&lease) || publication!=surface_gate.publication || lease!=surface_gate.lease)publication=lease=0;';assert s.count(old)==1;s=s.replace(old,old.replace('if(!surface_popup_ready()','if(controlled_retiring || !surface_popup_ready()'))
old='        if(subject_present && !surface_popup_ready()) {';assert s.count(old)==1;s=s.replace(old,'        /* Sticky old-realm retirement survives every later popup intent.\n         * Its original detachment facts/receipts must keep progressing; only\n         * strict Native closure can admit that later popup as a fresh realm. */\n        if(subject_present && (controlled_retiring || !surface_popup_ready())) {');p.write_text(s)
(root/'ANCESTRY.json').write_text(json.dumps({'owner':common['owner'],'parent':str(parent),'parentManifestSHA256':sha(parent/'component-manifest.json'),'acceptedFoundation':str(r/'implementation/warlock-preview-provider-v132/component-manifest.json'),'scope':'Fresh GUI134 fixes actual Native149 rapid pending-intent deadlock. Sticky controlled_retiring forces original old-realm poll publication/lease0 and continues required native detachment inventories even when later popup is ready. Native issuer/Elm policy/physical/journal/confirmation/readers/original deadlines unchanged. Same original real retained-reader stimulus and unchanged149 oracle must pass alongside original normal and delayed tests.','nativeAcceptance':False,'fullReleaseAccepted':False},indent=2)+'\n')
sys.path.insert(0,str(r/'implementation/elm-build-loop-v1'));import loop
print(loop.write_checkpoint(r,common['owner'],str(root.relative_to(r)),['PROGRESS heldGUI133 rapid pending-intent failure: Native149 original6s drain deadline despite actual original reader release and jobs physically drained; old realm subject retained because later popup stops original detachment inventory. Failed host1/12 other normal exits/private cleanup, original14729/13 and slower14851/18 pass separately. Reader6named200samples/8coupled stages do not prove producer liveness; failures preserved. Own fresh GUI134 with only sticky retirement producer gates: closing realm poll uses original no-current stamps and detachment inventory continues independent of later popup. Full119 plus original normal, slower and byte-identical rapid149 oracle then delayed regressions/model/coupling required. No reset/Native gate/deadline/oracle change; installed/drafts/foreign preserved.'],'progress',[str((parent/'component-manifest.json').relative_to(r)),str((root/'ANCESTRY.json').relative_to(r)),str(out.relative_to(r))]))
