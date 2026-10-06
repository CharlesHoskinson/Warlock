"""Preserve failed duplicated-request premise; route actual native initial requests."""
import ast,hashlib,json,pathlib,resource,sys
sys.path.insert(0,'/home/hoskinson/window-integration-qa')
from qa_launch import require_qa_scope
require_qa_scope();assert resource.getrlimit(resource.RLIMIT_CORE)==(1,1)
repo=pathlib.Path('/home/hoskinson/omarchy-windows-parity');root=repo/'implementation/warlock-preview-provider-v92'
sha=lambda p:hashlib.sha256(p.read_bytes()).hexdigest()
failed=root/'qa/retirement-native-elm-check-v2-1791326662419817285/report.json';proof=json.loads(failed.read_text())
assert not proof['passed'] and [(row['name'],row['exitCode']) for row in proof['commands']]==[('flags',0),('compile',0),('roundtrip',1)]
for rel,value in proof['inputs'].items():assert sha(root/rel)==value,rel
for rel,value in proof['artifacts'].items():assert sha(failed.parent/rel)==value,rel
source=root/'native/retirement-elm-channel-test-v3.cpp';assert not source.exists()
s=(root/'native/retirement-elm-channel-test-v2.cpp').read_text()
old='            terminal(1);\n';assert s.count(old)==1
s=s.replace(old,'            check(endpoint.native([](auto& broker){return broker.recordCount()==2 && broker.activeItems()==1;}),"Actual cancellation already physically settled its original untouched producer");\n')
start=s.index('            Json packet("{\\"rows\\":');end=s.index('            check(!warlock_imported_clients_empty(owner)',start)
s=s[:start]+'''            output("neighbor-terminal",events);g_free(events);events=nullptr;
        }else if(op=="check-close") {
'''+s[end:]
source.write_text(s)
script=root/'qa/retirement-native-elm-roundtrip-v2.js';assert not script.exists()
s=(root/'qa/retirement-native-elm-roundtrip.js').read_text()
start=s.index(" await send('presentation',presentation);");end=s.index(' const neighbor=',start)
s=s[:start]+''' await send('presentation',presentation);let result;const issued=[];
 for(const event of start.events){result=await send('native',event);issued.push(...result.commands.flatMap(row=>row.commands));}
 assert.equal(result.models.length,2);checks++;
 assert.equal(issued.length,2);assert.equal(issued[0].kind,'acquire');assert.deepEqual(issued[0].job,start.job);checks++;
 // ImportedClients already emits each original exact request after its seed.
 // A repeated Request deliberately emits nothing; never invent another request.
 await send('native',start.channel);
'''+s[end:]
start=s.index(" const drained=await control({op:'drain-neighbor'});");end=s.index(" const duplicate=",start)
s=s[:start]+''' const drained=await control({op:'drain-neighbor'});result=await feed(drained.events);
 assert.deepEqual(result.commands.flatMap(v=>v.commands).map(v=>v.kind),['acknowledge']);checks++;
 await control({op:'controls',entries:result.commands});
 const closeBarrier=await control({op:'check-close'});assert.deepEqual(closeBarrier.events,completed.events);checks++;
 const confirmed=await control({op:'controls',entries:firstAck});assert.deepEqual(confirmed.events,[]);checks++;
'''+s[end:]
script.write_text(s)
runner=root/'qa/retirement-native-elm-check-v3.py';assert not runner.exists()
s=(root/'qa/retirement-native-elm-check-v2.py').read_text().replace('retirement-native-elm-check-v2','retirement-native-elm-check-v3').replace('native/retirement-elm-channel-test-v2.cpp','native/retirement-elm-channel-test-v3.cpp').replace('qa/retirement-native-elm-roundtrip.js','qa/retirement-native-elm-roundtrip-v2.js')
ast.parse(s);runner.write_text(s)
print(source)
