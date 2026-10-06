"""Freeze complete native122 observation evidence and unchanged original controls."""
import hashlib, importlib.util, json, pathlib, re, resource, stat, sys
sys.path.insert(0,'/home/hoskinson/window-integration-qa')
from qa_launch import require_qa_scope
require_qa_scope()
assert resource.getrlimit(resource.RLIMIT_CORE)==(1,1)
repo=pathlib.Path('/home/hoskinson/omarchy-windows-parity')
root=repo/'implementation/warlock-client-provider-native-v122'
sha=lambda path:hashlib.sha256(path.read_bytes()).hexdigest()
path=next(root.glob('qa/native-*/report.json'));proof=json.loads(path.read_text())
assert proof['passed'] and proof['cleanupPassed'] and all(row['passed'] for row in proof['checks'])
assert all(row['exitCode']==0 for row in proof['ownedExitCodes'])
for name,value in proof['artifacts'].items():assert sha(path.parent/name)==value,name
preflight=json.loads((root/'qa/preflight.json').read_text());assert preflight['passed']
for name,value in preflight['inputs'].items():assert sha(pathlib.Path(name))==value,name
spec=importlib.util.spec_from_file_location('reuse_comparison',root/'qa/reuse_comparison.py');audit=importlib.util.module_from_spec(spec);spec.loader.exec_module(audit)
readonly={'styleDimPendingNativeReadonlyScope','styleAgainDimPendingNativeReadonlyScope','styleRestoreIntermediateReadonlyScope','styleCropDimIntermediateReadonlyScope'}
def stable(rows):return [re.sub(r'^opacityPrivateForeignWindowMoved-0x[0-9a-f]+$','opacityPrivateForeignWindowMoved-<native-address>',row['name']) for row in rows if row['name'] not in readonly]
previous=json.loads(pathlib.Path(preflight['retainedNative118Report']).read_text());comparison=audit.compare(previous,proof,stable)
assert comparison==proof['addressReuseComparisonEvidence'] and comparison['fixedOrderedControls']==2437
observations=proof['incarnationRetirementNativeEvidence']['observations']
assert proof['nativeIncarnationRetirementObservationBoundedQualified']
assert [row['state'] for row in observations]==['Active','Future','Active','Retired','Active']
owner=observations[0]['binding'];lastSequence=lastNow=lastFrontier=0
for row in observations:
 assert row['binding']==owner and row['clock']==owner['lifetime'] and row['protocolVersion']==3 and row['retirementProtocol']==1
 assert int(row['sequence'])>lastSequence and int(row['now'])>=lastNow and int(row['issuedThrough'])>=lastFrontier
 assert (int(row['subjectIncarnation'])>int(row['issuedThrough']))==(row['state']=='Future')
 lastSequence,lastNow,lastFrontier=map(int,[row['sequence'],row['now'],row['issuedThrough']])
evidence=proof['incarnationRetirementNativeEvidence']
assert evidence['foreign']=={'protocolVersion':3,'kind':'refused','reason':'binding-mismatch'}
assert evidence['zero']['kind']=='refused' and not evidence['physicalRetirementAccepted'] and not evidence['actorTurnoverAccepted']
for name in ['stoppedActualFirstClassMinimized','receiverGrowthThirdSourceNormalExit','allPriorNative116StableOrderedAssertionsRetained','allPriorNative118FixedOrderedAndActualRetryAssertionsRetained']:
 assert any(row['name']==name and row['passed'] for row in proof['checks']),name
nativeManifest=pathlib.Path(preflight['incarnationRetirementManifest']);nativeHeld=json.loads(nativeManifest.read_text());assert nativeHeld['passed'] and nativeHeld['sourceHeld']
for name,row in nativeHeld['files'].items():assert sha(nativeManifest.parent/name)==row['sha256'],name
provider=repo/'implementation/warlock-preview-provider-v84/component-manifest.json';gui=json.loads(provider.read_text());assert gui['passed'] and gui['sourceHeld']
for name,row in gui['files'].items():assert sha(provider.parent/name)==row['sha256'],name
typed=proof['typedNativeRetirementEvidence'];assert proof['typedNativeRetirementObservationBoundedQualified'] and typed['normalExit'] and typed['complete']['passed'] and not typed['complete']['actorTurnoverAccepted']
facts=typed['observations'];assert [row['state'] for row in facts]==['Active','Active','Retired','Active']
assert facts[0]['subject']==facts[2]['subject'] and facts[1]['subject']==facts[3]['subject'] and facts[0]['subject']!=facts[1]['subject']
assert all(row['kind']=='native-incarnation-retirement' and row['binding']==facts[0]['binding'] and row['clock']==facts[0]['binding']['lifetime'] for row in facts)
assert all(int(b['sequence'])>int(a['sequence']) and int(b['now'])>=int(a['now']) and int(b['issuedThrough'])>=int(a['issuedThrough']) for a,b in zip(facts,facts[1:]))
assert all(int(row['subject'])<=int(row['issuedThrough']) for row in facts)
prior121=json.loads(pathlib.Path(preflight['retainedNative121Report']).read_text());comparison121=audit.compare(prior121,proof,stable)
assert any(row['name']=='allPriorNative121FixedOrderedAndActualRetryAssertionsRetained' and row['passed'] and row['evidence']==comparison121 for row in proof['checks'])
for field in ['retirementDecoderReport','retirementCReport']:
 current=pathlib.Path(gui[field]);checked=json.loads(current.read_text());assert checked['passed']
 for rel,value in checked['inputs'].items():assert sha(provider.parent/rel)==value,rel
 for rel,value in checked['artifacts'].items():assert sha(current.parent/rel)==value,rel
files={}
for source in sorted(root.rglob('*')):
 rel=source.relative_to(root)
 if '__pycache__' in rel.parts:continue
 assert not source.is_symlink(),source
 if source.is_file():files[str(rel)]={'kind':'file','sha256':sha(source),'size':source.stat().st_size,'mode':oct(stat.S_IMODE(source.stat().st_mode))}
manifest=root/'component-manifest.json';assert not manifest.exists()
manifest.write_text(json.dumps({'schema':1,'owner':'f6779148-8f5d-4bdf-8a0f-044184e486f2','sourceHeld':True,'passed':True,'evidenceIntegrityPassed':True,'files':files,
 'nativeReport':str(path),'nativeReportSHA256':sha(path),'nativeModuleManifest':str(nativeManifest),'nativeModuleManifestSHA256':sha(nativeManifest),
 'providerManifest':str(provider),'providerManifestSHA256':sha(provider),'nativeChecks':len(proof['checks']),'normalOwnedExits':len(proof['ownedExitCodes']),
 'prior118FixedOrderedControls':2437,'nativeIncarnationRetirementObservationBoundedQualified':True,
 'typedNativeRetirementObservationBoundedQualified':True,'prior121FixedOrderedControls':comparison121['fixedOrderedControls'],'typedNativeRetirementEvidence':typed,'nativeAcceptance':False,'fullReleaseAccepted':False},indent=2)+'\n')
report={'passed':True,'nativeManifest':str(manifest),'nativeManifestSHA256':sha(manifest),'nativeReport':str(path),
 'nativeModuleManifest':str(nativeManifest),'nativeModuleManifestSHA256':sha(nativeManifest),'providerManifest':str(provider),'providerManifestSHA256':sha(provider),
 'nativeChecks':len(proof['checks']),'normalOwnedExits':len(proof['ownedExitCodes']),'prior118FixedOrderedControls':2437,'addressReuseComparison':comparison,
 'nativeRetirementStates':['Active','Future','Active','Retired','Active'],'selectedClassifierScenarios':8,'classifierTraces':20,'classifierStates':438,'unsafeClassifierMutants':2,'unsafeComparisonMutants':8,
 'nativeIncarnationRetirementObservationBoundedQualified':True,'typedNativeRetirementObservationBoundedQualified':True,'typedNativeRetirementEvidence':typed,'prior121FixedOrderedControls':comparison121['fixedOrderedControls'],'typedDecoderScenarios':13,'typedDecoderTraces':25,'typedDecoderStates':439,'unsafeDecoderMutants':3,'retirementCChecks':96,'actorTurnoverAccepted':False,'ordinaryEligibleCaptureAccepted':False,
 'nativeAcceptance':False,'fullReleaseAccepted':False,
 'next':'Commit/publish exact held failedGUI83/passedGUI84/native122 evidence. Fresh GUI85 replaces vector index identities with bounded active membership and nonreused monotonic entry serials, full build66449 running. Integrate atomic proof-safe physical/journal/receiver/Coordinator/Broker/ledger/C retirement and exact Elm settlement facts, then actual more-than256 window turnover; ordinary capture and all original release gates remain.'}
(repo/'docs/warlock-preview/v84/report.json').write_text(json.dumps(report,indent=2)+'\n')
sys.path.insert(0,str(repo/'implementation/elm-build-loop-v1'));import loop
print(loop.write_checkpoint(repo,'f6779148-8f5d-4bdf-8a0f-044184e486f2',str(root.relative_to(repo)),
 ['PROGRESS native122 exact core16/plugin18/currentGUI84 PASS '+str(len(proof['checks']))+'/'+str(len(proof['ownedExitCodes']))+'normalclean. Real owning C/bootstrap/socket/ImportedClients typed Active/Retired/liveNeighbor observations, native clocks/cursors/frontier and original untouched reservations/exact final journal ACKs; all original121 fixed gates and actual allocator trials verified. Current GUI84 full95/all original suites/decoder13/25/439states/3mutants/C96 pass; failed83 held. PUBLIC59 ba21f432 source83e294 and receipt70d888. Fresh GUI85 serial registry/fullcompile66449, then atomic actor/history retirement beyond256 and all original release gates; main desktop/drafts preserved, no full release claim.'],
 'progress',[str(manifest.relative_to(repo)),'docs/warlock-preview/v84/report.json']))
