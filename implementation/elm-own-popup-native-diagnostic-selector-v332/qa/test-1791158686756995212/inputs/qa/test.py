"""Actual strict stamp boundaries plus inert source import; no GUI."""
import json,pathlib,sys,time,copy,resource
ROOT=pathlib.Path(__file__).resolve().parents[1];sys.path.insert(0,str(ROOT/'qa'))
import stamp
from preflight import verify,sha,load,checked_guard
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
 sys.path.insert(0,str(ROOT/'qa/helpers'));import target,protocol
 binding={'lifetime':'1','session':'2','frontend':'3'}
 transcript=b'[1.000] -> wl_compositor@1.create_surface(new id wl_surface@20)\n[1.001] -> xdg_wm_base@2.get_xdg_surface(new id xdg_surface@21, wl_surface@20)\n[1.002] -> xdg_surface@21.get_toplevel(new id xdg_toplevel@22)\n[1.003] -> xdg_toplevel@22.set_title("ELM-GTK4-A-100")\n[1.004] -> xdg_surface@21.set_window_geometry(0, 0, 320, 180)\n[1.005] xdg_surface@21.configure(11)\n[1.006] -> xdg_surface@21.ack_configure(11)\n[1.007] -> wl_surface@20.attach(wl_buffer@23, 0, 0)\n[1.008] -> wl_surface@20.commit()\n'
 wire=protocol.Trace(transcript).role(role='A',pid=100,surface_id=20)
 bound={'identity':{'role':'A','instance':1,'mapGeneration':1,'surfaceId':20},'gtk':{'pid':100},'native':{'pid':100,'title':'ELM-GTK4-A-100','address':'0x10','at':[10,20],'size':[320,180],'xwayland':False},'wire':wire}
 snapshot={'binding':binding,'windows':[{'label':'ELM-GTK4-A-100','incarnation':'5','application':'gtk','minimized':False}]}
 facts={'binding':binding,'facts':{'windows':[{'incarnation':'5','application':'gtk','minimized':False,'geometry':[10,20,320,180],'owner':None}]}}
 selected=target.join_target(bound,snapshot,facts,pid=100,binding=binding)
 check('actual-Trace-configure-ACK-buffer-and-native-incarnation-join',lambda:selected['incarnation']=='5' and selected['wire']['bufferId']==23)
 def target_deny(change):
  x,y,z=copy.deepcopy(bound),copy.deepcopy(snapshot),copy.deepcopy(facts);change(x,y,z)
  try:target.join_target(x,y,z,pid=100,binding=binding)
  except ValueError:return True
  return False
 for name,change in [('resource',lambda x,y,z:x['identity'].update(surfaceId=24)),('ACK',lambda x,y,z:x['wire']['ack'].update(serial=12)),('native-PID',lambda x,y,z:x['native'].update(pid=101)),('ambiguous-label',lambda x,y,z:y['windows'].append(copy.deepcopy(y['windows'][0]))),('incarnation',lambda x,y,z:z['facts']['windows'][0].update(incarnation='6')),('geometry',lambda x,y,z:z['facts']['windows'][0].update(geometry=[10,20,319,180])),('binding',lambda x,y,z:y['binding'].update(frontend='4'))]:
  check('actual-target-refuse-'+name,lambda change=change:target_deny(change))
 def retired_wire():
  raw=transcript+b'[1.009] -> wl_surface@20.destroy()\n[1.010] -> wl_compositor@1.create_surface(new id wl_surface@20)\n'
  try:protocol.Trace(raw).role(role='A',pid=100,surface_id=20)
  except ValueError:return True
  return False
 check('actual-Trace-resource-reuse-cannot-retarget-old-ACK',retired_wire)
 guard,guard_files=checked_guard();check('exact-held330-inert-source-import',lambda:callable(guard.verify_tuple) and callable(guard.verify_process));report['guardFiles']=guard_files
 host,core,observer,fixture,hb,build,files=verify();report['sourceFiles']=files;report['coherentHost']=str(hb);report['compiledAssets']=str(build/'inputs/assets');report['actualOwnSourcesVerified']=len(files)
 native=load('inert_actual325_native',ROOT/'qa/native.py');check('inert-native-import',lambda:True)
 # Polling a live host must not parse an incomplete trailing write as a receipt.
 logfile=out/'partial.log';logfile.write_text('backend-frame: {\"kind\":\"attached\"}\nbackend-frame: {bad')
 check('incomplete-live-tail-unqualified',lambda:native.packets(logfile,'backend-frame: ')==[{'kind':'attached'}])
 logfile.write_text('backend-frame: {bad}\n')
 def bad_complete():
  try:native.packets(logfile,'backend-frame: ')
  except ValueError:return True
  return False
 check('complete-malformed-frame-refused',bad_complete)
 # Execute the actual final-predicate budget guard with a controlled clock.
 real_clock=native.time.monotonic;clock=[0.0];native.time.monotonic=lambda:clock[0]
 class Session:
  def guard(self):pass
 try:
  check('actual-wait-positive-within-parent-budget',lambda:native.wait(Session(),lambda:True,1.0) is True)
  def late():clock[0]=2.0;return True
  def late_refused():
   try:native.wait(Session(),late,1.0)
   except ValueError:return True
   return False
  check('actual-wait-rejects-late-positive',late_refused)
 finally:native.time.monotonic=real_clock
 # The metadata decoder must parse exactly the same once-read bytes it hashes.
 import preflight,hashlib
 metadata=out/'metadata.json';metadata.write_bytes(b'{\"safe\":true}')
 check('single-read-hash-bound-metadata',lambda:preflight.packet(metadata,hashlib.sha256(metadata.read_bytes()).hexdigest())=={'safe':True})
 def wrong_digest():
  try:preflight.packet(metadata,'0'*64)
  except ValueError:return True
  return False
 check('metadata-wrong-hash-refused',wrong_digest)
 report['passed']=True
except BaseException as e:report['error']=repr(e)
report['inputs']={str(p.relative_to(ROOT)):sha(p) for p in (ROOT/'qa').glob('*.py')}
for rel in report['inputs']:
 p=out/'inputs'/rel;p.parent.mkdir(parents=True,exist_ok=True);p.write_bytes((ROOT/rel).read_bytes())
(out/'report.json').write_text(json.dumps(report,indent=2)+'\n');print(out/'report.json');raise SystemExit(not report['passed'])
