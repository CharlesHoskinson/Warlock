"""Whole-function conservation proof for the root-approved oracle-only delta."""
import ast,difflib,hashlib,json,stat
from pathlib import Path
B=Path(__file__).resolve().parent
P=B.with_name('pin-max-native-campaign-b-v2')
def meta(p):return dict(sha256=hashlib.sha256(p.read_bytes()).hexdigest(),mode=stat.S_IMODE(p.stat().st_mode))
def dump(n):return ast.dump(n,include_attributes=False)
def selected(tree,name):return next(n for n in ast.walk(tree)if isinstance(n,ast.FunctionDef)and n.name==name)
def verify():
 old=P/'controller/minimal_controller.py';new=B/'controller/minimal_controller.py';a=ast.parse(old.read_bytes());b=ast.parse(new.read_bytes())
 original=selected(a,'native_max_case');refined=selected(b,'native_max_case')
 conserved=next(n.value for n in refined.body if isinstance(n,ast.Assign)and any(isinstance(t,ast.Name)and t.id=='conserved'for t in n.targets))
 assert len(conserved.elts)==18
 assert [n.value for n in conserved.elts]==['internalMode','clientMode','floating','logicalBox','visualBox','restoreValid','restoreGeneration','restoreLogicalBox','restoreVisualBox','restoreFloating','restoreLayoutHandled','restoreTarget','restoreLayoutTarget','restoreSpace','target','space','workspace','output']
 markerMessages=['exact native MAX pin-origin and managed markers immediately after genuine pin','exact native MAX unpin-origin and managed markers immediately after genuine unpin','exact native MAX unpin-origin and managed markers at final observation']
 markerStatements=[n for n in refined.body if isinstance(n,ast.Expr)and isinstance(n.value,ast.Call)and len(n.value.args)==2 and isinstance(n.value.args[1],ast.Constant)and n.value.args[1].value in markerMessages]
 assert len(markerStatements)==3
 # Exact expected source text binds every introduced predicate and its phase.
 expected=["require(first_after['owned']['body']['restoreOrigin']is True and first_after['owned']['body']['restoreManaged']is True,"+repr(markerMessages[0])+")", "require(second_after['owned']['body']['restoreOrigin']is False and second_after['owned']['body']['restoreManaged']is True,"+repr(markerMessages[1])+")", "require(current['restoreOrigin']is False and current['restoreManaged']is True,"+repr(markerMessages[2])+")"]
 assert [dump(x)for x in markerStatements]==[dump(ast.parse(x).body[0])for x in expected]
 refined.body=[n for n in refined.body if n not in markerStatements]
 conserved.elts[14:14]=[ast.Constant(value='restoreOrigin'),ast.Constant(value='restoreManaged')]
 assert dump(a)==dump(b),'complete controller inverse must equal inherited source'
 oldtests=ast.parse((P/'tests/test_controller_packet.py').read_bytes());newtests=ast.parse((B/'tests/test_controller_packet.py').read_bytes());added=[n for n in newtests.body if isinstance(n,ast.ClassDef)and n.name=='NativeMaxMarkerTests'];assert len(added)==1
 newtests.body.remove(added[0]);assert dump(oldtests)==dump(newtests),'all original tests whole AST exact'
 exact=['run_native.py','host/candidate_host.py','host/b_closure.py','producer-registry/registry.py','observer/decode_observation.py','producer_closure.qnt','producer-formal-before-classification-final.json','producer-formal-final-0.log','producer-formal-final-1.log','producer-formal-final-2.log','promotion_preflight.py']
 for name in exact:assert meta(P/name)==meta(B/name),name
 return dict(result='pass',wholeControllerInverse=True,exactConservedFields=18,exactMarkerPredicates=3,allOriginal16TestBodiesExact=True,originalFirstPinCorruptionTestExact=True,unchangedRuntimeAndFormal={n:meta(B/n)for n in exact},sourceOnly=True,nativeExecuted=False)
if __name__=='__main__':print(json.dumps(verify(),indent=2))
