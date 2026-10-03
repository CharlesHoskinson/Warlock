"""Run only QCoreApplication/Qt CPU programs; no display, GUI, window, input or Hypr plugin."""
from pathlib import Path
import hashlib,json,os,shutil,stat,subprocess,sys,time,uuid
sys.path.insert(0,'/home/hoskinson/window-integration-qa')
from qa_launch import require_qa_scope
B=Path(__file__).resolve().parent
MODES=('lifecycle','image-mode','config-mode','config-duplicate','config-replacement','fake-quickshell','wrong-thread','wrong-thread-first','duplicate-image')
def sha(p):return hashlib.sha256(Path(p).read_bytes()).hexdigest()
def main():
 require_qa_scope();stamp=str(time.time_ns());evidence=B/('cpu-evidence-'+stamp);evidence.mkdir(mode=0o700)
 sources={str(p):{'sha256':sha(p),'mode':stat.S_IMODE(p.stat().st_mode)}for p in B.iterdir()if p.is_file()and p.suffix in('.cpp','.hpp','.py','.so')or p.is_file()and p.name in('cpu-registry','cpu-dso','qmldir')}
 rows=[];configs=[]
 env=dict(os.environ)
 for k in tuple(env):
  if k in ('DISPLAY','WAYLAND_DISPLAY','WAYLAND_SOCKET','DBUS_SESSION_BUS_ADDRESS','DBUS_SYSTEM_BUS_ADDRESS','LD_PRELOAD','LD_AUDIT','QML_IMPORT_PATH','QT_PLUGIN_PATH','QT_QPA_PLATFORM','WINDOW_OBJECT_LIFETIME_CONFIG'):env.pop(k)
 r=subprocess.run([str(B/'cpu-registry')],env=env,capture_output=True,text=True,timeout=30)
 rows.append({'mode':'actual-registry','argv':[str(B/'cpu-registry')],'exitCode':r.returncode,'stdout':r.stdout,'stderr':r.stderr})
 for mode in MODES:
  runtime=Path('/run/user')/str(os.getuid())/'wqa'/uuid.uuid4().hex[:4]
  runtime.mkdir(mode=0o700);home=runtime/'home';home.mkdir(mode=0o700)
  image=home/'libobjectlifetime.so';shutil.copy2(B/'libobjectlifetime.so',image);os.chmod(image,0o644)
  config=home/'lifetime.config';selected={**env,'HOME':str(home),'XDG_RUNTIME_DIR':str(runtime),'WINDOW_OBJECT_LIFETIME_CONFIG':str(config)}
  argv=[str(B/'cpu-dso'),str(image),mode]
  try:r=subprocess.run(argv,env=selected,capture_output=True,text=True,timeout=30)
  except subprocess.TimeoutExpired as e:
   rows.append({'mode':mode,'argv':argv,'timeout':True,'stdout':str(e.stdout),'stderr':str(e.stderr),'retainedPrivateRuntime':str(runtime)});continue
  row={'mode':mode,'argv':argv,'exitCode':r.returncode,'stdout':r.stdout,'stderr':r.stderr,'initialImage':{'sha256':sources[str(B/'libobjectlifetime.so')]['sha256'],'mode':420},'actualRuntime':str(runtime)}
  case=evidence/mode;case.mkdir(mode=0o700)
  for name in ('lifetime.config','lifetime.config.old'):
   p=home/name
   if p.exists():shutil.copy2(p,case/name)
  row['normalExit']=r.returncode>=0;rows.append(row)
  if r.returncode==0:shutil.rmtree(runtime)
  else:row['retainedPrivateRuntime']=str(runtime)
 unchanged=all(Path(p).exists()and sha(p)==v['sha256']and stat.S_IMODE(Path(p).stat().st_mode)==v['mode']for p,v in sources.items())
 good=unchanged and len(rows)==len(MODES)+1 and all(r.get('exitCode')==0 for r in rows)
 result={'result':'pass'if good else'fail','GUI':False,'nativeWidgetAccepted':False,'QtCpuLibraryLoaded':True,'sources':sources,'sourceUnchanged':unchanged,'rows':rows}
 path=evidence/'report.json';path.write_text(json.dumps(result,indent=2)+'\n');print(json.dumps({'result':result['result'],'report':str(path),'cases':[(r['mode'],r.get('exitCode'))for r in rows],'sourceUnchanged':unchanged}));return int(not good)
if __name__=='__main__':raise SystemExit(main())
