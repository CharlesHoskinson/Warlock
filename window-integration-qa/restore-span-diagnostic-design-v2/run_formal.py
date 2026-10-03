import json,os,re,subprocess,hashlib
from pathlib import Path
QA=Path('/home/hoskinson/window-integration-qa');D=Path(__file__).resolve().parent
import sys
sys.path.insert(0,str(QA))
from qa_launch import require_qa_scope
require_qa_scope()
Q='/home/hoskinson/.local/share/mise/installs/npm-informalsystems-quint/latest/node_modules/.bin/quint';OUT=QA/'restore-span-diagnostic-formal-v2';OUT.mkdir(mode=0o700)
checks=[];named=0
for n in ('preparation_profile','span_source_binding'):
 for phase,argv in (('typecheck',[Q,'typecheck',str(D/(n+'_test.qnt'))]),('test',[Q,'test',str(D/(n+'_test.qnt')),'--backend=rust','--seed=2026100711']),('run',[Q,'run',str(D/(n+'.qnt')),'--invariant=allProps','--max-samples=2000','--max-steps=100','--backend=rust','--seed=2026100711','--verbosity=1'])):
  p=OUT/(n+'-'+phase+'.log')
  with p.open('x')as f:r=subprocess.run(argv,stdout=f,stderr=subprocess.STDOUT,timeout=60,cwd='/home/hoskinson');f.flush();os.fsync(f.fileno())
  x={'argv':argv,'exitCode':r.returncode,'log':str(p),'sha256':hashlib.sha256(p.read_bytes()).hexdigest()};checks.append(x)
  if r.returncode:raise RuntimeError(str(p))
  if phase=='test':count=int(re.search(r'(\d+) passing',p.read_text()).group(1));named+=count;x['named']=count
row={'result':'pass','named':named,'models':2,'samplesPerModel':2000,'steps':100,'checks':checks,'formalBeforeRuntime':True,'nativeLaunch':False,'sources':{str(p):{'sha256':hashlib.sha256(p.read_bytes()).hexdigest(),'mode':p.stat().st_mode&0o7777}for p in D.iterdir()if p.is_file()}}
with (OUT/'report.json').open('x')as f:json.dump(row,f,indent=2);f.write('\n')
print(json.dumps({'result':'pass','named':named,'models':2}))
