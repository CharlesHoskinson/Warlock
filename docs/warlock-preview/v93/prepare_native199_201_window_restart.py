"""Retain the exact qualified198 oracle for complementary real fault boundaries."""
import ast,hashlib,json,pathlib,resource,shutil,sys
sys.path.insert(0,'/home/hoskinson/window-integration-qa')
from qa_launch import require_qa_scope
require_qa_scope();assert resource.getrlimit(resource.RLIMIT_CORE)==(1,1)
repo=pathlib.Path('/home/hoskinson/omarchy-windows-parity');parent=repo/'implementation/warlock-client-provider-native-v198'
sha=lambda p:hashlib.sha256(pathlib.Path(p).read_bytes()).hexdigest()
pre=json.loads((parent/'qa/preflight.json').read_text())
for path,h in pre['inputs'].items():assert sha(path)==h,path
p=parent/'qa/native-1791403711809185595/report.json';report=json.loads(p.read_text())
assert report['passed'] and report['cleanupPassed'] and len(report['checks'])==63 and report['actualWindowCommandRestartQualified'] and report['actualWindowCommandDurableUnknownQualified']
assert all(c['passed'] for c in report['checks']) and all(h['exitCode']==0 for h in report['ownedHelperExits'])
for v,operation,fault in [(199,'minimize','lost'),(200,'restore','unread'),(201,'minimize','unread')]:
 root=repo/f'implementation/warlock-client-provider-native-v{v}';assert not root.exists();root.mkdir(mode=0o700);(root/'qa').mkdir(mode=0o700)
 for base,target in [(parent,root),(parent/'qa',root/'qa')]:
  for source in base.iterdir():
   if source.is_file() and source.name not in {'preflight.json','ANCESTRY.json','component-manifest.json'}:shutil.copy2(source,target/source.name)
 runner=root/'qa/native-window-restart.py';text=runner.read_text();old="OPERATION='restore';FAULT='lost'";assert text.count(old)==1;text=text.replace(old,f'OPERATION={operation!r};FAULT={fault!r}');ast.parse(text);runner.write_text(text)
 inputs=dict(pre['inputs']);inputs[str(parent/'qa/preflight.json')]=sha(parent/'qa/preflight.json');inputs[str(p)]=sha(p);inputs[str(pathlib.Path(__file__))]=sha(__file__)
 for base in [root,root/'qa']:
  for source in base.iterdir():
   if source.is_file():inputs[str(source)]=sha(source)
 capsule=dict(pre,inputs=inputs,operation=operation,faultBoundary=fault,retainedNative198Qualification=str(p),retainedNative198QualificationSHA256=sha(p))
 (root/'qa/preflight.json').write_text(json.dumps(capsule,indent=2)+'\n')
 (root/'ANCESTRY.json').write_text(json.dumps({'owner':'f6779148-8f5d-4bdf-8a0f-044184e486f2','parent':str(parent),'parentQualification':str(p),'qualificationSHA256':sha(p),'operation':operation,'faultBoundary':fault,'change':'Only the original declared operation/fault selector changes; exact198 behavior/pixel/keyboard/Unknown/native Restart/historical reservation/cleanup controls and deadlines retained.','nativeAcceptance':False,'fullReleaseAccepted':False},indent=2)+'\n')
 sys.path.insert(0,str(repo/'implementation/elm-build-loop-v1'));import loop
 print(loop.write_checkpoint(repo,'f6779148-8f5d-4bdf-8a0f-044184e486f2',str(root.relative_to(repo)),[f'Native{v} prepared exact198 real window-command Restart/Unknown oracle for {operation}/{fault}. Qualified19863 controls and19 waited-normal short-lived helpers/private cleanup retained. Original native effect/after-submit or actual before-write hook, Pending admission, exact recovered historical Unknown/no replay, native retirement/post-proof reads, explicit newer command, actual pixels/keyboard/cohort cleanup and deadlines preserved. No production/installed changes; combined controlled-preview/native uncertainty/full release open.'],'progress',[str((root/'qa/preflight.json').relative_to(repo)),str(p.relative_to(repo))]))
