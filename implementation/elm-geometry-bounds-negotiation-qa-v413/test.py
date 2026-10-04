import copy,hashlib,json,resource,sys,time
from pathlib import Path
sys.path.insert(0,"/home/hoskinson/window-integration-qa")
from qa_launch import require_qa_scope
require_qa_scope();assert resource.getrlimit(resource.RLIMIT_CORE)==(1,1)
ROOT=Path(__file__).resolve().parent;REPO=ROOT.parents[1];SOURCE=REPO/"implementation/elm-shared-geometry-bounds-v410"
OUT=ROOT/("checks-"+str(time.time_ns()));OUT.mkdir();sys.path.insert(0,str(SOURCE/"adapter"))
from geometry_endpoint import GeometryEndpoint
from endpoint import Refused
sha=lambda p:hashlib.sha256(p.read_bytes()).hexdigest()
files=[SOURCE/"adapter/geometry_endpoint.py",SOURCE/"adapter/geometry_size_policy.py",SOURCE/"adapter/endpoint.py",SOURCE/"adapter/effect_endpoint.py",Path(__file__).resolve()]
report={"passed":False,"nativeAcceptance":False,"scope":"Actual Python observation negotiation and refusal correlation, synthetic native replies","inputs":{str(p):sha(p) for p in files}}
checks=0
try:
 template=json.loads((SOURCE/"qa/shared-geometry-fixtures.json").read_text())["attach"]
 def client(response):
  c=object.__new__(GeometryEndpoint);c.bound=copy.deepcopy(template["binding"]);c.geometry_protocol=None;c.requests=[]
  def request(packet):c.requests.append(packet);return copy.deepcopy(response)
  c.request=request;return c
 for version in [1,2]:
  packet=copy.deepcopy(template);packet["geometryProtocol"]=version;c=client(packet)
  response=c.geometry_attach(template["requestId"],version)
  assert c.geometry_protocol==version and c.geometry_binding==c.bound and c.requests[0]["geometryProtocol"]==version;checks+=1
 packet=copy.deepcopy(template);packet["geometryProtocol"]=2;c=client(packet);c.geometry_attach(template["requestId"]);assert c.geometry_protocol==2;checks+=1
 for version in [True,False,0,3,"2",None]:
  c=client(packet)
  try:c.geometry_attach(template["requestId"],version);raise AssertionError("invalid negotiated version accepted")
  except Refused:pass
  assert c.requests==[] and c.geometry_protocol is None;checks+=1
 for field,value in [("geometryProtocol",1),("geometryProtocol",True),("requestId","999"),("kind","geometry-facts")]:
  bad=copy.deepcopy(packet);bad[field]=value;c=client(bad)
  try:c.geometry_attach(template["requestId"]);raise AssertionError("bad response accepted")
  except Refused:pass
  assert c.geometry_protocol is None;checks+=1
 for p in files:assert sha(p)==report["inputs"][str(p)]
 report.update(passed=True,checks=checks)
except Exception as error:report["error"]=repr(error)
(OUT/"report.json").write_text(json.dumps(report,indent=2)+"\n");print(json.dumps(report));raise SystemExit(not report["passed"])
