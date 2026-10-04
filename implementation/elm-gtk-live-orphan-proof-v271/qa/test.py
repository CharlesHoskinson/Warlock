"""Real live orphan stress control; source snapshot, no GTK/native acceptance."""
import hashlib,json,os,resource,shutil,signal,subprocess,sys,time
from pathlib import Path
sys.path.insert(0,'/home/hoskinson/window-integration-qa')
from qa_launch import require_qa_scope,private_runtime
require_qa_scope();assert resource.getrlimit(resource.RLIMIT_CORE)==(1,1)
ROOT=Path(__file__).resolve().parents[1];REPO=ROOT.parents[1]
SOURCE=REPO/'implementation/elm-gtk-native-acquisition-fix-v268/qa/activation-supervisor.py'
def sha(p):return hashlib.sha256(Path(p).read_bytes()).hexdigest()
def identity(pid):return {'pid':pid,'start':Path('/proc',str(pid),'stat').read_text().rsplit(')',1)[1].split()[19]}
def live(row):
 try:return identity(row['pid'])==row
 except FileNotFoundError:return False
out=ROOT/'qa'/('orphan-'+str(time.time_ns()));out.mkdir();snapshot=out/'activation-supervisor.py';snapshot.write_bytes(SOURCE.read_bytes())
report={'passed':False,'nativeAcceptance':False,'sourceSHA256':sha(snapshot),'observedSource':str(SOURCE),'cases':[]}
try:
 for ordinal in range(8):
  case=out/str(ordinal);case.mkdir();runtime=private_runtime();proc=None;record={'case':ordinal,'passed':False,'cleanupSignals':[]};report['cases'].append(record)
  toy=case/'actual-fork.py';toy.write_text('''import json,os,sys,time
from pathlib import Path
directory=Path(sys.argv[1]);ordinal=int(sys.argv[2])
for index in range(8):
 child=os.fork()
 if child==0:
  if index%2:os.setsid()
  pid=os.getpid();start=Path('/proc',str(pid),'stat').read_text().rsplit(')',1)[1].split()[19]
  (directory/('born-'+str(pid)+'.json')).write_text(json.dumps({'pid':pid,'start':start}))
  time.sleep(.04+.005*index+.001*ordinal)
  (directory/('complete-'+str(pid))).write_text('normal0')
  os._exit(0)
 time.sleep(.0002*ordinal)
os._exit(0)
''')
  descriptor=runtime/'descriptor.json';descriptor.write_text(json.dumps({'argv':['/usr/bin/python3','-B',str(toy),str(case),str(ordinal)],'binarySHA256':sha('/usr/bin/python3')}));(case/'descriptor.json').write_bytes(descriptor.read_bytes())
  journal=case/'events.jsonl'
  try:
   with (case/'stdout').open('xb') as stdout,(case/'stderr').open('xb') as stderr:
    proc=subprocess.Popen(['/usr/bin/python3','-B',str(snapshot),str(descriptor),str(journal)],env=dict(os.environ,XDG_RUNTIME_DIR=str(runtime)),stdout=stdout,stderr=stderr,start_new_session=True)
    proc.wait(timeout=3);record['supervisorExitCode']=proc.returncode
   events=[json.loads(line) for line in journal.read_text().splitlines()];terminal=events[-1];born=[json.loads(p.read_text()) for p in case.glob('born-*.json')]
   record.update(terminal=terminal,recordedOrphans=len(born),normalCompletionMarkers=len(list(case.glob('complete-*'))),liveOrphans=[r for r in born if live(r)])
   assert proc.returncode==0 and terminal['kind']=='terminal' and terminal['error'] is None and not terminal['fallback'] and not terminal['cancelled']
   assert len(born)==8 and record['normalCompletionMarkers']==8 and not record['liveOrphans']
   statuses=terminal['allWaitStatuses'];assert len(statuses)==9 and all(row['exitCode']==0 for row in statuses)
   assert {(r['pid'],r['start']) for r in born}.issubset({(r['identity']['pid'],r['identity']['start']) for r in statuses})
   record['passed']=True
  finally:
   if proc is not None and proc.poll() is None:
    proc.terminate()
    try:proc.wait(timeout=.5)
    except subprocess.TimeoutExpired:proc.kill();proc.wait(timeout=.5)
   for path in case.glob('born-*.json'):
    row=json.loads(path.read_text())
    if live(row):os.kill(row['pid'],signal.SIGTERM);record['cleanupSignals'].append(row)
   deadline=time.monotonic()+.5
   while any(live(json.loads(p.read_text())) for p in case.glob('born-*.json')) and time.monotonic()<deadline:time.sleep(.01)
   assert not any(live(json.loads(p.read_text())) for p in case.glob('born-*.json')),'toy orphan must be retired before runtime removal'
   shutil.rmtree(runtime);record['runtimeGone']=not runtime.exists()
 report.update(passed=True,currentSourceUnchanged=sha(SOURCE)==sha(snapshot),actualOrphanExitRecords=64)
finally:
 (out/'test.py').write_bytes(Path(__file__).read_bytes());(out/'report.json').write_text(json.dumps(report,indent=2)+'\n');print(out/'report.json')
