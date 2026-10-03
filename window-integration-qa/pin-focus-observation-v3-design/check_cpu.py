from pathlib import Path
import hashlib, json, os, subprocess, sys, ast
sys.path.insert(0, '/home/hoskinson/window-integration-qa')
from qa_launch import require_qa_scope
require_qa_scope()
QA = Path('/home/hoskinson/window-integration-qa')
B = QA/'pin-native-qa-v3'
O = QA/'pin-focus-observation-v3-cpu-v1'
O.mkdir(mode=0o700)
sources = {str(p): hashlib.sha256(p.read_bytes()).hexdigest() for p in B.rglob('*')
           if p.is_file() and '__pycache__' not in p.parts}
def methods(p):
    t=ast.parse(p.read_text())
    return {n.name: ast.dump(n,include_attributes=False) for n in ast.walk(t) if isinstance(n,ast.FunctionDef)}
old=methods(QA/'pin-native-qa-v2/native_cases.py');new=methods(B/'native_cases.py')
assert set(new)-set(old)=={'focus_pair'}
assert [n for n in old if old[n]!=new[n]]==['focus']
assert old['wait']==new['wait']
def gates(p):
    return [ast.dump(n,include_attributes=False) for n in ast.walk(ast.parse(p.read_text()))
            if isinstance(n,ast.Call) and isinstance(n.func,ast.Attribute) and n.func.attr=='check'
            and isinstance(n.func.value,ast.Name) and n.func.value.id=='self']
assert gates(QA/'pin-native-qa-v2/native_cases.py')==gates(B/'native_cases.py')
env=dict(os.environ,PYTHONDONTWRITEBYTECODE='1',PYTHONPATH=str(B))
cmd=['/usr/bin/python3','-B','-m','unittest','discover','-s',str(B),'-v']
with (O/'cpu.log').open('x') as f:
    r=subprocess.run(cmd,cwd='/home/hoskinson',env=env,stdout=f,stderr=subprocess.STDOUT,timeout=60)
    f.flush();os.fsync(f.fileno())
unchanged=all(hashlib.sha256(Path(p).read_bytes()).hexdigest()==h for p,h in sources.items())
row={'result':'pass' if r.returncode==0 and unchanged else 'fail','exitCode':r.returncode,
     'sourceUnchanged':unchanged,'sources':sources,'nativeLaunch':False,'mainChanged':False,
     'originalSixStaticGatesExact':True,'originalWaitASTExact':True,'originalOtherMethodsExact':True,
     'scope':Path('/proc/self/cgroup').read_text().strip()}
with (O/'report.json').open('x') as f:
    json.dump(row,f,indent=2);f.write('\n');f.flush();os.fsync(f.fileno())
print(json.dumps({k:v for k,v in row.items() if k!='sources'}))
raise SystemExit(row['result']!='pass')
