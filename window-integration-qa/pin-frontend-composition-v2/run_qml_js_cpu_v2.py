from pathlib import Path
import hashlib,json,os,shutil,subprocess,sys,time
sys.path.insert(0,'/home/hoskinson/window-integration-qa')
from qa_launch import require_qa_scope
from popup_authority import engine_pair,popup_pair
B=Path(__file__).resolve().parent
def digest(p):return hashlib.sha256(Path(p).read_bytes()).hexdigest()
def main():
 require_qa_scope();files=[B/'frontend/PinWindowMenu.qml',B/'test_qml_diagnostic_v2.js',B/'popup_authority.py',Path(__file__)];before={str(p):digest(p)for p in files}
 command=[shutil.which('node'),str(B/'test_qml_diagnostic_v2.js'),str(B/'frontend/PinWindowMenu.qml')];r=subprocess.run(command,capture_output=True,text=True,timeout=15);checks=[]
 if r.returncode==0:
  values=json.loads(r.stdout);assert len(values)==3
  for v in values:
   meta=engine_pair(v['value']);checks.append({'name':v['scenario']+' raw metadata','passed':True})
   if v['scenario']=='open':popup_pair(v['value'],meta);checks.append({'name':'normal full raw popup tuple','passed':True})
   elif v['scenario']=='getter-mutation':
    try:popup_pair(v['value'],meta)
    except ValueError:checks.append({'name':'real JS getter mutation refused by new decoder','passed':True})
    else:raise AssertionError('Changed getter witness accepted')
   else:
    try:popup_pair(v['value'],meta)
    except ValueError:checks.append({'name':'closed menu metadata has no popup authority','passed':True})
    else:raise AssertionError('Closed tuple accepted')
 stable=all(digest(Path(p))==h for p,h in before.items());good=r.returncode==0 and stable
 report={'result':'pass'if good else'fail','command':command,'exitCode':r.returncode,'stdout':r.stdout,'stderr':r.stderr,'checks':checks,'sourceSHA256':before,'sourceStable':stable,'exactQMLFunctionExecutedAsJS':True,'actualQtQSNativeSemantics':False,'GUI':False}
 target=B/('qml-js-v2-cpu-report.json'if good else f'qml-js-failure-{time.time_ns()}.json');assert not target.exists();target.write_text(json.dumps(report,indent=2)+'\n');os.chmod(target,0o600);print(json.dumps({'result':report['result'],'path':str(target),'checks':len(checks)}));return int(not good)
if __name__=='__main__':raise SystemExit(main())
