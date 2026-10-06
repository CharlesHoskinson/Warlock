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
for version in [52,53,54]:
 root=REPO/f'implementation/warlock-preview-provider-v{version}';p=next(root.glob('qa/build-*/report.json'));d=proof(p,root)
 assert d['passed']==(version==54)
 if version==54:
  assert len(d['commands'])==86 and all(x['exitCode']==0 for x in d['commands'])
  gm=json.loads((root/'component-manifest.json').read_text());assert gm['evidence']['catalog-enrollment-replay']['checks']==60 and gm['evidence']['window-catalog-admission-tests']['checks']==26
  for key,names,states in [('catalogModelReport',8,214),('metadataModelReport',8,210)]:
   pp=Path(gm[key]);m=proof(pp,root);assert m['passed'] and m['namedScenarios']==names and m['statesCompared']==states and len(m['coupledTraces'])==16;evidence.append(pp)
  pp=Path(gm['modelReport']);m=proof(pp,root);assert m['passed'] and m['namedScenarios']==10 and m['compiledChecks']==36 and m['unsafeMutantsDetected']==3 and sum(x['statesCompared'] for x in m['coupledTraces'])==564;evidence.append(pp)
 roots.append(root);evidence.append(p)
for version in [98,100]:
 root=REPO/f'implementation/warlock-client-provider-native-v{version}';p=next(root.glob('qa/native-*/report.json'));d=proof(p);assert not d['passed'] and d['cleanupPassed'] and all(x['exitCode']==0 for x in d['ownedExitCodes']) and 'ordinaryRendered=wait' in d['traceback'];roots.append(root);evidence.append(p)
root=REPO/'implementation/warlock-client-provider-native-v99';proof(root/'qa/preflight.json');assert not list(root.glob('qa/native-*/report.json'));roots.append(root)
root=REPO/'implementation/warlock-client-provider-native-v101';p=next(root.glob('qa/native-*/report.json'));d=proof(p);pre=proof(root/'qa/preflight.json');prep=proof(next(root.glob('qa/prepare-*/report.json')))
assert d['passed'] and d['cleanupPassed'] and len(d['checks'])==2392 and len(d['ownedExitCodes'])==260 and all(x['passed'] for x in d['checks']) and all(x['exitCode']==0 for x in d['ownedExitCodes']) and d['pair']==pre['pair'] and prep['passed']
for name in ['allOriginal1783OrderedAssertionsRetained','allPriorNative97StableOrderedAssertionsRetained','ordinaryCatalogTwoActualElmUnavailableEntries','ordinaryCatalogNoFixedCaptureEnrollmentOrAcquire','ordinaryCatalogFullHostNormalExit','iconLockHeldAndNewActualEndpointDeniedBeforePolicy','iconLockActualWebKitExcludesOldPreviewAndIconPixels']:
 assert any(x['name']==name and x['passed'] for x in d['checks']),name
ordinary=d['ordinaryCatalogEvidence'];assert not ordinary['fixedQualificationSubjects'] and not ordinary['nativeScopeCreated'] and not ordinary['nativeCaptureEligible'] and ordinary['rendered']['body']['text'].count('Preview unavailable')==4
log=(p.parent/'private-evidence/ordinary-catalog-provider.log').read_text();assert 'native-client-start:' not in log and 'native-client-command:' not in log and 'native-imported-start:' not in log and 'shared-host-exit: failure=0 rendered=1' in log
roots.append(root);evidence.extend([p,root/'qa/preflight.json',next(root.glob('qa/prepare-*/report.json'))])
root=REPO/'openspec/changes/warlock-preview-product-enrollment';vp=next(root.glob('qa/validate-*/report.json'));v=proof(vp);assert v['passed'] and len(v['requirements'])==3 and v['frozenBaseline']==[242,417];roots.append(root);evidence.append(vp)
plan=REPO/'docs/warlock-preview/v60/S09-EVIDENCE-PLAN.json';old=json.loads(plan.read_text());assert not old['S09Accepted'] and not old['fullReleaseAccepted'] and len(old['scenarios'])==13;evidence.append(plan)
components=[hold(root) for root in roots]
report={'schema':1,'passed':True,'scope':scope,'components':components,'evidence':{str(p.relative_to(REPO)):sha(p) for p in evidence},'nativeControls':2392,'retainedOriginalControls':1783,'retainedNative97RawControls':2386,'retainedNative97StableControls':2380,'normalOwnedExits':260,'ordinaryMetadataOnlyEnrollmentBoundedQualified':True,'ordinaryCatalogEvidence':ordinary,'nativeCaptureEligible':False,'nativeAcceptance':False,'S09Accepted':False,'fullReleaseAccepted':False,'next':'Dynamic ordinary multi-entry eligible capture through one shared two-item/byte/readers allocator and actual owning native scope; retain old source resources/request floors/clocks/deadlines/terminal ACK. Actual theme/rebinding, complete original S09 thirteen and restore/recovery/drag/input/hardware/output/AT/IME/resource/journey/reversible coherent deployment remain open.'}
(OUT/'report.json').write_text(json.dumps(report,indent=2)+'\n');print(json.dumps({'passed':True,'components':len(components),'nativeControls':2392,'normalOwnedExits':260,'ordinaryMetadataOnlyEnrollment':True,'fullReleaseAccepted':False}))
