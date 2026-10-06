"""Explicit selected receipt abstraction coupled to the actual optimized Elm implementation."""
import hashlib,json,pathlib,re,resource,shutil,subprocess,sys,time
ROOT=pathlib.Path(__file__).resolve().parents[1]
sys.path.insert(0,"/home/hoskinson/window-integration-qa")
from qa_launch import require_qa_scope
scope=require_qa_scope();assert resource.getrlimit(resource.RLIMIT_CORE)==(1,1)
OUT=ROOT/"qa"/("receipt-check-"+str(time.time_ns()));OUT.mkdir()
sha=lambda p:hashlib.sha256(p.read_bytes()).hexdigest()
TOOL=pathlib.Path("/home/hoskinson/.local/share/mise/installs/npm-informalsystems-quint/latest/node_modules/.bin/quint")
source={str(p.relative_to(ROOT)):sha(p) for folder in ["src","native","spec","qa"] for p in (ROOT/folder).glob("*") if p.is_file() and p.name!="current-build.json"}
report={"passed":False,"scope":scope,"inputs":source,"nativeAcceptance":False,"fullReleaseAccepted":False,"toolSHA256":sha(TOOL.resolve()),"commands":[],"projection":"Exact known-job terminal correlation, single retained terminal(job,sequence) replay, next request and emitted ACKs against current compiled Elm for one fixed own binding/scope and Refused receipts. Later jobs are controlled typed messages; no native ownership/pixels or whole policy refinement."}
def run(name,cmd,input=None,cwd=None):
 p=subprocess.run(cmd,cwd=cwd or OUT,capture_output=True,text=True,timeout=180,input=input)
 (OUT/(name+".stdout")).write_text(p.stdout);(OUT/(name+".stderr")).write_text(p.stderr)
 report["commands"].append({"name":name,"argv":cmd,"exitCode":p.returncode});print(name,p.returncode,flush=True)
 assert p.returncode==0,p.stderr or p.stdout
 return p.stdout
try:
 builds=sorted(ROOT.glob("qa/build-*/report.json"));build=builds[-1];held=json.loads(build.read_text());assert held["passed"]
 assert all(sha(ROOT/rel)==value for rel,value in held["inputs"].items()),"Actual full GUI build source changed"
 report["compiledBuild"]={"path":str(build),"sha256":sha(build)}
 for rel in ["spec/receipt.qnt","spec/receipt_tests.qnt","qa/receipt-replay.js","qa/native-source-fixture.json"]:
  dst=OUT/"inputs"/rel;dst.parent.mkdir(parents=True,exist_ok=True);shutil.copy2(ROOT/rel,dst)
 compiled=build.parent/"inputs/assets/preview-replay.js";shutil.copy2(compiled,OUT/"receipt-replay.js");report["compiledElmSHA256"]=sha(compiled)
 folder=OUT/"inputs/spec";names=re.findall(r"run (\w+)\s*=",(folder/"receipt_tests.qnt").read_text());assert len(names)==len(set(names))==8
 run("typecheck",[str(TOOL),"typecheck","receipt_tests.qnt"],cwd=folder)
 run("selected",[str(TOOL),"test","receipt_tests.qnt","--main=receipt_tests","--backend=typescript","--match=^("+"|".join(names)+")$","--seed=710003","--max-samples=1","--out-itf="+str(OUT/"named-{test}-{seq}.itf.json")],cwd=folder)
 assert len(list(OUT.glob("named-*.itf.json")))==8
 run("samples",[str(TOOL),"run","receipt.qnt","--main=receipt","--backend=typescript","--invariant=safety","--seed=710004","--max-samples=100","--max-steps=24","--n-traces=8","--out-itf="+str(OUT/"sample-{seq}.itf.json")],cwd=folder)
 def decode(value):
  if isinstance(value,list):return [decode(v) for v in value]
  if isinstance(value,dict):
   if "#bigint" in value:return int(value["#bigint"])
   return {k:decode(v) for k,v in value.items()}
  return value
 coupled=[]
 for path in sorted(OUT.glob("*.itf.json")):
  states=[row["s"] for row in decode(json.loads(path.read_text()))["states"]];history=states[-1]["history"]
  actual=json.loads(run("replay-"+path.stem,["node",str(OUT/"inputs/qa/receipt-replay.js"),str(OUT/"receipt-replay.js"),str(OUT/"inputs/qa/native-source-fixture.json"),"--replay"],input=json.dumps(history)))
  expected=[];count=0
  for state in states:
   if len(state["history"])==count:continue
   count=len(state["history"]);expected.append({**state,"history":[]})
  assert actual==expected,(path.name,actual,expected)
  coupled.append({"trace":path.name,"statesCompared":len(actual)})
 assert len(coupled)==16
 report.update(selectedNames=names,namedScenarios=8,invariantSamples=100,coupledTraces=coupled,statesCompared=sum(v["statesCompared"] for v in coupled))
 assert all(sha(ROOT/rel)==value for rel,value in source.items()),"Source changed during selected implementation checks"
 parent=ROOT.parent/'warlock-preview-provider-v70';oldBuild=next(parent.glob('qa/build-*/report.json'));old=json.loads(oldBuild.read_text());assert old['passed'];oldElm=oldBuild.parent/'inputs/assets/preview-replay.js';assert sha(oldElm)==old['compiledAssetPackage']['files']['preview-replay.js']
 caught=[]
 for name in ['futureAfterOriginalFinal','alteredSequenceRefused']:
  paths=list(OUT.glob('named-'+name+'-*.itf.json'));assert len(paths)==1
  states=[row['s'] for row in decode(json.loads(paths[0].read_text()))['states']];history=states[-1]['history'];expected=[];count=0
  for state in states:
   if len(state['history'])==count:continue
   count=len(state['history']);expected.append({**state,'history':[]})
  actual=json.loads(run('retained-unsafe-'+name,['node',str(OUT/'inputs/qa/receipt-replay.js'),str(oldElm),str(OUT/'inputs/qa/native-source-fixture.json'),'--replay'],input=json.dumps(history)))
  assert actual!=expected,(name,'retained actual unsafe Elm escaped oracle');caught.append({'name':name,'observableMismatch':True})
 report.update(unsafeCounterexamplesDetected=len(caught),retainedUnsafeProgram={'buildReport':str(oldBuild),'sha256':sha(oldBuild),'compiledElmSHA256':sha(oldElm)},counterexamples=caught)
 report["passed"]=True
except Exception as error:report["error"]=repr(error)
report["artifacts"]={str(p.relative_to(OUT)):sha(p) for p in OUT.rglob("*") if p.is_file()}
(OUT/"report.json").write_text(json.dumps(report,indent=2)+"\n");print(json.dumps({"passed":report["passed"],"report":str(OUT/"report.json"),"error":report.get("error")}),flush=True);raise SystemExit(not report["passed"])
