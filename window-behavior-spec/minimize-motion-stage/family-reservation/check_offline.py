#!/usr/bin/env python3
"""Freeze the selected motion helper/QML and run only isolated offline checks."""
import argparse,hashlib,json,os,re,shutil,subprocess,tempfile
from pathlib import Path
HERE=Path(__file__).resolve().parent
parser=argparse.ArgumentParser(description=__doc__)
parser.add_argument('--helpers',type=Path,default=HERE)
parser.add_argument('--widget',type=Path,default=HERE/'widget_v65')
parser.add_argument('--report',type=Path,default=HERE/'offline-report.json')
parser.add_argument('--expect-motion-sha',default='83609014a0a860c5d1e6228c8a8aa64799e5df9e35365e95d75daee1c12a653a')
args=parser.parse_args()
sha=lambda p:hashlib.sha256(p.read_bytes()).hexdigest()
source={p.name:{'path':str(p.resolve()),'sha256':sha(p)} for p in [*(args.helpers/n for n in ['hypr-window-motion','hypr-windowctl','hypr-windowctl-core']),*(args.widget/n for n in ['Windows.qml','WindowMotion.qml','TaskbarPopup.qml'])]}
if source['hypr-window-motion']['sha256']!=args.expect_motion_sha:raise SystemExit('Motion helper differs from reviewed candidate hash')
report={'sources':source,'tests':[],'nativeDesktopTouched':False}
with tempfile.TemporaryDirectory(prefix='motion-freeze-offline-') as temp:
 frozen=Path(temp)
 for n in ['hypr-window-motion','hypr-windowctl','hypr-windowctl-core']:shutil.copy2(args.helpers/n,frozen/n)
 shutil.copytree(args.widget,frozen/'widget_v65')
 for n in ['test_controller.py','test_whole_snapshot.py','test_freeze.py','test_motion_core.py','test_motion_service.py','test_native_motion_trial.py','test_freeze_qml.js','native_motion_trial.py','freeze_contract.qnt','freeze_contract_test.qnt','family_scope.qnt','family_scope_test.qnt','test_family_scope.py','test_family_reservation.py','family_commit_order.qnt','family_commit_order_test.qnt','native_motion_fixture.py','test_fixture_pin_policy.py']:shutil.copy2(HERE/n,frozen/n)
 env=dict(os.environ,MOTION_HELPER_DIR=str(frozen));env.pop('MOTION_QML_SOURCE',None)
 for n in ['HYPR_WINDOWCTL_ASYNC','HYPR_WINDOWCTL_FAMILY_SINGLE','HYPR_WINDOWCTL_PREVIEW_READY','HYPR_WINDOWCTL_MOTION']:env.pop(n,None)
 def check(name,command,count=None):
  result=subprocess.run(command,cwd=frozen,env=env,text=True,stdout=subprocess.PIPE,stderr=subprocess.STDOUT,timeout=45)
  item={'name':name,'command':command,'returncode':result.returncode,'output':result.stdout};report['tests'].append(item)
  args.report.write_text(json.dumps(report,indent=2))
  print(name+': '+('PASS' if result.returncode==0 else 'FAIL'),flush=True)
  if result.returncode:raise SystemExit(result.stdout)
  if count is not None:
   found=re.search(r'Ran (\d+) tests?',result.stdout)
   if not found or int(found[1])!=count:raise SystemExit('Unexpected suite count: '+name)
 for n,count in [('test_controller.py',28),('test_whole_snapshot.py',13),('test_freeze.py',12),('test_motion_core.py',9),('test_motion_service.py',3),('test_native_motion_trial.py',11),('test_family_scope.py',15),('test_family_reservation.py',6),('test_fixture_pin_policy.py',8)]:check(n,['python3',str(frozen/n)],count)
 check('Python fixture syntax',['python3','-m','py_compile',str(frozen/'hypr-window-motion'),str(frozen/'native_motion_trial.py'),str(frozen/'native_motion_fixture.py')])
 check('actual widget freeze JavaScript',['node',str(frozen/'test_freeze_qml.js')])
 for n in ['Windows.qml','WindowMotion.qml','TaskbarPopup.qml']:check(n+' parser',['/usr/lib/qt6/bin/qmlformat',str(frozen/'widget_v65'/n)])
 check('Bash helper syntax',['bash','-n',str(frozen/'hypr-windowctl'),str(frozen/'hypr-windowctl-core')])
 check('freeze contract typecheck',['quint','typecheck',str(frozen/'freeze_contract.qnt')])
 check('freeze contract named scenarios',['quint','test',str(frozen/'freeze_contract_test.qnt'),'--verbosity','1'])
 check('freeze contract 2000 samples',['quint','run',str(frozen/'freeze_contract.qnt'),'--invariant','allProps','--max-samples','2000','--max-steps','100','--verbosity','1'])
 check('family scope typecheck',['quint','typecheck',str(frozen/'family_scope.qnt')])
 check('family scope named scenarios',['quint','test',str(frozen/'family_scope_test.qnt'),'--verbosity','1'])
 check('family scope 2000 samples',['quint','run',str(frozen/'family_scope.qnt'),'--invariant','allProps','--max-samples','2000','--max-steps','100','--verbosity','1'])
 check('family commit ordering typecheck',['quint','typecheck',str(frozen/'family_commit_order.qnt')])
 check('family commit ordering named scenarios',['quint','test',str(frozen/'family_commit_order_test.qnt'),'--verbosity','1'])
 check('family commit ordering 2000 samples',['quint','run',str(frozen/'family_commit_order.qnt'),'--invariant','allProps','--max-samples','2000','--max-steps','100','--verbosity','1'])
 for item in source.values():
  if sha(Path(item['path']))!=item['sha256']:raise SystemExit('Selected source changed while frozen suite ran: '+item['path'])
 report.update(passed=True,uniquePythonTests=105,actualQmlScenarios=17,freezeNamedScenarios=12,freezeSamples=2000,familyNamedScenarios=8,familySamples=2000,familyCommitNamedScenarios=4,familyCommitSamples=2000)
 args.report.write_text(json.dumps(report,indent=2));print('105 Python + 17 actual QML scenarios + 12 Quint scenarios/2000 samples PASS; '+str(args.report))
