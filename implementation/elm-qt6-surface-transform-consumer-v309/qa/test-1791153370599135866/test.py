import copy,hashlib,json,pathlib,sys,time,traceback
ROOT=pathlib.Path(__file__).resolve().parents[1];sys.path.insert(0,str(ROOT/'qa'))
import geometry
from journal import Refused

def main():
 out=ROOT/'qa'/('test-'+str(time.time_ns()));out.mkdir();checks=[];report={'passed':False,'nativeAcceptance':False}
 def yes(name,call):
  assert call(),name;checks.append(name)
 def no(name,call):
  try:call()
  except Refused:checks.append(name);return
  raise AssertionError(name)
 try:
  role={'role':'A','instance':1,'mapGeneration':2,'surfaceId':11,'visible':True,'windowWidth':320,'windowHeight':180,'devicePixelRatio':1.0,'landmarkWindowX':10,'landmarkWindowY':20,'landmarkWidth':100,'landmarkHeight':60,'surfaceTransformAvailable':True,'surfaceTransformResourceId':11,'surfaceToWindowX':-6,'surfaceToWindowY':-30,'clientMarginLeft':6,'clientMarginTop':30,'clientMarginRight':7,'clientMarginBottom':8}
  def marker(r=role):return geometry.marker(r,identity={'role':'A','instance':1,'mapGeneration':2,'surfaceId':11},native_real=[100,200,320,180],window_geometry=[6,30,320,180])
  yes('measured-decoration-inverse',lambda:marker()['surface']==[24,58])
  yes('native-xdg-transform-independent',lambda:marker()['global']==[118,228])
  yes('window-input-local-retained',lambda:marker()['window']==[18,28])
  for field,value,name in [('surfaceTransformAvailable',False,'unavailable'),('surfaceTransformAvailable',1,'bool-not-int'),('surfaceTransformResourceId',12,'wrong-resource'),('surfaceTransformResourceId',True,'bool-resource'),('surfaceToWindowX',float('nan'),'nan'),('surfaceToWindowY',float('inf'),'inf'),('surfaceToWindowX',-7,'map-disagreement'),('clientMarginLeft',-1,'negative-margin'),('clientMarginRight',2**24,'oversize-margin'),('clientMarginTop',True,'bool-margin'),('surfaceToWindowX',10**1000,'huge-int'),('instance',2,'replaced-instance')]:
   r=dict(role);r[field]=value;no(name,lambda r=r:marker(r))
  zero=dict(role,surfaceToWindowX=0,surfaceToWindowY=0,clientMarginLeft=0,clientMarginTop=0)
  yes('actual-zero-map-admitted',lambda:marker(zero)['surface']==[18,28])
  p=dict(role,role='P',windowWidth=100,windowHeight=50,popupMarkerBoundsAvailable=True,popupMarkerWindowX=4,popupMarkerWindowY=4,popupMarkerWidth=8,popupMarkerHeight=8,actionBoundsAvailable=True,popupActionEnabled=True,popupActionVisible=True,actionWindowX=10,actionWindowY=12,actionWidth=40,actionHeight=20)
  action=geometry.action_region(p,native_real=[100,200,100,50],window_geometry=[6,30,100,50])
  yes('action-whole-rect-inverse',lambda:action['surface']==[16,42,40,20] and action['global']==[110,212,40,20] and action['point']==[130,222])
  no('action-unavailable-map',lambda:geometry.action_region(dict(p,surfaceTransformAvailable=False),native_real=[100,200,100,50],window_geometry=[6,30,100,50]))
  yes('right-margin-snapshot-visible',lambda:marker(dict(role,clientMarginRight=9))!=marker())
  report.update(passed=True,checks=checks,sourceSHA256=hashlib.sha256((ROOT/'qa/geometry.py').read_bytes()).hexdigest())
 except BaseException as e:report.update(error=repr(e),traceback=traceback.format_exc(),checks=checks)
 (out/'geometry.py').write_bytes((ROOT/'qa/geometry.py').read_bytes());(out/'test.py').write_bytes(pathlib.Path(__file__).read_bytes());(out/'report.json').write_text(json.dumps(report,indent=2)+'\n');print(json.dumps({'report':str(out/'report.json'),'passed':report['passed'],'checks':len(checks),'error':report.get('error')}));return 0 if report['passed'] else 1
if __name__=='__main__':raise SystemExit(main())
