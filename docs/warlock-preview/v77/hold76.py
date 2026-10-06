"""Hold current full feedback provider with exact compiled and coupled evidence."""
import hashlib,json,pathlib,resource,stat,sys
sys.path.insert(0,'/home/hoskinson/window-integration-qa');from qa_launch import require_qa_scope
require_qa_scope();assert resource.getrlimit(resource.RLIMIT_CORE)==(1,1)
r=pathlib.Path('/home/hoskinson/omarchy-windows-parity');root=r/'implementation/warlock-preview-provider-v76';sha=lambda f:hashlib.sha256(f.read_bytes()).hexdigest()
def only(base,pattern):
 rows=list(base.glob(pattern));assert len(rows)==1,rows;return rows[0]
def verify(base,p):
 d=json.loads(p.read_text());assert d['passed'],p
 for name,h in d['inputs'].items():assert sha(pathlib.Path(name) if pathlib.Path(name).is_absolute() else base/name)==h,name
 for name,h in d.get('artifacts',{}).items():assert sha(p.parent/name)==h,name
 return d
bp=only(root,'qa/build-*/report.json');b=verify(root,bp);assert len(b['commands'])==95 and all(row['exitCode']==0 for row in b['commands'])
for section in ['compilerDependencies','linkedLibraries','tools']:
 for name,row in b[section].items():assert sha(pathlib.Path(name))==row['sha256'],name
assert sha(bp.parent/'elm-host')==b['binarySHA256']
reports={}
for key,pattern,count in [('receiptModelReport','qa/receipt-check-*/report.json',214),('metadataModelReport','qa/metadata-check-*/report.json',210),('catalogModelReport','qa/catalog-check-*/report.json',214)]:
 p=only(root,pattern);d=verify(root,p);assert d['namedScenarios']==8 and d['statesCompared']==count and d['compiledBuild']=={'path':str(bp),'sha256':sha(bp)};reports[key]=str(p)
assert json.loads(pathlib.Path(reports['receiptModelReport']).read_text())['unsafeCounterexamplesDetected']==2
cp=only(root,'qa/resume-check-*/report.json');c=verify(root,cp);assert c['checks']==79 and c['elmEvidence']['checks']==17 and c['buildReport']==str(bp);reports['resumeCReport']=str(cp)
fp=only(root,'qa/feedback-check-*/report.json');f=verify(root,fp);assert f['namedScenarios']==9 and len(f['coupledTraces'])==21 and f['guardControls']['checks']==43 and f['nativeFixtureControls']['checks']==18 and [row['checks'] for row in f['nativeFixtureControls']['cases']]==[25,24]
assert f['fullBuild']=={'path':str(bp),'sha256':sha(bp)};reports['feedbackReport']=str(fp)
parent=root.parent/'warlock-preview-provider-v75';pm=parent/'component-manifest.json';pheld=json.loads(pm.read_text());assert pheld['sourceHeld']
for name in (root/'native').glob('*'):
 if name.is_file():assert sha(name)==sha(parent/'native'/name.name),name
for key,names in [('modelReport',10),('deliveryModelReport',6),('resumeModelReport',8),('intentModelReport',6),('enrollmentModelReport',8)]:
 p=pathlib.Path(pheld[key]);d=verify(parent,p);assert d['namedScenarios']==names;reports[key]=str(p)
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
m=root/'component-manifest.json';assert not m.exists();m.write_text(json.dumps({'schema':1,'owner':'f6779148-8f5d-4bdf-8a0f-044184e486f2','passed':True,'sourceHeld':True,'evidenceIntegrityPassed':True,'buildReport':str(bp),**reports,'evidence':evidence,'files':files,'retainedNativeModelSource':str(pm),'nativeProductionUnchangedFrom75':True,'nativeAcceptance':False,'fullReleaseAccepted':False,'scope':'Current full95 Elm/native build; local feedback9 explicitly selected cases/21 coupled traces and current optimizedElm43 guards; actual C/socket/Broker49 controls plus18 optimizedElm actual wire replay controls for capacity/expiry/original cutoff. Original resumeC79/Elm17 and currentreceipt8/metadata8/catalog8 pass. Native demand/delivery/resume/intent/enrollment newly rerun in exact unchanged75 native production. No actual compositor/AT/hardware/ordinary eligibility/full release acceptance from this component.'},indent=2)+'\n')
spec=r/'openspec/changes/warlock-preview-local-feedback';sm=spec/'component-manifest.json';assert not sm.exists();specFiles={str(p.relative_to(spec)):{'sha256':sha(p),'size':p.stat().st_size} for p in sorted(spec.rglob('*')) if p.is_file()}
sm.write_text(json.dumps({'sourceHeld':True,'requirements':3,'scenarios':6,'files':specFiles,'nativeAcceptance':False,'fullReleaseAccepted':False,'scope':'Additive local-feedback contract. Source/component evidence does not close native or original release gates.'},indent=2)+'\n')
report=r/'docs/warlock-preview/v77/report.json';report.write_text(json.dumps({'passed':True,'providerManifest':str(m),'providerManifestSHA256':sha(m),'buildCommands':95,'feedbackScenarios':9,'feedbackStates':f['statesCompared'],'feedbackTraces':21,'feedbackControls':110,'legacyResumeControls':79,'nativeAcceptance':False,'fullReleaseAccepted':False,'next':'Serialized native113 fullGTK threewindow capacity/expiry/original cutoff plus original109 controls; retain exact tuple and normal physical/journal cleanup. Distinct later intents/history longevity, ordinary eligible sources and all original release gates remain open.'},indent=2)+'\n')
sys.path.insert(0,str(r/'implementation/elm-build-loop-v1'));import loop
e=loop.write_checkpoint(r,'f6779148-8f5d-4bdf-8a0f-044184e486f2',str(root.relative_to(r)),['PROGRESS76 actualfull95/feedback9+21traces110controls/legacy79 andcurrentreceipt8metadata8catalog8 passed/held. CurrentnativeModels retainedfromexactsame75sources freshlyrerun5 suites. Source/failedderivatives72–75 retained, originalbaselinepreserved. NextCPUpreflight113 thenserializedownnativeGUI3windowstatus/cutoff/cleanup qualification. All original fullreleasegatesactive.'],'progress',[str(m.relative_to(r)),str(report.relative_to(r))]);print(json.dumps({'passed':True,'manifest':str(m),'files':len(files),'checkpoint':str(e)}))
