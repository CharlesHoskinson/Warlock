"""Hold exact source and separate bounded native address-reuse evidence."""
import re,hashlib,json,resource,stat,sys
from pathlib import Path
sys.path.insert(0,'/home/hoskinson/window-integration-qa')
from qa_launch import require_qa_scope
scope=require_qa_scope();assert resource.getrlimit(resource.RLIMIT_CORE)==(1,1)
REPO=Path('/home/hoskinson/omarchy-windows-parity');OUT=Path(__file__).parent
sha=lambda p:hashlib.sha256(p.read_bytes()).hexdigest()
def only(root,pattern):
 xs=list(root.glob(pattern));assert len(xs)==1,(root,pattern,xs);return xs[0]
def proof(p,owner=None):
 d=json.loads(p.read_text())
 for x,h in d.get('inputs',{}).items():
  q=Path(x);q=q if q.is_absolute() else owner/q;assert sha(q)==h,(p,q)
 for x,h in d.get('artifacts',{}).items():assert sha(p.parent/x)==h,(p,x)
 return d
def held(p):
 d=json.loads(p.read_text());assert d.get('passed') or (d.get('sourceHeld') and d.get('evidenceIntegrityPassed'))
 for x,v in d['files'].items():assert sha(p.parent/x)==v['sha256'] and (p.parent/x).stat().st_size==v['size'],x
 return d
priorPath=REPO/'docs/warlock-preview/v51/report.json';prior=proof(priorPath);assert prior['passed']
for c in prior['components']:
 p=REPO/c['path'];assert sha(p)==c['sha256'];held(p)
guiRoot=REPO/'implementation/warlock-preview-provider-v38';gm=held(guiRoot/'component-manifest.json');build=proof(Path(gm['buildReport']),guiRoot);model=proof(Path(gm['modelReport']),guiRoot)
assert build['passed'] and len(build['commands'])==77 and all(x['exitCode']==0 for x in build['commands'])
assert model['passed'] and model['namedScenarios']==10 and len(model['coupledTraces'])==22 and model['unsafeMutantsDetected']==3
assert gm['evidence']['qa-reader-control-tests']=={'passed':True,'checks':15}
roots=[REPO/'implementation/warlock-preview-provider-v37',guiRoot]
evidence=[priorPath,Path(gm['buildReport']),Path(gm['modelReport'])]
failedGui=json.loads((roots[0]/'qa/build-failure.json').read_text());assert not failedGui['passed'] and not failedGui['nativeLaunched'];evidence.append(roots[0]/'qa/build-failure.json')
for version in [89,90,91,92]:
 root=REPO/f'implementation/warlock-client-provider-native-v{version}';pp=only(root,'qa/prepare-*/report.json');prepared=proof(pp);assert prepared['passed'];pre=proof(root/'qa/preflight.json');np=only(root,'qa/native-*/report.json');n=proof(np);assert pre['pair']==n['pair'] and n['cleanupPassed'] and all(x['exitCode']==0 for x in n['ownedExitCodes'])
 if version==89:assert not n['passed'] and 'newWindow=wait' in n['traceback'] and not any(not x['passed'] for x in n['checks'])
 elif version==90:assert not n['passed'] and [x['name'] for x in n['checks'] if not x['passed']]==['allPrior2341OrderedAssertionsRetained'] and n['addressReuseEvidence']['actualAddressReuse']
 elif version==91:assert not n['passed'] and [x['name'] for x in n['checks'] if not x['passed']]==['allPriorNative88StableOrderedAssertionsRetained'] and n['addressReuseEvidence']['actualAddressReuse']
 else:assert n['passed'] and n['nativeAddressReuseFullGUIQualified'] and all(x['passed'] for x in n['checks']);accepted=n;nativePath=np
 roots.append(root);evidence.extend([pp,root/'qa/preflight.json',np])
originalPath=REPO/'implementation/warlock-client-provider-native-v88/qa/native-1791285595852446427/report.json';original=proof(originalPath);readonly={'styleDimPendingNativeReadonlyScope','styleAgainDimPendingNativeReadonlyScope','styleRestoreIntermediateReadonlyScope','styleCropDimIntermediateReadonlyScope'}
def stable(rows):return [re.sub(r'^opacityPrivateForeignWindowMoved-0x[0-9a-f]+$','opacityPrivateForeignWindowMoved-<native-address>',x['name']) for x in rows if x['name'] not in readonly]
names=stable(original['checks']);assert len(original['checks'])==2341 and [x for x in stable(accepted['checks']) if x in set(names)]==names and accepted['priorNative88Retention']['allActualChecksPassed']
a=accepted['addressReuseEvidence'];frame=a['originalFrame'];ready=a['readerReady'];probe=a['beforePolicyProbe'];terminal=a['terminalStatus']
assert a['scenarioId']=='ELM-REN-004 ren-004' and a['actualAddressReuse'] and a['oldAddress']==a['replacementAddress'] and int(a['replacementSubject'])>int(a['oldSubject'])
assert ready['uri']==probe['uri']=='elm-shell://preview/'+frame['handle'] and ready['status']['job']==probe['status']['job']==terminal['job']==frame['job']
assert a['heldAndFreshDeniedBeforePolicyEffects'] and probe['heldDenied'] and probe['freshDenied'] and probe['heldRead']==-1 and int(probe['status']['charge'])>0
assert not any(probe['status'][x] for x in ['mappedFDClosed','exportReleased','producerRetired'])
assert a['probeNativeScope']['clock']==frame['job']['clock'] and int(a['probeNativeScope']['now'])<int(frame['expires'])
assert terminal['charge']=='0' and all(terminal[x] for x in ['mappedFDClosed','exportReleased','producerRetired']) and not terminal['retirementPending']
assert a['webkitPixels'][0]['styledRoot']>128 and a['webkitPixels'][1]['styledRoot']==0 and a['webkitPixels'][1]['foreignGreen']==0
assert not a['hardwarePresentation'] and not a['nativeAcceptance'] and not a['fullReleaseAccepted']
log=(nativePath.parent/'private-evidence/full-client-reuse.log').read_text();assert log.index('native-client-reader-probe:')<log.index('native-client-reader-released:')<log.index('native-client-command: {"kind":"release"')<log.index('native-client-ack:')<log.index('native-client-complete:')
assert log.count('native-client-command: {"kind":"acquire"')==1 and 'native-client-resume:' not in log
spec=REPO/'openspec/changes/warlock-preview-native-address-reuse';vp=only(spec,'qa/validate-*/report.json');v=proof(vp);assert v['passed'] and len(v['requirements'])==4 and v['frozenBaseline']==[242,417];roots.append(spec);evidence.extend([originalPath,vp])
plan=REPO/'docs/warlock-preview/v52/S09-EVIDENCE-PLAN.json';inventory=json.loads(plan.read_text());assert not inventory['S09Accepted'] and len(inventory['scenarios'])==13;evidence.append(plan)
components=[]
for root in roots:
 p=root/'component-manifest.json'
 if not p.exists():
  files={}
  for f in sorted(root.rglob('*')):
   rel=f.relative_to(root)
   if any(x in {'__pycache__','elm-stuff','mutable-elm-home'} for x in rel.parts):continue
   assert not f.is_symlink(),f
   if f.is_file():files[str(rel)]={'kind':'file','sha256':sha(f),'size':f.stat().st_size,'mode':oct(stat.S_IMODE(f.stat().st_mode))}
  p.write_text(json.dumps({'schema':1,'sourceHeld':True,'evidenceIntegrityPassed':True,'files':files,'nativeAddressReuseFullGUIQualified':root.name=='warlock-client-provider-native-v92','nativeAcceptance':False,'fullReleaseAccepted':False,'previewEligible':False},indent=2)+'\n')
 h=held(p);components.append({'path':str(p.relative_to(REPO)),'sha256':sha(p),'files':len(h['files'])})
report={'schema':1,'passed':True,'scope':scope,'components':components,'evidence':{str(p.relative_to(REPO)):sha(p) for p in evidence},'nativeControls':len(accepted['checks']),'retainedPriorNativeControls':2341,'retainedOriginalControls':1783,'normalOwnedExits':len(accepted['ownedExitCodes']),'nativeAddressReuseFullGUIQualified':True,'addressReuseEvidence':a,'nativeAcceptance':False,'S09Accepted':False,'fullReleaseAccepted':False,'next':'Continue original S09 correct-title/icon/no-unrelated-pixels fallback and ordinary product enrollment/fidelity/clock/fence/state gates, then original restore38/recovery34/case34/two-second/cursor/receipt/drag52/input/AT/IME/hardware/resources/journeys/reversible deployment.'}
assert not (OUT/'report.json').exists();(OUT/'report.json').write_text(json.dumps(report,indent=2)+'\n');print(json.dumps({'passed':True,'report':str(OUT/'report.json'),'components':len(components),'nativeControls':len(accepted['checks']),'normalOwnedExits':len(accepted['ownedExitCodes'])}))
