from pathlib import Path
import hashlib,json,os,subprocess,sys,stat
sys.path.insert(0,'/home/hoskinson/window-integration-qa')
from qa_launch import require_qa_scope
scope=require_qa_scope();B=Path('/home/hoskinson/window-behavior-spec/minimize-motion-stage/provisional-route/family-scene-integration/service-family-preparation-v24');D=Path(__file__).resolve().parent
sha=lambda p:hashlib.sha256(Path(p).read_bytes()).hexdigest()
names=['batch_preview.py','native_runtime.py','test_renderer_job_role.py','renderer_role_cpu_fixture.c','pipe_transport.py','owned_launch.py','owned_commands.py','helper_supervisor.py','recovery_resources.py']
before={n:dict(sha256=sha(B/n),mode=stat.S_IMODE((B/n).stat().st_mode))for n in names}
env={k:v for k,v in os.environ.items()if k not in ('WAYLAND_DISPLAY','WAYLAND_SOCKET','DISPLAY','XAUTHORITY','HYPRLAND_INSTANCE_SIGNATURE','DBUS_SESSION_BUS_ADDRESS','AT_SPI_BUS_ADDRESS','QS_CONFIG_PATH','QS_CONFIG_NAME','QS_MANIFEST')}
command=[sys.executable,'-m','unittest','test_renderer_job_role','-v'];r=subprocess.run(command,cwd=B,env=env,text=True,stdout=subprocess.PIPE,stderr=subprocess.STDOUT,timeout=60)
def write(n,data):
 with os.fdopen(os.open(D/n,os.O_WRONLY|os.O_CREAT|os.O_EXCL,0o600),'wb')as f:f.write(data)
write('focused.log',r.stdout.encode());stable=all(sha(B/n)==v['sha256']and stat.S_IMODE((B/n).stat().st_mode)==v['mode']for n,v in before.items());assert stable
row=dict(result='pass'if r.returncode==0 else'fail',command=command,exitCode=r.returncode,scope=scope,sources=before,sourceUnchanged=True,logSHA256=sha(D/'focused.log'),nativeLaunch=False,nativeAccepted=False)
write('report.json',(json.dumps(row,indent=2)+'\n').encode());print(r.stdout,flush=True);sys.exit(r.returncode)
