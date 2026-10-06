"""Keep rejected fixture clock; use actual native struct field order in fresh replay."""
import ast,hashlib,json,pathlib,resource,sys
sys.path.insert(0,'/home/hoskinson/window-integration-qa')
from qa_launch import require_qa_scope
require_qa_scope();assert resource.getrlimit(resource.RLIMIT_CORE)==(1,1)
root=pathlib.Path('/home/hoskinson/omarchy-windows-parity/implementation/warlock-preview-provider-v93');sha=lambda p:hashlib.sha256(p.read_bytes()).hexdigest()
failed=root/'qa/retirement-readiness-check-v2-1791327885384017994/report.json';proof=json.loads(failed.read_text());assert not proof['passed'] and 'Exact permanent retirement observation' in proof['error']
assert all(row['exitCode']==0 for row in proof['commands'][:5])
for rel,value in proof['inputs'].items():assert sha(root/rel)==value,rel
for rel,value in proof['artifacts'].items():assert sha(failed.parent/rel)==value,rel
p=root/'native/retirement-readiness-replay-v3.cpp';assert not p.exists()
s=(root/'native/retirement-readiness-replay-v2.cpp').read_text();old='observation{binding,{20},1,1,{17},100,30,IncarnationState::Retired}';assert s.count(old)==1
p.write_text(s.replace(old,'observation{binding,{20},{17},1,1,100,30,IncarnationState::Retired}'))
p=root/'qa/retirement-readiness-check-v3.py';assert not p.exists()
s=(root/'qa/retirement-readiness-check-v2.py').read_text().replace('retirement-readiness-check-v2','retirement-readiness-check-v3').replace('native/retirement-readiness-replay-v2.cpp','native/retirement-readiness-replay-v3.cpp')
ast.parse(s);p.write_text(s);print(p)
