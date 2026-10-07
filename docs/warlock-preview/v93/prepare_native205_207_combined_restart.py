"""Retain qualified204 combined oracle at the other actual command boundaries."""
import ast,hashlib,json,pathlib,resource,shutil,sys
sys.path.insert(0,'/home/hoskinson/window-integration-qa')
from qa_launch import require_qa_scope
require_qa_scope();assert resource.getrlimit(resource.RLIMIT_CORE)==(1,1)
repo=pathlib.Path('/home/hoskinson/omarchy-windows-parity');parent=repo/'implementation/warlock-client-provider-native-v204';sha=lambda p:hashlib.sha256(pathlib.Path(p).read_bytes()).hexdigest()
pre=json.loads((parent/'qa/preflight.json').read_text())
for path,h in pre['inputs'].items():assert sha(path)==h,path
qualified=parent/'qa/native-1791405433168520892/report.json';report=json.loads(qualified.read_text())
assert report['passed'] and report['cleanupPassed'] and report['combinedKnownPreviewBeforeRestartQualified'] and report['combinedControlledPreviewRestartQualified'] and report['actualWindowCommandDurableUnknownQualified']
assert all(c['passed'] for c in report['checks']) and all(c['exitCode']==0 for c in report['ownedHelperExits'])
for v,operation,fault in [(205,'restore','lost'),(206,'minimize','unread'),(207,'restore','unread')]:
 root=repo/f'implementation/warlock-client-provider-native-v{v}';assert not root.exists();root.mkdir(mode=0o700);(root/'qa').mkdir(mode=0o700)
 for base,target in [(parent,root),(parent/'qa',root/'qa')]:
  for p in base.iterdir():
   if p.is_file() and p.name not in {'preflight.json','ANCESTRY.json','component-manifest.json'}:shutil.copy2(p,target/p.name)
 p=root/'qa/native-window-restart.py';source=p.read_text();old="OPERATION='minimize';FAULT='lost'";assert source.count(old)==1;source=source.replace(old,f'OPERATION={operation!r};FAULT={fault!r}');ast.parse(source);p.write_text(source)
 inputs=dict(pre['inputs']);inputs[str(parent/'qa/preflight.json')]=sha(parent/'qa/preflight.json');inputs[str(qualified)]=sha(qualified);inputs[str(pathlib.Path(__file__))]=sha(__file__)
 for base in [root,root/'qa']:
  for p in base.iterdir():
   if p.is_file():inputs[str(p)]=sha(p)
 capsule=dict(pre,inputs=inputs,operation=operation,faultBoundary=fault,retainedNative204Qualification=str(qualified),retainedNative204QualificationSHA256=sha(qualified))
 (root/'qa/preflight.json').write_text(json.dumps(capsule,indent=2)+'\n')
 (root/'ANCESTRY.json').write_text(json.dumps({'owner':'f6779148-8f5d-4bdf-8a0f-044184e486f2','parent':str(parent),'parentQualification':str(qualified),'qualificationSHA256':sha(qualified),'operation':operation,'faultBoundary':fault,'change':'Only declared original operation/boundary selector changes; actual held native reader, revocation/strict close before GTK Restart, historical window Unknown/no replay, fresh own native capture/source clock/pixels, pointer-established original final fault focus if visible, helper/cohort checks and original deadlines retained.','nativeAcceptance':False,'fullReleaseAccepted':False},indent=2)+'\n')
 sys.path.insert(0,str(repo/'implementation/elm-build-loop-v1'));import loop
 print(loop.write_checkpoint(repo,'f6779148-8f5d-4bdf-8a0f-044184e486f2',str(root.relative_to(repo)),[f'PROGRESS Native{v} prepared exact qualified204 combined known-preview/uncertain-window-command/whole-host Restart oracle for {operation}/{fault}. Source/custody/native facts/pixels/keyboard/no replay/historical Unknown/fresh-own-native namespace/original deadlines and cleanup unchanged. No production/installed changes, no uncertain-preview or full-release acceptance.'],'progress',[str((root/'qa/preflight.json').relative_to(repo)),str(qualified.relative_to(repo))]))
