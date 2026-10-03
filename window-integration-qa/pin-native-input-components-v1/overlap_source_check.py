"""Exact whole-body inverse and current CPU-adapter binding; no native launch."""
import ast,json,hashlib,stat
from pathlib import Path
B=Path(__file__).resolve().parent
P=B.with_name('pin-max-native-campaign-b-v3')
AUDIT=B.parent/'pin-max-native-b-v3-overlap-audit-v1'
def meta(p):return dict(sha256=hashlib.sha256(p.read_bytes()).hexdigest(),mode=stat.S_IMODE(p.stat().st_mode))
def verify():
 before=ast.parse((P/'controller/minimal_controller.py').read_bytes());after=ast.parse((B/'controller/minimal_controller.py').read_bytes())
 assignments=[n for n in ast.walk(after)if isinstance(n,ast.Assign)and any(isinstance(t,ast.Name)and t.id=='peer_box'for t in n.targets)]
 assert len(assignments)==1;n=assignments[0]
 assert ast.dump(n.value,include_attributes=False)==ast.dump(ast.parse("self.qt_box(actor,'peer',peer)",mode='eval').body,include_attributes=False)
 n.value=ast.parse("peer_max['body']['visualBox']",mode='eval').body
 assert ast.dump(before,include_attributes=False)==ast.dump(after,include_attributes=False)
 assert (B/'controller/minimal_controller.py').read_bytes()==(AUDIT/'minimal_controller.py.proposed').read_bytes(),'CPU whole-body adapter exact current source'
 exact=['tests/test_controller_packet.py','run_native.py','host/candidate_host.py','host/b_closure.py','producer-registry/registry.py','observer/decode_observation.py','producer_closure.qnt','producer-formal-before-classification-final.json','producer-formal-final-0.log','producer-formal-final-1.log','producer-formal-final-2.log','promotion_preflight.py']
 for name in exact:assert meta(P/name)==meta(B/name),name
 return dict(result='pass',wholeControllerInverse=True,onlyExpressionChanged='self.qt_box(actor,\'peer\',peer)',currentWholeBodyCPUAdapterExact=True,allOriginal19TestsExact=True,unchangedRuntimeAndFormal={n:meta(B/n)for n in exact},newNativeReachabilityClaim=False,sourceOnly=True)
if __name__=='__main__':print(json.dumps(verify(),indent=2))
