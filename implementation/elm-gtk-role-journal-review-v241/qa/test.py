#!/usr/bin/python3
import copy,hashlib,importlib.util,json,pathlib,subprocess,sys,tempfile,time,types
ROOT=pathlib.Path(__file__).resolve().parents[1]
def sha(p):return hashlib.sha256(p.read_bytes()).hexdigest()
def load(name,path):
 spec=importlib.util.spec_from_file_location(name,path);m=importlib.util.module_from_spec(spec);sys.modules[name]=m;spec.loader.exec_module(m);return m

def main():
 out=ROOT/'qa'/f'characterization-{time.time_ns()}';out.mkdir(mode=0o700)
 consumer=load('journal',ROOT/'inputs/journal.py');actor=load('actor',ROOT/'inputs/actor.py')
 report={'passed':False,'nativeAcceptance':False,'scope':'actual snapshot decoder/Actor.close executed with synthetic journal/mock owned process; no GUI or native delivery','sourceInputs':{str(p.relative_to(ROOT)):sha(p) for p in sorted((ROOT/'inputs').glob('*'))},'cases':[]}
 try:
  c=out/'gdk-enums.c';c.write_text('#include <gdk/gdk.h>\n#include <stdio.h>\nint main(void){printf("[%d,%d,%d,%d]\\n",GDK_BUTTON_PRESS,GDK_BUTTON_RELEASE,GDK_KEY_PRESS,GDK_KEY_RELEASE);return 0;}\n')
  flags=subprocess.check_output(['/usr/bin/pkg-config','--cflags','--libs','gtk4'],text=True).split();p=subprocess.run(['/usr/bin/cc','-std=c11','-Wall','-Wextra','-Werror',str(c),'-o',str(out/'gdk-enums'),*flags],capture_output=True);(out/'compile.stderr').write_bytes(p.stderr);assert p.returncode==0,p.stderr
  enums=json.loads(subprocess.check_output([str(out/'gdk-enums')],text=True));report['actualGdkEnums']=enums
  report['gdkHeader']={'path':'/usr/include/gtk-4.0/gdk/gdkevents.h','sha256':sha(pathlib.Path('/usr/include/gtk-4.0/gdk/gdkevents.h'))}
  def base(seq,event='button-press'):
   return dict(schema=1,pid=1234,processStarted=77,sequence=seq,monotonicUs=100+seq,requestSequence=1,event=event,profile='independent-groups',role='A',instance=1,mapGeneration=1,surfaceId=19,sourceSurfaceId=19,button=1,rawButton=1,rawEventAvailable=True,rawEventType=enums[0] if event=='button-press' else enums[1],rawEventTime=1000+seq,rawModifiers=0,hasSurfacePosition=True,surfaceX=4,surfaceY=8)
  def encode(rows):return ('\n'.join(json.dumps(r) for r in rows)+'\n').encode()
  def decode(rows):return consumer.parse(encode(rows),pid=1234,started='77')
  def pointer(rows):return consumer.full_pointer_interval(decode(rows),0,role='A',instance=1,surface_id=19,expected_surface=[4,8])
  def classify(name,fn,expected,witness=None):
   try:fn();result='accepted'
   except consumer.Refused as e:result='typed-refused';error=str(e)
   except Exception as e:result='other-error';error=repr(e)
   row={'name':name,'classification':result,'expectedCharacterization':expected,'matched':result==expected}
   if result!='accepted':row['error']=error
   if witness is not None:(out/(name+'.json')).write_text(json.dumps(witness,indent=2)+'\n');row['witness']=str(out/(name+'.json'))
   report['cases'].append(row);assert row['matched'],row
  rows=[base(1),base(2,'button-release')]
  classify('valid-owned-pointer',lambda:pointer(rows),'accepted',rows)
  for name,field,value in [('stale-map-generation','mapGeneration',2),('float-source-surface','sourceSurfaceId',19.0),('missing-raw-event','rawEventAvailable',False),('wrong-raw-kind','rawEventType',enums[2]),('float-raw-time','rawEventTime',1.5),('negative-raw-time','rawEventTime',-1),('absent-profile','profile',None),('unknown-profile','profile','unknown'),('mixed-profile','profile','default-group')]:
   changed=copy.deepcopy(rows);changed[1][field]=value
   if name=='absent-profile':changed[1].pop(field)
   classify(name,lambda r=changed:pointer(r),'accepted',changed)
  changed=copy.deepcopy(rows);changed[1].update(sequence=3,monotonicUs=103);classify('hidden-row-gap',lambda:pointer(changed),'accepted',changed)
  changed=[dict(base(2)),dict(base(3,'button-release'))];classify('missing-first-row',lambda:pointer(changed),'accepted',changed)
  changed=[dict(r,surfaceId=1,sourceSurfaceId=True) for r in rows];classify('bool-resource-equality',lambda:consumer.full_pointer_interval(decode(changed),0,role='A',instance=1,surface_id=1,expected_surface=[4,8]),'accepted',changed)
  for name,field,value in [('foreign-pid','pid',1235),('foreign-start','processStarted',78),('foreign-role','role','C'),('foreign-instance','instance',2),('button-evdev-domain','button',272),('button-bool','button',True),('nonfinite-checked-coordinate','surfaceX',float('inf'))]:
   changed=copy.deepcopy(rows);changed[0][field]=value;classify(name,lambda r=changed:pointer(r),'typed-refused',changed)
  changed=copy.deepcopy(rows);changed[0]['landmarkNativeX']=float('inf');raw=encode(changed).replace(b'Infinity',b'1e400');classify('nonfinite-unchecked-metadata',lambda:consumer.parse(raw,pid=1234,started='77'),'accepted',{'raw':raw.decode()})
  classify('duplicate-json-key',lambda:consumer.parse(encode(rows).replace(b'"schema": 1',b'"schema":1,"schema":1',1),pid=1234,started='77'),'typed-refused')
  classify('malformed-json-typed-gap',lambda:consumer.parse(b'{broken}\n',pid=1234,started='77'),'other-error')
  classify('invalid-utf8-typed-gap',lambda:consumer.parse(b'\xff\n',pid=1234,started='77'),'other-error')
  for profile in ['independent-groups','default-group']:
   changed=[dict(r,profile=profile) for r in rows];classify('valid-profile-'+profile,lambda r=changed:pointer(r),'accepted',changed)
  extra=base(3);extra['role']='C';classify('full-pointer-extra-foreign-role',lambda:pointer(rows+[extra]),'typed-refused',rows+[extra])
  keys=[]
  for i,event in enumerate(['key-press','key-release'],1):
   r=base(i,event);r.update(keyval=65470,rawKeyval=65470,keycode=67,rawKeycode=67,modifiers=0,rawModifiers=0,rawEventType=enums[2+i-1]);keys.append(r)
  def key(values):return consumer.full_key_interval(decode(values),0,role='A',instance=1,surface_id=19,keyval=65470,keycode=67)
  classify('valid-owned-key',lambda:key(keys),'accepted',keys)
  changed=copy.deepcopy(keys);changed[1]['rawEventType']=enums[0];classify('key-wrong-raw-kind',lambda:key(changed),'accepted',changed)
  changed=copy.deepcopy(keys);changed[1]['keycode']=59;classify('key-evdev-domain-mismatch',lambda:key(changed),'typed-refused',changed)
  classify('blocked-pointer-full-key-leak',lambda:consumer.blocked_interval(decode(keys),0),'accepted',keys)
  inspect=dict(base(3,'inspect'),instance=99,mapGeneration=99,surfaceId=99,draftUTF8='ELM-ROLE-DRAFT',draftBytes=14)
  classify('draft-stale-role-recreation',lambda:consumer.stable_drafts(decode([inspect]),0,{'A':'ELM-ROLE-DRAFT'}),'accepted',[inspect])
  # Execute actual Actor.close with mock ownership/process primitives and real bounded logs.
  def close_with(raw):
   directory=out/('actor-'+str(len(report['cases'])));directory.mkdir();a=actor.Actor.__new__(actor.Actor);a.directory=directory;a.stdout=directory/'journal.jsonl';a.stderr=directory/'wayland.log';a.stdout.write_bytes(raw);a.stderr.write_bytes(b'');a.record={};a.rows=[];a.pid=1234;a.started='77';a.session=types.SimpleNamespace(guard=lambda:None)
   class Input:
    closed=False
    def close(self):self.closed=True
   class Process:
    returncode=0;stdin=Input()
    def wait(self,timeout):return 0
    def poll(self):return 0
   a.process=Process();a.send=lambda *args:None;a.abort=lambda:None;a.close(time.monotonic()+2);assert a.record['normalExit']
  terminal=dict(base(1,'normalexit'));terminal.pop('role');terminal.pop('instance');terminal.pop('mapGeneration');terminal.pop('surfaceId')
  classify('normal-terminal-close',lambda:close_with(encode([terminal])),'accepted',[terminal])
  classify('normalexit-plus-partial-malformed-tail',lambda:close_with(encode([terminal])+b'{broken'),'accepted',{'raw':(encode([terminal])+b'{broken').decode()})
  after=dict(base(2,'inspect'));classify('normalexit-followed-by-live-record',lambda:close_with(encode([terminal,after])),'accepted',[terminal,after])
  report.update(passed=True,unsafeAccepted=[r['name'] for r in report['cases'] if r['classification']=='accepted' and not r['name'].startswith(('valid-','normal-terminal'))],typedErrorGaps=[r['name'] for r in report['cases'] if r['classification']=='other-error'])
 except Exception as e:report['error']=repr(e)
 (out/'report.json').write_text(json.dumps(report,indent=2)+'\n');print(json.dumps({'report':str(out/'report.json'),'passed':report['passed'],'cases':len(report['cases']),'error':report.get('error')}));return 0 if report['passed'] else 1
if __name__=='__main__':raise SystemExit(main())
