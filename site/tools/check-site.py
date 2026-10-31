#!/usr/bin/env python3
"""Static release checks. Dynamic JavaScript references require explicit declaration."""
import argparse, hashlib, json, re, sys
from html.parser import HTMLParser
from pathlib import Path
from urllib.parse import urlsplit, unquote

SCENARIOS=set('taskbar launcher switcher task-view transfer picker preview-states snap notifications settings files system window-menu confirmation application-actions status-recovery'.split())
FAMILIES=set('taskbar window-group utility recovery popup applications picker menu menu-item preview preview-image preview-caption status native-fallback'.split())
CATALOG=set('overview philosophy foundations tokens states patterns accessibility library references evidence changelog'.split())
class Parser(HTMLParser):
 def __init__(self): super().__init__(convert_charrefs=True); self.refs=[]; self.ids=[]
 def handle_starttag(self,tag,attrs):
  a=dict(attrs)
  if 'id' in a:self.ids.append(a['id'])
  for key in ('href','src','poster','data'):
   if key in a and (key!='data' or tag=='object'): self.refs.append((a[key],tag,key))
  if 'srcset' in a:
   for item in a['srcset'].split(','): self.refs.append((item.strip().split()[0],tag,'srcset'))
 def handle_startendtag(self,tag,attrs): self.handle_starttag(tag,attrs)
class Check:
 def __init__(self,root,base): self.root=Path(root).resolve(); self.base=base; self.errors=[]; self.ids={}; self.refs=[]; self.warnings=[]
 def error(self,p,msg): self.errors.append(f'{p.relative_to(self.root)}: {msg}')
 def ref(self,p,url,tag='',attr=''):
  url=url.strip()
  if not url:return
  u=urlsplit(url)
  if u.scheme or u.netloc:
   if u.scheme in ('data',) and tag in ('img','source'):return
   if u.scheme=='node' and tag=='script' and (p.suffix=='.mjs' or p.name.endswith('.test.js')):return
   if tag=='a' and attr=='href' and u.scheme=='https' and u.hostname=='github.com':return
   self.error(p,'forbidden external reference '+url);return
  if url.startswith('/') or re.match(r'^[A-Za-z]:[\\/]',url): self.error(p,'root-relative or filesystem path '+url);return
  path=unquote(u.path); target=(p.parent/path).resolve() if path else p
  try: target.relative_to(self.root)
  except ValueError: self.error(p,'path escapes root '+url);return
  if target.is_dir(): target=target/'index.html'
  if not target.is_file():
   parent=target.parent
   if parent.is_dir() and any(x.name.lower()==target.name.lower() for x in parent.iterdir()): self.error(p,'case mismatch '+url)
   else:self.error(p,'missing '+url)
   return
  if u.query:
   from urllib.parse import parse_qs
   q=parse_qs(u.query)
   if 'scenario' in q and any(x not in SCENARIOS for x in q['scenario']): self.error(p,'invalid scenario '+url)
  if u.fragment and target.suffix.lower()=='.html': self.refs.append((p,target,unquote(u.fragment),url))
 def run(self):
  declarations={}
  declaration_file=self.root/'metadata/dynamic-assets.json'
  if declaration_file.exists():
   try:
    for item in json.loads(declaration_file.read_text())['references']:
     source=self.root/item['source']; declarations[source]=item
     if not source.is_file() or hashlib.sha256(source.read_bytes()).hexdigest()!=item.get('sourceSha256'): self.error(declaration_file,'dynamic reference source changed or missing: '+item['source'])
     if not item.get('review') or not item.get('assets'): self.error(declaration_file,'dynamic reference requires review and assets: '+item['source'])
     if item['source']=='test-drive/scenarios/index.js' and set(item['assets']) != {f'test-drive/scenarios/{name}.json' for name in SCENARIOS}: self.error(declaration_file,'scenario declaration does not cover the registry')
     for asset in item['assets']:
      target=(self.root/asset).resolve()
      if not target.is_relative_to(self.root) or not target.is_file(): self.error(declaration_file,'invalid dynamic asset: '+asset)
   except (ValueError,KeyError,TypeError) as e: self.error(declaration_file,'invalid dynamic declarations: '+str(e))
  files=[p for p in self.root.rglob('*') if p.is_file() and not any(x in p.parts for x in ('.git','design'))]
  for p in files:
   try:
    if p.suffix.lower()=='.html':
     parser=Parser();parser.feed(p.read_text(encoding='utf-8'));self.ids[p]=set(parser.ids)
     for i in set(parser.ids):
      if parser.ids.count(i)>1:self.error(p,'duplicate id '+i)
     for ref,tag,attr in parser.refs:self.ref(p,ref,tag,attr)
    elif p.suffix.lower()=='.css':
     s=p.read_text(encoding='utf-8');s=re.sub(r'/\*.*?\*/','',s,flags=re.S)
     for m in re.finditer(r'url\(\s*[\'"]?([^\)\'"\s]+)|@import\s+[\'"]([^\'"]+)',s): self.ref(p,m.group(1) or m.group(2),'css','url')
    elif p.suffix.lower() in ('.js','.mjs') and 'reference/catalog/v6/' not in p.as_posix() and 'tools' not in p.relative_to(self.root).parts:
     s=p.read_text(encoding='utf-8')
     for m in re.finditer(r'(?m)\bimport\s+(?:[^\n;]*?\s+from\s*)?[\'"]([^\'"\n]+)[\'"]|\bimport\s*\(\s*[\'"]([^\'"\n]+)[\'"]',s):self.ref(p,m.group(1) or m.group(2),'script','import')
     for m in re.finditer(r'\bfetch\s*\(\s*[\"\']([^\"\']+)[\"\']',s):self.ref(p,m.group(1),'script','fetch')
     if re.search(r'\b(?:fetch|import)\s*\(\s*[^\'\"\s]',s) and p not in declarations:self.warnings.append(f'{p.relative_to(self.root)}: dynamic fetch/import requires declaration and review')
   except (UnicodeDecodeError,ValueError) as e:self.error(p,'parse error '+str(e))
  for p,target,frag,url in self.refs:
   if target.relative_to(self.root).as_posix()=='reference/catalog/v6/index.html':
    parts=frag.split('/'); anchors={'overview':{'start','model','scope'},'component':{'overview','anatomy','behavior','accessibility','content','evidence'}}
    script=self.root/'reference/catalog/v6/catalog.js'
    if script.exists():
     source=script.read_text(); chunks=re.split(r"if\(route==='([^']+)'\)return",source)
     for i in range(1,len(chunks)-1,2): anchors[chunks[i]]=set(re.findall(r"section\('([^']+)'",chunks[i+1]))
    valid=((len(parts)==1 and parts[0] in CATALOG) or (len(parts)==2 and parts[0] in CATALOG and parts[1] in anchors.get(parts[0],set())) or (len(parts) in (2,3) and parts[0]=='component' and parts[1] in FAMILIES and (len(parts)==2 or parts[2] in anchors['component'])))
    if valid:continue
   if frag not in self.ids.get(target,set()):self.error(p,'missing fragment '+url)
  self.model(); self.manifests(); self.components();self.routes()
  for e in self.errors:print('ERROR:',e)
  for w in self.warnings:print('REVIEW:',w)
  print(f'{len(self.errors)} error(s), {len(self.warnings)} dynamic reference review(s)')
  return bool(self.errors)
 def model(self):
  p=self.root/'architecture/architecture.json'; expected=p
  if not p.exists():
   if (self.root/'assets/shared/routes.json').exists():self.error(p,'missing mandatory architecture model')
   return
  if p.exists() and hashlib.sha256(p.read_bytes()).hexdigest()!='3f1460606173e0b65aba11013c28f1ba1a5f59a18cdf6563f40e9bcc46ad9a17':self.error(p,'architecture model differs from verified source')
  if p.exists():
   try:
    d=json.loads(p.read_text()); nodes=d.get('nodes',[]); edges=d.get('edges',[])
    if isinstance(nodes,list) and isinstance(edges,list) and nodes:
     ids={str(x.get('id')) for x in nodes}
     if len(nodes)!=35 or len(edges)!=68 or len(d.get('flows',[]))!=7:self.error(p,'architecture model count mismatch')
     for e in edges:
      if str(e.get('from')) not in ids or str(e.get('to')) not in ids:self.error(p,'architecture edge has unknown endpoint')
   except (ValueError,AttributeError,TypeError) as e:self.error(p,'invalid architecture model '+str(e))
 def manifests(self):
  for p in self.root.rglob('package-manifest.json'):
   if 'design' in p.parts:continue
   try:
    d=json.loads(p.read_text()); entries=d.get('assets',[])
    if not isinstance(entries,list):self.error(p,'assets must be an array');continue
    for a in entries:
     if not isinstance(a,dict):self.error(p,'asset entry must be an object');continue
     required=('source','destination','sha256','bytes','license','classification','alt','caption')
     missing=[k for k in required if k not in a]
     if missing:self.error(p,'manifest asset missing fields '+', '.join(missing))
     dest=a.get('destination') or a.get('path')
     if dest:
      t=(self.root/dest).resolve()
      if not t.is_relative_to(self.root) or not t.is_file():self.error(p,'missing or escaped manifest asset '+str(dest));continue
      if a.get('sha256') and hashlib.sha256(t.read_bytes()).hexdigest()!=a['sha256']:self.error(p,'manifest hash mismatch '+dest)
      if 'bytes' in a and a['bytes']!=t.stat().st_size:self.error(p,'manifest byte count mismatch '+dest)
   except (ValueError,TypeError) as e:self.error(p,'invalid manifest '+str(e))
 def components(self):
  base=self.root/'components'
  if not base.exists():return
  expected=set('taskbar application-groups launcher window-picker window-switcher task-view workspace-transfer previews popup-surfaces window-menu snap-layouts application-actions notifications appearance-settings motion-shortcuts-help files system-menu dialogs status-recovery'.split())
  for name in sorted(expected):
   if not (base/name/'index.html').is_file():self.error(base,'missing component page '+name)
  for p in base.glob('*/index.html'):
   s=p.read_text()
   for section in ('overview','anatomy','states','specimen','behavior','accessibility','content','evidence','try-it'):
    if section not in self.ids.get(p,set()):self.error(p,'missing component section '+section)
   if not re.search(r'test-drive/index\.html\?scenario=('+ '|'.join(SCENARIOS)+r')',s):self.error(p,'missing valid Try it scenario link')
 def routes(self):
  p=self.root/'assets/shared/routes.json'
  if not p.exists():return
  try:
   data=json.loads(p.read_text())
   def visit(x):
    if isinstance(x,dict):
     for k,v in x.items():
      if k in ('path','url','href') and isinstance(v,str) and not v.startswith('#'):self.ref(p,'../../'+v)
      else:visit(v)
    elif isinstance(x,list):
     for v in x:visit(v)
   visit(data)
  except ValueError as e:self.error(p,'invalid route registry '+str(e))
def main():
 ap=argparse.ArgumentParser();ap.add_argument('--root',default='.');ap.add_argument('--base-path',default='/Warlock/');a=ap.parse_args()
 if not a.base_path.startswith('/') or not a.base_path.endswith('/'):ap.error('base path must begin and end with /')
 failed=Check(a.root,a.base_path).run()
 # The full release also requires registry, ownership and scenario contracts.
 import importlib.util
 spec=importlib.util.spec_from_file_location('release_contracts',Path(__file__).with_name('check-contracts.py'))
 module=importlib.util.module_from_spec(spec);spec.loader.exec_module(module)
 errors,_,_,_=module.validate(Path(a.root).resolve())
 for error in errors:print('CONTRACT ERROR:',error)
 return failed or bool(errors)
if __name__=='__main__':sys.exit(main())
