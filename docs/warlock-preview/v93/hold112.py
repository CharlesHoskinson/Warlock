"""Freeze readonly original native realm recovery and exact regression evidence."""
import hashlib,json,pathlib,resource,stat,sys
sys.path.insert(0,'/home/hoskinson/window-integration-qa');from qa_launch import require_qa_scope
require_qa_scope();assert resource.getrlimit(resource.RLIMIT_CORE)==(1,1)
repo=pathlib.Path('/home/hoskinson/omarchy-windows-parity');root=repo/'implementation/warlock-preview-provider-v112';sha=lambda p:hashlib.sha256(pathlib.Path(p).read_bytes()).hexdigest()
def verify(path):
 d=json.loads(path.read_text());assert d['passed'] and not d.get('nativeAcceptance',False) and not d.get('fullReleaseAccepted',False)
 for rel,value in d['inputs'].items():assert sha(root/rel)==value,(path,rel)
 for rel,value in d.get('artifacts',{}).items():assert sha(path.parent/rel)==value,(path,rel)
 return d
paths={'recovery':root/'qa/native-outbox-recovery-check-v3-1791355285169842681/report.json','model':root/'qa/recovered-pages-model-check-v3-1791355359626645528/report.json','nativeVariants':root/'qa/recovery-native-variants-v2-1791355389638849943/report.json','build':root/'qa/build-1791355033265613007/report.json','resourceRegressions':root/'qa/resource-regression-check-1791355033267391725/report.json','scopedRegressions':next(root.glob('qa/detachment-regression-check-*/report.json'))}
reports={k:verify(p) for k,p in paths.items()};c=reports['recovery']['evidence'];assert c['checks']==129 and c['normalOwnedExit'] and c['actualNativeRecovery'] and c['freshJSContexts']==2 and c['realmEpochs']==2 and c['syntheticNativeRemainsActive']
q=reports['model'];assert q['namedScenarios']==24 and len(q['coupledTraces'])==36 and q['statesCompared']==498 and q['invariantSamples']==200 and q['unsafeActualJSVariantsDetected']==9
v=reports['nativeVariants'];assert v['unsafeCompiledNativeVariantsDetected']==3 and all(x['compiled'] and x['namedObservableMismatch'] for x in v['variants'])
b=reports['build'];assert len(b['commands'])==98 and all(x['exitCode']==0 for x in b['commands']) and sha(paths['build'].parent/'elm-host')==b['binarySHA256']
for key in ['resourceRegressions','scopedRegressions']:
 assert len(reports[key]['reports'])==4
 for name,row in reports[key]['reports'].items():
  p=pathlib.Path(row['path']);assert sha(p)==row['sha256'];verify(p)
a=json.loads((root/'ANCESTRY.json').read_text());parent=pathlib.Path(a['parent']);m=parent/'component-manifest.json';assert sha(m)==a['parentManifestSHA256'];previous=json.loads(m.read_text());assert previous['sourceHeld'] and previous['passed']
for rel,row in previous['files'].items():assert sha(parent/rel)==row['sha256'],rel
changed={'native/control_reservations.hpp','native/imported-clients.h','native/imported-clients.cpp'}
for name in ['src','assets','adapter','native']:
 for p in (parent/name).glob('*'):
  if p.is_file() and str(p.relative_to(parent)) not in changed:assert sha(root/name/p.name)==sha(p),p
for p in (parent/'qa').glob('*'):
 if p.is_file() and p.name!='current-build.json':assert sha(root/'qa'/p.name)==sha(p),p
old=json.loads(pathlib.Path(previous['reports']['build']['path']).read_text());assert [x['name'] for x in b['commands'] if x['name']!='recovered-outbox-syntax']==[x['name'] for x in old['commands']]
assert 'recovered-native-preview-control-outbox' not in (root/'assets/popup.html').read_text()
failed=[str(p) for p in sorted((root/'qa').glob('*/report.json')) if not json.loads(p.read_text()).get('passed',False)];assert len(failed)==3
result={'schema':1,'owner':'f6779148-8f5d-4bdf-8a0f-044184e486f2','sourceHeld':True,'passed':True,'evidenceIntegrityPassed':True,'reports':{k:{'path':str(p),'sha256':sha(p)} for k,p in paths.items()},'nativeRecoveryChecks':129,'freshJSContexts':2,'realmEpochs':2,'syntheticNativeRemainsActive':True,'recoveryScenarios':24,'recoveryTraces':36,'recoveryStates':498,'recoverySamples':200,'unsafeActualJSVariantsDetected':9,'unsafeCompiledNativeVariantsDetected':3,'fullBuildCommands':98,'originalBuildCommands':97,'currentResourceRegressionSuites':4,'currentScopedRegressionSuites':4,'parentManifest':str(m),'parentManifestSHA256':sha(m),'heldFailedReports':failed,'readonlyNativeRealmRecoveryImplemented':True,'freshJSContextRecoveryQualified':True,'actualWebKitContextReloadQualified':False,'fullElmRecoveryQualified':False,'typedHostRoutingActivated':False,'webKitActivated':False,'actualWaylandWindowAcceptance':False,'nativeAcceptance':False,'fullReleaseAccepted':False,'scope':(root/'RECOVERY-HANDOFF.md').read_text()}
files={}
for p in sorted(root.rglob('*')):
 rel=p.relative_to(root)
 if any(part in {'elm-stuff','mutable-elm-home','elm-home','__pycache__'} for part in rel.parts) and 'toolchain' not in rel.parts:continue
 assert not p.is_symlink(),p
 if p.is_file():files[str(rel)]={'kind':'file','sha256':sha(p),'size':p.stat().st_size,'mode':oct(stat.S_IMODE(p.stat().st_mode))}
result['files']=files;assert not (root/'component-manifest.json').exists();(root/'component-manifest.json').write_text(json.dumps(result,indent=2)+'\n')
out=pathlib.Path(__file__).parent/'component-report112.json';assert not out.exists();out.write_text(json.dumps({k:v for k,v in result.items() if k!='files'},indent=2)+'\n')
sys.path.insert(0,str(repo/'implementation/elm-build-loop-v1'));import loop
print(loop.write_checkpoint(repo,result['owner'],str(root.relative_to(repo)),['PROGRESS heldGUI112 inactive readonly bounded original native realm recovery. Actual controlled C129/two fresh JS VMs/two Active-subject epochs on unchanged Native grant. Complete consistent pages before post; native-issued neighbor survives context loss; captured-prefix/epoch/exact-wire guards. Quint24/36 actualJS traces/498 states/200 samples/nine JS variants; three compiled native variants; full98 retains97; current four resource and four scoped regressions pass. Three fixture failures retained. Next PUBLIC81 then typed host realm/retained Elm recovery and actual WebKit callback/context/Core integration; original full release gates remain open. Native130 current110 legacy2518/278/full cleanup PUBLIC79 baseline; GUI111 PUBLIC80. No installed changes.'],'progress',[str((root/'component-manifest.json').relative_to(repo)),str(out.relative_to(repo))]))
