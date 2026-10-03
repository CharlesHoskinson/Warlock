"""Freeze candidate frontend product code, builder, evidence and accepted V8/V12 closure."""
from pathlib import Path
import hashlib,json,os,stat
B=Path(__file__).resolve().parent;Q=B.parent;files={};links={}
def sha(p):return hashlib.sha256(Path(p).read_bytes()).hexdigest()
def add(p,expected=None):
 p=Path(p)
 if p.is_symlink():links[str(p)]=os.readlink(p);add(p.resolve(),expected)
 actual=sha(p)
 if expected is not None and actual!=expected:raise RuntimeError('Inherited input changed:'+str(p))
 row={'path':str(p),'sha256':actual,'mode':stat.S_IMODE(p.stat().st_mode)}
 if str(p) in files and files[str(p)]!=row:raise RuntimeError('Conflicting input:'+str(p))
 files[str(p)]=row
 if p.resolve()!=p:add(p.resolve(),expected)
def include(p):
 add(p);r=json.loads(Path(p).read_text());rows=r.get('files',r.get('inputs',{}))
 for path,value in rows.items() if isinstance(rows,dict) else [(x['path'],x['sha256']) for x in rows]:add(path,value)
 source=r.get('symlinks',{})
 for path,target in source.items() if isinstance(source,dict) else [(x['path'],x['target']) for x in source]:
  if not Path(path).is_symlink() or os.readlink(path)!=target:raise RuntimeError('Inherited link changed:'+path)
  links[path]=target
include(Q/'family-service-taskbar-v8/frozen-inputs.json')
add(Q/'family-service-taskbar-v8/attempt-1/root-causal-completion.json')
add(Q/'family-service-taskbar-v8/attempt-1/report.json')
for name in ['qa_run.py','qa_launch.py']:add(Q/name)
for folder in ['/usr/lib/python3.14']:
 for p in Path(folder).rglob('*'):
  if p.is_file() and '__pycache__' not in p.parts and 'site-packages' not in p.parts:add(p)
add('/usr/bin/python3')
for p in B.rglob('*'):
 if p.is_file() and '__pycache__' not in p.parts and p.name not in ['frozen-inputs.json','preflight-report.json']:add(p)
p=B/'frozen-inputs.json';assert not p.exists()
r={'scope':'Candidate opt-in native product frontend min/restore via genuine unmodified taskbar CLI callback; no native execution/deployment in this packet','files':[files[x] for x in sorted(files)],'symlinks':[{'path':p,'target':v} for p,v in sorted(links.items())],'byteModeLinkClosure':True,'candidateSourceSHA256':sha(B/'native_frontend.py'),'builderSourceSHA256':sha(B/'prepare_config.py'),'acceptedBackendBaselineSHA256':sha(Q/'family-service-taskbar-v8/frozen-inputs.json'),'nativeCandidateSHA256':'bdd8bab3b3cea6f2dd2e49b317f133691cc920700f9743d21438c0e3338a0dc7','realV12DelegatedOnce':True,'actualServicePeerAndEOFRequired':True,'frontend0MeansOnlyAcceptedReceipt':True,'postSendUnknownNoRetryOrFallback':True,'genuineTaskbarClickProved':False,'nativeExecution':False,'mainWrites':False,'productionDeployment':False,'publicCLIComplete':False,'nativeIntegrationPending':'Fresh heldmatrix V2 own closure/root review and genuine click/held input/release/outcome gates','preflightCommand':['/usr/bin/python3',str(B/'verify.py')]}
p.write_text(json.dumps(r,indent=2)+'\n');p.chmod(0o600);print(json.dumps({'files':len(files),'links':len(links),'manifestSHA256':sha(p),'candidateSourceSHA256':r['candidateSourceSHA256'],'builderSourceSHA256':r['builderSourceSHA256'],'nativeExecution':False}))
