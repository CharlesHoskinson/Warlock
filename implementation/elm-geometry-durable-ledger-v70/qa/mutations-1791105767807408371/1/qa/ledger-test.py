"""External behavioral oracles against actual durable filesystem ledger."""
import copy,errno,fcntl,hashlib,json,os,resource,shutil,signal,stat,subprocess,sys,tempfile,time,traceback
from pathlib import Path
from unittest.mock import patch
sys.path.insert(0,'/home/hoskinson/window-integration-qa')
from qa_launch import require_qa_scope
scope=require_qa_scope();assert resource.getrlimit(resource.RLIMIT_CORE)==(1,1)
ROOT=Path(__file__).resolve().parents[1];OUT=ROOT/'qa'/('ledger-'+str(time.time_ns()));OUT.mkdir(mode=0o700)
def sha(p):return hashlib.sha256(Path(p).read_bytes()).hexdigest()
files=[*sorted((ROOT/'adapter').glob('*.py')),ROOT/'SPEC.md',ROOT/'upstream.json',Path(__file__)]
inputs={str(p.relative_to(ROOT)):sha(p) for p in files}
for p in files:
 q=OUT/'inputs'/p.relative_to(ROOT);q.parent.mkdir(parents=True,exist_ok=True);shutil.copy2(p,q)
sys.path.insert(0,str(OUT/'inputs/adapter'))
import durable_ledger as module
from durable_ledger import Ledger,NAME,MAX_UNRESOLVED
from recovery_journal import Journal,guarded,RecoveryFailure
from endpoint import Refused
checks=[]
def failure_packet(kind,value,tb):
 report={'passed':False,'checks':checks,'inputs':inputs,'error':repr(value),'traceback':''.join(traceback.format_exception(kind,value,tb)),'nativeAcceptance':False}
 report['artifacts']={str(p.relative_to(OUT)):sha(p) for p in OUT.rglob('*') if p.is_file() and not p.is_symlink()}
 (OUT/'report.json').write_text(json.dumps(report,indent=2)+'\n');print(json.dumps({'passed':False,'report':str(OUT/'report.json'),'error':repr(value)}),flush=True)
sys.excepthook=failure_packet
def check(name,fn):
 try:fn()
 except Exception:
  checks.append({'name':name,'passed':False});raise
 checks.append({'name':name,'passed':True})
def eq(a,b):assert a==b,(a,b)
def refused(fn):
 try:r=fn()
 except (Refused,OSError,ValueError):return
 if hasattr(r,'close'):r.close()
 raise AssertionError('unsafe admission unexpectedly succeeded')
def bound(front='3',session='2',life='71'):return {'lifetime':life,'session':session,'frontend':front}
def intent(n=1,inc=None,op='maximize',b=None):
 b=b or bound();return {'request':str(n),'generation':str(n),'incarnation':str(inc or n),'operation':op,'context':{'lifetime':b['lifetime'],'epoch':b['frontend'],'output':'5','revision':'6'}}
def outcome(b,i,status='Committed',version=2):return {'protocolVersion':3,'kind':'effect-outcome','effectProtocol':version,'binding':copy.deepcopy(b),'intent':copy.deepcopy(i),'status':status,'reason':'applied','revision':'7','outputGeneration':'5'}
def runtime(name):
 p=OUT/'runtime'/name;p.mkdir(parents=True,mode=0o700);p.parent.chmod(0o700);return p

def independent_lifecycle():
 r=runtime('independent');b=bound();a=intent(1);bi=intent(2,op='minimize')
 with Ledger(r,'fixture','71') as j:
  eq(j.begin(b,a,2),True);eq(j.begin(b,a,2),False);eq(len(j.snapshot()['entries']),1)
  j.settle(outcome(b,a,'Unknown'));eq(j.begin(b,a,2),False)
  eq(j.begin(b,bi,1),True);j.settle(outcome(b,bi,version=1))
  eq([(e['intent']['incarnation'],e['status']) for e in j.snapshot()['entries']],[('1','Unknown')])
 with Ledger(r,'fixture','71') as j:
  recovered=j.recover(bound('9','8'));eq(recovered['binding'],bound('9','8'));eq(recovered['entries'][0]['binding'],b);eq(recovered['entries'][0]['intent'],a)
  eq(recovered['watermarks'][0]['request'],'2');eq(j.blocked('71','1'),True)
  for op,v in [('restore',1),('activate',1),('restore-geometry',2)]:refused(lambda:j.begin(bound('9','8'),intent(3,1,op,bound('9','8')),v))
  j.settle(outcome(b,a));eq(j.snapshot()['entries'],[]);eq(j.begin(bound('9','8'),intent(3,1,b=bound('9','8')),2),True)
check('AUnknown survives B legacy commit and restart then original A receipt frees exactly its target',independent_lifecycle)

def delayed_receipt():
 with Ledger(runtime('delayed'),'fixture','71') as j:
  b=bound();a=intent(1);other=bound('8','9');bi=intent(2,2,b=other)
  j.begin(b,a,2);j.settle(outcome(b,a,'Unknown'));j.begin(other,bi,2);j.settle(outcome(b,a))
  eq([r['intent'] for r in j.snapshot()['entries']],[bi]);eq(j.blocked('71','2'),True)
  saved=(j.path/NAME).read_bytes();refused(lambda:j.settle(outcome(b,a)));eq((j.path/NAME).read_bytes(),saved)
check('late original receipt cannot settle unrelated current binding target and terminal duplicate is inert',delayed_receipt)

for field in ['lifetime','session','frontend']:
 def bad_binding(f=field):
  with Ledger(runtime('binding-'+f),'fixture','71') as j:
   i=intent();j.begin(bound(),i,2);before=(j.path/NAME).read_bytes();o=outcome(bound(),i);o['binding'][f]='8';refused(lambda:j.settle(o));eq((j.path/NAME).read_bytes(),before)
 check('full original binding receipt mismatch '+field,bad_binding)
for field in ['request','generation','incarnation','operation']:
 def bad_intent(f=field):
  with Ledger(runtime('intent-'+f),'fixture','71') as j:
   i=intent();j.begin(bound(),i,2);before=(j.path/NAME).read_bytes();o=outcome(bound(),i);o['intent'][f]='restore-geometry' if f=='operation' else '8';refused(lambda:j.settle(o));eq((j.path/NAME).read_bytes(),before)
 check('full original intent receipt mismatch '+field,bad_intent)
for field in ['lifetime','epoch','output','revision']:
 def bad_context(f=field):
  with Ledger(runtime('context-'+f),'fixture','71') as j:
   i=intent();j.begin(bound(),i,2);before=(j.path/NAME).read_bytes();o=outcome(bound(),i);o['intent']['context'][f]='8';refused(lambda:j.settle(o));eq((j.path/NAME).read_bytes(),before)
 check('full original context receipt mismatch '+field,bad_context)
for name,change in [('protocolbool',{'effectProtocol':True}),('wrongversion',{'effectProtocol':1}),('version3',{'effectProtocol':3}),('wrongkind',{'kind':'host-uncertain'}),('statusPending',{'status':'Pending'}),('statusCancelled',{'status':'Cancelled'}),('reasonObject',{'reason':{}}),('reasonBound',{'reason':'x'*257}),('reasonSurrogate',{'reason':'\ud800'}),('metadatazero',{'revision':'0'}),('extrafield',{'extra':1})]:
 def bad_receipt(n=name,c=change):
  with Ledger(runtime('receipt-'+n),'fixture','71') as j:
   i=intent();j.begin(bound(),i,2);before=(j.path/NAME).read_bytes();refused(lambda:j.settle(dict(outcome(bound(),i),**c)));eq((j.path/NAME).read_bytes(),before)
 check('closed typed receipt '+name,bad_receipt)

def capacity():
 r=runtime('capacity')
 with Ledger(r,'fixture','71') as j:
  for n in range(1,65):eq(j.begin(bound(),intent(n),2),True)
  j.settle(outcome(bound(),intent(1),'Unknown'));before=(j.path/NAME).read_bytes()
  refused(lambda:j.begin(bound(),intent(65),2));eq((j.path/NAME).read_bytes(),before);eq(len(j.snapshot()['entries']),64)
 with Ledger(r,'fixture','71') as j:
  eq(len(j.recover(bound('9'))['entries']),64);eq(j.blocked('71','1'),True)
  j.settle(outcome(bound(),intent(32)));eq(j.begin(bound(),intent(65),2),True)
  eq(len(j.snapshot()['entries']),64);eq(j.blocked('71','1'),True);eq(j.blocked('71','32'),False)
check('64 full entries persist unknown and refuse65 without eviction then exact one settlement frees capacity',capacity)

def watermarks():
 with Ledger(runtime('watermarks'),'fixture','71') as j:
  b=bound();i=intent(7,op='minimize');j.begin(b,i,1);j.settle(outcome(b,i,version=1))
  refused(lambda:j.begin(b,intent(7,8),2));x=intent(8);x['generation']='7';refused(lambda:j.begin(b,x,2));eq(j.begin(b,intent(8),2),True)
  j.settle(outcome(b,intent(8)));refused(lambda:j.begin(b,intent(7,op='minimize'),1))
check('one allocation watermark across protocols prevents definitive replay and generation reuse',watermarks)

def scope_budget():
 with Ledger(runtime('scopebudget'),'fixture','71') as j:
  for n in range(1,129):
   b=bound(str(n));i=intent(1,b=b);j.begin(b,i,2);j.settle(outcome(b,i))
  eq(len(j.snapshot()['watermarks']),128);before=(j.path/NAME).read_bytes();b=bound('129');refused(lambda:j.begin(b,intent(1,b=b),2));eq((j.path/NAME).read_bytes(),before)
check('allocation scope budget128 fails129 without destroying watermarks',scope_budget)

def migration():
 r=runtime('migration');b=bound();a=intent(1,op='minimize')
 with Journal(r,'fixture','71') as old:
  old.begin(b,a,1);old.settle({'binding':b,'intent':a,'status':'Unknown','effectProtocol':1})
 with Ledger(r,'fixture','71') as j:eq(j.snapshot()['entries'][0]['intent'],a)
 with Journal(r,'fixture','71') as old:old.begin(b,intent(2,op='minimize'),1)
 refused(lambda:Ledger(r,'fixture','71'))
check('strict old singleton import once refuses later old producer write rather than losing evidence',migration)

def migrated_commit():
 r=runtime('migration-commit');b=bound();i=intent(1,op='restore')
 with Journal(r,'fixture','71') as old:
  record={'schema':1,'binding':b,'intent':i,'status':'Pending'};p=old.path/'host-intent.json';p.write_text(json.dumps(record));p.chmod(0o600)
  old.begin(b,i,1);old.settle({'binding':b,'intent':i,'status':'Committed','effectProtocol':1})
 with Ledger(r,'fixture','71') as j:eq(j.snapshot()['entries'],[]);refused(lambda:j.begin(b,i,1))
check('exact legacy settlement supersedes matching admitted pending without resurrecting or replay',migrated_commit)

def ownership():
 r=runtime('ownership')
 with Ledger(r,'fixture','71') as j:
  p=j.path/NAME;eq(stat.S_IMODE(p.stat().st_mode),0o600);eq(stat.S_IMODE(j.path.stat().st_mode),0o700)
  refused(lambda:Ledger(r,'fixture','71'));p.chmod(0o644);refused(j.snapshot);p.chmod(0o600)
  hard=j.path/'hard';os.link(p,hard);refused(j.snapshot);hard.unlink();eq(j.snapshot()['entries'],[])
  original=p.read_bytes();p.unlink();target=j.path/'target';target.write_bytes(original);target.chmod(0o600);p.symlink_to(target);refused(j.snapshot)
check('real writer lock private record modes hardlink and symlink guards remain strict',ownership)

def writes():
 with Ledger(runtime('partial'),'fixture','71') as j:
  write=os.write;fsync=os.fsync;replace=os.replace;events=[];first=[True]
  def limited(fd,data):
   if first[0]:first[0]=False;raise InterruptedError()
   events.append('write');return write(fd,data[:7])
  def sync(fd):events.append('directory-fsync' if stat.S_ISDIR(os.fstat(fd).st_mode) else 'file-fsync');return fsync(fd)
  def rename(*a,**kw):events.append('rename');return replace(*a,**kw)
  with patch.object(module.os,'write',limited),patch.object(module.os,'fsync',sync),patch.object(module.os,'replace',rename):eq(j.begin(bound(),intent(),2),True)
  eq(events[-3:],['file-fsync','rename','directory-fsync']);assert events.count('write')>5;eq(j.snapshot()['entries'][0]['intent'],intent())
check('actual partial writes and EINTR finish before file fsync rename directory fsync',writes)

for name,stage,code in [('full','write',errno.ENOSPC),('readonly','write',errno.EROFS),('nofilefsync','fsync',errno.EIO),('norename','replace',errno.EIO),('nodirfsync','directory',errno.EIO),('zerowrite','zero',None)]:
 def storage_fault(n=name,s=stage,c=code):
  r=runtime('fault-'+n)
  with Ledger(r,'fixture','71') as j:
   original=(j.path/NAME).read_bytes();sync=os.fsync
   def failure(*a,**kw):raise OSError(c,'injected storage fault')
   def directories(fd):
    if stat.S_ISDIR(os.fstat(fd).st_mode):return failure()
    return sync(fd)
   target='write' if s in ['write','zero'] else 'fsync' if s in ['fsync','directory'] else 'replace'
   replacement=(lambda *a:0) if s=='zero' else directories if s=='directory' else failure
   with patch.object(module.os,target,replacement):refused(lambda:j.begin(bound(),intent(),2))
   refused(j.snapshot);refused(lambda:j.begin(bound(),intent(2),2));assert not list(j.path.glob('ledger-pending-*'))
   if s!='directory':eq((j.path/NAME).read_bytes(),original)
  with Ledger(r,'fixture','71') as fresh:
   state=fresh.snapshot();eq(len(state['entries']),1 if s=='directory' else 0)
   if s=='directory':eq(fresh.begin(bound(),intent(),2),False)
   else:eq(fresh.begin(bound(),intent(),2),True)
 check('storage failure poisons current object explicit correction only '+name,storage_fault)

def abrupt():
 r=runtime('abrupt');code="import sys,json,time;sys.path.insert(0,sys.argv[1]);from durable_ledger import Ledger;j=Ledger(sys.argv[2],'fixture','71');j.begin(json.loads(sys.argv[3]),json.loads(sys.argv[4]),2);print('durable',flush=True);time.sleep(30)"
 child=subprocess.Popen(['/usr/bin/python3','-B','-c',code,str(OUT/'inputs/adapter'),str(r),json.dumps(bound()),json.dumps(intent())],stdout=subprocess.PIPE,stderr=subprocess.PIPE,text=True)
 try:
  import selectors
  with selectors.DefaultSelector() as select:
   select.register(child.stdout,selectors.EVENT_READ);assert select.select(3);eq(child.stdout.readline().strip(),'durable')
  child.kill();eq(child.wait(timeout=3),-signal.SIGKILL)
 finally:
  if child.poll() is None:child.kill();child.wait(timeout=3)
 with Ledger(r,'fixture','71') as j:
  eq(j.recover(bound('9'))['entries'][0]['intent'],intent());eq(j.begin(bound(),intent(),2),False)
check('real abrupt writer death releases lock and recovers informational original key without replay',abrupt)

def close_failure():
 with Ledger(runtime('close-failure'),'fixture','71') as j:
  close=os.close;once=[True]
  def fail(fd):
   regular=stat.S_ISREG(os.fstat(fd).st_mode)
   close(fd)
   if regular and once[0]:once[0]=False;raise OSError(errno.EIO,'injected close failure')
  # Avoid the preceding validated-read descriptors: inject only the actual
  # data-file close by tracking the freshly allocated temporary fd.
  opened=os.open;data_fd=[None]
  def tracked(name,*args,**kwargs):
   fd=opened(name,*args,**kwargs)
   if str(name).startswith('ledger-pending-'):data_fd[0]=fd
   return fd
  def fail_data(fd):
   close(fd)
   if fd==data_fd[0]:raise OSError(errno.EIO,'injected data-file close failure')
  with patch.object(module.os,'open',tracked),patch.object(module.os,'close',fail_data):refused(lambda:j.begin(bound(),intent(),2))
  refused(j.snapshot);refused(lambda:j.begin(bound(),intent(2),2))
check('data descriptor close failure cannot leave object authorizing more operations',close_failure)

for name,stage in [('data','fsync'),('rename','replace'),('directory','directory')]:
 def failed_settlement(n=name,s=stage):
  r=runtime('settlement-'+n)
  with Ledger(r,'fixture','71') as j:
   j.begin(bound(),intent(),2);j.settle(outcome(bound(),intent(),'Unknown'));sync=os.fsync
   def failure(*a,**kw):raise OSError(errno.EIO,'injected definitive settlement storage failure')
   def directories(fd):return failure() if stat.S_ISDIR(os.fstat(fd).st_mode) else sync(fd)
   with patch.object(module.os,'fsync' if s!='replace' else 'replace',directories if s=='directory' else failure):refused(lambda:j.settle(outcome(bound(),intent())))
   refused(j.snapshot)
  with Ledger(r,'fixture','71') as fresh:
   eq(fresh.blocked('71','1'),s!='directory')
   # Even a complete visible terminal-write after directory failure never
   # permits resubmitting the original allocation key.
   if s=='directory':refused(lambda:fresh.begin(bound(),intent(),2))
 check('definitive receipt storage failure no success or replay '+name,failed_settlement)

# Persisted adversaries are external edits to real private records, never
# assertions against a second implementation of the ledger.
for name,mutate in [
 ('booleanSchema',lambda s:s.update(schema=True)),
 ('foreignLifetime',lambda s:s.update(lifetime='72')),
 ('unknownField',lambda s:s.update(extra=1)),
 ('missingHashes',lambda s:s.pop('bootstrapHashes')),
 ('missingWatermark',lambda s:s.update(watermarks=[])),
 ('regressedWatermark',lambda s:s['watermarks'][0].update(request='0')),
 ('duplicateWatermark',lambda s:s['watermarks'].append(copy.deepcopy(s['watermarks'][0]))),
 ('duplicateKey',lambda s:s['entries'].append(copy.deepcopy(s['entries'][0]))),
 ('duplicateTargetNewBinding',lambda s:s['entries'].append(dict(copy.deepcopy(s['entries'][0]),binding=bound('3','9')))),
 ('terminalInUnresolved',lambda s:s['entries'][0].update(status='Committed')),
 ('crossProtocolOperation',lambda s:s['entries'][0].update(effectProtocol=1)),
 ('legacyRecordInCollection',lambda s:s['entries'][0].update(schema=1)),
 ('wrongContextLifetime',lambda s:s['entries'][0]['intent']['context'].update(lifetime='72')),
 ('unknownCounterType',lambda s:s['entries'][0]['intent'].update(generation=True)),
 ('noncanonicalCounter',lambda s:s['entries'][0]['intent'].update(request='01')),
 ('overflowCounter',lambda s:s['entries'][0]['intent'].update(request='18446744073709551616')),
 ('tooManyEntries',lambda s:s.update(entries=[copy.deepcopy(s['entries'][0]) for _ in range(65)])),
 ('tooManyWatermarks',lambda s:s.update(watermarks=[copy.deepcopy(s['watermarks'][0]) for _ in range(129)])),
 ('changedBootstrapHash',lambda s:s['bootstrapHashes'].update(**{'intent.json':'0'*64}))]:
 def corrupt(n=name,m=mutate):
  r=runtime('corrupt-'+n)
  with Ledger(r,'fixture','71') as j:
   j.begin(bound(),intent(),2);state=j.snapshot();m(state);p=j.path/NAME;p.write_text(json.dumps(state));p.chmod(0o600);before=p.read_bytes()
   refused(j.snapshot);eq(p.read_bytes(),before)
  refused(lambda:Ledger(r,'fixture','71'));eq(p.read_bytes(),before)
 check('persisted malformed ledger refuses without correction '+name,corrupt)

def raw_corruption():
 r=runtime('raw-corruption')
 with Ledger(r,'fixture','71') as j:
  p=j.path/NAME;original=p.read_bytes()
  for raw in [b'{"schema":3,"schema":3}',b'{',b'x'*524289]:
   p.write_bytes(raw);refused(j.snapshot);eq(p.read_bytes(),raw)
  p.write_bytes(original);eq(j.snapshot()['entries'],[])
check('duplicate JSON malformed JSON and byte overflow fail without automatic normalization',raw_corruption)

def deep_copy():
 with Ledger(runtime('deep-copy'),'fixture','71') as j:
  j.begin(bound(),intent(),2);r=j.recover(bound('9'));r['entries'][0]['intent']['incarnation']='999';r['watermarks'][0]['generation']='999'
  s=j.snapshot();s['entries'].clear();eq(j.snapshot()['entries'][0]['intent'],intent());eq(j.snapshot()['watermarks'][0]['generation'],'1')
check('informational recovery and snapshot cannot mutate durable source',deep_copy)

def max_uint():
 with Ledger(runtime('max-uint'),'fixture','71') as j:
  i=intent();i['request']=i['generation']='18446744073709551615';j.begin(bound(),i,2);j.settle(outcome(bound(),i));refused(lambda:j.begin(bound(),intent(2),2));eq(j.snapshot()['watermarks'][0]['generation'],'18446744073709551615')
check('exact UInt64 maximum retained without float conversion or wrap reuse',max_uint)

report={'passed':False,'checks':checks,'inputs':inputs,'qaScope':scope,'nativeAcceptance':False,'fullRecoveryAcceptance':False,'completedRequirementIds':[]}
try:
 for row in json.loads((ROOT/'upstream.json').read_text())['parents']:eq(sha(ROOT.parents[1]/row['path']),row['sha256'])
 for rel,digest in inputs.items():eq(sha(ROOT/rel),digest)
 report['passed']=True
except Exception as e:report.update(error=repr(e),traceback=traceback.format_exc())
report['artifacts']={str(p.relative_to(OUT)):sha(p) for p in OUT.rglob('*') if p.is_file() and not p.is_symlink()}
(OUT/'report.json').write_text(json.dumps(report,indent=2)+'\n');print(json.dumps({'passed':report['passed'],'checks':len(checks),'report':str(OUT/'report.json')}))
raise SystemExit(not report['passed'])
