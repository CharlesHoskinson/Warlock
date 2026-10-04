import copy,hashlib,json,os,resource,shutil,signal,subprocess,sys,time
from pathlib import Path
sys.path.insert(0,'/home/hoskinson/window-integration-qa')
from qa_launch import require_qa_scope,private_runtime
require_qa_scope();assert resource.getrlimit(resource.RLIMIT_CORE)==(1,1)
from outcomes import classify,Refused
from credentials import identity
ROOT=Path(__file__).resolve().parent;out=ROOT/('outcomes-'+str(time.time_ns()));out.mkdir();runtime=private_runtime();report={'passed':False,'nativeAcceptance':False,'checks':[]};inputs={}
def sha(p):return hashlib.sha256(Path(p).read_bytes()).hexdigest()
def record(name,argv,source):
 d={'argv':argv,'binarySHA256':sha(argv[0])};original=runtime/(name+'.json');original.write_text(json.dumps(d));capture=out/(name+'.json');capture.write_bytes(original.read_bytes())
 return {'name':name,'argv':argv,'binarySHA256':d['binarySHA256'],'source':str(source),'sourceSHA256':sha(source),'descriptor':str(original),'descriptorCapture':str(capture),'descriptorSHA256':sha(capture)}
def result(name,rec,rows,expected):
 accepted=True
 try:value=classify(rec,rows)
 except Refused:accepted=False;value=None
 assert accepted is expected,name;report['checks'].append({'name':name,'passed':True,'accepted':accepted,'classification':value})
try:
 source=Path('/usr/share/dbus-1/services/org.freedesktop.systemd1.service');rec=record('org.freedesktop.systemd1',['/bin/false'],source);journal=out/'false.jsonl'
 with (out/'false.stdout').open('wb') as stdout,(out/'false.stderr').open('wb') as stderr:
  p=subprocess.Popen([sys.executable,'-B',str(ROOT/'activation-supervisor.py'),rec['descriptor'],str(journal)],env=dict(os.environ,XDG_RUNTIME_DIR=str(runtime)),stdout=stdout,stderr=stderr);assert p.wait(timeout=3)==2
 rows=[json.loads(x) for x in journal.read_text().split('\n') if x];assert rows[-1]['childExitCode']==1
 result('actual-installed-false-expected-unavailable',rec,rows,True)
 shutil.rmtree(runtime);result('actual-descriptor-capture-after-runtime-removal',rec,rows,True)
 for name,change in [('wrong-name',lambda r:r.update(name='arbitrary.false')),('wrong-source',lambda r:r.update(source='/bin/false')),('wrong-hash',lambda r:r.update(binarySHA256='0'*64)),('wrong-argv',lambda r:r.update(argv=['/bin/false','ignored']))]:
  changed=copy.deepcopy(rec);change(changed);result(name,changed,rows,False)
 changed=copy.deepcopy(rows);changed[-1]['cancelled']=True;result('unavailable-cancelled-refused',rec,changed,False)
 changed=copy.deepcopy(rows);changed[-1]['allWaitStatuses'][0]['identity']['start']='1';result('wrong-life-ledger-refused',rec,changed,False)
 changed=copy.deepcopy(rows);changed[-1]['allWaitStatuses'][0]['exitCode']=0;result('wrong-status-ledger-refused',rec,changed,False)
 # Synthetic classification boundaries use a genuine current identity; no actual GVfs exit is claimed.
 runtime=private_runtime();source=Path('/usr/share/dbus-1/services/org.gtk.vfs.Daemon.service');gvfs=record('org.gtk.vfs.Daemon',['/usr/lib/gvfsd'],source);ident=identity(os.getpid());base=[{'kind':'supervisor-start','argv':gvfs['argv'],'descriptor':gvfs['descriptor'],'descriptorSHA256':gvfs['descriptorSHA256']},{'kind':'owned-child','identity':ident},{'kind':'signal','identity':ident,'observedIdentity':ident,'signal':signal.SIGTERM},{'kind':'child-exit','identity':ident,'observedIdentity':ident,'waitStatus':3840,'exitCode':15},{'kind':'terminal','error':None,'fallback':False,'liveDescendants':[],'cancelled':True,'childExitCode':15,'allWaitStatuses':[{'identity':ident,'exitCode':15}]}]
 result('synthetic-exact-gvfs-handler-cancellation',gvfs,base,True)
 for name,mutate in [('unsignalled15',lambda r:r.pop(2)),('signal-after-exit',lambda r:r.insert(3,r.pop(2))),('wrong-signal-start',lambda r:r[2].update(identity=dict(ident,start='1'))),('wrong-signal-uid',lambda r:r[2].update(observedIdentity=dict(ident,effectiveUid=0))),('kill-fallback',lambda r:r[-1].update(fallback=True)),('uncancelled15',lambda r:r[-1].update(cancelled=False)),('wrong-waitstatus',lambda r:r[3].update(waitStatus=256)),('duplicate-ledger',lambda r:r[-1]['allWaitStatuses'].append(r[-1]['allWaitStatuses'][0]))]:
  changed=copy.deepcopy(base);mutate(changed);result(name,gvfs,changed,False)
 changed=copy.deepcopy(gvfs);changed['name']='arbitrary';result('other-service15',changed,base,False)
 report['passed']=True
finally:
 if runtime.exists():shutil.rmtree(runtime)
 report['inputs']={str(p):sha(p) for p in [Path(__file__),ROOT/'outcomes.py',ROOT/'credentials.py',ROOT/'activation-supervisor.py',Path('/usr/share/dbus-1/services/org.freedesktop.systemd1.service'),Path('/bin/false'),Path('/usr/share/dbus-1/services/org.gtk.vfs.Daemon.service'),Path('/usr/lib/gvfsd')]};(out/'report.json').write_text(json.dumps(report,indent=2)+'\n');print(out/'report.json')
