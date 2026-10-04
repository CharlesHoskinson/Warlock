#!/usr/bin/python3
import copy,hashlib,json,pathlib,resource,stat,sys,time
ROOT=pathlib.Path(__file__).resolve().parents[1]
SOURCE=ROOT.parent/'elm-gtk-sibling-consumer-v257'
sys.path.insert(0,str(ROOT/'inputs'))
from journal import parse,gtk_parent_relation,Refused
from actor import command
assert resource.getrlimit(resource.RLIMIT_CORE)==(1,1)
def sha(p):return hashlib.sha256(p.read_bytes()).hexdigest()
def rows_for(parent='B',profile='independent-groups'):
 child={'instance':5,'mapGeneration':2,'surfaceId':55};owner={'instance':2,'mapGeneration':3,'surfaceId':20}
 def row(sequence,event,request,**fields):return dict(schema=1,pid=1234,processStarted=77,sequence=sequence,monotonicUs=sequence,requestSequence=request,event=event,profile=profile,**fields)
 def role(sequence,event,name,identity,request):return row(sequence,event,request,role=name,mapped=True,transientSurfaceId=20 if name=='E' else 0,requestedModal=name=='E',**identity)
 rows=[row(1,'request',1,command='reparent-sibling',requestedRole=parent),role(2,'requested-parent','E',child,1),row(3,'request',2,command='inspect'),role(4,'inspect',parent,owner,2),role(5,'inspect','E',child,2)]
 return rows,child,owner
out=ROOT/'qa'/f'review-{time.time_ns()}';out.mkdir(mode=0o700)
r={'passed':False,'nativeAcceptance':False,'checks':[]}
def relation(rows,child,owner,parent='B',profile='independent-groups',**opts):
 raw=('\n'.join(json.dumps(row) for row in rows)+'\n').encode()
 parsed=parse(raw,pid=1234,started='77',profile=profile)
 return gtk_parent_relation(parsed,opts.get('baseline',0),request_sequence=opts.get('request_sequence',1),parent_role=parent,child_identity=child,parent_identity=owner)
def check(name,fn,reject=False):
 try:
  result=fn()
  if reject:raise AssertionError('unexpected acceptance: '+name)
  if isinstance(result,dict) and 'nativeParentProved' in result:assert result['nativeParentProved'] is False
 except Refused:
  if not reject:raise
 r['checks'].append({'name':name,'passed':True})
try:
 manifest=json.loads((SOURCE/'component-manifest.json').read_text());assert manifest['sourceHeld'] is True
 for name,row in manifest['files'].items():
  p=SOURCE/name;assert not p.is_symlink() and sha(p)==row['sha256'] and p.stat().st_size==row['size'] and stat.S_IMODE(p.stat().st_mode)==row['mode'],name
 for name,digest in manifest['externalFiles'].items():assert sha(pathlib.Path(name))==digest,name
 for name in ['journal.py','actor.py']:assert sha(ROOT/'inputs'/name)==sha(SOURCE/'qa'/name)
 for parent in ['A','B']:
  for profile in ['independent-groups','default-group']:
   rows,child,owner=rows_for(parent,profile);check('exact-'+parent+'-'+profile,lambda:relation(rows,child,owner,parent,profile))
 rows,child,owner=rows_for()
 mutations=[(0,'requestedRole','A'),(0,'command','open-sibling'),(0,'requestSequence',True),(1,'role','D'),(1,'mapped',False),(1,'requestedModal',1),(1,'transientSurfaceId',20.0),(1,'transientSurfaceId',True),(3,'instance',3),(3,'surfaceId',21),(3,'mapped',False),(4,'mapGeneration',3),(4,'surfaceId',56),(4,'mapped',False),(4,'requestedModal',False),(4,'transientSurfaceId',21),(4,'profile','default-group'),(4,'sequence',7),(4,'monotonicUs',0),(4,'processStarted',78),(4,'role','F')]
 for index,field,value in mutations:
  altered=copy.deepcopy(rows);altered[index][field]=value
  check(f'hostile-{index}-{field}-{value!r}',lambda a=altered:relation(a,child,owner),True)
 for event in ['unmap','destroy-request','local-destroy']:
  for role,identity in [('B',owner),('E',child)]:
   altered=copy.deepcopy(rows);altered.append(dict(altered[3 if role=='B' else 4],sequence=6,monotonicUs=6,event=event,mapped=False))
   check('latest-retired-'+role+'-'+event,lambda a=altered:relation(a,child,owner),True)
 for field,value in [('instance',6),('mapGeneration',4),('surfaceId',66),('transientSurfaceId',21),('requestedModal',False)]:
  altered=copy.deepcopy(rows);altered.append(dict(altered[4],sequence=6,monotonicUs=6,**{field:value}))
  check('latest-child-'+field,lambda a=altered:relation(a,child,owner),True)
 for target in [None,'C','D','E','P','AB',False]:check('closed-parent-'+str(target),lambda t=target:relation(rows,child,owner,t),True)
 for identity in [dict(owner,surfaceId=55),dict(owner,instance=5),dict(owner,mapGeneration=True),dict(owner,surfaceId=20.0),dict(owner,extra=1),{},None]:check('identity-bound-'+str(identity),lambda i=identity:relation(rows,child,i),True)
 for baseline in [True,-1,1.0,5]:check('baseline-'+str(baseline),lambda b=baseline:relation(rows,child,owner,baseline=b),True)
 for request in [True,0,1.0,2]:check('request-'+str(request),lambda q=request:relation(rows,child,owner,request_sequence=q),True)
 for index in [0,1,3,4]:
  altered=copy.deepcopy(rows);altered.pop(index)
  for sequence,row in enumerate(altered,1):row['sequence']=sequence;row['monotonicUs']=sequence
  check('missing-required-'+str(index),lambda a=altered:relation(a,child,owner),True)
 altered=copy.deepcopy(rows);altered.insert(2,dict(altered[1]))
 for sequence,row in enumerate(altered,1):row['sequence']=sequence;row['monotonicUs']=sequence
 check('duplicate-parent-intent',lambda:relation(altered,child,owner),True)
 for target in [None,'C','D','E','P','AB',True]:check('actor-closed-reparent-'+str(target),lambda t=target:command(1,'reparent-sibling',t),True)
 for target in ['A','B']:check('actor-canonical-reparent-'+target,lambda t=target:command(1,'reparent-sibling',t))
 for op in ['open-sibling','close-sibling']:check('actor-canonical-'+op,lambda o=op:command(1,o))
 for sequence in [0,-1,True,1.0,2**63]:check('actor-sequence-'+str(sequence),lambda q=sequence:command(q,'open-sibling'),True)
 origin=json.loads((SOURCE/'origin.json').read_text());parent=pathlib.Path(origin['parentManifest']).parent
 old=(parent/'qa/actor.py').read_text();new=(SOURCE/'qa/actor.py').read_text();assert old[old.index('class Actor:'):]==new[new.index('class Actor:'):]
 old=(parent/'qa/journal.py').read_text();new=(SOURCE/'qa/journal.py').read_text().split('def gtk_parent_relation(',1)[0];assert old.rstrip()==new.replace("('A','B','C','D','P','E')","('A','B','C','D','P')").rstrip()
 r.update(passed=True,verifiedHeldFiles=len(manifest['files']),sourceManifestSHA256=sha(SOURCE/'component-manifest.json'),unchangedActorLifecycle=True,unchangedDecoderExceptERole=True)
except BaseException as error:r['error']=repr(error)
(out/'report.json').write_text(json.dumps(r,indent=2)+'\n')
if r['passed']:
 files={str(p.relative_to(ROOT)):{'sha256':sha(p),'size':p.stat().st_size,'mode':stat.S_IMODE(p.stat().st_mode)} for p in sorted(ROOT.rglob('*')) if p.is_file() and p.name!='component-manifest.json'}
 (ROOT/'component-manifest.json').write_text(json.dumps({'sourceHeld':True,'evidenceIntegrityPassed':True,'nativeAcceptance':False,'sourceManifest':str(SOURCE/'component-manifest.json'),'sourceManifestSHA256':r['sourceManifestSHA256'],'files':files,'report':str(out/'report.json'),'reportSHA256':sha(out/'report.json')},indent=2)+'\n')
print(json.dumps({'passed':r['passed'],'checks':len(r['checks']),'report':str(out/'report.json'),'error':r.get('error'),'manifestSHA256':sha(ROOT/'component-manifest.json') if r['passed'] else None}));raise SystemExit(0 if r['passed'] else 1)
