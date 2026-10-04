"""New command write/receipt lifecycle with real subprocesses and fake journals."""
import ast,hashlib,json,os,resource,time
from pathlib import Path
from types import SimpleNamespace
assert resource.getrlimit(resource.RLIMIT_CORE)==(1,1)
from actor import Actor
from journal import Refused
ROOT=Path(__file__).parent;out=ROOT/('actor-sibling-'+str(time.time_ns()));out.mkdir()
tree=ast.parse((ROOT/'actor-test.py').read_text())
source=next(ast.literal_eval(n.value) for n in tree.body if isinstance(n,ast.Assign) and any(isinstance(t,ast.Name) and t.id=='source' for t in n.targets)).replace('MODE','pass')
class Original:
 @staticmethod
 def process(pid):return {'pid':pid,'start':Path('/proc',str(pid),'stat').read_text().rsplit(')',1)[1].split()[19]}
report={'passed':False,'nativeAcceptance':False,'fakeJournalRealSubprocessOnly':True,'checks':[]}
try:
 for profile in ['independent-groups','default-group']:
  case=out/profile;case.mkdir();binary=case/'fake-client';binary.write_text(source);binary.chmod(0o700)
  session=SimpleNamespace(host=SimpleNamespace(runtime=out,processes=[]),env=dict(os.environ),guard=lambda:None)
  actor=Actor(session,SimpleNamespace(original=Original),binary,case/'evidence',time.monotonic()+1,profile=profile)
  try:
   actor.send('open-sibling',time.monotonic()+1)
   actor.send('reparent-sibling',time.monotonic()+1,'B')
   before=len(actor.record['commands'])
   try:actor.send('reparent-sibling',time.monotonic()+1,'C');raise AssertionError('invalid parent written')
   except Refused:pass
   assert len(actor.record['commands'])==before
   actor.send('reparent-sibling',time.monotonic()+1,'A')
   actor.send('close-sibling',time.monotonic()+1)
   actor.close(time.monotonic()+1)
   receipts=[r for r in actor.rows if r['event']=='request']
   assert [(r['command'],r.get('requestedRole')) for r in receipts]==[('open-sibling',None),('reparent-sibling','B'),('reparent-sibling','A'),('close-sibling',None),('quit',None)]
   assert actor.record['normalExit'] is True and actor.process.returncode==0
   report['checks'].append({'profile':profile,'passed':True,'receiptCount':len(receipts),'registered':len(session.host.processes)==1,'invalidParentNotWritten':True})
  finally:actor.abort()
 report['passed']=True
finally:
 report['inputs']={str(p):hashlib.sha256(p.read_bytes()).hexdigest() for p in [Path(__file__),ROOT/'actor-test.py',ROOT/'actor.py',ROOT/'journal.py']}
 (out/'report.json').write_text(json.dumps(report,indent=2)+'\n');print(out/'report.json')
