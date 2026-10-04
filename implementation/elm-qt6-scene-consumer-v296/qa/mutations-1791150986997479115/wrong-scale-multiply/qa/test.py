import copy,hashlib,json,resource,sys,time,traceback,py_compile
from pathlib import Path
sys.path.insert(0,'/home/hoskinson/window-integration-qa')
from qa_launch import require_qa_scope
require_qa_scope();assert resource.getrlimit(resource.RLIMIT_CORE)==(1,1)
ROOT=Path(__file__).resolve().parents[1];OUT=ROOT/'qa'/('test-'+str(time.time_ns()));OUT.mkdir();sys.path.insert(0,str(ROOT/'qa'))
from scene import current_role,join_window,join_popup,same
from geometry import marker,action_region,identity
from protocol import Trace
from journal import Refused
checks=[]
def yes(name,fn):
 fn();checks.append({'name':name,'passed':True})
def equal(a,b):assert a==b,(a,b)
def refuses(name,fn):
 try:fn()
 except Refused:checks.append({'name':name,'passed':True});return
 raise AssertionError(name)
q={'event':'inspect','role':'A','instance':1,'mapGeneration':1,'surfaceId':42,'pid':100,'processStarted':300,'visible':True,'windowWidth':320,'windowHeight':180,'devicePixelRatio':2,'landmarkWindowX':10,'landmarkWindowY':20,'landmarkWidth':100,'landmarkHeight':60}
c={'address':'0xabc','pid':100,'title':'ELM-QT6-A-100','xwayland':False,'at':[83,61],'size':[320,180]}
n={'address':'0xabc','pid':100,'parentAddress':'0x0','xdgToplevel':True,'dialogPresent':False,'dialogModal':False,'nativeModal':False,'inputBlocked':False,'acceptsInput':True,'hidden':False,'xwayland':False}
st={'schema':1,'pid':200,'windows':[n]}
lines=['-> wl_compositor@1.create_surface(new id wl_surface@42)','-> xdg_wm_base@2.get_xdg_surface(new id xdg_surface@43, wl_surface@42)','-> xdg_surface@43.get_toplevel(new id xdg_toplevel@44)','-> xdg_toplevel@44.set_title("ELM-QT6-A-100")','-> xdg_surface@43.set_window_geometry(16, 24, 320, 180)','xdg_surface@43.configure(7)','-> xdg_surface@43.ack_configure(7)','-> wl_surface@42.attach(wl_buffer@50, 0, 0)','-> wl_surface@42.commit()']
def raw(v=lines):return ('\n'.join('[19:18:30.269154] {Default Queue} '+x for x in v)+'\n').encode()
def window(qq=q,cc=None,ss=None,rr=None,**kw):return join_window([qq],raw() if rr is None else rr,[c] if cc is None else cc,st if ss is None else ss,name='A',pid=100,started=300,compositor_pid=200,**kw)
report={'passed':False,'nativeAcceptance':False,'fullCampaign':False,'checks':checks,'sourceInputs':{str(p):hashlib.sha256(p.read_bytes()).hexdigest() for p in (ROOT/'qa').glob('*.py')}}
try:
 for p in (ROOT/'qa').glob('*.py'):py_compile.compile(str(p),cfile=str(OUT/(p.stem+'.pyc')),doraise=True)
 b=window();yes('window exact process role/native/passive epoch join',lambda:equal(b['identity']['processStarted'],300))
 yes('origin subtracted once no device scale multiplication',lambda:equal(b['marker']['global'],[85,65]))
 yes('queued commit never presentation',lambda:equal(b['presentationProved'],False))
 yes('native inputBlocked authoritative retained',lambda:equal(window(ss={**st,'windows':[{**n,'inputBlocked':True,'acceptsInput':False}]})['nativeRole']['inputBlocked'],True))
 yes('absent mapped role readiness',lambda:equal(window(cc=[]),None))
 yes('absent ACK readiness',lambda:equal(window(rr=raw(lines[:5])),None))
 yes('retired wl surface unavailable',lambda:equal(window(rr=raw(lines+['-> wl_surface@42.destroy()'])),None))
 yes('native extent mismatch not admitted',lambda:equal(window(cc=[{**c,'size':[321,180]}]),None))
 yes('Qt extent mismatch not admitted',lambda:equal(window(qq={**q,'windowWidth':321}),None))
 yes('invisible no scene',lambda:equal(current_role([{**q,'visible':False}],'A'),None))
 yes('late old localdestroy preserves newinstance',lambda:equal(current_role([q,{**q,'instance':2},{**q,'event':'local-destroy'}],'A')['instance'],2))
 refuses('late old non-destroy callback refuses',lambda:current_role([q,{**q,'instance':2},q],'A'))
 for key in ['instance','mapGeneration','surfaceId','pid','processStarted']:
  for v in [True,1.0,0,-1,10**400]:refuses(f'{key} canonical {repr(v)[:20]}',lambda key=key,v=v:window(qq={**q,key:v})) if key not in ('surfaceId','mapGeneration') or v!=0 else yes(f'{key} premapzero notadmitted',lambda key=key:equal(window(qq={**q,key:0}),None))
 refuses('wrong processStart',lambda:window(qq={**q,'processStarted':301}))
 refuses('native duplicate address entire inventory',lambda:window(cc=[c,c]))
 refuses('duplicate matching title different address',lambda:window(cc=[c,{**c,'address':'0xabd'}]))
 refuses('foreign observer owner',lambda:window(ss={**st,'pid':201}))
 refuses('native eligibility bool alias',lambda:window(ss={**st,'windows':[{**n,'acceptsInput':1}]}))
 refuses('wrong native xwayland',lambda:window(cc=[{**c,'xwayland':True}]))
 refuses('huge marker coordinate typed',lambda:window(qq={**q,'landmarkWindowX':10**400}))
 refuses('NaN marker coordinate typed',lambda:window(qq={**q,'landmarkWindowX':float('nan')}))
 refuses('marker allocation outside window',lambda:window(qq={**q,'landmarkWindowX':319}))
 refuses('protocol malformed created resource',lambda:window(rr=raw(['-> wl_compositor@1.create_surface(new id wl_surface@0)'])))
 refuses('protocol giant number typed',lambda:Trace(raw(['-> wl_compositor@'+('9'*5000)+'.create_surface(new id wl_surface@42)'])))
 yes('stable same snapshot',lambda:equal(same(b,copy.deepcopy(b)),True))
 for key in ['identity','wire','native','nativeRole','marker']:
  changed=copy.deepcopy(b);changed[key]['testChanged']=True
  yes('changed '+key+' capture rejected',lambda changed=changed:equal(same(b,changed),False))
 p={**q,'role':'P','instance':2,'surfaceId':60,'transientSurfaceId':42,'windowWidth':100,'windowHeight':60,'actionBoundsAvailable':True,'popupActionEnabled':True,'popupActionVisible':True,'actionWindowX':0,'actionWindowY':16,'actionWidth':100,'actionHeight':24,'popupMarkerBoundsAvailable':True,'popupMarkerWindowX':4,'popupMarkerWindowY':4,'popupMarkerWidth':8,'popupMarkerHeight':8}
 pl=lines+['-> wl_compositor@1.create_surface(new id wl_surface@60)','-> xdg_wm_base@2.get_xdg_surface(new id xdg_surface@61, wl_surface@60)','-> xdg_surface@61.get_popup(new id xdg_popup@62, xdg_surface@43, xdg_positioner@63)','-> xdg_popup@62.grab(wl_seat@3, 8)','xdg_popup@62.configure(10, 20, 100, 60)','xdg_surface@61.configure(9)','-> xdg_surface@61.set_window_geometry(0, 0, 100, 60)','-> xdg_surface@61.ack_configure(9)','-> wl_surface@60.attach(wl_buffer@64, 0, 0)','-> wl_surface@60.commit()']
 res=lambda sid:{'id':sid,'pid':100,'uid':1000}
 pn={'viewAddress':'0xabd','surface':res(60),'t1Root':res(42),'position':[110,120],'size':[100,60],'visible':True,'grabMember':True,'rootGrabMember':True}
 ps={'schema':1,'pid':200,'grabPresent':True,'grabKeyboard':True,'grabPointer':True,'keyboardFocus':res(60),'pointerFocus':res(60),'popups':[pn]}
 def popup(qq=p,ss=ps,rr=None):return join_popup([qq],raw(pl) if rr is None else rr,ss,parent=b,pid=100,started=300,uid=1000,compositor_pid=200)
 pb=popup();yes('popup actual raw parent native T1 root join',lambda:equal(pb['wire']['parentXdgSurfaceId'],43))
 yes('popup measured magenta point',lambda:equal(pb['marker']['global'],[118,128]))
 yes('popup measured QAction center',lambda:equal(pb['action']['point'],[160,148]))
 yes('popup queuedcommit never presentation',lambda:equal(pb['wire']['presentationProved'],False))
 for key in ['actionBoundsAvailable','popupActionEnabled','popupActionVisible','popupMarkerBoundsAvailable']:
  for v in [False,1]:refuses(key+' unavailable/alias '+str(v),lambda key=key,v=v:popup(qq={**p,key:v}))
 refuses('action entire rectangle bounds',lambda:popup(qq={**p,'actionWidth':101}))
 refuses('foreign native root',lambda:popup(ss={**ps,'popups':[{**pn,'t1Root':res(41)}]}))
 refuses('foreign popup UID',lambda:popup(ss={**ps,'popups':[{**pn,'surface':{**res(60),'uid':0}}]}))
 refuses('foreign raw immediateparent',lambda:popup(rr=raw([x.replace('xdg_surface@43, xdg_positioner','xdg_surface@99, xdg_positioner') for x in pl])))
 refuses('duplicate nativepopup',lambda:popup(ss={**ps,'popups':[pn,pn]}))
 refuses('malformed foreign popup never filtered',lambda:popup(ss={**ps,'popups':[pn,{**pn,'viewAddress':'0xabe','surface':{'id':True,'pid':101,'uid':1000}}]}))
 refuses('focus resource bool alias',lambda:popup(ss={**ps,'keyboardFocus':{'id':True,'pid':100,'uid':1000}}))
 yes('retired raw parent does not bind popup',lambda:equal(popup(rr=raw(pl+['-> xdg_toplevel@44.destroy()'])),None))
 refuses('same-ID replacement parent epoch refuses',lambda:popup(rr=raw(pl+['-> wl_surface@42.destroy()']+lines)))
 yes('no popup observer match readiness',lambda:equal(popup(ss={**ps,'popups':[]}),None))
 report['passed']=True
except BaseException as e:report['error']=repr(e);report['traceback']=traceback.format_exc()
finally:
 (OUT/'report.json').write_text(json.dumps(report,indent=2)+'\n');print(json.dumps({'passed':report['passed'],'checks':len(checks),'report':str(OUT/'report.json'),'error':report.get('error')}))
if not report['passed']:sys.exit(1)
