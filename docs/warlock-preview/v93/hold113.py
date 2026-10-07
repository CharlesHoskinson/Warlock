"""Freeze current single Elm realm policy and immutable earlier phase evidence."""
import hashlib,json,pathlib,resource,stat,sys
sys.path.insert(0,'/home/hoskinson/window-integration-qa');from qa_launch import require_qa_scope
require_qa_scope();assert resource.getrlimit(resource.RLIMIT_CORE)==(1,1)
repo=pathlib.Path('/home/hoskinson/omarchy-windows-parity');root=repo/'implementation/warlock-preview-provider-v113';sha=lambda p:hashlib.sha256(pathlib.Path(p).read_bytes()).hexdigest()
paths={
 'boundaries':'scoped-presenter-check-v3-1791358090496396801',
 'nativeElmOutbox':'scoped-presenter-native-check-v4-1791358090496614068',
 'model':'scoped-elm-model-check-v2-1791358090497978778',
 'coldCohort':'scoped-cold-cohort-check-v2-1791358252987480139',
 'permanent':'retirement-delivery-check-v2-1791358117552830188',
 'permanentNative':'retirement-native-elm-check-v5-1791358194455481744',
 'permanentModel':'retirement-delivery-model-check-v3-1791358230842625480',
 'build':'build-1791358252985183504'}
paths={k:root/'qa'/v/'report.json' for k,v in paths.items()};declared=set()
def verify(path,current=False):
 d=json.loads(path.read_text());assert not d.get('nativeAcceptance',False) and not d.get('fullReleaseAccepted',False)
 if current:assert d['passed']
 for rel,value in d.get('inputs',{}).items():
  p=root/rel
  if current or (p.exists() and sha(p)==value):assert sha(p)==value,(path,rel)
  else:assert sha(path.parent/'inputs'/rel)==value,(path,rel,'historical input snapshot')
 for rel,value in d.get('artifacts',{}).items():
  p=path.parent/rel;assert sha(p)==value,(path,rel);declared.add(str(p.relative_to(root)))
 if 'pluginResourceHeaderSHA256' in d:assert sha(root.parent/'warlock-family-style-crop-capture-v19/native/capture-resources.hpp')==d['pluginResourceHeaderSHA256']
 if 'compiledControls' in d:
  row=d['compiledControls'];p=pathlib.Path(row['path']);assert sha(p)==row['sha256'];proof=json.loads(p.read_text());assert proof['passed']
  for rel,value in proof['inputs'].items():assert sha(root/rel)==value,(path,rel,'current compiled policy dependency')
  assert sha(path.parent/'preview-replay.js')==row['compiledElmSHA256']
 return d
reports={k:verify(p,True) for k,p in paths.items()}
assert reports['boundaries']['evidence']['checks']==44
n=reports['nativeElmOutbox']['evidence'];assert n['checks']==175 and n['normalOwnedExit'] and n['realmEpochs']==2 and n['nativeGrantResets']==0 and n['syntheticNativeRemainsActive'] and n['singlePreviewPolicy']
q=reports['model'];assert q['namedScenarios']==20 and q['invariantSamples']==200 and q['unsafeCompiledElmVariantsDetected']==6 and q['evidence']['statesCompared']==469 and len(q['evidence']['coupledTraces'])==32
assert reports['coldCohort']['evidence']['checks']==1549 and reports['coldCohort']['evidence']['coldMetadataEntries']==256
assert reports['permanent']['evidence']['checks']==45
p=reports['permanentNative']['evidence'];assert p['checks']==20 and p['nativeCChecks']==34 and p['normalOwnedExit']
p=reports['permanentModel'];assert p['namedScenarios']==14 and p['evidence']['statesCompared']==667 and len(p['evidence']['coupledTraces'])==34 and p['unsafeModelMutantsDetected']==3
b=reports['build'];assert len(b['commands'])==103 and all(x['exitCode']==0 for x in b['commands']) and sha(paths['build'].parent/'elm-host')==b['binarySHA256']
a=json.loads((root/'ANCESTRY.json').read_text());parent=pathlib.Path(a['parent']);m=parent/'component-manifest.json';assert sha(m)==a['parentManifestSHA256'];prior=json.loads(m.read_text());assert prior['sourceHeld'] and prior['passed']
for rel,row in prior['files'].items():assert sha(parent/rel)==row['sha256'],rel
for base in ['native','assets','adapter','src']:
 for p in (parent/base).glob('*'):
  if p.is_file() and str(p.relative_to(parent))!='src/PreviewPresenter.elm':assert sha(root/base/p.name)==sha(p),p
for p in (parent/'qa').glob('*'):
 if p.is_file() and p.name!='current-build.json':assert sha(root/'qa'/p.name)==sha(p),p
old=json.loads(pathlib.Path(prior['reports']['build']['path']).read_text());added={'scoped-realm-replay-build','scoped-realm-replay','scoped-cold-cohort-replay','typed-realm-replay-build','typed-realm-decoder-replay'}
assert [x['name'] for x in b['commands'] if x['name'] not in added]==[x['name'] for x in old['commands']]
history=[];failed=[]
for path in sorted((root/'qa').glob('*/report.json')):
 if path in paths.values():continue
 d=verify(path);row={'path':str(path),'sha256':sha(path),'passed':d['passed'],'qualifiesFinalPresenter':False,'scope':'Immutable original phase source snapshot; not final source qualification.'};history.append(row)
 if not d['passed']:failed.append(str(path))
assert len(failed)==8
result={'schema':1,'owner':a['owner'],'sourceHeld':True,'passed':True,'evidenceIntegrityPassed':True,'reports':{k:{'path':str(p),'sha256':sha(p)} for k,p in paths.items()},'historicalPhaseReports':history,'heldFailedReports':failed,'singlePreviewPolicy':True,'typedRealmBoundariesImplemented':True,'scopedElmDetachmentImplemented':True,'boundaryChecks':44,'nativeElmOutboxChecks':175,'realmEpochs':2,'nativeGrantResets':0,'scopedScenarios':20,'scopedTraces':32,'scopedStates':469,'scopedSamples':200,'unsafeCompiledElmVariantsDetected':6,'coldMetadataEntries':256,'coldCohortChecks':1549,'permanentElmChecks':45,'permanentRoundtripChecks':20,'permanentCChecks':34,'permanentScenarios':14,'permanentTraces':34,'permanentStates':667,'fullBuildCommands':103,'originalBuildCommands':98,'parentNativeProductUnchanged':True,'parentAdapterAndLegacyAssetsUnchanged':True,'parentManifest':str(m),'parentManifestSHA256':sha(m),'fullElmRecoveryQualified':False,'typedHostRoutingActivated':False,'webKitActivated':False,'actualWaylandWindowAcceptance':False,'nativeAcceptance':False,'fullReleaseAccepted':False,'scope':(root/'SCOPED-ELM-HANDOFF.md').read_text()}
files={}
for p in sorted(root.rglob('*')):
 rel=p.relative_to(root);name=str(rel)
 if any(part in {'elm-stuff','mutable-elm-home','elm-home','__pycache__'} for part in rel.parts) and 'toolchain' not in rel.parts and name not in declared:continue
 assert not p.is_symlink(),p
 if p.is_file():files[name]={'kind':'file','sha256':sha(p),'size':p.stat().st_size,'mode':oct(stat.S_IMODE(p.stat().st_mode))}
result['files']=files;assert not (root/'component-manifest.json').exists();(root/'component-manifest.json').write_text(json.dumps(result,indent=2)+'\n')
out=pathlib.Path(__file__).parent/'component-report113.json';assert not out.exists();out.write_text(json.dumps({k:v for k,v in result.items() if k!='files'},indent=2)+'\n')
task=repo/'openspec/changes/warlock-preview-actor-retirement/tasks.md';s=task.read_text();old='- [ ] Freeze CONTROL-026 typed realm/scoped detachment';assert s.count(old)==1;task.write_text(s.replace(old,'- [x] Freeze CONTROL-026 typed realm/scoped detachment'))
sys.path.insert(0,str(repo/'implementation/elm-build-loop-v1'));import loop
print(loop.write_checkpoint(repo,a['owner'],str(root.relative_to(repo)),['PROGRESS heldGUI113 single existing Elm policy with typed native realms/scoped detachment. Current boundaries44/nativeC+Elm+outbox175/two Active-subject epochs/unchanged Native grant/normal exits; Quint20/32 actual optimizedElm traces/469 states/200 samples/six compiled variants; cold256/1549 checks; original permanent45/native20+C34/model14/34/667/three variants; full103 retains98. Eight failed attempts and earlier phases retained at original snapshots, not final-source acceptance. CONTROL026/OpenSpec six scenarios. Next PUBLIC82 then real typed shared-host realm/outbox/stable WebKit/Core integration and full Elm recovery. Native130 GUI110 legacy/core16/plugin19/AQ1552518/278/full cleanup remains actual bounded native baseline. All original full release gates open; no installed changes.'],'progress',[str((root/'component-manifest.json').relative_to(repo)),str(out.relative_to(repo))]))
print(json.dumps({'heldFiles':len(files),'fullBuildCommands':103,'failedAttemptsHeld':len(failed)}))
