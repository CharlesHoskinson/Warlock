import hashlib,json,os,resource,subprocess,sys,time
from pathlib import Path
assert resource.getrlimit(resource.RLIMIT_CORE)==(1,1)
r=Path(__file__).resolve().parents[1];o=r.parent/'elm-gtk-native-acquisition-fix-v268';n=o/'qa/native-1791146650894471270';sha=lambda p:hashlib.sha256(p.read_bytes()).hexdigest()
sys.path.insert(0,str(o/'qa'))
from activation_import import identity
code="""import ctypes,json,os,sys
assert ctypes.CDLL(None,use_errno=True).prctl(4,0,0,0,0)==0
p='/proc/'+str(os.getpid());u=next(x for x in open(p+'/status') if x.startswith('Uid:')).split()[1:]
print(json.dumps({'pid':os.getpid(),'ruid':os.getuid(),'euid':os.geteuid(),'procOwner':os.stat(p).st_uid,'statusUIDs':list(map(int,u))}),flush=True)
sys.stdin.readline()
"""
child=subprocess.Popen([sys.executable,'-B','-c',code],stdin=subprocess.PIPE,stdout=subprocess.PIPE,stderr=subprocess.PIPE,text=True)
try:
 row=json.loads(child.stdout.readline());assert row['ruid']==row['euid']==os.getuid() and row['statusUIDs']==[os.getuid()]*4
 refused=None
 try:identity(child.pid)
 except RuntimeError as e:refused=str(e)
 nondumpable={'credentials':row,'identityRefusal':refused,'expectedMismatchReproduced':row['procOwner']!=os.getuid() and refused=='foreign UID'}
finally:
 child.stdin.write('quit\n');child.stdin.flush();stdout,stderr=child.communicate(timeout=3)
assert child.returncode==0
helper=subprocess.Popen(['/usr/bin/fusermount3','--version'],stdout=subprocess.PIPE,stderr=subprocess.PIPE,text=True)
try:
 deadline=time.monotonic()+3
 while True:
  pending=os.waitid(os.P_PID,helper.pid,os.WEXITED|os.WNOHANG|os.WNOWAIT)
  if pending is not None:break
  assert time.monotonic()<deadline;time.sleep(.001)
 proc=Path('/proc')/str(helper.pid)
 helperEvidence={'pid':helper.pid,'waitidUID':pending.si_uid,'waitidCode':pending.si_code,'waitidStatus':pending.si_status,'procOwner':proc.stat().st_uid,'statusUIDs':next(x for x in (proc/'status').read_text().splitlines() if x.startswith('Uid:')).split()[1:]}
 try:identity(helper.pid);helperEvidence['identityRefusal']=None
 except RuntimeError as error:helperEvidence['identityRefusal']=str(error)
finally:
 stdout,stderr=helper.communicate(timeout=3)
helperEvidence.update(exitCode=helper.returncode,stdout=stdout,stderr=stderr)
m=json.loads((n/'report.json').read_text());assert not m['passed'] and not m['cleanupPassed'] and len(m['checks'])==27 and all(x['passed'] for x in m['checks'])
journals=[];inputs={str(n/'report.json'):sha(n/'report.json'),str(o/'qa/activation-supervisor.py'):sha(o/'qa/activation-supervisor.py')}
for p in sorted((n/'native-evidence/activation-journals').glob('*/*.jsonl')):
 rows=[json.loads(x) for x in p.read_text().splitlines()];t=rows[-1];journals.append({'service':p.parent.name,'argv':rows[0]['argv'],'primary':t['childExitCode'],'error':t['error'],'fallback':t['fallback'],'statuses':[{'pid':x['identity']['pid'],'exitCode':x['exitCode']} for x in t['allWaitStatuses']]});inputs[str(p)]=sha(p)
assert sum(x['service']=='org.freedesktop.systemd1' and x['primary']==1 for x in journals)==2
assert next(x for x in journals if x['service']=='org.freedesktop.portal.Documents')['error']=="RuntimeError('foreign UID')"
assert 15 in [v['exitCode'] for x in journals if x['service']=='org.gtk.vfs.Daemon' for v in x['statuses']]
report={'passed':True,'nativeAcceptance':False,'actualNativePassed':False,'recordedPassedChecks':27,'actualNondumpableControl':nondumpable,'actualOwnedFusermountVersionControl':helperEvidence,'childExit':child.returncode,'journals':journals,'exactForeignChildIdentityKnown':False,'inputs':inputs}
out=r/'qa'/('diagnose-'+str(time.time_ns()));out.mkdir();(out/'report.json').write_text(json.dumps(report,indent=2)+'\n')
files={str(p.relative_to(r)):{'sha256':sha(p),'size':p.stat().st_size} for p in sorted(r.rglob('*')) if p.is_file() and p.name!='component-manifest.json'}
(r/'component-manifest.json').write_text(json.dumps({'sourceHeld':True,'nativeAcceptance':False,'scope':'Actual268 all-journal failure and actual credential characterization controls','files':files,'externalFiles':inputs,'verificationReport':str((out/'report.json').relative_to(r))},indent=2)+'\n')
print(json.dumps({'manifestSHA256':sha(r/'component-manifest.json'),'report':str(out/'report.json')}))
