from pathlib import Path
import hashlib,importlib.util,json,resource,sys,time
sys.path.insert(0,'/home/hoskinson/window-integration-qa')
from qa_launch import require_qa_scope
require_qa_scope();assert resource.getrlimit(resource.RLIMIT_CORE)==(1,1)
root=Path(__file__).resolve().parents[1];source=root/'qa/rejected/parent-observation-before-hugeint.py'
spec=importlib.util.spec_from_file_location('preserved_unsafe_point',source);m=importlib.util.module_from_spec(spec);spec.loader.exec_module(m)
cases=[]
for sign in (1,-1):
 value=json.loads(json.dumps([sign*10**400,61]))
 try:m.point(value);observed='accepted'
 except Exception as e:observed=type(e).__name__
 assert observed=='OverflowError'
 cases.append({'sign':sign,'actualException':observed,'requiredTypedRefusal':'Refused'})
out=root/'qa'/('overflow-witness-'+str(time.time_ns()));out.mkdir()
(out/'report.json').write_text(json.dumps({'passed':True,'scope':'Actual preserved unsafe point function characterization; two JSON-decoded huge integers, no native query','cases':cases,'source':str(source),'sourceSHA256':hashlib.sha256(source.read_bytes()).hexdigest()},indent=2)+'\n')
print(json.dumps({'passed':True,'cases':2,'report':str(out/'report.json')}))
