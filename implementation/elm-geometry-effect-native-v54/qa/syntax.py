import hashlib,json,time
from pathlib import Path
import sys
sys.path.insert(0,"/home/hoskinson/window-integration-qa")
from qa_launch import require_qa_scope
require_qa_scope()
p=Path(__file__).with_name("native.py")
compile(p.read_bytes(),str(p),"exec")
out=p.parent/("syntax-"+str(time.time_ns()));out.mkdir()
r={"passed":True,"scope":"Syntax only; no native acceptance", "input":str(p),"sha256":hashlib.sha256(p.read_bytes()).hexdigest()}
(out/"report.json").write_text(json.dumps(r,indent=2)+"\n")
print(str(out/"report.json"))
