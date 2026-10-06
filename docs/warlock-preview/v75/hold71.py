"""Hold exact changed native resume and Elm receipt policy qualification."""
import hashlib,json,pathlib,resource,stat,sys
sys.path.insert(0,'/home/hoskinson/window-integration-qa');from qa_launch import require_qa_scope
require_qa_scope();assert resource.getrlimit(resource.RLIMIT_CORE)==(1,1)
r=pathlib.Path('/home/hoskinson/omarchy-windows-parity');root=r/'implementation/warlock-preview-provider-v71';sha=lambda f:hashlib.sha256(f.read_bytes()).hexdigest()
def only(base,pat):
 rows=list(base.glob(pat));assert len(rows)==1,rows;return rows[0]
def verify(base,path):
 d=json.loads(path.read_text());assert d['passed'],path
 for name,value in d['inputs'].items():assert sha(pathlib.Path(name) if pathlib.Path(name).is_absolute() else base/name)==value,name
 for name,value in d.get('artifacts',{}).items():assert sha(path.parent/name)==value,name
 return d
bp=only(root,'qa/build-*/report.json');b=verify(root,bp);assert len(b['commands'])==94 and all(row['exitCode']==0 for row in b['commands'])
for section in ['compilerDependencies','linkedLibraries','tools']:
 for name,row in b[section].items():assert sha(pathlib.Path(name))==row['sha256'],name
assert sha(bp.parent/'elm-host')==b['binarySHA256']
reports={}
for key,pat,states in [('receiptModelReport','qa/receipt-check-*/report.json',214),('metadataModelReport','qa/metadata-check-*/report.json',210),('catalogModelReport','qa/catalog-check-*/report.json',214)]:
 p=only(root,pat);d=verify(root,p);assert d['namedScenarios']==8 and d['statesCompared']==states and d['compiledBuild']=={'path':str(bp),'sha256':sha(bp)};reports[key]=str(p)
assert json.loads(pathlib.Path(reports['receiptModelReport']).read_text())['unsafeCounterexamplesDetected']==2
cp=only(root,'qa/resume-check-*/report.json');c=verify(root,cp);assert c['checks']==79 and c['elmEvidence']['checks']==17 and c['buildReport']==str(bp) and c['compiledElm']['sha256']==b['compiledAssetPackage']['files']['preview-replay.js'];reports['resumeCReport']=str(cp)
parent=root.parent/'warlock-preview-provider-v69';pm=parent/'component-manifest.json';held=json.loads(pm.read_text());assert held['sourceHeld']
for key,pat,names,states in [('modelReport','qa/check-*/report.json',10,564),('deliveryModelReport','qa/delivery-check-*/report.json',6,388),('resumeModelReport','qa/resume-model-check-*/report.json',8,584)]:
 p=only(parent,pat);d=verify(parent,p);assert d['namedScenarios']==names and sum(row['statesCompared'] for row in d['coupledTraces'])==states;reports[key]=str(p)
for name in ['imported_lifecycle.hpp','imported_clients.hpp','imported-clients.cpp','imported-clients.h','imported_admission.hpp','imported_enrollment.hpp','demand.hpp','preview_uri.hpp','preview_uri.cpp']:assert sha(root/'native'/name)==sha(parent/'native'/name),name
baseline=root.parent/'warlock-preview-provider-v65';old=json.loads((baseline/'component-manifest.json').read_text())
for key in ['intentModelReport','enrollmentModelReport']:
 p=pathlib.Path(old[key]);verify(baseline,p);reports[key]=str(p)
for name in ['imported_admission.hpp','imported_enrollment.hpp','demand.hpp','preview_uri.hpp','preview_uri.cpp']:assert sha(root/'native'/name)==sha(baseline/'native'/name),name
evidence={}
for name in ['catalog-enrollment-replay','delivery-extension-physical-tests','metadata-privacy-replay','metadata-icon-physical-tests','receiver-extension-physical-tests','imported-admission-tests','imported-lifecycle-tests']:
 d=json.loads((bp.parent/(name+'.stdout')).read_text());assert d['passed'];evidence[name]=d
evidence['dynamic-enrollment-tests']=json.loads((bp.parent/'dynamic-enrollment-tests.stdout').read_text().splitlines()[-1]);assert evidence['dynamic-enrollment-tests']['checks']==34
files={}
for p in sorted(root.rglob('*')):
 rel=p.relative_to(root)
 if any(part in {'elm-stuff','mutable-elm-home','__pycache__'} for part in rel.parts):continue
 assert not p.is_symlink(),p
 if p.is_file():files[str(rel)]={'kind':'file','sha256':sha(p),'size':p.stat().st_size,'mode':oct(stat.S_IMODE(p.stat().st_mode))}
m=root/'component-manifest.json';assert not m.exists();m.write_text(json.dumps({'schema':1,'owner':'f6779148-8f5d-4bdf-8a0f-044184e486f2','passed':True,'sourceHeld':True,'evidenceIntegrityPassed':True,'buildReport':str(bp),**reports,'evidence':evidence,'files':files,'retainedNativeModelSource':str(pm),'nativeProductionUnchangedFrom69':True,'nativeAcceptance':False,'fullReleaseAccepted':False,'scope':'Full94 changed GUI/native resume production compilation; actual C/socket and current optimized Elm79 controls incl17 same-owner request history/real NativeRejected/earlyfutureproof/no premature ACK/exact duplicate tuple/altered sequence/no capture/wrong and exact ACK/floors; receipt8/100samples/16traces214states detects2 preserved actual unsafe parent70 behaviors; metadata8/210 andcatalog8/214 current compiled Elm. Native resume/demand/delivery models retained from exact unchanged69 production; intent/enrollment retained unchanged65 direct helper dependency sources. No GUI71 actual compositor/pixels/hardware/native eligibility/full release acceptance yet.'},indent=2)+'\n')
spec=r/'openspec/changes/warlock-preview-resume-intents';specFiles={str(p.relative_to(spec)):{'kind':'file','sha256':sha(p),'size':p.stat().st_size} for p in sorted(spec.rglob('*')) if p.is_file()};sm=spec/'component-manifest.json';assert not sm.exists();sm.write_text(json.dumps({'owner':'f6779148-8f5d-4bdf-8a0f-044184e486f2','sourceHeld':True,'requirements':5,'scenarios':11,'files':specFiles,'nativeAcceptance':False,'fullReleaseAccepted':False,'scope':'Additive EARS design contract; native qualification and original release remain open. Planning tasks are an immutable preparation snapshot.'},indent=2)+'\n')
report=r/'docs/warlock-preview/v75/report.json';report.write_text(json.dumps({'passed':True,'provider':str(m),'providerManifestSHA256':sha(m),'buildCommands':94,'resumeCControls':79,'resumeElmControls':17,'resumeModelStates':584,'resumeModelScenarios':8,'receiptModelStates':214,'receiptModelScenarios':8,'receiptActualUnsafeCounterexamplesDetected':2,'metadataStates':210,'catalogStates':214,'nativeAcceptance':False,'fullReleaseAccepted':False,'next':'Owning serialized native109; preserve original controls/deadlines and run actual retained resume cutoff/FD/GIO/journal/floor/receiver-before-query. Continue typed local GUI feedback, distinct later unissued intents and all originalS09/S01-S16/recovery/drag/hardware/ATIME/journeys/deployment gates.'},indent=2)+'\n')
sys.path.insert(0,str(r/'implementation/elm-build-loop-v1'));import loop
e=loop.write_checkpoint(r,'f6779148-8f5d-4bdf-8a0f-044184e486f2',str(root.relative_to(r)),['PROGRESS GUI71 held full94/C79/Elm17/currentreceipt8/214states2actualunsafecounterexamples/currentmetadata8/210/catalog8/214; native resume8/584states3mutants/demand10/delivery6 retained exactunchanged69, oldintent/enrollment exacthelperdependency65. Failed67-70 retained. Additive EARS5/11 held. Nextserializednative109actualCresumeoriginalcutoff/realphysicaldrain/ACK/receiverqueryguard; alloriginalfullreleasegatesactive. No externalblocker.'],'progress',[str(m.relative_to(r)),str(report.relative_to(r))]);print(json.dumps({'passed':True,'manifest':str(m),'files':len(files),'checkpoint':str(e)}))
