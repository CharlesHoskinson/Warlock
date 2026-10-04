"""Actual popup transform/samples, wire modifier order, and shell keyboard selection."""
import ast,copy,hashlib,importlib.util,json,pathlib,resource,sys,time
from types import SimpleNamespace
ROOT=pathlib.Path(__file__).resolve().parents[1];sys.path.insert(0,str(ROOT/'qa/helpers'));sys.path.insert(0,str(ROOT/'qa'))
assert resource.getrlimit(resource.RLIMIT_CORE)==(1,1)
import popup,keyboard,shell
out=ROOT/'qa'/('helper-test-'+str(time.time_ns()));out.mkdir();(out/'inputs').mkdir();report={'passed':False,'nativeAcceptance':False,'checks':[]}
for path in [pathlib.Path(__file__),ROOT/'qa/popup.py',ROOT/'qa/keyboard.py',ROOT/'qa/shell.py']:(out/'inputs'/path.name).write_bytes(path.read_bytes())
def check(name,fn,refuse=False):
 try:fn();assert not refuse,name
 except (popup.Refused,keyboard.Refused,shell.Refused):assert refuse,name
 report['checks'].append({'name':name,'passed':True})
def assertion(value):assert value
try:
 rgb=bytearray(800*600*3)
 for y in range(99,102):
  for x in range(99,102):rgb[(y*800+x)*3:(y*800+x)*3+3]=bytes([255,0,255])
 check('actual-nine-magenta-samples',lambda:assertion(popup.samples(bytes(rgb),[100,100],[255,0,255])['passed']))
 rgb[(99*800+99)*3]=0;check('one-corner-mismatch-not-pass',lambda:assertion(not popup.samples(bytes(rgb),[100,100],[255,0,255])['passed']))
 for point in [[0,0],[799,599],[True,100],[100.0,100]]:check('reject-sample-bound-'+str(point),lambda p=point:popup.samples(bytes(rgb),p,[255,0,255]),True)
 def row(method,args,direction='event',iface='wl_keyboard'):return dict(iface=iface,id=8,direction=direction,method=method,args=args)
 prefix=[row('enter','1, wl_surface@42, array[0]'),row('modifiers','2, 0, 0, 0, 0')]
 before_key=prefix+[row('modifiers','3, 1, 0, 0, 0'),row('key','4, 100, 42, 1'),row('modifiers','5, 0, 0, 0, 0'),row('key','6, 101, 42, 0')]
 after_key=prefix+[row('key','4, 100, 42, 1'),row('modifiers','3, 1, 0, 0, 0'),row('key','6, 101, 42, 0'),row('modifiers','5, 0, 0, 0, 0')]
 def wire(calls):return keyboard.shift_pair(SimpleNamespace(calls=calls),2,surface_id=42,xkb_shift_mask=1,gdk_shift_mask=1)
 check('actual-modifiers-before-key-order',lambda:assertion([r['gdkModifiers'] for r in wire(before_key)]==[1,0]))
 check('actual-modifiers-after-key-order-no-assumed-release',lambda:assertion([r['gdkModifiers'] for r in wire(after_key)]==[0,1]))
 for name,altered in [('wrong-surface',[row('enter','1, wl_surface@43, array[0]')]+before_key[1:]),('unrelated-key',before_key+[row('key','7, 102, 30, 1')]),('duplicate-key',before_key+[before_key[-1]]),('nonshift-mod',prefix+[row('modifiers','3, 4, 0, 0, 0')]+before_key[3:]),('missing-key',before_key[:-1])]:check('reject-'+name,lambda c=altered:wire(c),True)
 # Execute the actual invoke method; fake only transport/observed DOM, never native claims.
 request={'protocolVersion':3,'kind':'window-effect','effectProtocol':1,'binding':{'lifetime':'1','session':'2','frontend':'3'},'intent':{'request':'4','generation':'5','incarnation':'6','operation':'minimize','context':{'lifetime':'1','epoch':'7','output':'8','revision':'9'}}};receipt=dict(copy.deepcopy(request),kind='effect-outcome',status='Committed')
 client=shell.Shell.__new__(shell.Shell);sent=[];actions=[{'label':'Restore','enabled':False},{'label':'Minimize','enabled':True},{'label':'Move','enabled':False},{'label':'Size','enabled':False},{'label':'Maximize','enabled':True}]
 client.journal=lambda:[request] if sent else [];client.outcomes=lambda:[receipt];client.pointer=lambda *a:None;client.group=lambda:{};client.selection=lambda title:{'incarnation':'6'};client.menu=lambda:{'body':{'menu':{'incarnation':'6','actions':actions}}};client.wait=lambda fn,deadline:fn();client.keys=lambda payload,deadline:sent.append(payload)
 check('Home-on-first-enabled-Minimize-needs-zero-Down',lambda:assertion(client.invoke('title','6','minimize',time.monotonic()+6)['request']==request and sent==['key 102 1\nkey 102 0\nkey 28 1\nkey 28 0\n']))
 sent.clear();request['effectProtocol']=2;request['intent']['operation']='maximize';receipt.update(effectProtocol=2);receipt['intent']['operation']='maximize';check('Maximize-skips-three-disabled-items-one-Down',lambda:assertion(client.invoke('title','6','maximize',time.monotonic()+6)['request']==request and sent[0].count('key 108 1\n')==1))
 report['passed']=True
except BaseException as error:report['error']=repr(error)
report['sourceSHA256']={str(p.relative_to(ROOT)):hashlib.sha256(p.read_bytes()).hexdigest() for p in [ROOT/'qa/popup.py',ROOT/'qa/keyboard.py',ROOT/'qa/shell.py',pathlib.Path(__file__)]};(out/'report.json').write_text(json.dumps(report,indent=2)+'\n');print(json.dumps({'report':str(out/'report.json'),'passed':report['passed'],'checks':len(report['checks']),'error':report.get('error')}));raise SystemExit(0 if report['passed'] else 1)
