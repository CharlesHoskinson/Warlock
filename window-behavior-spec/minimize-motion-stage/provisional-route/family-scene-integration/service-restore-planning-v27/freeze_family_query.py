"""Fresh V19 freeze after source review; source-only and no native launch."""
from pathlib import Path
import difflib,hashlib,json,os,stat,subprocess
B=Path(__file__).resolve().parent
V17=B.parent/'service-recovery-terminal-v17'
QA=Path('/home/hoskinson/window-integration-qa')
BASE_SHA='b7169939fcb0f50281fc50f4e897a3085e68ae4706d3426139fd9d58174d8aa4'
def sha(path):return hashlib.sha256(Path(path).read_bytes()).hexdigest()
def main():
 target=B/'manifest-family-query-v19.json';checkpoint=B/'checkpoint-family-query-v19.json'
 if target.exists() or checkpoint.exists():raise SystemExit('fresh immutable freeze required')
 base=V17/'manifest-recovery-terminal-v17.json'
 if sha(base)!=BASE_SHA:raise SystemExit('frozen V17 manifest changed')
 old=json.loads(base.read_text());inputs={};modes={};links={}
 def add(path,expected=None,mode=None):
  p=Path(path);p=p if p.is_absolute() else Path('/home/hoskinson')/p
  actual=sha(p);actualmode=stat.S_IMODE(p.stat().st_mode)
  if expected is not None and actual!=expected:raise ValueError('retained bytes changed: '+str(p))
  if mode is not None and actualmode!=mode:raise ValueError('retained mode changed: '+str(p))
  for alias in (p,p.resolve()):inputs[str(alias)]=actual;modes[str(alias)]=actualmode
  for alias in (p,*p.parents):
   if alias.is_symlink():links[str(alias)]=os.readlink(alias)
 for path,digest in old['inputs'].items():add(path,digest,old['inputModes'][path])
 for path,value in old['links'].items():
  if not Path(path).is_symlink() or os.readlink(path)!=value:raise ValueError('retained V17 link changed')
  links[path]=value
 add(base,BASE_SHA);add(V17/'checkpoint-recovery-terminal-v17.json')
 # Failed native route and exact bounded CPU counterexample remain immutable inputs.
 for path in (QA/'recovery-baseline-v2-lock-counterexample-v1').rglob('*'):
  if path.is_file() and '__pycache__' not in path.parts:add(path)
 for path in (QA/'family-recovery-cancel-v2/attempt-baseline-1').rglob('*'):
  if path.is_file():add(path)
 add(QA/'family-recovery-cancel-v2/frozen-inputs.json')
 report=json.loads((B/'offline-checkpoint.json').read_text())
 if (report['pythonTests'],report['quintNamedScenarios'],report['quintModels'])!=(304,191,23) or not report['sourceUnchangedDuringProof']:raise ValueError('full V19 offline gate required')
 for path,digest in report['sourceSHA256'].items():add(path,digest)
 for p in (Path('/usr/bin/cat'),):
  add(p);r=subprocess.run(['/usr/bin/ldd',str(p)],capture_output=True,text=True,timeout=5)
  if r.returncode:raise ValueError('CPU helper closure unavailable')
  for line in r.stdout.splitlines():
   for word in line.split():
    if word.startswith('/') and Path(word).is_file():add(word)
 changed=[p.name for p in B.glob('*.py') if (V17/p.name).exists() and p.read_bytes()!=(V17/p.name).read_bytes()]
 if set(changed)!={'native_desktop.py','check_offline.py','test_pipe_transport.py','test_actor_resources.py'}:raise ValueError('narrow inherited source diff changed')
 for p in B.rglob('*'):
  if p.is_file() and '__pycache__' not in p.parts:add(p)
 for p,h in inputs.items():
  if sha(p)!=h or stat.S_IMODE(Path(p).stat().st_mode)!=modes[p]:raise ValueError('closure changed before freeze')
 packet={k:old[k] for k in ('pairedManifest','pairedManifestSHA256','pairedNativeSHA256','producerManifest','producerManifestSHA256','producer','producerSHA256')}
 packet.update(scope='fresh read-only family-query mutex correction; original native baseline/restart proof required',nativeLaunch=False,nativeAccepted=False,mainChanged=False,productionDeployed=False,
  baseManifest=str(base),baseManifestSHA256=BASE_SHA,allFrozenV17InputsPreserved=True,changedExistingSources=changed,
  originalDeadlineUnchanged=True,atomicNativeAndReceiptGuardsUnchanged=True,threadLocalFamilyEvidencePreserved=True,
  actualNativeLockOwnershipNotArchived=True,currentUserCancellationIngressImplemented=False,reductionV18Paired=False,
  inputs=dict(sorted(inputs.items())),inputModes=dict(sorted(modes.items())),links=dict(sorted(links.items())))
 target.write_text(json.dumps(packet,indent=2)+'\n')
 checkpoint.write_text(json.dumps({'manifest':str(target),'manifestSHA256':sha(target),'inputCount':len(inputs),'modeCount':len(modes),'linkCount':len(links),'offlineSHA256':sha(B/'offline-checkpoint.json'),'nativeAccepted':False,'currentStageFrozen':True},indent=2)+'\n')
 print(json.dumps({'manifestSHA256':sha(target),'checkpointSHA256':sha(checkpoint),'inputs':len(inputs),'modes':len(modes),'links':len(links),'nativeLaunch':False}))
if __name__=='__main__':main()
