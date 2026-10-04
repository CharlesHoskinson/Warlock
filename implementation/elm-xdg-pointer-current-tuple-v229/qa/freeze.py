from pathlib import Path
import hashlib,json,resource,sys
sys.path.insert(0,'/home/hoskinson/window-integration-qa')
from qa_launch import require_qa_scope
require_qa_scope();assert resource.getrlimit(resource.RLIMIT_CORE)==(1,1)
ROOT=Path(__file__).resolve().parents[1]
def sha(path):return hashlib.sha256(Path(path).read_bytes()).hexdigest()
selected={name:sorted((ROOT/'qa').glob(prefix+'*/report.json'))[-1] for name,prefix in [('preflight','preflight-'),('syntax','test-'),('observer','observer-test-'),('lifecycle','lifecycle-'),('mapping','mapping-')]}
for name,path in selected.items():
 packet=json.loads(path.read_text());assert packet['passed'],name
 if name in ('syntax','observer','lifecycle'):assert len(packet['checks'])=={'syntax':22,'observer':28,'lifecycle':92}[name]
 for original,value in packet['inputs'].items():assert sha(original)==value,original
preflight=json.loads(selected['preflight'].read_text());external={}
for name,value in preflight['inputs'].items():
 if not Path(name).is_relative_to(ROOT):external[name]={'sha256':value,'size':Path(name).stat().st_size}
files={str(p.relative_to(ROOT)):{'sha256':sha(p),'size':p.stat().st_size} for p in sorted(ROOT.rglob('*')) if p.is_file() and '__pycache__' not in p.parts and p.name!='component-manifest.json'}
manifest={'sourceHeld':True,'evidenceIntegrityPassed':True,'nativeAcceptance':False,'physicalHardwareAccepted':False,'nonzeroCapabilityAccepted':False,'scope':'Owned225 parent proof current470/471/AQ155 fourprofile candidate; CPU142+11mapping/preflight only','files':files,'externalFiles':external,'selectedReports':{name:{'path':str(path),'sha256':sha(path)} for name,path in selected.items()}}
path=ROOT/'component-manifest.json';assert not path.exists();path.write_text(json.dumps(manifest,indent=2)+'\n')
for name,row in files.items():assert sha(ROOT/name)==row['sha256'],name
for name,row in external.items():assert sha(name)==row['sha256'],name
print(json.dumps({'passed':True,'files':len(files),'externalFiles':len(external),'manifestSHA256':sha(path),'nativeSHA256':sha(ROOT/'qa/native.py')}))
