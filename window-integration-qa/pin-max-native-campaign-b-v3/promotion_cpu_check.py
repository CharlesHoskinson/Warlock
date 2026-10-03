"""Mechanical source relocation CPU check; never enters a host or runs core."""
from pathlib import Path
import json,hashlib,stat,ast,importlib.util,sys,copy
sys.dont_write_bytecode=True
B=Path(__file__).resolve().parent
P=Path('/home/hoskinson/window-behavior-spec/pin-max-campaign-b-controller-v1-proposal')
V2=Path('/home/hoskinson/window-integration-qa/pin-maximized-native-v2')
checks=[]
def meta(p):return dict(sha256=hashlib.sha256(p.read_bytes()).hexdigest(),mode=stat.S_IMODE(p.stat().st_mode))
record=json.loads((B/'PROMOTION_RECORD.json').read_bytes())
for row in record['copyRecords']:
 src=Path(row['original']);dst=Path(row['copy']);assert meta(src)==dict(sha256=row['sha256'],mode=row['mode'])
 if dst in {B/'capture_packet.py',B/'PAIR_READY.json'}:continue
 assert meta(dst)==meta(src),dst
checks.append(dict(name='all copied bytes/modes exact except declared collector/pair deltas',passed=True,copies=len(record['copyRecords'])))
for rel in ['controller/minimal_controller.py','producer-registry/registry.py','host/b_closure.py','host/candidate_host.py','run_native.py','observer/decode_observation.py','tests/test_controller_packet.py','tests/final-cpu.log','producer_closure.qnt','producer-formal-before-classification-final.json','producer-formal-final-0.log','producer-formal-final-1.log','producer-formal-final-2.log']:assert meta(B/rel)==meta(P/rel)
checks.append(dict(name='runtime/test16/formal14 proof byte/mode conservation',passed=True))
spec=importlib.util.spec_from_file_location('_promoted_b_controller',B/'controller/minimal_controller.py');m=importlib.util.module_from_spec(spec);spec.loader.exec_module(m);assert m.HERE==B
sys.path.insert(0,str(B/'host'));spec=importlib.util.spec_from_file_location('_promoted_b_host',B/'host/candidate_host.py');host=importlib.util.module_from_spec(spec);spec.loader.exec_module(host);assert host.B==B
lua=(V2.parent/'browser-files-flow-v20/nested-qt.lua').read_bytes()+(V2/'private-controls.lua').read_bytes()
obj=host.PrivateHyprSession(B/'attempt-999/host',{},1600,1000,lua);assert obj.host.output==B/'attempt-999/host'and obj.host.runtime is None and obj.host.processes==[]
checks.append(dict(name='actual HERE/B/host constructor resolves promoted QA with no enter/launch',passed=True))
source=Path('/home/hoskinson/window-integration-qa/private-weston-host-v2/weston_host.py');tree=ast.parse(source.read_bytes());cls=next(x for x in tree.body if isinstance(x,ast.ClassDef)and x.name=='PrivateWestonHost');method=next(x for x in cls.body if isinstance(x,ast.FunctionDef)and x.name=='__enter__');guard=next(x for x in method.body if isinstance(x,ast.Assert)and 'startswith'in ast.unparse(x.test));code=compile(ast.Expression(copy.deepcopy(guard.test)),str(source),'eval')
assert eval(code,{'str':str,'Path':Path,'self':obj.host})is True
old=host.PrivateHyprSession(P/'attempt-999/host',{},1600,1000,lua);assert eval(code,{'str':str,'Path':Path,'self':old.host})is False
checks.append(dict(name='exact original guard AST refuses oldSPEC/admitted newQA location',passed=True,primaryGuardSource=meta(source),noEnter=True))
sys.path.insert(0,str(V2/'proposed'));import pair_binding
pair_binding.read_pair(B/'PAIR_READY.json');assert not (B/'ROOT_NATIVE_GRANT.json').exists()and not (B/'frozen-inputs.json').exists()
checks.append(dict(name='actual completed pair/readelf exact and no new native grant',passed=True))
report=dict(result='pass',checks=checks,noGUI=True,noHostEnter=True,noCandidateExecution=True,noNewSemanticProofNeeded=True)
with (B/'PROMOTION_CPU_PROOF.json').open('x')as f:json.dump(report,f,indent=2);f.write('\n')
print(json.dumps(dict(result='pass',checks=len(checks),runtimeDeltas=0,hostEntered=False,sourceOnly=True)))
