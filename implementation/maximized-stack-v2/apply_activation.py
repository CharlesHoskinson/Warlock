"""Apply prepared next-session wiring; this command does not log out or restart."""
import hashlib,json,os,stat,subprocess,sys,tempfile
from pathlib import Path
sys.path.insert(0,'/home/hoskinson/window-integration-qa')
from qa_launch import require_qa_scope
scope=require_qa_scope();B=Path(__file__).resolve().parent;home=Path.home();ready=json.loads((B/'activation-ready.json').read_text())
config=home/'.config/hypr/autostart.lua';unit=home/'.config/systemd/user/wayland-wm@hyprland.desktop.service.d/60-floating-max-stack.conf';backup=home/'.local/state/omarchy/windows-parity-upgrades/maximized-stack-v2'
def sha(p):return hashlib.sha256(Path(p).read_bytes()).hexdigest()
def atomic(p,data,mode=0o644):
 fd,name=tempfile.mkstemp(prefix='.'+p.name+'.',dir=p.parent)
 try:
  os.fchmod(fd,mode)
  with os.fdopen(fd,'wb') as f:f.write(data);f.flush();os.fsync(f.fileno())
  os.replace(name,p)
 finally:
  if os.path.exists(name):os.unlink(name)
def check(cmd):return subprocess.run(cmd,check=True,capture_output=True,text=True,timeout=15).stdout
if len(sys.argv)!=2 or sys.argv[1] not in ('apply','rollback'):raise SystemExit('apply or rollback required; logout is separate')
if sys.argv[1]=='apply':
 for p,h in ready['files'].items():
  if sha(p)!=h:raise RuntimeError('Prepared pair changed: '+p)
 if sha(config)!=ready['autostartOriginalSHA256']:raise RuntimeError('User autostart changed after preparation')
 if unit.exists() or backup.exists():raise RuntimeError('Activation destination or backup exists')
 for file,digest in [('autostart.lua',ready['autostartCandidateSHA256']),('60-floating-max-stack.conf',ready['stagedUnitSHA256'])]:
  if sha(B/'activation'/file)!=digest:raise RuntimeError('Prepared wiring changed')
 backup.mkdir(parents=True,mode=0o700);mode=stat.S_IMODE(config.stat().st_mode)
 atomic(backup/'autostart.lua',config.read_bytes(),0o600)
 atomic(backup/'before.json',json.dumps({'mode':mode,'sha256':sha(config),'unitInitiallyAbsent':True}).encode(),0o600)
 try:
  unit.parent.mkdir(parents=True,exist_ok=True)
  atomic(config,(B/'activation/autostart.lua').read_bytes(),mode)
  atomic(unit,(B/'activation/60-floating-max-stack.conf').read_bytes())
  check(['systemctl','--user','daemon-reload']);check(['hyprctl','reload'])
  errors=check(['hyprctl','configerrors']).strip()
  if errors:raise RuntimeError('Hyprland config errors: '+errors)
 except BaseException:
  atomic(config,(backup/'autostart.lua').read_bytes(),mode)
  if unit.exists():unit.unlink()
  check(['systemctl','--user','daemon-reload']);check(['hyprctl','reload']);raise
 result={'scope':scope,'enabledForNextSession':True,'restartPerformed':False,'unit':str(unit),'unitSHA256':sha(unit),'configSHA256':sha(config),'backup':str(backup)}
else:
 deployed=json.loads((B/'activation-applied.json').read_text());before=json.loads((backup/'before.json').read_text())
 if sha(config)!=deployed['configSHA256'] or sha(unit)!=deployed['unitSHA256']:raise RuntimeError('Active wiring changed; refusing overwrite')
 if sha(backup/'autostart.lua')!=before['sha256']:raise RuntimeError('Backup changed')
 atomic(config,(backup/'autostart.lua').read_bytes(),before['mode']);unit.unlink()
 check(['systemctl','--user','daemon-reload']);check(['hyprctl','reload'])
 result={'scope':scope,'rolledBackForNextSession':True,'restartPerformed':False}
(B/('activation-applied.json' if sys.argv[1]=='apply' else 'activation-rollback.json')).write_text(json.dumps(result,indent=2)+'\n');print(json.dumps(result))
