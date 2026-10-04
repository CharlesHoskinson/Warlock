import hashlib,json,resource,sys,time
from pathlib import Path
sys.path.insert(0,'/home/hoskinson/window-integration-qa')
from qa_launch import require_qa_scope
require_qa_scope();assert resource.getrlimit(resource.RLIMIT_CORE)==(1,1)
ROOT=Path(__file__).resolve().parents[1];OUT=ROOT/'qa'/('capture-scope-'+str(time.time_ns()));OUT.mkdir();sys.path.insert(0,str(ROOT/'qa/helpers'));sys.path.insert(0,str(ROOT/'qa'));from capture_scope import surface_extent,attribution,Refused
report={'passed':False,'nativeAcceptance':False,'checks':[]}
def check(n,v):assert v,n;report['checks'].append({'name':n,'passed':True})
def refused(n,fn):
 try:fn()
 except Refused:check(n,True)
 else:check(n,False)
def raw(width=200,height=100,scale=1,extra=''):
 return ('[01:02:03.123456] -> wl_shm_pool#6.create_buffer(new id wl_buffer#8, 0, %d, %d, %d, 0)\n[01:02:03.123457] -> wl_surface#21.set_buffer_scale(%d)\n%s[01:02:03.123459] -> wl_surface#21.commit()\n'%(width,height,width*4,scale,extra)).encode()
b={'identity':{'surfaceId':21},'wire':{'bufferId':8,'lastCommitIndex':3,'windowGeometry':[16,24,100,50]},'native':{'at':[300,300],'size':[100,50]}}
try:
 check('full-actual-SHM-extent',surface_extent(raw(),b)['logical']==[200,100])
 check('buffer2-divides-only-SHM-physical-extent',surface_extent(raw(400,200,2),b)['logical']==[200,100])
 selected={'marker':{'global':[100,100]},'native':{'at':[90,90],'size':[40,40]}}
 check('whole-other-buffer-disjoint',attribution(raw(),selected,b)['excludedOtherSurfaceRect']==[284,276,200,100])
 shadow=dict(b,native={'at':[115,124],'size':[100,50]})
 refused('surface-origin-shadow-intersection-refuses',lambda:attribution(raw(),selected,shadow))
 refused('missing-actual-buffer-refuses',lambda:surface_extent(b'',b))
 refused('unqualified-raster-dimensions-refuse',lambda:surface_extent(raw(4097,100),b))
 refused('fractional-logical-buffer-refuses',lambda:surface_extent(raw(201,100,2),b))
 refused('destroyed-buffer-cannot-certify-extent',lambda:surface_extent(raw(extra='[01:02:03.123458] -> wl_buffer#8.destroy()\n'),b))
 report['passed']=True
finally:
 report['inputs']={str(p):hashlib.sha256(p.read_bytes()).hexdigest() for p in [Path(__file__),ROOT/'qa/capture_scope.py',ROOT/'qa/helpers/protocol.py']};(OUT/'report.json').write_text(json.dumps(report,indent=2)+'\n');print(OUT/'report.json')
