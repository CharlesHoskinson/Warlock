"""Fresh registered-helper path repair, preserving Native196 observer failure."""
import ast,hashlib,json,pathlib,resource,shutil,sys
sys.path.insert(0,'/home/hoskinson/window-integration-qa')
from qa_launch import require_qa_scope
require_qa_scope();assert resource.getrlimit(resource.RLIMIT_CORE)==(1,1)
repo=pathlib.Path('/home/hoskinson/omarchy-windows-parity');parent=repo/'implementation/warlock-client-provider-native-v196';root=repo/'implementation/warlock-client-provider-native-v197'
sha=lambda p:hashlib.sha256(pathlib.Path(p).read_bytes()).hexdigest()
pre=json.loads((parent/'qa/preflight.json').read_text())
for path,h in pre['inputs'].items():assert sha(path)==h,path
failed=parent/'qa/native-1791403529142543477/report.json';report=json.loads(failed.read_text());assert not report['passed'] and report['cleanupPassed'] and 'PosixPath' in report['error']
assert not root.exists();root.mkdir(mode=0o700);(root/'qa').mkdir(mode=0o700)
for base,target in [(parent,root),(parent/'qa',root/'qa')]:
 for p in base.iterdir():
  if p.is_file() and p.name not in {'preflight.json','ANCESTRY.json','component-manifest.json'} and not p.name.startswith('helper-input-'):shutil.copy2(p,target/p.name)
p=root/'qa/native-window-restart.py';source=p.read_text()
for old,new in [("p=ROOT/'qa'/('helper-input-'+str(helper_sequence))","p=OUTPUT/('helper-input-'+str(helper_sequence))"),("str(ROOT/'qa/helper-input-'+str(helper_sequence))","str(OUTPUT/('helper-input-'+str(helper_sequence)))")]:
 assert source.count(old)==1;source=source.replace(old,new)
ast.parse(source);p.write_text(source)
inputs=dict(pre['inputs']);inputs[str(parent/'qa/preflight.json')]=sha(parent/'qa/preflight.json');inputs[str(failed)]=sha(failed);inputs[str(pathlib.Path(__file__))]=sha(__file__)
for base in [root,root/'qa']:
 for p in base.iterdir():
  if p.is_file():inputs[str(p)]=sha(p)
pre.update(inputs=inputs,retainedNative196Failure=str(failed),retainedNative196FailureSHA256=sha(failed));(root/'qa/preflight.json').write_text(json.dumps(pre,indent=2)+'\n')
(root/'ANCESTRY.json').write_text(json.dumps({'owner':'f6779148-8f5d-4bdf-8a0f-044184e486f2','parent':str(parent),'retainedFailure':str(failed),'failureSHA256':sha(failed),'change':'Correct registered helper path composition; sealed input files stay in the private session output. Original effect/recovery oracles and all deadlines unchanged.','nativeAcceptance':False,'fullReleaseAccepted':False},indent=2)+'\n')
sys.path.insert(0,str(repo/'implementation/elm-build-loop-v1'));import loop
print(loop.write_checkpoint(repo,'f6779148-8f5d-4bdf-8a0f-044184e486f2',str(root.relative_to(repo)),['Native196 current integer authority grant reaches real coherent Elm group and keyboard control; retained QA helper path TypeError before first command, private cleanup passed. Fresh Native197 fixes path composition and keeps transient sealed helper input in private output. Original lost-receipt/Unknown/whole-host Restart checks and deadlines unchanged; production unchanged.'],'progress',[str((root/'qa/preflight.json').relative_to(repo)),str(failed.relative_to(repo))]))
