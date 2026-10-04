from pathlib import Path
import hashlib,json,resource,sys
sys.path.insert(0,'/home/hoskinson/window-integration-qa')
from qa_launch import require_qa_scope
require_qa_scope();assert resource.getrlimit(resource.RLIMIT_CORE)==(1,1)
root=Path(__file__).resolve().parents[1]
sha=lambda p:hashlib.sha256(Path(p).read_bytes()).hexdigest()
selected={'preflight':'preflight-1791135861606184309','lifecycle':'lifecycle-1791135634174967459','observer':'observer-test-1791135634039083643','syntax':'test-1791135819291879477','overflow':'overflow-witness-1791135896216066023'}
reports={k:root/'qa'/v/'report.json' for k,v in selected.items()}
for key,path in reports.items():
 packet=json.loads(path.read_text());assert packet['passed'],key
 if key in ('lifecycle','observer','syntax'):
  assert len(packet['checks'])=={'lifecycle':92,'observer':28,'syntax':22}[key]
  for p,d in packet['inputs'].items():assert sha(p)==d,p
preflight=json.loads(reports['preflight'].read_text());external={}
for p,d in preflight['inputs'].items():
 assert sha(p)==d,p
 if not Path(p).is_relative_to(root):external[p]={'sha256':d,'size':Path(p).stat().st_size}
files={str(p.relative_to(root)):{'sha256':sha(p),'size':p.stat().st_size} for p in sorted(root.rglob('*')) if p.is_file() and '__pycache__' not in p.parts and p.name!='component-manifest.json'}
manifest={'sourceHeld':True,'evidenceIntegrityPassed':True,'nativeAcceptance':False,'physicalHardwareAccepted':False,'nonzeroCapabilityAccepted':False,'scope':'Actual owned runner/typed225 parent query current450+451+AQ155: CPU114+28/preflight only; root native review pending','files':files,'externalFiles':external,'selectedReports':{k:{'path':str(p),'sha256':sha(p)} for k,p in reports.items()}}
path=root/'component-manifest.json';assert not path.exists();path.write_text(json.dumps(manifest,indent=2)+'\n')
for name,row in files.items():assert sha(root/name)==row['sha256']
for name,row in external.items():assert sha(name)==row['sha256']
print(json.dumps({'passed':True,'files':len(files),'externalFiles':len(external),'manifestSHA256':sha(path),'nativeAcceptance':False}))
