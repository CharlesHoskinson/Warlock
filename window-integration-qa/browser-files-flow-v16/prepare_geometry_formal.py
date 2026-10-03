"""Run the exact geometry models before changing V13 runtime source."""
from pathlib import Path
import hashlib,json,subprocess
B=Path(__file__).resolve().parent;OLD=B.with_name('browser-files-flow-v13')
def sha(p):return hashlib.sha256(Path(p).read_bytes()).hexdigest()
rows=[]
for model in ['viewport_geometry','coordinate_representation','pointer_syntax']:
 for command in [['quint','test',str(B/(model+'_test.qnt'))],['quint','run',str(B/(model+'.qnt')),'--invariant=allProps','--max-samples=2000','--max-steps=100','--seed=20261002','--verbosity=1']]:
  r=subprocess.run(command,capture_output=True,text=True,timeout=45);rows.append(dict(command=command,returncode=r.returncode,stdout=r.stdout,stderr=r.stderr))
  if r.returncode:
   (B/'geometry-formal-preparation-failure.json').write_text(json.dumps(rows,indent=2)+'\n');raise RuntimeError(rows[-1])
names=['private_session.py','compose.html','cdp_readonly.py']
assert all((B/k).read_bytes()==(OLD/k).read_bytes()for k in names),'Runtime must remain frozen V13 until this proof'
report=dict(result='pass',commands=rows,nativeExecuted=False,runtimeStillExactFrozenV13=True,namedCases=45,models=3,randomTracesPerModel=2000,maxSteps=100,sourceSHA256={k:sha(B/k)for k in ['V14_GEOMETRY_CONTRACT.md','viewport_geometry.qnt','viewport_geometry_test.qnt','coordinate_representation.qnt','coordinate_representation_test.qnt','pointer_syntax.qnt','pointer_syntax_test.qnt',*names]},preparationFailuresRetained=['Missing assignment parentheses QNT000','Undefined abs QNT404','Annotated action parameter missing bool return QNT parser error'])
p=B/'geometry-formal-before-implementation.json';assert not p.exists();p.write_text(json.dumps(report,indent=2)+'\n');print(json.dumps({'result':'pass','named':45,'models':3,'randomEach':2000,'sha256':sha(p)}))
