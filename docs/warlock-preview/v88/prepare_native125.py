"""Current GUI88 native campaign on the unchanged owning core16/plugin18."""
import ast,hashlib,json,pathlib,resource,shutil,sys
sys.path.insert(0,'/home/hoskinson/window-integration-qa');from qa_launch import require_qa_scope
require_qa_scope();assert resource.getrlimit(resource.RLIMIT_CORE)==(1,1)
r=pathlib.Path('/home/hoskinson/omarchy-windows-parity');p=r/'implementation/warlock-client-provider-native-v124';t=r/'implementation/warlock-client-provider-native-v125'
sha=lambda path:hashlib.sha256(path.read_bytes()).hexdigest()
manifest=p/'component-manifest.json';m=json.loads(manifest.read_text());assert m['passed'] and m['sourceHeld']
for rel,row in m['files'].items():assert sha(p/rel)==row['sha256'],rel
gui=r/'implementation/warlock-preview-provider-v88/component-manifest.json';g=json.loads(gui.read_text());assert g['passed'] and g['sourceHeld']
for rel,row in g['files'].items():assert sha(gui.parent/rel)==row['sha256'],rel
assert not t.exists()
def ignore(path,names):return [n for n in names if n in {'component-manifest.json','preflight.json','ANCESTRY.json','__pycache__'} or (pathlib.Path(path)==p/'qa' and n.startswith(('native-','prepare-')))]
shutil.copytree(p,t,ignore=ignore)
source=t/'qa/prepare.py';s=source.read_text();old="provider=REPO/'implementation/warlock-preview-provider-v85'";assert s.count(old)==1;s=s.replace(old,"provider=REPO/'implementation/warlock-preview-provider-v88'")
marker=' assert all(sha(p)==h for p,h in inputs.items());';assert s.count(marker)==1
extra=""" prior124=REPO/'implementation/warlock-client-provider-native-v124/qa/native-1791319779543397011/report.json';proof124=json.loads(prior124.read_text());assert proof124['passed'] and proof124['cleanupPassed'] and len(proof124['checks'])==2463 and len(proof124['ownedExitCodes'])==277 and all(row['exitCode']==0 for row in proof124['ownedExitCodes']);inputs[str(prior124)]=sha(prior124);pre['retainedNative124Report']=str(prior124)
 for field in ['actorRetirementReport','elmRetirementReport','controlPrefixReport','controlAdapterReport']:
  evidence=pathlib.Path(providerHeld[field]);checked=json.loads(evidence.read_text());assert checked['passed'];inputs[str(evidence)]=sha(evidence);pre[field]=str(evidence)
  for rel,value in checked['inputs'].items():
   file=pathlib.Path(rel);file=file if file.is_absolute() else provider/file;assert sha(file)==value,rel;inputs[str(file)]=value
  for rel,value in checked['artifacts'].items():assert sha(evidence.parent/rel)==value,rel;inputs[str(evidence.parent/rel)]=value
"""
s=s.replace(marker,extra+marker);ast.parse(s);source.write_text(s)
source=t/'qa/native.py';s=source.read_text();marker=" check('allPriorNative122FixedOrderedAndActualRetryAssertionsRetained',len(prior122['checks'])==2462 and comparison122['passed'],evidence=comparison122)";assert s.count(marker)==1
extra="\n prior124=json.loads(pathlib.Path(pre['retainedNative124Report']).read_text());comparison124=compare(prior124,r,stableNames)\n check('allPriorNative124FixedOrderedAndActualRetryAssertionsRetained',len(prior124['checks'])==2463 and comparison124['passed'],evidence=comparison124)"
s=s.replace(marker,marker+extra);ast.parse(s);source.write_text(s)
(t/'ANCESTRY.json').write_text(json.dumps({'owner':'f6779148-8f5d-4bdf-8a0f-044184e486f2','parent':str(p),'parentManifestSHA256':sha(manifest),'providerManifest':str(gui),'providerManifestSHA256':sha(gui),'purpose':'Current full GUI88 Elm exact retirement settlement and explicit original-popup control delivery ordinals. Unchanged owning core16/plugin18, stable-inode strict lock publisher and every original124 runtime/deadline/physical/receipt/input/pixel oracle. Actual compositor/Elm actor retirement routing and more-than256 native/Elm turnover remain unqualified; no ordinary capture or full release acceptance.','nativeAcceptance':False,'fullReleaseAccepted':False},indent=2)+'\n')
sys.path.insert(0,str(r/'implementation/elm-build-loop-v1'));import loop
print(loop.write_checkpoint(r,'f6779148-8f5d-4bdf-8a0f-044184e486f2',str(t.relative_to(r)),['PROGRESS GUI88 held full95/original12/C96/decoder13-25-439states-3mutants/Caggregate9068through280synthetic/Elm33/Cprefix7-15-180states-3mutants/adapter10. Fresh native125 qualifies current changed Elm/host assets on exact core16/plugin18 and retains every original124 runtime predicate/deadline and actual retry oracle. Next preflight and serialized native; independently fresh own native retirement/readiness/completion routing, then actual continuing native/Elm >256 turnover and all original full release gates.'],'progress',[str((t/'ANCESTRY.json').relative_to(r)),str(gui.relative_to(r))]))
