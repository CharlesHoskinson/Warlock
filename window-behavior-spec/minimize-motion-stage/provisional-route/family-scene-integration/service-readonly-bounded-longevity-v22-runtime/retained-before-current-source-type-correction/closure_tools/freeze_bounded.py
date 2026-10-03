"""Exact V21 + approved V22 design + current packet closure. Inventory unless root freezes."""
from pathlib import Path
import hashlib,importlib.util,json,os,stat
B=Path(__file__).resolve().parent.parent
V21=B.parent/'service-readonly-longevity-v21'
DESIGN=B.parent/'service-readonly-bounded-longevity-v22'
READY21=V21/'source-handoff-v21.json'
READY21_SHA='f36282537be5978b479bc9ace61101e58fd1050a70e8ea15e5af064bed30ec6b'
DESIGN_READY=DESIGN/'design-handoff-v22.json'
DESIGN_READY_SHA='b12cf53276b806e4035e8373c04d0190b430a02e1422a90b37b36f5e92ff5bec'
MANIFEST=B/'manifest-readonly-bounded-v22.json'
CHECKPOINT=B/'checkpoint-readonly-bounded-v22.json'
HANDOFF=B/'source-handoff-v22.json'

def sha(path):return hashlib.sha256(Path(path).read_bytes()).hexdigest()

def inventory():
 if sha(READY21)!=READY21_SHA or sha(DESIGN_READY)!=DESIGN_READY_SHA:raise ValueError('approved ancestry/contract replaced')
 descriptor=V21/'closure_tools/freeze_longevity.py'
 expected=json.loads(READY21.read_text())['localSources'][str(descriptor)]
 if sha(descriptor)!=expected['sha256'] or stat.S_IMODE(descriptor.stat().st_mode)!=expected['mode']:raise ValueError('ancestral closure provider replaced')
 spec=importlib.util.spec_from_file_location('reviewed_v21_freezer',descriptor);module=importlib.util.module_from_spec(spec);spec.loader.exec_module(module)
 old=module.inventory()
 inputs=dict(old['inputs']);modes=dict(old['inputModes']);links=dict(old['links'])
 def add(path,expected=None,mode=None):
  path=Path(path)
  if not path.is_absolute():path=Path('/home/hoskinson')/path
  actual=sha(path);actual_mode=stat.S_IMODE(path.stat().st_mode)
  if expected is not None and expected!=actual:raise ValueError('declared source bytes replaced: '+str(path))
  if mode is not None and mode!=actual_mode:raise ValueError('declared source mode replaced: '+str(path))
  for alias in (path,path.resolve()):
   k=str(alias)
   if k in inputs and (inputs[k]!=actual or modes[k]!=actual_mode):raise ValueError('source alias conflicts')
   inputs[k]=actual;modes[k]=actual_mode
  for alias in (path,*path.parents):
   if alias.is_symlink():links[str(alias)]=os.readlink(alias)
 add(READY21,READY21_SHA);add(DESIGN_READY,DESIGN_READY_SHA)
 for ready in (READY21,DESIGN_READY):
  for n,item in json.loads(ready.read_text())['localSources'].items():add(n,item['sha256'],item['mode'])
 original=json.loads((B/'runtime-authorized-provenance.json').read_text())['inheritedTopSources'];changed=[]
 for name,item in original.items():
  add(V21/name,item['sha256'],item['mode'])
  if stat.S_IMODE((B/name).stat().st_mode)!=item['mode']:raise ValueError('copied original mode differs')
  if sha(B/name)!=item['sha256']:changed.append(name)
 if set(changed)!={'readonly_ipc.py','test_readonly_longevity.py'}:raise ValueError('unreviewed inherited source delta: '+str(changed))
 proof=json.loads((B/'bounded-typed-final-offline-checkpoint.json').read_text())
 if (proof['pythonTests'],proof['quintNamedScenarios'],proof['quintModels'])!=(386,378,33) or not proof['sourceUnchangedDuringProof']:raise ValueError('complete exact current gate required')
 for n,h in proof['sourceSHA256'].items():add(n,h)
 for path in sorted(B.rglob('*')):
  # Skip only our own root output descriptors; retain all nested ancestral names.
  if path.is_file() and '__pycache__' not in path.parts and path not in (MANIFEST,CHECKPOINT):add(path)
 for n,h in inputs.items():
  if sha(n)!=h or stat.S_IMODE(Path(n).stat().st_mode)!=modes[n]:raise ValueError('source closure changed during inventory')
 for n,target in links.items():
  if not Path(n).is_symlink() or os.readlink(n)!=target:raise ValueError('declared link replaced')
 result={k:v for k,v in old.items() if k not in ('inputs','inputModes','links','version','changedExistingSources')}
 result.update(version='service-readonly-bounded-v22',v21SourceHandoff=str(READY21),v21SourceHandoffSHA256=READY21_SHA,
  approvedDesign=str(DESIGN_READY),approvedDesignSHA256=DESIGN_READY_SHA,allV21AndDesignClosurePreserved=True,
  changedExistingSources=changed,nativeLaunch=False,nativeAccepted=False,mainChanged=False,productionDeployed=False,
  currentDataNeverHistoricalNativeSettlementAuthority=True,fullHistoryStartupAuditNormalClose=True,
  inputs=dict(sorted(inputs.items())),inputModes=dict(sorted(modes.items())),links=dict(sorted(links.items())))
 return result

def exclusive(path,value):
 fd=os.open(path,os.O_WRONLY|os.O_CREAT|os.O_EXCL|os.O_NOFOLLOW|os.O_CLOEXEC,0o600)
 try:
  with os.fdopen(fd,'wb') as stream:
   fd=None;stream.write((json.dumps(value,indent=2)+'\n').encode());stream.flush();os.fsync(stream.fileno())
  directory=os.open(path.parent,os.O_RDONLY|os.O_DIRECTORY|os.O_NOFOLLOW|os.O_CLOEXEC)
  try:os.fsync(directory)
  finally:os.close(directory)
 finally:
  if fd is not None:os.close(fd)

def main():
 import argparse
 parser=argparse.ArgumentParser();parser.add_argument('--freeze',action='store_true');options=parser.parse_args()
 if MANIFEST.exists() or CHECKPOINT.exists():raise SystemExit('immutable descriptors already exist')
 packet=inventory()
 for n,item in json.loads(HANDOFF.read_text())['localSources'].items():
  if packet['inputs'].get(n)!=item['sha256'] or packet['inputModes'].get(n)!=item['mode']:raise ValueError('incomplete handoff closure: '+n)
 if options.freeze:
  exclusive(MANIFEST,packet);exclusive(CHECKPOINT,{'manifest':str(MANIFEST),'manifestSHA256':sha(MANIFEST),'sourceHandoffSHA256':sha(HANDOFF),'inputs':len(packet['inputs']),'modes':len(packet['inputModes']),'links':len(packet['links']),'offlineSHA256':sha(B/'bounded-typed-final-offline-checkpoint.json'),'nativeAccepted':False,'currentStageFrozen':True})
 print(json.dumps({'freeze':options.freeze,'inputs':len(packet['inputs']),'modes':len(packet['inputModes']),'links':len(packet['links']),'manifestSHA256':sha(MANIFEST) if options.freeze else None,'sourceHandoffSHA256':sha(HANDOFF),'nativeLaunch':False}))
if __name__=='__main__':main()
