"""Fresh current integer authority-config adaptation; retain failed Native195."""
import ast,hashlib,json,pathlib,resource,shutil,sys
sys.path.insert(0,'/home/hoskinson/window-integration-qa')
from qa_launch import require_qa_scope
require_qa_scope();assert resource.getrlimit(resource.RLIMIT_CORE)==(1,1)
repo=pathlib.Path('/home/hoskinson/omarchy-windows-parity')
parent=repo/'implementation/warlock-client-provider-native-v195'
root=repo/'implementation/warlock-client-provider-native-v196'
sha=lambda p:hashlib.sha256(pathlib.Path(p).read_bytes()).hexdigest()
pre=json.loads((parent/'qa/preflight.json').read_text())
for path,h in pre['inputs'].items():assert sha(path)==h,path
failed=parent/'qa/native-1791403446987902432/report.json'
report=json.loads(failed.read_text())
assert not report['passed'] and report['cleanupPassed'] and len(report['checks'])==3
assert 'Host own native preview grant unavailable: Native integer field' in (failed.parent/'native-evidence/generation-1.log').read_text()
assert not root.exists();root.mkdir(mode=0o700);(root/'qa').mkdir(mode=0o700)
for base,target in [(parent,root),(parent/'qa',root/'qa')]:
 for p in base.iterdir():
  if p.is_file() and p.name not in {'preflight.json','ANCESTRY.json','component-manifest.json'}:shutil.copy2(p,target/p.name)
p=root/'qa/native-window-restart.py';source=p.read_text();old="'expected_start':start_time(native['pid'])";assert source.count(old)==1
source=source.replace(old,"'expected_start':int(start_time(native['pid']))");ast.parse(source);p.write_text(source)
inputs=dict(pre['inputs']);inputs[str(parent/'qa/preflight.json')]=sha(parent/'qa/preflight.json');inputs[str(failed)]=sha(failed);inputs[str(pathlib.Path(__file__))]=sha(__file__)
for base in [root,root/'qa']:
 for p in base.iterdir():
  if p.is_file():inputs[str(p)]=sha(p)
pre.update(inputs=inputs,retainedNative195Failure=str(failed),retainedNative195FailureSHA256=sha(failed))
(root/'qa/preflight.json').write_text(json.dumps(pre,indent=2)+'\n')
(root/'ANCESTRY.json').write_text(json.dumps({'owner':'f6779148-8f5d-4bdf-8a0f-044184e486f2','parent':str(parent),'retainedFailure':str(failed),'failureSHA256':sha(failed),'change':'Current native authority expected_start is an integer; no grant or native admission bypass. Original native/pointer/IPC deadlines and scenarios unchanged.','nativeAcceptance':False,'fullReleaseAccepted':False},indent=2)+'\n')
sys.path.insert(0,str(repo/'implementation/elm-build-loop-v1'));import loop
print(loop.write_checkpoint(repo,'f6779148-8f5d-4bdf-8a0f-044184e486f2',str(root.relative_to(repo)),['Native195 retained safe setup failure: original textual expected_start refused by current strict native grant; three checks/no command submitted/private cleanup passed. Fresh Native196 encodes actual verified compositor start as required integer, preserves all original window-command lost-receipt/Unknown/whole-host Restart behavior oracles and deadlines. No production source change or grant bypass. Separate controlled-preview recovery/full release remain open.'],'progress',[str((root/'qa/preflight.json').relative_to(repo)),str(failed.relative_to(repo))]))
