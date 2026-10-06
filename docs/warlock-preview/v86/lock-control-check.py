"""Reproduce the old inode race at the actual unchanged C fixture guard."""
import hashlib,json,pathlib,resource,shlex,shutil,subprocess,sys,time
sys.path.insert(0,'/home/hoskinson/window-integration-qa');from qa_launch import require_qa_scope
require_qa_scope();assert resource.getrlimit(resource.RLIMIT_CORE)==(1,1)
root=pathlib.Path(__file__).parent;repo=root.parents[2];out=root/('lock-control-check-'+str(time.time_ns()));out.mkdir(mode=0o700)
sha=lambda p:hashlib.sha256(p.read_bytes()).hexdigest()
old=repo/'implementation/warlock-session-lock-fixture-v1/qa/lock-build-1791243868430702627'
report={'passed':False,'commands':[],'inputs':{},'nativeAcceptance':False,'fullReleaseAccepted':False}
def run(name,args):
 p=subprocess.run(args,capture_output=True,text=True,timeout=60);(out/(name+'.stdout')).write_text(p.stdout);(out/(name+'.stderr')).write_text(p.stderr);report['commands'].append({'name':name,'args':args,'exitCode':p.returncode});print(name,p.returncode,flush=True);assert p.returncode==0,p.stderr;return p.stdout
try:
 proof=json.loads((old/'report.json').read_text());assert proof['passed']
 source=old/'inputs/session-lock.c';assert sha(source)==proof['inputs'][str(repo/'implementation/warlock-session-lock-fixture-v1/native/session-lock.c')]
 for path in [source,old/'generated/session-lock-client.h',old/'generated/session-lock-protocol.c',root/'lock-control-race.c',root/'lock_control.py',pathlib.Path(__file__),old/'report.json']:report['inputs'][str(path)]=sha(path)
 shutil.copy2(source,out/'session-lock.c');shutil.copy2(root/'lock-control-race.c',out/'race.c')
 flags=shlex.split(run('flags',['pkg-config','--cflags','--libs','wayland-client']))
 run('compile',['gcc','-std=c11','-O1','-Wall','-Wextra','-Werror','-fsanitize=address,undefined','-fno-omit-frame-pointer','-I'+str(old/'generated'),str(out/'race.c'),str(old/'generated/session-lock-protocol.c'),'-o',str(out/'checks'),*flags,'-lm'])
 modes=[]
 for mode in ['replace','stable']:
  control=out/(mode+'-control');run(mode+'-hold',['/usr/bin/python3','-B',str(root/'lock_control.py'),str(control),'hold'])
  evidence=json.loads(run(mode,[str(out/'checks'),str(root/'lock_control.py'),str(control),mode]));assert evidence['passed'];modes.append(evidence)
 assert modes[0]['reproducedOriginalUnlinkedReaderRefusal'] and modes[1]['stableIdentityPublisherAccepted']
 assert all(sha(pathlib.Path(p))==h for p,h in report['inputs'].items())
 report.update(passed=True,evidence=modes,scope='Actual unchanged C wants_unlock/fstat identity guard and real protected Python publisher, deterministic publication between open and fstat; no Wayland lock/GUI acceptance.')
except Exception as e:report['error']=repr(e)
report['artifacts']={str(p.relative_to(out)):sha(p) for p in out.rglob('*') if p.is_file()};(out/'report.json').write_text(json.dumps(report,indent=2)+'\n');print(json.dumps({'passed':report['passed'],'report':str(out/'report.json'),'error':report.get('error')}),flush=True);sys.exit(not report['passed'])
