"""Preserve reserved-name Quint failure; fresh model and zero-aware trace codec."""
import ast,hashlib,json,pathlib,resource,sys
sys.path.insert(0,'/home/hoskinson/window-integration-qa')
from qa_launch import require_qa_scope
require_qa_scope();assert resource.getrlimit(resource.RLIMIT_CORE)==(1,1)
repo=pathlib.Path('/home/hoskinson/omarchy-windows-parity');root=repo/'implementation/warlock-preview-provider-v93';sha=lambda p:hashlib.sha256(p.read_bytes()).hexdigest()
failed=root/'qa/retirement-readiness-check-1791327783011053041/report.json';proof=json.loads(failed.read_text());assert not proof['passed'] and 'QNT101' in proof['error'] and "Built-in name 'next'" in proof['error']
for rel,value in proof['inputs'].items():assert sha(root/rel)==value,rel
for rel,value in proof['artifacts'].items():assert sha(failed.parent/rel)==value,rel
p=root/'spec/retirement_readiness_v2.qnt';assert not p.exists()
s=(root/'spec/retirement_readiness.qnt').read_text();old="val next=reduce(s,e);s'={...next,history:";assert s.count(old)==1;p.write_text(s.replace(old,"val updated=reduce(s,e);s'={...updated,history:"))
p=root/'spec/retirement_readiness_tests_v2.qnt';assert not p.exists();p.write_text((root/'spec/retirement_readiness_tests.qnt').read_text().replace('./retirement_readiness"','./retirement_readiness_v2"'))
p=root/'native/retirement-readiness-replay-v2.cpp';assert not p.exists()
s=(root/'native/retirement-readiness-replay.cpp').read_text();old='return decimal(Json::text(Json::child(object,name),"#bigint"));';assert s.count(old)==1;p.write_text(s.replace(old,'const std::string_view text=Json::text(Json::child(object,name),"#bigint");\n    return text=="0"?0:decimal(text);'))
p=root/'qa/retirement-readiness-check-v2.py';assert not p.exists()
s=(root/'qa/retirement-readiness-check.py').read_text().replace('retirement-readiness-check-','retirement-readiness-check-v2-').replace('qa/retirement-readiness-check.py','qa/retirement-readiness-check-v2.py').replace('retirement_readiness.qnt','retirement_readiness_v2.qnt').replace('retirement_readiness_tests.qnt','retirement_readiness_tests_v2.qnt').replace('native/retirement-readiness-replay.cpp','native/retirement-readiness-replay-v2.cpp')
ast.parse(s);p.write_text(s);print(p)
