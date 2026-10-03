"""Reviewable full source closure; explicit freezing is a root review step."""
from pathlib import Path
import argparse,hashlib,json,os,subprocess,sys
B=Path(__file__).resolve().parent;QA=B.parent
FRONT=QA/'native-frontend-adapter-v1/frozen-inputs.json'
FRONT_SHA='cf51f3d5814875428a500d691614e601f82ae4069be9f72c018fe3bd451c6448'
def sha(path):return hashlib.sha256(Path(path).read_bytes()).hexdigest()
def save(path,value):
 with Path(path).open('x') as stream:json.dump(value,stream,indent=2);stream.write('\n')
 Path(path).chmod(0o600)
def verify(row=None):
 if row is None:row=json.loads((B/'frozen-inputs.json').read_text())
 for name,digest in row['inputs'].items():
  if Path(name).is_symlink() or sha(name)!=digest:raise RuntimeError('Frozen input bytes changed: '+name)
  if Path(name).stat().st_mode&0o7777!=row['inputModes'][name]:raise RuntimeError('Frozen input mode changed: '+name)
 for name,target in row['symlinks'].items():
  if not Path(name).is_symlink() or os.readlink(name)!=target:raise RuntimeError('Frozen link changed: '+name)
 return row

def collect():
 inputs={};modes={};links={};packets=[]
 def add(path,digest=None,mode=None):
  path=Path(path);name=str(path)
  if path.is_symlink():
   target=os.readlink(path)
   if name in links and links[name]!=target:raise RuntimeError('Conflicting link closure')
   links[name]=target
   if path.resolve().is_file():add(path.resolve())
   return
  actual=sha(path);actualmode=path.stat().st_mode&0o7777
  if digest is not None and digest!=actual:raise RuntimeError('Retained immutable source changed: '+name)
  if mode is not None and mode!=actualmode:raise RuntimeError('Retained immutable mode changed: '+name)
  if name in inputs and inputs[name]!=actual:raise RuntimeError('Conflicting source closure')
  inputs[name]=actual;modes[name]=actualmode
 def packet(path,expected=None):
  path=Path(path)
  if expected and sha(path)!=expected:raise RuntimeError('Exact reviewed manifest changed')
  raw=json.loads(path.read_text());files=raw.get('inputs',raw.get('files'));oldmodes=raw.get('inputModes',{})
  if files is None:
   files={str(path.parent/name):digest for name,digest in raw['dependencies'].items()};files.update(raw['externalDependencies'])
   oldmodes={str(path.parent/name):mode for name,mode in raw['dependencyModes'].items()};oldmodes.update(raw['externalModes'])
  if isinstance(files,list):
   for row in files:add(row['path'],row['sha256'],row.get('mode',oldmodes.get(row['path'])))
  else:
   for name,digest in files.items():add(name,digest,oldmodes.get(name))
  oldlinks=raw.get('symlinks',raw.get('links',raw.get('externalSymlinks',{})))
  if isinstance(oldlinks,list):oldlinks={row['path']:row['target'] for row in oldlinks}
  for name,target in oldlinks.items():
   if not Path(name).is_symlink() or os.readlink(name)!=target:raise RuntimeError('Retained immutable link changed')
   links[name]=target
   if Path(name).resolve().is_file():add(Path(name).resolve())
  add(path);packets.append(dict(path=str(path),sha256=sha(path)))
 packet(FRONT,FRONT_SHA)
 packet(QA/'toolkit-held-matrix-v2/frozen-inputs.json')
 packet(QA/'toolkit-held-matrix-v3/frozen-inputs.json')
 packet(QA/'toolkit-held-matrix-v4/frozen-inputs.json')
 packet(QA/'toolkit-held-matrix-v5/frozen-inputs.json')
 packet(QA/'toolkit-held-matrix-v6/frozen-inputs.json')
 for retained in sorted((QA/'toolkit-held-matrix-v6/attempt-1').rglob('*')):
  if retained.is_file() or retained.is_symlink():add(retained)
 for retained in sorted((QA/'held-load-causal-review-v1').rglob('*')):
  if '__pycache__' not in retained.parts and (retained.is_file() or retained.is_symlink()):add(retained)
 for retained in sorted((QA/'toolkit-held-matrix-v5/attempt-1').rglob('*')):
  if retained.is_file() or retained.is_symlink():add(retained)
 for retained in sorted((QA/'held-focus-causal-review-v1').rglob('*')):
  if '__pycache__' not in retained.parts and (retained.is_file() or retained.is_symlink()):add(retained)
 for retained in sorted((QA/'toolkit-held-matrix-v4/attempt-1').rglob('*')):
  if retained.is_file() or retained.is_symlink():add(retained)
 for retained in sorted((QA/'toolkit-held-matrix-v3/attempt-1').rglob('*')):
  if retained.is_file() or retained.is_symlink():add(retained)
 for name in ('audit.py','test_audit.py','CONTRACT.md'):
  add(QA/'toolkit-held-terminal-audit-v2'/name)
  add(QA/'toolkit-held-retirement-audit-v1'/name)
 # Retain every current V2 terminal artifact; no historical source/result rewrite.
 for retained in sorted((QA/'toolkit-held-matrix-v2/attempt-1').rglob('*')):
  if retained.is_file() or retained.is_symlink():add(retained)
 for name in ('audit.py','archive_replay.py','test_audit.py','CONTRACT.md'):
  add(QA/'toolkit-held-terminal-audit-v1'/name)
 packet(QA/'family-service-taskbar-v8/frozen-inputs.json','cd3a914a47cc5f57c5a6b95cc245749a9bcdfa673b984fc7319d3a583ec4b57b')
 packet(QA/'toolkit-interruption-v5/frozen-inputs.json','b5a1363da1f0635ce21e05f961324c246bf31cb914993b798b2ff8eb00909e8a')
 packet(QA/'toolkit-interruption-v6/frozen-inputs.json')
 packet(QA/'qt-modal-private-x11-v2/frozen-inputs.json')
 packet(QA/'recovery-audit/keyboard-monitor/production-native-proof-v4/proof-frozen-stage-report.json')
 for name in ('toolkit-v5-root-source-review.json','toolkit-v6-root-source-review.json','family-service-taskbar-v8/attempt-1/root-causal-completion.json','family-service-taskbar-v8/attempt-1/report.json'):
  add(QA/name)
 # Original held source is retained as immutable provenance even though it was
 # never a native-authorized campaign.
 for root in (B,QA/'toolkit-held-matrix-v1'):
  for path in sorted(root.rglob('*')):
   if '__pycache__' in path.parts or any(part.startswith('attempt-') for part in path.parts) or path.name in ('frozen-inputs.json','source-ready.json'):continue
   if path.is_file() or path.is_symlink():add(path)
 build=json.loads((B/'native-probe/build-v2-third-report.json').read_text())
 for row in build['sourceDependencies']:add(row['path'],row['sha256'])
 # GTK introspection import captures actual loader sources/modules/maps without
 # Gtk.init(), display connection, GUI or native plugin execution.
 for name,digest in json.loads((B/'qs-cli-source-proof.json').read_text())['inputs'].items():add(name,digest)
 packet(B/'qt-loader-inputs.json')
 loader=json.loads((B/'gtk-loader-inputs.json').read_text())
 for name,digest in loader['inputs'].items():add(name,digest)
 for name,target in loader['symlinks'].items():
  if os.readlink(name)!=target:raise RuntimeError('Actual GTK loader link changed')
  links[name]=target
  if Path(name).resolve().is_file():add(Path(name).resolve())
 for name in ('/usr/bin/python3','/usr/bin/qs','/usr/bin/hyprctl','/usr/bin/env','/usr/bin/lua'):add(name)
 for row in json.loads((B/'payload-manifest.json').read_text())['externalSymlinks'].items():
  name,target=row
  if os.readlink(name)!=target:raise RuntimeError('Production payload external link changed')
  links[name]=target
  if Path(name).resolve().is_file():add(Path(name).resolve())
 row=dict(inputs=inputs,inputModes=modes,symlinks=links,retainedManifests=packets,scope='Candidate held52 actual public toolkit inputs and genuine frontend, native pending root review',mainChanges=False,nativeLaunch=False,fullWindowsParityAccepted=False)
 verify(row);return row

def main():
 p=argparse.ArgumentParser();p.add_argument('--freeze',action='store_true');p.add_argument('--source-ready',action='store_true');p.add_argument('--verify',action='store_true');a=p.parse_args()
 if a.verify:row=verify()
 else:
  row=collect()
  if a.freeze:save(B/'frozen-inputs.json',row)
  elif a.source_ready:save(B/'source-ready.json',dict(result='source-ready',inputCount=len(row['inputs']),linkCount=len(row['symlinks']),modeCount=len(row['inputModes']),nativeLaunch=False,rootReviewPending=True,fullWindowsParityAccepted=False,closure=row))
  else:raise ValueError('Explicit review operation required')
 print(json.dumps(dict(result='pass',inputs=len(row['inputs']),links=len(row['symlinks']),modes=len(row['inputModes']),nativeLaunch=False)))
if __name__=='__main__':main()
