from pathlib import Path
import hashlib,json,resource,sys
sys.path.insert(0,'/home/hoskinson/window-integration-qa')
from qa_launch import require_qa_scope
require_qa_scope();assert resource.getrlimit(resource.RLIMIT_CORE)==(1,1)
root=Path(__file__).resolve().parents[1]
sha=lambda p:hashlib.sha256(Path(p).read_bytes()).hexdigest()
latest=root/'qa/preflight-1791134069196132387/report.json'
test=root/'qa/test-1791134069055850677/report.json'
assert json.loads(test.read_text())['passed'] and len(json.loads(test.read_text())['checks'])==22
preflight=json.loads(latest.read_text());assert preflight['passed'] and preflight['nativeAcceptance'] is False
external={}
for name,digest in preflight['inputs'].items():
 assert sha(name)==digest,name
 p=Path(name)
 if not p.is_relative_to(root):external[name]={'sha256':digest,'size':p.stat().st_size}
files={str(p.relative_to(root)):{'sha256':sha(p),'size':p.stat().st_size} for p in sorted(root.rglob('*')) if p.is_file() and p.name!='component-manifest.json' and '__pycache__' not in p.parts}
packet={'sourceHeld':True,'evidenceIntegrityPassed':True,'nativeAcceptance':False,'physicalHardwareAccepted':False,'nonzeroCapabilityAccepted':False,'scope':'zero-origin synthetic parent-seat pointer alignment runner; protected CPU22/preflight only','files':files,'externalFiles':external,'selectedTest':str(test),'selectedTestSHA256':sha(test),'selectedPreflight':str(latest),'selectedPreflightSHA256':sha(latest)}
out=root/'component-manifest.json';assert not out.exists(),'Already frozen'
out.write_text(json.dumps(packet,indent=2)+'\n')
for name,row in files.items():assert sha(root/name)==row['sha256']
for name,row in external.items():assert sha(name)==row['sha256']
print(json.dumps({'passed':True,'files':len(files),'externalFiles':len(external),'manifestSHA256':sha(out)}))
