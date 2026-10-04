"""Freeze actual V307 source/evidence and all referenced executable closure."""
import hashlib,json,os,resource,sys
from pathlib import Path
sys.path.insert(0,'/home/hoskinson/window-integration-qa');from qa_launch import require_qa_scope
require_qa_scope();assert resource.getrlimit(resource.RLIMIT_CORE)==(1,1)
ROOT=Path(__file__).resolve().parents[1];R=ROOT.parent;BUILD=ROOT/'build-1791154124276959170';external={}
def sha(p):
 h=hashlib.sha256()
 with Path(p).open('rb') as f:
  for b in iter(lambda:f.read(1048576),b''):h.update(b)
 return h.hexdigest()
def pin(p,w=None):
 p=Path(p);assert p.is_file(),str(p);digest=sha(p);assert w is None or digest==w,str(p);external[str(p)]={'sha256':digest,'size':p.stat().st_size}
# Verify exact full upstream manifest, including nested compiler/header evidence.
ancestor=R/'elm-core-keyboardless-focus-v205/component-manifest.json';a=json.loads(ancestor.read_text());assert a['sourceHeld'] and a['evidenceIntegrityPassed'];pin(ancestor)
for rel,row in a['files'].items():pin(ancestor.parent/rel,row['sha256'])
for p,row in a.get('externalFiles',{}).items():pin(p,row['sha256'])
reports=[ROOT/'qa/audit-1791154009981036333/report.json',ROOT/'qa/compile-1791153820804918030/report.json',BUILD/'report.json',ROOT/'qa/getter-1791154267456611843/report.json']
for p in reports:
 d=json.loads(p.read_text());assert d['passed'];pin(p)
 for key in ['dependencies','linkDependencies','linkedLibraries','tools']:
  for path,w in d.get(key,{}).items():pin(path,w)
 for x in d.get('objects',[]):
  pin(x['source'],x['sourceSHA256']);pin(x['object'],x['objectSHA256'])
  if 'report' in x:pin(x['report'],x['reportSHA256'])
  if 'dependencyFile' in x:pin(x['dependencyFile'],x['dependencySHA256'])
  for path,w in x.get('dependencyInventory',{}).items():pin(path,w)
 for rel,row in d.get('owningHeaderOrigins',{}).items():pin(row['path'],row['sha256'])
d=json.loads((BUILD/'report.json').read_text());pin(d['binary'],d['binarySHA256']);pin(BUILD/'libhyprland_lib.a',d['archiveSHA256'])
descriptor={'binary':d['binary'],'sha256':d['binarySHA256'],'buildReport':str(BUILD/'report.json'),'buildReportSHA256':sha(BUILD/'report.json'),'archive':str(BUILD/'libhyprland_lib.a'),'archiveSHA256':d['archiveSHA256'],'owningVersionHeaderSHA256':d['owningVersionHeaderSHA256'],'nativeAcceptance':False,'installed':False,'scope':'Core205 derivative with additive current XDG grab accessor; new consumer plugin/native pairing required'}
(ROOT/'core-build-report.json').write_text(json.dumps(descriptor,indent=2)+'\n')
files={}
for p in sorted(ROOT.rglob('*')):
 if not p.is_file() or p==ROOT/'component-manifest.json' or '__pycache__' in p.parts:continue
 files[str(p.relative_to(ROOT))]={'sha256':sha(p),'size':p.stat().st_size,'mode':oct(p.stat().st_mode&0o777)}
m={'sourceHeld':True,'evidenceIntegrityPassed':True,'nativeAcceptance':False,'installed':False,'buildReport':str(BUILD/'report.json'),'buildReportSHA256':sha(BUILD/'report.json'),'files':files,'externalFiles':external}
(ROOT/'component-manifest.json').write_text(json.dumps(m,indent=2)+'\n');print('PASS',len(files),'own',len(external),'external','manifest',sha(ROOT/'component-manifest.json'))
