"""Hold exact same-policy native icon lock bitmap evidence and retained failures."""
import hashlib,json,resource,stat,sys
from pathlib import Path
sys.path.insert(0,'/home/hoskinson/window-integration-qa')
from qa_launch import require_qa_scope
scope=require_qa_scope();assert resource.getrlimit(resource.RLIMIT_CORE)==(1,1)
REPO=Path('/home/hoskinson/omarchy-windows-parity');OUT=Path(__file__).parent
sha=lambda p:hashlib.sha256(p.read_bytes()).hexdigest()
def proof(p,root=None):
 d=json.loads(p.read_text())
 for rel,h in d.get('inputs',{}).items():
  q=Path(rel);q=q if q.is_absolute() else root/q;assert sha(q)==h,(p,q)
 for rel,h in d.get('artifacts',{}).items():assert sha(p.parent/rel)==h,(p,rel)
 return d
def hold(root):
 p=root/'component-manifest.json'
 if not p.exists():
  files={}
  for f in sorted(root.rglob('*')):
   rel=f.relative_to(root)
   if any(x in {'__pycache__','elm-stuff','mutable-elm-home'} for x in rel.parts):continue
   assert not f.is_symlink(),f
   if f.is_file():files[str(rel)]={'kind':'file','sha256':sha(f),'size':f.stat().st_size,'mode':oct(stat.S_IMODE(f.stat().st_mode))}
  p.write_text(json.dumps({'schema':1,'owner':'f6779148-8f5d-4bdf-8a0f-044184e486f2','sourceHeld':True,'evidenceIntegrityPassed':True,'files':files,'nativeAcceptance':False,'fullReleaseAccepted':False},indent=2)+'\n')
 d=json.loads(p.read_text());assert d.get('passed') or (d.get('sourceHeld') and d.get('evidenceIntegrityPassed'))
 for rel,row in d['files'].items():assert sha(root/rel)==row['sha256'] and (root/rel).stat().st_size==row['size'],rel
 return {'path':str(p.relative_to(REPO)),'sha256':sha(p),'files':len(d['files'])}
roots=[];evidence=[]
for version in [44,47]:
 root=REPO/f'implementation/warlock-preview-provider-v{version}';p=next(root.glob('qa/build-*/report.json'));d=proof(p,root);assert not d['passed'];roots.append(root);evidence.append(p)
for version in [45,46,48,49,50]:
 root=REPO/f'implementation/warlock-preview-provider-v{version}';gm=json.loads((root/'component-manifest.json').read_text());b=proof(Path(gm['buildReport']),root);m=proof(Path(gm['modelReport']),root);mm=proof(Path(gm['metadataModelReport']),root)
 assert b['passed'] and len(b['commands'])==82 and all(x['exitCode']==0 for x in b['commands'])
 assert m['passed'] and m['compiledChecks']==36 and m['namedScenarios']==10 and len(m['coupledTraces'])==22 and sum(x['statesCompared'] for x in m['coupledTraces'])==564 and m['unsafeMutantsDetected']==3
 assert gm['evidence']['metadata-privacy-replay']['checks']==82 and gm['evidence']['metadata-icon-physical-tests']['checks']==74
 assert mm['passed'] and mm['namedScenarios']==8 and mm['invariantSamples']==100 and len(mm['coupledTraces'])==16 and mm['statesCompared']==210 and mm['compiledBuild']=={'path':gm['buildReport'],'sha256':sha(Path(gm['buildReport']))}
 roots.append(root);evidence.extend([Path(gm['buildReport']),Path(gm['modelReport']),Path(gm['metadataModelReport'])])
for version in [94,95,96]:
 root=REPO/f'implementation/warlock-client-provider-native-v{version}';p=next(root.glob('qa/native-*/report.json'));d=proof(p);assert not d['passed'] and d['cleanupPassed'] and 'concealed=wait' in d['traceback']
 assert any(x['name']=='iconLockHeldAndNewActualEndpointDeniedBeforePolicy' and x['passed'] for x in d['checks'])
 roots.append(root);evidence.extend([p,root/'qa/preflight.json',next(root.glob('qa/prepare-*/report.json'))])
native=REPO/'implementation/warlock-client-provider-native-v97';prepPath=next(native.glob('qa/prepare-*/report.json'));prep=proof(prepPath);assert prep['passed'];pre=proof(native/'qa/preflight.json');np=next(native.glob('qa/native-*/report.json'));n=proof(np)
assert n['passed'] and n['cleanupPassed'] and len(n['checks'])>2372 and all(x['passed'] for x in n['checks']) and all(x['exitCode']==0 for x in n['ownedExitCodes']) and n['pair']==pre['pair']
required=['allOriginal1783OrderedAssertionsRetained','allPriorNative93StableOrderedAssertionsRetained','iconLockHeldAndNewActualEndpointDeniedBeforePolicy','iconLockActualElmConcealedBeforeProducerRetired','iconLockActualWebKitExcludesOldPreviewAndIconPixels','iconLockOriginalControllerCommitsBoundedAndFlushedOnce','iconLockSameWebKitCarrierRetiresAfterRealPopupDestruction','iconLockSeparatePhysicalIconRetirement','iconLockBitmapHasActualOpaqueSurfaceAndText']
assert all(any(x['name']==name and x['passed'] for x in n['checks']) for name in required)
f=n['iconLockEvidence'];assert f['actualNativeLock'] and not f['hardwarePresentation'] and not f['ordinaryProductEnrollmentQualified'] and not f['fullReleaseAccepted']
assert f['readerProbe']['heldDenied'] and f['readerProbe']['freshDenied'] and f['readerProbe']['icons']['readers']==1 and f['readerReleased']['icons']['readers']==0
assert f['concealedDOM']['fallbacks']==[{'state':'unavailable','title':'Preview unavailable','icons':[]}] and f['concealedDOM']['status']['retirementPending'] and not f['concealedDOM']['status']['producerRetired']
assert all(f['afterPixels'][key]==0 for key in ['red','yellow','blue','green']) and f['afterIconPixels']['ownApplicationIconPixels']==0
assert n['nativeIconLockBoundedQualified'] and n['nativeTitleIconFallbackBoundedQualified'] and n['nativeAddressReuseFullGUIQualified']
log=(np.parent/'private-evidence/full-client-locked.log').read_text();assert log.index('native-icon-reader-probe:')<log.index('native-client-command: {"kind":"release"')<log.index('native-client-concealed-fallback:')<log.index('native-client-ack:')<log.index('native-client-complete:')<log.index('native-icon-retired:')
roots.append(native);evidence.extend([prepPath,native/'qa/preflight.json',np])
for name,count in [('warlock-preview-icon-lock-boundary',5),('warlock-preview-icon-lock-delivery',1),('warlock-preview-locked-snapshot-carrier',1)]:
 root=REPO/'openspec/changes'/name;vp=next(root.glob('qa/validate-*/report.json'));v=proof(vp);assert v['passed'] and len(v['requirements'])==count and v['frozenBaseline']==[242,417];roots.append(root);evidence.append(vp)
controller=next((REPO/'docs/warlock-preview/v58').glob('controller-check-v5-*/report.json'));c=proof(controller);assert c['passed'] and c['evidence']['checks']==22;evidence.append(controller)
plan=REPO/'docs/warlock-preview/v56/S09-EVIDENCE-PLAN.json';p=json.loads(plan.read_text());assert not p['S09Accepted'] and not p['fullReleaseAccepted'] and len(p['scenarios'])==13;evidence.append(plan)
components=[hold(root) for root in roots]
report={'schema':1,'passed':True,'scope':scope,'components':components,'evidence':{str(p.relative_to(REPO)):sha(p) for p in evidence},'nativeControls':len(n['checks']),'retainedOriginalControls':1783,'retainedNative93Controls':2372,'normalOwnedExits':len(n['ownedExitCodes']),'nativeIconLockBoundedQualified':True,'iconLockEvidence':f,'nativeAcceptance':False,'S09Accepted':False,'fullReleaseAccepted':False,'next':'Actual product re-enrollment/theme changes, ordinary multi-entry preview enrollment, all original S09 thirteen and restore/recovery/drag/input/hardware/output/AT/IME/resource/journey/reversible coherent deployment gates.'}
assert not (OUT/'report.json').exists();(OUT/'report.json').write_text(json.dumps(report,indent=2)+'\n');print(json.dumps({'passed':True,'report':str(OUT/'report.json'),'components':len(components),'nativeControls':len(n['checks']),'normalOwnedExits':len(n['ownedExitCodes'])}))
