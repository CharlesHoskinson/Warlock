"""Actual frozen313 capture method +freshly recomputed309 joins; synthetic I/O only."""
import copy,hashlib,json,pathlib,sys,time,traceback
from types import SimpleNamespace
ROOT=pathlib.Path(__file__).resolve().parents[1];BASE=ROOT.parent/'elm-qt6-full-driver-surface-transform-v313';sys.path.insert(0,str(BASE/'qa/helpers'));sys.path.insert(0,str(BASE/'qa'))
import scene,geometry
from driver import Driver,Refused

q={'event':'inspect','role':'A','instance':1,'mapGeneration':1,'surfaceId':42,'pid':100,'processStarted':300,'visible':True,'windowWidth':320,'windowHeight':180,'devicePixelRatio':2,'landmarkWindowX':10,'landmarkWindowY':20,'landmarkWidth':100,'landmarkHeight':60,'surfaceTransformAvailable':True,'surfaceTransformResourceId':42,'surfaceToWindowX':-6,'surfaceToWindowY':-30,'clientMarginLeft':6,'clientMarginTop':30,'clientMarginRight':7,'clientMarginBottom':8}
c={'address':'0xabc','pid':100,'title':'ELM-QT6-A-100','xwayland':False,'at':[83,61],'size':[320,180]}
n={'address':'0xabc','pid':100,'parentAddress':'0x0','xdgToplevel':True,'dialogPresent':False,'dialogModal':False,'nativeModal':False,'inputBlocked':False,'acceptsInput':True,'hidden':False,'xwayland':False};state={'schema':1,'pid':200,'windows':[n]}
lines=['-> wl_compositor@1.create_surface(new id wl_surface@42)','-> xdg_wm_base@2.get_xdg_surface(new id xdg_surface@43, wl_surface@42)','-> xdg_surface@43.get_toplevel(new id xdg_toplevel@44)','-> xdg_toplevel@44.set_title("ELM-QT6-A-100")','-> xdg_surface@43.set_window_geometry(16, 24, 320, 180)','xdg_surface@43.configure(7)','-> xdg_surface@43.ack_configure(7)','-> wl_surface@42.attach(wl_buffer@50, 0, 0)','-> wl_surface@42.commit()']
def raw(rows=lines):return ('\n'.join('[19:18:30.269154] {Default Queue} '+x for x in rows)+'\n').encode()
def join(qq=q):return scene.join_window([qq],raw(),[c],state,name='A',pid=100,started=300,compositor_pid=200)

def main():
 out=ROOT/'qa'/('test-'+str(time.time_ns()));out.mkdir();checks=[];report={'passed':False,'nativeAcceptance':False,'scope':'Actual frozen driver/join/decoder functions; synthetic native state, protocol journal and capture collaborators, no PNG/native presentation claim.'}
 def yes(name,value):assert value,name;checks.append(name)
 def refuses(name,fn):
  try:fn()
  except Refused:checks.append(name);return
  raise AssertionError(name)
 def capture(after,name):
  before=join();d=Driver.__new__(Driver);d.phase='QT01';d.deadline=time.monotonic()+1;d.directory=out/name;d.directory.mkdir();d.report={'checks':[],'nativeAcceptance':False};bound=iter([before,after]);d.binding=lambda role:next(bound);d.inspect=lambda:[];d.session=SimpleNamespace(data=lambda kind:[c],ctl=lambda command:'{}');d.host=SimpleNamespace();d.actor=SimpleNamespace()
  def fake_capture(session,host,directory,deadline,selected):
   directory.mkdir();return b'synthetic-capture',{'nativeAcceptance':False,'mockCapture':True}
  d.h=SimpleNamespace(scene=scene,pixels=SimpleNamespace(capture=fake_capture,yellow_marker=lambda data,point:{'passed':True,'mockPixels':True}))
  try:return Driver.stable_capture(d,'A')
  finally:(d.directory/'checks.json').write_text(json.dumps(d.report,indent=2)+'\n')
 try:
  before=join();yes('fresh-actual-join-positive',before['marker']['surface']==[24,58])
  yes('unchanged-actual-capture-method',capture(copy.deepcopy(before),'positive')==before)
  for changes,name in [({'surfaceToWindowX':-9,'clientMarginLeft':9},'left-map-change'),({'surfaceToWindowY':-31,'clientMarginTop':31},'top-map-change'),({'clientMarginRight':9},'right-margin-change'),({'clientMarginBottom':10},'bottom-margin-change'),({'landmarkWindowX':11},'marker-allocation-change')]:
   after=join(dict(q,**changes));yes(name+'-identical-rawACK-and-commit',before['wire']==after['wire']);yes(name+'-fresh-mapping-differs',before['marker']!=after['marker']);refuses(name+'-actual-method-refuses',lambda after=after,name=name:capture(after,name))
  # Popup roles freshly bind raw/native parent and derive action map independently.
  p=dict(q,role='P',instance=2,surfaceId=60,surfaceTransformResourceId=60,transientSurfaceId=42,windowWidth=100,windowHeight=60,actionBoundsAvailable=True,popupActionEnabled=True,popupActionVisible=True,actionWindowX=0,actionWindowY=16,actionWidth=100,actionHeight=24,popupMarkerBoundsAvailable=True,popupMarkerWindowX=4,popupMarkerWindowY=4,popupMarkerWidth=8,popupMarkerHeight=8)
  pl=lines+['-> wl_compositor@1.create_surface(new id wl_surface@60)','-> xdg_wm_base@2.get_xdg_surface(new id xdg_surface@61, wl_surface@60)','-> xdg_surface@61.get_popup(new id xdg_popup@62, xdg_surface@43, xdg_positioner@63)','-> xdg_popup@62.grab(wl_seat@3, 8)','xdg_popup@62.configure(10, 20, 100, 60)','xdg_surface@61.configure(9)','-> xdg_surface@61.set_window_geometry(0, 0, 100, 60)','-> xdg_surface@61.ack_configure(9)','-> wl_surface@60.attach(wl_buffer@64, 0, 0)','-> wl_surface@60.commit()']
  resource=lambda sid:{'id':sid,'pid':100,'uid':1000}
  ps={'schema':1,'pid':200,'grabPresent':True,'grabKeyboard':True,'grabPointer':True,'keyboardFocus':resource(60),'pointerFocus':resource(60),'popups':[{'viewAddress':'0xabd','surface':resource(60),'t1Root':resource(42),'position':[110,120],'size':[100,60],'visible':True,'grabMember':True,'rootGrabMember':True}]}
  def popup(pp):return scene.join_popup([pp],raw(pl),ps,parent=before,pid=100,started=300,uid=1000,compositor_pid=200)
  pb=popup(p);yes('popup-fresh-action-map-positive',scene.same(pb,copy.deepcopy(pb)))
  for changes,name in [({'surfaceToWindowX':-8,'clientMarginLeft':8},'popup-measured-map'),({'actionWindowY':17},'popup-QAction-allocation')]:
   after=popup(dict(p,**changes));yes(name+'-same-original-protocol',after['wire']==pb['wire']);yes(name+'-action-change-refused',after['action']!=pb['action'] and not scene.same(pb,after))
  yes('entire-frozen313-native-deadline-preserved','remaining(self.deadline)' in (BASE/'qa/driver.py').read_text())
  report.update(passed=True,checks=checks)
 except BaseException as e:report.update(error=repr(e),traceback=traceback.format_exc(),checks=checks)
 report['inputs']={str(p):hashlib.sha256(p.read_bytes()).hexdigest() for p in [pathlib.Path(__file__),BASE/'qa/driver.py',BASE/'qa/helpers/scene.py',BASE/'qa/helpers/geometry.py',BASE/'qa/helpers/protocol.py']}
 (out/'fixture.json').write_text(json.dumps({'role':q,'native':c,'roleState':state,'raw':raw().decode()},indent=2)+'\n');(out/'test.py').write_bytes(pathlib.Path(__file__).read_bytes());(out/'report.json').write_text(json.dumps(report,indent=2)+'\n');print(json.dumps({'report':str(out/'report.json'),'passed':report['passed'],'checks':len(checks),'error':report.get('error')}));return 0 if report['passed'] else 1
if __name__=='__main__':raise SystemExit(main())
