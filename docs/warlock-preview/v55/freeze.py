"""Hold actual full GUI native fallback proof and separate lower-level evidence."""
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
for version in range(39,43):
 root=REPO/f'implementation/warlock-preview-provider-v{version}';p=next(root.glob('qa/build-*/report.json'));d=proof(p,root);assert not d['passed'];roots.append(root);evidence.append(p)
gui=REPO/'implementation/warlock-preview-provider-v43';gm=json.loads((gui/'component-manifest.json').read_text());b=proof(Path(gm['buildReport']),gui);m=proof(Path(gm['modelReport']),gui)
assert b['passed'] and len(b['commands'])==82 and all(x['exitCode']==0 for x in b['commands'])
assert m['passed'] and m['compiledChecks']==36 and m['namedScenarios']==10 and len(m['coupledTraces'])==22 and sum(x['statesCompared'] for x in m['coupledTraces'])==564 and m['unsafeMutantsDetected']==3
for name in ['metadata-privacy-replay','metadata-icon-physical-tests']:assert gm['evidence'][name]['checks']==74 and gm['evidence'][name]['passed']
modelRoot=REPO/'implementation/warlock-preview-metadata-model-v1';modelPath=Path(gm['metadataModelReport']);mm=proof(modelPath,modelRoot);assert mm['passed'] and mm['namedScenarios']==8 and mm['invariantSamples']==100 and len(mm['coupledTraces'])==16 and mm['statesCompared']==210 and mm['compiledBuild']=={'path':gm['buildReport'],'sha256':sha(Path(gm['buildReport']))}
failed=Path(gm['retainedFailedMetadataModelReport']);f=proof(failed,gui);assert not f['passed'] and f['commands'][-1]['name']=='typecheck'
roots.extend([gui,modelRoot]);evidence.extend([Path(gm['buildReport']),Path(gm['modelReport']),modelPath,failed])
native=REPO/'implementation/warlock-client-provider-native-v93';prepPath=next(native.glob('qa/prepare-*/report.json'));prep=proof(prepPath);assert prep['passed'];pre=proof(native/'qa/preflight.json');np=next(native.glob('qa/native-*/report.json'));n=proof(np);assert n['passed'] and n['cleanupPassed'] and len(n['checks'])==2372 and all(x['passed'] for x in n['checks']) and len(n['ownedExitCodes'])==255 and all(x['exitCode']==0 for x in n['ownedExitCodes']) and n['pair']==pre['pair']
assert n['nativeTitleIconFallbackBoundedQualified'] and n['nativeAddressReuseFullGUIQualified']
f=n['fallbackMetadataEvidence'];assert f['scenarioId']=='ELM-UX-007 ux-007' and f['metadata']['title']==f['actualNativeTitle']=='WARLOCK-CHILD-PROBE' and f['metadata']['application']==f['actualNativeApplication']=='warlock-child-probe' and f['metadata']['binding']==f['originalJob']['binding'] and f['metadata']['subject']==f['originalJob']['context']['incarnation'] and f['metadata']['iconKind']=='application'
assert f['beforePixels']['oldSourceExactNativePixels']==12516 and f['beforePixels']['foreignGreenPixels']==0 and f['beforePixels']['ownApplicationIconPixels']==0
assert f['afterPixels']['ownApplicationIconPixels']==2304 and f['afterPixels']['oldSourceExactNativePixels']==f['afterPixels']['foreignGreenPixels']==0
assert len(f['dom'])==1 and f['dom'][0]['title']==f['actualNativeTitle'] and f['dom'][0]['state']=='unavailable' and f['dom'][0]['icons'][0]['uri']=='elm-shell://icon/'+f['metadata']['icon'] and f['dom'][0]['icons'][0]['complete']
assert not any(f[x] for x in ['hardwarePresentation','nativeAcceptance','fullReleaseAccepted','lockedConcealmentNativeQualified','ordinaryProductEnrollmentQualified'])
log=(np.parent/'private-evidence/full-generated-backdrop-source-loss.log').read_text();assert log.index('native-client-command: {"kind":"release"')<log.index('native-client-ack:')<log.index('native-client-fallback:');assert log.count('native-client-command: {"kind":"acquire"')==1 and 'native-client-resume:' not in log
assert any(x['name']=='allOriginal1783OrderedAssertionsRetained' and x['passed'] for x in n['checks']) and any(x['name']=='allPriorNative92StableOrderedAssertionsRetained' and x['passed'] for x in n['checks'])
roots.append(native);evidence.extend([prepPath,native/'qa/preflight.json',np])
sp=REPO/'openspec/changes/warlock-preview-window-metadata';vp=next(sp.glob('qa/validate-*/report.json'));v=proof(vp);assert v['passed'] and len(v['requirements'])==4 and v['frozenBaseline']==[242,417];roots.append(sp);evidence.append(vp)
plan=REPO/'docs/warlock-preview/v54/S09-EVIDENCE-PLAN.json';p=json.loads(plan.read_text());assert not p['S09Accepted'] and not p['fullReleaseAccepted'] and len(p['scenarios'])==13;evidence.append(plan)
components=[hold(root) for root in roots]
report={'schema':1,'passed':True,'scope':scope,'components':components,'evidence':{str(p.relative_to(REPO)):sha(p) for p in evidence},'nativeControls':2372,'retainedOriginalControls':1783,'retainedNative92Controls':2363,'normalOwnedExits':255,'nativeTitleIconFallbackBoundedQualified':True,'fallbackMetadataEvidence':f,'nativeAcceptance':False,'S09Accepted':False,'fullReleaseAccepted':False,'next':'Compile/verify freshGUI44 binding reset/theme update, actual native privacy/held icon URI, ordinary multi-entry enrollment and all original S09/restore/recovery/drag/input/hardware/output/AT/IME/resource/journey/reversible deployment gates.'}
assert not (OUT/'report.json').exists();(OUT/'report.json').write_text(json.dumps(report,indent=2)+'\n');print(json.dumps({'passed':True,'report':str(OUT/'report.json'),'components':len(components),'nativeControls':2372,'normalOwnedExits':255}))
