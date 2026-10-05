import hashlib,importlib.util,json,resource,sys,time
from pathlib import Path
sys.path.insert(0,'/home/hoskinson/window-integration-qa');from qa_launch import require_qa_scope
require_qa_scope();assert resource.getrlimit(resource.RLIMIT_CORE)==(1,1)
ROOT=Path(__file__).resolve().parent;P=ROOT.parent/'elm-own-popup-runtime-closure-guard-v329/guard.py';OUT=ROOT/('pid-'+str(time.time_ns()));OUT.mkdir(mode=0o700);raw=P.read_bytes();q=OUT/'guard.py';q.write_bytes(raw);q.chmod(0o444)
spec=importlib.util.spec_from_file_location('guard',q);g=importlib.util.module_from_spec(spec);spec.loader.exec_module(g)
r={'passed':True,'nativeAcceptance':False,'scope':'Actual329 malformed PID caller boundary characterization; no arbitrary process action','sourceSHA256':hashlib.sha256(raw).hexdigest(),'cases':[]}
for value in [True,'not-a-pid',-1]:
 try:g.verify_process(pid=value,start=1,tuple_evidence={},deadline=time.monotonic()+0.1);outcome='accepted';detail=None
 except g.Refused as e:outcome='typed-refused';detail=str(e)
 except Exception as e:outcome='ordinary-error';detail=repr(e)
 r['cases'].append({'pid':value,'outcome':outcome,'detail':detail})
assert all(x['outcome']=='ordinary-error' for x in r['cases'])
(OUT/'report.json').write_text(json.dumps(r,indent=2)+'\n');print(OUT/'report.json');print('PASS preserved late PID guards')
