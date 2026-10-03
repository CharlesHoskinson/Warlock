"""Reviewed source-only V20 closure; never starts native clients or compositor."""
import hashlib,json,os,stat,subprocess
from pathlib import Path
B=Path(__file__).resolve().parent
QA=Path('/home/hoskinson/window-integration-qa')
V19=B.parent/'service-family-query-v19'
BASE=V19/'manifest-family-query-v19.json'
BASE_SHA='57ef24c0b73d80aa6b2de78366d7a40f21fefc4ca464928f5f6ef27524981b0e'
COLLECTOR=QA/'family-recovery-cancel-v3/frozen-inputs.json'
COLLECTOR_SHA='e41e787f2d8c64997f7df7e285f324af82d8ce465ccb131ad0d3a566ac348be7'
MANIFEST=B/'manifest-readonly-ipc-v20.json'
CHECKPOINT=B/'checkpoint-readonly-ipc-v20.json'
HANDOFF=B/'source-handoff-v20.json'
ALLOWED={'owned_commands.py','native_runtime.py','service_runtime.py','recovery_runtime.py','check_offline.py','test_socket_frontend.py','test_renderer_terminal.py'}
def sha(p):return hashlib.sha256(Path(p).read_bytes()).hexdigest()
def inventory():
 inputs={};modes={};links={}
 def add(p,expected=None,mode=None):
  p=Path(p);p=p if p.is_absolute() else Path('/home/hoskinson')/p
  actual=sha(p);m=stat.S_IMODE(p.stat().st_mode)
  if expected is not None and actual!=expected:raise ValueError('declared bytes changed: '+str(p))
  if mode is not None and m!=mode:raise ValueError('declared mode changed: '+str(p))
  for alias in (p,p.resolve()):
   name=str(alias)
   if name in inputs and (inputs[name]!=actual or modes[name]!=m):raise ValueError('conflicting retained alias')
   inputs[name]=actual;modes[name]=m
  for alias in (p,*p.parents):
   if alias.is_symlink():links[str(alias)]=os.readlink(alias)
 def retain(path,expected,key):
  if sha(path)!=expected:raise ValueError('frozen descriptor replaced: '+str(path))
  old=json.loads(path.read_text())
  if set(old['inputs'])!=set(old['inputModes']):raise ValueError('declared modes incomplete')
  for p,h in old['inputs'].items():add(p,h,old['inputModes'][p])
  for p,target in old[key].items():
   if not Path(p).is_symlink() or os.readlink(p)!=target:raise ValueError('declared link changed: '+p)
   links[p]=target
  add(path,expected)
  return old
 old=retain(BASE,BASE_SHA,'links')
 retained_collector=retain(COLLECTOR,COLLECTOR_SHA,'symlinks')
 add(V19/'checkpoint-family-query-v19.json')
 lock=json.loads((B/'evidence-lock-v20.json').read_text())
 for p,item in lock['files'].items():add(p,item['sha256'],item['mode'])
 add(B/'evidence-lock-v20.json')
 report=json.loads((B/'offline-checkpoint.json').read_text())
 if (report['pythonTests'],report['quintNamedScenarios'],report['quintModels'])!=(328,244,27) or not report['sourceUnchangedDuringProof']:raise ValueError('full final offline gate required')
 for p,h in report['sourceSHA256'].items():add(p,h)
 changed=[]
 inherited=json.loads((B/'runtime-inherited-v19.json').read_text())
 for name,item in inherited['sources'].items():
  add(V19/name,item['sha256'],item['mode'])
  p=B/name
  if stat.S_IMODE(p.stat().st_mode)!=item['mode']:raise ValueError('copied runtime mode changed')
  if sha(p)!=item['sha256']:changed.append(name)
 if set(changed)!=ALLOWED:raise ValueError('inherited source diff exceeds reviewed wiring: '+str(changed))
 for p in B.rglob('*'):
  # Only this packet's own output descriptors are excluded. Retained nested
  # frozen-inputs.json and every ancestral descriptor remain included.
  if p.is_file() and '__pycache__' not in p.parts and p not in (MANIFEST,CHECKPOINT):add(p)
 for p in (Path('/usr/bin/hyprctl'),):
  add(p);r=subprocess.run(['/usr/bin/ldd',str(p)],capture_output=True,text=True,timeout=5)
  if r.returncode:raise ValueError('selected IPC executable dependency closure failed')
  for line in r.stdout.splitlines():
   for word in line.split():
    if word.startswith('/') and Path(word).is_file():add(word)
 for p,h in inputs.items():
  if sha(p)!=h or stat.S_IMODE(Path(p).stat().st_mode)!=modes[p]:raise ValueError('closure moved during inventory')
 result={k:old[k] for k in ('pairedManifest','pairedManifestSHA256','pairedNativeSHA256','producerManifest','producerManifestSHA256','producer','producerSHA256')}
 result.update(scope='owned fixed read-only data IPC; original38 native baseline and recovery faults unaccepted',baseManifest=str(BASE),baseManifestSHA256=BASE_SHA,retainedFailedCollector=str(COLLECTOR),retainedFailedCollectorSHA256=COLLECTOR_SHA,allFrozenV19InputsPreserved=True,allFailedV3CollectorInputsPreserved=True,changedExistingSources=sorted(changed),nativeLaunch=False,nativeAccepted=False,mainChanged=False,productionDeployed=False,originalDeadlineUnchanged=True,atomicNativeAndReceiptGuardsUnchanged=True,currentUserCancellationIngressImplemented=False,reductionV18Paired=False,inputs=dict(sorted(inputs.items())),inputModes=dict(sorted(modes.items())),links=dict(sorted(links.items())))
 return result

def main():
 import argparse
 a=argparse.ArgumentParser();a.add_argument('--freeze',action='store_true');args=a.parse_args()
 if MANIFEST.exists() or CHECKPOINT.exists():raise SystemExit('immutable output already exists')
 packet=inventory()
 handoff=json.loads(HANDOFF.read_text())
 for p,item in handoff['localSources'].items():
  if packet['inputs'].get(p)!=item['sha256'] or packet['inputModes'].get(p)!=item['mode']:raise ValueError('handoff not covered by planned freeze: '+p)
 if args.freeze:
  MANIFEST.write_text(json.dumps(packet,indent=2)+'\n')
  CHECKPOINT.write_text(json.dumps({'manifest':str(MANIFEST),'manifestSHA256':sha(MANIFEST),'inputCount':len(packet['inputs']),'modeCount':len(packet['inputModes']),'linkCount':len(packet['links']),'offlineSHA256':sha(B/'offline-checkpoint.json'),'sourceHandoffSHA256':sha(HANDOFF),'nativeAccepted':False,'currentStageFrozen':True},indent=2)+'\n')
 print(json.dumps({'freeze':args.freeze,'inputs':len(packet['inputs']),'modes':len(packet['inputModes']),'links':len(packet['links']),'handoffLocalSources':len(handoff['localSources']),'sourceHandoffSHA256':sha(HANDOFF),'manifestSHA256':sha(MANIFEST) if args.freeze else None,'nativeLaunch':False}))
if __name__=='__main__':main()
