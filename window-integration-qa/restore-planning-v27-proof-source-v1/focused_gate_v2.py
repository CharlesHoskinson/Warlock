"""Durable actual CPU/kernel proof, external to selected product sources."""
import hashlib,json,os,re,stat,subprocess,sys,time
from pathlib import Path
QA=Path('/home/hoskinson/window-integration-qa')
B=Path('/home/hoskinson/window-behavior-spec/minimize-motion-stage/provisional-route/family-scene-integration/service-restore-planning-v27')
P=QA/'restore-planning-v27-focused-proof-v2'
sys.path.insert(0,str(QA))
from qa_launch import require_qa_scope
def stamp(p):return {'sha256':hashlib.sha256(p.read_bytes()).hexdigest(),'mode':stat.S_IMODE(p.stat().st_mode)}
def main():
 scope=require_qa_scope();P.mkdir(mode=0o700)
 env={k:v for k,v in os.environ.items() if k not in ('WAYLAND_DISPLAY','WAYLAND_SOCKET','DISPLAY','XAUTHORITY','HYPRLAND_INSTANCE_SIGNATURE','DBUS_SESSION_BUS_ADDRESS','AT_SPI_BUS_ADDRESS','QS_CONFIG_PATH','QS_CONFIG_NAME','QS_MANIFEST')};env['PYTHONDONTWRITEBYTECODE']='1'
 paths=[p for p in B.iterdir() if p.is_file() and p.suffix in ('.py','.qnt','.md')]+[Path(__file__),Path('/usr/bin/hyprctl')]
 sources={str(p):stamp(p) for p in paths}
 cmd=['/usr/bin/python3','-m','unittest','-v','test_restore_planning']
 log=P/'actual-kernel-tests.log';started=time.monotonic()
 with os.fdopen(os.open(log,os.O_WRONLY|os.O_CREAT|os.O_EXCL,0o600),'w') as f:r=subprocess.run(cmd,cwd=B,env=env,stdout=f,stderr=subprocess.STDOUT,timeout=60)
 text=log.read_text();m=re.search(r'Ran (\d+) tests',text);count=int(m[1]) if m else 0
 exact=sources=={str(p):stamp(p) for p in paths}
 row={'result':'pass' if r.returncode==0 and count==14 and exact else 'fail','scope':scope,'command':cmd,'exitCode':r.returncode,'tests':count,'seconds':time.monotonic()-started,'log':str(log),**stamp(log),'sources':sources,'sourceUnchanged':exact,'nativeGUI':False,'nativeAccepted':False}
 with os.fdopen(os.open(P/'report.json',os.O_WRONLY|os.O_CREAT|os.O_EXCL,0o600),'w') as f:json.dump(row,f,indent=2);f.write('\n');f.flush();os.fsync(f.fileno())
 print(json.dumps({k:v for k,v in row.items() if k!='sources'}));return int(row['result']!='pass')
if __name__=='__main__':raise SystemExit(main())
