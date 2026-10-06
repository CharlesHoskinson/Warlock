"""Qualify the current explicit C entry registry on the same owning ABI pair."""
import ast,hashlib,json,pathlib,resource,shutil,sys
sys.path.insert(0,'/home/hoskinson/window-integration-qa');from qa_launch import require_qa_scope
require_qa_scope();assert resource.getrlimit(resource.RLIMIT_CORE)==(1,1)
repo=pathlib.Path('/home/hoskinson/omarchy-windows-parity')
parent=repo/'implementation/warlock-client-provider-native-v122';target=repo/'implementation/warlock-client-provider-native-v123'
sha=lambda p:hashlib.sha256(p.read_bytes()).hexdigest()
manifest=parent/'component-manifest.json';held=json.loads(manifest.read_text());assert held['passed'] and held['sourceHeld']
for rel,row in held['files'].items():assert sha(parent/rel)==row['sha256'],rel
gui=repo/'implementation/warlock-preview-provider-v85/component-manifest.json';proof=json.loads(gui.read_text());assert proof['passed'] and proof['sourceHeld']
for rel,row in proof['files'].items():assert sha(gui.parent/rel)==row['sha256'],rel
assert not target.exists()
def ignore(path,names):return [name for name in names if name in {'component-manifest.json','preflight.json','ANCESTRY.json','__pycache__'} or (pathlib.Path(path)==parent/'qa' and name.startswith(('native-','prepare-')))]
shutil.copytree(parent,target,ignore=ignore)
path=target/'qa/prepare.py';text=path.read_text();old="provider=REPO/'implementation/warlock-preview-provider-v84'";assert text.count(old)==1;text=text.replace(old,"provider=REPO/'implementation/warlock-preview-provider-v85'")
marker=' assert all(sha(p)==h for p,h in inputs.items());';assert text.count(marker)==1
extra=" prior122=REPO/'implementation/warlock-client-provider-native-v122/qa/native-1791318697436457682/report.json';proof122=json.loads(prior122.read_text());assert proof122['passed'] and proof122['cleanupPassed'] and len(proof122['checks'])==2462 and len(proof122['ownedExitCodes'])==277 and all(row['exitCode']==0 for row in proof122['ownedExitCodes']);inputs[str(prior122)]=sha(prior122);pre['retainedNative122Report']=str(prior122)\n"
text=text.replace(marker,extra+marker);ast.parse(text);path.write_text(text)
path=target/'qa/native.py';text=path.read_text()
marker=" check('allPriorNative121FixedOrderedAndActualRetryAssertionsRetained',len(prior121['checks'])==2458 and comparison121['passed'],evidence=comparison121)";assert text.count(marker)==1
extra="\n prior122=json.loads(pathlib.Path(pre['retainedNative122Report']).read_text());comparison122=compare(prior122,r,stableNames)\n check('allPriorNative122FixedOrderedAndActualRetryAssertionsRetained',len(prior122['checks'])==2462 and comparison122['passed'],evidence=comparison122)"
text=text.replace(marker,marker+extra);ast.parse(text);path.write_text(text)
(target/'ANCESTRY.json').write_text(json.dumps({'owner':'f6779148-8f5d-4bdf-8a0f-044184e486f2','parent':str(parent),'parentManifestSHA256':sha(manifest),'providerManifest':str(gui),'providerManifestSHA256':sha(gui),
 'purpose':'Current full GUI85 explicit bounded active C membership and nonreused entry serials, unchanged owning core16/plugin18. Preserve every original122 runtime predicate, physical/journal/pixel/receipt/input/deadline gate and actual allocator trial. No actor erasure or capacity increase; aggregate retirement/Elm settlement/turnover beyond256 remains open.',
 'nativeAcceptance':False,'fullReleaseAccepted':False},indent=2)+'\n')
sys.path.insert(0,str(repo/'implementation/elm-build-loop-v1'));import loop
print(loop.write_checkpoint(repo,'f6779148-8f5d-4bdf-8a0f-044184e486f2',str(target.relative_to(repo)),
 ['PROGRESS PUBLIC60 03582f63 verified8175 exactowner blobs. Sourcea0dd6 GUI84/native1222462/277normal held. Current GUI85 explicit bounded C membership/monotonic entry serials full95/originalregressions/current decoder13/25/439states/3mutants/C96 held. Fresh native123 same core16/plugin18, unchanged122 runtime gates and actual allocator trials; next preflight/serialized native. Then implement atomic multi-owner/Elm retirement and actual turnover beyond256; full release remains open.'],
 'progress',[str((target/'ANCESTRY.json').relative_to(repo))]))
