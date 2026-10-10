"""Protected incremental Quint and optional compiled local-field checks."""
import hashlib, json, pathlib, resource, subprocess, sys, time
sys.path.insert(0, '/home/hoskinson/window-integration-qa')
from qa_launch import require_qa_scope
scope = require_qa_scope()
assert resource.getrlimit(resource.RLIMIT_CORE) == (1, 1)
root = pathlib.Path(__file__).resolve().parents[1]
assert sys.argv[1:] in ([], ['--init'])
out = root/'qa/runs'/('local-field-'+str(time.time_ns()))
out.mkdir(parents=True)
model = root/'qa/local-field-publication.qnt'
report = {'passed':False,'scope':'Quint sampled/named local field publication abstraction; no native/AT acceptance','sourceSHA256':hashlib.sha256(model.read_bytes()).hexdigest(),'protectedScope':scope,'commands':[]}
commands = [('typecheck',['quint','typecheck',str(model)])]
if not sys.argv[1:]: commands += [('named',['quint','test',str(model),'--match','.*Test'])]
commands += [('sampled',['quint','run',str(model),'--invariant','safety','--max-samples','1' if sys.argv[1:] else '500','--max-steps','5' if sys.argv[1:] else '40','--seed','10010'])]
try:
 for name,args in commands:
  p=subprocess.run(args,cwd=root,capture_output=True,text=True,timeout=120)
  (out/(name+'.stdout')).write_text(p.stdout);(out/(name+'.stderr')).write_text(p.stderr)
  report['commands'].append({'name':name,'argv':args,'exitCode':p.returncode})
  assert p.returncode==0,p.stdout+p.stderr
 report['passed']=True
except Exception as error: report['error']=str(error)
(out/'report.json').write_text(json.dumps(report,indent=2)+'\n')
print(json.dumps({'passed':report['passed'],'report':str(out/'report.json'),'error':report.get('error')}))
raise SystemExit(not report['passed'])
