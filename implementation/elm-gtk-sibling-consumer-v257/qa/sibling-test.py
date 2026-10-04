"""Strict sibling journal/command boundaries; synthetic evidence, no GTK display."""
import copy,hashlib,json,resource,time
from pathlib import Path
assert resource.getrlimit(resource.RLIMIT_CORE)==(1,1)
from journal import parse,gtk_parent_relation,Refused
from actor import command
ROOT=Path(__file__).parent;out=ROOT/('sibling-'+str(time.time_ns()));out.mkdir()
report={'passed':False,'nativeAcceptance':False,'syntheticJournalOnly':True,'checks':[]}
child={'instance':5,'mapGeneration':1,'surfaceId':55};parent={'instance':2,'mapGeneration':1,'surfaceId':20}
def base(seq,event,request=1,**fields):
 return dict(schema=1,pid=1234,processStarted=77,sequence=seq,monotonicUs=seq,requestSequence=request,event=event,profile='independent-groups',**fields)
def role(seq,event,name,identity,request=1):
 return base(seq,event,request,role=name,**identity,mapped=True,transientSurfaceId=20 if name=='E' else 0,requestedModal=True)
rows=[base(1,'request',command='reparent-sibling',requestedRole='B'),role(2,'requested-parent','E',child),base(3,'request',2,command='inspect'),role(4,'inspect','B',parent,2),role(5,'inspect','E',child,2)]
def decode(values):return parse(('\n'.join(json.dumps(r) for r in values)+'\n').encode(),pid=1234,started='77')
def check(name,fn,reject=False):
 try:fn();ok=not reject
 except Refused:ok=reject
 report['checks'].append({'name':name,'passed':ok});assert ok,name
def relation(values):return gtk_parent_relation(decode(values),0,request_sequence=1,parent_role='B',child_identity=child,parent_identity=parent)
try:
 check('exact-reparent-B-with-live-inspections',lambda:relation(rows))
 check('toolkit-evidence-never-native-parent-proof',lambda:None if relation(rows)['nativeParentProved'] is False else (_ for _ in ()).throw(AssertionError()))
 for name,index,field,value in [('wrong-command',0,'command','open-sibling'),('wrong-parent-target',0,'requestedRole','A'),('wrong-child-intent',1,'role','D'),('wrong-parent-resource',1,'transientSurfaceId',21),('bool-parent-resource',1,'transientSurfaceId',True),('nonmodal-intent',1,'requestedModal',False),('stale-parent-instance',3,'instance',99),('stale-child-map',4,'mapGeneration',2),('wrong-final-parent',4,'transientSurfaceId',21),('unmapped-final-child',4,'mapped',False),('unknown-role',4,'role','F')]:
  changed=copy.deepcopy(rows);changed[index][field]=value;check(name,lambda c=changed:relation(c),True)
 for name,index in [('missing-parent-inspection',3),('missing-child-inspection',4),('missing-intent',1),('missing-request',0)]:
  changed=copy.deepcopy(rows);changed.pop(index)
  for n,r in enumerate(changed,1):r['sequence']=n;r['monotonicUs']=n
  check(name,lambda c=changed:relation(c),True)
 for name,event,target,identity in [('late-child-retire','destroy-request','E',child),('late-parent-unmap','unmap','B',parent),('late-child-replacement','inspect','E',dict(child,instance=6))]:
  changed=copy.deepcopy(rows)+[role(6,event,target,identity,2)];check(name,lambda c=changed:relation(c),True)
 duplicate=copy.deepcopy(rows);duplicate.insert(2,role(3,'requested-parent','E',child))
 for n,r in enumerate(duplicate,1):r['sequence']=n;r['monotonicUs']=n
 check('duplicate-parent-intent',lambda:relation(duplicate),True)
 check('aliased-parent-child-resource',lambda:gtk_parent_relation(decode(rows),0,request_sequence=1,parent_role='B',child_identity=child,parent_identity=dict(parent,surfaceId=55)),True)
 for op,target in [('open-sibling',None),('close-sibling',None),('reparent-sibling','A'),('reparent-sibling','B')]:check('closed-'+op+'-'+str(target),lambda o=op,t=target:command(1,o,t))
 for target in ['C','D','E','P',None,'AB',True]:check('reject-parent-'+str(target),lambda t=target:command(1,'reparent-sibling',t),True)
 check('role-on-plain-sibling-command',lambda:command(1,'open-sibling','A'),True)
 report['passed']=True
finally:
 report['inputs']={str(p):hashlib.sha256(p.read_bytes()).hexdigest() for p in [Path(__file__),ROOT/'journal.py',ROOT/'actor.py']}
 (out/'report.json').write_text(json.dumps(report,indent=2)+'\n');print(out/'report.json')
