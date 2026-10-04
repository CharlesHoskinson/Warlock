"""Actual driver/input decoder controls; no compositor, display, or fake native receipt."""
import copy,hashlib,json,pathlib,sys,time,traceback
from types import SimpleNamespace
ROOT=pathlib.Path(__file__).resolve().parents[1];sys.path.insert(0,str(ROOT/'qa/helpers'));sys.path.insert(0,str(ROOT/'qa'))
import coordinates,geometry,journal
from driver import Driver

def main():
 out=ROOT/'qa'/('coordinates-test-'+str(time.time_ns()));out.mkdir();report={'passed':False,'nativeAcceptance':False};checks=[]
 def yes(name,value):assert value,name;checks.append(name)
 def no(name,call):
  try:call()
  except (journal.Refused,ValueError):checks.append(name);return
  raise AssertionError(name)
 try:
  types=json.loads((ROOT/'qt-domains-build-report.json').read_text())['constants']
  q={'role':'A','instance':1,'mapGeneration':2,'surfaceId':11,'visible':True,'windowWidth':320,'windowHeight':180,'windowPositionX':999,'windowPositionY':888,'devicePixelRatio':1,'landmarkWindowX':10,'landmarkWindowY':20,'landmarkWidth':100,'landmarkHeight':60,'surfaceTransformAvailable':True,'surfaceTransformResourceId':11,'surfaceToWindowX':-6,'surfaceToWindowY':-30,'clientMarginLeft':6,'clientMarginTop':30,'clientMarginRight':7,'clientMarginBottom':8}
  b={'qt':q,'identity':geometry.identity(q),'native':{'at':[100,200],'size':[320,180]},'wire':{'windowGeometry':[6,30,320,180]}}
  b['marker']=geometry.marker(q,identity=b['identity'],native_real=[100,200,320,180],window_geometry=b['wire']['windowGeometry'])
  expected=coordinates.input_coordinates(b,b['marker']['global'])
  yes('global-to-surface-to-window',expected['surface']==[24,58] and expected['window']==[18,28])
  yes('Qt-global-observation-not-desktop-authority',expected['toolkitGlobal']==[1017,916] and expected['toolkitGlobal']!=b['marker']['global'])
  for key,value,name in [('surfaceTransformAvailable',False,'missing-map'),('surfaceTransformResourceId',12,'stale-map'),('surfaceToWindowX',-7,'map-margin-disagreement'),('surfaceToWindowY',float('inf'),'infinite-map'),('windowPositionX',float('nan'),'nan-Qt-global'),('windowWidth',True,'bool-width'),('visible',False,'hidden')]:
   changed=copy.deepcopy(b);changed['qt'][key]=value;no(name,lambda c=changed:coordinates.input_coordinates(c,[118,228]))
  bad=copy.deepcopy(b);bad['identity']['surfaceId']=True;no('bool-captured-resource',lambda:coordinates.input_coordinates(bad,[118,228]))
  bad=copy.deepcopy(b);bad['native']['size']=[321,180];no('Q1-mismatch',lambda:coordinates.input_coordinates(bad,[118,228]))
  no('outside-content',lambda:coordinates.input_coordinates(b,[99,199]))
  no('nonfinite-global',lambda:coordinates.input_coordinates(b,[float('nan'),200]))
  def rows(local=[18,28],global_qt=[1017,916],extra=False):
   result=[]
   for i,(event,buttons) in enumerate([('window-button-press',1),('window-button-release',0)],1):
    result.append(dict(schema=1,sequence=i,pid=4000,processStarted=9000,monotonicUs=100+i,requestSequence=0,event=event,profile='window-modal',role='A',instance=1,mapGeneration=2,surfaceId=11,sourceSurfaceId=11,trackedRecipient=True,qtTimestamp=1000+i,qtModifiers=0,rawEventType=types[event],qtButton=1,qtButtons=buttons,qtMouseSource=types['mouseNotSynthesized'],localX=local[0],localY=local[1],globalQtX=global_qt[0],globalQtY=global_qt[1]))
   if extra:
    r=copy.deepcopy(result[-1]);r.update(sequence=3,monotonicUs=103,event='window-button-press',role='C');result.append(r)
   return journal.parse(b''.join(json.dumps(r).encode()+b'\n' for r in result),pid=4000,started='9000')
  def pair(raw):
   d=Driver.__new__(Driver);d.deadline=time.monotonic()+1;d.phase='QT01';d.types=types;d.h=SimpleNamespace(journal=journal);calls=[];d.binding=lambda role:b;d.interval_start=lambda:0;d.pointer_parent=lambda point:calls.append(('motion',point));d.parent=SimpleNamespace(send=lambda op,deadline:calls.append(('button',op)));d.inspect=lambda:raw;d.check=lambda name,value,**kw:yes(name,value);Driver.pair(d,'A');return calls
  calls=pair(rows());yes('actual-Driver-pair-measured-desktop-injection',calls[0]==('motion',[118,228]))
  no('old-surface-as-Qt-local-refused',lambda:pair(rows(local=[24,58])))
  no('desktop-as-Qt-global-refused',lambda:pair(rows(global_qt=[118,228])))
  no('entire-extra-recipient-refused',lambda:pair(rows(extra=True)))
  # Same canonical content point with a measured zero offset preserves baseline behavior.
  zero=copy.deepcopy(b);zero['qt'].update(surfaceToWindowX=0,surfaceToWindowY=0,clientMarginLeft=0,clientMarginTop=0)
  yes('available-zero-transform-retains-input',coordinates.input_coordinates(zero,[112,198])['window']==[18,28])
  report.update(passed=True,checks=checks,compiledEventTypes=types)
 except BaseException as e:report.update(error=repr(e),traceback=traceback.format_exc(),checks=checks)
 report['inputs']={str(p):hashlib.sha256(p.read_bytes()).hexdigest() for p in [pathlib.Path(__file__),ROOT/'qa/coordinates.py',ROOT/'qa/driver.py',ROOT/'qa/shell.py',ROOT/'qa/helpers/geometry.py',ROOT/'qa/helpers/journal.py']}
 for p in [pathlib.Path(__file__),ROOT/'qa/coordinates.py',ROOT/'qa/driver.py',ROOT/'qa/shell.py']:(out/p.name).write_bytes(p.read_bytes())
 (out/'report.json').write_text(json.dumps(report,indent=2)+'\n');print(json.dumps({'report':str(out/'report.json'),'passed':report['passed'],'checks':len(checks),'error':report.get('error')}));return 0 if report['passed'] else 1
if __name__=='__main__':raise SystemExit(main())
