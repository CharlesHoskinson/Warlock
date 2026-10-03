"""Preserve downloaded evidence and build a portable, hashed local Elm corpus."""
import ast, hashlib, json, shutil
from pathlib import Path
HERE=Path(__file__).resolve().parent
DEST=HERE/'corpus'
SOURCES={
 'official':Path('/home/hoskinson/.cache/windows-parity-research/elm-pivot/official'),
 'architecture':Path('/home/hoskinson/.cache/windows-parity-research/elm-pivot/architecture'),
 'implementation':Path('/home/hoskinson/.cache/elm-pivot/implementation'),
 'frp':Path('/home/hoskinson/.cache/elm-pivot/frp'),
 'compiler-stable':Path('/home/hoskinson/.cache/elm-pivot/compiler-stable'),
 'elm-ui':Path('/home/hoskinson/.cache/elm-pivot/elm-ui'),
}
def digest(path):return hashlib.sha256(path.read_bytes()).hexdigest()
# Use the collector's declaration function without executing network acquisition.
module=ast.parse((HERE/'collect_official.py').read_text())
function=next(node for node in module.body if isinstance(node,ast.FunctionDef) and node.name=='declaration')
scope={};exec(compile(ast.Module(body=[function],type_ignores=[]),'declaration','exec'),scope)
for category,source in SOURCES.items():
 if source.exists():shutil.copytree(source,DEST/category,dirs_exist_ok=True)
manifest=json.loads((DEST/'official/manifest.json').read_text())
for row in manifest['entries']:
 raw=DEST/'official'/Path(row['raw']).relative_to(SOURCES['official'])
 assert digest(raw)==row['sha256'],raw
 if row['kind']=='package-api':
  lines=['# '+str(raw.relative_to(DEST)),'Source: '+row['url'],'']
  for module in json.loads(raw.read_text()):
   lines+=['# '+module['name'],'',module.get('comment',''),'']
   for group in ('aliases','unions','values','binops'):
    for item in module.get(group,[]):
     lines+=['## '+item['name'],'','```elm',scope['declaration'](group,item),'```','',item.get('comment',''),'']
  generated=raw.with_suffix('.md');generated.write_text('\n'.join(lines))
  row['markdown']=str(generated.relative_to(DEST));row['markdownSHA256']=digest(generated)
 elif row.get('markdown'):
  generated=DEST/'official'/Path(row['markdown']).relative_to(SOURCES['official'])
  assert digest(generated)==row['markdownSHA256'],generated
  row['markdown']=str(generated.relative_to(DEST))
 row['raw']=str(raw.relative_to(DEST))
(DEST/'official/portable-manifest.json').write_text(json.dumps(manifest,indent=2)+'\n')
# Agent source manifests are retained verbatim; independently check their evidence hashes.
checks=272
for row in json.loads((DEST/'frp/manifest.json').read_text())['sources']:
 for field,hashfield in [('artifact','sha256'),('extracted','extracted_sha256')]:
  assert digest(DEST/'frp'/Path(row[field]).name)==row[hashfield],row['name']
 checks+=1
for row in json.loads((DEST/'implementation/sources.json').read_text()):
 assert digest(DEST/'implementation'/(row['name']+'.txt'))==row['sha256'],row['name']
 checks+=1
for row in json.loads((DEST/'architecture/manifest.json').read_text()):
 for suffix,hashfield in [('.html','html_sha256'),('.raw','html_sha256'),('.txt','text_sha256')]:
  path=DEST/'architecture'/(row['name']+suffix)
  if path.exists() and row.get(hashfield):assert digest(path)==row[hashfield],path
 checks+=1
if (DEST/'compiler-stable/sources.json').exists():
 for row in json.loads((DEST/'compiler-stable/sources.json').read_text())['records']:
  for field,hashfield in [('raw_path','sha256'),('extracted_path','extracted_sha256')]:
   assert digest(DEST/'compiler-stable'/row[field])==row[hashfield],row['requested_url']
  checks+=1
if (DEST/'elm-ui/manifest.json').exists():
 for row in json.loads((DEST/'elm-ui/manifest.json').read_text())['sources']:
  assert digest(DEST/'elm-ui'/row['path'])==row['sha256'],row['url']
  checks+=1
files=[{'path':str(p.relative_to(HERE)),'bytes':p.stat().st_size,'sha256':digest(p)} for p in sorted(DEST.rglob('*')) if p.is_file()]
(HERE/'CORPUS_MANIFEST.json').write_text(json.dumps({'format':1,'acquisition':'Scrapling; primary official documentation and curated literature','sourceRecordsHashVerified':checks,'files':files},indent=2)+'\n')
packages=json.loads((DEST/'official/official-package-versions.json').read_text())
index=['# Local documentation corpus','', 'Downloaded with Scrapling on 2026-10-03. Raw sources and original acquisition manifests are retained. [Portable inventory](CORPUS_MANIFEST.json) records SHA-256 for every corpus file. [Official source mapping](corpus/official/portable-manifest.json) uses repository-relative paths. Agent acquisition manifests retain original cache paths as provenance.','', '## Coverage','', '- All 40 reachable English official Guide pages.', '- All 20 indexed `elm/*` and `elm-explorations/*` packages: 77 published versions, 406 module versions; API JSON, generated readable Markdown, package metadata and README for each.', '- Selected tagged runtime, host, Wayland and current compiler/tooling references in the research reports.', '- 17 curated FRP/runtime primary sources, including Fran, push-pull FRP, Yampa, Flapjax and Elm’s original thesis. This is not all FRP literature.', '- Official translations, the entire third-party ecosystem and unpublished/deleted package versions are outside this collection. HTTP-200 JavaScript shells are retained as evidence, not substantive documentation.','', '## Read first','', '- [Elm Architecture](corpus/official/guide/architecture.html.md)' ]
# Guide filenames retain the original .html -> .md conversion.
index[-1]='- [Elm Architecture](corpus/official/guide/architecture.md)'
index+=['- [Ports](corpus/official/guide/interop/ports.md)','- [Interop limits](corpus/official/guide/interop/limits.md)','- [Optimization](corpus/official/guide/optimization.md)','- [FRP survey and primary references](FRP.md)','- [Host and window-system architecture](ARCHITECTURE.md)','- [Compiler, runtime and migration](IMPLEMENTATION.md)','', '## Official packages','', '| Package | Latest indexed version | Archived versions | API |','| --- | --- | ---: | --- |']
for package,versions in sorted(packages.items()):
 latest=max(versions,key=lambda v:tuple(map(int,v.split('.'))))
 index.append(f'| {package} | {latest} | {len(versions)} | [Modules](corpus/official/packages/{package}/{latest}/docs.md) |')
index+=['','## Guide pages','']
for row in manifest['entries']:
 if row['kind']=='guide':index.append(f"- [{row['url']}]({row['markdown']})".replace('](official/','](corpus/official/'))
index+=['','## FRP sources','']
for row in json.loads((DEST/'frp/manifest.json').read_text())['sources']:
 index.append(f"- [{row['name']}](corpus/frp/{Path(row['extracted']).name}) — [original]({row['url']})")
if (DEST/'compiler-stable').exists():index+=['','## Stable compiler supplemental sources','', '[Compiler source manifest](corpus/compiler-stable/sources.json) covers all eight files in the stable tagged documentation tree, ten installer READMEs, and official reference routes. [Acquisition report](SUPPLEMENT.md) distinguishes extracted content and failed routes.']
if (DEST/'elm-ui').exists():index+=['','## Selected GUI library','', '[elm-ui 1.1.8 API](corpus/elm-ui/docs.md), [README](corpus/elm-ui/README.md), [provenance](corpus/elm-ui/manifest.json). This is an optional third-party layout library, not a native window manager.']
(HERE/'CORPUS_INDEX.md').write_text('\n'.join(index)+'\n')
print(json.dumps({'files':len(files),'bytes':sum(f['bytes'] for f in files),'sourceRecordsHashVerified':checks}))
