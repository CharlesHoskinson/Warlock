"""Fresh source-only union; never freezes or launches the native campaign."""
from pathlib import Path
import hashlib,json,os,stat,sys
from closure_union import union
B=Path(__file__).resolve().parent.parent
QA=Path('/home/hoskinson/window-integration-qa')
C=Path('/home/hoskinson/window-behavior-spec/pin-maximized-core-v3-hit-fallback')
def metadata(p):return dict(sha256=hashlib.sha256(p.read_bytes()).hexdigest(),mode=stat.S_IMODE(p.stat().st_mode))
def normalize_ready(stage,closure):
 row=dict(inputs={str(stage/rel):m['sha256']for rel,m in closure['files'].items()},inputModes={str(stage/rel):m['mode']for rel,m in closure['files'].items()},symlinks={str(stage/rel):m['target']for rel,m in closure['links'].items()},directoryModes={str(stage/rel):mode for rel,mode in closure['directories'].items()})
 for name in ['SOURCE_READY.json','SOURCE_READY_INPUTS.json']:
  p=stage/name;m=metadata(p);row['inputs'][str(p)]=m['sha256'];row['inputModes'][str(p)]=m['mode']
 return row

def normalize_manifest(raw):
 links=raw.get('symlinks',{})
 if type(links)is list:links={r['path']:r['target']for r in links}
 values=raw.get('inputs',raw.get('files'))
 if type(values)is list:declared=[(r['path'],r['sha256'],r['mode'])for r in values]
 else:declared=[(p,sha,raw['inputModes'][p])for p,sha in values.items()]
 inputs={};modes={};aliases=[]
 for name,sha,mode in declared:
  p=Path(name)
  if type(mode)is not int or metadata(p)!={'sha256':sha,'mode':mode}:raise RuntimeError('Ancestral declared byte/mode changed: '+name)
  target=str(p.resolve()) if p.is_symlink()else name
  if p.is_symlink():
   if links.get(name)!=os.readlink(p):raise RuntimeError('Ancestral alias literal target changed')
   aliases.append(dict(path=name,canonical=target,sha256=sha,mode=mode,literalTarget=links[name]))
  if target in inputs and (inputs[target]!=sha or modes[target]!=mode):raise RuntimeError('Conflicting normalized ancestral input')
  inputs[target]=sha;modes[target]=mode
 return dict(inputs=inputs,inputModes=modes,symlinks=links,directoryModes=raw.get('directoryModes',{})),aliases

def inventory():
 paths=[QA/'browser-files-flow-v20/frozen-inputs.json',QA/'family-continuous-c1-v4/frozen-inputs.json',QA/'toolkit-held-matrix-v14/frozen-inputs.json',QA/'private-weston-aq-bootstrap-host-v5/frozen-inputs.json',QA/'aquamarine-nested-bootstrap-v2/frozen-inputs.json',QA/'pin-native-qa-v2/frozen-inputs.json']
 rows=[];extra=[];records=[]
 for path in paths:
  raw=path.read_bytes();r=json.loads(raw)
  normalized,aliases=normalize_manifest(r)
  rows.append(normalized);extra.append(path);records.append(dict(path=str(path),declaredAliases=aliases,**metadata(path)))
 component=json.loads((B/'a3-component.json').read_text())
 rows.append(dict(inputs={p:m['sha256']for p,m in component['sources'].items()},inputModes={p:m['mode']for p,m in component['sources'].items()},symlinks={}))
 closure=json.loads((C/'SOURCE_READY_INPUTS.json').read_text());rows.append(normalize_ready(C,closure))
 for ancestor in closure['ancestors']:rows.append(normalize_ready(Path(ancestor['stage']),ancestor))
 # Retain exact actual failures/reviews and the original helper, fixtures and QA dependencies.
 for path in [QA/'pin-focus-observation-v3-component-handoff-v1.json',QA/'pin-native-qa-v2/attempt-1/root-failure-audit-v1.json',QA/'pin-max-core-final-root-source-review-v1.json',QA/'pin-max-hit-fallback-root-review-v1.json',QA/'pin-helper-v1-root-source-handoff-v1.json',QA/'producer-c1-v13-root-source-review.json',QA/'browser-files-flow-v20/attempt-1/root-completion.json',QA/'browser-files-flow-v20/attempt-1/root-physical-keyboard-causal-replay-v1.json',QA/'crash-handoff-v5/review.json']:extra.append(path)
 # Full live V25 source and declared build/physical dependency records remain immutable.
 product=Path('/home/hoskinson/window-behavior-spec/pin-lifetime-v3')
 for p in sorted(product.rglob('*')):
  if any(part in {'.git','__pycache__'}or part.startswith('attempt-')for part in p.parts):continue
  if p.is_file()or p.is_symlink():extra.append(p)
 result=union(B,rows,extra)
 # All selected probe compiler inputs and actual linked libraries are explicit bytes/modes.
 probe=json.loads((B/'readonly-probe/build-report.json').read_text())
 deps=dict(inputs={p:m['sha256']for p,m in probe['dependencies'].items()},inputModes={p:m['mode']for p,m in probe['dependencies'].items()},symlinks={})
 result=union(B,[result,deps],extra)
 result['retainedManifests']=records;result['nativeLaunch']=False;return result
if __name__=='__main__':
 row=inventory();p=B/'source-ready-inputs.json'
 with p.open('x')as f:json.dump(row,f,indent=2);f.write('\n');f.flush();os.fsync(f.fileno())
 p.chmod(0o600);print(json.dumps(dict(inputs=len(row['inputs']),links=len(row['symlinks']),directories=len(row['directoryModes']),nativeLaunch=False)))
