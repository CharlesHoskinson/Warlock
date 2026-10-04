"""Filesystem isolation and restartable, ownership-qualified legacy migration."""
import copy,fcntl,hashlib,json,os,resource,sys,tempfile,time,traceback
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1];sys.path.insert(0,str(ROOT/'adapter'))
from recovery_journal import Journal
from endpoint import Refused
assert resource.getrlimit(resource.RLIMIT_CORE)==(1,1)
OUT=ROOT/'qa'/('namespace-'+str(time.time_ns()));OUT.mkdir()
report={'passed':False,'checks':[],'scope':'CPU filesystem/migration evidence; native GUI acceptance separate','inputs':{str(p):hashlib.sha256(p.read_bytes()).hexdigest() for p in [Path(__file__),ROOT/'adapter/recovery_journal.py',ROOT/'adapter/endpoint.py']}}
def check(name,value):
 report['checks'].append({'name':name,'passed':bool(value)});assert value,name
def refused(fn):
 try:
  value=fn()
  if isinstance(value,Journal):value.close()
 except (OSError,ValueError,Refused):return True
 return False
def record(life='71',status='Pending',request='1'):
 return {'schema':1,'binding':{'lifetime':life,'session':'2','frontend':'3'},'intent':{'request':request,'generation':request,'incarnation':'4','operation':'minimize','context':{'lifetime':life,'epoch':'3','output':'5','revision':'6'}},'status':status}
def put(path,value):
 path.parent.mkdir(parents=True,exist_ok=True,mode=0o700);path.write_text(json.dumps(value,separators=(',',':')));path.chmod(0o600)
def seed(runtime,host=None,broker=None,owner=True):
 base=runtime/'elm-window-recovery';base.mkdir(mode=0o700)
 if host is not None:put(base/'host-intent.json',host)
 if broker is not None:put(base/'intent.json',broker)
 if owner:put(base/'legacy-owner.json',{'schema':1,'instance':'alpha','lifetime':'71'})
 return base
try:
 with tempfile.TemporaryDirectory(prefix='elm-namespace-') as tmp:
  root=Path(tmp);root.chmod(0o700)
  def runtime(name):
   p=root/name;p.mkdir(mode=0o700);return p
  r=runtime('isolation')
  with Journal(r,'alpha','71') as a,Journal(r,'beta','71') as b,Journal(r,'alpha','72') as c:
   a.write(record());check('sameLifetimeOtherInstanceIsEmpty',b.read() is None)
   check('sameInstanceOtherLifetimeIsEmpty',c.read() is None)
   b.write(record(request='7'));c.write(record('72',request='8'))
   check('threeConcurrentNamespacesRemainIndependent',[j.read()['intent']['request'] for j in [a,b,c]]==['1','7','8'])
   check('sameNamespaceWriterRefused',refused(lambda:Journal(r,'alpha','71')))
   check('foreignLifetimeWriteRefused',refused(lambda:a.write(record('72'))))
   check('foreignWritePreservesOwnRecord',a.read()['intent']['request']=='1')
   check('namespaceDirectoryPrivate',all((p.stat().st_mode&0o777)==0o700 for p in [a.path,a.path.parent,a.path.parent.parent]))
   check('metadataFilesPrivate',all((p.stat().st_mode&0o777)==0o600 for p in a.path.iterdir()))
  for instance in ['../alpha','alpha/beta','','a-b','é']:
   check('invalidInstanceRefused:'+repr(instance),refused(lambda:Journal(r,instance,'71')))
  for life in ['0','071','../71',71,'18446744073709551616']:
   check('invalidLifetimeRefused:'+repr(life),refused(lambda:Journal(r,'alpha',life)))
  r=runtime('pending');base=seed(r,record(),record());saved={p.name:p.read_bytes() for p in base.iterdir()}
  with Journal(r,'alpha','71') as a:
   check('matchingLegacyPendingImported',a.read()==record() and a.read('host-intent.json')==record())
   check('matchingLegacyPendingRemainsInformationalUnknown',a.uncertain(record()['binding'])['intent']==record()['intent'])
   plan=json.loads((a.path/'migration-plan.json').read_text());marker=json.loads((a.path/'migration.json').read_text())
   check('migrationMarkerHashesDurablePlan',marker['planSHA256']==hashlib.sha256((a.path/'migration-plan.json').read_bytes()).hexdigest())
   check('legacySourceHashesRecorded',all(plan['sourceHashes'][n]==hashlib.sha256(saved[n]).hexdigest() for n in ['host-intent.json','intent.json']))
   a.settle(dict(record(),status='Committed'));check('newSettlementSuppressesUnknown',a.uncertain(record()['binding']) is None)
  check('legacyRecordsNeverModified',all((base/n).read_bytes()==raw for n,raw in saved.items()))
  put(base/'intent.json',record(request='9'))
  with Journal(r,'alpha','71') as a:check('completedMigrationNeverResurrectsChangedLegacy',a.read()['status']=='Committed' and a.read()['intent']['request']=='1')
  with Journal(r,'beta','71') as b:check('otherInstanceCannotImportOwnedLegacy',b.read() is None and b.read('host-intent.json') is None)
  r=runtime('ambiguous');base=seed(r,record(),owner=False)
  check('matchingUnownedLegacyRefused',refused(lambda:Journal(r,'alpha','71')))
  check('ambiguousLegacyPreserved',json.loads((base/'host-intent.json').read_text())==record())
  r=runtime('foreign');base=seed(r,record('72'),record('72'),owner=False)
  with Journal(r,'alpha','71') as a:check('foreignLifetimeLegacyExcludedWithoutOwnershipGuess',a.read() is None and a.read('host-intent.json') is None)
  r=runtime('settled');seed(r,record(),record(status='Committed'))
  with Journal(r,'alpha','71') as a:check('exactLegacySettlementSuppressesUnknown',a.uncertain(record()['binding']) is None)
  r=runtime('stale');seed(r,record(request='2'),record(status='Committed'))
  with Journal(r,'alpha','71') as a:check('olderLegacySettlementCannotClearLatestAdmission',a.uncertain(record()['binding'])['intent']['request']=='2')
  r=runtime('resume');base=seed(r,record(),record());path=Journal.namespace_path(r,'alpha','71');path.mkdir(parents=True,mode=0o700);path.parent.chmod(0o700)
  plan={'schema':1,'target':{'instance':'alpha','lifetime':'71'},'records':{'host-intent.json':record(),'intent.json':record()},'sourceHashes':{n:hashlib.sha256((base/n).read_bytes()).hexdigest() for n in ['host-intent.json','intent.json']}}
  put(path/'migration-plan.json',plan);put(path/'host-intent.json',record(request='99'));put(base/'intent.json',record(request='88'))
  with Journal(r,'alpha','71') as a:
   check('interruptedCopiesResumeFromStablePlan',a.read()['intent']['request']=='1' and a.read('host-intent.json')['intent']['request']=='1')
   check('resumedMigrationPublishesCompletionMarker',(path/'migration.json').is_file())
  marker=json.loads((path/'migration.json').read_text());bad=copy.deepcopy(marker);bad['planSHA256']='0'*64;put(path/'migration.json',bad)
  check('wrongPlanHashRefused',refused(lambda:Journal(r,'alpha','71')))
  bad=copy.deepcopy(marker);bad['schema']=True;put(path/'migration.json',bad)
  check('BooleanSchemaMarkerRefused',refused(lambda:Journal(r,'alpha','71')))
  put(path/'migration.json',marker);bad=copy.deepcopy(plan);bad['target']['instance']='beta';put(path/'migration-plan.json',bad)
  check('foreignPlanTargetRefused',refused(lambda:Journal(r,'alpha','71')))
  r=runtime('locked');base=seed(r,record(),record());fd=os.open(base/'writer.lock',os.O_RDWR|os.O_CREAT,0o600)
  try:
   fcntl.flock(fd,fcntl.LOCK_EX|fcntl.LOCK_NB)
   check('activeLegacyWriterPreventsMigration',refused(lambda:Journal(r,'alpha','71')))
   check('refusedMigrationPublishesNoCompletion',not (Journal.namespace_path(r,'alpha','71')/'migration.json').exists())
  finally:os.close(fd)
  with Journal(r,'alpha','71') as a:check('migrationSucceedsAfterLegacyWriterQuiesces',a.read()==record())
  for name,mutate in [('public',lambda p:p.chmod(0o644)),('symlink',lambda p:(p.unlink(),p.symlink_to('/dev/null'))),('malformed',lambda p:p.write_text('{'))]:
   r=runtime(name);base=seed(r,record(),record());mutate(base/'intent.json')
   check('unsafeLegacyRefused:'+name,refused(lambda:Journal(r,'alpha','71')))
 report['passed']=True
except Exception as error:report.update(error=repr(error),traceback=traceback.format_exc())
(OUT/'report.json').write_text(json.dumps(report,indent=2)+'\n');print(json.dumps({'passed':report['passed'],'checks':len(report['checks']),'report':str(OUT/'report.json'),'error':report.get('error')}));raise SystemExit(not report['passed'])
