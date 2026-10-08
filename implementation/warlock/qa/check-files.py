"""Actual Quickshell IPC fixture with private runtime/home and offscreen Qt.

Protocol/admission evidence only. Actual installed explorer is a separate native GUI case.
"""
import hashlib,json,os,pathlib,subprocess,sys,tempfile,time
ROOT=pathlib.Path(__file__).resolve().parents[1];sys.path.insert(0,str(ROOT/'adapter'))
from explorer import Explorer,Refused
APP=pathlib.Path('/home/hoskinson/.local/share/omarchy-files');checks=[]
def check(name,value):assert value,name;checks.append(name)
class Client:
 bound={'lifetime':'1','session':'1','frontend':'1'}
 def verify_process(self):pass
 def verify_paths(self):pass
serial=10
def request(intent=None):
 global serial
 serial+=1
 return {'protocolVersion':3,'kind':'files-open' if intent else 'files-request','binding':Client.bound,'requestId':str(serial),**({'intent':intent} if intent else {})}
def intent(snapshot,target):return {'service':snapshot['service'],'revision':snapshot['revision'],'target':target}
def wait(fn):
 deadline=time.monotonic()+3
 while time.monotonic()<deadline:
  value=fn()
  if value:return value
  time.sleep(.01)
 raise AssertionError('Original private explorer readiness deadline')
sha=lambda p:hashlib.sha256(p.read_bytes()).hexdigest();preserved={str(p):sha(p) for p in [APP/'scripts/ops.sh',APP/'spec/fileops.qnt']};original=os.environ.copy()
with tempfile.TemporaryDirectory(prefix='warlock-files-') as temporary:
 root=pathlib.Path(temporary);home=root/'home';home.mkdir(mode=0o700);runtime=root/'runtime';runtime.mkdir(mode=0o700)
 for name in ['Pictures','Documents','Downloads']:(home/name).mkdir()
 (home/'Documents/native-fixture.txt').write_text('Files collection fixture')
 app=root/'ipc-fixture';app.mkdir();(app/'scripts').mkdir();(app/'spec').mkdir();(app/'scripts/ops.sh').symlink_to(APP/'scripts/ops.sh');(app/'spec/fileops.qnt').symlink_to(APP/'spec/fileops.qnt')
 (app/'shell.qml').write_text('''import QtQuick
import Quickshell
import Quickshell.Io
ShellRoot {
 property string selected: Quickshell.env("FILES_OPEN") || "home"
 IpcHandler { target: "files"
 function migrationStatus(): string { return JSON.stringify({ready:true,error:"",pid:Quickshell.processId,instance:Quickshell.instanceId}) }
 function uiState(): string { return JSON.stringify({view:selected==="home" ? "home" : "folder",cwd:selected.startsWith("/") ? selected : Quickshell.env("HOME"),collId:selected.startsWith("coll:") ? selected.slice(5) : "",visible:true}) }
 function open(path: string): void { selected=path }
 }
}
''')
 env={**os.environ,'HOME':str(home),'XDG_RUNTIME_DIR':str(runtime),'XDG_DATA_HOME':str(home/'.local/share'),'XDG_CACHE_HOME':str(home/'.cache'),'XDG_CONFIG_HOME':str(home/'.config'),'QT_QPA_PLATFORM':'offscreen','WAYLAND_DISPLAY':'warlock-files-private','FILES_OPEN':'home','FILES_WIDGET':'0','FILES_DRYRUN':'1','QT_QUICK_CONTROLS_STYLE':'Basic','DBUS_SESSION_BUS_ADDRESS':'unix:path='+str(runtime/'absent'),'DBUS_SYSTEM_BUS_ADDRESS':'unix:path='+str(runtime/'absent')}
 log=open(root/'explorer.log','wb');process=subprocess.Popen(['/usr/bin/qs','-p',str(app),'--no-duplicate'],env=env,stdout=log,stderr=log)
 try:
  os.environ.update(env)
  with Explorer(app) as explorer:
   observed=wait(lambda:(snapshot:=explorer.observe()) and snapshot['peer'] and snapshot);print('OBSERVED',json.dumps(observed),file=sys.stderr)
   check('Native protocol fixture identity observed',observed['peer']['pid']==str(process.pid) and observed['peer']['target']=='home')
   old=intent(observed,'coll:images');opened=explorer.open(request(old),Client());check('Native IPC observes requested collection',opened['status']=='Opened' and opened['snapshot']['peer']['target']=='coll:images')
   check('IPC reuses exact native instance/PID/start',all(opened['snapshot']['peer'][k]==observed['peer'][k] for k in ['pid','start','instance']))
   check('Old queued collection intent cannot repeat',explorer.open(request(old),Client())['status']=='Refused')
   folder=explorer.open(request(intent(opened['snapshot'],str(home/'Documents'))),Client());check('Requested absolute folder is observed',folder['status']=='Opened' and folder['snapshot']['peer']['target']==str(home/'Documents'))
   same=explorer.open(request(intent(folder['snapshot'],str(home/'Documents'))),Client());check('Fresh same-folder gesture reuses current explorer',same['status']=='Opened' and same['snapshot']['peer']['pid']==str(process.pid))
   invalid=explorer.open(request(intent(same['snapshot'],'coll:execute')),Client());check('Unsupported collection is Refused without changing location',invalid['status']=='Refused' and invalid['snapshot']['peer']['target']==str(home/'Documents'))
   unsafe=explorer.open(request(intent(invalid['snapshot'],'$(touch injected)')),Client());check('Navigation input is never executed as a command',unsafe['status']=='Refused' and not (home/'injected').exists())
   bad=request(intent(invalid['snapshot'],'home'));bad['intent']['instance']='foreign'
   try:explorer.open(bad,Client());raise AssertionError('Frontend instance selected')
   except Refused:checks.append('Frontend cannot select executable, instance or QML root')
   process.terminate();process.wait(timeout=3);gone=explorer.observe()
   check('Retired native explorer identity is withdrawn',gone['peer'] is None and gone['available'])
   check('Old identity intent cannot target a replacement',explorer.open(request(intent(folder['snapshot'],'home')),Client())['status']=='Refused')
  check('Installed file operations and Quint spec are byte-identical',all(sha(pathlib.Path(p))==h for p,h in preserved.items()))
 except Exception:
  log.flush();print((root/'explorer.log').read_text()[-3500:],file=sys.stderr);raise
 finally:
  os.environ.clear();os.environ.update(original)
  if process.poll() is None:process.terminate()
  try:process.wait(timeout=3)
  except subprocess.TimeoutExpired:process.kill();process.wait()
  log.close()
print(json.dumps({'passed':True,'checks':checks,'scenario':'ux-033','installedSourceHashes':preserved,'evidenceScope':'Actual Quickshell IPC protocol fixture in private offscreen runtime; installed explorer/native-window/AT acceptance separate'}))
