#!/usr/bin/env python3
"""Validate release registries and package provenance, then optionally aggregate it."""
import argparse, hashlib, json, re, sys
from pathlib import Path

BASELINE='bc3daf7b80ac7295a1ba1e56639a0e130e520a3c'
SCENARIOS=set('taskbar launcher switcher task-view transfer picker preview-states snap notifications settings files system window-menu confirmation application-actions status-recovery'.split())
COMPONENTS=set('taskbar application-groups launcher window-picker window-switcher task-view workspace-transfer previews popup-surfaces window-menu snap-layouts application-actions notifications appearance-settings motion-shortcuts-help files system-menu dialogs status-recovery'.split())
T04_COMPONENTS=set('application-actions notifications appearance-settings motion-shortcuts-help files system-menu dialogs status-recovery'.split())
def owner_of(path):
 parts=Path(path).parts
 if not parts:return None
 if parts[0] in ('reference','tools','metadata') or path=='.nojekyll':return 'T10'
 if parts[0] in ('assets','search') or path=='index.html':return 'T01'
 if parts[0] in ('foundations','styles'):return 'T02'
 if parts[0]=='components':return 'T04' if len(parts)>1 and parts[1] in T04_COMPONENTS else 'T03'
 if parts[0]=='get-started':return 'T04'
 if parts[0]=='architecture':return 'T05'
 if parts[0]=='test-drive':
  area=parts[1] if len(parts)>1 else ''
  if area in ('host','runtime') or area in ('contracts.js','contracts.md'):return 'T07'
  if area in ('input','previews'):return 'T08'
  if area in ('services','scenarios','tour'):return 'T09'
  return 'T06'
 return None
OWNERS={f'T{i:02}' for i in range(1,11)}

def canonical_stylesheet_errors(root):
 """Require the reviewed preview stylesheet itself, not a stale runtime copy."""
 errors=[]
 popup=root/'test-drive/runtime/popup.html'
 if popup.exists():
  html=popup.read_text()
  if '../../design/previews-snap/preview.css' not in html:
   errors.append('popup must import canonical design/previews-snap/preview.css')
  if 'theme/preview.css' in html:
   errors.append('popup imports copied preview stylesheet')
 if (root/'test-drive/runtime/theme/preview.css').exists():
  errors.append('unintended copied preview stylesheet: test-drive/runtime/theme/preview.css')
 return errors

def validate(root):
 errors=canonical_stylesheet_errors(root); packages=[]; assets=[]
 def fail(msg): errors.append(str(msg))
 def read(path):
  try:return json.loads(path.read_text())
  except (OSError,ValueError) as e:fail(f'{path.relative_to(root)}: {e}');return None
 manifests=sorted(p for p in root.rglob('package-manifest.json') if 'design' not in p.parts)
 if not manifests:fail('missing package manifests')
 for p in manifests:
  d=read(p)
  if not isinstance(d,dict):fail(f'{p}: manifest must be an object');continue
  packages.append({'manifest':str(p.relative_to(root)),'data':d}); owner=str(d.get('package','')).split()[0].split('-')[0]; entries=d.get('assets')
  if owner not in OWNERS:fail(f'{p}: unknown package ownership {owner}')
  elif owner_of(p.relative_to(root).as_posix())!=owner:fail(f'{p}: manifest outside {owner} ownership')
  if not isinstance(entries,list):fail(f'{p}: assets must be an array');continue
  for a in entries:
   if not isinstance(a,dict):fail(f'{p}: asset must be an object');continue
   assets.append(dict(a,manifest=str(p.relative_to(root))))
   for key in ('source','destination','sha256','bytes','license','classification','alt','caption'):
    if key not in a or (key!='alt' and (a[key] is None or a[key]=='')):fail(f'{p}: asset missing {key}')
   dest=a.get('destination')
   if not isinstance(dest,str):continue
   if owner in OWNERS and owner_of(dest)!=owner:fail(f'{p}: destination outside {owner} ownership: {dest}')
   t=(root/dest).resolve()
   if not t.is_relative_to(root) or not t.is_file():fail(f'{p}: asset missing or escaped: {dest}');continue
   if a.get('sha256')!=hashlib.sha256(t.read_bytes()).hexdigest():fail(f'{p}: hash mismatch {dest}')
   if a.get('bytes')!=t.stat().st_size:fail(f'{p}: byte count mismatch {dest}')
 routes=root/'assets/shared/routes.json';d=read(routes); paths=[]
 if isinstance(d,dict) and isinstance(d.get('routes'),list):
  for route in d['routes']:
   if not isinstance(route,dict) or any(not isinstance(route.get(k),str) or not route[k].strip() for k in ('title','path','section')) or not isinstance(route.get('keywords'),list) or any(not isinstance(x,str) for x in route.get('keywords',[])):
    fail('incomplete route metadata');continue
   path=route['path'];paths.append(path);target=(root/path.split('#')[0].split('?')[0]).resolve()
   if not target.is_relative_to(root) or not target.is_file():fail(f'route missing or escaped: {path}')
  if len(paths)!=len(set(paths)):fail('duplicate route paths')
  for path in ['index.html','test-drive/index.html','architecture/index.html','search/index.html','foundations/index.html','styles/index.html','components/index.html','get-started/index.html']+[f'components/{c}/index.html' for c in COMPONENTS]:
   if path not in paths:fail(f'missing registered route: {path}')
 else:fail('invalid route registry schema')
 scenario_dir=root/'test-drive/scenarios'
 for name in sorted(SCENARIOS):
  p=scenario_dir/(name+'.json'); seed=read(p)
  if not isinstance(seed,dict):continue
  for key in ('id','title','description','component','sourceCommit','initialExternalFacts','entryIntent','expectedObservations'):
   if key not in seed or not seed[key]:fail(f'{p}: missing scenario {key}')
  if seed.get('id')!=name or seed.get('component') not in COMPONENTS or seed.get('sourceCommit')!=BASELINE or not isinstance(seed.get('initialExternalFacts'),dict) or not isinstance(seed.get('expectedObservations'),dict):fail(f'{p}: invalid scenario schema')
  expected=seed.get('expectedObservations')
  if isinstance(expected,dict) and (expected.get('surface') not in ('bar','popup') or not isinstance(expected.get('mode'),str) or not isinstance(expected.get('controls'),list) or not all(isinstance(x,str) for x in expected.get('controls',[])) or expected.get('applied') is not True):fail(f'{p}: invalid expected observations')
  if not isinstance(seed.get('entryIntent'),(str,dict)):fail(f'{p}: invalid entry intent')
 # Binary assets and compiled bundles must be recorded, including stage build outputs.
 covered={a.get('destination') for a in assets}
 for p in root.rglob('*'):
  if not p.is_file() or 'design' in p.parts or '__pycache__' in p.parts:continue
  rel=p.relative_to(root).as_posix()
  if p.suffix.lower() in ('.png','.jpg','.jpeg','.webp','.woff','.woff2','.ttf','.otf','.svg') or rel in ('test-drive/stage/desktop-stage.js',):
   if rel not in covered:fail('missing provenance coverage: '+rel)
 for package in packages:
  build=package['data'].get('build')
  if build is None:continue
  if not isinstance(build,dict):fail(package['manifest']+': invalid build record');continue
  for field in ('source','bundle'):
   name=build.get(field); digest=build.get(field+'_sha256')
   if not isinstance(name,str) or not isinstance(digest,str):fail(package['manifest']+': incomplete build '+field);continue
   target=(root/name).resolve()
   if not target.is_relative_to(root) or not target.is_file() or hashlib.sha256(target.read_bytes()).hexdigest()!=digest:fail(package['manifest']+': build hash mismatch '+name)
  if not build.get('compiler') or not build.get('command'):fail(package['manifest']+': incomplete build instructions')
 for path in ('test-drive/host/index.js','test-drive/stage/index.js','test-drive/input/index.js','test-drive/previews/index.js','test-drive/services/index.js','test-drive/tour/index.js','test-drive/runtime/controller.html','test-drive/runtime/bar.html','test-drive/runtime/popup.html','architecture/architecture.json','.nojekyll'):
  if not (root/path).is_file():fail(f'missing mandatory artifact: {path}')
 dynamic=read(root/'metadata/dynamic-assets.json')
 if isinstance(dynamic,dict) and isinstance(dynamic.get('references'),list):
  for entry in dynamic['references']:
   if not isinstance(entry,dict) or not isinstance(entry.get('source'),str) or not isinstance(entry.get('assets'),list) or not entry['assets']:fail('invalid dynamic asset declaration');continue
   if not (root/entry['source']).is_file():fail('missing dynamic reference source '+entry['source'])
   for name in entry['assets']:
    target=(root/name).resolve()
    if not target.is_relative_to(root) or not target.is_file():fail('missing or escaped dynamic asset '+str(name))
   declared={e.get('source') for e in dynamic['references'] if isinstance(e,dict)}
  for source in root.rglob('*.js'):
   if any(part in source.parts for part in ('design','reference')):continue
   code=source.read_text(errors='replace')
   if re.search(r'\b(?:fetch|import)\s*\(\s*[^\'\"\s]',code) and source.relative_to(root).as_posix() not in declared:fail('undeclared dynamic reference: '+source.relative_to(root).as_posix())
 else:fail('missing dynamic asset declarations')
 model=root/'architecture/architecture.json';record=None
 if model.is_file():
  raw=model.read_bytes(); d=read(model)
  if isinstance(d,dict):
   try:
    ids={x['id'] for x in d['nodes']};record={'sha256':hashlib.sha256(raw).hexdigest(),'bytes':len(raw),'nodes':len(d['nodes']),'edges':len(d['edges']),'flows':len(d['flows'])}
    if record['sha256']!='3f1460606173e0b65aba11013c28f1ba1a5f59a18cdf6563f40e9bcc46ad9a17' or (len(ids),len(d['edges']),len(d['flows']))!=(35,68,7) or any(e['from'] not in ids or e['to'] not in ids for e in d['edges']):fail('architecture model integrity failed')
   except (KeyError,TypeError):fail('architecture model schema invalid')
 return errors,packages,assets,record

def main():
 ap=argparse.ArgumentParser();ap.add_argument('--root',default='.');ap.add_argument('--write',action='store_true');a=ap.parse_args();root=Path(a.root).resolve();errors,packages,assets,record=validate(root)
 if a.write:
  out=root/'metadata';out.mkdir(exist_ok=True)
  (out/'packages.json').write_text(json.dumps({'schema':1,'source_baseline':BASELINE,'architecture':record,'packages':packages},indent=2)+'\n')
  (out/'assets.json').write_text(json.dumps({'schema':1,'assets':assets},indent=2)+'\n')
 for e in errors:print('ERROR:',e)
 print(f'{len(packages)} manifests, {len(assets)} declared assets, {len(errors)} errors')
 return bool(errors)
if __name__=='__main__':sys.exit(main())
