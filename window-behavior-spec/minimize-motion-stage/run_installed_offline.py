#!/usr/bin/env python3
"""Freeze installed helper/widget bytes, then run offline tests against that copy."""
import argparse,hashlib,json,os,re,shutil,subprocess,tempfile,time
from pathlib import Path
HERE=Path(__file__).resolve().parent
EXPECTED='793c77b4ec2c9984a52db2d64841ce3f72114f04b6dab9555dad3a0e9b5a2c70'

def digest(path):return hashlib.sha256(path.read_bytes()).hexdigest()
def main():
 parser=argparse.ArgumentParser(description=__doc__)
 parser.add_argument('--report',type=Path,required=True)
 parser.add_argument('--helpers',type=Path,default=Path.home()/'.local/bin')
 parser.add_argument('--widget',type=Path,default=Path.home()/'.config/omarchy/plugins/hoskinson.windows/widget_v64')
 parser.add_argument('--expected-motion-sha',default=EXPECTED)
 args=parser.parse_args();args.report.parent.mkdir(parents=True,exist_ok=True)
 assert digest(args.helpers/'hypr-window-motion')==args.expected_motion_sha,'installed motion source differs from expected frozen version'
 report={'started':time.time(),'sources':[],'checks':[],'uniquePythonTests':0,'qmlScripts':0}
 try:
  with tempfile.TemporaryDirectory(prefix='motion-audit-') as temp:
   root=Path(temp);helpers=root/'helpers';helpers.mkdir();widget=root/'widget_v64';widget.mkdir();tests=root/'tests';tests.mkdir()
   for name in ['hypr-window-motion','hypr-windowctl','hypr-windowctl-core']:
    source=args.helpers/name;target=helpers/name;shutil.copy2(source,target)
    report['sources'].append({'source':str(source),'sha256':digest(target)})
   for name in ['Windows.qml','WindowMotion.qml','TaskbarPopup.qml']:
    source=args.widget/name;target=widget/name;shutil.copy2(source,target)
    report['sources'].append({'source':str(source),'sha256':digest(target)})
   suites=[('whole-window/test_controller.py',28),('whole-window/test_whole_snapshot.py',13),('test_motion_core.py',9),('test_motion_service.py',3),('test_native_motion_trial.py',None)]
   for source,count in suites:shutil.copy2(HERE/source,tests/Path(source).name)
   for name in ['native_motion_trial.py','test_motion_qml.js']:shutil.copy2(HERE/name,tests/name)
   env=dict(os.environ,MOTION_HELPER_DIR=str(helpers),MOTION_QML_SOURCE=str(widget/'WindowMotion.qml'),PYTHONDONTWRITEBYTECODE='1')
   for key in ['HYPR_WINDOWCTL_CORE','HYPR_WINDOWCTL_FRONTEND','HYPR_WINDOWCTL_FAMILY_SINGLE','HYPR_WINDOWCTL_ASYNC','HYPR_WINDOWCTL_PREVIEW_READY']:env.pop(key,None)
   def check(name,command,expected=None):
    result=subprocess.run(command,env=env,capture_output=True,text=True,timeout=40)
    output=result.stdout+result.stderr
    item={'name':name,'exitCode':result.returncode,'output':output};report['checks'].append(item)
    if name.endswith('.py'):
     found=re.search(r'Ran (\d+) tests',output);assert found and int(found.group(1))>0,'suite reported no tests: '+name
     actual=int(found.group(1))
     if expected is not None:assert actual==expected,'unexpected suite count: '+name
     item['tests']=actual;report['uniquePythonTests']+=actual
    print(name+': '+('PASS' if result.returncode==0 else 'FAIL')+(f' ({expected} tests)' if expected else ''))
    assert result.returncode==0,output
   for source,count in suites:check(Path(source).name,['python3',str(tests/Path(source).name)],count)
   check('frozen widget64 motion functions',['node',str(tests/'test_motion_qml.js')]);report['qmlScripts']=1
   check('frozen Bash syntax',['bash','-n',str(helpers/'hypr-windowctl'),str(helpers/'hypr-windowctl-core')])
   for name in ['Windows.qml','WindowMotion.qml','TaskbarPopup.qml']:
    check('frozen widget64 '+name+' parser',['/usr/lib/qt6/bin/qmlformat',str(widget/name)])
   for source in report['sources']:
    source['unchangedDuringRun']=digest(Path(source['source']))==source['sha256'];assert source['unchangedDuringRun'],'installed source changed during audit'
   report['passed']=True
 except Exception as error:report['passed']=False;report['error']=str(error);raise
 finally:
  report['finished']=time.time();args.report.write_text(json.dumps(report,indent=2))
 print(f"Installed source audit PASS: {report['uniquePythonTests']} unique Python tests + 1 actual-source QML JS script; report {args.report}")

if __name__=='__main__':main()
