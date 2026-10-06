"""Derive current GUI89 native campaign without changing original oracles."""
import ast,hashlib,json,pathlib,resource,shutil,sys
sys.path.insert(0,'/home/hoskinson/window-integration-qa');from qa_launch import require_qa_scope
require_qa_scope();assert resource.getrlimit(resource.RLIMIT_CORE)==(1,1)
r=pathlib.Path('/home/hoskinson/omarchy-windows-parity');p=r/'implementation/warlock-client-provider-native-v125';t=r/'implementation/warlock-client-provider-native-v126'
sha=lambda path:hashlib.sha256(path.read_bytes()).hexdigest()
manifest=p/'component-manifest.json';m=json.loads(manifest.read_text());assert m['passed'] and m['sourceHeld']
for rel,row in m['files'].items():assert sha(p/rel)==row['sha256'],rel
gui=r/'implementation/warlock-preview-provider-v89/component-manifest.json';g=json.loads(gui.read_text());assert g['passed'] and g['sourceHeld']
for rel,row in g['files'].items():assert sha(gui.parent/rel)==row['sha256'],rel
assert not t.exists()
def ignore(path,names):return [n for n in names if n in {'component-manifest.json','preflight.json','ANCESTRY.json','__pycache__'} or (pathlib.Path(path)==p/'qa' and n.startswith(('native-','prepare-')))]
shutil.copytree(p,t,ignore=ignore)
source=t/'qa/prepare.py';s=source.read_text();old="provider=REPO/'implementation/warlock-preview-provider-v88'";assert s.count(old)==1;s=s.replace(old,"provider=REPO/'implementation/warlock-preview-provider-v89'")
marker=' assert all(sha(p)==h for p,h in inputs.items());';assert s.count(marker)==1
extra=""" prior125=REPO/'implementation/warlock-client-provider-native-v125/qa/native-1791322713358499938/report.json';proof125=json.loads(prior125.read_text());assert proof125['passed'] and proof125['cleanupPassed'] and len(proof125['checks'])==2464 and len(proof125['ownedExitCodes'])==277 and all(row['exitCode']==0 for row in proof125['ownedExitCodes']);inputs[str(prior125)]=sha(prior125);pre['retainedNative125Report']=str(prior125)
 for field in ['asynchronousRetirementReport','asynchronousRefinementReport','asynchronousElmMutantReport']:
  evidence=pathlib.Path(providerHeld[field]);checked=json.loads(evidence.read_text());assert checked['passed'];inputs[str(evidence)]=sha(evidence);pre[field]=str(evidence)
  for rel,value in checked['inputs'].items():
   file=pathlib.Path(rel);file=file if file.is_absolute() else provider/file;assert sha(file)==value,rel;inputs[str(file)]=value
  for rel,value in checked['artifacts'].items():assert sha(evidence.parent/rel)==value,rel;inputs[str(evidence.parent/rel)]=value
"""
s=s.replace(marker,extra+marker);ast.parse(s);source.write_text(s)
source=t/'qa/native.py';s=source.read_text();marker=" check('allPriorNative124FixedOrderedAndActualRetryAssertionsRetained',len(prior124['checks'])==2463 and comparison124['passed'],evidence=comparison124)";assert s.count(marker)==1
extra="\n prior125=json.loads(pathlib.Path(pre['retainedNative125Report']).read_text());comparison125=compare(prior125,r,stableNames)\n check('allPriorNative125FixedOrderedAndActualRetryAssertionsRetained',len(prior125['checks'])==2464 and comparison125['passed'],evidence=comparison125)"
s=s.replace(marker,marker+extra);ast.parse(s);source.write_text(s)
(t/'ANCESTRY.json').write_text(json.dumps({'owner':'f6779148-8f5d-4bdf-8a0f-044184e486f2','parent':str(p),'parentManifestSHA256':sha(manifest),'providerManifest':str(gui),'providerManifestSHA256':sha(gui),'purpose':'Current full GUI89 independently delivered per-actor retirement completion and nondecreasing shared native cutoffs. Unchanged core16/plugin18 and all original125 runtime controls/deadlines, resource/pixel/input/normal-exit/cleanup oracles. Actual retirement routing and continuing native/Elm turnover remain open.','nativeAcceptance':False,'fullReleaseAccepted':False},indent=2)+'\n')
sys.path.insert(0,str(r/'implementation/elm-build-loop-v1'));import loop
print(loop.write_checkpoint(r,'f6779148-8f5d-4bdf-8a0f-044184e486f2',str(t.relative_to(r)),['PROGRESS current GUI89 held full95/original12 and all retirement regressions; asynchronous10 selected/30 actualElm traces/641 state-command comparisons plus3model/3 compiledElm mutants. Native126 must qualify current owningGUI89/core16/plugin18, retain original125 runtime/deadline/physical/receipt/pixel/input oracles. Next preflight then serialized native. Native observation/readiness/completion routing with retained completion delivery and all original GUI release gates remain.'],'progress',[str((t/'ANCESTRY.json').relative_to(r)),str(gui.relative_to(r))]))
