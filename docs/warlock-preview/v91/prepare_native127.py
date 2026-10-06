"""Keep every native126 oracle; change only held GUI identity and add prior audit."""
import ast,hashlib,json,pathlib,resource,shutil,sys
sys.path.insert(0,'/home/hoskinson/window-integration-qa')
from qa_launch import require_qa_scope
require_qa_scope();assert resource.getrlimit(resource.RLIMIT_CORE)==(1,1)
repo=pathlib.Path('/home/hoskinson/omarchy-windows-parity')
parent=repo/'implementation/warlock-client-provider-native-v126';target=repo/'implementation/warlock-client-provider-native-v127'
sha=lambda p:hashlib.sha256(p.read_bytes()).hexdigest()
manifest=parent/'component-manifest.json';m=json.loads(manifest.read_text());assert m['passed'] and m['sourceHeld']
for rel,row in m['files'].items():assert sha(parent/rel)==row['sha256'],rel
gui=repo/'implementation/warlock-preview-provider-v92/component-manifest.json';g=json.loads(gui.read_text());assert g['passed'] and g['sourceHeld']
for rel,row in g['files'].items():assert sha(gui.parent/rel)==row['sha256'],rel
assert not target.exists()
def ignore(path,names):return [n for n in names if n in {'component-manifest.json','preflight.json','ANCESTRY.json','__pycache__'} or (pathlib.Path(path)==parent/'qa' and n.startswith(('native-','prepare-')))]
shutil.copytree(parent,target,ignore=ignore)
p=target/'qa/prepare.py';s=p.read_text();old="provider=REPO/'implementation/warlock-preview-provider-v89'";assert s.count(old)==1
s=s.replace(old,"provider=REPO/'implementation/warlock-preview-provider-v92'")
marker=' assert all(sha(p)==h for p,h in inputs.items());';assert s.count(marker)==1
extra=""" prior126=REPO/'implementation/warlock-client-provider-native-v126/qa/native-1791324457218690108/report.json';proof126=json.loads(prior126.read_text());assert proof126['passed'] and proof126['cleanupPassed'] and len(proof126['checks'])==2465 and len(proof126['ownedExitCodes'])==277 and all(row['exitCode']==0 for row in proof126['ownedExitCodes']);inputs[str(prior126)]=sha(prior126);pre['retainedNative126Report']=str(prior126)
 for field in ['retainedDeliveryReport','retainedDeliveryModelReport','retainedDeliveryElmMutantsReport','retainedDeliveryNativeElmReport']:
  evidence=pathlib.Path(providerHeld[field]);checked=json.loads(evidence.read_text());assert checked['passed'];inputs[str(evidence)]=sha(evidence);pre[field]=str(evidence)
  for rel,value in checked['inputs'].items():
   file=pathlib.Path(rel);file=file if file.is_absolute() else provider/file;assert sha(file)==value,rel;inputs[str(file)]=value
  for rel,value in checked.get('artifacts',{}).items():assert sha(evidence.parent/rel)==value,rel;inputs[str(evidence.parent/rel)]=value
"""
s=s.replace(marker,extra+marker);ast.parse(s);p.write_text(s)
p=target/'qa/native.py';s=p.read_text();marker=" check('allPriorNative125FixedOrderedAndActualRetryAssertionsRetained',len(prior125['checks'])==2464 and comparison125['passed'],evidence=comparison125)";assert s.count(marker)==1
s=s.replace(marker,marker+"\n prior126=json.loads(pathlib.Path(pre['retainedNative126Report']).read_text());comparison126=compare(prior126,r,stableNames)\n check('allPriorNative126FixedOrderedAndActualRetryAssertionsRetained',len(prior126['checks'])==2465 and comparison126['passed'],evidence=comparison126)")
ast.parse(s);p.write_text(s)
(target/'ANCESTRY.json').write_text(json.dumps({'owner':'f6779148-8f5d-4bdf-8a0f-044184e486f2','parent':str(parent),'parentManifestSHA256':sha(manifest),'providerManifest':str(gui),'providerManifestSHA256':sha(gui),'purpose':'Current full GUI92 typed retained completion channel and processing ACK; actual runtime retains all original126 controls and unchanged core16/plugin18. New retained protocol has C/native/Elm CPU round-trip proof only; actual WebKit routing and real window turnover remain open.','nativeAcceptance':False,'fullReleaseAccepted':False},indent=2)+'\n')
sys.path.insert(0,str(repo/'implementation/elm-build-loop-v1'));import loop
print(loop.write_checkpoint(repo,'f6779148-8f5d-4bdf-8a0f-044184e486f2',str(target.relative_to(repo)),['PROGRESS heldGUI92 full95/all original12 and original retirement regressions; retained45/14/34/667 with3model+3compiledElm mutants and48actualCnativeElm controls, loss/ACK/neighbor/close/normalexit. Native127 next preflight then exact serialized original126 campaign. FreshGUI93 actual shared-host retirement readiness persistence/poll, original channel/epoch and outgoing delivery liveness; real windows, captured retirement and all release gates remain.'],'progress',[str(gui.relative_to(repo)),str((target/'ANCESTRY.json').relative_to(repo))]))
