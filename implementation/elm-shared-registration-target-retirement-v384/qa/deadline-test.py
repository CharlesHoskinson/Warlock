import ast,json,pathlib,resource,sys,time,types
sys.path.insert(0,"/home/hoskinson/window-integration-qa")
from qa_launch import require_qa_scope
require_qa_scope();assert resource.getrlimit(resource.RLIMIT_CORE)==(1,1)
ROOT=pathlib.Path(__file__).resolve().parents[1];OUT=ROOT/"qa"/("deadline-"+str(time.time_ns()));OUT.mkdir()
def load(path,finish):
 tree=ast.parse(path.read_text());fn=next(n for n in tree.body if isinstance(n,ast.FunctionDef) and n.name=="wait")
 clock=types.SimpleNamespace(now=0.)
 ns={"time":types.SimpleNamespace(monotonic=lambda:clock.now,sleep=lambda seconds:setattr(clock,"now",clock.now+seconds)),"s":types.SimpleNamespace(guard=lambda:None)}
 exec(compile(ast.fix_missing_locations(ast.Module(body=[fn],type_ignores=[])),str(path),"exec"),ns)
 def result():clock.now=finish;return "observed"
 return ns["wait"],result
checks=[]
for finish in [6.001,6.,9.]:
 old,predicate=load(ROOT.parent/"elm-shared-context-disposition-native-v133/qa/native.py",finish);assert old(predicate)=="observed"
 new,predicate=load(ROOT/"qa/native.py",finish)
 try:new(predicate);raise AssertionError("Late result accepted")
 except RuntimeError as e:assert str(e)=="Unchanged observation deadline"
 checks.append("Late truthy predicate at "+str(finish)+" rejected; inherited control accepted")
new,predicate=load(ROOT/"qa/native.py",5.999);assert new(predicate)=="observed";checks.append("In-budget observation accepted")
report={"passed":True,"checks":checks,"nativeAcceptance":False,"scope":"Actual extracted inherited/current wait functions; original six-second budget retained"}
(OUT/"report.json").write_text(json.dumps(report,indent=2)+"\n");print(json.dumps({"report":str(OUT/"report.json"),"checks":len(checks)}))
