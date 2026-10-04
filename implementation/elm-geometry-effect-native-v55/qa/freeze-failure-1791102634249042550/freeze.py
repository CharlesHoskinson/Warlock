"""Append-only qualified singleton geometry freeze; protected CPU, never GUI."""
import hashlib,json,os,resource,stat,sys,time
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1];REPO=ROOT.parents[1]
LANES=['elm-window-geometry-effects-negotiated-v48','elm-geometry-native-contract-tests-v50','elm-geometry-effect-native-v51','elm-geometry-client-suspend-v53','elm-geometry-effect-native-v54','elm-geometry-effect-native-v55']
NATIVE=ROOT/'qa/native-1791102357953536490/report.json'
CPU=REPO/'implementation/elm-geometry-native-contract-tests-v50/qa/contract-1791101638979185401/report.json'
DOC=REPO/'docs/elm-roadmap/delivery/GEOMETRY-NATIVE-V55-ACCEPTANCE.md'
PAIR=REPO/'implementation/elm-window-geometry-owning-pair-v49'
CORE=REPO/'implementation/elm-window-geometry-default-limits-v40'
LEGACY=REPO/'implementation/elm-geometry-menu-regression-v52/component-manifest.json'
def sha(path):return hashlib.sha256(Path(path).read_bytes()).hexdigest()
def read(path):return json.loads(Path(path).read_text())
def artifacts(report,path):
 for rel,wanted in report.get('artifacts',{}).items():assert sha(Path(path).parent/rel)==wanted,(path,rel)
def manifest_check(path,wanted):
 assert sha(path)==wanted,path
 m=read(path);assert m['passed'] is True,path
 base=Path(m.get('inventoryBase',Path(path).parent))
 if isinstance(m['files'],dict):
  for rel,h in m['files'].items():assert sha(base/rel)==h,(path,rel)
 else:
  for e in m['files']:
   p=base/e['path']
   if 'symlink' in e:assert p.is_symlink() and os.readlink(p)==e['symlink'],p
   else:
    assert p.is_file() and not p.is_symlink() and sha(p)==e['sha256'] and p.stat().st_size==e['size'],p
    if 'mode' in e:assert stat.S_IMODE(p.stat().st_mode)==e['mode'],p
 return m
def inventory(root,excluded):
 result=[]
 for p in sorted(root.rglob('*')):
  if p in excluded:continue
  if p.is_symlink():result.append({'path':str(p.relative_to(root)),'symlink':os.readlink(p)})
  elif p.is_file():result.append({'path':str(p.relative_to(root)),'size':p.stat().st_size,'mode':stat.S_IMODE(p.stat().st_mode),'sha256':sha(p)})
 return result
sys.path.insert(0,'/home/hoskinson/window-integration-qa')
from qa_launch import require_qa_scope
scope=require_qa_scope();assert resource.getrlimit(resource.RLIMIT_CORE)==(1,1)
roots=[REPO/'implementation'/name for name in LANES];targets=[root/'component-manifest.json' for root in roots]
assert not any(p.exists() for p in targets),'Never replace component manifests'
native=read(NATIVE);assert native['passed'] is True and native['cleanupPassed'] is True and native['mainDesktopActions'] is False and native['menuTransportIntegrated'] is False
assert len(native['checks'])==96 and all(c['passed'] is True for c in native['checks'])
for p,w in native['inputs'].items():assert sha(p)==w,p
artifacts(native,NATIVE)
assert sha(ROOT/'qa/native.py')==native['inputs'][str(ROOT/'qa/native.py')]==sha(NATIVE.parent/'native.py')
pixel_checks=[c for c in native['checks'] if c['name'].endswith(':actualInteriorPixelsMatchSelectedConfigure')]
assert len(pixel_checks)==7 and len(native['pixelAttempts'])==7
for c in pixel_checks:
 assert all(sample==c['expectedRGB'] for sample in c['capture']['samples'])
 archived=NATIVE.parent/'native-evidence'/Path(c['capture']['path']).name
 assert sha(archived)==c['capture']['sha256'],archived
private=native['privateHost'];assert private['runtimeGone'] is True and private['mainDisplayUsed'] is False
for field in ['cleanupErrors','unexpectedInnerDescendants','remainingDescendants']:assert not private[field],field
assert not native.get('clientCleanupError') and not native.get('pluginCleanupError')
byname={c['name']:c for c in native['checks']}
assert byname['maxOriginalSurvivesFrontendHello']['geometry']['ordinaryPlacementKnown'] is True
minimized=byname['minimize-maximized:retainsMaximizedModeAndOriginal']['buffer'];assert minimized['suspended'] is True
restored=byname['restore-minimized-maximized:exactNativePlacement']['buffer'];assert restored['suspended'] is False and restored['sequence']>minimized['sequence']
assert byname['exactGeometryRetryReturnsOriginalReceipt']['passed'] and byname['effectVersionCannotReuseSharedIdentity']['passed'] and byname['changedPayloadSameIdentityRefused']['passed']
assert all(x['receipt']['status']=='Committed' and x['receipt']['intent']==x['intent'] for x in native['effectReceipts'])
assert [x['receipt']['effectProtocol'] for x in native['effectReceipts']]==[2,2,1,1,2,2]
pair_manifest=PAIR/'qa/build-pair-manifest.json'
pair=manifest_check(pair_manifest,'bd2e92fafa05355a0fb1fb07fadc5ff83f1e42a446dc00aad3ea8c120afbd81b')
core_manifest=CORE/'component-manifest.json';manifest_check(core_manifest,'dd924d35c3568b4b0e0434bbc2eb841789e69c4451806a6a62659111180ca712')
descriptor=read(PAIR/'native-build-report.json');plugin_report=Path(descriptor['pluginBuildReport']);assert sha(plugin_report)==descriptor['pluginBuildReportSHA256']
build=read(plugin_report);assert build['passed'] and not build['missingSymbols'] and len(build['owningHeaders'])==691 and build['strongUndefinedCount']==152
for section in ['dependencies','coreDependencies','coreLinkDependencies','tools','linkedLibraries']:
 for p,w in build[section].items():assert sha(p)==w,p
for rel,w in build['inputs'].items():assert sha(PAIR/rel)==sha(plugin_report.parent/'inputs'/rel)==w,rel
for rel,w in build['owningHeaders'].items():assert sha(plugin_report.parent/'owning-headers'/rel)==w,rel
for field in ['linkClosureReport','coreDescriptor','coreClosureReport','coreConsumerAudit','coreLimitsReport','parentManifest','parentBuildReport']:assert sha(build[field])==build[field+'SHA256'],field
artifacts(build,plugin_report)
for rel,w in build['sourceLineage']['sourceFiles'].items():assert sha(Path(build['sourceLineage']['source'])/rel)==sha(PAIR/rel)==w,rel
assert native['pluginBuild']==str(plugin_report) and native['pluginSHA256']==build['binarySHA256']==sha(build['binary'])
core=native['coreBuild'];assert core['binary']==build['core']['path'] and core['sha256']==build['core']['sha256']==sha(core['binary'])
for field in ['buildReport','closureReport']:assert sha(core[field])==core[field+'SHA256'],field
assert private['hyprlandMaps']['files'][str(Path(core['binary']).resolve())]==core['sha256']
assert native['pluginMapsAfterLoad']['files'][str(Path(build['binary']).resolve())]==build['binarySHA256']
aq=private['privateAquamarine'];assert aq['mappedVerified'] is True and sha(aq['path'])==aq['sha256']==private['hyprlandMaps']['files'][str(Path(aq['path']).resolve())]
aq_desc=read(CORE/'core/aq-tuple.json');manifest_check(aq_desc['manifest'],aq_desc['manifestSHA256']);assert aq_desc['librarySHA256']==aq['sha256']
fixture_root=REPO/'implementation/elm-geometry-client-suspend-v53';fixture=read(fixture_root/'client-build-report.json')
assert sha(fixture_root/'client-build-report.json')=='a6fa464f3390d64e8e18b3275d1cbb2d5cc2b5bed55df635fc27166f347911cc' and fixture==native['clientBuild']
assert fixture['requiresXdgVersion']==6 and fixture['suspendedStateObserved'] is True
assert sha(fixture['client'])==fixture['clientSHA256'] and sha(fixture['buildReport'])==fixture['buildReportSHA256']
client_build=read(fixture['buildReport']);assert client_build['passed'] and client_build['stateTests']['passed']
assert len(client_build['stateTests']['checks'])==5 and all(c['passed'] for c in client_build['stateTests']['checks'])
for section in ['inputs','dependencies','tools','linkedLibraries']:
 for p,w in client_build[section].items():assert sha(p)==w,p
artifacts(client_build,fixture['buildReport'])
cpu=read(CPU);assert cpu['passed'] and cpu['nativeAcceptance'] is False and len(cpu['checks'])==8 and all(x['passed'] for x in cpu['checks'])
assert cpu['checks'][0]['stdout']=='checks 296\n';artifacts(cpu,CPU)
for rel,w in cpu['inputs'].items():assert sha(roots[0]/rel)==w,rel
assert sha(roots[1]/'qa/test.py')==sha(CPU.parent/'test.py')
preflight=ROOT/'qa/preflight-1791102259102730218/report.json';p=read(preflight);assert p['passed'] and p['nativeAcceptance'] is False and p['runnerSHA256']==sha(ROOT/'qa/native.py');artifacts(p,preflight)
old=REPO/'implementation/elm-geometry-effect-native-v51/qa/preflight-1791102156356623552/report.json';o=read(old);assert o['passed'] and o['nativeAcceptance'] is False and sha(old.parent/'native.py')==o['runnerSHA256'];artifacts(o,old)
failure=REPO/'implementation/elm-geometry-effect-native-v54/qa/preflight-1791102233943763456/report.json';f=read(failure);assert f['passed'] is False and f['nativeAcceptance'] is False and 'xdgVersion' in f['error'];artifacts(f,failure)
manifest_check(LEGACY,'8a7bb989909ae5572dc3152c67779293c72f9b989cefcabac747b3cb34b391e7')
qualification={'report':str(NATIVE),'reportSHA256':sha(NATIVE),'nativeChecks':96,'pixelChecks':7,'normalCleanup':True,'mainDesktopActions':False,'nativeCore':core,'plugin':{'path':build['binary'],'sha256':build['binarySHA256']},'aquamarine':{'path':aq['path'],'sha256':aq['sha256']},'client':fixture,'pairManifest':str(pair_manifest),'pairManifestSHA256':sha(pair_manifest),'coreManifest':str(core_manifest),'coreManifestSHA256':sha(core_manifest),'contractCPU':str(CPU),'contractCPUSHA256':sha(CPU),'legacyMenuManifest':str(LEGACY),'legacyMenuManifestSHA256':sha(LEGACY),'preflight':str(preflight),'preflightSHA256':sha(preflight),'historicalOldFixtureCPU':str(old),'historicalOldFixtureCPUSHA256':sha(old),'failedDescriptorKeyPreflight':str(failure),'failedDescriptorKeyPreflightSHA256':sha(failure)}
common={'schema':1,'passed':True,'frozenUTCUnixNs':time.time_ns(),'qaScope':scope,'geometryNativeAccepted':True,'geometryMenuAccepted':False,'fullRoadmapAccepted':False,'unknownNativeFaultRecoveryAccepted':False,'competingPeersAccepted':False,'workareaOwnershipChangeAccepted':False,'releaseAccepted':False,'deploymentAccepted':False,'quintGeometryModelLogicApproved':False,'scope':'Isolated singleton native effect2 maximize/restore geometry + legacy minimized MAX composition; CPU and historical failures separately attributed','nativeQualification':qualification,'acceptanceDocument':str(DOC),'acceptanceDocumentSHA256':sha(DOC)}
packets=[dict(common,component=root.name,files=inventory(root,set(targets))) for root in roots]
for target,packet in zip(targets,packets):
 with target.open('x') as output:output.write(json.dumps(packet,indent=2)+'\n')
 target.chmod(0o444)
print(json.dumps({'passed':True,'nativeChecks':96,'pixelChecks':7,'manifests':{str(t):sha(t) for t in targets},'acceptanceDocumentSHA256':sha(DOC)}),flush=True)
