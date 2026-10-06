import hashlib,json,pathlib,resource,stat,sys
sys.path.insert(0,'/home/hoskinson/window-integration-qa');from qa_launch import require_qa_scope
require_qa_scope();assert resource.getrlimit(resource.RLIMIT_CORE)==(1,1)
REPO=pathlib.Path('/home/hoskinson/omarchy-windows-parity');OUT=pathlib.Path(__file__).parent
sha=lambda p:hashlib.sha256(pathlib.Path(p).read_bytes()).hexdigest()
root=REPO/'implementation/warlock-preview-provider-v32';builds=list((root/'qa').glob('build-*/report.json'));assert len(builds)==1;buildPath=builds[0];build=json.loads(buildPath.read_text());assert build['passed'] and all(row['exitCode']==0 for row in build['commands'])
oldPath=REPO/'implementation/warlock-preview-provider-v31/qa/build-1791263130169139602/report.json';old=json.loads(oldPath.read_text());assert old['passed'];oldNames=[row['name'] for row in old['commands']];assert [row['name'] for row in build['commands'] if row['name'] in set(oldNames)]==oldNames
for rel,h in build['inputs'].items():assert sha(root/rel)==h,rel
for section in ['compilerDependencies','linkedLibraries','tools']:
 for path,row in build[section].items():assert sha(path)==row['sha256'],path
assert sha(buildPath.parent/'elm-host')==build['binarySHA256']
for rel,h in build['artifacts'].items():assert sha(buildPath.parent/rel)==h,rel
coupled=json.loads((buildPath.parent/'family-source-coupled-decoder.stdout').read_text());assert coupled['passed'] and coupled['checks']==107 and coupled['nativeScopes']==3 and coupled['malformedScopes']==43
fdProof=json.loads((buildPath.parent/'family-fd-physical-tests.stdout').read_text());assert fdProof['passed'] and fdProof['checks']==295 and fdProof['physicalFDClosed'] and fdProof['physicalMappingClosed'] and fdProof['chargeReleasedAfterClose']
assert sha(root/'native/preview_fd.hpp')==sha(REPO/'implementation/warlock-preview-provider-v31/native/preview_fd.hpp')
fixture=json.loads((root/'qa/family-source-fixture.json').read_text());nativePath=pathlib.Path(fixture['nativeReport']);assert sha(nativePath)==fixture['sha256'];native=json.loads(nativePath.read_text());assert native['passed'] and native['cleanupPassed'] and fixture['scopes']==[row['source'] for row in native['styleCropCaptureSamples']]
for name in ['demand.hpp','preview_broker.hpp','client_producer.hpp','imported_clients.hpp','imported_lifecycle.hpp']:
 assert sha(root/'native'/name)==sha(REPO/'implementation/warlock-preview-provider-v30/native'/name),name
parentManifest=REPO/'implementation/warlock-preview-provider-v31/component-manifest.json';parent=json.loads(parentManifest.read_text());assert parent['sourceHeld']
for rel,row in parent['files'].items():assert sha(parentManifest.parent/rel)==row['sha256'],rel
files={};target=root/'component-manifest.json';assert not target.exists()
for p in sorted(root.rglob('*')):
 rel=p.relative_to(root)
 if any(part in ['__pycache__','elm-stuff','mutable-elm-home'] for part in rel.parts):continue
 assert not p.is_symlink(),p
 if p.is_file():files[str(rel)]={'kind':'file','sha256':sha(p),'size':p.stat().st_size,'mode':oct(stat.S_IMODE(p.stat().st_mode))}
metadata={'schema':1,'sourceHeld':True,'evidenceIntegrityPassed':True,'files':files,'nativeAcceptance':False,'fullReleaseAccepted':False,'previewEligible':False,'actualFamilyMetadataDecoderQualified':True,'compiledCommands':len(build['commands']),'retainedOriginalCommands':len(oldNames),'coupledDecoderChecks':107,'newNativeFamilyProviderTransportQualified':False,'physicalFamilyFDControls':295,'newFamilyQueryNativeQualified':False}
target.write_text(json.dumps(metadata,indent=2)+'\n');report=OUT/'report.json';assert not report.exists();report.write_text(json.dumps({'schema':1,'passed':True,'components':[{'path':str(target.relative_to(REPO)),'sha256':sha(target),'files':len(files)}],'evidence':{str(p.relative_to(REPO)):sha(p) for p in [buildPath,oldPath,parentManifest,nativePath]},'compiledCommands':len(build['commands']),'retainedOriginalCommands':len(oldNames),'coupledDecoderChecks':107,'physicalFamilyFDControls':295,'nativeAcceptance':False,'fullReleaseAccepted':False,'next':'Wire distinct family FD3/capture/PNG/URI into own shared provider and single Elm lifecycle, preserving actual native deadline/source checks and physical retirement; complete source/style/fidelity and original preview13/coherent release.'},indent=2)+'\n');print(json.dumps({'passed':True,'report':str(report),'compiledCommands':len(build['commands']),'retainedOriginalCommands':len(oldNames),'coupledDecoderChecks':107}))
