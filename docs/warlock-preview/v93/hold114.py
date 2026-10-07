"""Hold exact proposal ingress evidence without claiming active host routing."""
import hashlib,json,pathlib,resource,stat,sys
sys.path.insert(0,'/home/hoskinson/window-integration-qa');from qa_launch import require_qa_scope
require_qa_scope();assert resource.getrlimit(resource.RLIMIT_CORE)==(1,1)
repo=pathlib.Path('/home/hoskinson/omarchy-windows-parity');root=repo/'implementation/warlock-preview-provider-v114'
sha=lambda p:hashlib.sha256(pathlib.Path(p).read_bytes()).hexdigest()
names={'nativeElmOutbox':'realm-ingress-native-check-1791359225978208807','packetizer':'native-proposals-check-1791359320008832665','model':'native-ingress-model-check-v2-1791359714937810894','build':'build-1791359262569976596','resource':'resource-regression-check-1791359262571504449','scoped':'detachment-regression-check-1791359262570618901'}
paths={k:root/'qa'/v/'report.json' for k,v in names.items()};declared=set();verified=set()
def verify(path,current=False):
 d=json.loads(path.read_text());assert not d.get('nativeAcceptance',False) and not d.get('fullReleaseAccepted',False)
 if current:assert d['passed'],path
 for rel,value in d.get('inputs',{}).items():
  p=root/rel
  if current or (p.exists() and sha(p)==value):assert sha(p)==value,(path,rel)
  else:assert sha(path.parent/'inputs'/rel)==value,(path,rel,'historical input snapshot')
 for rel,value in d.get('artifacts',{}).items():
  p=path.parent/rel;assert sha(p)==value,(path,rel);declared.add(str(p.relative_to(root)))
 for rel,value in d.get('runnerInputs',{}).items():assert sha(root/'qa'/rel)==value
 for row in d.get('reports',{}).values():
  p=pathlib.Path(row['path']);assert sha(p)==row['sha256'];verify(p,current)
 if 'compiledControls' in d:
  row=d['compiledControls'];p=pathlib.Path(row['path']);assert sha(p)==row['sha256'];verify(p,current)
  assert sha(p.parent/'checks')==row['binarySHA256']
 if 'pluginResourceHeaderSHA256' in d:assert sha(root.parent/'warlock-family-style-crop-capture-v19/native/capture-resources.hpp')==d['pluginResourceHeaderSHA256']
 assert all(x['exitCode']==0 for x in d.get('commands',[]) if current),path
 verified.add(path);return d
reports={k:verify(p,True) for k,p in paths.items()}
n=reports['nativeElmOutbox']['evidence'];assert n['checks']==192 and n['singlePreviewPolicy'] and n['normalOwnedExit'] and n['realmEpochs']==2 and n['nativeGrantResets']==0 and n['syntheticNativeRemainsActive']
assert reports['packetizer']['evidence']['checks']==43 and reports['packetizer']['evidence']['purePacketization']
q=reports['model'];assert q['namedScenarios']==12 and q['invariantSamples']==200 and q['unsafeCompiledNativeVariantsDetected']==5 and q['evidence']['statesCompared']==300 and len(q['evidence']['coupledTraces'])==22 and all(x['normalOwnedExit'] for x in q['evidence']['coupledTraces'])
b=reports['build'];assert len(b['commands'])==104 and sha(paths['build'].parent/'elm-host')==b['binarySHA256']
assert len(reports['resource']['reports'])==4 and len(reports['scoped']['reports'])==4
a=json.loads((root/'ANCESTRY.json').read_text());parent=pathlib.Path(a['parent']);m=parent/'component-manifest.json';assert sha(m)==a['parentManifestSHA256'];prior=json.loads(m.read_text());assert prior['sourceHeld'] and prior['passed']
for rel,row in prior['files'].items():assert sha(parent/rel)==row['sha256'],rel
changed={'native/imported-clients.h','native/imported-clients.cpp','src/Popup.elm'}
for base in ['native','assets','adapter','src']:
 for p in (parent/base).glob('*'):
  if p.is_file() and str(p.relative_to(parent)) not in changed:assert sha(root/base/p.name)==sha(p),p
old=json.loads(pathlib.Path(prior['reports']['build']['path']).read_text());assert [x['name'] for x in b['commands'] if x['name']!='native-proposals-syntax']==[x['name'] for x in old['commands']]
history=[];failed=[]
for p in sorted((root/'qa').glob('*/report.json')):
 if p in verified:continue
 d=verify(p);history.append({'path':str(p),'sha256':sha(p),'passed':d['passed'],'qualifiesFinalSource':False})
 if not d['passed']:failed.append(str(p))
assert len(failed)==1
result={'schema':1,'owner':a['owner'],'sourceHeld':True,'passed':True,'evidenceIntegrityPassed':True,'reports':{k:{'path':str(p),'sha256':sha(p)} for k,p in paths.items()},'historicalPhaseReports':history,'heldFailedReports':failed,'singlePreviewPolicy':True,'nativeProposalIngressImplemented':True,'pureProposalPacketizerImplemented':True,'popupTypedPortsCompiled':True,'popupTypedPortsWebKitExecuted':False,'nativeElmOutboxChecks':192,'packetizerChecks':43,'realmEpochs':2,'nativeGrantResets':0,'ingressScenarios':12,'ingressTraces':22,'ingressStates':300,'ingressSamples':200,'unsafeCompiledNativeVariantsDetected':5,'fullBuildCommands':104,'originalBuildCommands':103,'resourceRegressionSuites':4,'scopedRegressionSuites':4,'parentPresenterUnchanged':True,'parentAdapterAndLegacyAssetsUnchanged':True,'parentManifest':str(m),'parentManifestSHA256':sha(m),'proposalRetentionQualified':False,'fullElmRecoveryQualified':False,'typedHostRoutingActivated':False,'webKitActivated':False,'actualWaylandWindowAcceptance':False,'nativeAcceptance':False,'fullReleaseAccepted':False,'scope':(root/'INGRESS-HANDOFF.md').read_text()}
files={}
for p in sorted(root.rglob('*')):
 rel=p.relative_to(root);name=str(rel)
 if any(part in {'elm-stuff','mutable-elm-home','elm-home','__pycache__'} for part in rel.parts) and 'toolchain' not in rel.parts and name not in declared:continue
 assert not p.is_symlink(),p
 if p.is_file():files[name]={'kind':'file','sha256':sha(p),'size':p.stat().st_size,'mode':oct(stat.S_IMODE(p.stat().st_mode))}
result['files']=files;assert not (root/'component-manifest.json').exists();(root/'component-manifest.json').write_text(json.dumps(result,indent=2)+'\n')
out=pathlib.Path(__file__).parent/'component-report114.json';assert not out.exists();out.write_text(json.dumps({k:v for k,v in result.items() if k!='files'},indent=2)+'\n')
task=repo/'openspec/changes/warlock-preview-actor-retirement/tasks.md';s=task.read_text();old='- [ ] Freeze CONTROL-027 exact native proposal ingress';assert s.count(old)==1;s=s.replace(old,'- [x] Freeze CONTROL-027 exact native proposal ingress');s+='\nGUI114 qualifies native ingress192, pure packetization43, Quint12/22 actual C\ntraces/300 states/200 samples/five compiled admission variants and full104\nretaining103. All four current resource and four scoped suites pass. Popup typed\nports compile;actual WebKit execution remains unqualified. One failed runner\nanchor attempt remains. Pre-issuance proposal retention, actual host activation\nand full Elm context recovery remain open.\n';task.write_text(s)
sys.path.insert(0,str(repo/'implementation/elm-build-loop-v1'));import loop
print(loop.write_checkpoint(repo,a['owner'],str(root.relative_to(repo)),['PROGRESS heldGUI114 exact native realm proposal ingress/pure ordered packetizer/actual Popup typed ports compiled. Current C+Elm+outbox192/two epochs/unchanged Native grant/same synthetic Active subject/normal exits; codec43; Quint12/22 actualC traces/300 states/200 samples/five compiled variants; full104 retains103; current resource4+scoped4 suites. One failed runner anchor retained. New host/HTML/adapter route inactive; actual Popup WebKit port execution unqualified. Next PUBLIC83 then GUI115 retained original Elm proposal ingress before native ticket issuance; full Elm context recovery/real WebKit/Core/Wayland activation and original release gates open. Native130 legacy2518/278/full cleanup remains actual baseline; no installed changes.'],'progress',[str((root/'component-manifest.json').relative_to(repo)),str(out.relative_to(repo))]))
print(json.dumps({'heldFiles':len(files),'fullBuildCommands':104,'failedAttemptsHeld':len(failed)}))
