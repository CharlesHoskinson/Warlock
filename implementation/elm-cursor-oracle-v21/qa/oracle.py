"""Meaningful pixel-oracle cases and replay of retained actual parent captures."""
import hashlib,json,resource,sys,time
from pathlib import Path
assert resource.getrlimit(resource.RLIMIT_CORE)==(1,1)
ROOT=Path(__file__).resolve().parents[1];REPO=ROOT.parents[1]
sys.path.insert(0,str(ROOT));from pixels import measure,pixels
OUT=ROOT/'qa'/('oracle-'+str(time.time_ns()));OUT.mkdir()
def digest(p):return hashlib.sha256(Path(p).read_bytes()).hexdigest()
r={'passed':False,'nativeAcceptance':False,'checks':[],'inputs':{str(p):digest(p) for p in [Path(__file__),ROOT/'pixels.py']}}
def check(name,value,**evidence):
 r['checks'].append({'name':name,'passed':bool(value),**evidence});assert value,name
try:
 def image(boxes,extra=()):
  raw=bytearray([240,240,240]*80*60)
  for box in boxes:
   x0,y0,x1,y1=box
   for y in range(y0,y1):
    for x in range(x0,x1):raw[(y*80+x)*3:(y*80+x)*3+3]=bytes([255,0,255])
   for y in range(y0+5,y0+9):
    for x in range(x0+7,x0+11):raw[(y*80+x)*3:(y*80+x)*3+3]=bytes([0,255,255])
  for x,y in extra:raw[(y*80+x)*3:(y*80+x)*3+3]=bytes([0,255,255])
  return measure(80,60,3,240,raw)
 a=image([[10,10,34,30]],[(1,1)])
 check('isolatedBackgroundCyanDoesNotMoveCursorBounds',a['bounds']==[10,10,34,30] and a['cyan']==16 and a['rawCyan']==17,image=a)
 a=image([[2,2,26,22],[45,35,69,55]])
 check('duplicateVisibleCursorRefusesSingleInstance',len(a['components'])==2 and a['bounds'] is None,image=a)
 a=image([],[(1,1)])
 check('hiddenCursorIgnoresIsolatedWallpaperPixel',len(a['components'])==0 and a['bounds'] is None,image=a)
 a=image([[10,10,34,30]])
 check('nativeClippingRemainsVisibleToExtentOracle',a['bounds']!=[10,10,58,50],image=a)
 packets=[('elm-parent-cursor-v18','qa/native-1791096006064024389/report.json',True),
          ('elm-parent-cursor-scale-v20','qa/native-1791096191973440672/report.json',False)]
 for name,relative,accepted in packets:
  root=REPO/'implementation'/name;p=root/relative;report=json.loads(p.read_text())
  r['inputs'][str(p)]=digest(p);assert report['passed'] is accepted and report['cleanupPassed']
  replayed=set()
  for c in report['checks']:
   if not (c['name'].endswith(':parentCursorHotspot') or c['name'].endswith(':cursorActuallyHidden')):continue
   sha=c['image']['sha256'];matches=[path for path in p.parent.rglob('*.png') if digest(path)==sha];assert len(matches)==1
   path=matches[0];r['inputs'][str(path)]=sha;actual=pixels(path)
   if c['name'].endswith(':cursorActuallyHidden'):
    check(name+':'+c['name'],not actual['components'],image=actual)
   else:
    expected=c['expectedBounds'];bounds=actual['bounds'];correct=bool(bounds and len(actual['components'])==1 and all(abs(a-b)<=2 for a,b in zip(bounds,expected)))
    shouldPass=c['passed']
    check(name+':'+c['name']+(':retainedFailure' if not shouldPass else ''),correct is shouldPass,image=actual,expectedBounds=expected)
   replayed.add(sha)
  check(name+':retainedSnapshotsReplayed',len(replayed)>8,count=len(replayed))
 for p,sha in r['inputs'].items():assert digest(p)==sha,p
 r['passed']=True
except Exception as e:r['error']=repr(e)
(OUT/'report.json').write_text(json.dumps(r,indent=2)+'\n');print(json.dumps({'passed':r['passed'],'report':str(OUT/'report.json'),'error':r.get('error')}));raise SystemExit(not r['passed'])
