"""Freeze exact full successor component with separate native-release claims."""
import hashlib,json,pathlib,resource,stat,sys
sys.path.insert(0,'/home/hoskinson/window-integration-qa');from qa_launch import require_qa_scope
require_qa_scope();assert resource.getrlimit(resource.RLIMIT_CORE)==(1,1)
r=pathlib.Path('/home/hoskinson/omarchy-windows-parity');root=r/'implementation/warlock-preview-provider-v80';sha=lambda p:hashlib.sha256(p.read_bytes()).hexdigest()
def only(pattern):
 rows=list(root.glob(pattern));assert len(rows)==1,rows;return rows[0]
def verify(p):
 d=json.loads(p.read_text());assert d['passed'],(p,d.get('error'))
 for rel,h in d['inputs'].items():assert sha(pathlib.Path(rel) if pathlib.Path(rel).is_absolute() else root/rel)==h,rel
 for rel,h in d.get('artifacts',{}).items():assert sha(p.parent/rel)==h,rel
 return d
bp=only('qa/build-*/report.json');b=verify(bp);assert len(b['commands'])==95 and all(row['exitCode']==0 for row in b['commands'])
for section in ['compilerDependencies','linkedLibraries','tools']:
 for path,row in b[section].items():assert sha(pathlib.Path(path))==row['sha256'],path
assert sha(bp.parent/'elm-host')==b['binarySHA256'];reports={}
for key,pattern,names in [('modelReport','qa/check-*/report.json',10),('deliveryModelReport','qa/delivery-check-*/report.json',6),('resumeModelReport','qa/resume-model-check-*/report.json',8),('intentModelReport','qa/intent-check-*/report.json',6),('enrollmentModelReport','qa/enrollment-check-*/report.json',8),('receiptModelReport','qa/receipt-check-*/report.json',8),('metadataModelReport','qa/metadata-check-*/report.json',8),('catalogModelReport','qa/catalog-check-*/report.json',8)]:
 p=only(pattern);d=verify(p);assert d['namedScenarios']==names;reports[key]=str(p)
 if 'compiledBuild' in d:assert d['compiledBuild']=={'path':str(bp),'sha256':sha(bp)}
fp=only('qa/feedback-check-*/report.json');f=verify(fp);assert f['namedScenarios']==9 and len(f['coupledTraces'])==21 and f['guardControls']['checks']==43 and f['nativeFixtureControls']['checks']==18;reports['feedbackReport']=str(fp)
assert f['fullBuild']=={'path':str(bp),'sha256':sha(bp)}
cp=only('qa/resume-check-*/report.json');c=verify(cp);assert c['checks']==79 and c['elmEvidence']['checks']==17;reports['resumeCReport']=str(cp)
np=only('qa/next-intent-check-*/report.json');n=verify(np);assert n['namedScenarios']==10 and len(n['coupledTraces'])==22 and n['unsafeMutantsDetected']==2 and n['wireControls']['checks']==21 and n['wireControls']['cControls']==45;reports['nextIntentReport']=str(np)
assert n['fullBuild']=={'path':str(bp),'sha256':sha(bp)}
evidence={}
for name in ['catalog-enrollment-replay','delivery-extension-physical-tests','metadata-privacy-replay','metadata-icon-physical-tests','receiver-extension-physical-tests','imported-admission-tests','imported-lifecycle-tests']:
 d=json.loads((bp.parent/(name+'.stdout')).read_text());assert d['passed'];evidence[name]=d
evidence['dynamic-enrollment-tests']=json.loads((bp.parent/'dynamic-enrollment-tests.stdout').read_text().splitlines()[-1]);assert evidence['dynamic-enrollment-tests']['checks']==34
files={}
for p in sorted(root.rglob('*')):
 rel=p.relative_to(root)
 if any(part in {'elm-stuff','mutable-elm-home','elm-home','__pycache__'} for part in rel.parts) and 'toolchain' not in rel.parts:continue
 assert not p.is_symlink(),p
 if p.is_file():files[str(rel)]={'kind':'file','sha256':sha(p),'size':p.stat().st_size,'mode':oct(stat.S_IMODE(p.stat().st_mode))}
m=root/'component-manifest.json';assert not m.exists()
m.write_text(json.dumps({'schema':1,'owner':'f6779148-8f5d-4bdf-8a0f-044184e486f2','passed':True,'sourceHeld':True,'buildReport':str(bp),**reports,'files':files,'evidence':evidence,'evidenceIntegrityPassed':True,'nativeAcceptance':False,'fullReleaseAccepted':False,'scope':'Full95 current Elm/native build; explicit successor10 selected cases/22 actual ledger/Broker traces with bounded predecessor and monotonic stamp; two actual unsafe native mutants detected; actual C/socket/bootstrap/delivery45 plus optimized Elm21 wire controls. Current original feedback/resume/receipt/metadata/catalog and five native models pass. Native GUI successor scheduling/image/reopen, expired resume intents, actor retirement, ordinary eligibility and all original release gates remain open.'},indent=2)+'\n')
report={'passed':True,'providerManifest':str(m),'providerManifestSHA256':sha(m),'buildCommands':95,'nextIntentScenarios':10,'nextIntentTraces':22,'nextIntentStates':n['statesCompared'],'unsafeMutantsDetected':2,'nativeCControls':45,'elmWireControls':21,'legacyResumeControls':79,'feedbackScenarios':9,'nativeAcceptance':False,'fullReleaseAccepted':False,'next':'Prioritize unissued subjects before resumed actors and qualify actual GUI successor image after native expiry/reopen. Continue resume-intent succession, proof-safe actor/history retirement, ordinary eligibility and all original release gates.'}
(r/'docs/warlock-preview/v80/report.json').write_text(json.dumps(report,indent=2)+'\n')
sys.path.insert(0,str(r/'implementation/elm-build-loop-v1'));import loop
print(loop.write_checkpoint(r,'f6779148-8f5d-4bdf-8a0f-044184e486f2',str(root.relative_to(r)),['PROGRESS80 full unissued-priority successor component held: full95/new10/22traces/'+str(n['statesCompared'])+'states/2unsafeMutants/C45Elm21; originalfeedback9/resume79/receiptmetadata/catalog/fivenativeModels currentpass. ActualGUI successor liveness remains open: resumeorder can refillpool beforeunissuedthird. Current80 unissuedpriority compiled; nextnative115 ownABI GUI expiry/reopen/image/cleanup. Full original release scope preserved.'],'progress',[str(m.relative_to(r)),'docs/warlock-preview/v80/report.json']))
