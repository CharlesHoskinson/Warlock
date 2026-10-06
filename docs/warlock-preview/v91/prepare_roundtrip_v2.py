"""Retain Werror fixture evidence, prepare fresh spelling correction and regressions."""
import ast,hashlib,json,pathlib,resource,sys
sys.path.insert(0,'/home/hoskinson/window-integration-qa')
from qa_launch import require_qa_scope
require_qa_scope();assert resource.getrlimit(resource.RLIMIT_CORE)==(1,1)
repo=pathlib.Path('/home/hoskinson/omarchy-windows-parity');root=repo/'implementation/warlock-preview-provider-v92'
sha=lambda p:hashlib.sha256(p.read_bytes()).hexdigest()
failed=root/'qa/retirement-native-elm-check-1791326583094783725/report.json';proof=json.loads(failed.read_text())
assert not proof['passed'] and [(row['name'],row['exitCode']) for row in proof['commands']]==[('flags',0),('compile',1)]
assert 'misleading-indentation' in proof['error']
for rel,value in proof['inputs'].items():assert sha(root/rel)==value,rel
for rel,value in proof['artifacts'].items():assert sha(failed.parent/rel)==value,rel
source=root/'native/retirement-elm-channel-test-v2.cpp';assert not source.exists()
s=(root/'native/retirement-elm-channel-test.cpp').read_text()
old='if(std::string_view(events)!="[]")emitted=events;g_free(events);events=nullptr;'
assert s.count(old)==1;source.write_text(s.replace(old,'if(std::string_view(events)!="[]") {emitted=events;}\n                        g_free(events);events=nullptr;'))
runner=root/'qa/retirement-native-elm-check-v2.py';assert not runner.exists()
s=(root/'qa/retirement-native-elm-check.py').read_text().replace('retirement-native-elm-check-', 'retirement-native-elm-check-v2-').replace('qa/retirement-native-elm-check.py','qa/retirement-native-elm-check-v2.py').replace('native/retirement-elm-channel-test.cpp','native/retirement-elm-channel-test-v2.cpp')
ast.parse(s);runner.write_text(s)
runner=pathlib.Path(__file__).parent/'regressions92.py';assert not runner.exists()
s=(repo/'docs/warlock-preview/v89/regressions89.py').read_text().replace('warlock-preview-provider-v89','warlock-preview-provider-v92').replace('regressions89-','regressions92-')
ast.parse(s);runner.write_text(s)
print(source)
