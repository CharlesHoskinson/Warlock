import hashlib,json,resource,shutil,subprocess,sys,time
from pathlib import Path
sys.path.insert(0,"/home/hoskinson/window-integration-qa")
from qa_launch import require_qa_scope
require_qa_scope();assert resource.getrlimit(resource.RLIMIT_CORE)==(1,1)
ROOT=Path(__file__).resolve().parent;REPO=ROOT.parents[1];OUT=ROOT/("diagnostic-"+str(time.time_ns()));OUT.mkdir()
sha=lambda p:hashlib.sha256(p.read_bytes()).hexdigest()
report={"passed":False,"scope":"Actual old380 versus new416 output-controller regression diagnostic, no changed production source or GUI","lanes":{},"inputs":{}}
try:
 for lane,sourceName in [("ancestor","elm-shared-registration-shutdown-merge-v380"),("bounds","elm-shared-geometry-bounds-fixtures-v416")]:
  source=REPO/"implementation"/sourceName;area=OUT/lane;area.mkdir();(area/"src").mkdir();(area/"qa").mkdir()
  for p in (source/"src").glob("*.elm"):
   shutil.copy2(p,area/"src"/p.name);report["inputs"][str(p)]=sha(p)
  shutil.copy2(source/"elm.json",area/"elm.json");report["inputs"][str(source/"elm.json")]=sha(source/"elm.json")
  p=source/"qa/outputs.cjs";text=p.read_text();report["inputs"][str(p)]=sha(p)
  before="verify(rows.at(-1),rows);cases.push({name,rows});"
  after="try{verify(rows.at(-1),rows)}catch(error){fs.writeFileSync(process.argv[3],JSON.stringify({passed:false,name,error:String(error),rows,cases},null,2));throw error};cases.push({name,rows});"
  assert text.count(before)==1;(area/"qa/outputs.cjs").write_text(text.replace(before,after))
  results=[]
  for name,args in [("compile",["npm","exec","--yes","--package=elm@0.19.2-0","--","elm","make","src/OutputReplay.elm","--output="+str(area/"worker.js")]),("replay",["node",str(area/"qa/outputs.cjs"),str(area/"worker.js"),str(area/"result.json")])]:
   result=subprocess.run(args,cwd=area,capture_output=True,text=True,timeout=180);(area/(name+".stdout")).write_text(result.stdout);(area/(name+".stderr")).write_text(result.stderr);results.append({"name":name,"exitCode":result.returncode})
   if name=="compile":assert result.returncode==0,result.stderr
  evidence=json.loads((area/"result.json").read_text());report["lanes"][lane]={"commands":results,"result":evidence}
 for path,digest in report["inputs"].items():assert sha(Path(path))==digest
 report["passed"]=True
except Exception as error:report["error"]=repr(error)
report["artifacts"]={str(p.relative_to(OUT)):sha(p) for p in OUT.rglob("*") if p.is_file() and "elm-stuff" not in p.parts}
(OUT/"report.json").write_text(json.dumps(report,indent=2)+"\n")
print(json.dumps({"passed":report["passed"],"lanes":{lane:{"passed":row["result"]["passed"],"case":row["result"].get("name")} for lane,row in report["lanes"].items()},"report":str(OUT/"report.json"),"error":report.get("error")}));raise SystemExit(not report["passed"])
