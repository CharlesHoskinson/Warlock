"""Freeze exact inactive native-issued renderer transport and current build."""
import hashlib,json,pathlib,resource,stat,sys
sys.path.insert(0,'/home/hoskinson/window-integration-qa');from qa_launch import require_qa_scope
require_qa_scope();assert resource.getrlimit(resource.RLIMIT_CORE)==(1,1)
repo=pathlib.Path('/home/hoskinson/omarchy-windows-parity');root=repo/'implementation/warlock-preview-provider-v111';sha=lambda p:hashlib.sha256(pathlib.Path(p).read_bytes()).hexdigest()
def verify(path):
 d=json.loads(path.read_text());assert d['passed'] and not d.get('nativeAcceptance',False) and not d.get('fullReleaseAccepted',False)
 for rel,value in d['inputs'].items():assert sha(root/rel)==value,(path,rel)
 for rel,value in d.get('artifacts',{}).items():assert sha(path.parent/rel)==value,(path,rel)
 return d
paths={'roundtrip':root/'qa/native-outbox-check-v4-1791354355501494232/report.json','protocol':root/'qa/native-outbox-protocol-check-1791354413823194560/report.json','model':root/'qa/native-outbox-model-check-1791354287844124126/report.json','build':next(root.glob('qa/build-*/report.json'))}
reports={k:verify(p) for k,p in paths.items()};c=reports['roundtrip']['evidence'];assert c['checks']==93 and c['normalOwnedExit'] and c['actualControlledC'] and c['realmEpochs']==2 and c['syntheticNativeRemainsActive']
p=reports['protocol']['evidence'];assert p['checks']==47 and p['fullUint64BindingAndEpoch'] and p['reentrantDepth']==1
q=reports['model'];assert q['namedScenarios']==14 and len(q['coupledTraces'])==26 and q['statesCompared']==463 and q['invariantSamples']==200 and q['unsafeActualJSVariantsDetected']==6
b=reports['build'];assert len(b['commands'])==97 and all(row['exitCode']==0 for row in b['commands']) and sha(paths['build'].parent/'elm-host')==b['binarySHA256']
a=json.loads((root/'ANCESTRY.json').read_text());parent=pathlib.Path(a['parent']);m=parent/'component-manifest.json';assert sha(m)==a['parentManifestSHA256'];previous=json.loads(m.read_text());assert previous['sourceHeld'] and previous['passed']
for rel,row in previous['files'].items():assert sha(parent/rel)==row['sha256'],rel
for name in ['src','assets','adapter','native']:
 for p in (parent/name).glob('*'):
  if p.is_file():assert sha(root/name/p.name)==sha(p),p
old=json.loads(pathlib.Path(previous['reports']['build']['path']).read_text());assert [row['name'] for row in b['commands'] if row['name']!='native-issued-outbox-syntax']==[row['name'] for row in old['commands']]
assert 'native-preview-control-outbox' not in (root/'assets/popup.html').read_text()
failed=[str(p) for p in sorted((root/'qa').glob('*/report.json')) if not json.loads(p.read_text()).get('passed',False)];assert len(failed)==3
native=repo/'implementation/warlock-client-provider-native-v130/component-manifest.json';n=json.loads(native.read_text());assert n['sourceHeld'] and n['passed'] and n['nativeChecks']==2518 and n['normalOwnedExits']==278 and n['currentGUI110LegacyRuntimeQualified']
for rel,row in n['files'].items():assert sha(native.parent/rel)==row['sha256'],rel
result={'schema':1,'owner':'f6779148-8f5d-4bdf-8a0f-044184e486f2','sourceHeld':True,'passed':True,'evidenceIntegrityPassed':True,'reports':{k:{'path':str(p),'sha256':sha(p)} for k,p in paths.items()},'nativeTicketRoundtripChecks':93,'protocolChecks':47,'realmEpochs':2,'syntheticNativeRemainsActive':True,'nativeOutboxScenarios':14,'nativeOutboxTraces':26,'nativeOutboxStates':463,'nativeOutboxSamples':200,'unsafeActualJSVariantsDetected':6,'fullBuildCommands':97,'originalBuildCommands':96,'unchangedProductParentManifest':str(m),'unchangedProductParentManifestSHA256':sha(m),'retainedLegacyNativeManifest':str(native),'retainedLegacyNativeManifestSHA256':sha(native),'retainedLegacyNativeChecks':2518,'retainedLegacyNativeNormalExits':278,'heldFailedReports':failed,'nativeIssuedRendererTransportImplemented':True,'rendererReloadRecoveryQualified':False,'typedHostRoutingActivated':False,'webKitActivated':False,'actualWaylandWindowAcceptance':False,'nativeAcceptance':False,'fullReleaseAccepted':False,'scope':(root/'NATIVE-OUTBOX-HANDOFF.md').read_text()}
files={}
for p in sorted(root.rglob('*')):
 rel=p.relative_to(root)
 if any(part in {'elm-stuff','mutable-elm-home','elm-home','__pycache__'} for part in rel.parts) and 'toolchain' not in rel.parts:continue
 assert not p.is_symlink(),p
 if p.is_file():files[str(rel)]={'kind':'file','sha256':sha(p),'size':p.stat().st_size,'mode':oct(stat.S_IMODE(p.stat().st_mode))}
result['files']=files;assert not (root/'component-manifest.json').exists();(root/'component-manifest.json').write_text(json.dumps(result,indent=2)+'\n')
out=pathlib.Path(__file__).parent/'component-report111.json';assert not out.exists();out.write_text(json.dumps({k:v for k,v in result.items() if k!='files'},indent=2)+'\n')
sys.path.insert(0,str(repo/'implementation/elm-build-loop-v1'));import loop
print(loop.write_checkpoint(repo,result['owner'],str(root.relative_to(repo)),['PROGRESS heldGUI111 inactive exact native-issued JS outbox. Actual controlled C93/two same-Active-subject epochs/unchanged Native grant/original strict barriers; protocol47/full uint64/UTF8/reentry; Quint14/26 actualJS traces/463 states/200 samples/six executable variants; full97 retains original96. Three fixture failures retained. Parent110 product files byte-identical; parent resource/scoped evidence stays110. Native130 current110 legacy2518/278/full cleanup PUBLIC79 remains bounded baseline. Next PUBLIC80 then original native ticket/prefix recovery and typed realm/actual WebKit/Core activation. Full release remains open; no installed changes.'],'progress',[str((root/'component-manifest.json').relative_to(repo)),str(out.relative_to(repo))]))
