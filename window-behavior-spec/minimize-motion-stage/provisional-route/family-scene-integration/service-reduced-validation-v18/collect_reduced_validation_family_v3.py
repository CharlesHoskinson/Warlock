"""Reviewable V18 source closure; root alone may freeze a reviewed packet."""
from pathlib import Path
import argparse,hashlib,json,os,stat
B=Path(__file__).resolve().parent;BASE=B.with_name('service-recovery-terminal-v17')
MANIFEST=BASE/'manifest-recovery-terminal-v17.json'
BASE_SHA='b7169939fcb0f50281fc50f4e897a3085e68ae4706d3426139fd9d58174d8aa4'
def sha(p):return hashlib.sha256(Path(p).read_bytes()).hexdigest()
def save(p,r):
 fd=os.open(p,os.O_WRONLY|os.O_CREAT|os.O_EXCL|os.O_NOFOLLOW,0o600)
 with os.fdopen(fd,'w')as f:json.dump(r,f,indent=2);f.write('\n')
def collect():
 assert sha(MANIFEST)==BASE_SHA
 inherited=json.loads(MANIFEST.read_text());inputs={};modes={};links={}
 def add(p,digest=None,mode=None):
  p=Path(os.path.abspath(p));name=str(p)
  if p.is_symlink():
   target=os.readlink(p)
   if name in links and links[name]!=target:raise RuntimeError('conflicting source link')
   links[name]=target;return add(p.resolve(),digest,mode)
  actual=sha(p);actualmode=stat.S_IMODE(p.stat().st_mode)
  if digest is not None and actual!=digest:raise RuntimeError('immutable input changed: '+name)
  if mode is not None and actualmode!=mode:raise RuntimeError('immutable mode changed: '+name)
  if name in inputs and inputs[name]!=actual:raise RuntimeError('conflicting source bytes')
  inputs[name]=actual;modes[name]=actualmode
  for parent in p.parents:
   if parent.is_symlink():links[str(parent)]=os.readlink(parent)
 for name,digest in inherited['inputs'].items():add(name,digest,inherited['inputModes'][name])
 for name,target in inherited['links'].items():
  if os.readlink(name)!=target:raise RuntimeError('immutable link changed: '+name)
  links[name]=target
 add(MANIFEST,BASE_SHA);add(BASE/'checkpoint-recovery-terminal-v17.json')
 # Prior successful proof belongs to the retained pre-refinement epoch.
 oldproof=json.loads((B/'offline-checkpoint.json').read_text())
 mapping=json.loads((B/'retained-before-exact-family-refinement/source-map.json').read_text())
 for name,digest in oldproof['sourceSHA256'].items():
  if sha(name)==digest:add(name,digest)
  else:
   witness=mapping.get(name)
   if witness is None or witness['sha256']!=digest:raise RuntimeError('old proof epoch not retained: '+name)
   add(witness['saved'],digest)
 counter=Path('/home/hoskinson/window-integration-qa/reduced-validation-scope-counterexample-v1')
 for p in counter.rglob('*'):
  if '__pycache__'not in p.parts and(p.is_file()or p.is_symlink()):add(p)
 proof=json.loads((B/'offline-family-checkpoint-v2.json').read_text())
 if (proof['pythonTests'],proof['quintNamedScenarios'],proof['quintModels'])!=(329,238,25)or not proof['sourceUnchangedDuringProof']:raise RuntimeError('full current source proof required')
 for name,digest in proof['sourceSHA256'].items():add(name,digest)
 for p in B.rglob('*'):
  if '__pycache__'in p.parts or p.name in ('source-ready-v18-family-v3.json','manifest-reduced-validation-v18-family-v3.json')or any(x.startswith('attempt-')for x in p.parts):continue
  if p.is_file()or p.is_symlink():add(p)
 counter=Path('/home/hoskinson/window-integration-qa/reduced-validation-counterexample-v1')
 for p in counter.rglob('*'):
  if '__pycache__'not in p.parts and(p.is_file()or p.is_symlink()):add(p)
 provenance=json.loads((B/'legacy-fixture-model-reuse-provenance.json').read_text())
 for name,digest in provenance['sourceInputs'].items():add(name,digest)
 add(provenance['rootReview']['path'],provenance['rootReview']['sha256'])
 unchanged=[];changed=[]
 for p in BASE.iterdir():
  if p.is_file()and p.suffix in ('.py','.qnt'):
   current=B/p.name
   if not current.is_file():raise RuntimeError('inherited source omitted: '+p.name)
   (unchanged if current.read_bytes()==p.read_bytes()else changed).append(p.name)
 expected={'scene_controller.py','scene_manager.py','check_offline.py','test_renderer_terminal.py'}
 if set(changed)!=expected:raise RuntimeError('unexpected inherited source delta: '+str(changed))
 row=dict(version='service-reduced-validation-v18',inputs=inputs,inputModes=modes,links=links,baseManifest=str(MANIFEST),baseManifestSHA256=BASE_SHA,changedInheritedSources=changed,inheritedSourcesExact=unchanged,productAdded=['visual_retirement.py'],sourceOnly=True,nativeAccepted=False,nativeLaunch=False,mainChanged=False,productionDeployed=False,explicitUserCancellationIngressImplemented=False,scope='retained original exact member tuple expectations after visual ACK, freshly reobserved before validation; accepted pending validation receipt survives reduction; exact old visual cancel ACK before fresh Scene/token/context rebind; V17 recovery and ordinary native/helper/runtime authorities exact; V20 gate-read synchronization reused in CPU fixture only; unpaired until root actual baseline and genuine reduced-setting campaign')
 verify(row);return row
def verify(row):
 for name,digest in row['inputs'].items():
  if Path(name).is_symlink()or sha(name)!=digest or stat.S_IMODE(Path(name).stat().st_mode)!=row['inputModes'][name]:raise RuntimeError('source closure differs: '+name)
 for name,target in row['links'].items():
  if not Path(name).is_symlink()or os.readlink(name)!=target:raise RuntimeError('source link differs: '+name)
def main():
 p=argparse.ArgumentParser();p.add_argument('--source-ready',action='store_true');p.add_argument('--freeze',action='store_true');p.add_argument('--verify',action='store_true');a=p.parse_args()
 if a.verify:r=json.loads((B/'manifest-reduced-validation-v18-family-v3.json').read_text());verify(r)
 elif a.source_ready or a.freeze:
  r=collect();name='manifest-reduced-validation-v18-family-v3.json'if a.freeze else 'source-ready-v18-family-v3.json';save(B/name,r)
 else:raise ValueError('explicit review operation required')
 print(json.dumps(dict(result='pass',inputs=len(r['inputs']),modes=len(r['inputModes']),links=len(r['links']),nativeLaunch=False)))
if __name__=='__main__':main()
