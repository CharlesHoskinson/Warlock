"""Preserve actual failed332 mapping evidence without inventing missing rows."""
import hashlib,importlib.util,json,os,re,resource,shutil,sys,time
from pathlib import Path
sys.path.insert(0,'/home/hoskinson/window-integration-qa');from qa_launch import require_qa_scope
require_qa_scope();assert resource.getrlimit(resource.RLIMIT_CORE)==(1,1)
ROOT=Path(__file__).resolve().parent;R=ROOT.parent;SOURCE=R/'elm-own-popup-native-diagnostic-selector-v332/qa/native-1791158834072814524';REPORT=SOURCE/'report.json';OUT=ROOT/('analysis-'+str(time.time_ns()));OUT.mkdir(mode=0o700)
r={'passed':False,'nativeAcceptance':False,'ownBlockerGrantQualified':False,'fullGTKCampaignPassed':False,'scope':'Actual failed native332 evidence integrity/recorded-map analysis only; failing raw map and conflicting pathname are unavailable','externalFiles':{},'recordedMaps':{}}
def sha(p):
 h=hashlib.sha256()
 with Path(p).open('rb') as f:
  for b in iter(lambda:f.read(1048576),b''):h.update(b)
 return h.hexdigest()
def pin(p,w=None):
 p=Path(p);d=sha(p);assert w is None or d==w,str(p);r['externalFiles'][str(p)]={'sha256':d,'size':p.stat().st_size}
try:
 pin(REPORT);d=json.loads(REPORT.read_text());assert not d['passed'] and not d['nativeAcceptance'] and d['error']=="Refused('mapping inode changed')";assert d['cleanupPassed'] and d['cleanup']['privateActivationCleanupPassed'] and d['cleanup']['privateActivationPostRetirement']['passed'];assert not d['cleanup']['remainingDescendants'] and not d['cleanup']['cleanupErrors'] and d['cleanup']['runtimeGone']
 for rel,w in d['artifacts'].items():pin(SOURCE/rel,w)
 for p,w in d['inputs'].items():pin(p,w)
 shutil.copy2(REPORT,OUT/'native-report.json')
 expected=['load-exact-authority','load-exact-observer','actual-private-parent-module-map','actual-owned-host-executable-inode','actual-stamped-host-and-library-maps'];assert [c['name'] for c in d['checks']]==expected and all(c['passed'] for c in d['checks'])
 r['nativeChecksPassed']=expected;r['cleanupPassed']=True;r['nativeFailure']=d['error'];r['nativeOwner']=d['nativeOwner'];r['successfulEarlierCoreMap']=d['processMaps'];r['failingRawMapsPresent']=False;r['actualConflictingPathnameIdentified']=False
 samples={'initial-core':d['cleanup']['hyprlandMaps']['maps'],'private-parent':d['cleanup']['westonMaps']['maps'],'stamped-host':next(c['maps']['maps'] for c in d['checks'] if c['name']=='actual-stamped-host-and-library-maps')}
 spec=importlib.util.spec_from_file_location('guard',R/'elm-own-popup-runtime-closure-guard-v330/guard.py');g=importlib.util.module_from_spec(spec);spec.loader.exec_module(g)
 for name,raw in samples.items():
  (OUT/(name+'.maps')).write_text(raw);parsed=g.parse_maps(raw);values={}
  for line in raw.splitlines():
   row=line.split(None,5)
   if len(row)==6 and row[5].startswith('/'):
    p=re.sub(r'\\([0-7]{3})',lambda m:chr(int(m[1],8)),row[5]);values.setdefault(p,set()).add((*[int(v,16) for v in row[3].split(':')],int(row[4])))
  conflicts={p:sorted(v) for p,v in values.items() if len(v)>1};assert not conflicts
  r['recordedMaps'][name]={'bytes':len(raw.encode()),'sha256':hashlib.sha256(raw.encode()).hexdigest(),'absolutePathCount':len(parsed),'duplicatePathDifferentIdentity':conflicts,'scope':'Recorded earlier/separate snapshot, not failing query bytes'}
 assert all('maps' not in k.lower() for k in d['artifacts'])
 r['failedGuardSite']='330 parse_maps before authority hello in332 native.py query guard';r['conclusion']='Captured earlier maps contain no conflicting pathname. Later failing core map bytes were not persisted, so actual conflicting name/inodes cannot be reconstructed. Same-named memfd legitimacy may be tested independently, but is not this run\'s proven cause.';r['passed']=True
except Exception as e:r['error']=repr(e)
finally:(OUT/'report.json').write_text(json.dumps(r,indent=2)+'\n');print(OUT/'report.json');print('PASS '+str(len(r['externalFiles']))+' evidence/source entries' if r['passed'] else r.get('error'))
if not r['passed']:raise SystemExit(1)
