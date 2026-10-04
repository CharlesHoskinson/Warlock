"""Bind independently reviewed joined-grab source to its final owning build."""
import hashlib,json,resource,sys,time
from pathlib import Path
sys.path.insert(0,'/home/hoskinson/window-integration-qa');from qa_launch import require_qa_scope
require_qa_scope();assert resource.getrlimit(resource.RLIMIT_CORE)==(1,1)
ROOT=Path(__file__).resolve().parent;SOURCE=ROOT.parent/'elm-own-popup-native-grab-join-v315';CORE=ROOT.parent/'elm-own-popup-xdg-grab-provenance-v307'
OUT=ROOT/('review-'+str(time.time_ns()));OUT.mkdir(mode=0o700);r={'passed':False,'nativeAcceptance':False,'scope':'Independent source/lifetime/join review and exact held source/build/header/tool closure; no actual observer callback/GUI execution','entries':[]}
def sha(p):
 h=hashlib.sha256()
 with Path(p).open('rb') as f:
  for b in iter(lambda:f.read(1048576),b''):h.update(b)
 return h.hexdigest()
def check(p,w=None):
 p=Path(p);assert p.is_file(),str(p);d=sha(p);assert w is None or d==w,str(p);r['entries'].append({'path':str(p),'sha256':d,'size':p.stat().st_size})
try:
 for root in [SOURCE,CORE]:
  p=root/'component-manifest.json';check(p);m=json.loads(p.read_text());assert m['sourceHeld'] and m['evidenceIntegrityPassed']
  for rel,row in m['files'].items():check(root/rel,row['sha256'])
  for path,row in m.get('externalFiles',{}).items():check(path,row['sha256'])
  if root==SOURCE:
   report=Path(m['buildReport']);check(report,m['buildReportSHA256']);d=json.loads(report.read_text());assert d['passed'] and not d['nativeAcceptance'];assert d['core']['buildReport']==str(CORE/'build-1791154124276959170/report.json')
   for rel,w in d['inputs'].items():check(SOURCE/rel,w);check(report.parent/'inputs'/rel,w)
   for rel,w in d['owningHeaders'].items():check(report.parent/'owning-headers'/rel,w)
   for section in ['dependencies','linkedLibraries','tools']:
    for path,w in d[section].items():check(path,w)
   assert not d['missingSymbols'];check(d['binary'],d['binarySHA256']);r['buildReport']=str(report)
 b=(SOURCE/'native/grab-join.inc').read_text();assert 'found->getT1Owner(' not in b and 'found->visible(' not in b
 assert 'ownerMatches != 1' in b and 'actualLayer != layerOwner' in b
 assert 'g_pSeatManager->m_seatGrab != grab' in b
 r['sourceManifestSHA256']=sha(SOURCE/'component-manifest.json');r['coreManifestSHA256']=sha(CORE/'component-manifest.json');r['passed']=True
except Exception as e:r['error']=repr(e)
finally:(OUT/'report.json').write_text(json.dumps(r,indent=2)+'\n');print(OUT/'report.json');print('PASS '+str(len(r['entries'])) if r['passed'] else r.get('error'))
if not r['passed']:raise SystemExit(1)
