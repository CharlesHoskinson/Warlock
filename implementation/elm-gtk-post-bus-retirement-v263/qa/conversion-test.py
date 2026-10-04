"""Independent boundary cases for measured GTK conversion/transcript joins."""
import copy,hashlib,json,resource,sys,time
from pathlib import Path
sys.path.insert(0,'/home/hoskinson/window-integration-qa')
from qa_launch import require_qa_scope
require_qa_scope();assert resource.getrlimit(resource.RLIMIT_CORE)==(1,1)
from geometry import marker
from protocol import Trace
from journal import Refused
OUT=Path(__file__).parent/('conversion-'+str(time.time_ns()));OUT.mkdir();checks=[];report={'passed':False,'nativeAcceptance':False,'syntheticTranscriptAndGeometryOnly':True,'checks':checks}
def check(name,fn,reject=False):
 try:fn();passed=not reject
 except Refused:passed=reject
 checks.append({'name':name,'passed':passed});assert passed,name
identity={'role':'A','instance':1,'mapGeneration':2,'surfaceId':5}
role={**identity,'mapped':True,'landmarkBoundsAvailable':True,'landmarkNativeX':10,'landmarkNativeY':20,'landmarkWidth':100,'landmarkHeight':60,'nativeSurfaceTransformX':-4,'nativeSurfaceTransformY':-8,'surfaceWidth':340,'surfaceHeight':220}
def measured(row=role):return marker(row,identity=identity,native_real=[83,61,320,180],window_geometry=[4,8,320,180])
raw=b'''[1.000] -> wl_compositor#1.create_surface(new id wl_surface#5)
[2.000] -> xdg_wm_base#2.get_xdg_surface(new id xdg_surface#6, wl_surface#5)
[3.000] -> xdg_surface#6.get_toplevel(new id xdg_toplevel#7)
[4.000] -> xdg_toplevel#7.set_title("ELM-GTK4-A-1234")
[5.000] xdg_toplevel#7.configure(320, 180, array[0])
[6.000] xdg_surface#6.configure(9)
[7.000] -> xdg_surface#6.ack_configure(9)
[8.000] -> xdg_surface#6.set_window_geometry(4, 8, 320, 180)
[8.500] -> wl_surface#5.attach(wl_buffer#12, 0, 0)
[9.000] -> wl_surface#5.commit()
'''
try:
 result=measured();check('widget-minus-transform-minus-origin-once',lambda:result['surface']==[22,36] and result['global']==[101,89] or (_ for _ in ()).throw(Refused('wrong independent expected point')))
 check('unequal-real-geometry-rejected',lambda:marker(role,identity=identity,native_real=[83,61,321,180],window_geometry=[4,8,320,180]),True)
 for name,field,value in [('stale-map','mapGeneration',3),('foreign-resource','surfaceId',6),('missing-bounds','landmarkBoundsAvailable',False),('huge-transform','nativeSurfaceTransformX',10**400),('bool-transform','nativeSurfaceTransformY',True),('nonfinite-transform','nativeSurfaceTransformX',float('nan'))]:
  changed={**role,field:value};check(name,lambda c=changed:measured(c),True)
 def joined(data=raw):return Trace(data).role(role='A',pid=1234,surface_id=5)
 check('owning-resource-configure-ACK-commit',lambda:joined())
 check('modern-at-object-format',lambda:joined(raw.replace(b'#',b'@')))
 for name,data in [('wrong-resource',raw.replace(b'wl_surface#5)',b'wl_surface#8)',1)),('wrong-actor-title',raw.replace(b'A-1234',b'A-1235')),('missing-buffer-attachment',raw.replace(b'[8.500] -> wl_surface#5.attach(wl_buffer#12, 0, 0)\n',b'')),('missing-ACK',raw.replace(b'[7.000] -> xdg_surface#6.ack_configure(9)\n',b'')),('wrong-ACK-serial',raw.replace(b'ack_configure(9)',b'ack_configure(10)')),('commit-before-ACK',raw.replace(b'[9.000] -> wl_surface#5.commit()\n',b'')+b'[10.000] -> xdg_surface#6.ack_configure(9)\n'),('surface-retired',raw+b'[10.000] -> wl_surface#5.destroy()\n')]:check(name,lambda d=data:joined(d),True)
 report['passed']=True
finally:
 report['inputs']={str(p):hashlib.sha256(p.read_bytes()).hexdigest() for p in [Path(__file__),Path(__file__).with_name('geometry.py'),Path(__file__).with_name('protocol.py'),Path(__file__).with_name('journal.py')]}
 (OUT/'report.json').write_text(json.dumps(report,indent=2)+'\n');print(OUT/'report.json')
