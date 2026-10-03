"""Source closure staging only. This script never freezes or launches native QA."""
from pathlib import Path
import hashlib,json,os,stat,subprocess,time
B=Path(__file__).resolve().parent;QA=B.parent;P=Path('/home/hoskinson/window-behavior-spec/pin-lifetime-v3')
def digest(p):return hashlib.sha256(Path(p).read_bytes()).hexdigest()
def build():
 inputs={};modes={};links={};records=[]
 def link(p):
  if p.is_symlink():
   target=os.readlink(p)
   if str(p)in links and links[str(p)]!=target:raise ValueError('Conflicting source link')
   links[str(p)]=target
 def add(p,expected=None,mode=None):
  p=Path(p).absolute()
  for part in [p,*p.parents]:link(part)
  if p.is_symlink():add(p.resolve(),expected,mode);return
  info=p.lstat()
  if not stat.S_ISREG(info.st_mode):raise ValueError('Regular exact source required: '+str(p))
  actual=digest(p);actualmode=stat.S_IMODE(info.st_mode)
  if expected is not None and actual!=expected or mode is not None and actualmode!=mode:raise ValueError('Retained byte/mode authority differs: '+str(p))
  if str(p)in inputs and inputs[str(p)]!=actual:raise ValueError('Conflicting inherited source')
  inputs[str(p)]=actual;modes[str(p)]=actualmode
 def packet(path):
  path=Path(path);raw=path.read_bytes();row=json.loads(raw);files=row.get('inputs',row.get('files'));oldmodes=row.get('inputModes',{})
  if isinstance(files,list):
   for r in files:add(r['path'],r['sha256'],r.get('mode'))
  else:
   for name,value in files.items():add(name,value,oldmodes.get(name))
  symlinks=row.get('symlinks',row.get('links',{}))
  if isinstance(symlinks,list):symlinks={r['path']:r['target']for r in symlinks}
  for name,target in symlinks.items():
   if not Path(name).is_symlink()or os.readlink(name)!=target:raise ValueError('Retained exact dependency link differs: '+name)
   links[name]=target
  add(path);records.append(dict(path=str(path),sha256=digest(path)))
  if path.read_bytes()!=raw:raise ValueError('Retained manifest changed during observation')
 for path in [QA/'browser-files-flow-v20/frozen-inputs.json',QA/'family-continuous-c1-v4/frozen-inputs.json',QA/'toolkit-held-matrix-v14/frozen-inputs.json',QA/'private-weston-aq-bootstrap-host-v5/frozen-inputs.json',QA/'aquamarine-nested-bootstrap-v2/frozen-inputs.json']:
  packet(path)
 # Immutable actual prior outcomes and root reviews are separate evidence inputs.
 for path in [QA/'pin-helper-v1-root-source-handoff-v1.json',QA/'producer-c1-v13-root-source-review.json',QA/'browser-files-flow-v20/attempt-1/root-completion.json',QA/'browser-files-flow-v20/attempt-1/root-physical-keyboard-causal-replay-v1.json',QA/'crash-handoff-v5/review.json']:
  add(path)
 for root in (P,B):
  for p in sorted(root.rglob('*')):
   if '__pycache__'in p.parts or any(s.startswith('attempt-')for s in p.parts)or p.name in ('source-ready.json','source-ready-inputs.json','frozen-inputs.json')or p.suffix=='.o':continue
   if p.is_symlink():link(p)
   elif p.is_file():add(p)
 # Actual per-TU installed ABI compiler dependency closure.
 for dependency in (P/'native-candidate').glob('*.d'):
  for word in dependency.read_text().replace('\\\n',' ').split(':',1)[1].split():
   name=Path(word);name=name if name.is_absolute()else P/'native-candidate'/name
   if name.is_file():add(name)
 physical=json.loads((P/'keyboard-chords/physical-build-report.json').read_text())
 for item in physical['dependencies']:add(item['path'],item['sha256'],item['mode'])
 for item in physical['symlinks']:
  name,target=item['path'],item['target']
  if os.readlink(name)!=target:raise ValueError('Physical driver map/loader link differs')
  links[name]=target
 # Pin helper -I/-S entire stdlib and loader sources are already in the original
 # Browser closure. Explicit selected executable/header/library checks below.
 for p in ('/usr/bin/python3','/usr/bin/python3.14','/usr/bin/quickshell','/usr/bin/hyprctl','/usr/bin/lua','/usr/bin/grim'):add(p)
 binary=P/'native-candidate/hyprbars-v25-pin-stacking-candidate.so'
 report=json.loads((P/'pin-v25-module-build-report.json').read_text())
 if report['returncode']!=0 or report['sourceUnchangedDuringBuild']is not True or report['binarySHA256']!=digest(binary):raise ValueError('Final full native source-stable binary required')
 for name,value in report['sourceSHA256'].items():
  if digest(name)!=value:raise ValueError('Native source changed since full module build')
 offline=json.loads((P/'offline-final-report.json').read_text())
 if offline['result']!='pass'or offline['sourceUnchanged']is not True:raise ValueError('Final meaningful CPU/model suite required')
 for name,value in offline['sourceSHA256'].items():
  if digest(name)!=value:raise ValueError('Source changed since final CPU/formal proof: '+name)
 row=dict(inputs=inputs,inputModes=modes,symlinks=links,retainedManifests=records,
          candidate=dict(path=str(binary),sha256=digest(binary),moduleSourceReviewPending=True),
          scope='Unfrozen source-only native Pin campaign A; taskbar/frontend/minimize/max and merged regressions remain pending',
          nativeLaunch=False,mainChanges=False,fullWindowsParityAccepted=False)
 destination=B/'source-ready-inputs.json'
 if destination.exists():raise ValueError('Fresh source-ready packet required; preserve prior capture')
 destination.write_text(json.dumps(row,indent=2)+'\n');destination.chmod(0o600)
 result=dict(result='source-ready',inputs=len(inputs),modes=len(modes),links=len(links),packet=str(destination),packetSHA256=digest(destination),candidate=row['candidate'],nativeLaunch=False,rootReviewPending=True,frozen=False,fullWindowsParityAccepted=False)
 (B/'source-ready.json').write_text(json.dumps(result,indent=2)+'\n');print(json.dumps(result));return result
if __name__=='__main__':build()
