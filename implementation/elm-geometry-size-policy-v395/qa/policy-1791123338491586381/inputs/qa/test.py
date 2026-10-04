import hashlib,json,resource,shutil,subprocess,sys,time
from pathlib import Path
sys.path.insert(0,'/home/hoskinson/window-integration-qa')
from qa_launch import require_qa_scope
require_qa_scope();assert resource.getrlimit(resource.RLIMIT_CORE)==(1,1)
ROOT=Path(__file__).resolve().parents[1];OUT=ROOT/'qa'/('policy-'+str(time.time_ns()));OUT.mkdir()
def sha(p):return hashlib.sha256(p.read_bytes()).hexdigest()
report={'passed':False,'scope':'Actual pure size-bound policy; no wire/native integration or mutation acceptance','inputs':{},'commands':[]}
try:
 for rel in ['candidate/SizeBounds.hpp','qa/policy-test.cpp','qa/test.py','spec/REQUIREMENTS.md']:
  p=ROOT/rel;report['inputs'][rel]=sha(p);q=OUT/'inputs'/rel;q.parent.mkdir(parents=True,exist_ok=True);shutil.copy2(p,q)
 for name,args in [('compile',['c++','-std=c++23','-O2','-Wall','-Wextra','-Werror',str(OUT/'inputs/qa/policy-test.cpp'),'-o',str(OUT/'policy-test')]),('checks',[str(OUT/'policy-test')])]:
  p=subprocess.run(args,capture_output=True,text=True,timeout=30);(OUT/(name+'.stdout')).write_text(p.stdout);(OUT/(name+'.stderr')).write_text(p.stderr);report['commands'].append({'name':name,'exitCode':p.returncode});assert p.returncode==0,p.stderr
 report['checks']=int(p.stdout.split(': ')[1]);assert report['checks']>=790
 report['passed']=True
except Exception as error:report['error']=repr(error)
report['artifacts']={str(p.relative_to(OUT)):sha(p) for p in OUT.rglob('*') if p.is_file()}
(OUT/'report.json').write_text(json.dumps(report,indent=2)+'\n');print(json.dumps({'passed':report['passed'],'checks':report.get('checks'),'report':str(OUT/'report.json'),'error':report.get('error')}));raise SystemExit(not report['passed'])
