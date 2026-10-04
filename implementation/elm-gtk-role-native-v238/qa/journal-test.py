import copy,hashlib,json,resource,sys,time
from pathlib import Path
sys.path.insert(0,'/home/hoskinson/window-integration-qa')
from qa_launch import require_qa_scope
require_qa_scope();assert resource.getrlimit(resource.RLIMIT_CORE)==(1,1)
from journal import parse,full_pointer_interval,full_key_interval,blocked_interval,stable_drafts,Refused
from actor import command
OUT=Path(__file__).parent/('journal-'+str(time.time_ns()));OUT.mkdir()
types={"button-press":2,"button-release":3,"key-press":4,"key-release":5}
checks=[]
def check(name,fn,reject=False):
 try:fn();passed=not reject
 except Refused:passed=reject
 checks.append({'name':name,'passed':passed});assert passed,name

def base(seq,event='button-press'):
 return dict(schema=1,pid=1234,processStarted=77,sequence=seq,monotonicUs=seq,requestSequence=1,event=event,role='A',instance=1,mapGeneration=1,profile="independent-groups",surfaceId=19,sourceSurfaceId=19,rawEventType=types[event] if event in types else 0,rawEventTime=100,rawModifiers=0,button=1,rawButton=1,rawEventAvailable=True,hasSurfacePosition=True,surfaceX=4,surfaceY=8)
def encoded(rows):return ('\n'.join(json.dumps(r) for r in rows)+'\n').encode()
rows=[base(1),base(2,'button-release')]
def decode(r):return parse(encoded(r),pid=1234,started='77')
def pointer(r):return full_pointer_interval(decode(r),0,role='A',instance=1,map_generation=1,surface_id=19,event_types=types,expected_surface=[4,8])
report={'passed':False,'nativeAcceptance':False,'syntheticJournalBoundaryOnly':True,'checks':checks}
try:
 check('full-owned-GDK-pointer-pair',lambda:pointer(rows))
 for name,field,value in [('foreign-pid','pid',1235),('foreign-start','processStarted',78),('bool-pid','pid',True),('bool-schema','schema',True),('foreign-resource','sourceSurfaceId',20),('foreign-role','role','C'),('foreign-instance','instance',2),('bool-button','button',True),('float-button','rawButton',1.0),('float-resource','sourceSurfaceId',19.0),('gap-sequence','sequence',9),('wrong-profile','profile','default-group'),('raw-event-unavailable','rawEventAvailable',False),('wrong-GDK-type','rawEventType',4),('bool-rawtime','rawEventTime',True),('Linux-button-not-GDK','button',272),('wrong-position','surfaceX',5),('huge-positive','surfaceX',10**400),('huge-negative','surfaceY',-10**400),('nonfinite','surfaceX',float('nan'))]:
  changed=copy.deepcopy(rows);changed[0][field]=value;check(name,lambda c=changed:pointer(c),True)
 for name,extra in [('extra-other-role',dict(base(3),role='C')),('extra-other-button',dict(base(3),button=3)),('duplicate-pair',base(3))]:check(name,lambda e=extra:pointer(rows+[e]),True)
 check('empty-blocked-interval',lambda:blocked_interval(decode(rows),2))
 check('blocked-delivery-refused',lambda:blocked_interval(decode(rows),0),True)
 check('release-before-press',lambda:pointer([dict(base(1),event='button-release'),base(2)]),True)
 check('changed-prefix',lambda:parse(encoded(rows),pid=1234,started='77',previous=[dict(rows[0],surfaceId=99)]),True)
 check('5000-digit-integer-typed-refusal',lambda:parse(b'{"n":'+b'1'*5000+b'}\n',pid=1234,started='77'),True)
 check('duplicate-JSON-key',lambda:parse(encoded(rows).replace(b'"schema": 1',b'"schema":1,"schema":1',1),pid=1234,started='77'),True)
 check('partial-tail-not-an-event',lambda:parse(encoded(rows)+b'{"schema":',pid=1234,started='77'))
 keys=[]
 for i,event in enumerate(['key-press','key-release'],1):
  r=base(i,event);r.update(keyval=65470,rawKeyval=65470,keycode=67,rawKeycode=67,modifiers=0,rawModifiers=0);keys.append(r)
 def key(r):return full_key_interval(decode(r),0,role='A',instance=1,map_generation=1,surface_id=19,event_types=types,keyval=65470,keycode=67)
 check('full-owned-GDK-key-pair',lambda:key(keys))
 for name,field,value in [('raw-key-mismatch','rawKeycode',66),('bool-key','keyval',True),('foreign-key-role','role','B'),('missing-raw-key','rawEventAvailable',False)]:
  changed=copy.deepcopy(keys);changed[0][field]=value;check(name,lambda c=changed:key(c),True)
 check('extra-other-role-key',lambda:key(keys+[dict(keys[0],sequence=3,monotonicUs=3,role='C')]),True)
 inspect=dict(base(3,'inspect'),draftUTF8='ELM-ROLE-DRAFT',draftBytes=14)
 check('actual-postinterval-draft',lambda:stable_drafts(decode(rows+[inspect]),2,{'A':'ELM-ROLE-DRAFT'},{'A':{'instance':1,'mapGeneration':1,'surfaceId':19}}))
 check('missing-postinterval-draft',lambda:stable_drafts(decode(rows),2,{'A':'ELM-ROLE-DRAFT'},{'A':{'instance':1,'mapGeneration':1,'surfaceId':19}}),True)
 check('changed-postinterval-draft',lambda:stable_drafts(decode(rows+[dict(inspect,draftUTF8='changed')]),2,{'A':'ELM-ROLE-DRAFT'},{'A':{'instance':1,'mapGeneration':1,'surfaceId':19}}),True)
 for op in ['create-owners','open-modal','close-modal','close-owner','open-nested','close-nested','open-popover','close-popover','inspect','quit']:check('closed-command-'+op,lambda o=op:command(1,o))
 check('targeted-C-command',lambda:command(1,'maximize','C'))
 check('command-injection',lambda:command(1,'inspect\nquit'),True)
 check('unknown-role-command',lambda:command(1,'maximize','B'),True)
 report['passed']=True
finally:
 report['inputs']={str(p):hashlib.sha256(p.read_bytes()).hexdigest() for p in [Path(__file__),Path(__file__).with_name('journal.py'),Path(__file__).with_name('actor.py')]}
 (OUT/'report.json').write_text(json.dumps(report,indent=2)+'\n');print(OUT/'report.json')
