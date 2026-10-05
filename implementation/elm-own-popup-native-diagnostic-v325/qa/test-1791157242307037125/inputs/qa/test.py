"""Actual strict stamp boundaries plus inert source import; no GUI."""
import json,pathlib,sys,time,copy,resource
ROOT=pathlib.Path(__file__).resolve().parents[1];sys.path.insert(0,str(ROOT/'qa'))
import stamp
from preflight import verify,sha,load
assert resource.getrlimit(resource.RLIMIT_CORE)==(1,1)
out=ROOT/'qa'/('test-'+str(time.time_ns()));out.mkdir();report={'passed':False,'nativeAcceptance':False,'checks':[]}
def check(name,predicate):
 assert predicate(),name;report['checks'].append({'name':name,'passed':True})
def deny(o,**kw):
 try:stamp.parse(json.dumps(o).encode(),pid=100,start=20,binding={'lifetime':'1','session':'2','frontend':'3'},**kw)
 except stamp.Refused:return True
 return False
try:
 o={'hostPopupProtocol':1,'kind':'host-popup-mapped','hostLifetime':'12345678-abcd-1234-1234-123456789abc','pid':'100','start':'20','sequence':'1','mapGeneration':'2','view':'3','generation':'4','topology':'5','publication':'6','lease':'7','popupSurface':10,'rootSurface':11,'binding':{'lifetime':'1','session':'2','frontend':'3'},'displaySyncComplete':False}
 kw=dict(pid=100,start=20,binding=o['binding']);a=stamp.parse(json.dumps(o).encode(),**kw);check('exact-valid-map',lambda:a==o)
 b={**o,'kind':'host-popup-sync-complete','sequence':'2','displaySyncComplete':True};b=stamp.parse(json.dumps(b).encode(),previous=1,**kw);check('exact-original-retirement',lambda:stamp.retired(a,b))
 for field,value in [('pid','101'),('start','21'),('sequence','0'),('view',True),('popupSurface',True),('rootSurface',10),('binding',{'lifetime':'1','session':'2','frontend':'4'}),('hostLifetime','bad'),('displaySyncComplete',True),('hostPopupProtocol',True)]:
  check('refuse-'+field,lambda field=field,value=value:deny({**o,field:value}))
 check('stale-sequence',lambda:deny(o,previous=1));check('unknown-field',lambda:deny({**o,'extra':False}));check('missing-field',lambda:deny({k:v for k,v in o.items() if k!='topology'}))
 for field,value in [('lease','8'),('popupSurface',12),('binding',{'lifetime':'1','session':'2','frontend':'4'})]:
  changed={**b,field:value}
  def terminal():
   try:stamp.retired(a,changed)
   except stamp.Refused:return True
   return False
  check('no-retarget-retired-'+field,terminal)
 host,core,observer,fixture,hb,build,files=verify();report['sourceFiles']=files;report['coherentHost']=str(hb);report['compiledAssets']=str(build/'inputs/assets');report['actualOwnSourcesVerified']=len(files)
 load('inert_actual325_native',ROOT/'qa/native.py');check('inert-native-import',lambda:True)
 report['passed']=True
except BaseException as e:report['error']=repr(e)
report['inputs']={str(p.relative_to(ROOT)):sha(p) for p in (ROOT/'qa').glob('*.py')}
for rel in report['inputs']:
 p=out/'inputs'/rel;p.parent.mkdir(parents=True,exist_ok=True);p.write_bytes((ROOT/rel).read_bytes())
(out/'report.json').write_text(json.dumps(report,indent=2)+'\n');print(out/'report.json');raise SystemExit(not report['passed'])
