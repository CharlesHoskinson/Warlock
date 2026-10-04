"""Source/profile preservation checks. No host imported or native actor launched."""
import ast,json,hashlib,resource,time
from pathlib import Path
assert resource.getrlimit(resource.RLIMIT_CORE)==(1,1)
s=Path(__file__).resolve().parents[1];r=s.parents[1];plan_path=r/'implementation/elm-geometry-feasible-bounds-profiles-v201/profiles.json'
assert (s/'profiles.json').read_bytes()==plan_path.read_bytes()
plan=json.loads(plan_path.read_text())['profiles'];assert len(plan)==22 and len({p['id'] for p in plan})==22
old=r/'implementation/elm-geometry-xdg-origin-native-v196/qa/native.py';new=s/'qa/native.py'
def names(path):
 return sorted(ast.dump(n.args[0]) for n in ast.walk(ast.parse(path.read_text())) if isinstance(n,ast.Call) and isinstance(n.func,ast.Name) and n.func.id=='check')
oldnames=names(old);newnames=names(new);assert all(n in newnames for n in oldnames)
# External201 baseline rows must match the actual original196 literal profile constructor.
globals196={};tree=ast.parse(old.read_text());assignment=next(n for n in tree.body if isinstance(n,ast.Assign) and any(isinstance(t,ast.Name) and t.id=='PROFILES' for t in n.targets));exec(compile(ast.Module(body=[assignment],type_ignores=[]),'original196profileconstructor','exec'),globals196)
assert globals196['PROFILES']==[(p['id'],[*p['origin'],*p['pads'],p['bufferScale']],p['maximum']) for p in plan if p['retainedBaseline']]
groups=[((800,600),1),((1600,1200),2),((800,600),2)];parts=[[p for p in plan if tuple(p['physicalMode'])==physical and p['monitorScale']==scale] for physical,scale in groups]
assert [len(p) for p in parts]==[14,6,2] and sum(len(p) for p in parts)==22
assert all(not p['expectedMAX'] and p['minimum']==[640,480] and p['expectedLogicalWorkarea']==[0,0,400,300] for p in parts[-1])
assert len([p for p in plan if p['expectedMAX']])==10
out=s/'qa'/('plan-test-'+str(time.time_ns()));out.mkdir();report={'passed':True,'checks':7,'scope':'Exact201 profile bytes, original196 profile/check-name AST preservation and independent closed campaign partition; no native mode/behavior qualification','inputs':{str(p):hashlib.sha256(p.read_bytes()).hexdigest() for p in [Path(__file__),plan_path,s/'profiles.json',old,new]}}
(out/'report.json').write_text(json.dumps(report,indent=2)+'\n');print(json.dumps({'passed':True,'report':str(out/'report.json')}))
